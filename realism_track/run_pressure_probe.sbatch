#!/bin/bash
#SBATCH -J press_probe
#SBATCH -o /scratch/11603/jcerrell0629/press_probe_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/press_probe_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail

REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
OUTDIR=$REPO/realism_track/pressure_probe_$SLURM_JOB_ID

hostname
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

PY="$VENV/bin/python"
if [ ! -x "$PY" ]; then echo "VENV MISSING at $VENV"; exit 1; fi
export PYTHONPATH="$REPO/mpm-engine/src:$REPO:${PYTHONPATH:-}"
mkdir -p "$OUTDIR"
cd "$REPO"

for NG in 64 96; do
  echo ""
  echo "############ pressure profile, n_grid=$NG ############"
  timeout 2400 $PY realism_track/pressure_profile.py \
    --n-grid "$NG" --box-bottom-cells 3.0 --depth-cells 18.0 \
    --settle-frames 900 --nbins 18 \
    --out "$OUTDIR/pressure_g${NG}.json" 2>&1 | tail -40
  echo "exit=$?"
done

for PC in off on; do
  echo ""
  echo "############ settle cost, precompress=$PC, n_grid=64 ############"
  timeout 2400 $PY realism_track/precompress_settle.py \
    --n-grid 64 --precompress "$PC" --box-bottom-cells 3.0 \
    --depth-cells 18.0 --settle-frames 900 \
    --out "$OUTDIR/precompress_${PC}_g64.json" 2>&1 | tail -25
  echo "exit=$?"
done

echo ""
echo "=== results ==="
ls -la "$OUTDIR"
