#!/usr/bin/env python3
"""Gradio frame-review app for can-it-ford renders.

WHY THIS EXISTS, and it is the strongest single argument in the whole tooling
set. On 2026-08-14 the most valuable diagnostic of the entire night came from
Josie watching a video and asking:

    "why do the cars move at the beginning?? like that makes no phyical sense??"

That found sim_standing.py:235, settle_frames=8, a hard-coded guess giving the
vehicle 8 frames to settle as a free rigid body before recording starts, while
the stack rings with a ~100-frame period. That single observation then:
  * invalidated a 6.07x traction-margin spread (true value 1.94x),
  * INVERTED a gate-error ordering across three vehicles,
  * explained a factor-of-two gap between measured and analytic normal load,
  * and refuted a mirror-control result the coordinator had just published.

NO AUTOMATED GATE CAUGHT ANY OF IT. The human eye did. This app industrialises
that: scrub frames, see the body's own numbers beside the picture, and flag a
frame in one click. Flags land in a findings JSONL that a dispatch can read.

INSTALL (the Mac system python has no numpy; use a venv):
    python3 -m venv ~/.venvs/canford-review
    ~/.venvs/canford-review/bin/pip install gradio
    ~/.venvs/canford-review/bin/python frame_review_app.py --frames <DIR>

Core frame browsing and flagging need ONLY gradio. metrics.csv overlay is
parsed with the stdlib csv module, so numpy is never required.
"""
import argparse
import csv
import datetime
import json
import os
import sys

FLAGS_DEFAULT = os.path.expanduser(
    "~/can-it-ford/.claude/state/frame_review_flags.jsonl")

# Things a reviewer should actually look for, drawn from defects this project
# has really had. Shown in the UI so the reviewer is not staring at a blank box.
CHECKLIST = [
    "Vehicle moves before any water reaches it (settle transient, see settle_frames=8)",
    "Water is invisible or black (SSC/attenuation out of validated range)",
    "Vehicle looks like flat clay (no specular, Lambert-only shader)",
    "Ground is untextured while assets/Asphalt015_*.jpg sit unused",
    "Water surface looks blobby or jelly-like (heightfield hack, not a real surface)",
    "Vehicle overhangs the domain / sits outside the visible floor patch",
    "Particles outside the domain or clipped through geometry",
    "Motion discontinuous between adjacent frames",
    "Caption occupies more of the frame than the render",
    "Body visibly off-centre in a scene that should be symmetric",
]


def load_frames(d):
    if not os.path.isdir(d):
        return []
    fs = [os.path.join(d, f) for f in sorted(os.listdir(d))
          if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return fs


def load_metrics(path):
    """Return list of dict rows. Pure stdlib: no numpy, no pandas."""
    if not path or not os.path.isfile(path):
        return []
    try:
        with open(path, newline="", errors="replace") as fh:
            return list(csv.DictReader(fh))
    except Exception:
        return []


def metrics_for(rows, i):
    if not rows:
        return "no metrics.csv supplied"
    if i >= len(rows):
        return "frame %d has no metrics row (csv has %d)" % (i, len(rows))
    r = rows[i]
    keep = [k for k in r
            if any(s in k.lower() for s in
                   ("time", "disp", "vel", "vx", "vy", "vz", "pitch", "roll",
                    "yaw", "z", "com", "depth", "force", "fz", "fy"))]
    if not keep:
        keep = list(r)[:10]
    return "\n".join("%-22s %s" % (k, r[k]) for k in keep[:16])


def build(frames_dir, metrics_path, flags_path, run_label):
    import gradio as gr

    frames = load_frames(frames_dir)
    rows = load_metrics(metrics_path)
    if not frames:
        raise SystemExit("no frames found in %s" % frames_dir)

    def show(i):
        i = int(i)
        i = max(0, min(i, len(frames) - 1))
        return frames[i], metrics_for(rows, i), os.path.basename(frames[i])

    def flag(i, note, checks):
        i = int(i)
        rec = {
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "run": run_label,
            "frame_index": i,
            "frame_file": frames[i] if i < len(frames) else None,
            "checklist": list(checks or []),
            "note": (note or "").strip(),
            "metrics_row": rows[i] if i < len(rows) else None,
        }
        os.makedirs(os.path.dirname(flags_path), exist_ok=True)
        with open(flags_path, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        n = sum(1 for _ in open(flags_path))
        return "FLAGGED frame %d. %d flag(s) in %s" % (i, n, flags_path)

    with gr.Blocks(title="can-it-ford frame review") as app:
        gr.Markdown(
            "## can-it-ford frame review\n"
            "**%d frames** from `%s`%s\n\n"
            "The settle-transient bug was found by eye, not by any gate. "
            "Scrub, compare the numbers to the picture, and flag anything "
            "that looks physically wrong."
            % (len(frames), frames_dir,
               "  ·  metrics: `%s` (%d rows)" % (metrics_path, len(rows))
               if rows else "  ·  no metrics.csv"))
        with gr.Row():
            with gr.Column(scale=3):
                img = gr.Image(label="frame", type="filepath",
                               value=frames[0], height=560)
                idx = gr.Slider(0, len(frames) - 1, value=0, step=1,
                                label="frame index")
                with gr.Row():
                    prev = gr.Button("< prev")
                    nxt = gr.Button("next >")
                    first = gr.Button("<< first 10 frames matter most")
            with gr.Column(scale=2):
                name = gr.Textbox(label="file", value=os.path.basename(frames[0]))
                met = gr.Textbox(label="this frame's own numbers",
                                 value=metrics_for(rows, 0), lines=16)
                checks = gr.CheckboxGroup(CHECKLIST, label="what looks wrong")
                note = gr.Textbox(label="note (plain language is fine)", lines=3)
                btn = gr.Button("FLAG THIS FRAME", variant="primary")
                status = gr.Textbox(label="status", interactive=False)

        idx.change(show, [idx], [img, met, name])
        prev.click(lambda i: max(0, int(i) - 1), [idx], [idx])
        nxt.click(lambda i: min(len(frames) - 1, int(i) + 1), [idx], [idx])
        first.click(lambda: 0, None, [idx])
        btn.click(flag, [idx, note, checks], [status])
    return app


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True, help="directory of PNG frames")
    ap.add_argument("--metrics", default="", help="optional metrics.csv")
    ap.add_argument("--flags", default=FLAGS_DEFAULT)
    ap.add_argument("--label", default="", help="run label recorded with flags")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--share", action="store_true")
    a = ap.parse_args()
    label = a.label or os.path.basename(a.frames.rstrip("/"))
    try:
        app = build(a.frames, a.metrics, a.flags, label)
    except ImportError:
        sys.stderr.write(
            "gradio is not installed in this interpreter.\n"
            "  python3 -m venv ~/.venvs/canford-review\n"
            "  ~/.venvs/canford-review/bin/pip install gradio\n"
            "  ~/.venvs/canford-review/bin/python %s --frames %s\n"
            % (os.path.abspath(__file__), a.frames))
        raise SystemExit(1)
    app.launch(server_port=a.port, share=a.share, inbrowser=True)


if __name__ == "__main__":
    main()
