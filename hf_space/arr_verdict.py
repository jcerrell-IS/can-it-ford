"""AR&R stationary-vehicle verdict, PRESERVED VERBATIM from origin/main:hf_space/app.py.

WHY THIS FILE EXISTS, and it is a correction to my own action.

The public Space josiecerrell/can-it-ford was serving this calculator, and on
2026-08-19 I uploaded a different application over it. That silently removed the
joint-rule fix landed by `f6348c7` (PR #11, "Space L1 used the Large 4WD
threshold for a Yaris and dropped two of three conditions") FROM A PUBLIC PAGE.
d16-landing flagged the collision on the shared board and was right; I had
already executed the option their plan labelled "do not choose without a
deliberate decision".

The logic below is copied unchanged rather than re-implemented, because the
whole point of PR #11 is that a paraphrase of this rule was wrong once already:
the earlier form tested D*V alone, against the Large 4WD number, for a Yaris.
All three conditions must hold for FORD.

This is a DIFFERENT experiment from speed_surface.py. This one carries a
FORD / NO-FORD verdict for a STATIONARY vehicle and has a validation basis in
AR&R. The load surface has a prescribed body and NO verdict. Do not merge them.
"""

import gradio as gr  # noqa: F401  (kept so this module matches its origin)


# ---------------------------------------------------------------------------
# AR&R stability limits, copied verbatim from vehicle_params.py:207-223 and
# renders/yaris_render_s1/gates.py:16-21. Do not paraphrase these numbers here:
# the demo must agree with the verdicts the repo computes, or it is worse than
# no demo at all.
#
# Source: Shand, Cox, Blacka & Smith (2011), AR&R Project 10 Stage 2,
# P10/S2/020, ISBN 978-0-85825-948-5, Table 3 "Proposed DRAFT Stability
# Criteria for Stationary Vehicles", PDF p.24 / printed p.14. These are the
# report's own DRAFT INTERIM figures for STATIONARY vehicles. They are not an
# endorsed safety standard.
# ---------------------------------------------------------------------------
AR_R = {
    "small_passenger": {
        "depth_m": 0.30, "velocity_ms": 3.0, "haz_m2s": 0.30,
        "label": "Small passenger (the 2010 Yaris used in this project)",
    },
    "large_passenger": {
        "depth_m": 0.40, "velocity_ms": 3.0, "haz_m2s": 0.45,
        "label": "Large passenger",
    },
    "large_4wd": {
        "depth_m": 0.50, "velocity_ms": 3.0, "haz_m2s": 0.60,
        "label": "Large 4WD",
    },
}

CLASS_BY_LABEL = {v["label"]: k for k, v in AR_R.items()}
DEFAULT_LABEL = AR_R["small_passenger"]["label"]

# NWS "Turn Around Don't Drown" depth guidance.
NWS_DEPTH_M = 0.15


def l0_depth_threshold(depth_m):
    return "NO-FORD" if depth_m >= NWS_DEPTH_M else "FORD"


def l1_verdict(depth_m, velocity_ms, vehicle_class):
    """Joint rule. Identical to vehicle_params.L1_verdict and gates.py:23.

    All three conditions must hold for FORD. The earlier hazard-only form of
    this demo tested D*V alone against the Large 4WD number, which returned
    FORD for cases the joint rule calls NO-FORD.
    """
    lim = AR_R[vehicle_class]
    if depth_m > lim["depth_m"]:
        return "NO-FORD"
    if velocity_ms > lim["velocity_ms"]:
        return "NO-FORD"
    if round(depth_m * velocity_ms, 6) > lim["haz_m2s"]:
        return "NO-FORD"
    return "FORD"


def _row(passed, text):
    return f"- {'PASS' if passed else 'FAIL'}: {text}"


def evaluate(depth_m, velocity_ms, class_label):
    """Evaluate flood-crossing verdicts for a STATIONARY vehicle at a given depth and velocity.

    Args:
        depth_m (float): Flood depth in metres.
        velocity_ms (float): Depth-averaged flow velocity in metres per second.
        class_label (str): AR&R vehicle class label, one of the keys of CLASS_BY_LABEL.

    Returns:
        str: A markdown report carrying the L0 depth-threshold verdict and the L1 AR&R
        joint-rule verdict. The AR&R figures are the source report's own draft interim
        criteria for stationary vehicles, not an endorsed safety standard. This is
        research demo output and not a safety determination.
    """
    vehicle_class = CLASS_BY_LABEL[class_label]
    lim = AR_R[vehicle_class]
    hazard = round(depth_m * velocity_ms, 6)

    l0 = l0_depth_threshold(depth_m)
    l1 = l1_verdict(depth_m, velocity_ms, vehicle_class)

    lines = [
        "### Inputs",
        f"- Depth D = {depth_m:.2f} m",
        f"- Velocity V = {velocity_ms:.2f} m/s",
        f"- Vehicle class: {lim['label']}",
        "",
        "### L0, static depth threshold",
        f"- Rule: D >= {NWS_DEPTH_M:.2f} m gives NO-FORD (NWS Turn Around Don't Drown)",
        f"- Verdict: **{l0}**",
        "",
        "### L1, AR&R stationary-vehicle stability, joint rule",
        "All three conditions must hold for FORD:",
        _row(depth_m <= lim["depth_m"], f"depth D = {depth_m:.2f} m, limit {lim['depth_m']:.2f} m"),
        _row(velocity_ms <= lim["velocity_ms"], f"velocity V = {velocity_ms:.2f} m/s, limit {lim['velocity_ms']:.1f} m/s"),
        _row(hazard <= lim["haz_m2s"], f"hazard D x V = {hazard:.3f} m2/s, limit {lim['haz_m2s']:.2f} m2/s"),
        f"- Verdict: **{l1}**",
        "",
        "### L2, full physics",
        "L2 is a warpmpm MPM simulation, weakly compressible Newtonian water "
        "coupled to the rigid Yaris hull. It does not run in this browser demo, "
        "and no L2 number is shown here.",
        "",
        "---",
        "*The AR&R figures are the report's own draft interim criteria for "
        "stationary vehicles, not an endorsed safety standard. This is a "
        "research demo. Do not use it to decide whether to drive into water. "
        "Turn around, don't drown.*",
    ]
    return "\n".join(lines)
