# Resolution study of the force-coupled Yaris hull float, 2026-08-13

Branch `realism-exploration`. Scope: does the `+0.035 %` figure from the single
`n_grid = 96` run survive a resolution check. Every number below is from a run in this
directory; nothing is carried from a summary.

Runs: `res_A_g{72,96,128}.json`, `res_B_g{72,128}.json` (band control),
`res2_A_g{72,96,128}.json` (re-run adding water bookkeeping).
Driver: `simulation/realism/proto_hull_float.py`, SDF `yaris_sdf_r48_v2.npz`,
mesh SHA256 `b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95`
(verified live, not by path). Grids chosen at a constant refinement ratio r = 4/3.

---

## 1. THE HEADLINE: `+0.035 %` IS NOT A BUOYANCY VALIDATION, AT ANY GRID

`DynamicSDFBody._step` integrates (dynamic_body.py:207)

    dv = J/(M + m_add) + g*dt

Set `dv = 0` and it rearranges to `J/dt = M g` **exactly**. So the reported
`Fz_err_pct` is algebraically identical to the body's residual acceleration:

    Fz_err_pct  ==  100 * a_z / g

Verified to machine precision on all eight runs (max |difference| 1.4e-16). It measures
**whether the body has stopped moving**, not whether the fluid reproduces Archimedes.
`+0.035 %` means a residual acceleration of 3.5e-4 g and nothing more.

`implied_disp_volume_m3` is `Fz/(rho g)`, a restatement of the same quantity, so it is
circular in exactly the same way. Neither may be cited as agreement with Archimedes.

## 2. ON ITS OWN TERMS, IT IS RESOLUTION-STABLE

Every arm reaches static equilibrium, none diverged:

| arm | n_grid | dx | band | Fz_err % | a_z (m/s^2) | settled vz |
|---|---|---|---|---|---|---|
| A_g72  |  72 | 0.09722 | 0.09722 | +0.0187 | 0.00184 | -0.0018 |
| A_g96  |  96 | 0.07292 | 0.07292 | +0.0397 | 0.00390 | -0.0024 |
| A_g128 | 128 | 0.05469 | 0.05469 | +0.0306 | 0.00300 | -0.0060 |
| B_g72  |  72 | 0.09722 | 0.07292 | +0.0255 | 0.00250 | -0.0017 |
| B_g128 | 128 | 0.05469 | 0.07292 | +0.0160 | 0.00157 | -0.0055 |

So the *convergence* claim holds across a 1.78x grid range and a 1.78x band range.
That is the defensible statement, and it is a statement about the integrator.

## 3. THE INDEPENDENT CHECK DOES NOT CONVERGE

The non-circular question: at the draft it settles to, does the hull geometrically
displace `M/rho_w = 1.100 m^3`? Nothing in the integrator forces this. Measured by
integrating the same SDF the collide kernel queries (`submerged_volume`), calibrated
against a 6.7x spacing sweep (3.0587 +/- 0.006 m^3, converged).

| arm | n_grid | draft (m) | V_submerged (m^3) | vs 1.100 |
|---|---|---|---|---|
| A_g72  |  72 | 0.4911 | 1.1263 | **+2.4 %** |
| A_g96  |  96 | 0.5249 | 1.2862 | **+16.9 %** |
| A_g128 | 128 | 0.5479 | 1.3925 | **+26.6 %** |
| B_g72  |  72 | 0.5110 | 1.2175 | +10.7 % |
| B_g128 | 128 | 0.5384 | 1.3432 | +22.1 % |

Monotone in both arms, increasing with refinement, with no asymptote in range.
Richardson extrapolation at r = 4/3:

    arm A   observed order p = 1.423   limit 1.6026 m^3   (+45.7 % vs 1.100)
    arm B   observed order p = 0.649   limit 1.6208 m^3   (+47.3 % vs 1.100)

Two arms with different contact geometry extrapolate to within 1.1 % of each other, so
the limit is not an artifact of one arm. **The hull settles roughly 46 % deeper than its
own mass requires**, i.e. the coupling produces about 69 % of the analytic buoyant force
at a given submergence. Refining the grid makes this worse, not better.

## 4. WHY: THE CONTACT BAND IS COUPLED TO THE WATER GRID

Read from source, not assumed (this was the explicit question):

* **SDF resolution is independent of the water grid.** The collide kernel takes the
  node's world position `xw = (gx,gy,gz)*model.dx`, maps it into the SDF's own
  `origin`/`cell` frame and trilerps (`mpm_solver_warp.py:2697-2711`). `param.res` is
  never compared against `model.dx`. **No SDF rebuild is required when n_grid changes.**
* **The contact band IS coupled.** `add_sdf_collider` sets
  `if band is None: band = float(self.mpm_model.dx)` (`:2626-2627`), and the kernel gates
  the entire boundary condition on `if sd <= param.band` (`:2711`). So refining the water
  grid also thins the contact shell, and a naive resolution sweep moves two things at
  once. That is why arm B exists.

Attribution from the two arms: shrinking the band alone accounts for +8.3 pp at g72 and
+4.5 pp at g128; at fixed band, refining g72 -> g128 still moves +10.7 -> +22.1 %.
**Both mechanisms push the same way and neither converges.**

The engine's own containment guard (`:2639`) never fired: the SDF's `boundary_min` is
0.43930 m and the largest band used was 0.09722 m.

## 5. SEPARATE DEFECT FOUND: THE SDF UNDER-REPRESENTS THE HULL BY 11.8 %

The collider the kernel actually sees is the *trilinearly interpolated* res=48 field, and
its enclosed volume is **3.0587 m^3**, against the 3.466632 m^3 decimated mesh it was
built from and the canonical 3.542739 m^3 hull:

    canonical hull                     3.542739 m^3
    decimated to 39,381 faces          3.466632 m^3   -2.15 %
    as trilerp'd from the 48^3 SDF     3.058270 m^3   -11.76 % vs mesh, -13.66 % vs canonical

Converged across spacings 0.05 -> 0.0075 m (spread 0.006 m^3), so this is the SDF, not
the integrator. Cause is under-resolution: `build_sdf` makes a **cubic** grid sized on the
longest axis, so cell = 0.10979 m puts only ~16 cells across the hull's width and ~14
across its height, and the deepest interior value is -0.1957 m, under two cells.

A res=96 rebuild was priced live: `_winding_number` runs at 266 pts/s over 39,381 faces,
so res=48 is 6.9 min, **res=96 is 55 min**, res=128 is 131 min.

## 6. WHAT IS STILL OPEN, STATED RATHER THAN PAPERED OVER

Section 3 depends on where the free surface is. Two estimators disagree:

| n_grid | percentile surface | mass-balance surface | gap | V by percentile | V by mass balance |
|---|---|---|---|---|---|
|  72 | 1.1744 | 1.3115 | +0.1371 | 1.1263 (+2.4 %) | 1.7407 (+58.2 %) |
|  96 | 1.0938 | 1.2386 | +0.1448 | 1.2863 (+16.9 %) | 1.9037 (+73.1 %) |
| 128 | 1.0504 | 1.1723 | +0.1219 | 1.3925 (+26.6 %) | 1.9120 (+73.8 %) |

`water_retained_frac` is **1.0000 at every grid**, so this is NOT leakage: no particle
left the domain. The mass-balance estimator assumes the water occupies the wall-to-wall
footprint `(lim - 8*dx)^2` with a flat surface; using the full domain area `lim^2`
instead nearly closes the gap, which points at water spreading past the inner slip planes
into the 4-cell margin. That has not been confirmed and the footprint has not been
measured directly.

**Both estimators agree on the sign and on the failure to converge**, so section 3's
conclusion is robust; only its magnitude is bracketed (+2.4 to +74 %), not pinned.

Also unresolved: `floor` and the side walls are placed at `4*dx`, so the tank geometry
itself moves with n_grid. Water depth under the hull stayed near-constant (0.294 / 0.277 /
0.284 m) so the hull never grounded, but this is a confound in the study as built.

## 7. WHAT MAY AND MAY NOT BE SAID

MAY: the force-coupled loop closes and reaches a static equilibrium at every resolution
tested, with residual acceleration below 4e-4 g and no divergence, over g72-g128.

MAY: the axis-transposition hazard was handled rather than dodged, and the SDF carve
matters (an SDF carve removes 3.44 m^3 where a bbox carve would remove 6.86 m^3).

MAY NOT: "the coupling reproduces buoyancy to +0.035 %". It does not, and the figure is
a residual-acceleration metric.

MAY NOT: any statement that the equilibrium draft is grid-converged.
