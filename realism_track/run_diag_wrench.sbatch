#!/bin/bash
#SBATCH -J diagwrench
#SBATCH -o /scratch/11603/jcerrell0629/diagwrench_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/diagwrench_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=$REPO/realism_track/diag_wrench_$SLURM_JOB_ID
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
mkdir -p "$OUTDIR"
cd "$REPO"
hostname
for MODE in fixed pose_zero_vel pose_full; do
  for NG in 64 96; do
    echo "######## mode=$MODE n_grid=$NG ########"
    timeout 2400 $PY realism_track/diag_wrench_fixed_pose.py \
      --n-grid "$NG" --mode "$MODE" --settle 900 --steps 120 \
      --out "$OUTDIR/diag_${MODE}_g${NG}.json" 2>&1 | grep -vE "DeprecationWarning|^Warp |Particles initialized" | tail -16
  done
done
ls -la "$OUTDIR"
