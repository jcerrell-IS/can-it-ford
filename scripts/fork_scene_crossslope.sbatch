#!/bin/bash
# Cross-slope sensitivity, formulation G (tilted gravity, bed-aligned frame).
# Dispatch 10. LS6 BATCH ONLY: idev burned 98.5-99.1% of Vista node-hours and
# 95 of 184 interactive jobs ended in TIMEOUT; LS6 shows 0 batch timeouts.
#
# FOUR ARMS. 0 and 1 are the SAME config at the SAME seed, so their spread is
# the noise floor. Register C-7: determinism_identical reports True on six runs
# that differ, so the flag cannot supply the noise floor and a repeated arm must.
#
# WRITES ONLY to a NEW $SCRATCH directory. Touches no canonical store, no
# existing run directory, and no other dispatch's branch.
#SBATCH -J d10_xslope
#SBATCH -o /scratch/11603/jcerrell0629/d10_xslope_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/d10_xslope_%j.err
#SBATCH -p gpu-a100
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -uo pipefail

VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
ENGINE=/work/11603/jcerrell0629/vista/can-it-ford/mpm-engine/src
FORK=/scratch/11603/jcerrell0629/fork_scene_2026-08-14
PLY=/work/11603/jcerrell0629/vista/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply
OUT=$FORK/results_$SLURM_JOB_ID

echo "=== node ==="
hostname
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

echo "=== provenance, so the result can be traced without trusting this script ==="
echo "engine pinned SHA:"; git -C "$(dirname $ENGINE)" rev-parse HEAD 2>&1 | head -1
echo "yaris ply sha256:";  sha256sum "$PLY" | cut -d' ' -f1

PY="$VENV/bin/python"
export PYTHONPATH="$ENGINE:$FORK:${PYTHONPATH:-}"

echo "=== versions ==="
$PY -c "import warp, torch, numpy, trimesh; print('warp', warp.__version__); print('torch', torch.__version__, 'cuda', torch.cuda.is_available()); print('numpy', numpy.__version__); print('trimesh', trimesh.__version__)" || exit 1
$PY -c "import warpmpm; print('warpmpm', warpmpm.__file__)" || exit 1

mkdir -p "$OUT"
cd "$FORK"

echo "=== cross-slope arms ==="
$PY simulation/fork_scene/runner.py --ply "$PLY" --outdir "$OUT" --frames 90 --n-grid 64
RC=$?
echo "=== runner rc=$RC ==="
ls -la "$OUT"
exit $RC
