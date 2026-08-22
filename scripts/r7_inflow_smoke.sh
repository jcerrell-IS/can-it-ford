#!/usr/bin/env bash
#SBATCH -J r7_inflow_smoke
#SBATCH -o /work/11603/jcerrell0629/vista/logs/r7_inflow_smoke_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/logs/r7_inflow_smoke_%j.out
#SBATCH -p gh
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:20:00
#SBATCH -A BCS20003
#
# Cheap end-to-end validation of scripts/inflow_vehicle_wrapper.py on a GPU node BEFORE the
# full matrix is submitted. Small grid, few frames. It answers only:
#   1. does the monkeypatch import and run at all
#   2. does the recycle arm drop EXACTLY 2 planes, and the closed arm 0
#   3. does the recycler actually fire, and stay inside the P2G guard margin
#   4. is the water count identical in both arms (one-in-one-out, nothing created)
# It measures no physics and must never be quoted as a result. g48 in particular is one of
# the three grids whose published runs already fail gate P-3.
#
# Partition gh, NOT gh-dev: gh-dev is interactive-class and 98.5 to 99.1 percent of this
# project's Vista node-hours have burned there, 95 of 184 ending in TIMEOUT.
set -uo pipefail

ENGINE=/work/11603/jcerrell0629/vista/mpm-engine
VENV=/work/11603/jcerrell0629/vista/.venv/bin/python
SRC=/work/11603/jcerrell0629/vista/r7_inflow_src
WRAP=$SRC/scripts/inflow_vehicle_wrapper.py
# The CANONICAL driver, sha256 4696c3b2...d10d9, the one that stamps the 17 published runs.
# $WORK/render_s2/sim_standing.py is a DIFFERENT, pre-registry copy (5215c38b...) and the
# wrapper refuses it. Confirmed live 2026-08-18 by sha256sum on both.
DRIVER=/work/11603/jcerrell0629/vista/render_s2/multigeom_2026-08-08/sim_standing.py
export OUT=/work/11603/jcerrell0629/vista/r7_inflow_smoke_${SLURM_JOB_ID:-manual}

mkdir -p "$OUT"
cd "$ENGINE" || exit 1
hostname
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1 | head -2
echo "TIMING_ANCHOR_START=$(date +%s)"
echo "DRIVER_SHA $(sha256sum "$DRIVER")"
echo "WRAPPER_SHA $(sha256sum "$WRAP")"
echo "BC_SHA $(sha256sum "$SRC/simulation/openchannel_bc.py")"

# The numpy-only checks, run on the node, so a staging mistake surfaces here and not
# after a GPU allocation has been spent.
$VENV -u "$WRAP" --selftest || exit 1
$VENV -u "$SRC/simulation/openchannel_bc.py" || exit 1

FAILS=0

run_bare () {
  local name=$1 frames=$2
  $VENV -u "$DRIVER" --label "$name" --out "$OUT/$name" \
    --mass 1100 --depth 0.30 --velocity 1.5 --frames "$frames" --grid 48 \
    --eta 1.0e-3 --floor-friction 0.55
  local rc=$?; echo "RC_${name}=$rc"; [ $rc -eq 0 ] || FAILS=$((FAILS+1))
}

run_wrapped () {   # run_wrapped <name> <bc> <noband:0|1> <frames>
  local name=$1 bc=$2 nb=$3 frames=$4 nbflag=""
  [ "$nb" = "1" ] && nbflag="--no-band"
  $VENV -u "$WRAP" --driver "$DRIVER" --bc "$bc" $nbflag \
    --label "$name" --out "$OUT/$name" \
    --depth 0.30 --velocity 1.5 --frames "$frames" --grid 48 \
    --mass 1100 --eta 1.0e-3 --floor-friction 0.55
  local rc=$?; echo "RC_${name}=$rc"; [ $rc -eq 0 ] || FAILS=$((FAILS+1))
}

run_bare    smoke__bare__rep1              5
run_wrapped smoke__closed__rep1  closed  0 5
run_wrapped smoke__recycle__rep1 recycle 0 20
run_wrapped smoke__recycnb__rep1 recycle 1 20

echo "TIMING_ANCHOR_END=$(date +%s)"
echo "--- assertions ---"
$VENV - "$OUT" <<'PY'
import json, sys
out = sys.argv[1]
ok = True
def chk(cond, msg):
    global ok
    print(("PASS " if cond else "FAIL ") + msg, flush=True)
    ok = ok and bool(cond)
def load(n):
    return json.load(open("%s/%s/inflow_summary.json" % (out, n)))
c = load("smoke__closed__rep1")
r = load("smoke__recycle__rep1")
n = load("smoke__recycnb__rep1")
chk(c["n_dropped_planes"] == 0, "closed arm drops 0 planes (got %d)" % c["n_dropped_planes"])
chk(r["n_dropped_planes"] == 2, "recycle arm drops 2 planes (got %d)" % r["n_dropped_planes"])
chk(all(abs(p["normal"][0]) > 0.5 for p in r["dropped_planes"]),
    "dropped planes are x-normal: %s" % [p["normal"] for p in r["dropped_planes"]])
chk(r["recycled_total"] > 0, "recycler fired (recycled_total=%d)" % r["recycled_total"])
chk(c["recycled_total"] == 0, "closed arm never recycles")
chk(r["max_overshoot_m"] < 1.5 * r["dx_m"],
    "max overshoot %.5f m < 1.5*dx = %.5f m, the P2G guard margin"
    % (r["max_overshoot_m"], 1.5 * r["dx_m"]))
chk(n["band"] is False and r["band"] is True and c["band"] is True,
    "band flag recorded correctly")
chk(c["n_water"] == r["n_water"] == n["n_water"],
    "same water count in every arm (%d / %d / %d)"
    % (c["n_water"], r["n_water"], n["n_water"]))
chk(r["x_in_m"] < r["x_out_m"], "x_in < x_out")
chk(abs(r["x_out_m"] - (r["grid_lim_m"] - 4.0 * r["dx_m"])) < 1e-9,
    "outflow plane sits exactly where the closed arm's downstream wall does")
chk(abs(c["reflection_prediction"]["stream_reflection_frame"] -
        r["reflection_prediction"]["stream_reflection_frame"]) < 1e-9,
    "both arms share the same reflection geometry, so the prediction is common")
print("SMOKE_OK" if ok else "SMOKE_FAILED", flush=True)
sys.exit(0 if ok else 1)
PY
ARC=$?
echo "ASSERT_RC=$ARC"
if [ $FAILS -ne 0 ] || [ $ARC -ne 0 ]; then
  echo "ALLDONE_WITH_FAILURES runs_failed=$FAILS assert_rc=$ARC"
  exit 1
fi
echo ALLDONE
