#!/bin/bash
# Ladder rungs (b) and (c) with the settle cap raised 1200 -> 5000.
# At 1200 both were settle_is_discard true, ratio_c_over_vmax 13.78 and 12.40 against
# the 20 required. This is the same cap defect that made job 3361443's g96 rows discards,
# where raising 900 -> 3000 met the gate at 1030. These runs cost under a minute each, so
# a large cap is nearly free and the gate breaks early if met.
set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUT=/scratch/11603/jcerrell0629/ladder_bc2_3362208
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
mkdir -p "$OUT"; cd "$REPO"
for RUNG in b c; do
  echo ""
  echo "############ RUNG ($RUNG) g64 settle-frames=5000 ############"
  date
  timeout 2400 $PY simulation/validate_coupling_force_ladder.py \
    --rung "$RUNG" --n-grid 64 --settle-frames 5000 \
    --out "$OUT/rung_${RUNG}_g64_s5000.json" 2>&1 | grep -v Deprecation | tail -6
  echo "exit=$?"
done
echo "=== done ==="; ls -la "$OUT"
