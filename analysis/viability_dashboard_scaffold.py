from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

import numpy as np


# Was 9.80665, the last file in the tree still carrying the pre-unification value. Every
# other G in the tree is 9.81 (four_rung_ladder, gates_both_scenarios, semi_empirical_
# baseline, test_rigid_body, failure_modes, validate_coupling_force), and failure_modes.py:14
# records that unification as done on 2026-08-12 against the solver. This file was missed.
# The constant was dead here until check_buoyancy_consistency below, so correcting it
# changes no existing result; leaving it would have put a 0.0342 percent fork straight into
# rho*V*g. Verified by git grep over tracked files at this HEAD, not from memory.
G = 9.81

RHO_WATER = 1000.0

RIGID_REQUIRED_COLUMNS = ("t", "dx", "dy", "dz", "vx", "vy", "vz")
OMEGA_COLUMNS = ("wx", "wy", "wz")

MOMENTUM_JUMP_REL_TOL = 0.5
ANGMOM_JUMP_REL_TOL = 0.5
JACOBIAN_MIN = 0.1
JACOBIAN_MAX = 10.0
MASS_REL_TOL = 1e-4
ENERGY_CREATION_REL_TOL = 1e-3
PENETRATION_TOL_M = -1e-3

ANGULAR_MOMENTUM_CONFIRMED = False


class Status(str, Enum):
    NOT_IMPLEMENTED = "not_implemented"
    HELD = "held"
    PASS = "pass"
    FAIL = "fail"
    INDETERMINATE = "indeterminate"


class Coverage(str, Enum):
    RIGID_LIVE = "rigid_live"
    RIGID_HELD = "rigid_held"
    CONTINUUM_STUB = "continuum_stub"


class MissingKinematicsError(ValueError):
    pass


@dataclass
class RigidTrajectory:
    t: np.ndarray
    disp: np.ndarray
    vel: np.ndarray
    omega: Optional[np.ndarray]
    mass_kg: float
    run_tag: str = ""


@dataclass
class InvariantResult:
    name: str
    paper_constraint: str
    coverage: Coverage
    status: Status
    value: Optional[float] = None
    tolerance: Optional[float] = None
    provenance: str = ""
    note: str = ""
    detail: dict = field(default_factory=dict)


def load_rigid_timeseries(path, mass_kg: float, run_tag: str = "") -> RigidTrajectory:
    path = Path(path)
    with open(path) as fh:
        header = fh.readline().strip().lstrip("#").strip().split(",")
    data = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2)
    if data.shape[1] != len(header):
        raise ValueError(
            f"{path.name}: header has {len(header)} names but data has {data.shape[1]} columns"
        )
    cols = {name.strip(): data[:, i] for i, name in enumerate(header)}
    missing = [c for c in RIGID_REQUIRED_COLUMNS if c not in cols]
    if missing:
        raise MissingKinematicsError(
            f"{path.name}: missing {missing}. This timeseries predates the FloodHistory.to_csv "
            f"velocity columns; rigid momentum cannot be computed from it. Regenerate the run."
        )
    t = cols["t"].astype(float)
    if t.size < 2:
        raise ValueError("need at least two frames to compute momentum")
    if not np.all(np.diff(t) > 0):
        raise ValueError("time column must be strictly increasing")
    disp = np.column_stack([cols["dx"], cols["dy"], cols["dz"]]).astype(float)
    vel = np.column_stack([cols["vx"], cols["vy"], cols["vz"]]).astype(float)
    if all(c in cols for c in OMEGA_COLUMNS):
        omega = np.column_stack([cols[c] for c in OMEGA_COLUMNS]).astype(float)
    else:
        omega = None
    return RigidTrajectory(t=t, disp=disp, vel=vel, omega=omega, mass_kg=float(mass_kg), run_tag=run_tag)


def inertia_box(mass_kg: float, l_m: float, w_m: float, h_m: float) -> np.ndarray:
    ixx = mass_kg / 12.0 * (w_m ** 2 + h_m ** 2)
    iyy = mass_kg / 12.0 * (l_m ** 2 + h_m ** 2)
    izz = mass_kg / 12.0 * (l_m ** 2 + w_m ** 2)
    return np.diag([ixx, iyy, izz])


def _max_relative_jump(series: np.ndarray) -> float:
    mag = np.linalg.norm(series, axis=1)
    scale = float(np.max(mag))
    if scale == 0.0:
        return 0.0
    jumps = np.linalg.norm(np.diff(series, axis=0), axis=1)
    return float(np.max(jumps) / scale)


def rigid_linear_momentum(traj: RigidTrajectory) -> dict:
    p = traj.mass_kg * traj.vel
    a = np.gradient(traj.vel, traj.t, axis=0)
    f = traj.mass_kg * a
    return {"t": traj.t, "p": p, "a": a, "f": f}


def rigid_angular_momentum(traj: RigidTrajectory, inertia: np.ndarray) -> dict:
    if traj.omega is None:
        raise MissingKinematicsError(
            "angular momentum requires logged omega columns (wx, wy, wz); regenerate the run"
        )
    L = traj.omega @ inertia.T
    tau = np.gradient(L, traj.t, axis=0)
    return {"t": traj.t, "L": L, "tau": tau}


def check_mass_conservation(continuum: object = None) -> InvariantResult:
    return InvariantResult(
        name="mass_conservation",
        paper_constraint="mass",
        coverage=Coverage.CONTINUUM_STUB,
        status=Status.NOT_IMPLEMENTED,
        tolerance=MASS_REL_TOL,
        provenance="continuum: per-step particle count x particle_mass_kg; not logged per step; Genesis MPM extraction API unverified from Mac",
        note="prior audit mass check retracted as tautological (ad0174e); needs new instrumentation on future runs",
    )


def check_jacobian_bounds(continuum: object = None) -> InvariantResult:
    return InvariantResult(
        name="mpm_jacobian_bounds",
        paper_constraint="kinematics",
        coverage=Coverage.CONTINUUM_STUB,
        status=Status.NOT_IMPLEMENTED,
        tolerance=JACOBIAN_MAX,
        provenance="continuum: per-step deformation gradient F from Genesis MPM solver; grep mpm_solver.py inside container to confirm accessor",
        note="det(F) expected within [JACOBIAN_MIN, JACOBIAN_MAX]; thresholds are unvalidated placeholders; flags element inversion at det(F)<=0",
    )


def check_linear_momentum(traj: Optional[RigidTrajectory]) -> InvariantResult:
    if traj is None:
        return InvariantResult(
            name="linear_momentum",
            paper_constraint="momentum",
            coverage=Coverage.RIGID_LIVE,
            status=Status.NOT_IMPLEMENTED,
            tolerance=MOMENTUM_JUMP_REL_TOL,
            provenance="track1 timeseries vx,vy,vz + manifest vehicle_mass_kg",
            note="no rigid trajectory supplied",
        )
    kin = rigid_linear_momentum(traj)
    p = kin["p"]
    finite = bool(np.all(np.isfinite(p)))
    jump = _max_relative_jump(p)
    if not finite or jump > MOMENTUM_JUMP_REL_TOL:
        status = Status.FAIL
    else:
        status = Status.PASS
    return InvariantResult(
        name="linear_momentum",
        paper_constraint="momentum",
        coverage=Coverage.RIGID_LIVE,
        status=status,
        value=jump,
        tolerance=MOMENTUM_JUMP_REL_TOL,
        provenance="track1 timeseries vx,vy,vz + manifest vehicle_mass_kg",
        note="rigid-body momentum continuity and finiteness only; closed-system conservation additionally needs water momentum (continuum instrumentation) to close the balance",
        detail={"peak_force_n": float(np.max(np.linalg.norm(kin["f"], axis=1)))},
    )


def check_energy_monotonicity(continuum: object = None) -> InvariantResult:
    return InvariantResult(
        name="energy_monotonicity",
        paper_constraint="energy",
        coverage=Coverage.CONTINUUM_STUB,
        status=Status.NOT_IMPLEMENTED,
        tolerance=ENERGY_CREATION_REL_TOL,
        provenance="continuum: per-step particle KE (vel+mass), PE (height), strain (F); none logged per step",
        note="total mechanical energy must not rise beyond forcing input within tolerance; needs new instrumentation",
    )


def check_angular_momentum(
    traj: Optional[RigidTrajectory] = None,
    inertia: Optional[np.ndarray] = None,
) -> InvariantResult:
    if not ANGULAR_MOMENTUM_CONFIRMED:
        return InvariantResult(
            name="angular_momentum",
            paper_constraint="momentum/SE3",
            coverage=Coverage.RIGID_HELD,
            status=Status.HELD,
            tolerance=ANGMOM_JUMP_REL_TOL,
            provenance="track1 omega columns (wx,wy,wz, not yet logged) + inertia_box(mass, bbox_l/w/h from manifest)",
            note="sixth-slot invariant unconfirmed: angular momentum vs buoyancy, awaiting Hassan; inertia_box assumes uniform-density box",
        )
    if traj is None or inertia is None:
        return InvariantResult(
            name="angular_momentum",
            paper_constraint="momentum/SE3",
            coverage=Coverage.RIGID_HELD,
            status=Status.NOT_IMPLEMENTED,
            tolerance=ANGMOM_JUMP_REL_TOL,
            provenance="track1 omega (wx,wy,wz) + inertia_box(mass, bbox)",
            note="trajectory or inertia tensor not supplied",
        )
    ang = rigid_angular_momentum(traj, inertia)
    L = ang["L"]
    finite = bool(np.all(np.isfinite(L)))
    jump = _max_relative_jump(L)
    status = Status.PASS if finite and jump <= ANGMOM_JUMP_REL_TOL else Status.FAIL
    return InvariantResult(
        name="angular_momentum",
        paper_constraint="momentum/SE3",
        coverage=Coverage.RIGID_HELD,
        status=status,
        value=jump,
        tolerance=ANGMOM_JUMP_REL_TOL,
        provenance="track1 omega (wx,wy,wz) + inertia_box(mass, bbox)",
        note="inertia assumes uniform-density box from manifest bbox; sixth-slot still unconfirmed vs buoyancy",
        detail={"peak_torque_nm": float(np.max(np.linalg.norm(ang["tau"], axis=1)))},
    )


def check_zero_penetration(continuum: object = None) -> InvariantResult:
    return InvariantResult(
        name="zero_penetration",
        paper_constraint="contact",
        coverage=Coverage.CONTINUUM_STUB,
        status=Status.NOT_IMPLEMENTED,
        tolerance=PENETRATION_TOL_M,
        provenance="continuum: per-step water pos (get_particles_pos) + vehicle pose/SDF from simulation/box_sdf_collider_setup.py; neither logged per step",
        note="signed distance of each water particle to rigid body must stay >= PENETRATION_TOL_M; most implementation-heavy of the six",
    )


@dataclass
class BuoyancyCase:
    """One measured buoyant force, plus the geometry needed to recompute it analytically.

    ``submerged_volume_m3`` is the DISPLACED volume, not the body's total volume. For a
    partially submerged body those differ, and scoring a partial run against the fully
    submerged analytic is the single easiest way to manufacture a large fake deficit.
    """
    run_tag: str
    f_measured_n: float
    submerged_volume_m3: float
    rho_fluid: float = RHO_WATER
    g: float = G
    provenance: str = ""


def submerged_volume_box(length_m: float, width_m: float, submerged_height_m: float) -> float:
    """Displaced volume of a box floating with ``submerged_height_m`` below the surface."""
    for name, v in (("length_m", length_m), ("width_m", width_m),
                    ("submerged_height_m", submerged_height_m)):
        if not np.isfinite(v) or v < 0.0:
            raise ValueError(f"{name} must be finite and non-negative, got {v}")
    return float(length_m) * float(width_m) * float(submerged_height_m)


def check_buoyancy_consistency(case: Optional[BuoyancyCase] = None) -> InvariantResult:
    """Recompute Archimedes from geometry and rho, and REPORT the error. No verdict.

    Deliberately carries no tolerance. The measured deficit on this path is a moving
    target: a separate dispatch is running the newly validated force-coupled body on a
    canonical arm, and a check that asserted today's figures as ground truth would go
    stale the moment those land and would then fail for the wrong reason. So this returns
    Status.INDETERMINATE with the error as its value, and whoever reads the certificate
    decides. That is the point of it, not a gap in it.

    What it does remove is the manual step: the analytic reference is recomputed from
    rho * V_submerged * g every time rather than being re-derived by hand and pasted into
    a doc, which is where the stale-number failures in this project have actually come
    from.

    Sign convention matches the engine's, so a body being pushed up reads a POSITIVE
    f_measured_n; the relative error is (measured - analytic) / analytic, so a shortfall
    is negative.
    """
    if case is None:
        return InvariantResult(
            name="buoyancy_consistency",
            paper_constraint="archimedes",
            coverage=Coverage.RIGID_HELD,
            status=Status.NOT_IMPLEMENTED,
            tolerance=None,
            provenance="needs a BuoyancyCase: measured force + displaced volume + rho + g",
            note="no case supplied; nothing measured",
        )

    if not np.isfinite(case.submerged_volume_m3) or case.submerged_volume_m3 < 0.0:
        raise ValueError(f"submerged_volume_m3 must be finite and non-negative, "
                         f"got {case.submerged_volume_m3}")
    if not np.isfinite(case.rho_fluid) or case.rho_fluid <= 0.0:
        raise ValueError(f"rho_fluid must be finite and positive, got {case.rho_fluid}")
    if not np.isfinite(case.g) or case.g <= 0.0:
        raise ValueError(f"g must be finite and positive, got {case.g}")
    if not np.isfinite(case.f_measured_n):
        raise ValueError(f"f_measured_n must be finite, got {case.f_measured_n}")

    f_analytic = case.rho_fluid * case.submerged_volume_m3 * case.g
    detail = {
        "run_tag": case.run_tag,
        "f_measured_n": float(case.f_measured_n),
        "f_analytic_n": float(f_analytic),
        "submerged_volume_m3": float(case.submerged_volume_m3),
        "rho_fluid": float(case.rho_fluid),
        "g": float(case.g),
    }

    if f_analytic == 0.0:
        return InvariantResult(
            name="buoyancy_consistency",
            paper_constraint="archimedes",
            coverage=Coverage.RIGID_LIVE,
            status=Status.INDETERMINATE,
            value=None,
            tolerance=None,
            provenance=case.provenance or "measured force + displaced volume",
            note="displaced volume is zero, so there is no analytic reference to divide "
                 "by; the body is not in contact with the fluid",
            detail=detail,
        )

    err_rel = (case.f_measured_n - f_analytic) / f_analytic
    detail["error_rel"] = float(err_rel)
    detail["error_pct"] = float(100.0 * err_rel)
    return InvariantResult(
        name="buoyancy_consistency",
        paper_constraint="archimedes",
        coverage=Coverage.RIGID_LIVE,
        status=Status.INDETERMINATE,
        value=float(100.0 * err_rel),
        tolerance=None,
        provenance=case.provenance or "measured force + displaced volume",
        note="reported, not judged: no tolerance is asserted because the measured deficit "
             "on this path is still moving. Value is percent error vs rho*V_sub*g",
        detail=detail,
    )


def run_dashboard(
    rigid: Optional[RigidTrajectory] = None,
    inertia: Optional[np.ndarray] = None,
    buoyancy: Optional[BuoyancyCase] = None,
) -> list[InvariantResult]:
    return [
        check_mass_conservation(),
        check_jacobian_bounds(),
        check_linear_momentum(rigid),
        check_energy_monotonicity(),
        check_angular_momentum(rigid, inertia),
        check_zero_penetration(),
        check_buoyancy_consistency(buoyancy),
    ]


def format_certificate(results: Sequence[InvariantResult]) -> str:
    header = f"{'invariant':<22}{'constraint':<16}{'coverage':<16}{'status':<18}{'value':<12}{'tol':<12}"
    lines = [header, "-" * len(header)]
    for r in results:
        value = "" if r.value is None else f"{r.value:.4g}"
        tol = "" if r.tolerance is None else f"{r.tolerance:.4g}"
        lines.append(
            f"{r.name:<22}{r.paper_constraint:<16}{r.coverage.value:<16}{r.status.value:<18}{value:<12}{tol:<12}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_certificate(run_dashboard()))
