#!/bin/bash
#SBATCH -J surfleak96
#SBATCH -o /scratch/11603/jcerrell0629/surfleak96_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/surfleak96_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=$REPO/realism_track/surface_leak_g96_$SLURM_JOB_ID
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
hostname
mkdir -p "$OUTDIR"
cd "$REPO"

echo "############ E: g96 FULL-submersion geometry, direct surface measurement ############"
timeout 3000 $PY realism_track/surface_and_leak.py --n-grid 96 --box-bottom-cells 3.0 \
  --out "$OUTDIR/E_full_g96.json" 2>&1 | tail -25
echo "exit=$?"

echo "############ F: g96 partial, higher settle cap (it failed the gate at 900) ############"
timeout 3600 $PY realism_track/surface_and_leak.py --n-grid 96 --box-bottom-cells 8.0 \
  --settle-frames 1800 --out "$OUTDIR/F_partial_g96.json" 2>&1 | tail -25
echo "exit=$?"

ls -la "$OUTDIR"
