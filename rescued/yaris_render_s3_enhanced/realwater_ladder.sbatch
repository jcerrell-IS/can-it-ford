#!/bin/bash
#SBATCH -J s3real
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00
#SBATCH -A BCS20003
#SBATCH -o /work/11603/jcerrell0629/vista/render_s3_enhanced/slurm_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/render_s3_enhanced/slurm_%j.err
# ===========================================================================
# STAGE 2. Physical sound speed. NOT CANONICAL.
#
# WHY THIS IS NOW POSSIBLE. Job 895330 measured actual GH200 throughput at
# 2 min 09 s for the whole 3-stage ladder, refuting this project's earlier
# assumption that a >500-substep run was unaffordable. Calibrated model, two
# points at g96/90 frames: 16 substeps -> 5.5 s, 156 substeps -> 30.0 s, i.e.
# wall ~= (2.7 + 0.175*substeps) * (grid/96)^3 seconds.
#
# WHAT THIS TESTS. bulk_modulus 1.9939e9 Pa gives c = 1480.976 m/s, i.e. REAL
# water, ratio 1.000 against 1481. Every gated run in this project used
# c = 12.845 m/s, off by a factor of 115. CLAUDE.md records Isik and He 2022:
# artificial sound speed can qualitatively FLIP a rigid-body outcome. Job
# 895330 already showed a roll SIGN FLIP (-0.0036 -> +1.109 deg) from a mere
# 10x sound-speed change at fixed grid, so this is not hypothetical.
#
#   stage A  g128 K=1.5e7    c=128.45   208 substeps  ~1.5 min
#   stage B  g96  K=1.9939e9 c=1480.98 1797 substeps  ~5.3 min
#   stage C  g128 K=1.9939e9 c=1480.98 2396 substeps ~16.7 min   MAX REALISM
#
# Sum ~24 min. Wall limit 02:00:00 leaves ~5x headroom.
#
# NO GATE HERE. The control already passed in job 895330 at -0.2106 percent
# against the canonical g64_m1100, and the g64->g96 transition reproduced the
# canonical grid study to 0.17 percentage points (-59.03 measured vs -59.2
# recorded). The pipeline is established; this job only varies physics.
# ===========================================================================
set -u

BASE=$WORK/render_s3_enhanced
PY=$WORK/.venv/bin/python
RUN=$BASE/run_enhanced.py
MESH=$WORK/can-it-ford/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply

echo "node    : $(hostname)"
echo "started : $(date -Is)"
echo "driver  : $(sha256sum $BASE/sim_enhanced.py)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
$PY -c "import warp,numpy;print('warp',warp.config.version,'numpy',numpy.__version__)"

stamp () { echo; echo "########## $* ##########"; date -Is; }

go () {  # label grid bulk
  stamp "$1  grid=$2 K=$3"
  time $PY "$RUN" --label "$1" --out "$BASE/$1" \
       --vehicle "$MESH" --grid "$2" --bulk-modulus "$3" \
       --mass 1100 --depth 0.30 --velocity 1.5 --frames 90 \
       > "$BASE/$1.log" 2>&1
  echo "rc=$?"
  tail -3 "$BASE/$1.log"
}

go enh_g128_c10   128 1.5e7
go enh_g96_real    96 1.9939e9
go enh_g128_real  128 1.9939e9

stamp "SUMMARY TABLE"
$PY - <<'PYEOF'
import json, pathlib, os
BASE = pathlib.Path(os.environ["WORK"]) / "render_s3_enhanced"
rows = ["ctrl_g64", "enh_g96", "enh_g96_c10",
        "enh_g128_c10", "enh_g96_real", "enh_g128_real"]
print("  %-16s %8s %8s %9s %8s %9s %9s %8s" %
      ("label", "disp_m", "c_m/s", "substeps", "cells/d", "passthru", "z_rise", "roll"))
for r in rows:
    f = BASE / r / "summary.json"
    if not f.exists():
        print("  %-16s MISSING" % r); continue
    s = json.load(open(f))
    print("  %-16s %8.5f %8.2f %9d %8.3f %9.5f %9.5f %8.3f" %
          (r, s["final_disp_mag_m"], s["sound_speed_ms"], s["substeps"],
           s["cells_per_depth"], s["passthrough_max_frac"],
           s["C2_veh_zmin_rise"], s["final_roll_deg"]))
print()
print("  gate limits: P-2 passthrough < 0.10 (gates.py:148)")
print("               P-3 abs(z_rise) <= 0.01 m (gates.py:150-151)")
PYEOF
date -Is
