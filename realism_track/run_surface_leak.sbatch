#!/bin/bash
#SBATCH -J surfleak
#SBATCH -o /scratch/11603/jcerrell0629/surfleak_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/surfleak_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=$REPO/realism_track/surface_leak_$SLURM_JOB_ID
PY="$VENV/bin/python"
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
hostname
mkdir -p "$OUTDIR"
cd "$REPO"

echo "############ A: partial submersion, baseline bulk, surface+leak audit ############"
timeout 1800 $PY realism_track/surface_and_leak.py --n-grid 64 --box-bottom-cells 8.0 \
  --out "$OUTDIR/A_partial_g64_bulk1.5e5.json" 2>&1 | tail -25
echo "exit=$?"

echo "############ B: FULL submersion control, baseline bulk ############"
timeout 1800 $PY realism_track/surface_and_leak.py --n-grid 64 --box-bottom-cells 3.0 \
  --out "$OUTDIR/B_full_g64_bulk1.5e5.json" 2>&1 | tail -25
echo "exit=$?"

echo "############ C: partial, bulk x10 (c=40.6), leak prediction test ############"
timeout 2400 $PY realism_track/surface_and_leak.py --n-grid 64 --box-bottom-cells 8.0 \
  --bulk 1.5e6 --out "$OUTDIR/C_partial_g64_bulk1.5e6.json" 2>&1 | tail -25
echo "exit=$?"

echo "############ D: partial, bulk x100 (c=128.5), leak prediction test ############"
timeout 3600 $PY realism_track/surface_and_leak.py --n-grid 64 --box-bottom-cells 8.0 \
  --bulk 1.5e7 --out "$OUTDIR/D_partial_g64_bulk1.5e7.json" 2>&1 | tail -25
echo "exit=$?"

ls -la "$OUTDIR"
