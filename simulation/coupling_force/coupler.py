"""Force-based fluid-rigid coupling: a partitioned explicit FSI loop for warpmpm.

WHY THIS EXISTS
    The engine's free-rigid path (material 8) never forms a force. Per step it
    gathers the mass-weighted grid velocity at each rigid particle and assigns
    v_cm = rigid_linear_mom / M (kernels/mpm_utils.py:1434, with M from
    kernels/mpm_solver_warp.py:856). The body therefore ADOPTS a mass-weighted
    average of the surrounding grid velocity. No buoyant force is ever
    integrated, so density cannot drive motion. The 2026-08-08 multigeom runs
    show the consequence directly: Rogue and Silverado sit at realized densities
    of 324 and 294 kg/m3, roughly a third of water, and their C2_veh_zmin_rise
    is -0.0220 m and -0.0003 m. They do not rise at all.

WHAT THIS DOES INSTEAD
    warpmpm already accumulates a true reaction wrench for FIXED colliders:
    force = sum m (v_free - v_new) / dt and torque = sum (x - c) x impulse / dt,
    exposed as Solver.sdf_wrench (core/solver.py:354) with Solver.reset_sdf_force
    to zero the accumulators. The body is therefore carried as an SDF COLLIDER,
    not as material 8, and each tick:

        reset_sdf_force(h)                  zero the accumulators
        step(dt)                            MPM advances; impulse accumulates
        F, tau = sdf_wrench(h, dt)          read the real reaction wrench
        integrate(state, F, tau, dt)        Newton-Euler, M dv/dt = F + Mg
        set_sdf_pose(h, center, quat, ...)  feed the new pose back

    This is the standard partitioned (weakly coupled) explicit FSI scheme used
    for MPM water entry by Qian et al. 2022 and analysed for explicit MPM FSI
    stability by Zhang et al. 2026. Buoyancy is not modelled or prescribed
    anywhere in this file: it EMERGES as the resolved pressure integral over the
    wetted hull, which is the entire point.

WHAT THIS DOES NOT DO
    It does not modify the kinematic material-8 path. That code is untouched and
    still reachable; this is an additive module. It also does not claim implicit
    or monolithic coupling. A partitioned explicit scheme has a well known
    added-mass stability limit: as the displaced fluid mass approaches the body
    mass, the explicit update over-predicts and can diverge. That regime is
    exactly a near-neutrally-buoyant vehicle, so the limit is REPORTED (see
    added_mass_ratio) and an optional under-relaxation is available, rather than
    being papered over. Under-relaxation damps the transient; it does not change
    the equilibrium the body settles to.

REFERENCES
    Qian et al. (2022), water entry of a half-buoyant cylinder/box,
        Computer Methods in Applied Mechanics and Engineering.
    Zhang et al. (2026), stabilized explicit MPM for fluid-structure
        interaction, Computer Methods in Applied Mechanics and Engineering.
    A released-code search for both was run on 2026-08-12 and is recorded in
        README.md; nothing usable was located from this node.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .rigid_body import RigidBodyState, integrate, inertia_from_particles  # noqa: F401

RHO_WATER = 1000.0


@dataclass
class CouplingConfig:
    dt: float
    gravity: tuple = (0.0, 0.0, -9.81)
    relax: float = 1.0             # 1.0 = no under-relaxation
    substeps_per_pose: int = 1     # MPM steps between pose updates
    max_speed: float | None = 25.0
    max_omega: float | None = 25.0
    freeze_rotation: bool = False  # rung (b) can be run translation-only
    warn_added_mass: float = 0.5


@dataclass
class CouplingTrace:
    t: list = field(default_factory=list)
    force: list = field(default_factory=list)
    torque: list = field(default_factory=list)
    x_cm: list = field(default_factory=list)
    v_cm: list = field(default_factory=list)
    omega: list = field(default_factory=list)
    quat: list = field(default_factory=list)
    clamped: list = field(default_factory=list)

    def as_arrays(self):
        return {k: np.asarray(v) for k, v in self.__dict__.items() if k != "clamped"}


class ForceCoupledBody:
    """Drives one SDF collider as a free rigid body from the MPM reaction wrench.

    solver           a warpmpm Solver with the body already added via
                     add_sdf_collider; pass its handle.
    state            RigidBodyState. Its x_cm MUST match the collider centre the
                     solver was built with, or the first torque is taken about
                     the wrong point.
    """

    def __init__(self, solver, handle: int, state: RigidBodyState, cfg: CouplingConfig,
                 displaced_volume_m3: float | None = None):
        self.solver = solver
        self.handle = handle
        self.state = state
        self.cfg = cfg
        self.trace = CouplingTrace()
        self._t = 0.0
        self._prev_F = np.zeros(3)
        self._prev_T = np.zeros(3)
        self.displaced_volume_m3 = displaced_volume_m3
        self._warned = False

        for name in ("reset_sdf_force", "sdf_wrench", "set_sdf_pose"):
            if not hasattr(solver, name):
                raise AttributeError(
                    f"solver has no {name}; this engine build cannot supply a "
                    "collider reaction wrench, so force coupling is impossible"
                )

    # ------------------------------------------------------------------ checks
    def added_mass_ratio(self):
        """Displaced fluid mass / body mass. The partitioned explicit stability knob.

        Ratios approaching and exceeding 1 are where an explicit partitioned
        scheme is expected to struggle (Zhang et al. 2026). Returns None when the
        displaced volume was not supplied.
        """
        if self.displaced_volume_m3 is None:
            return None
        return RHO_WATER * self.displaced_volume_m3 / self.state.mass

    def _check_added_mass(self):
        r = self.added_mass_ratio()
        if r is not None and r > self.cfg.warn_added_mass and not self._warned:
            self._warned = True
            print(f"COUPLING WARNING added_mass_ratio={r:.2f} exceeds "
                  f"{self.cfg.warn_added_mass}; a partitioned explicit scheme is at "
                  f"its stability limit here. Reduce dt or set relax<1 and treat "
                  f"the transient as unconverged until a dt study says otherwise.")

    # -------------------------------------------------------------------- step
    def step(self):
        """One coupled tick: reset, advance MPM, read wrench, integrate, re-pose."""
        cfg = self.cfg
        self._check_added_mass()

        self.solver.reset_sdf_force(self.handle)
        for _ in range(cfg.substeps_per_pose):
            self.solver.step(cfg.dt)

        w = self.solver.sdf_wrench(self.handle, cfg.dt * cfg.substeps_per_pose)
        F = np.asarray(w["force"], dtype=float)
        T = np.asarray(w["torque"], dtype=float)

        if cfg.relax != 1.0:                      # Aitken-free constant relaxation
            F = cfg.relax * F + (1.0 - cfg.relax) * self._prev_F
            T = cfg.relax * T + (1.0 - cfg.relax) * self._prev_T
        self._prev_F, self._prev_T = F.copy(), T.copy()

        if cfg.freeze_rotation:
            T = np.zeros(3)

        info = integrate(self.state, F, T, cfg.dt * cfg.substeps_per_pose,
                         gravity=cfg.gravity,
                         max_speed=cfg.max_speed, max_omega=cfg.max_omega)
        if cfg.freeze_rotation:
            self.state.omega = np.zeros(3)
            self.state.quat = np.array([0.0, 0.0, 0.0, 1.0])

        self.solver.set_sdf_pose(
            self.handle,
            center=tuple(self.state.x_cm),
            quat=tuple(self.state.quat),
            velocity=tuple(self.state.v_cm),
            omega=tuple(self.state.omega),
        )

        self._t += cfg.dt * cfg.substeps_per_pose
        tr = self.trace
        tr.t.append(self._t)
        tr.force.append(F.copy())
        tr.torque.append(T.copy())
        tr.x_cm.append(self.state.x_cm.copy())
        tr.v_cm.append(self.state.v_cm.copy())
        tr.omega.append(self.state.omega.copy())
        tr.quat.append(self.state.quat.copy())
        if info["clamped"]:
            tr.clamped.append((self._t, info["clamped"]))
        return info

    def run(self, n_steps: int, progress_every: int = 0):
        for i in range(n_steps):
            self.step()
            if progress_every and i % progress_every == 0:
                F = self.trace.force[-1]
                print(f"  t={self._t:7.4f}  Fz={F[2]:+11.2f} N  "
                      f"z={self.state.x_cm[2]:+.5f}  vz={self.state.v_cm[2]:+.5f}",
                      flush=True)
        if self.trace.clamped:
            print(f"COUPLING NOTE {len(self.trace.clamped)} step(s) hit a velocity clamp; "
                  f"first at t={self.trace.clamped[0][0]:.4f} ({self.trace.clamped[0][1]}). "
                  f"Treat the trace past that point as unconverged, not physical.")
        return self.trace

    # ------------------------------------------------------------- diagnostics
    def expected_static_buoyancy(self):
        """rho g V for the supplied displaced volume. A YARDSTICK, not an input.

        Nothing in the coupling loop uses this value. It exists so a run can be
        scored against Archimedes without the scoring quantity ever entering the
        simulation.
        """
        if self.displaced_volume_m3 is None:
            return None
        return RHO_WATER * abs(self.cfg.gravity[2]) * self.displaced_volume_m3
