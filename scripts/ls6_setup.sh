#!/bin/bash
# Stand up warpmpm on LS6, pinned to exactly what Vista runs.
#
# WHY LS6 AT ALL. Measured 2026-08-18: Vista had 616 SUs left and LS6 had 9,539,
# so LS6 holds 15.5x the remaining budget and had nothing installed on it.
#
# WHY THE PINS ARE THE WHOLE POINT. Left to itself, pip installs warp-lang 1.16.0
# on LS6 while Vista runs 1.15.0. A cross-machine comparison across two different
# solver versions is not a cross-machine comparison. Every version below is pinned
# to the value MEASURED on Vista the same day:
#
#     warp-lang    1.15.0          ($WORK/.venv/bin/python -c "import warp")
#     torch        2.11.0+cu128    (same)
#     mpm-engine   627367e         (git -C $WORK/mpm-engine rev-parse --short HEAD)
#
# NOTE ON 627367e. That is VISTA'S working-copy HEAD, which is NOT the SHA this
# repo vendors (third_party/mpm-engine-544c93dd). That discrepancy is recorded and
# unresolved. This script deliberately matches VISTA, because the point is to
# reproduce Vista's results; if the vendored SHA is later declared canonical, change
# the pin here and re-run the reproduction rather than assuming it still holds.
#
# ARCHITECTURE. LS6 is x86_64, Vista is aarch64. That is why the install takes
# minutes here with stock wheels. It also means note L-8's DualSPHysics
# "x86-only static libraries, hard aarch64 blocker" does not apply on this machine.
#
# TWO TRAPS, both hit on 2026-08-18:
#   1. `module load python/3.12.11` does NOT change what `python3` resolves to.
#      Use the absolute interpreter path below.
#   2. scripts/tacc.sh refuses commands containing destructive verbs, so this
#      script never deletes. If a venv already exists at the target path it stops
#      rather than clobbering it; remove it yourself if that is what you want.

set -euo pipefail

WORK=/work/11603/jcerrell0629/ls6
PY=/opt/apps/python/3.12.11/bin/python3      # trap 1: absolute, not `python3`
VENV=$WORK/.venv-mpm312
ENGINE=$WORK/mpm-engine

WARP_PIN="1.15.0"
TORCH_PIN="2.11.0"
TORCH_INDEX="https://download.pytorch.org/whl/cu128"
ENGINE_PIN="627367e"

if [ -e "$VENV" ]; then
    echo "[ls6_setup] $VENV already exists; stopping rather than overwriting it." >&2
    echo "[ls6_setup] Remove it yourself if you want a clean rebuild." >&2
    exit 3
fi

echo "[ls6_setup] interpreter: $($PY --version)"
"$PY" -m venv "$VENV"
V="$VENV/bin/python"
"$V" -m pip install --quiet --upgrade pip setuptools wheel

echo "[ls6_setup] warp-lang==$WARP_PIN, numpy, trimesh"
"$V" -m pip install --quiet "warp-lang==$WARP_PIN" numpy trimesh

echo "[ls6_setup] torch==$TORCH_PIN from $TORCH_INDEX (large download, several minutes)"
"$V" -m pip install --quiet "torch==$TORCH_PIN" --index-url "$TORCH_INDEX"

if [ ! -d "$ENGINE" ]; then
    echo "[ls6_setup] cloning mpm-engine"
    git clone --quiet https://github.com/kks32/mpm-engine.git "$ENGINE"
fi
git -C "$ENGINE" checkout --quiet "$ENGINE_PIN"

echo "[ls6_setup] verifying the pins actually took"
PYTHONPATH="$ENGINE/src" "$V" - <<'PYEOF'
import warp, torch, warpmpm
assert warp.config.version == "1.15.0", "warp pin drifted: %s" % warp.config.version
assert torch.__version__.startswith("2.11.0"), "torch pin drifted: %s" % torch.__version__
print("warp", warp.config.version, "| torch", torch.__version__)
print("warpmpm", warpmpm.__file__)
PYEOF
echo "[ls6_setup] engine SHA $(git -C "$ENGINE" rev-parse --short HEAD)"
echo "[ls6_setup] OK. Run with:"
echo "  PYTHONPATH=$ENGINE/src $V your_driver.py ..."
echo "[ls6_setup] GPU queues here are gpu-a100, gpu-a100-dev and gpu-h100."
