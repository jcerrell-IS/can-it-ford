# Handoff: session of 2026-08-15 to 08-18, and the prompt for the next session

Written at the end of a long session. Part 1 is what exists now and how it was
verified. Part 2 is everything asked for that is NOT done. Part 3 is a
ready-to-paste prompt for a fresh Claude Code session.

Every claim in Part 1 was measured live in this session unless marked otherwise.

---

# UPDATE, LATER ON 2026-08-18: PHASE C IS DONE AND B3 IS QUANTIFIED

Appended by the session that ran Part 8. Read this before Parts 1 to 7; where it
conflicts with them, this wins. Full working in register **J20 to J23**.

**Phase C (unbound the domain) is implemented and measured.** Commit `be1b138`:
`simulation/openchannel_bc.py` and `simulation/sim_channel.py`, artifacts in
`data/openchannel_2026-08-18/`. Five runs on Vista c642-032, g64, water only.

**B3 is no longer an assertion.** At ZERO grade the closed box manufactures
`+0.09268 +/- 0.00161 m/m` of free-surface slope. A 3 degree road has a bed slope
of `tan(3 deg) = 0.05241 m/m`. **The artifact is 1.77x the whole signal.** Opening
the streamwise faces leaves `-0.00284 +/- 0.00029`, 33x smaller, and never drains
a bin where the closed box empties 2 of 12 at zero grade and 4 of 12 at 3 degrees.

**Four things in Parts 1 to 7 are now corrected.**

1. **"The driver already has a sustained inflow of sorts" is WRONG.** `_sustain_inflow`
   only overwrites vx in an upstream band and creates no particle. Neither inflow
   nor outflow exists. The `inflow=` count decays because the band empties: measured
   9044 at frame 0 to 4 at frame 89.
2. **Gravity IS overridable through the public API**, so tilted gravity needs no
   engine change. `set_material` spreads `**params` last, and `set_parameters_dict`
   honours a `g` key. August 4 item 3's "unconditionally" describes the 17 gated
   runs, not the API.
3. **`periodic_x` is ruled out**, not merely trappy: its docstring says
   "Incompatible with CDF colliders and rigid bodies" and the vehicle is one.
4. **The g128 runs used a DIFFERENT driver** from the repo's canonical
   `sim_standing.py`: `$WORK/render_s2/sim_standing.py`, 389 lines, sha256
   `5215c38b`, not the 564-line `4696c3b2`. Scene physics is identical bar one
   bookkeeping line, so J17 to J19 stand, but "its sha256 stamps 40 D5 runs" does
   not extend to the g128 set. See J23 for a latent reporting fork this creates.

**J22, and a correction to my own first draft of it.** I wrote the sound-speed
shortfall up as a new finding. It is not: `.claude/checks/params_check.py` already
emits `[lit:sound_speed_cfl] 15/17 runs below the 10x convention ... only 4.28x
v_max`, with the same numbers. Running the repo's own gates before committing is
what caught it. What is genuinely new is only that the shortfall carries into the
g128 set, and that Zhao et al 2019 is a second independent citation for the same
10x convention. No verdict is known to turn on it and that has not been tested.

**Still open in Phase C.** Zhao's free-overfall case and its end-depth ratio is NOT
tested; only the uniform channel is. Their target is Rouse's critical-depth-is-
about-1.4x-brink-depth, taken from their own full text via Scite because **neither
PDF was retrievable**: Undermind failed on both, and the CityU green-OA copy of the
hydroplaning paper is behind a Cloudflare bot challenge that was not bypassed. So
**Phase A step 1 is only partly done** - `10.1063/5.0276643` is verified (matched,
high confidence) and its 51-item reference list is in hand, but its pavement
representation, the thing Phase D needs, is still unread.

**Correct the author list before citing it.** Part 2.1 and Part 3 say "Zhou, Qing &
Wang 2025". Crossref gives **Zhou Changhong, Zhong Qing, He Zhihe, Wang Yixuan,
Tang Xianyuan, Li Peilin**. "Qing" is Zhong Qing's given name, not a family name.

**Known defects in what I shipped.** `leaked_particle_frames` is 2 to 3x higher in
recycle mode than closed and is undiagnosed. Both grade=3 runs are non-stationary
at 5 percent over 90 frames. `n_eff` is 3.9 to 9.1 of 90 frames in every run. The
inlet and outlet end bins sit about 25 percent above mid-channel depth.

**Next, in order.** (a) Diagnose the recycle-mode leak count. (b) Implement the
free-overfall case and test against the 1.4x ratio, which is the only external
validation target currently in hand. (c) Longer records for the graded runs until
they pass the reverse-arrangement test. (d) Then Phase D (road geometry), which
still wants the hydroplaning paper's pavement method, so getting that PDF is worth
one focused effort. (e) Phases E, F, G unchanged.

---

---

# PART 1: WHAT NOW EXISTS

## Ten commits, all local on `claude/add-ci-checks`, none pushed

| SHA | What |
|---|---|
| `072e4f3` | `stationarity.py`, `settle_audit.py`, `probabilistic_verdict.py`, `docs/RESEARCH_TO_IMPLEMENTATION_2026-08-15.md` |
| `46282bc` | 332-paper research index, `research-corpus` skill, `.gitignore` un-ignore |
| `790d999` | Documents merged into index, SessionStart hardwiring, 2 CI steps, CLAUDE.md + register addendum |
| `ffc05d9` | 15 citations added to `paper/can_it_ford_references_IEEE.bib`, all verified |
| `50b70c0` | `tests/test_physics_gates.py`, the three physics gates |
| `df52bee` | `scripts/run_analytic_benchmarks_vista.sh` + gate 1 rewrite |
| `a677a59` | g128 canonical set, register J17 |
| `4dac5f0` | g128 velocity sweep, register J18 |
| `623360b` | g128 depth sweep, register J19 |

`pre-commit` refuses more than 8 staged files. `pre-push` needs `PUSH_OK=1`.
Bulk staging is blocked by a hook: stage explicit paths, and note that
`git add <directory>` also trips it.

## The research corpus is queryable from inside the repo

`data/research_corpus_index.json`, built by `analysis/research_index.py`.
**332 distinct papers** (222 with abstracts) merged from eight Undermind reports,
plus **44 research documents** (39 on-topic) covering the Claude.ai artifacts,
five Perplexity reports and the Elicit extracts. 25 method tags.

```bash
python3 analysis/research_index.py --stats
python3 analysis/research_index.py --method added-mass -v
python3 analysis/research_index.py --query hydroplaning -v
python3 analysis/research_index.py --docs --query claude
python3 analysis/research_index.py --gaps --method validation-dataset
```

Only **43 of 332 papers reach a reader-facing document**. 256 are cited nowhere.
60 carry no DOI and are undiffable; 110 are metadata-only because each report
details its top 50 only. **There are 323 abstracts on disk, not 426.**

Two traps already hit and fixed, do not reintroduce:
- Excluding `.claude/worktrees/` is mandatory when computing cited status. A
  first version included it and reported 269 of 332 as cited, because another
  session's `r5_citation_xref.tsv` holds 489 DOIs.
- `data/*` is gitignored, so any new data directory needs an explicit
  `!data/<name>/` un-ignore pair or it silently never travels.

`orient_live.sh` announces the corpus at every SessionStart. The
`research-corpus` skill routes queries before novelty or method claims.

## The settle length is contradicted by the data

`sim_standing.py:154` uses `settle_frames=8`. `analysis/settle_audit.py` over 25
local runs: **all 25 need more than 8 frames discarded**, min 29, median 48, max
80, of 91 total. **N_eff is 2.9 to 11.0**, so uncertainty from N=91 is overstated
roughly three to five times. 12 of 25 windows are still non-stationary after
trimming, which reads as the runs being too short and independently reaches D9's
250-frame conclusion by a different route.

`analysis/stationarity.py` implements MSER (Bergmann 2021), Chodera
equilibration (2015), Flyvbjerg blocking (1989), the reverse-arrangement test
(Pan & Patton 2017) and the Transient Scanning Technique with RUM (Brouwer 2019).
Pure stdlib, 10 self-tests.

**MSER minimises standard error, which is NOT stationarity.** A residual trend
can survive inside the MSER-optimal window; only the reverse-arrangement test
catches it. Both are reported for that reason.

**Do not remove the transient before a SLIDE verdict.** Incipient motion is an
event, not a steady state. Removing it drops SLIDE from 21 of 24 to 5 of 24 and
would silently contradict the published 16 SLIDE / 1 STUCK. This was a real
error made and corrected in this session.

## The g128 result: 11 cases, verdict grid-invariant, passthrough worse

Run on Vista node **c642-032** (GH200 120GB) inside idev job 917886, via the
unmodified `run_s2.sh 128` and `run_sweep.sh 128`, both writing to new
directories so the 2026-07-26 overwrite was not repeated.

**All 11 verdicts are identical to their g64 counterparts** (3 masses, 5
velocities, 3 depths), including the single STUCK at v=0.5. `margin_frames`
does NOT converge (m1100 runs 22, 41, 15, 39 across g48/g64/g96/g128), which is
what Syamlal 2017 predicts for a transient quantity.

**Passthrough rose in all 11 cases.** At v=3.0, g64 0.1588 to g128 0.1771.
`sweepD_d0p25` passed at g64 (0.0968) and **fails at g128** (0.1051), so
refinement created a new P-2 failure. **Never offer resolution as the remedy for
passthrough.** `water_layers` rises 4 to 8, retiring the L-3 four-layer
limitation; that measures water-column sampling, passthrough measures the hull
boundary, and only the second needs a boundary treatment.

Artifacts: `data/g128_2026-08-18/` and `data/g128_sweeps_2026-08-18/`. The
`sweepD_g128_*` **metrics.csv were not retrieved**, only summaries.

## The solver's own analytic suite passes, and had never been run

`$WORK/mpm-engine/tests/test_analytic_benchmarks.py`, following the CB-Geo MPM
benchmark suite. **4 passed in 27.99s** on the GH200: Coulomb incline (<15%),
static hold (<0.02 m/s), hydrostatic column basal force (<8%), free-free elastic
bar period (<3%). Reproduce with `scripts/run_analytic_benchmarks_vista.sh <jobid>`.

Its own docstring cautions that two scenes route around measured engine failure
modes and are "characterizations to fix, not physics gates passed".

**PROVENANCE DISCREPANCY, unresolved:** Vista's working copy reported HEAD
`627367e`; this repo vendors `third_party/mpm-engine-544c93dd`. Confirm which
produced any published number.

## Vista operational facts, learned the hard way

- `srun` into a live idev needs `--overlap`, or the step kills the session.
- Vista's submit filter rejects a step missing `-p`, `-N` **or** `-t`, even an
  `--overlap` attach. Full working form:
  `srun --overlap --jobid=<J> -p gh-dev -N1 -n1 -t 00:25:00 bash -c '...'`
- Interpreter is `$WORK/.venv/bin/python3.12`. Default `python3` is 3.9.
- warpmpm imports in ~24 s on a compute node. It BLOCKS on login nodes.
- A three-mass g128 sweep takes about 2 minutes. An 8-run velocity+depth sweep
  takes about 10. These are cheap; do not assume otherwise.
- `run_s2.sh <grid>` and `run_sweep.sh <grid>` both write to `g${GRID}_*` /
  `sweep?_g${GRID}_*`, so a new grid never overwrites an old one.

## Citations

`paper/can_it_ford_references_IEEE.bib` went 21 to 36 entries. All 14
DOI-bearing additions were verified through Scholar Sidekick before commit:
**14 matched, high confidence, 0 mismatch, 0 retracted.** That caught one real
error (Khapane's title uses a hyphen, not a colon). Pazouki has no DOI and is
machine-unverifiable, flagged in its entry.

The four prior fording works are now in the bib. **They are still not in the
paper prose.**

## Permissions and configuration changed

- `disableClaudeAiConnectors` flipped **true to false**. This was the single
  biggest self-inflicted blocker. Connectors still need a session restart plus
  OAuth, which a non-interactive session cannot perform.
- User-level allow list went **6 to 80 rules**, all read-only.
- `Bash(idev:*)` **moved from deny to allow** at Josie's explicit override, with
  `srun --overlap` and `scancel`. Always pass `-m 120`.
- Dropped 4 dead or counterproductive deny rules, including
  `Read(designsafe-staging/**)` which was blocking review of the
  publication-bound tree.
- **Retained:** the `git add -A` family (2026-08-07 incident, concurrent
  sessions), and the `*_DEPRECATED*` / `*_SUPERSEDED*` / `track1_sweep_v2` read
  denials, which are correctness guards.

---

# PART 2: ASKED FOR, NOT DONE

Ordered by what the next session should do first.

## 2.1 The realistic environment. This is the current headline ask.

**There IS a published MPM paper doing nearly this**, and it is uncited where a
reviewer would see it: **`10.1063/5.0276643`**, Zhou, Qing & Wang 2025, *Physics
of Fluids*, "Analysis of tire–pavement viscous hydroplaning based on the material
point method". A tire–water film–pavement FSI model in MPM with a rolling tire.
It refutes any claim that MPM cannot host a real road. **Read it first.**

`.claude/dispatch_prompts/REALISTIC_ENVIRONMENT_PLAN.md` (untracked) already
documents five blockers:

- **B1** The scene is one frictional plane inside a box. Floor at friction 0.55,
  four slip walls at friction 0.0. No camber, crown, curb, gutter, gradient,
  drain or embankment.
- **B2** warpmpm forces a **cubic** domain. A road is long, thin and shallow, so
  a cube spends most cells on empty air. `grid_lim` derives from the hull extent.
- **B3, the deepest** A bounded domain physically cannot measure a slope.
  Conserving volume in a closed box forces redistribution larger than the effect.
  Water running downslope piles at the wall. **Tilting the floor does not work.**
- **B4** The correct instrument is wired but never validated.
- **B5** The literature has not solved it either, so this is a contribution.

**Inlet/outlet is the unlock for B3.** The citation is **Zhao, Bolognin, Liang,
Rohe & Vardon 2019**, `10.1016/J.COMPFLUID.2018.10.007`, "Development of
in/outflow boundary conditions for MPM simulation of uniform and non-uniform open
channel flows", implemented in Anura3D. It adds and removes material points with
appropriate kinematic properties. **This is a translation into warpmpm, not a
port.** It is NOT Kumar's work; that misattribution was corrected on 2026-08-07.
`docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md` exists.

Note the current driver already has a *sustained inflow* of sorts: g128 summaries
report `SCENARIO=STANDING_WATER_SUSTAINED_INFLOW` and an `inflow=` count per
frame that decays to near zero. Read `sim_standing.py` before assuming inflow is
absent; what is missing is a true **outflow**, which is why the domain stays
bounded.

## 2.2 Three vehicle meshes

`--vehicle` **now exists** at `sim_standing.py:310`, so the old blocker is gone.
Rogue and Silverado meshes exist and are simulation-ready. The D5 three-class
matched-dx work (40 runs, 8 arms) lives on branch **`claude/fork-three-class`,
14 commits unpushed**, with `docs/THREE_CLASS_MATCHED_2026-08-14.md` and six CSVs
that are NOT on the current branch.

Traps: at fixed `n_grid`, a different hull changes both `dx` and realized depth,
so a cross-vehicle run is not "same resolution". And every number in the D5 doc
was measured at the 8-frame settle now known inadequate.

## 2.3 Numerics that would improve physical realism, ranked

None implemented. Verified absent from `analysis/` and `simulation/`: **CPDI**,
**GIMP**, **moving-reference-frame MPM**.

1. `10.1002/nme.7217` Baumgarten & Kamrin 2023, spatial-integration-error
   mitigation. Targets particle ringing and solution-dependent integration error,
   "without requiring significant augmentation of existing MPM frameworks".
2. Schulz & Sutmann 2019, **image-particle boundaries**. Grid-momentum-zeroing
   walls "distort the stress multiple grid lengths into the object". **This is
   the candidate fix for the passthrough that refinement made worse.**
3. `10.1016/j.jcp.2016.10.064` hourglass damping and incompressible MPM.
4. `10.1016/j.cma.2022.114809` IFEMP, particle rearranging against numerical
   cavities, sharp immersed interface for real two-way coupling.

**Precondition:** fixed particles-per-cell can lose convergence under refinement.
But note D9 **refuted PPC** as the non-monotone mechanism; band width dominates
and `COLLIDER_FRICTION 0.4` is influential. Any AMR must control band width.

## 2.4 Everything else outstanding

- **239 of 323 abstracts unread.** Extracted per report under the session
  scratchpad; rebuild with `research_index.py --build`.
- **Paper prose.** The bib has the entries; the limitations paragraphs are
  unwritten: AR&R rests on pre-1993 vehicles (`10.1080/15715124.2019.1687487`),
  no experimental basis for the 1.5 m/s rule, published thresholds disagree
  (`10.1111/jfr3.12551`), transient-vs-time-averaged convergence.
- **Overleaf.** `overleaf/main` is `6466dfa` and shares **no ancestor** with
  local `main`, so `git push overleaf main` from this repo **replaces the whole
  project**. Use `~/can-it-ford-paper` (clean, at the Overleaf head, holds
  `conference_101719_1.tex`, flat figure paths). **Rotate the Overleaf token
  first**, it is off local disk but valid server-side.
- **`can-it-ford-demo` `4d228d9`** is single-copy and unpushed; the public demo
  still serves the superseded bare-hazard-product L1 rule.
- **Analytical gate half-armed.** `tests/data/poiseuille_profile.csv` does not
  exist, so the free-surface comparison skips.
- **`sweepD_g128_*` metrics.csv** not retrieved from Vista.
- **W&B, HuggingFace, Gradio** unblocked but unauthenticated.
- **Claude chat receives nothing.** The Project syncs from
  `jcerrell-IS/mpm-engine`, a fork of `kks32/mpm-engine`, **not** this repo.
  Committing here never reaches it. Paste Snippet 2 from
  `~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/MEMORY_UPDATE_PASTE_BLOCK.md`.
- **`claude-md-improver` and `cowork-plugin-customizer` never run**, deliberately:
  CLAUDE.md is 800+ lines, dirty, with a concurrent session live.
- **Photorealistic rendering untouched.** This Mac has **no render stack**:
  numpy, scipy, matplotlib, trimesh, pyvista, skimage all absent. The eight
  `renders/yaris_render_s1/render_*.py` are all untracked.
- **vPIC, USGS/NOAA, RO-Crate, Apptainer `.def`, Zenodo** all absent. vPIC would
  source the unsourced 1609 and 2337 kg masses; USGS would ground the 3.0 m/s cap
  that is currently administrative.
- **Nothing pushed.**

---

# PART 3: PROMPT FOR THE NEXT SESSION

Paste everything below into a fresh Claude Code session in `~/can-it-ford`.

---

Read `docs/HANDOFF_2026-08-18_REALISTIC_ENVIRONMENT.md` in full before doing
anything. It is the state of play. Then read `CLAUDE.md`, and load the
`research-corpus` skill.

**Your goal: make the simulation physically realistic and renderable as a real
flooded roadway, by removing the bounded-box artifact and using all three
vehicle meshes.** Work in dependency order, and verify each step before moving
on.

**Standing constraints, non-negotiable.** Another Claude Code session may be
live in this tree: re-check `git status` immediately before every commit, stage
explicit paths only, never `git add -A` or a bare directory. Any push, force
push, delete or overwrite needs Josie's explicit confirmation; the repo is
PUBLIC and six credentials are unrotated. Never quote a number you have not
measured live this session. No em-dashes anywhere.

**Order of work.**

1. **Read `10.1063/5.0276643`** (Zhou, Qing & Wang 2025, tire–pavement viscous
   hydroplaning in MPM). It is the closest published prior art to what you are
   building and it is uncited in `paper/`. Find out specifically **how they
   expressed a road surface inside an MPM grid**, because that is blocker B2.
   Add it to the bib and verify it with Scholar Sidekick before committing.

2. **Read `sim_standing.py` end to end** before changing anything. It already
   reports `SCENARIO=STANDING_WATER_SUSTAINED_INFLOW` with a per-frame `inflow=`
   count, so inflow partly exists. Establish exactly what exists and what does
   not. **Do not edit `sim_standing.py` in place**: its sha256 stamps 40 D5 runs.
   Use a wrapper or a new driver and say which.

3. **Implement outflow, then inflow, per Zhao et al 2019**
   (`10.1016/J.COMPFLUID.2018.10.007`), which adds and removes material points
   with appropriate kinematic properties. Read
   `docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md` first. This is the unlock for
   blocker B3, that a bounded domain cannot measure a slope. Validate against
   their reported end-depth ratio and pressure distribution for free overfall,
   not against a screenshot.

4. **Only once outflow works, attempt road geometry.** B2 says warpmpm forces a
   cubic grid, so establish how the hydroplaning paper handled that before
   designing. Camber, crown and a gutter are the minimum for a road to read as a
   road.

5. **Run all three meshes.** `--vehicle` exists at `sim_standing.py:310`. First
   check out `claude/fork-three-class` and read
   `docs/THREE_CLASS_MATCHED_2026-08-14.md`: 14 commits of matched-dx work are
   unpushed there. Do not repeat it. Note every number in it was measured at the
   inadequate 8-frame settle, and at fixed `n_grid` a different hull changes both
   `dx` and realized depth.

6. **Fix passthrough with a boundary treatment, not resolution.** Register J18
   and J19 show refinement makes it worse in all 11 g128 cases and created a new
   failure at `d0p25`. Implement image particles (Schulz & Sutmann 2019), then
   re-measure `passthrough_max_frac` against the g64 and g128 baselines already
   in `data/g128_*`.

7. **Apply the settling protocol to every new run.** Use
   `analysis/stationarity.py` and `analysis/settle_audit.py`. Never quote a fixed
   settle length. Never compute uncertainty from frame count; use `N_eff`.
   Report verdicts with `analysis/probabilistic_verdict.py` and state the
   probability cut.

8. **Then, and only then, photorealism.** Better shading on a flat plane in a box
   is not realism. The rendering stack does not exist on the Mac, so this is a
   Vista job.

**Vista.** Node c642-032 may be gone; check `ssh vista squeue -u $USER`. Start a
bounded node with `idev -m 120`. Attach with
`srun --overlap --jobid=<J> -p gh-dev -N1 -n1 -t 00:25:00 bash -c '...'`; all
four flags are required by the submit filter and `--overlap` is mandatory or the
step kills the session. Interpreter is `$WORK/.venv/bin/python3.12`; do not
mutate that shared venv. A three-mass g128 sweep costs about 2 minutes, so
iterate freely, but check SUs first; the cached figure was 626 and is stale.

**Before you claim anything is novel or untried**, run
`python3 analysis/research_index.py --query <topic> -v`. 332 papers are indexed
and only 43 reach a reader-facing document. This project has already almost
published a novelty claim contradicted by four papers in its own corpus.

**Finish by** updating this handoff, appending to
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` in its own style, and telling
Josie plainly what you did not get to.

---

# PART 4: THE COMPLETE RESEARCH INVENTORY, WITH PATHS

Everything below was located live on 2026-08-15 and is indexed in
`data/research_corpus_index.json`. Query it rather than re-walking the disk.

## Undermind deep-research reports, 8, 426 catalog rows, 323 abstracts

All in `~/Downloads/` except the last:

    Reliable_AI_Scientific_Software.md                       79 papers
    MPM_Simulation_Verification_Provenance.md                68
    Multi-resolution_MPM_for_Large-domain_Flooding.md        78
    Settling_and_Force_Reporting_in_Free_Surface_Flow.md     68
    Validated_MPM_Vehicle_Water_Coupling.md                  60  (+ divergent "(1)" copy)
    Moving_Rigid_Body_Free_Surface_Validation.md             44
    Quantitative_MPM_Wall_Penetration.md                     16
    UNDERMIND_FINDINGS_DEPLOYMENT_ORDER_2026-08-08.md        synthesis, read first
    ~/Claude/Projects/SCIPE UT Austin baby/REU_Knowledge/Trustworthy_AI_Assisted_Scientific_Simulation.md   13

**Each report details only its TOP 50.** 103 of the 426 have no abstract
anywhere on disk. Never describe those as read.

## Claude.ai artifacts, 288 files collapsing to 37 distinct ids, 30 on-topic

Roots: `~/Claude/reu` (73 files), `~/Documents/Claude/reu` (70),
`~/Documents/Claude/Projects/SCIPE UT Austin baby/REU_Knowledge` (123 compass
files), `~/Downloads` (37). The 6-to-9-copy spread is the macOS sync-cache
signature; the index dedupes by content hash.

Subject index at `<corpus>/00_COMPASS_ARTIFACT_SUBJECT_INDEX_v2_2026-08-14.tsv`.
The three most relevant to configuring Claude itself are `62a7f8e6` (AI research
tools and infrastructure), `2c1e05ae` (configuring Claude across five surfaces,
ROI-ranked), `aae75abf` (Claude Code configuration and remediation plan).

## Perplexity reports, 5

`~/Downloads/perplexity research on claude gaps/`:
`citation_verification_report.md`, `drift_threshold_citation_research.md`,
`genesis-gh200-report.md`, `genesis-mpm-flood-sim-parameters.md`,
`physgaussian_bridge_findings.md`. All dated 2026-07-07, so Genesis-era: treat
engine-specific content as superseded, citation content as live.

## Elicit, 2

`citations/Elicit - extract-results-review-*.csv` and
`citations/Elicit - Flood-Crossing Tire-Ground Friction and Speed Evidence.bib`.

## The corpus

`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/`, ~6,500 manifest rows,
`00_CANONICAL_REPO` pointing at `~/can-it-ford`, and
`MEMORY_UPDATE_PASTE_BLOCK.md` whose Snippet 2 is the only route into Claude chat.

---

# PART 5: WHAT IS NOT INSTALLED THAT THE RESEARCH CALLS FOR

Measured 2026-08-18. **Correction to an earlier statement in this session:** I
first reported "no render stack on this Mac" after checking only the SYSTEM
interpreters. That was wrong. `~/can-it-ford-env/bin/python` has:

    numpy 2.5.1    matplotlib 3.11.1    pandas 3.0.5
    scipy ABSENT   trimesh ABSENT   pyvista ABSENT   skimage ABSENT   warp ABSENT

`uv`, `pip3`, `brew` and `ffmpeg` are all present. The stale memory note "no Mac
python has numpy" applies to the SYSTEM interpreters only and should be corrected.

**To render locally you need:** `trimesh` (hull loading), `pyvista` (3D render,
what `render_pv*.py` import), `scipy` and `scikit-image` (surface extraction).
Install into `can-it-ford-env`, never into the shared Vista venv.

**Called for by the research and entirely absent:**

| Item | Why | Fixes |
|---|---|---|
| **NHTSA vPIC** client | class-specific geometry, not mass alone | the unsourced 1609 and 2337 kg masses |
| **USGS / NOAA water APIs** | realistic depth-velocity parameterisation | the 3.0 m/s cap being administrative, L-2 |
| **RO-Crate** | FAIR packaging for DesignSafe | register J10, DOI pending |
| **Apptainer `.def`** committed | reproducibility, Apptainer is TACC's container system | no `.def` in the repo |
| **Zenodo DOIs** | citable code and container beside the data DOI | nothing minted |
| MLflow, Connected Papers, NotebookLM | lower priority, flagged as heaviest lifts | |

---

# PART 6: PERMISSIONS AND ACCESS STILL TO REVISE

Done this session: `disableClaudeAiConnectors` true to false; user allow list 6
to 80 read-only rules; `idev` deny to allow with `srun --overlap` and `scancel`;
four dead or counterproductive deny rules dropped.

**Still blocking:**

1. **Connectors need a session restart plus OAuth.** A non-interactive session
   cannot run the flow. W&B, HuggingFace, Gradio and the `plugin:engineering:*`
   and `plugin:data:*` sets stay unavailable until Josie authorises them in
   claude.ai connector settings, or via `claude mcp` or `/mcp` interactively.
   **Do not ask her for tokens.**
2. **`.claude/settings.json` and `.mcp.json` are uncommitted** and mix this
   session's permission changes with another session's `commit_autoapprove` hook
   and three MCP servers. Review and commit deliberately.
3. **`pre-push` requires `PUSH_OK=1`**; eleven commits are unpushed.
4. **Retained deliberately:** the bulk-staging deny family (`git` `add` with `-A`, `--all` or `.`), and the `*_DEPRECATED*`,
   `*_SUPERSEDED*` and `data/track1_sweep_v2/**` read denials, which are
   correctness guards rather than access limits.

---

# PART 7: MAKE THE REPO MATCH WHAT THE PAPERS ESTABLISH

None of these is yet applied to the paper text or the scripts.

1. **Grid refinement does not converge a transient quantity.** Syamlal, Celik &
   Benyahia 2017, `10.1002/AIC.15868`. Stop presenting non-monotone
   `final_disp_mag_m` as a defect. Report a time-averaged observable over a
   demonstrated-stationary window with a GCI, or say it is not expected to
   converge.
2. **Report a movement probability, not a bare label.** Dancey et al 2002.
   17 of 24 runs flip somewhere in p >= 0.01 to 0.50.
3. **Never compute uncertainty from frame count.** N_eff is 2.9 to 11.0 of 91.
4. **Added mass is not constant during acceleration.** Grift et al 2019,
   `10.1017/jfm.2019.102`, define an entrainment rate, and measure steady drag
   rising 45 percent at one-fifth-height submergence. The surge the SLIDE
   verdicts live inside is exactly this regime.
5. **AR&R rests on pre-1993 vehicles.** Shah et al 2019,
   `10.1080/15715124.2019.1687487`.
6. **Published stability thresholds disagree.** Bocanegra et al 2019,
   `10.1111/jfr3.12551`.
7. **No experimental basis for the 1.5 m/s rule** exists in the corpus. Say so.
8. **Unsteady flow raises drag 40 to 50 percent** (Azhar 2026), unmodelled, and
   a realistic environment makes it worse.
9. **Order-dependent reductions can flip a discrete gate.** SLIDE / STUCK / FLOAT
   is such a gate. Xu et al 2019 `10.1016/J.PARCO.2019.04.002`, Siklosi et al
   2024 `10.3390/app14020639`.
10. **Resolution is not the remedy for passthrough.** J18 and J19, measured.

---

# PART 8: EXPANDED PROMPT, SUPERSEDES PART 3 WHERE THEY CONFLICT

Read Parts 1 to 7, then `CLAUDE.md`, then load the `research-corpus` skill.

**PRIORITY: a photorealistic, physically accurate flooded-roadway simulation and
render.** Everything else serves that. Work in dependency order; do not skip to
rendering.

**Phase A, read and index.** Read `UNDERMIND_FINDINGS_DEPLOYMENT_ORDER_2026-08-08.md`,
then `10.1063/5.0276643` (tire-pavement hydroplaning in MPM, the closest prior
art), then the 239 abstracts not yet read. Use
`python3 analysis/research_index.py --method <tag> -v` rather than re-walking
`~/Downloads`. Append findings to `docs/RESEARCH_TO_IMPLEMENTATION_2026-08-15.md`.
Add every method paper you act on to the bib and **verify with Scholar Sidekick
`auditBibliography` before committing**; that caught a real title error this
session.

**Phase B, install and enable.**
`~/can-it-ford-env/bin/python -m pip install trimesh pyvista scipy scikit-image`.
Never touch the shared Vista venv. Then tell Josie which connectors to authorise.

**Phase C, unbound the domain. The physics unlock.**
Implement outflow then inflow per **Zhao, Bolognin, Liang, Rohe & Vardon 2019**,
`10.1016/J.COMPFLUID.2018.10.007`, which adds and removes material points with
appropriate kinematic properties. Read `docs/OPTION_A_INFLOW_OUTFLOW_BC_PLAN.md`.
The driver already reports `SCENARIO=STANDING_WATER_SUSTAINED_INFLOW` with a
per-frame `inflow=` count, so establish what exists first. **Outflow is the
missing half**, and it makes blocker B3 tractable: a bounded domain cannot
measure a slope because conserving volume forces redistribution larger than the
effect. **Do not edit `sim_standing.py` in place**; its sha256 stamps 40 D5 runs.
Use a wrapper or a new driver and say which. Validate against Zhao's reported
end-depth ratio and pressure distribution, not a screenshot.

**Phase D, the road.** Only after outflow works. warpmpm forces a cubic grid
(B2), so learn from `10.1063/5.0276643` how they expressed a pavement surface.
Camber, crown and a gutter are the minimum for a road to read as a road; surface
roughness is an explicit variable in that paper.

**Phase E, the three vehicles.** `--vehicle` exists at `sim_standing.py:310`.
**First check out `claude/fork-three-class`** and read
`docs/THREE_CLASS_MATCHED_2026-08-14.md`: 14 unpushed commits, 40 runs. Do not
redo it. Two traps: every number there used the inadequate 8-frame settle, and at
fixed `n_grid` a different hull changes both `dx` and realized depth, so a
cross-vehicle run is not "same resolution".

**Phase F, fix passthrough properly.** Refinement makes it worse in all 11 g128
cases and created a new failure at `d0p25`. Implement **image particles**,
Schulz & Sutmann 2019, targeting the stress artefact that smears multiple grid
lengths into the body. Re-measure `passthrough_max_frac` against the baselines in
`data/g128_*`. Consider `10.1002/nme.7217` alongside.

**Phase G, render.** Only now. The eight `renders/yaris_render_s1/render_*.py`
are untracked; read before editing, commit what you keep. Render from g128 or
finer: `water_layers` is 8 there against 4 at g64. Realism comes from the
resolved surface, the real road and the correct hull, not from shading.

**Throughout.** Apply `analysis/stationarity.py` to every new run; never quote a
fixed settle length; never compute uncertainty from frame count. Report verdicts
with `analysis/probabilistic_verdict.py` and state the probability cut. Run
`python3 tests/test_physics_gates.py` and the three `.claude/checks/` scripts
before every commit. Re-check `git status` immediately before each commit, stage
explicit paths, never a bare directory. No push without Josie's explicit yes.
Query the index before claiming anything is novel or untried.
