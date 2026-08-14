#!/bin/bash
#SBATCH -J s3hull
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 01:00:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/render_s3_hullsweep/slurm_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/render_s3_hullsweep/slurm_%j.err
# ===========================================================================
# HULL SWEEP. The first run in this project where vehicle GEOMETRY actually
# varies. NOT CANONICAL.
#
# WHY THIS DID NOT EXIST BEFORE
#   sim_standing.py has accepted an arbitrary --vehicle since it was written
#   (:228, a free-form path, not an enum). run_s2.sh never passed it. That,
#   not the driver, is why all 17 gated runs used the same Yaris hull.
#   run_s2.sh is byte-identical to the archived as-ran copy at
#   analysis/render_v1/as_ran_local_copies/run_s2.sh, so it is NOT edited;
#   the provenance link to the 17 runs is preserved and this is a new file.
#
# TWO PREREQUISITE FIXES LANDED 2026-08-08, BOTH IN sim_enhanced.py
#   1. HULL was a hardcoded Yaris literal 3.542739 used as the fill_ratio
#      denominator. Swapping the hull left hull_m3 reporting the Yaris volume
#      and fill_ratio computed against the wrong denominator: silent, and the
#      numbers stayed plausible. hull_m3 is now derived from the loaded mesh.
#      realized_rho was never affected; it divides by solid_volume, not HULL.
#   2. The E8 grid_lim anchor compared against the Yaris literal
#      CANON_GRID_LIM unconditionally, so ANY non-Yaris hull hit ANCHOR FAIL
#      and the only escape was --allow-lim-drift, which disables the axis-trap
#      guard wholesale. The anchor is now derived from each hull's own sorted
#      extents, which still catches the axis trap and now does so for every
#      hull. --allow-lim-drift is therefore NOT passed anywhere below.
#
# THE RESOLUTION CONFOUND, AND WHY THERE ARE TWO ARMS
#   lim = max(2.2*ext_long, 3.5*ext_short, 6.0*depth), so lim tracks vehicle
#   size:  yaris 9.421742314   rogue 10.442536068   silverado 13.067932987
#   At a FIXED n_grid the three hulls therefore run at different dx:
#     n_grid 96 -> yaris 0.098143, rogue 0.108776 (+10.8%), silverado
#     0.136124 (+38.7%).
#   CLAUDE.md L-4: coarse resolution usually OVER-predicts peak hydrodynamic
#   force. A fixed-n_grid sweep would therefore bias the larger vehicles
#   toward higher force and the comparison would be uninterpretable.
#
#   ARM A  matched dx = 0.098143 m (the Yaris g96 value). n_grid scales with
#          lim: 96 / 106 / 133. THIS IS THE SCIENCE ARM. Compare across hulls.
#   ARM B  fixed n_grid = 96. Control that MEASURES the confound. Do not read
#          across hulls; read it against Arm A to size the resolution effect.
#
# MASS IS HELD AT 1100 kg IN BOTH ARMS, DELIBERATELY
#   This isolates geometry. It is NOT the physical mass of a Rogue or a
#   Silverado. CLAUDE.md item 10 records that 1609 and 2337 kg have no source
#   in vehicle_params.py, and the Rogue's LS-DYNA mass is still missing, so a
#   realistic-mass arm cannot be sourced today. Do not report these as
#   vehicle-class results; they are hull-shape results at fixed mass.
#
# COST. Canonical bulk modulus 1.5e5 (c = 12.845 m/s), so substeps stay low.
#   Model wall ~= (2.7 + 0.175*substeps) * (grid/96)^3 s. At matched dx the
#   substeps are identical across hulls, so cost scales as (n_grid/96)^3:
#   1.000 / 1.362 / 2.668. Both arms together are well under two minutes of
#   GPU. The 01:00:00 wall is ~30x headroom.
# ===========================================================================
set -u

BASE=$WORK/render_s3_hullsweep
PY=$WORK/.venv/bin/python
RUN=$BASE/run_enhanced.py
HULLS=$WORK/hulls

YARIS=$WORK/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply
ROGUE=$HULLS/rogue_g96_pd8_coarse_watertight.ply
SILVERADO=$HULLS/silverado_g96_pd8_coarse_watertight.ply

echo "node    : $(hostname)"
echo "started : $(date -Is)"
echo "driver  : $(sha256sum $BASE/sim_enhanced.py)"
echo "hulls   :"
sha256sum "$YARIS" "$ROGUE" "$SILVERADO"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
$PY -c "import warp,numpy;print('warp',warp.config.version,'numpy',numpy.__version__)"

stamp () { echo; echo "########## $* ##########"; date -Is; }

go () {  # label mesh grid
  stamp "$1  grid=$3  mesh=$(basename $2)"
  time $PY "$RUN" --label "$1" --out "$BASE/$1" \
       --vehicle "$2" --grid "$3" --bulk-modulus 1.5e5 \
       --mass 1100 --depth 0.30 --velocity 1.5 --frames 90 \
       > "$BASE/$1.log" 2>&1
  echo "rc=$?"
  grep -E "^INSTRUMENT hull_source|^ANCHOR" "$BASE/$1.log" || true
  tail -3 "$BASE/$1.log"
}

# ---- ARM A: matched dx = 0.098143 m. The science arm. --------------------
go hull_yaris_dxm      "$YARIS"      96
go hull_rogue_dxm      "$ROGUE"     106
go hull_silverado_dxm  "$SILVERADO" 133

# ---- ARM B: fixed n_grid 96. Confound control, not a hull comparison. ----
go hull_rogue_g96      "$ROGUE"      96
go hull_silverado_g96  "$SILVERADO"  96

stamp "SUMMARY TABLE"
$PY - <<'PYEOF'
import json, pathlib, os
BASE = pathlib.Path(os.environ["WORK"]) / "render_s3_hullsweep"
ARM_A = ["hull_yaris_dxm", "hull_rogue_dxm", "hull_silverado_dxm"]
ARM_B = ["hull_rogue_g96", "hull_silverado_g96"]

hdr = ("  %-20s %9s %9s %10s %9s %8s %9s %9s %8s" %
       ("label", "hull_m3", "d_ref_%", "fill_ratio", "dx", "disp_m",
        "passthru", "z_rise", "roll"))

def show(rows, title):
    print("\n  == %s ==" % title)
    print(hdr)
    for r in rows:
        f = BASE / r / "summary.json"
        if not f.exists():
            print("  %-20s MISSING" % r); continue
        s = json.load(open(f))
        print("  %-20s %9.6f %+9.3f %10.4f %9.6f %8.5f %9.5f %9.5f %8.3f" %
              (r, s["hull_m3"], s["hull_ref_delta_pct"], s["fill_ratio"],
               s["dx"], s["final_disp_mag_m"], s["passthrough_max_frac"],
               s["C2_veh_zmin_rise"], s["final_roll_deg"]))

show(ARM_A, "ARM A  matched dx, compare across these")
show(ARM_B, "ARM B  fixed n_grid 96, confound control ONLY")

print("""
  TRIPWIRES, check these before reading any physics:
    hull_ref_delta_pct  must be  ~0.000 yaris | +39.732 rogue | +124.744 silverado
                        If all three read ~0, --vehicle did NOT take effect.
    fill_ratio          must be ~1.00 for ALL hulls now that hull_m3 is derived.
                        A rogue reading ~1.3973 or silverado ~2.2474 means the
                        old hardcoded-HULL denominator is still in the driver.
    dx (ARM A)          must be ~0.098143 for all three. That is the point of the arm.
  gate limits: P-2 passthrough < 0.10 (gates.py:148)
               P-3 abs(z_rise) <= 0.01 m (gates.py:150-151)
""")
PYEOF
date -Is
