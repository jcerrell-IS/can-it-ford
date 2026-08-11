# Session findings, 2026-08-07 (into 2026-08-08)

Cumulative record of one Claude Code session on the Mac. Four workstreams:
an upstream-version census, a cross-tree file reconciliation, a Bingham-sweep
rescue preparation, and a new enhanced-physics simulation that ran six times on Vista.

**Status of every claim below:** verified live during the session by file read, checksum,
network read, or job output. Where something was NOT verified, or was verified and then
refuted, it says so. Several of my own earlier statements in this session were wrong and
are corrected here rather than quietly dropped; see section 6.

**Nothing was committed, pushed, or deleted.** Every file produced is new. Two existing
untracked files were moved (section 2) and nothing was overwritten.

---

## 0. Artifacts produced

| path | what |
|---|---|
| `~/canitford_census_2026-08-07/upstream_report.md` | upstream version census |
| `renders/yaris_render_s3_enhanced/sim_enhanced.py` | enhanced driver |
| `renders/yaris_render_s3_enhanced/run_enhanced.py` | canonical-vehicle binding launcher |
| `renders/yaris_render_s3_enhanced/enhanced_ladder.sbatch` | gated 3-stage job (895330) |
| `renders/yaris_render_s3_enhanced/realwater_ladder.sbatch` | 3-stage job (895378) |
| `renders/yaris_render_s3_enhanced/NOTES_2026-08-07.md` | working notes |
| `renders/yaris_render_s3_enhanced/results/*.json` | six pulled summaries |
| `.claude/worktrees/bingham-sweep-2026-08-07/analysis/bingham_sweep/RESCUE_PLAN.md` | rescue plan, not executed |
| `docs/FULL_SESSION_FINDINGS_2026-08-07.md` | this file (see 6c for why not `SESSION_*`) |

---

## 1. Upstream version census

### 1.1 kks32/mpm-engine has NOT moved

`git ls-remote` returned, in full:

```
544c93dd02cb9c7ead89e1155a62967243244fce	HEAD
544c93dd02cb9c7ead89e1155a62967243244fce	refs/heads/main
cffa5868ba07332fdc0b7c349e09eaccb08b4b40	refs/pull/1/head
463afbd7dbd196c10fa6ba0b9f9adeb4ecd5d45e	refs/pull/2/head
```

`refs/heads/main` is byte-identical to the pinned SHA. Repo `pushed_at` is
2026-07-14T11:53:28Z, the pinned commit's own day. Both pull refs are merged and predate
the pin (PR #1 merged 2026-07-02, PR #2 merged 2026-07-07), so both are already ancestors.
**Zero commits ahead. No action.**

### 1.2 Genesis HAS moved, five releases, and the spread is three-way

No pinned Genesis SHA exists anywhere in the repo. The pin is `environment.yml:96`,
`genesis-world==1.2.0`.

| tag | published |
|---|---|
| v1.2.1 | 2026-07-03 |
| v1.2.2 | 2026-07-11 |
| v1.2.3 | 2026-07-18 |
| v1.3.0 | 2026-07-29 |
| **v1.3.1** | **2026-07-30** |

PyPI latest is 1.3.1 (uploaded 2026-07-30T12:53:17Z). `main` HEAD is
`79e06e8204bea931d976af85885565058bad96f5`, matching no tag, so main is further ahead.

```
Vista runtime    1.1.1   (recorded claim, NOT re-verified from the Mac)
environment.yml  1.2.0   (verified live)
docs URLs        1.2.0   (verified live)
upstream latest  1.3.1   (verified live)
```

**Why it probably does not matter:** CLAUDE.md item 1 establishes Genesis is only the
Track 2 box-proxy path and no Genesis scene has ever loaded the Yaris hull, so no gated
verdict can be affected.

**The one real exposure:** Genesis source citations that carry a line number but no
version qualifier now point into code two minor releases downstream. Notably
`genesis/engine/couplers/legacy_coupler.py:322` for the `coup_friction` finding in
CLAUDE.md, and the three `blob/main/` URLs in `reference_docs/ford_oss_report.md`. Stamp
those with the version they were read at before citing them again. The semantic claim
(`coup_friction` is Coulomb, `coup_softness` is the regulariser) is independent of line
numbering and is not in question.

### 1.3 Both arXiv papers are still v1

- **2605.30542**, "Physically Viable World Models: A Case for Query-Conditioned Embodied
  AI", Thorpe, Tretiakov, Hsiao, Low, Li, Iqbal, Bhatt, Topcu, Kumar. `[v1] Thu, 28 May
  2026`. **No v2.**
- **2607.00673**, "Path Planning in Physically Viable World Models", Low, Hsiao, Li,
  Thorpe, Topcu, Kumar. `[v1] Wed, 1 Jul 2026`. Comments: "18 pages, 7 figures, submitted
  to CORL". **No v2.**

The live author list of 2607.00673 matches CLAUDE.md L-7 exactly, so no correction needed.
Note the two papers do NOT share an author set: 2605.30542 has nine names including
Tretiakov, Iqbal and Bhatt. **Watch item:** "submitted to CoRL" makes a camera-ready v2
the single most likely future change.

### 1.4 Xia 2011 and Shu 2011 remain closed

First, a framing correction that matters for citation: **only Shu is JHR.**

| paper | journal | DOI |
|---|---|---|
| Shu, Xia, Falconer & Lin 2011 | **Journal of Hydraulic Research** 49, 709-717 | `10.1080/00221686.2011.616318` |
| Xia, Teo, Lin & Falconer 2011 | **Natural Hazards** 58(1), 1-14 | `10.1007/s11069-010-9639-x` |

Unpaywall v2, queried live:

| DOI | is_oa | oa_status | OA locations |
|---|---|---|---|
| `10.1080/00221686.2011.616318` | false | **closed** | 0 |
| `10.1007/s11069-010-9639-x` | false | **closed** | 0 |
| `10.1007/s11069-013-0889-2` | false | **closed** | 0 |

**Limitation:** all three records show `updated: 2025-05-22`, so a deposit made after that
would not necessarily be reflected. Unpaywall also excludes ResearchGate and Academia.edu
by policy. Strong evidence, not proof.

Spot-checks: ProQuest is abstract-only, verbatim "This is a short preview of the
document". SpringerLink returns HTTP 303 to `idp.springer.com/authorize`.

### 1.4b RESOLVED 2026-08-08: the ORCA lead is a dead end. Gap confirmed closed.

The Cardiff ORCA record at `https://orca.cardiff.ac.uk/17057` returned HTTP 403 with no
body to both WebFetch and curl. That was correctly diagnosed as a **bot block, not a
paywall**: opened in a real browser via the Chrome extension it loaded immediately,
redirecting to `https://orca.cardiff.ac.uk/id/eprint/17057/`.

**The record is real and is the right paper:**

| field | value |
|---|---|
| title | Incipient velocity for partially submerged vehicles in floodwaters |
| authors | Shu, Caiwen; Xia, Junqiang; Falconer, Roger Alexander (ORCID 0000-0001-5960-2864); Lin, BinLiang (ORCID 0000-0001-8622-5822) |
| year / journal | 2011, Journal of Hydraulic Research |
| DOI | 10.1080/00221686.2011.616318 |
| publisher / ISSN | IAHR / 0022-1686 |
| last modified | 18 Oct 2022 |
| Scopus / Dimensions citations | 67 / 72 |

**And it carries no file. Verbatim from the page: "Full text not available from this
repository."** There is no Download button and no "Request a copy" control; the only
actions are an "Official URL" pointing at the paywalled DOI and an "Edit Item (repository
staff only)" button.

So the outcome is **(a) metadata-only record**, exactly consistent with Unpaywall's
`closed` / zero OA locations rather than in tension with it. Unpaywall harvested this
record's metadata and correctly found no deposited file.

**Conclusion: Shu 2011 is genuinely not openly retrievable.** The recorded route stands
unchanged: UT Austin library proxy or ILL. The standing instruction in
`_inbox/CAN_IT_FORD_PROJECT_INSTRUCTIONS_v8.md:222`, "Do not reconstruct from citing
papers", also stands. The one thing freely readable on the ORCA page is the paper's own
abstract, which is not a substitute for the force-balance derivation the semi-empirical
baseline needs.

### 1.4c CONFIRMED AND CLARIFIED 2026-08-08 via Elicit export + scite

**No Elicit MCP connector exists on this machine.** The research connectors available are
consensus, scite and zotero. What was used instead: the existing Elicit extraction already
in the repo, `citations/Elicit - extract-results-review-5e368aae-...csv` (42 papers), plus
scite's per-DOI access resolver. A fresh Elicit run would need elicit.com opened in the
browser under Josie's login.

**Signal 1: Elicit never captured Shu 2011 at all.** Zero rows in the 42-paper extraction
match DOI `10.1080/00221686.2011.616318`. Elicit's pipeline extracts from full text, so its
absence is consistent with the text being unreachable, not merely unsearched. Xia 2013,
Arrighi 2016, Martínez-Gomariz 2018 and three Shah papers are all present.

**Signal 2: scite reports `contentDenied: true` on both papers.** That is the *same term*
this project's own gap note uses at `_inbox/CAN_IT_FORD_PROJECT_INSTRUCTIONS_v8.md:222`
("Both paywalled, `contentDenied`, absent from Scholar Gateway, no local PDF"), so scite
independently reproduces the recorded diagnosis. Both are `isOa: false`,
`oaStatus: "closed"`.

**NEW: the gap has a price, so it is not "unobtainable".**

| paper | purchase | rental | citations (scite) |
|---|---:|---:|---:|
| Shu 2011, JHR | $73.95 | **$25.00** | 121 total / 79 citing pubs |
| Xia 2011, Nat Hazards | $37.95 | **$19.00** | 108 total / 91 citing pubs |

A $25 rental closes the Shu gap immediately and beats an ILL turnaround if a deadline is
near. UT Austin proxy remains free if the subscription covers JHR.

**NEW: exactly what is behind the paywall, and it is narrow.** Xia 2011's abstract IS
freely returned by scite in full, and it specifies the structure:

> a formula has been derived to predict the incipient velocity of flooded vehicles
> according to the mechanical condition of sliding equilibrium

and, critically:

> The experimental data obtained for the small-scale model vehicles were used to determine
> **the two parameters** in the derived formula

So the **derivation is a sliding-equilibrium force balance, which is reconstructable from
first principles. What is NOT reconstructable is the pair of empirically fitted
coefficients.** That is the whole cost of the gap: two calibration constants, not a method.
This is why the standing "do not reconstruct from citing papers" instruction matters — a
citing paper may quote a threshold but will not give you the fit.

Also from the free abstract: three die-cast model types at two scales each, validated
small-scale-fit against large-scale data, and the finding that incipient velocity is
minimised as incoming depth approaches vehicle height, with Mini Cooper easiest to slide.

**Partial substitute already in hand.** Elicit DID extract Xia 2013/2014
(`10.1007/s11069-013-0889-2`) with usable numbers:

- rolling friction coefficient **0.25 parallel flow, 0.75 perpendicular flow**
- Honda Accord 2.0 m/s and Audi Q7 4.3 m/s incipient velocity at 0.35 m, 0/180 deg
- slope effect, Honda Accord at 0.25 m: 3.9 / 3.3 / 2.9 m/s for flat / 1:100 / 1:50
- 2 models, scales 1:14 and 1:24, motion state **Stationary** (corroborates L-1)

**LEAD, not a correction.** The project records "0.25-0.75 as the documented sensitivity
range across studies (Xiong et al. 2024)". This extraction instead attributes 0.25 and 0.75
to **Xia 2013 directly, as two flow orientations** (parallel vs perpendicular), not as a
cross-study range. If that holds against the primary text it changes what the range means:
two specific orientation values from one paper rather than spread across the literature.
**Not verified** — an Elicit extraction is LLM-generated and secondary. Check it against
the Xia 2013 PDF before it is used or cited.

**Method note on what was and was not used.** scite Smart Citations are quotations from
citing papers. They were NOT used to reconstruct any formula, per the standing instruction.
scite was used only for access metadata and for the publisher's own abstract of Xia 2011.

**Year trap reconfirmed.** scite returns Xia 2011 as `year: 2010`, `date: 2010-10-20`,
vol 58, issue 1, pp 1-14. Online-first 2010, print 2011. Cite the bib key, never a bare year.

**Tooling caution learned here.** `get_page_text` on this record returned the abstract of a
*different* paper (Shah et al. 2021, "A review of safety guidelines for vehicles in
floodwaters") because it prioritised an embedded CORE "related recommendations" widget over
the actual record body. The page `<title>` was correct while the extracted body was not.
On repository pages, read the accessibility tree or target the record element; do not trust
a single text extraction to be the record you asked for.

---

## 2. renders_preview cross-tree split, RECONCILED

### 2.1 The split had no convention behind it

**No script in either tree contains the string `renders_preview` or `_combined`.** Both
files were produced by ad-hoc command-line invocation. `render_frames.py:186`
(`out_path.parent.mkdir(parents=True, exist_ok=True)`) creates whatever parent the caller
names, cwd-relative, silently, which explains the split exactly.

The repo holds two contradictory conventions: `render_frames.py` is cwd-relative
(`--output` defaults to the bare name `"mpm_water_box.mp4"`), while `render_hero_shot.py`
is script-location-anchored (`PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))`).
The sweep's own collector `collect_bingham_sweep.py:17,55` is script-anchored and writes
beside the run data, which is the convention that decided the destination.

### 2.2 The two files were proven paired by arithmetic, not timestamps

```
rollout.npz  water                (90, 48367, 3)
rollout.npz  veh_particles_scene0     (8905, 3)
                                  ------------
combined.npz positions           (90, 57272, 3)   48367 + 8905 = 57272 exactly
combined.npz is_vehicle             (57272,) bool
```

Byte arithmetic closes too: 90 x 57272 x 3 x 4 = 61,853,760 against 61,853,888 stored.

### 2.3 Action taken

Both moved to `analysis/bingham_sweep/tau0p0_control/`, beside `rollout.npz`. Checksums
byte-identical before and after (`66f6701d…` mp4, `239acec0…` npz). Same filesystem, so
each `mv` was an atomic rename. `mv -n` used as a second overwrite guard on top of an
explicit pre-flight existence test.

Root retained only the unrelated prior occupant `j1_force_comparison.png` (16:19, 18 min
older than the mp4). The worktree's `renders_preview/` is now empty and has disappeared
from its git status.

### 2.4 Defect found: the mp4 has the wrong frame rate

Both `.npz` files record `fps = 30`. `ffprobe` reports the mp4 at `r_frame_rate=24/1`,
`duration=3.750000`, 90 frames. `render_frames.py:232` defaults `--fps` to 24 and was left
at default. **The preview plays 25 percent slow; anything timed off it is wrong.**
Re-render at 30 fps before it is used or committed.

### 2.5 Count reconciliation, honestly incomplete

Post-move the worktree holds **54** untracked files; pre-move it held **53**. The proven
delta is **+1**, the mp4 arriving from root. Against the stated baseline of 51 there is a
**2-file gap I could not close by proof.** I refuted the obvious hypothesis that 51 came
from the other tree (root's `-uall` is 7). From mtimes the likely explanation is a capture
mid-write during the `_replicate` run, whose files landed at 15:24:31 and 15:24:32, so the
tree passed through 49, 50, 51, 52 inside one second. **Inference from timestamps, not
proof.**

---

## 3. Bingham sweep: findings and rescue prep (NOT executed)

### 3.1 Result

**All 11 ladder points return NO-FORD.** `final_disp_mag_m` spans 0.519301 to 0.659482 m;
the minimum is **10.39x** the 0.05 m DRIFT_THRESHOLD. Largest rheology effect is
**-21.26 percent** at `tau_y = 100 Pa`.

**Read precisely:** the verdict is invariant because the operating point is an order of
magnitude from the threshold, NOT because rheology is negligible. The claim is "Newtonian
is the simplest sufficient model **for this verdict at this operating point**". It does
not transfer near the threshold and must never be written as "rheology does not matter".

### 3.2 Two results absent from the results table

**(a) The Mac run is bit-exact deterministic.** `_replicate/` is not in
`collect_bingham_sweep.py`'s `ORDER`, so it never reaches the CSV. Its `final_disp_mag_m`
is `0.6594815254211426`, identical to the control to all 16 digits.

**(b) Cross-venue fidelity beats the canonical run's internal agreement.**

| comparison | value |
|---|---|
| control vs canonical `summary.json` (0.6585370302200317) | **+0.1434 percent** |
| control vs canonical `rollout.npz` (0.637019) | +3.5262 percent |
| canonical `summary.json` vs its own `rollout.npz` | +3.3779 percent |

The Mac control reproduces the canonical `summary.json` measure ~24x tighter than the
canonical run's own internal inconsistency. Always name which canonical number is meant.

### 3.3 New observation: P-2 is rheology-sensitive though the verdict is not

Yield stress **monotonically reduces water pass-through** and pushes two of eleven points
across gate P-2 (`tau100p0` 0.08741 and `etacoup_tau40p0` 0.09719 pass; the other nine
fail). This is a statement about a numerical containment gate, not physics: CLAUDE.md item
6 establishes no gate is a physics validation.

### 3.4 The rescue problem

```
13 .npz files      769.4 MB
everything else      1.17 MB   <- the entire scientific content (40 files)
total              770.6 MB
```

`git check-ignore` confirms **nothing is ignored**: `.gitignore:14` covers `renders/`,
which does not match `analysis/bingham_sweep/`, and **no `*.npz` rule exists anywhere in
the repo**. A commit puts 771 MB into history permanently. **99.85 percent of the bytes
carry none of the conclusions.**

**Proposed mechanism, drafted not created:** a scoped `analysis/bingham_sweep/.gitignore`
containing `*.npz`. Verified safe: no `.gitignore` exists under `analysis/` or
`analysis/bingham_sweep/`, and no conflicting rule or negation exists. **Do NOT edit root
`.gitignore`** — it is tracked, shared across branches, and the live-state hook reported
up to 3 concurrent sessions; it is exactly the file that got swept up in the 2026-08-07
breach.

Also discovered: `.git/info/exclude` already carries `.claude/worktrees/`, which is why
root's `git status` never showed any of this. That pattern does not fire inside the
worktree, where paths are relative to its own root.

Full plan with exact staging commands is in `RESCUE_PLAN.md`. **Nothing in it was run.**

---

## 4. Enhanced simulation: BUILT, DEPLOYED, SIX RUNS COMPLETE

### 4.1 Provenance established by checksum

`renders/yaris_render_s1/sim_standing.py` and Vista's `$WORK/render_s2/sim_standing.py`
are both `5215c38bed607ef6…`, **byte-identical**. So the local file provably is the code
that produced the 17 gated runs, and the enhanced driver's diff against it is a real audit
trail rather than a claim about a reconstruction.

### 4.2 Venue decision, counterintuitive

| cluster | SUs (live) | warpmpm ready |
|---|---:|---|
| Vista (GH200, aarch64) | **670** | yes, `$WORK/mpm-engine/src/warpmpm` |
| LS6 (A100/H100, x86) | **9644** | **no**, only gsplat + pycolmap |

LS6 has 14x the allocation and would be obvious, but has no warpmpm environment at all.
**Building one on LS6 is the highest-value infrastructure task available**, precisely
because of that split.

### 4.3 Results, jobs 895330 and 895378

| run | disp (m) | c (m/s) | substeps | cells/depth | P-2 | P-3 | wall |
|---|---:|---:|---:|---:|---|---|---:|
| ctrl_g64 | 0.65715 | 12.85 | 11 | 2.038 | 0.10673 FAIL | -0.00708 PASS | 13 s |
| enh_g96 | 0.26921 | 12.85 | 16 | 3.057 | 0.09654 PASS | +0.00000 PASS | 6 s |
| enh_g96_c10 | 0.48839 | 128.45 | 156 | 3.057 | 0.08502 PASS | -0.04368 FAIL | 30 s |
| enh_g128_c10 | 0.67768 | 128.45 | 208 | 4.076 | 0.09495 PASS | -0.02406 FAIL | 89 s |
| **enh_g96_real** | **0.28232** | **1480.98** | **1797** | **3.057** | **0.06623 PASS** | **-0.00738 PASS** | 293 s |
| enh_g128_real | 0.33524 | 1480.98 | 2396 | 4.076 | 0.08387 PASS | -0.01637 FAIL | ~950 s |

Gate criteria read from source, not assumed: P-2 is `passthrough_max_frac < 0.10`
(`gates.py:148`, strict `<`); P-3 is `abs(C2_veh_zmin_rise) <= 0.01` (`gates.py:150-151`).

**Cost: 4 SUs.** Vista went 670 -> 666 across both jobs, 00:02:09 + 00:21:23 = 23 min 32 s
of single-node GH200 time for six runs including two at physical sound speed. Batch only,
no idev.

### 4.4 Validation: the pipeline reproduces canonical behaviour

- **Control gate: -0.2106 percent** against the canonical g64_m1100.
- **The g64 -> g96 transition reproduced the canonical grid study to 0.17 percentage
  points**: measured **-59.03 percent**, CLAUDE.md item 5 records **-59.2 percent**.
  Nothing was fitted to that number. It also reproduces the known non-monotonicity rather
  than smoothing it away.
- The `--estimate` mode self-tests against eight recorded values before any enhanced number
  is trusted: substeps 11, `term_acoustic` 311.6253 vs 311.6252878790618, `term_advective`
  20.3784 vs 20.37839643738194, `term_viscous` 0.000277 vs 0.0002768526942394007, c 12.8452
  vs 12.84523257866513, dx to 9 digits, clearance 1.226 and 0.998 cells.

### 4.5 The best run: `enh_g96_real`

**The first physically-correct sound speed in this project's history**, c = 1480.976 m/s,
error factor **1.0000162** against real water's 1481. All 17 gated runs used 12.845 m/s,
off by 115.3x. It is also numerically the cleanest:

| | g64 baseline | enh_g96_real |
|---|---|---|
| P-2 pass-through | 0.10673 FAIL | **0.06623 PASS** (lowest of six) |
| P-3 z-rise | -0.00708 PASS | -0.00738 PASS |
| leaked particle-frames | 153,172 | **6,037** (25.4x fewer) |
| sound-speed error | 115.3x | **1.0000162x** |

Only `enh_g96` and `enh_g96_real` pass both gates; the latter does so at a correct sound
speed.

### 4.6 Finding: sound-speed sensitivity is NON-MONOTONE. Do not extrapolate.

At fixed grid g96:

```
c =   12.85   disp 0.26921    (the as-run value in all 17 gated runs)
c =  128.45   disp 0.48839    +81.4 percent   <- the OUTLIER
c = 1480.98   disp 0.28232     +4.9 percent   <- physically correct
```

**The intermediate is the outlier, not the endpoint.** A partial sound-speed correction is
worse than either endpoint, so **no intermediate sweep point can be used to extrapolate
toward the physical value.** Anyone testing sound-speed sensitivity must run the physical
value directly.

This does NOT vindicate 12.845 m/s: the agreement is one operating point, one metric, and
roll still differs (-0.004 vs +0.590 deg). It is direct confirmation of Isik and He 2022,
which CLAUDE.md records as the citable result that artificial sound speed can qualitatively
flip a rigid-body outcome. At c=128 the roll **changed sign**, -0.0036 -> +1.109 deg.

### 4.7 Finding: grid sensitivity roughly halves at physical sound speed

Same pair g96 -> g128: **+38.8 percent** at c=128.45 versus **+18.7 percent** at c=1480.98.

Suggestive that the artificial sound speed amplifies the project's known grid
non-convergence. **NOT established:** one grid pair, two sound speeds, no third point, no
repeat. Do not put it in the paper without more points.

### 4.8 Finding: every g128 run fails P-3

`enh_g128_c10` -0.02406 and `enh_g128_real` -0.01637. The hull sinks into the floor plane
more at higher resolution, the same pathology CLAUDE.md item 7 records for the g48 runs.
**Cause not diagnosed.** Consequence: the highest-resolution runs are NOT the ones to
quote.

### 4.9 Verdict

**All six are NO-FORD**, 0.26921 to 0.67768 m = 5.38x to 13.55x the threshold. Invariant
across a 115x sound-speed range, a 2x grid refinement, and a 2.5x displacement spread.

### 4.10 Two latent bugs in the canonical driver, found and NOT inherited

Both are live in `sim_standing.py` right now. Neither was edited there.

1. **`summary.json` can lie.** `:355` writes `"bulk_modulus": 1.5e5` as a hardcoded literal
   instead of reading the scene value. Harmless until the value is varied, which is exactly
   what this work does.
2. **`KeyError` after all compute is spent.** `:302` checkpoints frames `(0, 45, frames-1)`
   and `:333` reads `checkpoints["45"]` unconditionally, so any run with `frames <= 45`
   dies at the very end, after the full rollout.

### 4.11 The login-node trap, caught before it cost anything

`from warpmpm.vehicle import load_vehicle` **blocks on the Vista login node**: 600 s wall
for 0.75 s CPU, exit 124, against 78.9 s on a compute node. My first version imported
warpmpm at module scope, so `--estimate` would have hung exactly where it must work.
Engine imports are now lazy behind `_load_engine()`. Verified: `--estimate` imports zero
warpmpm and runs on the Vista login node in **0.178 s**.

### 4.12 Environment forks recorded

- warp **1.16.0** on the Mac venv vs **1.15.0** on Vista. Same Python 3.12.13, numpy 2.5.1.
  Do not expect bit-exact cross-venue agreement across a warp minor version.
- The Mac's pip-installed `warpmpm.vehicle` has **no** `solidify_watertight`; Vista's does.
  This confirms Vista runs a later revision than the pinned SHA. `run_enhanced.py` detects
  which it has and binds `vehicle_live.py` only when needed, so one launcher is correct on
  both machines.

---

## 5. What was NOT fixed, and must not be claimed

**The hull exerts no pressure on the water.** `mpm_utils.py:1100` initialises rigid
particle stress to a zero mat33, `:1104` excludes material 8 from the SVD, and no
`mat == 8` branch in `:1105-1147` ever assigns one. This is the largest remaining realism
gap. Fixing it means patching a vendored engine at a pinned SHA; **no driver can do it.**

Section 4 showed P-2 pass-through improves with resolution alone (0.10673 fail -> 0.09654
pass, physics unchanged). That is the first measurement bearing on the seven gated P-2
failures, but it **does not refute the zero-stress hypothesis** — both mechanisms could
operate and nothing here separates them. Do not write this up as having identified a cause.

**No inflow/outflow boundary conditions exist upstream at all** (zero hits across the
install). The channel remains a Dirichlet velocity clamp on an upstream particle slab. The
citable design is Zhao, Bolognin, Liang, Rohe and Vardon 2019, Computers and Fluids 179,
27-33, DOI 10.1016/j.compfluid.2018.10.007. Writing it is a translation, not a port.

**Resolution is unconverged everywhere.** The best run reaches 3.057 cells per flow depth
against a rule of thumb of ~10 particles per depth; reaching 10 needs about n_grid 314.
Ground clearance stays sub-stencil throughout (1.840 cells at g96 against a 3-cell
quadratic B-spline). `docs/limitations.md` L-11 records why CPIC does not fix it.

---

## 6. Corrections to my own claims during this session

Kept rather than dropped, because each changed what was possible.

1. **"No numpy on this Mac at all" — WRONG.** I checked the wrong interpreters.
   `/Users/josie/.venvs/canitford-mpm` has numpy 2.5.1, warp 1.16.0 and warpmpm. This is
   what made local development and testing possible at all.
2. **">500 substeps/frame is not affordable on 670 SUs" — REFUTED by measurement.** I wrote
   that warning into the estimator myself. Actual: the whole 3-stage ladder ran in 2 min
   09 s. Replaced with a model calibrated on two real points
   (`wall ~= (2.7 + 0.175*substeps)*(grid/96)^3`), which reproduces both (6 s vs 5.5 s
   measured, 30 s vs 30.0 s). **This correction is what made the real-water runs happen.**
3. **Wall-clock estimates were ~30x too conservative.** I predicted ~81 min for the first
   ladder; actual 2:09. Cause: the historical "~1.5 min baseline" I scaled from included
   job setup and warp JIT warmup, visible in the data as g64 taking 13.4 s for 11 substeps
   while g96 took 5.5 s for 16.
4. **The count prediction in RESCUE_PLAN.md was stale on arrival** (41/54 corrected to
   43/55) because writing the plan file changed the number it predicted.

---

## 6b. New instance of a documented `check_claims.py` defect: rule C13

Writing this file tripped the `check_claims` PostToolUse hook with
`ERROR [C13] ... :229`. **Verified false positive, left as written.**

Line 229 restates the authority in AGREEMENT with it: it says gates are
self-consistency and numerical-containment checks, which is verbatim what
`CLAUDE.md:150` asserts. The hook's own message covers this case: "If the text quotes
the claim in order to correct or retire it, that is correct and you should leave it as
written."

**Mechanism, read from source.** `scripts/check_claims.py:239-245` defines C13 with a
pattern and a `context=r"gate|G-\d|P-\d"` filter, but **no `exclude=` parameter**. So it
fires on any correct restatement, not only on a violation.

This is the **same defect shape** already recorded for C8 in
`docs/UNEXPLORED_AREAS_ASSESSMENT_2026-08-07.md` item 8 ("fires on the refutation itself
because, unlike C10b and C14, it carries no `exclude=`"). That assessment found only 15 of
260 hits (5.8 percent) were real. **C13 should be added to the list of rules needing an
`exclude=`.** Not applied here: `scripts/check_claims.py` is the file CLAUDE.md flags as
contested between sessions, and landing rule-table edits from one of several concurrent
sessions is how the 2026-08-07 breach happened. It needs a sequenced owner.

The accompanying WARN on the Xia year is also benign: the authority asks for
disambiguation between two Xia papers, and this file disambiguates by DOI, which is
stronger than the bib key the rule requests.

## 6c. This file was silently gitignored on creation. Fifth occurrence.

Written first as `docs/SESSION_FINDINGS_2026-08-07.md`. `git status --porcelain` returned
**empty** for a brand-new file, which is the tell. Cause, confirmed by
`git check-ignore -v`:

```
.gitignore:25:session_*.md	docs/SESSION_FINDINGS_2026-08-07.md
```

`.gitignore:25` is `session_*.md`. The volume is **APFS, case-insensitive**, so
`SESSION_FINDINGS_...` matches the lowercase `session_` pattern. The file existed on disk
and was **completely invisible to git**.

**This repo has been bitten by this at least four times before**, and three explicit
negations already exist at `.gitignore:95-97` (`!docs/SESSION_CLAIMS.md`,
`!docs/SESSION_DISPATCH_2026-07-25.md`, `!docs/SESSION_INDEX_2026-07-25_SHIPv3.md`).
Git history: `a72f66d` ("case-insensitive fs was swallowing them"), `c998ecc` and `9d53acc`
("was silently gitignored"), `34ea9d1` (the negations a72f66d's message claimed but did
not actually contain).

**Fix applied: renamed to `docs/FULL_SESSION_FINDINGS_2026-08-07.md`.** The pattern anchors
on the basename start, so `FULL_...` does not match. Verified with `git check-ignore`
before the move, and `git status` now reports `?? docs/FULL_SESSION_FINDINGS_2026-08-07.md`.

**Why rename rather than add a fourth negation**, which is the established precedent:
`.gitignore` is tracked and shared across branches, and the live-state hook reported a
concurrent session in this repo at the time. CLAUDE.md records an active breach in which
one session captured another's uncommitted edits. Renaming needs no shared-file edit at
all. Adding `!docs/SESSION_FINDINGS_2026-08-07.md` at :98 would have worked equally well
and is the more consistent choice if a single owner is sequencing `.gitignore`.

**Standing advice:** after creating any doc under `docs/`, run
`git status --porcelain <path>`. Empty output for a new file means it is ignored, not that
it is clean. Any name beginning `session_` or `SESSION_` will vanish.

---

## 7. Open items needing a human

1. ~~Open `https://orca.cardiff.ac.uk/17057` in a browser.~~ **DONE 2026-08-08, see 1.4b
   and 1.4c.** Confirmed closed four independent ways (Unpaywall, ORCA record, scite
   `contentDenied`, absence from the Elicit extraction). **Now actionable rather than
   blocked:** Shu 2011 rents for $25.00 or sells for $73.95; Xia 2011 rents for $19.00.
   Free routes are UT Austin proxy or ILL. What is actually behind the paywall is narrow:
   the sliding-equilibrium derivation is reconstructable, only the **two fitted
   coefficients** are not. Decide: pay ~$25, request via ILL, or proceed citing the
   threshold values already extracted from Xia 2013.
2. **Decide the Bingham rescue.** `RESCUE_PLAN.md` is ready; nothing executed. 771 MB is
   currently un-ignored and one `git add` from entering history permanently.
3. **Re-render `tau0p0_control.mp4` at 30 fps** before it is used. Needs `combined.npz`,
   which the rescue plan excludes, so do this first.
4. **Empty `renders_preview/` directory** left in the worktree; removing it is a delete and
   needs explicit confirmation.
5. **Version-stamp Genesis source citations** before they are cited again (section 1.2).
6. **Consider building warpmpm on LS6** — 9644 SUs sitting unused against Vista's 666.

---

## 8. Note on the "dub command"

No `dub` command, skill, slash-command or binary exists anywhere on this machine.
Searched `.claude/commands/` (contains only `resume-pane`, `submit`, `tacc`, `verify`),
`~/.claude`, the repo, and `$PATH` (`which dub` -> not found). Notes were written to files
instead. The closest available match is the `remember` plugin's `/remember`.
