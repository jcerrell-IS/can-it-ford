# The 2026-08-18/19 adversarial-review backlog, cleared 2026-08-26

## Why this file exists

`CLAUDE.md` records that the `physics-skeptic` subagent path was dead fleet-wide on
2026-08-19, that sessions d11, d12, d14, d15, d18 and d19 correctly marked their claims
UNREVIEWED rather than faking a review, and that the outage ended on 2026-08-20. It also
states the thing that kept mattering:

> **THE CLAIMS ARE STILL UNREVIEWED.** ... **The path being alive does not review them
> retroactively.** Do not upgrade any of those claims until somebody actually runs the
> review.

Nobody ran it for six days. This file is that review.

**Path liveness, measured 2026-08-26:** four `physics-skeptic` agents launched and all four
returned substantive reports. The `deepseek-ai/DeepSeek-V4-Flash:deepinfra` failure does not
reproduce. The outage is over in practice, not just on paper.

**Scope caveat, stated up front.** Six documents were reviewed across four agents, not every claim from those
two nights. Documents NOT reviewed here remain UNREVIEWED and must still be marked so:
`R8_FORCE_ROUTE`, `R8_DETERMINISM_RENAME`, `R8_LICENCE_RECONCILE`, `R8_REGISTER_MERGE`,
`R9_ACCESSOR_DEFECT`, `R9_CORPUS_BIB_GAP`, `R9_LANDING_PLAN`, `R9_RENDER_MATERIALS`,
`R9_MOVING_VEHICLE`, `R9_PROPAGATION_MEASUREMENT`, `R9_PROVENANCE_AUDIT`,
`R9_APPEARANCE_HULL_COSTING`, `R9_CYCLES_PRESENTATION_RENDER`, `R9_DISCREPANCY_REGISTER`,
`R9_JOBC_PREREGISTRATION_AND_BLOCKER`, `R10_WEB_ACQUISITION`. **Clearing six is not clearing the backlog.**

---

## A. `docs/HANDOFF_ROUND_7_2026-08-18.md`, the floor-BC mechanism. TWO REAL DEFECTS.

### A1. BLOCKING for anyone citing the floor BC. The quoted expression is the WRONG BRANCH.

The document (around line 225) attributes the floor BC to
`v -= min(normal_component,0)*n`. Read live in the pinned engine
`third_party/mpm-engine-544c93dd-solver-core/`:

- `sim_standing.py:210` adds the floor with `surface="slip"`.
- `core/solver.py:220` forwards the surface string unchanged.
- `mpm_solver_warp.py:1906` maps `"slip"` to `surface_type = 1`.
- `surface_type == 1` executes `mpm_solver_warp.py:1978`:
  `v = v - normal_component * n`, projecting out the ENTIRE normal component.
- The `min()` form the document quotes is `mpm_solver_warp.py:1982`, the `else` branch,
  `surface_type == 2`, `"separable"`, which is the **SDF vehicle collider**, not the floor.

**REFUTED as written.** The floor is more constraining than the document says, which
sharpens rather than softens the question of why water still leaks. The higher-level
conclusion, that this is a grid-node velocity projection and NOT a repulsive layer so the
DualSPHysics mDBC framing does not transfer, **survives on both branches.**

### A2. The stated mechanism imports SPH density summation into a code that has none. UNSUPPORTED.

The document explains the leak via "the nodes below carry no particle mass, so P2G leaves
them mass-deficient and the particle sees a density deficit underneath with a pressure
gradient pointing INTO the boundary."

In this solver, pressure is an equation of state on the particle's own Jacobian:
`kernels/mpm_utils.py:22`, `pressure = -bulk * (wp.pow(J, -gamma) - 1.)`, same form at `:43`
and `:68`. Grid mass `grid_m` enters ONLY the momentum-to-velocity divide (`:935`) and the
P2G mass deposit (`:915`). **It never enters the stress or pressure path.** A mass-deficient
node underneath therefore cannot create a pressure gradient into the boundary by the stated
route.

This is precisely the trap already recorded in project memory: SPH boundary papers cannot
explain this floor, because SPH needs boundary particles and this floor writes only a
grid-node velocity. The mechanism silently re-imported the particle-density picture.

**A correct MPM framing that IS available:** the BC is enforced on grid-node velocities,
then G2P re-interpolates each near-floor particle from a 3-node stencil straddling the
plane, mixing projected sub-floor nodes with unprojected interior nodes above, so a net
downward particle velocity survives and advects through. That needs no density argument.

### A3. "Three measured signatures, all three match" is one instrument on one run pair. OVERSTATED.

All three trace to `water_budget()` in `sphere_heave.py` on the single run pair
918240/918251. One tool, one pair, decomposed three ways. The project rule is explicit that
a claim plus the tool that measured it is not corroboration. Also, the floor-leak ratio is
**1.19 against its own area-distributed prediction of 1.00**, and the document's own prose
concedes "The floor leak does not [scale as predicted]", so signature 2 is a weak match
reported as a clean one. Area-distributed floor plus perimeter-scaled walls is what ANY
grid-node BC failing to stop G2P penetration would produce, so the signatures do not
discriminate this mechanism from the simpler interpolation story.

### A4. Diagnosed on a floor that is not the canonical floor. SCOPE GAP.

Measured on `sphere_heave.py:577`, `"slip", friction=0.0, restitution=0.0`. The canonical 17
runs use `sim_standing.py:210`, `"slip", friction=0.55, restitution=0.05`, and restitution
0.05 activates `_apply_rigid_restitution` via the `mpm_solver_warp.py:1915` gate, which the
sphere floor never triggers. Both are surface_type 1 for the fluid projection so the leak
plausibly transfers, but it was **not measured on the canonical configuration.**

### A5. CONFIRMED, do not re-litigate.

The quadratic B-spline half-width **is** 1.5 dx. Weights at `mpm_utils.py:837-844` are the
classic MLS-MPM quadratic, with 3-node loops at `:862-864` and `:993-995`. This is NOT a
quadratic-versus-cubic mixup, and the stencil genuinely straddles the plane, so the
geometric premise is sound. **The `# tricubic interpolation` comments at `mpm_utils.py:873`
and `:1002` are mislabels; the math is quadratic.** Also confirmed: `if dotproduct < 0.0:`
at `:1955` is strict, so a node exactly on the plane is unconstrained, and the job 918450
`< 0.0` to `<= 0.0` change is correctly scoped.

### A6. The falsifier, already built.

`sphere_heave.py:529-557` implements `--ghost-layers N`. Run `n_ghost=3` and re-measure the
leak at the nominal floor. If the density-deficit story is right, restoring sub-floor mass
should nearly eliminate it. **If the leak persists, A2's mechanism is falsified** and the
cause is G2P velocity interpolation. Re-reference `measure_surface` first, since the seeded
column moves the free surface.

---

## B. `docs/R10_FULL_CONTEXT_AUDIT_2026-08-19.md`. TWO BLOCKING, FOUR NON-BLOCKING.

### B1. BLOCKING. "16 enumerated ... across three named views" misrepresents its own source.

Upstream source `docs/R8_PRIOR_ART_2026-08-18.md:609-616` says verbatim: "at least 16 from
the catalogs, plus 16 more from one graph hop, plus 8 from the author sweep. Treat as a
floor, never a total." So **16 is the catalog view ALONE**, the three views give 16 / 16 / 8
separately, and their union is unknown. R10 collapses "16 from one view" into "16 across
three views", which is smaller than the honest floor union, and drops the "floor, never a
total" caveat entirely. This is a relay distortion toward the more quotable number.

**This wording must not be copied into `CLAUDE.md` or the paper.** `CLAUDE.md` was corrected
accordingly on 2026-08-26.

### B2. BLOCKING. Slot 8 instructs writing "the enumerated 16" into the constitution, contradicting the document's own section 9.3.

Section 9.3 correctly says the count "grew from four to eight or nine to sixteen ... I would
not bet that sixteen is the ceiling ... expect it to move again." Slot 8 then instructs that
a firm "enumerated 16" replace the CLAUDE.md sentence. **Do not execute Slot 8 as a fixed
total.** To the document's credit it does NOT commit the "growth proves thoroughness"
inversion; the defect is the internal contradiction between its uncertainty section and its
action section.

### B3. What the count actually is today, with its scope.

Live index (2026-08-25 build), `--method vehicle-fording` returns **13 papers**, the most
complete single route because the tag is builder-assigned and so reaches the 3 of 13 with
`has_abstract=False`. Roughly **11 to 12 are simulations**; one, Kramer 2016
`10.1016/j.ijdrr.2016.04.003`, is a road-trafficability criteria paper, not a simulation.
`--query fording` returns 5 and `--query wading` 4, both under-counts, and the tool itself
now prints that 171 of 382 records have no abstract. **The one narrow claim that survives is
a ZERO: no MPM simulation of a full road vehicle in floodwater in the searched views**, with
tyre-hydroplaning MPM (Zhou) as the adjacent precedent.

### B4. Reach versus cited, re-verified live against `overleaf/main`.

For He 2026 `10.1115/1.4071177`, Wasfy 2015 `10.1115/DETC2015-47142`, Khapane 2014
`10.4271/2014-01-0936`, Al-Qadami 2022 `10.1111/jfr3.12828`, plus `pazouki2016fording`:

- present in the corpus index: **4 of 4**
- `cited_in_repo` and `cited_reader_facing` True: **4 of 4**, meaning only that the DOI
  string appears in the tracked tree or in `docs/`
- in the submitted Overleaf bib: **0 of 4**, by cite key and by DOI
- `\cite`d in `overleaf/main:conference_101719_1.tex`: **0 of 5**

The document's claim that the paper cites none of them is **TRUE**, and the document did not
fall into the `cited_reader_facing` trap. Recorded here so the next reader does not.

### B5. NON-BLOCKING. The "+34 to +64 percent" sphere excess is untagged and is the criticised path.

Used at `R10_FULL_CONTEXT_AUDIT_2026-08-19.md:88` and `:397` with no provenance tag, despite
the file's own tagging convention. It is **relayed** from the R9 Job B documents, and it is
the **free-rigid measured-accessor** result, distinct from the validated SDF-collider path at
7.3 to 7.7 percent and from the free-rigid late-window fit at +1.5 / +0.7 to 0.8 percent.
Tag it relayed and name the path.

### B6. NON-BLOCKING. Section 1.4's corpus census is stale.

It reports 332 records / 76 cited_in_repo / 43 cited_reader_facing / 8 of 21 deep searches.
Live 2026-08-25 build: **382 / 164 / 131 / 11 of 28**. The document predates the rebuild so
this is post-hoc staleness, not an authoring error, but none of those integers may be quoted
forward. The ladder STRUCTURE is methodologically fine; only the integers moved.

### B7. Al-Qadami D x V ambiguity: REFUTED, the document is clean.

Every mention names the paper (2022) and cites only the critical depth 0.38 m, on which the
2022 and 2023 papers agree. The document contains no "0.39" and never quotes a bare D x V.
**No instance to flag.**

---

## C. `docs/R8_KRAMER_INTERCODE_2026-08-18.md` and `docs/R9_KRAMER_FULL_EXTRACT_2026-08-18.md`. NO BLOCKING ISSUES.

Reviewed by independent recomputation in pure standard-library Python, with a hand-written
trapezoidal integrator rather than the project's own scripts. Neither document is on
`origin/main` and no gated verdict depends on them, which caps every finding at
non-blocking.

### C1. The numeric spine reproduced live, all of it.

11 codes, 31 series (not 33), 6 groups, RANS3 present at 05D only, row counts spanning
20.47x (951 to 19468), WG on 4 codes and 10 series, 22 of 31 non-uniformly sampled, 78 zip
entries as 63 files plus 15 dirs, archive sha256 matching byte for byte. **All CONFIRMED.**

### C2. The reversal finding SURVIVES, strongly.

Independent eta^2 integrals reproduce R9 section 5 to the digit. RANS2 and RANS3 are
monotone up as declared; **RANS4 (3 of 3) and RANS5 (3 of 3) are strictly monotone down, so
reversed.** The experimental control has all 12 repetitions as declared, band [2.654, 3.418]
against R9's [2.655, 3.418], a windowing difference, immaterial. Falsifier: a re-download
whose RANS4/RANS5 WG columns integrate monotone-up.

### C3. The "manufactured trend" hazard was HEEDED, not committed.

The reversal lives only in the WG columns. The period and decay trends use the x3 heave
column and are untouched. The one WG-based trend claim is computed on the **experimental**
gauges, as-declared. `_extrema` at `kramer_benchmark.py:347-381` brackets by zero-crossings
and quadratic-refines, and its docstring cites the 20x row range as the reason. **No
manufactured trend found, and no raw different-length comparison found.**

### C4. NON-BLOCKING, worth one edit. R8's "resolves RANS4 completely" was withdrawn by R9 and R8 was never annotated.

`R8_KRAMER_INTERCODE_2026-08-18.md:809`. R9 (`:404-412`, `:461-463`) ran a drop-matched
control and withdrew the related pure-column-swap claim; inverting RANS4's shipped ratio
misses its own drop's experimental band on all three drops at +0.8 / +1.6 / +13.2 percent,
reproduced independently against R9's +0.7 / +1.7 / +13.3. R8's claim is true only of the
gauge-SPREAD metric, not the ratio-MAGNITUDE metric, and never says which. **A reader of R8
alone over-concludes a proven relabelling.** Annotate `:809` to point at R9 section 5.1.

### C5. NON-BLOCKING. R8 section 4's "five of the six independent groups" depends on an unstated key.

True under the AUTHOR key, false under the INSTITUTION key the sheet actually ships, where
it is 4 of 6 with two different groups at the two ends. R8 never states the key. R9 section 3
already caught and fixed this; the R8 text remains uncorrected.

### C6. NON-BLOCKING, wording. Two "independent" labels are generous.

R9 section 3 calls the Kramer slide deck "a second artifact with a separate origin" for his
dual affiliation, but deck and paper are both authored by Kramer and both live in the same
archive. R8's "three independent checks" and "independently confirmed by the data itself"
validate the reduction against the same source. Each is disclosed in context and none is
offered as physics validation, so only the word is loose.

### C7. R9's self-attacks are the strongest part of either document.

Its withdrawals (swap hypothesis 5.1, Archimedes 6.1, a33 6.3, the 0.3 percent figure 12.1)
were reproduced and are **sound**. R9 explicitly downgrades same-source checks from
"independent". This is the standard the rest of the corpus should be held to.

---

## D. `docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md` and `docs/R9_JOBB_ROUTE_DECISION_2026-08-19.md`. VERDICT SURVIVES, FIVE DEFECTS.

**The Job B FAIL is NOT overturned.** The graded accessor is manifest-designated, the
measured ratio is stationary under the project's own blocked test, and the excess clears
the FAIL band by 2.4 to 2.6x. What follows must be fixed before the text is cited, not
because the verdict is wrong.

### D1. Both load-bearing citations in the FAIL argument are stale.

- `R6:489` cites `R5_PHYSICS_BATCH_MANIFEST.md:214` for "Any FAIL stops the ladder." It is
  at **`:258`**, off by 44 lines; `:214` is "Three cautions on 69.2180 N."
- `R6:491` cites `sphere_heave.py:669-670` for the accessor designation. Live `:669-670` is
  `mach_peak` and `group_velocity_m_s`. **The designating comment was rewritten to
  disclaim itself** at `sphere_heave.py:893-903`, "THIS COMMENT NO LONGER DESIGNATES
  ANYTHING", and it names `r6_repeat_stats.py` as a downstream that propagated the
  withdrawn designation.

The designation now lives in **manifest criterion 3** (`:266`, `:313`, amended
2026-08-19), which is why the verdict survives its own stale citations. Note the ordering:
R6 was written 2026-08-18, one day BEFORE the amendment, so at authoring time the
designation really was only a comment.

### D2. THE HEADLINE RESULT. "The two accessors disagree in magnitude and sign" is arithmetic, not physics.

`sphere_heave.py:866` computes `fz` **once**. `:929` divides it by `fb_meas`, the buoyancy
at the drained measured surface (`buoyancy_at`, `:849-853`). `:930` divides **the same
`fz`** by the design hemisphere 69.21799 N. They cannot disagree about physics; they
disagree about which reference volume divides a shared force.

Back-solved from the reported windows: last-100 gives measured 1.6308 and nominal 0.77424,
and **1.6308 x 32.86 = 0.77424 x 69.218 = 53.591 N by both routes**, exactly the "Late-window
mean 53.5913 N" the document itself states. **The sign flip is guaranteed:** the true force,
roughly 49 to 62 N, lies between the drained cap (~30 to 39 N) and 69.218 N, so it must
read above one and below the other.

**"A factor of two" is also wrong.** The ratio is `69.218 / fb_meas(window)` and it drifts
as the tank drains: **2.32 at last-20, 2.11 at last-100, 1.78 at last-200.**

`sphere_heave.py:912-917` already says this in the source. The project memory phrasing
"disagree on MAGNITUDE and SIGN", at the now-stale `:818`/`:819`, is what invited the
physics misreading. That memory was corrected on 2026-08-26.

### D3. +63 percent is superseded inside its own document.

`R6:521-523` states 918043 is "biased HIGH", the corrected run is **918240 at +50.06
percent**, and verbatim "**Quote +50.06, not +63.**" R9 section 11.3 drives it further: the
one-character bcfix (`<` to `<=` at `mpm_solver_warp.py:1955`) reaches ratio 1.355, **+35.5
percent**. So the magnitude has moved +63 to +50 to +35.5 across corrections while the FAIL
verdict stayed invariant. This is the project's own "cite the verdict, never the magnitude"
pattern. Anyone quoting +63 as current is quoting a retired number.

### D4. "Every number in this document is regenerated by one script" does not hold from the repo.

`R6:829`. Verified live: the interpreter is not the blocker (`r6_a1_caveats.py` and
`r6_repeat_stats.py --jobB` run fine under numpy and fail only on missing input). **The
inputs are Vista-only.** A search of `/Users/josie` found no `brake_mu*/metrics.csv`, no
`sphere_fixed_g64.json`, no `rep_g96m2337_*`. The only part reproducible standalone is
`r6_hull_clearance.py`, which reads the local hull PLY and **reproduces exactly**:
underbody clearance 177.4 mm, D/10 wants dx <= 17.74 mm, and the full grid table.

So the Job B numbers are self-consistent on inspection but **not independently regenerable
without Vista payloads the repo does not archive.** That is the check-18 provenance gap.

### D5. The reproduction script still prints the retracted label.

`analysis/r6_repeat_stats.py:241` and `:252` still call `fz_over_analytic_measured` "the
designated accessor" and cite `sphere_heave.py:669-670`. This is exactly the stale
propagation that `sphere_heave.py:900` calls out by filename. Harmless to the verdict,
since the manifest independently designates the same accessor.

### D6. Two of my own framings were REFUTED by this review. Recording both.

- **+63 percent is the SDF-collider path, NOT free-rigid.** `sphere_heave.py:219`
  self-labels it and `:865` reads `sdf_wrench`. R6 and R9 do NOT conflate the three ranges.
  The real tension to keep visible: the same SDF path validated at 7.3 to 7.7 percent reads
  +35 to +63 percent here because this is a leaky-floor draining-tank scene, and **97
  percent of the surface fall reproduces with the body removed**. So +63 must never be
  quoted as a coupling-accuracy number, for a different reason than the one I assumed.
- **`N_eff` 2.9 to 11.0 does not apply here.** That is the vehicle 91-frame scene. This is a
  200-frame sphere run with tau_int 2.396, so N_eff is about 40 on the late window.
  Importing the vehicle figure is a category error. The 0.15 sigma test is already
  autocorrelation-corrected at `blocking.py:402`, not a naive-N test. The six windows ARE
  six nested views of one record, so "window-robust" is not six independent confirmations,
  but the series is genuinely trend-free so window choice cannot move the verdict.

---

## E. What changed in the repo as a result

- `CLAUDE.md`: the prior-art line rewritten to state a floor with its named view, per B1 and
  B2, and to record the 0-of-4-cited result from B4.
- Nothing else was edited on the strength of these reviews. **The defects in A1, A2, A3, C4
  and C5 are recorded here and NOT yet fixed in their source documents.** That is the next
  session's work, and it is listed in the order the reviews rank it.

## F. Open items these reviews created

1. Correct the floor-BC quote in `HANDOFF_ROUND_7_2026-08-18.md` from the `min()` form to
   the surface_type-1 full projection at `mpm_solver_warp.py:1978`. (A1)
2. Downgrade that document's mechanism to UNSUPPORTED and its "three signatures" to one
   water-budget measurement on one run pair. (A2, A3)
3. Run the `--ghost-layers 3` control, which is already built, to settle A2 either way. (A6)
4. Fix the `# tricubic interpolation` mislabels at `mpm_utils.py:873` and `:1002`. (A5)
5. Annotate `R8_KRAMER_INTERCODE_2026-08-18.md:809` with R9's withdrawal. (C4)
6. State the grouping key in R8 section 4. (C5)
7. Tag the "+34 to +64 percent" figure as relayed. Note it is the SDF-collider path, not
   free-rigid, per D6. (B5, D6)
8. Fix the two stale citations in `R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md`:
   manifest `:214` becomes `:258`, and `sphere_heave.py:669-670` becomes manifest criterion
   3 at `:266` and `:313`. (D1)
9. Reframe the accessor pair everywhere as one numerator over two denominators, and stop
   describing the ratio as a factor of two. (D2)
10. Replace every current-tense "+63 percent" with +50.06, or with the bcfix +35.5, or with
    the FAIL verdict alone. (D3)
11. Remove the retracted "designated accessor" label from `analysis/r6_repeat_stats.py:241`
    and `:252`. (D5)
12. Either archive the Vista payloads or a fixture, or downgrade the "every number
    regenerates" claim in `R6:829` to name what actually reproduces standalone. (D4)
