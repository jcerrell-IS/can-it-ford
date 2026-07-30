import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

N_GRID_60K = [64, 96, 128, 192]
VOL_60K = [7.697913, 7.096399, 6.355574, 4.439533]

N_GRID_400K = [64, 96, 128, 192, 256]
VOL_400K = [7.832869, 7.387112, 7.194586, 6.926466, 6.591542]

HULL_M3 = 3.542739

SAMPLE_SPACING_M = (0.020, 0.024)
H_AT_192_M = 0.0245

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(REPO_ROOT / "figures" / "fig3_geometry_pipeline.pdf"))
ap.add_argument("--acknowledge-superseded-column-fill", action="store_true")
args = ap.parse_args()

if not args.acknowledge_superseded_column_fill:
    raise SystemExit(
        "REFUSING TO RUN. VOL_60K and VOL_400K are COLUMN-FILL solidify volumes, a method\n"
        "that has been replaced. At n_grid=64 this script plots 7.697913 m3, 2.173x the\n"
        "3.542739 m3 hull, sourced to docs/VERIFIED_FACTS_LEDGER_july24.md:251.\n"
        "\n"
        "The current solidify_watertight path measures, live in data/all_runs_inventory.csv:\n"
        "    n_grid=48  solid_volume 3.6357101018957585  fill_ratio 1.0262  rho 302.55\n"
        "    n_grid=64  solid_volume 3.5513843861695054  fill_ratio 1.0024  rho 309.74\n"
        "    n_grid=96  solid_volume 3.5217987479492066  fill_ratio 0.9941  rho 312.34\n"
        "paper/conference_101719.tex Table II uses those values. This figure contradicts\n"
        "them by a factor of 2.17 and is a historical diagnostic, not a current result.\n"
        "\n"
        "The values here were NOT swapped for the live ones, because this figure's whole\n"
        "thesis is the column-fill overfill: its band is labelled residual over-fill that\n"
        "never closes, its y-axis spans 3.12 to 8.80, and its right panel reports volume\n"
        "recovered by 60k-to-400k resampling. Substituting solidify_watertight volumes\n"
        "would compare two different methods and invert the band. No solidify_watertight\n"
        "run exists at n_grid 128, 192 or 256, so those points have no live counterpart.\n"
        "\n"
        "Pass --acknowledge-superseded-column-fill to emit it anyway."
    )

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedFormatter, FixedLocator

S60 = "#B03A2E"
S400 = "#0E6655"
HULL = "#154360"
BAND = "#5DADE2"

RECOVERED_PCT = [100.0 * (b / a - 1.0) for a, b in zip(VOL_60K, VOL_400K)]
HULL_MULT_400K = [v / HULL_M3 for v in VOL_400K]

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["axes.facecolor"] = "white"
plt.rcParams["savefig.facecolor"] = "white"

fig, (axL, axR) = plt.subplots(1, 2, figsize=(18.666, 10.2), facecolor="white",
                               gridspec_kw={"width_ratios": [1.62, 1.0]})

fig.suptitle("Sampling density, not grid resolution, drove the volume collapse",
             fontsize=27, fontweight="bold", color="black", y=0.985)
fig.text(0.5, 0.925,
         "Neither curve reaches the true hull: column fill merges wheel wells and "
         "window openings into the solid, by design",
         fontsize=19.5, color="black", ha="center", va="center")

axL.fill_between(N_GRID_400K, VOL_400K, HULL_M3, color=BAND, alpha=0.20, zorder=1,
                 label="Residual over-fill, by design (never closes)")
axL.axhline(HULL_M3, color=HULL, linestyle="--", linewidth=3.0, zorder=3,
            label="True watertight hull volume: %.6f m$^3$" % HULL_M3)
axL.plot(N_GRID_400K, VOL_400K, "s-", color=S400, markersize=15, linewidth=3.2,
         zorder=5, label="400,000 surface samples")
axL.plot(N_GRID_60K, VOL_60K, "o-", color=S60, markersize=15, linewidth=3.2,
         zorder=5, label="60,000 surface samples (the shipped default)")

axL.annotate("", xy=(192, VOL_60K[-1]), xytext=(192, VOL_400K[3]),
             arrowprops=dict(arrowstyle="<->", color="black", linewidth=2.6,
                             shrinkA=10, shrinkB=10), zorder=6)
axL.annotate("+%.1f%% recovered by resampling alone\nSAME mesh, SAME grid" % RECOVERED_PCT[-1],
             xy=(192, VOL_60K[-1]), xytext=(0, -24), textcoords="offset points",
             ha="center", va="top", fontsize=18, fontweight="bold", color="black",
             bbox=dict(boxstyle="round,pad=0.42", facecolor="white", edgecolor="0.45",
                       alpha=1.0), zorder=7)

axL.annotate("%.2fx hull" % HULL_MULT_400K[-1], xy=(256, VOL_400K[-1]),
             xytext=(0, 24), textcoords="offset points", ha="center",
             fontsize=17.5, fontweight="bold", color=S400,
             bbox=dict(boxstyle="round,pad=0.28", facecolor="white", edgecolor="none",
                       alpha=0.92), zorder=7)

axL.text(0.035, 0.46,
         "Gap never closes: wheel wells and window\n"
         "openings are filled into the solid, by design",
         transform=axL.transAxes, fontsize=17.5, ha="left", va="center", color="black",
         bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="0.6",
                   alpha=1.0), zorder=7)

axL.text(61.5, HULL_M3 + 0.09, "true hull, %.6f m$^3$, never reached" % HULL_M3,
         fontsize=16.5, ha="left", va="bottom", color=HULL, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none",
                   alpha=0.92), zorder=7)

axL.set_xscale("log", base=2)
axL.xaxis.set_major_locator(FixedLocator(N_GRID_400K))
axL.xaxis.set_major_formatter(FixedFormatter([str(n) for n in N_GRID_400K]))
axL.xaxis.set_minor_locator(FixedLocator([]))
axL.set_xlim(58, 292)
axL.set_ylim(3.12, 8.80)
axL.set_xlabel("MPM grid resolution $n_{grid}$ (cells per domain edge, dimensionless)",
               fontsize=19.5)
axL.set_ylabel("Solidified body volume (m$^3$)", fontsize=20)
axL.set_title("Column-fill solid volume vs grid resolution", fontsize=21.5, color="black",
              pad=14)
axL.tick_params(axis="both", labelsize=17.5)
axL.grid(alpha=0.28, linestyle=":", color="0.5")
axL.legend(fontsize=16.5, loc="upper right", framealpha=1.0, facecolor="white",
           edgecolor="0.7")

bars = axR.bar([str(n) for n in N_GRID_60K], RECOVERED_PCT, width=0.62,
               color=S400, edgecolor="black", linewidth=1.1, zorder=3)
for rect, pct in zip(bars, RECOVERED_PCT):
    axR.annotate("+%.2f%%" % pct, xy=(rect.get_x() + rect.get_width() / 2, pct),
                 xytext=(0, 11), textcoords="offset points", ha="center",
                 fontsize=18.5, fontweight="bold", color="black",
                 bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                           edgecolor="none", alpha=0.92), zorder=5)

axR.text(0.035, 0.955,
         "A resolution limit would not care how\n"
         "densely the surface was sampled.\n"
         "This one cares more and more.",
         transform=axR.transAxes, fontsize=18, ha="left", va="top", color="black",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="0.55",
                   alpha=1.0), zorder=6)

axR.text(0.035, 0.60,
         "60k surface point spacing is %.3f to %.3f m.\n"
         "The cell pitch h at $n_{grid}$ = 192 is %.4f m,\n"
         "so columns start catching no surface hits." % (
             SAMPLE_SPACING_M[0], SAMPLE_SPACING_M[1], H_AT_192_M),
         transform=axR.transAxes, fontsize=16.5, ha="left", va="top", color="black",
         bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="0.6",
                   alpha=1.0), zorder=6)

axR.set_xlabel("MPM grid resolution $n_{grid}$ (dimensionless)", fontsize=19.5)
axR.set_ylabel("Volume recovered by 60k to 400k resampling (percent)", fontsize=20)
axR.set_title("The 60k deficit grows with resolution", fontsize=21.5, color="black",
              pad=14)
axR.set_ylim(0, 68)
axR.tick_params(axis="both", labelsize=17.5)
axR.grid(axis="y", alpha=0.28, linestyle=":", color="0.5")
axR.set_axisbelow(True)

fig.tight_layout(rect=[0, 0, 1, 0.905])

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, format="pdf", dpi=300, bbox_inches="tight", facecolor="white")
print("wrote %s" % out)
for n, a, b, p in zip(N_GRID_60K, VOL_60K, VOL_400K, RECOVERED_PCT):
    print("n_grid=%-4d 60k=%.6f 400k=%.6f recovered=+%.2f%%" % (n, a, b, p))
print("400k hull multiples: %s" % ", ".join("%d:%.3fx" % (n, m)
                                            for n, m in zip(N_GRID_400K, HULL_MULT_400K)))
