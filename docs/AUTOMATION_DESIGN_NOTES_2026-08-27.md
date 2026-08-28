# Automation design notes: SLURM to W&B, HF webhook, headless CI

Design only. **Nothing in this file was wired, and nothing should be wired from it
without checking back.** Written 2026-08-27.

Claims are tagged. **[CONFIRMED]** was measured. **[DOC]** was read from a primary
document. **[INFERRED]** is reasoning.

## 6c. Two bridges, designed and deliberately not built

### 6c-i. SLURM to W&B bridge

The problem is that a GPU node cannot reach the network, so `wandb.init()` inside an
allocation cannot stream. The shape that fits is offline logging plus a deferred
upload, and there are two ways to run the upload.

**Option A, dependent SLURM job.** Set `WANDB_MODE=offline` in the batch script, then
chain `sbatch --dependency=afterok:$SLURM_JOB_ID sync_wandb.sh`, where the sync script
walks `wandb/offline-run-*` and calls `wandb sync` on each.

**Option B, login-node sync, no second job.** Same offline logging, but the upload runs
on the login node afterward, reading the run directory straight off the shared
filesystem.

**Option B is cheaper and is the recommendation.** Every TACC job bills a 0.25 hour
floor regardless of how long it runs, so option A spends a second 15 minute floor per
run purely to move a few megabytes. Option B spends nothing, because login nodes are
not billed. The same argument favours Trackio over W&B for this specific seam, and that
comparison is written up separately in `docs/TRACKIO_OFFLINE_VISTA_2026-08-27.md`.

**Unverified and load-bearing:** the premise that Vista compute nodes have no outbound
internet was **not measured**. Measure it before building either option, because if the
premise is false the whole bridge is unnecessary.

### 6c-ii. HF Hub webhook to GitHub repository_dispatch

Watch `josiecerrell/can-it-ford-results` for `repo.update`, and have the webhook fire a
GitHub `repository_dispatch` event that triggers a regeneration workflow.

**This one has a credential problem that the W&B bridge does not.** A
`repository_dispatch` call requires a GitHub token with `repo` scope, and that token
has to be stored in the HF webhook configuration, which is outside this repository and
outside its review path. A leaked token there is write access to a public repository.

**The alternative that avoids the token entirely** is to target an HF Job directly
rather than GitHub. The payload arrives as `WEBHOOK_PAYLOAD` carrying `event.action`,
`repo.type`, `repo.name` and `repo.owner`, the job runs inside Hugging Face, and no
GitHub credential is created or stored. **[INFERRED]** that this is sufficient for the
intended use, which is regenerating a figure or re-running the L0 sweep when new
simulation output lands.

**Recommendation: if this gets built, target an HF Job, not `repository_dispatch`.**
Not built, not wired.

## 6d. Headless Claude Code in GitHub Actions. STOP POINT.

**This one is blocked on an explicit decision from Josie and was not implemented.**

### What it would need

Two new GitHub Actions secrets: `ANTHROPIC_API_KEY` and `CLAUDE_GITHUB_APP_TOKEN`,
plus `anthropics/claude-code-action@v1` in automation mode, triggered by
`workflow_dispatch`, `schedule` or `push`, with no mention required.

### Why this is not a config tweak

**The repository is public.** [CONFIRMED] 2026-08-27 against the GitHub API:
`jcerrell-IS/can-it-ford`, `private: false`, `visibility: public`, 0 forks. Five
workflows already exist: `canford-checks.yml`, `csv-check.yml`, `hf-space-checks.yml`,
`physics-consistency-review.yml`, `sync-to-hub.yml`.

Three consequences, and the first is the one that matters.

**1. A public repository means anyone can propose a workflow run.** GitHub withholds
secrets from `pull_request` runs triggered by forks, which is the protection people
rely on. That protection is lost the moment a workflow uses `pull_request_target`,
which runs in the context of the base repository **with** secrets available. A
`pull_request_target` workflow that checks out the pull request head and then executes
anything from it is the standard exfiltration path for repository secrets. Any Claude
Code workflow added here must therefore be restricted to `workflow_dispatch` and
`schedule`, both of which run from the default branch and require write access to
trigger, and must never use `pull_request_target`. Forks are currently 0, which lowers
present exposure but is not a control, since a fork can be created by anyone at any
time.

**2. `ANTHROPIC_API_KEY` is a billing-bearing credential.** Unlike a read-scoped token,
a leak is not only an access problem, it is a direct financial one, and it is spendable
by whoever holds it until it is rotated.

**3. The cost is recurring and unbounded by default.** A `schedule` trigger bills tokens
on every firing whether or not anything changed. If this is built, it needs
`--max-turns` set, a least-privilege `--allowedTools` list, and a concrete answer to
how often it should fire.

### What headless CI can and cannot see

**A GitHub-hosted runner has no route into the TACC filesystem.** The corrections
register, the run manifests and the mesh data are not reachable from it. So a CI job
here can check claims against the repository and the open web, and it cannot verify
anything that requires reading a run directory on Vista. The complementary pattern is
`claude -p` running **on** Vista as a SLURM dependency, which sees the filesystem but
needs no GitHub secret at all.

**That asymmetry is the actual design conclusion: the Vista-side headless job is both
cheaper and lower risk than the GitHub Actions one, and it covers the data that
matters.** If only one gets built, build that one.

### The decision Josie has to make

Adding `ANTHROPIC_API_KEY` and `CLAUDE_GITHUB_APP_TOKEN` to a public repository's
secrets is a new attack surface and a new recurring cost. **Neither secret was added,
and neither should be added on an agent's judgment.** The question to answer is whether
the GitHub-side automation is worth it at all, given that the Vista-side job covers the
data the project actually needs checked.
