import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]
GATES = REPO / "renders" / "yaris_render_s1" / "gates_results_both_scenarios.json"
OUT = REPO / "figures" / "fig2_mass_sensitivity.pdf"
OUT_PNG = REPO / "figures" / "fig2_mass_sensitivity.png"

ARR_BOUNDARY_KG = 1250.0
ARR_4WD_BOUNDARY_KG = 2000.0
XMIN, XMAX = 950.0, 2980.0
YMAX = 0.83

rows = [r for r in json.load(open(GATES)) if r["scenario"] == "standing_water_sustained_inflow"]
rows.sort(key=lambda r: r["mass_kg"])

mass = np.array([r["mass_kg"] for r in rows])
disp = np.array([r["L2_final_disp_mag_m"] for r in rows])
dxv = np.array([r["dxv_nominal"] for r in rows])
l1a = [r["L1a_verdict"] for r in rows]

spread = disp[0] / disp[-1]
dxv_val = float(dxv[0])
assert len(set(np.round(dxv, 9))) == 1, "D x V is not identical across runs"

mgrid = np.linspace(XMIN, XMAX, 3000)
thresh = np.where(mgrid < ARR_BOUNDARY_KG, 0.30,
                  np.where(mgrid < ARR_4WD_BOUNDARY_KG, 0.45, 0.60))

fig, axL = plt.subplots(figsize=(8.6, 5.4))
fig.patch.set_facecolor("white")
axL.set_facecolor("white")

axL.axvspan(XMIN, ARR_BOUNDARY_KG, color="#dce9f4", alpha=0.6, zorder=0, lw=0)
axL.axvline(ARR_BOUNDARY_KG, color="#333333", lw=1.4, ls="--", zorder=3)
axL.axvline(ARR_4WD_BOUNDARY_KG, color="#999999", lw=1.0, ls=":", zorder=3)

lineA, = axL.plot(mass, disp, "o-", color="#c0392b", lw=2.8, ms=10, zorder=7,
                  label="L2 coupled MPM: final displacement (left axis)")
for m, d, off in zip(mass, disp, [(-14, -16), (16, 8), (0, 16)]):
    axL.annotate(f"{d:.3f} m", (m, d), textcoords="offset points", xytext=off,
                 ha=("center" if off[0] == 0 else ("right" if off[0] < 0 else "left")), fontsize=10,
                 color="#c0392b", fontweight="bold", zorder=8)

xb = 2450.0
axL.annotate("", xy=(xb, disp[0]), xytext=(xb, disp[-1]),
             arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=2.0))
axL.plot([mass[0], xb], [disp[0], disp[0]], color="#c0392b", lw=0.8, ls=":", alpha=0.6)
axL.plot([mass[-1], xb], [disp[-1], disp[-1]], color="#c0392b", lw=0.8, ls=":", alpha=0.6)
axL.text(xb + 34, 0.5 * (disp[0] + disp[-1]), f"{spread:.2f}x", color="#c0392b",
         fontsize=17, fontweight="bold", va="center", ha="left")

axR = axL.twinx()
axR.set_facecolor("none")
lineB, = axR.plot(mass, dxv, "s-", color="#1f6f9c", lw=2.8, ms=10, zorder=7,
                  label="L1a criterion value: D x V (right axis)")
lineC, = axR.plot(mgrid, thresh, color="#1f6f9c", lw=1.9, ls="--", alpha=0.9, zorder=5,
                  label="AR&R interim D x V limit, looked up by mass class")

axR.text(990, 0.315, "small passenger", fontsize=8.6, color="#1f6f9c", ha="left")
axR.text(1690, 0.472, "large passenger", fontsize=8.6, color="#1f6f9c", ha="left")
axR.text(2030, 0.615, "large 4WD", fontsize=8.6, color="#1f6f9c", ha="left")

axR.text(1320, 0.815,
         "D x V is FLAT at 0.441644 m$^2$/s: the criterion has no mass term.\n"
         "Only the AR&R limit moves, and it moves in discrete steps by\n"
         "mass class. That step, not the physics, is the entire verdict change.",
         fontsize=9.4, color="#0d4f73", ha="left", va="top", zorder=9,
         bbox=dict(boxstyle="round,pad=0.45", facecolor="white",
                   edgecolor="#9dc3dc", alpha=0.97))

for m, v in zip(mass, l1a):
    axR.text(m, 0.030, f"L1a\n{v}", ha="center", fontsize=9,
             color=("#0d7a3f" if v == "FORD" else "#8a1c12"), fontweight="bold", zorder=8)

axL.text(ARR_BOUNDARY_KG - 22, 0.155, "AR&R 1250 kg\nmass boundary", fontsize=8.6,
         color="#333333", ha="right", va="bottom")

axL.set_xlabel("Vehicle mass (kg), at ONE fixed geometry 1.746 x 4.283 x 1.518 m", fontsize=11)
axL.set_ylabel("L2 final displacement (m)", fontsize=11.5, color="#c0392b")
axR.set_ylabel("D x V and AR&R interim limit (m$^2$/s)", fontsize=11.5, color="#1f6f9c")
axL.tick_params(axis="y", colors="#c0392b")
axR.tick_params(axis="y", colors="#1f6f9c")
axL.set_xlim(XMIN, XMAX)
axL.set_ylim(0, YMAX)
axR.set_ylim(0, YMAX)
axL.set_xticks([1100, 1250, 1609, 2000, 2337])
axL.grid(alpha=0.2, zorder=1)

axL.set_title("The cheap criterion cannot see mass.\n"
              f"The coupled simulation resolves a {spread:.2f}x effect over the same range.",
              fontsize=13, fontweight="bold", pad=12)

axL.legend(handles=[lineA, lineB, lineC], loc="upper center",
           bbox_to_anchor=(0.5, -0.155), ncol=1, fontsize=9.6,
           framealpha=1.0, facecolor="white", edgecolor="#cccccc")

fig.text(0.5, -0.055,
         "d = 0.29443 m, v = 1.5 m/s, standing water, n_grid = 64. L1a evaluated with "
         "vehicle_params.L1_verdict (full AR&R rule).\nAR&R values are that report's DRAFT "
         "INTERIM criteria for STATIONARY vehicles. Left and right axes are independent "
         "quantities;\nranges are matched only for legibility.",
         ha="center", va="top", fontsize=8.4, color="#555555")

fig.tight_layout()
OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, format="pdf", bbox_inches="tight")
fig.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
print(f"wrote {OUT}")
print(f"wrote {OUT_PNG}")
print(f"spread = {spread:.4f}x   D x V = {dxv_val:.9f}   L1a = {l1a}")
