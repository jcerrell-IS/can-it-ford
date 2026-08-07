#!/bin/bash
#SBATCH -J j1c1sdf
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 06:00:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c1sdf_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c1sdf_%j.err
#
# C1-SDF discriminator: is the sign-inverted C1 result a defect in the free rigid
# coupling, or in the scene/harness?
#
# C1 infers the buoyant force from a free rigid body's acceleration, but that path
# materialises no force: rigid_body_integrate sets v_cm = rigid_linear_mom / M
# (kernels/mpm_utils.py:1434), rigid_linear_mom is the mass-weighted sum of GRID
# velocity gathered at each rigid particle (:1411), and M is the sum of those same
# particle masses (mpm_solver_warp.py:851-853). The body adopts a mass-weighted
# AVERAGE grid velocity. C1-SDF puts the identical cube in the identical water as a
# FIXED collider, which DOES form an impulse, and reads it directly.
#
# Every run below uses the SAME flags c1only.sbatch used for the published C1
# numbers: --depth-cells 18 --box-bottom-cells 3 --settle-frames 900
# --measure-substeps 160. Nothing is tuned. At these settings the cube top sits
# 0.736074 m below the nominal free surface, 5.0 dx at g64 and 7.5 dx at g96, so
# partial submersion is not in play; the analytic target is rho_w*V*g = 31298.4443 N.
#
# NO `set -e`. It is deliberate and it is the fix for a real trap: c1only.sbatch had
# no `set -e` either, so four crashed variants still exited 0 and sacct reported
# COMPLETED. Here every run's exit code is captured and echoed as a STATUS line, and
# the job exits nonzero if any run failed, so the exit code means something AND one
# crash does not cancel the remaining runs.
set -u

PY=$WORK/can-it-ford/mpm-engine/.venv/bin/python
SCRIPT=$WORK/can-it-ford/simulation/validate_coupling_force.py
OUT=$WORK/can-it-ford/data/coupling_validation
COMMON="--depth-cells 18 --box-bottom-cells 3 --settle-frames 900 --measure-substeps 160 --device cuda:0"
mkdir -p "$OUT"

echo "host=$(hostname)  jobid=${SLURM_JOB_ID:-none}"
date -Is
$PY -c "import warp, warpmpm; print('warp', warp.config.version)" 2>&1 | tail -2

FAILED=0
run() {                      # run <tag> <extra args...>
  local tag="$1"; shift
  echo "########## $tag ##########"
  local t0=$SECONDS
  $PY "$SCRIPT" "$@" $COMMON --out "$OUT/${tag}.json" > "$OUT/${tag}.log" 2>&1
  local rc=$?
  local el=$((SECONDS - t0))
  if [ $rc -ne 0 ]; then
    FAILED=$((FAILED + 1))
    echo "STATUS $tag rc=$rc elapsed=${el}s FAILED"
    tail -25 "$OUT/${tag}.log"
  else
    echo "STATUS $tag rc=0 elapsed=${el}s OK"
    grep -E '"(F_steady_tail_mean|F_first3_mean|F_buoy_analytic|err_steady_vs_analytic_pct|err_first3_vs_analytic_pct|F_lateral_over_Fz|fully_submerged_at_measure|a_headline_first3|a_ideal|err_headline_vs_ideal_pct|F_buoy_from_a|err_F_pct)"' \
      "$OUT/${tag}.log" | head -20
  fi
}

# Primary: the mesh-SDF collider, as scoped.
run c1sdf_sdf_g64 --variant c1sdf --collider sdf --n-grid 64
run c1sdf_sdf_g96 --variant c1sdf --collider sdf --n-grid 96

# Control: the free rigid body, same job, same code revision, to put both numbers
# side by side rather than comparing against a value from an earlier submission.
run c1_rigid_g64 --variant c1 --n-grid 64
run c1_rigid_g96 --variant c1 --n-grid 96

# Cross-check: axis-aligned box collider. Same grid-impulse accounting as sdf_wrench
# (solver.py:358 calls sdf_wrench its 6-DOF analogue) but EXACT cube geometry with no
# SDF interpolation, so an sdf-vs-box disagreement isolates the SDF representation.
run c1sdf_box_g64 --variant c1sdf --collider box --n-grid 64
run c1sdf_box_g96 --variant c1sdf --collider box --n-grid 96

date -Is
echo "ALLDONE_C1SDF failed=$FAILED"
exit $((FAILED > 0))
