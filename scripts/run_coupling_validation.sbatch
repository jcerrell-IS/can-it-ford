#!/bin/bash
#SBATCH -J j1coupling
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 01:30:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/slurm_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/slurm_%j.err

set -u

PY=$WORK/can-it-ford/mpm-engine/.venv/bin/python
SCRIPT=$WORK/can-it-ford/simulation/validate_coupling_force.py
OUT=$WORK/can-it-ford/data/coupling_validation
mkdir -p "$OUT"

echo "node   : $(hostname)"
echo "started: $(date -Is)"
echo "script : $(sha256sum $SCRIPT)"
echo "solver : $(cd $WORK/can-it-ford/mpm-engine && git rev-parse HEAD)"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

stamp () { echo; echo "########## $* ##########"; date -Is; }

for NG in 64 96; do
  stamp "C0 dry drop n_grid=$NG"
  time $PY "$SCRIPT" --variant c0 --n-grid $NG --device cuda:0 \
       --out "$OUT/c0_g${NG}.json" > "$OUT/c0_g${NG}.log" 2>&1
  tail -3 "$OUT/c0_g${NG}.log"
done

for NG in 64 96; do
  for OFF in 0 2; do
    stamp "C2 equilibrium draft n_grid=$NG offset=${OFF}dx"
    time $PY "$SCRIPT" --variant c2 --n-grid $NG --offset-cells $OFF \
         --depth-cells 18 --settle-frames 600 --max-frames 2500 --device cuda:0 \
         --out "$OUT/c2_g${NG}_off${OFF}.json" > "$OUT/c2_g${NG}_off${OFF}.log" 2>&1
    tail -3 "$OUT/c2_g${NG}_off${OFF}.log"
  done
done

for NG in 64 96; do
  stamp "C1 submerged acceleration n_grid=$NG"
  time $PY "$SCRIPT" --variant c1 --n-grid $NG --depth-cells 18 \
       --box-bottom-cells 8 --settle-frames 900 --measure-substeps 160 --device cuda:0 \
       --out "$OUT/c1_g${NG}.json" > "$OUT/c1_g${NG}.log" 2>&1
  tail -3 "$OUT/c1_g${NG}.log"
done

stamp "C3 neutral buoyancy null n_grid=64"
time $PY "$SCRIPT" --variant c3 --n-grid 64 --depth-cells 18 \
     --box-bottom-cells 8 --settle-frames 900 --measure-substeps 160 --device cuda:0 \
     --out "$OUT/c3_g64.json" > "$OUT/c3_g64.log" 2>&1
tail -3 "$OUT/c3_g64.log"

echo
echo "finished: $(date -Is)"
echo ALLDONE
