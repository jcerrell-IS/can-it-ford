#!/bin/bash
# D13 x86 reproduction of the Chrono GetNormal vertex-hit defect.
# Self-contained: builds Chrono core+vehicle (CPU only, no CUDA, no GPU),
# regenerates the mesh, embeds and compiles the classifier, runs it.
# Controlled against the Vista aarch64 build: same Chrono SHA, gcc 13.2.0,
# cmake 4.1.1, Eigen 3.4.0. Only the ISA differs.
set -uo pipefail

SRCROOT=$SCRATCH/chrono_x86_2026-08-14
BUILDDIR=$WORK/chrono_x86_build          # NOT $SCRATCH: file(COPY) mtime fails there
OBJ=$SCRATCH/external_road_x86.obj
EIGEN=$SRCROOT/eigen-3.4.0

module load gcc/13.2.0 2>/dev/null
module load cmake/4.1.1 2>/dev/null

echo "node $(hostname)   arch $(uname -m)"
echo "g++   $(g++ --version | head -1)"
echo "cmake $(cmake --version | head -1)"
echo "chrono $(git -C "$SRCROOT/chrono" rev-parse HEAD 2>/dev/null)"

# --- Eigen -------------------------------------------------------------------
if [ ! -d "$EIGEN" ]; then
  ( cd "$SRCROOT" && curl -sL -o eigen.tgz \
      https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz && tar xzf eigen.tgz )
fi
echo "eigen $(test -d "$EIGEN" && echo OK || echo MISSING)"

# --- configure + build -------------------------------------------------------
if [ ! -f "$BUILDDIR/lib/libChrono_vehicle.so" ]; then
  mkdir -p "$BUILDDIR" && cd "$BUILDDIR" || exit 1
  cmake "$SRCROOT/chrono" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_COMPILER="$(which gcc)" \
    -DCMAKE_CXX_COMPILER="$(which g++)" \
    -DEIGEN3_INCLUDE_DIR="$EIGEN" \
    -DCHRONO_GPU_VENDOR=NONE \
    -DCH_ENABLE_MODULE_VEHICLE=ON \
    -DCH_ENABLE_MODULE_FSI=OFF \
    -DBUILD_DEMOS=OFF -DBUILD_TESTING=OFF -DBUILD_BENCHMARKING=OFF \
    > "$BUILDDIR/cfg.log" 2>&1
  echo "configure rc=$?"
  grep -m3 "CMake Error" "$BUILDDIR/cfg.log" 2>/dev/null
  make -j 16 > "$BUILDDIR/build.log" 2>&1
  echo "build rc=$?"
  tail -3 "$BUILDDIR/build.log"
fi
ls "$BUILDDIR/lib/libChrono_vehicle.so" >/dev/null 2>&1 || { echo "BUILD FAILED, stopping"; exit 1; }

# --- mesh, identical maths to the Vista one ----------------------------------
[ -f "$OBJ" ] || python3 "$SCRATCH/make_obj_portable.py" "$OBJ"
echo "mesh $(wc -c < "$OBJ") bytes"

# --- classifier --------------------------------------------------------------
cat > "$SRCROOT/classify.cpp" <<'CPPEOF'
#include <cstdio>
#include <cmath>
#include <string>
#include "chrono/physics/ChSystemSMC.h"
#include "chrono/physics/ChContactMaterialSMC.h"
#include "chrono_vehicle/terrain/RigidTerrain.h"
using namespace chrono;
using namespace chrono::vehicle;
static void truth(double x, double y, double& nx, double& ny, double& nz) {
    double e = 0.15 * std::exp(-(((x - 5) * (x - 5)) + y * y) / 2.0);
    double zx = e * (-(x - 5)), zy = 0.02 + e * (-y);
    double m = std::sqrt(zx * zx + zy * zy + 1.0);
    nx = -zx / m; ny = -zy / m; nz = 1.0 / m;
}
int main(int argc, char** argv) {
    std::string obj = (argc > 1 ? argv[1] : "external_road.obj");
    ChSystemSMC sys;
    sys.SetCollisionSystemType(ChCollisionSystem::Type::BULLET);
    auto mat = chrono_types::make_shared<ChContactMaterialSMC>();
    RigidTerrain terrain(&sys);
    terrain.AddPatch(mat, ChCoordsys<>(ChVector3d(0,0,0), QUNIT), obj, true, 0.0, true);
    terrain.Initialize();
    sys.DoStepDynamics(1e-4);
    const double sx = 0.125, sy = 0.05;
    long cnt[3][2] = {{0,0},{0,0},{0,0}};
    double worst[3] = {0,0,0};
    for (int i = 0; i < 60; i++) for (int j = 0; j < 60; j++) for (int mode = 0; mode < 3; mode++) {
        double x = -12.0 + i * 0.125, y = -4.0 + j * 0.05;
        if (mode == 1) x += sx / 2;
        if (mode == 2) { x += sx / 2; y += sy / 2; }
        auto n = terrain.GetNormal(ChVector3d(x, y, 20.0));
        double tx, ty, tz; truth(x, y, tx, ty, tz);
        double dot = n.x()*tx + n.y()*ty + n.z()*tz;
        if (dot > 1.0) dot = 1.0; if (dot < -1.0) dot = -1.0;
        double ang = std::acos(dot) * 180.0 / M_PI;
        bool bad = ang > 5.0;
        cnt[mode][bad ? 1 : 0]++;
        if (ang > worst[mode]) worst[mode] = ang;
    }
    const char* names[3] = {"ON-VERTEX (both on grid)","ON-EDGE  (one on grid)","INTERIOR (neither)"};
    printf("=== RESULT TABLE ===\n");
    printf("%-28s %8s %8s %9s %12s\n","class","samples","bad","bad rate","worst angle");
    for (int c = 0; c < 3; c++) {
        long n = cnt[c][0] + cnt[c][1];
        printf("%-28s %8ld %8ld %8.1f%% %11.2f deg\n", names[c], n, cnt[c][1],
               100.0 * cnt[c][1] / (n ? n : 1), worst[c]);
    }
    printf("'bad' = returned normal more than 5 deg from the analytic normal.\n");
    printf("Vista aarch64 gave: 100.0%% / 0.0%% / 0.0%%, worst 88.85 / 1.02 / 1.09 deg.\n");
    return 0;
}
CPPEOF

SRC=$SRCROOT/chrono/src
g++ -std=c++17 -O2 "$SRCROOT/classify.cpp" -o "$SRCROOT/classify_x86" \
  -I"$SRC" -I"$BUILDDIR" -I"$EIGEN" -I"$SRC/chrono_thirdparty/yaml-cpp/include" \
  -L"$BUILDDIR/lib" -lChrono_core -lChrono_vehicle -lyaml-cpp \
  -Wl,-rpath,"$BUILDDIR/lib" 2>&1 | tail -4

echo
"$SRCROOT/classify_x86" "$OBJ" 2>&1 | tail -12
