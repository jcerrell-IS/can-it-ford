#!/bin/bash
#SBATCH -J rungb_a100
#SBATCH -o /scratch/11603/jcerrell0629/rungb_a100_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/rungb_a100_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail

REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=$REPO/realism_track/rung_b_ls6_$SLURM_JOB_ID

echo "=== node ==="
hostname
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

if [ ! -x "$VENV/bin/python" ]; then
  echo "=== creating venv $VENV ==="
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip
  echo "=== installing warp-lang, torch, numpy ==="
  "$VENV/bin/pip" install -q "warp-lang>=1.10.1,<2" "torch>=2.4" "numpy>=1.26" || {
    echo "PIP INSTALL FAILED"; exit 1; }
fi

PY="$VENV/bin/python"
echo "=== versions ==="
$PY -c "import warp, torch, numpy; print('warp', warp.__version__); print('torch', torch.__version__, 'cuda', torch.cuda.is_available()); print('numpy', numpy.__version__)" || exit 1

export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
echo "=== warpmpm import check ==="
$PY -c "import warpmpm; print('warpmpm', warpmpm.__file__)" || exit 1

mkdir -p "$OUTDIR"
cd "$REPO"

echo "=== rigid-body unit tests first ==="
$PY simulation/coupling_force/test_rigid_body.py 2>&1 | tail -20

for NG in 64 96; do
  echo "=== rung b coupled, n_grid=$NG ==="
  timeout 2400 $PY simulation/coupling_force/rung_b_coupled.py \
    --n-grid "$NG" \
    --rho-box 600.0 \
    --depth-cells 18.0 \
    --submersion-frac 0.80 \
    --settle 900 \
    --steps 120 \
    --out "$OUTDIR/rung_b_g${NG}.json" 2>&1 | tail -40
  echo "exit=$?"
done

echo "=== results ==="
ls -la "$OUTDIR"
for f in "$OUTDIR"/*.json; do [ -f "$f" ] && echo "--- $f ---" && head -c 1200 "$f"; done
