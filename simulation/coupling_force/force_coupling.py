#!/usr/bin/env python3
"""Force-based fluid-rigid coupling for warpmpm. NEW PATH, nothing existing touched.

SUPERSEDED 2026-08-13. DO NOT USE FOR NEW WORK.
=================================================================
This module is superseded by coupler.py (ForceCoupledBody, CouplingConfig,
CouplingTrace) and rigid_body.py (RigidBodyState, integrate,
inertia_from_particles); it is imported by nothing and retained for reference
only, so start from `simulation/coupling_force/__init__.py` instead.

Why this file lost, and how that was established (all verified live 2026-08-13,
none of it taken from a summary):
  - `__init__.py` exports ONLY the coupler.py/rigid_body.py API. Nothing in this
    file is re-exported, so `from simulation.coupling_force import ...` cannot
    reach CoupledRigidState, step_newton_euler or accumulate_impulse_numpy.
  - rung_b_coupled.py:37-38, the only in-repo driver, imports the surviving API.
  - A `/usr/bin/grep` for CoupledRigidState, force_coupling, step_newton_euler
    and accumulate_impulse_numpy across *.py, *.md, *.json and *.sbatch (shell
    `grep` skips gitignored paths, register H0) found NO importer anywhere. The
    only hits are this file's own definitions and two prose mentions in
    .remember/vista_session_2026-08-12.md:95,108.
  - Both clusters were checked, because an importer there would have changed the
    answer. Vista's /work/.../can-it-ford/simulation/coupling_force/ does not
    contain force_coupling.py AT ALL, while carrying __init__.py, coupler.py,
    rigid_body.py and README.md at byte sizes identical to this tree's
    pre-2026-08-13 copies (sizes compared, contents not diffed). LS6's only hit
    is a copy of this file under canitford_track1b/, self-references at the same
    line numbers, not an importer.

Two things here are NOT superseded and are worth reading before any reimplementation:
  1. The commissioning-brief correction below ("no accumulator exists anywhere"
     is too strong; :2223-2224 has one, on kinematic collider paths only). That
     correction is what makes the force path an adaptation rather than an
     invention, and it is not recorded in coupler.py.
  2. CoupledRigidState's outright REFUSAL of vehicle_params.py's {463, 1893,
     1960} box-fallback inertia, and the reason (axis-transposed, +379.2% on the
     pitch axis). coupler.py/rigid_body.py must not silently lose that guard.

Nothing here is deleted, because deletion needs explicit confirmation per
CLAUDE.md. Physics context for the path this file was written to replace:
docs/LIMITATION_COUPLING_KINEMATIC_VS_FORCE_2026-08-13.md.
=================================================================

Written 2026-08-12. Status: IMPLEMENTED AND ANALYTICALLY SELF-TESTED ON CPU.
NOT yet run against the GPU solver, NOT validated against a gated run, and no
verdict anywhere in this repo depends on it. Do not cite it as validated.

WHY THIS EXISTS
===============
The 17 canonical runs use the material-8 free-rigid path. There, the body's
velocity is set from the grid momentum it accumulated:

    v_cm_new = rigid_linear_mom[b] / M        kernels/mpm_utils.py:1434

That is a mass-weighted AVERAGE of grid velocity. No force is ever formed, so
"the coupling force" cannot be read off the path, only back-computed as m*dv/dt
(register A3). Hu, Fang, Ge, Qu, Zhu, Pradhana and Jiang 2018, ACM TOG 37(4),
doi:10.1145/3197517.3201293, describe genuine two-way MPM/rigid coupling as
requiring an ACCUMULATED CONTACT FORCE rather than velocity averaging.

THE CORRECTION THAT SHAPED THIS FILE
====================================
The commissioning brief said "no force/impulse/torque accumulator exists anywhere
in this engine". Verified live 2026-08-12 against the pinned core
third_party/mpm-engine-544c93dd-solver-core/: that is TOO STRONG. The engine
already accumulates force AND torque with a lever arm, at
kernels/mpm_solver_warp.py:2223-2224:

    wp.atomic_add(param.force,  0, imp)
    wp.atomic_add(param.torque, 0, wp.cross(rel, imp))

and a linear-only variant at :2084. What is true, and is what register A3 and A7
actually say, is narrower and more useful: those accumulators exist ONLY on the
KINEMATIC collider paths, which the 17 runs never create, and never on the
material-8 free-rigid path. So this is an ADAPTATION of a mechanism the engine
already has, not an invention. That is a much lower-risk change and it is why the
kernel below deliberately mirrors the :2223-2224 pattern instead of inventing one.

WHAT THIS MODULE DOES NOT DO
============================
- It does not modify sim_standing.py, vehicle_params.py, mpm_utils.py, or any
  kernel in third_party/. The existing kinematic path is untouched, as instructed.
- It does not wire inertia_kg_m2 or cg_height_m. Those are an axis-transposed box
  fallback (REALISM_UPGRADE_ASSESSMENT_2026-08-08 section 1: -69.2% on Ixx,
  +379.2% on Iyy against the hull truth). The inertia used here is the one the
  SOLVER already computes from the real particle cloud, mpm_solver_warp.py:859-871.
- It forms no pressure field. Register B7: warpmpm has none, at any point.
"""
from __future__ import annotations

import numpy as np

__all__ = ["accumulate_impulse_numpy", "CoupledRigidState", "step_newton_euler",
           "archimedes_equilibrium_draft", "buoyant_force_analytic"]

G_DEFAULT = 9.81          # matches the solver, core/solver.py:167-169 (register A2)


# ---------------------------------------------------------------------------
# 1. Impulse accumulation. This is the part that replaces velocity averaging.
# ---------------------------------------------------------------------------
def accumulate_impulse_numpy(node_mass, v_free, v_new, node_pos, x_cm, dt):
    """Grid-impulse -> (force, torque) about the body centre of mass.

    Pure-numpy reference for the warp kernel below, so the physics can be tested
    on a laptop with no GPU and no warp install. Mirrors
    kernels/mpm_solver_warp.py:2223-2224 exactly in form:

        imp    = m_node * (v_free - v_new)     impulse the body took from the grid
        force  = sum(imp) / dt
        torque = sum(cross(node_pos - x_cm, imp)) / dt

    v_free is the node velocity BEFORE the rigid constraint is applied, v_new the
    velocity AFTER. Their mass-weighted difference is the momentum the body
    exchanged with the fluid over one step. Dividing by dt turns an impulse into a
    force, which is the quantity the material-8 path never forms.

    Units check, because this repo requires one:
      node_mass [kg] * (v_free - v_new) [m/s] = [kg m/s] = impulse. /dt [s] -> [N].
      cross(r [m], imp [kg m/s]) = [kg m2/s] = angular impulse. /dt -> [N m]. OK.

    Sign convention: force is what the FLUID exerts ON THE BODY. If the grid node
    is slowed by the body (v_new < v_free), the body gains that momentum, so the
    force on the body is positive along the velocity difference.
    """
    node_mass = np.asarray(node_mass, dtype=np.float64).reshape(-1)
    v_free = np.asarray(v_free, dtype=np.float64).reshape(-1, 3)
    v_new = np.asarray(v_new, dtype=np.float64).reshape(-1, 3)
    node_pos = np.asarray(node_pos, dtype=np.float64).reshape(-1, 3)
    if dt <= 0.0:
        raise ValueError("dt must be positive, got %r" % dt)

    imp = node_mass[:, None] * (v_free - v_new)          # (N,3) kg m/s
    rel = node_pos - np.asarray(x_cm, dtype=np.float64).reshape(3)
    force = imp.sum(axis=0) / dt
    torque = np.cross(rel, imp).sum(axis=0) / dt
    return force, torque


def build_warp_kernel():
    """Return the warp kernel form, or raise if warp is absent.

    Kept behind a function so this module imports on a machine with no warp and
    no GPU, which is where the analytic self-test runs. The kernel body is a
    deliberate transcription of mpm_solver_warp.py:2223-2224 onto the free-rigid
    body, so the only new thing is WHICH body the impulse is credited to.
    """
    import warp as wp

    @wp.kernel
    def accumulate_rigid_impulse(
        grid_m: wp.array3d(dtype=float),
        grid_v_free: wp.array3d(dtype=wp.vec3),
        grid_v_new: wp.array3d(dtype=wp.vec3),
        grid_rigid_id: wp.array3d(dtype=int),
        x_cm: wp.array(dtype=wp.vec3),
        dx: float,
        dt: float,
        body: int,
        out_force: wp.array(dtype=wp.vec3),
        out_torque: wp.array(dtype=wp.vec3),
    ):
        i, j, k = wp.tid()
        if grid_rigid_id[i, j, k] != body:
            return
        m = grid_m[i, j, k]
        if m <= 0.0:
            return
        imp = m * (grid_v_free[i, j, k] - grid_v_new[i, j, k])
        pos = wp.vec3(float(i) * dx, float(j) * dx, float(k) * dx)
        rel = pos - x_cm[body]
        wp.atomic_add(out_force, body, imp / dt)
        wp.atomic_add(out_torque, body, wp.cross(rel, imp) / dt)

    return accumulate_rigid_impulse


# ---------------------------------------------------------------------------
# 2. Newton-Euler integration of the free body under the accumulated force.
# ---------------------------------------------------------------------------
class CoupledRigidState:
    """Free rigid body integrated from FORCE, not from averaged grid velocity.

    inertia_body MUST be the tensor the solver computes from the actual rigid
    particle cloud (mpm_solver_warp.py:859-871). Do NOT pass vehicle_params.py's
    inertia_kg_m2: it is a uniform-density box fallback whose axes are transposed
    relative to the scene, and wiring it naively gives +379.2% on the pitch axis
    (REALISM_UPGRADE_ASSESSMENT_2026-08-08 section 1). This constructor refuses
    the known-bad triple outright rather than trusting the caller.
    """

    _BOX_FALLBACK = (463.0, 1893.0, 1960.0)   # vehicle_params.py:100, do not use

    def __init__(self, mass, inertia_body, x_cm, R=None, v_cm=None, omega=None):
        inertia_body = np.asarray(inertia_body, dtype=np.float64)
        if inertia_body.shape == (3,):
            inertia_body = np.diag(inertia_body)
        if inertia_body.shape != (3, 3):
            raise ValueError("inertia_body must be (3,) or (3,3)")

        diag = np.diag(inertia_body)
        if np.allclose(sorted(diag), sorted(self._BOX_FALLBACK), rtol=1e-3):
            raise ValueError(
                "Refusing vehicle_params.py's inertia_kg_m2 box fallback "
                "%s. It reproduces exactly from box_inertia(1100, 4.30, 1.70, "
                "1.47), it overstates every principal moment of the real hull by "
                "+16.3 to +26.1 percent, and its (L,W,H)->(x,y,z) convention is "
                "transposed against the scene, whose hull long axis is Y. Pass the "
                "tensor the solver computes from the particle cloud "
                "(mpm_solver_warp.py:859-871) instead. See "
                "docs/REALISM_UPGRADE_ASSESSMENT_2026-08-08.md section 1."
                % (tuple(diag),))

        self.mass = float(mass)
        self.I_body = inertia_body
        self.I_body_inv = np.linalg.inv(inertia_body)
        self.x_cm = np.asarray(x_cm, dtype=np.float64).reshape(3).copy()
        self.R = np.eye(3) if R is None else np.asarray(R, np.float64).reshape(3, 3).copy()
        self.v_cm = np.zeros(3) if v_cm is None else np.asarray(v_cm, np.float64).reshape(3).copy()
        self.omega = np.zeros(3) if omega is None else np.asarray(omega, np.float64).reshape(3).copy()


def step_newton_euler(st: CoupledRigidState, force, torque, dt, g=G_DEFAULT,
                      gravity_axis=2):
    """Semi-implicit (symplectic) Euler step under an EXTERNAL force and torque.

    This is the substantive difference from the existing path. Instead of
    overwriting v_cm with a mass-weighted grid average, the accumulated coupling
    force enters Newton's second law alongside gravity:

        a       = F_coupling / m + g_vec
        v_cm   += a * dt
        x_cm   += v_cm * dt                 (semi-implicit: uses the NEW v)
        I_world = R I_body R^T
        omega  += I_world^-1 (tau - omega x (I_world omega)) dt
        R      += skew(omega) R dt , then re-orthogonalised

    The omega x (I omega) term is the gyroscopic coupling the existing momentum
    update gets for free by storing angular momentum; carrying it explicitly here
    is what makes this a force formulation rather than a momentum one.

    Re-orthogonalisation is by SVD polar decomposition, matching the intent of the
    polar-decomp step at mpm_utils.py:1444-1450.
    """
    force = np.asarray(force, dtype=np.float64).reshape(3)
    torque = np.asarray(torque, dtype=np.float64).reshape(3)

    g_vec = np.zeros(3)
    g_vec[gravity_axis] = -g

    a = force / st.mass + g_vec
    st.v_cm = st.v_cm + a * dt
    st.x_cm = st.x_cm + st.v_cm * dt

    I_world = st.R @ st.I_body @ st.R.T
    I_world_inv = st.R @ st.I_body_inv @ st.R.T
    gyro = np.cross(st.omega, I_world @ st.omega)
    st.omega = st.omega + I_world_inv @ (torque - gyro) * dt

    ox, oy, oz = st.omega
    skew = np.array([[0.0, -oz, oy], [oz, 0.0, -ox], [-oy, ox, 0.0]])
    R_new = st.R + skew @ st.R * dt
    U, _, Vt = np.linalg.svd(R_new)
    st.R = U @ Vt
    if np.linalg.det(st.R) < 0:          # guard against a reflection
        U[:, -1] *= -1.0
        st.R = U @ Vt
    return st


# ---------------------------------------------------------------------------
# 3. Analytic references. These are what rung (b) must be scored against.
# ---------------------------------------------------------------------------
def buoyant_force_analytic(v_submerged_m3, rho_water=1000.0, g=G_DEFAULT):
    """Archimedes: F = rho_w * g * V_displaced, upward, in newtons."""
    return rho_water * g * float(v_submerged_m3)


def archimedes_equilibrium_draft(rho_body, rho_water=1000.0):
    """Submerged VOLUME FRACTION at free-surface equilibrium.

    Floating equilibrium is rho_body * V_body = rho_w * V_submerged, so the
    submerged fraction is rho_body / rho_w. This is the rung (b) target and it is
    the reason rung (b) cannot be scored with rung (a)'s formula: for a FULLY
    submerged body the target acceleration is g(rho_w/rho_body - 1), but for a
    PARTIALLY submerged body at equilibrium the target acceleration is ZERO and
    the meaningful observable is the draft. REALISM_UPGRADE_ASSESSMENT section 2
    records that all six existing ladder rungs were scored against a placeholder
    a_ideal = -9.0, which is why no ladder number is currently citable.
    """
    f = float(rho_body) / float(rho_water)
    if f >= 1.0:
        raise ValueError(
            "rho_body %.3f >= rho_water %.3f: the body sinks, there is no floating "
            "equilibrium and the rung (b) draft target is undefined."
            % (rho_body, rho_water))
    return f


if __name__ == "__main__":
    # Self-test. Analytic only, no solver, no GPU. Run:
    #   python3 simulation/coupling_force/force_coupling.py
    print("force_coupling self-test")
    print("-" * 62)

    # (1) A body held at rest against gravity by a buoyant force must not move.
    rho_b, rho_w = 310.494, 1000.0        # canonical Yaris effective density, B5
    V = 3.542739                          # canonical hull volume, register E1
    m = rho_b * V
    frac = archimedes_equilibrium_draft(rho_b, rho_w)
    F_b = buoyant_force_analytic(frac * V, rho_w)
    W = m * G_DEFAULT
    print("submerged fraction        : %.6f  (rho_body/rho_water)" % frac)
    print("buoyancy at that draft    : %.4f N" % F_b)
    print("weight                    : %.4f N" % W)
    print("residual                  : %.3e N  (must be ~0)" % (F_b - W))
    assert abs(F_b - W) < 1e-6 * W, "equilibrium draft does not balance weight"

    st = CoupledRigidState(mass=m, inertia_body=[1501.5, 395.0, 1685.4],
                           x_cm=[0.0, 0.0, 0.0])
    dt = 1.0 / 3000.0
    for _ in range(3000):
        step_newton_euler(st, force=[0.0, 0.0, F_b], torque=[0.0, 0.0, 0.0], dt=dt)
    print("drift after 1.0 s at equil: %+.3e m  (must be ~0)" % st.x_cm[2])
    assert abs(st.x_cm[2]) < 1e-9, "body drifted while in analytic equilibrium"

    # (2) Fully submerged release must reproduce a = g(rho_w/rho_b - 1), the
    #     rung (a) formula, as a regression guard on the integrator.
    st2 = CoupledRigidState(mass=m, inertia_body=[1501.5, 395.0, 1685.4],
                            x_cm=[0.0, 0.0, 0.0])
    F_full = buoyant_force_analytic(V, rho_w)
    step_newton_euler(st2, force=[0.0, 0.0, F_full], torque=[0.0, 0.0, 0.0], dt=dt)
    a_meas = st2.v_cm[2] / dt
    a_ideal = G_DEFAULT * (rho_w / rho_b - 1.0)
    print("fully-submerged a measured: %+.6f m/s2" % a_meas)
    print("fully-submerged a ideal   : %+.6f m/s2" % a_ideal)
    print("relative error            : %.3e" % abs(a_meas / a_ideal - 1.0))
    assert abs(a_meas / a_ideal - 1.0) < 1e-12, "rung (a) formula not reproduced"

    # (3) The box-fallback inertia must be refused.
    try:
        CoupledRigidState(mass=1100.0, inertia_body=[463.0, 1893.0, 1960.0],
                          x_cm=[0, 0, 0])
    except ValueError as e:
        print("box-fallback inertia      : REFUSED, correct")
        assert "transposed" in str(e)
    else:
        raise AssertionError("box fallback was NOT refused")

    # (4) Impulse accumulator: a single node pushing +z on a body offset in +x
    #     must give +z force and a torque about -y (r x F, r=+x, F=+z -> -y).
    f, t = accumulate_impulse_numpy(
        node_mass=[2.0], v_free=[[0.0, 0.0, 1.0]], v_new=[[0.0, 0.0, 0.0]],
        node_pos=[[1.0, 0.0, 0.0]], x_cm=[0.0, 0.0, 0.0], dt=0.5)
    print("impulse accum force       : %s N   (expect [0,0,4])" % f)
    print("impulse accum torque      : %s N m (expect [0,-4,0])" % t)
    assert np.allclose(f, [0.0, 0.0, 4.0])
    assert np.allclose(t, [0.0, -4.0, 0.0])

    print("-" * 62)
    print("ALL ANALYTIC SELF-TESTS PASS.")
    print("This is CPU-only and proves the FORMULATION, not the coupling. "
          "Nothing here has touched the GPU solver or any gated run.")
