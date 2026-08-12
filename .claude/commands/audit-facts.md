---
description: Run the full local factual-integrity stack (register, params, literature gates, claim checks) and report what actually failed.
argument-hint: "[--all] optional, widens check_claims from the staged index to every tracked file"
allowed-tools: Bash(python3 /Users/josie/can-it-ford/.claude/checks/register_integrity.py:*), Bash(python3 /Users/josie/can-it-ford/.claude/checks/params_check.py:*), Bash(python3 /Users/josie/can-it-ford/.claude/checks/physics_gates_literature.py:*), Bash(python3 /Users/josie/can-it-ford/scripts/check_claims.py:*), Read, Grep, Glob
---

Run all four local verification tools and report the combined result. Run them in
order, and do not stop on the first failure, because they check disjoint things.

1. Register integrity, catches duplicate item numbers, dangling cross-references,
   unresolved cited paths and unresolved cited hex tokens:
   !`python3 /Users/josie/can-it-ford/.claude/checks/register_integrity.py`

2. Parameter and literature gates, including lit:geometry_bbox,
   lit:sound_speed_cfl, lit:resolution_convergence_gci and lit:manifest_provenance:
   !`python3 /Users/josie/can-it-ford/.claude/checks/params_check.py`

3. Claim checks C1 through C14 against $ARGUMENTS scope:
   !`python3 /Users/josie/can-it-ford/scripts/check_claims.py $ARGUMENTS`

Then report, in this order:

- Any BLOCKING defect, verbatim, with the file and line it names.
- Any WARNING that is NEW relative to the known-explained set below. A warning in
  the known set is expected and is not a finding, so do not report it as one.
- One line stating whether the repo's factual state is self-consistent right now.

KNOWN-EXPLAINED WARNINGS, expected, not findings:

- register_integrity unresolved-path `genesis/engine/entities/mpm_entity.py`. That
  is a Genesis install path on Vista, not a repo file. Register C7.
- register_integrity unresolved-path `scratchpad/classify_17_runs.py`. The register
  is deliberately quoting the bad provenance path it already corrected. Register D6a.
- register_integrity unresolved-path `track1_sweep_v2/manifest.csv`. The register is
  deliberately quoting the bare path it already corrected to `data/track1_sweep_v2/`.
- params_check lit:sound_speed_cfl on 15 of 17 runs. Register B8, a disclosed
  limitation, not a defect.
- params_check lit:resolution_convergence_gci cannot compute an apparent order.
  Register B2, the study is genuinely non-monotone. Report the raw spread.
- params_check inertia, cg_height, ssf never referenced by sim_standing.py. CLAUDE.md
  item 4 extension, this absence is CORRECT and must not be "fixed".

DO NOT treat a clean run as proof of physical correctness. Register D5: no gate here
is a physics validation. Every one is a self-consistency or numerical-containment
check. Say "self-consistent", never "validated".
