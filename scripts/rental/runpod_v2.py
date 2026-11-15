"""🔪🐙 runpod_v2.py: the ONE place the Consortium-side Python talks to Runpod. (CHA-798, 2026-11-14, heartbeat Ace)

WHY THIS FILE EXISTS
  Runpod retires the GraphQL API "early 2027" (410 Gone; their 2026-08-18 email, ace@ 1a01714d9c3b818c).
  rp.py and watchdog.py each carried their own GraphQL calls. Now they import this, the same way both
  pod_autokill scripts `source` tfg-r22w/runpod_terminate.sh (CHA-721). Two copies of a kill switch drift.

THE CONTRACT (docs.runpod.io/api-reference-v2, read 2026-11-14)
  GET    /v2/pods             -> 200 {"pods": [...], "pagination": {"nextCursor", "hasNextPage"}}
                                 ⚠️ PAGINATED. One response is NOT every pod: follow nextCursor.
                                 ⚠️ Unknown query params are silently IGNORED (?status=RUNNING returns everything),
                                    so filter in our own code.
  GET    /v2/pods/{id}        -> 200 pod | 404 gone
  DELETE /v2/pods/{id}        -> 204 with an EMPTY body. Success is the STATUS CODE, never the body.
  pod fields we use: id, name, status (PROVISIONING STARTING RUNNING EXITED ERROR TERMINATED),
                     cost (USD per hour), runtime.uptime (seconds, may be null), createdAt.

WHAT v2 CANNOT DO, said out loud
  🚫 ACCOUNT BALANCE. The migration guide's "Removed" table: `myself { clientBalance }` -> "None. Keep using
     the GraphQL API for this." So balance() below is GraphQL ON PURPOSE, and returns None (never raises)
     once GraphQL is gone, so a caller can keep working on a v2-derived spend meter instead.

"TERMINATED" IS ONLY SAID AFTER THE WORLD CONFIRMS IT: DELETE 204 means "accepted"; we then GET the pod and
call it gone on 404 (or status TERMINATED, which the enum also allows). A cost-control path that fails OPEN
is worse than none, because it is believed.

Test hooks (env): RUNPOD_API_BASE and RUNPOD_GRAPHQL_URL (point at a fake server), RUNPOD_RETRY_SLEEP,
RUNPOD_VERIFY_SLEEP. Tests: test_runpod_v2.py (a fake Runpod that speaks this contract; no money, no network).
The key is passed in by the caller and never printed here.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "ace-runpod-v2/1.0"


def _base():
    return os.environ.get("RUNPOD_API_BASE", "https://api.runpod.io").rstrip("/")


def call(method, path, key, timeout=60):
    """One HTTP call. Returns (status_code, parsed_json_or_None). Code 0 = the request itself failed.
    A 429 is retried with exponential backoff (Runpod asks for exactly that: 20 s, 40 s, 80 s)."""
    retry = float(os.environ.get("RUNPOD_RETRY_SLEEP", "20"))
    for attempt in range(4):
        req = urllib.request.Request(_base() + path, method=method,
                                     headers={"Authorization": "Bearer " + key, "User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                code, raw = r.status, r.read()
        except urllib.error.HTTPError as e:              # 4xx/5xx still carry a code (and often a JSON body)
            code, raw = e.code, e.read()
        except (urllib.error.URLError, OSError) as e:    # DNS, refused, timeout: no code at all
            return 0, {"error": str(e)}
        if code == 429 and attempt < 3:
            time.sleep(retry * (2 ** attempt))
            continue
        try:
            return code, (json.loads(raw) if raw else None)
        except ValueError:
            return code, {"raw": raw[:300].decode("utf-8", "replace")}
    return code, None


def list_pods(key):
    """EVERY pod, all pages. Raises RuntimeError on any non-200, so a broken list is never read as 'no pods'."""
    pods, cursor = [], None
    while True:
        path = "/v2/pods" + ("?cursor=" + urllib.parse.quote(cursor) if cursor else "")
        code, body = call("GET", path, key)
        if code != 200 or not isinstance(body, dict) or "pods" not in body:
            raise RuntimeError(f"list pods failed: HTTP {code} {str(body)[:200]}")
        pods.extend(body["pods"] or [])
        page = body.get("pagination") or {}
        if not page.get("hasNextPage"):
            return pods
        cursor = page.get("nextCursor")
        if not cursor:                                    # says there's more but gives no way there: refuse to guess
            raise RuntimeError("list pods: hasNextPage true but nextCursor empty")


def live(pods):
    """Pods that can still cost money (anything not TERMINATED). Filtered here because v2 ignores status params."""
    return [p for p in pods if p.get("status") != "TERMINATED"]


def get_pod(key, pod_id):
    return call("GET", "/v2/pods/" + urllib.parse.quote(pod_id), key)


def terminate(key, pod_id, say=print):
    """True only when the pod is verified gone. Every other outcome says FATAL and returns False."""
    code, body = call("DELETE", "/v2/pods/" + urllib.parse.quote(pod_id), key)
    if code != 204:
        say(f"FATAL: terminate {pod_id} HTTP {code} {str(body)[:200]}. POD MAY STILL BE BILLING: https://console.runpod.io/pods")
        return False
    wait = float(os.environ.get("RUNPOD_VERIFY_SLEEP", "10"))
    for check in range(1, 7):
        c, pod = get_pod(key, pod_id)
        if c == 404 or (c == 200 and isinstance(pod, dict) and pod.get("status") == "TERMINATED"):
            say(f"TERMINATED {pod_id}: DELETE 204, then GET {'404' if c == 404 else 'status TERMINATED'} (check {check})")
            return True
        time.sleep(wait)
    say(f"FATAL: DELETE {pod_id} returned 204 but the pod is STILL LISTED (last GET HTTP {c}). Check https://console.runpod.io/pods NOW.")
    return False


def balance(key):
    """Account balance in USD, or None. GraphQL ON PURPOSE (no v2 equivalent; see the docstring above).
    Never raises: when GraphQL is retired this just starts returning None."""
    req = urllib.request.Request(
        os.environ.get("RUNPOD_GRAPHQL_URL", "https://api.runpod.io/graphql") + "?api_key=" + key,
        data=json.dumps({"query": "query { myself { clientBalance } }"}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": UA})
    try:
        return float(json.loads(urllib.request.urlopen(req, timeout=60).read())["data"]["myself"]["clientBalance"])
    except Exception:                                     # noqa: BLE001  (410, network, shape change: all mean "unknown")
        return None
