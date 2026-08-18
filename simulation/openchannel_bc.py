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

__all__ = ["RecyclingChannelBC", "depth_profile", "tilted_gravity"]


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
                 prescribe="full"):
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
        self.recycled_total = 0
        self.recycled_last = 0
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
        x[:nw, 0][crossed] = self.x_in + np.mod(overshoot, L)
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
    x[:, 0] = rng.uniform(0.6, 8.8, nw + nveh)
    x[:, 1] = rng.uniform(0.6, 8.8, nw + nveh)
    x[:, 2] = rng.uniform(0.45, 0.75, nw + nveh)
    v = rng.normal(0, 0.3, (nw + nveh, 3)).astype(np.float32)
    x0, v0 = x.copy(), v.copy()

    bc = RecyclingChannelBC(n_water=nw, x_in=0.60, x_out=8.80,
                            inlet_velocity=1.5, dx=dx, grid_lim=lim)
    n = bc.apply(x, v)
    moved = x0[:nw, 0] >= 8.80
    assert n == int(moved.sum()), (n, int(moved.sum()))
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

    print("openchannel_bc selftest: 11 checks PASS")


if __name__ == "__main__":
    _selftest()
