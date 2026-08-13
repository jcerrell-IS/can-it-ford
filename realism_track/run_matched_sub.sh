#!/bin/bash
# Remove the one stated confound in the J1b result.
#
# The four gate-met rung-b rows compare g64 at realized frac_submerged 0.754 against
# g96 at 0.844, so the refinement comparison has a second variable moving. This raises
# g64's water so its SETTLED surface matches g96's, making the pair a clean refinement
# test at matched submersion.
#
# Sizing, derived not guessed. Water depth = depth_cells * DX_CANON, and DX_CANON is a
# fixed constant equal to the g64 dx of 0.147215 m (18.0 * 0.147215 = 2.6499 m, the
# grid-independent depth the register records). g64 settled to surface 2.730499 and g96
# to 2.861478, a shortfall of 0.130979 m, which is 0.8897 cells. First probe therefore
# runs depth-cells 18.89. If the realized frac overshoots or undershoots 0.8437, the
# printed GEOM line gives the next correction directly.

set -uo pipefail

REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
DC=${1:-18.89}
TAG=${2:-probe}
OUTDIR=/scratch/11603/jcerrell0629/rungb_matched_${TAG}

echo "=== node ==="; hostname
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"

mkdir -p "$OUTDIR"
cd "$REPO"

for MODE in coupled fixed; do
  echo ""
  echo "############ n_grid=64 mode=$MODE depth-cells=$DC (target frac 0.8437) ############"
  date
  timeout 2400 $PY realism_track/rung_b_settled.py \
    --n-grid 64 \
    --mode "$MODE" \
    --rho-box 600.0 \
    --depth-cells "$DC" \
    --box-bottom-cells 8.0 \
    --settle-frames 3000 \
    --steps 120 \
    --out "$OUTDIR/matched_${MODE}_g64_dc${DC}.json" 2>&1 | grep -v "^  i=" | tail -30
  echo "exit=$?"
done

echo "=== results ==="; ls -la "$OUTDIR"
