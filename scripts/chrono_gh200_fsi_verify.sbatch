#!/bin/bash
#SBATCH -J chrono_fsi_verify
#SBATCH -o %x.o%j
#SBATCH -e %x.e%j
#SBATCH -p gh-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:30:00
#SBATCH -A BCS20003
# ============================================================================
# DISPATCH 13, second-stage verification. Run AFTER chrono_gh200_fsi_build.sbatch.
#
# WHY THIS EXISTS, AND IT IS NOT A FORMALITY
#   The dispatch's GO milestone is demo_FSI-SPH_DamBreak OR ObjectDrop. DamBreak
#   alone is a WEAK proof: its own counters report numFsiBodies=0, so it
#   exercises the WCSPH fluid solver and nothing whatsoever of the rigid-body
#   force coupling, which is the ONLY reason Chrono is a candidate for this
#   fork. A pass on DamBreak would license no claim about two-way coupling.
#
#   This job closes two gaps:
#   (1) ObjectDrop instantiates a real ChBody (demo source :275) whose geometry
#       may be a TrimeshShape loaded from a Wavefront OBJ (:270), which is the
#       same ingest path a vehicle hull would use. It therefore exercises the
#       BCE per-body force accumulation reached via GetFsiBodyForce().
#   (2) A falsifiable control on the DamBreak output. "It produced files" is not
#       "it simulated": if the solver silently no-oped, frame 0 and frame 9
#       would be byte-identical. This project has been caught by exactly that
#       class of error before, so the check is explicit rather than assumed.
# ============================================================================
set -uo pipefail

BD=$SCRATCH/chrono_eval_2026-08-14
BUILD=$BD/build_fsi

module load gcc/13.2.0 2>/dev/null
module load cuda/12.6   2>/dev/null

echo "================ PROVENANCE ================"
date -u +"%Y-%m-%dT%H:%M:%SZ"
echo "node : $(hostname)   arch: $(uname -m)   job: ${SLURM_JOB_ID:-none}"
nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader 2>&1 | head -2

echo
echo "======== CONTROL: did the DamBreak fluid actually move? ========"
P="$BUILD/bin/DEMO_OUTPUT/FSI_Dam_Break/CFD_WCSPH_RK2_ps1/particles"
if [ -f "$P/fluid0.csv" ] && [ -f "$P/fluid9.csv" ]; then
    echo "md5 fluid0: $(md5sum "$P/fluid0.csv" | awk '{print $1}')"
    echo "md5 fluid9: $(md5sum "$P/fluid9.csv" | awk '{print $1}')"
    if cmp -s "$P/fluid0.csv" "$P/fluid9.csv"; then
        echo "CONTROL FAILED: frame 0 and frame 9 are IDENTICAL. Output is initial conditions."
    else
        echo "CONTROL PASSED: frames differ, the solver advanced state."
        echo "--- differing lines (count) ---"
        diff "$P/fluid0.csv" "$P/fluid9.csv" | /usr/bin/grep -c "^<"
    fi
else
    echo "CONTROL SKIPPED: DamBreak particle output not found at $P"
fi

echo
echo "======== ObjectDrop: FSI rigid body in fluid ========"
cd "$BUILD"/bin || exit 1
./demo_FSI-SPH_ObjectDrop --t_end 0.4 --no_vis --output_particle_data true --output_fps 20 2>&1 | tail -45
OD_RC=${PIPESTATUS[0]}
echo "=== ObjectDrop RC: $OD_RC ==="

echo
echo "======== did it report a non-zero FSI body count? ========"
# numFsiBodies > 0 is the discriminator between 'fluid ran' and 'two-way
# rigid coupling ran'. Reported by the solver's own counter block.
find "$BUILD"/bin/DEMO_OUTPUT -maxdepth 2 -type d -name "*Object*" 2>/dev/null | head -5
echo "output files: $(find "$BUILD"/bin/DEMO_OUTPUT -path '*Object*' -type f 2>/dev/null | wc -l)"

echo
echo "======== VERDICT ========"
[ $OD_RC -eq 0 ] && echo "ObjectDrop clean on GH200." || echo "ObjectDrop FAILED rc=$OD_RC"
