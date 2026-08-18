"""Two-panel summary of the closed-vs-open comparison.

Panel A is the late-window streamwise free-surface profile: the closed box ramps
and drains its upstream bins, the open channel does not.
Panel B is every slope measured, against the bed slope of a 3 degree road. The
point of putting tan(3 deg) on the axis is that the closed-box artifact sits ABOVE
it, so a slope study run in that configuration reads its own boundary condition.

The recycle points are drawn at BOTH record lengths on purpose. They disagree, two
of them in sign, which is the honest statement: the residual is bounded, not
resolved. Drawing only the 90-frame set would imply a precision the data does not
support.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stationarity import analyze


def load(d):
    raw = np.genfromtxt(d / "depth_profile.csv", delimiter=",", names=True)
    prof = np.vstack([raw[n] for n in raw.dtype.names]).T
    s = json.loads((d / "summary.json").read_text())
    e = np.linspace(s["x_in"], s["x_out"], prof.shape[1] + 1)
    return prof, s, 0.5 * (e[:-1] + e[1:])


def slope_of(prof, c):
    out = []
    for row in prof:
        fin = np.isfinite(row)
        out.append(np.polyfit(c[fin], row[fin], 1)[0] if fin.sum() >= 3 else np.nan)
    return [v for v in out if np.isfinite(v)]


def main(root, out_png):
    root = Path(root)
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13, 5.0))

    panelA = [("closed_g64", "closed, 0 deg", "#c0392b", "-"),
              ("closed_g64_grade3p0", "closed, 3 deg", "#e67e22", "--"),
              ("recycle_g64", "recycle, 0 deg", "#1f6fb4", "-"),
              ("recycle_g64_grade3p0", "recycle, 3 deg", "#16a085", "--")]
    for name, lab, col, ls in panelA:
        d = root / name
        if not d.exists():
            continue
        prof, s, c = load(d)
        rep = analyze(slope_of(prof, c))
        mp = np.nanmean(prof[rep["recommended_discard"]:], axis=0)
        axA.plot(c, mp, ls, color=col, marker="o", ms=4, lw=1.8, label=lab)
        drained = np.isnan(mp)
        if drained.any():
            axA.plot(c[drained], np.zeros(drained.sum()), "x", color=col, ms=9, mew=2)
    axA.axhline(0.30, color="0.45", lw=1.0, ls=":", label="nominal depth 0.30 m")
    axA.set_xlabel("streamwise position x (m)")
    axA.set_ylabel("free-surface height above the floor (m)")
    axA.set_title("A. Late-window depth profile\n(x marks a bin that holds no water)",
                  fontsize=10, loc="left")
    axA.legend(fontsize=8, loc="upper left")
    axA.grid(alpha=0.25)

    pts = [("closed", 0.0, 90, +0.09268, 0.00161), ("closed", 3.0, 90, +0.16946, 0.00224),
           ("recycle", 0.0, 90, -0.00284, 0.00029), ("recycle", 1.0, 90, -0.00072, 0.00096),
           ("recycle", 3.0, 90, +0.00596, 0.00086),
           ("recycle", 0.0, 300, +0.00673, 0.00090), ("recycle", 1.0, 300, -0.00350, 0.00075),
           ("recycle", 3.0, 300, -0.00876, 0.00047)]
    for bc, g, fr, v, e in pts:
        col = "#c0392b" if bc == "closed" else "#1f6fb4"
        mk = "o" if fr == 90 else "s"
        axB.errorbar(g + (0.06 if fr == 300 else -0.06), v, yerr=e, fmt=mk, color=col,
                     ms=7, capsize=3, mfc="white" if fr == 300 else col)
    for y, lab, col in ((np.tan(np.deg2rad(3)), "bed slope of a 3 deg road", "#555555"),
                        (-np.tan(np.deg2rad(3)), None, "#555555")):
        axB.axhline(y, color=col, lw=1.1, ls="--")
        if lab:
            axB.text(3.05, y + 0.004, lab, fontsize=8, color=col, ha="right")
    axB.axhline(0, color="0.7", lw=0.8)
    axB.axhspan(-0.00876, 0.00673, color="#1f6fb4", alpha=0.10)
    axB.text(1.5, 0.012, "recycle spans this band across BOTH record lengths:\n"
                         "bounded, not resolved (2 of 3 flip sign)",
             fontsize=7.5, color="#1f6fb4", ha="center")
    axB.set_xlabel("road grade (degrees)")
    axB.set_ylabel("free-surface slope (m/m)")
    axB.set_title("B. Every slope measured\n"
                  "filled = 90 frames, open = 300 frames", fontsize=10, loc="left")
    axB.set_xticks([0, 1, 3])
    axB.grid(alpha=0.25)

    fig.suptitle("A bounded MPM domain cannot represent a flooded roadway: the "
                 "closed-box artifact exceeds the slope it would mask",
                 fontsize=11.5, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=160)
    print("wrote", out_png)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
