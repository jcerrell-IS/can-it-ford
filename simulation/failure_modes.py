from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vehicle_params import get_vehicle

G = 9.80665

SURGE_AXIS = 0
LONG_AXIS = 1
UP_AXIS = 2

REQUIRED_COLUMNS = ("t", "dx", "dy", "dz", "vx", "vy", "vz")
OMEGA_COLUMNS = ("wx", "wy", "wz")


class FailureMode(Enum):
    FORD = "FORD"
    STUCK = "STUCK"
    SLIDE = "SLIDE"
    TOPPLE = "TOPPLE"
    FLOAT = "FLOAT"


MODE_SEVERITY = (FailureMode.TOPPLE, FailureMode.FLOAT, FailureMode.SLIDE)


class MissingKinematicsError(ValueError):
    pass


@dataclass
class FailureThresholds:
    slide_m: float = 0.05
    slide_speed_ms: float = 0.05
    float_m: float = 0.05
    float_speed_ms: float = 0.02
    sustain_frames: int = 3


@dataclass
class Kinematics:
    t: np.ndarray
    disp: np.ndarray
    vel: np.ndarray
    omega: np.ndarray
    accel: np.ndarray
    force: np.ndarray
    mass_kg: float


@dataclass
class ClassificationResult:
    mode: FailureMode
    magnitude_ratio: float
    ratios: dict = field(default_factory=dict)
    sustained: dict = field(default_factory=dict)
    max_surge_drift_m: float = 0.0
    max_vertical_lift_m: float = 0.0
    max_speed_ms: float = 0.0
    peak_surge_force_n: float = 0.0
    peak_vertical_force_n: float = 0.0
    peak_surge_accel_g: float = 0.0
    weight_n: float = 0.0
    ssf: float = 0.0


def load_timeseries(path) -> dict:
    path = Path(path)
    with open(path) as fh:
        header = fh.readline().strip().lstrip("#").strip().split(",")
    data = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2)
    if data.shape[1] != len(header):
        raise ValueError(
            f"{path.name}: header has {len(header)} names but data has {data.shape[1]} columns"
        )
    cols = {name.strip(): data[:, i] for i, name in enumerate(header)}
    missing = [c for c in REQUIRED_COLUMNS if c not in cols]
    if missing:
        raise MissingKinematicsError(
            f"{path.name}: missing {missing}. This timeseries predates the FloodHistory.to_csv "
            f"velocity columns; net force cannot be computed from it. Regenerate the run."
        )
    return cols


def kinematics_from_columns(cols: dict, mass_kg: float) -> Kinematics:
    t = np.asarray(cols["t"], dtype=float)
    if t.size < 2:
        raise ValueError("need at least two frames to differentiate velocity")
    if not np.all(np.diff(t) > 0):
        raise ValueError("time column must be strictly increasing")
    disp = np.column_stack([cols["dx"], cols["dy"], cols["dz"]]).astype(float)
    vel = np.column_stack([cols["vx"], cols["vy"], cols["vz"]]).astype(float)
    if all(c in cols for c in OMEGA_COLUMNS):
        omega = np.column_stack([cols[c] for c in OMEGA_COLUMNS]).astype(float)
    else:
        omega = np.zeros_like(vel)
    accel = np.gradient(vel, t, axis=0)
    force = mass_kg * accel
    return Kinematics(t=t, disp=disp, vel=vel, omega=omega, accel=accel,
                      force=force, mass_kg=float(mass_kg))


def _sustained(mask: np.ndarray, frames: int) -> bool:
    if frames <= 1:
        return bool(np.any(mask))
    run = 0
    for flag in np.asarray(mask, dtype=bool):
        run = run + 1 if flag else 0
        if run >= frames:
            return True
    return False


def _safe_ratio(value: float, threshold: float) -> float:
    if threshold <= 0:
        return float("inf") if value > 0 else 0.0
    return float(value) / float(threshold)


def classify_kinematics(kin: Kinematics, ssf: float,
                        thresholds: FailureThresholds | None = None) -> ClassificationResult:
    th = thresholds or FailureThresholds()

    surge_drift = np.abs(kin.disp[:, SURGE_AXIS])
    lift = kin.disp[:, UP_AXIS]
    surge_speed = np.abs(kin.vel[:, SURGE_AXIS])
    rise_speed = kin.vel[:, UP_AXIS]
    surge_accel_g = np.abs(kin.accel[:, SURGE_AXIS]) / G
    surge_force = kin.force[:, SURGE_AXIS]
    vertical_force = kin.force[:, UP_AXIS]
    speed = np.linalg.norm(kin.vel, axis=1)
    weight_n = kin.mass_kg * G

    slide_hold = _sustained(
        (surge_drift >= th.slide_m) & (surge_speed >= th.slide_speed_ms), th.sustain_frames
    )
    float_hold = _sustained(
        (lift >= th.float_m) & (rise_speed >= th.float_speed_ms), th.sustain_frames
    )
    topple_hold = _sustained(surge_accel_g >= ssf, th.sustain_frames)

    driven_downstream = float(np.max(np.abs(surge_force))) > 0.0
    driven_upward = float(np.max(vertical_force)) > 0.0

    ratios = {
        FailureMode.SLIDE: _safe_ratio(float(np.max(surge_drift)), th.slide_m),
        FailureMode.TOPPLE: _safe_ratio(float(np.max(surge_accel_g)), ssf),
        FailureMode.FLOAT: _safe_ratio(float(np.max(lift)), th.float_m),
    }
    sustained = {
        FailureMode.SLIDE: bool(slide_hold and driven_downstream),
        FailureMode.TOPPLE: bool(topple_hold),
        FailureMode.FLOAT: bool(float_hold and driven_upward),
    }

    common = dict(
        ratios=ratios,
        sustained=sustained,
        max_surge_drift_m=float(np.max(surge_drift)),
        max_vertical_lift_m=float(np.max(lift)),
        max_speed_ms=float(np.max(speed)),
        peak_surge_force_n=float(np.max(np.abs(surge_force))),
        peak_vertical_force_n=float(np.max(vertical_force)),
        peak_surge_accel_g=float(np.max(surge_accel_g)),
        weight_n=float(weight_n),
        ssf=float(ssf),
    )

    for mode in MODE_SEVERITY:
        if sustained[mode]:
            return ClassificationResult(mode=mode, magnitude_ratio=ratios[mode], **common)

    worst = max(ratios.values()) if ratios else 0.0
    return ClassificationResult(mode=FailureMode.FORD, magnitude_ratio=worst, **common)


def classify_timeseries(path, mass_kg: float, ssf: float,
                        thresholds: FailureThresholds | None = None) -> ClassificationResult:
    cols = load_timeseries(path)
    kin = kinematics_from_columns(cols, mass_kg)
    return classify_kinematics(kin, ssf, thresholds)


def classify_manifest(manifest_path, thresholds: FailureThresholds | None = None) -> list:
    manifest_path = Path(manifest_path)
    data_dir = manifest_path.parent
    out = []
    with open(manifest_path, newline="") as fh:
        for row in csv.DictReader(fh):
            run_id = row["run_id"]
            ts = data_dir / f"{run_id}_timeseries.csv"
            record = {
                "run_id": run_id,
                "vehicle_class": row.get("vehicle_class", ""),
                "params_class": row.get("params_class", ""),
                "depth_m": float(row["depth_m"]),
                "velocity_ms": float(row["velocity_ms"]),
                "density_plausible": row.get("density_plausible", ""),
            }
            if not ts.exists():
                record["error"] = "timeseries missing"
                out.append(record)
                continue
            ssf = get_vehicle(row["params_class"])["ssf"]
            try:
                res = classify_timeseries(ts, float(row["vehicle_mass_kg"]), ssf, thresholds)
            except MissingKinematicsError as exc:
                record["error"] = str(exc)
                out.append(record)
                continue
            record.update({
                "mode": res.mode.value,
                "magnitude_ratio": round(res.magnitude_ratio, 4),
                "max_surge_drift_m": round(res.max_surge_drift_m, 4),
                "max_vertical_lift_m": round(res.max_vertical_lift_m, 4),
                "max_speed_ms": round(res.max_speed_ms, 4),
                "peak_surge_force_n": round(res.peak_surge_force_n, 2),
                "peak_vertical_force_n": round(res.peak_vertical_force_n, 2),
                "peak_surge_accel_g": round(res.peak_surge_accel_g, 4),
                "weight_n": round(res.weight_n, 2),
                "ssf": res.ssf,
            })
            out.append(record)
    return out


def format_verdict(result: ClassificationResult) -> str:
    if result.mode == FailureMode.FORD:
        return (f"FORD, worst-case margin {result.magnitude_ratio:.2f}x threshold "
                f"(surge drift={result.max_surge_drift_m:.3f}m, lift={result.max_vertical_lift_m:.3f}m, "
                f"peak surge accel={result.peak_surge_accel_g:.3f}g vs SSF {result.ssf:.2f})")
    return (f"{result.mode.value}, exceeds threshold by {result.magnitude_ratio:.2f}x "
            f"(surge drift={result.max_surge_drift_m:.3f}m, lift={result.max_vertical_lift_m:.3f}m, "
            f"peak surge force={result.peak_surge_force_n:.1f}N vs weight {result.weight_n:.1f}N, "
            f"peak surge accel={result.peak_surge_accel_g:.3f}g vs SSF {result.ssf:.2f})")
