#!/bin/bash
#SBATCH -J 3classX
#SBATCH -o /scratch/11603/jcerrell0629/three_class_massswap_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/three_class_massswap_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:40:00
#SBATCH -A BCS20003
# ============================================================================
# BATCH, NOT idev. LS6 has a one-idev-per-user QOS cap and shows 0 batch
# timeouts, while interactive burned 98.5 to 99.1 percent of Vista node-hours
# with 95 of 184 jobs ending in TIMEOUT.
#
# WALL TIME. 40 min against a measured 6:57 for the NINE runs of job 3364497 on
# the same partition and node class, of which the three heaviest were the same
# matched-dx Silverado arms this job re-runs. Three runs here, two of them the
# heavy n_grid 154 and 111 cells. The margin is deliberate, not an estimate.
#
# NON-CANONICAL. Writes only inside
# /scratch/11603/jcerrell0629/three_class_massswap_<TAG>/, a NEW directory the
# runner refuses to reuse.
# ============================================================================
set -uo pipefail

echo "=== allocation ==="
date -Is
hostname
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-none} partition=${SLURM_JOB_PARTITION:-none}"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader

export CUDA_VISIBLE_DEVICES=0

bash /scratch/11603/jcerrell0629/run_three_class_massswap.sh "${1:-2026-08-14}"
RC=$?
echo "runner rc=$RC"
echo "=== done ==="
date -Is
exit $RC
