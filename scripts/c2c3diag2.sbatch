#!/bin/bash
#SBATCH -J j1c2c3d2
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:30:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c2c3diag2_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c2c3diag2_%j.err
set -u

PY=$WORK/can-it-ford/mpm-engine/.venv/bin/python
SCRIPT=$WORK/can-it-ford/simulation/validate_coupling_force.py
OUT=$WORK/can-it-ford/data/coupling_validation
COMMON="--device cuda:0"
mkdir -p "$OUT"

echo "host=$(hostname)  jobid=${SLURM_JOB_ID:-none}"
date -Is

FAILED=0
run() {
  local tag="$1"; shift
  echo "########## $tag ##########"
  local t0=$SECONDS
  $PY "$SCRIPT" "$@" $COMMON --out "$OUT/${tag}.json" > "$OUT/${tag}.log" 2>&1
  local rc=$?
  local el=$((SECONDS - t0))
  if [ $rc -ne 0 ]; then
    FAILED=$((FAILED + 1))
    echo "STATUS $tag rc=$rc elapsed=${el}s FAILED"
    tail -15 "$OUT/${tag}.log"
    echo "-- com_frame trace, if any --"
    grep "^com_frame" "$OUT/${tag}.log" | tail -20
  else
    echo "STATUS $tag rc=0 elapsed=${el}s OK"
    tail -15 "$OUT/${tag}.log"
  fi
}

run c2_diag2_g64_off0 --variant c2 --n-grid 64 --rho-box 600.0 --depth-cells 18 --offset-cells 0 --settle-frames 60 --max-frames 200
run c3_fixed2_g64 --variant c3 --n-grid 64 --box-bottom-cells 3 --depth-cells 18

date -Is
echo "ALLDONE_C2C3DIAG2 failed=$FAILED"
exit $((FAILED > 0))
