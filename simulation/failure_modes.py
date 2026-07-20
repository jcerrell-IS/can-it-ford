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
    STUCK = "STUCK"
    SLIDE = "SLIDE"
    TOPPLE = "TOPPLE"
    FLOAT = "FLOAT"


MODE_SEVERITY = (FailureMode.SLIDE, FailureMode.TOPPLE, FailureMode.FLOAT)

MODE_UNITS = {
    FailureMode.SLIDE: "m",
    FailureMode.TOPPLE: "g",
    FailureMode.FLOAT: "m",
}


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
    first_reached_frame: int | None = None
    first_reached_time: float | None = None
    magnitude_ratio: float | None = None
    percent_over_threshold: float | None = None
    absolute_over_threshold: float | None = None
    threshold_value: float | None = None
    threshold_units: str = ""
    ratios: dict = field(default_factory=dict)
    first_index: dict = field(default_factory=dict)
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


def _first_sustained_index(mask: np.ndarray, frames: int) -> int:
    mask = np.asarray(mask, dtype=bool)
    if frames <= 1:
        idx = int(np.argmax(mask))
        return idx if mask.size and mask[idx] else -1
    run = 0
    start = -1
    for i, flag in enumerate(mask):
        if flag:
            if run == 0:
                start = i
            run += 1
            if run >= frames:
                return start
        else:
            run = 0
    return -1


def _sustained(mask: np.ndarray, frames: int) -> bool:
    return _first_sustained_index(mask, frames) >= 0


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

    driven_downstream = float(np.max(np.abs(surge_force))) > 0.0
    driven_upward = float(np.max(vertical_force)) > 0.0

    slide_idx = _first_sustained_index(
        (surge_drift >= th.slide_m) & (surge_speed >= th.slide_speed_ms), th.sustain_frames
    )
    topple_idx = _first_sustained_index(surge_accel_g >= ssf, th.sustain_frames)
    float_idx = _first_sustained_index(
        (lift >= th.float_m) & (rise_speed >= th.float_speed_ms), th.sustain_frames
    )

    first_index = {
        FailureMode.SLIDE: slide_idx,
        FailureMode.TOPPLE: topple_idx,
        FailureMode.FLOAT: float_idx,
    }
    sustained = {
        FailureMode.SLIDE: bool(slide_idx >= 0 and driven_downstream),
        FailureMode.TOPPLE: bool(topple_idx >= 0),
        FailureMode.FLOAT: bool(float_idx >= 0 and driven_upward),
    }

    max_surge_drift = float(np.max(surge_drift))
    max_lift = float(np.max(lift))
    max_surge_accel_g = float(np.max(surge_accel_g))

    mode_value = {
        FailureMode.SLIDE: max_surge_drift,
        FailureMode.TOPPLE: max_surge_accel_g,
        FailureMode.FLOAT: max_lift,
    }
    mode_threshold = {
        FailureMode.SLIDE: th.slide_m,
        FailureMode.TOPPLE: ssf,
        FailureMode.FLOAT: th.float_m,
    }
    ratios = {m: _safe_ratio(mode_value[m], mode_threshold[m]) for m in MODE_SEVERITY}

    common = dict(
        ratios=ratios,
        first_index=first_index,
        sustained=sustained,
        max_surge_drift_m=max_surge_drift,
        max_vertical_lift_m=max_lift,
        max_speed_ms=float(np.max(speed)),
        peak_surge_force_n=float(np.max(np.abs(surge_force))),
        peak_vertical_force_n=float(np.max(vertical_force)),
        peak_surge_accel_g=max_surge_accel_g,
        weight_n=float(weight_n),
        ssf=float(ssf),
    )

    reached = [m for m in MODE_SEVERITY if sustained[m]]
    if not reached:
        return ClassificationResult(mode=FailureMode.STUCK, **common)

    mode = reached[-1]
    value = mode_value[mode]
    thr = mode_threshold[mode]
    idx = first_index[mode]
    percent_over = ((value / thr) - 1.0) * 100.0 if thr > 0 else float("inf")
    return ClassificationResult(
        mode=mode,
        first_reached_frame=int(idx),
        first_reached_time=float(kin.t[idx]),
        magnitude_ratio=ratios[mode],
        percent_over_threshold=float(percent_over),
        absolute_over_threshold=float(value - thr),
        threshold_value=float(thr),
        threshold_units=MODE_UNITS[mode],
        **common,
    )


def classify_timeseries(path, mass_kg: float, ssf: float,
                        thresholds: FailureThresholds | None = None) -> ClassificationResult:
    cols = load_timeseries(path)
    kin = kinematics_from_columns(cols, mass_kg)
    return classify_kinematics(kin, ssf, thresholds)


def _round(value, ndigits):
    return round(value, ndigits) if value is not None else None


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
                "first_reached_frame": res.first_reached_frame,
                "first_reached_time_s": _round(res.first_reached_time, 4),
                "percent_over_threshold": _round(res.percent_over_threshold, 2),
                "absolute_over_threshold": _round(res.absolute_over_threshold, 6),
                "threshold_value": _round(res.threshold_value, 4),
                "threshold_units": res.threshold_units,
                "magnitude_ratio": _round(res.magnitude_ratio, 4),
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
    if result.mode == FailureMode.STUCK:
        return (f"STUCK (stable), no instability criterion tripped "
                f"(max surge drift={result.max_surge_drift_m:.4f}m, "
                f"max lift={result.max_vertical_lift_m:.4f}m, "
                f"peak surge accel={result.peak_surge_accel_g:.3f}g vs SSF {result.ssf:.2f})")
    unit = result.threshold_units
    if unit == "m":
        absolute = f"{result.absolute_over_threshold * 1000.0:.4g} mm"
    else:
        absolute = f"{result.absolute_over_threshold:.4g} g"
    return (f"{result.mode.value} first reached at frame {result.first_reached_frame} "
            f"(t={result.first_reached_time:.4f}s), exceeds criterion by "
            f"{result.percent_over_threshold:.2f}% ({absolute} past "
            f"{result.threshold_value:.4g}{unit})")
