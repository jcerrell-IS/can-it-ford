#!/bin/bash
# ============================================================================
# ARM F: complete a balanced 3x3 factorial in (hull, mass) at matched dx,
# and give the flip configuration its missing repeat.  NON-CANONICAL.
#
# WHY. The 2x2 (arm X) showed mass x2.06 -> ratio_slide x0.19 and volume x2.25 ->
# x0.43, with ~3.3 percent interaction. Two weaknesses in that, both real:
#   1. It is a 2x2 with the Rogue absent, so each main effect rests on two cells.
#   2. THE FLIP CELL HAS NO REPEAT. M_silverado_n154_m2270 is the only STUCK run
#      at n154 and this stack is non-deterministic at fixed configuration, so the
#      single most load-bearing verdict in the set is unreplicated. A repeat is
#      the cheapest possible strengthening and its absence was raised in review.
#
# THE SQUARE, masses {1100, 1609, 2270} x hulls {yaris, rogue, silverado}, all at
# the matched-dx grid n_grid 111/123/154 (dx ~0.08486, realized depth ~0.29700):
#
#                 1100 kg              1609 kg              2270 kg
#   yaris         M_yaris  (have)      F_yaris_1609 (NEW)   X_yaris  (have)
#   rogue         F_rogue_1100 (NEW)   X_rogue  (have)      F_rogue_2270 (NEW)
#   silverado     X_silverado (have)   F_silverado_1609(NEW) M_silverado (have)
#
# 1609 is used as the middle mass rather than 1571.3 because a live NHTSA pull
# matches 1609 to the 2020 Rogue AWD trim (1610) while 1571.3 falls between the
# FWD (1550) and AWD trims and pins to no published trim. The Rogue is already
# measured at 1537.052 / 1571.3 / 1609 and is SLIDE at all three, so this choice
# does not disturb any existing result.
#
# NOTE ON WHAT A ROW STILL CANNOT SEPARATE: at fixed hull, changing mass changes
# bulk density too, so a row measures mass-and-density jointly. At fixed mass,
# changing hull changes the TANK as well, because grid_lim follows the hull
# extent, so a column measures vehicle-plus-tank. Neither is a clean single-factor
# effect and the write-up must not claim they are. The 3x3 improves the ESTIMATES
# and tests additivity; it does not remove either confound.
#
# ENGINE: warpmpm. NOT Genesis. Writes only inside $BASE.
# ============================================================================
set -uo pipefail

REPO=/scratch/11603/jcerrell0629/canitford_track1b/can-it-ford
ENGINE=/work/11603/jcerrell0629/vista/mpm-engine/src
VENV=/scratch/11603/jcerrell0629/warpmpm_ls6_env
TAG=${1:-2026-08-14}
BASE=/scratch/11603/jcerrell0629/three_class_full33_${TAG}

if [ -e "$BASE" ]; then
    echo "REFUSING: $BASE exists. Never writes into an existing run dir (register item 16)."
    exit 3
fi
mkdir -p "$BASE"

PY="$VENV/bin/python"
export PYTHONPATH="$ENGINE:$REPO:${PYTHONPATH:-}"
DRIVER="$REPO/renders/yaris_render_s1/sim_standing.py"
PROV="$BASE/00_provenance.txt"
COMMON="--depth 0.30 --velocity 1.5 --frames 90 --eta 1.0e-3 --floor-friction 0.55"

{
  echo "start=$(date -Is) host=$(hostname)"
  echo "ARM F, balanced 3x3 plus a repeat of the flip cell. NON-CANONICAL."
  echo "engine=warpmpm (NOT Genesis) engine_src=$ENGINE"
  echo "driver sha256: $(sha256sum "$DRIVER")"
  echo "runner sha256: $(sha256sum "$0")"
  echo "common: $COMMON"
  V=/work/11603/jcerrell0629/vista/can-it-ford/vehicle_geometry_research
  sha256sum "$V/yaris_coarse_v1l_watertight.ply" "$V/rogue_g96_pd8_coarse_watertight.ply" \
            "$V/silverado_g96_pd8_coarse_watertight.ply"
  nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
} >> "$PROV" 2>&1

run_one() {
    local label="$1" vehicle="$2" ngrid="$3" mass="$4" note="$5"
    local out="$BASE/$label"; mkdir -p "$out"
    echo "=== $(date -Is) $label vehicle=$vehicle n_grid=$ngrid mass=$mass"
    "$PY" "$DRIVER" --vehicle "$vehicle" --grid "$ngrid" --mass "$mass" \
        --label "$label" --out "$out" $COMMON > "$BASE/${label}.log" 2>&1
    local rc=$?
    { echo "--- $label ---"; echo "ARM=F VEHICLE=$vehicle N_GRID=$ngrid MASS=$mass NOTE=$note"
      echo "RC_${label}=$rc"
      /usr/bin/grep -h -E '^(PREFLIGHT|INSTRUMENT|SUBSTEP_TERMS|DETERMINISM|grid )' \
          "$BASE/${label}.log" 2>/dev/null | sed 's/^/    /'; } >> "$PROV" 2>&1
    [ $rc -ne 0 ] && { echo "  FAILED rc=$rc"; tail -15 "$BASE/${label}.log"; }
    return $rc
}

# --- the repeat of the flip cell, FIRST so it lands even if time runs short ---
run_one F_silverado_n154_m2270_rep silverado 154 2270.0 "REPEAT of M_silverado, the flip cell, no repeat existed"

# --- the four cells that balance the 3x3 --------------------------------------
run_one F_rogue_n123_m1100      rogue     123 1100.0 "3x3 fill"
run_one F_rogue_n123_m2270      rogue     123 2270.0 "3x3 fill"
run_one F_yaris_n111_m1609      yaris     111 1609.0 "3x3 fill"
run_one F_silverado_n154_m1609  silverado 154 1609.0 "3x3 fill"

echo "ALLDONE end=$(date -Is)" >> "$PROV"
echo "=== finished $(date -Is), results in $BASE"
