"""Three-hull force-balance figure (v3). This repository includes only the Yaris table
(simulation/steady_force/hull_tables/yaris_geometry.json), so running this file directly needs the
Rogue and Silverado tables from the development repository. The paper figure,
paper_fig_force_balance_v3_yaris.py, imports curves(), flotation_depth() and font() from here.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

REPO = Path(__file__).resolve().parents[1]
TABLES = REPO / "simulation" / "steady_force" / "hull_tables"
RHO = 1000.0
G = 9.81
VEHICLES = [
    ("yaris", "2010 Toyota Yaris", 1100.0, "small_passenger", "#0072B2", "-", "o"),
    ("rogue", "2020 Nissan Rogue", 1571.3, "large_passenger", "#E69F00", "--", "s"),
    ("silverado", "2007 Chevrolet Silverado", 2270.0, "large_4wd", "#009E73", "-.", "^"),
]
ARR = {"small_passenger": (0.30, 0.30), "large_passenger": (0.40, 0.45), "large_4wd": (0.50, 0.60)}
V_CAP = 3.0


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def font():
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
              "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if Path(f).exists():
            font_manager.fontManager.addfont(f)
            plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
            break
    plt.rcParams.update({"font.size": 8, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                         "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
                         "lines.linewidth": 1.1, "pdf.fonttype": 42, "ps.fonttype": 42})


def curves(table, mass, cd, mus, d, cd_band=None):
    z = np.asarray(table["z_m"])
    vsub = np.interp(d, z, table["submerged_volume_m3"])
    length = float(table["extent_m"][1])
    # Drag reference area: the hull's own submerged projected area facing the flow (+x), as in
    # WRL TR 2017/07 Eq. 3, which defines C_d with each vehicle's projected profile area. Length x
    # full depth ignores the ground clearance and is about 2.16x too large at 0.30 m for this hull.
    ax = np.interp(d, z, table["projected_area_flow_x_m2"])
    w = mass * G
    b = RHO * G * vsub
    n = np.maximum(w - b, 0.0)
    out = {"buoy_over_weight": b / w, "normal_N": n, "area_m2": ax, "vsub_m3": vsub}
    def uc(mu, c):
        with np.errstate(divide="ignore", invalid="ignore"):
            v = np.sqrt(2.0 * mu * n / (RHO * c * np.maximum(ax, 1e-12)))
        return np.where(ax > 1e-9, v, np.inf)
    for mu in mus:
        out["uc_mu%.2f" % mu] = uc(mu, cd)
    if cd_band is not None:
        out["uc_env_lo"] = uc(min(mus), max(cd_band))
        out["uc_env_hi"] = uc(max(mus), min(cd_band))
    out["length_m"] = length
    return out


def flotation_depth(table, mass):
    z = np.asarray(table["z_m"])
    v = np.asarray(table["submerged_volume_m3"])
    need = mass / RHO
    i = int(np.searchsorted(v, need))
    if i == 0 or i >= len(z):
        return float("nan")
    return float(z[i - 1] + (need - v[i - 1]) * (z[i] - z[i - 1]) / (v[i] - v[i - 1]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cd", type=float, default=1.38)
    p.add_argument("--cd-band", type=float, nargs=2, default=[1.0, 1.8])
    p.add_argument("--mu", type=float, nargs=3, default=[0.30, 0.55, 0.78])
    p.add_argument("--out", default=str(REPO / "figures" / "force_balance_v3"))
    a = p.parse_args()
    font()
    mu_lo, mu_mid, mu_hi = a.mu
    d = np.round(np.arange(0.0, 0.7001, 0.0025), 4)
    data, rows = {}, []
    summary = {"cd": a.cd, "cd_band": a.cd_band, "mu": a.mu, "rho": RHO, "g": G,
               "drag_reference_area": "submerged projected area of the hull facing the flow, from hull_tables (WRL TR 2017/07 Eq. 3 uses each vehicle's own projected area)",
               "cd_source": "mean of the 48 side-on Toyota Yaris tests in WRL TR 2017/07 Table 6-1 is 1.377; "
                            "range 0.98 to 1.74; the report states 1.0 to 1.8",
               "buoyancy": "rho g V_sub(D) of the watertight hull mesh, which encloses the body structure and interior parts but not the cabin air (about 30 percent of its bounding box)", "vehicles": {}}
    for key, label, mass, cls, *_ in VEHICLES:
        tp = TABLES / ("%s_geometry.json" % key)
        t = json.loads(tp.read_text())
        c = curves(t, mass, a.cd, a.mu, d, a.cd_band)
        data[key] = c
        dfl = flotation_depth(t, mass)
        uc03 = float(np.interp(0.30, d, c["uc_mu%.2f" % mu_mid]))
        summary["vehicles"][key] = {
            "label": label, "mass_kg": mass, "arr_class": cls, "table": str(tp.relative_to(REPO)),
            "table_sha256": sha(tp), "mesh_sha256": t["mesh_sha256"],
            "flotation_depth_hull_m": dfl,
            "uc_at_0p30m_mu_mid_ms": uc03,
            "vsub_at_0p30m_m3": float(np.interp(0.30, d, c["vsub_m3"])),
            "area_ref_at_0p30m_m2": float(np.interp(0.30, d, c["area_m2"])),
            "length_m": c["length_m"],
            "uc_at_0p30m_envelope_ms": [float(np.interp(0.30, d, c["uc_env_lo"])),
                                         float(np.interp(0.30, d, c["uc_env_hi"]))],
        }
        for i, di in enumerate(d):
            rows.append({"vehicle": key, "depth_m": float(di), "vsub_m3": float(c["vsub_m3"][i]),
                         "area_ref_projected_m2": float(c["area_m2"][i]),
                         "uc_env_lo_ms": float(c["uc_env_lo"][i]), "uc_env_hi_ms": float(c["uc_env_hi"][i]),
                         "buoyancy_over_weight": float(c["buoy_over_weight"][i]),
                         **{"uc_mu%.2f_ms" % mu: float(c["uc_mu%.2f" % mu][i]) for mu in a.mu}})

    fig, (axa, axb) = plt.subplots(2, 1, figsize=(3.4, 4.2), dpi=600,
                                   gridspec_kw={"height_ratios": [1.0, 1.25], "hspace": 0.62})
    for key, label, mass, cls, col, ls, mk in VEHICLES:
        c = data[key]
        axa.plot(d, c["buoy_over_weight"], color=col, ls=ls, label="%s, %d kg" % (label.split(" ")[-1], round(mass)))
        dfl = summary["vehicles"][key]["flotation_depth_hull_m"]
        axa.plot([dfl], [1.0], marker=mk, color=col, ms=3.5, mec="black", mew=0.4, ls="none")
    axa.axhline(1.0, color="0.25", lw=0.6, ls=":")
    axa.set_xlim(0, 0.7)
    axa.set_ylim(0, 2.2)
    axa.set_xlabel("water depth $D$ (m)", labelpad=1.5)
    axa.set_ylabel("buoyancy / weight", labelpad=2)
    axa.text(0.012, 1.035, "buoyancy = weight: the hull mesh floats", fontsize=7, color="0.25", va="bottom")
    axa.legend(loc="upper left", fontsize=7, frameon=False, handlelength=2.4, borderaxespad=0.2,
               bbox_to_anchor=(0.0, 1.0))
    axa.text(-0.17, 1.02, "(a)", transform=axa.transAxes, fontsize=8, fontweight="bold", va="bottom")

    offsets = {"yaris": -0.011, "rogue": 0.0, "silverado": 0.011}
    for key, label, mass, cls, col, ls, mk in VEHICLES:
        c = data[key]
        dfl = summary["vehicles"][key]["flotation_depth_hull_m"]
        flo = d >= dfl
        mid = np.where(flo, np.nan, np.minimum(c["uc_mu%.2f" % mu_mid], 9.0))
        axb.plot(d, mid, color=col, ls=ls)
        for dbar in (0.20, 0.30, 0.40):
            if dbar >= dfl:
                continue
            lo_v = float(np.interp(dbar, d, c["uc_env_lo"]))
            hi_v = float(np.interp(dbar, d, c["uc_env_hi"]))
            mid_v = float(np.interp(dbar, d, c["uc_mu%.2f" % mu_mid]))
            xb = dbar + offsets[key]
            axb.errorbar([xb], [mid_v], yerr=[[mid_v - lo_v], [max(min(hi_v, 3.98) - mid_v, 0.0)]],
                         fmt=mk, ms=2.8, color=col, mec="black", mew=0.35, elinewidth=0.8, capsize=1.6,
                         capthick=0.8, zorder=4)
        dcap, dv = ARR[cls]
        dd = np.linspace(0.02, dcap, 200)
        axb.plot(dd, np.minimum(dv / dd, V_CAP), color=col, ls=":", lw=0.9)
        axb.plot([dcap, dcap], [0, min(dv / dcap, V_CAP)], color=col, ls=":", lw=0.9)
    axb.set_xlim(0, 0.7)
    axb.set_ylim(0, 4.0)
    axb.set_xlabel("water depth $D$ (m)", labelpad=1.5)
    axb.set_ylabel("flow velocity $V$ (m/s)", labelpad=2)
    h1 = matplotlib.lines.Line2D([], [], color="0.2", lw=1.1,
                                 label="sliding, $\\mu$ %.2f, $C_d$ %.2f" % (mu_mid, a.cd))
    h2 = matplotlib.lines.Line2D([], [], color="0.2", lw=0.8, marker="o", ms=2.8, mfc="0.6", mec="black",
                                 mew=0.35, label="bars: $\\mu$ %.2f to %.2f, $C_d$ %.1f to %.1f"
                                 % (mu_lo, mu_hi, a.cd_band[0], a.cd_band[1]))
    h3 = matplotlib.lines.Line2D([], [], color="0.2", lw=0.9, ls=":", label="AR&R class limit")
    axb.legend(handles=[h1, h3, h2], loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=1, fontsize=7,
               frameon=False, handlelength=1.8, columnspacing=1.0, borderaxespad=0.15)
    axb.text(-0.17, 1.27, "(b)", transform=axb.transAxes, fontsize=8, fontweight="bold", va="bottom")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out) + ".pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(str(out) + ".png", dpi=600, bbox_inches="tight", pad_inches=0.02)
    with open(str(out) + "_data.csv", "w", newline="") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wtr.writeheader()
        wtr.writerows(rows)
    summary["script_sha256"] = sha(__file__)
    Path(str(out) + "_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
