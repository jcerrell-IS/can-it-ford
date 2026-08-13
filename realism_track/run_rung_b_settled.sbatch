#!/bin/bash
#SBATCH -J rungb_settled
#SBATCH -o /scratch/11603/jcerrell0629/rungb_settled_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/rungb_settled_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail

REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=$REPO/realism_track/rung_b_settled_$SLURM_JOB_ID

echo "=== node ==="
hostname
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

PY="$VENV/bin/python"
if [ ! -x "$PY" ]; then echo "VENV MISSING at $VENV"; exit 1; fi

export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
$PY -c "import warpmpm, warp, torch; print('warpmpm', warpmpm.__file__); print('warp', warp.__version__, 'cuda', torch.cuda.is_available())" || exit 1

mkdir -p "$OUTDIR"
cd "$REPO"

for NG in 64 96; do
  for MODE in fixed coupled; do
    echo ""
    echo "############ n_grid=$NG mode=$MODE (reference geometry, gated settle) ############"
    timeout 3000 $PY realism_track/rung_b_settled.py \
      --n-grid "$NG" \
      --mode "$MODE" \
      --rho-box 600.0 \
      --depth-cells 18.0 \
      --box-bottom-cells 8.0 \
      --settle-frames 900 \
      --steps 120 \
      --out "$OUTDIR/settled_${MODE}_g${NG}.json" 2>&1 | grep -v "^  i=" | tail -40
    echo "exit=$?"
  done
done

echo ""
echo "=== results ==="
ls -la "$OUTDIR"
