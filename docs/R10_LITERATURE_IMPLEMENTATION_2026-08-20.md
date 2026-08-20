# EVERY LITERATURE SOURCE THIS PROJECT PAID FOR, READ AND ROUTED

Written 2026-08-20 03:0x, completing section 13A of `docs/R9_SESSION_HANDOFF_2026-08-20.md`.
Companion to `docs/R10_JOURNAL_AUDIT_2026-08-20.md`, which covers the two workflow journals.
This file covers the rest: all 21 deep searches, the five unread audit documents, the paper
stores on disk, and the Claude artifacts. Everything below was read live in this session
unless marked otherwise.

**What changed as a result, in code:** `analysis/research_index.py` (four fixes),
`analysis/cm_floor_check.py` (new), `data/deep_searches/` (22 new tracked files),
`.gitignore` (two un-ignore pairs). Commits `de891a9` and the three record batches.

---

## 1. ALL 21 DEEP SEARCHES ARE NOW OPEN, AND FOUR OF THEM ALREADY ANSWERED LIVE QUESTIONS

The corpus index reached 8 of 21. The other 13 were invisible to every query for five weeks.
All 21 were pulled live from workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c` and written to
`data/deep_searches/`, which is now tracked. Query them:

```bash
python3 analysis/research_index.py --searches --query crowned
```

### 1.1 The missing tolerance was never missing. It was in a July search.

Handoff section 4.3 concludes that no canonical floating-body benchmark states a quantitative
tolerance on a static force, so any band is this project's own choice. **That conclusion
stands.** What "Physics Simulation Validation Protocol" (81 papers, 2026-07-15, never opened)
supplies is what to do instead, in ASME V&V 20 vocabulary:

> "At each validation point report signed discrepancy and a validation interval combining
> reference-data, numerical, and parameter uncertainty; this estimates model error rather than
> producing a binary 'validated' status."

A validation interval REPLACES a tolerance. The question "what band do I inherit" has no
answer because it is the wrong question. It also prescribes at least three grid and timestep
refinements with observed order and Richardson/GCI intervals for every decision quantity, and
keeping aleatory and epistemic uncertainty separate.

**And the line that bears on the paper's own contribution:**

> "Decision credibility, not numerical agreement, is the governing endpoint: a FORD claim
> requires validated six-DOF outcomes and a conservative margin to the hazard threshold,
> whereas a NO-FORD claim may be issued whenever uncertainty spans or exceeds that boundary."

**All 17 gated runs are NO-FORD.** That asymmetry licenses the project's published result
under exactly the uncertainty it has. It is a stronger version of the handoff's section 6.4
reframe and it arrives with a citation chain.

### 1.2 The crowned road is genuinely novel, confirmed by a search nobody opened

"which realism effects change a flood vehicle stability verdict" (47 papers, 2026-08-18):

> "Road/tyre friction and vehicle watertightness have the clearest demonstrated power to
> change a flood-stability verdict; slope and flow orientation also matter, whereas **no
> retrieved study quantifies a crowned or cambered road against a flat plane**."

That is the novelty claim for the crown work, established independently of the session that
did it. The same search settles four more things:

- **The ten-times-flow-speed sound-speed rule has no primary derivation.** It is convention.
- **No retrieved study shows air entrainment, spray, surface tension, turbulence closure,
  reduced sound speed, or outlet-boundary choice flipping vehicle motion.** That is a
  ranked do-not-spend-GPU-here list, measured rather than asserted.
- A 5 percent grade study reports buoyancy onset at 0.055 m model depth, but it is not a
  flat-road comparison.
- No source isolates a sealed-versus-flooding threshold difference in metres.

### 1.3 The surrogate design literature reaches the settle result by a different route

"Small Data Physics Surrogates at 36 Conditions" (47 papers, 2026-07-15):

> "its effective sample size is the 36 conditions, not the 90 frames or mesh/particle count"

The settle work reached N_eff from a stationarity statistic on one record. This reaches the
same place from computer-experiment design. **Separate origins, so it counts as
corroboration.** It also says the defensible baseline at N=36 is a Gaussian-process response
surface with a separate classifier for the verdict, not a trajectory-level GNS, which
validates `analysis/gp_surrogate.py` as the right family. And it prescribes the split:
leave-one-condition-out, then leave-one-depth-row-out for interior rows only, because
omitting a boundary row tests extrapolation and must be reported separately. Random splits
leak grid neighbours.

**One limit worth carrying into any cross-vehicle claim:** pooling the three known classes
with mass and dimensions as inputs is defensible for interpolation *within* those classes and
cannot substantiate transfer to an unseen class, because only three class levels exist.

### 1.4 The credibility search is the paper's methods section, already written

"how computational researchers audit and defend simulation credibility" (92 papers,
2026-08-18) answers, point for point, the problems the project actually has:

| the project's problem | what the search returns |
|---|---|
| `final_disp_mag_m` is non-monotone across g48/g64/g96 | "nonmonotone or nonconverged results should be treated as numerical uncertainty, **not reduced to spurious significant figures**" |
| a binary verdict from unconverged continuous quantities | "the useful object is a **robustness or failure-probability statement over record length, friction, resolution, and model assumptions**" |
| what tolerance grades a comparison | threshold-based validation "relates comparison error to **distance from the engineering threshold**" |
| Shah is 1:10 scale, three orders from full scale | a scale-mismatched benchmark supports **partial validation only**, unless a hierarchy of shared-physics tests links it |
| Chrono builds on both architectures | "**cross-architecture agreement is evidence of robustness, not physical validity**" |
| two accessors agreed and the agreement was forced | documented traps include "**agreement for the wrong reasons**" |
| the round refuted several of its own claims | null and self-refuting results "are strongest when reported as sensitivity, uncertainty, and decision-boundary findings rather than buried" |

The second row is the same recommendation an R10 agent reached independently, that the binary
verdict be published as a robustness statement with the deterministic 16 SLIDE / 1 STUCK
demoted to one point on it, with every input already on disk and no cluster time needed.

### 1.5 Prior art, implementations and the reproducibility gap

From "moving vehicle floodwater simulation open source implementations" (105 papers) and
"moving vehicle floodwater GPU particle simulation" (48 papers), both never opened:

- **Body-fixed formulations are established for Eulerian immersed-boundary and level-set
  solvers but are NOT evident as a developed moving-reference formulation for MPM, and a
  body-following refinement window appears unreported.** That is the moving-vehicle novelty,
  confirmed independently.
- Reusable open-source routes, named: DualSPHysics with Project Chrono DVI coupling and
  Chrono::FSI vehicle-fording models; OpenFOAM overset and dynamic meshes; **FloatStepper**
  with released code and added-mass treatment; **sdfibm**, signed-distance immersed
  boundaries, which is this project's collider architecture in another code; and IBAMR, which
  uses force constraints rather than surface-stress integration.
- **Al-Qadami's record does not expose its motion algorithm or wheel model**, so its 0.38 m
  and its depth-velocity threshold cannot be reproduced from the paper.
- **The reproducibility gap is a publishable contribution nobody has claimed.** No supplied
  study reports, in one place, particle and grid counts, GPU model, wall time per simulated
  second, multi-GPU scaling, and a runnable case. This project has all of those.

### 1.6 The vehicle mesh provenance, and a third origin for the measured Yaris tensor

"Simulation Ready Vehicle Mesh Assets" (36 papers, 2026-07-21):

> "The Camry was dismantled part-by-part; parts were catalogued, scanned, thickness-measured
> and material-classified, **with model mass and inertia checked against the production
> vehicle**. Yaris and Silverado include functioning suspension/steering and extended impact
> validation."

The documented CCSA/NCAC set is **2010 Yaris, 2012 Camry, 2007 Silverado**. Not the Rogue.
And **no citable, publicly redistributable OBJ/PLY/glTF/USD conversion of any of them is
verified**, which bears on register E8.

This is a third independent origin for the claim that a measured 2010 Yaris inertia tensor
exists, against CLAUDE.md item 4 extension (a). See section 3.1.

### 1.7 Geometry, traction, and portability, in one line each

- **Optical Vehicle Collision Geometry** (23 papers): treat appearance geometry, contact
  geometry and inertial parameters as **three distinct assets**. Laser point-cloud vehicle
  reconstruction reports mean signed deviations of +1.36 and -1.14 cm against the original
  body, which is a geometric accuracy benchmark this project's hull has never been held to.
  Inertia errors materially affect 3-D trajectories, and pendulum-based measurement work
  cautions that simple estimators are inadequate, which supports item 4's refusal to wire the
  box estimate from a direction item 4 does not currently use.
- **Dynamic Vehicle Traction in Floodwater** (43 papers): tire-scale flooded-pavement work
  supplies a **depth- and speed-dependent tire-force law**, not a fixed coefficient. Off-road
  egress models include buoyancy, suspension, soil reaction and wheel loading.
- **GPU particle solver portability** (56 papers): see section 3.2. It could not confirm the
  premise of CLAUDE.md's L-8.

---

## 2. WHAT THE FIVE UNREAD DOCUMENTS CONTAINED

### 2.1 An external falsifier with a hard floor, and it is now built and run

`R10_WEB_ACQUISITION_2026-08-19.md` section 3.2 names Baumgarten, Couchman and Kamrin
(`10.1002/nme.7217`, CC BY), which grades MPM variants against a theoretical minimum on the
fluid centre of mass, and points out that `rollout.npz` holds every water particle for every
frame, so it is pure post-processing.

**Built as `analysis/cm_floor_check.py` and run on all 17 canonical runs.** Results and the
three bugs in my own first pass are in section 4.

### 2.2 Findings that survive from the acquisition slot

- **Schulz 2019 cannot carry the sphere result**, on three independent grounds: it reports
  **von Mises stress, which is by construction blind to the hydrostatic part, and a buoyancy
  force IS that part**; refinement fixes their artefact after a fivefold grid cut, while ours
  survives 24 gradings; and it is "defined for boxes only", undefined on a sphere or a hull.
- **Fourtakas et al 2019** measure, in a still-water tank, a pressure dip near the wall
  boundary "on the order of 10 percent of the total pressure", and their kinetic-energy
  evolution figure for a 3-D still-water case is used as a **published pass criterion**, which
  is exactly the bodyless-column diagnostic. **The fix does not port**: a search of the
  vendored solver for density diffusion, delta-SPH or artificial viscosity returns nothing.
  There is no term here to correct. What transfers is the diagnostic and the magnitude scale,
  and 10 percent is well short of 35, which weakly argues a boundary term alone is not the
  whole story.
- **The well-posedness classification.** Zhao et al 2019's rule is that one boundary condition
  must control the kinematics. This project applies a per-frame Dirichlet velocity clamp on an
  upstream slab inside a domain closed by slip walls: **kinematic control at inflow, no
  outflow, momentum injected every frame into a box mass cannot leave.** That is a limitation
  statement the paper should carry.
- **`xiong2024`, the one bibliography entry that never prints, is the closest validated prior
  art.** Xiong, Liang, Zheng, Wang and Tong 2024, Water Resources Research,
  `10.1029/2023WR036739`, CC BY: a coupled model for entrainment, transport and deposition of
  vehicles in flood hydrodynamics, used to reproduce **a real flash flood that moved over 100
  vehicles, with results consistent with post-event report and survey.** BibTeX drops it
  because nothing cites it. That is a sourcing decision being made by a default.

### 2.3 A register-level threshold disagreement

`10.1111/jfr3.12828` (2022) gives critical depth 0.38 m and minimum depth-velocity **0.39
m2/s**. `10.3390/su151713262` (2023), by the same group, gives the same **0.38 m** depth and a
sliding threshold of **0.36 m2/s**. The depth agrees exactly and the depth-velocity figure
does not. **Anyone quoting a depth-velocity threshold from Al-Qadami must name the paper.**
The 2023 paper also reports drag DECREASING with Froude number and flow velocity, which runs
against the intuition behind this project's velocity sweep.

### 2.4 The method failure named three times, and my own fourth instance

`R10_WEB_ACQUISITION` section 3.13 records three cases in one night where "we do not have it"
meant "we never looked properly at what we already own": Kramer 2021 sitting in
`~/can-it-ford-refs/2026-08-16/` while three passes called it the most valuable unretrieved
item; 35 comparable long records already on Vista; and a DOI recorded in this project's own
register while its resolver called the work unfindable.

**Its standing fix, adopted here:** before recording any work as unobtainable, grep the
register and `~/can-it-ford-refs/` for its title and DOI.

**I added a fourth instance tonight, of the same family.** My own shell scan for raw DOI dumps
in `docs/` returned zero because my bracket expression was malformed. The file exists and
carries exactly 34 DOI strings. A false zero from a broken predicate, in the session auditing
false zeros.

**And the acquisition slot's clean negative is worth keeping:** across `~/can-it-ford-refs/`,
`~/Zotero/storage/`, `~/Downloads/vehicle_meshes/` and the Desktop corpus directory, a pool of
136 PDFs, **0 of 154 unreachable works are present.** The missing works are missing, not
mislaid. Local stores measured live tonight: 73 PDFs in `~/can-it-ford-refs/`, 25 in
`~/Zotero/storage/`, 3 in `citations/`, 170 in `~/Downloads`, 50 in the gapscan worktree.

### 2.5 The re-aiming section rests on a withdrawn premise

`R10_WEB_ACQUISITION` section 3.14 opens by relaying, and explicitly flagging as under review,
that "the instrument is exonerated". **That was withdrawn by its own author at 02:10 in commit
`87ae518`.** Its conclusions mostly survive anyway, because they rest on the disturbance being
at the floor rather than on the exoneration, but the section's framing should be read against
the withdrawal. Its narrowing of what to acquire next, to wall and floor boundary treatment
for weakly compressible particle methods measured at the boundary, survives intact.

---

## 3. THREE STANDING CLAIMS THAT NOW HAVE COUNTER-EVIDENCE

### 3.1 The measured Yaris tensor: three origins, one address

CLAUDE.md item 4 extension (a) states "It is not measured ... **No measured Yaris tensor
exists anywhere**: SAE 1999-01-1336 ends Nov 1998." Three independent sources now say
otherwise:

1. R10 agent `a2bcb1f09`, read-directly.
2. R10 agent `a25a0c14c`, read-directly, naming the location: **the very document the project
   cites as its own hull provenance, register E1, DOI `10.13021/G8JS5D`.**
3. The vehicle-mesh deep search, which records that the CCSA/NCAC Yaris carries measured or
   calibrated mass and inertial properties and functioning suspension and steering.

**This does not license wiring inertia.** Item 4's legs (b) and (c) are untouched: the solver
already computes a better tensor from the real hull particle cloud, and the documented axes
are transposed against the gated scene. Only leg (a) is in question, and it is one of three.

### 3.2 L-8's premise is unconfirmed by the literature

CLAUDE.md's AUGUST 5 RESEARCH INTEGRATION carries: "Engine decision: do not switch.
DualSPHysics ships x86-only static libraries, a hard aarch64 blocker on GH200."

The GPU-portability deep search, commissioned to test exactly this, returns:

> "The supplied literature neither confirms that the cited SPH package is intrinsically
> x86-only today nor documents an ARM-host CUDA build failure."

Separately, this project's own memory records Chrono::FSI-SPH building and running on Vista
aarch64 in 94 seconds. **The DECISION may still be right and the stated REASON is unverified.**
A conclusion resting on an unverified premise should say so.

### 3.3 L-4 has a documented counter-example, and the register already wants it deleted

L-4 reads: "Coarse resolution usually OVER-predicts peak hydrodynamic force. Over-threshold
NO-FORD verdicts are therefore conservative." Two independent hits:

- **Counter-example.** Smith and Mack 2014, reported in WRL 2014/07 section 6.3.2, found
  numerical models at 1 m, 5 m and 10 m grids **UNDER-predicted** peak local velocity around a
  building, against both a physical model and observed real-world damage.
- **Internal contradiction.** CLAUDE.md states L-4 as a flat rule while the register's Section
  I lists that exact sentence for deletion on sight.

L-4 is the argument that the published NO-FORD verdicts are safe-side. It cannot stay a flat
rule. Note the direction of the damage: an under-predicted force makes a NO-FORD verdict
*less* conservative, not more.

### 3.4 The register contradicts itself on `floor_friction`

Register item 29 (2026-08-18) asserts `floor_friction = 0.55` **is unsourced** and "nothing
sources it". Register G4a (2026-08-07) and the submitted paper both source it to a
spring-balance measurement by Azhar et al 2023. Two rows of the same corrections authority,
opposite verdicts, eleven days apart. This sits on top of the friction bracket of 0.024 to
1.15 across braked, rolling and washaway regimes.

---

## 4. THE FALSIFIER, BUILT AND RUN

`analysis/cm_floor_check.py`, run with Blender's Python because it is the only interpreter on
this Mac carrying numpy (2.3.4; all five system interpreters fail `import numpy`).

**The bound.** For a fluid of fixed volume confined above a floor,
`z_cm >= z_bottom + (A_tank - A_hull) * depth / (2 * A_tank)`, the centre of mass of the same
volume lying flat. No tolerance is chosen by anybody. The method is Baumgarten et al's; the
number is not, because their `2/3 m` belongs to their geometry.

**My first pass failed 23 of 23, which is the uniform-result signature this project
distrusts, and it was my instrument.** Three bugs, all pushing toward a false failure:
voxelising frame 0 overcounted the volume by **18.4 percent** at g64; the hull's plan area was
ignored, another **11 percent**; and the `floor` scalar is **not** the bottom of the water,
because the driver clamps at `floor - 0.25*dx` and **2334 of 48367 particles sit below `floor`
at rest**, before any dynamics.

**Corrected, all 17 canonical runs present on local disk:**

| group | margin, fraction of depth | frame of minimum | particles below clamp |
|---|---|---|---|
| g48 x3 | **-0.068** | **0** | **0** |
| g64 baseline x3 | -0.0006 to +0.0011 | 3 | 296 to 609 |
| g96 x3 | -0.018 | 1 | 0 |
| sweepD d0.25 / d0.35 / d0.45 | -0.050 / +0.014 / -0.014 | 3 to 5 | 373 / 231 / 275 |
| sweepV v0.5 to v3.0 | **-0.012 to +0.020, monotone** | 3 to 4 | 0.5 to 4.6 percent, monotone |
| m1100/m1609/m2337, **not canonical** | **-0.20** | **89** | **17.8 percent** |

11 of 17 canonical runs violate over the full record; **4 survive the settle transient**:
the three g48 runs at about -0.035 of depth, and `sweepD_g64_d0p25` at -0.009.

**Four things this shows.**

1. **The g48 runs violate at frame 0 with zero particles below the clamp.** That is the
   initial condition, not dynamics: at the coarsest grid the water is initialised in a state a
   volume-conserving fluid could not occupy. Those are the same three runs CLAUDE.md item 7
   flags for gate P-3, negative z rise, hull sank into the floor. **Two gates now flag the
   same three runs, one internal and one external.**
2. **The g64 baseline sits on the bound**, within 0.1 percent of depth, which is what weak
   compressibility at Mach near zero should look like.
3. **The sweepV margin is monotone in velocity**, from -0.0035 m at 0.5 m/s to +0.0060 m at
   3.0 m/s, and the below-clamp fraction rises monotonically with it too, 0.5 to 4.6 percent.
   That second trend matches item 7's independently recorded P-2 rise across the same sweep.
   A coherent physical trend is evidence the instrument measures something real.
4. **The three largest violations are not canonical runs.** `m1100`, `m1609` and `m2337` sit
   on disk beside the gated ones, violate by three times as much, and leak 17.8 percent of
   their particles below the clamp. The check reads membership from
   `data/all_runs_inventory.csv` so that split cannot be lost by a later reader.

**A pass here is not a validation.** It is a failure to falsify against a bound made
conservative four separate ways. That is still more than the gate set had, because the bound
comes from outside the pipeline.

**One unexplained observation, recorded rather than resolved.** At g64 about 2300 to 2800
water particles sit below the `floor` scalar at frame 0. At g48 and g96 the count is **zero**.
Nothing in this session explains a resolution-dependent initialisation difference of that
shape, and it should not be quoted as a defect until somebody reads the initialisation path.

---

## 5. WHAT WAS FIXED IN CODE

| file | change | defect it closes |
|---|---|---|
| `analysis/research_index.py` | reads `data/deep_searches/` | the index saw 8 of 21 searches |
| same | `--searches`, `--source-audit` | a search reaching the corpus by no route now exits 1 |
| same | `parse_report` records missing paths | a missing report wrote a smaller index and exited 0 |
| same | `RAW_SEARCH_DUMPS` excluded from reader-facing | `cited_reader_facing` inflated by exactly 9 |
| same | `--query` matches authors and journal | an author query returned 0 and the 0 read as coverage |
| `analysis/cm_floor_check.py` | new | no gate could fail for a reason outside the pipeline |
| `data/deep_searches/` | 22 tracked files | the searches were unreachable from a clone or worktree |
| `.gitignore` | two un-ignore pairs | `data/*` would have hidden both of the above |

Verified live after the change: `--query Al-Qadami` returns **5** where it returned 0,
`--source-audit` reports 21 searches with **0 reaching the corpus by no route**, and the
reader-facing delta from excluding the raw dump is **exactly 9**, reproducing
`docs/r10/corpus_revision.md` section 1.3.

---

## 6. THE CLAUDE ARTIFACTS

Six exist, all owned. `Console Against Can It Ford` (2026-08-17) is the one that matters and
**its headline finding is now false**: it concluded zero Anthropic rate or usage limits across
28 days and 72,126 turns, and the night of 2026-08-19 hit both a monthly spend limit and a
weekly limit. It should be marked superseded rather than left standing. What remains correct
and valuable in it: Console cannot see sessions or chats; the Admin, Usage-and-Cost and Claude
Code Analytics APIs are closed to individual accounts; and **never export
`ANTHROPIC_API_KEY`**, because it silently converts a session from subscription to metered
billing.

The other five are `The Round That Refuted Itself`, `R9_Cross_Session_Readout.md`,
`The Unbuilt Register`, `RECONCILIATION_AND_DISPATCH_2026-08-14.md` and
`RESEARCH_BRIEFS_REALISTIC_ENV_2026-08-14.md`.

---

## 7. WHAT IS STILL NOT DONE

Stated plainly so the next reader does not have to infer it.

1. **115 of 135 deep-research claims and roughly 350 of 399 R10 findings remain unrouted.**
   This session read the 20 adjudicated claims in full, the 14 read-directly findings that
   propagated nowhere, and the 34 asserting a contradiction. The filter is in
   `docs/R10_JOURNAL_AUDIT_2026-08-20.md` section 8.
2. **No external PDF was read from its own text in this session.** Everything in sections 1
   and 2 is a live connector read of a search record, or a read of another session's
   document. The 15 percent scrape error rate the acquisition slot measured applies to
   anything sourced from a scraped PDF, including claims quoted here at second hand.
3. **The five wall and floor boundary papers the acquisition slot identified as most on-target
   were not obtained.** Three are genuinely paywalled; two are recorded as open access and are
   not retrievable by any route available here. `10.3390/jmse9040416` is gold open access in a
   fully open journal and a browser will very likely fetch it where a plain client cannot.
   **That is the single highest-value human minute available.**
4. **Register rows were not written.** Sections 3.1 to 3.4 belong on `claude/r8-register`, not
   on the integration branch, because writing register rows to `add-ci-checks` is what widened
   the only merge conflict still growing.
5. **The recent work listed in `R10_WEB_ACQUISITION` section 3.9 is unread**, including seven
   2024-onward locking and boundary papers with DOIs and a fording paper by the same group as
   the Chrono work that appears in no deep search and no bibliography.
