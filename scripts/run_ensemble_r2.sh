#!/bin/bash
# R2 independent-start ensemble worker. NON-CANONICAL. See analysis/ensemble_seed_runner.py
# for why the seed is injected by a wrapper rather than by editing the shared driver.
# Args: TAG N_GRID SEED_FIRST SEED_LAST
# The parent creates BASE; this refuses only if an individual run dir already exists,
# so three of these can share one BASE across three GPUs (register item 16 still honoured).
set -uo pipefail
REPO=/scratch/11603/jcerrell0629/canitford_track1b/can-it-ford
ENGINE=/work/11603/jcerrell0629/vista/mpm-engine/src
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
TAG=$1; NG=$2; S0=$3; S1=$4
BASE=/scratch/11603/jcerrell0629/three_class_ensemble_${TAG}
PY="$VENV/bin/python"
export PYTHONPATH="$ENGINE:$REPO:${PYTHONPATH:-}"
export CANFORD_REPO="$REPO"
WRAP="$REPO/analysis/ensemble_seed_runner.py"
PROV="$BASE/00_provenance_g${NG}_${S0}_${S1}.txt"
{ echo "start=$(date -Is) host=$(hostname) n_grid=$NG seeds ${S0}..${S1}"
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
  echo "driver sha256: $(sha256sum $REPO/renders/yaris_render_s1/sim_standing.py)"
  echo "wrapper sha256: $(sha256sum $WRAP)"
  nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used --format=csv,noheader
} >> "$PROV" 2>&1
for s in $(seq $S0 $S1); do
  L="E${NG}_silverado_m2270_s${s}"; OUT="$BASE/$L"
  if [ -e "$OUT" ]; then echo "REFUSING existing $OUT"; continue; fi
  mkdir -p "$OUT"
  echo "=== $(date -Is) $L"
  ENSEMBLE_SEED=$s "$PY" "$WRAP" --vehicle silverado --grid "$NG" --mass 2270.0 \
      --label "$L" --out "$OUT" --depth 0.30 --velocity 1.5 --frames 90 \
      --eta 1.0e-3 --floor-friction 0.55 > "$BASE/${L}.log" 2>&1
  echo "RC_${L}=$?" >> "$PROV"
done
echo "WORKERDONE n_grid=$NG seeds ${S0}..${S1} end=$(date -Is)" >> "$PROV"
