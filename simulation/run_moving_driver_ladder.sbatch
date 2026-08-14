#!/bin/bash
# DISPATCH 9: arms (a) and (b) for the driven hull, as a RESOLUTION LADDER.
#
# BATCH, not idev. Per the project's own measurement, interactive burned 98.5 to 99.1
# percent of Vista node-hours with 95 of 184 jobs ending in TIMEOUT, while LS6 shows
# 0 batch timeouts. GPU work is routed to LS6 as batch.
#
# WHY A LADDER RATHER THAN ONE RUN. The exploratory scene's finding is that this
# geometry cannot resolve its own water column: at the canonical 0.30 m depth the
# water is 1.84 cells deep at n_grid 64 against the validated harness's 18. A single
# run therefore cannot distinguish a physical result from a resolution artefact. Three
# resolutions can at least show which way the numbers move.
#
# THE SDF CACHE IS SHARED ACROSS THE THREE RUNS ON PURPOSE. load_vehicle is seeded, so
# the mesh is bitwise identical between runs and build_sdf_cached's content hash
# matches. Run 1 pays the build; runs 2 and 3 should hit the cache. That is a live
# demonstration of the seeded-load fix, and the log records each build time.
#
#SBATCH -J d9_moving
#SBATCH -o /scratch/11603/jcerrell0629/fork_moving_driver_2026-08-14/logs/d9_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/fork_moving_driver_2026-08-14/logs/d9_%j.err
#SBATCH -p gpu-a100
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00
#SBATCH -A BCS20003

set -o pipefail

OUT=/scratch/11603/jcerrell0629/fork_moving_driver_2026-08-14
ENGINE=/work/11603/jcerrell0629/vista/can-it-ford/mpm-engine/src
PY=/scratch/11603/jcerrell0629/warpmpm_ls6_env/bin/python
HULL=/work/11603/jcerrell0629/vista/hulls/rogue_g96_pd8_coarse_watertight.ply

export PYTHONPATH="$OUT/pylibs:$ENGINE"

echo "host=$(hostname)  jobid=${SLURM_JOB_ID}  start=$(date -Is)"
nvidia-smi || echo "NO GPU VISIBLE"

cd "$OUT" || exit 1

echo "=============== engine provenance ==============="
git -C /work/11603/jcerrell0629/vista/can-it-ford/mpm-engine rev-parse HEAD
echo "expected 544c93dd02cb9c7ead89e1155a62967243244fce"
sha256sum "$HULL"
echo "expected c0b778e2c443263105c079ec5fed7b68a9aca902e51d21fac5153b2f06c310b2"

echo "=============== trap contract tests, ON THE GPU ==============="
"$PY" tests/test_sdf_wrench_contract.py --json-out "$OUT/out/trap_tests_gpu.json"
echo "trap_tests_rc=$?"

echo "=============== geometry gate ==============="
"$PY" analysis/hull_geometry_gate.py --ply "$HULL" --repeats 1 \
      --json-out "$OUT/out/gate_gpu.json"
echo "gate_rc=$?"

for NG in 64 96 128; do
  echo "=============== driven hull, n_grid=${NG} ==============="
  "$PY" simulation/moving_vehicle_driver.py \
      --ply "$HULL" \
      --n-grid "$NG" \
      --depth 0.30 \
      --velocity 1.5 \
      --mass 1609.0 \
      --sdf-res 32 \
      --settle-frames 60 \
      --ramp-frames 15 \
      --drive-frames 70 \
      --mesh-seed 0 --water-seed 0 \
      --cache-dir "$OUT/sdf_cache" \
      --out "$OUT/out" \
      --tag "driven_g${NG}"
  echo "run_g${NG}_rc=$?"
done

echo "end=$(date -Is)"
