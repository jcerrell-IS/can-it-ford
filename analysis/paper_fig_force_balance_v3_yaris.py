"""paper_fig_force_balance_v3_yaris.py
====================================
Yaris-only version of the v3 force-balance figure for the paper (Fig. 4), with the two
other estimates of where the car stops being safe drawn on the same axes:

  (a) buoyancy over weight of the Yaris hull mesh against water depth, with its flotation depth;
  (b) critical flow velocity against depth from the quasi-static sliding balance
      mu (W - B) = 0.5 rho C_d A V^2, using the hull's own submerged volume B and projected area A
      (functions imported unchanged from paper_fig_force_balance_v3.py), together with
      - the limiting curve of Smith, Modra and Felder 2019 Eq. 6, a single fit over their three test cars,
        evaluated at their 2006 Yaris sedan's floor-pan height (imported unchanged from smith_eq6_l1.py), and
      - the AR&R small-passenger limit, read from vehicle_params.AR_R_STABILITY_LIMITS.

Why a separate file: the three-hull v3 figure also plots a 2020 Nissan Rogue whose 1571.3 kg mass is
recorded as web-sourced and pinned to no published trim (noted in the development repository),
so the paper uses the one canonical hull only. Nothing in the v3 script is changed.

Run from the repository root:
    python3 analysis/paper_fig_force_balance_v3_yaris.py --out <dir>/force_balance_v3_yaris
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import paper_fig_force_balance_v3 as v3  # noqa: E402
import smith_eq6_l1 as eq6  # noqa: E402
sys.path.insert(0, str(HERE.parent))
from vehicle_params import AR_R_STABILITY_LIMITS  # noqa: E402  (Shand et al. 2011 Table 3)

_ARR = AR_R_STABILITY_LIMITS["small_passenger"]
ARR_DEPTH_CAP_M = _ARR["depth_m"]
ARR_DV_CAP = _ARR["haz_m2s"]
ARR_V_CAP = _ARR["velocity_ms"]

MASS_KG = 1100.0          # vehicle_params.py mass_kg (CCSA FE model 1101 kg, rounded)
L2_POINT = (0.30, 1.5)    # requested depth and nominal velocity of the canonical coupled runs


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cd", type=float, default=1.38)
    p.add_argument("--cd-band", type=float, nargs=2, default=[1.0, 1.8])
    p.add_argument("--mu", type=float, nargs=3, default=[0.30, 0.55, 0.78])
    p.add_argument("--out", default=str(HERE.parent / "figures" / "force_balance_v3_yaris"))
    a = p.parse_args()
    v3.font()
    mu_lo, mu_mid, mu_hi = a.mu

    table_path = v3.TABLES / "yaris_geometry.json"
    table = json.loads(table_path.read_text())
    d = np.round(np.arange(0.0, 0.7001, 0.0025), 4)
    c = v3.curves(table, MASS_KG, a.cd, a.mu, d, a.cd_band)
    d_float = v3.flotation_depth(table, MASS_KG)
    v_eq6 = np.array([np.nan if (x := eq6.eq6_limit_velocity(float(di))) is None else x for di in d])
    v_eq6[v_eq6 <= 0.0] = np.nan

    fig, (axa, axb) = plt.subplots(2, 1, figsize=(3.4, 4.6), dpi=600,
                                   gridspec_kw={"height_ratios": [0.62, 1.25], "hspace": 1.05})
    blue, orange, grey = "#0072B2", "#D55E00", "0.35"

    axa.plot(d, c["buoy_over_weight"], color=blue)
    axa.axhline(1.0, color=grey, lw=0.6, ls=":")
    axa.plot([d_float], [1.0], marker="o", color=blue, ms=3.5, mec="black", mew=0.4, ls="none")
    axa.annotate("hull mesh floats, %.2f m" % d_float, (d_float, 1.0), xytext=(0.035, 1.45),
                 fontsize=7, color="0.2", arrowprops=dict(arrowstyle="-", lw=0.5, color="0.4"))
    axa.set_xlim(0, 0.7)
    axa.set_ylim(0, 2.1)
    axa.set_xlabel("water depth $D$ (m)", labelpad=1.5)
    axa.set_ylabel("buoyancy / weight", labelpad=2)
    axa.text(-0.17, 1.02, "(a)", transform=axa.transAxes, fontsize=8, fontweight="bold", va="bottom")

    dry = d < d_float
    lo = np.where(dry, np.minimum(c["uc_env_lo"], 9.0), np.nan)
    hi = np.where(dry, np.minimum(c["uc_env_hi"], 9.0), np.nan)
    axb.fill_between(d, lo, hi, color=blue, alpha=0.15, lw=0,
                     label="sliding band, $\\mu$ %.2f to %.2f, $C_d$ %.1f to %.1f"
                     % (mu_lo, mu_hi, a.cd_band[0], a.cd_band[1]))
    for mu, lw, ls in ((mu_lo, 0.7, "--"), (mu_mid, 1.2, "-"), (mu_hi, 0.7, "--")):
        y = np.where(dry, np.minimum(c["uc_mu%.2f" % mu], 9.0), np.nan)
        lab = "sliding, $\\mu$ %.2f, $C_d$ %.2f" % (mu_mid, a.cd) if mu == mu_mid else None
        axb.plot(d, y, color=blue, lw=lw, ls=ls, label=lab)
    axb.plot(d, v_eq6, color=orange, lw=1.1, ls="-.", label="Smith et al. Eq. 6, Yaris floor pan")
    dd = np.linspace(0.02, ARR_DEPTH_CAP_M, 200)
    axb.plot(dd, np.minimum(ARR_DV_CAP / dd, ARR_V_CAP), color="black", lw=0.9, ls=":",
             label="AR&R small passenger limit")
    axb.plot([ARR_DEPTH_CAP_M, ARR_DEPTH_CAP_M], [0, ARR_DV_CAP / ARR_DEPTH_CAP_M], color="black", lw=0.9, ls=":")
    axb.plot([L2_POINT[0]], [L2_POINT[1]], marker="s", color="0.5", mec="black", mew=0.4, ms=3.2, ls="none",
             label="coupled-run condition")
    axb.axvline(d_float, color=grey, lw=0.5, ls=":")
    axb.set_xlim(0, 0.7)
    axb.set_ylim(0, 4.0)
    axb.set_xlabel("water depth $D$ (m)", labelpad=1.5)
    axb.set_ylabel("flow velocity $V$ (m/s)", labelpad=2)
    axb.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), fontsize=6.5, frameon=False, handlelength=2.2,
               borderaxespad=0.1)
    axb.text(-0.17, 1.47, "(b)", transform=axb.transAxes, fontsize=8, fontweight="bold", va="bottom")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out) + ".pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(str(out) + ".png", dpi=600, bbox_inches="tight", pad_inches=0.02)

    def at(arr, x):
        return float(np.interp(x, d, arr))

    summary = {
        "mass_kg": MASS_KG, "cd": a.cd, "cd_band": a.cd_band, "mu": a.mu,
        "table": str(table_path.relative_to(HERE.parent)), "table_sha256": sha(table_path),
        "mesh_sha256": table["mesh_sha256"], "flotation_depth_hull_m": d_float,
        "at_0p30m": {
            "projected_area_m2": at(c["area_m2"], 0.30), "buoyancy_over_weight": at(c["buoy_over_weight"], 0.30),
            "uc_mu_lo_ms": at(c["uc_mu%.2f" % mu_lo], 0.30), "uc_mu_mid_ms": at(c["uc_mu%.2f" % mu_mid], 0.30),
            "uc_mu_hi_ms": at(c["uc_mu%.2f" % mu_hi], 0.30),
            "uc_envelope_ms": [at(c["uc_env_lo"], 0.30), at(c["uc_env_hi"], 0.30)],
            "eq6_limit_ms": eq6.eq6_limit_velocity(0.30), "arr_limit_ms": ARR_DV_CAP / 0.30,
            "length_x_depth_over_projected": 0.30 * c["length_m"] / at(c["area_m2"], 0.30),
        },
        "eq6_still_water_limit_m": eq6.COEFFS["D_PAN_YARIS_2006_M"][0] + eq6.COEFFS["EQ6_INTERCEPT_M"][0],
        "script_sha256": sha(__file__), "v3_script_sha256": sha(v3.__file__), "eq6_script_sha256": sha(eq6.__file__),
    }
    Path(str(out) + "_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
