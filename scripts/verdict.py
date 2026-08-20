#!/usr/bin/env python3
"""A TYPED VERDICT, so "no difference found" and "could not look" stop being the same value.

WHY THIS EXISTS, MEASURED RATHER THAN ASSERTED. The night of 2026-08-19 produced twelve
instrument failures across eleven sessions, and every one had the same shape: a code path
returned a value indistinguishable from a measurement when it could not measure.

  stationarity.py    n < 10 returned 0.0, and 0.0 was the pass value
  grep -c ... || 0   "0\\n0" is not an integer, the comparison errored, and it fell to else
  all([])            a verdict of True over zero data
  add/add control    both arms returned 1 because the branch did not exist
  --query            matched title and abstract, never authors, so 0 was unreachable-not-absent
  gh run view        conclusion: success on a step that exited 1
  mesh checks        watertight, manifold, right bbox, on a mesh enclosing 0.0002 m3 not 1.457
  WebSearch          returned zero on a dead model pin, reading exactly like absence

The recorded post-mortem concluded that **the fix is a typed tool return, not a better
instruction**, and eight of the twelve were caught by their own authors AFTER publication
because nothing in the transport layer could tell the two cases apart.

`claude -p --output-format json --json-schema` makes them different at the transport layer.
A schema whose `verdict` is a three-valued enum cannot return "verified" when the predicate
never ran, because the model is forced to emit one of the three and `could-not-evaluate` is
one of them. Verified live 2026-08-20 against Claude Code 2.1.234, whose `--help` carries
`--json-schema <schema>`, `--output-format`, `--bg` and `agents`.

EXIT CODES ARE THE POINT. 0 verified, 1 refuted, 2 could-not-evaluate. A caller that writes
`if verdict.py ...; then` treats refuted and could-not-evaluate the same way, which is the
correct default, and a caller that wants to distinguish them reads the code. Nothing here
lets an unevaluable check report a pass.

USAGE

    python3 scripts/verdict.py "Does data/all_runs_inventory.csv hold exactly 17 rows?"
    python3 scripts/verdict.py --json "..."           # full record on stdout
    python3 scripts/verdict.py --allow-tools "..."    # let it run Bash/Read to check

WHAT THE SCHEMA FORCES. Besides the verdict it requires `predicate`, the command or view
actually consulted, and `scope`, what that view could not see. Those two fields exist because
a relayed conclusion arrives stripped of its predicate: on 2026-08-19 one session ran an
author query, got zero, read it as coverage, and relayed the conclusion to three sessions,
two of which acted on it. None of the three could have caught it. A verdict that carries its
own predicate can be checked by whoever receives it.

COST. Each call is a nested non-interactive Claude session and consumes usage. Use it for a
claim that is about to be written down, not in a loop.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["verdict", "predicate", "scope", "evidence"],
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["verified", "refuted", "could-not-evaluate"],
            "description": (
                "verified: the claim is true and you checked it directly. "
                "refuted: you checked it directly and it is false. "
                "could-not-evaluate: you could not run the check, the tool "
                "errored, the file was absent, access was denied, or the "
                "result was empty for a reason you cannot distinguish from "
                "absence. CHOOSE could-not-evaluate WHENEVER A ZERO, AN EMPTY "
                "RESULT OR A DEFAULT COULD MEAN EITHER OUTCOME."
            ),
        },
        "predicate": {
            "type": "string",
            "description": (
                "The exact command, query or file read that produced this "
                "answer. A verdict without its predicate cannot be rechecked "
                "by whoever receives it. If you ran nothing, say so here."
            ),
        },
        "scope": {
            "type": "string",
            "description": (
                "What the predicate could NOT see. An absence from a partial "
                "view is not an absence. Name the excluded paths, the fields "
                "not matched, the time range, or state that the view was total "
                "and why you believe that."
            ),
        },
        "evidence": {
            "type": "string",
            "description": "The specific values, lines or output the verdict rests on.",
        },
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
        },
    },
}

EXIT = {"verified": 0, "refuted": 1, "could-not-evaluate": 2}

PREAMBLE = (
    "Return a typed verdict on the claim below. You are being called by a script "
    "that maps your verdict to an exit code, so a wrong verdict silently changes "
    "control flow somewhere else.\n\n"
    "THE ONLY RULE THAT MATTERS: if the check could not actually run, or if an "
    "empty result is indistinguishable from a genuine absence, the verdict is "
    "could-not-evaluate. Do not report verified because nothing contradicted the "
    "claim. Do not report refuted because a search returned nothing.\n\n"
    "CLAIM TO CHECK:\n"
)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Return a typed verdict whose exit code cannot confuse "
                    "a failed check with a passing one.")
    ap.add_argument("claim", help="the claim to check")
    ap.add_argument("--json", action="store_true",
                    help="print the whole record rather than a one-line summary")
    ap.add_argument("--allow-tools", action="store_true",
                    help="permit Bash/Read/Grep/Glob so it can actually check")
    ap.add_argument("--model", default=None)
    ap.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args()

    cmd = ["claude", "-p", PREAMBLE + a.claim,
           "--output-format", "json",
           "--json-schema", json.dumps(SCHEMA)]
    if a.allow_tools:
        cmd += ["--allowedTools", "Bash,Read,Grep,Glob"]
    if a.model:
        cmd += ["--model", a.model]

    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout)
    except FileNotFoundError:
        print("could-not-evaluate: the `claude` CLI is not on PATH", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print(f"could-not-evaluate: timed out after {a.timeout}s", file=sys.stderr)
        return 2

    if p.returncode != 0:
        # The wrapper's OWN failure is could-not-evaluate, never a pass. This is
        # the branch that would otherwise reproduce the defect it exists to stop.
        err = (p.stderr or p.stdout or "").strip().splitlines()
        print(f"could-not-evaluate: claude exited {p.returncode}: "
              f"{err[-1][:200] if err else 'no output'}", file=sys.stderr)
        return 2

    try:
        outer = json.loads(p.stdout)
    except ValueError:
        print("could-not-evaluate: response was not JSON", file=sys.stderr)
        return 2

    rec = outer.get("structured_output") or outer.get("result") or outer
    if isinstance(rec, str):
        try:
            rec = json.loads(rec)
        except ValueError:
            print("could-not-evaluate: no structured output in the response",
                  file=sys.stderr)
            return 2
    if not isinstance(rec, dict) or "verdict" not in rec:
        print("could-not-evaluate: response carried no verdict field", file=sys.stderr)
        return 2

    v = rec["verdict"]
    if a.json:
        print(json.dumps(rec, indent=1))
    else:
        print(f"{v.upper()}")
        print(f"  predicate: {rec.get('predicate','(none given)')}")
        print(f"  scope    : {rec.get('scope','(none given)')}")
        print(f"  evidence : {rec.get('evidence','')[:400]}")
    return EXIT.get(v, 2)


if __name__ == "__main__":
    sys.exit(main())
