import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[1]

N_GRID = [64, 96, 128]
SUBMERGED_M3 = [0.842252, 0.644214, 0.506268]
TRUE_SUBMERGED_M3 = 0.432718
INFLATION = [1.95, 1.49, 1.17]
TRACTION_N = [1390.7, 2459.2, 3203.5]
TRUE_TRACTION_N = 3495.2
UNDERSTATEMENT_PCT = [60.0, 30.0, 8.3]
MU_SENSITIVITY = [(0.30, 1906.5), (0.40, 2542.0), (0.55, 3495.2)]
MU_SPREAD = 1.83

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(REPO_ROOT / "figures" / "traction_bias.pdf"))
args = ap.parse_args()

MEAS = "#B03A2E"
REF = "#154360"
BAND = "#5DADE2"

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"

fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 5.4), facecolor="white")
fig.suptitle(
    "One-sided resolution bias: every tested grid over-fills volume and understates traction",
    fontsize=14.5, fontweight="bold", color="black", y=0.99)

axL.plot(N_GRID, SUBMERGED_M3, "o-", color=MEAS, markersize=10, linewidth=2.2,
         label="Column-fill solidified volume", zorder=4)
axL.axhline(TRUE_SUBMERGED_M3, color=REF, linestyle="--", linewidth=2.4,
            label="True watertight mesh: 0.432718 m$^3$", zorder=3)
for x, y, f in zip(N_GRID, SUBMERGED_M3, INFLATION):
    axL.annotate("%.2fx" % f, xy=(x, y), xytext=(0, 13), textcoords="offset points",
                 ha="center", fontsize=11.5, fontweight="bold", color=MEAS,
                 bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                           edgecolor="none", alpha=0.85))
axL.set_xlabel("MPM grid resolution $n_{grid}$ (cells per domain edge, dimensionless)", fontsize=11.5)
axL.set_ylabel("Submerged solid volume (m$^3$)", fontsize=12)
axL.set_title("Solid volume below the 0.30 m waterline", fontsize=12.5, color="black")
axL.set_xticks(N_GRID)
axL.set_xlim(52, 140)
axL.set_ylim(0.37, 0.95)
axL.grid(alpha=0.28, linestyle=":", color="0.5")
axL.legend(fontsize=10, loc="upper right", framealpha=1.0, facecolor="white", edgecolor="0.7")

axR.axhspan(MU_SENSITIVITY[0][1], MU_SENSITIVITY[-1][1], color=BAND, alpha=0.16, zorder=1,
            label="True geometry across $\\mu$ = 0.30 to 0.55 (%.2fx)" % MU_SPREAD)
axR.plot(N_GRID, TRACTION_N, "o-", color=MEAS, markersize=10, linewidth=2.2,
         label="Modeled traction at $\\mu$ = 0.55", zorder=4)
axR.axhline(TRUE_TRACTION_N, color=REF, linestyle="--", linewidth=2.4,
            label="True geometry at $\\mu$ = 0.55: 3495.2 N", zorder=3)
for x, y, p in zip(N_GRID, TRACTION_N, UNDERSTATEMENT_PCT):
    dx_off = -30 if x == N_GRID[-1] else 0
    ha = "right" if x == N_GRID[-1] else "center"
    axR.annotate("%g%% low" % p, xy=(x, y), xytext=(dx_off, -27), textcoords="offset points",
                 ha=ha, fontsize=11.5, fontweight="bold", color=MEAS,
                 bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                           edgecolor="none", alpha=0.95))
axR.set_xlabel("MPM grid resolution $n_{grid}$ (cells per domain edge, dimensionless)", fontsize=11.5)
axR.set_ylabel("Available traction force (N)", fontsize=12)
axR.set_title("Tire traction at $\\mu$ = 0.55, 1100 kg vehicle", fontsize=12.5, color="black")
axR.set_xticks(N_GRID)
axR.set_xlim(52, 140)
axR.set_ylim(980, 3950)
axR.grid(alpha=0.28, linestyle=":", color="0.5")
axR.legend(fontsize=9.5, loc="upper left", framealpha=1.0, facecolor="white", edgecolor="0.7")

mu_lines = "\n".join(["  $\\mu$ = %.2f  ->  %.1f N" % (m, v) for m, v in MU_SENSITIVITY])
axR.text(0.975, 0.045,
         "Friction uncertainty, true geometry:\n%s\n  spread %.2fx" % (mu_lines, MU_SPREAD),
         transform=axR.transAxes, fontsize=9.5, va="bottom", ha="right", color="black",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="0.55", alpha=1.0))

fig.tight_layout(rect=[0, 0, 1, 0.955])

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, format="pdf", dpi=300, bbox_inches="tight", facecolor="white")
print("wrote %s" % out)
