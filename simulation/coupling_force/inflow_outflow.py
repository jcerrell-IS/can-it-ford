#!/usr/bin/env python3
"""Zhao et al. 2019 in/outflow BCs for warpmpm: inlet IMPLEMENTED, outflow SUBSTITUTED.

Written 2026-08-12. Status: CPU reference implementation, analytically self-tested.
NOT run against the GPU solver. No gated run uses it. Do not cite as validated.

Source BC paper, per register and CLAUDE.md (NOT Kumar, corrected 2026-08-07):
  Zhao, Bolognin, Liang, Rohe and Vardon 2019, Computers & Fluids 179, 27-33,
  doi:10.1016/j.compfluid.2018.10.007. Implemented by them in Anura3D. Porting it
  here is a TRANSLATION, not a port (register J8).

WHY THE OUTFLOW HALF CANNOT BE PORTED, AND IS NOT ATTEMPTED
===========================================================
Zhao et al.'s outflow is PRESSURE-CONTROLLED. Register B7, verified live:
`grep -ci pressure kernels/mpm_solver_warp.py` returns 0 across 3,181 lines at
pinned SHA 544c93dd. There is NO pressure field in warpmpm at any point. Pressure
exists only implicitly, per particle, via J = det(F) and bulk_modulus inside the
weakly-compressible EOS. A literal port would have to Dirichlet-constrain a field
that does not exist. The brief says not to attempt one, the register says the same,
and this file does not. **Never describe a warpmpm outflow BC as pressure-controlled.**

THE SUBSTITUTE, AND THE ENGINE CONSTRAINT THAT PICKED IT
========================================================
Constraint, from CLAUDE.md item 2 / register F5: particle count is FIXED AT LOAD
(sim_standing.py:126) and no particle is created or destroyed during a run. So a
naive inlet that injects particles and an outlet that deletes them is not
expressible without changing the allocation, which would fork every gated run.

The substitute is therefore a RECYCLING CONVEYOR, and the pairing is what makes it
work: the outlet does not delete a particle, it RETIRES it, and the inlet does not
create one, it REISSUES a retired particle at the upstream face. Particle count is
conserved exactly, the allocation never changes, and mass is conserved to within
the retired-pool occupancy. Two keys are offered for retirement, as instructed:

  POSITION-KEYED  retire when x > x_out. Simple, and the honest default.
  DEPTH-KEYED     retire when x > x_out AND z > target free-surface height. This is
                  the register's own recommended re-expression of Zhao's pressure
                  control (B7: "a depth-controlled outflow, deactivating particles
                  above a target free-surface height"). It is what actually
                  addresses the measured defect below.

WHY THIS MATTERS FOR THE PROJECT, MEASURED NOT ASSERTED
=======================================================
REALISM_UPGRADE_ASSESSMENT_2026-08-08 section 4 measured the bounded tank: water
surface at the downstream wall rises 0.2729 -> 0.6750 m by mid-run, a 2.5x
pile-up, and only 20 of 90 frames sit within +/-10% of the nominal 0.30 m depth.
The vehicle spends 78% of the run at a depth that is not the labelled depth. The
streamwise fetch is 2.2 hull-lengths. A working outflow is the fix for exactly
that, which is why this is worth building rather than a formality.
"""
from __future__ import annotations

import numpy as np

__all__ = ["InletBC", "OutflowRetirement", "RecyclingConveyor"]


class InletBC:
    """Velocity-controlled inlet: the Zhao et al. 2019 half that DOES translate.

    Zhao et al. prescribe velocity on the inflow boundary. warpmpm has no grid
    boundary-condition machinery for this (register C8 records the same absence in
    Genesis), so it is applied at PARTICLE level on a slab at the upstream face,
    which is the same mechanism the gated driver already uses for its Dirichlet
    clamp (sim_standing.py:190-198, register F5).

    The difference from the existing clamp is the point of the exercise. The
    existing clamp OVERWRITES the velocity of whatever particles happen to sit in
    the slab, every frame, forever: it is a treadmill, and it neither adds mass nor
    sustains a discharge. This inlet issues particles that then advect away freely,
    so the upstream condition is a FLUX rather than a velocity stencil.
    """

    def __init__(self, x_in, slab_thickness, y_span, z_span, velocity,
                 rho=1000.0, profile="uniform"):
        if slab_thickness <= 0:
            raise ValueError("slab_thickness must be positive")
        if profile not in ("uniform", "loglaw"):
            raise ValueError("profile must be 'uniform' or 'loglaw'")
        self.x_in = float(x_in)
        self.slab = float(slab_thickness)
        self.y_span = tuple(float(v) for v in y_span)
        self.z_span = tuple(float(v) for v in z_span)
        self.velocity = float(velocity)
        self.rho = float(rho)
        self.profile = profile

    def area(self):
        """Wetted inflow area, m2."""
        return (self.y_span[1] - self.y_span[0]) * (self.z_span[1] - self.z_span[0])

    def discharge(self):
        """Volumetric discharge Q = U * A, m3/s. Units check: m/s * m2 = m3/s."""
        return self.velocity * self.area()

    def mass_flux(self):
        """Mass flux rho * Q, kg/s."""
        return self.rho * self.discharge()

    def particles_per_step(self, particle_volume, dt):
        """How many particles the inlet must issue per step to sustain Q.

        n = Q * dt / v_p. Returned as an exact float; the caller accumulates the
        fractional remainder rather than rounding every step, or the realised
        discharge drifts low by up to one particle per step.
        """
        if particle_volume <= 0:
            raise ValueError("particle_volume must be positive")
        return self.discharge() * float(dt) / float(particle_volume)

    def velocity_at(self, z):
        """Inlet velocity profile.

        'uniform' matches how the gated runs are posed and is the default, so a
        comparison against them is not confounded by a profile change. 'loglaw' is
        offered but is NOT calibrated here: no roughness height for a flooded road
        is sourced anywhere in this repo, so using it would introduce an unsourced
        parameter. It raises rather than inventing one.
        """
        z = np.asarray(z, dtype=np.float64)
        if self.profile == "uniform":
            return np.full(z.shape, self.velocity)
        raise NotImplementedError(
            "log-law inlet needs a roughness height z0 for a flooded road surface. "
            "No value for that is sourced anywhere in this repo, and CLAUDE.md "
            "forbids writing an unsourced parameter into a script. Source it first.")

    def seed_positions(self, n, rng):
        """Uniformly seed n particles in the inlet slab."""
        n = int(n)
        x = rng.uniform(self.x_in, self.x_in + self.slab, n)
        y = rng.uniform(self.y_span[0], self.y_span[1], n)
        z = rng.uniform(self.z_span[0], self.z_span[1], n)
        return np.stack([x, y, z], axis=1)


class OutflowRetirement:
    """The pressure-controlled-outflow SUBSTITUTE. Not a port. See module docstring.

    mode='position' : retire when x > x_out.
    mode='depth'    : retire when x > x_out AND z > z_target. This is register B7's
                      recommended re-expression: it bleeds off exactly the water
                      that constitutes the pile-up above the intended free surface,
                      instead of pretending to constrain a pressure.
    """

    def __init__(self, x_out, mode="depth", z_target=None):
        if mode not in ("position", "depth"):
            raise ValueError("mode must be 'position' or 'depth'")
        if mode == "depth" and z_target is None:
            raise ValueError("mode='depth' requires z_target, the intended "
                             "free-surface height in metres")
        self.x_out = float(x_out)
        self.mode = mode
        self.z_target = None if z_target is None else float(z_target)

    def select(self, pos):
        """Boolean mask of particles to retire this step."""
        pos = np.asarray(pos, dtype=np.float64).reshape(-1, 3)
        past = pos[:, 0] > self.x_out
        if self.mode == "position":
            return past
        return past & (pos[:, 2] > self.z_target)


class RecyclingConveyor:
    """Couples the two so particle count is conserved EXACTLY.

    active[i] is False for a retired particle. A retired particle holds its slot in
    the allocation, so n_particles never changes and the solver's arrays are never
    reallocated. That is the property that lets this coexist with a fixed-count
    engine instead of forking it.

    HONEST LIMITATION, stated because it will otherwise be discovered later: while
    a particle sits retired it is mass that has left the domain. If the retired
    pool is non-empty on average, the domain carries less water than the initial
    condition implies. The occupancy is reported by `retired_fraction()` and any
    run using this must publish it, exactly as `water_layers` is published now.
    """

    def __init__(self, inlet: InletBC, outflow: OutflowRetirement, n_particles,
                 particle_volume, seed=0):
        self.inlet = inlet
        self.outflow = outflow
        self.n = int(n_particles)
        self.particle_volume = float(particle_volume)
        self.active = np.ones(self.n, dtype=bool)
        self.rng = np.random.default_rng(seed)
        self._pending = 0.0
        self.retired_total = 0
        self.reissued_total = 0

    def retired_fraction(self):
        return 1.0 - float(self.active.mean())

    def step(self, pos, vel, dt):
        """Retire what has left, reissue as many as the discharge supports.

        Returns (pos, vel, n_retired, n_reissued). Order matters: retire FIRST, so
        a particle that leaves this step is available to be reissued this step.
        """
        pos = np.asarray(pos, dtype=np.float64).copy()
        vel = np.asarray(vel, dtype=np.float64).copy()

        leaving = self.outflow.select(pos) & self.active
        self.active[leaving] = False
        n_ret = int(leaving.sum())
        self.retired_total += n_ret

        self._pending += self.inlet.particles_per_step(self.particle_volume, dt)
        want = int(np.floor(self._pending))
        idle = np.flatnonzero(~self.active)
        n_iss = int(min(want, idle.size))
        if n_iss > 0:
            take = idle[:n_iss]
            pos[take] = self.inlet.seed_positions(n_iss, self.rng)
            v = np.zeros((n_iss, 3))
            v[:, 0] = self.inlet.velocity_at(pos[take][:, 2])
            vel[take] = v
            self.active[take] = True
            self._pending -= n_iss
            self.reissued_total += n_iss
        return pos, vel, n_ret, n_iss


if __name__ == "__main__":
    print("inflow_outflow self-test")
    print("-" * 62)
    # Canonical g64 geometry, register / all_runs_inventory: lim 9.4217 m,
    # dx 0.1472147236519959, realized depth 0.2944294473039918 (= exactly 2 dx).
    lim, dx, depth, U = 9.4217, 0.1472147236519959, 0.2944294473039918, 1.5
    inlet = InletBC(x_in=0.0, slab_thickness=3.0 * dx, y_span=(0.0, lim),
                    z_span=(3.0 * dx, 3.0 * dx + depth), velocity=U)
    A, Q = inlet.area(), inlet.discharge()
    print("inlet area      : %.6f m2   (span %.4f m x depth %.6f m)" % (A, lim, depth))
    print("discharge Q     : %.6f m3/s  (units: m/s * m2 = m3/s)" % Q)
    print("mass flux       : %.4f kg/s" % inlet.mass_flux())
    assert abs(A - lim * depth) < 1e-12
    assert abs(Q - U * A) < 1e-12

    h = 0.5 * dx                      # particle spacing, h = dx/2
    vp = h ** 3
    dt = 1.0 / 30.0
    n_per = inlet.particles_per_step(vp, dt)
    print("particle volume : %.6e m3   (h = dx/2 = %.6f m)" % (vp, h))
    print("particles/step  : %.3f at dt = %.5f s" % (n_per, dt))

    # depth-keyed outflow must retire ONLY the pile-up above the target surface
    z_surf = 3.0 * dx + depth
    out = OutflowRetirement(x_out=lim - 3.0 * dx, mode="depth", z_target=z_surf)
    pos = np.array([
        [lim - 0.01, 0.0, z_surf + 0.20],   # past outlet AND above surface -> retire
        [lim - 0.01, 0.0, z_surf - 0.05],   # past outlet, below surface    -> keep
        [1.0,        0.0, z_surf + 0.20],   # above surface, not past outlet-> keep
    ])
    sel = out.select(pos)
    print("depth-keyed mask: %s   (expect [True, False, False])" % sel.tolist())
    assert sel.tolist() == [True, False, False]

    selp = OutflowRetirement(x_out=lim - 3.0 * dx, mode="position").select(pos)
    print("position-keyed  : %s   (expect [True, True, False])" % selp.tolist())
    assert selp.tolist() == [True, True, False]

    # conveyor conserves particle count exactly
    N = 5000
    conv = RecyclingConveyor(inlet, out, n_particles=N, particle_volume=vp)
    p = np.zeros((N, 3)); p[:, 0] = np.linspace(0.0, lim, N)
    p[:, 2] = z_surf + 0.10
    v = np.zeros((N, 3))
    tot_r = tot_i = 0
    for _ in range(20):
        p, v, r, i = conv.step(p, v, dt)
        tot_r += r; tot_i += i
        p[:, 0] += U * dt
    print("after 20 steps  : retired %d, reissued %d, array length %d (must stay %d)"
          % (tot_r, tot_i, len(p), N))
    print("retired fraction: %.4f  (MUST be published with any run using this)"
          % conv.retired_fraction())
    assert len(p) == N, "particle count changed; the fixed-count invariant is broken"

    try:
        InletBC(0.0, 0.1, (0, 1), (0, 1), 1.5, profile="loglaw").velocity_at([0.5])
    except NotImplementedError:
        print("loglaw profile  : REFUSED without a sourced z0, correct")
    else:
        raise AssertionError("loglaw returned an unsourced profile")

    print("-" * 62)
    print("ALL SELF-TESTS PASS. Inlet implemented; outflow is a DEPTH/POSITION-keyed")
    print("retirement SUBSTITUTE, never a pressure-controlled port (register B7).")
