from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

import numpy as np


G = 9.80665

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


def run_dashboard(
    rigid: Optional[RigidTrajectory] = None,
    inertia: Optional[np.ndarray] = None,
) -> list[InvariantResult]:
    return [
        check_mass_conservation(),
        check_jacobian_bounds(),
        check_linear_momentum(rigid),
        check_energy_monotonicity(),
        check_angular_momentum(rigid, inertia),
        check_zero_penetration(),
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
