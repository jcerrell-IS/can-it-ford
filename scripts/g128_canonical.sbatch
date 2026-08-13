#!/bin/bash
#SBATCH -J g128canon
#SBATCH -o /scratch/11603/jcerrell0629/g128_canonical_%j.out
#SBATCH -e /scratch/11603/jcerrell0629/g128_canonical_%j.err
#SBATCH -p gpu-a100-dev
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -t 00:40:00
#SBATCH -A BCS20003
# ============================================================================
# BATCH, NOT idev, deliberately. sacct on this account shows the interactive
# split: jobs 3362340, 3362386 and 3362478 all ended TIMEOUT at 00:30:01 with
# nobody attached, and 3362208, which produced the g128 Rogue/Silverado rows now
# cited in register J15, was itself an idev session that ran to a 2-hour TIMEOUT
# to do about 3 minutes of stepping. The science here is a few minutes long, so it
# goes to batch and the allocation ends when it ends.
#
# Wall time 40 min against a measured 3 min for six comparable runs (rs_sweep_v2,
# 05:16:09 to 05:19:09). g128 carries more particles than anything in that sweep,
# so the margin is deliberate, not an estimate of the runtime.
# ============================================================================
set -uo pipefail

echo "=== allocation ==="
date -Is
hostname
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-none} partition=${SLURM_JOB_PARTITION:-none}"

export CUDA_VISIBLE_DEVICES=0

bash /scratch/11603/jcerrell0629/run_g128_canonical.sh "${1:-2026-08-13}"
RC=$?
echo "runner rc=$RC"
echo "=== done ==="
date -Is
exit $RC
