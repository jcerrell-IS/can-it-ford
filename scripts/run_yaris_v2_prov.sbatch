#!/bin/bash
#SBATCH -J yaris_v2_prov
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/logs/yaris_v2_prov_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/logs/yaris_v2_prov_%j.err
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00

set -o pipefail
REPO=/work/11603/jcerrell0629/vista/can-it-ford
VENV=/work/11603/jcerrell0629/vista/.venv
OUT=data/track1_sweep_v2_yaris

echo "host=$(hostname)"
echo "jobid=${SLURM_JOB_ID}"
echo "start=$(date -Is)"
nvidia-smi
cd "$REPO" || exit 1
source "$VENV/bin/activate"
python scripts/ford_sweep_driver.py --vehicle yaris --config v2 --output "$OUT"
rc=$?
echo "end=$(date -Is)"
echo "rc=$rc"
exit $rc
