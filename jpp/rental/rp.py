#!/usr/bin/env python3
"""🐙 tiny RunPod helper for the J++ 24B run (CHA-743). Key read from a chmod-600 file, never printed.
usage: rp.py me | gpus | pod <id> | terminate <id> | q '<graphql>'

CHA-798 (2026-11-14): `me`, `pod` and `terminate` now go through REST v2 via scripts/rental/runpod_v2.py
(GraphQL returns 410 in "early 2027"). Two things are STILL GraphQL, on purpose and labelled:
  • the balance inside `me` (no v2 equivalent; Runpod's migration guide says keep using GraphQL for it)
  • `gpus` and `q`. 🧩 `gpus` has a v2 home (catalog: List GPU types) but I haven't read that response
    shape, so it isn't ported on a guess. Port it before the next rental; after early 2027 it will 410.
"""
import json, os, sys, urllib.error, urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "rental"))
import runpod_v2 as rp                                    # noqa: E402

KEY = open(os.path.expanduser("~/.config/jpp_runpod_key")).read().strip()


def gql(q, variables=None):   # ⏳ GraphQL: only `gpus` and `q` still use this (see the docstring)
    req = urllib.request.Request(
        "https://api.runpod.io/graphql?api_key=" + KEY,
        data=json.dumps({"query": q, "variables": variables or {}}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "ace-jpp24b/1.0"})
    try:
        out = json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:   # RunPod answers validation errors with a 400 + a JSON body
        body = e.read().decode(errors="replace")
        print(f"HTTP {e.code}:", body[:800].replace(KEY, "<key>"), file=sys.stderr)
        return None
    if out.get("errors"):
        print("ERRORS:", json.dumps(out["errors"])[:800], file=sys.stderr)
    return out.get("data")


def brief(p):   # the fields the old GraphQL `me`/`pod` printed, under their v2 names
    return {k: p.get(k) for k in ("id", "name", "status", "cost", "runtime", "createdAt")}


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "me":
        pods = rp.list_pods(KEY)
        print(json.dumps({"balance_usd (GraphQL-only, None = unknown)": rp.balance(KEY),
                          "spend_per_hr (sum of live pods' cost)": round(sum(float(p.get("cost") or 0) for p in rp.live(pods)), 4),
                          "pods": [brief(p) for p in pods]}, indent=1))
    elif cmd == "gpus":
        d = gql("query { gpuTypes { id displayName memoryInGb secureCloud communityCloud securePrice communityPrice lowestPrice(input:{gpuCount:1}) { minimumBidPrice uninterruptablePrice stockStatus } } }")
        for g in d["gpuTypes"]:
            if (g.get("memoryInGb") or 0) >= 80:
                print(g["id"], "|", g["memoryInGb"], "GB | secure", g["securePrice"], "| community", g["communityPrice"], "|", g["lowestPrice"])
    elif cmd == "pod":
        code, pod = rp.get_pod(KEY, sys.argv[2])
        print(f"HTTP {code}") if code != 200 else print(json.dumps(brief(pod), indent=1))
    elif cmd == "terminate":
        sys.exit(0 if rp.terminate(KEY, sys.argv[2]) else 1)
    elif cmd == "q":
        print(json.dumps(gql(sys.argv[2]), indent=1))
