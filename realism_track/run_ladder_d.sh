#!/bin/bash
# Rung (d): rung (c) plus flow, matching the gated scene's velocity clamp.
# This is the last rung before the gated configuration itself.
set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUT=/scratch/11603/jcerrell0629/ladder_d_3362208
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
mkdir -p "$OUT"; cd "$REPO"
echo "############ RUNG (d) g64 settle-frames=5000 ############"
date
timeout 2700 $PY simulation/validate_coupling_force_ladder.py \
  --rung d --n-grid 64 --settle-frames 5000 \
  --out "$OUT/rung_d_g64_s5000.json" 2>&1 | grep -v Deprecation | tail -8
echo "exit=$?"
date
