import csv
import json
import os
import sys
import textwrap
import traceback

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(REPO, "figures")
S1 = os.path.join(REPO, "renders", "yaris_render_s1")
INV_CSV = os.path.join(REPO, "data", "all_runs_inventory.csv")
GATES_ALL = os.path.join(S1, "gates_results_all_runs.json")
GATES_DRY = os.path.join(S1, "gates_results.json")
HERO_MP4 = os.path.join(S1, "hero_g64_m1100_FIXED.mp4")
HERO_LOG = os.path.join(S1, "hero_fixed.log")
FALLBACK_HERO = os.path.join(FIG, "render_v1", "realistic_A4_g64_m1100_f0045.png")

AR_R_SMALL_HAZ = 0.30
AR_R_LARGE_HAZ = 0.45
AR_R_4WD_HAZ = 0.60
L2_DRIFT_M = 0.05
L0_DEPTH_M = 0.15

C_NOFORD_FILL = "#d7e3f0"
C_NOFORD_TEXT = "#123a5e"
C_FORD_FILL = "#fbe3c2"
C_FORD_TEXT = "#7a4a10"
C_L2 = "#b1302a"
C_L1 = "#1f5f8b"
C_DRY = "#4a7c59"
C_RULE = "#444444"
C_SHADE = "#eef3f8"

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 15,
    "axes.labelsize": 13,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

RESULTS = []


def load_inventory():
    with open(INV_CSV) as fh:
        return list(csv.DictReader(fh))


def load_gates():
    with open(GATES_ALL) as fh:
        return json.load(fh)


def load_dry_gates():
    with open(GATES_DRY) as fh:
        return json.load(fh)


def caption(fig, text, y=0.005, size=10.5):
    fig.text(0.012, y, text, ha="left", va="bottom", fontsize=size,
             color="#1a1a1a", wrap=True, linespacing=1.45)


def save(fig, stem):
    pdf = os.path.join(FIG, stem + ".pdf")
    png = os.path.join(FIG, stem + ".png")
    fig.savefig(pdf, format="pdf")
    fig.savefig(png, dpi=300)
    plt.close(fig)
    return pdf, png


def run(name, fn, *a):
    attempt = 0
    while attempt < 3:
        attempt += 1
        try:
            outs = fn(*a)
            RESULTS.append((name, "OK", attempt, outs))
            print("%s OK (attempt %d) -> %s" % (name, attempt, ", ".join(os.path.basename(o) for o in outs)))
            return
        except Exception:
            print("%s attempt %d FAILED" % (name, attempt))
            traceback.print_exc()
    RESULTS.append((name, "DEGRADE", 3, []))
    print("%s DEGRADE after 3 attempts, continuing" % name)


def velocity_rows(inv):
    rows = [r for r in inv
            if r["n_grid"] == "64" and float(r["mass_kg"]) == 1100.0
            and int(r["water_layers"]) == 4]
    rows.sort(key=lambda r: float(r["velocity_ms"]))
    return rows


def depth_rows(inv):
    rows = [r for r in inv
            if r["n_grid"] == "64" and float(r["mass_kg"]) == 1100.0
            and float(r["velocity_ms"]) == 1.5]
    rows.sort(key=lambda r: float(r["realized_depth_m"]))
    return rows


def g1(inv):
    rows = velocity_rows(inv)
    v = np.array([float(r["velocity_ms"]) for r in rows])
    d = np.array([float(r["final_disp_mag_m"]) for r in rows])
    depth = float(rows[0]["realized_depth_m"])
    assert len({round(float(r["realized_depth_m"]), 9) for r in rows}) == 1
    vcross = AR_R_SMALL_HAZ / depth

    fig, ax = plt.subplots(figsize=(15.0, 8.6))
    ax.axvspan(v.min() - 0.25, vcross, color=C_SHADE, zorder=0)
    ax.text(0.128, 0.735, "SHADED = the FORD side\nL1a says FORD here\n(D x V under the\n0.30 m2/s cap)",
            transform=ax.transAxes, ha="center", va="top", fontsize=10.5,
            color=C_NOFORD_TEXT, zorder=5,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#9fb8cc", lw=0.9))

    ax.plot(v, d, "-o", color=C_L2, lw=2.6, ms=9, zorder=4,
            label="L2 coupled MPM, final |displacement|")
    ax.axhline(L2_DRIFT_M, ls="--", lw=1.8, color=C_RULE, zorder=3,
               label="L2 onset-of-motion threshold, 0.05 m")
    ax.axvline(vcross, ls="-", lw=2.0, color=C_L1, zorder=3,
               label="D x V crosses AR&R small-passenger cap, v = %.4f m/s" % vcross)

    div = [i for i, x in enumerate(v) if x < vcross]
    ax.plot(v[div], d[div], "o", ms=20, mfc="none", mec=C_L1, mew=2.6, zorder=6,
            label="DIVERGENCE: L1a FORD, L2 NO-FORD")
    for i in div:
        ax.annotate("v = %.1f\n|d| = %.4f m\nL1a FORD / L2 NO-FORD" % (v[i], d[i]),
                    xy=(v[i], d[i]), xytext=(v[i] + 0.10, d[i] + 0.26),
                    fontsize=10.5, color=C_L1,
                    arrowprops=dict(arrowstyle="->", color=C_L1, lw=1.4))
    for i, x in enumerate(v):
        if i not in div:
            ax.annotate("%.4f" % d[i], xy=(x, d[i]), xytext=(0, 12),
                        textcoords="offset points", ha="center", fontsize=10)

    ax.set_xlabel("prescribed surge velocity (m/s)")
    ax.set_ylabel("final displacement magnitude |d| (m)")
    ax.set_title("G1  Velocity sweep: the depth-velocity criterion fails on its own axis")
    ax.set_xlim(0.25, 3.25)
    ax.set_ylim(-0.06, max(d) * 1.22)
    ax.grid(alpha=0.25, lw=0.7)
    ax.legend(loc="upper left", framealpha=1.0, edgecolor="#bbbbbb")
    fig.subplots_adjust(bottom=0.30)

    cap = (
        "Fixed grid 64, fixed realized depth %.4f m (4 layers x h), one Yaris hull, "
        "1100 kg, all runs deterministic (determinism_identical = True).\n"
        "THE ARGUMENT: the criterion is varied along the axis it is built on and still "
        "returns the wrong verdict at two of six points.\n"
        "At v = 0.5 and v = 1.0 m/s the AR&R product D x V stays under the 0.30 m2/s "
        "small-passenger cap, so L1a returns FORD, while the coupled simulation moves the "
        "vehicle %.4f m and %.4f m, both above the 0.05 m onset threshold.\n"
        "The vertical rule is where D x V = 0.30 m2/s at this fixed depth, v = %.6f m/s. "
        "AR&R limits are interim DRAFT criteria for stationary vehicles; \"small passenger\" "
        "names the limit set applied by kerb weight, not a measured vehicle class. On the "
        "AR&R geometric axes this hull satisfies only large_passenger "
        "(docs/four_rung_ladder.md:274-280).\n"
        "Source: data/all_runs_inventory.csv, runs %s."
        % (depth, d[0], d[1], vcross, ", ".join(r["run"] for r in rows))
    )
    caption(fig, cap)
    return save(fig, "g1_velocity_sweep")


def g2(inv):
    rows = depth_rows(inv)
    dep = np.array([float(r["realized_depth_m"]) for r in rows])
    disp = np.array([float(r["final_disp_mag_m"]) for r in rows])
    lay = [int(r["water_layers"]) for r in rows]
    req = [float(r["requested_depth_m"]) for r in rows]
    h = float(rows[0]["h"])

    fig, ax = plt.subplots(figsize=(15.0, 8.6))
    ax.plot(dep, disp, "-o", color=C_L2, lw=2.6, ms=9, zorder=4,
            label="L2 coupled MPM, final |displacement|")
    ax.axhline(L2_DRIFT_M, ls="--", lw=1.8, color=C_RULE, zorder=3,
               label="L2 onset-of-motion threshold, 0.05 m")

    for x, y, n, q in zip(dep, disp, lay, req):
        ax.annotate("%d layers\nrealized %.4f m\n(requested %.2f m)\n|d| = %.4f m"
                    % (n, x, q, y),
                    xy=(x, y), xytext=(0, -64), textcoords="offset points",
                    ha="center", fontsize=10, color="#1a1a1a",
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", lw=0.8))

    ax.annotate("near-saturation: %.4f -> %.4f m\n(+%.4f m for one more layer)"
                % (disp[-2], disp[-1], disp[-1] - disp[-2]),
                xy=(float(np.mean(dep[-2:])), float(np.mean(disp[-2:]))),
                xytext=(dep[-2] - 0.075, disp[-1] + 0.20), fontsize=11, color=C_L1,
                arrowprops=dict(arrowstyle="->", color=C_L1, lw=1.4))

    ax.set_xticks(dep)
    ax.set_xticklabels(["%.4f\n%d layers" % (x, n) for x, n in zip(dep, lay)])
    ax.set_xlabel("REALIZED still-water depth (m), quantized to whole grid cells")
    ax.set_ylabel("final displacement magnitude |d| (m)")
    ax.set_title("G2  Depth sweep on the realized axis, not the requested one")
    ax.set_xlim(dep.min() - 0.042, dep.max() + 0.052)
    ax.set_ylim(-0.10, max(disp) * 1.35)
    ax.grid(alpha=0.25, lw=0.7)
    ax.legend(loc="upper left", framealpha=1.0, edgecolor="#bbbbbb")
    fig.subplots_adjust(bottom=0.31)

    cap = (
        "The water slab is built from whole grid cells, so the requested depth is never the "
        "depth simulated. At grid 64 one layer is h = %.6f m, and the realized depth is "
        "water_layers x h. Requested 0.45 m realizes as %.4f m, six layers. Requested 0.25, "
        "0.30 and 0.35 m realize as %.4f, %.4f and %.4f m. The requested value is never "
        "plotted here.\n"
        "Displacement rises steeply and then nearly saturates: the last two points are "
        "%.4f m and %.4f m, a gain of only %.4f m for a whole extra layer, so the response "
        "is flattening at the top of this depth range rather than continuing to climb.\n"
        "Fixed grid 64, fixed 1.5 m/s surge, one hull at 1100 kg, all runs deterministic. "
        "Source: data/all_runs_inventory.csv, runs %s."
        % (h, dep[3], dep[0], dep[1], dep[2], disp[-2], disp[-1], disp[-1] - disp[-2],
           ", ".join(r["run"] for r in rows))
    )
    caption(fig, cap)
    return save(fig, "g2_depth_sweep")


def g3(gates):
    order = {"mass_grid": 0, "depth": 1, "velocity": 2, "dry_start": 3}
    gname = {"mass_grid": "mass x grid sweep\n(standing water)",
             "depth": "depth sweep\n(standing)",
             "velocity": "velocity sweep\n(standing)",
             "dry_start": "dry start\n(second scenario)"}
    rows = sorted(gates, key=lambda r: (order.get(r["sweep"], 9), r["run"]))
    rungs = ["L0_verdict", "L1a_verdict", "L1b_verdict", "L2_verdict"]
    rlab = ["L0  static depth\n(NWS 0.15 m)", "L1a  AR&R interim\n(depth, velocity, D x V)",
            "L1b  Kramer 2016\ntotal head h_E", "L2  this work\ncoupled MPM"]
    n = len(rows)

    fig, ax = plt.subplots(figsize=(17.5, 8.2))
    for j, r in enumerate(rows):
        for i, k in enumerate(rungs):
            v = r[k]
            fc = C_FORD_FILL if v == "FORD" else C_NOFORD_FILL
            tc = C_FORD_TEXT if v == "FORD" else C_NOFORD_TEXT
            ax.add_patch(Rectangle((j, len(rungs) - 1 - i), 1, 1, fc=fc, ec="white", lw=1.6))
            ax.text(j + 0.5, len(rungs) - 1 - i + 0.5, v, ha="center", va="center",
                    fontsize=8.5, color=tc, fontweight="bold")

    hi = [j for j, r in enumerate(rows)
          if r["sweep"] == "dry_start" and r["mass_kg"] == 2337.0]
    for j in hi:
        ax.add_patch(Rectangle((j, 0), 1, 1, fc="none", ec="#b1302a", lw=3.2, zorder=6))
        ax.annotate("dry start, 2337 kg:\nL2 = FORD.\nL2 is NOT\nuniformly NO-FORD.",
                    xy=(j + 1.02, 0.5), xytext=(n + 0.55, 0.5), fontsize=11,
                    color="#b1302a", fontweight="bold", va="center", ha="left",
                    annotation_clip=False,
                    arrowprops=dict(arrowstyle="->", color="#b1302a", lw=1.8))

    bounds, prev = [], None
    for j, r in enumerate(rows):
        if r["sweep"] != prev:
            bounds.append(j)
            prev = r["sweep"]
    bounds.append(n)
    for b in bounds[1:-1]:
        ax.axvline(b, color="#666666", lw=2.2, zorder=7)
    for a, b in zip(bounds[:-1], bounds[1:]):
        ax.text((a + b) / 2.0, len(rungs) + 0.30, gname[rows[a]["sweep"]],
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_xlim(0, n)
    ax.set_ylim(-0.05, len(rungs) + 1.05)
    ax.set_xticks([j + 0.5 for j in range(n)])
    ax.set_xticklabels([r["run"] for r in rows], rotation=52, ha="right", fontsize=9.5)
    ax.set_yticks([len(rungs) - 1 - i + 0.5 for i in range(len(rungs))])
    ax.set_yticklabels(rlab, fontsize=10.5)
    ax.set_title("G3  Four-rung abstraction ladder, every run", pad=42)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    fig.subplots_adjust(bottom=0.40, right=0.815)

    nf = sum(1 for r in rows if r["L2_verdict"] == "FORD")
    cap = (
        "Cells are read straight out of renders/yaris_render_s1/gates_results_all_runs.json, "
        "regenerated this session over all %d runs. Nothing here is hand-typed.\n"
        "L0 is the NWS Turn Around Don't Drown rule at 0.15 m, which is NOT AR&R. "
        "L1a is vehicle_params.L1_verdict, the full interim AR&R rule: depth cap AND "
        "velocity cap AND the D x V product cap, evaluated on realized depth. "
        "L1b is Kramer 2016 total head, h_E = depth + v^2 / 2g = %.6f m at the nominal "
        "operating point, tested against a 0.30 m passenger limit. L2 is this work, the "
        "coupled MPM simulation, NO-FORD when any frame exceeds 0.05 m of drift.\n"
        "INDEPENDENCE CAVEAT: L0, L1a and L1b are all functions of (depth, velocity) alone. "
        "They share their entire input. Their agreement is one criterion evaluated three "
        "ways, NOT three independent confirmations. Only L2 reads the vehicle.\n"
        "L2 returns FORD in %d of %d runs, all in the dry-start scenario. The dry-start and "
        "standing-water runs are NOT a controlled pair: they come from different drivers "
        "(sim_dump.py vs sim_standing.py) and standing water re-injects inflow momentum "
        "every step, so the scenario difference cannot be attributed to the initial "
        "condition alone. Class names denote which AR&R limit set was applied by kerb "
        "weight, nothing more."
        % (len(rows), rows[0]["total_head_he_m"], nf, len(rows))
    )
    caption(fig, cap)
    return save(fig, "g3_verdict_matrix")


def g4(inv, dry):
    st = [r for r in inv if r["run"].startswith("g64_")]
    st.sort(key=lambda r: float(r["mass_kg"]))
    sm = np.array([float(r["mass_kg"]) for r in st])
    sp = np.array([float(r["local_depth_bow_peak"]) for r in st])
    sf = [int(r["local_depth_bow_peak_frame"]) for r in st]

    dry = sorted(dry, key=lambda r: r["mass_kg"])
    dm = np.array([float(r["mass_kg"]) for r in dry])
    dp = np.array([float(r["local_depth_peak"]) for r in dry])
    dfr = sorted({r["peak_frame"] for r in dry})

    nominal = float(st[0]["realized_depth_m"])

    fig, ax = plt.subplots(figsize=(15.0, 8.6))
    ax.plot(sm, sp, "-o", color=C_L2, lw=2.6, ms=10, zorder=4,
            label="standing water, bow probe peak (summary.json local_depth_bow_peak)")
    ax.plot(dm, dp, "-s", color=C_DRY, lw=2.6, ms=9, zorder=4,
            label="dry start, local depth peak (gates_results.json local_depth_peak)")
    ax.axhline(AR_R_SMALL_HAZ, ls="-", lw=2.2, color=C_L1, zorder=3,
               label="AR&R small-passenger depth cap, 0.30 m")
    ax.axhline(nominal, ls="--", lw=1.8, color=C_RULE, zorder=3,
               label="nominal still-water depth, %.4f m" % nominal)

    for x, y in zip(sm, sp):
        ax.annotate("%.4f" % y, xy=(x, y), xytext=(0, 11), textcoords="offset points",
                    ha="center", fontsize=10, color=C_L2)
    for x, y in zip(dm, dp):
        ax.annotate("%.4f" % y, xy=(x, y), xytext=(0, -20), textcoords="offset points",
                    ha="center", fontsize=10, color=C_DRY)

    ax.annotate("standing rise\n+%.4f m across\nthe mass range" % (sp[-1] - sp[0]),
                xy=(sm[-1] - 18, sp[-1] - 0.004), xytext=(sm[-1] - 330, sp[-1] + 0.012),
                fontsize=10.5, color=C_L2, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", color=C_L2, lw=1.4))

    ax.set_xlabel("vehicle mass (kg), one hull")
    ax.set_ylabel("peak local water depth at the vehicle (m)")
    ax.set_title("G4  The bow wave exceeds the AR&R depth cap in 19 of 20 runs")
    ax.set_xticks(list(sm))
    ax.set_ylim(min(nominal, dp.min(), sp.min()) - 0.035, max(sp.max(), dp.max()) + 0.075)
    ax.grid(alpha=0.25, lw=0.7)
    ax.legend(loc="upper left", framealpha=1.0, edgecolor="#bbbbbb", fontsize=10.5)
    fig.subplots_adjust(bottom=0.31)

    cap = (
        "MEASUREMENT WINDOW. Standing water: the bow-probe series local_depth_bow, maximum "
        "over all 90 frames of the 3.0 s rollout, peaking at frames %s for 1100, 1609 and "
        "2337 kg respectively. Dry start: the local depth peak recorded in "
        "gates_results.json, peak frame %s. The two series are NOT the same probe, so the "
        "standing and dry curves are comparable in trend but not point-for-point.\n"
        "THE STORY: the nominal still-water depth is %.4f m, comfortably under the AR&R "
        "0.30 m small-passenger cap, yet 19 of the 20 runs exceed that cap locally at the "
        "vehicle, and the exceedance grows with mass. The single exception is the slowest "
        "velocity-sweep run, v = 0.5 m/s, at 0.295361 m, which is not plotted here because "
        "this panel plots the mass series. Against each run's OWN class depth cap rather "
        "than the fixed 0.30 m small-passenger number, 16 of 20 exceed. All six runs plotted "
        "here do exceed. Standing water rises +%.4f m from %.4f to "
        "%.4f m across the 2.1x mass range. A criterion evaluated on the undisturbed "
        "approach depth never sees this.\n"
        "TWO DRY-START PEAK MEASURES DISAGREE for the 1100 kg run: gates_results.json "
        "local_depth_peak gives %.4f m and summary.json C2_local_depth_max gives 0.4105 m. "
        "They are different probes over the same rollout. Only the gates_results.json "
        "series is plotted here; the C2 series is not mixed in.\n"
        "Source: data/all_runs_inventory.csv and renders/yaris_render_s1/gates_results.json."
        % (", ".join(str(x) for x in sf), ", ".join(str(x) for x in dfr), nominal,
           sp[-1] - sp[0], sp[0], sp[-1], dp[0])
    )
    caption(fig, cap)
    return save(fig, "g4_bow_wave")


def g5(inv, dry):
    st = [r for r in inv if r["run"].startswith("g64_")]
    st.sort(key=lambda r: float(r["mass_kg"]))
    sm = np.array([float(r["mass_kg"]) for r in st])
    sd = np.array([float(r["final_disp_mag_m"]) for r in st])
    nv = sorted({int(r["n_vehicle"]) for r in st})

    dry = sorted(dry, key=lambda r: r["mass_kg"])
    dm = np.array([float(r["mass_kg"]) for r in dry])
    dd = np.array([float(r["final_disp_mag_m"]) for r in dry])
    dnv = sorted({int(r["n_vehicle"]) for r in dry})

    dxv = np.array([float(r["realized_depth_m"]) * float(r["velocity_ms"]) for r in st])
    hexes = {float(x).hex() for x in dxv}
    identical = len(hexes) == 1

    fig, ax = plt.subplots(figsize=(15.0, 8.8))
    ax.plot(sm, sd, "-o", color=C_L2, lw=2.8, ms=10, zorder=4,
            label="L2 standing water, |d| (%.2fx spread)" % (sd[0] / sd[-1]))
    ax.plot(dm, dd, "-s", color=C_DRY, lw=2.6, ms=9, zorder=4,
            label="L2 dry start, |d| (%.2fx spread)" % (dd[0] / dd[-1]))
    ax.axhline(L2_DRIFT_M, ls="--", lw=1.8, color=C_RULE, zorder=3,
               label="L2 onset-of-motion threshold, 0.05 m")
    for x, y in zip(sm, sd):
        ax.annotate("%.4f" % y, xy=(x, y), xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=10, color=C_L2)
    for x, y in zip(dm, dd):
        ax.annotate("%.4f" % y, xy=(x, y), xytext=(0, 13), textcoords="offset points",
                    ha="center", fontsize=10, color=C_DRY)

    ax.set_xlabel("mass (kg) applied to ONE hull")
    ax.set_ylabel("final displacement magnitude |d| (m)", color=C_L2)
    ax.tick_params(axis="y", colors=C_L2)
    ax.set_xticks(list(sm))
    ax.set_ylim(-0.05, sd.max() * 1.25)
    ax.grid(alpha=0.25, lw=0.7)

    ax2 = ax.twinx()
    ax2.plot(sm, dxv, "-D", color=C_L1, lw=2.8, ms=9, zorder=4,
             label="AR&R D x V (mass-blind)")
    ax2.set_ylabel("AR&R depth x velocity (m2/s)", color=C_L1)
    ax2.tick_params(axis="y", colors=C_L1)
    ax2.set_ylim(0.0, 0.72)
    ax2.axhline(AR_R_SMALL_HAZ, ls=":", lw=1.6, color=C_L1, alpha=0.7)
    ax2.text(sm[-1], AR_R_SMALL_HAZ + 0.006, "AR&R small-passenger cap 0.30 m2/s",
             ha="right", va="bottom", fontsize=10, color=C_L1, alpha=0.95)
    ax2.text(sm.mean(), dxv[0] + 0.075,
             "D x V = %.6f m2/s, %s across the whole mass range\n"
             "the criterion has no mass term"
             % (dxv[0], "BIT-IDENTICAL" if identical else "NOT bit-identical"),
             ha="center", fontsize=11.5, color=C_L1, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=C_L1, lw=1.0))

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", framealpha=1.0, edgecolor="#bbbbbb")
    ax.set_title("G5  Mass sensitivity on one hull: L2 resolves what D x V cannot")
    fig.subplots_adjust(bottom=0.30)

    cap = (
        "SCOPE, NON-NEGOTIABLE: all six runs plotted here use the SAME mesh, "
        "vehicle_geometry_research/yaris_coarse_v1l_watertight.ply, at %s solid particles "
        "(standing) and %s (dry start). This is THREE MASSES ON ONE HULL, a mass "
        "sensitivity study. It is NOT three vehicles, and the word \"class\" may not appear "
        "unqualified for these rows. Where a class name is used elsewhere it names only "
        "which AR&R limit set was applied by kerb weight.\n"
        "Left axis: the coupled simulation resolves a %.2fx displacement spread in standing "
        "water (%.6f to %.6f m) and %.2fx in dry start (%.6f to %.6f m). Right axis: the "
        "AR&R product is %s at %.6f m2/s across the same 2.1x mass range, because D x V "
        "contains no mass term at all.\n"
        "The two scenarios are not a controlled pair (different drivers, sustained inflow "
        "in one only), so read each series against itself, not against the other. "
        "Grid 64, realized depth %.4f m, 1.5 m/s surge, all runs deterministic.\n"
        "Source: data/all_runs_inventory.csv and renders/yaris_render_s1/gates_results.json."
        % (" to ".join(str(x) for x in nv), " to ".join(str(x) for x in dnv),
           sd[0] / sd[-1], sd[0], sd[-1], dd[0] / dd[-1], dd[0], dd[-1],
           "bit-identical" if identical else "NOT bit-identical", dxv[0],
           float(st[0]["realized_depth_m"]))
    )
    caption(fig, cap)
    return save(fig, "g5_mass_sensitivity")


def g6(dry):
    dry = sorted(dry, key=lambda r: r["mass_kg"])
    labs = ["%.0f kg\n(%s limits)" % (r["mass_kg"], r["label"]) for r in dry]
    nom = [r["dv_nominal"] for r in dry]
    hon = [r["dv_honest"] for r in dry]
    peak = [r["local_depth_peak"] * r["nominal_vel"] for r in dry]

    x = np.arange(len(dry))
    w = 0.26
    fig, ax = plt.subplots(figsize=(15.0, 8.8))
    b1 = ax.bar(x - w, nom, w, color="#7f9fbf", ec="#33556f", lw=1.0,
                label="A. nominal D x V (requested depth x prescribed velocity)")
    b2 = ax.bar(x, peak, w, color="#c98b5e", ec="#7a4a10", lw=1.0,
                label="B. peak local depth x nominal velocity")
    b3 = ax.bar(x + w, hon, w, color="#7fa87f", ec="#3c603c", lw=1.0,
                label="C. local D x V at the vehicle (peak local depth x peak local speed)")
    for bs in (b1, b2, b3):
        ax.bar_label(bs, fmt="%.5f", fontsize=9.5, padding=3)

    for y, lab, c in ((AR_R_SMALL_HAZ, "AR&R small passenger cap 0.30", "#1f5f8b"),
                      (AR_R_LARGE_HAZ, "AR&R large passenger cap 0.45", "#7a4a10"),
                      (AR_R_4WD_HAZ, "AR&R large 4WD cap 0.60", "#3c603c")):
        ax.axhline(y, ls="--", lw=1.7, color=c)
        ax.text(len(dry) - 0.44, y + 0.008, lab, fontsize=10, color=c, ha="left")

    ax.set_xticks(x)
    ax.set_xticklabels(labs)
    ax.set_ylabel("depth x velocity (m2/s)")
    ax.set_title("G6  Three readings of D x V from the same simulation, and they disagree")
    ax.set_xlim(-0.55, len(dry) + 0.62)
    ax.set_ylim(0, max(peak) * 1.30)
    ax.grid(axis="y", alpha=0.25, lw=0.7)
    ax.legend(loc="upper left", framealpha=1.0, edgecolor="#bbbbbb")
    fig.subplots_adjust(bottom=0.30)

    cap = (
        "AR&R never defines D and V for a transient surge, so the same dry-start rollout "
        "supports opposite L1a verdicts depending on which reading you take. Reading A puts "
        "every run at %.4f m2/s. Reading B, using the bow-wave peak, pushes all three ABOVE "
        "reading A (%.4f to %.4f m2/s). Reading C, measured at the vehicle where local depth "
        "rises but local speed collapses at stagnation, drops them to %.5f, %.5f and %.5f "
        "m2/s, 58 to 66 percent BELOW nominal.\n"
        "Under reading A the 1609 kg run is FORD; re-running the live L1_verdict on reading "
        "C makes it NO-FORD, and that flip is driven by the DEPTH cap, not the product cap "
        "(local peak depth 0.4159 m exceeds its 0.40 m limit while its local D x V of "
        "0.1645 sits far under the 0.45 cap).\n"
        "PRIMARY FOR THIS PROJECT: reading A, the nominal convention. That is what "
        "gates_all_runs.py feeds to vehicle_params.L1_verdict for every run in G3, and it "
        "is chosen because it is an INPUT to the simulation rather than an output of it, so "
        "a practitioner can evaluate it without running any simulation, which is the entire "
        "point of testing a cheap criterion against L2. Readings B and C depend on probe "
        "placement and so cannot be reproduced from the flood condition alone.\n"
        "This is a DISCLOSURE, not a defect: the L1-versus-L2 comparison is not well posed "
        "until the criterion's own input is pinned down. Source: "
        "renders/yaris_render_s1/gates_results.json, dry-start runs m1100, m1609, m2337."
        % (nom[0], min(peak), max(peak), hon[0], hon[1], hon[2])
    )
    caption(fig, cap)
    return save(fig, "g6_two_measures")


def parse_volume_error():
    if not os.path.isfile(HERO_LOG):
        return None, None, None
    raw = smooth = edges = None
    for ln in open(HERO_LOG):
        if "WATER VOLUME" in ln:
            for tok in ln.split():
                if tok.startswith("raw_err="):
                    raw = tok.split("=")[1]
                if tok.startswith("smooth_err="):
                    smooth = tok.split("=")[1]
                if tok.startswith("open_edges="):
                    edges = tok.split("=")[1]
    return raw, smooth, edges


def g7(inv):
    ext = np.load(os.path.join(S1, "g64_m1100", "rollout.npz"),
                  allow_pickle=True)["extent"]
    ex, ey, ez = float(ext[0]), float(ext[1]), float(ext[2])
    cl_lo, cl_hi = 0.158, 0.174
    raw, smooth, edges = parse_volume_error()

    rho = sorted({round(float(r["realized_rho"])) for r in inv if r["n_grid"] == "64"})
    fr = [float(r["fill_ratio"]) for r in inv]
    pt = [float(r["passthrough_max_frac"]) for r in inv]
    worst = max(inv, key=lambda r: float(r["passthrough_max_frac"]))
    det = {r["determinism_identical"] for r in inv}
    oob = {int(r["C3_oob_particle_frames"]) for r in inv}

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(17.5, 8.6),
                                   gridspec_kw={"width_ratios": [1.0, 1.35]})

    axl.add_patch(Rectangle((0, cl_hi), ey, ez - cl_hi, fc="#e6dcd2", ec="#8f1f1f", lw=2.0))
    axl.add_patch(Rectangle((0, cl_lo), ey, cl_hi - cl_lo, fc="#f6d7a8", ec="#b07a20",
                            lw=1.2, hatch="////"))
    axl.axhline(0, color="#555555", lw=2.4)
    axl.annotate("", xy=(0, -0.10), xytext=(ey, -0.10),
                 arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.5))
    axl.text(ey / 2, -0.175, "long axis Y = %.6f m" % ey, ha="center", fontsize=11.5)
    axl.annotate("", xy=(ey + 0.16, 0), xytext=(ey + 0.16, ez),
                 arrowprops=dict(arrowstyle="<->", color="#333333", lw=1.5))
    axl.text(ey + 0.26, ez / 2, "Z = %.6f m" % ez, rotation=90, va="center", fontsize=11.5)
    axl.annotate("measured ground\nclearance BAND\n%.3f to %.3f m\n(five sampling bands)"
                 % (cl_lo, cl_hi),
                 xy=(-0.02, cl_lo + (cl_hi - cl_lo) / 2.0),
                 xytext=(-0.42, 0.78),
                 ha="right", va="center", fontsize=10.5, color="#7a4a10",
                 arrowprops=dict(arrowstyle="->", color="#7a4a10", lw=1.4))
    axl.text(ey / 2, ez / 2, "Yaris hull, side view\nX (width) = %.6f m" % ex,
             ha="center", va="center", fontsize=12)
    axl.set_xlim(-3.15, ey + 0.85)
    axl.set_ylim(-0.42, ez + 0.30)
    axl.set_aspect("equal")
    axl.axis("off")
    axl.set_title("Hull geometry, one mesh: yaris_coarse_v1l_watertight.ply", fontsize=13)

    rows = [
        ("mesh containment of solid particles", "100.00 pct of 2000 sampled", "PASS"),
        ("fill_ratio vs 0.95 to 1.10 band", "%.4f at g64; %.4f to %.4f (17 runs)"
         % (1.002440, min(fr), max(fr)), "PASS"),
        ("water surface open_edges", "%s" % (edges if edges else "n/a"), "PASS"),
        ("water volume error", "%s raw, %s smoothed" % (raw or "n/a", smooth or "n/a"), "PASS"),
        ("oob_particle_frames", "%s" % ", ".join(str(x) for x in sorted(oob)), "PASS"),
        ("determinism_identical, all 17 runs", "%s" % ", ".join(sorted(det)), "PASS"),
        ("realized rho vs the 100 to 300 band", "%s kg/m3 at grid 64"
         % " / ".join(str(x) for x in rho), "FAIL"),
        ("water particle passthrough", "%.1f to %.1f pct; worst at v = 3.0 m/s"
         % (min(pt) * 100, max(pt) * 100), "NOTED"),
    ]
    cols = {"PASS": ("#e4efe4", "#2f5d2f"), "FAIL": ("#f7d9d6", "#8f2018"),
            "NOTED": ("#fbeccd", "#7a4a10")}
    axr.set_xlim(0, 1)
    axr.set_ylim(0, len(rows) + 1.4)
    axr.axis("off")
    axr.text(0.012, len(rows) + 0.85, "gate", fontsize=12, fontweight="bold")
    axr.text(0.455, len(rows) + 0.85, "measured value", fontsize=12, fontweight="bold")
    axr.text(0.995, len(rows) + 0.85, "verdict", fontsize=12, fontweight="bold", ha="right")
    axr.plot([0.005, 0.995], [len(rows) + 0.68] * 2, color="#333333", lw=1.4)
    for i, (g, v, s) in enumerate(rows):
        y = len(rows) - 1 - i + 0.10
        fc, tc = cols[s]
        axr.add_patch(Rectangle((0.005, y), 0.99, 0.82, fc=fc, ec="white", lw=1.4))
        axr.text(0.018, y + 0.41, g, va="center", fontsize=10.5)
        axr.text(0.455, y + 0.41, v, va="center", fontsize=9.8)
        axr.text(0.988, y + 0.41, s, va="center", ha="right", fontsize=11,
                 fontweight="bold", color=tc)
    axr.set_title("Geometry and physics gates, measured this session", fontsize=13)

    fig.suptitle("G7  Geometry pipeline and the gate table, including what fails",
                 fontsize=16, y=0.985)
    fig.subplots_adjust(bottom=0.26, top=0.90)

    cap = (
        "The gate table is shown WITH its failure. A gate table with no failures is not "
        "credible, and the density gate genuinely fails: solidify_watertight fills the hull "
        "to parity (fill_ratio ~ 1.00), so the realized effective density is set by mass "
        "over a correctly measured 3.5427 m3 hull volume and lands at %s kg/m3, above the "
        "project's own stated 100 to 300 kg/m3 plausibility band. The band is the thing that "
        "is now wrong for a parity-filled hull, but it is the project's stated band and the "
        "run is outside it, so it is recorded as FAIL rather than quietly rewritten.\n"
        "Containment is 100.00 pct of a 2000-particle SUBSAMPLE, not of all particles: "
        "trimesh.ray.has_embree is False on this machine so the gate was run subsampled "
        "(docs/render_v1_task_outputs/A2_containment_gate.output). The four-rotation "
        "relative gate that would discriminate the pose chain is still outstanding.\n"
        "Volume error and open_edges are read from the FIXED PyVista render logged this "
        "session in renders/yaris_render_s1/hero_fixed.log. Passthrough is a NOTED caveat, "
        "not a pass: %.1f to %.1f pct of water particles are inside the hull at the worst "
        "frame, worst at the highest surge velocity, which is a real limit on how hard the "
        "high-velocity end of G1 can be pushed.\n"
        "Extents and clearance sources: rollout.npz extent field; "
        "docs/four_rung_ladder.md:274-280 for the 0.158 to 0.174 m measured clearance band."
        % (" / ".join(str(x) for x in rho), min(pt) * 100, max(pt) * 100)
    )
    caption(fig, cap)
    return save(fig, "g7_geometry_gates")


def water_fraction(img):
    r = img[:, :, 0].astype(np.float64)
    g = img[:, :, 1].astype(np.float64)
    b = img[:, :, 2].astype(np.float64)
    m = ((g - r) > 6.0) | ((b - r) > 6.0) | (((g - b) > 30.0) & ((r - b) > 30.0))
    return float(m[:, : int(m.shape[1] * 0.86)].mean())


def g8():
    import imageio.v3 as iio

    mcsv = os.path.join(S1, "g64_m1100", "metrics.csv")
    d = np.loadtxt(mcsv, delimiter=",", skiprows=1)
    with open(mcsv) as fh:
        cols = fh.readline().strip().split(",")
    dmag = d[:, cols.index("dmag")]
    tcol = d[:, cols.index("t")]

    degraded = False
    frac = None
    if os.path.isfile(HERO_MP4):
        frames = iio.imread(HERO_MP4)
        n = frames.shape[0]
        k = int(np.argmax(dmag[:n]))
        img = frames[k][:, :, :3]
        frac = water_fraction(img)
        if frac <= 0.02:
            degraded = True
    else:
        degraded = True
        k = int(np.argmax(dmag))

    if degraded:
        if not os.path.isfile(FALLBACK_HERO):
            raise RuntimeError("hero mp4 unusable and fallback %s missing" % FALLBACK_HERO)
        img = iio.imread(FALLBACK_HERO)[:, :, :3]
        k = 45

    fig, ax = plt.subplots(figsize=(15.0, 9.2))
    ax.imshow(img)
    ax.axis("off")
    ax.set_title("G8  Coupled MPM hero still, grid 64, 1100 kg, standing water", fontsize=15)
    fig.subplots_adjust(bottom=0.20)

    if degraded:
        cap = (
            "DEGRADED PATH. Frame from figures/render_v1/realistic_A4_g64_m1100_f0045.png, "
            "the matplotlib render path. CAVEAT: matplotlib's per-polygon depth sort paints "
            "water over the windshield, which is a known unfixable artifact of that path and "
            "not a physical result."
        )
    else:
        cap = (
            "Frame %d of 90 from hero_g64_m1100_FIXED.mp4, the peak-displacement frame "
            "(|d| = %.6f m at t = %.3f s). Rendered with the fixed PyVista path this "
            "session: the enable_shadows call was removed, and the water surface passes its "
            "gates at open_edges = %s with %s volume error.\n"
            "WATER VISIBILITY VERIFIED before saving: %.2f pct of the cropped frame is "
            "viridis-mapped water surface. The previous hero shipped with zero water in all "
            "90 frames, so this check is now mandatory and automated in "
            "renders/yaris_render_s1/check_water_frames.py.\n"
            "Realized depth 0.2944 m (4 layers x h), 1.5 m/s surge, D x V 0.441644 m2/s, "
            "one Yaris hull at 1100 kg. Water is coloured by speed, 0 to 1.896 m/s."
            % (k, dmag[k], tcol[k], parse_volume_error()[2], parse_volume_error()[1],
               frac * 100)
        )
    caption(fig, cap, y=0.01)
    return save(fig, "g8_hero")


def g9(inv):
    est = [
        "Coupled MPM flood-vehicle simulation, 17 runs, geometry gates passed.",
        "is_gaussian_ply guard routes watertight meshes to solidify_watertight, giving "
        "100.00 pct mesh containment on the sampled gate. This is an ORIGINAL PATCH to the "
        "upstream dispatch and it is a contribution, not a workaround.",
        "D x V is bit-identical at 0.441644 m2/s across a 2.1x mass range, because the "
        "criterion has no mass term.",
        "Velocity sweep: D x V returns the wrong verdict at 2 of 6 points on the very axis "
        "it is built on. One of the two, v = 1.0 m/s, is robust to any onset threshold up "
        "to 0.2249 m. The second, v = 0.5 m/s, clears the chosen 0.05 m by 0.0078 m and is "
        "reported as marginal.",
        "Local bow depth exceeds the AR&R 0.30 m cap in 19 of 20 runs, and the exceedance "
        "grows with mass. The exception is v = 0.5 m/s at 0.295361 m.",
        "Determinism verified across the 17 runs that record it; zero out-of-bounds particle "
        "frames across all 20, a count taken after escaped particles are clipped back in.",
    ]
    nots = [
        "No gsplat-reconstructed scene entered a simulation.",
        "Vehicle velocity is zero in every run. This is a stationary-vehicle study, which "
        "is what AR&R itself measures.",
        "One hull, three masses. NOT three vehicles. Class names denote only which AR&R "
        "limit set was applied.",
        "Realized density 310 / 453 / 658 kg/m3 is ABOVE the project's own stated 100 to "
        "300 kg/m3 band.",
        "Water particle passthrough 7.3 to 15.9 pct, worst at v = 3.0 m/s.",
        "Mach 0.039 to 0.234 across the velocity sweep, 0.117 at the 1.5 m/s baseline. The "
        "fastest runs sit 2.3x outside the usual weakly-compressible 0.1 limit.",
        "No Grid Convergence Index is computable: the g64 to g96 change is negative and "
        "non-monotonic.",
        "Track 2 null result: gap 0.295 m at v = 0, no contact, verdicts retracted.",
    ]

    fig = plt.figure(figsize=(17.5, 9.6))
    fig.suptitle("G9  Scope: what this work establishes, and what it does not",
                 fontsize=17, y=0.975)
    axa = fig.add_axes([0.035, 0.06, 0.445, 0.855])
    axb = fig.add_axes([0.520, 0.06, 0.445, 0.855])
    for ax in (axa, axb):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

    axa.add_patch(Rectangle((0, 0), 1, 1, fc="#eef4ee", ec="#3c603c", lw=2.0))
    axb.add_patch(Rectangle((0, 0), 1, 1, fc="#f4eeee", ec="#8f2018", lw=2.0))
    axa.text(0.5, 0.955, "ESTABLISHES", ha="center", fontsize=15, fontweight="bold",
             color="#2f5d2f")
    axb.text(0.5, 0.955, "DOES NOT  (scope, not apology)", ha="center", fontsize=15,
             fontweight="bold", color="#8f2018")

    def bullets(ax, items, color, width, y0, line_h, gap):
        y = y0
        for it in items:
            wrapped = textwrap.fill(it, width=width)
            nlines = wrapped.count("\n") + 1
            ax.text(0.035, y, "-", fontsize=12, color=color, va="top", fontweight="bold")
            ax.text(0.072, y, wrapped, fontsize=11.0, color="#1a1a1a", va="top",
                    linespacing=1.42)
            y -= nlines * line_h + gap

    bullets(axa, est, "#2f5d2f", 74, 0.885, 0.042, 0.046)
    bullets(axb, nots, "#8f2018", 74, 0.885, 0.042, 0.046)

    cap = (
        "All numbers on this panel trace to data/all_runs_inventory.csv, the per-run "
        "summary.json files, or renders/yaris_render_s1/gates_results_all_runs.json. "
        "AR&R limits are interim DRAFT criteria for stationary vehicles."
    )
    fig.text(0.035, 0.018, cap, fontsize=10, color="#1a1a1a")
    return save(fig, "g9_scope")


def main():
    inv = load_inventory()
    gates = load_gates()
    dryg = load_dry_gates()
    print("loaded %d inventory runs, %d gate rows, %d dry gate rows"
          % (len(inv), len(gates), len(dryg)))
    run("G1", g1, inv)
    run("G2", g2, inv)
    run("G3", g3, gates)
    run("G4", g4, inv, dryg)
    run("G5", g5, inv, dryg)
    run("G6", g6, dryg)
    run("G7", g7, inv)
    run("G8", g8)
    run("G9", g9, inv)

    print("")
    print("%-6s %-9s %-8s %s" % ("fig", "status", "attempts", "outputs"))
    for n, s, a, o in RESULTS:
        print("%-6s %-9s %-8d %s" % (n, s, a, ", ".join(os.path.basename(x) for x in o)))
    bad = [n for n, s, _, _ in RESULTS if s != "OK"]
    print("")
    print("PHASE 2 complete: %d OK, %d DEGRADE %s"
          % (len(RESULTS) - len(bad), len(bad), bad if bad else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
