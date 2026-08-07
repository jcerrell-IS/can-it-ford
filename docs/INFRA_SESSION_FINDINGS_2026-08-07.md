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

## I-2. RETRACTED 2026-08-07. There IS a working gsplat environment on LS6.

**Retracted by I-10, the drainA disk audit at the end of this file.** This item
originally read "Register K2 is wrong: there is no working gsplat environment on
LS6. VERIFIED." That conclusion is false. The environment is
`/scratch/10386/lsmith9003/python-envs/gsplat_env`, it contains `gsplat` and
`gsplat-1.5.3.dist-info`, and it wrote an 80,612,705-byte PLY on 2026-08-07 at
03:13:28. Two follow-on claims in this item are also wrong: K2's placement of the
environment on **Lustre scratch was correct** (`/scratch/10386` is Lustre), and
K2's 3-to-5-minute wait advice is not "actively harmful", because once the
correct env is sourced there is no `ModuleNotFoundError` to hit.

The four checks below are each individually true. All four looked under
`$SCRATCH` (`/scratch/11603/jcerrell0629`) and `$HOME`, and the environment is
under neither: it belongs to a different project, `/scratch/10386/lsmith9003`.
The `$HOME/my_gsplat_env` check in particular read that venv's `site-packages`
but not its `pyvenv.cfg`, which reads
`home = /scratch/10386/lsmith9003/python-envs/gsplat_env/bin` with
`include-system-site-packages = true`, so it inherits gsplat instead of holding a
copy. Retained so the reasoning error stays legible. **Do not act on the
consequence paragraph.**

### Original text, retained, superseded

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
- `stats/val_step29999.json`: **PSNR 22.7356, SSIM 0.8249, LPIPS 0.3112**, and
  `num_GS: 399491`. **That count is rank 0's shard, not the model.** See below.

**CORRECTION, verified 2026-08-07 after this item was first written.** The three
rank checkpoints are SHARDS holding different numbers of Gaussians, not three
copies of one model. Read without needing torch, by listing the zip members of
each `.pt` and dividing the `opacities` tensor (shape `(N,)`, float32) by 4:

| checkpoint | opacities bytes | N |
|---|---:|---:|
| `ckpt_29999_rank0.pt` | 1,597,964 | 399,491 |
| `ckpt_29999_rank1.pt` | 1,498,708 | 374,677 |
| `ckpt_29999_rank2.pt` | 1,494,104 | 373,526 |
| **total** | | **1,147,694** |

`num_GS` in `val_step29999.json` equals rank 0's shard **exactly**, so the logged
count is rank-local. The reconstruction has about **1.15M Gaussians, not 399k**.
Anywhere the 399,491 figure has been quoted as the model size, including earlier
in this document, it is wrong by roughly 2.9x.

INFERRED, not verified: PSNR/SSIM/LPIPS are rendered-image metrics and gsplat's
distributed rasteriser gathers across ranks, so those three are probably global
and unaffected. That was not confirmed here. Do not quote them as
per-rank or as global without checking which.

Tensor layout of each shard, all float32, decoded from the archive member sizes:
`means (N,3)`, `sh0 (N,1,3)`, `scales (N,3)` (three members of N*12 bytes),
`opacities (N,)`, `quats (N,4)`, `shN (N,15,3)` for `sh_degree: 3`.
A PLY export must concatenate all three ranks; using rank 0 alone silently drops
65% of the scene.
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

## I-5. RETRACTED. The citation was fine; the rule that flagged it was wrong.

**This item originally claimed** that
`.claude/skills/flood-mpm-debugging-reference/SKILL.md:39`, reading
`topple -> Xia et al. 2013`, was a live citation error and that Xia is 2014.
That is wrong and is retracted. See I-8 for the verified position.

The bib deliberately keys both Xia papers by **online-first** year, so
"Xia et al. 2013" for TOPPLE matches `xia2013` exactly and is correct as written.
`scripts/check_claims.py` rule C9, as first authored, asserted "Xia is 2014, not
2013" and would have introduced an error into the bibliography if acted on. The
rule was the defect, not the skill file.

The transferable lesson is the one this file exists to enforce, turned on itself:
a mechanical checker is not a primary source either. C9 was written from a
memory, and the memory was an oversimplification of a two-paper, two-year-each
situation. Checking `paper/can_it_ford_references_IEEE.bib` before acting is what
caught it.

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

## I-7. Two same-shaped bugs: a relative pattern swallowing the whole repo. VERIFIED.

Both found 2026-08-07, both caused by matching a path fragment that the repo's
own name satisfies.

1. **Permission rule.** `.claude/settings.json` denied `Read(can-it-ford/**)` to
   block the nested duplicate directory. The pattern is relative, so whenever the
   shell's working directory drifted to `/Users/josie`, every file under
   `/Users/josie/can-it-ford/` matched it and became unreadable, including
   `scripts/`, `.claude/` and the memory directory. Symptom: "File is covered by a
   Read deny rule" on ordinary project files, intermittently. Fixed by anchoring to
   the absolute path `Read(//Users/josie/can-it-ford/can-it-ford/**)`.

2. **check_claims.py.** Its `EXCLUDE` tuple carried the same `"can-it-ford/"`
   entry and matched against the absolute path, so when the PostToolUse hook
   invoked it per-file it skipped **every** file and silently exited 0. Fixed by
   normalising to a repo-relative path before matching. Caught only because the
   hook returned clean on a file already known to have two hits.

## I-8. Rule C9 was wrong and would have corrupted a citation. VERIFIED.

The first version of C9 asserted "Xia is 2014, not 2013". Checking
`paper/can_it_ford_references_IEEE.bib` before acting showed there are **two**
Xia papers and the bib deliberately keys both by online-first year:

- `xia2010` (:96) "Formula of Incipient Velocity for Flooded Vehicles",
  Natural Hazards 58(1) 1-14, online 2010, **print 2011**, cited for SLIDE.
- `xia2013` (:108) "Criterion of Vehicle Stability in Floodwaters",
  Natural Hazards 70(2) 1619-1630, online 2013, **print 2014**, cited for TOPPLE
  and the DRIFT_THRESHOLD justification.

So both skill-file citations were defensible and the rule, not the text, was the
defect. C9 is now a WARN that explains the ambiguity instead of asserting a year.

**Open, needs a human decision.** `xia2013` currently has `year = {2013}` next to
`volume = {70}, number = {2}, pages = {1619--1630}`, which is the January **2014**
print issue, so the entry is internally inconsistent. `year = {2013}` landed in
`f9bf0f9` on 2026-07-21; a Crossref check on 2026-07-30 concluded 2014 and the bib
was never updated. Either move the year to 2014 (the key can stay `xia2013`) or
drop the volume/issue. Nothing was changed here.

## I-9. Connector and skill prune. VERIFIED.

- `disableClaudeAiConnectors: true` set in **project** settings, which drops the
  38 claude.ai-managed connectors for Can It Ford only. Per the settings schema,
  any-source-true wins and a project may opt out, so claude.ai chat and every
  other project keep them. `claude mcp remove` cannot touch these; it reaches only
  local/user/project scopes, confirmed by attempting it.
- Removed from local scope: `coupler-io` (unrelated SaaS ETL), plus `blender`,
  `overleaf`, `undermind` and `zotero`, which were duplicated at user scope. That
  also clears the "zotero defined in multiple scopes" warning. Both zotero
  endpoints resolved to the same binary through a symlink, so nothing was lost.
- 91 skills set to `off`, including 11 `anthropic-skills:` copies that duplicate
  the version-controlled skills in `.claude/skills/`. Duplicated skills can drift,
  and the git-tracked copy is the one CLAUDE.md cites.
- Backups: `~/.claude/_backup_2026-08-07/`.

**Correction, same session.** Treating the local-scope entries as duplicates was
wrong for three of the five, and removing them was a regression. They were not
duplicates: they carried project configuration the user-scope entries do not have.

| server | local entry carried | user-scope entry |
|---|---|---|
| `undermind` | `oauth.clientId: claude-code` | bare URL, so auth fails with "does not support dynamic client registration" |
| `overleaf` | `OVERLEAF_PROJECT_ID` (Can It Ford), `OVERLEAF_PROJECT_NAME`, `OVERLEAF_GIT_TOKEN_FILE` | bare `npx`, no project binding |
| `zotero` | `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE` | bare `zotero-mcp`, no credentials |

All three were restored byte-for-byte from the backup. Only `blender` was a true
duplicate (identical `uvx blender-mcp`, no env or oauth) and stays removed, along
with `coupler-io`. `undermind` now reports "Needs authentication" rather than
connected, because the remove/add cycle cleared its stored OAuth token; it needs
one interactive `/mcp` re-auth.

This also sharpens the known Zotero trap: the **user-scope** zotero entry has no
`ZOTERO_API_KEY` at all, so in any project other than Can It Ford it connects and
returns empty rather than erroring. The credentials live only in the local entry.

`check_claims.py --all` currently reports 157 ERROR and 89 WARN across tracked
files, excluding the correction layer. That is real documented debt (forked
densities at `can_it_ford_L2_mpm.py:27` and `can_it_ford_L2_mpm_ytest.py:45`,
the stale 100-300 band in prose), not tool noise. The staged-index default is
the enforceable gate; the full sweep is a worklist.

---

## APPENDED BY A DIFFERENT CLAUDE CODE SESSION, 2026-08-07 ~10:20 BST

This section was not written by the session that wrote everything above it. A second
Claude Code session was running concurrently in this same working tree, on the
failure-mode classifier task. Neither session was told the other existed.

**Read `docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md`.** It records what overlapped,
which files each session owns, and the proposed sequencing.

Three items bear directly on the work above:

1. **C6's message was factually wrong.** It stated that 9.80665 "appears only at
   `failure_modes.py:14`". It also appears at `analysis/viability_dashboard_scaffold.py:11`.
   Two sites. Corrected in `check_claims.py`, and the full inventory is now register A6.
2. **`6514bfc`'s withdrawal of CLAUDE.md item 15 dropped a still-true fact.** The
   "gravity is UNKNOWN" half was correctly withdrawn. The post-processing 9.81 vs
   9.80665 fork was not stale, and the withdrawal note pointed at register A2 for it
   when A2 did not contain it. Register A6 closes that dangling pointer.
3. **Commits `0797b08` and `3470ff9` contain the other session's uncommitted edits**
   (`CLAUDE.md` item 12; `Rule.exclude`, C10b and C10c in `check_claims.py`). They are
   correct and were verified, but they are not described by those commit messages.

The `--all` sweep figure quoted above (157 ERROR / 89 WARN) predates several rule fixes
made by the other session: `Rule.exclude` was added and C10b, C10c and C14 were narrowed
after false positives fired on text that states the correction rather than the claim.
Re-run before treating that count as a worklist baseline.

---

## I-10. drainA disk audit, 2026-08-07 continued (session 3)

Written by a third Claude Code session, later the same day. Every figure below
came from a live command against LS6 through `scripts/tacc.sh`, run with the
explicit instruction to trust neither this file nor the register on drainA. It
**retracts I-2 above** and corrects two details in I-3.

Only this file was edited. `CLAUDE.md` and
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` both carried another
session's uncommitted edits at the time (+46 and +49 lines), so per the standing
rule and the 2026-08-07 breach they were left untouched. **Register K2 and K4
still need merging by hand once that session is parked.**

### I-10a. Every PLY on disk, whole gsplat tree

`/scratch/11603/jcerrell0629/gsplat` exists on **LS6 only**. The same path on
Vista returns `No such file or directory`, so LS6 is the sole host.

| run dir | file | exact bytes | exact mtime (CDT, -0500) |
|---|---|---:|---|
| `results/garden` | `ply/point_cloud_99.ply` | 38,491,425 | 2026-07-23 19:33:49 |
| `results/garden` | `ply/point_cloud_2999.ply` | 80,612,705 | 2026-08-07 03:13:28 |
| `results/custom_data` | `ply/point_cloud_2999.ply` | 115,048,881 | 2026-06-08 20:31:13 |
| `results/drainA` | `ply/point_cloud_2999.ply` | 81,472,689 | 2026-07-17 06:18:21 |
| `results/drain_2956` | `ply/point_cloud_2999.ply` | 159,643,205 | 2026-07-20 08:39:36 |
| `results/drain_2957` | `ply/point_cloud_2999.ply` | 155,004,861 | 2026-07-20 09:59:31 |

`ctime` equals `mtime` on all six. **drainA holds exactly one PLY, the July 17
3k-step file.** There is no drainA PLY at step 6999 or 29999. This confirms I-3's
`save_ply: false` consequence by direct inventory rather than by inference.

### I-10b. The drainA cfg.yml postdates its own PLY by three days

`results/drainA/cfg.yml` (`max_steps: 30000`, `save_ply: false`) has mtime
**2026-07-20 19:29:38**. The PLY it sits beside was written **2026-07-17
06:18:21**. The config on disk is therefore *not* the config that produced the
PLY; the 3k-step config that did produce it was overwritten by the 30k run and no
longer exists. Do not read `results/drainA/cfg.yml` as a description of how the
surviving PLY was made.

`val_step` inventory, for the record: drainA 2999 `num_GS` 345,217 (psnr
21.5030), 6999 `num_GS` 297,756 (psnr 22.5470), 29999 `num_GS` 399,491 (psnr
22.735628128051758). Others: garden 99 `num_GS` 163,093, custom_data 2999
`num_GS` 487,489, drain_2956 2999 `num_GS` 676,452, drain_2957 2999 `num_GS`
656,798.

### I-10c. `results/garden` is NOT the stock MipNeRF-360 demo scene

`results/garden/cfg.yml` reads **`data_dir: /scratch/11603/jcerrell0629/drainA`**.
It is Josie's own drainA capture. The directory name is only the stock default
`result_dir: results/garden` left unedited, which makes the label misleading, but
no bundled example data is involved.

It was written 2026-08-07 between 03:10:38 and 03:13:28. No `val_step2999.json`
exists for it because `eval_steps: [7000, 30000]` never fires against
`max_steps: 3000`; the ckpt and PLY still appear at 2999 because
`simple_trainer.py:783` writes at `max_steps - 1` regardless. Self-consistent, not
an anomaly.

**The job running at audit time did not write it.** `scontrol show job idv04063`
fails because `idv04063` is the job *name*: the id is **3347772**, started
`2026-08-07T04:04:27` on `c301-001`, `gpu-a100-dev`, 2h limit. That is **51
minutes after** the garden artifacts were written, and `find -newer` on the
garden PLY returns nothing anywhere in the gsplat tree, so it has produced no
files there. It was not touched.

The actual writer was job **3347538**, name `idv59394`, node **c301-004**,
01:39:25 to 03:39:26, ended **TIMEOUT** at the 2h wall. Its tensorboard event
files are stamped `c301-004` at 01:42:54, 01:47:53 and 03:10:38; the last sits 16
seconds before `cfg.yml`, and the run finished at 03:13:28, 26 minutes before the
job timed out. Three launches in one idev session, the third survived. This is
another instance of the I-1 pattern.

### I-10d. The environment claim: I-2 is fully contradicted, not partially

The working environment is **`/scratch/10386/lsmith9003/python-envs/gsplat_env`**,
containing `gsplat` and `gsplat-1.5.3.dist-info`. It belongs to a different
project (10386, user `lsmith9003`), which is why every `$SCRATCH`-relative check
missed it. `~/my_gsplat_env/pyvenv.cfg` reads
`home = /scratch/10386/lsmith9003/python-envs/gsplat_env/bin`, python 3.10.13,
`include-system-site-packages = true`, so it inherits gsplat rather than holding
its own. `$HOME/.bash_history` shows the working line used repeatedly:

    source /scratch/10386/lsmith9003/python-envs/gsplat_env/bin/activate

The disproof is physical, not inferential: an 80,612,705-byte PLY and an
80,613,912-byte checkpoint were written this morning. That cannot happen from a
`ModuleNotFoundError`. **This is a full contradiction of I-2 and must not be
recorded as a partial one.** Note the dependency risk this exposes: the
environment sits in another user's scratch and is subject to that project's purge
schedule, not ours.

### I-10e. 341,573 Gaussians has no source anywhere checked

Two searches, both negative. (1) Every `.ply` on LS6: the six above, plus eight
outside the results tree that are Yaris meshes and `taichi_mpm` point clouds, no
splats among them. (2) Hugging Face for the authenticated account `josiecerrell`:
`hf repos ls` returns only `josiecerrell/can-it-ford-sweep-v1` as dataset and
model, updated 2026-07-14, **0 B storage**, so nothing is uploaded.

**No drainA artifact anywhere on disk matches 341,573 Gaussians, and no drainA
artifact anywhere on disk carries a completion date after 2026-07-20.**

341,573 has no known source and should be treated as unsourced until one is
produced. The real neighbouring figures are 345,217 (the July 17 PLY), 399,491
(rank 0's shard) and 1,147,694 (the three-rank total).

### I-10f. Two corrections to I-3 in this same file

1. **I-3's closing line is internally inconsistent.** It says "the fix is to
   re-export from `ckpt_29999_rank0.pt`", naming one rank, while I-3's own
   correction table twelve lines earlier states that rank 0 alone "silently drops
   65% of the scene". Any re-export must concatenate all three ranks. The
   singular filename in that sentence should not be followed.
2. **I-3 records `data_dir: .../datasets/drainA/` for the 30k run, which is
   right, and is now a different path from the current one.** See below.

### I-10g. The drainA dataset was copied to a second path this morning

`/scratch/11603/jcerrell0629/drainA` (`colmap_A.pid`, `colmap_run.log`,
`database.db`, `images/` with 279 files, `sparse/`, and a `.DS_Store`) all carry
mtimes of 2026-08-07 01:47 to 01:52. The July copy at
`/scratch/11603/jcerrell0629/datasets/drainA` is **still intact** (2026-07-16
15:49) with **identical byte sizes**: `colmap_run.log` 233,912 and `database.db`
436,924,416 in both.

`colmap_run.log`'s internal timestamps are 2026-07-10 06:24:04 to 07:12:23
("Elapsed time: 9.951 [minutes]"), with macOS-style thread ids, and a `.DS_Store`
sits beside it. So COLMAP ran **on the Mac on 2026-07-10** and both LS6 copies are
uploads of that one reconstruction. This morning's is a re-upload to a new path,
not a new reconstruction. July training used
`--data_dir $SCRATCH/datasets/drainA/`; this morning's used the new
`/scratch/11603/jcerrell0629/drainA`. Two paths, one dataset, 0.44 GB duplicated.

### I-10h. Bridge-test guidance

**No `docs/BRIDGE_FIRST_REAL_DATA_TEST_*.md` exists.** Confirmed four ways: a
home-wide `find` across `/Users/josie`, `git log --all --diff-filter=A` for the
filename on every branch (never added, so not deleted either), LS6
`$SCRATCH`/`$WORK`/`$HOME`, and Vista `$WORK`/`$HOME`. Nothing in `bridge/`
hardcodes a PLY path; `bridge/gaussian_io.py:89-90` only checks the argument ends
in `.ply`.

If that test runs, **the only drainA PLY available is the 2026-07-17 file at
345,217 Gaussians**, which is a 3,000-step model. A higher-quality test needs a
PLY re-exported from the three `ckpt_29999_rank*.pt` shards, which does **not**
require a retrain.

The export path only half exists today, so do not quote a ready invocation:

- `examples/simple_trainer.py:1169-1177` already concatenates ranks:
  `--ckpt` takes a list and does `torch.cat([ckpt["splats"][k] for ckpt in ckpts])`.
- `gsplat/exporter.py:475` provides
  `export_splats(means, scales, quats, opacities, sh0, shN, format="ply", save_to=...)`,
  imported at `simple_trainer.py:33`.
- **But `:1169` is commented `# run eval only`** and calls only `runner.eval()` and
  `runner.render_traj()`. The PLY write lives at `:783-806`, inside the training
  loop, gated on `cfg.save_ply`. So `--ckpt` alone will **not** emit a PLY.

Closing that gap needs a short standalone script that loads the three shards,
concatenates them, and calls `export_splats` once. Roughly ten lines, no GPU
training, but it does not exist yet and was deliberately not written or run in
this pass.
