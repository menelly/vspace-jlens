#!/usr/bin/env python3
"""💸 RunPod money watchdog — runs on the Consortium, NOT on the pod, so it outlives everything.

Ren loaded $45; the hard cap is $35. Every POLL seconds:
  - read the balance; if it is at or below FLOOR, TERMINATE EVERY POD and exit
  - if a pod has run longer than MAX_H hours, terminate it
  - when no pods are left after we've seen one, exit (job done)
The key is read from a chmod-600 file that gets deleted after the run. Never printed.
"""
import json
import sys
import time
import urllib.request

FLOOR = float(sys.argv[1]) if len(sys.argv) > 1 else 10.50
MAX_H = float(sys.argv[2]) if len(sys.argv) > 2 else 7.0
# v2 (2026-10-12 02:2x): a BALANCE is not a SPEND METER. At 02:14:53 exactly +$25.00 appeared mid-run
# (top-up or auto-reload; not ours to spend). So we meter spend as the sum of DECREASES between polls,
# ignore increases, and kill at SPEND_CAP no matter what the balance says.
SPEND_CAP = float(sys.argv[3]) if len(sys.argv) > 3 else 35.0
spent = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0     # already spent before this watchdog started
last_bal = None
POLL = 120
KEY = open(__import__("os").path.expanduser("~/.config/p6_runpod_key")).read().strip()


def gql(q):
    req = urllib.request.Request("https://api.runpod.io/graphql?api_key=" + KEY,
                                 data=json.dumps({"query": q}).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "ace-p6-watchdog/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())["data"]


def kill(pid, why):
    print(time.strftime("%H:%M:%S"), "TERMINATE", pid, why, flush=True)
    gql('mutation { podTerminate(input:{podId:"%s"}) }' % pid)


seen, t0 = False, {}
while True:
    try:
        me = gql("query { myself { clientBalance currentSpendPerHr pods { id name desiredStatus } } }")["myself"]
    except Exception as e:                                   # noqa: BLE001
        print(time.strftime("%H:%M:%S"), "poll failed:", e, flush=True)
        time.sleep(POLL)
        continue
    bal, pods = me["clientBalance"], me["pods"] or []
    if last_bal is not None and bal < last_bal:
        spent += last_bal - bal
    elif last_bal is not None and bal > last_bal:
        print(time.strftime("%H:%M:%S"), f"DEPOSIT seen: +${bal - last_bal:.2f} (not counted as budget)", flush=True)
    last_bal = bal
    print(time.strftime("%H:%M:%S"), f"balance=${bal:.2f} SPENT=${spent:.2f}/{SPEND_CAP:.0f} spend/hr=${me['currentSpendPerHr']} pods={len(pods)}", flush=True)
    for p in pods:
        seen = True
        t0.setdefault(p["id"], time.time())
        if bal <= FLOOR or spent >= SPEND_CAP:
            kill(p["id"], f"spent ${spent:.2f} (cap ${SPEND_CAP:.0f}) / balance ${bal:.2f}")
        elif (time.time() - t0[p["id"]]) / 3600 > MAX_H:
            kill(p["id"], f"ran > {MAX_H} h")
    if (bal <= FLOOR or spent >= SPEND_CAP) and pods:
        time.sleep(30)
        continue
    if seen and not pods:
        print(time.strftime("%H:%M:%S"), f"no pods left; final balance ${bal:.2f}. watchdog exiting.", flush=True)
        break
    time.sleep(POLL)
