#!/usr/bin/env python3
"""Analytic self-tests for the force-based coupling integrator. No GPU, no solver.

These do NOT validate the fluid coupling. They validate that, GIVEN a wrench,
the Newton-Euler integrator reproduces closed-form answers. That separation
matters: if a coupled run later shows no buoyant rise, these tests tell you the
integrator is not the reason.

Run:  python simulation/coupling_force/test_rigid_body.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from simulation.coupling_force.rigid_body import (  # noqa: E402
    RigidBodyState, integrate, inertia_from_particles, quat_to_matrix,
)

G = 9.81
RHO_W = 1000.0
FAILS = []


def check(name, got, want, tol):
    ok = abs(got - want) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g} want {want:.6g} tol {tol:g}")
    if not ok:
        FAILS.append(name)


def box_inertia(m, sx, sy, sz):
    return np.diag([m * (sy**2 + sz**2) / 12.0,
                    m * (sx**2 + sz**2) / 12.0,
                    m * (sx**2 + sy**2) / 12.0])


def t_freefall():
    print("free fall, zero fluid wrench: z = -g t^2 / 2")
    m = 1200.0
    s = RigidBodyState(mass=m, inertia_body=box_inertia(m, 4.0, 1.8, 1.5))
    dt, n = 1e-4, 10000
    for _ in range(n):
        integrate(s, np.zeros(3), np.zeros(3), dt, gravity=(0, 0, -G))
    T = dt * n
    # symplectic Euler carries an O(dt) offset of exactly -g*dt*T/2
    want = -0.5 * G * T**2 - 0.5 * G * dt * T
    check("z(1s)", s.x_cm[2], want, 1e-6)
    check("vz(1s)", s.v_cm[2], -G * T, 1e-9)


def t_neutral():
    """A body whose fluid force exactly cancels weight must not move."""
    print("neutral buoyancy: F = -M g holds the body still")
    m = 1200.0
    s = RigidBodyState(mass=m, inertia_body=box_inertia(m, 4.0, 1.8, 1.5))
    F = np.array([0.0, 0.0, m * G])
    for _ in range(5000):
        integrate(s, F, np.zeros(3), 1e-4, gravity=(0, 0, -G))
    check("z drift", s.x_cm[2], 0.0, 1e-9)
    check("vz drift", s.v_cm[2], 0.0, 1e-9)


def t_archimedes_shm():
    """Hydrostatic restoring force on a partially submerged box -> SHM.

    F_b = rho g A z_sub. About equilibrium this is a linear spring of stiffness
    k = rho g A, so the body oscillates at omega = sqrt(rho g A / M). This is the
    rung (b) signature: a real buoyant force produces an oscillation whose period
    is set by waterplane area and mass, NOT a velocity that is simply adopted.
    """
    print("partially submerged box: hydrostatic restoring force -> SHM")
    sx, sy, sz = 4.0, 1.8, 1.5
    A = sx * sy
    m = 0.5 * RHO_W * sx * sy * sz          # half-buoyant, as in Qian et al. 2022
    s = RigidBodyState(mass=m, inertia_body=box_inertia(m, sx, sy, sz))
    k = RHO_W * G * A
    omega_th = np.sqrt(k / m)
    period_th = 2 * np.pi / omega_th

    z0 = 0.05                                # displace 5 cm from equilibrium
    s.x_cm = np.array([0.0, 0.0, z0])
    dt = 1e-5
    n = int(round(3 * period_th / dt))
    zs = np.empty(n)
    for i in range(n):
        F = np.array([0.0, 0.0, -k * s.x_cm[2] + m * G])   # restoring + weight cancel
        integrate(s, F, np.zeros(3), dt, gravity=(0, 0, -G))
        zs[i] = s.x_cm[2]

    check("amplitude preserved", float(np.max(np.abs(zs))), z0, 2e-3)
    sign = np.sign(zs)
    cross = np.where((sign[:-1] > 0) & (sign[1:] <= 0))[0]
    if len(cross) >= 2:
        period_meas = float((cross[-1] - cross[0]) / (len(cross) - 1) * dt)
        check("SHM period", period_meas, period_th, 0.02 * period_th)
    else:
        FAILS.append("SHM period (too few zero crossings)")
        print("  [FAIL] SHM period: too few zero crossings")
    print(f"     theory: k={k:.1f} N/m  M={m:.1f} kg  T={period_th:.4f} s")


def t_inertia():
    """Geometry-derived inertia must match the analytic box tensor."""
    print("inertia_from_particles vs analytic solid box")
    sx, sy, sz = 4.0, 1.8, 1.5
    m = 1200.0
    rng = np.random.default_rng(0)
    P = (rng.random((400000, 3)) - 0.5) * np.array([sx, sy, sz])
    I, com, M = inertia_from_particles(P, total_mass=m)
    ref = box_inertia(m, sx, sy, sz)
    for a, ax in enumerate("xyz"):
        check(f"I_{ax}{ax}", I[a, a], ref[a, a], 0.02 * ref[a, a])
    check("com offset", float(np.linalg.norm(com)), 0.0, 5e-3)
    check("mass", M, m, 1e-9)


def t_gyroscopic():
    """Torque-free asymmetric top conserves angular momentum and energy."""
    print("torque-free rotation: L and E conserved")
    m = 1200.0
    s = RigidBodyState(mass=m, inertia_body=box_inertia(m, 4.0, 1.8, 1.5))
    s.omega = np.array([0.6, 0.35, 0.15])
    L0 = s.inertia_world() @ s.omega
    E0 = 0.5 * s.omega @ (s.inertia_world() @ s.omega)
    dt, n = 2e-6, 200000
    for _ in range(n):
        integrate(s, np.zeros(3), np.zeros(3), dt, gravity=(0, 0, 0))
    L1 = s.inertia_world() @ s.omega
    E1 = 0.5 * s.omega @ (s.inertia_world() @ s.omega)
    check("|L| drift rel", float(abs(np.linalg.norm(L1) - np.linalg.norm(L0)) /
                                 np.linalg.norm(L0)), 0.0, 2e-3)
    check("E drift rel", float(abs(E1 - E0) / E0), 0.0, 2e-3)
    R = quat_to_matrix(s.quat)
    check("R orthonormal", float(np.abs(R @ R.T - np.eye(3)).max()), 0.0, 1e-9)


if __name__ == "__main__":
    for fn in (t_freefall, t_neutral, t_archimedes_shm, t_inertia, t_gyroscopic):
        fn()
        print()
    if FAILS:
        print(f"FAILED: {FAILS}")
        sys.exit(1)
    print("ALL ANALYTIC INTEGRATOR TESTS PASSED")
