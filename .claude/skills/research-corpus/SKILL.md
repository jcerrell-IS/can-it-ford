---
name: research-corpus
description: Query the project's own 332-paper external research index before making any method claim, novelty claim, citation, or "nobody has done this" statement, and before proposing a numerical method or a validation target. Trigger on "has anyone done X", "is this novel", "what do we know about", "which paper says", "what should we cite", "how should we validate", "what method should I use", any DOI about to enter paper/ or docs/, any claim that a technique is untried, and before writing Methods or Limitations text. Also trigger before proposing a settle length, a convergence claim, or a verdict threshold.
---

# The project's own research is indexed. Query it before asserting.

This project holds **332 distinct external papers** across eight Undermind
deep-research reports, 37 Claude artifacts, five Perplexity reports and two
Elicit extracts. The failure mode this skill exists to stop is **asserting
something the corpus already answers**, in either direction: claiming novelty
that prior art contradicts, or proposing a method the reports already evaluated.

## READ THIS FIRST: the index holds 8 of the project's 20 deep searches

Measured 2026-08-19 against the live Undermind workspace
`17299f2a-8dc8-438b-8c84-5abf19395e2c`. **A negative result from this index is
NOT a negative result for the project's research.** Twelve completed deep
searches are not in it: six predate the index build of 2026-08-15 and were never
ingested, six postdate it. Run `python3 analysis/research_index.py --coverage`
for the current ladder and the full list.

**Why `--build` will not fix it:** `REPORTS` in `analysis/research_index.py` is a
hardcoded list of eight local file paths. The builder has no directory scan, no
glob and no API call, so it cannot discover or reach a deep search. Adding one is
two manual steps that nothing automates or checks. **The gap therefore grows
silently every time anyone runs a search.**

**What this has already cost:** the `Simulation Ready Vehicle Mesh Assets` search
of 21 July answers the vehicle-mesh provenance question in full, covering the
CCSA/NCAC LS-DYNA models, the MASH designations (the 2010 Yaris is the MASH
**1100 kg** vehicle, this project's exact vehicle and mass), and the explicit
negative finding that no citable public OBJ/PLY/glTF/USD conversion of the Yaris,
Silverado or Rogue models exists. None of it is indexed, and `--query` returns
**0** for `Silverado`, `Camry` and `Toyota Yaris`. A session re-derived part of it
by hand on 2026-08-19.

**So before concluding the project has not researched something, check the
workspace, not just this index.**

## The ladder. Five numbers, five different predicates, never one number.

Scope, stated here because it decides every figure below: index built 2026-08-15,
tracked tree only, **`.claude/worktrees/` excluded**, bibliography read at
`overleaf/main:can_it_ford_references_IEEE.bib` and paper source at
`overleaf/main:conference_101719_1.tex`.

| n | predicate | how it is measured |
|---|---|---|
| **332** | papers in the corpus | distinct records in the index |
| **76** | DOI-shaped string **anywhere in the tracked tree** | `cited_in_repo` |
| **43** | DOI-shaped string in a **reader-facing directory** | `cited_reader_facing`, meaning `paper/` `docs/` `deliverables/` `citations/` |
| **4** | hold an entry in the **shipped bibliography** | census against the 15 entries on `overleaf/main` |
| **3** | are `\cite`d, so they **print in the reference list** | census against the 14 distinct cite keys |

**"REACH" IS NOT "CITED", AND THIS FILE USED TO SAY IT WAS.** Corrected
2026-08-19. This section previously read "43 of the 332 reach a reader-facing
document, and **256 are cited nowhere at all**". That clause is **WITHDRAWN**. It
took the complement of *reach* and reported it as *cited*, which is a different
predicate measured a different way. The arithmetic is **332 - 76 = 256**, so the
number is the complement of the **76** rung, DOI-string-appears-anywhere, and it
was published under the word "cited", which is the **3** rung. Two rungs apart.
`CLAUDE.md` withdrew the identical clause on 2026-08-18; this file was not
updated with it and kept asserting the retracted number for a day.

Why the two cannot be collapsed: **reach** asks whether a DOI string appears in a
directory. **Cited** asks whether a bibliography entry exists and a `\cite`
command references it. A paper can be named in twelve `docs/` files and still
print nowhere. That is not an edge case, it is the normal case here: **40 papers
reach a reader-facing directory without reaching the reader.** 43 and 3 are both
correct and answer different questions. The field names `cited_in_repo` and
`cited_reader_facing` are what mislead. The data is internally consistent, so do
not go looking for a data bug.

**Never quote a rung without its scope, and never quote the complement of one
rung as if it were another.** An earlier index build that failed to exclude
`.claude/worktrees/` reported 269 of 332 as cited, because another session's
`r5_citation_xref.tsv` carries 489 DOIs.

**60 of the 332 carry no DOI at all**, so they are excluded from the 76 and the 43
by construction. The denominator for any DOI-join statement is **272, not 332**.

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
python3 analysis/research_index.py --bib-audit                 # corpus vs the bib
python3 analysis/research_index.py --coverage                  # what is NOT indexed
```

`--bib-audit` censuses the shipped bibliography against the corpus AND against
the eight source reports, and every row states the ROUTE it matched or failed to
match by, plus the best rejected candidate and its score. Name the ref with
`--bib-ref`: the entry count is **21** on `origin/main`, **42** on
`claude/add-ci-checks` and **15** on `overleaf/main`, so a bare bibliography
count is wrong on two of the three. It ends with an INDEX SELF-CHECK. It refuses
to run at all unless all eight source reports load, because a partial read would
silently report works from the unread reports as never ingested.

Status flags in output, and read these as REACH, not as citation: `IN-PAPER` means
its DOI string appears in a reader-facing directory, `repo-only` means the string
appears somewhere in the tree but nowhere a reviewer looks, and `UNCITED` means
the string appears **in no tracked file**. None of the three tells you whether the
paper is in the bibliography or is `\cite`d. For that, run `--bib-audit`. In
particular `UNCITED` is automatic for the 60 records with no DOI, because the
match is gated on having a DOI at all, so for those it is a statement about the
record and not about the repo. Rebuild with `--build` only when a new report is
added.

25 method tags exist. Run `--stats` rather than guessing tag names.

### Four traps that return a FALSE ZERO. A zero from any of them looks exactly like absence.

**1. `--query` searched only titles and abstracts until 2026-08-19, never authors.**
So every author-name query returned zero regardless of the corpus contents.
Measured that day: `--query "Al-Qadami"` returned **0 match** while **5** records
carry Al-Qadami in `authors`, including `10.1111/jfr3.12828`, the moving
full-scale vehicle paper this project's own prior-art section cites. A
coordinating session used that zero as evidence the corpus was silent on the
project's closest prior art. It was not: 4 of the 6 flood-vehicle DOIs in that
check were present. **Fixed**, `--query` now searches authors too. If you are
reading an older checkout, search the authors field directly before concluding
absence.

**2. `--query` is a LITERAL SUBSTRING match, and for a third of the corpus it is
title-only.** It does not stem and does not survive a paraphrase. **110 of the
332 records have no abstract**, so for those a topic query can only match words
appearing in the title. `--query` now prints that ratio to stderr on every run,
so a zero arrives with its own caveat attached. A search for "vehicle fording
feasibility" returns 0 and that is nearly meaningless.

**3. An author's name is not their work.** Even with the fix, a surname hit is a
surname, not an identity, and a miss on one work by an author whose other work is
present is the interesting case rather than a null result. The corpus holds six
papers from the Shah/Mustaffa flood-vehicle group and **not** `shah2018`
(`10.1051/matecconf/201820307003`), which the paper cites. Beware short surnames
in the other direction too: a substring search for "Xia" returns **23** records,
nearly all of them hits inside given names such as "Lingxiao" and "Xiao-Guang".

**4. Testing deep-search membership against the `documents` list.** `documents`
holds Claude artifacts, Perplexity reports, Elicit extracts and bibliographies,
and **never holds a deep search**: those live in `source_reports`. A session
checked eight deep-search names against `documents` on 2026-08-19, got nothing,
and reported "eight of eight absent". Three of the eight were ingested. Use
`--coverage`, which reads the right container.

**Before writing "the corpus has nothing on X", run at least two of: `--query`
against the term, a direct DOI check, an author check, and `--coverage` to see
whether the relevant deep search is even indexed. State which you ran.**
A single search that could not match the field you care about is not evidence of
absence.

## Facts already established. Do not re-derive, do not contradict without evidence.

**Four prior vehicle fording or wading simulations exist and none of them prints
in the reference list.** Any novelty claim about simulating a vehicle in
floodwater has to be positioned against these first:

| Work | Identifier |
|---|---|
| He et al 2026, physics-based and data-driven, model-scale validated | `10.1115/1.4071177` |
| Wasfy, Wasfy & Peters 2015, multibody dynamics plus SPH, Humvee-type | `10.1115/DETC2015-47142` |
| Pazouki, Jayakumar & Negrut, fluid-MBS, point-cloud solid discretisation | Semantic Scholar `61da26b6` |
| Khapane & Ganeshwade 2014, "Wading Simulation, Challenges and Solutions" | `10.4271/2014-01-0936` |

**"Cites none of them" was sharpened 2026-08-19, and A BIB ENTRY IS NOT A
CITATION.** On `claude/add-ci-checks` all four now HAVE entries in
`paper/can_it_ford_references_IEEE.bib` (keys `he2026vehiclewater`,
`wasfy2015fording`, `pazouki2016fording`, `khapane2014wading`, added by slot
`d5-priorart`), so a DOI search over `paper/` now returns hits and a naive
re-check would call this claim stale. It is not: **zero of the four appear in any
`\cite` command in `paper/conference_101719.tex`**, so BibTeX drops all four and
none reaches the reader. Same reach-versus-cited distinction as the ladder at the
top of this file. On `origin/main` they have no entries either.

Al-Qadami et al 2022 (`10.1111/jfr3.12828`) additionally claim "for the very
first time" a full-scale passenger vehicle **moving** perpendicular to
floodwaters, reporting critical depth 0.38 m and minimum depth x velocity
0.39 m^2/s. **That paper IS in the corpus**, along with four others by the same
group, which is worth knowing because a `--query` on the author name returned
zero until the fix above.

**The corpus is NOT a superset of the bibliography, and that is a sourcing gap
rather than a dropped merge.** Measured 2026-08-19, scope `overleaf/main`: of the
14 works the paper `\cite`s, 3 are in the corpus and 11 are not, and the 11 are
absent from the **raw text** of all eight source reports, which is upstream of
the index build. But they are not 11 of the same thing: 3 preprints, 1 GitHub
repo, 1 web page, 1 crash-test FE model, 2 techreports, and 3 peer-reviewed of
which two are computer graphics. A literature search does not return software
repositories or government pages, so that is a category boundary. **Exactly one
in-scope absence: `shah2018`.** Do not quote "11 of 14" as a corpus quality
figure. Full working in `docs/R9_CORPUS_BIB_GAP_2026-08-18.md`.

**A fixed settle length is not defensible, and ours is contradicted by our own
data.** `sim_standing.py:154` uses `settle_frames=8`. `analysis/settle_audit.py`
run over 25 local runs: **all 25 need more than 8 frames discarded**, median 48
of 91, and N_eff is only 2.9 to 11.0, so any uncertainty computed from N=91 is
overstated roughly three to five times. Use `analysis/stationarity.py` to state a
settle length, never a constant.

**THE "25 RUNS" DENOMINATOR NEEDS ITS SCOPE.** Added 2026-08-19 from slot
`d15-settle`'s committed `docs/R9_SETTLE_FRAMES_2026-08-18.md`, not re-derived
here. That 25 is records under `renders/` **with duplicates kept**; 3 of them are
byte-identical duplicates of their `_incoming/` originals (md5-confirmed), so
**the audited population was 22 distinct records presented as 25**. It also
includes `renders/mpm-engine-out/flood_vehicle`, which is the bundled model-scale
truck, not the Yaris and not full scale. The true population is **51 on disk, 48
distinct**, and on that corrected scope, on the `dx` channel the SLIDE gate
actually reads, the finding gets STRONGER: **48 of 48 need more than 8 frames
discarded**, min 29, median 54, max 80.

Also do not put the `settle_frames=8` citation and the discard statistic in
adjacent sentences without saying they are DIFFERENT QUANTITIES. They are, and
the adjacency invites the invalid inference "so `settle_frames` should be 48".

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

**NEVER QUOTE THAT 17 AS A BARE INTEGER: IT CARRIES A CHANNEL.** Added 2026-08-19.
`analysis/probabilistic_verdict.py` gates `p_move` on the MAGNITUDE channel
(`dmag`, `vmag`) while `simulation/failure_modes.py` gates SLIDE on the SURGE
axis (`SURGE_AXIS = 0`, so `|dx|` and `|vx|`). Since `dmag >= |dx|` and
`vmag >= |vx|` elementwise, **every published `p_move` is an UPPER BOUND** on the
classifier's own gate. On the corrected surge channel slot `d2-persist` measured
**15 of 24** flipping, and full-record SLIDE going from **21 of 24 to 19 of 24**,
each reproduced exactly on the committed channel first as a held-fixed control.

**17 and 21 remain the correct figures for the code as committed**, because
d2-persist's diff is DELIBERATELY UNAPPLIED pending a human decision. Both sets
are right and answer different questions. Quote the channel with the number, every
time.

Unresolved as of 2026-08-19, flagged rather than silently picked: `d2-persist`
records the mapping as "17 of 24 flip -> 15 of 24", while `d15-settle`'s committed
`docs/R9_SETTLE_FRAMES_2026-08-18.md` records "the 21 of 24 and 5 of 24 figures
are on the COMMITTED magnitude channel; on the corrected surge channel
d2-persist measured 19 of 24 and 15 of 24". Those disagree about WHICH figure
becomes 15. Neither has been re-derived here. Do not repeat either mapping as
settled until the two slots reconcile it.

**Removing the startup transient is wrong for a SLIDE verdict.** Incipient motion
is an event, not a steady state; the settling report says impact and water-entry
loading have no steady force and want peak or event statistics. Transient removal
is correct for a mean force, and only 5 of 24 runs still satisfy the slide
condition after it, which is a robustness diagnostic and not the verdict.

## Method families the corpus evaluated and this repo has never tried

**No implementation** in `analysis/` or `simulation/`: **CPDI**, **GIMP**,
**moving-reference-frame MPM**. Re-measured 2026-08-19 and the wording is now
narrower than "verified zero occurrences", which had become literally false: a
case-insensitive search returns 2 hits for CPDI and 1 for GIMP, and **all three
are inside `analysis/research_index.py` itself**, in this index's own method-tag
regex table and a usage example. The tool that measures the absence is what
falsifies the string form of the claim. `moving.reference.frame` is still a true
zero. The substantive claim stands: no CPDI, GIMP or moving-reference-frame
scheme is implemented here. The multi-resolution report found no MPM study
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

`--method validation-dataset` returns 76 papers, 65 of them carrying no DOI-shaped
string anywhere in the tracked tree, `.claude/worktrees/` excluded (22 of the 76
have no DOI at all, so they cannot match by construction).

**THE "NO PHYSICS REGRESSION TEST" CLAIM IS STALE AND IS WITHDRAWN.** Corrected
2026-08-19. This paragraph read "The repo has **no physics regression test**;
`tests/` holds only `test_count_claims_check.py` and `test_csv_schema.py`." That
was true when written and stopped being true on 2026-08-18, so the file was
simultaneously recommending Poiseuille and Couette as "the natural content for a
locked CI regression test" and asserting no such test existed. **A session
reading it today could build a second one.**

Live, and the answer is REF-DEPENDENT, so name the ref:

| ref | `tests/` contents |
|---|---|
| `origin/main` | `test_count_claims_check.py`, `test_csv_schema.py`. The old claim is still TRUE here. |
| `claude/add-ci-checks` and every r8/r9 branch | the above **plus `tests/test_physics_gates.py`** |

`tests/test_physics_gates.py` was **added by `50b70c0`** ("Add the three physics
gates: analytical, conservation, metamorphic") and extended by `df52bee` (+30/-7,
which also added `scripts/run_analytic_benchmarks_vista.sh`). It carries **12 test
functions** covering exactly the recommendation two paragraphs above: Poiseuille
against its governing equation, no-slip and peak, mean-is-two-thirds-of-peak,
Couette linearity and superposition with Poiseuille, plus conservation
(particle-count, finite-and-bounded metrics, unit anchors) and metamorphic gates
(verdict invariance under grid refinement, heavier-vehicle ordering).

It RUNS, pure standard library, no pytest needed: `python3 tests/test_physics_gates.py`.
Measured 2026-08-19: **0 failures**, and the skip count depends on where you run it.

- **Main checkout: 1 skip.** Only the solver-vs-analytical comparison, which waits
  on solver output at `tests/data/poiseuille_profile.csv`. That is the genuine
  outstanding item and it needs a Vista run.
- **A worktree: 5 skips.** The extra four are `renders/` data being physically
  absent from a worktree, not a gap in the suite. **Do not read a worktree skip
  count as an open gap**, which is the same worktree-absence trap that has
  produced false counts in this repo before.

`.github/workflows/canford-checks.yml:31` runs it as `python3 tests/test_physics_gates.py`.
**But that workflow is NOT on `origin/main` either**, so as of 2026-08-19 the gate
exists, passes, and executes nowhere automatically until that branch lands. The
honest statement is "built and green, not yet running in CI on the default
branch", never "no physics regression test".

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
- **Three records are in the index with an EMPTY DOI and raw markdown left in
  their title**, so they can never be marked cited however often the repo cites
  them: `settling-force#11`, `#29`, `#30`. Cause: `parse_report` pulls the DOI
  with a `[link](url)` regex, that report escapes its brackets, and an ASCE DOI
  legitimately contains parentheses, so the non-greedy match truncates. **One of
  them is Dancey et al 2002** (`10.1061/(ASCE)0733-9429(2002)128:12(1069)`), which
  this file cites above for the verdict-threshold claim. So 3 of the 60 no-DOI
  records are a parse bug, not a source without a DOI. `--bib-audit` prints an
  INDEX SELF-CHECK that detects this class. **The data has NOT been repaired**,
  because that needs a `--build` which would move the 332, the 60 and the 76/43
  rungs; whoever owns the index build owns the fix.
- **The index cannot report its own coverage of the bibliography.** Use
  `--bib-audit` for that, and see the two false-zero traps above before making
  any absence claim.
