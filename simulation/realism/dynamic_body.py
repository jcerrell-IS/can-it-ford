"""Force-coupled 6-DOF rigid body driven by an SDF collider's grid impulse.

WHY THIS EXISTS
---------------
The material-8 free-rigid path used by the 17 canonical runs does not form a force.
`kernels/mpm_utils.py:1411-1412` accumulates `rigid_linear_mom` by atomic_add of
`v_interp * mass_p`, and `:1434` then sets

    v_cm_new = rigid_linear_mom[b] / M

which OVERWRITES the body velocity with the mass-weighted grid velocity. There is no
`v_old + F*dt/M` anywhere, and no force, impulse or torque accumulator exists on that
path (register A3, verified live 2026-08-12 against the pinned vendored core).

The SDF collider path in the SAME engine does form one. Its collide kernel at
`kernels/mpm_solver_warp.py:2732-2736` computes

    impulse = m * (v_free - v_new)
    atomic_add(param.force,  impulse)
    atomic_add(param.torque, cross(rel, impulse))

and writes the constrained node velocity back. That wrench is exposed on the wrapper at
`core/solver.py:354` (`sdf_wrench`, = accumulated impulse / dt) and is already validated
to 7.3-7.7 percent against analytic buoyancy (register A-2, job 894731, c1sdf g64/g96).

What is missing is ONLY the feedback loop. Both pose integrators in the engine are
kinematic: the SDF `modify` closure at `mpm_solver_warp.py:2740-2760` and
`_integrate_cdf_poses` at `:3107-3148` both advance `center += dt*velocity` with a
PRESCRIBED velocity, and neither ever reads `param.force`. This module supplies the
missing loop by replacing that closure, so the body responds to net force instead of
being told where to go. No kernel is written and the vendored engine is not edited.

SIGN CONVENTION
---------------
Documented at `core/solver.py:302-313`: a static cup holding m kg of settled liquid
reads `force = (0, 0, -m*g)`. So `param.force` is the force the MATERIAL exerts ON the
body, and a submerged body reads buoyancy as POSITIVE z. No sign flip is needed:

    M dv/dt = F_fluid + M g

UNITS
-----
`param.force` is an accumulated impulse in kg*m/s (N*s), not a force: the engine only
divides by dt inside `sdf_wrench`. This module works in impulse directly and never
divides, which removes a dt round-trip:

    dv = J / M + g*dt          [kg*m/s / kg] + [m/s^2 * s] = m/s
    dL = T_impulse             [N*m*s = kg*m^2/s]
    omega = R I_body^-1 R^T L  [kg^-1 m^-2 * kg m^2 /s] = 1/s

TRAP THIS CODE HANDLES
----------------------
`param.force` is NEVER zeroed by the engine on the SDF path. The only reset in the
engine, `reset_cdf_wrench` at `mpm_solver_warp.py:3153`, targets the CDF state arrays,
not `SDFCollider.force`. Left alone the accumulator grows monotonically from creation
and every force read is the run-to-date total. This module zeroes it at the end of every
substep, so each read is exactly one substep's impulse.

STABILITY LIMIT, STATED RATHER THAN DISCOVERED
----------------------------------------------
This is an explicit (loosely coupled) partitioned scheme, so it destabilises as the
added mass approaches the body mass. For the canonical hull, volume 3.542739 m^3 and
mass 1100 kg:

    equilibrium displaced volume  = M / rho_w = 1.100 m^3   (31.0 percent of the hull)
    added mass at that draft, Ca=1 = 1000 * 1.100 = 1100 kg -> m_a/M = 1.00   MARGINAL
    at the 0.30 m standing draft   = 1000 * 0.459 = 459 kg  -> m_a/M = 0.42   OK
    fully submerged                = 1000 * 3.543 = 3543 kg -> m_a/M = 3.22   DIVERGES

`added_mass` below is an OPTIONAL stabiliser and defaults to 0.0, i.e. unmodified
physics. It is not tuned to make any test pass; if a configuration diverges the correct
report is that it diverged, not a fitted value that hides it.
"""
from __future__ import annotations

import numpy as np

__all__ = ["DynamicSDFBody"]


def _omega_step_quat(q: np.ndarray, omega: np.ndarray, dt: float) -> np.ndarray:
    """First-order quaternion update under body-rate `omega`, renormalised.

    Mirrors the engine's own `_omega_step_quat` (mpm_solver_warp.py:198-211) so the
    orientation advances identically to the kinematic path this replaces. Quaternion
    layout is warp's (x, y, z, w), matching `SDFCollider.quat`.
    """
    w = np.asarray(omega, dtype=float)
    n = float(np.linalg.norm(w))
    if n < 1e-14:
        return q
    dq = np.array([w[0], w[1], w[2], 0.0]) * 0.5
    # dq_quat = 0.5 * omega_quat * q
    x, y, z, s = q
    ox, oy, oz = dq[0], dq[1], dq[2]
    qd = np.array([
        s * ox + oy * z - oz * y,
        s * oy + oz * x - ox * z,
        s * oz + ox * y - oy * x,
        -(ox * x + oy * y + oz * z),
    ])
    q = q + qd * dt
    return q / np.linalg.norm(q)


def _quat_to_R(q: np.ndarray) -> np.ndarray:
    """Rotation matrix from a warp-layout (x, y, z, w) quaternion."""
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


class DynamicSDFBody:
    """Turn a kinematic SDF collider into a free body driven by the fluid wrench.

    Install AFTER `solver.add_sdf_collider(...)` returns a handle. Installing replaces
    `sim.modify_bc[handle]`, which is the per-substep hook the engine calls at
    `mpm_solver_warp.py:1333`, immediately after the collide kernel at `:1320` has
    deposited this substep's impulse. So at hook time `param.force` holds exactly one
    substep of momentum transfer.

    Parameters
    ----------
    mass          body mass in kg. An SDF collider carries NO particles, so it has no
                  self-weight in the MPM sense and gravity must be applied here. That is
                  a property of the representation, not an approximation.
    inertia_body  (3,3) body-frame inertia tensor in kg*m^2. Must NOT come from
                  vehicle_params.py's `inertia_kg_m2`: that is a uniform-density box
                  fallback which reproduces exactly from box_inertia(1100, 4.30, 1.70,
                  1.47), and its axis convention is transposed against the scene (the
                  hull's long axis is y, measured extents 1.7078 / 4.2014 / 1.4853), so
                  a naive wire gives Ixx -69.2 percent and Iyy +379.2 percent. Compute it
                  from the solidified particle cloud instead, the same construction the
                  solver itself uses at `mpm_solver_warp.py:859-871`.
    locked_axes   optional booleans (x, y, z) freezing translation on an axis. Used to
                  isolate the vertical response in a heave-only test; a free run passes
                  (False, False, False).
    added_mass    optional scalar added-mass stabiliser in kg, default 0.0 = off.
    """

    def __init__(self, solver, handle, mass, inertia_body, gravity=(0.0, 0.0, -9.81),
                 locked_axes=(False, False, False), added_mass=0.0, floor_z=None):
        self.solver = solver
        self.sim = solver._sim
        self.handle = int(handle)
        self.param = self.sim.collider_params[self.handle]

        self.M = float(mass)
        self.I_body = np.asarray(inertia_body, dtype=float).reshape(3, 3)
        self.I_body_inv = np.linalg.inv(self.I_body)
        self.g = np.asarray(gravity, dtype=float)
        self.locked = np.asarray(locked_axes, dtype=bool)
        self.m_add = float(added_mass)
        self.floor_z = floor_z

        p = self.param
        self.x = np.array([p.center[0], p.center[1], p.center[2]], dtype=float)
        self.q = np.array([p.quat[0], p.quat[1], p.quat[2], p.quat[3]], dtype=float)
        self.v = np.array([p.velocity[0], p.velocity[1], p.velocity[2]], dtype=float)
        self.L = np.zeros(3)

        # per-substep trace, so the response can be audited rather than asserted
        self.trace = []
        self._prev_installed = None
        self.diverged = False

    # ------------------------------------------------------------------ install
    def install(self):
        """Replace the kinematic pose closure with the force-driven integrator."""
        import warp as wp
        self._wp = wp
        self._prev_installed = self.sim.modify_bc[self.handle]
        self.sim.modify_bc[self.handle] = self._step
        # Zero once at install so the first read is not the pre-install accumulation.
        self.param.force.zero_()
        self.param.torque.zero_()
        return self

    def uninstall(self):
        if self._prev_installed is not None:
            self.sim.modify_bc[self.handle] = self._prev_installed
        return self

    # ------------------------------------------------------------------ the loop
    def _step(self, time, dt, param):
        """One substep of rigid-body EOM driven by the accumulated grid impulse.

        Called by `_apply_grid_bc` at mpm_solver_warp.py:1333, after the collide kernel
        has run for this substep. `param.force` is an IMPULSE (N*s) covering this substep
        only, because this method zeroes it on the way out.
        """
        wp = self._wp
        if self.diverged:
            return

        J = np.asarray(param.force.numpy()[0], dtype=float)      # N*s, fluid on body
        Timp = np.asarray(param.torque.numpy()[0], dtype=float)  # N*m*s, about param.center

        if not np.all(np.isfinite(J)) or not np.all(np.isfinite(Timp)):
            self.diverged = True
            return

        # --- linear:  dv = J/(M + m_add) + g*dt
        dv = J / (self.M + self.m_add) + self.g * dt
        v_new = self.v + dv
        v_new[self.locked] = 0.0

        # --- angular: L += T*dt_impulse ; omega = R I_body^-1 R^T L
        self.L = self.L + Timp
        R = _quat_to_R(self.q)
        omega = R @ self.I_body_inv @ R.T @ self.L

        # --- advance pose
        x_new = self.x + v_new * dt
        if self.floor_z is not None and x_new[2] < self.floor_z:
            x_new[2] = self.floor_z
            if v_new[2] < 0.0:
                v_new[2] = 0.0
        q_new = _omega_step_quat(self.q, omega, dt)

        if not (np.all(np.isfinite(x_new)) and np.all(np.isfinite(v_new))):
            self.diverged = True
            return

        self.x, self.v, self.q = x_new, v_new, q_new

        # --- write the pose back to the collider for the next substep
        param.center = wp.vec3(float(x_new[0]), float(x_new[1]), float(x_new[2]))
        param.quat = wp.quat(float(q_new[0]), float(q_new[1]), float(q_new[2]), float(q_new[3]))
        param.velocity = wp.vec3(float(v_new[0]), float(v_new[1]), float(v_new[2]))
        param.omega = wp.vec3(float(omega[0]), float(omega[1]), float(omega[2]))

        self.trace.append({
            "t": float(time), "dt": float(dt),
            "F": (J / dt).tolist(),          # N, reported not used
            "z": float(x_new[2]), "vz": float(v_new[2]),
            "az": float(dv[2] / dt),
        })

        # --- the trap: the engine never zeroes this accumulator
        param.force.zero_()
        param.torque.zero_()

    # ------------------------------------------------------------------ helpers
    def state(self):
        return {"x": self.x.copy(), "v": self.v.copy(), "q": self.q.copy(),
                "L": self.L.copy(), "diverged": self.diverged}


def box_inertia_from_cloud(points, masses):
    """Inertia tensor about the mass centroid from a particle cloud.

    Identical construction to the solver's own at `mpm_solver_warp.py:859-871`,
    I = sum_i m_i (|r_i|^2 * 1 - r_i (x) r_i), so a tensor built here and one built by
    `finalize_rigid_bodies()` agree by construction rather than by coincidence. This is
    the sanctioned route to a better tensor; `vehicle_params.py` is not.
    """
    p = np.asarray(points, dtype=float)
    m = np.asarray(masses, dtype=float)
    com = (p * m[:, None]).sum(axis=0) / m.sum()
    r = p - com
    I = np.zeros((3, 3))
    r2 = (r * r).sum(axis=1)
    for k in range(3):
        I[k, k] = (m * (r2 - r[:, k] ** 2)).sum()
    for a, b in ((0, 1), (0, 2), (1, 2)):
        off = -(m * r[:, a] * r[:, b]).sum()
        I[a, b] = I[b, a] = off
    return I, com
