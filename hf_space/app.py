import gradio as gr

DEPTH_THRESHOLD_M = 0.15
HAZARD_THRESHOLD_M2S = 0.60
SAFE_ZONE_M2S = 0.30
L2_NOTICE = "**L2 (full physics simulation) is under active rebuild, no verdict published yet.**"


def l0_depth_threshold(depth_m):
    if depth_m >= DEPTH_THRESHOLD_M:
        return "NO-FORD"
    return "FORD"


def l1_hazard_scalar(depth_m, velocity_ms):
    return depth_m * velocity_ms


def classify_l1(hazard):
    if hazard < SAFE_ZONE_M2S:
        return "FORD", "below the 0.30 m2/s H1 generally-safe zone"
    if hazard < HAZARD_THRESHOLD_M2S:
        return "FORD", "in the 0.30 to 0.60 m2/s marginal band, still below the Large 4WD limit"
    return "NO-FORD", "at or above the 0.60 m2/s Large 4WD hazard threshold"


def evaluate(depth_m, velocity_ms):
    l0_result = l0_depth_threshold(depth_m)
    hazard = l1_hazard_scalar(depth_m, velocity_ms)
    l1_result, zone_note = classify_l1(hazard)
    lines = [
        "### Inputs",
        f"- Depth D = {depth_m:.2f} m",
        f"- Velocity V = {velocity_ms:.2f} m/s",
        "",
        "### L0, static depth threshold",
        f"- Rule: D >= {DEPTH_THRESHOLD_M:.2f} m gives NO-FORD (NWS Turn Around Don't Drown)",
        f"- Verdict: **{l0_result}**",
        "",
        "### L1, depth-velocity hazard scalar",
        f"- H = D x V = {hazard:.3f} m2/s",
        f"- Rule: H >= {HAZARD_THRESHOLD_M2S:.2f} m2/s gives NO-FORD (Large 4WD class, AR&R Shand et al. 2011, draft and interim criterion, not an endorsed safety standard)",
        f"- This value is {zone_note}.",
        f"- Verdict: **{l1_result}**",
        "",
        "### L2, full physics",
        L2_NOTICE,
    ]
    return "\n".join(lines)


with gr.Blocks(title="Can It Ford?") as demo:
    gr.Markdown("# Can It Ford?")
    gr.Markdown(
        "Enter a flood depth and a flow velocity to compare two flood-traversability checks. "
        "L0 uses depth alone. L1 uses the depth-velocity hazard scalar. Both run as pure arithmetic, live."
    )
    with gr.Row():
        depth_in = gr.Slider(0.0, 1.5, value=0.30, step=0.05, label="Flood depth D (m)")
        velocity_in = gr.Slider(0.0, 4.0, value=1.5, step=0.1, label="Flow velocity V (m/s)")
    output = gr.Markdown()
    depth_in.change(evaluate, [depth_in, velocity_in], output)
    velocity_in.change(evaluate, [depth_in, velocity_in], output)
    demo.load(evaluate, [depth_in, velocity_in], output)

if __name__ == "__main__":
    demo.launch()
