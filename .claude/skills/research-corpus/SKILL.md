---
name: research-corpus
description: Query the project's own 332-paper external research index before making any method claim, novelty claim, citation, or "nobody has done this" statement, and before proposing a numerical method or a validation target. Trigger on "has anyone done X", "is this novel", "what do we know about", "which paper says", "what should we cite", "how should we validate", "what method should I use", any DOI about to enter paper/ or docs/, any claim that a technique is untried, and before writing Methods or Limitations text. Also trigger before proposing a settle length, a convergence claim, or a verdict threshold.
---

# The project's own research is indexed. Query it before asserting.

This project holds **332 distinct external papers** across eight Undermind
deep-research reports, 37 Claude artifacts, five Perplexity reports and two
Elicit extracts. Measured 2026-08-15: only **43 of the 332 reach a reader-facing
document** (`paper/`, `docs/`, `deliverables/`, `citations/`).

**DO NOT SAY "256 ARE CITED NOWHERE".** That clause was WITHDRAWN 2026-08-18: it took
the complement of *reach* (332 - 76 = 256) and reported it as *cited*, which are
different predicates measured different ways. The correct ladder is
**332 in the corpus / 76 with a DOI anywhere in the tracked tree / 43 reaching a
reader-facing directory / 4 in the shipped bibliography / 3 actually `\cite`d and
printing.** State the scope in the same sentence as any of these numbers. The failure mode this skill exists to stop is **asserting
something the corpus already answers**, in either direction: claiming novelty
that prior art contradicts, or proposing a method the reports already evaluated.

## The tool

`analysis/research_index.py`, pure standard library, reads the committed index at
`data/research_corpus_index.json`. It never touches `~/Downloads`, which has
returned EPERM in past sessions and made a recursive search silently report zero
hits.

```bash
python3 analysis/research_index.py --stats                    # method coverage
python3 analysis/research_index.py --method added-mass -v     # by method tag
python3 analysis/research_index.py --query "wall penetration" # free text
python3 analysis/research_index.py --doi 10.1002/nme.7217     # one paper
python3 analysis/research_index.py --gaps --method validation-dataset
```

Status flags in output: `IN-PAPER` reaches a reader-facing doc, `repo-only` is
cited somewhere in the tree but nowhere a reviewer looks, `UNCITED` appears
nowhere. Rebuild with `--build` only when a new report is added.

25 method tags exist. Run `--stats` rather than guessing tag names.

## Facts already established. Do not re-derive, do not contradict without evidence.

**Four prior vehicle fording or wading simulations exist and `paper/` cites none
of them.** Any novelty claim about simulating a vehicle in floodwater has to be
positioned against these first:

| Work | Identifier |
|---|---|
| He et al 2026, physics-based and data-driven, model-scale validated | `10.1115/1.4071177` |
| Wasfy, Wasfy & Peters 2015, multibody dynamics plus SPH, Humvee-type | `10.1115/DETC2015-47142` |
| Pazouki, Jayakumar & Negrut, fluid-MBS, point-cloud solid discretisation | Semantic Scholar `61da26b6` |
| Khapane & Ganeshwade 2014, "Wading Simulation, Challenges and Solutions" | `10.4271/2014-01-0936` |

Al-Qadami et al 2022 (`10.1111/jfr3.12828`) additionally claim "for the very
first time" a full-scale passenger vehicle **moving** perpendicular to
floodwaters, reporting critical depth 0.38 m and minimum depth x velocity
0.39 m^2/s.

**A fixed settle length is not defensible, and ours is contradicted by our own
data.** `sim_standing.py:154` uses `settle_frames=8`. `analysis/settle_audit.py`
run over 25 local runs: **all 25 need more than 8 frames discarded**, median 48
of 91, and N_eff is only 2.9 to 11.0, so any uncertainty computed from N=91 is
overstated roughly three to five times. Use `analysis/stationarity.py` to state a
settle length, never a constant.

**Grid refinement is not expected to converge a transient quantity.** Syamlal,
Celik & Benyahia 2017 (`10.1002/AIC.15868`). The non-monotone `final_disp_mag_m`
across g48/g64/g96 is documented expected behaviour for an instantaneous value.
If grid convergence is the claim, report a time-averaged observable over a
demonstrated-stationary window with a GCI.

**A verdict threshold is a choice that must be stated.** Incipient motion is
probabilistic and record-length dependent (Dancey et al 2002). Measured with
`analysis/probabilistic_verdict.py`: **17 of 24 runs flip verdict somewhere in
p >= 0.01 to 0.50**, and `g96_m2337` has a one-frame margin. Report a probability
and the cut, not a bare label.

**Removing the startup transient is wrong for a SLIDE verdict.** Incipient motion
is an event, not a steady state; the settling report says impact and water-entry
loading have no steady force and want peak or event statistics. Transient removal
is correct for a mean force, and only 5 of 24 runs still satisfy the slide
condition after it, which is a robustness diagnostic and not the verdict.

## Method families the corpus evaluated and this repo has never tried

Verified zero occurrences in `analysis/` and `simulation/`: **CPDI**, **GIMP**,
**moving-reference-frame MPM**. The multi-resolution report found no MPM study
anywhere that follows a rigid vehicle with a refinement window through a large
flood domain, and no moving-reference-frame MPM result at all, so this is both an
opening and untried.

Highest payoff per unit effort, with the reason:

1. `10.1002/nme.7217` Baumgarten & Kamrin 2023, spatial-integration-error
   mitigation. Targets particle ringing and solution-dependent integration error,
   and states it improves fluid-like MPM "without requiring significant
   augmentation of existing MPM frameworks".
2. Schulz & Sutmann 2019, image-particle boundaries. Grid-momentum-zeroing walls
   "distort the stress multiple grid lengths into the object", which is the
   smeared layer behind the seven P-2 failures at 7.99 to 15.88 percent water
   inside the hull bbox.
3. `10.1016/j.jcp.2016.10.064` hourglass damping and incompressible MPM by
   operator splitting, reported more accurate than the weakly compressible
   formulation this project runs.
4. `10.1016/j.cma.2022.114809` IFEMP, particle rearranging against numerical
   cavities, plus a sharp immersed interface for real two-way coupling.

**Precondition for any adaptive scheme:** fixed particles-per-cell can lose
convergence under refinement, so PPC must be co-refined or AMR silently changes
quadrature. Standard MPM, GIMP, CPDI and B-spline MPM are not interchangeable.

## Validation targets that exist and are unused

`--method validation-dataset` returns 76 papers, 65 of them uncited. The repo has
a physics regression test **as of 2026-08-18**: `tests/test_physics_gates.py`,
added by `df52bee` ("Run the solver's own analytic suite on a GH200, and wire it in"),
carrying 12 test functions and covering Poiseuille, Couette and closed-form analytics.
`tests/` also holds `test_count_claims_check.py` and `test_csv_schema.py`.
**The earlier claim that no physics regression test exists is STALE. Do not build a
second one without reading that file first.**

- **Analytical, no download needed:** Poiseuille and Couette flow are the standard
  MPM fluid verification cases with exact closed-form solutions
  (`10.1504/PCFD.2016.10001222`). This is the natural content for a locked CI
  regression test.
- **`10.3390/en14020269`** floating-sphere heave decay, 0.3 percent uncertainty at
  95 percent confidence, three drop heights, with a test case formulated so
  readers can run their own numerics. Closest published analogue to this
  project's buoyancy-and-settle problem.
- **`10.1016/J.JFLUIDSTRUCTS.2019.01.015`** dam-break onto a vertical cylinder,
  with gate motion, pressures and video supplied.
- **`10.1504/pcfd.2019.10018820`** MPM FSI benchmark, three method-matched cases.

## Framing constraints the corpus imposes on the paper

- **AR&R's limits rest on pre-1993 vehicles.** Shah et al 2019
  (`10.1080/15715124.2019.1687487`) state the AR&R 2011 guidelines derive from
  work spanning 1967 to 1993 on "old-fashioned vehicles". This project validates
  against AR&R, so it is a limitation, not a strength.
- **Published stability thresholds disagree.** Bocanegra et al 2019
  (`10.1111/jfr3.12551`) find they "vary over a relatively wide range" with
  several models not fitting measured data.
- **There is no experimental basis for the 1.5 m/s rule** in the corpus. Say so
  rather than implying one.
- **Added mass is not constant during acceleration.** Grift et al 2019
  (`10.1017/jfm.2019.102`) show prolonged acceleration is not captured by a single
  added-mass coefficient and define an entrainment rate instead.

## Known limits of the index itself

- **60 of 332 papers carry no DOI** and cannot be diffed against the bibliography.
  Absence from an uncited list is not proof of absence.
- **222 of 332 have an abstract.** Each report details only its top 50, so 110
  papers are title-and-metadata only. Do not describe a metadata-only paper as
  read.
- Method tags come from regex over title and abstract, so a metadata-only paper is
  under-tagged. Widen with `--query` before concluding the corpus is silent.
- The index excludes `.claude/worktrees/` when computing cited status, per the
  standing H0 rule. An earlier version did not and reported 269 of 332 as cited
  because another session's cross-reference file holds 489 DOIs.

---

# THE INDEX IS NOT THE WHOLE CORPUS. THE DEEP-SEARCH LAYER IS MISSING FROM IT.

Added 2026-08-19 after a session manually re-derived a vehicle-mesh finding that a
completed deep search had answered in full on 21 July.

`data/research_corpus_index.json` was built from **44 documents that are Claude
artifacts and Perplexity reports.** The Undermind workspace holds **19 completed deep
searches**, and eight checked by name are **all absent from those 44**. So querying the
index and finding nothing is NOT evidence the project has not researched something.

**Workspace id `17299f2a-8dc8-438b-8c84-5abf19395e2c`.** Query it directly:

```
mcp__undermind__inspect_deep_searches(workspace_id=..., names=[])        # list all 19
mcp__undermind__inspect_deep_searches(workspace_id=..., names=['/NAME']) # goal + summary + ranked papers
```

The nineteen, with what each actually settles:

| deep search | settles |
|---|---|
| Simulation Ready Vehicle Mesh Assets | the CCSA/NCAC vehicle models, below |
| Moving Rigid Body Free Surface Validation | validation cases for a moving body |
| Quantitative MPM Wall Penetration | the mechanism behind the seven P-2 failures |
| Multi-resolution MPM for Large-domain Flooding | refinement windows, and the moving-frame gap |
| moving vehicle floodwater GPU particle simulation | the moving-vehicle prior art |
| which realism effects change a flood vehicle stability verdict | which realism upgrades move a verdict |
| MPM SPH buoyancy force overestimation and hydrostatic validation benchmarks | the buoyancy error |
| Settling and Force Reporting in Free Surface Flow | settle length and force statistics |
| GPU particle solver portability scaling and surrogate fidelity | engine and GH200 portability |
| Dynamic Vehicle Traction in Floodwater | traction under partial flotation |
| Validated MPM Vehicle Water Coupling | coupling validation |
| Incipient / stability searches (Jul 15) | threshold provenance |
| how computational researchers audit and defend simulation credibility | verification practice |
| plus 6 more, see the live listing |

## THE VEHICLE MESH ANSWER, so nobody re-derives it again

From "Simulation Ready Vehicle Mesh Assets", 21 July, 36 papers. The NHTSA-grade assets
are the **CCSA/NCAC reverse-engineered LS-DYNA finite-element vehicles**:

    2010 Toyota Yaris         passenger sedan           MASH 1100 kg vehicle
    2012 Toyota Camry         MIDSIZE sedan             teardown part-by-part; parts
                                                        catalogued, scanned, thickness
                                                        measured, material classified;
                                                        mass and inertia checked against
                                                        the production vehicle
    2007 Chevrolet Silverado  quad-cab light pickup     MASH 2270 kg vehicle

All three carry NHTSA NCAP full-scale validation. Yaris and Silverado include working
suspension and steering.

**THE NISSAN ROGUE IS NOT ONE OF THEM.** The documented midsize is the Camry. This
repo's `MASS = {"rogue": 1571.3}` has no MASH anchor and no teardown provenance, while
`silverado: 2270.0` and the Yaris 1100 kg ARE the MASH designations exactly.

**HARD NEGATIVE, stated as a finding by that search:** no citable, publicly
redistributable OBJ / PLY / glTF / USD conversion of the Yaris, Silverado or Rogue
models is verified to exist anywhere, including GitHub, Kaggle and Hugging Face.
So this repo's `.ply` hulls are its OWN conversions, there is no external artifact to
check them against, and `vehicle_mesh_pipeline.py` (in `~/Downloads/vehicle_meshes/`,
UNTRACKED, with `_v5` and `_v6` revisions) is the only provenance any hull has.

Measured hull fidelity, from PLY headers 2026-08-19:

    yaris_coarse_v1l_watertight.ply                 327,212 vertices
    rogue_g96_pd6_coarse_watertight.ply              31,357 vertices
    silverado_g32_pd8_dq0.02_coarse_watertight.ply    2,108 vertices   <-- 155x coarser

Better hulls exist unused in `~/Downloads/vehicle_meshes/` (52 files):
`rogue_coarse_watertight.ply` 66,987 and `silverado_coarse_watertight.ply` 48,706.

# `--query` CANNOT FIND WHAT YOU PROBABLY WANT

`analysis/research_index.py:518-521` is a **literal substring match over `title` and
`abstract` only.** It does NOT search `authors`, `methods`, `journal` or `doi`.

- An author query can never match. `--query "Al-Qadami"` returns 0 while **five records
  carry Al-Qadami as an author**. A zero here is structurally guaranteed, not measured.
- 110 of 332 records have no abstract, so for a third of the corpus it is title-only.
- Any paraphrase fails: "moving reference frame" misses "moving frame of reference".

Use `--doi` for a known paper, read the JSON fields directly for anything else, and
never report an absence measured with `--query` alone.
