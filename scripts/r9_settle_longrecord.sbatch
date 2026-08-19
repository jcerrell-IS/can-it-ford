#!/bin/bash
#SBATCH -J r9_settle_longrec
#SBATCH -A BCS20003
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00
#SBATCH -o /work/11603/jcerrell0629/vista/r9_settle_longrecord/slurm_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/r9_settle_longrecord/slurm_%j.err

# ===========================================================================
# d15-settle, LONG-RECORD TEST. Pre-registered in
# docs/R9_SETTLE_FRAMES_2026-08-18.md section 19 BEFORE submission.
#
# THE QUESTION. Every claim this slot has made about record length is an
# inference from records that do not exist. The canonical runs are 91 rows and
# nobody has ever run a longer one. Register D9 reaches a 250-frame conclusion
# by a different route and is also an inference. This is the direct test.
#
# DESIGN. Three arms, one held-fixed variable. Only --frames changes.
#   probe    10 frames, to MEASURE the per-frame cost rather than guess it.
#   control  90 frames, the canonical length. Its job is to distinguish
#            "the environment still reproduces" from "cannot evaluate". If the
#            control does not reproduce, the 400-frame numbers are
#            uninterpretable and must NOT be reported as a result.
#   long     400 frames, past D9's 250 so saturation is visible if it exists.
#
# DRIVER CHOICE, STATED BECAUSE IT IS A DECISION AND NOT A DETAIL.
#   Three drivers exist and none matches another:
#     4696c3b2  Mac, current repo canonical
#     7236e474  Vista $WORK/class_specific_2026-08-08, the Aug 8 staged copy
#     5215c38b  Vista $WORK/render_s2, THE DRIVER THAT PRODUCED THE 17 GATED RUNS
#   This job uses 5215c38b. The entire value of the control arm is
#   comparability with the canonical records, which that driver produced. The
#   cost is that this does NOT test the current repo driver, and any
#   difference between 4696c3b2 and 5215c38b is out of scope here.
#   Verified before submission: 5215c38b has --frames (:224) and its
#   checkpoint guard is `if f in (0, 45, a.frames - 1)` (:302), so f=45 exists
#   at every length used here and the npz write cannot KeyError.
#
# HULL. md5 372a709ffb22e0c914ecf25d4f34a76c, verified identical on the Mac,
# at the driver's expected VEHICLE_DIR, and in the track1-6dof tree.
#
# NO set -e. A failing arm must not abort the arm after it, and the probe
# failing must not cost us the control.
# ===========================================================================
set -o pipefail

PY=$WORK/.venv/bin/python
DRIVER=$WORK/render_s2/sim_standing.py          # sha256 5215c38b
BASE=$WORK/r9_settle_longrecord

# Canonical g64 m1100 parameters. Verbatim from
# scripts/class_specific_2026-08-08.sbatch COMMON, which took them from
# run_s2.sh as-ran for the 17 gated runs, with --frames removed so each arm
# sets its own and nothing else can drift between arms.
COMMON="--depth 0.30 --velocity 1.5 --grid 64 --eta 1.0e-3 --floor-friction 0.55"
MASS=1100.0

mkdir -p "$BASE"

{
  echo "job=${SLURM_JOB_ID}  host=$(hostname)  start=$(date -Is)"
  nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv
  "$PY" -c "import warpmpm; print('warpmpm:', warpmpm.__file__)"
  echo "driver sha256: $(sha256sum "$DRIVER")"
  echo "common args  : $COMMON"
  echo "mass         : $MASS"
} > "$BASE/00_provenance.txt" 2>&1
sync

go () {  # label  frames  timeout_s
  echo "=== $1  frames=$2  start=$(date -Is) ==="
  local t0=$SECONDS
  timeout "$3" "$PY" -u "$DRIVER" --mass "$MASS" --label "$1" \
    --out "$BASE/$1" --frames "$2" $COMMON \
    > "$BASE/$1.log" 2>&1
  local rc=$?
  local dt=$(( SECONDS - t0 ))
  # Per-frame cost is logged for EVERY arm, so the next person sizing a job
  # reads a measurement instead of repeating this guess.
  echo "RC_$1=${rc}  wall_s=${dt}  frames=$2  s_per_frame=$(awk "BEGIN{printf \"%.3f\", $dt/$2}")" \
    | tee -a "$BASE/00_provenance.txt"
  sha256sum "$BASE/$1/metrics.csv" 2>&1 | tee -a "$BASE/00_provenance.txt"
  wc -l "$BASE/$1/metrics.csv" 2>&1 | tee -a "$BASE/00_provenance.txt"
  sync
}

go probe_f10    10   600
go control_f90  90   1800
go long_f400   400   5400

echo "done=$(date -Is)" | tee -a "$BASE/00_provenance.txt"
