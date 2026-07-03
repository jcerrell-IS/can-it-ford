import os
try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    HERE = os.getcwd()
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def pick(df, exact, subs):
    low = {c.lower(): c for c in df.columns}
    for e in exact:
        if e in low:
            return low[e]
    for c in df.columns:
        cl = c.lower()
        for s in subs:
            if s in cl:
                return c
    return None

grid = pd.read_csv(os.path.join(HERE, "scenario_sweep.csv"))
gd = pick(grid, ["depth_m", "depth", "d"], ["dep"])
gv = pick(grid, ["velocity_ms", "velocity", "v"], ["vel"])
gh = pick(grid, ["l1_haz", "haz"], ["haz", "dxv", "product"])
g1 = pick(grid, ["l1_verdict", "l1"], ["l1"])
if None in (gd, gv, gh, g1):
    raise SystemExit("scenario_sweep.csv columns not recognized: %s" % list(grid.columns))
grid = grid.rename(columns={gd: "depth", gv: "velocity", gh: "L1_haz", g1: "L1"})

def l2_rule(d, v, haz):
    if haz > 0.60:
        return "NO-FORD"
    if v == 0:
        return "FORD"
    if 0.10 <= d <= 0.60 and v >= 1.0:
        return "NO-FORD"
    return "FORD"

cat = []
for _, r in grid.iterrows():
    l2 = l2_rule(r.depth, r.velocity, r.L1_haz)
    if str(r.L1).upper().replace("-", "").replace("_", "").replace(" ", "") != l2.replace("-", ""):
        cat.append("diverge")
    elif "NO" in str(r.L1).upper():
        cat.append("agreeN")
    else:
        cat.append("agreeF")
grid["cat"] = cat

C = {"agreeF": "#639922", "agreeN": "#E24B4A", "diverge": "#EF9F27"}

fig, ax = plt.subplots(figsize=(8.4, 6.0), dpi=200)
for c, col in C.items():
    s = grid[grid.cat == c]
    ax.scatter(s.depth, s.velocity, s=230, marker="s", c=col,
               edgecolors="white", linewidths=0.7, zorder=2)

dd = np.linspace(0.1, 1.0, 300)
for k, ls, lw, al in [(0.30, ":", 1.0, 0.6), (0.45, "-.", 1.0, 0.6), (0.60, "--", 1.7, 0.95)]:
    vv = k / dd
    m = vv <= 3.05
    ax.plot(dd[m], vv[m], ls=ls, lw=lw, alpha=al, color="#2b2b2b", zorder=3)

ax.axvline(0.15, color="#8a8a8a", ls=(0, (2, 2)), lw=1.0, alpha=0.7, zorder=1)
ax.text(0.157, 3.05, "L0  d=0.15 m", fontsize=8, color="#8a8a8a", rotation=90, va="top")

src = ""
plotted = False
if os.path.exists(os.path.join(HERE, "phase_space_results.csv")):
    try:
        l2 = pd.read_csv(os.path.join(HERE, "phase_space_results.csv"))
        d2 = pick(l2, ["depth_m", "depth", "d"], ["dep"])
        v2 = pick(l2, ["velocity_ms", "velocity", "v"], ["vel"])
        verd = pick(l2, ["l2_verdict", "verdict", "result", "label"], ["verdict", "result", "ford", "label"])
        drift = pick(l2, ["drift_m", "peak_drift", "x_drift", "drift"], ["drift", "displac"])
        noford = None
        if verd is not None:
            norm = l2[verd].astype(str).str.upper().str.replace("-", "", regex=False).str.replace("_", "", regex=False).str.replace(" ", "", regex=False)
            noford = l2[norm.str.contains("NOFORD")]
        elif drift is not None:
            noford = l2[l2[drift].astype(float) > 0.05]
        if noford is not None and d2 is not None and v2 is not None and len(noford):
            ax.scatter(noford[d2], noford[v2], s=150, marker="D", facecolors="#EF9F27",
                       edgecolors="black", linewidths=1.7, zorder=5)
            src = "N=%d L2 runs, %d NO-FORD overlaid" % (len(l2), len(noford))
            plotted = True
        else:
            print("WARNING: found phase_space_results.csv but could not read verdicts. columns =", list(l2.columns))
    except Exception as e:
        print("WARNING: phase_space_results.csv failed to load:", e)

if not plotted:
    a = [(0.10, 1.5), (0.30, 2.0), (0.60, 1.0)]
    ax.scatter([p[0] for p in a], [p[1] for p in a], s=150, marker="D",
               facecolors="#EF9F27", edgecolors="black", linewidths=1.7, zorder=5)
    src = "confirmed anchors (drop phase_space_results.csv beside this script for all 23)"

ax.annotate("10 cm water\nstill drifts the car", xy=(0.10, 1.5), xytext=(0.34, 2.55),
            fontsize=8, color="#7a4a00",
            arrowprops=dict(arrowstyle="->", color="#7a4a00", lw=1.0))

ax.set_xlabel("Water depth  d  (m)", fontsize=11)
ax.set_ylabel("Flow velocity  v  (m/s)", fontsize=11)
ax.set_title("Can It Ford?   L0 / L1 / L2 Phase Space", fontsize=13, weight="bold")
ax.set_xlim(0.03, 1.05)
ax.set_ylim(-0.18, 3.2)

handles = [
    Line2D([], [], marker="s", ls="", mfc=C["agreeF"], mec="white", ms=11, label="L1 = L2 = FORD"),
    Line2D([], [], marker="s", ls="", mfc=C["agreeN"], mec="white", ms=11, label="L1 = L2 = NO-FORD"),
    Line2D([], [], marker="s", ls="", mfc=C["diverge"], mec="white", ms=11, label="L1 FORD, L2 NO-FORD"),
    Line2D([], [], marker="D", ls="", mfc=C["diverge"], mec="black", ms=9, label="L2 confirmed run"),
    Line2D([], [], ls="--", color="#2b2b2b", lw=1.7, label="AR&R 0.60 (4WD)"),
]
ax.legend(handles=handles, loc="upper right", fontsize=8.5, framealpha=0.96)
fig.text(0.5, 0.005, "Background: L0/L1 sweep. Amber = L1 clears the crossing, L2 drifts the car. " + src,
         ha="center", fontsize=7.2, color="#666")
plt.tight_layout(rect=[0, 0.02, 1, 1])
plt.savefig(os.path.join(HERE, "phase_space_current.png"), dpi=200, bbox_inches="tight")
print("OK saved phase_space_current.png |", src)
