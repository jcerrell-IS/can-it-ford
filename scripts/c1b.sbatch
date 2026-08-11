#!/bin/bash
#SBATCH -J j1c1b
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
# 20 minutes, not 6 hours. Job 894731 ran SIX validator arms (four of them g96) in
# 8 minutes wall. This job is TWO g64 arms. The 900-frame g64 arms in that job took
# ~2 min each; at the 1200 cap the worst case is a cap-hit arm at ~3x the settle
# work, so ~6 min for the pair. Padded ~3x over that, not trimmed to it. On a gh
# partition a short request backfills where a long one waits in (Resources).
#SBATCH -t 00:20:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c1b_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/can-it-ford/data/coupling_validation/c1b_%j.err
#
# C1b: C1 with the cube PARTIALLY submerged, to isolate the free surface.
#
# C1 holds the cube entirely below the surface, so the only interface touching the
# body is water-against-solid. C1b raises the SAME cube in the SAME tank at the SAME
# water depth and the SAME rho_box until a stated fraction sits below the surface.
# Still water, and NO boundary planes added or removed relative to C1: the floor
# plane and the four slip walls are C1's, at restitution 0.0 and friction 0.0. The
# free surface is therefore the only thing that changes.
#
# SUBMERSION FRACTION IS 0.80 AND IT IS STATED, NOT IMPLIED.
# --submersion-frac 0.80 DERIVES box_bottom_cells = depth_cells - 0.80*10 = 10.0, so
# --box-bottom-cells is ignored for this variant and cannot silently disagree with the
# stated fraction. The mapping is exact, not tuned: the water is CARVED against the
# cube, so the carve removes exactly what the submerged part displaces and the settled
# surface stays at the nominal column top for any box height whose bottom is under it.
# Verified numerically at box_bottom_cells 8..12, all giving 21.000000 dx. That leaves
# 8 dx of draft and 2 dx (4 particle layers) of freeboard at g64.
#
# WHY 0.80 AND NOT SOMETHING NEARER A HALF. a_ideal = g*(rho_w/rho_box*frac - 1)
# VANISHES at frac = rho_box/rho_w = 0.60, the equilibrium floating draft, where the
# body is neutrally buoyant and a percent error against a_ideal is meaningless. 0.80
# sits 0.20 clear of that and gives a_ideal = +3.2700 m/s^2, exactly half of C1's
# fully submerged +6.5400. Going higher shrinks the freeboard below 2 dx and stops
# resolving the free surface, which is the one thing this run exists to introduce.
#
# THE ANALYTIC REFERENCE IS RECOMPUTED AND IS NOT C1's. A partially submerged cube
# displaces only its wetted part:
#     C1  full     rho_w*g*L^3          = 31298.444315 N   a_ideal = +6.5400 m/s^2
#     C1b 0.80     rho_w*g*L^2*h_sub    = 25038.755452 N   a_ideal = +3.2700 m/s^2
# The run's HEADLINE reference is rebuilt from the MEASURED settled surface, not from
# the requested 0.80, because the request is a placement target and the settled surface
# is what the body actually feels. Both are written to the JSON.
#
# SETTLE CAP RAISED 900 -> 1200. Read the STATUS lines with care: at g64 the C1
# free-rigid arm ALREADY met ratio_target=20 at frame 444 of 900 (c1_rigid_g64.json,
# settle_gate_met true), so the cap was never the binding constraint at this grid. The
# 16.94 / 9.31 pair quoted as the reason to raise it is diagnostics.sound_speed_over_vmax,
# an END-OF-RUN quantity, not the settle gate's ratio. The raise is kept because it is
# free when the gate fires early and because C1b's free surface is a new slosh mode that
# may well settle slower, but it is not expected to change the g64 result on its own.
#
# A CAP HIT IS A DISCARD, NOT A RESULT. settle_gate_met and settle_is_discard are both
# written to the JSON and echoed below. Do not quote a_late_window from an arm whose
# gate did not fire.
#
# The c1_g64_ctrl arm is C1 itself at C1's own published flags (--box-bottom-cells 3),
# rerun in THIS job at THIS revision so C1b is compared against a same-revision number
# rather than against a value from an earlier submission. It also checks that raising
# the cap to 1200 leaves C1 unchanged, since its gate fires at 444 either way.
#
# NO `set -e`. Deliberate, for the reason c1sdf.sbatch:28-32 records: c1only.sbatch had
# none, so four crashed variants still exited 0 and sacct reported COMPLETED. Here every
# run's exit code is captured and echoed as a STATUS line, one crash does not cancel the
# rest, and the job's own exit code means something.
set -u

PY=$WORK/can-it-ford/mpm-engine/.venv/bin/python
SCRIPT=$WORK/can-it-ford/simulation/validate_coupling_force.py
OUT=$WORK/can-it-ford/data/coupling_validation
COMMON="--depth-cells 18 --settle-frames 1200 --measure-substeps 160 --device cuda:0"
mkdir -p "$OUT"

echo "host=$(hostname)  jobid=${SLURM_JOB_ID:-none}"
date -Is
$PY -c "import warp, warpmpm; print('warp', warp.config.version)" 2>&1 | tail -2
echo "script_sha256=$(sha256sum "$SCRIPT" | cut -d' ' -f1)"

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
    grep -E '"(submersion_frac_requested|submersion_frac_realized|submerged_height_dx|freeboard_dx|box_bottom_cells_derived|partially_submerged_at_release|settle_frames_run|settle_gate_met|settle_is_discard|a_ideal|a_headline_first3|a_late_window|err_headline_vs_ideal_pct|err_late_vs_ideal_pct|F_buoy_analytic|err_F_pct|margin_to_neutral_frac|a_ideal_is_degenerate|surface_agreement_column_vs_area_m)"' \
      "$OUT/${tag}.log" | head -30
  fi
}

# Primary: C1b at g64, the canonical resolution of the 17 gated runs.
run c1b_g64 --variant c1b --n-grid 64 --submersion-frac 0.80

# Same-revision control: C1 itself, at C1's own published flags.
run c1_g64_ctrl --variant c1 --n-grid 64 --box-bottom-cells 3

date -Is
echo "ALLDONE_C1B failed=$FAILED"
exit $((FAILED > 0))
