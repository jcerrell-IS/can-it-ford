from dataclasses import dataclass
from enum import Enum

class FailureMode(Enum):
    FORD = "FORD"
    STUCK = "STUCK"
    SLIDE = "SLIDE"
    TOPPLE = "TOPPLE"
    FLOAT = "FLOAT"

@dataclass
class FailureThresholds:
    slide_m: float
    topple_deg: float
    float_m: float
    stuck_velocity_ms: float

@dataclass
class ClassificationResult:
    mode: FailureMode
    magnitude_ratio: float
    lateral_drift_m: float
    vertical_lift_m: float
    tilt_deg: float
    forward_velocity_ms: float

def classify_failure(lateral_drift_m, vertical_lift_m, tilt_deg, forward_velocity_ms, thresholds):
    if abs(forward_velocity_ms) < thresholds.stuck_velocity_ms and abs(lateral_drift_m) < thresholds.slide_m:
        return ClassificationResult(FailureMode.STUCK, 0.0, lateral_drift_m, vertical_lift_m, tilt_deg, forward_velocity_ms)
    ratios = {
        FailureMode.SLIDE: abs(lateral_drift_m) / thresholds.slide_m,
        FailureMode.TOPPLE: abs(tilt_deg) / thresholds.topple_deg,
        FailureMode.FLOAT: abs(vertical_lift_m) / thresholds.float_m,
    }
    worst_mode, worst_ratio = max(ratios.items(), key=lambda kv: kv[1])
    if worst_ratio < 1.0:
        return ClassificationResult(FailureMode.FORD, worst_ratio, lateral_drift_m, vertical_lift_m, tilt_deg, forward_velocity_ms)
    return ClassificationResult(worst_mode, worst_ratio, lateral_drift_m, vertical_lift_m, tilt_deg, forward_velocity_ms)

def format_verdict(result):
    if result.mode == FailureMode.FORD:
        return f"FORD, worst-case margin {result.magnitude_ratio:.2f}x threshold"
    return f"{result.mode.value}, exceeds threshold by {result.magnitude_ratio:.2f}x (lateral={result.lateral_drift_m:.3f}m, vertical={result.vertical_lift_m:.3f}m, tilt={result.tilt_deg:.1f}deg, v_fwd={result.forward_velocity_ms:.3f}m/s)"
