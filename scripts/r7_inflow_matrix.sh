#!/usr/bin/env bash
#SBATCH -J r7_inflow
#SBATCH -o /work/11603/jcerrell0629/vista/logs/r7_inflow_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/logs/r7_inflow_%j.out
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00
#SBATCH -A BCS20003
#
# TASK 7: port the Zhao et al 2019 recycling in/outflow BC from the water-only channel
# (simulation/openchannel_bc.py, commit be1b138) to the CANONICAL VEHICLE SCENE, and
# measure what it changes.
#
# THE MATRIX, and why each row is here rather than a sweep of comfortable cases.
#
#   g64m1100v1p5   bare x1     the UNWRAPPED canonical driver. The wrapper-inertness
#                              control: closed-wrapped must land inside the bare spread,
#                              or the instrumentation is not read-only and nothing below
#                              means anything.
#                  closed x5   matched control, same code path as the treatment
#                  recycle x5  treatment
#                  recycnb x3  treatment with sim_standing's upstream velocity band
#                              removed, i.e. the faithful sim_channel.py recycle mode.
#                              Sensitivity arm: it separates "the boundary changed things"
#                              from "the drive changed things".
#   g64m1100v0p5   closed x5 / recycle x5
#                              sweepV_g64_v0p5 is the ONLY STUCK among the 17 published
#                              runs. If a boundary change can move a verdict, the single
#                              non-SLIDE run is where it is cheapest to detect.
#   g96m2337v1p5   closed x5 / recycle x5
#                              the tightest published margin (register J15, margin 1
#                              frame), and R6 measured that margin as a random variable
#                              spanning 0 to 1 rather than a scalar. Repeating comfortable
#                              runs measures nothing.
#
# N=5 IS NOT DECORATION, AND THE REASON WAS STATED WRONG IN THE FIRST VERSION OF THIS
# COMMENT. summary.json determinism_identical reads TRUE on all 17 published runs, checked
# live. It is not a reproducibility flag: sim_standing.py:389 defines it as
# (v1.n_particles == v2.n_particles) and (lim1 == lim2), a particle count and a grid limit,
# so it says the HULL LOAD is bit-identical and nothing more. Hull loading genuinely is
# deterministic; the nondeterminism is in the SOLVE, and handoff 3a records all 20 R6 A2
# repeats coming out bit-different at every grid, diverging by the first recorded frame.
# So every run is a draw, a single closed-vs-recycle pair cannot establish a verdict change,
# and this matrix reports the within-arm spread as its own evidence of that.
#
# 250 FRAMES, NOT 90. The canonical horizon is metrics row 90, and everything is reported
# there as well; 250 exists so the wall-reflection window at about frame 112 is INSIDE the
# record rather than beyond it. Both horizons are classified separately.
#
# EVERY OUTPUT PATH CARRIES $SLURM_JOB_ID. Job 866887 overwrote fixed paths in July and
# made six margins permanently unverifiable.
set -uo pipefail

ENGINE=/work/11603/jcerrell0629/vista/mpm-engine
VENV=/work/11603/jcerrell0629/vista/.venv/bin/python
SRC=/work/11603/jcerrell0629/vista/r7_inflow_src
WRAP=$SRC/scripts/inflow_vehicle_wrapper.py
# CANONICAL driver, sha256 4696c3b2...d10d9. $WORK/render_s2/sim_standing.py is a
# different, pre-registry copy (5215c38b...) and the wrapper refuses it by sha.
DRIVER=/work/11603/jcerrell0629/vista/render_s2/multigeom_2026-08-08/sim_standing.py
OUT=/work/11603/jcerrell0629/vista/r7_inflow_${SLURM_JOB_ID:-manual}
FRAMES=250

mkdir -p "$OUT"
cd "$ENGINE" || exit 1
hostname
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1 | head -2
echo "TIMING_ANCHOR_START=$(date +%s)"
echo "FRAMES=$FRAMES  OUT=$OUT"
echo "DRIVER_SHA $(sha256sum "$DRIVER")"
echo "WRAPPER_SHA $(sha256sum "$WRAP")"
echo "BC_SHA $(sha256sum "$SRC/simulation/openchannel_bc.py")"
$VENV -u "$WRAP" --selftest || exit 1

FAILS=0
RUNS=0

# run_bare <cfg> <rep> <grid> <mass> <velocity>
run_bare () {
  local name="$1__bare__rep$2"
  $VENV -u "$DRIVER" --label "$name" --out "$OUT/$name" \
    --mass "$4" --depth 0.30 --velocity "$5" --frames "$FRAMES" --grid "$3" \
    --eta 1.0e-3 --floor-friction 0.55
  local rc=$?; RUNS=$((RUNS+1)); echo "RC_${name}=$rc"
  [ $rc -eq 0 ] || FAILS=$((FAILS+1))
}

# run_wrapped <cfg> <arm> <rep> <grid> <mass> <velocity> <bc> <noband:0|1>
run_wrapped () {
  local name="$1__$2__rep$3" nbflag=""
  [ "$8" = "1" ] && nbflag="--no-band"
  $VENV -u "$WRAP" --driver "$DRIVER" --bc "$7" $nbflag \
    --label "$name" --out "$OUT/$name" \
    --depth 0.30 --velocity "$6" --frames "$FRAMES" --grid "$4" \
    --mass "$5" --eta 1.0e-3 --floor-friction 0.55
  local rc=$?; RUNS=$((RUNS+1)); echo "RC_${name}=$rc"
  [ $rc -eq 0 ] || FAILS=$((FAILS+1))
}

# ---- config A: the canonical g64 baseline ------------------------------------------
run_bare g64m1100v1p5 1 64 1100 1.5
for i in 1 2 3 4 5; do
  run_wrapped g64m1100v1p5 closed  "$i" 64 1100 1.5 closed  0
  run_wrapped g64m1100v1p5 recycle "$i" 64 1100 1.5 recycle 0
done
for i in 1 2 3; do
  run_wrapped g64m1100v1p5 recycnb "$i" 64 1100 1.5 recycle 1
done

# ---- config B: the only STUCK of the 17 --------------------------------------------
for i in 1 2 3 4 5; do
  run_wrapped g64m1100v0p5 closed  "$i" 64 1100 0.5 closed  0
  run_wrapped g64m1100v0p5 recycle "$i" 64 1100 0.5 recycle 0
done

# ---- config C: the tightest published margin ---------------------------------------
for i in 1 2 3 4 5; do
  run_wrapped g96m2337v1p5 closed  "$i" 96 2337 1.5 closed  0
  run_wrapped g96m2337v1p5 recycle "$i" 96 2337 1.5 recycle 0
done

echo "TIMING_ANCHOR_END=$(date +%s)"
echo "SUMMARY runs=$RUNS failed=$FAILS out=$OUT"
# Job 917786 reported COMPLETED with ExitCode 0:0 while all 23 of its runs failed, because
# its last statement was `echo ALLDONE` and the echo succeeded. Make the exit status mean
# something.
if [ $FAILS -ne 0 ]; then
  echo "ALLDONE_WITH_FAILURES runs=$RUNS failed=$FAILS"
  exit 1
fi
echo ALLDONE
