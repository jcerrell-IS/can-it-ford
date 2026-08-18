#!/bin/bash
# ============================================================================
# THE CONTROL D5 NAMED AS MISSING AND DID NOT RUN. NON-CANONICAL.
#
# 10.20 established that at the margin-0 cell the discrete verdict flips across
# INDEPENDENT STARTS (7/8 SLIDE, 1/8 STUCK) and that k_crit spreads 19 percent.
# It could NOT attribute that to initial conditions, because seed 0 also failed to
# reproduce the original run by 13.6 percent, i.e. the stack is non-deterministic
# at FIXED seed and config. Both effects were present and confounded.
#
# THE SEPARATION: run both policies on ONE machine, same cell, same everything.
#   arm F  seed FIXED at 0, 8 repeats   -> pure stack non-determinism
#   arm I  seed VARIED 0..7, 8 runs     -> stack + initial-condition sensitivity
# If spread(I) is materially larger than spread(F), initial conditions matter.
# If they are comparable, the 10.20 flip is stack noise and the independent-start
# framing must be weakened.
#
# WHY BOTH ARMS RUN HERE rather than comparing against the LS6 ensemble: LS6 is
# warp 1.12.1 on x86_64 A100, Vista is warp 1.15.0 on aarch64 GH200. Comparing an
# LS6 independent-start arm against a Vista fixed-seed arm would confound seed
# policy with machine. Arm I also gives a cross-machine check of 10.20 for free.
#
# Cell: silverado, n_grid 96, 2270 kg, the margin-0 knife edge, which is where a
# discrete gate is most likely to move.
# ============================================================================
set -uo pipefail
D=/work/11603/jcerrell0629/vista/d5_seedpolicy
PY=/work/11603/jcerrell0629/vista/mpm-engine/.venv/bin/python
export PYTHONPATH=/work/11603/jcerrell0629/vista/mpm-engine/src:/work/11603/jcerrell0629/vista/.venv/lib/python3.12/site-packages:$D
export CANFORD_REPO=$D
BASE=$D/out
mkdir -p $BASE
PROV=$BASE/00_provenance.txt
{ echo "start=$(date -Is) host=$(hostname) machine=vista-gh200-aarch64"
  echo "driver sha256: $(sha256sum $D/renders/yaris_render_s1/sim_standing.py)"
  echo "wrapper sha256: $(sha256sum $D/analysis/ensemble_seed_runner.py)"
  $PY -c "import warp,trimesh,numpy;print('warp',warp.__version__,'trimesh',trimesh.__version__,'numpy',numpy.__version__)"
  nvidia-smi --query-gpu=index,name,memory.used --format=csv,noheader
} >> $PROV 2>&1
one() { # label seed
  local L=$1 S=$2 O=$BASE/$1
  [ -e "$O" ] && { echo "skip $L"; return 0; }
  mkdir -p "$O"
  echo "=== $(date -Is) $L seed=$S"
  ENSEMBLE_SEED=$S $PY $D/analysis/ensemble_seed_runner.py --vehicle silverado --grid 96 \
    --mass 2270.0 --label "$L" --out "$O" --depth 0.30 --velocity 1.5 --frames 90 \
    --eta 1.0e-3 --floor-friction 0.55 > $BASE/$L.log 2>&1
  echo "RC_${L}=$?" >> $PROV
}
for i in 0 1 2 3 4 5 6 7; do one FIXED_s0_r$i 0; done      # arm F: seed pinned
for s in 0 1 2 3 4 5 6 7; do one INDEP_s$s   $s; done      # arm I: seed varied
echo "ALLDONE end=$(date -Is)" >> $PROV
