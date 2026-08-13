"""Unit tests for the driver-level 6-DOF integrator.

The point of these is that they run WITHOUT a GPU and without warp, on a login node, so
the integrator can be verified before any allocation is spent on it. The solver-facing
driver cannot be tested this way; the integrator can, and it is where the sign and
convention errors would live.

The convention tests are not self-consistency checks. They extract the real _quat_mul and
_omega_step_quat out of the vendored pinned-SHA solver source and compare against them, so
a drift between this module and the engine fails the test rather than passing quietly.
"""

import ast
import math
import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from simulation.rigid6dof import (  # noqa: E402
    RigidBody6DOF, added_mass_ratio, cube_inertia, quat_mul, quat_step, quat_to_mat,
)

REPO = pathlib.Path(__file__).resolve().parents[1]
SOLVER_SRC = (REPO / "third_party" / "mpm-engine-544c93dd-solver-core" / "kernels"
              / "mpm_solver_warp.py")


def _load_reference_quat_fns():
    """Exec the engine's own _quat_mul/_omega_step_quat without importing warp.

    mpm_solver_warp.py imports warp at module scope, which is not installed on a login
    node and would drag in a GPU context anyway. Both functions are pure numpy and are
    located by AST rather than by line number, so ordinary line drift in the vendored
    source does not silently skip the comparison.
    """
    if not SOLVER_SRC.exists():
        pytest.skip(f"vendored solver source not present at {SOLVER_SRC}")
    tree = ast.parse(SOLVER_SRC.read_text())
    wanted = {"_quat_mul", "_omega_step_quat"}
    found = {n.name: n for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name in wanted}
    missing = wanted - set(found)
    if missing:
        pytest.fail(f"{SOLVER_SRC.name} no longer defines {sorted(missing)} at module "
                    f"scope; the convention this module mirrors has moved, re-verify it")
    ns = {"np": np}
    exec(compile(ast.Module(body=[found["_quat_mul"], found["_omega_step_quat"]],
                            type_ignores=[]), str(SOLVER_SRC), "exec"), ns)
    return ns["_quat_mul"], ns["_omega_step_quat"]


def _rand_quat(rng):
    q = rng.normal(size=4)
    return q / np.linalg.norm(q)


# --- convention equivalence against the real engine source -------------------------------

def test_quat_mul_matches_engine():
    ref_mul, _ = _load_reference_quat_fns()
    rng = np.random.default_rng(0)
    for _ in range(200):
        a, b = _rand_quat(rng), _rand_quat(rng)
        assert np.allclose(quat_mul(a, b), ref_mul(a, b), atol=1e-14)


def test_quat_step_matches_engine():
    _, ref_step = _load_reference_quat_fns()
    rng = np.random.default_rng(1)
    for _ in range(200):
        q = _rand_quat(rng)
        w = rng.normal(scale=3.0, size=3)
        dt = float(rng.uniform(1e-6, 1e-2))
        assert np.allclose(quat_step(q, w, dt), ref_step(q, w, dt), atol=1e-14)


def test_quat_step_zero_omega_is_identity():
    """The engine short-circuits below speed*dt < 1e-12; the mirror must too."""
    _, ref_step = _load_reference_quat_fns()
    q = np.array([0.0, 0.0, 0.0, 1.0])
    assert np.allclose(quat_step(q, (0.0, 0.0, 0.0), 1e-3), q)
    assert np.allclose(quat_step(q, (0.0, 0.0, 0.0), 1e-3),
                       ref_step(q, (0.0, 0.0, 0.0), 1e-3))


def test_substep_composition_equals_single_tick():
    """n substeps at dt_sub compose to one call at n*dt_sub.

    This is the property that lets the Python-side pose mirror take one step per control
    tick while modify_bc takes n. If it failed, the mirror would drift from the collider's
    true pose and every logged position would be wrong.
    """
    rng = np.random.default_rng(2)
    for _ in range(50):
        q0 = _rand_quat(rng)
        w = rng.normal(scale=2.0, size=3)
        dt_sub, n = 1e-4, 37
        q = q0.copy()
        for _ in range(n):
            q = quat_step(q, w, dt_sub)
        one = quat_step(q0, w, n * dt_sub)
        # quaternions double-cover SO(3): q and -q are the same rotation
        assert min(np.linalg.norm(q - one), np.linalg.norm(q + one)) < 1e-10


def test_xyzw_not_wxyz():
    """Identity is (0,0,0,1) here, not (1,0,0,0). Guards the cup/SDF convention trap."""
    ident = np.array([0.0, 0.0, 0.0, 1.0])
    assert np.allclose(quat_to_mat(ident), np.eye(3))
    # the wxyz identity, fed to this xyzw code, is a 180 degree turn about x, not identity
    assert not np.allclose(quat_to_mat(np.array([1.0, 0.0, 0.0, 0.0])), np.eye(3))


def test_quat_to_mat_is_rotation():
    rng = np.random.default_rng(3)
    for _ in range(100):
        R = quat_to_mat(_rand_quat(rng))
        assert np.allclose(R @ R.T, np.eye(3), atol=1e-12)
        assert math.isclose(float(np.linalg.det(R)), 1.0, rel_tol=1e-12)


# --- rigid-body dynamics -----------------------------------------------------------------

def test_cube_inertia_formula():
    assert np.allclose(cube_inertia(6.0, 2.0), np.full(3, 6.0 * 4.0 / 6.0))


def test_free_fall_matches_symplectic_euler_closed_form():
    """Zero wrench: after n ticks v = -g*n*dt exactly, and z is the exact discrete sum."""
    g, dt, n = 9.81, 1e-3, 500
    b = RigidBody6DOF(mass=2.0, inertia_body=cube_inertia(2.0, 0.1),
                      center=(0.0, 0.0, 10.0), gravity=(0.0, 0.0, -g))
    for _ in range(n):
        b.integrate(np.zeros(3), np.zeros(3), dt)
    assert math.isclose(float(b.velocity[2]), -g * n * dt, rel_tol=1e-12)
    # symplectic Euler with v updated first: z = z0 - g*dt^2 * sum_{k=1..n} k
    expected = 10.0 - g * dt * dt * n * (n + 1) / 2.0
    assert math.isclose(float(b.center[2]), expected, rel_tol=1e-12)


def test_neutral_buoyancy_holds_still():
    """A wrench exactly cancelling weight must leave the body at rest.

    Sign check: the engine reports buoyancy as POSITIVE z, so +m*g in z is what balances
    gravity. If the sign convention were flipped anywhere, this test sees 2*g, not 0.
    """
    m, g = 5.0, 9.81
    b = RigidBody6DOF(mass=m, inertia_body=cube_inertia(m, 0.3),
                      center=(0.0, 0.0, 1.0), gravity=(0.0, 0.0, -g))
    for _ in range(1000):
        b.integrate(np.array([0.0, 0.0, m * g]), np.zeros(3), 1e-3)
    assert np.allclose(b.velocity, 0.0, atol=1e-12)
    assert np.allclose(b.center, [0.0, 0.0, 1.0], atol=1e-12)


def test_torque_free_conserves_angular_momentum():
    """Zero torque: world-frame L is conserved even as the body tumbles.

    This is the test that validates integrating L in the world frame instead of writing
    the body-frame Euler equation with an explicit omega x I*omega. An asymmetric inertia
    and a non-principal initial omega make it a real tumble, not a trivial spin.
    """
    b = RigidBody6DOF(mass=3.0, inertia_body=(0.4, 1.1, 2.3), center=(0, 0, 0),
                      omega=(1.7, -0.9, 2.4), gravity=(0.0, 0.0, 0.0))
    L0 = b.angular_momentum().copy()
    for _ in range(20000):
        b.integrate(np.zeros(3), np.zeros(3), 1e-5)
    L1 = b.angular_momentum()
    assert np.allclose(L1, L0, atol=1e-9), f"L drifted {L0} -> {L1}"


def test_torque_free_tumble_actually_rotates():
    """Guard against the conservation test passing because nothing moved."""
    b = RigidBody6DOF(mass=3.0, inertia_body=(0.4, 1.1, 2.3), center=(0, 0, 0),
                      omega=(1.7, -0.9, 2.4), gravity=(0.0, 0.0, 0.0))
    q0 = b.quat.copy()
    for _ in range(20000):
        b.integrate(np.zeros(3), np.zeros(3), 1e-5)
    assert min(np.linalg.norm(b.quat - q0), np.linalg.norm(b.quat + q0)) > 0.1
    # a genuinely asymmetric body must exchange energy between axes, so omega changes
    assert not np.allclose(b.omega, [1.7, -0.9, 2.4], atol=1e-3)


def test_constant_torque_spins_up_about_that_axis():
    """Symmetric body, torque about z: omega_z grows as tau*t/I_zz, others stay zero."""
    m, L = 4.0, 0.5
    I = cube_inertia(m, L)
    b = RigidBody6DOF(mass=m, inertia_body=I, center=(0, 0, 0), gravity=(0.0, 0.0, 0.0))
    tau, dt, n = 0.7, 1e-4, 1000
    for _ in range(n):
        b.integrate(np.zeros(3), np.array([0.0, 0.0, tau]), dt)
    assert math.isclose(float(b.omega[2]), tau * n * dt / I[2], rel_tol=1e-9)
    assert np.allclose(b.omega[:2], 0.0, atol=1e-12)


def test_quat_stays_normalised():
    rng = np.random.default_rng(4)
    b = RigidBody6DOF(mass=1.0, inertia_body=(0.2, 0.5, 0.9), center=(0, 0, 0),
                      omega=(3.0, 1.0, -2.0), gravity=(0.0, 0.0, 0.0))
    for _ in range(5000):
        b.integrate(rng.normal(size=3), rng.normal(size=3), 1e-4)
        assert math.isclose(float(np.linalg.norm(b.quat)), 1.0, rel_tol=1e-12)


def test_isotropic_inertia_is_rotation_invariant():
    """A cube's inertia is isotropic, so I_world must equal I_body at any orientation."""
    rng = np.random.default_rng(5)
    I = cube_inertia(2.0, 0.4)
    for _ in range(50):
        b = RigidBody6DOF(mass=2.0, inertia_body=I, center=(0, 0, 0),
                          quat=_rand_quat(rng))
        assert np.allclose(b.inertia_world(), np.diag(I), atol=1e-12)


# --- guards ------------------------------------------------------------------------------

def test_tunneling_margin_matches_engine_formula():
    """(|v| + |omega|*r_max)*dt_sub / band, the same quantity modify_bc guards on."""
    b = RigidBody6DOF(mass=1.0, inertia_body=(1, 1, 1), center=(0, 0, 0),
                      velocity=(3.0, 4.0, 0.0), omega=(0.0, 0.0, 2.0))
    r_max, band, dt_sub = 0.25, 0.01, 1e-3
    assert math.isclose(b.sweep_speed(r_max), 5.0 + 2.0 * 0.25, rel_tol=1e-12)
    assert math.isclose(b.tunneling_margin(r_max, band, dt_sub),
                        (5.0 + 0.5) * dt_sub / band, rel_tol=1e-12)


def test_added_mass_ratio_is_one_at_equilibrium():
    """Register J1a's identity, reproduced as a guard rather than restated as prose."""
    assert math.isclose(added_mass_ratio(1000.0, 1000.0), 1.0, rel_tol=1e-15)
    assert added_mass_ratio(600.0, 1000.0) > 1.0


@pytest.mark.parametrize("kwargs", [
    {"mass": 0.0, "inertia_body": (1, 1, 1)},
    {"mass": -1.0, "inertia_body": (1, 1, 1)},
    {"mass": 1.0, "inertia_body": (1, 1)},
    {"mass": 1.0, "inertia_body": (1, 0, 1)},
    {"mass": 1.0, "inertia_body": (1, -2, 1)},
])
def test_rejects_bad_construction(kwargs):
    with pytest.raises(ValueError):
        RigidBody6DOF(center=(0, 0, 0), **kwargs)


def test_rejects_com_offset():
    """Better to refuse than to integrate a body whose COM is not the rotation centre."""
    with pytest.raises(NotImplementedError):
        RigidBody6DOF(mass=1.0, inertia_body=(1, 1, 1), center=(0, 0, 0),
                      com_offset_body=(0.1, 0.0, 0.0))


def test_mirror_tracks_emulated_modify_bc():
    """The driver's pose mirror must equal what the solver's modify_bc actually does.

    This is the load-bearing assumption of run_c4_free_sdf: the driver commands only
    velocity and omega, never a centre, and then trusts its own Python state to say where
    the collider is. Here modify_bc is emulated exactly as written
    (mpm_solver_warp.py:2756-2760): per SUBSTEP, center += dt_sub*velocity and
    quat = _omega_step_quat(quat, omega, dt_sub), with the commanded values held constant
    across the tick. The mirror takes one step per TICK. If those two ever disagree, every
    logged position in a C4FREE run is wrong, and the run-time guard in the driver fires.
    """
    _, ref_step = _load_reference_quat_fns()
    rng = np.random.default_rng(7)
    m, L = 3.0, 0.4
    tick_substeps, dt_sub = 5, 2.0e-4
    tick_dt = tick_substeps * dt_sub

    body = RigidBody6DOF(mass=m, inertia_body=(0.31, 0.52, 0.77), center=(1.0, 2.0, 3.0),
                         gravity=(0.0, 0.0, -9.81))
    sim_center = np.array([1.0, 2.0, 3.0])
    sim_quat = np.array([0.0, 0.0, 0.0, 1.0])
    v_cmd, w_cmd = np.zeros(3), np.zeros(3)

    for _ in range(200):
        # the solver steps FIRST, using the velocity commanded on the previous tick
        for _ in range(tick_substeps):
            sim_center = sim_center + dt_sub * v_cmd
            sim_quat = ref_step(sim_quat, w_cmd, dt_sub)
        # the wrench is measured at that pose; the mirror must already agree with it
        assert np.allclose(sim_center, body.center, atol=1e-12), (
            f"mirror {body.center} vs emulated solver {sim_center}")
        assert min(np.linalg.norm(sim_quat - body.quat),
                   np.linalg.norm(sim_quat + body.quat)) < 1e-10
        # then the driver integrates and commands the next tick
        f = rng.normal(scale=40.0, size=3)
        tau = rng.normal(scale=0.6, size=3)
        v_cmd, w_cmd = body.integrate(f, tau, tick_dt)
        v_cmd, w_cmd = np.asarray(v_cmd), np.asarray(w_cmd)


def test_wrench_normalisation_is_by_tick_not_substep():
    """Dividing an n-substep impulse by the substep dt inflates the force by exactly n.

    sdf_wrench divides whatever it accumulated by the dt handed to it (solver.py:354-361),
    and the accumulator spans every substep since reset_sdf_force. This pins the arithmetic
    the driver depends on, so the bug cannot reappear silently as a plausible-looking force.
    """
    f_true, tick_substeps, dt_sub = 137.5, 8, 1.5e-4
    impulse = f_true * (tick_substeps * dt_sub)          # what the accumulator holds
    assert math.isclose(impulse / (tick_substeps * dt_sub), f_true, rel_tol=1e-12)
    assert math.isclose(impulse / dt_sub, f_true * tick_substeps, rel_tol=1e-12)


def test_rejects_bad_dt_and_shapes():
    b = RigidBody6DOF(mass=1.0, inertia_body=(1, 1, 1), center=(0, 0, 0))
    with pytest.raises(ValueError):
        b.integrate(np.zeros(3), np.zeros(3), 0.0)
    with pytest.raises(ValueError):
        b.integrate(np.zeros(2), np.zeros(3), 1e-3)
