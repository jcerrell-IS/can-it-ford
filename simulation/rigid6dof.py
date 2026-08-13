"""Driver-level 6-DOF rigid-body integrator for the moving-SDF collider path.

Nothing in warpmpm needs to change to give an SDF collider free motion. The solver
already exposes the whole contract:

  add_sdf_collider(sdf, center, quat, velocity, omega, ...)  core/solver.py:324
  set_sdf_pose(handle, center, quat, velocity, omega)        core/solver.py:339
  reset_sdf_force(handle)                                    core/solver.py:348
  sdf_wrench(handle, dt) -> {'force':(3,), 'torque':(3,)}    core/solver.py:354

What is missing is the ordinary Python that closes the loop: read the reaction wrench,
integrate rigid-body dynamics, command the resulting velocity and omega back. That is
this module. It imports nothing from warpmpm and touches no GPU, so it is unit-testable
on a login node; the solver-facing driver lives in validate_coupling_force.py.

All four line citations above were verified live against the vendored pinned-SHA source
at third_party/mpm-engine-544c93dd-solver-core/ on 2026-08-13, not carried from a doc.

CONVENTIONS, each verified against the source rather than assumed
----------------------------------------------------------------
Quaternion order is (x, y, z, w), scalar LAST, body->world. This is not universal in
this codebase: add_sdf_collider defaults quat=(0,0,0,1) which is xyzw identity
(solver.py:324), while add_cup documents wxyz and defaults (1,0,0,0) (solver.py:256,262).
Handing an SDF collider a wxyz quaternion silently applies a wrong rotation rather than
failing, so the two must never be crossed.

omega is a WORLD-frame angular velocity and left-multiplies the orientation, per
_omega_step_quat's own docstring (mpm_solver_warp.py:198-200). quat_step below is a
line-for-line mirror of that function, and test_rigid6dof.py asserts the two agree.

The solver integrates the commanded pose itself: modify_bc advances
center += dt*velocity and rotates quat by omega on EVERY substep
(mpm_solver_warp.py:2756-2760). So a tick of n_sub substeps of size dt_sub advances the
collider by (n_sub*dt_sub)*velocity. Command the start-of-tick pose and the per-tick
velocity; passing the end-of-tick target as center double-applies the motion and leaves
the collider one tick ahead (set_box docstring, solver.py:240-246).

sdf_wrench divides the accumulated impulse by the dt handed to it, and the accumulator is
zeroed only by an explicit reset_sdf_force (solver.py:348-361). The accumulation runs over
every substep since that reset, so a multi-substep tick must be normalised by the TICK
duration n_sub*dt_sub, not by dt_sub. Passing the substep dt for a multi-substep tick
inflates the force by exactly n_sub.

SIGN
----
The wrench is the force the MATERIAL exerts on the collider, and the engine's stated
convention (solver.py:305-307) is that a static cup holding m kg of settled liquid reads
force = (0, 0, -m*g). A submerged body therefore reads buoyancy as POSITIVE z. Gravity is
NOT included in the wrench and is added here.

WHAT THIS MODULE DELIBERATELY DOES NOT DO
-----------------------------------------
It does not under-relax the coupling. Register J1a records that under-relaxation was
tried on this path and REFUTED (job 3361371, error grew monotonically), so it is not
re-proposed here as if untried. The added-mass constraint J1a documents is a property of
the explicit partitioned scheme class, not a tuning gap; added_mass_ratio() below exposes
it as a diagnostic so a run can report where it sits, and makes no claim to fix it.
"""

from __future__ import annotations

import math

import numpy as np

__all__ = [
    "quat_mul", "quat_step", "quat_to_mat", "cube_inertia",
    "RigidBody6DOF", "added_mass_ratio",
]


# --- quaternion helpers, mirroring the solver's host-side functions exactly --------------

def quat_mul(q1, q2):
    """Hamilton product of two (x, y, z, w) quaternions.

    Mirror of _quat_mul, kernels/mpm_solver_warp.py:186-196.
    """
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return np.array([
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
    ], dtype=float)


def quat_step(q, omega, dt):
    """Advance orientation q (body->world, xyzw) by world-frame omega over dt.

    Exponential map, exact for constant omega, world omega left-multiplies. Mirror of
    _omega_step_quat, kernels/mpm_solver_warp.py:198-211. Kept byte-equivalent in
    behaviour so the Python-side pose mirror cannot drift from the solver's own.

    Because the solver applies this once per substep with the SAME omega, n successive
    rotations of angle |omega|*dt_sub about a fixed axis compose exactly to one rotation
    of angle |omega|*n*dt_sub. A single call with dt = n*dt_sub is therefore equivalent,
    which is what lets the mirror below use one call per tick.
    """
    w = np.asarray(omega, dtype=float)
    speed = float(np.linalg.norm(w))
    if speed * dt < 1e-12:
        return np.asarray(q, dtype=float)
    half = 0.5 * speed * dt
    axis = w / speed
    dq = np.array([axis[0] * math.sin(half), axis[1] * math.sin(half),
                   axis[2] * math.sin(half), math.cos(half)], dtype=float)
    qn = quat_mul(dq, q)
    return qn / np.linalg.norm(qn)


def quat_to_mat(q):
    """Body->world rotation matrix for an (x, y, z, w) quaternion.

    Same expression the solver builds when it computes an SDF collider's world AABB
    (mpm_solver_warp.py:2763-2770), so R here and R there agree term for term.
    """
    qx, qy, qz, qw = (float(c) for c in q)
    return np.array([
        [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
        [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
        [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)],
    ], dtype=float)


def cube_inertia(mass, length):
    """Principal inertia of a uniform cube of edge ``length`` about its centre.

    I = m*L^2/6 on each axis, the a=b=L case of the standard m*(a^2+b^2)/12. Returned as
    a 3-vector. The cube is the harness's own body (BoxTank builds mass = rho*L^3 from a
    cube mesh), so this is derived from the harness geometry rather than quoting any
    vehicle inertia. No vehicle mass, rho, or inertia tensor is hardcoded in this module.
    """
    m = float(mass)
    L = float(length)
    return np.full(3, m * L * L / 6.0, dtype=float)


def added_mass_ratio(rho_body, rho_fluid, c_a=1.0):
    """Diagnostic only: c_a * (displaced mass / body mass) = c_a * rho_fluid/rho_body.

    Register J1a's identity is that this is exactly 1.000000 for ANY body floating at
    equilibrium, because equilibrium means displaced mass equals body mass. An explicit
    partitioned scheme is at its stability limit there and no parameter escapes it. This
    function exists so a run can REPORT the number it is operating at, not to correct it.
    """
    return float(c_a) * float(rho_fluid) / float(rho_body)


class RigidBody6DOF:
    """Free rigid body driven by a measured wrench, in the solver's own conventions.

    Angular motion is integrated as world-frame angular momentum, L += torque*dt with
    omega = I_world^-1 L. This is equivalent to the body-frame Euler form
    tau = I*omega_dot + omega x I*omega but carries the gyroscopic term implicitly, so
    there is no explicit omega x I*omega to sign-error. test_rigid6dof.py checks
    torque-free angular momentum conservation to hold the two equivalent.

    The SDF collider rotates about ``param.center`` (mpm_solver_warp.py:2697, the body
    query is quat_rotate_inv(quat, x_world - center)), and sdf_wrench reports torque about
    that same centre (solver.py:354-358). Both therefore coincide with the centre of mass
    only when the body is centre-symmetric, which the harness cube is. A non-zero COM
    offset would require migrating the collider centre to track the COM each tick, which
    is NOT implemented; the constructor rejects it rather than integrating something
    subtly wrong.
    """

    def __init__(self, mass, inertia_body, center, quat=(0.0, 0.0, 0.0, 1.0),
                 velocity=(0.0, 0.0, 0.0), omega=(0.0, 0.0, 0.0),
                 gravity=(0.0, 0.0, -9.81), com_offset_body=(0.0, 0.0, 0.0)):
        if float(mass) <= 0.0:
            raise ValueError("mass must be positive; a fixed collider has no dynamics")
        if not np.allclose(np.asarray(com_offset_body, dtype=float), 0.0):
            raise NotImplementedError(
                "com_offset_body != 0 is not supported: the SDF collider rotates about "
                "its centre and sdf_wrench reports torque about that centre, so a body "
                "whose COM is offset from the SDF centre needs the collider centre "
                "migrated to track the COM each tick. Implement that explicitly rather "
                "than letting this integrator silently treat centre as COM.")
        self.mass = float(mass)

        inertia_body = np.asarray(inertia_body, dtype=float)
        if inertia_body.shape == (3,):
            inertia_body = np.diag(inertia_body)
        if inertia_body.shape != (3, 3):
            raise ValueError("inertia_body must be a 3-vector of principal moments "
                             "or a full 3x3 tensor")
        if not np.allclose(inertia_body, inertia_body.T):
            raise ValueError("inertia_body must be symmetric")
        eigs = np.linalg.eigvalsh(inertia_body)
        if float(eigs.min()) <= 0.0:
            raise ValueError("inertia_body must be positive definite")
        self.inertia_body = inertia_body

        self.center = np.asarray(center, dtype=float).copy()
        q = np.asarray(quat, dtype=float).copy()
        n = float(np.linalg.norm(q))
        if n == 0.0:
            raise ValueError("quat must be non-zero")
        self.quat = q / n
        self.velocity = np.asarray(velocity, dtype=float).copy()
        self.gravity = np.asarray(gravity, dtype=float).copy()
        # World-frame angular momentum is the stored angular state, NOT omega. Storing
        # omega instead makes the zero-torque case wrong in a way that looks plausible:
        # recovering L from omega every tick forces omega constant and lets L drift with
        # the orientation, which is backwards. Torque-free motion conserves L and varies
        # omega. test_torque_free_conserves_angular_momentum caught exactly this.
        self._L = self.inertia_world() @ np.asarray(omega, dtype=float)

    # --- derived state ------------------------------------------------------------------
    def rotation(self):
        """Current body->world rotation matrix."""
        return quat_to_mat(self.quat)

    def inertia_world(self):
        """R I_body R^T, the inertia tensor in the world frame."""
        R = self.rotation()
        return R @ self.inertia_body @ R.T

    def angular_momentum(self):
        """World-frame angular momentum, the primary angular state."""
        return self._L.copy()

    @property
    def omega(self):
        """World-frame angular velocity, derived from L at the CURRENT orientation.

        Deriving it rather than storing it is what produces torque-free precession: as the
        body tumbles, I_world changes, so the same conserved L maps to a different omega.
        """
        return np.linalg.solve(self.inertia_world(), self._L)

    def kinetic_energy(self):
        return (0.5 * self.mass * float(self.velocity @ self.velocity)
                + 0.5 * float(self.omega @ self.angular_momentum()))

    # --- the integrator -----------------------------------------------------------------
    def integrate(self, force, torque, dt):
        """Advance one control tick of duration ``dt`` under a measured wrench.

        ``force`` and ``torque`` are the wrench the material exerts on the collider, world
        frame, torque about the collider centre, exactly as sdf_wrench returns them.
        Gravity is added here; the wrench does not contain it.

        Symplectic (semi-implicit) Euler: velocities are updated first, then the pose is
        advanced with the UPDATED velocities. That ordering is required, not stylistic:
        the solver will advance the pose using the velocity and omega commanded for this
        tick, so the mirror must use the same post-update values or the Python-side pose
        silently diverges from the collider's actual pose.

        Returns (velocity, omega) to command through set_sdf_pose.
        """
        dt = float(dt)
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        f = np.asarray(force, dtype=float)
        tau = np.asarray(torque, dtype=float)
        if f.shape != (3,) or tau.shape != (3,):
            raise ValueError("force and torque must each be 3-vectors")

        # linear: gravity is a body force, the wrench is the fluid reaction
        accel = f / self.mass + self.gravity
        self.velocity = self.velocity + accel * dt

        # angular: torque changes L and only L. omega is then read off at the current
        # orientation, before the pose advances, because that is the omega the solver will
        # be told to spin at across this tick.
        self._L = self._L + tau * dt
        omega = self.omega

        # pose, with the updated velocities, mirroring what modify_bc will do
        self.center = self.center + self.velocity * dt
        self.quat = quat_step(self.quat, omega, dt)
        return self.velocity.copy(), omega.copy()

    # --- guards -------------------------------------------------------------------------
    def sweep_speed(self, r_max):
        """Surface sweep rate the solver's own tunnelling guard computes.

        speed = |v| + |omega|*r_max, matching mpm_solver_warp.py:2747-2748 term for term,
        where r_max is the collider's farthest surface point from its centre.
        """
        return (float(np.linalg.norm(self.velocity))
                + float(np.linalg.norm(self.omega)) * float(r_max))

    def tunneling_margin(self, r_max, band, dt_sub):
        """Ratio of per-substep surface sweep to the contact band.

        The solver warns once when this exceeds 1 (mpm_solver_warp.py:2749-2755) and then
        stays silent, so a driver that wants a per-tick record has to compute it itself.
        Above 1, material can jump from outside the band to inside the solid unconstrained,
        which corrupts the very wrench the loop is integrating.
        """
        return self.sweep_speed(r_max) * float(dt_sub) / float(band)

    def state(self):
        """Serialisable snapshot, for per-tick logging into a results JSON."""
        return {
            "center": [float(c) for c in self.center],
            "quat_xyzw": [float(c) for c in self.quat],
            "velocity": [float(c) for c in self.velocity],
            "omega": [float(c) for c in self.omega],
            "speed": float(np.linalg.norm(self.velocity)),
            "omega_mag": float(np.linalg.norm(self.omega)),
            "kinetic_energy": self.kinetic_energy(),
        }
