---
description: Find Genesis/warpmpm engine conflation and untagged solver claims, using a grep that does not silently skip renders/ and data/.
argument-hint: "[path] optional, defaults to the whole repo"
allowed-tools: Bash(/usr/bin/grep:*), Bash(/usr/bin/find:*), Read, Glob
---

Audit for cross-engine parameter conflation between Genesis and warpmpm.

SCOPE RULE, non-negotiable. Register H0: `grep` in this shell is a function wrapping
ugrep with `--ignore-files`, so it skips every gitignored path. `.gitignore:14` is
`renders/` and `:10` is `data/*`, which is where `sim_standing.py`, `vehicle_live.py`,
`gates*.py` and all 17 runs' `metrics.csv` live. Use `/usr/bin/grep -rn` for every
search below, and exclude `./can-it-ford/` (nested duplicate), `./third_party/`
(vendored upstream) and `./.claude/worktrees/` (stale copies that multiply hits
roughly twentyfold). An absent hit is NOT evidence of absence: say "not found by
<exact command>", never "does not exist".

Search target: $ARGUMENTS if given, otherwise /Users/josie/can-it-ford.

Flag each of these, reporting file:line for every hit:

1. `cfrc_coupling_vel` anywhere outside a Genesis-tagged file. That accessor is
   Genesis-only and has no counterpart in warpmpm. Register A3.
2. Any Genesis identifier appearing inside the warpmpm driver directory. Register A1
   names that directory and its driver script. A Genesis identifier anywhere in it is
   an engine conflation, so report every hit with its line.
3. Any solver-behavior claim missing a GENESIS, WARPMPM or BOTH tag.
4. `coup_friction` and `floor_friction` used interchangeably. They are different
   parameters in different engines that both happen to appear as 0.55 in this
   project's documents. Register C10.
5. A dx or depth-resolution figure quoted without an engine tag. warpmpm gives about
   2 cells across 0.30 m depth, Genesis at gd 64 gives 19.2. Register B1 says these
   two numbers must never appear in one sentence untagged.
6. Any claim that gravity is unknown or unset. Settled at -9.81. Register A2.
7. Any use of `failure_modes_result.json` as evidence. Condemned, register D6h.

For each finding give: file:line, the offending text, which register item refutes it,
and the corrected wording. Then state the exact command you ran for each search so the
scope is auditable. End with a count of files searched, and name explicitly whether
`renders/` and `data/` were inside that count.
