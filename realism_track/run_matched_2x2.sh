#!/bin/bash
# Complete a 2x2 matched-submersion design so grid and submersion are separated.
#
# Existing gate-met points:
#   g64 dc18.00 frac 0.7540 | g96 dc18.00 frac 0.8437 | g64 dc18.89 frac 0.8567
# Missing: g96 at the LOW submersion, and a g64 point landing ON 0.8437 rather than
# 0.8567 so the high-submersion comparison is direct instead of interpolated.
#
# Sizing from the measured g64 sensitivity: dc 18.00 -> 18.89 moved frac 0.7540 ->
# 0.8567, so 0.1154 frac per cell.
#   g64 target 0.8437: 18.89 - (0.8567-0.8437)/0.1154 = 18.78
#   g96 target 0.7540: 18.00 - (0.8437-0.7540)/0.1154 = 17.22   (g64 slope reused;
#   if g96's sensitivity differs the realized frac will say so and it is still a
#   valid gate-met point, just not exactly on target)

set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=/scratch/11603/jcerrell0629/rungb_matched_2x2
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
mkdir -p "$OUTDIR"; cd "$REPO"

run () {  # n_grid depth_cells mode
  echo ""
  echo "############ g$1 dc=$2 mode=$3 ############"
  date
  timeout 2400 $PY realism_track/rung_b_settled.py \
    --n-grid "$1" --mode "$3" --rho-box 600.0 \
    --depth-cells "$2" --box-bottom-cells 8.0 \
    --settle-frames 3000 --steps 120 \
    --out "$OUTDIR/m_g$1_dc$2_$3.json" 2>&1 | grep -v "^  i=" | tail -12
  echo "exit=$?"
}

# g64 landing on the g96 submersion, both modes. Cheap, do first.
run 64 18.78 coupled
run 64 18.78 fixed
# g96 dropped to the g64 submersion, both modes. This is the expensive pair.
run 96 17.22 coupled
run 96 17.22 fixed

echo "=== results ==="; ls -la "$OUTDIR"
