#!/bin/bash
# Bingham / Herschel-Bulkley sensitivity ladder at the canonical g64 baseline.
# NOT part of the 17-run gated result set. See analysis/bingham_sweep/README.md.
#
# Ladder points come from analysis/bingham_cfl_crossover.py (root tree, untracked).
# Regime labels there are indicative and NOT cited to a primary source.
set -u -o pipefail

WT=/Users/josie/can-it-ford/.claude/worktrees/bingham-sweep-2026-08-07
PY=/Users/josie/.venvs/canitford-mpm/bin/python3
DRV="$WT/renders/yaris_render_s1/run_bingham.py"
MESH="$WT/vehicle_geometry_research/yaris_coarse_v1l_watertight.ply"
OUT="$WT/analysis/bingham_sweep"

mkdir -p "$OUT"

# tag              tau_y   eta     K     n
POINTS="
tau0p0_control     0.0     0.001   0.0   1.0
tau0p1             0.1     0.001   0.0   1.0
tau1p0             1.0     0.001   0.0   1.0
tau3p0             3.0     0.001   0.0   1.0
tau10p0           10.0     0.001   0.0   1.0
tau30p0           30.0     0.001   0.0   1.0
tau100p0         100.0     0.001   0.0   1.0
etacoup_tau3p1     3.1     0.300   0.0   1.0
etacoup_tau40p0   40.0     2.700   0.0   1.0
hb_tau10_K5_n0p8  10.0     0.000   5.0   0.8
hb_tau0_K5_n0p8    0.0     0.000   5.0   0.8
"

echo "$POINTS" | while read -r tag ty eta K n; do
  [ -z "${tag:-}" ] && continue
  if [ -f "$OUT/$tag/summary.json" ]; then
    echo "SKIP $tag (already has summary.json)"
    continue
  fi
  echo "=== RUN $tag  tau_y=$ty eta=$eta K=$K n=$n ==="
  "$PY" -u "$DRV" \
    --mass 1100 --label "$tag" --out "$OUT/$tag" \
    --depth 0.30 --velocity 1.5 --frames 90 --grid 64 \
    --eta "$eta" --floor-friction 0.55 --vehicle "$MESH" \
    --tau-y "$ty" --hb-k "$K" --hb-n "$n" \
    > "$OUT/$tag.log" 2>&1
  rc=$?
  echo "RC_$tag=$rc"
done

echo ALLDONE
