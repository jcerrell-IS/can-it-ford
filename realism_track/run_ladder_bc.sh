#!/bin/bash
# The regime ladder proper: rungs (b) and (c) at the GATED scene geometry.
# This is a DIFFERENT experiment from realism_track/rung_b_settled.py. That one floats
# a cube at frac 0.75 to 0.86 mid-water. This one puts the body's bottom face ON the
# floor at frac 0.20 with water depth 0.2944294473039918 m and 4 layers, which are the
# g64_m1100 gated values to the last digit. Predictions are pre-registered in the
# module docstring, so they cannot be fitted after the fact.
set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUT=/scratch/11603/jcerrell0629/ladder_bc_3362208
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
mkdir -p "$OUT"; cd "$REPO"
hostname
for RUNG in b c; do
  echo ""
  echo "############ RUNG ($RUNG) g64 gated-scene geometry ############"
  date
  timeout 2700 $PY simulation/validate_coupling_force_ladder.py \
    --rung "$RUNG" --n-grid 64 \
    --out "$OUT/rung_${RUNG}_g64.json" 2>&1 | grep -v Deprecation | tail -35
  echo "exit=$?"
done
echo "=== results ==="; ls -la "$OUT"
