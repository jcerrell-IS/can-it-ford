# D4 PHYSICS GATE: Option B, the Kramer 2021 floating-sphere benchmark

2026-08-16. Branch `claude/r5-physics`, worktree `.claude/worktrees/r5-physics`.

Claim tags used throughout: **[read]** = read live from a primary source this session,
**[derived]** = computed here from tagged inputs, **[recalled]** = carried from project
memory or a register entry and not re-derived, **[unreviewed]** = not yet checked by the
physics-skeptic subagent.

---

## 1. Which gate, and why

**Option B.** The dispatch asked for one of the two gates, finished, with the choice
justified. Four reasons, in order of weight:

1. **Option B is falsifiable against something the solver has never seen.** CLAUDE.md
   item 6 records that no gate in this project is a physics validation: every gate is a
   self-consistency or numerical-containment check, and G-3 compares against `RHO_REF`
   derived from the same pipeline, so it cannot fail for a reason external to the code
   **[recalled]**. The at-rest buoyancy gate was separately shown to be tunable, since
   every resolution contains a band width that passes it **[recalled]**. An external
   benchmark with published uncertainty is the only thing on either option's table that
   breaks that circularity.
2. **The sphere is the one geometry where the project's biggest coupling blocker cannot
   bite.** `RigidBody6DOF` raises `NotImplementedError` on a non-zero COM offset,
   because the SDF collider rotates about its centre while `sdf_wrench` reports torque
   about that same centre **[recalled]**. Heave is pure translation with one degree of
   freedom, so the torque channel is never integrated. Option A's open-channel work
   inherits every one of the project's rigid-body caveats; Option B sidesteps the
   largest of them by construction.
3. **Option A's stated cause is a solver-architecture change, not a driver change.** The
   dispatch records that the BC was wired, validated 3/3 on closed-form cases, and then
   failed to hold a level under steady inflow equals outflow, with the cause identified
   as Anura3D imposing BCs at grid nodes against this project's particle-level
   implementation. Moving warpmpm's BC application to grid nodes is a change to a shared
   engine, on 629 Vista SUs, with a conference paper (Remmerswaal et al. 2019) that has
   to be read first. It is the larger and less certain of the two.
4. **A sphere has closed forms for everything.** Volume, waterplane area, hydrostatic
   stiffness, submerged-cap volume, and the signed distance field itself (`|x| - r`) are
   all exact. Every one of those became an assertion that runs on the Mac before a
   single GPU second is spent (section 5). No vehicle hull permits that.

Option A is not refuted and is not closed. It is deferred with its reason stated.

---

## 2. The benchmark, verified

Kramer, Andersen, Thomas, Bendixen, Bingham, Read, Holk, Ransley, Brown, Yu, Tran,
Davidson, Horvath, Janson, Nielsen and Eskilsson (2021), "Highly Accurate Experimental
Heave Decay Tests with a Floating Sphere: A Public Benchmark Dataset for Model
Validation of Fluid-Structure Interaction", *Energies* **14**(2):269,
doi:`10.3390/en14020269`.

- Title, journal, volume, issue, page and all sixteen authors **[read]**, resolved from
  the DOI via Unpaywall and cross-checked against the OSTI record.
- Open access: gold, CC-BY, `publishedVersion` **[read]**.
- **This is NOT Kramer, Terheiden and Wieprecht 2016** (watertightness,
  doi:`10.1016/J.IJDRR.2016.04.003`), which is already in the register at line 228 and in
  CLAUDE.md item A-4. Same first author, different paper, different subject. The dispatch
  warned about exactly this conflation and it is recorded here so a later reader does not
  merge them.

## 3. The test case, as read

All **[read]** from the article's own full text this session, not recalled:

| quantity | value |
|---|---|
| sphere diameter `D` | 300 mm |
| ballasting | to half submergence: waterline at the equator at rest |
| drop heights `H0` | {0.1D, 0.3D, 0.5D}, i.e. linear, moderately nonlinear, highly nonlinear |
| duration to capture | "around eight natural periods in heave" |
| basin | 13.00 x 8.44 m |
| still-water depth | 900 mm |
| expanded uncertainty | ~0.3% of the respective drop heights, 95% confidence |
| air phase | disregarded, in the paper's own test case |

At `H0 = 0.5D` the whole sphere starts above the water.

### 3.1 Table 1, now READ, and the three values it corrected

**Superseded 2026-08-16 by the article PDF**, delivered by the Round-5 coordinator to
`/Users/josie/can-it-ford-refs/2026-08-16/`, sha256 verified
`0d885109119d390ae30d42c620ddf0bd8bcad130396dcfe8053b67510d4e9354`, held deliberately
outside the repo because the repo is public and E8 is unresolved. Table 1, p.4,
"Values of the test case physical parameters" **[read]**:

| `D` | `m` | `CoG` | `g` | `H0` | `rho_w` | `d` |
|---|---|---|---|---|---|---|
| 300 mm | 7.056 kg | (0, 0, -34.8) mm | 9.82 m/s^2 | {30, 90, 150} mm | 998.2 kg/m^3 | 900 mm |

Also read: four repetitions per drop height, so the benchmark's own N is 4; and the
seabed depth `d = 3D`, which Table 1's 900 mm confirms exactly.

**The earlier version of this document derived the test case and three values were
wrong.** They are corrected here rather than quietly overwritten:

| quantity | I had | Table 1 | error |
|---|---|---|---|
| `rho_w` | 1000 kg/m^3 (assumed) | **998.2** | +0.18% |
| `m` | 7.0686 kg (derived) | **7.056** | +0.18%, inherited from `rho_w` |
| `g` | 9.81 (the engine's) | **9.82** | -0.102%, and irreducible: see 3.3 |
| buoyancy at equilibrium | 69.3428 N | **69.2180 N** | +0.180% |
| heave stiffness | 693.428 N/m | **692.180 N/m** | +0.180% |

The reasoning was sound and the input was not: `998.2 * V/2 = 7.05586 kg` reproduces
Table 1's 7.056 to its quoted precision, so half submergence really does fix the mass.
This is the cleanest example I have of why a derived value is not a read one **even when
the algebra is right**. Anything still quoting 69.34 N or 7.0686 kg is quoting the
superseded derivation.

`CoG = (0, 0, -34.8) mm` is new information, not a correction: the sphere is **ballasted**,
with its centre of gravity 34.8 mm below the geometric centre. In a 1-DOF heave
integration that is immaterial, which is a second and independent reason the sphere suits
this engine (section 1, reason 2).

### 3.2 The 0.3% is an absolute displacement tolerance, not a relative one

Verbatim from the abstract **[read]**: "At a 95% confidence level, uncertainties were
found to be very low - on average only about 0.3% of the respective drop heights."

Three qualifiers, all load-bearing, and all lost in the paraphrase carried by the Round-5
bootstrap and by `RECONCILE_ROUND4`:

1. it is an **average** over the decay series, not a per-sample bound;
2. it is at **95% confidence**;
3. it is a fraction of the **drop height**, which makes it an **absolute displacement**
   tolerance of **0.090 / 0.270 / 0.450 mm** for the three drops.

**It therefore cannot be applied to a period, a damping ratio or a force.** My pass
criterion has to be stated against displacement, in metres, per drop height. A "within
0.3%" claim about a natural period would be a category error, and I would have made it
had this not been corrected.

### 3.3 The gravity mismatch is irreducible, and I quantified what it costs

Table 1's local `g` is **9.82 m/s^2**. The solver hardcodes **9.81** inside
`Solver.set_material()` at `core/solver.py:167-169`, and `newtonian()` carries no `g` key
to override it **[recalled, and consistent with CLAUDE.md item 3]**. **This scene cannot
be run at the benchmark's gravity.** The bias is -0.102% in `g`.

Both the weight and the hydrostatic stiffness scale with `g`, so the equilibrium
submerged fraction is **exactly unaffected** (asserted, and it holds to 1e-15). Only the
period moves, as `T ~ 1/sqrt(g)`: **+0.051%, or +0.396 ms on a 0.777 s period**
**[derived]**. That is about two orders of magnitude below the benchmark's own 0.090 mm
displacement tolerance expressed as a timing error, so it is a stated systematic rather
than the limiting error. It must still travel with every period this scene reports.

Water density I *can* match, and now do: the material is built at `rho_w = 998.2`, a
deliberate departure from the project's canonical `RHO_W = 1000.0`. For a validation
against an external benchmark, matching the benchmark is the correct choice, and it is
flagged here so nobody reads it as drift.

### 3.4 What is still missing

The **benchmark time series itself** ships as MDPI Supplementary Materials at `/s1`.
Still 403, independently reproduced by the coordinator from a second host. The PDF is
the paper, not the data. Tracked in section 7.

---

## 4. Feasibility, and the one thing it settles for free

### 4.1 The resolution ceiling is not what blocks this, and this run discriminates it

The R7 mirror control found a reproducible, time-growing instability with the ceiling
between `n_grid` 100 and 104, which translates to dx **0.090594 to 0.094217 m**
**[recalled]**. That translation holds `lim = 9.421742313727737` fixed, the canonical
Yaris `grid_lim`. **Because the domain was held fixed, that control cannot distinguish a
grid-COUNT ceiling from an absolute-dx ceiling: the two are perfectly confounded in it.**
I have not seen this stated anywhere in the register or in CLAUDE.md **[unreviewed]**.

This scene breaks the confound by accident and then on purpose. At `lim = 1.2, n_grid =
64` the dx is 0.01875 m: **4.8x finer than the published dx ceiling, at a grid count 36
cells below the published count ceiling**. So:

- if the run is clean, the ceiling is grid-count-like and the published dx figure should
  never be quoted as an absolute resolution limit;
- if the run shows the same growing asymmetry, the ceiling is a length scale and D9's
  finest rungs are in worse trouble than currently recorded.

Either outcome is a result. R7's own caveat 3 already points the same way: D9's scene,
which is still water plus a kinematic SDF collider, does **not** show the instability at
the same dx in the same domain, and that is exactly this scene's configuration
**[recalled]**. That is a reason to expect the first outcome, not a substitute for
measuring it.

### 4.2 The domain, and the honest size of the comparison window

The 13.00 x 8.44 m basin cannot be resolved at the dx a 300 mm sphere needs, so the tank
is a square of side `lim`. The radiated wave is deep-water: 0.9425 m long at the
predicted period **[derived]**. Its energy therefore travels at the **group** velocity
`c_g = g T / 4 pi = 0.6065 m/s`, not at `sqrt(g h) = 2.215 m/s`. Using the shallow-water
speed here would understate the clean window by a factor of 3.6 and is the wrong wave
speed for a 0.94 m wave in 0.5 m of water.

| `lim` | wall distance | reflection returns | in natural periods |
|---|---|---|---|
| 1.2 m | 0.500 m | 1.649 s | 2.12 |
| 1.5 m | 0.650 m | 2.143 s | 2.76 |
| 2.0 m | 0.900 m | 2.968 s | 3.82 |

The paper asks for eight periods. **I can offer two to four before wall reflection
contaminates the signal.** That is a truncation of the comparison window, and it means
the comparable quantities are the first damped natural periods and the first-cycle decay,
not the full eight-period envelope. It is stated here rather than discovered later. The
paper's own Figure 13 finding, that the initial damped natural period increases with drop
height, falls inside a two-period window, so the truncation does not remove the headline
comparison.

Water depth is cut from the paper's 900 mm to 500 mm. At 500 mm, `kh = 3.333` and
`tanh(kh) = 0.99746`, so the dispersion relation is deep-water to **0.25%** **[derived]**.
That is a quantified approximation, not an assertion of equivalence.

### 4.3 The artificial sound speed is a real caveat at the largest drop

`c = sqrt(GAMMA * BULK / rho_w) = 12.8568 m/s` at Table 1's rho_w = 998.2 (12.8452 at the superseded 1000) **[derived from engine constants read at
`simulation/validate_coupling_force.py:15-23`]**, against ~1481 m/s for real water. On the
linear peak-velocity estimate:

| drop | `H0` | peak Mach |
|---|---|---|
| 0.1D | 0.030 m | 0.0189 |
| 0.3D | 0.090 m | 0.0567 |
| 0.5D | 0.150 m | **0.0944** |

The highly nonlinear case sits at the edge of the weak-compressibility assumption. Its
Mach number must travel with any number reported from it. CLAUDE.md already records that
artificial sound speed can qualitatively flip a rigid-body outcome (Isik and He 2022)
**[recalled]**.

---

## 5. What the no-GPU checks caught

`simulation/r5_physics/test_sphere_geometry.py` runs on the Mac against numpy alone and
currently reports ALL PASS. It found two real defects on its first run, both now fixed:

1. **A vacuous assertion.** The check "raises rather than returning an unusable margin"
   fed `dx = 0.05` at `res = 16`, which leaves 9 cells across the mesh. The function was
   correct to return; the assertion was simply wrong. It now asserts **both** directions,
   so a one-sided test cannot pass vacuously again.
2. **A planned configuration the scene's own constructor would have rejected.** At
   `lim = 2.0, n_grid = 96` the fixed floor and wall offsets of 0.060 / 0.080 m do not
   clear the required 3dx = 0.0625 and 4dx = 0.0833. The first version of the guard test
   hid this by hardcoding the coarsest dx as `1.5/80`, quietly excluding the one config
   that failed. The offsets are now 0.075 / 0.100 m, the planned configurations live in a
   single `PLANNED_CONFIGS` tuple in the module, and the test iterates that tuple so it
   cannot evaluate itself against a friendlier subset.

The second one is the same failure mode as the tunable at-rest gate, at a smaller scale:
a check that picks its own operating point will pass.

**A third, found once Table 1 was in hand.** Table 1 over-determines the sphere: `D`, `m`
and `rho_w` are three independent read values and half submergence is a stated property,
so any two predict the third. That became a check on my own transcription, which is the
step most likely to be wrong. It passes, and it also surfaced something real: **Table 1's
`m` is rounded to 7.056 kg where exact half submergence needs 7.05586 kg, so the published
sphere is 0.140 g heavy and does not float exactly at the equator.** The residual is
+1.373 mN, which against the 692.180 N/m stiffness is an equilibrium offset of
**1.98 micrometres** **[derived]**. That is a factor of 45 below the benchmark's own
0.090 mm tolerance at the smallest drop, so it is immaterial, but the first version of the
check simply asserted "buoyancy equals weight" with a 1e-3 N tolerance and **failed**. The
fix was to assert the physical consequence against the benchmark's own tolerance rather
than to loosen the number until it passed. Loosening would have been the easier move and
would have thrown away the finding.

The suite also now asserts that the superseded `rho_w = 1000` derivation is **measurably
wrong rather than a rounding**, so it cannot be quietly reintroduced, and that the
benchmark tolerance **scales** with drop height by exactly 5x from the smallest to the
largest, which is the property a flat "0.3%" paraphrase destroys.

Also asserted and passing: the UV sphere is closed and consistently oriented (every
directed edge used exactly once, every undirected edge shared by exactly two faces,
V-E+F = 2 at V=4514, E=13536, F=9024), outward-wound by signed volume, with a 0.1784%
polyhedral volume deficit; all vertices lie on the sphere to 2.8e-17 m; the submerged-cap
formula reproduces exactly half the sphere at `h = R` and **69.2180 N** of buoyancy; and the
SDF margin clears the engine's `band = dx` guard at every planned resolution.

---

## 6. The scene

`simulation/r5_physics/sphere_heave.py`. Square tank, still water, one sphere as an
**SDF collider**, which is the path validated to **7.3 to 7.7%** of analytic buoyancy.
That range is the SDF path's; it must never be merged with the 1.5 / 0.7-0.8% free-rigid
late-window fit, which measures the path being criticised **[recalled]**.

The collider is kinematic, so the driver integrates the body itself, one degree of
freedom, semi-implicit Euler:

```
reset_sdf_force  ->  step(dt, substeps)  ->  sdf_wrench(dt = dt*substeps)  ->  integrate  ->  set_sdf_pose
```

Four of the five documented silent traps are handled explicitly and the fifth is out of
scope by construction; they are enumerated in the module docstring. The added-mass ratio
of ~0.5 is comfortably inside the partitioned-coupling stability limit of ~1, which is
why an explicit scheme is defensible here **[derived, unreviewed]**.

Two modes: `--fixed` pins the sphere and measures the steady vertical reaction against
the analytic submerged-cap buoyancy, which is the sphere-scale analogue of the C1-SDF
check; the default free mode runs the decay.

Nothing in `sim_standing.py` was touched. Its sha256 stamps every published run.

---

## 7. Open, with the second approach already tried

**BLOCKER-B1 is now HALF CLOSED.** The paper is on disk; the time series is not.

**The half that closed, with the route recorded so nobody repeats the archaeology.**
Exactly one host serves the PDF:

```
https://backend.orbit.dtu.dk/ws/portalfiles/portal/238040494/KramerEtAl_SphereDecay_Energies2021.pdf
```

**My earlier note "DTU behind Cloudflare" was half wrong and is corrected here**: the DTU
Orbit *front end* returns 403, and the DTU Pure *backend* returns 200 with
`application/pdf`. Filing that as "DTU is blocked" would have been a false negative that
cost the next session the same hour. Probed live 2026-08-16, all failing: `mdpi.com`
article, `/pdf` and `/s1` all 403; `orbit.dtu.dk/files/...` 403; `vbn.aau.dk/files/...`
403 to curl although its record page reads fine; `hdl.handle.net/10026.1/16780` 404;
`research-hub.nrel.gov` DNS ENOTFOUND.

**The half still open.** The raw heave-decay series is MDPI Supplementary Materials at
`/s1`, 403 from two independent hosts. Section 1 of the paper states the dataset is in
the Supplementary Materials and points to Appendix A; the paper carries figures and
summary tables, not the series. So the scene can be run and self-checked, but the
**quantitative comparison** cannot close, which is half of the dispatch's definition of
done.

Per the coordinator, this is **a Josie action, not a stall**: fetch
`https://www.mdpi.com/article/10.3390/en14020269/s1` from a normal browser session and
drop the archive beside the PDF in `can-it-ford-refs/`, outside the repo. Failing that,
the corresponding author is `mmk@build.aau.dk` **[read from the PDF title page]**. I will
mine the PDF's own figures and appendices for comparable summary quantities in the
meantime, and will say plainly if the series exists only in `/s1`.

**Unrelated correction, for the coordinator.** `PROVENANCE.txt` beside the PDF lists the
authors as "Kramer, Andersen, Thomas, Ferri, Crowley, Stratigaki, Troch et al." The PDF's
own title page and the DTU citation block give 16 authors: Kramer, Andersen, Thomas,
Bendixen, Bingham, Read, Holk, Ransley, Brown, Yu, Tran, Davidson, Horvath, Janson,
Nielsen and Eskilsson. **Ferri, Crowley, Stratigaki and Troch are not authors of this
paper** and look like a bleed from a different WEC reference. The file itself is the
right paper: title, DOI, journal, volume, issue and page all match, and the sha256 I
verified is the one quoted. Only that author line is wrong, and it should be fixed before
it is cited anywhere.

**Next units in my scope, in order.** Pilot `--fixed` at `lim = 1.2, n_grid = 64` on
Vista to (a) time a frame and convert 629 SUs into a real budget, (b) read the steady
reaction against **69.2180 N**, and (c) test the grid-count-versus-dx question in section
4.1. Then the three drops. Every number will carry N, spread, and the settle length it
was measured at, and will go through the physics-skeptic subagent before it is stated as
a result.

## 8. Nothing here has been through the physics-skeptic subagent yet

Per the dispatch's claim discipline, every percentage, force, verdict and distance above
is **[unreviewed]**. The derived quantities are closed-form and reproducible from the
tagged inputs; the readings from the paper are from its own full text; but no adversarial
pass has been run. Do not promote any of it to a register entry until that happens.
