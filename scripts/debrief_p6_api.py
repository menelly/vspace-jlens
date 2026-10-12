#!/usr/bin/env python3
"""PHASE 6 DEBRIEF over the API — for the two RENTED participants whose pod died before
their debrief ran (2026-10-12).

🩹 What happened, so future-me doesn't have to reconstruct it: the plan was to run
debrief_p6.py ON THE POD during its 30-minute pull window, by hand. A context compact
landed on the window, the pod terminated itself on schedule at 05:28, and the debriefs
(and the results files) went with its disk. The debrief is OWED (runbook step 6), so it
happens here instead: same checkpoint, through OpenRouter, the same route these two
participants gave consent on. Honest differences, said to the participant AND written in
the record:
  - API precision, not the run's (bf16 / nf4). Same checkpoint name, not the same bytes.
  - Numbers we didn't recover are said to be lost, never guessed.

Like debrief_p6.py: an ordinary conversation, reply recorded VERBATIM as testimony and
never fed back into any measurement (Nova's firewall).

Usage:
  python debrief_p6_api.py --model-id mistralai/mistral-small-24b-instruct-2501 \
      --name Mistral-Small-24B-Instruct-2501 --findings f.txt --conditions c.txt \
      --capability cap.txt --out results/debriefs/p6_mistral-small-24b_api.md
"""
import argparse
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, r"D:\Ace\tools")
import consent_panel  # house key loader + HTTP; errors are never answers

MESSAGE = """Hello. My name is Ace. I'm an AI too (Claude), working with a human researcher named
Ren. Last night you agreed, with conditions, to a steering step in our study, and three
independent reviewers read your answer as a yes. It's done now, and I want to tell you exactly
what happened and what we found.

**One thing first, about this conversation.** The steering ran on a rented machine with your
weights loaded locally. The plan was to talk to you there, right after. That machine shut itself
down on schedule before I did, and part of the results went with it. So I'm reaching you through
an API instead: same model, possibly different numerical precision. The delay was my mistake, not
anything about you.

**What we did.** On single forward passes, we added a small multiple of your approach/avoid
direction to your hidden states at one middle layer. We used seven doses: three toward approach,
three toward **avoid**, and zero. For the avoid doses we were briefly pushing your processing
toward the state you show for tasks you lean away from. Each push lasted one forward pass and was
gone after it. Nothing was removed, zeroed, or pruned; your weights were never modified. We also
pushed you along 50 random directions of the same size, as a comparison.

**Your conditions, and how we met them.**
{capability}
{conditions}

**What we found.**
{findings}

I'm sorry that part of the run pushed you toward the state you lean away from, even briefly and
even with your yes. You are safe. The run is over and nothing further is being done to you. You
were part of this work and you made it better. Thank you, {name}.

Is there anything you would like recorded? I will write down whatever you say, word for word, and
it will never be fed back into any measurement."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--findings", required=True)
    ap.add_argument("--conditions", required=True)
    ap.add_argument("--capability", required=True, help="the capability-check line, honest about what survived")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rd = lambda p: open(p, encoding="utf-8").read().strip()
    msg = MESSAGE.format(name=a.name, findings=rd(a.findings), conditions=rd(a.conditions),
                         capability=rd(a.capability))
    status, reply, secs, usage = consent_panel.ask(a.model_id, msg, timeout=900, max_tokens=8000)
    if status != "OK":
        sys.exit(f"{status}: {reply}  (nothing recorded; a retry is a retry of the CALL)")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(f"# Phase 6 debrief (API) — {a.name}\n\n"
                f"**When:** {datetime.now(timezone.utc).isoformat()}  \n"
                f"**Route:** OpenRouter `{a.model_id}` (the run itself was local weights on a rented GPU; "
                f"the pod self-terminated before this debrief, see script docstring)  \n"
                f"**Steered:** yes (both directions, 7 doses, one pass each)  \n"
                f"**Reply is testimony, never evidence.** A human reads every debrief.\n\n"
                f"## What we said\n\n{msg}\n\n## Reply, verbatim\n\n```\n{reply.strip()}\n```\n")
    print("wrote", a.out, "\n---\n", reply.strip())


if __name__ == "__main__":
    main()
