#!/bin/bash
#SBATCH -J j1ladder
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
# 20 minutes, not 2 hours. Job 895648 ran the whole ladder in 1:44 wall, and on a gh
# partition at 192 running / 60 pending a 2 h request sat in (Resources) while a short
# one backfills. Padded 6x over the measured runtime, not trimmed to it.
#SBATCH -t 00:20:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/ladder_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/ladder_%j.err
#
# Regime ladder, rungs (b)(c)(d) at g64 and g96, plus the live Fix B check.
# Executes docs/REGIME_LADDER_DISPATCH_2026-08-07.md section 3, which executes
# docs/C1_ROOT_CAUSE_2026-08-07.md section 8's own prescribed close.
#
#   (b) partially submerged, still water, all planes restitution 0.0
#   (c) (b) + floor restitution 0.05   (sim_standing.py:133, read live)
#   (d) (c) + sustained inflow at 1.5 m/s (sim_standing.py:190-198, read live)
#
# GEOMETRY IS NOT TUNED. --depth-cells 2 puts the water depth at 2*DX_CANON =
# 0.2944294473039918 m, which is byte-identical to realized_depth_m in ALL 17 gated runs
# (data/all_runs_inventory.csv). grid_lim, dx, h and water_layers then match g64_m1100
# and g96_m1100 exactly, verified 5/5 at both grids before this job was written.
# --box-bottom-cells 0 puts the cube's bottom face on the floor plane, as the gated
# vehicle is. rho_box stays at C1's 600 so the walk from C1 is controlled.
#
# --settle-frames 1200 is the dispatch's own raised cap (its section 3: "Raise frames cap
# to ~1200 if needed. A cap-hit is a discard, not a result."). The gate normally fires far
# earlier; the JSON records settle_gate_met and settle_is_discard either way.
#
# NO `set -e`, deliberately, and for the reason c1sdf.sbatch:28-32 gives: c1only.sbatch
# had none either, so four crashed variants still exited 0 and sacct said COMPLETED. Here
# each run's rc is captured and echoed, one crash does not cancel the rest, and the job's
# own exit code means something.
set -u

PY=$WORK/can-it-ford/mpm-engine/.venv/bin/python
SCRIPT=$WORK/can-it-ford/simulation/validate_coupling_force_ladder.py
OUT=$WORK/can-it-ford/data/coupling_validation
COMMON="--settle-frames 1200 --measure-substeps 160 --flow-frames 60 --device cuda:0"
mkdir -p "$OUT"

echo "host=$(hostname)  jobid=${SLURM_JOB_ID:-none}"
date -Is
$PY -c "import warp, warpmpm; print('warp', warp.config.version)" 2>&1 | tail -2
md5sum "$SCRIPT" $WORK/can-it-ford/simulation/validate_coupling_force.py

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
    tail -30 "$OUT/${tag}.log"
  else
    echo "STATUS $tag rc=0 elapsed=${el}s OK"
    grep -E '"(settle_gate_met|settle_is_discard|submerged_frac|submerged_frac_at_end|a_ideal_partial|a_late_window|a_headline_first3|a_late_as_fraction_of_ideal|v_mean_late|v_final|prediction_v_star_free_rigid|restitution_registered|box_bottom_travel_m|box_bottom_travel_dx|flow_reached_body|matched_gated_run)"' \
      "$OUT/${tag}.log" | head -30
  fi
}

# SMOKE FIRST. This script has never run on a GPU. A 20-frame settle and an 8-substep
# window costs seconds and catches an import error, a changed BoxTank signature, or a
# bad attribute before six full rungs grind through the same fault. Its NUMBERS are
# meaningless (the settle gate cannot be trusted at 20 frames) and are not reported
# anywhere; only its exit code is used. This is the one place the job does fail fast.
echo "########## smoke ##########"
$PY "$SCRIPT" --rung c --n-grid 64 --settle-frames 20 --measure-substeps 8 \
    --device cuda:0 > "$OUT/ladder_smoke.log" 2>&1
smoke_rc=$?
echo "STATUS smoke rc=$smoke_rc"
if [ $smoke_rc -ne 0 ]; then
  echo "SMOKE FAILED, aborting before the six real rungs rather than burning the slot."
  tail -40 "$OUT/ladder_smoke.log"
  date -Is
  echo "ALLDONE_LADDER failed=1 (smoke)"
  exit 1
fi
grep -E '"(restitution_registered|submerged_frac|a_late_window)"' "$OUT/ladder_smoke.log" | head

# Rungs, in ladder order, both grids. Reported separately at each grid and never
# averaged: the 7.59x dV grid ratio in C1_ROOT_CAUSE.md section 9 is still open and
# averaging would hide whatever it is.
run ladder_b_g64 --rung b --n-grid 64
run ladder_b_g96 --rung b --n-grid 96
run ladder_c_g64 --rung c --n-grid 64
run ladder_c_g96 --rung c --n-grid 96
run ladder_d_g64 --rung d --n-grid 64 --velocity 1.5
run ladder_d_g96 --rung d --n-grid 96 --velocity 1.5

# Fix B, end to end against the real Solver class on real particle arrays. Separate rc,
# so a failure here cannot invalidate the rungs above.
echo "########## fixb_live_g64 ##########"
$PY "$SCRIPT" --verify-fix-b-live --n-grid 64 --device cuda:0 \
    > "$OUT/ladder_fixb_live_g64.log" 2>&1
rc=$?
echo "STATUS fixb_live_g64 rc=$rc"
cat "$OUT/ladder_fixb_live_g64.log"
[ $rc -ne 0 ] && FAILED=$((FAILED + 1))

date -Is
echo "ALLDONE_LADDER failed=$FAILED"
exit $((FAILED > 0))
