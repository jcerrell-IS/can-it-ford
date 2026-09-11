#!/bin/bash
set -x
set -o pipefail

ENGINE=/work/11603/jcerrell0629/vista/mpm-engine
VENV=/work/11603/jcerrell0629/vista/.venv/bin/python
BASE=$SCRATCH/render_s1
DRIVER=$BASE/sim_dump.py

cd $ENGINE
hostname
nvidia-smi --query-gpu=name,memory.used --format=csv

$VENV -u $DRIVER --mass 1100 --label small_passenger --out $BASE/m1100 \
  --depth 0.30 --velocity 1.5 --frames 90 --grid 64
echo RC_1100=$?

$VENV -u $DRIVER --mass 1609 --label large_passenger --out $BASE/m1609 \
  --depth 0.30 --velocity 1.5 --frames 90 --grid 64
echo RC_1609=$?

$VENV -u $DRIVER --mass 2337 --label large_4wd --out $BASE/m2337 \
  --depth 0.30 --velocity 1.5 --frames 90 --grid 64
echo RC_2337=$?

echo ALLDONE
