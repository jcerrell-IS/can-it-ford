#!/bin/bash
#SBATCH -J surfrep
#SBATCH -o /scratch/11603/jcerrell0629/surfrep_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/surfrep_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=$REPO/realism_track/surface_leak_repeat_$SLURM_JOB_ID
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
hostname
mkdir -p "$OUTDIR"
cd "$REPO"

echo "############ H: g64 partial REPEAT of run A, reproducibility check ############"
timeout 1800 $PY realism_track/surface_and_leak.py --n-grid 64 --box-bottom-cells 8.0 \
  --out "$OUTDIR/H_partial_g64_repeat.json" 2>&1 | tail -12
echo "exit=$?"

echo "############ I: g64 full REPEAT of run B, reproducibility check ############"
timeout 1800 $PY realism_track/surface_and_leak.py --n-grid 64 --box-bottom-cells 3.0 \
  --out "$OUTDIR/I_full_g64_repeat.json" 2>&1 | tail -12
echo "exit=$?"

echo "############ G: g96 full, settle cap 2400, aiming for a GATE-MET g96 point ############"
timeout 5400 $PY realism_track/surface_and_leak.py --n-grid 96 --box-bottom-cells 3.0 \
  --settle-frames 2400 --out "$OUTDIR/G_full_g96_cap2400.json" 2>&1 | tail -12
echo "exit=$?"

ls -la "$OUTDIR"
