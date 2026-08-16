# D4: Option A re-diagnosed. The blocker is mass, not grid nodes.

2026-08-17. Branch `claude/r5-physics`. Mac only, no GPU. Every source line below was read
live this session from the pinned engine at
`third_party/mpm-engine-544c93dd-solver-core/`, SHA `544c93dd`.

Claim tags: **[read]** primary source this session, **[measured]** computed here,
**[recalled]** from memory or a sibling, **[unreviewed]** no skeptic pass.

---

## 1. Why I came back to Option A

I chose Option B and deferred Option A as "the larger and less certain of the two". My own
last commit overturned that reasoning: the canonical scene has **no outflow boundary
condition**, so it cannot reach a steady state by construction, and the entire
settle-length programme is aimed at a target that does not exist. Option A stopped being
the deferred item and became the upstream one.

**First I verified the no-outflow claim myself rather than inheriting it** from the review
that raised it **[read, `renders/yaris_render_s1/sim_standing.py`]**:

- `:210-214` closes the domain: floor plane plus four slip walls at `restitution=0.05`,
  then `add_domain_walls()`.
- `:269-277` `_sustain_inflow` sets `vw[band, 0] = self.velocity` for particles with
  `x < inflow_x`. That is a **velocity clamp on a fixed spatial band of existing
  particles**, not an inflow.
- `:265-267` `_project_water` clamps outward velocity at the boundary. Containment, not
  outflow.
- No creation, deletion or recycling anywhere. Particle count is fixed at load.

`:410` prints `SCENARIO=STANDING_WATER_SUSTAINED_INFLOW`. **There is neither sustained
inflow nor outflow.** The name asserts a boundary condition the code does not implement.

## 2. The consequence, measured across all 17 runs

Water bulk mean particle speed, all 17 canonical runs, **settle length 8, 90 recorded
frames** **[measured]**:

| | median | range |
|---|---|---|
| total change over the run | **-73.0%** | -92.9% to -51.5% |
| change over the **second half alone** | **-34.4%** | -62.4% to +0.1% |

**0 of 17 runs gain. 16 of 17 are still losing more than 10% in the second half alone.**
The three g48 runs decay strictly monotonically at every one of 90 frames.

The single exception is instructive: `sweepV_g64_v3p0`, the fastest clamp, is the only run
near balance in its second half at **+0.1%**. That is consistent with the clamp injecting
momentum in proportion to its velocity while dissipation removes it, and it is the closest
thing in the set to a steady state.

## 3. The re-diagnosis, and it is not what the dispatch says

My dispatch states the cause as: "the Anura3D team impose BCs at **GRID NODES**; ours is
particle-level." **That is true of the driver and false of the engine** **[read]**.

`kernels/mpm_solver_warp.py:1283` `_apply_grid_bc` iterates `self.grid_postprocess[k]` and
launches each registered kernel over a grid box. Six kernels register into it: planes
`:2017`, cuboid_velocity `:2105`, revolved_cup `:2267`, domain_walls `:2379`, SDF `:2615`,
CDF `:2775`. Every one writes `state.grid_v_out[gx, gy, gz]` directly, e.g. `:2088`.

**The engine already imposes every one of its boundary conditions at grid nodes.** It even
already has a **prescribed-velocity cuboid grid BC** with a reaction-impulse accumulator
(`:2040-2058`). What is particle-level is the *driver*, which reaches around the engine and
writes particle velocities through `Solver.set_v`.

So the grid-node half of Option A is far cheaper than billed: it is a **wrapper**, not a
translation. `add_cuboid_velocity` exists at the warp layer and is simply **not exposed in
the public `Solver` API** (`core/solver.py` has `add_plane`, `add_box`, `set_box`,
`add_cup`, `set_cup`, `add_domain_walls`, `add_sdf_collider`, `add_cdf_collider`, and no
cuboid) **[read]**.

## 4. The actual blocker: no kernel can change mass

Here is the part that matters, and it explains the failure the dispatch records as
unexplained.

**Every registered grid BC writes velocity. None creates or destroys material.**
`_apply_grid_bc` operates on `grid_v_out`; particle count is fixed at `load_particles` and
no engine call adds or removes particles **[read]**.

The dispatch records that the BC "was wired and validated 3/3 on closed-form cases, then
**the level did NOT hold under steady inflow equals outflow**" **[recalled]**. That is
exactly what a velocity-only boundary must do. In a closed domain with fixed particle
count, **the free-surface level is fixed by conserved mass**. Prescribing node velocities
at an inlet and an outlet does not move mass across the boundary; it only redistributes
what is already inside. So the level cannot hold under a nominal inflow-equals-outflow
because there is no flow across the boundary at all, in either direction.

**Grid nodes were never the blocker. Mass conservation is.** Imposing the BC at nodes
instead of particles would not have fixed it, which is why that diagnosis, followed
faithfully, would have cost a solver rewrite and still failed.

### 4a. I tried to falsify this against the data, and it corrected the claim's status

The prediction I set out to break: if the level is fixed by conserved mass, a level proxy
should be near-invariant while the flow decays by tens of percent. Measured across all 17,
**settle 8, 90 frames** **[measured]**:

| | median | range |
|---|---|---|
| mass-weighted mean z | **+5.19%** | +1.10% to +6.37% |
| water bulk mean speed | **-73.0%** | -92.9% to -51.5% |
| ratio of the two | **0.058** | 0.021 to 0.082 |

**The level proxy is about 17x more stable than the flow**, which is the direction the
claim predicts. But **+5.19% exceeds the EOS compressibility bound of 1.80%** at 0.3 m
depth, so mean z is NOT invariant and my chosen proxy was wrong.

The resolution matters more than the numbers. For a fixed volume over a fixed footprint,
the mass centroid is **minimised** when the surface is flat, so any wave or splash raises
mean z at constant mass. A +5% centroid rise with 0% mass change is therefore evidence of
**sustained redistribution**, i.e. the surface never flattens, and is fully consistent with
conserved mass rather than evidence against it.

**So section 4's claim is not an empirical finding and I should not have implied it was.**
Total water volume is fixed **by construction**: particle count is set once at
`load_particles` and per-particle volume is assigned once at load, so the product cannot
change. It is an identity in the code, not a measurement. The measurement above adds
something different and still useful: the surface is still being actively redistributed at
frame 90, and the level-like quantity is an order of magnitude stiffer than the flow.

The status change is the point. A claim that is true by construction is stronger than one
supported by a correlation, but only if it is labelled correctly, and it cannot be
"confirmed" by a proxy that measures something else.

## 5. What Option A actually requires, in cost order

1. **Expose the existing grid-node velocity BC.** A public `Solver.add_cuboid_velocity`
   wrapper over the warp-layer registrar. Small, and it removes the driver's particle-level
   `set_v` write, which is a correctness improvement on its own.
2. **A mass sink, and this is the real work.** A true outflow needs particles to leave.
   The engine offers no hook, so the options are:
   (a) **particle recycling** in the driver, teleporting particles that cross the outlet
       back to the inlet, which conserves mass exactly and is the cheapest honest
       approximation of a periodic channel, but is not an open boundary;
   (b) **variable particle count** in the engine, which is a genuine solver change and
       touches every fixed-size warp array allocated at `load_particles`;
   (c) **a damping/sponge layer** at the outlet, which absorbs momentum without removing
       mass. That suppresses reflection but still cannot hold a level against a net inflow.
3. **Only then** the Zhao, Bolognin, Liang, Rohe and Vardon 2019 formulation
   (`10.1016/J.COMPFLUID.2018.10.007`), and the Remmerswaal et al. 2019 companion, become
   the thing being implemented rather than the thing being guessed at.

**Recommended:** (1) plus (2a). Recycling gives a genuine sustained channel flow with exact
mass conservation and needs no engine change, and it converts the scene from "spins down by
73%" to something that can actually reach a steady state. It is honest about what it is: a
periodic channel, not an open boundary, and it must be written up as such.

## 6. What this does to the rest of my work

- The settle-length programme is **downstream of this**. There is no steady state to detect
  in the current scene, so `blocking.py`'s `undecidable_too_short` on 17/17 is the correct
  answer twice over: the runs are too short *and* the target does not exist.
- **Peak and time-resolved quantities remain valid.** `failure_modes.py` takes peaks and no
  means, so the 16 SLIDE / 1 STUCK verdicts are not affected by this **[recalled]**.
- The **brake-state result is unaffected**: it rests on peak accelerations and a bound, not
  on any window mean.
- **Kramer Job B is unaffected**: the sphere hydrostatic pilot is a still-water scene with
  no through-flow, so it has no outflow requirement at all.

## 7. Status

Nothing here has been run. Section 2 is measured; sections 3 and 4 are read from source;
section 5 is a plan and is **[unreviewed]**. The claim I would most want attacked is section
4: that a velocity-only grid BC cannot hold a level in a fixed-particle-count domain, and
therefore that the recorded 3/3 closed-form validation and the level failure are consistent
with each other rather than in tension.
