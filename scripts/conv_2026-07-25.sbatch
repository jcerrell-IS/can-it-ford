#!/bin/bash
#SBATCH -J yarisconv
#SBATCH -A BCS20003
#SBATCH -p gh-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 02:00:00
#SBATCH -o /work/11603/jcerrell0629/vista/render_s2/conv_2026-07-25/slurm_%j.out
#SBATCH -e /work/11603/jcerrell0629/vista/render_s2/conv_2026-07-25/slurm_%j.err

# No set -e. A failing task must not abort the ones after it.
set -o pipefail

PY=/work/11603/jcerrell0629/vista/.venv/bin/python
ENGINE=/work/11603/jcerrell0629/vista/mpm-engine
BASE=/work/11603/jcerrell0629/vista/render_s2
LOGS=$BASE/conv_2026-07-25

mkdir -p "$LOGS"

{
  echo "job=${SLURM_JOB_ID}  host=$(hostname)  start=$(date -Is)"
  nvidia-smi --query-gpu=name,memory.total --format=csv
  "$PY" -c "import warpmpm; print('warpmpm resolves to:', warpmpm.__file__)"
  echo "driver sha256: $(sha256sum "$BASE/sim_standing.py")"
  echo "runner sha256: $(sha256sum "$BASE/run_s2.sh")"
} > "$LOGS/00_provenance.txt" 2>&1
sync

echo "=== TASK 1 pytest incline benchmarks  $(date -Is) ==="
cd "$ENGINE" || exit 1
timeout 900 "$PY" -m pytest tests/test_analytic_benchmarks.py -v -k incline \
  > "$LOGS/01_pytest_incline.txt" 2>&1
T1=$?
sync
echo "TASK1_RC=${T1}  done=$(date -Is)" | tee -a "$LOGS/00_provenance.txt"

echo "=== TASK 2 n_grid=96 standing water, three masses  $(date -Is) ==="
timeout 5400 bash "$BASE/run_s2.sh" 96 \
  > "$LOGS/02_run_s2_g96.log" 2>&1
T2=$?
sync
echo "TASK2_RC=${T2}  done=$(date -Is)" | tee -a "$LOGS/00_provenance.txt"

# TASK 3 is OPTIONAL and is the third grid a Roache GCI needs. Two grids give a
# Richardson difference only if the order p is assumed; three grids let p be observed.
# Predicted cost about 1.6 minutes. Delete this block if you want the dispatch scope
# exactly as written.
echo "=== TASK 3 n_grid=48 third grid for GCI  $(date -Is) ==="
timeout 1800 bash "$BASE/run_s2.sh" 48 \
  > "$LOGS/03_run_s2_g48.log" 2>&1
T3=$?
sync
echo "TASK3_RC=${T3}  done=$(date -Is)" | tee -a "$LOGS/00_provenance.txt"

echo "ALLDONE T1=${T1} T2=${T2} T3=${T3}  end=$(date -Is)" | tee -a "$LOGS/00_provenance.txt"
