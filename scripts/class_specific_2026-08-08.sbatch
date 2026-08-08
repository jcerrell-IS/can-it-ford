#!/bin/bash
#SBATCH -J classspec
#SBATCH -A BCS20003
#SBATCH -p gh-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 01:00:00
#SBATCH -o /work/11603/jcerrell0629/vista/class_specific_2026-08-08/slurm_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/class_specific_2026-08-08/slurm_%j.err

# ===========================================================================
# CLASS-SPECIFIC HULL RUNS, Rogue and Silverado, canonical g64.
# Structure, venv, provenance block and no-set-e convention are taken from
# scripts/conv_2026-07-25.sbatch. NOT CANONICAL: the 17 gated runs are Yaris
# only, and nothing here is added to that set.
#
# WHY THIS DOES NOT CALL run_s2.sh
#   conv_2026-07-25.sbatch reaches sim_standing.py only through
#   $WORK/render_s2/run_s2.sh, which hardcodes the three-mass Yaris loop and
#   passes no --vehicle. run_s2.sh is byte-identical to the archived as-ran
#   copy at analysis/render_v1/as_ran_local_copies/run_s2.sh and that
#   byte-identity is the provenance link to the 17 gated runs, so it is not
#   edited. This script calls the driver directly instead.
#
# WHY THE DRIVER IS A STAGED COPY, NOT $WORK/render_s2/sim_standing.py
#   That file is sha256 5215c38b, Jul 25, and still divides fill_ratio by the
#   hardcoded Yaris literal HULL (:269, :361) and has no yaris_ref_delta_pct
#   tripwire. Swapping the hull under it reports the Yaris volume silently.
#   The staged driver is sha256 7236e474, the Aug 8 corrected canonical
#   driver, hull_m3 derived from the loaded mesh at :248 and the tripwire at
#   :287-290. render_s2 is left untouched.
#
# HULLS. Watertight confirmed through the exact load_vehicle branch
#   (trimesh.load force=mesh, then the process=False rebuild), 1 body each.
#   NEVER substitute a *_poisson_raw.ply: those are not watertight (5 to 337
#   bodies), would silently take the solidify_columns branch, and would give a
#   wrong displaced volume with no error raised.
# ===========================================================================

# No set -e. A failing run must not abort the one after it.
set -o pipefail

PY=$WORK/.venv/bin/python                       # editable -> vista/mpm-engine/src
BASE=$WORK/class_specific_2026-08-08
DRIVER=$BASE/sim_standing.py                    # sha256 7236e474
HULLS=$WORK/hulls

ROGUE=$HULLS/rogue_g96_pd8_coarse_watertight.ply
SILVERADO=$HULLS/silverado_g96_pd8_coarse_watertight.ply

# --- MASS. Chosen by Josie 2026-08-08: deck / class-specific masses. --------
#   Silverado 2270 kg is PRIMARY-SOURCED, deck header silverado-coarse-v3a.key:28.
#   Rogue 1571.3 kg is WEB-SOURCED ONLY (2020 Rogue FWD S curb weight 3464 lb,
#   cars.com). The Rogue LS-DYNA deck header states NO mass, unlike the Yaris
#   and Silverado decks. Label it as web-sourced in any writeup; do not present
#   it as deck-derived.
#   Realized densities: Rogue 317.4, Silverado 285.1 kg/m3, against the
#   canonical Yaris 310.494. All three sit above the stale 100-300 band.
MASS_ROGUE=1571.3
MASS_SILVERADO=2270.0

# Canonical g64 parameters, verbatim from run_s2.sh as-ran for the 17 runs.
COMMON="--depth 0.30 --velocity 1.5 --frames 90 --grid 64 --eta 1.0e-3 --floor-friction 0.55"

mkdir -p "$BASE"

{
  echo "job=${SLURM_JOB_ID}  host=$(hostname)  start=$(date -Is)"
  nvidia-smi --query-gpu=name,memory.total --format=csv
  "$PY" -c "import warpmpm, warpmpm.vehicle as v; print('warpmpm resolves to:', warpmpm.__file__); print('solidify_watertight present:', hasattr(v,'solidify_watertight'))"
  echo "driver sha256: $(sha256sum "$DRIVER")"
  echo "hull sha256  :"
  sha256sum "$ROGUE" "$SILVERADO"
  echo "common args  : $COMMON"
  echo "mass rogue   : $MASS_ROGUE"
  echo "mass silvrdo : $MASS_SILVERADO"
} > "$BASE/00_provenance.txt" 2>&1
sync

go () {  # label  mesh  mass
  echo "=== $1  mass=$3  mesh=$(basename $2)  $(date -Is) ==="
  timeout 1800 "$PY" -u "$DRIVER" --mass "$3" --label "$1" \
    --out "$BASE/$1" --vehicle "$2" $COMMON \
    > "$BASE/$1.log" 2>&1
  local rc=$?
  echo "RC_$1=${rc}" | tee -a "$BASE/00_provenance.txt"
  # TRIPWIRE. Must read ~+39.732 for the Rogue and ~+124.744 for the
  # Silverado. A ~0.000 means --vehicle did not take effect and the run is
  # the Yaris hull mislabelled. Do not read any physics until this passes.
  grep -E "^INSTRUMENT hull_source" "$BASE/$1.log" | tee -a "$BASE/00_provenance.txt"
  sync
}

go class_rogue_g64      "$ROGUE"     "$MASS_ROGUE"
go class_silverado_g64  "$SILVERADO" "$MASS_SILVERADO"

echo "ALLDONE end=$(date -Is)" | tee -a "$BASE/00_provenance.txt"
