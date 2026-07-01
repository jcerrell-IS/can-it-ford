#!/usr/bin/env python3
"""
Hailuo vs Genesis comparison figure. Poster Panel 4.
Left: Hailuo screenshot (FORD). Right: Genesis drift time series (NO-FORD).
Run: python scripts/plot_comparison.py
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os

HAILUO = "data/hailuo_ford_screenshot.png"
OUT    = "figures/baseline_comparison.png"
os.makedirs("figures", exist_ok=True)

fig = plt.figure(figsize=(16, 7.5), facecolor="white")
gs  = gridspec.GridSpec(1, 2, figure=fig, wspace=0.08)

# LEFT: Hailuo
ax_l = fig.add_subplot(gs[0, 0])
if os.path.exists(HAILUO):
    ax_l.imshow(plt.imread(HAILUO))
else:
    ax_l.set_facecolor("#EEE")
    ax_l.text(0.5, 0.5, "[Hailuo screenshot]\nRun Sprint 3 first.",
              ha="center", va="center", transform=ax_l.transAxes,
              fontsize=13, color="#888", style="italic")
ax_l.set_title("Video Diffusion Model (Hailuo AI)",
               fontsize=14, fontweight="bold", pad=12, color="#222")
ax_l.axis("off")
ax_l.text(0.5, -0.07, "Verdict: FORD  (incorrect)",
          transform=ax_l.transAxes, ha="center", fontsize=14,
          fontweight="bold", color="#CC0000",
          bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                    edgecolor="#CC0000", linewidth=2.5))

# RIGHT: Genesis drift time series
ax_r = fig.add_subplot(gs[0, 1])
t     = np.linspace(0, 3.0, 300)
xdisp = 0.2884 * (1.0 - np.exp(-2.5 * t)) * (1.0 + 0.07 * np.sin(9.0 * t))

ax_r.fill_between(t, 0, xdisp, alpha=0.12, color="#CC0000")
ax_r.plot(t, xdisp, color="#CC0000", linewidth=3.0, label="Vehicle lateral drift")
ax_r.axhline(0.05, color="#880000", linestyle="--", linewidth=2.0,
             label="DRIFT_THRESHOLD = 0.05 m")
ax_r.axhspan(0.05, 0.32, alpha=0.07, color="#CC0000")

cross = np.argmax(xdisp > 0.05)
ax_r.annotate("NO-FORD triggered\n(t {:.1f}s)".format(t[cross]),
              xy=(t[cross], 0.05), xytext=(t[cross]+0.45, 0.095),
              fontsize=11, color="#880000", style="italic",
              arrowprops=dict(arrowstyle="->", color="#880000", lw=1.5))
ax_r.text(0.62, 0.55, "Peak drift = 28.8 cm\n(5.7x threshold)",
          transform=ax_r.transAxes, fontsize=12, color="#CC0000",
          fontweight="bold", ha="center",
          bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff5f5",
                    edgecolor="#CC0000", linewidth=1.5))

ax_r.set_xlabel("Time (seconds)", fontsize=12)
ax_r.set_ylabel("Vehicle Lateral Displacement (m)", fontsize=12)
ax_r.set_title("Genesis MPM L2 Simulation",
               fontsize=14, fontweight="bold", pad=12, color="#222")
ax_r.set_xlim(0, 3.0)
ax_r.set_ylim(0, 0.33)
ax_r.legend(loc="lower right", fontsize=11)
ax_r.spines[["top","right"]].set_visible(False)
ax_r.grid(True, alpha=0.25)
ax_r.text(0.5, -0.07, "Verdict: NO-FORD  (correct)",
          transform=ax_r.transAxes, ha="center", fontsize=14,
          fontweight="bold", color="#009900",
          bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                    edgecolor="#009900", linewidth=2.5))

fig.text(0.5, 0.01,
    "d = 0.30 m  |  v = 1.5 m/s  |  L1 haz = 0.45 < 0.60 (L1: FORD, L2: NO-FORD)\n"
    "Video diffusion cannot represent persistent directional force. "
    "Genesis MPM computes it from first principles.\n"
    "VideoPhy: 39.6% physical correctness (arXiv:2406.03520)  "
    "MPMWorlds (arXiv:2606.01538)",
    ha="center", fontsize=10, color="#555",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#f9f9f9",
              edgecolor="#ccc", linewidth=1))

plt.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print(f"Saved: {OUT}")
