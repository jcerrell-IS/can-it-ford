#!/bin/bash
#SBATCH -J v3_sweep
#SBATCH -o v3_sweep_%j.out
#SBATCH -e v3_sweep_%j.err
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -o pipefail

REPO=$STOCKYARD/vista/can-it-ford
VENV=$STOCKYARD/vista/.venv

echo "host=$(hostname)"
echo "jobid=${SLURM_JOB_ID}"
echo "start=$(date -Is)"

nvidia-smi

cd "$REPO" || exit 1

"$VENV/bin/python" scripts/ford_sweep_driver.py --config v3
rc=$?

echo "end=$(date -Is)"
echo "rc=$rc"

exit $rc
