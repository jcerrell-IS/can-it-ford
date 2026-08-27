## Compact Instructions
When summarizing this conversation: preserve the full VERIFIED/CONTRADICTED/REPLACED
ledger in exact form, preserve the list of every file touched with old-string and
new-string, preserve the TodoWrite task count vs. completed count. Do not summarize
these away even under aggressive compaction.

## Multi-Pane Standing Rules

These apply to every pane in every session automatically, do not
restate them in chat prompts.

- DO NOT CITE THIS FILE POSITIONALLY. Quote the section heading and the
  sentence, never `CLAUDE.md:NNN`. Added 2026-08-18 after the rule proved
  itself inside one hour: a session was given corrected line numbers for two
  claims, this file was then edited, and the same two claims moved again, so
  three different line numbers existed for them within the hour. The edit that
  invalidated them was itself the commit fixing a STALE LINE NUMBER elsewhere
  in this file. Line numbers here are cited by other people verbatim and this
  file changes several times a night, so a positional citation is stale on
  arrival. The identical rule already existed for `.gitignore` below; it
  applies to this file for the same reason and more strongly.

- Never fabricate a command, parameter, or claim. Pull from actual
  file content, actual output, or actual verified search results.
  This includes a prior claim from Claude itself, verify independently
  rather than trust at face value.
- `grep` IN THIS ENVIRONMENT IS NOT `grep`. Confirmed live 2026-08-07
  by `declare -f grep`: it is a shell function wrapping ugrep with
  `--ignore-files`, so it SKIPS EVERY GITIGNORED PATH. `data/*` and a
  `renders/*` pair are among the rules, so a
  repo-wide `grep -rn "pattern" .` silently omits most of
  renders/yaris_render_s1/ and most of data/. An absent hit is NOT
  evidence of absence.
  THE OLD "5 hits from `.` and 7 when renders/ was named" MEASUREMENT
  IS WITHDRAWN, 2026-08-12. It never named the pattern, so nobody can
  re-derive it, and the 2026-08-12 carve-out invalidated its premise
  anyway: the shell `grep` now reaches 22 previously-hidden .py files,
  so the gap it measured no longer exists in that form. Re-measure with
  a named pattern before quoting any figure here. For any
  inventory or audit claim, use `/usr/bin/grep -rn`, or name renders/
  and data/ explicitly, and exclude ./third_party/ and
  ./.claude/worktrees/.
  LINE NUMBERS UPDATED 2026-08-12, and the rule they describe CHANGED.
  This clause used to read "`.gitignore:14` is `renders/`". The blanket
  `renders/` was replaced that day by a walk-down carve-out, because it
  was also hiding 24 SOURCE scripts, among them sim_standing.py and
  vehicle_live.py, which this file cites by file:line as the primary
  source for A1, A2, A5 and F5 and which implement the Contribution 1
  code. Those 24 .py files are now UN-IGNORED, so the shell `grep`
  reaches them and the H0 blind spot no longer covers them. Generated
  output under renders/ is still ignored, so the H0 warning still
  applies to metrics.csv, frames and every other artifact.
  DO NOT READ "un-ignored" AS "tracked". Corrected 2026-08-12 after an
  independent check caught this exact conflation here: only 2 of the 24
  are tracked, sim_standing.py and vehicle_live.py, committed in
  00b735c. The other 22, including gates.py, gates_all_runs.py and
  gates_both_scenarios.py, are visible to grep but still UNTRACKED and
  still have no commit history. Verify with
  `git ls-files --cached -- renders/yaris_render_s1/` before citing any
  of them as having provenance.
  The carve-out is also TOP-LEVEL ONLY. A second copy of the driver
  exists at renders/yaris_render_s1/_incoming/sim_standing.py and is
  STILL ignored by the `renders/yaris_render_s1/*` rule, which
  `git check-ignore -v` will locate for you; do not cite its line
  number, see the .gitignore note below. "sim_standing.py is no longer
  hidden" is true only of the top-level copy, and register D4a records
  `_incoming/` as the canonical per-run tree, so check which copy you
  are reading.
  RE-MEASURED 2026-08-20 AND THE 2 IS NOW STALE IN THE OTHER DIRECTION.
  This clause read "`./.claude/worktrees/` holds 2 directories, not 27, so
  the multiplies-every-hit-~20x figure is stale". Live today,
  `git worktree list` returned **33 worktrees, 28 of them under
  `.claude/worktrees/`**. So the exclusion is load-bearing again and the
  ~20x inflation is real again. The lesson is the clause itself: this
  number has now been wrong in both directions within eight days, so
  RE-MEASURE IT rather than quoting any figure here, including 28.
  RE-MEASURED 2026-08-25 AND 33/28 IS NOW STALE TOO, WHICH IS THE THIRD
  DIRECTION CHANGE. Live: **11 worktrees, 6 of them under
  `.claude/worktrees/`**. The exclusion still matters but the ~20x figure
  does not describe it any more. Do not quote 33, 28, 11 or 6; run the
  command. The clause has now been wrong three times in twelve days,
  which is the point it is making about itself.
  And `./can-it-ford/` no longer exists, so excluding it is now a no-op,
  see the section below.
- Any parameter assigned to a variable (rho, coup_friction, box
  dimensions, mass, thresholds) must trace to a primary source before
  being written into a script or command.
- Do not accept a physical result on intuition. State the formula or
  law used, do a units check, and compare against these anchors: water
  1000 kg/m^3, vehicle effective density 310.494 kg/m^3 for the canonical Yaris hull, the 100-300 band is STALE, sedan
  mass 1000-1600 kg, g=9.81, realistic depth 0-1.0m, velocity
  0-3.0 m/s. coup_friction IS the Coulomb friction coefficient in the
  LegacyCoupler MPM-rigid momentum exchange
  (genesis/engine/couplers/legacy_coupler.py:322), applied as
  |v_t_new| = max(0, |v_t| - mu*|v_n|). The separate numerical
  regularisation parameter is coup_softness, default 0.002. Confirmed
  2026-08-05 by direct source read, superseding all earlier statements
  that coup_friction was numerical-only.
- grid_density >= 96 is NOT the crash threshold and 64 is NOT
  confirmed safe. Replicated bisection 2026-08-05 found gd 80 and 88
  pass 3/3 at 60 steps, gd 90+ fails, non-monotone above the boundary,
  non-deterministic at fixed config. Before citing any grid_density
  as safe, check docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md section C2.
- Before treating any claim in this file as settled: a claim cited
  from another session's confidence, a skill file, or a prior audit's
  conclusion is not a second source, it is the same source cited
  twice. Only a primary-source line, a runtime read, or a replicated
  control counts as verification. Before archiving or superseding any
  dated audit file, pull its VERIFIED-tier findings into
  docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md first, the file can
  go stale, the facts inside it should not disappear with it.
- For any rendered output: water reads as one connected fluid body,
  vehicle position matches its known density, no particles outside
  domain or clipped through geometry, motion continuous across frames.
- rho, coup_friction, box dimensions, mass, and grid resolution are
  coupled. Never flag a value as wrong by pattern-analogy to a
  different script's bug, recompute against the actual script's own
  geometry.
- Never let two panes touch the same file, branch, or process without
  explicit sequencing. ACTIVE BREACH 2026-08-07: two Claude Code
  sessions edited this working tree simultaneously and one committed
  the other's uncommitted edits inside 0797b08 and 3470ff9 without
  either knowing. Read docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md
  before touching scripts/check_claims.py, CLAUDE.md or the register.
  If you see edits appear in a file you did not write, the default
  assumption is ANOTHER SESSION, not a linter and not the user.
- Never run `git add -A`, `git add .`, or `git commit -a` in this repo.
  Stage explicit paths. A shared working tree means -A captures another
  session's in-progress work and commits it unreviewed under your
  message. This is not hypothetical, it happened on 2026-08-07.
- Any git push, force-push, file delete, or overwrite of an existing
  file requires explicit confirmation before execution.
- Every prescribed task should trace to the poster (July 27), the
  paper (July 31), or a verified rendered physically-plausible MPM
  simulation with a vehicle. Flag anything else as optional/deferred.
- If a specific pane's blocking issue persists unresolved across 3+
  rounds, stop re-prescribing the same diagnostic, escalate to
  Cristian Moran per the 15-minute-stuck rule.
- Prefer event-driven pane signaling over polling: same machine, tmux
  wait-for; same machine automated, a Claude Code Stop hook;
  cross-machine, ntfy.
- Before prescribing idev/GPU allocation, confirm the task actually
  needs GPU. File checks, git operations, and monitoring belong on the
  login node, not inside idev.
- Before asserting any parameter, threshold, citation, mesh property, or
  milestone as fact, read docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md.
  Section I lists claims already proven false. Section E is the vehicle
  asset inventory: there is ONE usable mesh, not three. The July 24
  ledger is historical only and its L1 counts predate the joint-rule fix.

- WHERE A NEW FINDING GOES, added 2026-08-19. This file is the CONSTITUTION:
  standing rules, hard prohibitions, and environment truth. It is NOT the place
  for a dated finding. A finding from one night goes in `docs/` and gets ONE
  line here only if it changes a standing rule. The reason is measured, not
  stylistic: a worktree carries the CLAUDE.md from ITS branch point, so every
  line added here is a line that silently diverges across every live worktree.
  On 2026-08-19 this file went from 906 to 983 lines in one evening and opened a
  77-line gap against nine live worktrees while they were reading it. A
  constitution that changes rarely is one a worktree freezes harmlessly. See
  docs/R9_COORDINATOR_AUDIT_2026-08-19.md for the measurement.


## MOVED OUT OF THIS FILE 2026-08-26, with every operative rule kept here

Three dated audit blocks, **710 lines**, were moved VERBATIM to
`docs/CLAUDE_MD_MOVED_SECTIONS_2026-08-26.md`: the August 4 ground-truth audit with
its August 5 literature review (was lines 162-605), August 5 Research Integration V2
(632-650), and the August 8 literature addendum with both August 15 blocks (700-946).
Nothing was summarised or dropped, the move was verified block by block against the
pre-move sha256, and that file records the provenance. **Read it for the working
behind any rule below.**

Why: this file is the CONSTITUTION, per "WHERE A NEW FINDING GOES" above, and a
worktree carries the `CLAUDE.md` from ITS branch point. Measured live 2026-08-26
before the move: this file was 1055 lines against nine live worktrees at 390 to 859,
**a worst gap of 665 lines, 8.6x the 77-line gap that was already recorded as the
defect on 2026-08-19.** Cite anything in the moved file with its own date. Where it
conflicts with the register, the register wins.

### The rules those sections were FOR. These bind. The evidence is in the moved file.

**Engine and scene identity**
- The 17 gated runs are **warpmpm** via `renders/yaris_render_s1/sim_standing.py`, NOT
  Genesis. Genesis is the abandoned box-proxy path only, and no Genesis scene has ever
  loaded the Yaris hull. Never label the 17 runs Genesis in a figure, caption, README,
  poster or paper.
- Velocity enters as a per-frame Dirichlet clamp on an upstream slab plus a one-shot
  additive kick. It is NOT a boundary condition and NOT a mass inflow. Particle count is
  fixed at load; nothing is created or destroyed during a run.
- The vehicle is a free rigid body. Constraints are the floor plane at friction 0.55 and
  four slip walls at friction 0.0.
- Gravity is **9.81 m/s^2** in all 17 runs. It is a solver DEFAULT, not a constant: a
  caller-supplied `g` wins. The conclusion is unchanged because the canonical driver
  passes no override. Exactly one 9.80665 survives, at
  `analysis/viability_dashboard_scaffold.py`, where `G` is assigned and never read, so it
  is dead code and cannot reach a verdict.

**Parameters, and one hard prohibition**
- `inertia_kg_m2`, `cg_height_m` and `ssf` never reach the solver. **DO NOT WIRE THEM.**
  The absence is correct, not a gap, and `.claude/checks/params_check.py`
  `check_inertia_wired()` enforces it. The measured Yaris tensor on slide 7 of DOI
  10.13021/G8JS5D puts the solver's own particle cloud within 2.3 percent and the box
  fallback 19 to 26 percent off. The axes are also transposed: the hull's long axis is on
  Y, so a naive write gives Ixx -69.2 percent and Iyy +379.2 percent.
- Three incompatible vehicle densities are live in the repo at once, and the 17 runs
  realise a fourth set. The canonical Yaris hull is **310.494 kg/m^3**; the 100-300 band
  is STALE.
- **1609 kg and 2337 kg have no source.** Do not describe the mass sweep as spanning cited
  vehicle classes.
- `EXT_REF` in `gates.py` differs from `bbox_m` in `vehicle_params.py` by 3.3 percent in
  height and 2.7 percent in width, both larger than gate G-1's own 2 percent tolerance.
- `gates.py` forks the AR&R table and `L1_verdict` instead of importing. Values agree
  today. Fork risk.

**DRIFT_THRESHOLD, the count that keeps moving**
- 0.05 m is declared under **FIVE names**: `DRIFT_THRESHOLD_M`, `L2_DRIFT_M`,
  `DRIFT_THRESHOLD`, `DRIFT_M`, `THRESHOLD`. FIVE is settled. **THE TOTAL IS NOT, and it
  is scope-sensitive, so never quote a total without its scope.** Two independent binary
  choices (include `archive/` or not; count the `gp_surrogate.py` CLI default or not) give
  22, 23, 23 and 24, and 23 is reachable two ways.
  `.claude/checks/count_claims_check.py` accepts 22, 23 or 24. Do not cite 16.
- `failure_modes.py` carries THREE 0.05 literals across TWO units: `slide_m` metres,
  `slide_speed_ms` **metres per second**, `float_m` metres. **Deduplicate by NAME and
  UNIT, never by value.** A find-and-replace on "0.05" silently converts a speed into a
  distance and changes the 16 published SLIDE verdicts.
- Re-measure any such count with a Python `re` walk that PRINTS every path. Three
  different commands gave three answers on the same tree.

**What the gates do and do not prove**
- **No gate is a physics validation.** Every gate is a self-consistency or
  numerical-containment check. G-3 compares against a constant derived from the same
  pipeline, so it cannot fail for a reason external to the code. G-6, P-4 and P-5 print
  with no pass criterion at all.
- Seven of the 17 runs fail gate P-2, and the failure rate rises monotonically across the
  velocity sweep. All three g48 runs also fail P-3: the hull sank into the floor.
- The grid convergence study is **non-monotone and unconverged**. The binary verdict is
  grid-invariant, all nine NO-FORD. **Cite the verdict, never the displacement
  magnitude.** Two disagreeing displacement measures differ by 3.4 percent for g64_m1100.
- `gates_results.json` holds 3 dry_start records and is NOT a 17-run store. The 17-run
  stores are `gates_results_all_runs.json` (20 records) and `data/all_runs_inventory.csv`
  (exactly 17).
- Verdicts are **16 SLIDE and 1 STUCK**, and that count is THRESHOLD-DEPENDENT. Never
  quote it bare; quote the thresholds with it. Three traps survive: `triggered_*` is the
  verdict and `ratio_*` is peak magnitude and they disagree; STUCK is the none-sustained
  case, not a fourth mode; the classifier reads the same `metrics.csv` the tables were
  built from, so it can never be independent confirmation.

**Settle length, stationarity and sample size**
- `sim_standing.py` uses `settle_frames=8` and **25 of 25 runs need more than 8 frames
  discarded**, min 29, median 48, max 80 of 91.
- **N_eff is 2.9 to 11.0**, so uncertainty computed from N=91 is overstated 3x to 5x. Use
  `effective_sample_size`, never the frame count.
- **DO NOT REMOVE THE TRANSIENT BEFORE A SLIDE VERDICT.** Incipient motion is an EVENT.
  Removing it drops SLIDE from 21 of 24 to 5 of 24 and silently contradicts the published
  result. `--stationary-window` is a robustness diagnostic only.
- MSER minimises standard error, which is NOT stationarity. Report both.
- Grid refinement does not converge a transient quantity (Syamlal, Celik and Benyahia 2017,
  `10.1002/AIC.15868`). If grid convergence is the claim, report a time-averaged observable
  over a demonstrated-stationary window with a GCI.

**Literature constraints on what may be claimed**
- AR&R and Shand thresholds describe a **STATIONARY vehicle**, stated in the primary
  sources. The tank scenario is the correct match. The word "ford" in the title is what
  mismatches, not the setup.
- The 3.0 m/s cap is **administrative**, set below human-stability curves. Not
  vehicle-derived.
- No accepted particle force-convergence criterion exists for MPM. Rules of thumb are
  ~10 particles per flow depth; g64 has 4 particle layers and exactly 2 grid cells. State
  it as a limitation, not a converged resolution.
- Coarse resolution **usually** over-predicts peak hydrodynamic force, but a
  counter-example exists (Smith and Mack 2014 in WRL 2014/07 section 6.3.2, under-predicted
  at 1 m, 5 m and 10 m). **Never use this alone to argue the published verdicts are
  safe-side.**
- Cite Steffen, Kirby and Berzins 2008 for MPM losing convergence under refinement at fixed
  particles-per-cell.
- The simplest-sufficient-abstraction principle is established prior art. Do not claim
  novelty for it.
- arXiv 2607.00673 covers reconstruction plus MPM plus route feasibility. The novelty here
  is the validation step, not the pipeline.
- **Engine decision: do not switch.** NVIDIA Warp is the only engine confirmed for aarch64
  plus Hopper. The x86-only DualSPHysics reason is UNVERIFIED and must not be restated as
  established; Chrono::FSI-SPH builds and runs on Vista aarch64 in 94 seconds.
- In/outflow BCs are **Zhao, Bolognin, Liang, Rohe and Vardon 2019**,
  `10.1016/j.compfluid.2018.10.007`, NOT Kumar. Implementing in warpmpm is a translation,
  not a port.
- No flood-vehicle study shows resolution moving the stability threshold. Never cite one as
  proof that it does.
- Artificial sound speed can qualitatively flip a rigid-body outcome (Isik and He 2022).
  Unsteady flow raises drag 40 to 50 percent (Azhar 2026).

**Coupling architecture and the SDF range**
- The 17 runs use the **material-8 free-rigid path**, a mass-weighted grid velocity average
  with **no force accumulator**. Hu et al 2018 (`10.1145/3197517.3201293`) and Pazouki et al
  2016 describe real two-way coupling as requiring accumulated contact force. This is a
  documented architecture choice with a literature-backed alternative. It does NOT change
  any of the 17 verdicts and does NOT clear them.
- **The SDF error range is 7.3 to 7.7 percent, NOT 1.6 to 7.7.** The stray 1.6 is a
  conflation with the free-rigid late-window fit, which measures the path being criticised
  rather than the validated one. Never merge the two ranges.
- Buoyancy, drag and lift lever arms and the sliding, float and roll thresholds depend on
  displaced volume, underbody shape, wheelbase, track and CoM, **not mass alone**.
- Watertightness materially shifts flotation depth (Kramer 2016
  `10.1016/J.IJDRR.2016.04.003`; Azhar 2026 `10.1111/jfr3.70181`). **Do NOT pair these with
  the solidify_watertight fix until register E2 is resolved**: the pipeline samples the mesh
  to 60,000 surface points before solidifying, so watertightness does not propagate.

**The research corpus, before asserting novelty**
- **Before claiming a method is untried, a result novel, or a citation needed, QUERY THE
  INDEX.** Load the `research-corpus` skill or run `analysis/research_index.py`. Do not
  quote a count from memory; run `--stats`.
- **"REACH" IS NOT "CITED".** They are different predicates measured by different means.
  Report them separately and state the scope, which is sensitive to whether
  `.claude/worktrees/` is excluded (it must be).
- **The corpus is NOT a superset of the bibliography.** Corpus coverage cannot answer what
  the paper cites, and the index cannot report this about itself.
- A record count is not a works count. Re-run the duplicate census rather than carrying any
  pair forward.
- Prior vehicle fording or wading simulations exist and `paper/` cites NONE of them.
  **NEVER STATE A TOTAL. STATE A FLOOR WITH ITS NAMED VIEW.** This count has read four,
  then eight or nine, then sixteen, and the live index tags **13** under
  `--method vehicle-fording` (2026-08-25 build), of which roughly 11 to 12 are
  simulations and one is a trafficability-criteria paper. The "16" is ONE view's floor
  from `docs/R8_PRIOR_ART_2026-08-18.md`, which says verbatim "at least 16 from the
  catalogs, plus 16 more from one graph hop, plus 8 from the author sweep. Treat as a
  floor, never a total." Do not write "16 across three views"; that misreads the source
  and drops its own caveat. Verified by adversarial review 2026-08-26, see
  `docs/ADVERSARIAL_REVIEW_BACKLOG_2026-08-26.md` D1 and D3.
- The four named prior works (He 2026 `10.1115/1.4071177`, Wasfy 2015
  `10.1115/DETC2015-47142`, Khapane 2014 `10.4271/2014-01-0936`, Al-Qadami 2022
  `10.1111/jfr3.12828`) are 4 of 4 present in the corpus and **0 of 4 in the submitted
  bibliography and 0 of 4 `\cite`d**, re-verified live against `overleaf/main`
  2026-08-26. `cited_reader_facing=True` on all four means the DOI string appears in
  `docs/`, NOT that the paper cites them. Never upgrade that field to "cited".
- **Never quote Al-Qadami's D x V without naming the paper.** `10.1111/jfr3.12828` (2022)
  gives 0.39 m^2/s and the same group's `10.3390/su151713262` (2023) gives 0.36 m^2/s. The
  0.38 m depth agrees in both; the D x V does not.

**Vista, verified live, not re-verifiable by file read from the Mac**
- Genesis on Vista is **1.1.1**, not 1.2.0. `module load tacc-apptainer` fails over
  non-interactive ssh; use `/opt/apps/tacc-apptainer/1.4.1/bin/apptainer` directly.


## git filter-repo standing note
Moved to the `git-history-rewrite` skill (.claude/skills/git-history-rewrite/).
Load it before any filter-repo pass or force-push of rewritten history.

## File provenance, do not cite anything not on this list without checking it live

CANONICAL:
- CLAUDE.md (this file, project root): Multi-Pane Standing Rules
- vehicle_params.py, mass_kg: 1100.0
- vehicle_geometry_research/yaris_coarse_v1l_watertight.ply: canonical Yaris mesh

DEPRECATED, do not read or cite. The deprecated files are also blocked
mechanically by the Read deny rules in .claude/settings.json, so this list
covers only what those rules do NOT block:
- data/track1_sweep_v2/: superseded box-proxy sweep (1390 kg box, 4.7352 m3
  solid volume vs the real hull's 3.542739 m3). Not archived, because
  analysis/gp_surrogate.py and analysis/build_poster_phase_space.py still read
  it and .gitignore explicitly un-ignores it with a `!data/track1_sweep_v2/` pair.
  DO NOT CITE A LINE NUMBER FOR .gitignore. Re-derive it every time:
  `/usr/bin/grep -n track1_sweep_v2 .gitignore`. This clause said ":17-18" until
  2026-08-12, then ":32-33", and both went stale within one session because two
  separate edits inserted lines above them. .gitignore line numbers have now been
  wrong three times in one day; the file is edited too often to cite positionally.
  Do not source a paper
  figure or a density number from it; use data/all_runs_inventory.csv instead.

## Corrections authority, 2026-08-06

docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md is the sole authority for
any factual claim it covers: solver identity, gravity, force accessors,
resolution, thresholds, citations, repo state. It is T1, read from live
source.

Demoted to historical, cite only with a date and never as current:
  docs/VERIFIED_FACTS_LEDGER_july24.md. ITS "_GRIDAWARE SIBLING" DOES NOT EXIST,
  checked 2026-08-21 by a find over the whole tree: eleven _GRIDAWARE files exist
  (README_GRIDAWARE.md, docs/GATES_GRIDAWARE.md, four analysis scripts and others)
  but NO VERIFIED_FACTS_LEDGER_july24_GRIDAWARE.md. Register H7 describes that
  sibling in the present tense and is the second carrier of the same dangling
  reference.
  ~/can-it-ford-audit/2026-08-04/CONFIRMED_FACTS_LEDGER.md
  docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md, WHICH DOES NOT EXIST ON DISK,
  checked 2026-08-21. scripts/semi_empirical_baseline.py:56 cites it too. Do not
  chase it; treat any claim sourced to it as unsourced until the file is produced.
Where any of them conflicts with the register, the register wins.

**RESEARCH-CORPUS READER RANKING, reset 2026-08-25. THERE IS NOW ONE LINE, NOT TWO.**
`docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` is the single master. It absorbs the two
dated readers, `CORPUS_MERGE_FINAL_2026-08-22.md` and its 138-DOI accounting, both
`CORPUS_FINAL_MERGE_REPORT_*` session reports, `CORPUS_BIB_MERGE_RESOLUTION_2026-08-25.md`,
`CORPUS_INGEST_BUILD_BLOCKER_2026-08-25.md`, `CORPUS_LINEAGE_STATUS_2026-08-23.md` and
`R9_CORPUS_READ_2026-08-19.md`. All nine remain on disk with SUPERSEDED banners; cite them
only with their date and never as current. The master does not outrank the register: where
it conflicts with the register, the register wins.
**THE PRIOR FORM OF THIS BLOCK SAID `CORPUS_MERGE_FINAL_2026-08-22.md` "is a SEPARATE line
and is NOT superseded" AND THAT "FINAL does not restate it". BOTH HALVES ARE NOW FALSE**,
withdrawn 2026-08-26: the master's section 4 is headed "The 138-DOI accounting, absorbed and
preserved as authority" and carries it forward, including the number that matters, 0 of 138
cited in the submitted paper. The master itself recorded this block as out of date in its
section 6.8 and drafted this replacement in its section 8, but left CLAUDE.md untouched
because another session held the file; three consecutive sessions then deferred the edit.
**The coupling-defect gap DOI is `10.1016/j.cma.2022.114809`**, joint top-ranked with
`10.1016/j.jcp.2016.10.064` at **7 reports each, re-measured live 2026-08-26** via
`analysis/research_index.py --doi`, and STILL UNREAD, closed access.
`10.1007/s00466-019-01783-3` is at 4, strictly below both, and is NOT the pair. The count is
instrument-dependent and time-dependent, the ranking is not. For the IFEMP paper
`10.1016/j.cma.2022.114809` specifically, this block previously recorded 4 reports from the
2026-08-14 catalogue TSV and 5 from the built index, and the live index now says 7. That is a
third instrument reading and not a correction of the other two. Quote the ranking, never a
bare count. N report appearances are N deep searches by ONE retrieval system, so they are a
relevance signal and NOT N independent sources.
**The corpus map is `docs/CORPUS_INVENTORY_2026-08-25.md`**, which inventories all 14 corpus
documents with their tracked state and records what is still open.


## THE ADVERSARIAL REVIEW PATH WAS DEAD FLEET-WIDE ON 2026-08-19. THE OUTAGE ENDED.

**OUTAGE OVER, measured 2026-08-20 03:40.** A `general-purpose` agent asked to run one
`git log` returned the correct SHA in 6.05 seconds, and a 15-agent workflow ran on the same
path immediately after. The section below is kept verbatim because it was true when written,
nine origins measured it, and the record of a fleet-wide outage is worth keeping. **Do not
delete it and do not act on it as current.**

Two things follow, and the second is the one that matters:

1. **A "do not re-attempt" instruction is advice against a retry LOOP, never a licence to
   carry a dated infrastructure claim as standing fact.** One probe costs six seconds; a
   fan-out launched onto a dead path costs the round. The verification rule at the top of this
   file already covers this, and this section is the worked example of what happens when an
   infrastructure claim is allowed to age into a fact.
2. **THE CLAIMS ARE STILL UNREVIEWED.** Every physics claim from 2026-08-18 and 2026-08-19 was
   marked UNREVIEWED because this layer was unavailable, and sessions d11, d12, d14, d15, d18
   and d19 were right to mark them so. **The path being alive does not review them
   retroactively.** Do not upgrade any of those claims until somebody actually runs the review.

---

### The outage as recorded on 2026-08-19, kept verbatim

Recorded here because it existed in five sessions' transcripts and **zero committed files**,
and a transcript is not a deliverable. Nine independent origins confirm it.

The `physics-skeptic` subagent, and any Agent call, dies with:

    deepseek-ai/DeepSeek-V4-Flash:deepinfra

**An explicit `model` override does NOT reach it.** Measured twice at 18:37 and 18:38: the
`physics-skeptic` agent at default and a `general-purpose` agent with an explicit `opus`
override produced the IDENTICAL error. The agent *launches* and then dies, which is why it
reads as a transient failure and gets retried instead of recorded.

**Consequence for every claim made on 2026-08-18 and 2026-08-19:** the operating protocol
asks for the physics-skeptic before finalising any percentage, force, verdict count or
distance. It was unavailable. Sessions d11, d12, d14, d15, d18 and d19 all correctly marked
their claims UNREVIEWED rather than faking the review. **Those claims remain unreviewed.**
Do not treat any of them as adversarially checked, and do not re-attempt the subagent
expecting a different result until the model id is fixed.


## ENVIRONMENT TRUTH THE PROJECT ALREADY PAID FOR AND FILED WHERE NOTHING READS IT

Added 2026-08-19 from the coordinator audit, finding V7. Both items below are Claude Code
bugs affecting HPC work. The first appears TEN TIMES in `_inbox/LIVE_SESSION_LOG.md` and
ZERO times in this file, the skills, or the register, so every session that needed it had
to rediscover it.

**1. `XDG_RUNTIME_DIR` on SLURM COMPUTE nodes (issue #21026).** The Bash tool can fail on a
compute node with `EACCES ... mkdir '/run/user/...'` because it hard-codes a runtime dir and
ignores `XDG_RUNTIME_DIR`. It works on login nodes. First line on any compute node:

    export XDG_RUNTIME_DIR="/tmp/xdg_runtime_${USER}" && mkdir -p "$XDG_RUNTIME_DIR"

This did NOT apply on 2026-08-19, because every session ran Claude Code on the Mac and
reached Vista through `ssh` and `scripts/tacc.sh`, which is the right architecture for
exactly this reason. Keep it that way.

**2. Interactive mode exiting immediately (issue #12507), and `claude -p` as the
workaround.** Reported cause is stdin being consumed by shell-detection subprocesses.
`claude -p` non-interactive mode is the documented workaround and appears ZERO times in
`scripts/r8/`.

The 2026-08-19 relaunch produced this SYMPTOM exactly: nine windows fell back to a bare zsh
prompt and a sender then pasted 4 KB of markdown into a shell, which executed it line by
line. The recorded MECHANISM was different, session-id reuse, and which one applied has not
been resolved. Two things hold regardless: the documented workaround was unavailable to the
launcher, and **the real defect was that a launcher failure degraded into pasting a prompt
into a shell.** A launcher must verify what it is talking to before it speaks.


## MOVED OUT OF THIS FILE 2026-08-19, with their operative rules kept here

Five sections, 171 lines, were moved VERBATIM to
`docs/CLAUDE_MD_MOVED_SECTIONS_2026-08-19.md`. Nothing was summarised or dropped and the
move was verified line by line. The rules below are what those sections were FOR; read the
moved file for the working behind any of them.

- **Repo-clone sprawl, 2026-08-15.** 28 locations, 31.6 GB, half non-canonical.
  `~/can-it-ford` is canonical. Full working is in the corrections register addendum L1 to
  L7, which is where it was already recorded; that is why the summary could leave this
  file. Three rules survive and are still live: do NOT test clone provenance by asking a
  clone whether its HEAD is an ancestor of origin/main, because that reads the clone's own
  stale cached ref; the claude.ai Project's GitHub sync points at `jcerrell-IS/mpm-engine`
  and does NOT reach this repo, so committing into `docs/` here will not appear in it; and
  `make_phase_space.py` forks on the 0.60 boundary operator, with `designsafe-staging/` the
  publication-bound tree.
- **Gate inventory, 2026-08-08.** `.claude/checks/params_check.py` already runs four
  literature-cited gate categories. DO NOT REBUILD THEM. Trap that has caught an audit
  before: `lit:resolution_convergence_gci` is assembled at runtime, so `grep -F` returns
  nothing and a naive sweep concludes the gate is missing. Run the script and read its
  output instead of grepping for the tag.
- **Overleaf credential, STILL OPEN.** The token is off local disk but NOT revoked, so it
  stays valid server-side until rotated in Overleaf account settings, and a push now
  prompts for credentials. `~/can-it-ford-paper` EXISTS despite an earlier note saying it
  was deleted.
- **Nested `./can-it-ford/` duplicate: GONE.** Verified by `ls -d`. Every exclusion of
  `./can-it-ford/` in this file, in skills and in audit scripts is now a NO-OP rather than
  a load-bearing guard. Do not conclude from a passing grep that the duplicate was handled;
  there is nothing left to handle. Re-run the `ls` before citing it as a live hazard.
- **MacOS-MCP `Snapshot` with `use_vision=true`** fails with `cannot identify image file`
  until macOS Screen Recording permission is granted to Claude Desktop. Without vision it
  works and needs no fix.
- **The refuted novelty claim** is already stated operatively in the research-corpus
  section above: do not cite "four prior vehicle fording or wading simulations", the
  deep-search layer puts it at eight or nine.
