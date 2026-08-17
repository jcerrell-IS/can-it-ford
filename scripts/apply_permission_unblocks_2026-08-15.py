#!/usr/bin/env python3
"""Apply the project-level permission unblocks found on 2026-08-15.

NOT RUN AUTOMATICALLY, on purpose. `.claude/settings.json` had uncommitted
changes from a CONCURRENT session at the time this was written (a
`commit_autoapprove.py` PreToolUse hook, plus three new MCP servers). Editing a
file another live session is mid-work in is the exact 2026-08-07 failure mode:
two sessions committed each other's work unreviewed. So this is staged for you to
run once that session's work is committed.

Run it:
    python3 scripts/apply_permission_unblocks_2026-08-15.py --dry-run
    python3 scripts/apply_permission_unblocks_2026-08-15.py --apply

It merges. It preserves every existing key, hook and MCP entry, and writes a
timestamped backup first.

WHAT IT CHANGES AND WHY
-----------------------
1. `disableClaudeAiConnectors: true -> false`
   This is the single biggest self-inflicted blocker found. It disables the
   claude.ai connectors, which is why Weights and Biases, Hugging Face and the
   rest read as unavailable. Nothing about it is a safety control.

2. Removes three deny rules whose targets no longer exist, so they are dead
   weight rather than protection:
     Read(reference_data/vehicle_data_master_reference_2026-07-21.json.OLD-4906B)
     Read(data/track1_sweep_v3/**)
     Read(//Users/josie/can-it-ford/can-it-ford/**)
   The last one also carries a malformed double-slash path, and the nested
   duplicate it guarded was confirmed gone on 2026-08-12.

3. Removes `Read(designsafe-staging/**)`.
   Evidence-based: `designsafe-staging/` is the PUBLICATION-BOUND tree, and on
   2026-08-15 a one-character verdict-rule fork was found inside it
   (`make_phase_space.py` carrying `h <= 0.60` against `h < 0.60`, on a boundary
   where 4 of 70 scenarios sit). Being unable to Read the tree that ships is a
   handicap, not a guard. It was only caught via a Bash grep, which the deny
   rule does not cover anyway, so the rule blocked review without blocking risk.

WHAT IT DELIBERATELY DOES NOT CHANGE
------------------------------------
`Bash(git add -A|--all|.)` and `Bash(git commit -a|--all)` stay denied. On
2026-08-07 two sessions in this tree committed each other's uncommitted edits
inside 0797b08 and 3470ff9 without either knowing. A concurrent session was live
while this file was written. This is the one rule most worth keeping.

`Bash(idev:*)` IS NOW UNBLOCKED, overruled by Josie 2026-08-15 after the cost was
put to her explicitly. See the note in DROP_DENY. `Bash(sbatch:*)` remains in
`ask` so a batch submission stays a conscious act. Every idev invocation should
carry `-m 120`.

The `Read()` denials on `*_DEPRECATED*`, `*_SUPERSEDED*` and
`data/track1_sweep_v2/**` stay. These are not access restrictions, they are
correctness guards: `track1_sweep_v2` is the superseded box-proxy sweep with a
1390 kg box against the real hull's 3.542739 m^3, and CLAUDE.md explicitly warns
against sourcing a figure or a density from it. Keeping them serves the goal of
Claude knowing what is correct.
"""
import argparse
import datetime
import json
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS = os.path.join(REPO, ".claude", "settings.json")

DROP_DENY = [
    "Read(reference_data/vehicle_data_master_reference_2026-07-21.json.OLD-4906B)",
    "Read(data/track1_sweep_v3/**)",
    "Read(//Users/josie/can-it-ford/can-it-ford/**)",
    "Read(designsafe-staging/**)",
    # OVERRULED BY JOSIE 2026-08-15, after the cost was put to her explicitly.
    # The prior reasoning, retained so nobody reinstates the deny by accident:
    # interactive idev burned 98.5 to 99.1 percent of Vista node-hours against
    # every gated run and 95 of 184 sessions ended in TIMEOUT. Her decision is
    # that Claude should be able to hold a bounded interactive node while it
    # works, which is a different tradeoff, not a mistake: an idle batch queue
    # also buys nothing. The mitigation is the -m 120 bound below plus
    # tacc_idle_check.sh, NOT a blanket denial.
    "Bash(idev:*)",
]

# Interactive allocation, explicitly bounded. `-m 120` is a 2-hour wall clock, so
# a forgotten session self-terminates instead of draining the allocation, which
# is what produced the 95 TIMEOUTs.
ADD_ALLOW = [
    "Bash(idev:*)",
    "Bash(srun --overlap:*)",
    "Bash(scancel:*)",
]

KEEP_DENY_SENTINELS = [
    "Bash(git add -A:*)",
    "Read(**/*_DEPRECATED*)",
    "Read(**/*_SUPERSEDED*)",
    "Read(data/track1_sweep_v2/**)",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not (a.apply or a.dry_run):
        ap.error("pass --dry-run or --apply")

    with open(SETTINGS, encoding="utf-8") as fh:
        d = json.load(fh)
    perms = d.setdefault("permissions", {})
    deny = perms.setdefault("deny", [])
    allow = perms.setdefault("allow", [])

    print(f"connectors: disableClaudeAiConnectors = "
          f"{d.get('disableClaudeAiConnectors')} -> False")
    removed = [r for r in DROP_DENY if r in deny]
    for r in DROP_DENY:
        print(f"  {'remove' if r in deny else 'absent'}  {r}")
    print()
    print("retained on purpose:")
    for s in KEEP_DENY_SENTINELS:
        print(f"  {'present' if s in deny else 'MISSING'}  {s}")

    print()
    print("interactive TACC allocation, unblocked per Josie 2026-08-15:")
    for r in ADD_ALLOW:
        print(f"  {'already' if r in allow else 'add   '}  {r}")
    print("  BOUND: always pass -m 120 (2 h wall clock). An unbounded idev is")
    print("  what produced 95 TIMEOUTs across 184 sessions.")

    if a.dry_run:
        print("\ndry run, nothing written")
        return 0

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = f"{SETTINGS}.bak-{stamp}"
    shutil.copy2(SETTINGS, bak)
    print(f"\nbackup: {bak}")

    d["disableClaudeAiConnectors"] = False
    perms["deny"] = [r for r in deny if r not in DROP_DENY]
    for r in ADD_ALLOW:
        if r not in allow:
            allow.append(r)
    perms["allow"] = allow
    with open(SETTINGS, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2)
        fh.write("\n")
    print(f"deny rules: {len(deny)} -> {len(perms['deny'])} "
          f"({len(removed)} removed)")
    print("hooks preserved:", list(d.get("hooks", {})))
    print("\nRestart the session for connector changes to take effect.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
