#!/bin/bash
#SBATCH -J rungb_coupled
#SBATCH -o realism_track/rungb_%j.out
#SBATCH -e realism_track/rungb_%j.err
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -euo pipefail

REPO=/work/11603/jcerrell0629/vista/can-it-ford
cd "$REPO"

OUTDIR=realism_track/rung_b_$SLURM_JOB_ID
mkdir -p "$OUTDIR"

python3 -c "import warpmpm, warp; print('warpmpm', warpmpm.__file__); print('warp', warp.__version__)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

for NG in 64 96; do
  echo "=== rung b coupled, n_grid=$NG, current bulk 1.5e5 ==="
  python3 simulation/coupling_force/rung_b_coupled.py \
    --n-grid "$NG" \
    --rho-box 600.0 \
    --depth-cells 18.0 \
    --submersion-frac 0.80 \
    --settle 900 \
    --steps 120 \
    --out "$OUTDIR/rung_b_g${NG}.json"
done

echo "=== done, results in $OUTDIR ==="
ls -la "$OUTDIR"
