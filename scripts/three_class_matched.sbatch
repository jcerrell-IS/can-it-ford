#!/bin/bash
#SBATCH -J 3class
#SBATCH -o /scratch/11603/jcerrell0629/three_class_matched_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/three_class_matched_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 01:30:00
#SBATCH -A BCS20003
# ============================================================================
# BATCH, NOT idev, deliberately and on the record.
#
# Per memory vista-su-burn-is-idev-not-science.md, re-verified 2026-08-13:
# interactive burns 98.5 to 99.1 percent of Vista node-hours against every gated
# run and 95 of 184 jobs ended in TIMEOUT, while LS6 shows 0 batch timeouts.
# LS6 also has a one-idev-per-user QOS cap. The science here is minutes long, so
# it goes to batch and the allocation ends when the work ends.
#
# WALL TIME. 90 min requested against an estimate of roughly 10 to 30 min. The
# estimate is anchored on rs_sweep_v2, which ran six rogue/silverado runs at
# g64/g96/g128 in 3 minutes (00_provenance.txt, 05:16:09 to 05:19:09). This job
# is nine runs and the matched arms carry more particles and more substeps than
# anything in that sweep: ~1.25 M water particles per matched arm against
# ~0.35 M for the heaviest rs_sweep_v2 run, and substeps rise with 1/dx. It also
# writes nine rollout.npz, which for the Silverado arms is ~90 x 593k x 3 float32
# before compression. The margin is deliberate, not a runtime estimate.
#
# NON-CANONICAL. Every path written is inside
# /scratch/11603/jcerrell0629/three_class_matched_<TAG>/, a NEW directory the
# runner refuses to reuse. No canonical store is touched.
# ============================================================================
set -uo pipefail

echo "=== allocation ==="
date -Is
hostname
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-none} partition=${SLURM_JOB_PARTITION:-none}"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader

export CUDA_VISIBLE_DEVICES=0

bash /scratch/11603/jcerrell0629/run_three_class_matched.sh "${1:-2026-08-14}"
RC=$?
echo "runner rc=$RC"
echo "=== done ==="
date -Is
exit $RC
