# Infrastructure and gsplat findings, 2026-08-07 (session 2)

Scope: TACC allocation accounting, the LS6 gsplat environment, and the drainA
reconstruction. Every item below was produced by a live command against the
named machine on 2026-08-07, not by reading a doc or a prior summary.

**This file is not the corrections register.** Session `56110039` was holding
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` and `CLAUDE.md` at the time
of writing (commits `8637099` 09:15, `8c173ef` 09:19, `9874cb5` 09:26), so per
the standing rule against two panes touching one file, nothing here was written
into the register. **Items I-2 and I-3 below correct register entries K2 and K4
and must be merged into it once that session is parked.**

Tiering: VERIFIED means a primary read or a replicated command in this session.
INFERRED means a conclusion drawn from VERIFIED facts, flagged as such.

---

## I-1. Interactive allocations consume 99.1% of Vista node-time. VERIFIED.

    scripts/tacc.sh vista 'sacct -X -S 2026-07-01 -o JobName%24,State%12,Elapsed,NNodes --parsable2'

187 jobs since 2026-07-01, classified by job name (`idv*` and `holder` are
interactive, everything else is batch):

| category                 | jobs | node-hours | share |
|--------------------------|-----:|-----------:|------:|
| interactive (idv/holder) |  164 |     150.35 | 99.1% |
| batch (science)          |   23 |       1.29 |  0.9% |
| **total**                |  187 |     151.65 |       |

End states: 80 of the 164 interactive jobs ended in **TIMEOUT**, meaning they ran
to their wall limit with nobody attached. 83 were cancelled. 58 jobs across both
categories recorded `00:00:00` elapsed, that is, allocated and immediately dead.

Every gated result came from the batch column: `yarisfinal` 1:25, `yarisford`
1:26, `f2_three_mass` 2:48, `yarisv2` 2:34, `yarisconv` 4:03. Interactive
sessions therefore cost roughly **117x more node-time than all the science
combined**.

Vista balance the same day: **673 SUs, expiring 2026-09-30** (LS6: 9656).
Vista is the only machine with the warpmpm/GH200 path, so Vista SUs, not
wall-clock or LS6, are the binding constraint on the remaining work.

INFERRED: the driver is workflow, not carelessness. `idev` was the only path
that worked without ssh gymnastics, so it absorbed work that `sbatch` should
have taken. Note that SLURM charges elapsed time, not requested time, so the
`-t 02:00:00` in the existing sbatch files is not itself waste.

**Not yet established:** the SU-per-node-hour multiplier for `gh` and `gh-dev`
was not read from a primary source, so node-hours above must not be converted
to SUs without checking the charge rate first.

## I-1b. A new interactive Vista job started during this session. VERIFIED.

`squeue` reported an empty Vista queue at 09:31 BST. Two minutes later `sacct`
showed job **894585 `idv10946`, partition gh-dev, RUNNING, started
2026-08-07T03:32:42 node time, 30 min limit, node c642-002**. The pattern in I-1
is ongoing, not historical.

## I-2. Register K2 is wrong: there is no working gsplat environment on LS6. VERIFIED.

Four independent checks, all on LS6:

- `$SCRATCH/python-envs` does not exist (`No such file or directory`). This is
  the path in the shell history that the idev session tried to `source`.
- `$HOME/my_gsplat_env` exists but its `site-packages` contains only
  `pip`, `setuptools`, `pkg_resources`, `_distutils_hack`. No gsplat, no torch.
- No real PyTorch anywhere under `$HOME` or `$SCRATCH`. The only `torch`
  directories are `$HOME/.cache/torch` and two copies of wandb's
  `wandb/integration/torch` shim.
- `$SCRATCH/gsplat` is a source checkout, not an install.

K2 also places the environment on Lustre scratch; the only candidate is on NFS
`/home1`. A sibling directory named `can-it-ford-OLD-pre-purge` is consistent
with a prior scratch purge.

Consequence: K2's operational advice, wait 3 to 5 minutes before assuming a
slow gsplat import has failed, is actively harmful today. There is nothing to
import, so the failure is an immediate `ModuleNotFoundError`.

## I-3. Register K4 resolves to YES. drainA training completed. VERIFIED.

This **contradicts** the 2026-08-07 session-1 claim that `simple_trainer.py`
never completed on drainA and that there were no checkpoints, no `.ply` and no
stats. All three exist.

    $SCRATCH/gsplat/examples/results/drainA/

- `ckpts/ckpt_29999_rank{0,1,2}.pt`, all dated **2026-07-20 19:57**, 88 to 94 MB
  each. Three ranks means a completed multi-GPU run to the full 30,000 steps.
- `stats/val_step29999.json`: **PSNR 22.7356, SSIM 0.8249, LPIPS 0.3112,
  399,491 Gaussians.**
- Earlier checkpoints at 6999 (19:35) and 2999 (2026-07-17), so the progression
  is visible and consistent.
- `videos/traj_29999.mp4` (16.2 MB), plus `renders/` and a `tb/` tensorboard dir.
- Train wall time `ellipse_time` 1635.5 s, about 27.3 minutes.
- Config: `sh_degree: 3`, `init_type: sfm`, `camera_model: pinhole`,
  `data_factor: 1`, `max_steps: 30000`, `data_dir:
  /scratch/11603/jcerrell0629/datasets/drainA/`.

INFERRED, and the actionable part: `cfg.yml` has **`save_ply: false`**, so
despite `ply_steps: [7000, 30000]` no PLY was written at 30k. The only PLY in
the tree is `ply/point_cloud_2999.ply` from the 2026-07-17 3k-step run. Any
downstream geometry work that consumes a PLY is therefore currently reading a
3,000-step model, not the finished 30,000-step one. The fix is to re-export from
`ckpt_29999_rank0.pt` rather than to retrain.

PSNR 22.74 is moderate rather than strong for a static scene. Treat the
reconstruction as usable but state the metric wherever it is relied on.

## I-4. Vista /home1 is 82.56% full. VERIFIED.

19.2 of 23.3 GB used, 120,737 of 500,000 files. `render_s2/` writes there.
Vista `/work` is at 4.30% of 1024 GB, so `/work` is the correct target for
anything large.

## I-5. A live citation error found mechanically. VERIFIED.

`scripts/check_claims.py` flagged
`.claude/skills/flood-mpm-debugging-reference/SKILL.md:39`, which reads
`topple -> Xia et al. 2013` under the heading "Citation anchors, already
resolved, don't re-derive". Xia is **2014**, four authors including Yejiang
Wang. The same string appears in the stale duplicate at
`vehicle_geometry_research/flood-mpm-debugging-reference_SKILL_v3_friction_corrected.md:39`.

This is the failure mode the register exists to prevent: a wrong value carrying
an explicit instruction not to re-check it.

## I-6. MCP configuration. VERIFIED.

- `hf-mcp-server`, the duplicate unauthenticated entry recommended for removal
  earlier today, is **already absent** from `~/.claude.json` at every scope. No
  action needed; do not re-run the removal.
- `hf` is authenticated as `josiecerrell` and healthy.
- A real conflict remains: **`zotero` is defined in two scopes with different
  endpoints**, user (`zotero-mcp`) and local
  (`/Users/josie/.local/bin/zotero-mcp`). OAuth tokens are stored per endpoint,
  so authenticating one does not carry to the other. This is a plausible
  contributor to the known "Zotero MCP reports connected but every search
  returns empty" behaviour. Resolve by keeping one endpoint.

---

## Tooling added this session

| path | purpose |
|---|---|
| `scripts/tacc_submit.sh` | Submit an sbatch job to Vista/LS6 from the Mac, wait, print the log. Refuses silently to stack on a live interactive job without saying so. Removes the reason `idev` was used for 4-minute runs. |
| `scripts/tacc_idle_check.sh` | Detect interactive allocations whose GPUs are at 0% and 0 MiB with load below 0.5. Reports and prints the `scancel` line; never cancels by itself. |
| `scripts/check_claims.py` | Pattern guard for the 14 refuted claims that have a stable surface form. Defaults to the staged git index so it gates new lines; `--all` audits the archive. |

`check_claims.py --all` currently reports 163 ERROR and 26 WARN across tracked
files, excluding the correction layer. That is real documented debt (forked
densities at `can_it_ford_L2_mpm.py:27` and `can_it_ford_L2_mpm_ytest.py:45`,
the stale 100-300 band in prose), not tool noise. The staged-index default is
the enforceable gate; the full sweep is a worklist.
