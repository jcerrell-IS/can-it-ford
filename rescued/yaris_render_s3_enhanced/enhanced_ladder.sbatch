#!/bin/bash
#SBATCH -J s3enh
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 03:00:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/render_s3_enhanced/slurm_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/render_s3_enhanced/slurm_%j.err
# ===========================================================================
# Enhanced-physics ladder. NOT CANONICAL.
#
# GATED ON PURPOSE. Stage 0 is a control at the exact as-run baseline parameters.
# If it does not reproduce the canonical g64_m1100 displacement, every later stage
# is uninterpretable, so the job ABORTS instead of burning SUs on runs whose
# baseline has already moved. That gate is the whole reason this is one script and
# not three submissions.
#
# BUDGET. Vista had 670 SUs on 2026-08-07, expiring 2026-09-30, and 99.1 percent of
# this project's historical node-time went to idle interactive sessions rather than
# science. This is batch. Costs below are from `run_enhanced.py --estimate`, which
# self-tests against the as-run substep count of 11 before it is trusted.
#
#   stage 0  control g64  K=1.5e5     1.00x    ~2 min
#   stage 1  g96          K=1.5e5     4.91x    ~7 min
#   stage 2  g96          K=1.5e7    47.86x   ~72 min
#
# Wall limit 03:00:00 leaves roughly 2x headroom on the sum.
# ===========================================================================
set -u

BASE=$WORK/render_s3_enhanced
PY=$WORK/.venv/bin/python
RUN=$BASE/run_enhanced.py
MESH=$WORK/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply

# Canonical anchor: data/all_runs_inventory.csv row g64_m1100, summary.json measure.
CANON_DISP=0.6585370302200317

echo "node    : $(hostname)"
echo "started : $(date -Is)"
echo "driver  : $(sha256sum $BASE/sim_enhanced.py)"
echo "launcher: $(sha256sum $RUN)"
echo "mesh    : $(sha256sum $MESH)"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
$PY -c "import warp,numpy;print('warp',warp.config.version,'numpy',numpy.__version__)"
echo

stamp () { echo; echo "########## $* ##########"; date -Is; }

# --- stage 0: control -------------------------------------------------------
stamp "STAGE 0  control g64 K=1.5e5  (must reproduce $CANON_DISP)"
time $PY "$RUN" --label ctrl_g64 --out "$BASE/ctrl_g64" \
     --vehicle "$MESH" --grid 64 --bulk-modulus 1.5e5 \
     --mass 1100 --depth 0.30 --velocity 1.5 --frames 90 \
     > "$BASE/ctrl_g64.log" 2>&1
RC=$?
tail -5 "$BASE/ctrl_g64.log"
if [ $RC -ne 0 ]; then echo "ABORT: control run exited $RC"; exit 1; fi

GATE=$($PY - "$BASE/ctrl_g64/summary.json" "$CANON_DISP" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))["final_disp_mag_m"]
canon = float(sys.argv[2])
rel = abs(d - canon) / canon
print("CONTROL disp=%.16f canon=%.16f rel=%.3e" % (d, canon, rel))
if rel < 1e-9:
    print("GATE PASS bit-exact"); sys.exit(0)
if rel < 1e-2:
    print("GATE PASS within 1 percent (cross-venue/backend drift, acceptable)"); sys.exit(0)
print("GATE FAIL: baseline moved by %.3f percent. Later stages uninterpretable." % (100*rel))
sys.exit(3)
PYEOF
)
echo "$GATE"
if echo "$GATE" | grep -q "GATE FAIL"; then
  echo "ABORT: control did not reproduce the canonical baseline. No SUs spent on stages 1-2."
  exit 3
fi

# --- stage 1: resolution ----------------------------------------------------
stamp "STAGE 1  g96 K=1.5e5  (resolution only, 4.91x)"
time $PY "$RUN" --label enh_g96 --out "$BASE/enh_g96" \
     --vehicle "$MESH" --grid 96 --bulk-modulus 1.5e5 \
     --mass 1100 --depth 0.30 --velocity 1.5 --frames 90 \
     > "$BASE/enh_g96.log" 2>&1
echo "rc=$?"; tail -4 "$BASE/enh_g96.log"

# --- stage 2: resolution + sound speed --------------------------------------
stamp "STAGE 2  g96 K=1.5e7  (c 10x, 47.86x)  THE HERO RUN"
time $PY "$RUN" --label enh_g96_c10 --out "$BASE/enh_g96_c10" \
     --vehicle "$MESH" --grid 96 --bulk-modulus 1.5e7 \
     --mass 1100 --depth 0.30 --velocity 1.5 --frames 90 \
     > "$BASE/enh_g96_c10.log" 2>&1
echo "rc=$?"; tail -4 "$BASE/enh_g96_c10.log"

stamp "ALL STAGES DONE"
for d in ctrl_g64 enh_g96 enh_g96_c10; do
  if [ -f "$BASE/$d/summary.json" ]; then
    $PY -c "
import json;s=json.load(open('$BASE/$d/summary.json'))
print('  %-14s disp=%.6f  passthru=%.5f  substeps=%-4d c=%.2f  cells/depth=%.3f  wall=%.0fs'
      % ('$d', s['final_disp_mag_m'], s['passthrough_max_frac'], s['substeps'],
         s['sound_speed_ms'], s['cells_per_depth'], s['wall_seconds']))"
  else
    echo "  $d MISSING"
  fi
done
date -Is
