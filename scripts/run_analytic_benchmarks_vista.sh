#!/usr/bin/env bash
# Run the solver's own analytic validation suite on a live Vista node.
#
# WHY THIS EXISTS
# ---------------
# The Undermind reports asked for "a locked free-surface regression case with a
# known analytical or experimental answer, run once, kept as a standing
# regression test". While building one from scratch it turned out THE ENGINE
# ALREADY SHIPS ONE and this project has never run it:
#
#     $WORK/mpm-engine/tests/test_analytic_benchmarks.py
#
# It follows the CB-Geo MPM benchmark suite and validates friction calibration,
# the EOS pressure and the elastic wave speed end to end through P2G/G2P. Those
# are the exact mechanisms the SLIDE verdicts depend on, which makes it more
# relevant here than the Poiseuille case originally planned.
#
# MEASURED 2026-08-18 on Vista node c642-032 (NVIDIA GH200 120GB), inside a live
# 2-hour idev allocation, job 917886:
#
#     4 passed in 27.99s
#
#   1. sliding block on a frictional incline, a = g (sin th - mu cos th)   <15%
#   2. mu > tan th block holds statically, drift                       <0.02 m/s
#   3. hydrostatic column basal support force = rho V g                    < 8%
#   4. free-free elastic bar longitudinal period T = 2 L / sqrt(E/rho)      < 3%
#
# READ THE SUITE'S OWN CAVEAT BEFORE QUOTING IT AS VALIDATION. Its module
# docstring states two of the scenes are substitutions that "route around
# measured engine failure modes ... particle-stress statics noise; sticky-clamp
# softening under tension" and are "characterizations to fix, not physics gates
# passed". So a green run means the engine reproduces four closed-form answers
# on scenes chosen to avoid two known defects. That is real and worth having; it
# is not a clean bill of health.
#
# PROVENANCE DISCREPANCY, verify before citing either as "the" solver: the Vista
# working copy reported HEAD 627367e, while this repo vendors
# third_party/mpm-engine-544c93dd. Those are different checkouts. Confirm which
# one produced any number you publish.
#
# USAGE
#   scripts/run_analytic_benchmarks_vista.sh <JOBID>
# with a RUNNING idev job. Find one with:  ssh vista squeue -u \$USER
#
# The srun flags are not optional. Vista's submit filter rejects a step that
# omits -p, -N or -t even when --overlap is attaching to an existing allocation,
# and without --overlap the step kills the interactive session outright.
set -euo pipefail

JOBID="${1:-}"
if [[ -z "$JOBID" ]]; then
  echo "usage: $0 <RUNNING idev jobid>" >&2
  echo "  ssh vista squeue -u \$USER -o '%.10i %.9T %R'" >&2
  exit 2
fi

PART="$(ssh -o BatchMode=yes vista \
  "scontrol show job $JOBID | tr ' ' '\n' | /usr/bin/grep '^Partition=' | cut -d= -f2" \
  2>/dev/null | tr -d '\r')"
if [[ -z "$PART" ]]; then
  echo "job $JOBID not found or not visible. Is it still RUNNING?" >&2
  exit 1
fi
echo "job $JOBID on partition $PART"

ssh -o BatchMode=yes vista "srun --overlap --jobid=$JOBID -p $PART -N1 -n1 -t 00:25:00 bash -c '
  cd \$WORK/mpm-engine
  echo \"node   \$(hostname)\"
  echo \"engine \$(git rev-parse --short HEAD 2>/dev/null || cat PINNED_SHA.txt 2>/dev/null)\"
  nvidia-smi --query-gpu=name --format=csv,noheader | head -1
  \$WORK/.venv/bin/python3.12 -m pytest tests/test_analytic_benchmarks.py -v --no-header -q 2>&1 | tail -20
'"
