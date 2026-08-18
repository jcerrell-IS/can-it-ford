#!/bin/bash
# ============================================================================
# THREE-CLASS DEMONSTRATION AT MATCHED CONDITIONS.  NON-CANONICAL.
#
# Produces the first physically comparable compact_sedan / midsize_suv /
# large_4wd result on the real converged hulls, with the cross-vehicle
# resolution confound actually controlled.
#
# NON-CANONICAL, AND IT STAYS THAT WAY. Writes only inside $BASE under
# $SCRATCH. Touches neither data/all_runs_inventory.csv nor
# renders/yaris_render_s1/gates_results_all_runs.json, both of which are
# Yaris-only. It never writes into an existing run directory: register item 16
# exists because job 866887 overwrote g48/g96 run directories on 2026-07-26 and
# made six canonical margins permanently unverifiable.
#
# ---------------------------------------------------------------------------
# WHY THREE ARMS
#
#   Arm S  shared n_grid = 96, the way a cross-vehicle sweep would naively be
#          run, and the way rs_sweep_v2 ran. Kept for continuity and because it
#          is the thing being falsified. NEVER averaged with Arm M.
#   Arm M  matched dx. THE PRIMARY ARM.
#   Arm D  matched dx with bulk density held equal across the three hulls.
#          Rules DENSITY out. It does NOT separate geometry from mass: holding
#          density fixed forces mass to scale with volume. That separation needs
#          the mass swap in run_three_class_massswap.sh.
#
# THE CONFOUND ARM S CARRIES, measured, not asserted (analysis/three_class_matched_grid.py):
#   sim_standing.py:160 sets lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth) from the
#   LOADED HULL, and solver.py:53-54 sets dx = lim/n_grid. So at a shared n_grid=96:
#       yaris      dx 0.0981431  realized depth 0.294429  6 water layers  depth/dx 3.0
#       rogue      dx 0.1087764  realized depth 0.326329  6 water layers  depth/dx 3.0
#       silverado  dx 0.1361243  realized depth 0.272249  4 water layers  depth/dx 2.0
#   That is a 38.70 percent dx spread and a 19.86 percent realized-depth spread,
#   and the Silverado is resolved across the water with TWO cells where the other
#   two get three. It is not one experiment at three sizes.
#
# THE MATCHED ARM, same source:
#       yaris      n_grid 111  dx 0.0848806  realized depth 0.297082  7 layers
#       rogue      n_grid 123  dx 0.0848987  realized depth 0.297145  7 layers
#       silverado  n_grid 154  dx 0.0848567  realized depth 0.296998  7 layers
#   dx spread 0.0494 percent, realized-depth spread 0.0494 percent, depth/dx
#   exactly 3.500 for all three. An EXACT common dx does not exist for any integer
#   triple, because the domain edges are measured floats; 0.0494 percent is what
#   was achieved, and every run stamps its own dx in summary.json.
#
# WHAT MATCHING dx DOES NOT FIX, stated here so it is not discovered later. The
# domain edge scales with the hull, so tank width, water volume and the fetch
# from the FIXED 1.5 m inflow band (sim_standing.py:155,:223) to the vehicle all
# still differ:
#       yaris      free span  8.7427 m  water 22.707 m3  fetch 3.8135 m
#       rogue      free span  9.7634 m  water 28.325 m3  fetch 4.4259 m
#       silverado  free span 12.3891 m  water 45.586 m3  fetch 6.0013 m
# Matching dx fixes RESOLUTION. It does not make the three tanks the same tank.
#
# ---------------------------------------------------------------------------
# MASSES. Two defensible sets exist and they are NOT interchangeable.
# Arm S and Arm M use the VEHICLE-SPECIFIC figure, which pairs each real hull
# with that real vehicle's own mass, and which is what rs_sweep_v2 used:
#       yaris      1100.0  deck header line 28, and vehicle_params.py mass_kg
#       rogue      1571.3  web-sourced; the Rogue deck states NO mass at all
#       silverado  2270.0  deck header line 28
# The AR&R CLASS figures are the labelled alternative: 1100 / 1609 / 2337.
# Every run's summary.json carries mass_alt_kg and mass_alt_source, so both
# survive whichever was used.
#
# PROVENANCE HIERARCHY, deliberately NOT inherited from the prior write-up.
# docs/MULTIGEOM_VALIDATION_2026-08-11.md labels 2337 "primary" for the
# Silverado and demotes 2270 to mass_alt_kg. That inverts the hierarchy: 2270 is
# the Silverado deck's own mass, 2337 is the AR&R large_4wd CLASS figure and is
# not this vehicle's mass. 2337 is a fine number to run; it is not the
# stronger-provenance one, and this file does not call it that.
#
# 1571.3 traced live 2026-08-14 to renders/yaris_render_s1/sim_standing.py:54,
# where it is mass_alt_kg. It is a cars.com 2020 Rogue FWD S curb weight of
# 3464 lb. Note 3464 lb is 1571.24 kg, so the trailing .3 is a conversion
# rounding artifact, and a live NHTSA pull puts the real trims at FWD 1550 /
# AWD 1610, so 1571.3 pins to NO published trim. Recorded, not silently fixed.
#
# ARM D, the equal-density control. Masses are rho_ref * hull_m3 with
# rho_ref = 1100/3.542739 = 310.494225 kg/m3, the canonical Yaris working
# density, so the Yaris arm is 1100 kg by construction:
#       yaris      1100.000    rogue  1537.052    silverado  2472.181
# LABELLED ASSUMPTION, reversible: this equalises mass/HULL volume, but the
# solver's own density is mass/SOLID volume, where solid volume is the
# solidified particle cloud (n_particles*h^3). fill_ratio sits at 0.994 to 1.026
# across the 17 gated runs, so the realized densities should agree to about
# +/-1.6 percent rather than exactly. The achieved realized_rho is read back
# from each summary.json and reported; it is not assumed.
#
# ARM D ALSO CONTAINS ITS OWN NO-FORCING CONTROL. D_yaris is bit-for-bit the
# same configuration as M_yaris (n_grid 111, 1100 kg). Register item 17 records
# this stack as NON-DETERMINISTIC at fixed configuration, and register J-item
# notes determinism_identical reported True on six runs that differ. Running the
# identical config twice IN THE SAME JOB, same node, same driver, measures the
# run-to-run draw directly, which is the only way to know whether a
# cross-vehicle difference is larger than noise. Compare the two metrics.csv
# directly; do not read determinism_identical.
#
# NOT WIRED, DELIBERATELY: inertia_kg_m2 and cg_height_m. CLAUDE.md item 4. The
# solver already derives a better tensor from the real hull particle cloud
# (kernels/mpm_solver_warp.py:859-871); the box tensor overstates every
# principal moment by +16.3 to +26.1 percent, and the documented (L,W,H)->(x,y,z)
# convention is transposed against this scene, which puts the long axis on Y.
#
# ENGINE: warpmpm. NOT Genesis.
# ============================================================================
set -uo pipefail

REPO=/scratch/11603/jcerrell0629/canitford_track1b/can-it-ford
# Two mpm-engine trees exist on /work. sim_standing.py needs solidify_watertight,
# which vista/can-it-ford/mpm-engine's warpmpm.vehicle does NOT have. This is the
# tree the g64 anchor runs (job 896273) and rs_sweep_v2 both resolved to.
ENGINE=/work/11603/jcerrell0629/vista/mpm-engine/src
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env

TAG=${1:-2026-08-14}
BASE=/scratch/11603/jcerrell0629/three_class_matched_${TAG}

if [ -e "$BASE" ]; then
    echo "REFUSING: $BASE already exists. This script never writes into an existing"
    echo "run directory (register item 16). Pass a different TAG."
    exit 3
fi
mkdir -p "$BASE"

PY="$VENV/bin/python"
export PYTHONPATH="$ENGINE:$REPO:${PYTHONPATH:-}"
DRIVER="$REPO/renders/yaris_render_s1/sim_standing.py"
PROV="$BASE/00_provenance.txt"

# Verbatim from run_rs_sweep.sh, which took it from
# scripts/class_specific_2026-08-08.sbatch, which took it from run_s2.sh as-ran.
# depth 0.30 / velocity 1.5 is the pair behind g48/g64/g96_m{1100,1609,2337}.
COMMON="--depth 0.30 --velocity 1.5 --frames 90 --eta 1.0e-3 --floor-friction 0.55"

{
  echo "start=$(date -Is) host=$(hostname)"
  echo "job_id=${SLURM_JOB_ID:-none} partition=${SLURM_JOB_PARTITION:-none}"
  echo "NON-CANONICAL companion experiment. Yaris-only canonical stores untouched."
  echo "engine=warpmpm (NOT Genesis)  engine_src=$ENGINE"
  echo "venv=$VENV"
  echo "driver sha256: $(sha256sum "$DRIVER")"
  echo "runner sha256: $(sha256sum "$0")"
  echo "common: $COMMON"
  echo "--- hull sha256 at the paths actually read ---"
  V=/work/11603/jcerrell0629/vista/can-it-ford/vehicle_geometry_research
  sha256sum "$V/yaris_coarse_v1l_watertight.ply" \
            "$V/rogue_g96_pd8_coarse_watertight.ply" \
            "$V/silverado_g96_pd8_coarse_watertight.ply"
  echo "--- gpu ---"
  nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
} >> "$PROV" 2>&1

run_one() {
    local label="$1" vehicle="$2" ngrid="$3" mass="$4" arm="$5" note="$6"
    local out="$BASE/$label"
    mkdir -p "$out"
    echo "=== $(date -Is) $label  arm=$arm vehicle=$vehicle n_grid=$ngrid mass=$mass"
    "$PY" "$DRIVER" --vehicle "$vehicle" --grid "$ngrid" --mass "$mass" \
        --label "$label" --out "$out" $COMMON > "$BASE/${label}.log" 2>&1
    local rc=$?
    {
      echo "--- $label ---"
      echo "ARM=$arm VEHICLE=$vehicle N_GRID=$ngrid MASS=$mass NOTE=$note"
      echo "RC_${label}=$rc"
      /usr/bin/grep -h -E '^(PREFLIGHT|INSTRUMENT|SUBSTEP_TERMS|DETERMINISM|SCENARIO|grid )' \
          "$BASE/${label}.log" 2>/dev/null | sed 's/^/    /'
    } >> "$PROV" 2>&1
    if [ $rc -ne 0 ]; then
        echo "  FAILED rc=$rc, tail:"; tail -20 "$BASE/${label}.log"
    fi
    return $rc
}

# --- Arm S: shared n_grid = 96. The confound, kept for continuity. -----------
run_one S_yaris_n96_m1100      yaris      96  1100.0  S "shared n_grid, deck mass"
run_one S_rogue_n96_m1571p3    rogue      96  1571.3  S "shared n_grid, web mass"
run_one S_silverado_n96_m2270  silverado  96  2270.0  S "shared n_grid, deck mass"

# --- Arm M: matched dx. PRIMARY. --------------------------------------------
run_one M_yaris_n111_m1100      yaris      111 1100.0  M "matched dx, deck mass"
run_one M_rogue_n123_m1571p3    rogue      123 1571.3  M "matched dx, web mass"
run_one M_silverado_n154_m2270  silverado  154 2270.0  M "matched dx, deck mass"

# --- Arm D: matched dx, equal bulk density. Geometry-vs-mass control. -------
# D_yaris repeats M_yaris exactly: the run-to-run determinism control.
run_one D_yaris_n111_m1100      yaris      111 1100.000 D "REPEAT of M_yaris, determinism control"
run_one D_rogue_n123_m1537p1    rogue      123 1537.052 D "equal-density 310.494225 * 4.950341"
run_one D_silverado_n154_m2472p2 silverado 154 2472.181 D "equal-density 310.494225 * 7.962083"

echo "ALLDONE end=$(date -Is)" >> "$PROV"
echo "=== finished $(date -Is), results in $BASE"
ls -la "$BASE"
