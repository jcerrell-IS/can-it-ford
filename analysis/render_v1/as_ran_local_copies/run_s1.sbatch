#!/bin/bash
#SBATCH -J yaris_s1
#SBATCH -A BCS20003
#SBATCH -p gh-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:30:00
#SBATCH -o /work/11603/jcerrell0629/vista/logs/yaris_s1_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/logs/yaris_s1_%j.err

set -x
set -o pipefail

ENGINE=/work/11603/jcerrell0629/vista/mpm-engine
VENV=/work/11603/jcerrell0629/vista/.venv/bin/python
BASE=$SCRATCH/render_s1
DRIVER=$SCRATCH/render_s1/sim_dump.py

cd $ENGINE
hostname
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv

mkdir -p $BASE

$VENV -u $DRIVER --mass 1100 --label small_passenger --out $BASE/m1100 \
  --depth 0.30 --velocity 1.5 --frames 90 --grid 64

$VENV -u $DRIVER --mass 1609 --label large_passenger --out $BASE/m1609 \
  --depth 0.30 --velocity 1.5 --frames 90 --grid 64

$VENV -u $DRIVER --mass 2337 --label large_4wd --out $BASE/m2337 \
  --depth 0.30 --velocity 1.5 --frames 90 --grid 64

echo ALLDONE_EXIT=$?
