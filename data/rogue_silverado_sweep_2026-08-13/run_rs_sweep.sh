#!/bin/bash
# STEP 6. Rogue / Silverado grid-resolution sweep, NON-CANONICAL by Part 2.7.
# Nothing here touches data/all_runs_inventory.csv or gates_results_all_runs.json.
#
# Depth/velocity are matched to the canonical Yaris point that the 17 gated runs
# use: --depth 0.30 --velocity 1.5 --frames 90 --eta 1.0e-3 --floor-friction 0.55,
# verbatim from the COMMON line of scripts/class_specific_2026-08-08.sbatch, which
# took it from run_s2.sh as-ran. requested_depth 0.30 / velocity 1.5 is the pair
# behind g48/g64/g96_m{1100,1609,2337} in data/all_runs_inventory.csv.
#
# MASSES are the ones the existing g64 runs used (job 896273, Vista), NOT the
# registry AR&R defaults of 1609 / 2337. This makes g64 a reusable anchor so the
# ladder is g64(existing) + g96 + g128 under one mass per vehicle. Silverado
# 2270.0 is deck-header primary per the 2026-08-13 provenance fix. Rogue 1571.3
# is WEB-SOURCED ONLY, the Rogue deck states no mass; label it as such.
#
# Runs on GPU 1: GPU 0 is busy with the rung-b g96 gated settle.

set -uo pipefail

REPO=/scratch/11603/jcerrell0629/canitford_track1b/can-it-ford
# NOTE: two mpm-engine trees exist on /work. The rung-b coupling work uses
# vista/can-it-ford/mpm-engine, whose warpmpm.vehicle has NO solidify_watertight.
# sim_standing.py needs it, and the existing g64 anchor runs (job 896273) resolved
# warpmpm to vista/mpm-engine per their 00_provenance.txt. Use that one, both
# because it is the only one that works and because it is the one the anchors used.
ENGINE=/work/11603/jcerrell0629/vista/mpm-engine/src
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
TAG=${1:-manual}
BASE=/scratch/11603/jcerrell0629/rs_sweep_${TAG}

export CUDA_VISIBLE_DEVICES=1

echo "=== node ==="
hostname
nvidia-smi --query-gpu=index,name,memory.used --format=csv,noheader

PY="$VENV/bin/python"
export PYTHONPATH="$ENGINE:$REPO:${PYTHONPATH:-}"

mkdir -p "$BASE"
cd "$REPO"

COMMON="--depth 0.30 --velocity 1.5 --frames 90 --eta 1.0e-3 --floor-friction 0.55"

{
  echo "start=$(date -Is) host=$(hostname)"
  echo "driver sha256: $(sha256sum $REPO/renders/yaris_render_s1/sim_standing.py)"
  echo "common: $COMMON"
  echo "mass rogue 1571.3 (web-sourced), mass silverado 2270.0 (deck header, primary)"
} > "$BASE/00_provenance.txt" 2>&1

go () {  # vehicle mass grid
  local LBL="rs_${1}_g${3}"
  echo "=== $LBL mass=$2 grid=$3 $(date -Is) ==="
  timeout 3000 "$PY" -u renders/yaris_render_s1/sim_standing.py \
    --vehicle "$1" --mass "$2" --grid "$3" --label "$LBL" \
    --out "$BASE/$LBL" $COMMON > "$BASE/$LBL.log" 2>&1
  local rc=$?
  echo "RC_${LBL}=${rc}" | tee -a "$BASE/00_provenance.txt"
  # TRIPWIRE: must read +39.732 (rogue) or +124.744 (silverado). ~0.000 means
  # --vehicle did not take effect and the run is the Yaris hull mislabelled.
  grep -E "^INSTRUMENT hull_source" "$BASE/$LBL.log" | tee -a "$BASE/00_provenance.txt"
  grep -E "^SUMMARY " "$BASE/$LBL.log" > "$BASE/$LBL.summary.jsonl" 2>/dev/null
}

# Cheapest grids first so a short window still yields a usable ladder.
for G in 64 96 128; do
  go rogue     1571.3 "$G"
  go silverado 2270.0 "$G"
done

echo "ALLDONE end=$(date -Is)" | tee -a "$BASE/00_provenance.txt"
ls -la "$BASE"
