#!/bin/bash
# Rung (b) g96 gated settle: raise the settle cap until settle_gate_met is true.
# Job 3361443 hit its 900-frame cap at c/vmax 9.87 (fixed) and 12.58 (coupled)
# against the 20 required, so BOTH g96 runs there are self-declared discards
# (settle_is_discard true) and the controlled refinement pair does not exist.
#
# settle_pinned breaks early once the gate is met (g64 stopped at 353/900), so a
# high cap costs nothing when it converges and bounds the decay when it does not.
# Coupled runs FIRST: it is the decisive mode, so a short window still yields it.

set -uo pipefail

REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
TAG=${1:-manual}
OUTDIR=/scratch/11603/jcerrell0629/rungb_g96_gated_${TAG}

echo "=== node ==="
hostname
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

PY="$VENV/bin/python"
if [ ! -x "$PY" ]; then echo "VENV MISSING at $VENV"; exit 1; fi

export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
$PY -c "import warpmpm, warp, torch; print('warpmpm', warpmpm.__file__); print('warp', warp.__version__, 'cuda', torch.cuda.is_available())" || exit 1

mkdir -p "$OUTDIR"
cd "$REPO"

# Identical to run_rung_b_settled.sbatch except n-grid fixed at 96 and the cap raised.
for MODE in coupled fixed; do
  echo ""
  echo "############ n_grid=96 mode=$MODE settle-frames=3000 ############"
  date
  timeout 2400 $PY realism_track/rung_b_settled.py \
    --n-grid 96 \
    --mode "$MODE" \
    --rho-box 600.0 \
    --depth-cells 18.0 \
    --box-bottom-cells 8.0 \
    --settle-frames 3000 \
    --steps 120 \
    --out "$OUTDIR/settled_${MODE}_g96_gated.json" 2>&1 | grep -v "^  i=" | tail -40
  echo "exit=$?"
  date
done

echo ""
echo "=== results ==="
ls -la "$OUTDIR"
