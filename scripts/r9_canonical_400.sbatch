#!/bin/bash
#SBATCH -J r9_canon400
#SBATCH -A BCS20003
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:40:00
#SBATCH -o /work/11603/jcerrell0629/vista/r9_canonical_400/slurm_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/r9_canonical_400/slurm_%j.err

# ===========================================================================
# d15-settle. THE CANONICAL SET AT 400 FRAMES, 3 DRAWS PER CELL.
#
# WHY THIS IS AFFORDABLE, MEASURED NOT ASSUMED. Job 922622 measured a g64
# 400-frame run at 21 s wall. Marginal cost from the 90 and 400 arms is
# (21-9)/(400-90) = 0.0387 s/frame with ~5.5 s startup. The entire "the record
# is too short" finding has been treated as blocked on GPU time it never
# needed.
#
# WALLTIME IS SIZED FROM THAT MEASUREMENT, NOT FROM A ROUND NUMBER. Job 922622
# asked 2:00:00 and ran 00:01:06, a 109x over-request that sat behind 139 jobs,
# because Slurm backfills short requests into gaps a long one cannot fit.
# Estimate here: 51 runs, grid mix 33 g64 / 9 g48 / 9 g96, cost taken as
# grid^4 (particles ~ grid^3 times substeps ~ grid), giving ~27 g64-equivalents
# per draw, ~8.6 min per draw, ~26 min for three. 00:40:00 is ~1.5x that.
#
# WHY THREE DRAWS AND NOT ONE. Job 922622 measured that this path is
# NON-DETERMINISTIC at fixed config: the 90 and 400 arms differ at frame 0 by
# 7.8e-08 in vz, float32 epsilon, and that grows to 1.9e-02 by frame 26. A
# single draw is therefore not a result on the free-rigid canonical path,
# whatever d17-moving measured for the SDF path.
#
# THIS ADDS TO THE RECORD, IT DOES NOT REPLACE IT. Output goes to a new tree.
# No canonical artifact under renders/ or data/ is read, written or moved, and
# these runs are NOT part of the 17 gated set.
#
# EXIT CODES ARE GATED. Job 922622's probe arm exited 1 and still wrote a
# metrics.csv with the right number of rows, so a reader checking only for the
# file, or only counting rows, would have graded a failed arm as a good one.
# That is this round's own instrument-failure pattern. Every RC is recorded,
# and the job ends by FAILING LOUDLY with a non-zero exit if any arm failed.
# ===========================================================================
set -o pipefail

PY=$WORK/.venv/bin/python
DRIVER=$WORK/render_s2/sim_standing.py          # sha256 5215c38b, the 17-run driver
BASE=$WORK/r9_canonical_400
FRAMES=400

# NOTE ON THE DRIVER'S FRAME HAZARD, found the hard way in 922622.
# 5215c38b writes veh_check_45=checkpoints["45"] unguarded, and only records a
# checkpoint at f in (0, 45, frames-1). ANY ARM WITH frames < 46 CRASHES WITH
# KeyError: '45' AFTER writing metrics.csv. Every arm here is 400, so it cannot
# fire, but do not add a short arm to this file without fixing the driver. The
# Mac canonical driver already carries the fix, f_check = min(45, frames-1).

mkdir -p "$BASE"
FAILED=0

{
  echo "job=${SLURM_JOB_ID}  host=$(hostname)  start=$(date -Is)"
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  echo "driver sha256: $(sha256sum "$DRIVER")"
  echo "frames: $FRAMES   draws: 3"
} > "$BASE/00_provenance.txt" 2>&1

go () {  # label  mass  grid  depth  velocity  seedtag
  local out="$BASE/$1_$6"
  local t0=$SECONDS
  timeout 1200 "$PY" -u "$DRIVER" --mass "$2" --label "$1_$6" --out "$out" \
    --grid "$3" --depth "$4" --velocity "$5" --frames "$FRAMES" \
    --eta 1.0e-3 --floor-friction 0.55 > "$BASE/$1_$6.log" 2>&1
  local rc=$?
  local dt=$(( SECONDS - t0 ))
  local rows="absent"
  [ -f "$out/metrics.csv" ] && rows=$(wc -l < "$out/metrics.csv")
  # RC AND ROWS ARE RECORDED SEPARATELY AND BOTH ARE CHECKED. Row count alone
  # graded 922622's crashed probe as healthy; rc alone would not have told us
  # the physics ran. Neither is sufficient, so print both.
  echo "RC_$1_$6=${rc} wall_s=${dt} rows=${rows}" | tee -a "$BASE/00_provenance.txt"
  if [ "$rc" -ne 0 ]; then FAILED=$(( FAILED + 1 )); fi
  sync
}

for SEED in d1 d2 d3; do
  # mass sweep, three grids
  for G in 48 64 96; do
    go "g${G}_m1100" 1100.0 "$G" 0.30 1.5 "$SEED"
    go "g${G}_m1609" 1609.0 "$G" 0.30 1.5 "$SEED"
    go "g${G}_m2337" 2337.0 "$G" 0.30 1.5 "$SEED"
  done
  # depth sweep, g64
  for D in 0.25 0.35 0.45; do
    go "sweepD_g64_d${D}" 1100.0 64 "$D" 1.5 "$SEED"
  done
  # velocity sweep, g64
  for V in 0.5 1.0 2.0 2.5 3.0; do
    go "sweepV_g64_v${V}" 1100.0 64 0.30 "$V" "$SEED"
  done
done

echo "done=$(date -Is)  FAILED_ARMS=${FAILED}" | tee -a "$BASE/00_provenance.txt"
if [ "$FAILED" -ne 0 ]; then
  echo "JOB FAILED: ${FAILED} arm(s) exited non-zero. Do not use this tree." >&2
  exit 1
fi
