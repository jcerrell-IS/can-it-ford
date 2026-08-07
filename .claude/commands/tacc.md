---
description: Live Vista and LS6 state: queue, SU balance, disk, and any idle allocation burning the budget
argument-hint: "[vista|ls6] (omit for both)"
allowed-tools: Bash(scripts/tacc.sh:*) Bash(scripts/tacc_idle_check.sh:*)
disable-model-invocation: true
---

Report the live TACC state. Do not answer from memory or from a doc.

Allocation and queue:

!`scripts/tacc.sh --status`

Idle-allocation probe (GPU utilisation on any interactive job):

!`scripts/tacc_idle_check.sh $ARGUMENTS`

Now summarise for me:

1. SUs remaining on each machine, and flag Vista if under 1000. Vista is the only
   machine with the warpmpm/GH200 path, so Vista SUs are the binding constraint,
   not wall-clock and not LS6.
2. Any job that is RUNNING, and whether the probe called it IDLE or active. If a
   node was unreachable the state is UNKNOWN, not idle; say so and do not guess.
3. Any filesystem over 80% used. Vista `/home1` was at 82.56% on 2026-08-07 and
   `render_s2/` writes there, so a full `/home1` means silent write failures.
4. If anything is idle, give me the exact `scancel` line. Do not run it yourself.

Do not convert node-hours to SUs. The `gh` and `gh-dev` charge multiplier has
never been read from a primary source here.
