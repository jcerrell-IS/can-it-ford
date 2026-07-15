# FINDING: Track 2 seeds 88-96% of the water slab inside the vehicle box

Date: July 15, 2026
Found by: the penetration panel added in the same pass (`simulation/can_it_ford_L2_mpm.py`)
Status: **open. Confirmed against real data. Proposed fix written up but NOT executed and NOT tested.**

## Scope: this affects every run on Track 2, not a subset

The x and y overlap are unconditional. Water x in [0.100, 0.450] is entirely swallowed by vehicle
x in [-1.330, 3.330], and the y extents overlap 99.4%. Both are fixed constants, independent of depth
and velocity. **Depth is the only axis that modulates anything, and it only changes severity:**

| depth | overlap of the water slab |
|---|---|
| 0.15 m | 76.2% |
| 0.30 m | 87.8% |
| 0.45 m | 91.7% |
| 0.60 m | 93.6% |
| 0.80 m | 95.1% |
| 1.00 m | 96.0% |

Overlap would vanish only below 0.035 m, the vehicle's underbody clearance. The shallowest depth this
project tests is 0.15 m, over 4x that. Velocity does not affect the overlap at all. So **all 36
historical depth/velocity cells are affected**, and this cannot be filtered down to salvage part of the
sweep. Deeper water is worse, not better.

## Confirmed against real particle data, not just geometry

Two independent confirmations, so this is not an inference from the morph definitions alone:

1. **Genesis does not carve the vehicle out of the water.** Particle count divided by water box volume
   is exactly 1.000e6 particles/m3 for every run: 189000 for a 0.189 m3 box, 378000 for 0.378 m3,
   630000 for 0.630 m3. Exact to the digit. The Box morph is sampled as a full solid volume with no
   subtraction of any other entity, so particles are generated at coordinates occupied by the vehicle.
2. **They are still there at the end.** In the real final-state `.npz` files, 54.8% of particles sit
   inside the vehicle box after 500 steps. Measured, not predicted. It starts at 87.8% by geometry at
   t=0, so the solver ejects some of the overlap over the run and roughly half never resolves.

Caveat: at t=0 the box is axis-aligned, so the axis-aligned test is exact then. Once the vehicle
rotates, the same test slightly overestimates. That does not affect the t=0 figure, which is the one
that matters.

## What

In `can_it_ford_L2_mpm.py` as currently written, the water slab is seeded almost entirely *inside* the
vehicle's collision box. Pure geometry from the scene as written, no simulation needed:

```
water   morph: pos=(0.275, 0.0, depth/2), size=(0.35, 1.8, depth)  -> x in [0.100, 0.450]
vehicle morph: pos=(1.0,   0.0, 0.755),   size=(4.66, 1.79, 1.44)  -> x in [-1.330, 3.330]
```

The water's entire x-extent lies inside the vehicle's x-extent. Overlap of the water slab volume:

| depth | overlap volume | share of the water slab |
|---|---|---|
| 0.30 m | 0.1660 m3 | **87.8%** |
| 0.60 m | 0.3540 m3 | **93.6%** |
| 1.00 m | 0.6046 m3 | **96.0%** |

The inflow clamp plane (`pts[:, 0] < 0.14`) is also inside the vehicle box, since `-1.330 < 0.14 < 3.330`.
So the boundary condition that drives the flow injects momentum into a region occupied by the solid.

## Why it happened

This is the COUPLED VARIABLES failure mode from CLAUDE.md, one dependent further than the one that was
caught. Commit `67915be` resized the vehicle box from the 1.0 x 1.6 x 1.5 m placeholder to the real
sedan bbox 4.66 x 1.79 x 1.44 m, but left `pos=(1.0, 0.0, 0.755)` unchanged.

- Before the resize: vehicle x in [0.500, 1.500]. Water x in [0.100, 0.450]. **No overlap** (0.45 < 0.50).
  The water sat just upstream of the bumper, which is what the scene intends.
- After the resize: the box grew 4.66x longer about its centre, so its leading face moved from
  x = 0.500 back to x = -1.330, sweeping backwards over the entire water inlet.

The resize's density dependent was caught and fixed (`rho` 604 -> 115.7, commit `e0dd0fe`). The
*position* dependent was not. Box dimensions are coupled to position whenever the box is defined by a
centre, and that coupling is not listed in CLAUDE.md's COUPLED VARIABLES section.

## Relationship to the ruled-out crash dead end

This is **not** a re-proposal of the ruled-out hypothesis. CLAUDE.md records water/vehicle overlap as
tested and ruled out *as the sole cause of the CUDA_ERROR_ILLEGAL_ADDRESS crash* (box reverted to
1.0 x 1.6 x 1.5, domain kept widened, crash still occurred identically). That result stands and is not
questioned here.

The claim here is narrower and different: independent of the crash, a run that completes is not
physically meaningful, because ~90% of the water starts inside a solid. Overlap not causing the crash
and overlap invalidating the physics are separate statements. Both can be true.

## Consequence for the penetration panel

`n_penetrating` / `penetration_max_m` will read near-saturation from step 0. That is the panel
reporting correctly, not a bug in it. But a panel that always reports a violation carries as little
information as one that can never report a violation, which is precisely the defect retracted in
`docs/viability_audit_mass_retraction.md`. Until the geometry is resolved, read the penetration panel
as a scene-setup indicator, not a solver-health indicator.

## PROPOSAL: move the vehicle downstream. Documented, NOT executed.

**Status: written up only. Not run, not tested on GPU, not committed to as the fix.** Track 2 is
dormant for compute. Everything below is arithmetic and hand-checkable; none of it has been validated
against an actual solver run, and it should not be treated as verified until it has been.

### 1. The shift arithmetic

```
vehicle now spans   x in [-1.330, 3.330]   leading face at -1.330
water slab          x in [ 0.100, 0.450]   downstream face at 0.450

minimum shift  = 0.450 - (-1.330) = 1.780 m   -> leading face exactly touching the water, zero standoff
proposed shift = 0.500 - (-1.330) = 1.830 m   -> restores the pre-resize leading face at x = 0.500
```

The proposed 1.830 m is not arbitrary: `bak2` had the vehicle's leading face at exactly x = 0.500,
giving a 0.050 m standoff from the water's downstream face at 0.450. That is the geometry the scene was
built around, so the proposal restores it rather than inventing a new one.

Result: `pos[0]` goes 1.0 -> **2.830**. Vehicle spans x in [0.500, 5.160].

### 2. Yes, this forces the domain wider. Whether that reintroduces the memory risk depends entirely on the lower bound.

The vehicle's trailing face lands at 5.160, against a current domain upper bound of x = 4.5. **It
protrudes 0.660 m outside the domain.** So the upper bound must move regardless. This is the coupling
that matters, and it cuts both ways.

Cell counts, computed with the solver's own formula `round(gd*upper) - round(gd*lower) + 1`
(`mpm_solver.py:53-57`), at `grid_density=128`:

| configuration | x-range | grid res | cells | vs current |
|---|---|---|---|---|
| `bak2`, pre-widening | [-0.1, 2.1], 2.2 m | [283, 257, 334] | 24.3M | baseline of the crash finding |
| **current** | [-2.5, 4.5], 7.0 m | [897, 257, 334] | **77.0M** | the live crash suspect |
| **A. naive shift**: keep lower = -2.5, extend upper to 5.4 | [-2.5, 5.4], 7.9 m | [1012, 257, 334] | **86.9M** | **+12.8%, WORSE** |
| **B. shift + re-centre**: lower = -0.5, upper = 5.4 | [-0.5, 5.4], 5.9 m | [756, 257, 334] | **64.9M** | **-15.7%, better** |

**Said plainly: option A reintroduces the risk and makes it worse than it is today.** It pushes cell
count 12.8% above the 77.0M configuration already suspected of exhausting memory, on the same x-axis
growth that took 24.3M to 77.0M in the first place. Do not do the naive shift.

Option B avoids it, and is the reason the shift is worth proposing at all. Once the vehicle's leading
face moves to x = 0.500, **nothing in the scene lives below x = 0.100 any more**, so the lower bound at
-2.5 exists only to accommodate a vehicle that is no longer there. Pulling it to -0.5 (0.6 m of upstream
splash margin) more than pays for the upper bound's extension: the domain gets *narrower*, 7.0 m -> 5.9 m,
and cell count drops 15.7% below today's. The shift and the re-centre are a single edit, not two.

Unverified caveat: 64.9M cells is still far above `bak2`'s 24.3M, so if the crash is driven by absolute
cell count rather than by the increment, option B reduces the risk without eliminating it. This has not
been tested.

### 3. Does the water still reach the vehicle? Yes, with 20x margin at the worst case.

The null-result risk is real and worth checking, but it is not close here. 500 steps at `dt = 4e-3` is
**2.0 s** of simulated time. The water's downstream face starts at x = 0.450 and the proposed leading
face is at x = 0.500, so the gap to close is **0.050 m**.

| inflow velocity | advection distance in 2.0 s | steps to close the 0.050 m gap | margin |
|---|---|---|---|
| 0.5 m/s (slowest tested) | 1.00 m | 25 of 500 | **20x** |
| 1.0 m/s | 2.00 m | 12 of 500 | 40x |
| 1.5 m/s | 3.00 m | 8 of 500 | 60x |
| 2.0 m/s (fastest tested) | 4.00 m | 6 of 500 | 80x |

Even at the slowest tested velocity the water makes contact within the first 5% of the run and has 20
times the travel it needs. This is advection alone. Gravitational collapse of the slab adds to it: the
dam-break front speed is roughly `2*sqrt(g*h)`, which is 2.43 m/s at depth 0.15 and 6.26 m/s at depth
1.00, faster than the imposed inflow in every tested case. So the front is if anything quicker than the
table suggests, and still-water runs at v = 0 also close a 0.050 m gap by collapse alone.

**The null-result boundary, for completeness:** at the slowest velocity of 0.5 m/s the front travels
1.00 m in 500 steps, so the leading face must sit at or below x = 1.450 for contact, i.e. a maximum
shift of 2.780 m. The proposed 1.830 m sits at the *bottom* of the 1.780 to 2.780 m safe window, which
is where the margin is greatest. A shift anywhere near 2.780 m would produce exactly the null result
worth avoiding: a vehicle the water only grazes as the run ends.

### 4. Coupled dependents, stated per the COUPLED VARIABLES rule

Changing `pos[0]` touches these, and all were checked:

- **domain bounds**: forced. Upper must reach >= 5.160. Lower should move to -0.5 in the same edit, or
  memory gets worse rather than better. See the table above.
- **cell count and memory**: -15.7% under option B, +12.8% under option A. Recomputed above, not assumed.
- **`rho` (115.7)**: **not affected.** Density couples to box *dimensions*, not box *position*, and the
  size is unchanged at 4.66 x 1.79 x 1.44. The 1390 kg sedan target still holds. This proposal does not
  reopen the `rho` fix in commit `e0dd0fe`.
- **inflow clamp plane (`x < 0.14`)**: stays at 0.14, still inside the water slab [0.100, 0.450], but
  now correctly *outside* the vehicle, which is the second half of what this fixes.
- **`grid_density`**: all counts above are at 128. It is now a CLI flag, so a run at 64 divides these
  by 8, and the descending 32/64/128 GCI ladder is unaffected by the reposition.

### 5. Alternatives not proposed, and why

- Moving the water slab upstream instead: changes what the inflow clamp plane at x < 0.14 means, since
  the clamp is defined in absolute coordinates and would no longer sit inside the slab.
- Reconsidering the abstraction: a 4.66 m vehicle against a 0.35 m water slab is a questionable pairing
  regardless of where either sits. The slab is 7.5% of the vehicle's length. Worth raising with Kumar
  as a modelling question, separate from this geometry bug.

### 6. What would have to happen before this is real

1. Apply the shift and the re-centre as one edit (`pos[0]` 1.0 -> 2.830, bounds -> [-0.5, 5.4]).
2. Smoke run under `PYTEST_VERSION` (horizon 5) to confirm the scene builds and allocates.
3. One `gh`-node run at `--depth 0.30 --velocity 1.5 --grid-density 64`, checking that
   `n_penetrating` now starts at ~0 instead of ~88%, which is the whole point.
4. Only then a grid128 run, watching memory against the 64.9M figure.
