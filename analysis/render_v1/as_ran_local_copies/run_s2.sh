#!/bin/bash
set -x
set -o pipefail

ENGINE=/work/11603/jcerrell0629/vista/mpm-engine
VENV=/work/11603/jcerrell0629/vista/.venv/bin/python
BASE=/work/11603/jcerrell0629/vista/render_s2
DRIVER=$BASE/sim_standing.py
GRID=${1:-64}

cd $ENGINE
hostname
nvidia-smi --query-gpu=name,memory.used --format=csv

for M in 1100:small_passenger 1609:large_passenger 2337:large_4wd; do
  MASS=${M%%:*}
  LAB=${M##*:}
  $VENV -u $DRIVER --mass $MASS --label $LAB --out $BASE/g${GRID}_m${MASS} \
    --depth 0.30 --velocity 1.5 --frames 90 --grid $GRID \
    --eta 1.0e-3 --floor-friction 0.55
  echo RC_${MASS}=$?
done

echo ALLDONE
