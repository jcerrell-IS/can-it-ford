import gradio as gr

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


with gr.Blocks(title="Can It Ford?") as demo:
    gr.Markdown("# Can It Ford?")
    gr.Markdown(
        "Enter a flood depth and a flow velocity to compare two flood-traversability "
        "checks. L0 uses depth alone. L1 applies the AR&R joint stability rule for the "
        "selected vehicle class. Both run as pure arithmetic, live."
    )
    with gr.Row():
        depth_in = gr.Slider(0.0, 1.5, value=0.30, step=0.05, label="Flood depth D (m)")
        velocity_in = gr.Slider(0.0, 4.0, value=1.5, step=0.1, label="Flow velocity V (m/s)")
    class_in = gr.Radio(
        choices=list(CLASS_BY_LABEL.keys()),
        value=DEFAULT_LABEL,
        label="AR&R vehicle class",
    )
    output = gr.Markdown()

    inputs = [depth_in, velocity_in, class_in]
    depth_in.change(evaluate, inputs, output)
    velocity_in.change(evaluate, inputs, output)
    class_in.change(evaluate, inputs, output)
    demo.load(evaluate, inputs, output)

if __name__ == "__main__":
    demo.launch()
