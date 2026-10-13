#!/usr/bin/env python3
"""💸🐙 J++ 24B supervisor — runs on the CONSORTIUM (nohup setsid), never on the pod, never in a chat.

D2 lost a run because the copy depended on a chat session being awake. This process does the copy itself:
every POLL seconds it
  1. meters SPEND (sum of balance DECREASES since launch; deposits ignored) -> at SPEND_KILL, terminate.
  2. projects total spend from the MEASURED seconds/prompt in the pod's log (amendment A1 money stop)
     -> projection > PROJ_STOP: write STOPPED_FOR_COST, pull logs, terminate. No partial verdict.
  3. every PULL_EVERY s, pulls the small files (logs, csv, json) so nothing small can be lost.
  4. on PIPELINE_FINISHED / PIPELINE_FAILED: pulls EVERYTHING in /root/run, verifies every byte count
     against the pod's own listing, drops PULLED on the pod, terminates it, confirms pods=[] and exits.
  5. if the pod is unreachable for UNREACH_MIN minutes, or its log goes silent for STALL_MIN, terminate.
The key is read from a chmod-600 file and never printed. Writes status.json for whoever checks in.

usage: supervise_24b.py POD_ID SSH_IP SSH_PORT START_BALANCE
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rp import gql  # noqa: E402

POD, IP, PORT, START_BAL = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
SPEND_KILL = 19.50   # Ren's hard cap is $20
PROJ_STOP = 18.50    # amendment A1
OVERHEAD_H = 0.5     # merges + weight fit + evals + pull, after the last fitted prompt (estimate, generous)
POLL, PULL_EVERY, UNREACH_MIN, STALL_MIN = 60, 600, 20, 50
FIT_PROMPTS = 64
LOCAL = Path("/mnt/nursery/jpp_runs/cha743_24b")   # cold storage has room; arcana is 91% full
LOCAL.mkdir(parents=True, exist_ok=True)
STATUS = Path(__file__).parent / "status.json"
SSH = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "ConnectTimeout=20",
       "-o", "LogLevel=ERROR", "-p", PORT, f"root@{IP}"]
t_launch = time.time()


def say(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def ssh(cmd, timeout=120):
    return subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=timeout)


def pull(full):
    """tar stream pod:/root/run -> LOCAL. full=False skips *.pt and shard artifacts."""
    ex = "" if full else "--exclude='*.pt' --exclude=./artifacts"
    p1 = subprocess.Popen(SSH + [f"cd /root/run && tar -cf - {ex} ."], stdout=subprocess.PIPE)
    p2 = subprocess.run(["tar", "-C", str(LOCAL), "-xf", "-"], stdin=p1.stdout, timeout=3600)
    p1.wait(timeout=60)
    return p1.returncode == 0 and p2.returncode == 0


def verify():
    """every file on the pod has the same byte count here: presence is a property of BYTES."""
    r = ssh("cd /root/run && find . -type f -printf '%s %p\\n'")
    if r.returncode != 0:
        return False, "could not list pod"
    bad = []
    for line in r.stdout.strip().splitlines():
        size, path = line.split(" ", 1)
        lp = LOCAL / path
        if path.endswith("pod.log"):
            continue  # still being appended while we copy
        if not lp.exists() or lp.stat().st_size != int(size):
            bad.append(path)
    return (not bad), (f"{len(r.stdout.splitlines())} files verified" if not bad else f"MISMATCH {bad[:5]}")


def terminate(why):
    say("TERMINATE", POD, why)
    for _ in range(5):
        try:
            gql('mutation { podTerminate(input:{podId:"%s"}) }' % POD)
            pods = gql("query { myself { pods { id } } }")["myself"]["pods"] or []
            if not any(p["id"] == POD for p in pods):
                say("pod gone; pods now:", [p["id"] for p in pods])
                return True
        except Exception as e:  # noqa: BLE001
            say("terminate attempt failed:", e)
        time.sleep(20)
    say("!!! could not confirm termination")
    return False


def finish(state, why):
    me = gql("query { myself { clientBalance } }")["myself"]
    STATUS.write_text(json.dumps({"state": state, "why": why, "final_balance": me["clientBalance"],
                                  "spent_by_balance": round(START_BAL - me["clientBalance"], 2),
                                  "pod_hours": round((time.time() - t_launch) / 3600, 3),
                                  "at": time.strftime("%Y-%m-%d %H:%M:%S %Z")}, indent=2))
    say("FINAL", STATUS.read_text())
    sys.exit(0)


last_bal, spent, last_pull, unreach_since = None, 0.0, 0.0, None
last_log_size, last_log_change = -1, time.time()
rate = None
while True:
    try:
        me = gql("query { myself { clientBalance currentSpendPerHr pods { id costPerHr } } }")["myself"]
        bal = me["clientBalance"]
        if last_bal is None:
            spent = max(0.0, START_BAL - bal)
        elif bal < last_bal:
            spent += last_bal - bal
        elif bal > last_bal:
            say(f"DEPOSIT seen +${bal - last_bal:.2f} (not counted as budget)")
        last_bal = bal
        mine = [p for p in (me["pods"] or []) if p["id"] == POD]
        if mine:
            rate = mine[0]["costPerHr"]
        elif time.time() - t_launch > 300:
            say("pod no longer exists (self-terminated?) — pulling is impossible now")
            finish("POD_GONE", "pod disappeared before supervisor saw a finish marker")
    except Exception as e:  # noqa: BLE001
        say("api poll failed:", e)
        time.sleep(POLL)
        continue

    hours = (time.time() - t_launch) / 3600
    # spend by the clock too: the balance updates in lumps, the clock does not
    spent_clock = hours * (rate or 0)
    spent_now = max(spent, spent_clock)
    if spent_now >= SPEND_KILL:
        try:
            pull(False)
        except Exception:  # noqa: BLE001
            pass
        terminate(f"spend ${spent_now:.2f} >= ${SPEND_KILL}")
        finish("KILLED_SPEND_CAP", f"spend ${spent_now:.2f}")

    # ---- look at the pod
    try:
        r = ssh("cat /root/run/pod.log 2>/dev/null | grep -a -E 'prompt [0-9]+/64|=== |FAILED|OOM' | tail -400; "
                "echo __M__; ls /root/run; echo __S__; stat -c %s /root/run/pod.log 2>/dev/null", timeout=60)
        ok = r.returncode == 0 and "__M__" in r.stdout
    except Exception:  # noqa: BLE001
        ok = False
    if not ok:
        unreach_since = unreach_since or time.time()
        mins = (time.time() - unreach_since) / 60
        say(f"pod unreachable {mins:.0f} min  spent~${spent_now:.2f}")
        if mins > UNREACH_MIN and hours > 0.4:
            terminate(f"unreachable {mins:.0f} min")
            finish("KILLED_UNREACHABLE", "ssh dead")
        time.sleep(POLL)
        continue
    unreach_since = None
    body, rest = r.stdout.split("__M__", 1)
    files, size = rest.split("__S__", 1)
    files = files.split()
    size = int(size.strip() or 0)
    if size != last_log_size:
        last_log_size, last_log_change = size, time.time()

    # ---- measured-rate projection (A1 money stop)
    shards = body.split("=== shard_")
    secs, done_by_shard = [], []
    for chunk in shards[1:]:
        ps = [(int(m.group(1)), int(m.group(2))) for m in re.finditer(r"prompt (\d+)/64\s+seq_len=\d+\s+num_source_positions=\d+\s+(\d+)s", chunk)]
        done_by_shard.append(max([p for p, _ in ps], default=0))
        secs += [s for p, s in ps if p > 1]   # prompt 1 carries warm-up
    proj = None
    if len(secs) >= 3 and rate:
        per = sum(secs[-12:]) / len(secs[-12:])
        n_shards_started = len(done_by_shard)
        remaining = (FIT_PROMPTS - done_by_shard[-1]) + FIT_PROMPTS * (2 - n_shards_started)
        proj_h = hours + remaining * per / 3600 + OVERHEAD_H
        proj = proj_h * rate
        if proj > PROJ_STOP and "PIPELINE_FINISHED" not in files:
            (LOCAL / "STOPPED_FOR_COST.txt").write_text(
                f"projected ${proj:.2f} > ${PROJ_STOP} at {per:.0f} s/prompt, ${rate}/h, {hours:.2f} h elapsed\n")
            pull(False)
            terminate(f"projected ${proj:.2f} > ${PROJ_STOP}")
            finish("STOPPED_FOR_COST", f"projected ${proj:.2f} at {per:.0f} s/prompt")

    STATUS.write_text(json.dumps({"state": "running", "hours": round(hours, 3), "rate_per_h": rate,
                                  "spent_balance": round(spent, 2), "spent_clock": round(spent_clock, 2),
                                  "projected_total": round(proj, 2) if proj else None,
                                  "prompts_done_by_shard": done_by_shard,
                                  "s_per_prompt_recent": round(sum(secs[-12:]) / len(secs[-12:]), 1) if secs else None,
                                  "markers": [f for f in files if f.isupper() or f.startswith("PIPELINE")],
                                  "at": time.strftime("%H:%M:%S")}, indent=1))
    say(f"h={hours:.2f} ${rate}/h spent~${spent_now:.2f} proj={proj and round(proj, 2)} shards={done_by_shard}")

    # ---- finish / fail
    if "PIPELINE_FINISHED" in files or "PIPELINE_FAILED" in files:
        state = "FINISHED" if "PIPELINE_FINISHED" in files else "FAILED"
        say("pod says", state, "-> full pull")
        okv, msg = False, ""
        for attempt in range(3):
            try:
                pull(True)
                okv, msg = verify()
            except Exception as e:  # noqa: BLE001
                msg = str(e)
            say("pull attempt", attempt + 1, okv, msg)
            if okv:
                break
        if okv:
            ssh("touch /root/run/PULLED")
            terminate(f"{state}, copy verified ({msg})")
            finish(state, msg)
        say("!!! copy did NOT verify after 3 tries; pod keeps its own deadline backstop; terminating anyway to stop spend")
        terminate("copy unverified after 3 tries")
        finish(state + "_COPY_UNVERIFIED", msg)

    if time.time() - last_log_change > STALL_MIN * 60:
        pull(False)
        terminate(f"log silent {STALL_MIN} min")
        finish("KILLED_STALLED", "no log growth")

    if time.time() - last_pull > PULL_EVERY:
        try:
            pull(False)
            last_pull = time.time()
        except Exception as e:  # noqa: BLE001
            say("small pull failed:", e)
    time.sleep(POLL)
