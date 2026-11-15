"""🧪 Tests for runpod_v2.py and watchdog.py against a FAKE Runpod (no money, no network). CHA-798.
Run: python scripts/rental/test_runpod_v2.py      (exit 0 = all passed)

The fake speaks the v2 contract from the docs: paginated GET /v2/pods, GET /v2/pods/{id}, DELETE -> 204 empty
body, plus a GraphQL endpoint for the balance. Every test also asks: could this have FAILED? (the 'refuse'
cases exist so a pass means something).
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


class Fake:
    """World state the handler reads and changes."""
    def __init__(self):
        self.pods = {}               # id -> pod dict
        self.page_size = 2
        self.delete_codes = []       # queued codes for DELETE (pop front); default 204
        self.ghost = False           # True: DELETE says 204 but the pod never goes away
        self.graphql_status = 200
        self.balance = 40.0
        self.calls = []


def make_handler(fake):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, obj=None):
            raw = b"" if obj is None else json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _authed(self):
            return self.headers.get("Authorization") == "Bearer TESTKEY"

        def do_GET(self):
            fake.calls.append(("GET", self.path))
            if not self._authed():
                return self._send(401, {"error": "unauthorized"})
            if self.path.startswith("/v2/pods/"):
                pid = self.path.rsplit("/", 1)[1]
                return self._send(200, fake.pods[pid]) if pid in fake.pods else self._send(404, {"error": "not found"})
            if self.path.startswith("/v2/pods"):
                ids = sorted(fake.pods)
                start = int(self.path.split("cursor=c")[1]) if "cursor=" in self.path else 0
                chunk = ids[start:start + fake.page_size]
                more = start + fake.page_size < len(ids)
                return self._send(200, {"pods": [fake.pods[i] for i in chunk],
                                        "pagination": {"nextCursor": f"c{start + fake.page_size}" if more else None,
                                                       "hasNextPage": more}})
            self._send(404, {"error": "no route"})

        def do_DELETE(self):
            fake.calls.append(("DELETE", self.path))
            if not self._authed():
                return self._send(401, {"error": "unauthorized"})
            pid = self.path.rsplit("/", 1)[1]
            code = fake.delete_codes.pop(0) if fake.delete_codes else 204
            if code == 204 and not fake.ghost:
                fake.pods.pop(pid, None)
            return self._send(code) if code == 204 else self._send(code, {"error": f"fake {code}"})

        def do_POST(self):            # GraphQL balance
            fake.calls.append(("POST", self.path))
            n = int(self.headers.get("Content-Length") or 0)
            self.rfile.read(n)
            if fake.graphql_status != 200:
                return self._send(fake.graphql_status, {"error": "gone"})
            return self._send(200, {"data": {"myself": {"clientBalance": fake.balance}}})
    return H


def start(fake):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(fake))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    os.environ.update(RUNPOD_API_BASE=base, RUNPOD_GRAPHQL_URL=base + "/graphql",
                      RUNPOD_RETRY_SLEEP="0", RUNPOD_VERIFY_SLEEP="0")
    return srv, base


def pod(i, cost=1.0, status="RUNNING"):
    return {"id": i, "name": i, "status": status, "cost": cost, "runtime": {"uptime": 60}}


results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("✅" if cond else "❌"), name)


import runpod_v2 as rp                                    # noqa: E402

# 1. pagination: 5 pods over 3 pages, all come back
f = Fake(); srv, base = start(f)
for i in "abcde":
    f.pods[i] = pod(i)
check("list_pods follows the cursor across 3 pages (5 pods)", len(rp.list_pods("TESTKEY")) == 5)
check("list_pods made exactly 3 list calls", sum(1 for m, p in f.calls if m == "GET" and p.startswith("/v2/pods") and "/v2/pods/" not in p) == 3)

# 2. a broken list RAISES (never reads as 'no pods')
try:
    rp.list_pods("WRONGKEY"); raised = False
except RuntimeError:
    raised = True
check("list_pods raises on 401 instead of returning []", raised)

# 3. live() drops TERMINATED only
check("live() keeps RUNNING/EXITED/ERROR, drops TERMINATED",
      [p["id"] for p in rp.live([pod("r"), pod("x", status="EXITED"), pod("e", status="ERROR"), pod("t", status="TERMINATED")])] == ["r", "x", "e"])

# 4. terminate happy path: 204 then 404
msgs = []
check("terminate: DELETE 204 + GET 404 -> True", rp.terminate("TESTKEY", "a", say=msgs.append) and "a" not in f.pods)
check("terminate prints TERMINATED only after the GET", any("TERMINATED a" in m for m in msgs))

# 5. terminate refuses: DELETE 500
f.delete_codes = [500]; msgs = []
check("terminate: DELETE 500 -> False with FATAL", not rp.terminate("TESTKEY", "b", say=msgs.append) and any("FATAL" in m for m in msgs))
check("...and the pod is still there (nothing pretended)", "b" in f.pods)

# 6. 429 is retried, then succeeds
f.delete_codes = [429, 429, 204]; msgs = []
check("terminate: 429, 429, 204 -> retried, then True", rp.terminate("TESTKEY", "b", say=msgs.append))

# 7. ghost: 204 but the pod never leaves -> False, loudly
f.ghost = True; msgs = []
check("terminate: 204 but still listed -> False, STILL LISTED", not rp.terminate("TESTKEY", "c", say=msgs.append) and any("STILL LISTED" in m for m in msgs))
f.ghost = False

# 8. status TERMINATED counts as gone
f.pods["t"] = pod("t", status="TERMINATED"); f.ghost = True; msgs = []
check("terminate: GET 200 with status TERMINATED -> True", rp.terminate("TESTKEY", "t", say=msgs.append))
f.ghost = False

# 9. balance: GraphQL alive -> number; GraphQL 410 -> None, no exception
check("balance() reads the GraphQL balance", rp.balance("TESTKEY") == 40.0)
f.graphql_status = 410
check("balance() returns None on 410 (doesn't raise)", rp.balance("TESTKEY") is None)
srv.shutdown()


# 10. THE WATCHDOG, end to end, with GraphQL already DEAD: the v2 meter alone must still enforce the cap.
def run_watchdog(fake, cap, timeout=40):
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".key") as k:
        k.write("TESTKEY")
    env = dict(os.environ, WATCHDOG_POLL="1", WATCHDOG_KEY_FILE=k.name, PYTHONIOENCODING="utf-8")
    try:
        out = subprocess.run([sys.executable, os.path.join(HERE, "watchdog.py"), "10.5", "7", str(cap), "0"],
                             env=env, capture_output=True, text=True, timeout=timeout, encoding="utf-8")
        return out.returncode, out.stdout + out.stderr
    finally:
        os.unlink(k.name)


f = Fake(); srv, base = start(f)
f.graphql_status = 410
f.pods["p1"] = pod("p1", cost=3600.0)          # $1 per second, so a $2 cap trips within a few polls
rc, log = run_watchdog(f, cap=2)
check("watchdog (GraphQL dead): v2 meter trips the cap and kills the pod", "TERMINATE p1" in log and "p1" not in f.pods)
check("watchdog says the balance is UNKNOWN rather than inventing one", "UNKNOWN" in log)
check("watchdog exits cleanly once no pods are left", rc == 0 and "watchdog exiting" in log)
srv.shutdown()

# 11. control: under the cap, nothing is killed (the test above can fail)
f = Fake(); srv, base = start(f)
f.pods["p2"] = pod("p2", cost=0.01)
with tempfile.NamedTemporaryFile("w", delete=False, suffix=".key") as k:
    k.write("TESTKEY")
env = dict(os.environ, WATCHDOG_POLL="1", WATCHDOG_KEY_FILE=k.name, PYTHONIOENCODING="utf-8")
proc = subprocess.Popen([sys.executable, os.path.join(HERE, "watchdog.py"), "10.5", "7", "35", "0"],
                        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
import time                                               # noqa: E402
time.sleep(4)
proc.terminate(); log = proc.communicate(timeout=10)[0]
os.unlink(k.name)
check("control: a cheap pod under the cap is NOT killed", "TERMINATE" not in log and "p2" in f.pods)
check("control: balance-meter is used while GraphQL is alive", "balance=$40.00" in log)
srv.shutdown()

failed = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} passed" + (f"; FAILED: {failed}" if failed else ""))
sys.exit(1 if failed else 0)
