# The four-rung ladder at the Yaris operating point

Produced 2026-07-25 22:5x CDT, Stage 1 of SHIP-v3.
Generator: `analysis/four_rung_ladder.py`, read-only against the rollouts, edits nothing.
Data: `data/four_rung_ladder.csv`, 6 rows (3 classes x 2 rollout sets).
Interpreter: `/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python`, 3.12.13.

Every number below is MEASURED, read out of `renders/yaris_render_s1/*/rollout.npz` this
session, unless the line says otherwise.

---

## 0. THE FINDING

**FROZEN 2026-07-25 23:2x.** The "2 of 3 classes" framing is withdrawn: the class labels
are not defensible at one fixed geometry (section 7), so the finding is restated on mass,
which verifiably varies. Superseded wording is in
`.claude/handoffs/2026-07-25_CORRECTIONS.md` C5 and C16.

> At one fixed geometry (extent 1.746 x 4.283 x 1.518 m) and one operating point
> (d = 0.29443 m, v = 1.5 m/s), varying only vehicle mass across 1100 / 1609 / 2337 kg:
> **all four rungs return NO-FORD at 1100 kg.** Above the AR&R mass boundary of
> **1250 kg**, L1a alone flips to FORD while L0, L1b and L2 hold NO-FORD. D x V is
> **bit-identical at 0.441644 m2/s** across all three runs, because the criterion contains
> no mass term; mass enters only as a threshold lookup. Over that same mass range the
> coupled simulation resolves a **4.86x spread in final displacement**, 0.658537 m to
> 0.135559 m.
>
> **Independence caveat, in the caption and not a footnote:** L0, L1a and L1b are all
> functions of (depth, velocity) alone. Their agreement is not three independent
> confirmations. The defensible claim is that three published criteria built on the same
> two variables agree with each other on the verdict, the coupled simulation agrees on the
> verdict, and the simulation alone resolves a 4.86x sensitivity to a variable the other
> three cannot represent at all.

Every clause checked against `renders/yaris_render_s1/gates_results_both_scenarios.json`:

| clause | check |
|---|---|
| all four NO-FORD at 1100 kg | `rungs_no_ford` = 4 |
| L1a alone flips above the boundary | `rungs_no_ford` = 3 at 1609 and 2337 kg; the single FORD is L1a in both |
| **mass boundary is 1250 kg** | **read at source: `vehicle_params.py:169` `kerb_weight_kg_max: 1250`, `:174` `kerb_weight_kg_min: 1250`** |
| D x V bit-identical | all three share `grid_lim = 9.421742313727737`, so `dxv_nominal` = 0.441644 exactly, one distinct value |
| 4.86x spread | 0.6585370302200317 / 0.13555917143821716 = 4.858 |
| mass enters L1a only as a lookup | `vehicle_params.py:186-199`, no mass term in the rule body |

**Preconditions that must travel with the finding:** the
`standing_water_sustained_inflow` scenario, the nominal still-water depth convention, and
`vehicle_params.L1_verdict` (the full AR&R rule) as the L1 implementation. Sections 4 and
5 give what changes otherwise.

**A further qualifier read at source this session, `vehicle_params.py:160-163`:** the AR&R
values are that report's own "Proposed DRAFT Stability Criteria for **Stationary**
Vehicles", described there as DRAFT INTERIM figures and explicitly "not an endorsed safety
standard". Captions must say "interim" and should not imply the criteria were derived for
a moving vehicle.

---

## 1. The operating point, measured

| quantity | value | provenance |
|---|---|---|
| grid | `n_grid = 64`, `h = 0.073607362806797` m | npz scalar |
| domain half-width | `lim = 9.42174243927002` m (Set B) | npz scalar |
| requested depth | 0.30000001192092896 m | npz scalar `depth` |
| **nominal still-water depth** | **0.2944294512271881 m = 4h** | derived, 4 water layers |
| velocity | 1.5 m/s | npz scalar `velocity` |
| D x V (nominal) | 0.441644 m2/s | derived |
| total head h_E | 0.409108 m | derived, see rung L1b |
| vehicle extent | [1.746378, 4.282610, 1.518008] m | npz `extent`, identical all 3 runs |
| vehicle particles | 8905 | npz |

The depth is quantized by the grid. The scene requests 0.30 m and gets 4 water layers of
thickness `h`, which is 0.29443 m, 1.9 percent under the request. This is why 0.29443
rather than 0.30 is the physically realized still-water depth, and it matters: 0.29443 sits
just **under** the AR&R small-passenger limiting depth of 0.30 m, while 0.30 sits just
over it. The verdict at that rung is decided by a 5.7 mm margin created by grid
quantization, not by physics.

---

## 2. Rung L0, resolved

**L0 is the NWS Turn Around Don't Drown single global 0.15 m depth rule. It is not AR&R.**
Resolved by grep and by reading the source, not inferred:

- `scripts/thresholds.py:1` : `L0_DEPTH_THRESHOLD = 0.15`
- `simulation/can_it_ford_L0.py:3` : `DEPTH_THRESHOLD_M = 0.15`
- `simulation/can_it_ford_L0.py:17` : prints `source=NWS_TADD`
- `hf_space/app.py:37` : "NWS Turn Around Don't Drown"

Verdict at 0.29443 m: **NO-FORD on every row**, since 0.29443 >= 0.15 for all classes.
This is the first row of the SHIP-v3 1.1 adjudication table and it is consistent with the
2B finding. No inversion. Caption source name must read **NWS TADD**, never AR&R.

### Defect found at this rung

The L0 boundary is implemented inconsistently across three call sites:

| file | test | verdict at exactly d = 0.15 |
|---|---|---|
| `simulation/can_it_ford_L0.py:6` | `depth_m < 0.15` gives FORD | NO-FORD |
| `scripts/gen_scenario_sweep.py:24` | `d <= 0.15` gives FORD | FORD |
| `analysis/make_phase_space.py:10` | `d > 0.15` gives NO-FORD | FORD |

0.15 m is an actual grid depth in `data/scenario_sweep.csv`, so this is not hypothetical.
It does not touch the 0.29443 m operating point and does not change anything in this
document. It should be reconciled before the sweep figure is captioned.

---

## 3. The ladder, Set B (`g64_m*`), nominal depth convention

Operating point: d = 0.29443 m, v = 1.5 m/s, D x V = 0.441644 m2/s, h_E = 0.409108 m.

| rung | criterion | source | small passenger (1100 kg) | large passenger (1609 kg) | large 4WD (2337 kg) |
|---|---|---|---|---|---|
| **L0** | depth >= 0.15 m | NWS TADD | NO-FORD | NO-FORD | NO-FORD |
| **L1a** | D x V vs per-class limit (0.30 / 0.45 / 0.60) | Shand et al. 2011, ARR Book 6, **interim** criteria | NO-FORD | **FORD** | **FORD** |
| **L1b** | total head h_E > 0.30 m | Kramer, Terheiden & Wieprecht 2016 | NO-FORD | NO-FORD | NO-FORD |
| **L2** | coupled MPM, drift > 0.05 m | this work | NO-FORD (frame 3) | NO-FORD (frame 3) | NO-FORD (frame 4) |

**Three of four rungs agree on NO-FORD across all three classes. L1a is the lone
outlier, and it clears the crossing for 2 of 3 classes.**

L2 supporting measurements:

| class | final \|d\| (m) | peak \|d\| (m) | peak \|yaw\| (deg) | onset frame |
|---|---|---|---|---|
| small passenger | 0.637019 | 0.644138 | 2.1108 | 3 |
| large passenger | 0.296321 | 0.303972 | 2.4113 | 3 |
| large 4WD | 0.123300 | 0.129882 | 0.3025 | 4 |

"SLIDE within 4 frames" is confirmed: onset at frames 3, 3 and 4 against
`DRIFT_THRESHOLD = 0.05` m. `renders/yaris_render_s1/failure_modes_by_run.json`
(generated 2026-08-05, keyed by run id, covers all 17 gated runs via
`simulation/failure_modes.py, classify_timeseries()`) independently
classifies all three as `FailureMode.SLIDE`, consistent with 16 of 17 runs
overall (the exception is `sweepV_g64_v0p5`, classified STUCK). Replaces
`failure_modes_result.json`, which carried no run identifier and was
written by no script in the repo.

### Rung L1b, arithmetic and its one soft spot

```
h_E = h + v^2 / (2 g) = 0.2944295 + 2.25 / 19.62 = 0.4091084 m
0.4091084 > 0.30  ->  NOT TRAFFICABLE, all three classes
```

The Kramer **values** are SOURCE-verified (section 6). The **formula** `h_E = h + v^2/2g`
is the standard hydraulic total head and is HYPOTHESIS-grade here: the abstract states the
criterion but does not print the defining equation, and the full text was not read this
session.

This matters more than the comfortable 36 percent margin suggests. The still-water term
alone is 0.29443, which is *below* the 0.30 limit. The entire L1b verdict is produced by
the velocity-head term. Any positive coefficient on `v^2/2g` above about 0.05 flips the
verdict to NOT TRAFFICABLE, so the result is robust to the coefficient, but it is **not**
robust to omitting the velocity head. Read the Kramer full text before L1b carries weight
in the paper.

---

## 4. Set A against Set B: the existing gate artifact describes the wrong run

There are two complete rollout sets in `renders/yaris_render_s1/`, and **they disagree on
the L2 verdict.**

| | Set A (`m1100`, `m1609`, `m2337`) | Set B (`g64_m1100`, ...) |
|---|---|---|
| written | 2026-07-25 19:17 | 2026-07-25 20:17 |
| size | 30 MB | 62 MB |
| water particles | 23 532 | 48 367 |
| `lim` | 9.42161750793457 | 9.42174243927002 |
| final \|d\|, 1100 / 1609 / 2337 kg | 0.0924 / 0.0510 / 0.0387 m | 0.6370 / 0.2963 / 0.1233 m |
| drift onset frame | 28 / 87 / never | 3 / 3 / 4 |
| **L2 verdict** | NO-FORD / NO-FORD / **FORD** | NO-FORD / NO-FORD / NO-FORD |

Displacements differ by a factor of 3 to 7 between the two sets at identical mass, and the
large 4WD case **changes verdict**.

**Consequence: `renders/yaris_render_s1/gates_results.json` is stale.** Its
`final_disp_mag_m` values are 0.09239930659532547, 0.05109738931059837 and
0.03890065848827362, which match Set A exactly. It records
`"large_4wd": {"L2": "FORD", "agreement": "AGREE"}`. Under Set B, the run SHIP-v3 names as
the render source, that row is NO-FORD and the ladder result is the one in section 3.
`gates_results.json` must be regenerated against Set B before it is attached to anything.

SHIP-v3 section 6 G4 quotes `lim=9.421742`, which is Set B, confirming Set B is the
intended current run. That is the basis for treating Set A as superseded here. **What
changed between the two runs, and why the water particle count roughly doubled, is not
recorded anywhere I could find and is UNRESOLVED.** Until it is explained, the factor-of-7
displacement change is an unexplained result, not a settled one.

---

## 5. The headline is convention-dependent, and this bounds the claim

L1a takes a depth. Three defensible depths exist, and they do not give the same answer.

| depth convention | value (m) | D x V | small pass. | large pass. | large 4WD | classes diverging from L2 |
|---|---|---|---|---|---|---|
| requested | 0.300000012 | 0.450000 | NO-FORD | FORD | FORD | 2 of 3 |
| **nominal still-water, 4h** | **0.294429** | **0.441644** | NO-FORD | FORD | FORD | **2 of 3** |
| local peak under footprint | 0.375 / 0.383 / 0.299 | 0.563 / 0.574 / 0.448 | NO-FORD | NO-FORD | FORD | 1 of 3 |

So the "L1 diverges on 2 of 3" headline holds under the requested and nominal conventions
and **collapses to 1 of 3** under the measured local-depth convention. State the
convention in the caption.

Two further findings from this table:

1. **Under the local-depth convention the D x V product almost never binds.** The binding
   constraint for small passenger becomes the AR&R **depth cap** (0.375 > 0.30), not the
   product. This is worth saying plainly, because it sharpens the argument: AR&R already
   carries a separate limiting still-water depth precisely because the product alone is
   insufficient, and at this operating point that depth cap is what does the work. The
   repo's own `L1_honest` column in `gates_results.json` shows the same mechanism.

2. **The `requested` convention trips the depth cap on a floating-point artifact.** The
   stored requested depth is 0.30000001192092896, which exceeds the 0.30 m cap by
   1.2e-8 m. Any L1 evaluation using the requested depth returns NO-FORD for small
   passenger via the depth cap rather than via the product. Do not use the requested
   depth for L1.

### Two different L1 implementations exist in this repo

- `simulation/can_it_ford_L1.py:3` : per-class D x V limits only, **no depth cap, no
  velocity cap**.
- `vehicle_params.py:186` `L1_verdict` : full AR&R rule, depth cap **and** velocity cap
  **and** product, per class.

At this operating point under the nominal convention they happen to agree, because
0.29443 clears every class depth cap. They diverge generally, for example at d = 0.35,
v = 0.8: the product is 0.28 which clears the small-passenger 0.30 limit, but 0.35 exceeds
the 0.30 depth cap, so the full rule returns NO-FORD and the product-only rule returns
FORD. SHIP-v3's instruction "L1 is already per-class, do not fix it" is correct for
`can_it_ford_L1.py` being per-class, but that file is **not** the full AR&R rule. Any
sentence written for Kumar must name which implementation produced the number.

---

## 6. Citation status for this document

| citation | status | evidence |
|---|---|---|
| Kramer, M., Terheiden, K. & Wieprecht, S. (2016), "Safety criteria for the trafficability of inundated roads in urban floodings", *Int. J. Disaster Risk Reduction*, DOI 10.1016/j.ijdrr.2016.04.003 | **SOURCE, verified** | Abstract retrieved this session via scite and the UNSW open-access record. Verbatim: "Based on both experiments, a constant total head is proposed as decisive parameter for determining trafficability." and "The recommended safety criteria for passenger cars and emergency vehicles are total heads of hE=0.3 m=const. and hE=0.6 m=const., respectively." |
| Kramer et al. proposes a Froude threshold near 0.5 | **REFUTED** | No Froude criterion appears in the abstract. The SHIP-v2 G5 gate built on it was correctly retracted. |
| Lazzarin, Viero, Molinari, Ballio & Defina (2022), *J. Hydrology* 607:127485, DOI 10.1016/j.jhydrol.2022.127485 | **title and DOI verified; the quote is UNRESOLVED** | DOI resolves via scite to "Flood damage functions based on a single physics- and data-based impact parameter that jointly accounts for water depth and velocity". The specific wording "does not represent any physically relevant principle" was **not** retrieved: ScienceDirect returned HTTP 403. |
| L0 source is NWS TADD, not AR&R | **SOURCE, verified** | Four call sites read this session, section 2. |

**Do not put the Lazzarin quotation in a caption or in anything sent to Kumar.** The paper
is real and its title is directionally consistent with the argument, but the sentence
attributed to it has not been read at source. Either obtain the full text through the
library proxy or make the point using AR&R's own separate depth cap, which is verified
here in section 5 and is sufficient on its own.

---

## 7. What this document does not establish

- It does not validate Set B. Section 4 records an unexplained factor-of-7 displacement
  change between two runs at identical mass, and that is not resolved.
- Realized density is **310, 453 and 658 kg/m3** for the three masses, against the
  100 to 300 kg/m3 band this project uses as its plausibility anchor (`CLAUDE.md:14-15`,
  and applied throughout `paper_draft.md` and `analysis/gp_surrogate_results.md`).
  **All three exceed the band**, the heaviest by a factor of 2.2. Every run here is denser
  than a plausible car. Whether that band originates in the engine's own `FloodScene`
  docstring is a separate question and remains ungrepped at source.
- The three runs share **identical geometry**: `extent` is
  [1.746378, 4.282610, 1.518008] m in all six rollouts. Only `--vehicle-mass` varies.
  `docs/GAP_MANIFEST_2026-07-25.md` gap 13 and `docs/mass_sensitivity_table.md` already
  record this independently. **This is a mass sensitivity study, not a class comparison**,
  and per `docs/mass_sensitivity_table.md` the word "class" may not appear unqualified for
  these rows until V2 real meshes exist. The class column in
  `data/four_rung_ladder.csv` names which AR&R *limit set* was applied, nothing more.

  Measured against the three AR&R axes, the single Yaris hull is 4.2826 m long with
  measured ground clearance **0.158 to 0.174 m** (five independent sampling bands,
  `.claude/handoffs/2026-07-25_vista.md:158-162`; the coarse `v1l` FE deck probably
  overestimates true clearance, so the error runs toward the bound). It therefore fails
  `small_passenger` on clearance (needs <= 0.12 m), fails `large_4wd` on both length
  (needs >= 4.5 m) and clearance (needs >= 0.22 m), and satisfies only `large_passenger`.
  Write "4WD-scale mass", never "a 4WD".

  **Correction to SHIP-v3:** the directive's Stage 8 quotes ground clearance as 0.182 m.
  The project's own measurement is 0.158 to 0.174 m. Use the measured range.
- L2 remains a single-resolution result. No grid convergence study exists yet; all six
  rollouts are `n_grid = 64`.
