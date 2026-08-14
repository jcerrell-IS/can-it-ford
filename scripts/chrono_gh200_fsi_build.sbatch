#!/bin/bash
#SBATCH -J chrono_fsi_gh200
#SBATCH -o %x.o%j
#SBATCH -e %x.e%j
#SBATCH -p gh-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00
#SBATCH -A BCS20003
# ============================================================================
# DISPATCH 13, engine go/no-go: does Chrono::FSI-SPH build and run on GH200?
#
# This is the recipe that was actually executed, not a reconstruction. It
# compiles Project Chrono with the FSI-SPH (CUDA) module on TACC Vista
# (NVIDIA Grace Hopper GH200, aarch64) and runs demo_FSI-SPH_DamBreak.
#
# WHY BATCH AND NOT idev
#   The Vista login node reports nproc=1 under its cgroup limit, so a login
#   node compile is both slow and against policy. GPU hardware is also
#   required at CONFIGURE time unless CHRONO_GPU_VENDOR is forced (see below).
#
# FOUR THINGS THAT ARE NOT OBVIOUS AND EACH COST A CONFIGURE CYCLE
#   1. The Vista default compiler is NVHPC nvc++ (module nvidia/24.7). Chrono's
#      C++17 feature check FAILS against it: "ERRORChrono requires at least
#      C++17 support". Load gcc/13.2.0 and pass the compilers explicitly.
#      13.x is also the newest host GCC that CUDA 12.6 accepts.
#   2. Chrono does not vendor Eigen. EIGEN3_INCLUDE_DIR must be supplied.
#      FSI-SPH additionally requires Eigen >= 3.3.6 (src/chrono_fsi/sph/
#      CMakeLists.txt returns early below that); 3.4.0 satisfies it.
#   3. Chrono resolves the GPU vendor by probing for HARDWARE via nvidia-smi,
#      not by finding the SDK. On any host without a visible GPU it reports
#      "GPU target vendor: NONE" and silently drops the CUDA backend.
#      -DCHRONO_GPU_VENDOR=NVIDIA bypasses detection entirely.
#   4. The FSI-SPH docs state "requires CUDA version 12.8 or newer". Vista's
#      newest module is cuda/12.6. That requirement is NOT enforced anywhere
#      in CMake, so configure succeeds; whether it survives compilation is
#      precisely what this job tests. Do not assume either outcome.
# ============================================================================
set -uo pipefail

BD=$SCRATCH/chrono_eval_2026-08-14
SRC=$BD/chrono
BUILD=$BD/build_fsi
EIGEN=$BD/deps/eigen-3.4.0

echo "================ PROVENANCE ================"
date -u +"%Y-%m-%dT%H:%M:%SZ"
echo "node       : $(hostname)"
echo "arch       : $(uname -m)"
echo "slurm job  : ${SLURM_JOB_ID:-none}  partition ${SLURM_JOB_PARTITION:-none}"
echo "chrono sha : $(git -C "$SRC" rev-parse HEAD 2>/dev/null)"

module load gcc/13.2.0 2>/dev/null
module load cuda/12.6   2>/dev/null

echo "cores      : $(nproc)"
echo "gcc        : $(g++ --version | head -1)"
echo "nvcc       : $(nvcc --version | tail -2 | head -1)"
echo "cmake      : $(cmake --version | head -1)"
echo "--- GPU actually present on this node ---"
nvidia-smi --query-gpu=name,compute_cap,driver_version,memory.total --format=csv 2>&1 | head -5

echo
echo "================ CONFIGURE ================"
mkdir -p "$BUILD"
cd "$BUILD" || exit 1
cmake "$SRC" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER="$(which gcc)" \
  -DCMAKE_CXX_COMPILER="$(which g++)" \
  -DEIGEN3_INCLUDE_DIR="$EIGEN" \
  -DCHRONO_GPU_VENDOR=NVIDIA \
  -DCHRONO_CUDA_ARCHITECTURES=90 \
  -DCH_ENABLE_MODULE_FSI=ON \
  -DBUILD_DEMOS=ON -DBUILD_TESTING=OFF -DBUILD_BENCHMARKING=OFF \
  -DCMAKE_INSTALL_PREFIX="$BD/install_fsi"
CFG_RC=$?
echo "=== CONFIGURE RC: $CFG_RC ==="
[ $CFG_RC -ne 0 ] && exit $CFG_RC

echo
echo "================ BUILD ================"
# Bounded parallelism: nvcc on the SPH translation units is memory hungry and
# the Grace superchip has 72 cores against shared LPDDR5X.
BUILD_START=$SECONDS
make -j 24 2>&1 | tail -80
BUILD_RC=${PIPESTATUS[0]}
echo "=== BUILD RC: $BUILD_RC  elapsed: $((SECONDS - BUILD_START))s ==="

echo
echo "================ ARTIFACTS ================"
ls -la "$BUILD"/bin/ 2>&1 | /usr/bin/grep -iE "FSI|total" | head -25

if [ $BUILD_RC -ne 0 ]; then
    echo "BUILD FAILED. Not attempting the demo."
    exit $BUILD_RC
fi

echo
echo "================ GO/NO-GO DEMO ================"
# Milestone fixed in advance by the dispatch: a clean run of
# demo_FSI-SPH_DamBreak or demo_FSI-SPH_ObjectDrop on a GH200 node,
# producing output. Short t_end keeps this a build/run proof, not a physics run.
cd "$BUILD"/bin || exit 1
DEMO_START=$SECONDS
./demo_FSI-SPH_DamBreak --t_end 0.5 --no_vis --output --output_fps 20 2>&1 | tail -40
DEMO_RC=${PIPESTATUS[0]}
echo "=== DEMO RC: $DEMO_RC  elapsed: $((SECONDS - DEMO_START))s ==="

echo
echo "================ OUTPUT PRODUCED ================"
find "$BUILD" -path "*FSI_Dam_Break*" -type f 2>/dev/null | head -20
echo "file count: $(find "$BUILD" -path '*FSI_Dam_Break*' -type f 2>/dev/null | wc -l)"

echo
echo "================ VERDICT ================"
if [ $BUILD_RC -eq 0 ] && [ $DEMO_RC -eq 0 ]; then
    echo "GO: Chrono::FSI-SPH built and ran a clean demo on GH200 aarch64."
else
    echo "NO-GO: build_rc=$BUILD_RC demo_rc=$DEMO_RC"
fi
