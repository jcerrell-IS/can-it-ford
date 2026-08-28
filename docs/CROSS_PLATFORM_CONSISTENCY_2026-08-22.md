# Cross-platform consistency: GitHub, HuggingFace, W&B, DesignSafe

Checked 2026-08-22, 03:0x-03:2x BST, from `Josephines-MacBook-Air.local`,
`/Users/josie/can-it-ford`, branch `claude/add-ci-checks`, HEAD `e9e80ad`, main
checkout (`.git` is a real directory, not a worktree file).

**This is a read-and-report pass. Nothing in `README.md` was edited.** The one
required change is supplied as `docs/README_hf_space_live_2026-08-22.patch`,
verified with `git apply --check` (dry run, applies nothing) and reported
`PATCH APPLIES CLEANLY`.

Every `README.md` cross-platform claim was treated as a citation to verify.
Claims below are tagged `[read live]` where I ran the command and read the
output this session, and `[inferred]` where I reasoned from those reads.

**Concurrent session warning.** A second Claude Code session was editing
`hf_space/**` while this pass ran (11 files touched within 10 minutes of start,
per the session live-state hook) `[read live]`. I read those files and never
wrote to them. Anything I say about the deployed Space is timestamped, because
that session may push at any moment.

---

## Verdict summary

| # | Claim | Verdict |
|---|---|---|
| 1 | W&B badge path, owner/org, run count | **VERIFIED-CURRENT** |
| 2 | `l2_results_from_wandb.csv`, 9 conditions, agree 5 of 9 | **VERIFIED-CURRENT**, and not undercounting |
| 3 | "Gradio demo: not yet deployed" | **FOUND-STALE**, stale for 5 days. Patch supplied |
| 4 | Corpus merge vs Citations section | **NO CHANGE**, stated explicitly below |
| 5 | DesignSafe "staged, not yet published" | **VERIFIED-CURRENT** |

> **SUPERSEDED IN TWO PLACES BY THE SECOND PASS AT THE END OF THIS FILE
> (2026-08-22 ~03:35 BST).** Row 3's patch **has since been applied** to the
> working tree, so do not apply it again, and the "Nothing was applied" line in
> the Limits section is no longer true. A sixth finding this pass missed, a
> **stale dataset licence in `README.md`**, is recorded there with its own patch.
> Rows 1, 2, 4 and 5 were independently re-verified and all four reproduce.

One finding outside the five, inside the task's framing: the HuggingFace Space
page understates its own shipped dataset by 20 records. Section 6. It is not a
`README.md` defect and I propose no patch for it, because the file is another
session's live work.

---

## 1. W&B project, owner/org, and run count: VERIFIED-CURRENT

`README.md:6` badge and `README.md:173` both point at
`wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford`.

Measured live `[read live]`:

- `curl -L` on that exact URL, **unauthenticated**, returns `http_code=200` with
  no redirect. A public reader clicking the badge lands on a page, not a login
  wall.
- `scripts/wb --doctor`: authenticates `YES as jcerrell29`,
  `entity/project : jcerrell29-claremont-mckenna-college/can-it-ford`,
  `run count : 108`, `doctor: all checks passed`.
- `analysis/wb.py doctor` (the read-only command; `snapshot` was **not** run, see
  the limits section): `runs : 108`, 99 with tags, 19 with group, 20 with
  job_type, 4 dataset artifact collections.
- Ownership: `api.viewer.username` is `jcerrell29` and
  `api.viewer.teams` is `['jcerrell29-claremont-mckenna-college']`. That entity
  holds exactly **one** project, `can-it-ford`. So the badge names a team the
  account belongs to, not a personal namespace, and the path is exact.

**The run count claim.** `README.md` itself states no run count anywhere, so the
badge cannot go stale on that axis: it is a static shields.io label reading
"experiment tracking", not a live counter `[read live]`. The nearest doc claim,
`docs/PLATFORM_LEVERAGE_STATUS_2026-08-22.md:227`, reads
"**108 runs**, 2 reports, 0 sweeps, 4 dataset artifact collections" and
**matches the live read exactly on both the run count and the artifact
collections** `[read live]`.

Older figures exist and are dated, so they are stale rather than wrong:
106 at `docs/SECOND_EYES_AUDIT_2026-08-20_1200.md:287`, 107 at
`docs/MCP_CONNECTOR_AUDIT_2026-08-20.md:133`, 106 at
`docs/R9_SESSION_HANDOFF_2026-08-20.md:1309`,
`docs/MERGED_RESEARCH_READER_CORPUS_2026-08-20.md:322` and
`docs/R10_HANDOFF_2026-08-20_1215.md:199`. All five carry their own date. None is
reader-facing and none needs a patch.

Scope of that grep: `README.md`, `docs/`, `citations/`, via `/usr/bin/grep -rn`,
excluding `docs/session_notes/archive`. It did not cover `.claude/worktrees/`,
`archive/` or `third_party/`.

---

## 2. `data/l2_results_from_wandb.csv`: VERIFIED-CURRENT, and it is NOT undercounting

`README.md:142` claims: "Confirmed L2 runs pulled from the W&B API. Backs the
pilot study: 9 unique conditions, L1 and L2 agree at 5 of 9".

**The file still supports that claim exactly** `[read live]`. Read in full,
9 data rows, 9 distinct `(depth_m, velocity_ms)` pairs, no duplicates:

| depth_m | velocity_ms | l1_verdict | l2_verdict | agree? |
|---|---|---|---|---|
| 0.15 | 0.0 | FORD | FORD | agree |
| 0.30 | 0.0 | FORD | FORD | agree |
| 0.60 | 0.0 | FORD | FORD | agree |
| 0.45 | 1.5 | NO-FORD | NO-FORD | agree |
| 0.60 | 1.5 | NO-FORD | NO-FORD | agree |
| 0.15 | 1.5 | FORD | NO-FORD | diverge |
| 0.30 | 1.0 | FORD | NO-FORD | diverge |
| 0.30 | 1.5 | FORD | NO-FORD | diverge |
| 0.30 | 2.0 | FORD | NO-FORD | diverge |

5 agree, 4 diverge, total 9. The file's own `divergence` column is `False` on
exactly the 5 and `True` on exactly the 4, so the count is internally
corroborated by a second column rather than only by my arithmetic `[read live]`.

The file has been committed once and never modified: `git log` returns the single
commit `43a82b0 Pull confirmed L2 run data from W&B API`, and it is tracked
(`git ls-files --error-unmatch` succeeds) `[read live]`.

### The dispatch's hypothesis was that this now undercounts. It does not, and here is why

Prompt 2's job **did finish**. Confirmed live against W&B, not against the doc
that claims it `[read live]`: group `gated-17` holds exactly **17 runs**,
job_type `gated-backfill`, and the grid study is present as tags `n_grid_48` (3),
`n_grid_64` (11), `n_grid_96` (3), summing to 17.
`docs/PLATFORM_LEVERAGE_STATUS_2026-08-22.md:241` says "17 gated runs and the
grid study confirmed logged", and that reproduces.

**So more data was logged. It still cannot raise this number, for two independent
reasons.**

First, the newly logged runs carry **no agreement pair**. Dumping the full
summary and config of `g64_m1100` and `sweepV_g64_v2p0` `[read live]`: they hold
`failure_mode`, `triggered_slide/float/topple`, `peak_ratio_*`,
`passthrough_max_frac`, `final_disp_mag_m`, `onset_frame_slide` and
`l1_verdict_joint_rule`. They hold **no `l2_verdict` and no `divergence` field**.
An agreement rate needs both halves of the pair. It is not computable over these
17 from what is logged. Any "17 of 17 agree" would require inventing an L2
verdict from `failure_mode`, which is a modelling choice, not a retrieved value
`[inferred]`.

Second, they are a **different scenario on a different engine**. The 9 pilot runs
are Genesis SPH, tagged `Genesis-MPM,L2,Vista`, created 2026-07-01, spanning 9
distinct depth and velocity conditions. The 17 are warpmpm
(`config.engine = "warpmpm"`, driver `renders/yaris_render_s1/sim_standing.py`),
created 2026-08-17, all at one fixed `realized_depth_m` of 0.2944294473039918
`[read live]`. Pooling them into one agreement rate would merge two engines and
two scenarios into a single number, which is the exact conflation the project
constitution forbids under its August 4 audit item 1.

**Verdict: the sentence is accurate, reproducible, and should not be changed.**

### One real hazard found here, worth knowing even though it needs no README edit

The `L2` **tag is now overloaded**. Live, 26 runs carry tag `L2`: the 9 Genesis
SPH pilot runs **and** all 17 warpmpm gated runs `[read live]`. So the README's
phrase "pulled from the W&B API" is no longer reproducible by tag alone. Anyone
re-running that pull filtering on `tags contains L2` today gets 26 rows across
two engines, not 9. Reproducing the 9 now requires filtering on the
`Genesis-MPM` tag, or on the `L2_d*_v*` name pattern, or on the July 1 date.

This is a W&B metadata issue, not a README error, so I propose no required
change. An optional one-clause clarification is in section 7 and Josie can
ignore it.

---

## 3. "Gradio demo: not yet deployed": FOUND-STALE. Patch supplied

**A Space exists, is public, and is running.** Measured against the HF API, not
the README `[read live]`, at 2026-08-22 ~03:1x BST:

```
id        : josiecerrell/can-it-ford
author    : josiecerrell
sdk       : gradio          sdk_version 6.24.0
private   : False           disabled : False
stage     : RUNNING         hardware : cpu-basic
createdAt : 2026-08-17T21:09:46.000Z
lastMod   : 2026-08-21T01:13:06.000Z
sha       : 3e27deb406a1dbbc8ccfcb0b9f25b97b55a5f2b2
license   : bsd-3-clause    (cardData.license, read directly, not from tags)
```

`stage: RUNNING` is the platform's own claim, so I tested it independently
rather than trusting it: `curl` on `https://josiecerrell-can-it-ford.hf.space/`
returns `http_code=200`, 15000 bytes, in 0.53 s, and the body carries
`<title>Can It Ford</title>` and two `gradio-app` markers `[read live]`. It
serves.

**It is a substantive demo, not a stub.** Its own README lists three live panels
`[read live]`: verdict-flip against a movable drift threshold over the 17 gated
runs; the `v_car` x `v_water` load surface at 20 cells by five seeds; and repeat
spread over 3 configurations. It also carries an explicit corrections section
recording that an earlier version of the page wrongly said "Genesis MPM" and
wrongly quoted rho = 115.7 and 1390 kg, both now corrected to warpmpm, 1100 kg
and 310.494 kg/m^3, which matches this project's canonical values.

### Why the line is stale, precisely

The line was written by commit `a078626`, "README: remove claims for assets that
are not live", dated **2026-08-02 17:52:34 +0100** `[read live]`. That commit
**removed** a badge and a link pointing at exactly
`https://huggingface.co/spaces/josiecerrell/can-it-ford`, and replaced the bullet
with "not yet deployed."

**That edit was correct when it was made.** The Space's `createdAt` is
2026-08-17T21:09:46Z, fifteen days later. On 2026-08-02 there genuinely was no
Space. The defect is that the Space was then created on 2026-08-17 and nobody
restored the line. **The README has understated a live public asset for 5 days**
`[inferred, from the two timestamps]`.

The patch restores the badge `a078626` removed and rewrites the bullet. It does
**not** restore the DesignSafe badge that the same commit removed, because
section 5 confirms that one is still correctly absent.

---

## 4. Corpus merge vs the Citations section: NO CHANGE. Stated explicitly

`docs/CORPUS_MERGE_FINAL_2026-08-22.md` exists (65030 bytes, mtime 2026-08-22
02:48), so Prompt 6 finished `[read live]`.

Its two priority DOIs, from its section 2 `[read live]`:

1. `10.1007/s00466-019-01783-3`, Gonzalez Acosta, Vardon, Remmerswaal and Hicks,
   "An investigation of stress inaccuracies and proposed solution in the material
   point method", Computational Mechanics 65(2) 555-581.
2. `10.1016/j.jcp.2016.10.064`, Zhang, Zhang, Sze, Lian and Liu, "Incompressible
   material point method for free surface flow", J. Comput. Phys. 330:92-110.

**Neither changes anything in `README.md`'s Citations section, and neither is
cited there.** Three separate checks, all negative:

- **Direct.** Grepped `docs/CORPUS_MERGE_FINAL_2026-08-22.md` for every DOI and
  author the Citations section names: `jfr3.12527`, `2023WR036739`,
  `s11069-013-0889-2`, `matecconf/201820307003`, `1999-01-1336`, `Smith, Modra`,
  `Xiong`, `Shand`. Two hits, both false positives on inspection `[read live]`.
  Line 203 matches "Xiong" only inside the author name **Xiong Zhang**, a
  co-author of the JCP paper, which is a different person from the Xiong et al.
  (2024) WRR paper the README cites. Line 507 is a bibliography-audit row noting
  the cite key `xiong2024` is never cited in the tex, which is a pre-existing
  fact already recorded in the project constitution, not a new finding.
- **By subject.** The two papers are about MPM cell crossing, nodal force sign
  error, stress oscillation, weakly compressible EOS, artificial sound speed and
  GIMP. Grepping `README.md` for `converg|refine|grid|cell.cross|sound speed|
  oscillat|GIMP|stress` returns exactly two lines, both directory or dataset
  descriptions ("Experiment CSVs", "Theoretical L0/L1 grid") `[read live]`. The
  README makes **no** numerical-method or convergence claim for either paper to
  touch.
- **By the merge doc's own prescription.** The only change it asks for is at its
  line 269: soften one inferential sentence in
  `docs/COUPLING_VALIDATION_J1_2026-08-07.md`, because divergence under
  refinement is now documented as also the signature of an unfixed cell-crossing
  and quadrature error, not uniquely of a wrong term. The doc states directly of
  the J.1 verdict: "Nothing in either paper touches any of that, and none of it
  changes." That file is internal and is not referenced by `README.md` `[read live]`.

Two adjacent items from the same doc, checked and also not README-affecting: the
one actionable erratum it found is on `10.1016/j.joes.2018.05.002`, which the
README does not cite; and its open item 11 notes the paper's own 15-entry
bibliography has never had a retraction check, which concerns `paper/`, not
`README.md` `[read live]`.

**Explicit answer to the question asked: the corpus merge changes nothing in
README.md's Citations section, and no edit to it is warranted.**

---

## 5. DesignSafe "staged, not yet published": VERIFIED-CURRENT

`README.md:176` and `README.md:165` both say PRJ-6388 is staged, with no DOI
minted.

`https://www.designsafe-ci.org/api/publications/v2/PRJ-6388` returns
`http_code=404`, body `{"message": "Publication not found."}` `[read live]`.

**A 404 is only evidence if the endpoint answers for things that do exist**, so I
ran a control rather than reporting the bare 404 `[read live]`:

| project | http_code | payload |
|---|---|---|
| PRJ-6388 (ours) | 404 | `Publication not found.` |
| PRJ-1892 (control) | **200** | 10085 bytes |
| PRJ-3213 (control) | **200** | 29592 bytes |
| PRJ-2740 (control) | 404 | `Publication not found.` |

Two controls return real payloads from the same endpoint, so the endpoint
discriminates published from unpublished and PRJ-6388's 404 is meaningful, not an
endpoint failure.

**One honest limit on this verdict.** The 404 proves there is **no published
record**, which is the half of the sentence that could have gone stale. It does
**not** prove a project numbered PRJ-6388 exists in the private Data Depot
workspace, because that needs an authenticated call I did not make. So
"not yet published" is verified; "staged" is **unverified from outside** and
rests on the project's own prior record `[inferred]`. It is not contradicted by
anything I read.

Consistent with this, commit `a078626` also removed a `DesignSafe-PRJ--6388`
badge on 2026-08-02, and unlike the HuggingFace badge that removal is still
correct. The supplied patch deliberately does not restore it.

---

## 6. Outside the five, inside the brief: the HF Space understates its own dataset by 20

The task asked whether GitHub, HuggingFace and W&B are consistent with each
other, so this belongs in the report even though it is not one of the five items.

The Space's page claims its load-surface panel is "live, **348 records**, 20
cells at five seeds". Three independent measurements say **368** `[read live]`:

- `hf_space/data/load_surface_manifest.json` states
  `force_magnitude_consistency.rows_checked: 368`.
- The CSV **deployed on HuggingFace**,
  `spaces/josiecerrell/can-it-ford/raw/main/data/load_surface.csv`, is 369 lines,
  so 368 records plus a header.
- The local `hf_space/data/load_surface.csv` is also 369 lines.

The linked dataset `josiecerrell/can-it-ford-speed-surface` was published as 368
records per `docs/handoffs/R9_BOARD_SNAPSHOT_2026-08-19.md:214`, and
`docs/R9_MOVING_VEHICLE_2026-08-19.md:1047` also says 368. The 348 traces to
`docs/R9_CROSS_SESSION_READOUT_2026-08-19.md:201`, "d18-platform ingested the
same 348 records into the Space and recomputed". The gap is exactly 20, which is
also exactly the cell count in the same sentence, so a transcription slip is the
likely mechanism `[inferred, not confirmed]`.

Both the deployed Space README and the local `hf_space/README.md` say 348, so
this is live to a reader right now.

**No patch proposed.** `hf_space/README.md` is in another session's active
working set as of this pass, and it is outside the file this dispatch scoped me
to. Flagging only. Whoever owns `hf_space/` should decide, and should check
whether the app's own displayed count agrees with its CSV.

---

## 7. The patch

Required change, one file, two hunks:
`docs/README_hf_space_live_2026-08-22.patch`.

Verified with a dry run that changes nothing:

```bash
git -C /Users/josie/can-it-ford apply --check --verbose docs/README_hf_space_live_2026-08-22.patch
```

reported `Checking patch README.md...` and applied cleanly. To apply:

```bash
git -C /Users/josie/can-it-ford apply docs/README_hf_space_live_2026-08-22.patch
```

Hunk 1 restores, at `README.md:6`, the badge that `a078626` removed, byte for
byte as it was before that commit:

```
[![HuggingFace](https://img.shields.io/badge/HuggingFace-live_demo-blue)](https://huggingface.co/spaces/josiecerrell/can-it-ford)
```

Hunk 2 replaces `README.md:174`:

```
- - **Gradio demo:** not yet deployed.
+ - **Gradio demo:** [josiecerrell/can-it-ford on HuggingFace Spaces](https://huggingface.co/spaces/josiecerrell/can-it-ford), live (verdict-flip explorer over the 17 gated runs, the `v_car` x `v_water` load surface, and repeat spread)
```

### Optional, NOT required, and NOT in the patch file

Section 2 found that the `L2` tag now returns 26 runs across two engines, so
"pulled from the W&B API" is no longer reproducible by tag alone. The README
sentence remains **true as written**, so this is a clarification and not a fix.
If Josie wants it, `README.md:142` would become:

```
| `data/l2_results_from_wandb.csv` | Confirmed L2 runs pulled from the W&B API, the 9 Genesis SPH pilot runs tagged `Genesis-MPM` (the `L2` tag alone now also returns the 17 warpmpm gated runs). Backs the pilot study: 9 unique conditions, L1 and L2 agree at 5 of 9 |
```

I have deliberately left this out of the patch file so that applying the patch
makes only the change that was actually found stale.

---

## Limits of this pass, stated so nothing here is over-read

- **Nothing was applied.** `README.md` is unmodified. The only files this pass
  created are this document and the `.patch`.
- **`analysis/wb.py snapshot` was NOT run.** Reading its source shows
  `cmd_snapshot` opens a W&B run and uploads every canonical store as an
  artifact, so it is a **write**. On a read-and-report task that would have added
  a 109th run and mutated the thing being measured. I used the read-only
  `doctor` command instead, which reports the same run count. If the dispatch
  literally wanted `snapshot` executed, that is a deliberate decision for Josie,
  not something to do silently.
- **The HF Space is a moving target.** Another session was editing `hf_space/**`
  during this pass. Every Space figure above is stamped to the deployed revision
  `3e27deb406a1dbbc8ccfcb0b9f25b97b55a5f2b2`, lastModified 2026-08-21T01:13:06Z.
  Re-read before quoting.
- **"Staged" is unverified**, see section 5. Only "not yet published" is proven.
- **Grep scope.** Doc searches used `/usr/bin/grep -rn` over `README.md`, `docs/`
  and `citations/`, per the project rule that the shell `grep` skips gitignored
  paths. They did **not** cover `.claude/worktrees/`, `archive/` or
  `third_party/`. A run count or a stale claim living only in a worktree would
  not have been seen.
- **Not independently reviewed.** The `physics-skeptic` and Agent paths were not
  used, because the dispatch is a platform-state audit and the standing rule is
  not to launch agents unrequested. No claim here is adversarially reviewed. All
  of them are single-command reproducible, and every command is named above.

---
---

# SECOND PASS, independent re-verification, 2026-08-22 ~03:24 to ~03:40 BST

Run from `Josephines-MacBook-Air.local`, `/Users/josie/can-it-ford`, main checkout,
branch `claude/add-ci-checks`, HEAD `e9e80ad`. Everything below was measured live
this pass. Nothing was carried over from the first pass on its own authority: the
project rule is that a written summary is not current fact, and this file is a
written summary, including the half of it written 20 minutes earlier.

**Why a second pass exists.** The first pass ended by stating "Nothing was
applied. `README.md` is unmodified." That was true when written and is now false.
`README.md` was modified at **03:20:15** and carries the first pass's patch,
uncommitted. So the document's own subject moved underneath it, which is exactly
the failure mode the first pass warned about for the HuggingFace Space.

## What changed since the first pass, and what that means

| | First pass said | Live now | Consequence |
|---|---|---|---|
| Item 3 patch | "supplied, not applied" | **applied**, uncommitted, `README.md` mtime 03:20:15 | Do **not** apply it again |
| Limits section | "Nothing was applied" | false | Corrected by the banner above |
| Dataset licence | not examined | **stale in `README.md`** | New patch, below |

`README.md` working-tree blob is `7501b97`, md5 `4f4c094d0fe786f94850c1c5ff328529`,
and it is **unchanged by this pass** (re-measured after the patch dry run) `[read live]`.

## Re-verification of the five, all four testable ones reproduce

**1. W&B: VERIFIED-CURRENT, reproduced.** `curl -sL` on the badge target returns
`http_code=200` with `url_effective` identical to the requested URL, so no redirect
and no login wall `[read live]`. `analysis/wb.py doctor` live: `viewer jcerrell29`,
`target jcerrell29-claremont-mckenna-college/can-it-ford`, `runs 108`,
`artifact type dataset: 4 collection(s)` `[read live]`. `api.viewer.teams` returns
`['jcerrell29-claremont-mckenna-college']`, so the badge names a team the account
belongs to, not a personal namespace `[read live]`.

Run-count claims across `README.md`, `docs/` and `citations/`, via `/usr/bin/grep`
excluding `session_notes/archive`: `docs/PLATFORM_LEVERAGE_STATUS_2026-08-22.md:227`
says **108** and `docs/CLUSTER_STATE_AUDIT_2026-08-22.md:475` says **108**, both
matching live exactly, including the 4 dataset collections. Older dated figures
(106, 107) sit in 2026-08-20 documents and are stale rather than wrong `[read live]`.
`README.md` itself states **no** run count, so the badge cannot go stale on that axis.

**On the dispatch's literal wording, "what `analysis/wb.py`'s snapshot actually
returns".** I did not run `snapshot`, and this is a deliberate refusal, not an
omission. Reading `analysis/wb.py:302-327` directly: `cmd_snapshot` opens
`with run(job_type="snapshot", ...)` and calls `put_artifact` in a loop, so it
**creates a 109th run and uploads artifacts** `[read live]`. On a read-and-report
task that mutates the quantity being measured. It also prints
`"WARNING: working tree is DIRTY. This snapshot is not reproducible from the
recorded sha alone."` when the tree is dirty, and the tree **is** dirty right now
(19 tracked files uncommitted), so a snapshot taken now would be non-reproducible
by its own standard `[read live]`. The read-only command reporting the same run
count is `doctor`, used above. If Josie wants an actual snapshot run, that is a
decision to take deliberately, on a clean tree.

**2. `l2_results_from_wandb.csv`: VERIFIED-CURRENT, and confirmed not undercounting.**
Re-read the file in full and recounted from scratch, without reference to the first
pass's table: 9 data rows, 9 distinct `(depth_m, velocity_ms)` pairs, `l1_verdict`
and `l2_verdict` equal on 5 and unequal on 4 `[read live]`. The file's own
`divergence` column is `False` on exactly those 5 and `True` on exactly those 4, so
a second column in the file corroborates the arithmetic `[read live]`.

The dispatch's hypothesis was that this now undercounts. **Prompt 2's job did
finish**, confirmed against W&B rather than against a doc claiming it: group
`gated-17` holds exactly **17** runs, `job_type` `gated-backfill`, and the grid
study is present as tags `n_grid_48` 3, `n_grid_64` 11, `n_grid_96` 3, summing to
17 `[read live]`.

**It still cannot raise the number, and I verified the reason directly rather than
accepting it.** Dumping summary keys live: a `gated-17` run
(`g48_m1100`, `config.engine = "warpmpm"`, driver
`renders/yaris_render_s1/sim_standing.py`, created 2026-08-17) carries
`failure_mode`, `final_disp_mag_m`, `l1_verdict_joint_rule`, `onset_frame_slide`,
`passthrough_max_frac`, `peak_ratio_{float,slide,topple}`,
`triggered_{float,slide,topple}` and **no `l2_verdict`, no `divergence`**. A
`Genesis-MPM` pilot run (`L2_d0.3_v1.5`, created 2026-07-01) carries `depth_m`,
`divergence`, `dv_product`, `l1_haz_score`, `l1_verdict`, `l2_verdict`,
`velocity_ms` `[read live]`. An agreement rate needs both halves of the pair, and
the 17 do not log an L2 verdict at all, so the statistic is not computable over
them from what exists. They are also a different engine and a different scenario.
**The sentence is accurate and should not be changed.**

The `L2` tag overload reproduces independently: 26 runs carry tag `L2` live, the 9
Genesis pilot plus the 17 warpmpm gated `[read live]`. This is W&B metadata, not a
`README.md` error, and I also propose no required change for it.

**3. Gradio demo: WAS STALE, ALREADY CORRECTED IN THE WORKING TREE, NOT YET COMMITTED.**
The Space is live: API gives `private False`, `disabled False`, `stage RUNNING`,
`sdk gradio`, `createdAt 2026-08-17T21:09:46Z`,
`lastModified 2026-08-21T01:13:06Z`, sha `3e27deb4`, `cardData.license bsd-3-clause`
`[read live]`. Tested independently of the platform's own `RUNNING` claim:
`https://josiecerrell-can-it-ford.hf.space/` returns `http_code=200`, 15000 bytes,
**0.30 s**, `<title>Can It Ford</title>`, 6 `gradio` markers `[read live]`.

**The applied README text is accurate**, which I checked rather than assumed. It
claims a verdict-flip explorer over the 17 gated runs, the `v_car` x `v_water` load
surface, and repeat spread. The deployed Space README's own panel table lists
exactly three panels: "Where the verdict flips" (live, 17 runs), "Load surface,
`v_car` x `v_water`" (live), "Repeat spread" (live, 3 configurations) `[read live]`.

**Remaining action on item 3 is a commit, not an edit.** The correction exists only
in the working tree.

**4. Corpus merge vs Citations: NO CHANGE. Reproduced by four independent negatives.**
`docs/CORPUS_MERGE_FINAL_2026-08-22.md` exists, 65030 bytes, mtime 02:48 `[read live]`.
Its two priority DOIs are `10.1007/s00466-019-01783-3` (Gonzalez Acosta et al.,
MPM stress inaccuracies and cell crossing) and `10.1016/j.jcp.2016.10.064` (Zhang
et al., incompressible MPM for free surface flow) `[read live]`.

- Tested all **nine** identifiers the Citations section cites
  (`jfr3.12527`, `s11069-013-0889-2`, `matecconf/201820307003`, `2023WR036739`,
  `1999-01-1336`, and arXiv `2605.30542`, `2507.09005`, `2311.12198`, `2308.04079`)
  against the merge doc: **0 hits each, nine for nine** `[read live]`.
- By subject: grepping `README.md` for
  `converg|refine|cell.cross|sound speed|oscillat|GIMP|stress|quadrature|incompressib`
  returns **no hits at all**. The README makes no numerical-method claim for either
  paper to touch `[read live]`.
- The merge doc contains the string `README.md` **zero times** `[read live]`.
- Its only prescribed change, at its line 269, is to soften one sentence in
  `docs/COUPLING_VALIDATION_J1_2026-08-07.md`, an internal file `[read live]`.

**Stated explicitly, as the dispatch asked: the corpus merge changes nothing in
`README.md`'s Citations section, and no edit to it is warranted.**

One trap worth keeping. The merge doc does contain "Xiong", but only as **Xiong
Zhang**, a co-author of the JCP paper. That is a different person from the
**Xiong et al. (2024)** WRR paper at `10.1029/2023WR036739` that the README cites.
A name-based match here produces a false positive; the DOI test above does not.

**5. DesignSafe "staged, not yet published": VERIFIED-CURRENT.**
`https://www.designsafe-ci.org/api/publications/v2/PRJ-6388` returns `404` with body
`{"message": "Publication not found."}` `[read live]`. A bare 404 proves nothing
unless the endpoint answers for things that exist, so this pass ran **four**
controls, two more than the first:

| project | http | note |
|---|---|---|
| PRJ-6388 (ours) | **404** | `Publication not found.` |
| PRJ-1892 | **200** | 10085 bytes |
| PRJ-3213 | **200** | real payload |
| PRJ-2740 | 404 | negative control |
| PRJ-2222 | 404 | negative control |

Two positives and two negatives from the same endpoint, so it discriminates and the
404 on PRJ-6388 is meaningful `[read live]`. The "not yet published" half is proven.
The "staged" half is **still not verifiable from outside**, because that needs an
authenticated Data Depot call I did not make. It is corroborated only by the
project's own record: `designsafe-staging/docs/README_designsafe.md:8` reads
"Status: provisional, staged ahead of DesignSafe submission, not yet published"
`[read live]`. Same-repo corroboration is not an independent source.

---

## 8. NEW FINDING, missed by the first pass: the dataset licence in `README.md` is stale

This is the one the dispatch's own framing was built to catch. `README.md` does not
merely state a licence, it **cites `CITATION.cff` as the source for it**, and that
citation now fails against the file it names.

`README.md:166` `[read live]`:

> The associated dataset is released under **ODC-By-1.0** (see `CITATION.cff` and
> the pending DesignSafe DOI, PRJ-6388).

Live, the cited file says the opposite `[read live]`:

| source | dataset licence |
|---|---|
| `README.md:166` | **ODC-By-1.0** |
| `CITATION.cff:17` | **CC-BY-4.0** |
| `citations/CITATION.cff:17` | **CC-BY-4.0** |
| HF dataset `can-it-ford-sweep-v1` | `cc-by-4.0` |
| HF dataset `can-it-ford-speed-surface` | `cc-by-4.0` |

**This was a deliberate decision, not drift.** `CITATION.cff:12-16` carries its own
note: "Changed 2026-08-20 from ODC-By-1.0 on the authors' decision. All three
Hugging Face datasets already advertised cc-by-4.0, so this file was the outlier"
`[read live]`. `docs/PLATFORM_LICENCE_STATE_2026-08-20.md:20-23` records the same
divergence as its "problem 1" and states at :63 that it "is a rights decision, not
an engineering one, and it belongs to Josie and Krishna" `[read live]`.

**The mechanism of the staleness is provable.** Commit `96393ca`, "The data licence
is now one licence", changed exactly three files: `CITATION.cff`,
`citations/CITATION.cff` and `docs/PLATFORM_LICENCE_STATE_2026-08-20.md`. `README.md`
is **not** in that commit `[read live]`. So the decision landed and the README was
left behind, the same shape of defect as item 3.

**Why this one matters more than a stale demo link.** It is a licensing statement on
a public repository, it points the reader at a file that contradicts it, and both
values are real licences, so a reader has no way to tell which governs. It also
reaches DesignSafe, see the companion below.

### The patch

> **UPDATE 2026-08-22 03:33:36 BST: THIS PATCH HAS SINCE BEEN APPLIED. DO NOT
> APPLY IT AGAIN.** `README.md`'s working-tree blob is now
> `d18862e8185d536c0c29c214963257e48ea710f8`, byte-identical to this patch's own
> stated output (`index 7501b97..d18862e`), and `git apply --check` now fails with
> `patch failed: README.md:163`, which is the signature of an already-applied
> patch `[read live]`. The change is **uncommitted**. The remaining action is a
> commit, not an edit. See the third pass at the end of this file.

`docs/README_dataset_licence_2026-08-22.patch`, one file, one hunk, one value.
Verified with a dry run that changes nothing:

```bash
git -C /Users/josie/can-it-ford apply --check --verbose docs/README_dataset_licence_2026-08-22.patch
```

reported `Checking patch README.md...` and applied cleanly. To apply:

```bash
git -C /Users/josie/can-it-ford apply docs/README_dataset_licence_2026-08-22.patch
```

It changes `ODC-By-1.0` to `CC-BY-4.0` on `README.md:166` and nothing else. It is
built against working-tree blob `7501b97`, that is, against the README **with** the
HuggingFace correction already in it, so the two do not conflict.

### Companion, outside `README.md`, flagged and not patched

`designsafe-staging/docs/README_designsafe.md:6` reads
`**License:** Open Data Commons Attribution License (ODC-By 1.0)` `[read live]`.
That is the second surviving ODC-By site, and it is the copy bound for **DesignSafe
publication**, so it is arguably the more consequential of the two. The exact change
would be to replace that line with
`**License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)`.

I did not build a patch for it, for two honest reasons: it is outside the file this
dispatch scoped me to, and a `sed` read of that path was **blocked by a permission
rule** in this session, so I could not verify a patch against its full content. I
read it only through `/usr/bin/grep`, which returned lines 4 to 8. Whoever owns the
DesignSafe package should make that change deliberately.

---

## 9. The HuggingFace record-count discrepancy, independently reproduced

The first pass reported the Space understating its dataset by 20. **It reproduces,
and the deployed and local copies are byte-identical** `[read live]`:

- `hf_space/data/load_surface.csv`: **369 lines**, so 368 records plus a header.
- The CSV deployed on HuggingFace, fetched from
  `spaces/josiecerrell/can-it-ford/raw/main/data/load_surface.csv`: **369 lines**,
  and `cmp` reports it **identical** to the local file.
- `hf_space/data/load_surface_manifest.json`: `"rows_checked": 368`.
- Both the deployed Space README and local `hf_space/README.md`, line 40, say
  **"live, 348 records, 20 cells at five seeds"**.

Three measurements say 368, the page says 348, and the gap of 20 equals the cell
count in the same sentence. **No patch proposed**, for the first pass's reason,
which still holds: `hf_space/**` was in another session's active working set during
both passes.

---

## Limits of this second pass

- **`README.md` was not edited by this pass.** Its md5 was
  `4f4c094d0fe786f94850c1c5ff328529` before and after, re-measured after the patch
  dry run `[read live]`. **That measurement went stale about one minute later**, at
  03:33:36, when a third party applied the licence patch. It was true when taken and
  is not true now. See the third pass. The only repo files this pass wrote are
  `docs/README_dataset_licence_2026-08-22.patch` and this appended section plus the
  banner near the top of this file.
- **The first pass's text was preserved, not overwritten.** It is untracked, so an
  overwrite would have been unrecoverable. A byte copy was taken to the session
  scratchpad before the banner was inserted.
- **`analysis/wb.py snapshot` was not run**, and section 1 explains why in full.
  The run count comes from the read-only `doctor`.
- **"Staged" remains unverified from outside.** Only "not yet published" is proven.
- **Two dataset repos were visible, not three.** The unauthenticated HF listing
  returned `can-it-ford-sweep-v1` and `can-it-ford-speed-surface`. The third,
  `can-it-ford-results`, is recorded as **private** at
  `docs/PLATFORM_LICENCE_STATE_2026-08-20.md:23` with `cc-by-4.0`, and a private
  repo is invisible to an anonymous call. So my listing is a partial view and its
  count is not evidence against that record. The third `sweep-v1` repo returned by
  the models endpoint is a **model**, not a dataset, and carries
  `cardData.license = None`.
- **`designsafe-staging/docs/README_designsafe.md` was read only via grep**, because
  a `sed` read of it was denied by a permission rule this session.
- **Not adversarially reviewed.** No agent or `physics-skeptic` pass was run, per the
  standing instruction not to launch agents unrequested. Every claim above names the
  command that produced it and is single-command reproducible.
- **Concurrency.** `README.md` changed at 03:20:15, mid-task, from another session.
  Two other sessions were active in this repo during this pass. Re-check
  `git status` and the README mtime before acting on anything here.

---
---

# THIRD PASS, 2026-08-22 ~03:42 BST: both README fixes are now applied and both are uncommitted

Prompted by Josie asking what `git diff README.md` shows and who changed it. The
answer moved the file's own conclusions again, which is now the third time in one
hour, so it is recorded rather than patched over.

## What `git diff README.md` shows live

Three hunks, `3` insertions and `2` deletions, `index 7731fed..d18862e` `[read live]`:

| # | line | committed at `e9e80ad` | working tree now |
|---|---|---|---|
| 1 | 7 | absent | `[![HuggingFace](...badge...)](https://huggingface.co/spaces/josiecerrell/can-it-ford)` |
| 2 | 166 | dataset "released under **ODC-By-1.0**" | "released under **CC-BY-4.0**" |
| 3 | 175 | "**Gradio demo:** not yet deployed." | full live-Space bullet |

Nothing else in `README.md` differs from the committed version.

## Reconstructed timeline, from file mtimes and commit timestamps

| time | event | evidence |
|---|---|---|
| 03:20:15 | Hunks 1 and 3 applied (first pass's patch) | `README.md` mtime at session start |
| 03:29:18 to 03:31:51 | Three `hf_space` commits, `adb5634`, `e91ab13`, `ca5ee11` | `git log`, none touches `README.md` |
| 03:30:28 | This session writes `docs/README_dataset_licence_2026-08-22.patch` | patch file mtime |
| 03:32:40 | This session appends the second pass to this file | this file's mtime |
| ~03:32:5x | Second pass measures `README.md` md5 `4f4c094d...`, mtime 03:20:15 | second pass Limits section |
| **03:33:36** | **Hunk 2 applied by a third party** | `README.md` mtime |

## Attribution: what is provable and what is not

**Provable `[read live]`.** The result is byte-identical to this session's patch.
The patch header states `index 7501b97..d18862e`; `git hash-object --path=README.md`
on the live file returns `d18862e8185d536c0c29c214963257e48ea710f8`. Re-running
`git apply --check` on it now fails with `patch failed: README.md:163`, the
signature of an already-applied patch. The change landed at 03:33:36, three minutes
after the patch file was written, so the causal order is consistent.

**Not provable, and I will not assert it.** *Who* applied it cannot be recovered
from git, because an uncommitted working-tree change carries **no author record**.
The three commits in the same window are all authored
`Josephine Cerrell <jcerrell29@students.claremontmckenna.edu>`, but that is the git
identity of every session on this machine, so authorship does not discriminate
between Josie and an agent session. The session hook reported **3 other sessions
active** in this repo at the time. So: either Josie ran the command this session
supplied, or another session applied the patch file it found on disk. Both fit
every observation, and nothing on disk separates them.

## What this changes in the five checks

**It answers the open action on two of them, and closes neither.**

- **Item 3 (Gradio demo)** and **item 8 (dataset licence)** are both now **corrected
  in the working tree and both are UNCOMMITTED**. `git log e9e80ad..HEAD -- README.md`
  is **empty**: none of the three new commits touches `README.md` `[read live]`.
- So the remaining action on both is identical and is a **commit**, not an edit.
  Until that commit, the public GitHub README still shows `ODC-By-1.0` and
  "not yet deployed", because the repository is public and serves committed
  content, not a working tree.
- Items 1, 2, 4 and 5 are untouched by this and their second-pass verdicts stand.

## The lesson, which this file has now demonstrated three times

The first pass ended "Nothing was applied", and was overtaken in 8 minutes. The
second pass ended "`README.md` md5 unchanged before and after", and was overtaken in
about 1 minute, before the response reporting it had finished being written. Both
statements were true when measured. **A timestamped measurement of a shared working
tree is a reading, not a property**, and in this repo, with multiple sessions live,
it can expire faster than the sentence describing it. The durable form is the one
used in the attribution section above: state the blob hash and the mtime, so a
reader can re-derive whether it still holds instead of trusting that it does.
