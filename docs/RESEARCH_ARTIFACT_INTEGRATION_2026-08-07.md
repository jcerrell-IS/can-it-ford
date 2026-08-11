# Research artifact integration, 2026-08-07

Thirty research reports were attached to this session as files in `~/Downloads`
(29 relevant, plus one unrelated Austin nightlife report). This document is the
cumulative record of what each one actually says, what was done about it, and
what is still open. It exists because an earlier answer in this session claimed
"3 of 26 acted on," and that accounting was itself wrong in both directions.

**This file is NOT canonical.** `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`
remains the sole authority for any claim it covers. Where a finding below is
strong enough to be canonical it has been written INTO the register, and this
file records only that it was. Where it has not, it is a lead, not a fact.

## Provenance tiers used below

| Tier | Meaning |
|---|---|
| **T1** | Verified live this session against a primary source in this repo or the pinned vendored solver core. Safe to cite. |
| **T2** | External research report claim, internally consistent and specific, NOT independently checked against the primary publication. Cite the report, not the underlying paper, until someone reads the paper. |
| **T3** | Report claim that CONFLICTS with another report, or that rests on a source the report itself could not access. Do not cite at all without resolving it first. |

A research report is one source. Two reports agreeing is two sources. A report
agreeing with a prior session's summary is one source counted twice.

---

## 1. Correction to this session's own earlier accounting

The earlier claim that only 3 of 26 reports had been acted on was wrong. Checked
live against the register:

- **Already integrated, contrary to that claim:** `c92f9ad4` and `67209420` are
  present as register **G11**, **G12** and **G13** (prior art for the
  simplest-sufficient-abstraction principle, the digital-twin decision pipeline,
  and arXiv 2607.00673). `baa355db` is present as **G1** and **G2**. `8f2c67a9`
  is present as **G6**, **G7** and **G8**. Those reports were used.
- **Genuinely not acted on:** the items in section 3 marked NEW or AMENDS.
- **Partly acted on:** `65474f37`, whose finding closes a gap register **G4**
  explicitly flags as open.

The reason the earlier accounting was wrong is that it was assembled from a
compacted conversation summary rather than from the register. That is the exact
failure mode CLAUDE.md's verification rule exists to prevent.

---

## 2. Conflicts between reports, resolve before citing either side

### 2.1 CCSA / NCAC vehicle mesh redistribution rights, UNRESOLVED, T3

Two reports reach opposite conclusions on whether a derived NCAC/CCSA vehicle
mesh may be redistributed:

- **`b0d2664f`** says redistribution is fine: NHTSA's Terms of Use states site
  content "is considered public information and may be distributed or copied,"
  grounded in 17 U.S.C. 105, and the DOT National Transportation Library states
  there are no copyright restrictions on DOT publications.
- **`289743f7`** says do NOT redistribute absent written permission: the models
  are **contractor works** (GWU and GMU under FHWA/NHTSA), so they are *not*
  automatically public-domain U.S. Government works under 17 U.S.C. 105, which
  covers works authored by government employees. It further reports that DOI
  10.13021/G8JS5D carries an **empty rights field** and points to a validation
  slide deck rather than a CC0 waiver, and that the CCSA GMU site carries no
  model licence at all.

**Adopted position: the conservative one (`289743f7`).** 17 U.S.C. 105 turns on
authorship by a government employee, and a contractor is not one, so
`b0d2664f`'s inference from the NHTSA Terms of Use to the GMU-hosted models does
not follow. This is a reasoning gap in `b0d2664f`, not a disagreement about
facts, which is why the conservative side wins rather than the question staying
50/50.

**Consequence, and it is live:** register **J10** (DesignSafe DOI pending Kumar
sign-off) must not proceed to publish any derived NCAC/CCSA geometry, and no
such mesh should be committed to the public GitHub repo, until someone obtains
written permission or confirms a licence. Recorded as register **E7**.

### 2.2 mu = 0.30, refuted or standard? Both, and the distinction matters

Register **G4** says `mu_wet ≈ 0.30` is REFUTED as a wet-road value. Report
`65474f37` says 0.30 is the dominant convention across the flood-vehicle
stability literature. These read as contradictory and are not:

- 0.30 is **refuted as a measurement** of wet road friction. Smith, Modra and
  Felder 2019 measure wet and dry concrete at about 0.78; 0.30 is their sand and
  gravel worst case.
- 0.30 is **real as an adopted convention**. Shand et al. 2011 record that
  "correspondence with various road experts and test laboratories" settled on
  mu = 0.3, and Bonham & Hattersley 1967 and Gordon & Stone 1973 both use it.

Both statements are true. The trap is that someone reading `65474f37` alone will
conclude G4 is wrong and resurrect 0.30 as best-sourced. Recorded as an amendment
to **G4** so the register carries both halves.

---

## 3. Per-report disposition

Ordered by consequence, not by ID.

### 3.1 Findings that changed the register this session

| ID | Report | Finding | Action |
|---|---|---|---|
| `266e9a8a` | Xia 2011 vs Shu 2011 incipient velocity | Claims **verified primary-source transcription of both**, from author-accepted manuscripts on academia.edu, with Shu matched against the typeset *J. Hydraulic Research* version of record. Gives both final formulas, all force terms, both fitted coefficient tables, flume geometry and scales. | **AMENDS G10, downgrades J6.** G10 said "NOT RETRIEVABLE." Section 4.1 records the equations. Retrieval is now T2, not closed. |
| `65474f37` | mu = 0.55 provenance audit | Azhar, Pauwels & Bui 2023 (DOI 10.1111/jfr3.12885, open access) **measured 0.55 themselves** with a spring balance on their rubber-mat road proxy, citing Wong *Theory of Ground Vehicles* only to show it sits in a 0.50 to 0.70 handbook range for wet asphalt. Clean two-hop chain, not inherited from a flood paper. | **AMENDS G4**, which said this attribution "has never been confirmed." Also fixed three refuted claims in the skill file, section 4.2. |
| `b0d2664f` | Vehicle geometry and deliverable triage | The three masses map to real CCSA models: 1100 kg = 2010 Toyota Yaris, **1609 kg = 2020 Nissan Rogue**, **2337 kg = 2018 Dodge Ram 1500** (2270P), with download URLs and element counts. | **AMENDS E6**, which said 1609 and 2337 kg are unsourced. |
| `289743f7` | GNN surrogates and mesh provenance | Mesh redistribution rights are NOT established, see 2.1. Separately: a GNN surrogate for fluid-rigid coupling is **not demonstrated in Kumar's own published work**; GNS is validated on granular self-interaction and on flow past *fixed* obstacles, never a freely moving rigid body. GNS code itself is MIT. | **NEW E7.** Also kills any plan that assumes a GNS speedup transfers to this problem. |
| `045982be` | Safe crossing speed | **Negative finding.** No literature outputs `v_max(depth, flow_velocity)`. The closest is Pregnolato et al. 2017, `v = 0.0009w^2 - 0.5529w + 86.9448`, which is depth-only, control-focused, not stability. | **NEW G14.** |
| `c963203d` | Buoyancy-reduced traction and propulsion | **Negative finding.** No coupled flood simulation applies propulsive force or engine torque; passive rigid body under drag is universal practice, Azhar 2023 included. The `F = mu(W - B - L)` physics is established and directly measured (Smith et al. 2019). Shah et al. 2018 is the closest, adding an engine driving force to a sliding balance. | **NEW G15.** This is a defensible novelty claim for the project. |
| `211aad60` | Particle resolution and force convergence | **No accepted force-convergence criterion exists** for SPH/MPM. Published resolutions span about 2 to 60 across a feature. Coarse resolution *usually* over-predicts peak force, but with documented exceptions, so it is a tendency, not a law. | **NEW G16**, and tightens G8. |
| `5e706c91` | `friction` forensic audit | warpmpm's collider `friction` is a **Coulomb coefficient**, not numerical damping. **Verified live T1** this session, section 4.3. Task B of the report failed: it could not access `jcerrell-IS/can-it-ford` at all and reports zero findings there. | **NEW A7.** |
| `baa355db` | Experimental configuration of the literature | Full comparison table of what was physically done in every foundational study, including restraint method, flume dimensions, yaw, wheel state and per-study mu. Adds that **blockage ratio and afflux corrections are unreported in essentially every incipient-motion study**, and that model-scale watertight vehicles float too shallow. | **AMENDS G1** with the blockage gap, which is a real limitation of the thresholds this project validates against. |

### 3.2 Reports whose findings were already in the register

No action needed; recorded here so nobody re-derives them.

| ID | Already present as |
|---|---|
| `c92f9ad4` | G11 |
| `67209420` | G12, G13 |
| `8f2c67a9` | G6, G7, G8 |
| `baa355db` | G1, G2 (plus the amendment above) |
| `d0ce5e82` | A3, and section C of the register (Genesis-only) |

### 3.3 Engine and pipeline reports, T2, no register change

These are consistent with existing register entries and with the standing
"do not switch engines" decision. They are recorded as leads.

| ID | Finding | Why no register change |
|---|---|---|
| `b2d7fede` | Genesis has **no** inlet/outlet/periodic boundary; both MPM and SPH use one closed reflecting `CubeBoundary`. A uniform initial velocity decays and recirculates. | Consistent with the existing in/outflow plan. Genesis is not the 17-run path, so this constrains Track 2 only. |
| `e7616dc5` | Genesis p2g writes a grid index with **no in-kernel bounds check**; domain padding is `3 * dx`. The rigid-body-near-boundary trigger is a hypothesis, not a confirmed issue. | Matches register C section. The `3 * dx` figure was already ruled out as the crash cause by direct test. |
| `a1fd6fdc`, `d50d614c` | Engine comparison sweeps. | Both conclude do not switch. Already the standing decision (L-8, aarch64 blocker). |
| `0c02e2cf` | `FloodScene` already emits 6-DOF (`t, dx, dy, dz, dmag, yaw_deg, pitch_deg, roll_deg`); **no** failure-mode classification and **no** threshold-violation magnitude exist in it. | Our own `failure_modes.py` covers classification, register D6. Useful if FloodScene is ever adopted. |
| `e31ed559` | The 23-point CSV phase-space dataset used a near-weightless frictionless box; the "friction-invariant drift" result is a symptom of that, not physics. | Consistent with the box-proxy deprecation already recorded. Do not resurrect that dataset. |

### 3.4 Mesh, splat and PLY pipeline reports, T2, no register change

| ID | Finding |
|---|---|
| `3a3af269`, `72adbe17` | Genesis `watertighten_mesh` **cannot** take a raw point cloud: it needs verts AND faces. It is an unsigned-distance-field, blur, dual-contouring shrink-wrap **outside** an existing triangle soup, not a Poisson reconstruction and not an interior fill. So an external surface-reconstruction step (screened Poisson recommended) is still required first. Once a mesh exists, Genesis's internal CoACD makes an external CoACD/V-HACD step redundant. |
| `82c51733` | `load_vehicle()` delegates to `load_gaussians_ply()`, standard INRIA 3DGS layout. SH degree is **inferred** from the `f_rest_*` field count, `degree_file = isqrt(n_rest_file // 3 + 1) - 1`, not hardcoded. No reference anywhere in the repo to InstantSplat, DUSt3R, COLMAP, nerfstudio or gsplat. |
| `86c0a734` | InstantSplat is a **sparse-view** method (validated 3 to 12 images, default 3) and is architecturally wrong for a dense 267-frame capture; its scene graph is O(N^2). Its PLY is schema-compatible with `load_gaussians_ply`, so only metric scale is missing. Expect failures on the metal railing: reflective and thin structures break both DUSt3R geometry and 3DGS appearance. |
| `63a4b5d4` | The "1 shell + 1 solid" element count from `lsdyna-mesh-reader` is **almost certainly an artifact**: the library reports the number of element *sections*, not elements, and recognises only four keywords. Verify with `len(deck.element_shell_sections[0].eid)` and by grepping the deck for `*INCLUDE`. |

Together these say the splat-to-collider path needs an external meshing step and
a metric scale step, which is what register F3 already says, so nothing here
changes the plan; it sharpens the tool choice.

### 3.5 Workflow and tooling reports, no repo science

`2c1e05ae`, `35a13e3e`, `62a7f8e6`, `7b8dbc33`, `7c6c2670`. These concern Claude
configuration, tool stacks and prompting. No factual claim about the simulation,
the literature or the repo. Not integrated, deliberately. One item worth
surfacing: `7b8dbc33` concludes that **no drop-in library exists** for the
gsplat-to-MPM bridge and that adapting PhysGaussian's particle-fill logic is the
right move, budgeted as core contribution rather than a tooling search. That
agrees with the register's addendum on the bridge.

`c62889de` is an Austin nightlife guide and is unrelated to this project.

---

## 4. What was actually changed

### 4.1 Xia 2011 and Shu 2011, equations now on record

Both are **sliding-only** formulations. Neither derives a toppling equation, and
neither publishes numeric CD, CL or mu inside the working formula: those are
folded into two lumped flume-calibrated parameters. Both are flat-bed.

**Xia, Teo, Lin & Falconer 2011**, *Natural Hazards* 58(1):1-14,
DOI 10.1007/s11069-010-9639-x. Fully submerged / water-filled focus, carries an
explicit lift term. Balance `FD = FR`, Eq. 5. Final form, Eq. 9:

> `Uc = a * (h/hc)^b * sqrt( 2g * ((rho_c - rho_f)/rho_f) * hc )`

Fitted (Table 3), partially submerged then fully submerged `a`, `b`:
Pajero 1.492, -0.731, 0.737, 0.532. BMW M5 1.116, -0.558, 0.816, 0.264.
Mini Cooper 1.225, -0.708, 0.932, 0.121. Sign convention: `b > 0` fully
submerged, `b < 0` partially submerged. Models 1:43 and 1:18, flume 10 m by
0.30 m, rough bakelite bed, rear facing flow.

**Shu, Xia, Falconer & Lin 2011**, *J. Hydraulic Research* 49(6):709-717,
DOI 10.1080/00221686.2011.616318. Partially submerged refinement; the interior
is assumed **watertight**, so the vehicle floats above a critical depth `hk`.
Balance `FD = FR`, Eq. 8. Final form, Eq. 12:

> `Uc = alpha * (hf/hc)^beta * sqrt( 2g*lc * ((rho_c/rho_f)*(hc/hf) - Rf) )`

Fitted: Ford Focus alpha 0.500 beta -0.178; Ford Transit 0.227, -0.764;
Volvo XC90 0.394, -0.630. Single scale 1:18, flume 15 m by 1.2 m by 1.0 m,
plastic-carpet bed. Measured friction on wet carpet: Transit 0.39, Focus 0.50,
XC90 0.68.

**Status: T2, and J6 stays open.** These are author-accepted manuscripts, and
only Shu was cross-checked against the version of record. Before any of this
enters the paper, pull the publisher PDFs through the UT Austin proxy and
confirm equation numbers and coefficients directly. The reason to keep J6 open
is not doubt about the report, it is that the paper must cite the published
paper, not a transcription of a preprint.

### 4.2 Skill file corrected in place

`vehicle_geometry_research/flood-mpm-debugging-reference_SKILL_v3_friction_corrected.md`
carried **three** claims that register Section I says must be corrected on sight.
All three fixed:

1. Line 58, "mu_wet ≈ 0.3 is the primary, best-sourced value." Refuted by G4.
   Replaced with the measurement/convention distinction from 2.2, plus the now
   confirmed Azhar provenance and Shu's measured 0.39 / 0.50 / 0.68.
2. Line 97, "`coup_friction` in Genesis is a numerical stability impulse
   coefficient, not Coulomb friction." Refuted by CLAUDE.md, confirmed
   2026-08-05 at `legacy_coupler.py:322`. Replaced, and extended so the same
   error cannot be made about warpmpm, which is a different parameter in a
   different engine.
3. Line 62, DRIFT_THRESHOLD "grounded conceptually in Xia et al. 2014 and Shah
   et al. 2018" and "independently derived three separate times, all three
   agree." Refuted by D7 and CLAUDE.md item 13: it has no peer-reviewed source,
   and repeated agreement inside this project is one source counted repeatedly.
   The old line also advised treating a fourth check as "wasted effort," which
   inverts the project's verification rule. This one was surfaced by the
   `check_claims` PostToolUse hook, not by the artifacts.

### 4.3 warpmpm `friction` classification, verified T1

`5e706c91` classified it from live GitHub via DeepWiki. Confirmed here against
the pinned vendored core, which is the stronger source:
`third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_solver_warp.py:2729`,
in the branch commented `separable + Coulomb friction`:

```python
scale = wp.max(0.0, tlen + param.friction * vn) / tlen
v_tan = v_tan * scale
```

Textbook Coulomb. Note this is the **SDF collider** path. The same read shows
that path accumulates `param.force` and `param.torque` by `atomic_add` of the
grid impulse, which is consistent with register A3: a force accessor exists, but
only on kinematic colliders, and the 17 runs never create one.

Also worth recording about `5e706c91` itself: its **Task B failed completely**.
It could not access `jcerrell-IS/can-it-ford` by any method and reports zero
findings, positive or negative, for this repo. Do not read its Task A conclusions
as having been checked against our code. That check happened here, not there.

### 4.4 Two infrastructure defects found and fixed

Neither came from the artifacts; both were hit while doing the work.

1. **`.claude/settings.json:92` invoked the commit gate by relative path**
   (`python3 .claude/hooks/pretooluse_git_commit_gate.py`) while every other
   hook in the file uses `$CLAUDE_PROJECT_DIR`. The Bash tool keeps one
   persistent cwd per session, so a single call that left the repo made the hook
   die on a missing file and **wedged every subsequent Bash call for the rest of
   the session**. Fixed to use `$CLAUDE_PROJECT_DIR`.
2. **`pretooluse_git_commit_gate.py` had the same bug internally**, resolving
   `.claude/checks/params_check.py` relative to cwd. Fixed to resolve against
   the project root, and to fail loudly if the check script is missing rather
   than silently returning a nonzero from a not-found interpreter.

Also observed, not fixed: the `check_claims` C8 rule fires on text that quotes a
refuted claim **in order to retire it**. The hook's own message anticipates this
and says to leave such text as written, so this is a known false positive, same
class as the C13 false positives logged earlier today. Whoever owns the rule may
want a suppression marker.

---

## 5. Still open after this pass

1. **J6 stays open.** Pull the Xia and Shu publisher PDFs via the UT Austin
   proxy and confirm section 4.1 against them. Do not cite the transcription.
2. **E7 / J10 blocker.** Establish CCSA/NCAC mesh redistribution rights in
   writing before any DesignSafe DOI or public commit of derived geometry.
3. **The three-mass swap-in is now possible but not done.** `b0d2664f` gives
   working download URLs for the Rogue and Ram models. Register E3 already notes
   the meshes exist but never entered a simulation. Doing it is a real piece of
   work: LS-DYNA keyword decks of shell elements in millimetres, multi-million
   elements, not watertight, exterior needs extracting. Not attempted here.
4. **`v_max` and traction, G14 and G15, are negative findings.** They belong in
   the paper's related-work and novelty framing. Nobody has written that text.
5. **Blockage ratio.** `baa355db` reports it is unreported across the entire
   incipient-motion literature. Our tank has a computable blockage ratio. Nobody
   has computed it. That is a cheap, self-contained contribution.
