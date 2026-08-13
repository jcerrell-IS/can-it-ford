#!/bin/bash
# ============================================================================
# The direct test register J15 calls "the single highest-value open item in the
# project": RUN THE CANONICAL SET AT g128.
#
# WHY THIS AND NOT THE DISPATCHED COMPOSITE
#   The RTFD dispatch asked for a canonical SLIDE arm re-run on the force-coupled
#   DynamicSDFBody path at "same floor_friction=0.55". That is not runnable today:
#   dynamic_body.py:218-221 is the ENTIRE floor treatment on that path,
#
#       if self.floor_z is not None and x_new[2] < self.floor_z:
#           x_new[2] = self.floor_z
#           if v_new[2] < 0.0:
#               v_new[2] = 0.0
#
#   a z-position clamp plus a normal-velocity clamp, with no tangential term. A
#   case-insensitive grep for friction, tangent or coulomb in that file returns
#   ZERO hits. So mu = 0.55 cannot be set on the force-coupled path, and no
#   realism module imports failure_modes or classify_timeseries either. See
#   docs/FLAG_DISPATCH1_COMPOSITE_BLOCKED_2026-08-13.md.
#
#   This runs the other direct test of the same published number instead, on the
#   axis that IS testable today.
#
# NON-CANONICAL. Writes only to $BASE. Touches neither
# data/all_runs_inventory.csv nor gates_results_all_runs.json.
#
# PARAMETERS are the canonical ones, not re-derived here. The COMMON line is
# verbatim from run_rs_sweep.sh, which took it from
# scripts/class_specific_2026-08-08.sbatch, which took it from run_s2.sh as-ran.
# requested_depth 0.30 / velocity 1.5 is the pair behind g48/g64/g96_m{1100,1609,
# 2337} in data/all_runs_inventory.csv, confirmed live 2026-08-13 against that file.
#
# MASSES 1100 / 1609 / 2337 are the canonical three. Register item 10 records that
# 1609 and 2337 have no source in vehicle_params.py; that is a provenance defect in
# the published set, and it is reproduced here deliberately so this is a refinement
# of the SAME experiment and not a different one.
#
# WHY g96 IS RE-RUN HERE RATHER THAN READ FROM THE FROZEN STORE. Two reasons, both
# on the record:
#   1. Register J16: six of the seventeen frozen margins, the g48_* and g96_* runs,
#      are NOT reproducible. Job 866887 overwrote those directories on 2026-07-26.
#      The frozen g96 margins came from outputs that no longer exist.
#   2. Register J17 / REGIME_LADDER_RESULTS section 5.5: this stack is
#      non-deterministic at fixed configuration. A cross-job comparison cannot
#      separate a refinement effect from a run-to-run draw.
#   So g96 and g128 are paired IN THE SAME JOB, same node, same driver sha, exactly
#   as the floor-friction rung paired its mu arms.
# ============================================================================
set -uo pipefail

REPO=/scratch/11603/jcerrell0629/canitford_track1b/can-it-ford
# Two mpm-engine trees exist on /work. sim_standing.py needs solidify_watertight,
# which vista/can-it-ford/mpm-engine's warpmpm.vehicle does NOT have. The g64
# anchor runs (job 896273) resolved warpmpm to vista/mpm-engine per their
# 00_provenance.txt. Use that one: it is the only one that works and the one the
# anchors used.
ENGINE=/work/11603/jcerrell0629/vista/mpm-engine/src
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env

TAG=${1:-2026-08-13}
BASE=/scratch/11603/jcerrell0629/g128_canonical_${TAG}

echo "=== node ==="
hostname
nvidia-smi --query-gpu=index,name,memory.used --format=csv,noheader

PY="$VENV/bin/python"
export PYTHONPATH="$ENGINE:$REPO:${PYTHONPATH:-}"

mkdir -p "$BASE"
cd "$REPO" || exit 1

COMMON="--depth 0.30 --velocity 1.5 --frames 90 --eta 1.0e-3 --floor-friction 0.55"

{
  echo "start=$(date -Is) host=$(hostname)"
  echo "driver sha256: $(sha256sum "$REPO/renders/yaris_render_s1/sim_standing.py")"
  echo "engine: $ENGINE"
  echo "common: $COMMON"
  echo "purpose: register J15 direct test, canonical Yaris set at g128 with an in-job g96 control"
  echo "expected g96 anchor: g96_m2337 ratio_slide 1.80047 frozen / 1.74225 live re-classified (register J16)"
} > "$BASE/00_provenance.txt" 2>&1

go () {  # mass grid
  local LBL="canon_g${2}_m${1%.*}"
  echo "=== $LBL mass=$1 grid=$2 $(date -Is) ==="
  timeout 3000 "$PY" -u renders/yaris_render_s1/sim_standing.py \
    --vehicle yaris --mass "$1" --grid "$2" --label "$LBL" \
    --out "$BASE/$LBL" $COMMON > "$BASE/$LBL.log" 2>&1
  local rc=$?
  echo "RC_${LBL}=${rc}" | tee -a "$BASE/00_provenance.txt"
  # TRIPWIRE, inverted from run_rs_sweep.sh's. That script asserted a NON-zero
  # delta to prove --vehicle took effect. Here the Yaris IS the reference, so the
  # delta must read ~+0.000. A non-zero value means a Rogue or Silverado hull was
  # loaded and the run is mislabelled.
  grep -E "^INSTRUMENT hull_source" "$BASE/$LBL.log" | tee -a "$BASE/00_provenance.txt"
  grep -E "^SUMMARY " "$BASE/$LBL.log" > "$BASE/$LBL.summary.jsonl" 2>/dev/null
}

# g96 first: it is the control and the cheaper grid, so a short window still
# yields the paired comparison rather than three orphaned g128 runs.
for G in 96 128; do
  for M in 1100 1609 2337; do
    go "$M" "$G"
  done
done

echo "ALLDONE end=$(date -Is)" | tee -a "$BASE/00_provenance.txt"
ls -la "$BASE"
