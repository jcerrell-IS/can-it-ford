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

Half submergence **fixes the mass**, so these follow with no further input **[derived]**:

| quantity | value |
|---|---|
| sphere volume | 0.014137167 m^3 |
| mass | 7.0686 kg |
| mean density | exactly 500.0 kg/m^3 |
| waterplane area at the equator | 0.0706858 m^2 |
| hydrostatic heave stiffness `rho g A_w` | 693.428 N/m |
| buoyancy at equilibrium | **69.3428 N** |
| natural period, at an assumed `a33/m = 0.5` | 0.7769 s |

The last row is a **prediction used to size the run**, not a result: the added-mass ratio
is an assumption. The measured period is what gets compared.

**What I could not get.** The paper's Table 1 (measured physical parameters) and the
benchmark **time series itself**, which lives in the MDPI Supplementary Materials, are
not reachable from this host. MDPI returns 403 to both the article page and the PDF;
DTU Orbit's full-text PDF sits behind a Cloudflare challenge; OSTI carries metadata
only. Scite's full-text index served the running prose, which is where everything in the
table above came from, but not the tables or the supplementary archive. This is a
**blocker on the comparison, not on the scene**, and is tracked in section 7.

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

`c = sqrt(GAMMA * BULK / RHO_W) = 12.8452 m/s` **[derived from engine constants read at
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

Also asserted and passing: the UV sphere is closed and consistently oriented (every
directed edge used exactly once, every undirected edge shared by exactly two faces,
V-E+F = 2 at V=4514, E=13536, F=9024), outward-wound by signed volume, with a 0.1784%
polyhedral volume deficit; all vertices lie on the sphere to 2.8e-17 m; the submerged-cap
formula reproduces exactly half the sphere at `h = R` and 69.3428 N of buoyancy; and the
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

**BLOCKER-B1: the benchmark time series is not reachable from this host.** MDPI 403s the
article and the PDF; DTU Orbit's PDF is behind a Cloudflare challenge; OSTI has metadata
only; scite's full-text index has the prose but not the tables or the supplementary
archive. Two genuinely different routes were tried (publisher, then three independent
repositories) before this was written down. Without the time series the scene can be run
and self-checked but the **comparison** cannot be closed, which is half of the dispatch's
definition of done for Option B.

Nearest paths, in order of expected cost: download the Supplementary Materials from
`https://www.mdpi.com/1996-1073/14/2/269#supplementary` on a normal browser session and
drop the archive into the corpus; or pull the same dataset from a citing paper's
replication package, since the OES Task 10 group reused it.

**Next units in my scope, in order.** Pilot `--fixed` at `lim = 1.2, n_grid = 64` on
Vista to (a) time a frame and convert 629 SUs into a real budget, (b) read the steady
reaction against 69.3428 N, and (c) test the grid-count-versus-dx question in section
4.1. Then the three drops. Every number will carry N, spread, and the settle length it
was measured at, and will go through the physics-skeptic subagent before it is stated as
a result.

## 8. Nothing here has been through the physics-skeptic subagent yet

Per the dispatch's claim discipline, every percentage, force, verdict and distance above
is **[unreviewed]**. The derived quantities are closed-form and reproducible from the
tagged inputs; the readings from the paper are from its own full text; but no adversarial
pass has been run. Do not promote any of it to a register entry until that happens.
