"""Recirculating open-channel in/outflow boundary condition for warpmpm.

WHY THIS SHAPE, AND NOT THE SHAPE ZHAO ET AL DESCRIBE
-----------------------------------------------------
Zhao, Bolognin, Liang, Rohe and Vardon (2019), Computers and Fluids 179, 27-33,
doi:10.1016/j.compfluid.2018.10.007, impose a velocity-controlled inflow and a
pressure-controlled outflow by ADDING and REMOVING material points at the domain
edges. warpmpm cannot add or remove a particle after load time.

Verified live 2026-08-18 by direct read of the pinned solver core at
third_party/mpm-engine-544c93dd-solver-core/core/solver.py: load_particles (:103)
constructs MPM_Simulator_WARP(len(pos)) exactly once, and the Solver class exposes
no add_particles, no remove_particles and no resize entry point anywhere in :58-641.

The engine's own streamwise wrap, periodic_x (:93), is NOT a way round this. Its
own docstring says "Incompatible with CDF colliders and rigid bodies", and the
gated vehicle IS a rigid body: sim_standing.py calls
set_material_range(n_water, n_total, "rigid", obj_id=0) then finalize_rigid_bodies().

So the translation into this engine is one-in-one-out RECYCLING inside a fixed
pool: a water particle that crosses the outflow plane is moved back to the inflow
plane in the same operation. That is exactly Zhao et al's UNIFORM channel case,
where inflow and outflow discharge are equal by construction. It does NOT express
their NON-UNIFORM case, which needs a net flux imbalance and therefore a spare
particle reservoir. That limitation is real and is stated in the run summary.

WHY (y, z) ARE PRESERVED ON RECYCLE
-----------------------------------
A recycled particle keeps whatever compression state it carries. For a warpmpm
fluid that state is ONE SCALAR: kernels/mpm_utils.py:1086-1089 overwrites F every
substep with J**(1/3) * I for mat 6, 10 and 12, discarding the deviatoric part
entirely, and the pressure is p = -bulk * (J**-1.1 - 1) inside
kirchoff_stress_newtonian (mpm_utils.py:28-54).

In a uniform channel the hydrostatic head is a function of z alone. Re-inserting a
particle at the SAME (y, z) therefore re-inserts it at the same head, where its
existing J is already the correct J. Moving it to a different depth would inject a
spurious pressure that NO host-side fix could undo, because F has no setter: the
Solver exposes F() (:543) and F_torch() (:625) but no set_F.

This is why the recycler translates in x only and never repositions in y or z.
"""

from __future__ import annotations

import numpy as np

# The four names below the first three were added by 7933f1e (OverfallBC,
# overfall_metrics, discharge_per_width) and 1315a4a (ReservePool), measured by
# `git cat-file blob` on each revision of this file rather than from the commit
# subjects, and they never reached __all__, so `from openchannel_bc import *`
# exported a module that had grown four public names and still advertised three.
# No caller uses a star import today, so nothing was broken; it is corrected
# here rather than carried forward.
__all__ = ["RecyclingChannelBC", "depth_profile", "tilted_gravity",
           "OverfallBC", "overfall_metrics", "discharge_per_width",
           "ReservePool"]


def tilted_gravity(grade_deg: float, g: float = 9.81):
    """Gravity for a road of longitudinal grade `grade_deg`, in road-aligned axes.

    The road surface stays the flat z = floor plane and gravity acquires a
    streamwise component, which is the standard chute formulation and the one the
    engine's own periodic_x docstring names ("tilted gravity + periodic streamwise
    direction", solver.py:90-92). Tilting the FLOOR instead does not work in a
    bounded domain: conserving volume in a closed box forces a redistribution
    larger than the slope effect being measured.

    Reachable through the public API with no engine change: Solver.set_material
    builds {"material": name, "g": [0, 0, -9.81], **params} with **params LAST
    (solver.py:165-167), so a g passed through **overrides wins, and
    set_parameters_dict honours it at kernels/mpm_solver_warp.py:742-743
    (`if "g" in kwargs: self.set_gravity(kwargs["g"])`).

    Positive grade_deg tilts gravity toward +x, i.e. water runs downhill in +x.
    """
    th = np.deg2rad(float(grade_deg))
    return [float(g * np.sin(th)), 0.0, float(-g * np.cos(th))]


class RecyclingChannelBC:
    """One-in-one-out streamwise recycling over water particles [0, n_water).

    Parameters
    ----------
    n_water : int
        Water occupies indices [0, n_water). Everything at or above n_water is
        never read and never written, so a rigid vehicle appended after the water
        (the sim_standing.py layout) is untouched by construction.
    x_in, x_out : float
        Inflow and outflow planes, metres, in grid coordinates. x_in < x_out.
    inlet_velocity : float
        Streamwise velocity prescribed at the inlet, m/s. This is Zhao et al's
        velocity-controlled inflow.
    dx : float
        Grid spacing, used only for the safety assertions.
    grid_lim : float
        Domain extent, used only for the safety assertions.
    prescribe : {"full", "streamwise"}
        "full" sets the recycled velocity to (inlet_velocity, 0, 0), which is the
        faithful velocity-controlled inflow. "streamwise" sets vx only and leaves
        vy and vz, which preserves any cross-stream structure the particle carried.

    NOTE ON sort_interval. This class addresses water by index range, so the
    Solver MUST keep sort_interval = 0 (its default, solver.py:80). A block sort
    permutes particle identity and the range [0, n_water) would stop meaning
    water. The driver asserts this.
    """

    def __init__(self, n_water, x_in, x_out, inlet_velocity, dx, grid_lim,
                 prescribe="full", inject_len=None, seed=0):
        if not (x_in < x_out):
            raise ValueError("x_in (%r) must be < x_out (%r)" % (x_in, x_out))
        # The engine raises if any particle sits within 2 cells of the grid edge,
        # because the quadratic P2G stencil would write out of bounds
        # (solver.py:_update_grid_box, :506-512, threshold 1.5*dx low / 2.5*dx high).
        # Recycling teleports particles, so the landing plane has to clear it.
        if x_in < 2.5 * dx:
            raise ValueError(
                "x_in %.4f is inside the P2G edge guard (needs >= 2.5*dx = %.4f); "
                "the recycled particle would corrupt grid memory" % (x_in, 2.5 * dx))
        if x_out > grid_lim - 2.5 * dx:
            raise ValueError(
                "x_out %.4f is inside the P2G edge guard (needs <= grid_lim - 2.5*dx "
                "= %.4f)" % (x_out, grid_lim - 2.5 * dx))
        if prescribe not in ("full", "streamwise"):
            raise ValueError("prescribe must be 'full' or 'streamwise'")
        self.n_water = int(n_water)
        self.x_in = float(x_in)
        self.x_out = float(x_out)
        self.inlet_velocity = float(inlet_velocity)
        self.prescribe = prescribe
        self.dx = float(dx)
        self.grid_lim = float(grid_lim)
        # Re-injection spread. DEFAULT None reproduces the original behaviour exactly
        # (land at x_in plus the sub-cell overshoot), because register items 20 and 24
        # were measured with it and changing a BC under published numbers is not a
        # free action. Set inject_len to spread injection over a band instead.
        #
        # WHY IT MATTERS: item 24 records that the end bins sit about 25 percent above
        # mid-channel. The inflow end of that is self-inflicted: every recycled
        # particle in a tick lands within one sub-cell overshoot of the same plane, so
        # a tick's worth of water arrives as a sheet. Spreading it over a band of a few
        # cells delivers the same flux without the sheet.
        self.inject_len = None if inject_len is None else float(inject_len)
        self.rng = np.random.default_rng(seed)
        self.recycled_total = 0
        self.recycled_last = 0
        self.clamped_y = 0
        self.clamped_z = 0
        # Largest single-tick overshoot seen. If this ever approaches the channel
        # length the recycler is being called too rarely and particles are jumping
        # more than one channel per tick, which would alias the flux.
        self.max_overshoot = 0.0

    @property
    def channel_length(self):
        return self.x_out - self.x_in

    def apply(self, x, v):
        """Recycle in place. Returns the number of particles moved this call.

        x, v are the (N, 3) host arrays from Solver.x() / Solver.v(). The caller
        writes them back with set_x / set_v. Only rows [0, n_water) are touched.
        """
        nw = self.n_water
        xs = x[:nw, 0]
        crossed = xs >= self.x_out
        n = int(crossed.sum())
        self.recycled_last = n
        if n == 0:
            return 0
        overshoot = xs[crossed] - self.x_out
        self.max_overshoot = max(self.max_overshoot, float(overshoot.max()))
        # Carry the sub-cell overshoot across, so particles land spread through the
        # first slab instead of stacking on the plane itself. Stacking would build a
        # sheet of coincident particles at x_in and show up as a pressure spike.
        # The modulo is a guard for the pathological case of an overshoot larger
        # than the channel, which would otherwise place the particle past x_out
        # again and recycle it forever within one tick.
        L = self.channel_length
        if self.inject_len is None:
            x[:nw, 0][crossed] = self.x_in + np.mod(overshoot, L)
        else:
            x[:nw, 0][crossed] = self.x_in + self.rng.uniform(0.0, self.inject_len, n)
        # y and z are deliberately untouched: see the module docstring on J.
        if self.prescribe == "full":
            v[:nw][crossed] = (self.inlet_velocity, 0.0, 0.0)
        else:
            v[:nw, 0][crossed] = self.inlet_velocity
        self.recycled_total += n
        return n

    def project_cross_stream(self, x, v, y_lo, y_hi, z_floor):
        """Clamp water into the cross-stream box, never in x.

        This is the recycling-mode replacement for sim_standing.py's
        _project_water, which clamps ALL THREE axes into [wall, lim-wall]. Clamping
        x is exactly the closed-box behaviour this class exists to remove, so x is
        left alone here and the outflow plane is the only streamwise condition.
        Returns the number of particle-axis clamps applied.
        """
        nw = self.n_water
        w = x[:nw]
        vw = v[:nw]
        lo = np.array([-np.inf, y_lo, z_floor], dtype=w.dtype)
        hi = np.array([np.inf, y_hi, np.inf], dtype=w.dtype)
        out_lo = w < lo
        out_hi = w > hi
        n = int(out_lo.sum() + out_hi.sum())
        # Per-axis, because a single total cannot say whether water is escaping
        # sideways or sinking through the bed, and those have different causes.
        self.clamped_y += int(out_lo[:, 1].sum() + out_hi[:, 1].sum())
        self.clamped_z += int(out_lo[:, 2].sum() + out_hi[:, 2].sum())
        if n:
            np.clip(w, lo, hi, out=w)
            vw[out_lo] = np.maximum(vw[out_lo], 0.0)
            vw[out_hi] = np.minimum(vw[out_hi], 0.0)
        return n


def depth_profile(xw, floor, x_lo, x_hi, n_bins=12, pct=99.5, min_count=20):
    """Free-surface height above `floor` in `n_bins` streamwise bins.

    Uses the same 99.5th-percentile-of-z estimator sim_standing.py already uses for
    local_depth_bow / local_depth_footprint (:470-478), so a depth here is
    commensurable with a depth there rather than being a new and differently-biased
    statistic.

    THIS IS THE FALSIFIABLE TEST FOR THE BOUNDED-DOMAIN ARTIFACT. A closed box with
    an upstream velocity clamp must pile water against the downstream wall, so the
    profile rises with x. A working outflow must not. Returns (centres, depths) with
    NaN in any bin holding fewer than min_count particles.
    """
    edges = np.linspace(x_lo, x_hi, int(n_bins) + 1)
    centres = 0.5 * (edges[:-1] + edges[1:])
    depths = np.full(int(n_bins), np.nan)
    idx = np.digitize(xw[:, 0], edges) - 1
    for b in range(int(n_bins)):
        sel = (idx == b) & (xw[:, 2] >= floor)
        if int(sel.sum()) >= min_count:
            depths[b] = float(np.percentile(xw[sel, 2], pct)) - floor
    return centres, depths


def _selftest():
    """Runs without warp, numpy only, so it is checkable on the Mac."""
    rng = np.random.default_rng(0)
    nw, nveh = 500, 37
    dx, lim = 0.147, 9.42
    x = np.zeros((nw + nveh, 3), dtype=np.float32)
    # Range deliberately EXCEEDS x_out. The first version of this fixture used
    # uniform(0.6, 8.8) against an outflow plane at 8.80, and numpy's uniform is
    # half-open, so not one particle ever crossed: n was 0 and checks 3 to 6 were
    # vacuous while reporting PASS. Same failure mode as register item 25, where
    # clamped_z == 0 read as clean containment and meant the check never ran.
    x[:, 0] = rng.uniform(0.6, 8.8, nw + nveh)
    # ...and then deliberately push a fifth of the WATER past the outflow plane, so
    # the recycler has something to do. A uniform spread over [0.6, 8.8) puts almost
    # nothing past 8.80, which is how the first version of this fixture came to
    # exercise nothing at all.
    # Overshoot range matched to what a real tick produces: the measured
    # max_overshoot in the g64 runs was 0.0425 m, so 0.05 m here. An unrealistically
    # large synthetic overshoot would flatter the default and understate what the
    # injection band actually changes.
    x[: nw // 5, 0] = rng.uniform(8.80, 8.85, nw // 5)
    x[:, 1] = rng.uniform(0.6, 8.8, nw + nveh)
    x[:, 2] = rng.uniform(0.45, 0.75, nw + nveh)
    v = rng.normal(0, 0.3, (nw + nveh, 3)).astype(np.float32)
    x0, v0 = x.copy(), v.copy()

    bc = RecyclingChannelBC(n_water=nw, x_in=0.60, x_out=8.80,
                            inlet_velocity=1.5, dx=dx, grid_lim=lim)
    n = bc.apply(x, v)
    moved = x0[:nw, 0] >= 8.80
    assert n == int(moved.sum()), (n, int(moved.sum()))
    assert n >= 100, ("fixture recycles too few particles to test anything", n)
    # 1. vehicle rows are untouched
    assert np.array_equal(x[nw:], x0[nw:]), "vehicle positions were modified"
    assert np.array_equal(v[nw:], v0[nw:]), "vehicle velocities were modified"
    # 2. non-crossing water untouched
    assert np.array_equal(x[:nw][~moved], x0[:nw][~moved])
    assert np.array_equal(v[:nw][~moved], v0[:nw][~moved])
    # 3. y and z preserved on the recycled ones (the J argument)
    assert np.array_equal(x[:nw][moved][:, 1:], x0[:nw][moved][:, 1:]), "y/z changed"
    # 4. they landed downstream of x_in, upstream of x_out
    got = x[:nw][moved][:, 0]
    assert (got >= 0.60).all() and (got < 8.80).all(), (got.min(), got.max())
    # 5. overshoot carried, so they are NOT all stacked on the plane
    if moved.sum() > 2:
        assert got.std() > 0.0, "recycled particles stacked on the inflow plane"
    # 6. velocity prescribed
    assert np.allclose(v[:nw][moved], np.array([1.5, 0.0, 0.0], dtype=np.float32))
    # 7. count conserved
    assert x.shape[0] == nw + nveh

    # 8. streamwise prescribe leaves vy, vz
    x2, v2 = x0.copy(), v0.copy()
    bc2 = RecyclingChannelBC(nw, 0.60, 8.80, 1.5, dx, lim, prescribe="streamwise")
    bc2.apply(x2, v2)
    assert np.array_equal(v2[:nw][moved][:, 1:], v0[:nw][moved][:, 1:])

    # 9. guards fire
    for bad in (dict(x_in=0.05, x_out=8.80), dict(x_in=0.60, x_out=9.41),
                dict(x_in=8.0, x_out=1.0)):
        try:
            RecyclingChannelBC(nw, bad["x_in"], bad["x_out"], 1.5, dx, lim)
        except ValueError:
            pass
        else:
            raise AssertionError("guard did not fire for %r" % bad)

    # 9b. inject_len spreads the arrivals instead of sheeting them onto one plane
    xA, vA = x0.copy(), v0.copy()
    bcA = RecyclingChannelBC(nw, 0.60, 8.80, 1.5, dx, lim)                  # default
    bcA.apply(xA, vA)
    xB, vB = x0.copy(), v0.copy()
    bcB = RecyclingChannelBC(nw, 0.60, 8.80, 1.5, dx, lim, inject_len=3.0 * dx, seed=7)
    bcB.apply(xB, vB)
    spread_default = float(xA[:nw][moved][:, 0].std())
    spread_band = float(xB[:nw][moved][:, 0].std())
    assert spread_band > 5.0 * spread_default, (spread_default, spread_band)
    assert (xB[:nw][moved][:, 0] >= 0.60).all()
    assert (xB[:nw][moved][:, 0] <= 0.60 + 3.0 * dx + 1e-6).all()
    # and the default is unchanged, so published numbers stay reproducible
    assert np.array_equal(xA, x), "default injection behaviour drifted"

    # 10. project_cross_stream never moves x
    x3, v3 = x0.copy(), v0.copy()
    bc3 = RecyclingChannelBC(nw, 0.60, 8.80, 1.5, dx, lim)
    bc3.project_cross_stream(x3, v3, y_lo=0.60, y_hi=8.80, z_floor=0.44)
    assert np.array_equal(x3[:, 0], x0[:, 0]), "project_cross_stream moved x"

    # 11. depth_profile flags a downstream pile-up and passes a flat surface
    flat = np.column_stack([np.linspace(1.0, 8.0, 4000),
                            np.full(4000, 4.0), np.full(4000, 0.74)])
    _, d_flat = depth_profile(flat, floor=0.44, x_lo=1.0, x_hi=8.0, n_bins=7)
    assert np.nanmax(d_flat) - np.nanmin(d_flat) < 1e-6, d_flat
    xs = np.linspace(1.0, 8.0, 4000)
    piled = np.column_stack([xs, np.full(4000, 4.0), 0.44 + 0.10 + 0.05 * xs])
    _, d_pile = depth_profile(piled, floor=0.44, x_lo=1.0, x_hi=8.0, n_bins=7)
    assert d_pile[-1] > d_pile[0] + 0.2, d_pile

    print("openchannel_bc selftest: 12 checks PASS")




class OverfallBC(RecyclingChannelBC):
    """Free-overfall recycling: the outflow trigger is a FALL, not a plane crossing.

    Zhao et al chose the free overfall as their stringent validation case because
    the bed level drops suddenly, and they report the end-depth ratio against
    Rouse, who found the critical depth is about 1.4x the brink depth (their own
    text, retrieved 2026-08-18 via Scite full-text search of
    doi:10.1016/j.compfluid.2018.10.007; the PDF itself was not retrievable).

    A particle that has fallen past `catch_z` is returned to the inlet. Everything
    else follows RecyclingChannelBC.

    THE (y, z) PRESERVATION ARGUMENT DOES NOT SURVIVE HERE, and pretending it does
    would be wrong. A particle in free fall past the brink carries J close to 1
    because nothing confines it, and it is re-injected into a water column whose
    head needs J of about 1.018 at 0.3 m depth (p = rho g h = 2943 Pa against
    bulk = 1.5e5). So re-injection introduces a pressure error of order 1.8
    percent. It is a TRANSIENT, not a bias: the acoustic time to cross 0.3 m at
    c = 12.85 m/s is 0.023 s, about 0.7 frames at 30 fps, so it relaxes almost
    immediately and cannot accumulate. It is recorded in the summary rather than
    hidden. F has no setter, so it cannot be corrected directly.
    """

    def __init__(self, n_water, x_in, catch_z, bed_top, inlet_velocity, dx, grid_lim,
                 x_brink, seed=0, prescribe="full"):
        # x_out is unreachable in overfall mode (the fall is the outflow), so it is
        # parked just inside the guard purely to satisfy the base-class validation.
        super().__init__(n_water=n_water, x_in=x_in, x_out=grid_lim - 2.6 * dx,
                         inlet_velocity=inlet_velocity, dx=dx, grid_lim=grid_lim,
                         prescribe=prescribe)
        self.catch_z = float(catch_z)
        self.bed_top = float(bed_top)
        self.x_brink = float(x_brink)
        self.rng = np.random.default_rng(seed)
        self.reinject_depth_last = float("nan")

    def apply(self, x, v):
        """Catch fallen water and return it to the inlet column."""
        nw = self.n_water
        w = x[:nw]
        fallen = w[:, 2] < self.catch_z
        n = int(fallen.sum())
        self.recycled_last = n
        if n == 0:
            return 0
        # Measure the live inlet column so re-injection matches the depth that
        # actually exists, rather than the nominal seeded depth.
        near = (w[:, 0] >= self.x_in) & (w[:, 0] < self.x_in + 6.0 * self.dx) & \
               (w[:, 2] >= self.bed_top)
        if int(near.sum()) >= 20:
            d = float(np.percentile(w[near, 2], 99.5)) - self.bed_top
        else:
            d = 4.0 * self.dx
        d = max(d, 2.0 * self.dx)
        self.reinject_depth_last = d
        x[:nw, 0][fallen] = self.x_in + self.rng.uniform(0.0, 2.0 * self.dx, n)
        x[:nw, 2][fallen] = self.bed_top + self.rng.uniform(0.05 * d, d, n)
        if self.prescribe == "full":
            v[:nw][fallen] = (self.inlet_velocity, 0.0, 0.0)
        else:
            v[:nw, 0][fallen] = self.inlet_velocity
        self.recycled_total += n
        return n


def overfall_metrics(xw, bed_top, x_brink, dx, width_m, q_m2_s, g=9.81):
    """Brink depth, critical depth and the Rouse ratio, from one frame.

    y_b is the free surface at the brink section, taken over the last half cell
    upstream of the brink so the sample sits on the bed rather than in the nappe.
    y_c = (q^2 / g)^(1/3) is the critical depth for a rectangular channel, with q
    the discharge PER UNIT WIDTH supplied by the caller from the recycling flux,
    which is an independent measurement from the free surface. Returns
    (y_b, y_c, y_c/y_b, froude_upstream) with NaN where the sample is too thin.
    """
    sel = (xw[:, 0] >= x_brink - 1.5 * dx) & (xw[:, 0] <= x_brink) & (xw[:, 2] >= bed_top)
    y_b = float(np.percentile(xw[sel, 2], 99.5)) - bed_top if int(sel.sum()) >= 20 else np.nan
    y_c = float((q_m2_s ** 2 / g) ** (1.0 / 3.0)) if q_m2_s > 0 else np.nan
    ratio = y_c / y_b if (np.isfinite(y_b) and np.isfinite(y_c) and y_b > 0) else np.nan
    up = (xw[:, 0] >= x_brink - 12.0 * dx) & (xw[:, 0] <= x_brink - 6.0 * dx) & \
         (xw[:, 2] >= bed_top)
    y_up = float(np.percentile(xw[up, 2], 99.5)) - bed_top if int(up.sum()) >= 20 else np.nan
    fr = (q_m2_s / y_up) / np.sqrt(g * y_up) if (np.isfinite(y_up) and y_up > 0) else np.nan
    return y_b, y_c, ratio, fr


def discharge_per_width(n_recycled, fps, h, width_m):
    """q = Q / b from the recycling flux. Each particle carries volume h^3, so
    Q = (particles per second) * h^3. This never reads the free surface, which is
    what makes the y_c it feeds independent of the y_b it is compared against."""
    return (float(n_recycled) * float(fps) * h ** 3) / float(width_m)


def _selftest_overfall():
    # Rouse: y_c is about 1.4x y_b. Build a surface that satisfies it exactly and
    # confirm the estimator recovers 1.4, so a later miss is physics, not algebra.
    g, q = 9.81, 0.30
    y_c = (q ** 2 / g) ** (1.0 / 3.0)
    y_b = y_c / 1.4
    bed, xbr, dx = 1.5, 2.6, 0.0625
    n = 4000
    xs = np.full(n, xbr - 0.25 * dx)
    zs = bed + np.linspace(0.0, y_b, n)
    pts = np.column_stack([xs, np.full(n, 1.0), zs])
    up = np.column_stack([np.full(n, xbr - 9.0 * dx), np.full(n, 1.0),
                          bed + np.linspace(0.0, 0.30, n)])
    allp = np.vstack([pts, up])
    yb, yc, r, fr = overfall_metrics(allp, bed, xbr, dx, width_m=3.5, q_m2_s=q)
    assert abs(r - 1.4) < 0.02, (yb, yc, r)
    assert abs(yc - y_c) < 1e-9
    qq = discharge_per_width(240, 30, 0.03125, 3.5)
    assert abs(qq - (240 * 30 * 0.03125 ** 3) / 3.5) < 1e-15
    assert 0.0 < fr < 1.0, fr          # the constructed approach flow is subcritical
    print("overfall selftest: 4 checks PASS (estimator recovers Rouse 1.4 exactly)")


def _selftest_overfall_bc():
    """Exercise the catch-and-reinject cycle on synthetic data, no solver needed.

    Written after the first three overfall runs drained themselves: every check
    here is something that failure would have shown, if it had been checked before
    the GPU time was spent rather than after.
    """
    dx, lim, bed, xbr = 0.041667, 4.0, 1.5, 2.6
    catch = bed - 0.7
    nw = 3000
    rng = np.random.default_rng(3)
    x = np.zeros((nw, 3), np.float32)
    # an inlet column 0.30 m deep sitting on the bed, plus a nappe past the brink
    n_col = 2000
    x[:n_col, 0] = rng.uniform(0.167, 0.167 + 6.0 * dx, n_col)
    x[:n_col, 1] = rng.uniform(1.6, 2.4, n_col)
    x[:n_col, 2] = rng.uniform(bed, bed + 0.30, n_col)
    x[n_col:, 0] = rng.uniform(xbr, xbr + 0.5, nw - n_col)
    x[n_col:, 1] = rng.uniform(1.6, 2.4, nw - n_col)
    x[n_col:, 2] = rng.uniform(0.2, bed, nw - n_col)      # some below catch, some above
    v = rng.normal(0, 0.4, (nw, 3)).astype(np.float32)
    x0, v0 = x.copy(), v.copy()

    bc = OverfallBC(n_water=nw, x_in=0.167, catch_z=catch, bed_top=bed,
                    inlet_velocity=0.7, dx=dx, grid_lim=lim, x_brink=xbr, seed=1)
    fallen = x0[:, 2] < catch
    n = bc.apply(x, v)
    assert n == int(fallen.sum()) and n > 50, (n, int(fallen.sum()))
    # 1. only the fallen moved
    assert np.array_equal(x[~fallen], x0[~fallen]), "a non-fallen particle was moved"
    # 2. reinjected inside the inlet band and ABOVE the bed, never inside it
    got = x[fallen]
    assert (got[:, 0] >= 0.167).all() and (got[:, 0] <= 0.167 + 2.0 * dx + 1e-6).all()
    assert (got[:, 2] > bed).all(), "a recycled particle was placed inside the bed"
    assert (got[:, 2] <= bed + 0.31).all(), got[:, 2].max()
    # 3. the measured inlet depth tracks the column that actually exists (0.30 m)
    assert 0.25 < bc.reinject_depth_last < 0.33, bc.reinject_depth_last
    # 4. velocity prescribed
    assert np.allclose(v[fallen], np.array([0.7, 0.0, 0.0], np.float32))
    # 5. y preserved even here, where z cannot be
    assert np.array_equal(x[fallen][:, 1], x0[fallen][:, 1]), "y was not preserved"
    # 6. count conserved and the pool never grows
    assert x.shape[0] == nw
    # 7. a second call must not re-recycle the same particles (they are now high)
    n2 = bc.apply(x, v)
    assert n2 == 0, "particles were recycled twice in one place"
    # 8. thin-column fallback: with almost no inlet water it must not divide by zero
    x2 = x0.copy(); v2 = v0.copy()
    x2[:n_col, 0] = 3.0                                   # empty the inlet band
    bc2 = OverfallBC(nw, 0.167, catch, bed, 0.7, dx, lim, xbr, seed=2)
    bc2.apply(x2, v2)
    assert np.isfinite(bc2.reinject_depth_last) and bc2.reinject_depth_last > 0
    print("overfall BC selftest: 8 checks PASS (catch, reinject above the bed, no double-recycle)")




class ReservePool:
    """A spare particle pool, so inflow can differ from outflow.

    WHY THIS EXISTS. Register item 30: every overfall configuration decays to
    q_last/q_first of 0.25 to 0.29, near-identically across grade, bed friction and
    grid, because one-in-one-out recycling fixes the total water and makes the
    channel its own only reservoir. Zhao et al 2019's UNIFORM channel case is
    expressible that way; their NON-UNIFORM case is not, and a free overfall is
    non-uniform. This module said so in its first commit. This class is the missing
    piece.

    HOW. Particles [n_water, n_water + n_reserve) are held out of the flow, parked
    in a compact block and PINNED every tick (position reset, velocity zeroed).
    Drawing from the pool activates particles at the inlet; retiring returns them to
    the park. Inflow and outflow are then independently controlled and the pool
    absorbs the difference.

    THE HONEST PROBLEM, AND THE CONTROL THAT TESTS IT. Particle volume is fixed at
    load, so a parked particle still carries h^3 of fluid and still deposits mass on
    the grid where it sits. There is nowhere in a warpmpm domain that is truly
    outside the simulation: the grid-edge guard forbids parking near the boundary
    (solver.py:_update_grid_box), and parking below the floor or outside the walls
    still writes to nodes. So the park is placed far from the wetted region and
    pinned, and the claim that it is inert is TESTED, not assumed:

        a reserve that is never drawn from must reproduce the no-reserve run.

    `sim_overfall.py --reserve N --reserve-hold` runs exactly that control. If the
    held run and the baseline disagree, the park is not inert and this design fails.
    Do not report a reserve-pool result without having run the control.

    J, again. An activated particle carries whatever J its parked history produced,
    which for a pinned particle at rest is near hydrostatic-free. It is injected into
    a column that wants J for the local head. Same transient as OverfallBC, same
    reason (F has no setter), same order: about 1.8 percent at 0.3 m of head,
    relaxing in under a frame.
    """

    def __init__(self, n_water, n_reserve, park_lo, park_hi, dx, grid_lim, seed=0):
        if n_reserve < 0:
            raise ValueError("n_reserve must be >= 0")
        park_lo = np.asarray(park_lo, dtype=np.float64)
        park_hi = np.asarray(park_hi, dtype=np.float64)
        if (park_lo < 2.0 * dx).any() or (park_hi > grid_lim - 3.0 * dx).any():
            raise ValueError(
                "park box %s..%s violates the P2G edge guard for dx=%.4f, lim=%.4f; "
                "the engine raises if any particle is within 1.5 dx of the grid edge"
                % (park_lo, park_hi, dx, grid_lim))
        self.n_water = int(n_water)
        self.n_reserve = int(n_reserve)
        self.lo = self.n_water
        self.hi = self.n_water + self.n_reserve
        self.park_lo, self.park_hi = park_lo, park_hi
        self.rng = np.random.default_rng(seed)
        # active[i] True means reserve particle i is in the flow, not parked
        self.active = np.zeros(self.n_reserve, dtype=bool)
        self.park_xyz = None
        self.drawn_total = 0
        self.retired_total = 0
        self.starved_total = 0          # ticks where the pool could not meet demand

    @property
    def n_parked(self):
        return int((~self.active).sum())

    @property
    def n_active(self):
        return int(self.active.sum())

    def build_park(self):
        """Fixed park coordinates, one slot per reserve particle, on a lattice."""
        n = self.n_reserve
        if n == 0:
            self.park_xyz = np.zeros((0, 3), np.float32)
            return self.park_xyz
        span = self.park_hi - self.park_lo
        side = max(int(np.ceil(n ** (1.0 / 3.0))), 1)
        g = [np.linspace(self.park_lo[k] + span[k] / (2 * side),
                         self.park_hi[k] - span[k] / (2 * side), side) for k in range(3)]
        pts = np.stack(np.meshgrid(*g, indexing="ij"), -1).reshape(-1, 3)[:n]
        if len(pts) < n:                      # ceil can undershoot by rounding
            pts = np.vstack([pts, np.repeat(pts[-1:], n - len(pts), axis=0)])
        self.park_xyz = pts.astype(np.float32)
        return self.park_xyz

    def pin_parked(self, x, v):
        """Hold every parked particle still. Call once per tick, before stepping."""
        if self.n_reserve == 0:
            return 0
        if self.park_xyz is None:
            self.build_park()
        idx = np.flatnonzero(~self.active)
        if idx.size:
            x[self.lo + idx] = self.park_xyz[idx]
            v[self.lo + idx] = 0.0
        return int(idx.size)

    def draw(self, k, x, v, x_lo, x_hi, y_lo, y_hi, z_lo, z_hi, velocity):
        """Activate up to k parked particles into the given inlet box.

        Returns the number actually activated, which is less than k when the pool
        is empty; that shortfall is counted in starved_total rather than hidden,
        because a silently starved inlet looks exactly like a physical result.
        """
        if self.n_reserve == 0 or k <= 0:
            return 0
        idx = np.flatnonzero(~self.active)
        take = min(int(k), idx.size)
        if take < int(k):
            self.starved_total += int(k) - take
        if take == 0:
            return 0
        sel = idx[:take]
        g = self.lo + sel
        x[g, 0] = self.rng.uniform(x_lo, x_hi, take)
        x[g, 1] = self.rng.uniform(y_lo, y_hi, take)
        x[g, 2] = self.rng.uniform(z_lo, z_hi, take)
        v[g] = (float(velocity), 0.0, 0.0)
        self.active[sel] = True
        self.drawn_total += take
        return take

    def retire_where(self, x, predicate_z_below=None, predicate_x_beyond=None):
        """Return active particles that have left the domain of interest to the park.

        Retirement is by the SAME test the outflow uses, so a particle is never
        counted as both outflowing and still in the channel.
        """
        if self.n_reserve == 0:
            return 0
        act = np.flatnonzero(self.active)
        if act.size == 0:
            return 0
        g = self.lo + act
        gone = np.zeros(act.size, dtype=bool)
        if predicate_z_below is not None:
            gone |= x[g, 2] < predicate_z_below
        if predicate_x_beyond is not None:
            gone |= x[g, 0] >= predicate_x_beyond
        n = int(gone.sum())
        if n:
            self.active[act[gone]] = False
            self.retired_total += n
        return n


def _selftest_reserve():
    dx, lim = 0.04167, 4.0
    nw, nr = 500, 300
    x = np.zeros((nw + nr, 3), np.float32)
    x[:nw, 2] = 1.6
    v = np.zeros((nw + nr, 3), np.float32)
    lo = np.array([3.0, 0.3, 0.3]); hi = np.array([3.7, 1.0, 1.0])
    p = ReservePool(nw, nr, lo, hi, dx, lim, seed=1)
    p.build_park()
    # 1. the park respects the P2G edge guard and its own box
    assert (p.park_xyz >= lo - 1e-6).all() and (p.park_xyz <= hi + 1e-6).all()
    assert (p.park_xyz >= 2.0 * dx).all() and (p.park_xyz <= lim - 3.0 * dx).all()
    # 2. a park box that violates the guard is refused
    try:
        ReservePool(nw, nr, [0.01, 0.3, 0.3], hi, dx, lim)
    except ValueError:
        pass
    else:
        raise AssertionError("guard-violating park box was accepted")
    # 3. pinning holds every parked particle and touches no water
    x0 = x.copy()
    n_pin = p.pin_parked(x, v)
    assert n_pin == nr and np.array_equal(x[:nw], x0[:nw])
    assert np.allclose(x[nw:], p.park_xyz) and not v[nw:].any()
    # 4. drawing activates exactly k and places them in the inlet box
    k = p.draw(120, x, v, 0.2, 0.3, 1.5, 2.5, 1.5, 1.8, velocity=0.5)
    assert k == 120 and p.n_active == 120 and p.n_parked == nr - 120
    g = p.lo + np.flatnonzero(p.active)
    assert (x[g, 0] >= 0.2).all() and (x[g, 0] <= 0.3).all()
    assert (x[g, 2] >= 1.5).all() and (x[g, 2] <= 1.8).all()
    assert np.allclose(v[g], np.array([0.5, 0.0, 0.0], np.float32))
    # 5. pinning after a draw leaves the ACTIVE ones alone
    before = x[g].copy()
    p.pin_parked(x, v)
    assert np.allclose(x[g], before), "pin_parked moved an active particle"
    # 6. retirement by the outflow test returns them and is counted
    x[g[:40], 2] = 0.5
    n_ret = p.retire_where(x, predicate_z_below=0.8)
    assert n_ret == 40 and p.n_active == 80, (n_ret, p.n_active)
    # 7. starvation is counted, not hidden
    p2 = ReservePool(nw, 10, lo, hi, dx, lim)
    p2.build_park()
    got = p2.draw(50, x, v, 0.2, 0.3, 1.5, 2.5, 1.5, 1.8, 0.5)
    assert got == 10 and p2.starved_total == 40, (got, p2.starved_total)
    # 8. a zero-size pool is a no-op everywhere, so --reserve 0 is a true baseline
    p3 = ReservePool(nw, 0, lo, hi, dx, lim)
    assert p3.pin_parked(x, v) == 0 and p3.draw(5, x, v, 0, 1, 0, 1, 0, 1, 1.0) == 0
    assert p3.retire_where(x, predicate_z_below=99.0) == 0
    print("reserve pool selftest: 8 checks PASS")


# ---------------------------------------------------------------------------
# FORWARD-COMPATIBILITY PARITY WITH THE ANCESTOR BLOB
# ---------------------------------------------------------------------------
# WHY THIS SECTION EXISTS. This module was committed twice from one lineage, not
# written twice. Blob 9a94e247c4a2fb674b5c8dda5fcc571a39a2f35b appears in BOTH
# be1b138 (branch claude/add-ci-checks, the commit that added the file) and
# 5ecf725 (branch claude/r7-inflow), byte for byte, verified by `git ls-tree`.
# The vehicle-scene inflow result on claude/r7-inflow was measured against that
# ancestor blob and its manifests stamp its sha256 as provenance. This branch's
# copy is the evolved blob 70946f61e759adc01cb78e2cc166f7739af4f579, four commits
# later, which added OverfallBC, overfall_metrics, discharge_per_width and
# ReservePool and touched five places inside RecyclingChannelBC.
#
# The two never diverged in lineage but they HAVE diverged in time, and nothing
# in the repo enforced that the older result still describes the newer code. This
# section is that enforcement: it pins, by digest, the behaviour of the exact API
# surface claude/r7-inflow exercised, measured from the ancestor blob itself.
#
# The surface was read from claude/r7-inflow:scripts/inflow_vehicle_wrapper.py,
# not assumed: keyword construction (:282-285), subclassing with a super().apply
# delegate (:200-219), .apply per frame (:306), .recycled_total (:573),
# .max_overshoot (:575), and depth_profile (:339). project_cross_stream is NOT in
# that surface, the wrapper uses its own clamp_box (:319), so it is digested here
# under a separate key and labelled.
#
# IF A FUTURE EDIT BREAKS THIS TEST, that is the intended outcome, not a bug in
# the test. It means the change moved the default path, and therefore that the
# r7 vehicle-scene numbers no longer describe this module. Either keep the change
# behind a non-default argument, as inject_len already is, or re-run r7's grid and
# supersede its result explicitly.
ANCESTOR_BLOB = "9a94e247c4a2fb674b5c8dda5fcc571a39a2f35b"
CURRENT_LINEAGE_BLOB = "70946f61e759adc01cb78e2cc166f7739af4f579"


def _sha(a):
    """Stable digest of an array's bytes, NaN payloads normalised.

    hashlib is imported here rather than at module top so that everything above
    this section stays byte-identical to CURRENT_LINEAGE_BLOB and a diff against
    claude/add-ci-checks shows only this block and the __all__ line.
    """
    import hashlib
    b = np.ascontiguousarray(a)
    if b.dtype.kind == "f":
        b = np.ascontiguousarray(np.where(np.isnan(b), np.float64(-1.0e30), b))
    return hashlib.sha256(b.tobytes()).hexdigest()[:16]


def _parity_fixture():
    """Deterministic fixture. NO RNG, deliberately.

    Every value is an integer scaled by a dyadic constant, so the float64
    intermediates and the float32 cast are bit-exact on any IEEE-754 platform.
    A fixture built from default_rng would tie these digests to numpy's random
    stream and turn a numpy upgrade into a false parity failure.

    THE FIXTURE MUST DO WORK. 103 of the 512 water rows start past the outflow
    plane, y reaches outside the channel on both sides, and z straddles the bed.
    The ancestor blob's own _selftest is the cautionary case: it drew x from
    uniform(0.6, 8.8) against an outflow plane at 8.80, numpy's uniform is half
    open, so it recycled 0 particles and reported "11 checks PASS" anyway.
    Measured live 2026-08-18: n = 0, max water x = 8.777121543884277.
    """
    nw, nveh = 512, 37
    n = nw + nveh
    i = np.arange(n, dtype=np.float64)
    x = np.zeros((n, 3), dtype=np.float32)
    x[:, 0] = (0.625 + (i % 256) * 0.03125).astype(np.float32)      # 0.625 .. 8.594
    x[:, 1] = (0.400 + (i % 384) * 0.0234375).astype(np.float32)    # 0.400 .. 9.377
    x[:, 2] = (0.300 + (i % 128) * 0.00390625).astype(np.float32)   # 0.300 .. 0.796
    # Push every fifth WATER row past the outflow plane by a realistic overshoot.
    # 0.0125 to 0.0713 m brackets the 0.0425 m max_overshoot the g64 runs measured,
    # so the recycler is exercised at the magnitude it actually sees, not flattered
    # by a tiny one or stressed by an unphysical one.
    k = np.arange(0, nw, 5)
    x[k, 0] = (8.8125 + (k % 16) * 0.00390625).astype(np.float32)
    v = np.zeros((n, 3), dtype=np.float32)
    v[:, 0] = (((i % 17) - 8.0) * 0.125).astype(np.float32)
    v[:, 1] = (((i % 13) - 6.0) * 0.0625).astype(np.float32)
    v[:, 2] = (((i % 7) - 3.0) * 0.25).astype(np.float32)
    return nw, nveh, x, v


def _parity_digest(bc_cls, depth_profile_fn, inject_len=None):
    """Digest the ancestor-exercised surface. Class and function are INJECTED.

    Injecting them is the whole point: the identical driver code below can be run
    against a different module object (the ancestor blob loaded from git) without
    copying the fixture into a second file where the two could silently drift.
    """
    nw, nveh, x0, v0 = _parity_fixture()
    kw = dict(n_water=nw, x_in=0.60, x_out=8.80, inlet_velocity=1.5,
              dx=0.147, grid_lim=9.42)
    if inject_len is not None:
        kw["inject_len"] = inject_len
    out = {}

    # A. the r7 path, prescribe="full", one tick
    x, v = x0.copy(), v0.copy()
    bc = bc_cls(prescribe="full", **kw)
    out["A_n"] = int(bc.apply(x, v))
    out["A_x"] = _sha(x)
    out["A_v"] = _sha(v)
    out["A_recycled_total"] = int(bc.recycled_total)
    out["A_max_overshoot"] = repr(float(bc.max_overshoot))

    # B. ten further ticks with a deterministic advection between them. r7 called
    #    apply once per frame for a 200-frame horizon, so a single tick cannot see
    #    state that accumulates across ticks (recycled_total, max_overshoot) or a
    #    particle recycled more than once.
    for _ in range(10):
        x[:nw, 0] += np.float32(0.35)
        bc.apply(x, v)
    out["B_x"] = _sha(x)
    out["B_v"] = _sha(v)
    out["B_recycled_total"] = int(bc.recycled_total)
    out["B_recycled_last"] = int(bc.recycled_last)
    out["B_max_overshoot"] = repr(float(bc.max_overshoot))

    # C. prescribe="streamwise", the other branch of the velocity write
    x, v = x0.copy(), v0.copy()
    bc2 = bc_cls(prescribe="streamwise", **kw)
    out["C_n"] = int(bc2.apply(x, v))
    out["C_x"] = _sha(x)
    out["C_v"] = _sha(v)

    # D. depth_profile, the only other name r7 imports
    x, v = x0.copy(), v0.copy()
    edges, depths = depth_profile_fn(x[:nw], floor=0.44, x_lo=0.60, x_hi=8.80,
                                     n_bins=12, pct=99.5, min_count=20)
    out["D_edges"] = _sha(np.asarray(edges, dtype=np.float64))
    out["D_depths"] = _sha(np.asarray(depths, dtype=np.float64))

    # F. the n == 0 early return. Nothing crosses, so apply must return 0 and leave
    #    both arrays untouched. Not reachable from the A/B/C fixtures, which all
    #    cross, and an untested early return is where a refactor hides.
    #    It applies a CROSSING tick first, then the empty one, because a fresh
    #    instance reports recycled_last == 0 whether or not the empty path resets
    #    it. Only the sequence can tell the difference, and the per-frame counter
    #    r7 records is read after exactly this kind of sequence.
    x, v = x0.copy(), v0.copy()
    bcF = bc_cls(prescribe="full", **kw)
    bcF.apply(x, v)
    x[:nw, 0] = np.float32(1.0)
    out["F_n"] = int(bcF.apply(x, v))
    out["F_x"] = _sha(x)
    out["F_v"] = _sha(v)
    out["F_recycled_last"] = int(bcF.recycled_last)
    out["F_recycled_total"] = int(bcF.recycled_total)

    # G. the np.mod guard, for an overshoot LARGER than the channel. Synthetic: no
    #    solver would produce it in one tick, which is exactly why it is the branch
    #    nobody would notice breaking. Without the modulo the particle lands past
    #    x_out again and is recycled forever inside one call.
    x, v = x0.copy(), v0.copy()
    x[0, 0] = np.float32(8.80 + 1.3 * (8.80 - 0.60))
    bcG = bc_cls(prescribe="full", **kw)
    out["G_n"] = int(bcG.apply(x, v))
    out["G_x0"] = repr(float(x[0, 0]))
    out["G_x"] = _sha(x)
    out["G_max_overshoot"] = repr(float(bcG.max_overshoot))

    # E. project_cross_stream. NOT part of the r7 surface, kept separate so a
    #    change here can never be mistaken for a change to what r7 ran.
    x, v = x0.copy(), v0.copy()
    bc3 = bc_cls(prescribe="full", **kw)
    out["E_n"] = int(bc3.project_cross_stream(x, v, y_lo=0.60, y_hi=8.80,
                                              z_floor=0.44))
    out["E_x"] = _sha(x)
    out["E_v"] = _sha(v)
    return out


# Measured 2026-08-18 by running _parity_digest against the ANCESTOR blob itself,
# loaded from `git show be1b138:simulation/openchannel_bc.py`, with this module's
# fixture and driver. Regenerate only by re-running that comparison, never by
# pasting what the current module happens to produce, which would make the test
# assert that the code equals itself.
ANCESTOR_PARITY = {
    'A_max_overshoot': '0.07109355926513672',
    'A_n': 103,
    'A_recycled_total': 103,
    'A_v': '438c8774d1f3a8fd',
    'A_x': '4060b0ffa9d8ef4f',
    'B_max_overshoot': '0.3437509536743164',
    'B_recycled_last': 17,
    'B_recycled_total': 272,
    'B_v': 'dfdaf31e1adf231d',
    'B_x': '349df16168912eb3',
    'C_n': 103,
    'C_v': 'ecf7c65c2655aec4',
    'C_x': '4060b0ffa9d8ef4f',
    'D_depths': 'd7ebf9098530e7a7',
    'D_edges': 'fe3a0270c6e26f4a',
    'E_n': 187,
    'E_v': '1053d8c8827c6ce6',
    'E_x': '62c0d118e7bb0134',
    'F_n': 0,
    'F_recycled_last': 0,
    'F_recycled_total': 103,
    'F_v': '438c8774d1f3a8fd',
    'F_x': 'da7f1a135ab494c1',
    'G_max_overshoot': '10.659998893737793',
    'G_n': 103,
    'G_x': 'd8061ac5458f9f1f',
    'G_x0': '3.0599989891052246',
}


def _selftest_ancestor_parity():
    got = _parity_digest(RecyclingChannelBC, depth_profile)

    # 0. the fixture does work. Without this the rest can pass vacuously, which is
    #    exactly how the ancestor's own selftest came to report PASS on 0 particles.
    assert got["A_n"] == 103, ("fixture recycles nothing", got["A_n"])
    assert got["B_recycled_total"] > got["A_recycled_total"], got
    assert got["E_n"] > 0, ("cross-stream fixture never violates a wall", got["E_n"])
    assert got["F_n"] == 0, ("F block was meant to exercise the empty early return",
                             got["F_n"])
    # G must genuinely enter the modulo branch: an overshoot SHORTER than the
    # channel would take the same arithmetic path as A and test nothing new.
    assert float(got["G_max_overshoot"]) > (8.80 - 0.60), got["G_max_overshoot"]

    # 1. every digested key matches the ancestor blob, key by key so a failure
    #    names WHICH behaviour moved rather than just "something did"
    missing = sorted(set(ANCESTOR_PARITY) - set(got))
    extra = sorted(set(got) - set(ANCESTOR_PARITY))
    assert not missing and not extra, (missing, extra)
    bad = {k: (ANCESTOR_PARITY[k], got[k]) for k in ANCESTOR_PARITY
           if ANCESTOR_PARITY[k] != got[k]}
    assert not bad, ("default path diverged from ancestor blob %s: %r"
                     % (ANCESTOR_BLOB[:8], bad))

    # 2. ANTI-VACUITY. The parity above is only meaningful if this fixture can
    #    detect a change at all. inject_len is the one added parameter that moves
    #    the default path's line, so with it set the digest MUST differ.
    band = _parity_digest(RecyclingChannelBC, depth_profile, inject_len=3 * 0.147)
    assert band["A_x"] != got["A_x"], "inject_len changed nothing, test is blind"
    assert band["A_n"] == got["A_n"], "inject_len must not change WHICH particles move"
    assert band["A_v"] == got["A_v"], "inject_len must not touch velocity"

    # 3. the added counters are inert on the ancestor surface: they record, they
    #    never feed back into a position, a velocity or a return value
    nw, _, x0, v0 = _parity_fixture()
    bc = RecyclingChannelBC(n_water=nw, x_in=0.60, x_out=8.80, inlet_velocity=1.5,
                            dx=0.147, grid_lim=9.42)
    assert bc.clamped_y == 0 and bc.clamped_z == 0
    x, v = x0.copy(), v0.copy()
    n = bc.project_cross_stream(x, v, y_lo=0.60, y_hi=8.80, z_floor=0.44)
    assert bc.clamped_y > 0 and bc.clamped_z > 0, (bc.clamped_y, bc.clamped_z)
    assert bc.clamped_y + bc.clamped_z == n, (bc.clamped_y, bc.clamped_z, n)

    print("ancestor parity selftest: 7 checks PASS "
          "(default path bit-identical to blob %s)" % ANCESTOR_BLOB[:8])


if __name__ == "__main__":
    _selftest()
    _selftest_overfall()
    _selftest_overfall_bc()
    _selftest_reserve()
    _selftest_ancestor_parity()
