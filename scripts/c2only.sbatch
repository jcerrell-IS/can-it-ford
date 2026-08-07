#!/bin/bash
#SBATCH -J j1c2
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 01:30:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c2only_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c2only_%j.err
set -u
PY=$WORK/can-it-ford/mpm-engine/.venv/bin/python
SCRIPT=$WORK/can-it-ford/simulation/validate_coupling_force.py
OUT=$WORK/can-it-ford/data/coupling_validation
mkdir -p "$OUT"
echo "node $(hostname)"; date -Is
for NG in 64 96; do
  for OFF in 0 2; do
    echo "########## C2 n_grid=$NG offset=${OFF}dx depth=18 ##########"
    time $PY "$SCRIPT" --variant c2 --n-grid $NG --offset-cells $OFF \
         --depth-cells 18 --settle-frames 600 --max-frames 2500 --device cuda:0 \
         --out "$OUT/c2_g${NG}_off${OFF}.json" > "$OUT/c2_g${NG}_off${OFF}.log" 2>&1
    tail -2 "$OUT/c2_g${NG}_off${OFF}.log"
  done
done
echo ALLDONE_C2
