# Research to implementation: what the reports say, what now exists, what is left

Compiled 2026-08-15 by a local Claude Code session. Companion to the Unbuilt
Register. Every status claim was verified live against this working tree, not
carried from a summary.

## 0. Coverage, stated first so it can be audited

**The corpus does not contain 426 abstracts.** Each Undermind report details only
its top 50 papers; the rest appear as catalog rows with title, year, authors and
DOI. Measured: 323 abstracts exist across the eight reports, 103 papers are
metadata-only.

| Report | Papers | Abstracts on disk | Read closely this pass |
|---|---:|---:|---|
| `Quantitative_MPM_Wall_Penetration` | 16 | 16 | **all 16** |
| `Moving_Rigid_Body_Free_Surface_Validation` | 44 | 44 | **all 44** |
| `Settling_and_Force_Reporting_in_Free_Surface_Flow` | 68 | 50 | **24** |
| `Validated_MPM_Vehicle_Water_Coupling` | 60 | 50 | summary only |
| `Multi-resolution_MPM_for_Large-domain_Flooding` | 78 | 50 | summary only |
| `MPM_Simulation_Verification_Provenance` | 68 | 50 | summary only |
| `Reliable_AI_Scientific_Software` | 79 | 50 | summary only |
| `Trustworthy_AI_Assisted_Scientific_Simulation` | 13 | 13 | summary only |

So: **84 abstracts read in full**, concentrated in the three reports densest in
implementable method, plus all eight Summary-of-Results sections read in full
earlier. The remaining 239 abstracts are extracted and staged for reading; they
are not yet read. Do not cite this document as having reviewed them.

## 1. What now exists in the repo that did not before

### `analysis/stationarity.py` (new)

Implements the settling protocol the literature actually prescribes, replacing
nothing yet but making the alternative measurable. Pure standard library so it
can run as a CI gate; no system interpreter here has numpy.

| Function | Method | Source |
|---|---|---|
| `mser_truncation` | Marginal Standard Error Rule | Bergmann et al 2021, `10.1115/1.4052402` |
| `chodera_equilibration` | maximise effectively uncorrelated samples | Chodera 2015, `10.1101/021659` |
| `integrated_autocorrelation_time`, `effective_sample_size` | automatic-window tau_int | Straatsma 1986, `10.1080/00268978600100071`; Grossfield 2018, `10.33011/livecoms.1.1.5067` |
| `blocking_error` | renormalisation-group blocking | Flyvbjerg & Petersen 1989, `10.1063/1.457480` |
| `reverse_arrangement_z` | reverse arrangement stationarity test | Pan & Patton 2017, `10.1175/JTECH-D-17-0038.1` |
| `transient_scan`, `random_uncertainty_of_mean` | Transient Scanning Technique, RUM from one record | Brouwer et al 2019, `10.1016/J.OCEANENG.2019.04.068` |

Ten self-tests, all passing: `python3 analysis/stationarity.py`.

One self-test exists specifically to encode a trap found while building it:
**MSER minimises standard error, which is not the same as achieving
stationarity.** A slowly decaying exponential still carries a residual trend
inside the MSER-optimal window, and only the reverse-arrangement test catches it.
A settle length chosen to stabilise a mean is therefore not evidence the record
is stationary. Both diagnostics are reported for that reason.

### `analysis/settle_audit.py` (new) and its measured result

Applies the above to every local run. **No GPU needed**: the 15-column
FloodHistory `metrics.csv` for 25 runs is already on disk.

Result on `dmag`, against the driver's `settle_frames=8`
(`renders/yaris_render_s1/sim_standing.py:154`):

- **25 of 25 runs need more than 8 frames discarded.** Min 29, median 48,
  max 80, out of 91 total frames.
- **12 of 25 retained windows are still not stationary at the 5% level** after
  trimming.
- `tau_int` ranges 1.00 to 11.47. **N_eff ranges 2.9 to 11.0.** A 91-frame record
  therefore contains roughly 3 to 11 independent samples, so any uncertainty
  computed from N = 91 is overstated by a factor of about 3 to 5.

Caveat recorded in the tool: MSER is bounded below by `min_keep=10`, so a run
reporting `need = n - 11` has hit that bound, meaning variance was still falling
at the end of the record. That reads as **the run is too short**, not as
"discard exactly that many". This independently reaches D9's conclusion that 60
frames were inadequate and 250 were needed. Treat as corroboration only because
the origins genuinely differ: this is a stationarity statistic on a single
record, D9 was a settle-length sweep across arms.

### `analysis/probabilistic_verdict.py` (new)

Movement-probability verdicts with detection uncertainty, per Dancey et al 2002,
"Probability of Individual Grain Movement and Threshold Condition", which
specifies a threshold by a fixed value of a probability rather than a critical
stress. Confidence intervals use the Wilson score interval on **effective**
sample size, not frame count.

Measured on the 24 local runs with a `dmag`/`vmag` record:

- The default full-record mode **reproduces the canonical pattern**, 21 of 24
  SLIDE, and independently returns **`margin_frames` = 1 for `g96_m2337`**,
  matching register J15's one-frame margin. The m2337 series margin collapses
  with refinement (g48 19, g64 8, g96 1), qualitatively matching J15's
  11 -> 10 -> 4. Values are not identical because this reads `vmag` where the
  classifier reads a component; treat as corroboration, not reproduction.
- **17 of 24 verdicts flip somewhere in p >= 0.01 to p >= 0.50.** The label
  therefore depends on a probability cut nobody has stated. That cut belongs in
  the paper next to the verdict.

**A correction I made to my own tool, recorded because shipping it silently would
have produced a false claim.** The first version removed the startup transient
before assessing, and reported mostly STUCK, contradicting the published
16 SLIDE / 1 STUCK. That was a category error on my part. Transient removal is
correct for a steady observable such as a mean resistance force; incipient motion
is an **event**, and the same report says impact and water-entry loading "generally
have no steady force: report peak distributions, impulses, envelopes or
cycle/event statistics ... rather than a steady mean." The default is now the full
record. The stationary-window pass survives as `--stationary-window`, a genuine
robustness diagnostic whose answer is interesting: **only 5 of 24 runs still
satisfy the slide condition once the startup transient is removed**, so the
verdicts live substantially inside the surge.

## 2. The finding that most changes how the grid study should be reported

Syamlal, Celik and Benyahia 2017, `10.1002/AIC.15868`, state that successive grid
refinement **may not** yield grid-independent transient quantities, while
time-averaged quantities do converge on sufficiently fine grids, and that
Richardson extrapolation plus a grid convergence index is then the right report.

The g48/g64/g96 study reports `final_disp_mag_m`, an instantaneous end-of-run
value, and finds it non-monotone (+87.8% then -59.2% at 1100 kg). **That is the
documented expected behaviour for a transient quantity, not necessarily a solver
defect.** The same paper also finds autocorrelation more reliable than binning for
time-averaging uncertainty, which is why `stationarity.py` uses it.

Actionable: if grid convergence is the claim, report a time-averaged observable
over a demonstrated-stationary window, with a GCI. If the instantaneous value is
what matters, say explicitly that it is not expected to converge and cite this.

## 3. Methods with a clear implementation path, none yet attempted

Ranked by payoff per unit effort. None of these is in the repo: verified 0 hits
in `analysis/` and `simulation/` for CPDI, GIMP and moving-reference-frame.

1. **Spatial-integration-error mitigation.** Baumgarten & Kamrin 2023,
   `10.1002/nme.7217`. Targets exactly the two errors this project exhibits, the
   particle ringing instability and solution-dependent integration error, and the
   abstract states it improves fluid-like MPM "without requiring significant
   augmentation of existing MPM frameworks". Cheapest real numerics win available.
2. **Image-particle boundary condition.** Schulz & Sutmann 2019 (Semantic Scholar
   `6c944911be46fde053bbe04cb66702254b620eec`). Traditional grid-momentum-zeroing
   walls "distort the stress multiple grid lengths into the object", which is the
   smeared wall layer behind the seven P-2 failures at 7.99% to 15.88% water
   inside the hull bbox. Includes an optimisation that avoids constructing mirror
   particles explicitly.
3. **Hourglass damping.** Zhang et al 2017, `10.1016/j.jcp.2016.10.064`. Suppresses
   spurious velocity modes. Ships inside their incompressible MPM but is
   separable, and spurious modes are a plausible contributor to the
   resolution-ceiling instability found between n_grid 100 and 104.
4. **Incompressible MPM by operator splitting.** Same paper. Reported "much more
   accurate and efficient" than weakly compressible MPM for free-surface flow,
   which is the formulation this project runs, and would remove the sound-speed
   sensitivity entirely rather than sweeping it.
5. **Particle rearranging to eliminate numerical cavities.** Li, Lian & Zhang 2022,
   `10.1016/j.cma.2022.114809` (IFEMP). Non-physical voids from disordered
   particle distribution. Also the sharp immersed-interface route to real two-way
   coupling, which is the architecture question A-1 left open.
6. **Blurred interfaces and VMS stabilisation.** Chandra, Hashimoto, Kamrin & Soga
   2024, `10.1016/j.jcp.2024.113457`. Stable transitions between free and porous
   domains; the stabilisation strategy is independently useful.
7. **B-spline MPM for noise.** Zhou & Sun 2021, `10.1016/j.jnnfm.2021.104678`
   report that WC-BSMPM eliminates traditional MPM numerical noise.
8. **PPC co-refinement before any AMR.** Any adaptive scheme silently changes
   quadrature unless particles-per-cell is co-refined; fixed PPC can lose
   convergence under refinement. This is the precondition for items in Unbuilt
   Register class B4, not an optional extra.

## 4. Validation targets, with the analytical cases that unblock gate A4

The repo has no physics regression test. `tests/` holds only
`test_count_claims_check.py` and `test_csv_schema.py`. Two routes now have
identified sources:

**Analytical, no data download needed.** Sun et al 2016,
`10.1504/PCFD.2016.10001222`, verify MPM fluid against **Poiseuille and Couette
flow**, both of which have exact closed-form solutions. These are the standard MPM
fluid verification cases and are the natural content for a locked regression test
that runs in CI.

**Experimental, public data.**

| Target | Why it is the right one | Identifier |
|---|---|---|
| Floating-sphere heave decay | **0.3% uncertainty at 95% CI**, three drop heights from linear to highly nonlinear, and the authors formulate a test case explicitly so readers can run their own numerics. A half-submerged sphere decaying in heave is the closest published analogue to this project's buoyancy-and-settle problem. | Kramer et al 2021, `10.3390/en14020269` |
| Dam-break onto a vertical cylinder | Gate motion, pressure measurements and high-resolution video supplied as Supplementary Materials | Kamra et al 2019, `10.1016/J.JFLUIDSTRUCTS.2019.01.015` |
| MPM FSI benchmark, three cases | Method-matched: sloshing tank with elastic bar, dam-break through an elastic gate, dam-break past an elastic obstacle | Sun, Huang & Zhou 2019, `10.1504/PCFD.2019.10018820` |
| Blind-test protocol | Shows spread between methods on identical input, useful as a limitation citation | CCP-WSI Blind Test 3, `10.17736/ijope.2020.jc774` |
| Towing-tank UQ methodology | ITTC-conformant bias/precision procedure | Longo & Stern 2005 |

## 5. Physics the model does not currently represent

- **Added mass is not a constant during acceleration.** Grift et al 2019,
  `10.1017/jfm.2019.102`, show drag during prolonged acceleration "is not captured
  by a single added mass coefficient" and define an entrainment rate instead. They
  also measure steady drag rising **45%** when a plate sits 1/5 of its height below
  the surface versus at it. Directly relevant to the surge that the SLIDE verdicts
  live inside.
- **Surge drag exceeds heave drag by at least 2x**, with added mass and radiation
  damping quantified: Gu et al 2018, `10.1016/J.JFLUIDSTRUCTS.2018.06.012`.
- **Free-surface proximity changes added mass** for a body accelerated from rest:
  Waugh & Ellis 1969, `10.2514/3.62822`. Chung 1977, `10.2514/3.63081`, measured a
  critical frequency near the free surface that existing theory did not predict.

## 6. Two threshold-literature findings that affect the paper's framing

- **AR&R's guidelines rest on pre-1993 vehicles.** Shah et al 2019,
  `10.1080/15715124.2019.1687487`, state the AR&R 2011 limits derive from work
  spanning 1967 to 1993 on "old-fashioned vehicles" and that chassis design has
  changed considerably since. This project validates against AR&R, so this is a
  limitation that belongs in the text.
- **Published stability thresholds disagree with each other.** Bocanegra,
  Vallés-Morán & Francés 2019, `10.1111/jfr3.12551`, review the models, find
  thresholds "vary over a relatively wide range", and report several do not fit
  measured data well. This is the external justification for reporting a
  probability rather than a single cut.
- Kramer et al 2016, `10.1016/J.IJDRR.2016.04.003`, propose constant total head as
  the decisive parameter, **0.3 m for passenger cars and 0.6 m for emergency
  vehicles**, and find floating depths *higher* in prototype than in a watertight
  model. A second threshold family, currently not evaluated here.
- The Moving-Rigid-Body report states plainly that its records **do not establish
  an experimental basis for the 1.5 m/s rule**. That belongs in limitations.

## 7. Prior art: the novelty risk, unresolved

Four prior vehicle fording or wading simulations sit in this project's own
research output. Verified live: **none appears anywhere in `paper/`.**

| Work | Identifier | In repo |
|---|---|---|
| He et al 2026, physics-based and data-driven vehicle-water models, model-scale experimental validation plus flume load measurement | `10.1115/1.4071177` | 1 doc, not in `paper/` |
| Wasfy, Wasfy & Peters 2015, coupled multibody dynamics and SPH for vehicle water fording, Humvee-type | `10.1115/DETC2015-47142` | `citations/` only |
| Pazouki, Jayakumar & Negrut, fluid-MBS with point-cloud solid discretisation for FSI forces | Semantic Scholar `61da26b6` | `docs/` only |
| Khapane & Ganeshwade 2014, "Wading Simulation, Challenges and Solutions" | `10.4271/2014-01-0936` | **cited nowhere at all** |

Also uncited and corroborated by three or four separate reports each:
`10.1016/j.cma.2022.114809` (IFEMP), `10.1016/j.jcp.2016.10.064` (incompressible
MPM), `10.1016/bs.aams.2019.11.001` (MPM after 25 years),
`10.1504/pcfd.2019.10018820` (MPM FSI benchmark).

Al-Qadami et al 2022, `10.1111/jfr3.12828`, claim "for the very first time"
numerical simulation of a full-scale passenger vehicle **moving** perpendicular to
floodwaters, and report critical depth **0.38 m** and minimum depth x velocity
**0.39 m^2/s**. Any moving-vehicle novelty claim has to be positioned against it.

## 8. Reproducible reductions, for the known GPU float-accumulation issue

Two concrete methods, neither implemented (`kahan|compensated` and
`sorted/reproducible reduction` both return 0 files):

- Xu et al 2019, `10.1016/J.PARCO.2019.04.002`: sorting by force-component value,
  80-bit long double, and a full-neighbour-list method ordered by particle
  distance. Reproducibility at any parallelism for about **50% extra compute**.
- Siklósi, Mudalige & Reguly 2024, `10.3390/app14020639`: bitwise reproducibility
  for the unstructured-mesh motif, including a graph colouring that gives
  identical results regardless of partition count. Deployed in a production
  Rolls-Royce CFD application.

This matters here because the gates are discrete: an order-dependent reduction
can flip a pass/fail without changing the physics.

## 9. Cross-surface runbook: what is left, and who has to do it

Nothing in this section has been executed. The repo is public, the Overleaf token
is off local disk but unrotated, and `git push` plus `scripts/tacc.sh` are
soft-denied in this session's settings, so every outward step needs a human.

### GitHub, `jcerrell-IS/can-it-ford`
Three new files are staged in the working tree but **not committed**:
`analysis/stationarity.py`, `analysis/settle_audit.py`,
`analysis/probabilistic_verdict.py`, plus this document. Another session is live
in this tree, so stage explicit paths only, never `-A`.

```bash
git -C /Users/josie/can-it-ford add analysis/stationarity.py analysis/settle_audit.py analysis/probabilistic_verdict.py docs/RESEARCH_TO_IMPLEMENTATION_2026-08-15.md
git -C /Users/josie/can-it-ford commit -m "Add a data-driven settling criterion and probabilistic verdicts" -- analysis/stationarity.py analysis/settle_audit.py analysis/probabilistic_verdict.py docs/RESEARCH_TO_IMPLEMENTATION_2026-08-15.md
```

The repo's own pre-commit hook refuses more than 8 staged files, and pre-push
needs `PUSH_OK=1`. Both are deliberate.

### Wiring the new gate into CI
`.github/workflows/canford-checks.yml` runs three checks. Add a fourth step:

```yaml
      - name: stationarity self-test
        run: python3 analysis/stationarity.py
```

It is dependency-free and takes under a second, so it costs nothing per push.

### `jcerrell-IS/can-it-ford-demo`
Still serving the superseded bare-hazard-product L1 rule. Commit `4d228d9` is
single-copy and unpushed. Publishing it is a public-facing action on a separate
public repo and needs your explicit go.

### Overleaf
Do **not** push. The token is unrotated server-side, so a push is a
credential-touching action. Rotate in Overleaf account settings first, then the
paper edits from sections 6 and 7 can go up. The limitations text needs: the AR&R
pre-1993 vehicle basis, the absent experimental basis for 1.5 m/s, the
transient-versus-time-averaged grid point from section 2, and the four prior
fording works from section 7.

### Vista and LS6
Nothing here needs a GPU. That is the useful finding: the settle audit and the
probabilistic verdicts both ran on the laptop from data already on disk. The
allocation cache in this session was 9 days stale, so re-check before any claim
about SUs. The one genuinely GPU-bound item is the **g128 canonical set**, which
register J15 already names as the highest-value open run.

### Weights and Biases
Not touched. If the settle audit becomes routine, log `n_eff`, `tau_int` and
`recommended_discard` per run alongside the existing metrics so the settle
adequacy is visible per run rather than assumed.

### Hugging Face
`.github/workflows/sync-to-hub.yml` exists and pushes to a Space. Nothing here
changes it. Note that syncing publishes, so it is subject to the same public-repo
caution.

### Claude chat, the Project custom instructions
Cannot be written from here; it lives in the web UI. The paste-ready text is in
`~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/MEMORY_UPDATE_PASTE_BLOCK.md`,
Snippet 2. Add one line to it: the corpus now contains a working data-driven
settling criterion, and the fixed 8-frame settle is contradicted by all 25 local
runs.

Also unchanged and still true: this Project's GitHub sync points at
`jcerrell-IS/mpm-engine`, a fork of `kks32/mpm-engine`, **not** at this repo, so
none of the above reaches the Project knowledge base by committing.

## 10. Still not done, honestly listed

- 239 of 323 abstracts extracted but not read. Staged per report.
- Gate A4's other three parts: conservation/units gate, metamorphic tests, and a
  per-run manifest carrying the driver git SHA at run time. Note the constraint
  that editing `sim_standing.py` invalidates the driver sha256 stamping 40 runs,
  so the manifest wants a wrapper, not an edit.
- The 147 catalog rows from `Reliable_AI_Scientific_Software` and
  `MPM_Simulation_Verification_Provenance` still never diffed against the
  bibliography.
- NHTSA vPIC and USGS/NOAA fetches, RO-Crate packaging, an Apptainer `.def`, and
  Zenodo DOIs: all still absent, all still the cheap rigor wins.
- No citation added to `paper/` yet. Section 7 is a list, not a patch.
