#!/usr/bin/env python3
"""Two figures for results that currently exist only as numbers in commit bodies.

SCOPE. Figure layer only. Reads committed CSVs and committed run metrics, applies
the project's OWN already-committed metric functions, and draws. It computes no
force, runs no simulation, changes no verdict and writes into no canonical store.
Engine for every run drawn here is warpmpm, not Genesis.

TWO SEPARATE RUN FAMILIES, AND CONFLATING THEM IS THE EASIEST MISTAKE TO MAKE.

  FIGURE A is the CANONICAL YARIS HULL carrying an AR&R large_4wd class MASS of
  2337 kg. It is NOT a Silverado. Verified live from data/all_runs_inventory.csv:
  g48/g64/g96_m2337 all record hull_m3 = 3.542739, the canonical Yaris hull, with
  realized densities 642.8 / 658.1 / 663.6 kg/m3. The mass comes from the AR&R
  class table, not from any vehicle deck.

  FIGURE B is the REAL SILVERADO HULL at 2270 kg, its deck-header mass, from the
  non-canonical Rogue/Silverado grid sweep. Different hull, different mass,
  different batch. The two figures agree in direction and must not be merged into
  one series.

WHAT FIGURE A SHOWS. The SLIDE criterion at simulation/failure_modes.py:181-183
is a JOINT, SUSTAINED condition: |surge drift| >= 0.05 m AND |surge speed| >=
0.05 m/s, held for 3 consecutive frames. So a verdict has a margin measured in
FRAMES, and for the canonical 2337 kg arm that margin collapses under refinement
from 8 frames at g48 to 0 frames at g128. Zero margin means the run clears the
criterion by exactly the minimum: delete one frame and the published verdict
changes.

A NAMING CORRECTION THIS FIGURE HAS TO MAKE. The series 11 -> 10 -> 4 is
`longest_joint_frames`, not `margin_frames`. `margin_frames` is that number minus
the 3 required frames, i.e. 8 -> 7 -> 1. Both columns are in
data/slide_verdict_fragility_2026-08-13.csv and its own docstring uses the
correct names; a later summary relabelled the first series with the second name.
Both are drawn here, labelled, so the confusion cannot survive the figure.

WHAT FIGURE B SHOWS, and it is not what a reader expects. At g128 the Silverado's
PEAK drift ratio is 1.556 and its PEAK speed ratio is 4.087, so BOTH exceed
threshold, and the classified mode is still STUCK. Nothing failed to exceed a
threshold; the two peaks simply never co-occur for 3 consecutive frames. This is
the trap CLAUDE.md item 12(a) records in general form: triggered_* is the verdict
and ratio_* is a peak magnitude, and filtering on ratio >= 1 reports events that
never happened.

PROVENANCE OF THE g128 POINTS. g48/g64/g96 come from the committed
data/slide_verdict_fragility_2026-08-13.csv, whose own docstring records that six
of its rows (including g96_m2337) cannot be reproduced against the canonical
store, because job 866887 overwrote those run directories on 2026-07-26. The g128
points, and an in-job g96 CONTROL, are computed HERE from the metrics.csv files
committed on branch claude/rtfd-test-phase-1-4-569130, using the same
longest_joint_run() and k_crit() functions from analysis/slide_verdict_fragility.py
rather than re-implementations. That branch is on origin, verified 2026-08-14, so
this is not a one-disk dependency.

THE CONTROL IS THE POINT OF INCLUDING g96 TWICE. The g128 job ran its own g96
arm on LS6 while the committed g96 row came from Vista. Drawing both shows how
much of the margin is reproducible across venues and how much is not.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "analysis"))
sys.path.insert(0, str(REPO / "simulation"))

import failure_modes as FM                                    # noqa: E402
from slide_verdict_fragility import longest_joint_run, k_crit  # noqa: E402

TH = FM.FailureThresholds()

G128_REF = "claude/rtfd-test-phase-1-4-569130"
G128_PATHS = {
    "g96_ls6_control": "data/g128_canonical_2026-08-13/canon_g96_m2337/metrics.csv",
    "g128": "data/g128_canonical_2026-08-13/canon_g128_m2337/metrics.csv",
}

def wrap(paragraphs, width):
    """Hard-wrap caption paragraphs. matplotlib's wrap=True measures against the
    FIGURE width and ignores the text's own x offset, so it overflows a
    left-anchored block; wrapping explicitly is the only reliable option."""
    return "\n".join(textwrap.fill(p, width=width) for p in paragraphs)


INK = "#1a1a1a"
ACCENT = "#8b1a1a"
GREY = "#7a7a7a"
OK = "#2f6f4f"


def git_show(ref, path):
    """Read a committed file from another branch WITHOUT checking it out.

    Read-only by construction: `git show` cannot modify the other branch, its
    worktree or the index. That matters here because the branch holding the g128
    data belongs to a different work thread.
    """
    try:
        out = subprocess.run(["git", "-C", str(REPO), "show", "%s:%s" % (ref, path)],
                             capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "cannot read %s:%s\n%s\nFetch or check out that branch first; this "
            "script will not invent the g128 points."
            % (ref, path, exc.stderr.decode("utf8", "replace").strip()))
    return out.stdout.decode("utf8")


def metrics_from_ref(ref, path, tmpdir):
    txt = git_show(ref, path)
    f = Path(tmpdir) / (path.replace("/", "_"))
    f.write_text(txt)
    return np.genfromtxt(str(f), delimiter=",", names=True)


def measure(d):
    """Every fragility number for one run, from its own timeseries."""
    dx, vx = np.abs(d["dx"]), np.abs(d["vx"])
    L = longest_joint_run(d["dx"], d["vx"], TH.slide_m, TH.slide_speed_ms)
    k = k_crit(d["dx"], d["vx"], TH.slide_m, TH.slide_speed_ms, TH.sustain_frames)
    need = TH.slide_m / np.maximum(np.minimum(dx, vx), 1e-12)
    n = TH.sustain_frames
    w = [need[i:i + n].max() for i in range(len(need) - n + 1)]
    i0 = int(np.argmin(w))
    joint = (dx >= TH.slide_m) & (vx >= TH.slide_speed_ms)
    return {
        "n_frames": int(len(dx)),
        "longest_joint_frames": L,
        "margin_frames": L - TH.sustain_frames,
        "k_crit": float(k), "headroom_x": float(1.0 / k),
        "ratio_slide": float(dx.max() / TH.slide_m),
        "peak_drift_m": float(dx.max()), "peak_drift_frame": int(np.argmax(dx)),
        "peak_speed_ms": float(vx.max()), "peak_speed_frame": int(np.argmax(vx)),
        "k_crit_window": [i0, i0 + n - 1],
        "k_crit_window_drift_m": [float(v) for v in dx[i0:i0 + n]],
        "joint_mask": joint, "dx": dx, "vx": vx,
    }


def load_fragility(run):
    for r in csv.DictReader(open(REPO / "data" / "slide_verdict_fragility_2026-08-13.csv")):
        if r["run"] == run:
            return r
    raise SystemExit("run %r not in the fragility CSV" % run)


def figure_a(out, dpi, tmpdir):
    """Margin collapse for the canonical Yaris hull at the 2337 kg class mass."""
    committed = [("g48_m2337", 48), ("g64_m2337", 64), ("g96_m2337", 96)]
    rows = []
    for run, g in committed:
        r = load_fragility(run)
        rows.append({
            "n_grid": g, "label": "g%d" % g,
            "longest": int(r["longest_joint_frames"]),
            "margin": int(r["margin_frames"]),
            "k_crit": float(r["k_crit"]),
            "ratio": float(r["ratio_slide_live"]),
            "mode": r["mode_live"],
            "repro": r["reproduces_frozen"] == "True",
            "source": "data/slide_verdict_fragility_2026-08-13.csv (Vista metrics)",
        })
    g128 = measure(metrics_from_ref(G128_REF, G128_PATHS["g128"], tmpdir))
    ctrl = measure(metrics_from_ref(G128_REF, G128_PATHS["g96_ls6_control"], tmpdir))
    rows.append({
        "n_grid": 128, "label": "g128",
        "longest": g128["longest_joint_frames"], "margin": g128["margin_frames"],
        "k_crit": g128["k_crit"], "ratio": g128["ratio_slide"],
        "mode": "SLIDE" if g128["margin_frames"] >= 0 else "STUCK",
        "repro": None,
        "source": "%s:%s, measured here" % (G128_REF, G128_PATHS["g128"]),
    })

    fig = plt.figure(figsize=(13.6, 8.0), dpi=dpi)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.86], left=0.075, right=0.985,
                          top=0.880, bottom=0.250, wspace=0.32, hspace=0.44)

    x = np.arange(len(rows))
    labels = [r["label"] for r in rows]

    # -- panel 1: frames --------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    ax.bar(x, [r["longest"] for r in rows], color="#c8d3dd", edgecolor=INK,
           linewidth=0.9, label="longest joint run")
    ax.bar(x, [TH.sustain_frames] * len(rows), color=ACCENT, alpha=0.85,
           edgecolor="none", label="3 frames required")
    for i, r in enumerate(rows):
        ax.text(i, r["longest"] + 0.9, "%d" % r["longest"], ha="center",
                fontsize=9, weight="bold", color=INK)
        # The margin label goes INSIDE tall bars and ABOVE short ones, otherwise
        # it collides with the count on the two refined arms, which are exactly
        # the arms the figure exists to show.
        if r["longest"] - TH.sustain_frames >= 4:
            ax.text(i, (r["longest"] + TH.sustain_frames) / 2.0, "margin %d" % r["margin"],
                    ha="center", va="center", fontsize=8, color=INK)
        else:
            ax.text(i, r["longest"] + 2.4, "margin %d" % r["margin"], ha="center",
                    fontsize=8.4, color=ACCENT, weight="bold")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("consecutive frames holding\nthe joint SLIDE condition", fontsize=8.6)
    ax.set_title("Margin in frames", fontsize=10, weight="bold")
    ax.legend(fontsize=7.4, frameon=False, loc="upper right")
    ax.set_ylim(0, max(r["longest"] for r in rows) * 1.42)
    ax.spines[["top", "right"]].set_visible(False)

    # -- panel 2: k_crit --------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    kk = [r["k_crit"] for r in rows]
    ax.plot(x, kk, "-o", color=ACCENT, lw=2.0, ms=7, zorder=3)
    ax.axhline(1.0, color=INK, lw=1.2, ls="--")
    ax.text(len(rows) - 0.5, 1.012, "k = 1: verdict flips to STUCK", fontsize=7.6,
            ha="right", va="bottom", color=INK)
    ax.fill_between([-0.5, len(rows) - 0.5], 1.0, 1.15, color=ACCENT, alpha=0.06)
    for i, r in enumerate(rows):
        ax.annotate("%.4f" % r["k_crit"], (i, r["k_crit"]), textcoords="offset points",
                    xytext=(0, -15), ha="center", fontsize=8, color=INK)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_xlim(-0.5, len(rows) - 0.5)
    ax.set_ylim(0.30, 1.10)
    ax.set_ylabel("$k_{crit}$, smallest uniform weakening\nthat still clears the criterion", fontsize=8.6)
    ax.set_title("How close the verdict is to flipping", fontsize=10, weight="bold")
    ax.spines[["top", "right"]].set_visible(False)

    # -- panel 3: the two metrics disagree about the trend ----------------
    ax = fig.add_subplot(gs[0, 2])
    ax.plot(x, [r["margin"] for r in rows], "-o", color=OK, lw=1.8, ms=6,
            label="margin, frames")
    ax.plot(x, [r["ratio"] for r in rows], "-s", color=GREY, lw=1.8, ms=6,
            label="ratio_slide (peak drift / 0.05 m)")
    ax.axhline(1.0, color=GREY, lw=0.8, ls=":")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("value")
    ax.set_title("Peak magnitude is not the margin", fontsize=10, weight="bold")
    ax.legend(fontsize=7.4, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.annotate("ratio_slide stays above 1\nat every grid; the margin\nreaches 0",
                (3, rows[3]["ratio"]), textcoords="offset points", xytext=(-96, 26),
                fontsize=7.4, color=GREY,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8))

    # -- panel 4: where the critical window actually is -------------------
    ax = fig.add_subplot(gs[1, :])
    for m, name, col in ((ctrl, "g96 (LS6 in-job control)", "#4a6d8c"),
                         (g128, "g128", ACCENT)):
        f = np.arange(m["n_frames"])
        ax.plot(f, m["dx"], color=col, lw=1.5, label="%s  |surge drift|" % name)
        i0, i1 = m["k_crit_window"]
        ax.axvspan(i0 - 0.5, i1 + 0.5, color=col, alpha=0.13, lw=0)
        ax.annotate("%s critical window,\nframes %d-%d" % (name.split(" ")[0], i0, i1),
                    (i1 + 0.5, m["k_crit_window_drift_m"][-1]),
                    textcoords="offset points", xytext=(14, 8 if col == ACCENT else 26),
                    fontsize=7.4, color=col,
                    arrowprops=dict(arrowstyle="->", color=col, lw=0.8))
        ax.plot([m["peak_drift_frame"]], [m["peak_drift_m"]], "o", color=col, ms=6)
        ax.annotate("peak, frame %d" % m["peak_drift_frame"],
                    (m["peak_drift_frame"], m["peak_drift_m"]),
                    textcoords="offset points", xytext=(6, 6), fontsize=7.4, color=col)
    ax.axhline(TH.slide_m, color=INK, lw=1.1, ls="--")
    ax.text(1, TH.slide_m * 1.03, "slide_m = 0.05 m", fontsize=7.6, va="bottom", color=INK)
    ax.set_xlabel("frame (30 fps)")
    ax.set_ylabel("|surge drift|, m")
    ax.set_title("The verdict is decided in the first ten frames, not at the peak",
                 fontsize=10, weight="bold")
    ax.legend(fontsize=7.6, frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, max(ctrl["n_frames"], g128["n_frames"]) - 1)

    fig.text(0.5, 0.982,
             "Grid refinement collapses the SLIDE margin to zero: canonical Yaris "
             "hull at the AR&R large_4wd class mass, 2337 kg",
             fontsize=13.5, ha="center", va="top", weight="bold")
    fig.text(0.5, 0.958,
             "SLIDE requires |drift| $\\geq$ 0.05 m AND |speed| $\\geq$ 0.05 m/s "
             "for 3 consecutive frames (simulation/failure_modes.py:181-183). "
             "Engine warpmpm. Hull sha256 b379fa4472c6..., hull volume 3.542739 m$^3$.",
             fontsize=8.6, ha="center", va="top", color="0.25")

    ratio_ls6, ratio_vista = ctrl["ratio_slide"], rows[2]["ratio"]
    cap = [
        "NON-CANONICAL for the g128 arm: the 17-run gated inventory exists only at "
        "g48/g64/g96. This is the canonical YARIS hull carrying an AR&R large_4wd "
        "class MASS of 2337 kg (realized density 642.8 / 658.1 / 663.6 kg/m$^3$ at "
        "g48/g64/g96, read from data/all_runs_inventory.csv). It is NOT a Silverado; "
        "for the real Silverado hull see the companion figure.",
        "MEASURED: every number above. g48/g64/g96 are read from the committed "
        "data/slide_verdict_fragility_2026-08-13.csv; g128 and the g96 control are "
        "measured here from metrics.csv committed on %s, using that same script's "
        "longest_joint_run() and k_crit() functions rather than re-implementations. "
        "NOTHING here is tuned or fitted." % G128_REF,
        "NAMING, corrected on this figure: 11 / 10 / 4 / 3 is longest_joint_frames. "
        "margin_frames is that minus the 3 required, i.e. 8 / 7 / 1 / 0. A summary "
        "that calls the first series margin_frames is using the wrong column name.",
        "THE CONTROL, and it cuts both ways. The g128 job ran its own g96 arm on LS6 "
        "while the committed g96 row came from Vista. Their k_crit agrees to "
        "%+.4f%% (%.6f against %.6f) but their peak drift ratio differs by %+.2f%% "
        "(%.5f against %.5f). The critical 3-frame window sits at frames %d-%d, "
        "before the trajectories diverge; the peak sits at frame %d, long after. So "
        "the margin is the reproducible quantity here and the peak is not, which is "
        "the opposite of how they are usually quoted."
        % (100 * (ctrl["k_crit"] - rows[2]["k_crit"]) / rows[2]["k_crit"],
           ctrl["k_crit"], rows[2]["k_crit"],
           100 * (ratio_ls6 - ratio_vista) / ratio_vista, ratio_ls6, ratio_vista,
           ctrl["k_crit_window"][0], ctrl["k_crit_window"][1], ctrl["peak_drift_frame"]),
        "LIMITS. $k_{crit}$ assumes drift and speed weaken by the SAME factor, a "
        "first-order stand-in; refinement also changes trajectory shape, so $k_{crit}$ "
        "ranks fragility and is not a prediction that a run flips at a given grid. "
        "The frame margin assumes nothing. Per CLAUDE.md L-3 no arm here is a "
        "converged resolution (g64 sits at depth/dx = 2.0 against a rule of thumb of "
        "~10 per flow depth), and per L-5 Steffen, Kirby and Berzins 2008 is the "
        "citable mechanism for MPM losing convergence under refinement at fixed "
        "particles-per-cell, which is this stack's case at 8 PPC.",
    ]
    fig.text(0.010, 0.208, wrap(cap, 226), fontsize=6.9, va="top", ha="left",
             linespacing=1.60, family="DejaVu Sans")

    png = out / "fig_margin_collapse_m2337.png"
    fig.savefig(png, dpi=dpi, facecolor="white")
    plt.close(fig)
    print("[fig] wrote %s" % png)

    return {
        "figure": str(png),
        "family": "canonical Yaris hull at AR&R large_4wd class mass 2337 kg",
        "hull_sha256": "b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95",
        "engine": "warpmpm",
        "criterion": {"slide_m": TH.slide_m, "slide_speed_ms": TH.slide_speed_ms,
                      "sustain_frames": TH.sustain_frames,
                      "source": "simulation/failure_modes.py:181-183"},
        "series": rows,
        "g96_ls6_control": {k: v for k, v in ctrl.items()
                            if k not in ("joint_mask", "dx", "vx")},
        "g128": {k: v for k, v in g128.items()
                 if k not in ("joint_mask", "dx", "vx")},
    }


def figure_b(out, dpi):
    """The Silverado verdict flip, on the real Silverado hull at 2270 kg."""
    rows = [r for r in csv.DictReader(
        open(REPO / "data" / "rogue_silverado_slide_classification_2026-08-13.csv"))]
    sweep = {v: sorted([r for r in rows if r["vehicle"] == v and r["run"].startswith("rs_")],
                       key=lambda r: int(r["n_grid"])) for v in ("silverado", "rogue")}

    fig = plt.figure(figsize=(13.6, 7.0), dpi=dpi)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(1, 3, left=0.062, right=0.985, top=0.855, bottom=0.265,
                          wspace=0.32)

    for col, veh in enumerate(("silverado", "rogue")):
        ax = fig.add_subplot(gs[0, col])
        rr = sweep[veh]
        x = np.arange(len(rr))
        drift = [float(r["ratio_slide"]) for r in rr]
        speed = [float(r["max_speed_ms"]) / TH.slide_speed_ms for r in rr]
        ax.plot(x, drift, "-o", color=ACCENT, lw=2.0, ms=7,
                label="peak drift / 0.05 m")
        ax.plot(x, speed, "-s", color="#4a6d8c", lw=2.0, ms=6,
                label="peak speed / 0.05 m/s")
        ax.axhline(1.0, color=INK, lw=1.1, ls="--")
        ax.text(0.02, 1.06, "threshold", fontsize=7.4, color=INK)
        ax.set_yscale("log")
        ax.set_xticks(x)
        ax.set_xticklabels(["g%s" % r["n_grid"] for r in rr])
        ax.set_ylabel("peak / threshold  (log scale)")
        ax.set_title("%s, %s kg, real hull" % (veh.capitalize(), rr[0]["mass_kg"]),
                     fontsize=10.5, weight="bold")
        ax.legend(fontsize=7.4, frameon=False, loc="lower left")
        ax.spines[["top", "right"]].set_visible(False)
        for i, r in enumerate(rr):
            mode = r["mode"]
            ax.annotate(mode, (i, max(drift[i], speed[i])), textcoords="offset points",
                        xytext=(0, 12), ha="center", fontsize=8.4, weight="bold",
                        color=ACCENT if mode == "STUCK" else OK)
            ax.annotate("%.4f" % drift[i], (i, drift[i]), textcoords="offset points",
                        xytext=(14 if i == 0 else 0, -14),
                        ha="left" if i == 0 else "center", fontsize=7.4, color=ACCENT)
        ax.set_ylim(min(min(drift), 1.0) * 0.55, max(max(speed), max(drift)) * 3.2)

    # third panel: the onset frame, which is what actually changes
    ax = fig.add_subplot(gs[0, 2])
    for veh, col, mk in (("silverado", ACCENT, "o"), ("rogue", "#4a6d8c", "s")):
        rr = sweep[veh]
        x = np.arange(len(rr))
        on = [int(r["onset_frame_slide"]) for r in rr]
        ax.plot(x, on, "-" + mk, color=col, lw=2.0, ms=7, label=veh.capitalize())
        for i, v in enumerate(on):
            ax.annotate("no 3-frame\nwindow" if v < 0 else "frame %d" % v, (i, v),
                        textcoords="offset points", xytext=(0, 11 if v >= 0 else -26),
                        ha="center", fontsize=7.4, color=col)
    ax.axhline(0, color=GREY, lw=0.8, ls=":")
    ax.set_xticks(np.arange(3)); ax.set_xticklabels(["g64", "g96", "g128"])
    ax.set_ylabel("first frame of a sustained joint window\n(-1 = never)")
    ax.set_title("What actually changes the verdict", fontsize=10.5, weight="bold")
    ax.legend(fontsize=7.6, frameon=False, loc="center left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(-3.2, 8.5)

    sil = sweep["silverado"][-1]
    fig.text(0.5, 0.978,
             "A verdict flips to STUCK while both thresholds are still exceeded: "
             "Silverado hull, 2270 kg, g64 to g128",
             fontsize=13.5, ha="center", va="top", weight="bold")
    fig.text(0.5, 0.948,
             "0.30 m nominal depth, 1.5 m/s surge, warpmpm. Silverado hull sha256 "
             "46fba11e77cd..., 7.9621 m$^3$; Rogue hull c0b778e2c443..., 4.9503 m$^3$.",
             fontsize=8.6, ha="center", va="top", color="0.25")

    cap = [
        "NON-CANONICAL COMPANION EXPERIMENT, not part of the 17-run gated inventory. "
        "Source: data/rogue_silverado_slide_classification_2026-08-13.csv, rows "
        "rs_* (job 3362208, LS6 A100). The Rogue rows carry mass 1571.3 kg, which "
        "is WEB-SOURCED ONLY; the Silverado rows carry 2270 kg from the vehicle "
        "deck header, the stronger provenance of the two.",
        "THE RESULT. At g128 the Silverado's peak drift is %.4f x threshold and its "
        "peak speed is %.3f x threshold, so BOTH are still exceeded, and the "
        "classified mode is STUCK. Nothing fell below a threshold. The joint "
        "condition simply never holds for 3 consecutive frames, so "
        "onset_frame_slide is -1 and triggered_slide is False."
        % (float(sil["ratio_slide"]),
           float(sil["max_speed_ms"]) / TH.slide_speed_ms),
        "WHY IT MATTERS BEYOND THIS RUN. CLAUDE.md item 12(a) records the general "
        "form of this trap: triggered_* is the verdict, ratio_* is a peak "
        "magnitude, and filtering the canonical store on ratio >= 1 reports 13 "
        "topples that never happened. This figure is that trap caught in the act "
        "on a real verdict.",
        "MEASURED, not modelled: every plotted value is a column of the committed "
        "CSV, except the speed ratio, which is that CSV's max_speed_ms divided by "
        "the 0.05 m/s threshold declared at simulation/failure_modes.py:47. Note "
        "that :47 is a SPEED that shares the numeral 0.05 with two DISTANCES at "
        ":46 and :48; per CLAUDE.md item 13 they must never be deduplicated by "
        "value.",
        "LIMIT. Fixed n_grid is not fixed resolution across vehicles: grid_lim "
        "follows the hull extent, so the Rogue and Silverado columns are each "
        "internally consistent refinement series but the two series are not at a "
        "common dx, and neither is at the canonical set's dx.",
    ]
    fig.text(0.010, 0.218, wrap(cap, 226), fontsize=6.9, va="top", ha="left",
             linespacing=1.60, family="DejaVu Sans")

    png = out / "fig_silverado_verdict_flip.png"
    fig.savefig(png, dpi=dpi, facecolor="white")
    plt.close(fig)
    print("[fig] wrote %s" % png)
    return {
        "figure": str(png),
        "family": "real Silverado and Rogue hulls, non-canonical grid sweep",
        "engine": "warpmpm",
        "source_csv": "data/rogue_silverado_slide_classification_2026-08-13.csv",
        "silverado_g128": {k: sil[k] for k in
                           ("run", "n_grid", "mass_kg", "mode", "triggered_slide",
                            "ratio_slide", "max_speed_ms", "onset_frame_slide")},
        "speed_ratio_g128": float(sil["max_speed_ms"]) / TH.slide_speed_ms,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--tmpdir", required=True,
                    help="scratch directory for files extracted from another branch")
    ap.add_argument("--dpi", type=int, default=170)
    a = ap.parse_args()
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    Path(a.tmpdir).mkdir(parents=True, exist_ok=True)

    man = {"generated_by": "analysis/make_resolution_margin_figures.py",
           "figure_a": figure_a(out, a.dpi, a.tmpdir),
           "figure_b": figure_b(out, a.dpi)}
    mp = out / "resolution_margin_figures_manifest.json"
    mp.write_text(json.dumps(man, indent=2, default=str) + "\n")
    print("[fig] wrote %s" % mp)


if __name__ == "__main__":
    main()
