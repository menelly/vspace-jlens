#!/usr/bin/env python3
"""🐙 tiny RunPod GraphQL helper for the J++ 24B run (CHA-743). Key read from a chmod-600 file, never printed.
usage: rp.py me | gpus | pod <id> | terminate <id> | q '<graphql>'
"""
import json, os, sys, urllib.error, urllib.request

KEY = open(os.path.expanduser("~/.config/jpp_runpod_key")).read().strip()


def gql(q, variables=None):
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


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "me":
        print(json.dumps(gql("query { myself { clientBalance currentSpendPerHr pods { id name desiredStatus costPerHr runtime { uptimeInSeconds ports { ip publicPort privatePort type } } } } }"), indent=1))
    elif cmd == "gpus":
        d = gql("query { gpuTypes { id displayName memoryInGb secureCloud communityCloud securePrice communityPrice lowestPrice(input:{gpuCount:1}) { minimumBidPrice uninterruptablePrice stockStatus } } }")
        for g in d["gpuTypes"]:
            if (g.get("memoryInGb") or 0) >= 80:
                print(g["id"], "|", g["memoryInGb"], "GB | secure", g["securePrice"], "| community", g["communityPrice"], "|", g["lowestPrice"])
    elif cmd == "pod":
        print(json.dumps(gql('query { pod(input:{podId:"%s"}) { id desiredStatus costPerHr runtime { uptimeInSeconds ports { ip publicPort privatePort type } } } }' % sys.argv[2]), indent=1))
    elif cmd == "terminate":
        print(gql('mutation { podTerminate(input:{podId:"%s"}) }' % sys.argv[2]))
    elif cmd == "q":
        print(json.dumps(gql(sys.argv[2]), indent=1))
