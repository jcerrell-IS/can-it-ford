#!/bin/bash
# ============================================================================
# ARM X, THE MASS-SWAP: completes a 2x2 factorial in (hull, mass) at matched dx.
# NON-CANONICAL.
#
# WHY THIS EXISTS. The 2026-08-14 three-class set
# (docs/THREE_CLASS_MATCHED_2026-08-14.md) established that removing the
# resolution confound flips the large_4wd verdict SLIDE -> STUCK, and it ruled
# density out. What it could NOT do is say whether the class ordering follows
# MASS or DISPLACED VOLUME, because mass and volume are RANK-CORRELATED in every
# arm that was run, and PROPORTIONAL by construction in the equal-density arm D.
# That is the question CLAUDE.md A-3 turns on (Smith/Modra/Felder 2019,
# Martinez-Gomariz 2017, Arrighi 2015: thresholds depend on displaced volume,
# underbody shape, wheelbase, track and CoM, not mass alone), and the three hulls
# differ 2.25x in displaced volume while their densities span only 285 to 317,
# which is exactly the regime where a mass-only and a geometry-aware account
# diverge.
#
# THE DESIGN. Two runs here, plus two that already exist, close the square:
#
#                        mass 1100 kg              mass 2270 kg
#   Yaris hull 3.54 m3   M_yaris_n111_m1100 (have) X_yaris_n111_m2270 (NEW)
#   Silverado  7.96 m3   X_silverado_n154_m1100    M_silverado_n154_m2270 (have)
#                        (NEW)
#
#   Compare COLUMNS for the main effect of geometry at fixed mass.
#   Compare ROWS    for the main effect of mass at fixed geometry.
#   The diagonal gives the interaction.
#
# This is the same "the 2x2 has never been run" gap the reconciliation document
# records against D8/J15 for friction versus refinement. Here it is run.
#
# WHAT EACH OUTCOME WOULD MEAN, written BEFORE the runs so it cannot be fitted
# afterwards:
#   - If X_yaris_n111_m2270 goes STUCK and X_silverado_n154_m1100 goes SLIDE, the
#     ordering follows MASS and the geometry-aware account gains nothing here.
#   - If X_yaris_n111_m2270 stays SLIDE and X_silverado_n154_m1100 stays STUCK,
#     the ordering follows GEOMETRY and is not reducible to mass.
#   - Any mixed result is an interaction and must be reported as one, not
#     rounded to whichever main effect is more convenient.
#
# NOTE THE ENTANGLEMENT, so the write-up does not overclaim. At fixed hull volume,
# changing mass changes bulk density, and density sets buoyancy, which sets the
# normal force, which sets Coulomb friction. "Mass" in this 2x2 therefore means
# "mass at fixed geometry", i.e. mass and density together. It cannot separate
# those two from each other. It CAN separate them jointly from geometry, which is
# the open question. The realized densities here are deliberately extreme:
#     Yaris     2270 kg / 3.542739 m3 = 640.75 kg/m3
#     Silverado 1100 kg / 7.962083 m3 = 138.15 kg/m3
# The Silverado arm is far more buoyant than anything in the canonical set and may
# reach FLOAT rather than SLIDE or STUCK. FLOAT is a real mode in
# simulation/failure_modes.py and would be a legitimate, reportable outcome, not a
# failed run.
#
# THIRD RUN, unrelated to the 2x2 and included because it is nearly free.
# X_rogue_n123_m1609 re-runs the midsize_suv at 1609 kg, the AR&R large_passenger
# class figure, which a live NHTSA Canadian Vehicle Specifications pull matches to
# the 2020 Rogue AWD trim (1610 kg) almost exactly. Arms S and M used 1571.3 kg,
# which that same pull places BETWEEN the FWD (1550) and AWD (1610) trims and
# therefore pins to no published trim. 1609 is the better-grounded figure and this
# measures whether the Rogue's verdict is sensitive to the choice at all. Arm D
# already ran the Rogue at 1537.052, so with this run the Rogue is measured at
# three masses, 1537.052 / 1571.3 / 1609, at identical geometry and resolution.
#
# GRID. n_grid 111 / 123 / 154 are the MATCHED-dx values, identical to arms M and
# D, so every run here is directly comparable to them: dx 0.0848806 / 0.0848987 /
# 0.0848567, realized depth 0.297082 / 0.297145 / 0.296998, 7 water layers.
#
# ENGINE: warpmpm. NOT Genesis.
# NON-CANONICAL: writes only inside $BASE. Touches neither
# data/all_runs_inventory.csv nor renders/yaris_render_s1/gates_results_all_runs.json.
# ============================================================================
set -uo pipefail

REPO=/scratch/11603/jcerrell0629/canitford_track1b/can-it-ford
ENGINE=/work/11603/jcerrell0629/vista/mpm-engine/src
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env

TAG=${1:-2026-08-14}
BASE=/scratch/11603/jcerrell0629/three_class_massswap_${TAG}

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

# Identical to arms S/M/D, verbatim, so the 2x2 is a clean comparison.
COMMON="--depth 0.30 --velocity 1.5 --frames 90 --eta 1.0e-3 --floor-friction 0.55"

{
  echo "start=$(date -Is) host=$(hostname)"
  echo "job_id=${SLURM_JOB_ID:-none} partition=${SLURM_JOB_PARTITION:-none}"
  echo "ARM X, mass swap. NON-CANONICAL companion to three_class_matched_${TAG}."
  echo "engine=warpmpm (NOT Genesis)  engine_src=$ENGINE"
  echo "driver sha256: $(sha256sum "$DRIVER")"
  echo "runner sha256: $(sha256sum "$0")"
  echo "common: $COMMON"
  V=/work/11603/jcerrell0629/vista/can-it-ford/vehicle_geometry_research
  sha256sum "$V/yaris_coarse_v1l_watertight.ply" \
            "$V/rogue_g96_pd8_coarse_watertight.ply" \
            "$V/silverado_g96_pd8_coarse_watertight.ply"
  nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
} >> "$PROV" 2>&1

run_one() {
    local label="$1" vehicle="$2" ngrid="$3" mass="$4" note="$5"
    local out="$BASE/$label"
    mkdir -p "$out"
    echo "=== $(date -Is) $label vehicle=$vehicle n_grid=$ngrid mass=$mass"
    "$PY" "$DRIVER" --vehicle "$vehicle" --grid "$ngrid" --mass "$mass" \
        --label "$label" --out "$out" $COMMON > "$BASE/${label}.log" 2>&1
    local rc=$?
    {
      echo "--- $label ---"
      echo "ARM=X VEHICLE=$vehicle N_GRID=$ngrid MASS=$mass NOTE=$note"
      echo "RC_${label}=$rc"
      /usr/bin/grep -h -E '^(PREFLIGHT|INSTRUMENT|SUBSTEP_TERMS|DETERMINISM|SCENARIO|grid )' \
          "$BASE/${label}.log" 2>/dev/null | sed 's/^/    /'
    } >> "$PROV" 2>&1
    if [ $rc -ne 0 ]; then echo "  FAILED rc=$rc"; tail -20 "$BASE/${label}.log"; fi
    return $rc
}

# --- the two cells that complete the 2x2 --------------------------------------
run_one X_yaris_n111_m2270     yaris     111 2270.0 "Silverado deck mass on the Yaris hull; rho 640.75"
run_one X_silverado_n154_m1100 silverado 154 1100.0 "Yaris mass on the Silverado hull; rho 138.15"

# --- the better-grounded Rogue mass -------------------------------------------
run_one X_rogue_n123_m1609     rogue     123 1609.0 "AR&R large_passenger figure; NHTSA AWD trim 1610"

echo "ALLDONE end=$(date -Is)" >> "$PROV"
echo "=== finished $(date -Is), results in $BASE"
ls -la "$BASE"
