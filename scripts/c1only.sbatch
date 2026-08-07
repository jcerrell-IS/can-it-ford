#!/bin/bash
#SBATCH -J j1c1
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 01:30:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c1only_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c1only_%j.err
set -u
PY=$WORK/can-it-ford/mpm-engine/.venv/bin/python
SCRIPT=$WORK/can-it-ford/simulation/validate_coupling_force.py
OUT=$WORK/can-it-ford/data/coupling_validation
mkdir -p "$OUT"
date -Is
for NG in 64 96; do
  echo "########## C1 n_grid=$NG spawn-submerged ##########"
  time $PY "$SCRIPT" --variant c1 --n-grid $NG --depth-cells 18 \
       --box-bottom-cells 3 --settle-frames 900 --measure-substeps 160 --device cuda:0 \
       --out "$OUT/c1_g${NG}.json" > "$OUT/c1_g${NG}.log" 2>&1
  tail -2 "$OUT/c1_g${NG}.log"
done
echo "########## C3 neutral null ##########"
time $PY "$SCRIPT" --variant c3 --n-grid 64 --depth-cells 18 \
     --box-bottom-cells 3 --settle-frames 900 --measure-substeps 160 --device cuda:0 \
     --out "$OUT/c3_g64.json" > "$OUT/c3_g64.log" 2>&1
tail -2 "$OUT/c3_g64.log"
echo ALLDONE_C1
