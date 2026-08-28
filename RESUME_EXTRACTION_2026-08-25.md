# Resume and LinkedIn extraction, Can It Ford, 2026-08-25

Every number below was produced by running a command in this session against the live
working tree, or by reading the live bytes of a named file. Nothing is carried from a
session summary, a memory file, or a prior audit's conclusion.

**Tagging, used on every claim:**

- **[CONFIRMED]** I ran the command in this session and saw the output.
- **[ESTIMATED]** I inferred it. The inference is stated so you can check it.
- **[DOC]** Read from a project document, not re-derived live in this session. A document
  is not a live fact. Treated as weaker than CONFIRMED throughout.
- **[UNVERIFIABLE HERE]** Could not be checked from this machine in this session. Chat, or
  a live login, has to cover it.

**One standing caution.** The shell `grep` in this environment is ugrep with `--ignore-files`
and skips gitignored paths. Every inventory command below used `/usr/bin/grep`,
`git ls-files`, or `git ls-tree`, never the shell `grep`. Counts are therefore auditable.

---

## 0. Orientation

**Working directory** `/Users/josie/can-it-ford`. **[CONFIRMED]**
`git rev-parse --show-toplevel` returns the same path, and `git rev-parse --git-dir`
returns `.git` as a real directory, so this is the **main checkout, not a worktree**.

**Branch** `claude/add-ci-checks`, HEAD `0845e1c8d8a5a4cafa9a3a0e6dbcdc5c72697883`. **[CONFIRMED]**
**This is not `main`.** That distinction runs through the whole document and changes
several public-facing numbers.

**Tree is dirty:** 16 tracked files modified, plus a large untracked set. **[CONFIRMED]**

### Copies of this repo on this machine

`git worktree list` returns **11 worktrees** (1 main checkout, 4 sibling clones registered
as worktrees, 6 under `.claude/worktrees/`). **[CONFIRMED]**

`find` over `/Users/josie` also returns **17 files named CLAUDE.md** and **21 named
SESSION_STATE.md**. **[CONFIRMED]**

### Which copy is canonical

Provenance was established by **git blob hash**, not by modification date or size, and
computed with `git hash-object --path=CLAUDE.md` so the repo's `text=auto` normalization
is applied. Result: **[CONFIRMED]**

| Copy | Lines | mtime | Blob |
|---|---|---|---|
| **`/Users/josie/can-it-ford/CLAUDE.md`** | **1046** | 2026-08-25 04:18 | `0e23188a` |
| `HEAD:CLAUDE.md` (committed) | 1022 | n/a | `e31e7018` |
| `can-it-ford-warpmpm-continue` | 700 | 2026-08-12 | `8e87caa1` |
| `Downloads/can-it-ford-main` | 676 | 2026-08-13 | `37983d25` |
| `can-it-ford-realism` | 603 | 2026-08-12 | `f5b4054b` |
| `can-it-ford-BACKUP-2026-08-11` | 544 | 2026-08-11 | `1da8c85f` |
| `can-it-ford-moving-vehicle` | 538 | 2026-08-11 | `23174e2a` |
| `can-it-ford-visual-trial` | 538 | 2026-08-11 | `23174e2a` |
| `can-it-ford-audit/2026-08-04/dl` | 49 | 2026-08-04 | `ebf2b5ad` |
| `can-it-ford-BACKUP-before-history-purge` (x2) | 41 | 2026-07-23 | `aab2fd2d` |

**Canonical: `/Users/josie/can-it-ford/CLAUDE.md`, 1046 lines.** It is the longest and the
newest, and every other copy is a strict predecessor. **[CONFIRMED]**

**Caveat that matters:** the canonical file **differs from its own committed version** by
24 lines. Those 24 lines exist only in the working tree. **[CONFIRMED]**

**Do not trust `SESSION_STATE.md`.** The canonical copy has mtime 2026-08-13 14:44, while
the last commit is 2026-08-25 20:53. It is **12 days stale** relative to the repo it
describes. **[CONFIRMED]** Nothing in this document is sourced from it.

---

## 1. Repo hygiene and GitHub-facing facts

### Remote

```
origin    https://github.com/jcerrell-IS/can-it-ford.git   (fetch and push)
overleaf  https://git@git.overleaf.com/6a5958d10484feadf65a934e   (fetch and push)
```
**[CONFIRMED]**

### Commit counts, and the gap that matters most

| Measure | Value |
|---|---|
| Commits reachable from HEAD (`claude/add-ci-checks`) | **867** |
| Commits reachable from `origin/main` | **396** |
| HEAD ahead of `origin/main` | **471** |
| HEAD behind `origin/main` | **0** |
| First commit | 2026-07-01 |
| Last commit | **Tue Aug 25 20:53:02 2026 +0100** |
| Commits in July 2026 | 255 |
| Commits in August 2026 | 612 |

All **[CONFIRMED]**.

**Read this before quoting a commit count.** 867 is the work. 396 is what a visitor to
the default branch sees. **The 471-commit difference is not unpushed:** `git ls-remote`
confirms `refs/heads/claude/add-ci-checks` on GitHub is at exactly `0845e1c`, the local
HEAD, and the remote carries **92 branches**. **[CONFIRMED]** So the work is published,
it is just not on `main`. If a resume says "867 commits", that is true and defensible.
If a recruiter opens the repo's default branch they will count 396.

### Authorship

| Author string | Email | Commits |
|---|---|---|
| Josephine Cerrell | jcerrell29@students.claremontmckenna.edu | 531 |
| Josie Cerrell | jcerrell29@students.claremontmckenna.edu | 287 |
| Josie Cerrell | jcerrell29@cmc.edu | 29 |
| Josie Cerrell | josiecerrell69@gmail.com | 7 |
| **Your Name** | josiecerrell69@gmail.com | **5** |
| Josie Cerrell | jcerrell0629@login1.ls6.tacc.utexas.edu | 4 |
| Josie Cerrell | jcerrell0629@c301-003.ls6.tacc.utexas.edu | 4 |

**[CONFIRMED]**

**All 867 commits are yours.** There is no second human contributor. The seven identity
strings are one person across an unset git config, two machines, and three email
addresses. **[CONFIRMED]**

On the "me vs Claude Code" question: **git attributes 100 percent of commits to you.**
Separately, **28 commits carry a `Co-Authored-By: Claude` trailer** and 11 mention
"Claude Code" in the message body. **[CONFIRMED]**

**The 5 "Your Name" commits are all dated 2026-07-01**, including `4bd2967 Can It Ford
initial commit`. **[CONFIRMED]** That is an unset `git config user.name` on day one.
Cosmetic, but it means the repo's own first commit is not attributed to you by name.

### Licences: the three-way split is resolved locally and NOT resolved publicly

Only **one** `LICENSE` file exists in the tree (excluding `third_party/`). **[CONFIRMED]**

| Where | Code licence | Data licence | Scope clause |
|---|---|---|---|
| Working tree / `claude/add-ci-checks` | BSD 3-Clause | **CC-BY-4.0** (`CITATION.cff:17`) | **Present** |
| **`origin/main` (what the public sees)** | BSD 3-Clause | **ODC-By-1.0** (`CITATION.cff:12`) | **Absent** |
| HF datasets (x2), HF model, HF Space | n/a | `cc-by-4.0` | n/a |
| GitHub API `licenseInfo` | `bsd-3-clause` | n/a | n/a |

All **[CONFIRMED]**, the HF values read live from `huggingface.co/api`.

**Definitive answer.** The ODC-BY / BSD / CC-BY three-way split **has been settled, to
CC-BY-4.0 for data and BSD-3-Clause for code, but the fix has not reached `main`.**
`origin/main:CITATION.cff` still reads `ODC-By-1.0` while all four Hugging Face repos
read `cc-by-4.0`. **The public repo and the public datasets currently disagree with each
other about the data licence.** **[CONFIRMED]**

**What each file covers, read live:**

- `LICENSE` (working tree) opens with a **SCOPE** paragraph: BSD 3-Clause covers
  "the original code and documentation authored for this project" and explicitly does
  **not** cover redistributed third-party material. **[CONFIRMED]**
- That scope paragraph and its closing pointer are the **only** difference from the
  `origin/main` version, which is a bare BSD 3-Clause with no scope statement. **[CONFIRMED]**
- `THIRD_PARTY_NOTICES.md` (17,317 bytes) carries the per-asset inventory. It is
  **absent from `origin/main`**. **[CONFIRMED]**

**The genuinely open licence item is not the three-way split, it is upstream.**
`THIRD_PARTY_NOTICES.md` marks **UNRESOLVED**, meaning no permission established:

| Asset | Holder | Status |
|---|---|---|
| CCSA/GMU FE vehicle models (4) | CCSA at George Mason, FHWA-sponsored | UNRESOLVED, "the most significant unresolved item in this repository" |
| Derived Yaris hull and other `.ply` | derived from the above | UNRESOLVED, inherited |
| AR&R Project 10 Stage 2 report | Engineers Australia | UNRESOLVED, 2 routes tried |
| AR&R Table 1 image | Engineers Australia | UNRESOLVED, inherited |
| WRL Technical Report 2014/07 figures (3) | Water Research Laboratory, UNSW | UNRESOLVED, 4 routes tried |

**[CONFIRMED]** by direct read. The notices file records **20 reproduced images totalling
7,213,546 bytes** across four distinct third-party sources.

`README.md:168` additionally records that **PhysGaussian has no detected licence**, and
that any PhysGaussian-derived bridge code must be resolved before commit or DesignSafe
submission. **[CONFIRMED]**

### README

**Yes, it has a real one-line description at the top.** Line 3 reads:
*"Autonomous vehicle flood traversability via reconstruct-to-decide world models"*. **[CONFIRMED]**
184 lines total.

| Link | In working-tree README | In `origin/main` README |
|---|---|---|
| Hugging Face Space (live demo badge) | **Yes**, line 7 and line 175 | **No.** `origin/main` contains no "huggingface" string at all |
| W&B project | Yes, line 6 | Yes |
| BSD-3-Clause badge | Yes, line 5 | Yes |
| **Vercel demo** | **No** | **No** |

All **[CONFIRMED]**. `origin/main:README.md` is 183 lines, working tree is 184; the one
added line is the Hugging Face badge.

**The Vercel demo is live and the README never mentions it.** `vercel.json` is tracked and
present on `main` (serving `outputDirectory: "web"`), the GitHub `homepageUrl` field is set
to `https://can-it-ford.vercel.app`, and that URL returns **HTTP 200** with
`<title>Can It Ford?</title>`. **[CONFIRMED]** So the deployment works, is wired as the repo
homepage, and is invisible to anyone reading the README.

### Live GitHub metadata

From `gh repo view --json ...`, `gh` authenticated as **jcerrell-IS**. **[CONFIRMED]**

```json
{
  "description": "",
  "repositoryTopics": null,
  "stargazerCount": 0,
  "forkCount": 0,
  "watchers": 0,
  "isPrivate": false,
  "visibility": "PUBLIC",
  "defaultBranchRef": "main",
  "homepageUrl": "https://can-it-ford.vercel.app",
  "licenseInfo": "bsd-3-clause",
  "createdAt": "2026-07-01T07:32:19Z",
  "pushedAt": "2026-08-25T19:53:04Z"
}
```

**Three things to fix before anyone is pointed at this repo:**

1. **`description` is the empty string.** The repo has no GitHub description at all.
2. **`repositoryTopics` is `null`.** No topics, so it is unfindable by search.
3. Stars 0, forks 0, watchers 0. The repo is public but has had no traffic.

All **[CONFIRMED]**. Items 1 and 2 are one-line fixes and are the highest-value cosmetic
work available: the README already contains a good description that has never been copied
into the field GitHub actually shows in search results and link previews.

### Open issues and PRs

**[CONFIRMED]** via `gh`:

- **2 open issues.** #6 vehicle geometry unresolved (car_mesh.ply scale, truck gsplat not
  bridged into particles); #5 `DRIFT_THRESHOLD = 0.05 m` hardcoded but not linked to its
  citation reframing.
- **5 closed issues.**
- **2 open PRs.** #15 `refresh_bib_from_zotero.sh` (open since 2026-08-18); #9 mark
  `paper/conference_101719.tex` superseded (open since **2026-07-31**, roughly 4 weeks).

### Lines of code

`cloc`, `tokei`, and `scc` are **not installed** on this machine. **[CONFIRMED]** Counted
instead with `git ls-files` / `git ls-tree` piped to `wc -l`, which excludes untracked
files, venvs, and build output by construction. `third_party/` excluded explicitly.

**On HEAD (`claude/add-ci-checks`), tracked:** **[CONFIRMED]**

| Language | Files | Lines |
|---|---|---|
| **Python** | **242** | **61,889** |
| HTML | 7 | 16,164 |
| Shell | 60 | 4,996 |
| YAML (`.yaml`) | 1 | 1,030 |
| LaTeX | 2 | 517 |
| YAML (`.yml`) | 6 | 472 |
| **Total** | **318** | **85,068** |

**On `origin/main`, tracked:** **[CONFIRMED]** Python 144 files / 28,114 lines; HTML 7 /
16,164; Shell 33 / 1,722; LaTeX 2 / 517; `.yml` 4 / 416. **Total 46,933.**

**Do not quote the HTML as code.** 4 of the 7 HTML files are **3,887 lines each and are
near-identical Plotly dumps** (`phase_space_interactive.html`,
`phase_space_interactive_JOINTRULE.html`, `poster_exports/can_it_ford_phase_space.html`,
`phase_space_poster_figure_JOINTRULE.html`). That is **15,548 of the 16,164 HTML lines
generated and duplicated fourfold.** **[CONFIRMED]** Counting it as authored code would
inflate the figure by roughly 18 percent.

**The defensible headline is Python.** 61,889 lines across 242 tracked files, distributed
across real modules rather than concentrated in generated output: **[CONFIRMED]**

| Directory | Files | Lines |
|---|---|---|
| `analysis/` | 112 | 31,484 |
| `simulation/` | 35 | 13,637 |
| `.claude/` (hooks, checks, skills) | 20 | 4,094 |
| `scripts/` | 26 | 3,934 |
| `hf_space/` | 5 | 1,525 |
| `docs/` | 11 | 1,254 |
| `renders/` | 2 | 1,076 |
| `tests/` | 4 | 933 |
| others (`realism_track`, `citations`, `bridge`, `designsafe-staging`, root, ...) | 27 | ~3,952 |

Largest single files: `analysis/research_index.py` 2,282 lines,
`analysis/kramer_extract_numerical.py` 1,936, `simulation/moving_vehicle_channel.py` 1,298.
**[CONFIRMED]**

**Also on disk but with no git history: 23 untracked `.py` files, 3,558 lines.** **[CONFIRMED]**
Most are in `renders/yaris_render_s1/` and include the gate scripts (`gates.py`,
`gates_all_runs.py`, `gates_both_scenarios.py`). **These have no provenance.** Do not
include them in a LOC claim, and do not cite them as having a commit history.

### Repo size on disk

`du -sh` **[CONFIRMED]**: whole checkout **9.3 GB**, of which `renders/` 3.6 GB,
`_inbox/` 504 MB, `vehicle_geometry_research/` 430 MB, `render_s2/` 165 MB,
`data/` **123 MB**, `deliverables/` 114 MB, `figures/` 81 MB.

---

## 2. Compute and scale

### Job geometry: single node, single GPU, every time

**27 Slurm batch scripts** in the main tree (worktree duplicates excluded). **[CONFIRMED]**
`#SBATCH` directives read from all 27.

**Every single one specifies `-N 1 -n 1`.** **[CONFIRMED]** There is no multi-node job in
this repository. **Do not describe this work as multi-node or distributed HPC.** The
accurate phrasing is single-GPU jobs on two national systems.

| Partition | System | Hardware | Scripts |
|---|---|---|---|
| `gh`, `gh-dev` | **TACC Vista** | NVIDIA **GH200** Grace Hopper | 19 |
| `gpu-a100-dev` | **TACC Lonestar6** | NVIDIA **A100** | 8 |

Allocation **BCS20003** on both. **No Frontera usage appears anywhere.** **[CONFIRMED]**

Requested walltimes range **00:20:00 to 06:00:00**, median 02:00:00. **[CONFIRMED]**

### Wall-time, job outcomes, and SU spend: MEASURED LIVE

**Upgraded from [DOC] to [CONFIRMED] at 21:5x on 2026-08-25.** The SSH control sockets were
opened, both systems answered, and every figure below was read from the live cluster in this
session. The earlier doc-sourced figures are kept underneath for comparison.

**Allocation balances, read live from `/usr/local/etc/taccinfo`:** **[CONFIRMED]**

| System | Project | Avail SUs (live, 2026-08-25) | Was, 2026-08-22 [DOC] | Expires |
|---|---|---|---|---|
| **Vista** | BCS20003 | **552** | 581 | 2026-09-30 |
| **LS6** | BCS20003 | **9536** | 9536 | 2026-09-30 |

Vista dropped 29 SU in three days. LS6 did not move. **Vista remains the binding constraint**
and is the only machine with the warpmpm/GH200 path.

**August job accounting, computed live from `sacct -A BCS20003 --allusers -S 2026-08-01`:** **[CONFIRMED]**

| System | Jobs | Node-hours | COMPLETED | TIMEOUT | CANCELLED | FAILED |
|---|---|---|---|---|---|---|
| **Vista** | **155** | **66.58** | 90 | 30 | 31 | 4 |
| **LS6** | **46** | **73.16** | 15 | 15 | 14 | 2 |
| **Total** | **201** | **139.74** | **105** | **45** | **45** | **6** |

Partitions actually used, live: Vista `gh` 88, `gh-dev` 64, `gg` 2, `gb` 1. LS6
`gpu-a100-dev` 29, `development` 10, `gpu-a100` 5, `gpu-a100-small` 1, `normal` 1. **[CONFIRMED]**
Note that `gg`, `gb`, `development`, `gpu-a100-small` and `normal` appear in the accounting but
in **none** of the 27 committed sbatch scripts, so a meaningful share of jobs was launched
interactively or from scripts that were never committed.

**The completion rate is the number to be careful with. Only 105 of 201 August jobs
COMPLETED, which is 52.2 percent.** 45 timed out and 45 were cancelled. **[CONFIRMED]**
Do not describe this as 201 successful runs. The defensible phrasing is "201 cluster jobs
submitted across two systems, 105 completed". The 30 Vista timeouts are consistent with
the oversized-walltime problem already recorded in project memory.

**Reconciliation against the 2026-08-22 audit [DOC]:** that pass measured Vista 64.58 and
LS6 72.66 node-hours by `sacct`, against **66.58 and 73.16 live today**. Both grew slightly,
by 2.00 and 0.50 node-hours over three days, which is the expected direction and magnitude.
**The two independent measurements agree**, so the August node-hour figures are corroborated
rather than single-sourced.

The billed-SU figures (Vista 79.80, LS6 146.19, 225.99 total) remain **[DOC]** from the
2026-08-22 audit: `sreport` was not re-run in this session, and node-hours are not SUs
(charge rates differ per partition).

Also confirmed live and worth acting on: **Vista `/home1` is at 90.78 percent of quota**
(21.1 of 23.3 GB), and `taccinfo` prints an explicit warning about it. **[CONFIRMED]**

### Simulation runs and scenarios

| Count | Value | Source |
|---|---|---|
| **Canonical gated MPM runs** | **17** | `data/all_runs_inventory.csv`, 17 data rows, 42 columns |
| `metrics.csv` files on disk under `renders/` | **30** | filesystem |
| `summary.json` on disk | 28 | filesystem |
| `rollout.npz` on disk | 27 | filesystem |
| **L1 analytical sweep conditions** | **70** | `data/scenario_sweep.csv`, 70 data rows, 10 columns |
| Distinct run output trees under `renders/` | 11 | filesystem |
| **W&B runs logged** | **108** | live GraphQL query against `api.wandb.ai` |

All **[CONFIRMED]**. The W&B figure was queried live in this session, not recalled.

The 17 canonical run ids, read live: `g48_m1100`, `g48_m1609`, `g48_m2337`, `g64_m1100`,
`g64_m1609`, `g64_m2337`, `g96_m1100`, `g96_m1609`, `g96_m2337`, `sweepD_g64_d0p25`,
`sweepD_g64_d0p35`, `sweepD_g64_d0p45`, `sweepV_g64_v0p5`, `sweepV_g64_v1p0`,
`sweepV_g64_v2p0`, `sweepV_g64_v2p5`, `sweepV_g64_v3p0`. **[CONFIRMED]** That is a 3x3
grid-by-mass factorial plus a 3-point depth sweep plus a 5-point velocity sweep.

**30 on disk against 17 canonical is not a contradiction:** the extra trees are
exploratory (`hullsweep`, `multigeom`, `openchannel`, `r9_cycles`, `track1_fullscale`).
Only the 17 are gated. **Claim 17, not 30.** **[CONFIRMED]**

### Solver configuration and particle counts

Read directly from all 17 rows of `data/all_runs_inventory.csv`. **[CONFIRMED]**

| Parameter | Value(s) across the 17 runs |
|---|---|
| `n_grid` (grid_density) | **48, 64, 96** (3 levels) |
| `dx` | 0.19629, 0.14721, 0.09814 m |
| **Water particles per run** | **18,194 to 180,067** (6 distinct) |
| **Vehicle particles per run** | **3,846 / 8,905 / 29,804** |
| Realized depth | 0.2208, 0.2944, 0.3680, 0.4416 m |
| Vehicle mass | 1100, 1609, 2337 kg |
| Inflow velocity | 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 m/s |
| Frames | 90, all runs |
| Substeps | 8, 11, 16 |
| **Sound speed** | **12.84523257866513 m/s, identical in all 17** |
| Bulk modulus | 1.5e5 Pa, all runs |
| Water viscosity | 1.0e-3, all runs |
| Floor friction | 0.55, all runs |
| Realized vehicle density | 302.55 to 663.58 kg/m3 |
| Max particle passthrough | 7.34 to 15.88 percent |

**Aggregate particle count across the 17 runs: 1,151,002 water + 198,905 vehicle =
1,349,907 particles.** **[CONFIRMED]** This is a sum across runs, **not** a single
simulation's size. The **largest single run is 180,067 water particles**. If a resume
needs one number, use 180,067 for the largest simulation, or "1.35 million particles
simulated across a 17-run gated study" if you want the aggregate. Do not let the two blur.

### Results and quality metrics

- **Failure-mode verdicts: 16 SLIDE, 1 STUCK** across the 17 runs, from
  `data/failure_modes_by_run_classified.csv`. **[CONFIRMED]** These are
  **threshold-dependent** (`slide_m=0.05 m`, `slide_speed_ms=0.05 m/s`, `float_m=0.05 m`,
  `sustain_frames=3`), so quote the thresholds with the count.
- **L1 FORD counts out of 70 conditions: 14 small passenger, 19 large passenger, 26 large
  4WD.** **[DOC]**, from `README.md`, backed by the live 70-row `scenario_sweep.csv`. **[CONFIRMED]**
- **Physics gate test suite: 11 pass, 0 fail, 1 skip.** `tests/test_physics_gates.py` run
  live. **[CONFIRMED]** The skip is real and is reported by the suite itself: no solver
  Poiseuille profile exists at `tests/data/poiseuille_profile.csv`, so the analytical side
  is verified and the solver comparison is **not**. The suite prints
  "SKIPS ARE NOT PASSES".
- **Research corpus index: 382 papers, 211 with abstracts, 164 cited, across 25 method
  axes.** `analysis/research_index.py --stats`, run live. **[CONFIRMED]**
- **Paper: 14 distinct `\cite` keys** in `conference_101719_1.tex` on `overleaf/main`,
  with 7 figure files alongside it. **[CONFIRMED]** Overleaf `main` last updated
  2026-08-23.
- **Gaussian splat training (drainA scene, LS6):** PSNR **22.7356**, SSIM **0.8249**,
  LPIPS **0.3112**, **399,491** Gaussians on rank 0 and **1,147,694** summed across 3 rank
  shards, at 30k steps, trained 2026-07-20. **[DOC]**, from
  `docs/CONTEXT_CENSUS_2026-08-07.md`, which records these as read live from LS6 at the
  time. **Not re-verifiable from this machine today** (LS6 socket cold). PSNR 22.74 is
  moderate rather than strong for a static scene; the project's own notes say so.
- **Hugging Face, read live from the API this session** **[CONFIRMED]**: Space
  `josiecerrell/can-it-ford` (gradio, **HTTP 200, live**, 0 likes); datasets
  `can-it-ford-sweep-v1` (**23 downloads**) and `can-it-ford-speed-surface`
  (**50 downloads**); model `can-it-ford-sweep-v1`.

### CI

**[CONFIRMED]** `.github/workflows/` holds 4 workflows: `canford-checks.yml`,
`csv-check.yml`, `physics-consistency-review.yml`, `sync-to-hub.yml`.

`gh run list` shows **12 of the last 12 `canford-checks` runs completed successfully**,
all on `claude/add-ci-checks`, most recent 2026-08-25T19:53, typical duration 19 to 38
seconds. **[CONFIRMED]**

**Two caveats, both confirmed by reading the workflow file:**

1. **`canford-checks.yml` is absent from `origin/main`.** **[CONFIRMED]** It runs on push
   from branches, so "CI is green" is true; "CI protects the default branch" is not.
2. **Two of its six steps carry `continue-on-error: true`** (`register_integrity` at line
   22, `count_claims` at line 25). **[CONFIRMED]** A green badge does not mean those two
   passed. Run locally in this session, both in fact report **0 blocking defects**, so
   they are currently clean, but the badge would be green either way.

Local run of the full check stack in this session **[CONFIRMED]**:

| Check | Result |
|---|---|
| `params_check.py` | **exit 0**, no blocking issues, **11 warnings** |
| `count_claims_check.py` | **0 blocking defects**, 27 assertions classified |
| `register_integrity.py` | **0 blocking defects**, 3 unresolved-hex warnings; 209 register items, 10 sections, 14 of 75 hex tokens unresolved, 17 of 82 paths unresolved |
| `tests/test_physics_gates.py` | **11 pass, 0 fail, 1 skip** |
| `analysis/research_index.py --stats` | parses, 382 papers |

---

## 3. Known open items, each checked live

### 3.1 Hardcoded vehicle box in the L2 MPM script: **STILL HARDCODED**

**[CONFIRMED]** by direct read of `simulation/can_it_ford_L2_mpm.py`:

```
:26   VEHICLE_SIZE          = (4.66, 1.79, 1.44)
:27   VEHICLE_RHO           = 115.7
:80   half   = np.asarray(VEHICLE_SIZE) / 2.0
:159  size=VEHICLE_SIZE,
```

Unchanged. The box is 4.66 x 1.79 x 1.44 m against the real hull's canonical volume of
3.542739 m3.

**Important nuance, and it changes how you describe this.** `params_check.py` classifies
this file as **"known abandoned Track 2 file, not blocking"**. **[CONFIRMED]** from the
live check output. So this is **not an unfixed defect in the production path**; it is a
defect in an abandoned script that the 17 gated runs never touch. The canonical driver is
`renders/yaris_render_s1/sim_standing.py`, which loads the real watertight hull.

**Accurate framing:** "a superseded standalone script retains a box proxy; the gated
pipeline uses the real hull." **Inaccurate framing:** "the simulation uses a hardcoded box."

### 3.2 Water sound-speed anomaly: **OPEN, and it is a disclosed limitation, not a bug**

**[CONFIRMED]** by three independent live checks in this session:

1. **All 17 canonical runs record `sound_speed_ms = 12.84523257866513`.** Read from
   `data/all_runs_inventory.csv`. Zero variance.
2. **The value is derived, not typed.** `renders/yaris_render_s1/sim_standing.py:225`
   computes `c = float(np.sqrt(1.1 * bulk_modulus / water_density))`. I evaluated
   `sqrt(1.1 * 1.5e5 / 1000)` and got **12.84523257866513**, matching the stored value
   to all 14 digits. So the sound speed is a consequence of `bulk_modulus = 1.5e5`, and
   changing it means changing the bulk modulus.
3. Against real water at ~1480 m/s, this is **115.2x low**. (The corrections register says
   "about 118x", which corresponds to a ~1516 m/s reference. The discrepancy is in the
   reference value, not the measurement.)

**I re-derived the project's own headline claim rather than repeating it.** Computing
`c / v_max` per run from the primary CSV: **15 of 17 runs fall below the 10x convention.**
This reproduces register item B8 exactly, from the data file rather than from the register.
**[CONFIRMED]**

| Runs | Ratio |
|---|---|
| `sweepV_g64_v3p0` | **4.28** (worst) |
| `sweepV_g64_v2p5` | 5.14 |
| `sweepV_g64_v2p0` | 6.42 |
| the other 12 violating runs (all at v = 1.5 m/s) | 8.56 |
| `sweepV_g64_v1p0` | 12.85 (passes) |
| `sweepV_g64_v0p5` | 25.69 (passes) |

**Status: not resolved, not abandoned. Carried as a disclosed limitation with a live
automated gate.** `params_check.py` emits `[lit:sound_speed_cfl]` on every run naming the
worst case. **[CONFIRMED]** The register's position, **[DOC]**, is that the criterion comes
from Zhao et al. 2019 citing Liang, is valid for their setup, and is not independently
validated as a hard requirement for this EOS and geometry, so it is a disclosed limitation
rather than evidence the results are wrong. It does not change the grid-invariance of the
binary verdict.

**One correction to the framing in the request.** A weakly-compressible solver using an
artificial sound speed is standard practice, not an anomaly. What is open is narrower and
more interesting: **the artificial sound speed was never swept**, so its influence on the
verdicts is unmeasured. The register ranks that sweep as **the second-highest-value
outstanding experiment**, and names artificial sound speed alongside `COLLIDER_FRICTION
0.4` as the project's largest class of unexamined parameter: **inherited defaults that
materially control a reported result.** **[DOC]**

The session-start banner claims "sound-speed sweep is DONE, jobs 895330 and 895378". I
could not corroborate that: `docs/R5_PHYSICS_SKEPTIC_CORRECTIONS.md:207` says only that
the sound-speed **caveat does not reference** those completed sweeps, and the canonical
17 runs all still carry the single unswept value. **Treat "the sweep is done" as
unconfirmed** until someone produces its results. **[CONFIRMED that I could not corroborate it.]**

### 3.3 Licence conflict

Covered in full in Section 1. **Resolved on-branch (CC-BY-4.0 data, BSD-3-Clause code with
a scope clause), not yet on `origin/main`, which still publishes ODC-By-1.0.** The
substantive open item is the five UNRESOLVED third-party assets, above all the CCSA/GMU FE
vehicle models and the hull derived from them. **[CONFIRMED]**

### 3.4 Other TODO / FIXME / known-issue markers

**Zero.** A `/usr/bin/grep` for `TODO|FIXME|XXX:|HACK|KNOWN ISSUE|NOT FIXED|BUG:` across
all **302 tracked `.py` and `.sh` files** (excluding `third_party/`) returns **0 matches**.
**[CONFIRMED]**

That is a genuinely clean result and worth stating, but read it correctly: **this project
does not track known issues in code comments.** They live in `CLAUDE.md`, in
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` (3,604 lines, 209 items, 10 sections),
and in GitHub issues. A zero here is not evidence of no known issues.

**Known issues that are live, from those sources:**

| Item | Status | Source |
|---|---|---|
| 15/17 runs below the 10x sound-speed convention | open, gated, disclosed | live `params_check` **[CONFIRMED]** |
| Grid study non-monotone, apparent order `p` not computable, no GCI band | open, gated | live `params_check` **[CONFIRMED]** |
| 17/17 runs: solid volume exceeds tolerance (fill_ratio 1.0023) | open, gated | live `params_check` **[CONFIRMED]** |
| Manifest provenance gaps across 67 manifests (`solver_git_sha` missing in 23, `mesh_sha256` missing in 23, `grid_density` missing in 23) | open, gated | live `params_check` **[CONFIRMED]** |
| `settle_frames=8` contradicted by all 25 audited runs (min 29 needed) | open | `CLAUDE.md` **[DOC]** |
| Solver Poiseuille comparison never run | open | live test suite skip **[CONFIRMED]** |
| Vehicle geometry: truck gsplat not bridged to particles | open | GitHub issue #6 **[CONFIRMED]** |
| `DRIFT_THRESHOLD` 0.05 m hardcoded, unlinked to citation | open | GitHub issue #5 **[CONFIRMED]** |
| **No gsplat reconstruction has ever entered a simulation** | open | `docs/POSTER_AND_PIPELINE_STATUS_2026-08-25.md` **[DOC]**, and README says so **[CONFIRMED]** |
| Overleaf credential off local disk but **not revoked** | open | `CLAUDE.md` **[DOC]** |
| 3 unresolved hex tokens cited in the register | open | live `register_integrity` **[CONFIRMED]** |

**The one that most affects how you describe this project publicly:** the reconstruct-to-decide
front end is **designed and not built**. `README.md` states it plainly at line 17: every
result in the repo and the paper starts from a watertight mesh and a parameterized flood
condition, **not from a splat**. **[CONFIRMED]** The gsplat reader is wired
(`vehicle_live.py:184`, `:221`) and has never been fed a splat. **[DOC]** Describe the
splat pipeline as trained and validated in isolation (PSNR 22.74), and the simulation as
mesh-driven. Do not describe an end-to-end video-to-verdict pipeline.

### 3.5 Nothing else changed as of right now

Both flagged items (3.1 hardcoded box, 3.2 sound speed) are **unchanged in the code**.
Neither was fixed. What changed since they were first raised is their **classification**:
the box lives in a file the gate now labels abandoned, and the sound speed has an
automated literature gate reporting it on every run. **[CONFIRMED]**

---

## 4. Multi-pane state

**Not applicable in this session. [CONFIRMED]**

`tmux ls` returns `error connecting to /private/tmp/tmux-501/default (No such file or
directory)`. **There is no tmux server running on this machine right now**, therefore no
`canitford` or `ford` panes exist to consolidate. A `ps` sweep for Claude processes returns
only the Claude desktop app and its MCP gateway helper, no pane sessions.

The consolidated "what is actually done" view that a panel audit would produce is instead
given by Sections 1 to 3 above, all measured from the repository rather than from pane
output.

---

## 5. Second pass, 2026-08-25 22:3x: connector-verified additions

Claude Desktop was restarted at **22:27:56** and the Docker MCP gateway respawned two
seconds later at **22:27:58** [CONFIRMED], which resolved the outage diagnosed in
`docs/MCP_GITHUB_GATEWAY_DIAGNOSIS_2026-08-25.md`. This section holds what the restored
connectors could establish that shell tools could not.

### 5.1 Connector status, tested not assumed

| Connector | Test performed | Result |
|---|---|---|
| `MCP_DOCKER` gateway | `get_me` round trip | **LIVE** (was `unavailable` at 21:54) |
| `github` (HTTP Copilot) | `get_me` round trip | **LIVE** |
| W&B | `probe_project_tool` + GraphQL | **LIVE** |
| Hugging Face | `hub_repo_details` on 3 repos | **LIVE** |
| Overleaf | `status_summary`, `get_sections` | **LIVE** |
| deepwiki / scite / wolfram | JSON-RPC `initialize` POST | **LIVE**, all HTTP 200 |
| TACC Vista + LS6 | `ssh` + `taccinfo` | **LIVE**, sockets held open |
| **Zotero** | `zotero_library_coverage` | **STILL DOWN** |

**One connector is still offline, so "all connectors are now connected" is not quite right.**
[CONFIRMED] Zotero returns `Error computing library coverage: [Errno 61] Connection refused`.
The cause is specific and worth recording: **three `zotero-mcp-server` processes ARE running**
(PIDs 62382, 62848, 44107), but `localhost:23119` refuses the connection because **the Zotero
desktop application is not open**. The MCP server is healthy and its backend is absent, which
is a failure mode that looks like a dead connector but is fixed by launching Zotero, not by
touching MCP config.

A methodological note: a bare `initialize` POST to the Copilot endpoint returned **401** in
the sweep above because that probe sent no `Authorization` header. With the token it returns
200. **That 401 is an artifact of the test, not a finding.** Recorded so it is not later
misread as an outage.

### 5.2 W&B project anatomy: the 108 runs decompose exactly

Previously this document carried only the bare total, 108. The full decomposition, from a live
GraphQL query returning all 108 run records with tags and creation timestamps: [CONFIRMED]

| Cohort | Runs | Tags | Created |
|---|---|---|---|
| L0/L1 analytical grid | **70** | `l0-l1-grid-only` | 2026-07-07 09:27:07 to 09:29:07 |
| **Genesis SPH pilot** | **9** | `Genesis-MPM`, `L2`, `Vista` | 2026-07-01 00:00:37 to 00:59:54 |
| early untagged | 9 | none | 2026-07-01 06:11:53 to 06:12:14 |
| **gated warpmpm study** | **17** | `gated-17`, `warpmpm`, `L2`, `n_grid_48/64/96` | 2026-08-17 21:30:15 to 21:31:16 |
| load-surface ensemble | 1 | `warpmpm`, `distributions`, `load-surface` | 2026-08-19 17:42:34 |
| artifact / snapshot admin | 2 | `canonical-data`, `artifact`, `dataset` | 2026-08-20 |
| **Total** | **108** | | |

**Three of these corroborate figures this document already carried, by an independent route:**

- The **70** `l0-l1-grid-only` runs match the **70 rows** of `data/scenario_sweep.csv` exactly.
  Run-name suffixes run 19 through 88 inclusive, which is 70. [CONFIRMED]
- The **9** `Genesis-MPM` runs match the README's "9 unique conditions" SPH pilot. [CONFIRMED]
- The **17** `gated-17` runs match the 17 rows of `data/all_runs_inventory.csv`, by name. [CONFIRMED]

**The engine distinction is correctly encoded in W&B, and that is a genuinely good finding.**
CLAUDE.md's first ground-truth item insists the 17 gated runs are warpmpm and that Genesis is
only the abandoned pilot path. The live tags honour that split precisely: the 17 carry
`warpmpm`, the 9 pilot runs carry `Genesis-MPM`, and no run carries both. [CONFIRMED] Anyone
auditing the W&B project will find the engine attribution correct.

**Two caveats that must travel with any "experiment tracking" claim:**

1. **All 17 gated runs were created inside 61 seconds**, 21:30:15 to 21:31:16 on 2026-08-17.
   [CONFIRMED] That is a backfill from local artifacts, not live logging from the cluster,
   and it confirms the project's own note that the W&B entries for the 17 are Mac backfills.
2. **`has_history` is `false` and `typical_steps` is `0`.** [CONFIRMED, from
   `probe_project_tool`] The project holds **no time-series history at all**, so there are no
   training or convergence curves behind the 108 runs. The runs carry **12 metric keys**
   (`depth_m`, `velocity_ms`, `dv_product`, `l1_haz_score`, `L1_hazard`, `L1_verdict`,
   `L2_verdict`, `L1_L2_divergence`, `divergence`, `verdict`, and two lowercase duplicates)
   and **7 config keys** (`level`, `compute`, `depth_m`, `velocity_ms`, `l1_threshold`,
   `vehicle_class`, `drift_threshold_m`) as **summary values only**.

**Safe phrasing:** "108 runs tracked in W&B across four labelled cohorts, with the solver
identity tagged per run." **Unsafe phrasing:** anything implying logged training curves,
live cluster streaming, or 108 distinct simulations.

### 5.3 CORRECTION to Section 2: two of the three Hugging Face data repos are empty

Section 2 of this document states "2 public datasets (23 and 50 downloads), 1 model".
**That overstates what is published, and the correction is material.** Verified by listing
the actual file manifest of each repo through the HF API: [CONFIRMED]

| HF repo | Type | Files | Real data? | Downloads (30d) |
|---|---|---|---|---|
| `can-it-ford-speed-surface` | dataset | 6 | **Yes**, 4 CSVs | **50** |
| `can-it-ford-sweep-v1` | dataset | **2** | **NO**, only `.gitattributes` + `README.md` | 23 |
| `can-it-ford-sweep-v1` | model | **39** | **Yes**, `manifest.csv` + 36 timeseries CSVs | 0 |
| `can-it-ford` | Space | n/a | live gradio app | 0 likes |

**The empty dataset says so itself.** Its README opens: "This repository holds no data. Please
read this before citing or fetching it," and explains it was created 2026-07-14, never
contained a data file, and is being labelled rather than deleted because it accumulated
downloads while empty. [CONFIRMED, read live] That is exactly the right call and it is
creditable handling of a mistake, but it means **only one published dataset actually contains
data.**

The four real files in `speed-surface` are `load_surface.csv`, `surface_cells.csv`,
`iso_vrel_arcs.csv`, `window_comparison.csv`. That dataset is tagged
`size_categories:n<1K` and its own card marks it **"PROVISIONAL, and deliberately not
frozen"**. [CONFIRMED] The model repo is tagged `superseded`. [CONFIRMED]

**SELF-CORRECTION, same day, second pass.** An earlier version of this row said the model
repo held **0 files**. That was **wrong and is withdrawn.** The probe used
`api/josiecerrell/can-it-ford-sweep-v1`, omitting the `/models/` path segment, and an empty
result from a malformed URL was read as an empty repository. Re-queried at
`api/models/josiecerrell/can-it-ford-sweep-v1`, it holds **39 files**: `manifest.csv` plus
**36 timeseries CSVs** covering sedan/suv/pickup at 4 depths x 3 velocities. [CONFIRMED]
This is the same class of error this document warns about elsewhere: a miss is not an
absence until you know what the predicate actually queried.

**So the real HF finding is not an empty repo, it is a repo-type mismatch.** The box-proxy
sweep data is published under a **model** repo while the identically-named **dataset** repo
is the empty one. Both are deliberately labelled and both point readers to
`speed-surface`.

**The Hugging Face presence is in good shape and needed no repair.** Read live, the model
card explains the supersession, names the box-proxy geometry and the two kept classes
(1390 kg sedan, 2300 kg pickup), states why the repo is retained rather than deleted
("it has accumulated real downloads while unlabeled"), and links the current data. The
empty dataset card does the same. Both are better documented than most published research
artifacts.

**Revised safe claim:** "a live Gradio Space, one current dataset (`speed-surface`,
50 downloads), and a superseded box-proxy sweep of 36 runs retained and explicitly labelled
rather than deleted." Do not claim two *current* datasets; do not claim anything is empty
except the placeholder dataset repo.

A download-count discrepancy, recorded rather than resolved: the HF MCP reported 57 downloads
for `sweep-v1` while two independent REST reads both returned **23**. The two agreeing reads
are the 30-day figure; 57 is likely a different window. Quote 23 with its window, or quote
neither.

### 5.4 The paper, measured

Previously this document had only the cite-key count. Full metrics, from the canonical
`overleaf/main:conference_101719_1.tex`: [CONFIRMED]

| Measure | Value |
|---|---|
| Words | **6,149** |
| Lines / characters | 268 / 45,160 |
| Sections and subsections | **17** (7 top-level) |
| Figures referenced by `includegraphics` | **7** |
| Bibliography entries | 15 |
| Distinct `\cite` keys | 14 |

Structure, read live via the Overleaf connector: Introduction; Prior Work (4 subsections:
Flood-Vehicle Stability Criteria, Physics-Grounded Scene Reconstruction, Why a Single Scalar
Threshold Is Insufficient, Forward and Inverse Property Estimation); Approach (Pipeline,
Three-Level Abstraction Ladder, Vehicle and Scene Representation); Results (Scene
Reconstruction Status, Synthetic-Geometry Pilot Study, Real-Simulation Sweep); Conclusions;
Future Work; Acknowledgment. [CONFIRMED]

**This is a complete conference paper, not a draft skeleton.** A 6,149-word IEEE-format paper
with 7 figures and 15 references is a defensible resume line. Note that the Results section
separates "Synthetic-Geometry Pilot Study" from "Real-Simulation Sweep", and carries a
"Scene Reconstruction Status" subsection, so the paper itself is explicit about the splat
front end not being built. That honesty is a strength to describe, not a gap to hide.

---

## 6. Summary: what is safe to put on a resume

**Safe, CONFIRMED live this session:**

- 867 commits over 8 weeks (2026-07-01 to 2026-08-25), sole author, on a public GitHub repo.
- ~62,000 lines of Python across 242 tracked files.
- A 17-run gated MPM study: 3 grid resolutions x 3 vehicle masses, plus depth and velocity
  sweeps, largest run 180,067 water particles, 1.35 M particles across the study.
- 70-condition analytical hazard sweep; three-level model ladder (L0/L1/L2).
- Single-GPU jobs on two national systems: NVIDIA GH200 (TACC Vista) and A100 (TACC Lonestar6).
- 108 experiment runs tracked in Weights and Biases across **four labelled cohorts** (70 L0/L1
  analytical, 9 Genesis SPH pilot, 17 gated warpmpm, 9 early untagged, plus 3 admin), with the
  **solver identity correctly tagged per run** so Genesis and warpmpm are never conflated.
- A complete 6,149-word IEEE conference paper: 17 sections, 7 figures, 15 references.
- A live Gradio demo on Hugging Face Spaces, one current dataset (`speed-surface`, 4 CSVs,
  50 downloads), and a retained-and-labelled superseded sweep of 36 timeseries runs. See 5.3.
- A live Vercel deployment.
- CI with a 6-step check suite, 12 of 12 recent runs green.
- An automated physics-gate test suite: 11 pass, 1 explicitly-reported skip.
- A 382-paper research index queryable from inside the repo.
- A 3,604-line corrections register with 209 tracked items and an integrity checker.

**Needs a caveat if used:**

- "Multi-node HPC" is **false**. Every job is `-N 1 -n 1`.
- "End-to-end video-to-verdict pipeline" is **false**. No splat has ever entered a simulation.
- "85,000 lines of code" is inflated by ~15,500 lines of duplicated generated Plotly HTML.
- **"2 public datasets" is wrong.** One dataset repo is an explicitly-labelled empty
  placeholder; the 36-run box-proxy sweep lives in the model repo and is marked superseded.
- **"108 simulations" is wrong.** 108 is the W&B run count across four cohorts; only 17 are
  the gated MPM study, and all 17 were backfilled in 61 seconds rather than logged live.
- W&B holds **no time-series history** (`has_history: false`), so claim tracked runs, never
  training or convergence curves.
- SU and node-hour figures are now **live as of 2026-08-25** and corroborated against the
  2026-08-22 audit. Billed-SU (not node-hour) figures remain 3 days old.
- **"201 cluster jobs" is not "201 runs": only 105 completed, 52.2 percent.**
- The gsplat quality metrics (PSNR 22.74) are doc-sourced, not re-verified today.

**Cannot be verified locally, Chat or a live login must cover it:**

- ~~TACC SU balances and node-hours~~ **RESOLVED 2026-08-25: sockets opened, both systems
  measured live. See the MEASURED LIVE block in Section 2.**
- Anything on LS6 scratch, including the gsplat checkpoints (reachable now that the socket
  is open, but not re-measured in this pass).
- **Zotero bibliography coverage.** The connector is up but Zotero desktop is closed, so
  `localhost:23119` refuses. Open the Zotero app and it becomes measurable (see 5.1).
- Whether the Overleaf token has actually been revoked.
- Which poster PDF was actually submitted before the 2026-07-27 09:00 CST deadline.
  `docs/SUBMISSION_STATUS.md` is blank on the question and the 2026-08-25 status pass
  explicitly declined to guess. **[DOC]**
- Any email, connector, or website state.

**Three highest-value fixes before showing this to anyone, all small:**

1. Set the GitHub **description** (currently empty) and **topics** (currently null). The
   README line 3 text is ready to paste.
2. Get `origin/main` current, or at minimum land the `CITATION.cff` licence fix. The
   public default branch contradicts the public datasets on the data licence, and shows
   396 of 867 commits.
3. Add the Hugging Face Space and Vercel links to the `main` README. Both are live and
   neither is discoverable from the default branch.
