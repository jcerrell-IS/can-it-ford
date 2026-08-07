#!/bin/bash
#SBATCH -J j1smoke
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:20:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/smoke_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/smoke_%j.err
# Smoke only: does the C1-SDF path import, build the cube SDF, pass the engine's
# containment guard, register both collider kinds, and read a wrench? Physics from a
# 6-frame settle is meaningless and must not be quoted.
set -u
PY=$WORK/can-it-ford/mpm-engine/.venv/bin/python
SCRIPT=$WORK/can-it-ford/simulation/validate_coupling_force.py
OUT=$WORK/can-it-ford/data/coupling_validation/smoke
mkdir -p "$OUT"
echo "host=$(hostname)"; date -Is
FAILED=0
for KIND in sdf box; do
  for NG in 64 96; do
    echo "########## smoke $KIND g$NG ##########"
    $PY "$SCRIPT" --variant c1sdf --collider $KIND --n-grid $NG \
        --depth-cells 18 --box-bottom-cells 3 --settle-frames 6 --measure-substeps 6 \
        --device cuda:0 --out "$OUT/smoke_${KIND}_g${NG}.json" > "$OUT/smoke_${KIND}_g${NG}.log" 2>&1
    rc=$?
    if [ $rc -ne 0 ]; then
      FAILED=$((FAILED+1)); echo "STATUS smoke_${KIND}_g${NG} rc=$rc FAILED"
      tail -30 "$OUT/smoke_${KIND}_g${NG}.log"
    else
      echo "STATUS smoke_${KIND}_g${NG} rc=0 OK"
      grep -E '"(sdf_res|sdf_margin_cells|sdf_cell_over_dx|sdf_band_clearance|box_mode|F_steady_tail_mean|F_buoy_analytic|F_lateral_over_Fz|fully_submerged_at_measure|submersion_margin_dx)"' \
        "$OUT/smoke_${KIND}_g${NG}.log" | head -12
    fi
  done
done
date -Is
echo "SMOKE_DONE failed=$FAILED"
exit $((FAILED > 0))
