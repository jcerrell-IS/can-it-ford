---
description: Submit a Vista batch job the right way instead of opening an idev session
argument-hint: "<remote .sbatch path, e.g. $WORK/render_s2/conv_2026-07-25.sbatch>"
allowed-tools: Bash(scripts/tacc_submit.sh:*) Bash(scripts/tacc.sh:*)
disable-model-invocation: true
---

Submit a batch job to Vista. Target: `$ARGUMENTS`

First show me what would be submitted, without submitting:

!`scripts/tacc_submit.sh --dry vista "$ARGUMENTS"`

Then, before running it for real, check with me if any of these are true:

- An interactive `idv` or `holder` job is already running. Stacking a batch job
  on top of one doubles the burn on an allocation that had 673 SUs left.
- Vista is under 300 SUs.
- The `#SBATCH -o` or `-e` path points under `/home1`, which was 82.56% full on
  2026-08-07. Full `/home1` means the job runs and its log silently truncates.

If all clear, submit and wait:

    scripts/tacc_submit.sh vista "$ARGUMENTS" --wait

Every gated run so far took 1 to 4 minutes of node time, so `--wait` is normal
here, not a long block. When it finishes, report the final SLURM state and the
tail of stdout, and say plainly whether it COMPLETED or not. Do not describe a
run as successful on the basis of the job state alone: check the log for the
per-task return codes the sbatch files write into `00_provenance.txt`.
