# The floor plane is NOT single-layer repulsive. It is a one-sided grid-velocity
# projection, and that distinction changes which remedy applies.

2026-08-18. Read directly from the pinned engine,
`third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_solver_warp.py`, the
`Dirichlet_collider` plane kernel at **:1935-1990**.

## 1. Diagnosis

**It is not a repulsive force at all, and it is not particle-based.** It is a
**grid-node velocity projection**:

```python
dotproduct = wp.dot(offset, n)
if dotproduct < 0.0:                     # STRICTLY outside the plane
    ...
    v = v - wp.min(normal_component, 0.0) * n     # separable: kill inward normal only
```

Three properties follow, and they are what matters for the leak:

1. **It acts on GRID NODES, not particles.** No repulsive body force is ever applied to a
   particle. So the DualSPHysics "single-layer repulsive boundary" framing does not
   transfer directly: the named failure mode there is force evaluation from a
   under-resolved repulsive layer, and there is no repulsive layer here.
2. **It is one-sided at strict inequality.** `dotproduct < 0.0` means a node lying
   **exactly on** the plane is untouched. `FLOOR = 0.075` is **exactly 4 dx** at g64, so
   the on-plane node is unconstrained, and the highest constrained node sits a full cell
   below the nominal floor. This is a real, separate bug and it is worth ~1.8 cm of the
   observed fall.
3. **Nothing is applied on the fluid side.** Nodes with `dotproduct > 0` receive no
   treatment whatsoever, so there is no boundary layer in the fluid at all.

## 2. Why this produces exactly the reported leak

The B-spline stencil half-width is **1.5 dx**. A particle within 1.5 dx of the plane has
support on nodes **both sides** of it. The nodes below carry **no particle mass**, because
no particles exist there, so P2G leaves them mass-deficient. The particle therefore sees a
truncated kernel and a density deficit on its underside, which is precisely the
**kernel-truncation density deficiency** the literature names, and the resulting pressure
gradient points **into** the boundary.

That predicts the measured signature, and it matches on all three counts:

- **penetration rather than compaction** (occupied volume flat after frame 50, counts
  still growing)
- **an area-distributed floor leak** (4.505% below floor, scaling 1.19 rather than the
  1.00 a pure area effect would give, and NOT the perimeter/area 2.00 the wall leak shows)
- **a perimeter-scaled wall leak** (2.410%, halving 1.96 against a predicted 2.00 when the
  domain doubles), which is the same mechanism acting on a boundary whose length scales
  differently

**So the wall leak and the floor leak are one mechanism with two geometries**, which is
consistent with the coordinator's measurement that only the wall part scales as
perimeter/area.

## 3. The named remedies, against what this engine actually exposes

| remedy | implementable from `simulation/r5_physics/`? |
|---|---|
| multi-layer / mDBC | **No.** The half-space below the plane is *already* fully constrained by `dotproduct < 0`, so stacking more planes adds nothing. Thickness is not the deficiency here. |
| boundary-integral / semi-analytical | **No.** Requires a P2G-side correction inside the engine. |
| **ghost-particle wall** | **Correct remedy, but BLOCKED at the scene level.** |

**The ghost-particle wall is the right fix** because the deficiency is missing *mass* below
the boundary, not missing *constraint*. Seeding frozen particles below the floor would
restore the density the truncated kernel is missing.

**It cannot be done from the scene.** Verified by direct search of the pinned engine's
public API: `core/solver.py` exposes **no** `pin`, `freeze`, `set_particle_*`,
`particle_selection` or ghost API, and `materials/__init__.py` exposes only `newtonian`,
`granular`, `elastic`, `vonmises`, `tabulated_viscous` and `tabulated_mu_i`. The
**stationary material 7** that would freeze them exists in the kernels but is **not
reachable** through `set_material_range`. The only freezing path, `"rigid"`, creates a
**free** material-8 body that would fall under gravity, which is worse than the leak.

## 4. What I recommend, and what I did not do

**I did not implement a fix, and I did not re-run job B.** Doing either would have meant
either editing the pinned engine, which is outside my scope and would break the sha256
that stamps every published run, or shipping a `"rigid"` bodge I could not test.

The cheapest *correct* fix is a one-line engine change: relax `dotproduct < 0.0` to
`<= 0.0` so the on-plane node is constrained. **That addresses defect 2 only**, worth
~1.8 cm of ~6 cm, and leaves the kernel-truncation deficiency untouched. It also changes
the sha256 of the pinned solver, so it needs an owner decision, not a D4 commit.

The correct full fix needs a ghost-particle or boundary-integral treatment **in the
engine**, which is a solver change and a different piece of work from this dispatch.

**UNREVIEWED.** No physics-skeptic pass. Given five of five headline claims were
overturned tonight, treat section 2's mechanism attribution as a hypothesis that matches
three measured signatures, not as established.
