import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["savefig.format"] = "pdf"
plt.rcParams["font.size"] = 7
plt.rcParams["axes.linewidth"] = 0.6
plt.rcParams["pdf.fonttype"] = 42

REPO_ROOT = Path(__file__).resolve().parents[1]

G = 9.81
RHO_W = 1000.0

MASS_KG = 1100.0
BBOX_L, BBOX_W, BBOX_H = 4.30, 1.70, 1.47
HULL_M3 = 3.5427
FOOTPRINT_FRAC = 0.75

C_D = 1.38
MU_PRIMARY = 0.30
MU_BAND = (0.30, 0.78)

DEPTHS_LEFT = (0.15, 0.30, 0.45, 0.60)
ARR_SMALL_CAR_DEPTH_CAP = 0.30
L2_TEST_VELOCITY = 1.5

SOURCES = {
    "mass_kg": "NCAC/CCSA 2010 Yaris coarse FE deck header, 'Version 1l, 1100 kg'",
    "bbox_m": "vehicle_params.py, measured from yaris-coarse-v1l FE mesh",
    "hull_m3": "yaris_coarse_v1l_watertight.ply, solidify_watertight volume",
    "C_D": "Smith, Modra & Felder 2019, 1:18 scale Toyota Yaris flume measurement",
    "mu": "Shand et al. 2011 AR&R P10/S2/020 adopted mu=0.30; "
          "Smith, Modra & Felder 2019 worst-case bed mu=0.30, concrete mu=0.78",
    "depth_cap": "Shand et al. 2011, Table 3, printed p.14 (PDF p.24), Small Car 0.30 m",
}

INK = "#1F2933"
MUTED = "#5A6472"
SURFACE = "#FFFFFF"
DEPTH_COLOR = {0.15: "#1D6B45", 0.30: "#2E6DA4", 0.45: "#B36B00", 0.60: "#A8322A"}
CRIT_COLOR = "#1F2933"
FORD_FILL = "#DCEBDD"
NOFORD_FILL = "#F6DEDC"


def prism_volume():
    return BBOX_L * BBOX_W * BBOX_H


def plan_area_effective():
    return FOOTPRINT_FRAC * BBOX_L * BBOX_W


def weight_n():
    return MASS_KG * G


def buoyant_force(depth_m):
    d = np.minimum(np.asarray(depth_m, dtype=float), BBOX_H)
    return RHO_W * G * plan_area_effective() * d


def normal_force(depth_m):
    return np.maximum(0.0, weight_n() - buoyant_force(depth_m))


def friction_limit(depth_m, mu):
    return mu * normal_force(depth_m)


def frontal_area(depth_m):
    d = np.minimum(np.asarray(depth_m, dtype=float), BBOX_H)
    return BBOX_W * d


def drag_force(depth_m, velocity_ms):
    return 0.5 * RHO_W * C_D * frontal_area(depth_m) * np.asarray(velocity_ms, dtype=float) ** 2


def flotation_depth():
    return weight_n() / (RHO_W * G * plan_area_effective())


def critical_velocity(depth_m, mu):
    depth_m = np.asarray(depth_m, dtype=float)
    area = frontal_area(depth_m)
    fric = friction_limit(depth_m, mu)
    out = np.zeros_like(depth_m, dtype=float)
    ok = area > 0
    out[ok] = np.sqrt(2.0 * fric[ok] / (RHO_W * C_D * area[ok]))
    return out


def verify():
    problems = []
    w = weight_n()
    if abs(w - 10791.0) > 1.0:
        problems.append(f"weight {w:.1f} N, expected 10791 N")
    prism = prism_volume()
    if abs(prism - 10.7457) > 1e-3:
        problems.append(f"prism {prism:.4f} m3, expected 10.7457 m3")
    fill = HULL_M3 / prism
    if abs(fill - 0.3297) > 1e-3:
        problems.append(f"fill factor {fill:.4f}, expected 0.3297")
    d_float = flotation_depth()
    if not (0.19 <= d_float <= 0.21):
        problems.append(f"flotation depth {d_float:.4f} m, expected 0.19 to 0.21 m")
    if normal_force(ARR_SMALL_CAR_DEPTH_CAP) > 0:
        problems.append("normal force is nonzero at 0.30 m, expected full flotation")
    for d in (0.30, 0.45, 0.60):
        if critical_velocity(np.array([d]), MU_PRIMARY)[0] > 0:
            problems.append(f"critical velocity nonzero at {d} m, expected 0")
    if d_float >= ARR_SMALL_CAR_DEPTH_CAP:
        problems.append("flotation depth is not below the AR&R Small Car depth cap")
    if problems:
        raise SystemExit("STOP: force-balance model failed its own anchors:\n  "
                         + "\n  ".join(problems))
    return {
        "weight_n": round(w, 1),
        "prism_m3": round(prism, 4),
        "hull_m3": HULL_M3,
        "fill_factor": round(fill, 4),
        "plan_area_eff_m2": round(plan_area_effective(), 4),
        "flotation_depth_m": round(float(d_float), 4),
        "buoyancy_at_0p30_kn": round(float(buoyant_force(0.30)) / 1000.0, 3),
        "normal_at_0p15_n": round(float(normal_force(0.15)), 1),
        "friction_at_0p15_n": round(float(friction_limit(0.15, MU_PRIMARY)), 1),
        "v_crit_at_0p15_ms": round(float(critical_velocity(np.array([0.15]), MU_PRIMARY)[0]), 4),
    }


LAYOUT = {
    "double": dict(figsize=(7.16, 2.65), base=7.0, title=7.5, tick=6.5,
                   legend=5.6, foot=5.2, note=6.0, lw=1.5),
    "single": dict(figsize=(3.5, 2.35), base=5.5, title=5.8, tick=5.0,
                   legend=4.2, foot=3.9, note=4.4, lw=1.1),
}


def build(stats, out_pdf, out_png, layout):
    L = LAYOUT[layout]
    plt.rcParams["font.size"] = L["base"]
    fig, (axL, axR) = plt.subplots(1, 2, figsize=L["figsize"], facecolor=SURFACE)
    for ax in (axL, axR):
        ax.set_facecolor(SURFACE)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(MUTED)
        ax.grid(True, alpha=0.22, lw=0.4)
        ax.tick_params(colors=INK, labelsize=L["tick"])

    v = np.linspace(0.0, 3.0, 400)
    for d in DEPTHS_LEFT:
        fd = drag_force(np.full_like(v, d), v) / 1000.0
        n = float(normal_force(d))
        fr = float(friction_limit(d, MU_PRIMARY)) / 1000.0
        axL.plot(v, fd, color=DEPTH_COLOR[d], lw=L["lw"], zorder=4,
                 label=f"d = {d:.2f} m  (N = {n/1000.0:.2f} kN)")
        axL.axhline(fr, color=DEPTH_COLOR[d], lw=L["lw"] * 0.7, ls=(0, (5, 3)), zorder=3)

    axL.set_xlim(0, 3.0)
    axL.set_ylim(0, 12)
    axL.set_xlabel("Flow velocity (m/s)", fontsize=L["title"], color=INK)
    axL.set_ylabel("Lateral force (kN)", fontsize=L["title"], color=INK)
    axL.set_title("Drag vs. friction limit\nsolid = drag, dashed = $\\mu N$",
                  fontsize=L["title"], color=INK, pad=4)
    axL.legend(fontsize=L["legend"], frameon=True, facecolor=SURFACE, edgecolor="#D6D6D0",
               loc="upper left", handlelength=1.8, borderpad=0.5, labelspacing=0.35)

    d = np.linspace(0.01, 1.0, 500)
    vc_lo = critical_velocity(d, MU_BAND[0])
    vc_hi = critical_velocity(d, MU_BAND[1])
    axR.fill_between(d, vc_lo, vc_hi, color="#B9CBDD", alpha=0.55, lw=0, zorder=2,
                     label=f"$\\mu$ = {MU_BAND[0]:.2f} to {MU_BAND[1]:.2f}")
    axR.plot(d, vc_lo, color=CRIT_COLOR, lw=L["lw"] + 0.1, zorder=5,
             label=f"critical velocity ($\\mu$ = {MU_PRIMARY:.2f})")

    d_float = stats["flotation_depth_m"]
    axR.axvline(d_float, color="#A8322A", lw=1.0, ls=":", zorder=4)
    axR.text(d_float + 0.04, 0.95, f"flotation\n{d_float:.2f} m",
             fontsize=L["note"], color="#A8322A", ha="left", va="bottom", zorder=6)
    axR.axvline(ARR_SMALL_CAR_DEPTH_CAP, color=MUTED, lw=1.0, ls=(0, (6, 3)), zorder=4)
    axR.text(ARR_SMALL_CAR_DEPTH_CAP + 0.04, 0.25,
             "AR&R Small Car\ncap 0.30 m",
             fontsize=L["note"], color=MUTED, ha="left", va="bottom", zorder=6)
    axR.axhline(L2_TEST_VELOCITY, color="#2E6DA4", lw=1.0, ls=(0, (4, 2)), zorder=4,
                label=f"L2 test velocity {L2_TEST_VELOCITY} m/s")

    axR.set_xlim(0, 1.0)
    axR.set_ylim(0, 4.0)
    axR.set_xlabel("Water depth (m)", fontsize=L["title"], color=INK)
    axR.set_ylabel("Critical velocity (m/s)", fontsize=L["title"], color=INK)
    axR.set_title("Critical velocity vs. depth\nzero once buoyancy cancels weight",
                  fontsize=L["title"], color=INK, pad=4)
    axR.legend(fontsize=L["legend"], frameon=True, facecolor=SURFACE, edgecolor="#D6D6D0",
               loc="upper right", handlelength=1.8, borderpad=0.5, labelspacing=0.35)

    parts = [
        "Analytical model, not simulation output.",
        f"$C_D$={C_D} (Smith, Modra & Felder 2019, 1:18 Yaris flume);",
        f"$\\mu$={MU_PRIMARY:.2f} (AR&R adopted, conservative);",
        f"m={MASS_KG:.0f} kg; prism {BBOX_L}x{BBOX_W}x{BBOX_H} m over "
        f"{FOOTPRINT_FRAC:.2f} of footprint.",
    ]
    if layout == "double":
        foot = " ".join(parts)
        rect_bottom = 0.055
    else:
        foot = "\n".join([parts[0] + " " + parts[1], parts[2] + " " + parts[3]])
        rect_bottom = 0.115
    fig.text(0.005, 0.012, foot,
             fontsize=L["foot"], color=MUTED, ha="left", va="bottom")

    fig.tight_layout(rect=[0, rect_bottom, 1, 1])
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, format="pdf", facecolor=SURFACE)
    fig.savefig(out_png, format="png", dpi=400, facecolor=SURFACE)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", choices=("single", "double", "both"), default="both")
    ap.add_argument("--outdir", default=str(REPO_ROOT / "figures"))
    args = ap.parse_args()

    stats = verify()
    outdir = Path(args.outdir)
    wanted = ("single", "double") if args.layout == "both" else (args.layout,)

    print("force-balance anchors verified:")
    for k, val in stats.items():
        print(f"  {k:24s} {val}")
    print("sources:")
    for k, val in SOURCES.items():
        print(f"  {k:12s} {val}")

    for layout in wanted:
        suffix = "" if layout == "double" else "_1col"
        out_pdf = outdir / f"force_balance_v2{suffix}.pdf"
        out_png = outdir / f"force_balance_v2{suffix}.png"
        build(stats, out_pdf, out_png, layout)
        w, h = LAYOUT[layout]["figsize"]
        print(f"wrote {out_pdf}  [{layout}, {w}x{h} in]")
        print(f"wrote {out_png}")

    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
