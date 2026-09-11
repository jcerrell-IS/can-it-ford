#!/bin/bash
#SBATCH -J rungb_relax
#SBATCH -o /scratch/11603/jcerrell0629/rungb_relax_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/rungb_relax_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=$REPO/realism_track/rung_b_relax_$SLURM_JOB_ID
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
mkdir -p "$OUTDIR"
cd "$REPO"
hostname
for R in 0.5 0.25; do
  for NG in 64 96; do
    echo "=== n_grid=$NG relax=$R ==="
    timeout 2400 $PY simulation/coupling_force/rung_b_coupled.py \
      --n-grid "$NG" --rho-box 600.0 --depth-cells 18.0 --submersion-frac 0.80 \
      --settle 900 --steps 120 --relax "$R" \
      --out "$OUTDIR/rung_b_g${NG}_relax${R}.json" 2>&1 | grep -E "SETTLED|REFERENCE|COUPLER|WARNING|^  t=" | tail -8
  done
done
ls -la "$OUTDIR"
