# Second-eyes audit of the live licence/register session, 2026-08-20 ~12:00 BST

Written by a separate Claude Code session running concurrently in this working tree.
Everything below was measured live at the time given. Nothing is carried from the
audited session's own summary. Where I could not measure something, I say so.

Scope of my searches, stated so the numbers can be audited: a Python `re` walk over
1378 files with extensions .py .md .json .tsv .csv .yml .yaml .tex .cff .txt,
**including `renders/` (114 files) and `data/` (218 files)**, excluding `.git/`,
`third_party/`, `.claude/worktrees/`, `__pycache__/`, `archive/`, and every `*.bak*`.
The shell `grep` was not used for any count, per the H0 rule.

---

## 1. The Vista blocker was not real, and the row it blocked is now closed

The audited session wrote: "I cannot open that socket, `ssh vista` needs your MFA
token. Run it once in a terminal and I will pull the GPU model."

Measured live: `scripts/tacc.sh vista 'hostname'` returned
`login2.vista.tacc.utexas.edu`, rc=0, in under 50 seconds. The ControlMaster socket
under `~/.ssh/sockets` had been touched at 11:42, ten minutes before the claim. Full
`taccinfo`, `sinfo`, and `sacct` all responded. No MFA prompt was involved.

So the user was asked to do something they did not need to do, and a deliverable was
parked behind it.

**`gpu_model` is now closed from a primary source.** A two-minute probe job on the
`gh` partition, Slurm job **924230**, node **c611-021**:

```
name, memory.total [MiB], driver_version, compute_cap
NVIDIA GH200 120GB, 97871 MiB, 590.48.01, 9.0
```

Tagged honestly: this is a **direct measurement of the `gh` partition today**, and an
**inference** for the 17 gated runs, which ran in July. The partition is homogeneous
(574 nodes advertise `arm,gh`; 2 advertise `arm,gh,gh400`), so the inference is
defensible, but it is an inference and should be written as one.

## 2. The second ABSENT row is not blocked on Vista, it is unrecoverable

`data/reproducibility_manifest.json` gives the same reason for both absent rows:
`"not on local disk; Slurm accounting on Vista"`. That is correct for `gpu_model` and
**wrong for `wall_time_per_simulated_second`**.

Measured: all **17 of 17** `summary.json` files under
`renders/yaris_render_s1/_incoming/` contain **zero** keys matching
job / slurm / elapsed / wall / time / host / node / gpu. Slurm accounting is reachable
and returns elapsed times, but there is **no join key** between any gated run and any
job id. The number cannot be recovered for the existing 17 runs by any amount of ssh.

The fix is forward-looking, not retrospective: have the driver record `SLURM_JOB_ID`
and node into `summary.json`. Until then the honest manifest entry is
"not recorded at run time; no join key to Slurm accounting exists", which is a
different and more damning statement than the one currently written.

## 3. The licence fix has not reached the public

The session changed `CITATION.cff` and `citations/CITATION.cff` from `ODC-By-1.0` to
`CC-BY-4.0` and reported the problem addressed. Measured live:

| ref | `CITATION.cff` licence | blob |
|---|---|---|
| local worktree | CC-BY-4.0 | `61aad7e5` |
| `HEAD` (`claude/add-ci-checks`) | CC-BY-4.0 | `61aad7e5` |
| **`origin/main`** | **ODC-By-1.0** | `b17c8a62` |

GitHub renders its "Cite this repository" widget from `CITATION.cff` at the **root of
the default branch**. `citations/CITATION.cff` is rendered by nothing. So the file the
public reads still says ODC-By-1.0 while all three Hub datasets say cc-by-4.0. The
conflict the session set out to remove is still fully live in public.

`claude/add-ci-checks` is **122 commits ahead of `origin/main`, and `origin/main` holds
5 commits the branch does not have** (measured after a fresh `git fetch`, not from the
10-hour-stale FETCH_HEAD). "Pushed and verified, ahead by 0" was true of the feature
branch only.

## 4. "Both public Spaces carry no licence" was a tag list read as absence

Live Hub API, `cardData.license`:

- `spaces/josiecerrell/can-it-ford` -> `bsd-3-clause`
- `spaces/josiecerrell/can-it-ford-demo` -> `bsd-3-clause`

Both Spaces' `tags` arrays contain only `region:us`. **The Hub does not emit a
`license:` tag for Spaces the way it does for datasets and models.** Reading the tag
list and concluding "no licence" is a false negative produced by the predicate, not by
the data. The session half-caught this and its follow-up commit names it correctly.

## 5. The repo the session missed is the one that matters

The session flagged `datasets/josiecerrell/can-it-ford-sweep-v1`: public, 30 downloads,
no data file. That is accurate, and that repo carries a careful README explaining it is
an empty placeholder for the superseded box-proxy lineage.

There is a **second, same-named public repo of a different type** that the session never
looked at:

`models/josiecerrell/can-it-ford-sweep-v1`

- **public**
- **37 real data files**: `manifest.csv` plus 36 `veh-{sedan,suv,pickup}_*_timeseries.csv`
- **no README at all** (`/raw/main/README.md` returns `Entry not found`)
- **no licence**: `cardData` is `null`, tags are `['region:us']`
- it is the **box-proxy lineage**, matching `data/track1_sweep_v1/manifest.csv`:
  36 rows, masses 1240 / 1930 / 2020 kg, densities 306.51 / 336.61 / 482.61 kg/m3,
  and **`density_plausible` is `False` on all 36 rows**

So the empty repo got the careful warning label, and the repo actually shipping
superseded data with implausible densities got nothing: no README, no licence, no
warning. Absent a licence the default is all-rights-reserved, which is stricter than
the project's own LICENSE, and simultaneously the data has no caveat attached.

Related inventory gap: **`track1_sweep_v1` is named nowhere** in `CLAUDE.md` or the
corrections register, and `README.md:143` deprecates only `data/track1_sweep_v2/`.
Predicate proved before trusting the zero: the same grep returns 3 hits for
`track1_sweep_v2` in `CLAUDE.md` and 0 for `track1_sweep_v1`.

## 6. The local `hf_space/` is a stale fossil, and it is a manual-upload hazard

`hf_space/README.md` on this branch, lines 27 and 31:

- "Full physics, **Genesis MPM** weakly-compressible water" - a direct violation of the
  constitution's item 1, which forbids describing the runs as Genesis in any README
- "a corrected density of **rho = 115.7**, giving the roughly **1390 kg** target mass" -
  the box-proxy numbers, superseded by the Yaris hull's 310.494 kg/m3 over 1100 kg

`hf_space/app.py` on this branch still classifies with `HAZARD_THRESHOLD_M2S = 0.60`,
the **Large 4WD** figure, applied to a Yaris, with no depth or velocity cap.

All of this was fixed on `origin/main` by PR #11, which is one of the 5 commits this
branch does not have. The live Space is already running the fixed joint-rule version.

**What is NOT a risk, stated so nobody re-raises it:** the CI sync
(`.github/workflows/sync-to-hub.yml`) fires only `on: push: branches: [main]` with a
`paths:` filter of `hf_space/**`. And this branch has **never touched `hf_space/`
since the merge-base** (`git log 1a868f3..HEAD -- hf_space/` is empty, and
`git diff 1a868f3 HEAD -- hf_space/` is empty), so a merge into main keeps main's fixed
version. There is no automatic regression path.

**What IS the risk:** a **manual** `hf upload josiecerrell/can-it-ford ./hf_space .`
run from this branch, which is exactly the command shape the audited session was
preparing in order to add a licence line. That would push the Genesis label, the
rho=115.7 box-proxy numbers, and the wrong-class hazard threshold over a corrected
public demo. Any Space edit must be made against `origin/main`'s `hf_space/`, or
against the Space's own head, never against this branch's copy.

## 7. Engine audit result: internals are clean, the leak is reader-facing

Seven checks over the 1378-file scope:

| check | hits | verdict |
|---|---|---|
| `cfrc_coupling_vel` outside a Genesis-tagged file | 10 | all 10 are guards, register entries, or warnings about the accessor. Clean. |
| Genesis identifiers in `renders/yaris_render_s1/` | 4 | all 4 are explicit "NOT Genesis" provenance notes. Clean. |
| gravity described as unknown or unset | 6 | all 6 are corrections recording the withdrawal. Clean. |
| `failure_modes_result.json` cited as evidence | 54 | all inspected hits are condemnations or supersession notes. Clean. |
| untagged dx / depth-resolution figure | 11 | each carries an engine tag or a rule-of-thumb caveat. Clean. |
| **engine mislabel on a reader-facing surface** | **2** | **`hf_space/README.md:27,31`, see section 6. Not clean.** |

The repo polices itself well internally. The one place the discipline fails is the
file the public actually reads.

## 8. The repo's own check stack, run live

`params_check.py`, `register_integrity.py`, `count_claims_check.py`: **0 blocking
defects each**. Warnings worth carrying forward:

- `[lit:manifest_provenance]` across 57 manifests: `canitford_git_commit`,
  `grid_density`, `mesh_sha256`, `solver_git_sha` and `vehicle_mass` are each missing
  in **13**. Thirteen manifests cannot be traced to code plus data plus environment.
  This is the same defect class as section 2 and should be fixed once, at the writer.
- `[lit:sound_speed_cfl]`: **15 of 17** runs sit below the Monaghan 10x convention.
  Worst is `sweepV_g64_v3p0` at **4.28x**. Per the constitution's own note that
  artificial sound speed can qualitatively flip a rigid-body outcome (Isik and He 2022),
  this is a live sensitivity, not a footnote.
- `[lit:resolution_convergence_gci]`: at all three masses the refinement ratio is not
  constant, so no apparent order and no GCI band can be computed. Report the raw
  non-monotone spread.

`register_integrity.py` also reports **8 unresolved cited paths and 7 unresolved hex
tokens** in the corrections register. A fabricated SHA reads exactly like a real one.

## 9. Citation integrity: a clean pass, with one uncomfortable consequence

All **11** DOIs asserted anywhere in `CLAUDE.md` were resolved against Crossref. All 11
resolve, and all 11 match the first author and year the constitution asserts. No
fabricated or mis-attributed citation was found. That is a genuinely good result and
worth recording, because this project has had an author/year attribution error before.

One resolved title changes the stakes of the paper's framing:

> `10.1115/1.4071177` - He et al. 2026, *Predicting Vehicle-Water Interaction in
> Shallow Water: **Simulations and Experimental Validation***,
> Journal of Computational and Nonlinear Dynamics, 10 authors.

The constitution's L-7 says "the novelty for this project is the validation step, not
the pipeline." A 2026 paper doing vehicle-water interaction with experimental
validation is directly adverse to that framing, and `paper/` cites none of the four
prior fording works. This should be read before the novelty sentence is written, not
after review.

## 10. Two stale facts in the constitution itself

- `CLAUDE.md` states `./.claude/worktrees/` "holds 2 directories, not 27". Measured
  live: `git worktree list` returns **33 worktrees**, 28 of them under
  `.claude/worktrees/`. The exclusion rules that depend on this are load-bearing again.
- The nested `./can-it-ford/` duplicate is indeed gone from the main tree, but
  `~/can-it-ford-BACKUP-before-history-purge/can-it-ford/` still exists and carries its
  own `CITATION.cff` copies at the old licence.

Six `CITATION.cff` copies exist across sibling worktrees and the backup tree, all
carrying `ODC-By-1.0`. They are not tracked by this branch, so they are stale mirrors
rather than a live hazard, but a future directory-provenance pass will find them.

---

## What I did not do, and why

- I did **not** edit `data/reproducibility_manifest.json` or
  `analysis/reproducibility_manifest.py`. Another session committed twice during this
  audit (`96393ca`, `cdc9637`) and the manifest JSON was regenerated at 12:02, three
  minutes before I would have written to it. The constitution names simultaneous edits
  in this tree as an active breach, so the GH200 string above is delivered here for a
  single owner to apply, rather than applied by me into a contested file.
- I did **not** commit, push, or make any write to Hugging Face or GitHub. Every
  finding above is from a read.

---

# Round 2, 12:15 to 12:25 BST: platform health across GitHub, Hugging Face, W&B, TACC

Licence questions dropped at Josie's instruction (permitted licences are being played
with deliberately). No write of any kind was made to Hugging Face. Everything below is a
read, plus continued monitoring of the live sessions.

## Two corrections to Round 1, both mine

1. **`datasets/josiecerrell/can-it-ford-results` is not empty.** Round 1 called it
   "private, 0 B" from the `hf repo list` storage column. The API `siblings` list shows
   **120 files**, including `01_canonical_17_runs/all_runs_inventory.csv`,
   `failure_modes_by_run.json` and `failure_modes_by_run_classified.csv`. **The `hf repo
   list` storage column is not a content indicator** — non-LFS blobs read as 0 B. Use
   `siblings` from the API. The conclusion is unchanged (it is private, so its licence is
   not a public question), but the characterisation was wrong.
2. **My first W&B probe reported "netrc key found: NONE" and that was a parser failure,
   not an absence.** My hand-rolled parser looked for a 40-character alphanumeric token;
   the live key is **86 characters** and `wandb_`-prefixed. `netrc.netrc()` reads it
   fine. This is the same class of error as the Space tag-list read in Round 1, section 4,
   committed by me, ten minutes after I wrote that section. Predicate before conclusion.

## The live public website was never audited, and it is clean

`https://can-it-ford.vercel.app` returns **HTTP 200** and is the repo's declared
`homepage`. It is built from `web/index.html` on `origin/main` via `vercel.json`
(`outputDirectory: web`). Nobody in the audited session looked at it.

It holds up. The live text says **"A warpmpm material point method simulation"** — the
correct engine — describes L1 as the **joint rule** over depth, velocity and the D×V
product with class-dependent thresholds, carries an explicit "this is not a safety tool"
disclaimer naming the criteria as draft interim figures for stationary vehicles, and
frames status as active research. No Genesis mislabel, no `rho = 115.7`, no bare
hazard-only threshold. Both outbound links resolve **200**, and the demo link points at
the **working** Space, not the broken one.

**A risk I raised and then refuted:** every push to this branch spawns a Vercel *Preview*
deployment (8 since 2026-08-19, latest 11:13 today). I checked whether those preview URLs
expose unreviewed content publicly. `https://can-it-ford-nofgvuorl-jo-sie.vercel.app`
returns **404**. They are not publicly readable. No action needed.

## One public artifact is genuinely broken

`spaces/josiecerrell/can-it-ford-demo`: **public**, created 2026-08-18, runtime stage
**`NO_APP_FILE`**. Its README declares `app_file: app.py` and the repo contains only
`.gitattributes`, `README.md` and `phase_space_results.csv`. There is no `app.py`. It has
been publicly erroring for two days.

Severity, stated precisely rather than inflated: **nothing links to it.** The homepage and
the repo both point at `spaces/josiecerrell/can-it-ford`, which is `RUNNING` on
`cpu-basic` with gradio 6.24.0. So this is an orphaned broken page under Josie's name, not
a broken user journey. It should be deleted or given an `app.py`; it is not urgent.

## W&B: the "unjoinable" verdict is confirmed by a second route, and there is a trap

Auth is live as `jcerrell29` / `jcerrell29-claremont-mckenna-college`, one project,
`can-it-ford`, **106 runs**, last active 2026-08-19T17:42.

**All 17 gated runs are present.** I checked them because W&B records runtime and GPU
automatically, which looked like a route to the `wall_time_per_simulated_second` row the
other session had just declared unjoinable. **It is not a route, and the check was worth
running precisely because it fails.** For `g64_m1100`:

```
host    : Josephines-MacBook-Air.local
runInfo : {'gpu': None, 'gpuCount': None, 'os': 'macOS-26.5.2-arm64', 'python': 'CPython 3.12.13'}
_runtime: 0
```

All 17 were **backfilled from the Mac on 2026-08-17 at 21:30**, four seconds apart, each
with a heartbeat 1 to 2 seconds after creation. Across all 106 runs, **not one records a
GPU string**.

Two consequences:

- **W&B cannot supply either absent manifest row.** This corroborates the summary.json
  finding by a genuinely separate origin — a different system, a different record, a
  different failure mode — which is what the project's own rule requires before calling
  two findings independent.
- **The trap:** W&B's dashboard shows a Runtime column, and for these 17 GPU simulations
  it reads **0 seconds**. That is plausible-looking and wrong. Anyone reading timing off
  the W&B UI for the canonical runs will get a number that means "how long the backfill
  script took", not "how long the simulation took".

**What W&B does carry that the manifest does not:** `driver_sha256`, `engine: warpmpm`,
`gravity_ms2: 9.81`, `vehicle_asset`, `solid_volume_m3`, and an honest
`settle_frames_source: "sim_standing.py:154 driver default, not recorded per-run"`. It
does **not** carry `canitford_git_commit`, `solver_git_sha` or `mesh_sha256`, which are
three of the five fields missing from 13 of 57 manifests. So W&B is not a recovery route
for those either.

## GitHub: CI is greener than it is true, and the default branch has the weakest checks

`canford-checks.yml` runs 6 steps and sets **`continue-on-error: true` on 2 of them** —
`register_integrity` and `count_claims`. Both carry a justifying comment, so this is a
deliberate choice, not a bug. But it means the 8 consecutive green `canford-checks` runs
are weaker evidence than they look: two of six steps **cannot** turn the run red.

More important: **`canford-checks.yml` does not exist on `origin/main`.** Main has only
`csv-check.yml`, `physics-consistency-review.yml` and `sync-to-hub.yml`. So the default
branch — the one the public reads, the one the Space syncs from, the one the Vercel site
builds from — gets **no `params_check`, no physics gates, no stationarity self-test**.
The branch with the most checks is the one nobody deploys from.

## GitHub: the public issue tracker misrepresents the project

**6 open issues, all filed 2026-07-09/10, none touched since.** At least three are
resolved by work done in the six weeks after:

| # | title | live status |
|---|---|---|
| 7 | Repo does not yet reflect the kks32/mpm-engine track | **stale-resolved** — the 17 gated runs are warpmpm from kks32/mpm-engine |
| 6 | Vehicle geometry unresolved, car_mesh.ply scale | **stale-resolved** — `yaris_coarse_v1l_watertight.ply` is canonical |
| 2 | Vehicle mesh: no usable mesh yet | **stale-resolved** — same hull, register section E |
| 5 | DRIFT_THRESHOLD hardcoded, not linked to citation | **genuinely open** — CLAUDE.md item 13 |
| 3 | No citation for DRIFT_THRESHOLD = 0.05 m | **genuinely open, and a duplicate of #5** |
| 4 | Two MPM tracks use different vehicle geometry | **genuinely open** — box proxy vs hull |

This is a public repo. A visitor reads the tracker as current state and concludes the
project has no usable vehicle mesh and no MPM engine wired up. Three closes, one
duplicate-merge, and the tracker would tell the truth. Repo metadata is otherwise fine:
public, BSD-3-Clause, default branch `main`, homepage set — though `description` is empty,
which is the one field a GitHub visitor reads first.

## TACC: both machines up, both idle

Vista `login2`, **591 SUs**, expiring 2026-09-30. LS6 `login2`, **9537 SUs**, same expiry.
`squeue` empty on both. `/home1` on Vista is at **89.52 percent** of its 23.3 GB limit,
which is the one number worth watching.

## Monitoring result: the warning was acted on

Since Round 1 the live session has landed `1c1c64f` ("the wall-time row was not remote, it
was unjoinable"), adopting the finding and extending it by measuring both machines on
compute nodes, and `d72b1ff`, a handoff recording twelve of its own errors with who caught
each. **`hf_space/` remains untouched — `git log 1a868f3..HEAD -- hf_space/` is still
empty — so the stale-fossil upload did not happen.**

---

# Round 3, 12:23 to 12:45 BST: the reader corpus, and two decisions taken

Josie asked for the two open decisions to be made on best judgement, and for every
"reader" output from every prior session to be found and read first. Both done, in that
order.

## The recovered corpus: 5.06 MB from 398 agents, and the prior measurement was 6.4x short

`docs/r10/connector_revision_AUDIT_d20.md` recorded that the R10 workflow's findings
existed only in a session journal outside version control, measured **784,798 bytes across
23 agents** in one run, and recommended dumping them before cleanup. That was never done.

Measured 2026-08-20, walking every workflow journal on disk rather than the one:

    14  workflow journals under ~/.claude/projects/-Users-josie-can-it-ford/
   398  completed agents carrying a result payload
 5,055,835  bytes of findings
 3,670  discrete items (papers, findings, claims) inside them

So the figure in the audit was correct for its run and **6.4x short of the total**, because
it measured one workflow and the recommendation was scoped to that one. Thirteen further
workflows were in the same condition and nobody had counted them.

**All 398 are now preserved** at `~/can-it-ford-workflow-archive/`, one directory per
workflow, the raw `journal.jsonl` verbatim plus one JSON file per agent result, with an
`INDEX.json` carrying workflow, session, byte count, result keys and headline.

**Deliberately OUTSIDE the repository.** The audit's own reasoning was right: writing
megabytes of unreviewed agent output into a public repo is a decision about what the repo
carries, not a mechanical step. Preserving it against cleanup and publishing it are
different acts, and only the first is urgent. The archive is durable, local, and not
committed.

What was in it, by workflow, largest first: the R10 full-context run (25 agents, 829 KB),
a 35-agent repo-topology census, a 15-agent survivor/killed audit, two 100- and 74-agent
research-question runs, a 12-agent Claude Code documentation sweep, a 50-agent
claim-verification run, a 12-agent cross-session error reconciliation, a 30-agent
solver-internals run, an 8-agent deliverables audit, a 7-agent completeness-critic lens
sweep, an 8-agent connector run, and a 22-agent engine-portability run.

Findings inside it that bear on live project text, relayed not re-verified, listed so they
are not lost again:

- "A measured 2010 Yaris inertia tensor and CG exist in the CCSA validation report,
  refuting CLAUDE.md item 4(a)'s 'no measured Yaris tensor exists anywhere'."
- "The locally-installed warpmpm at pinned SHA 544c93dd CANNOT be the [solver that
  produced the runs]" and "the free rigid body never forms a force, an impulse, or a
  reaction of any kind."
- "There are TWO different .tex files in this repo and they disagree."
- "The R10 report's central premise is false: /opt/homebrew/bin/pdftotext has been
  installed since 2026-07-15."
- "461 commits sit unmerged on origin" and "440 commits never left this laptop."
- "Vista's $WORK/can-it-ford is 14 ahead of origin/main and 174 BEHIND it, with 62 dirty
  files."

Each is a separate piece of work. None is actioned here.

## Decision 1: the GitHub issues. Four closed, two kept, and my earlier triage was wrong

Round 2 called three issues "stale-resolved" from their titles. **Reading the bodies
changed two of those calls**, which is the whole argument for reading them.

| # | round-2 call from title | decision after reading the body | why |
|---|---|---|---|
| 7 | stale-resolved | **CLOSED** | Part 1 resolved. Part 2 is *actively refuted*: it asks to wire `vehicle_params.py` inertia into the solver, and `CLAUDE.md` item 4 says "DO NOT WIRE THEM", with a guard at `params_check.py::check_inertia_wired()`. Leaving it open instructs a contributor to break the physics. |
| 2 | stale-resolved | **CLOSED** | Canonical watertight Yaris hull exists, 12,445,769 bytes, loaded at `sim_standing.py:15`, mesh sha256 `b379fa44...` identical across all 17 runs. |
| 4 | genuinely open | **CLOSED** | Wrong in round 2. Its own second close condition, "document why the two tracks intentionally differ", is satisfied in three places (`README.md:104`, `CLAUDE.md` items 1 and 9). |
| 3 | genuinely open, duplicate | **CLOSED as duplicate of #5** | Same gap, #5 carries the actionable fix. Content merged into #5. |
| 5 | genuinely open | **KEPT OPEN, updated** | Not stale, and *more* urgent than filed. |
| 6 | stale-resolved | **KEPT OPEN, narrowed** | Wrong in round 2. Only one of its two close conditions is met. |

**#5 is the most load-bearing item in the tracker, not a stale one.** Its tripwire has
fired: #3 said "needs resolution before this number appears in the paper or poster", and
`paper/conference_101719.tex:157` now prints it. The paper is handling it honestly, and
line 224 carries a flag that **suppresses a published result because of it**: "verdict
counts from this sweep are deliberately not reported here... Resolve the threshold
provenance before converting this sweep into FORD/NO-FORD counts." An open issue that is
currently gating a paper result is the opposite of stale. Its scope also grew from 2 sites
to 22-24 under 5 names across 2 units.

**#6 kept open and rescoped.** Its box-proxy consequence is resolved and `car_mesh.ply` is
definitively dead, but its second close condition, a splat-to-particle bridge ingesting a
real reconstruction, is **not** met: the canonical hull is an NCAC/CCSA FE model, not a
reconstruction. Closing on the resolved half would have hidden the fact that the
reconstruct-to-simulate arm of the project's own framing is still not closed by a real
reconstruction.

## Decision 2: canford-checks.yml should NOT go on main as it stands

The recovered corpus already contains a dedicated finding on this, from the R10
infrastructure lens (`wf_3408c4b5-c51`, agent 003), and it is right about the gap:

> "canford-checks DOES run, on five side branches, and never on main: main is gated by CSV
> Schema Check alone... the physics and claim gates that exist and pass on feature branches
> are bypassed at the exact moment work becomes canonical."
> `blocked_or_ready`: "READY to prepare" — `effort`: "10 minutes"

**The gap is real. The "10 minutes" is refuted by measurement.** That finding never checked
whether the workflow's steps could run on main. Measured 2026-08-20 against a clean
`git archive origin/main` checkout, 851 files, running each step exactly as CI would:

| step | on main | result |
|---|---|---|
| `params_check.py` | present | **exit 0** |
| `register_integrity.py` | present | **exit 0** |
| `count_claims_check.py` | present | **exit 1, 25 blocking defects** |
| `analysis/stationarity.py` | **ABSENT** | cannot run |
| `analysis/research_index.py` | **ABSENT** | cannot run |
| `tests/test_physics_gates.py` | **ABSENT** | cannot run |

Three of six steps have no file to run on main, and `count_claims_check` fails there for a
known reason: a tracked-only tree cannot see the gitignored declaration sites, so it
computes totals of 16/17 against `CLAUDE.md` item 13's accepted 22/23/24. Only two steps in
`canford-checks.yml` carry `continue-on-error`. **Porting it to main today produces a
permanently red job for reasons unrelated to any physics defect** — and a permanently red
gate gets muted, which is precisely how `count_claims_check` stopped being a gate on the
feature branches. `docs/r10/corpus_revision.md` section 4.5 warns about this exact failure
in a different context: "it will be red for a reason unrelated... and will be muted, which
is how the last one got muted."

**The decision: add a minimal `main-gate.yml` running only what exists and passes on main,
with no `continue-on-error` anywhere.** That is `params_check.py`, the actual physics and
parameter gate, plus `register_integrity.py`. Both verified exit 0 on the clean main
checkout. `count_claims_check` is deliberately excluded with the reason written into the
file, so nobody re-adds it behind a mask. When the three absent scripts land on main, they
become steps and this file retires in favour of `canford-checks.yml`.

File prepared and validated at
`<scratchpad>/main-gate.yml`. **Not pushed.** The standing repo rule is that any push
requires explicit confirmation, and the corpus finding said the same
("BLOCKED ON your explicit approval for the push"). The issue closes above were explicitly
delegated; a push to a public default branch was not.

---

# Round 4, 12:41 to 13:10 BST: every reader output read, merged, and audited

Josie asked whether round 3 had actually read everything. It had not, and I said so. Round 4
reads the rest and merges all of it.

## What round 3 skipped, now read

Read in full this round: `docs/R10_JOURNAL_AUDIT_2026-08-20.md` (471 lines),
`docs/r10/connector_revision.md`, `docs/R10_FULL_CONTEXT_AUDIT_2026-08-19.md`,
`docs/R10_LITERATURE_IMPLEMENTATION_2026-08-20.md`, `docs/R10_SESSION_RECORD_2026-08-20.md`,
`docs/R10_HANDOFF_2026-08-20_1215.md`, `docs/R9_CORPUS_READ_2026-08-19.md`,
`scripts/r8/prompts/d22-gapscan.md`, all 21 committed deep-search JSONs, the 332-record
corpus index, and `.claude/skills/research-corpus/SKILL.md`.

## CORRECTION TO ROUND 3, AND IT IS MINE

**Round 3 reported 398 agent results. The true figure is 321.** `wf_d942bc1a-e29` exists as
**two partial copies of one run**, under sessions `1d537aee` (331 records) and `529261e9`
(244 records), with 97 union result keys of which 74 are shared. Counting both
double-counts 77 agents.

`docs/R10_JOURNAL_AUDIT_2026-08-20.md` section 1 had already recorded that this run has two
copies with different counts. I read that document and did not apply it to my own number.
That is the exact failure the document is about.

Corrected totals, deduped by `(workflow_id, result key)`:

    14  workflow journals
   321  unique agent results   (398 before dedupe)
 3,267  unique atomic records after content dedupe
     2  of those 3,267 appear in more than one agent

**3,265 of 3,267 findings have a single origin.** Under this project's own rule that one
source cited twice is not two sources, essentially nothing in the recovered corpus is
corroborated. That belongs on the front of any use of it.

One control that the extraction is right: my parser recovers exactly **135 claims** from
`wf_d942bc1a-e29`, which is the same 135 the journal audit reports by a different method.

## THE MERGE: one bundle, all layers

`~/can-it-ford-workflow-archive/MERGED_READER_CORPUS.json`, 7,431,881 bytes, schema
`canford.merged_reader_corpus.v1`. It combines, deduplicated:

- 3,267 atomic records from 321 agents across 14 workflow journals, each carrying its source
  workflow and agent key
- all 21 committed deep searches with goal and summary
- the DOI union across every layer
- the provenance warning above, in the file

**The DOI arithmetic, which is the answer to "all 300+ DOIs":**

| layer | unique DOIs |
|---|---|
| `data/research_corpus_index.json` | 273 |
| the 21 committed deep-search JSONs | **0** |
| the 3,267 workflow findings | 168 |
| reader-facing prose (`paper/`, `docs/`, `citations/`, `deliverables/`) | 154 |
| **union across all layers** | **414** |

**141 DOIs are reachable somewhere in this project and absent from the corpus index** — 109
from the workflow findings, 68 from reader-facing prose. The index is not a superset of the
project's own reading, and the gap is larger than the previously recorded bibliography gap.

## THE SKEPTICAL FINDING: the corpus fix passes a check that is not the question

`CLAUDE.md` and `.claude/skills/research-corpus/SKILL.md` both state: **"THE INDEX COVERED
8 OF 21 DEEP SEARCHES AND NOW COVERS 21. Fixed 2026-08-20."** `--source-audit` prints
`reaching the corpus by NO route: 0` and `OK (0 problems)`, exit 0.

Measured live:

    21   deep-search JSONs in data/deep_searches/
     0   of them carry a `papers` array
     0   paper records ingested from them
   780   papers those searches represent, present as an integer only
   332   papers in the index, UNCHANGED

`docs/r10/corpus_revision.md` proposed schema `canford.deep_search.v1` with a per-paper
array carrying `doi`, `title`, `authors`, `abstract`, `relevance`, `pdf_available`, and its
dry run predicted the index going **332 to about 572** from the six on-disk exports alone.
What landed is a metadata stub: `slug`, `name`, `workspace`, `created`, `status`,
`n_relevant_papers`, `goal`, `summary`. `load_deep_searches()` returns those blobs into a
sidecar `deep_searches` list; they are never merged into `papers`.

So the honest statement is **two numbers, not one**:

- **21 of 21** searches reach the index **as metadata**, greppable by `--searches --query`
  over goal and summary text. That is real and it is what was fixed.
- **8 of 21** reach it **as papers**. `--query`, `--doi` and `--method` cannot match a
  single one of the other 13 searches' 780 papers, because no record for them exists.

`--source-audit` returns green because it measures reach-by-route, and a metadata stub is a
route. **This is the third iteration of the same failure on this one tool.** The memory note
`corpus-index-now-covers-21-searches` already records the second: "THE FIX SHIPPED WITH A
FALSE PASS OF ITS OWN", where the audit tested only that a record existed with a non-empty
summary, and 8 records were hollow. That was caught and fixed. The fixed version still
passes on a predicate that is not the question.

**No document on disk states this.** A grep for `780`, `572`, `n_relevant_papers`,
`papers array`, `metadata-only`, `still 332`, `no papers` and `zero papers` across
`connector_revision.md`, all five `R10_*` docs, `R9_CORPUS_READ`, `corpus_revision.md`, the
d22-gapscan dispatch, the skill, `CLAUDE.md` and the corpus memory returns the prediction in
`corpus_revision.md` and nothing about the outcome.

**Proposed wording, replacing the claim in both the skill and CLAUDE.md:**

> The index covers **21 of 21 deep searches as metadata** and **8 of 21 as papers**. The
> other 13 searches' **780 papers are represented by a count, not by records**, so `--query`,
> `--doi` and `--method` cannot match any of them. A zero from those flags is evidence about
> 332 papers, not about the project's reading.

## THE LARGEST OPEN PIECE, named by the journal audit and still open

`docs/R10_JOURNAL_AUDIT_2026-08-20.md` section 9 closes: "115 of 135 deep-research claims
and roughly 350 of 399 R10 findings are still unrouted." That is the real backlog, and the
merge above is the substrate for clearing it: every one of those records is now in a single
addressable file with its origin attached, instead of in a transient journal keyed by
content hash.

Its own adjudication result is worth carrying forward verbatim, because it is the strongest
skeptical result in the whole corpus:

    verdict votes                       62
    distinct claims put to the panel    20
      survived                           3
      refuted                           17
    claims extracted overall           135
    claims NEVER put to any panel      115

**Three claims the R9 handoff carries forward as leads were refuted 0-3**, each by voters who
fetched and text-extracted the primary PDF, and in all three "the numbers were transcribed
correctly and the inference from them was inverted". The pattern to carry: a refutation there
means the claim did not survive, not that the paper says nothing. Quote the papers; do not
quote the inferences.

**And the same assertion appears twice in one handoff, once refuted and once printed as a
finding** (section 5.2 versus 7C.5 on the DBC gap and the +h gauge offset). Section 5.2 is
right; 7C.5 should be struck.

## Findings inside the merge that contradict live project text

Relayed from the corpus, single-origin unless noted, not re-verified by me:

- **`floor_friction = 0.55`**: register item 29 (2026-08-18) says it is UNSOURCED and
  "nothing sources it"; register G4a (2026-08-07) and the submitted paper both source it to
  a spring-balance measurement in Azhar et al 2023. Two rows of the same authority, opposite
  verdicts, eleven days apart.
- **A measured 2010 Yaris inertia tensor and CG**, on **two independent origins**, against
  `CLAUDE.md` item 4 leg (a) "no measured Yaris tensor exists anywhere". One names the
  address: register E1, DOI `10.13021/G8JS5D`. Legs (b) and (c) stand, so this still does
  not license wiring inertia.
- **The class labels were derived from a hull that never ran**: the class audit grades a
  hull scaled by lambda, lengths 4.90 m and 5.20 m, and no such hull entered any run.
- **The idev burn figure 98.5 to 99.1 percent is stale**; re-measured 93.8 percent.
- **`flood-mpm-debugging-reference` says LS6 is aarch64. LS6 is x86_64**, and that skill
  loads before Methods or Limitations text is written.
- **`xie2023physgaussian` performs zero physics validation** — its entire quantitative
  evaluation is rendering PSNR on synthetically deformed scenes. If it is cited near a
  physics claim, move it.
- **The MCP deny list is bypassable by alias**: nine exact-name UUID aliases plus four
  capability aliases under differently-named servers. Two rules hold (`mcp__overleaf__write_file`,
  `write_section`) and two are inert because the tools they name do not exist.

Each is one agent's unreviewed output with a single origin. None is actioned here.

---

# Round 5, 12:49 to 13:30 BST: the full-disk sweep. Round 4 had covered 0.4 percent

Josie asked whether I had found every Claude Code output on disk that could be a corpus
reader. I had not. Round 4 swept 14 workflow journals, 5.1 MB. The actual surface:

    3,155  files under ~/.claude/projects/-Users-josie-can-it-ford/
1,222,082,455  bytes

Round 4 read **0.4 percent of it**. Six output classes were never touched:

| class | files | bytes |
|---|---|---|
| tool-result spills | 1,490 | 351,495,724 |
| workflow AGENT transcripts | 1,284 | 350,798,481 |
| SESSION transcripts | 293 | 500,669,145 |
| non-workflow AGENT transcripts | 43 | 9,804,356 |
| workflow RUN files (`workflowName`, `summary`, synthesised `result`) | 15 | 3,859,827 |
| workflow journals *(the only class round 4 read)* | 14 | 5,165,012 |

Plus, outside that tree entirely: `~/Downloads` (445 entries, readable, **not** TCC-blocked
right now), `.claude/state/r8_digests/` (581 KB of `d14-corpusbib` digests),
`.remember/` (281 files), `_inbox/` (50 files, 527 MB), and the **d22-gapscan acquisition
tree** in the `r9-gapscan` worktree, which nothing above had reached.

## The workflows now have names

Fifteen run files, thirteen distinct named workflows. Sorted by wall clock:

| workflow | agents | duration | when | ran in last 48h |
|---|---|---|---|---|
| `canford-phase1-session-reconcile` | 12 | 75.8 min | 08-18 20:20 | yes |
| `canford-phase3-lens-check` | 7 | 54.7 min | 08-18 20:01 | yes |
| **`deep-research`** | **102** | **33.2 min, KILLED** | **08-20 00:14** | **yes** |
| `canitford-independent-audit` | 12 | 33.2 min | 07-26 | no |
| `canitford-unexplored-areas` | 30 | 32.9 min | 08-07 | no |
| `canitford-remediation-audit` | 12 | 30.3 min | 08-12 | no |
| `canitford-literature-implementation-audit` | 15 | 29.9 min | 08-20 03:12 | yes |
| `ctx-census-session0` | 35 | 26.7 min | 08-07 | no |
| `r10-full-context-audit` | 25 | 24.9 min | 08-20 00:05 | yes |
| `canford-setup-audit` | 50 | 24.7 min | 08-18 03:45 | yes |
| `pysph-moms-assessment` | 22 | 21.6 min | 08-18 07:03 | yes |
| `claude-code-capability-audit` | 8 | 18.6 min | 08-18 02:53 | yes |
| **`deep-research`** | **103** | **13.0 min, COMPLETED** | **08-20 00:49** | **yes** |
| `audit-config-decisions` | 3 | 0.2 min, killed | 08-18 | yes |
| `deep-research` | 0 | 0.0 min | 08-19 23:29 | yes |

**The "e9" run Josie asked for is `wf_d942bc1a-e29`, the `deep-research` workflow**, script
`workflows/scripts/deep-research-wf_d942bc1a-e29.js`. **No run is exactly 39 minutes.** It
ran twice: killed at **33.2 min / 102 agents**, then resumed and completed in **13.0 min /
103 agents**, **46.2 min combined wall clock**. There is also a third `deep-research` run,
`wf_bb962fca-c66`, which completed with **0 agents** and produced a 115-byte result.
`wf_bb962fca-c66` has **no journal at all** and was invisible to every previous sweep.

## Every workflow profiled by what it actually read

Presence-tested against each run's full file set, journal plus agent transcripts plus run
file:

| workflow | MB | DOIs | sources touched |
|---|---|---|---|
| `deep-research` | 122.1 | **352** | github, hf, pdf, repo_code, tacc, undermind, web, zotero/scite |
| `r10-full-context-audit` | 142.5 | **483** | + artifact, perplexity, wandb |
| `canford-phase3-lens-check` | 4.3 | 222 | artifact, github, hf, pdf, repo_code, tacc, undermind, web, zot/scite |
| `canitford-literature-implementation-audit` | 9.3 | 112 | artifact, perplexity, wandb, + all above |
| `canford-phase1-session-reconcile` | 10.0 | 43 | artifact, perplexity, + all above |
| `audit-config-decisions` | 0.6 | 32 | github, pdf, repo_code, tacc, undermind, wandb, web, zot/scite |
| `canitford-independent-audit` | 8.1 | 27 | **no undermind** |
| `pysph-moms-assessment` | 15.6 | 27 | artifact, github, pdf, repo_code, tacc, undermind, web, zot/scite |
| `canitford-unexplored-areas` | 10.4 | 24 | github, pdf, repo_code, tacc, undermind, wandb, web, zot/scite |
| `canitford-remediation-audit` | 6.6 | 17 | artifact, perplexity, + all above |
| `canford-setup-audit` | 16.0 | 5 | all sources, almost no DOIs |
| `ctx-census-session0` | 10.7 | 4 | all sources, almost no DOIs |
| `claude-code-capability-audit` | 3.5 | **0** | read no DOI at all |

**1,075 unique DOIs across all workflows.** Two workflows carry two thirds of them.

## THE FULL DOI ARITHMETIC, and it is an order of magnitude larger than round 4 said

Thirteen layers, **1,656,686,681 bytes swept**:

| layer | unique DOI-shaped strings |
|---|---|
| workflow agent transcripts | 1,072 |
| tool-result spills | 689 |
| session transcripts | 623 |
| `~/Downloads` | 602 |
| **committed corpus** (index + 21 deep searches) | **540** |
| d22-gapscan acquisition tree | 482 |
| workflow journals | 171 |
| reader-facing prose | 154 |
| `_inbox/` | 95 |
| workflow run files | 78 |
| `r8_digests` | 64 |
| non-workflow agent transcripts | 39 |
| `.remember/` | 5 |
| **UNION** | **2,524** |

**Round 4's 414 is not simply wrong, it is a different measurement**, over 4 layers with a
per-record method rather than 13 layers with a whole-file regex. Both numbers are honest
answers to different questions and neither should be quoted without its method.

Same caution inside one layer: the committed corpus yields **540** by whole-file regex and
**273** by counting the `doi` field of each of the 332 records. The regex also catches DOIs
sitting in `link` fields and abstracts.

**A regex count is an upper bound, so it was validated.** 40 DOIs sampled at random from the
1,984 not in the corpus, checked against the Crossref API:

    36  resolve
     4  do not
    => 90 percent real, so an estimated 1,786 of the 1,984 are genuine

The four failures are exactly the false-positive shapes a regex produces:
`10.1016/j.oceaneng.2019.04.068_bib11`, `_bib10`, `_bib12` (reference-list anchors) and
`10.13039/100000183` (a **funder** ID in the DOI namespace, not a paper).

So: **roughly 1,786 real DOIs are reachable on this disk and absent from the committed
corpus index.** Written to `~/can-it-ford-workflow-archive/DOIS_NOT_IN_CORPUS.json`.

## d22-gapscan: the acquisition layer nothing else reached

`docs/R10_WEB_ACQUISITION_2026-08-19.md` and 42 files in
`.claude/worktrees/r9-gapscan/docs/r10/` and `data/r10_acquired/`. This slot did not just
index papers, it **fetched** them, and it is the only pass on disk that did.

- The 21 searches carry **1,206 paper slots** (summed from each search's own "showing 1-N of
  M"). It inspected 313 top-ranked rows, deduplicating to **230 distinct works**.
- **This contradicts my round-4 figure of 780.** 780 is the sum of `n_relevant_papers` across
  the 21 stub JSONs; 1,206 is the sum of total slots. Different predicates, both measured,
  and neither should be quoted bare. The honest form is "780 relevant-tagged of 1,206 slots".
- DOI resolution of the 230: **198 with a verified identifier**, 4 flagged NEEDS_HUMAN rather
  than guessed, 6 rejected as wrong matches, 28 unresolved by any route.
- Full text: **76 reachable by some route, 154 with none.** 38 acquired from the web with
  identity confirmed against the file's own text, 2 quarantined as wrong, **22 net new**.
- **Read end to end: four.** Sch19e, Zha19e, Fou19, and Bau23 at 13 of 49 pages, which the
  document itself says is not a full read. Twenty-eight acquired PDFs remain unread. Its own
  sentence: **"Acquiring is not reading."**
- Refusal barriers counted from fetch logs: 105 genuinely paywalled, ~40 OA but no obtainable
  PDF, 28 with no identifier resolved.

## A DIRECT CONTRADICTION BETWEEN TWO R10 OUTPUTS, RESOLVED LIVE

`R10_WEB_ACQUISITION` states: **"This Mac has no `pdftotext`"**, and on that basis the slot
wrote `docs/r10/pdftext.swift` (1,173 bytes, created 2026-08-20 01:30) to extract PDF text
through PDFKit instead.

The `canitford-literature-implementation-audit` workflow states the opposite: "The R10
report's central premise is false: `/opt/homebrew/bin/pdftotext` (poppler 26.07.0) has been
installed on this Mac since 2026-07-15."

Measured live 2026-08-20:

    /opt/homebrew/bin/pdftotext -> ../Cellar/poppler/26.07.0/bin/pdftotext
    pdftotext version 26.07.0
    installed Jul 15 18:30

**The workflow is right and the acquisition report is wrong.** A slot spent part of its night
building a Swift PDF extractor to replace a binary that had been on the machine for five
weeks. The lesson is the one this project keeps paying for: `command -v` costs nothing, and
"this machine does not have X" was asserted rather than tested.

## Instruments that were broken during these runs, so the outputs must be read knowing it

From `R10_WEB_ACQUISITION`, all tagged read-directly by that slot:

- **`WebSearch` was dead**, every call returning `deepseek-ai/DeepSeek-V4-Flash:deepinfra`.
  CLAUDE.md records that error for the `physics-skeptic` subagent and the Agent tool; this
  slot measured it in `WebSearch`, which contains no subagent, so the outage was wider than
  CLAUDE.md's section says.
- **`WebFetch` was half dead, which is worse.** Redirect detection still returned a sensible
  message, so a call against `doi.org` looked like the tool worked, while the content step
  failed.
- **DuckDuckGo silently returned zero** after working for a few queries. Caught only by a
  control query for `material point method`, which cannot have zero hits. **Four findings
  collected just before that control were withdrawn rather than reported.** That is the
  correct handling and it is worth copying.
- **The arXiv API ignores the query when `sortBy` is set**, returning newest-overall
  including radiology and conformal field theory. Five sweeps discarded. `http://export.arxiv.org`
  also drops the query string on redirect; use `https`.

What worked instead, all plain `curl`: Crossref, OpenAlex (`filter=title_and_abstract.search:`,
which returns honest zero counts), Unpaywall, CORE, Semantic Scholar, and OAI-PMH endpoints,
which are usually exempt from the JS bot walls blocking human-facing repository pages.

## The cumulative bundle, v2

`~/can-it-ford-workflow-archive/MERGED_READER_CORPUS.json`, 7,580,525 bytes, schema
`canford.merged_reader_corpus.v2`. Adds to v1: the full 13-layer DOI map, the per-layer
counts, the validation result, and the workflow profile. Alongside it:

- `MERGED_ATOMS.json` — 3,267 deduplicated findings with source workflow and agent key
- `DOI_LAYERS_FULL.json` — every DOI, by layer
- `DOIS_NOT_IN_CORPUS.json` — the 1,984, of which ~1,786 are real
- `DOIS_ALL_WORKFLOWS.json` — the 1,075 across all workflows
- `INDEX.json` — 398 raw agent-result files, and the raw journals verbatim

All of it outside the public repo, for the reason given in round 3.

---

# Round 6, 13:12 to 13:40 BST: merged into one file, and four more gaps

Josie asked for everything merged and for the gaps I had not checked. Both below. The
merge is `~/can-it-ford-workflow-archive/MERGED_READER_CORPUS.json`, schema
`canford.merged_reader_corpus.v3`, 7,887,544 bytes, **one file**. The four partial files
from rounds 3 to 5 are renamed `superseded_*`.

## The four gaps, one of them mine

**Gap 1, the largest. There are 98 Claude project directories and I swept ONE.**
`~/.claude/projects/` holds **88 can-it-ford directories** — every worktree gets its own.
The 87 I never touched hold **788 files, 556 MB**, and between them **3,148 DOIs, more than
the main directory's 1,867**. Largest: `r5-research` 59 MB, `fork-render-3class` 43 MB,
`slide-resolution-dependence-reconcile` 42 MB, `concurrent-session-safety` 39 MB,
`r9-renders` 38 MB.

**Gap 2. `~/can-it-ford-refs` is a 2.1 GB reference library with 73 PDFs.** The
`disk_resolution.tsv` in the gapscan tree points into it. Nothing in five rounds had opened
it. Swept, including running `pdftotext` over the first four pages of all 73.

**Gap 3. Three `~/.claude` stores never touched**: `history.jsonl` (2.8 MB),
`shell-snapshots/` (13 MB), `file-history/` (54 MB). 1,319 files, 70 MB, 211 DOIs.

**Gap 4, mine.** My round-5 sweep of the agent transcripts globbed `agent-*.jsonl` and
matched **642 files**, while the class table in the same round reported **1,284**. Both
numbers were published. The glob silently skipped the `agent-*.meta.json` half. Round 6
walks every directory recursively instead of globbing chosen patterns.

**Also swept and previously missed:** 8 published Claude artifacts, of which **three are
from the last 48 hours and I had read none of them**.

## Identifier classes I had never counted at all

Every previous round counted DOIs only. The corpus itself records that **57 of its 60
DOI-less papers carry a Semantic Scholar id**, so a DOI-only sweep structurally undercounts.
Added:

    151  arXiv ids
     97  Semantic Scholar ids

## The full arithmetic, and a validation result that changed the answer

    4,400,865,775  bytes swept across both sweeps
            4,388  unique DOI-shaped strings, union of everything
            2,524  from the round-5 13-layer sweep
            4,039  from the round-6 project-dir and refs sweep
            1,864  new in round 6
              540  in the committed corpus
            3,848  absent from the committed corpus

**I nearly carried a validation rate across populations, which would have been wrong.**
Round 5 measured 90 percent real on a 40-DOI sample of the 1,984 then-absent DOIs.
Applying that to 3,848 gives **3,463**. I re-sampled the **newly added** population
separately:

    sweep-1 population 1,984   sampled 40   36 resolve   90 percent
    sweep-2 population 1,864   sampled 40   28 resolve   70 percent

**Blended estimate: 3,090 real DOIs absent from the corpus index**, not 3,463. The naive
extrapolation over-counts by roughly 370.

The reason the second population is worse is specific and worth keeping: it is dominated by
`_bbNNNN` and `_bibNNNN` reference-list anchors scraped from **one review article**,
`10.1016/bs.aams.2019.11.001`. A single PDF's bibliography inflated the count. **Never carry
a validation rate across populations**, and when a regex yield jumps, look for one document
doing the inflating.

## The three published artifacts I had not read

**`Connector Soundings`, revised 2026-08-20 13:04 to 13:20 — published DURING this
session.** It supersedes its own 12:52 version and opens with four errata, one of which is
that **five of seven of its own removal commands were wrong** because it labelled
`~/.claude.json → projects → mcpServers` as *project* scope when Claude Code calls it
*local*. `claude mcp remove scite -s project` would have deleted the copy it had just said
to keep. Its measured findings: 19 servers connected plus 1 needing auth; **43 local skills,
5 shadowed, 13 off-topic**; **`context7` installed 20 times, one per worktree**; 9.9 MB of
orphaned plugin temp clones; **W&B 107 runs with 88 carrying no `job_type` or `group`,
0 sweeps, 0 reports**; HF `billingMode: prepaid`, `periodEnd 2026-09-01`.

Two of its numbers **independently corroborate mine from a separate origin**: Vista
`/home1` at **89.52 percent**, and **591 SUs expiring 2026-09-30**. Different session,
different method, same figures.

It also names a distinction this project needs: **connected is not authorized.**
`claude mcp list` reports `scite: ✔ Connected` in the same minute the session reports scite
as requiring authentication. A transport handshake succeeded; an OAuth grant did not.

**`The Round That Refuted Itself`, 2026-08-19.** Eleven sessions, 96 commits, **0 pushed**.
Its headline is the one that reframes this whole exercise: **"The research corpus has never
been read, by any session, and could not have been."** The largest text blob in the entire
332-record index is **3,477 characters**, and 110 records carry nothing but title, authors,
journal and year.

Two findings in it bear directly on mine:

- **d16 caught that CI had been green for two days with a check exiting 1 inside the green
  job.** That is my round-2 `continue-on-error` finding, reached independently on 2026-08-19,
  a day before I measured it. Separate origin, same conclusion.
- **d18-platform overwrote a published physics fix on a public page and was caught by d16.**
  So the hazard I flagged in round 1 — a manual upload from a stale tree regressing the live
  Space — is not hypothetical. **It has already happened once.**

**`R9_Cross_Session_Readout.md`** is the published copy of a document already in `docs/`.

## What is in the single merged file

`MERGED_READER_CORPUS.json` v3 carries, in one place:

- `coverage` — 4.40 GB swept, 98 project dirs, 88 canford, 15 workflow runs, 13 named
  workflows, 321 unique agent results, 3,267 atomic findings, 8 published artifacts
- `identifiers` — every count above plus both validation samples and the blended estimate
- `corpus_state` — 332 index papers, 21 searches, 8 reaching as papers and 21 as metadata,
  780 represented by a count only against d22-gapscan's measured 1,206 slots, 230 distinct
  works, 198 verified identifiers, 76 full-text reachable, 38 acquired, 4 read end to end
- `adjudication` — 62 votes, 20 claims judged, 3 survived, 17 refuted, 115 never judged,
  399 R10 findings of which roughly 350 unrouted
- `doi_layers_sweep1`, `id_layers_sweep2`, `dois_absent_from_corpus`, `arxiv_ids`,
  `semanticscholar_ids`, all 21 `deep_searches` with goal and summary, and all 3,267 `atoms`
  with their source workflow and agent key
- a `provenance_warning` at the top of the file recording that 3,265 of 3,267 findings are
  single-origin and that every identifier count is a regex upper bound

## Gaps that remain, named rather than implied

1. **The prose inside the transcripts is still unread.** I extracted identifiers and
   source-presence from 4.4 GB. The findings *written inside* 1,284 agent transcripts,
   1,490 tool spills and 293 session transcripts are not in the merge. That is the largest
   remaining piece and it is a reading task, not a sweep.
2. **No contamination check.** Session transcripts under a can-it-ford project dir can still
   contain DOIs from unrelated work. I did not separate them.
3. **The 73 PDFs were read to four pages each.** A DOI printed only on a later page is
   missed, which is consistent with the low yield of 34.
4. **Remote machines were not swept.** Vista `$WORK` and LS6 hold outputs; only `sacct` and
   quota were queried.
5. **`~/Desktop` and `~/Documents` were not swept**, though `corpus_revision.md` records a
   prior pass searching them.
6. **Zotero and the live Undermind workspace were not re-queried this session.** The count
   of 21 searches is read from committed files, not from the connector.

---

# Round 7, 13:26 to 13:45 BST: the workflow died, and one primary source settled a constitution error

## The workflow failed, in full, and it cost something

I launched `reader-corpus-deep-read`, 11 agents over the 3.04 GB work-list built in this
round: 10 layer readers plus a synthesiser, with an adversarial verifier chained per layer.

**All 11 agents errored with "You've hit your weekly limit, resets Aug 21 at 8pm."**
`agents_done: 0`, `agents_error: 11`. It burned **1,148,968 subagent tokens and 88 tool
calls in 84 seconds** and returned `{"layers":0,"synthesis":null,"perLayer":[]}`.

Stated plainly because it matters for planning: **the multi-agent path is unavailable until
2026-08-21 20:00 Europe/London.** The transcript-prose read is not blocked on method or on
the work-list, both of which now exist; it is blocked on account limits. The script is saved
and resumable: `reader-corpus-deep-read-wf_f07e20a0-bec.js`, run id `wf_f07e20a0-bec`, and
completed agents replay from cache, of which there are none.

This is the second time this project has lost a workflow's deliverable to a limit. The first
is recorded in `docs/r10/connector_revision_AUDIT_d20.md`, where three agents died on a
monthly spend limit and took the synthesis stage with them. **The pattern is that the
synthesis stage dies last and takes the product with it.** A workflow that writes each
layer's result to disk as it completes would have survived both.

## A repeat of my own error, ten minutes after writing it into memory

Building the work-list, my first glob returned **0 files** for three layers that hold 2,818
files, because I globbed `<project>/subagents/...` when the real path has a session-uuid
level in between. I had written "a glob is not a walk" into memory in round 6 and then did
it again in round 7. The corrected work-list walks recursively: **4,031 files, 3.04 GB**
across 10 layers, at `~/can-it-ford-workflow-archive/WORKLIST.json`.

## Three named gaps closed inline

**1. The live Undermind workspace, re-queried.** Exactly **21 deep searches, all completed,
none created since 2026-08-19 17:47**. The count of 21 that every document carries is
current. Clean negative, and the gap named in round 6 is closed.

**2. Zotero, queried.** The library holds **28 items, 18 with a PDF, 10 without, 64.3
percent coverage**. Against a 332-record corpus and 4,388 DOIs on disk, the Zotero library
is not a corpus, it is a shortlist. Do not treat it as one.

**3. Vista `$WORK`, measured live.** **14 commits ahead of `origin/main` and 174 behind**,
with 4 modified tracked files including `CLAUDE.md`. The 14 are a `realism_track` series
carrying real physics with retractions in the messages: "the -50% is a reference artifact,
wrench is sound to ~8%", "deficit is a constant pressure offset; two claims retracted",
"artifact confirmed by measurement and by intervention", "mass-based head gives ~1% at g64;
g96 settle not reproducible", and `868302e` committing `validate_coupling_force.py`,
"untracked since first use". **Fourteen commits of physics exist only on Vista.**

## THE RESULT: a measured Yaris inertia tensor exists, and the solver already matches it

Zotero flagged `10.13021/G8JS5D`, the CCSA 2010 Yaris FE validation report, as **missing its
PDF**. That is the document `R10_FULL_CONTEXT_AUDIT_2026-08-19.md:330` names as refuting
`CLAUDE.md` item 4 leg (a). The PDF is on disk at
`~/Downloads/2010-toyota-yaris-coarse-validation-v1.pdf`, 5,035,861 bytes.

Read directly with `/opt/homebrew/bin/pdftotext -layout`, slide 7, "Inertia Comparisons":

```
                              Actual Vehicle    FE Model
    Weight, kg                     1078            1101
    Pitch inertia, kg-m^2          1498            1545
    Yaw inertia, kg-m^2            1647            1718
    Roll inertia, kg-m^2            388             396
    Vehicle CG X, mm               1022            1025
    Vehicle CG Y, mm                -8.3            -3.0
    Vehicle CG Z, mm                558             557
```

**`CLAUDE.md` item 4 leg (a) is false.** It reads: "It is not measured... No measured Yaris
tensor exists anywhere: SAE 1999-01-1336 ends Nov 1998." A measured tensor for an actual
2010 Yaris is printed on slide 7 of the very report the project cites as its own hull
provenance. This is now verified by me from the primary source, not relayed: the R10 audit's
quoted figures reproduce exactly.

**And the more useful half. Leg (b) is confirmed by an external anchor the project has never
had.** Item 4 leg (b) says the solver already computes a better tensor from the real hull
particle cloud, and leg (c) says the axes are transposed because the hull's long axis is Y.
Mapping accordingly, measured roll ↔ Iyy, pitch ↔ Ixx, yaw ↔ Izz:

| axis | measured | solver particle cloud | error | `vehicle_params` box | error |
|---|---|---|---|---|---|
| roll | 388 | **395.0** | **+1.8%** | 463.0 | +19.3% |
| pitch | 1498 | **1501.5** | **+0.2%** | 1893.0 | +26.4% |
| yaw | 1647 | **1685.4** | **+2.3%** | 1959.8 | +19.0% |

The measured vehicle is **1078 kg** against the project's canonical **1100 kg, +2.0%**, and
inertia scales roughly linearly with mass. **The residual is the mass difference.** After
that correction the solver's rigid-body representation agrees with a measured vehicle to
well under a percent, while the box fallback the code deliberately does not use is out by 19
to 26 percent.

CG height, same slide:

    measured CG Z              0.558 m   primary source
    solver particle-cloud CG   0.6312 m  +13.1%
    vehicle_params estimate    0.510  m   -8.6%
    hull bbox mid-height       0.7427 m  +33.1%

So the cloud CG is 13.1 percent high against measurement rather than "23.8 percent above the
0.51 m estimate", and the 0.51 m estimate is itself 8.6 percent low. A too-high CG biases
toward topple and the 17 runs show zero topples, so `CLAUDE.md`'s conservatism argument
survives, now against a measured number instead of an estimate.

**What should change, and it is three sentences, not a rewrite.** Item 4's conclusion, DO NOT
WIRE, is unchanged and now better supported. Only leg (a)'s stated reason is wrong. Replace
"no measured Yaris tensor exists anywhere" with: a measured tensor DOES exist, at
`10.13021/G8JS5D` slide 7, and the reason not to wire `vehicle_params.py` is that its numbers
are a box fallback 19 to 26 percent off that measurement, while the solver's own particle
cloud is within 2.3 percent before mass correction. **That turns item 4 from an argument from
absence into an argument from measurement**, which is strictly stronger and is the first
external anchor this project has for its rigid-body representation.

This is a correction to the corrections authority, so it belongs in the register and in
`CLAUDE.md` item 4, and both are files other sessions are live in. Not applied here.

---

# Round 8, 14:30 to 15:05 BST: deterministic mining instead of agents

Josie asked for whatever saves credits and is still thorough. The evidence said stop using
agents: attempt 1 burned **1,148,968 subagent tokens for 0 results**; attempt 2 burned 12
agents for **1 result**; and the one agent that did finish measured that **153 of 472 unique
workflow agents (32.4 percent) produce nothing and 109 are killed outright by account
limits**. Roughly 92 percent waste, before any project defect.

So the whole remaining read was done by a **deterministic miner**, no LLM in the loop:
`mine.py` streams every file line by line, scores every text block against finding-shaped
language, drops anything already in the merged corpus by content hash, and writes the top
blocks per layer. The script does the reading; tokens are spent only on what it surfaces.

**Result: 7,675 novel blocks from 4,031 files and 3.04 GB**, plus 30 of 73 PDFs carrying
signal. Full cost: a handful of Bash calls.

| layer | files | MB | novel blocks |
|---|---|---|---|
| `session_transcripts_87_worktrees` | 448 | 503.1 | **3,433** |
| `session_transcripts_main` | 293 | 502.9 | **1,843** |
| `wf_agent_transcripts` | 1,284 | 350.8 | **1,032** |
| `workflow_runfiles` | 15 | 3.9 | 392 |
| `inbox` | 97 | 527.6 | 368 |
| `tool_result_spills` | 1,490 | 351.5 | 204 |
| `r8_digests` | 128 | 8.4 | 180 |
| `downloads_reports` | 158 | 20.0 | 120 |
| `nonwf_agents` | 43 | 9.8 | 103 |
| `refs_pdfs` | 73 | 758.2 | 30 with signal |

The richest layer is the one nothing had ever read: **3,433 novel blocks from the 87 other
project directories.** Distillates are in `~/can-it-ford-workflow-archive/mined/`.

**Two bugs in my own miner, both caught by disbelieving a zero.** `workflow_runfiles` first
returned **0 novel blocks** for the deliverable layer, because a `.json` file is one object
and my paragraph splitter saw a single blob over the length cap; walking it as JSON gives
**392**. Earlier, three layers returned 0 because I globbed past the session-uuid level. In
both cases the zero was my predicate, not the data. **A zero from a tool you wrote is a
claim about the tool first.**

## THE FINDING THAT MATTERS MOST: a floating-point verdict flip, and the repo already fixed it

From `deliverables/paper/overleaf/sections/results.tex:7`: *"Four of the 70 cells flip on
binary floating point alone. The product 0.1 x 3.0 evaluates to 0.30000000000000004, which
spuriously exceeds a 0.30 cap unless the product is rounded to six decimals before the
comparison."*

Reproduced live:

    0.1*3.0            = 0.30000000000000004
    p > 0.30           -> True     spurious NO-FORD
    round(p,6) > 0.30  -> False    correct

Across a depth-velocity grid: **2 cells flip at the 0.30 cap, 0 at 0.45, 2 at 0.60** — four
in total across the three AR&R class caps, which is exactly the claimed count.

**And the canonical path is already protected.** `vehicle_params.py:239` and
`renders/yaris_render_s1/gates.py:29` both read
`if round(depth_m * velocity_ms, 6) > lim["haz_m2s"]`. This is a defence that is in place and
was never written down anywhere a reader would find it. It belongs in the register: the
verdict boundary is a product of two floats and must be rounded before comparison, or four
cells of the published phase space flip on representation alone.

## A finding that was REAL in its transcript and is FALSE now, which is the methodological result

A mined block quoted `README.md:80` as: *"compact_sedan | Toyota Corolla, Honda Civic | 1390
kg | measured, NHTSA SAE 1999-01-1336"*, contradicting the constitution's Yaris at 1100 kg.

Checked live: **README.md:61 now reads "Toyota Yaris (2010, NCAC/CCSA FE model) | 1100 kg |
4.30 x 1.70 x 1.47 | uniform-box fallback"**. The README was corrected at some point after
that transcript was written. **The mined block is historical, not current.**

That is the trap this whole layer carries: **every block the miner surfaces is what was true
when the transcript was written.** Nine layers of transcripts are nine layers of frozen past
state. Anything taken from them must be re-checked live before it is recorded as current,
and I nearly filed a stale contradiction as a live one.

## But checking it live surfaced a real one

`README.md:61` says **"uniform-box fallback (no NHTSA-measured Yaris)"** and, in the same
table cell, links `https://doi.org/10.13021/G8JS5D`.

That is the document whose **slide 7 prints the measured tensor**: 1078 kg, roll 388, pitch
1498, yaw 1647 kg m2, CG Z 558 mm, verified by me from the PDF in round 7. **The README cites
the document that refutes its own parenthetical, in the same sentence.** The same claim sits
in `CLAUDE.md` item 4 leg (a) and in `vehicle_params.py` note 3. Three files carry it; one of
them supplies its own refutation.

Correct wording for all three: not "no measured Yaris tensor exists", but "a measured tensor
exists at `10.13021/G8JS5D` slide 7; the box fallback here is 19 to 26 percent off it, while
the solver's own particle cloud is within 2.3 percent, so do not wire the box."

## Other verified items from the mine

- **`check_claims.py --all` returns 161 ERROR + 99 WARN = 260**, composition C9=72, C7=63,
  C1=44, C8=34, C12=13, C6=10, C2=10, C4=5, C14=4, C11=2, C3/C5/C13=1 each.
- **Line-number citation fragility, measured** in `friction-resolution-reconcile-84465d`:
  51 citation instances against one file, **18 cite line 14 (stable), 33 cite a line above 14
  and therefore shift whenever the file grows**. 22 distinct files cite it, 18 of them
  fragilely. This is the quantitative case for `CLAUDE.md`'s own "do not cite positionally"
  rule, and it is not recorded anywhere.
- **A live challenge to `CLAUDE.md` item 3** sits in `simulation/fork_scene/runner.py:101`:
  *"No engine patch is needed. CLAUDE.md item 3's word 'unconditionally' is wrong."* Item 3
  says `core/solver.py:167-169` hardcodes `g=[0,0,-9.81]` unconditionally. Unresolved.
- **`r8-kramer` reported its own bridge broken**: *"All three of your named attacks reproduce,
  two of them break the claim, and the fallback in 6.3 does not survive either."*
- **The PDF library's highest-signal papers** are Kramer 2016 trafficability criteria, Martinez
  2017, Pregnolato 2017, Riedmaier 2020 (V&V), Al-Qadami 2023 mesh-independence at 0.05 m
  cell, Jourdan 2020 SPH Neumann BC validation, an Anura3D `VerificationManual_2021`, Oberkampf
  2004 V&V, and the Kramer 2021 sphere-heave benchmark.

## What remains unread, stated plainly

The miner surfaces **blocks**, not conclusions. 7,675 blocks are now addressable and ranked,
and I have read roughly the top 90 of them. The remaining ~7,585 are triaged but unread. That
is a much better position than 3.04 GB of undifferentiated JSONL, and it is not the same as
having read them.

Also still true: the 768 base64 PDF page images (148.4 MB) inside the agent transcripts were
counted, never decoded; `refs_pdfs` was read to 12 pages per PDF; and no contamination check
separates DOIs belonging to unrelated work.

---

# Round 9, 14:35 to 15:20 BST: the citations checked mechanically

Round 8 left 7,675 ranked blocks that I could only read a fraction of. Rather than read on and
keep hitting the stale-state trap, I made the checking mechanical: extract every `file:line`
citation from every block and resolve it against the live tree. A script can do that for all
of them, which converts "is this block still true?" from a reading problem into an arithmetic
one.

**7,445 distinct `file:line` citations** across the ten mined layers.

## Two corrections to my own predicate, before any number

**First regex was leaky in both directions.** It matched mid-word, so `REFERENCE.md:151`
yielded a citation to a non-existent `ENCE.md`, and it dropped the leading slash on absolute
paths, so `/Users/josie/.claude.json` became `Users/josie/.claude.json` and never resolved.
It reported 7,279 citations and 2,154 absent files. With a proper left boundary and absolute
paths kept: **7,445 citations**. The leaky version was simultaneously inventing files and
losing real ones.

**First resolver tried only the repo root**, and called **2,217 instances unresolved**. Most
of the top hits were solver-relative: `kernels/mpm_solver_warp.py` (153), `core/solver.py`
(89), `kernels/mpm_utils.py` (83). Those resolve inside the vendored solver or the pinned
venv. Trying the real root set:

    1,842  instances first called unresolved
      923  resolve once solver, venv and repo subdirectory roots are tried
      919  genuinely resolve nowhere

**A bare "unresolved citations" count without its root set is the same error class as a bare
DOI count without its method.** I made it, and the corrected split is above.

## The result, against the live tree

    7,445  distinct file:line citations in the mined blocks
    5,204  resolve at the repo root
      923  resolve under the solver, venv or a repo subdirectory
      919  resolve nowhere: Vista paths, Genesis, deleted worktrees
       24  point at a REAL file, at a line that no longer exists

**The 24 are the project's own positional-citation rule, made concrete and current.**
Thirteen of them point into `SESSION_STATE.md` at lines 111 to 302. That file is **108 lines**
today, last committed `b62d554` on 2026-08-13. Every one of those citations is dead, and they
were made from five different layers: `inbox`, `tool_result_spills`, `wf_agent_transcripts`,
`session_transcripts_main` and `session_transcripts_87_worktrees`. Three more point past the
end of `README.md`, which is now 183 lines. Three point into `.remember/now.md`, which is
**zero lines**.

`CLAUDE.md` opens by forbidding positional citation of itself, and gives the reason: the file
changes several times a night, so a line number is stale on arrival. **The same failure is
measurable across the whole corpus, and `SESSION_STATE.md` is where it concentrates.** Nothing
had counted it.

## A relayed claim corrected: `sphere_heave.py` is not at risk

The round-1 workflow critique said *"sphere_heave.py, the file behind the force-accessor
factor-of-two question that Slot 4 exists to resolve, exists only under `.claude/worktrees/`."*
Twenty-six citations in the mined corpus point into
`.claude/worktrees/r5-physics/simulation/r5_physics/sphere_heave.py`, and **that worktree is
gone**: not in `git worktree list`, and the directory is absent from disk.

But the file is fine. Measured:

- it is committed on `claude/r5-physics` **and on `origin/claude/r5-physics`**, so it is pushed
- it is present in five live worktrees: `r8-force`, `r8-kramer`, `r9-accessor`,
  `r9-jobb-route`, `r9-kramer-extract`

So the file behind the Job B force-accessor question is **on the remote and in five working
trees**. "Exists only under `.claude/worktrees/`" was true of the main checkout's working tree
and false as a statement about risk. The 26 dead citations are a stale *path*, not a lost file.

## What this leaves

`~/can-it-ford-workflow-archive/CITATION_CHECK.json` holds all 7,445 citations classified,
the 24 dead ones with their current file lengths, the 919 unresolvable paths with counts, and
the resolver correction. It is re-runnable: the same script against a later tree gives a later
answer, which is what the positional-citation problem needs.

Still unread: the block *text* below the top ~90. The citations inside all 7,675 blocks are
now checked; the prose around them is not.
