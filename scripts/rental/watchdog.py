#!/usr/bin/env python3
"""💸 RunPod money watchdog — runs on the Consortium, NOT on the pod, so it outlives everything.

Ren loaded $45; the hard cap is $35. Every POLL seconds:
  - if SPENT reaches SPEND_CAP, or the balance is at or below FLOOR, TERMINATE EVERY POD (and keep at it)
  - if a pod has run longer than MAX_H hours, terminate it
  - when no pods are left after we've seen one, exit (job done)
The key is read from a chmod-600 file that gets deleted after the run. Never printed.

v3 (2026-11-14, CHA-798): pods and kills moved to REST v2 via runpod_v2.py, because GraphQL returns 410 in
"early 2027". The BALANCE has no v2 equivalent (Runpod's migration guide says keep using GraphQL for it), so:
  🅰️ GraphQL meter (as before): spend = sum of balance DECREASES between polls; deposits ignored.
  🅱️ v2 meter (new, independent): spend += each live pod's `cost` ($/h) x hours since the last poll.
  SPENT = the LARGER of the two, so whichever sees more money going out wins (fails toward killing).
  When GraphQL is gone, balance() returns None, 🅰️ stops moving and the FLOOR check is skipped (said in the
  log every poll), but the 🅱️ meter and SPEND_CAP keep working. 🅱️ overestimates a little on purpose: it
  counts every pod that isn't TERMINATED, including stopped ones, at their full rate.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runpod_v2 as rp                                    # noqa: E402

FLOOR = float(sys.argv[1]) if len(sys.argv) > 1 else 10.50
MAX_H = float(sys.argv[2]) if len(sys.argv) > 2 else 7.0
# v2 (2026-10-12 02:2x): a BALANCE is not a SPEND METER. At 02:14:53 exactly +$25.00 appeared mid-run
# (top-up or auto-reload; not ours to spend). So we meter spend as the sum of DECREASES between polls,
# ignore increases, and kill at SPEND_CAP no matter what the balance says.
SPEND_CAP = float(sys.argv[3]) if len(sys.argv) > 3 else 35.0
spent_gql = spent_v2 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0   # already spent before this watchdog started
POLL = float(os.environ.get("WATCHDOG_POLL", "120"))
KEY = open(os.path.expanduser(os.environ.get("WATCHDOG_KEY_FILE", "~/.config/p6_runpod_key"))).read().strip()


def stamp():
    return time.strftime("%H:%M:%S")


def kill(pid, why):
    print(stamp(), "TERMINATE", pid, why, flush=True)
    rp.terminate(KEY, pid, say=lambda m: print(stamp(), m, flush=True))


seen, t0, last_bal, last_poll, last_pods = False, {}, None, None, []
while True:
    try:
        pods = rp.live(rp.list_pods(KEY))
    except Exception as e:                                   # noqa: BLE001
        print(stamp(), "poll failed (pods NOT checked this round):", e, flush=True)
        time.sleep(POLL)
        continue
    now = time.time()
    if last_poll is not None:                                # 🅱️ bill the interval at the rates we last saw
        spent_v2 += sum(float(p.get("cost") or 0) for p in last_pods) * (now - last_poll) / 3600
    last_poll, last_pods = now, pods

    bal = rp.balance(KEY)                                    # 🅰️ GraphQL-only; None once it's retired
    if bal is not None and last_bal is not None and bal < last_bal:
        spent_gql += last_bal - bal
    elif bal is not None and last_bal is not None and bal > last_bal:
        print(stamp(), f"DEPOSIT seen: +${bal - last_bal:.2f} (not counted as budget)", flush=True)
    if bal is not None:
        last_bal = bal
    spent = max(spent_gql, spent_v2)
    floor_hit = bal is not None and bal <= FLOOR
    rate = sum(float(p.get("cost") or 0) for p in pods)
    print(stamp(), f"balance={'$%.2f' % bal if bal is not None else 'UNKNOWN (GraphQL gone? floor check OFF, cap still on)'} "
                   f"SPENT=${spent:.2f}/{SPEND_CAP:.0f} (balance-meter ${spent_gql:.2f}, v2-meter ${spent_v2:.2f}) "
                   f"spend/hr=${rate:.2f} pods={len(pods)}", flush=True)

    for p in pods:
        seen = True
        t0.setdefault(p["id"], now)
        if floor_hit or spent >= SPEND_CAP:
            kill(p["id"], f"spent ${spent:.2f} (cap ${SPEND_CAP:.0f}) / balance {bal}")
        elif (now - t0[p["id"]]) / 3600 > MAX_H:
            kill(p["id"], f"ran > {MAX_H} h")
    if (floor_hit or spent >= SPEND_CAP) and pods:
        time.sleep(30)
        continue
    if seen and not pods:
        print(stamp(), f"no pods left; final balance {bal}. watchdog exiting.", flush=True)
        break
    time.sleep(POLL)
