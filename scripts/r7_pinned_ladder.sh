#!/bin/bash
#SBATCH -A BCS20003
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
# ============================================================================
# r7_pinned.sh  --  THE PINNED-SPAN LADDER CONTROL. Round 7, task 1.
#
# WHAT THIS SETTLES
# The R6 refinement ladder (jobs 918247-918250, 918350, 918351) is FOUR-PLUS
# DIFFERENT TANKS, not one tank at several resolutions. sim_standing.py:82 sets
#   lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth)      -- independent of n_grid
# while :86 and :100 set floor = 3.0*dx and wall = 4.0*dx -- IN CELLS. So the
# water interior span is lim - 8*dx = lim*(1 - 8/n) and it GROWS under
# refinement: +12.5 percent span, +26.6 percent plan area, +30.7 percent water
# volume from g48 to g128. The tank is LARGEST exactly where the g160 verdict
# flips SLIDE -> STUCK. Tank growth and resolution are co-directional and no
# existing run separates them.
#
# THIS JOB pins the interior span to S metres for every grid, by presenting a
# different extent[1] through scripts/pinned_span_wrapper.py. The HULL IS NOT
# RESCALED: mesh, surface, particles, mass and spacing are the real hull, so
# blockage is held fixed. hull_m3 MUST come back 3.542739 on every rung; that
# is the falsifier for "the wrapper secretly shrank the vehicle".
#
# S = 7.851451928106448 m, the g48 interior span, derived as
#   S = 9.421742313727737 * (1 - 8/48)
# from grid_lim read live out of all six unpinned summary.json files.
#
# WHY sim_standing.py IS NOT EDITED. Its sha256 stamps every published run.
# The wrapper monkeypatches canonicalize(), the single point every downstream
# consumer reads (:81 lim, :236 h_probe, :239/:240 determinism, :337 summary),
# so the override propagates by construction and self-documents in the output.
#
# TWO VARIANTS, because pinning the span does NOT pin the realized water depth.
# Depth is quantized to L*h with L = ceil(depth/h - 0.5), so it moves unless
# 40 | (n-8). The unpinned ladder happens to hold realized depth EXACTLY at
# 0.2944294473039918 m on every rung, which is a real control that must not be
# surrendered silently.
#   free    span pinned, depth allowed to move   n = 48 64 96 128 141 160 192
#   exact   span AND depth both pinned           n = 48 88 128 168 208
# n=48 and n=128 are exact-depth grids and therefore belong to BOTH variants;
# they are run ONCE and shared, not run twice.
#
# n=48 IS A NULL CONTROL. At n=48 the pinned lim equals the unpinned lim to
# float precision, so this rung must reproduce job 918250 exactly:
#   grid_lim 9.421742313727737  dx 0.1962863  layers 3  n_water 18194
#   n_carved 529  hull_m3 3.542739  solid_volume_m3 3.6357101018957585
# If it does not, the wrapper is wrong and NOTHING ELSE HERE IS VALID.
#
# WHY EVERY PATH CARRIES ${SLURM_JOB_ID}. run_s2.sh writes FIXED paths
# g${GRID}_m${MASS}; a second invocation silently overwrites the first. That is
# the 2026-07-26 job-866887 overwrite that destroyed six margins and made
# register J16 permanently unverifiable.
#
# WHY THE EXIT STATUS IS COMPUTED. Job 917786 reported COMPLETED ExitCode 0:0
# while all 23 of its runs failed, because its last statement was an echo.
# ============================================================================
set -uo pipefail

GRID=${1:?usage: r7_pinned.sh GRID MODE(free|exact) NREP}
MODE=${2:?usage: r7_pinned.sh GRID MODE(free|exact) NREP}
NREP=${3:?usage: r7_pinned.sh GRID MODE(free|exact) NREP}

WORKD=/work/11603/jcerrell0629/vista
ENGINE=$WORKD/mpm-engine
VENV=$WORKD/.venv/bin/python
DRIVER=$WORKD/render_s2/sim_standing.py
WRAPPER=$WORKD/r7_pinned/pinned_span_wrapper.py
SPAN=7.851451928106448

export PYTHONPATH=$WORKD/mpm-engine/src:$WORKD/.venv/lib/python3.12/site-packages

OUT=$WORKD/r7_pin_g${GRID}_${MODE}_${SLURM_JOB_ID:-manual}
mkdir -p "$OUT"
cd "$ENGINE" || exit 1

hostname
echo "TIMING_ANCHOR_START=$(date +%s)"
echo "PIN_GRID=$GRID PIN_MODE=$MODE PIN_NREP=$NREP PIN_SPAN=$SPAN"
echo "PIN_OUT=$OUT"

# Provenance. A result whose driver is unstamped cannot be compared to anything.
echo "DRIVER_SHA256=$(sha256sum "$DRIVER" | awk '{print $1}')"
echo "DRIVER_SHA256_EXPECTED=5215c38bed607ef6fa0723afa4e9593de87a1fd82818a0e92989f52daffc9d45"
echo "WRAPPER_SHA256=$(sha256sum "$WRAPPER" | awk '{print $1}')"
echo "WRAPPER_SHA256_EXPECTED=c7a0804cf826b3722051e365237fded8847903293d617564b80ce20f18fc0779"

# The driver sha is the one that produced the g160 flip (job 918350 line 3).
# Refuse to spend GPU on a driver that is not that file.
GOT=$(sha256sum "$DRIVER" | awk '{print $1}')
if [ "$GOT" != "5215c38bed607ef6fa0723afa4e9593de87a1fd82818a0e92989f52daffc9d45" ]; then
  echo "REFUSED: driver sha256 mismatch. The control must differ from the confounded"
  echo "REFUSED: experiment ONLY in the pinned span, so the driver must be byte-identical."
  exit 2
fi

EXTRA=""
if [ "$MODE" = "exact" ]; then
  EXTRA="--require-exact-depth"
fi

FAILS=0
RUNS=0
for i in $(seq 1 "$NREP"); do
  echo "===== REP $i / $NREP  grid=$GRID mode=$MODE ====="
  $VENV -u "$WRAPPER" \
    --driver "$DRIVER" \
    --span "$SPAN" \
    --grid "$GRID" \
    --depth 0.30 \
    --out "$OUT/rep_$i" \
    --label pin_g${GRID}_${MODE}_m2337_$i \
    --provenance "$OUT/rep_${i}_provenance.json" \
    $EXTRA \
    --mass 2337 --velocity 1.5 --frames 90 \
    --eta 1.0e-3 --floor-friction 0.55
  RC=$?
  RUNS=$((RUNS+1)); [ $RC -eq 0 ] || FAILS=$((FAILS+1))
  echo "RC_rep_${i}=$RC"
done

echo "TIMING_ANCHOR_END=$(date +%s)"
echo "SUMMARY grid=$GRID mode=$MODE runs=$RUNS failed=$FAILS"
if [ $FAILS -ne 0 ]; then
  echo "ALLDONE_WITH_FAILURES"
  exit 1
fi
echo ALLDONE
