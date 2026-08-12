"""Newton-Euler rigid body state and explicit integrator for force-based coupling.

This module is deliberately free of any warpmpm import. It knows nothing about
MPM; it takes a wrench in and advances a rigid body. That separation is what
lets the coupling be unit-tested against analytic buoyancy without a solver.

CONVENTIONS
    quaternion  (x, y, z, w), matching warpmpm's add_sdf_collider default
                (0, 0, 0, 1). NOT (w, x, y, z).
    inertia     body-frame 3x3, about the centre of mass.
    frames      x_cm, v_cm, omega, force, torque are all WORLD frame.
                omega is world-frame angular velocity, so the body-frame inertia
                is rotated per step: I_world = R I_body R^T.

INERTIA PROVENANCE, deliberate refusal
    This module NEVER imports vehicle_params. Its inertia_kg_m2 is an
    axis-transposed box fallback carrying a documented 379% error on the pitch
    axis (docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md section 1), so wiring it
    into a solver would silently corrupt every rotational result. Inertia here is
    either passed in explicitly by the caller or computed from the actual
    particle cloud by inertia_from_particles(), which is geometry-derived and
    self-consistent with the hull the SDF was built from.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


# ------------------------------------------------------------------ quaternion
def quat_normalize(q):
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q)
    if n < 1e-12:
        return np.array([0.0, 0.0, 0.0, 1.0])
    return q / n


def quat_to_matrix(q):
    """(x, y, z, w) -> 3x3 rotation matrix."""
    x, y, z, w = quat_normalize(q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w),     2 * (x * z + y * w)],
        [2 * (x * y + z * w),     1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w),     2 * (y * z + x * w),     1 - 2 * (x * x + y * y)],
    ])


def quat_derivative(q, omega_world):
    """dq/dt for world-frame omega, with q = (x, y, z, w)."""
    x, y, z, w = q
    wx, wy, wz = omega_world
    return 0.5 * np.array([
        w * wx + y * wz - z * wy,
        w * wy + z * wx - x * wz,
        w * wz + x * wy - y * wx,
        -(x * wx + y * wy + z * wz),
    ])


# -------------------------------------------------------------------- inertia
def inertia_from_particles(points, masses=None, total_mass=None):
    """Body-frame inertia tensor about the centre of mass, from a particle cloud.

    Geometry-derived, so it inherits the hull's real axis lengths rather than a
    box approximation. Returns (I_body 3x3, com 3, mass float).
    """
    P = np.asarray(points, dtype=float)
    if masses is None:
        if total_mass is None:
            raise ValueError("give masses or total_mass")
        m = np.full(len(P), float(total_mass) / len(P))
    else:
        m = np.asarray(masses, dtype=float)
    M = float(m.sum())
    com = (P * m[:, None]).sum(0) / M
    r = P - com
    r2 = (r * r).sum(1)
    I = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            I[a, b] = (m * ((r2 if a == b else 0.0) - r[:, a] * r[:, b])).sum()
    return I, com, M


# ----------------------------------------------------------------------- body
@dataclass
class RigidBodyState:
    mass: float
    inertia_body: np.ndarray                       # (3, 3) about the CM
    x_cm: np.ndarray = field(default_factory=lambda: np.zeros(3))
    v_cm: np.ndarray = field(default_factory=lambda: np.zeros(3))
    omega: np.ndarray = field(default_factory=lambda: np.zeros(3))   # world frame
    quat: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 1.0]))

    def __post_init__(self):
        self.inertia_body = np.asarray(self.inertia_body, dtype=float).reshape(3, 3)
        self.x_cm = np.asarray(self.x_cm, dtype=float).reshape(3)
        self.v_cm = np.asarray(self.v_cm, dtype=float).reshape(3)
        self.omega = np.asarray(self.omega, dtype=float).reshape(3)
        self.quat = quat_normalize(self.quat)
        if self.mass <= 0:
            raise ValueError("mass must be positive")
        if np.linalg.det(self.inertia_body) <= 0:
            raise ValueError("inertia tensor must be positive definite")

    @property
    def R(self):
        return quat_to_matrix(self.quat)

    def inertia_world(self):
        R = self.R
        return R @ self.inertia_body @ R.T

    def kinetic_energy(self):
        Iw = self.inertia_world()
        return 0.5 * self.mass * self.v_cm @ self.v_cm + 0.5 * self.omega @ (Iw @ self.omega)


def integrate(state: RigidBodyState, force, torque, dt, gravity=(0.0, 0.0, -9.81),
              max_speed=None, max_omega=None):
    """One explicit semi-implicit (symplectic Euler) Newton-Euler step.

        M dv/dt = F_fluid + M g
        I dw/dt = tau_fluid - w x (I w)

    Velocity is updated first and position from the NEW velocity, which is the
    symplectic variant and is markedly better behaved than forward Euler for the
    oscillatory buoyancy response this module exists to produce.

    max_speed / max_omega are optional guards. They do NOT stabilise a genuinely
    unstable added-mass ratio; they only stop a diverging run from producing inf
    and destroying an otherwise readable trace. When either clamp fires it is
    reported through the returned dict so a run is never silently truncated.
    """
    F = np.asarray(force, dtype=float).reshape(3)
    T = np.asarray(torque, dtype=float).reshape(3)
    g = np.asarray(gravity, dtype=float).reshape(3)

    a = F / state.mass + g
    v_new = state.v_cm + a * dt

    Iw = state.inertia_world()
    gyro = np.cross(state.omega, Iw @ state.omega)
    alpha = np.linalg.solve(Iw, T - gyro)
    w_new = state.omega + alpha * dt

    clamped = []
    if max_speed is not None:
        s = np.linalg.norm(v_new)
        if s > max_speed:
            v_new = v_new * (max_speed / s)
            clamped.append(f"speed {s:.3f}>{max_speed}")
    if max_omega is not None:
        s = np.linalg.norm(w_new)
        if s > max_omega:
            w_new = w_new * (max_omega / s)
            clamped.append(f"omega {s:.3f}>{max_omega}")

    state.v_cm = v_new
    state.omega = w_new
    state.x_cm = state.x_cm + v_new * dt
    state.quat = quat_normalize(state.quat + quat_derivative(state.quat, w_new) * dt)

    return {
        "accel": a, "alpha": alpha, "clamped": clamped,
        "v": state.v_cm.copy(), "omega": state.omega.copy(),
        "x_cm": state.x_cm.copy(), "quat": state.quat.copy(),
    }
