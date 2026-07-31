import argparse
import json
import os

import matplotlib
matplotlib.use("PDF")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODES = ["STUCK", "SLIDE", "TOPPLE", "FLOAT"]
MODE_COLOR = {"STUCK": "#4C72B0", "SLIDE": "#DD8452", "TOPPLE": "#C44E52", "FLOAT": "#55A868"}

BASE_D_CUT = 0.05
BASE_R_CUT = 1.0
BASE_Z_CUT = 0.01


def classify(df, d_cut, r_cut, z_cut):
    out = []
    for _, r in df.iterrows():
        moved = float(r["final_disp_mag_m"]) > d_cut
        rolled = abs(float(r["final_roll_deg"])) > r_cut
        rose = float(r["C2_veh_zmin_rise"]) > z_cut
        if rose:
            out.append("FLOAT")
        elif moved and rolled:
            out.append("TOPPLE")
        elif moved:
            out.append("SLIDE")
        else:
            out.append("STUCK")
    return pd.Series(out, index=df.index)


def counts(labels):
    c = labels.value_counts().to_dict()
    return [int(c.get(m, 0)) for m in MODES]


def sweep_axis(df, values, which):
    rows = []
    for v in values:
        if which == "d":
            lab = classify(df, v, BASE_R_CUT, BASE_Z_CUT)
        elif which == "r":
            lab = classify(df, BASE_D_CUT, v, BASE_Z_CUT)
        else:
            lab = classify(df, BASE_D_CUT, BASE_R_CUT, v)
        rows.append(counts(lab))
    return np.array(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inventory", default="data/all_runs_inventory.csv")
    p.add_argument("--out-pdf", default="failure_modes.pdf")
    p.add_argument("--out-json", default="failure_modes.json")
    a = p.parse_args()

    df = pd.read_csv(a.inventory)
    base = classify(df, BASE_D_CUT, BASE_R_CUT, BASE_Z_CUT)
    df = df.assign(mode=base)

    d_vals = np.round(np.arange(0.01, 1.001, 0.01), 4)
    r_vals = np.round(np.arange(0.05, 10.001, 0.05), 4)
    z_vals = np.round(np.arange(0.001, 0.0501, 0.001), 5)

    d_sweep = sweep_axis(df, d_vals, "d")
    r_sweep = sweep_axis(df, r_vals, "r")
    z_sweep = sweep_axis(df, z_vals, "z")

    fig, ax = plt.subplots(1, 3, figsize=(7.16, 2.35))

    order = ["STUCK", "SLIDE", "TOPPLE", "FLOAT"]
    cts = counts(base)
    ax[0].bar(order, cts, color=[MODE_COLOR[m] for m in order], width=0.62)
    for i, v in enumerate(cts):
        ax[0].text(i, v + 0.35, str(v), ha="center", va="bottom", fontsize=8)
    ax[0].set_ylim(0, max(cts) + 2.2)
    ax[0].set_ylabel("runs (of %d)" % len(df))
    ax[0].set_title("(a) modes at operational cutoffs", fontsize=8)
    ax[0].tick_params(axis="both", labelsize=7.5)

    for j, m in enumerate(MODES):
        ax[1].step(d_vals, d_sweep[:, j], where="post", color=MODE_COLOR[m], label=m, lw=1.3)
    ax[1].axvline(BASE_D_CUT, color="0.25", ls="--", lw=0.9)
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"displacement cutoff $d_{\rm cut}$ (m)", fontsize=8)
    ax[1].set_ylabel("runs", fontsize=8)
    ax[1].set_title("(b) sweep of displacement cutoff", fontsize=8)
    ax[1].tick_params(axis="both", labelsize=7.5)
    ax[1].legend(fontsize=6.2, frameon=False, ncol=2, loc="center left")

    for j, m in enumerate(MODES):
        ax[2].step(r_vals, r_sweep[:, j], where="post", color=MODE_COLOR[m], label=m, lw=1.3)
    ax[2].axvline(BASE_R_CUT, color="0.25", ls="--", lw=0.9)
    ax[2].set_xscale("log")
    ax[2].set_xlabel(r"roll cutoff $r_{\rm cut}$ (deg)", fontsize=8)
    ax[2].set_title("(c) sweep of roll cutoff", fontsize=8)
    ax[2].tick_params(axis="both", labelsize=7.5)

    for x in ax:
        x.spines["top"].set_visible(False)
        x.spines["right"].set_visible(False)

    fig.tight_layout(pad=0.5)
    fig.savefig(a.out_pdf, format="pdf", bbox_inches="tight")

    r_stable = len(set(map(tuple, r_sweep)))
    z_stable = len(set(map(tuple, z_sweep)))

    payload = {
        "n_runs": int(len(df)),
        "baseline_cutoffs": {"d_cut_m": BASE_D_CUT, "r_cut_deg": BASE_R_CUT, "z_cut_m": BASE_Z_CUT},
        "baseline_counts": dict(zip(MODES, counts(base))),
        "per_run": [
            {
                "run": r["run"],
                "label": r["label"],
                "requested_depth_m": float(r["requested_depth_m"]),
                "velocity_ms": float(r["velocity_ms"]),
                "mass_kg": float(r["mass_kg"]),
                "n_grid": int(r["n_grid"]),
                "final_disp_mag_m": float(r["final_disp_mag_m"]),
                "final_roll_deg": float(r["final_roll_deg"]),
                "final_pitch_deg": float(r["final_pitch_deg"]),
                "final_yaw_deg": float(r["final_yaw_deg"]),
                "C2_veh_zmin_rise": float(r["C2_veh_zmin_rise"]),
                "mode": r["mode"],
            }
            for _, r in df.iterrows()
        ],
        "sweep_distinct_outcomes": {
            "d_cut_0.01_to_1.00_step_0.01": int(len(set(map(tuple, d_sweep)))),
            "r_cut_0.05_to_10.00_step_0.05": int(r_stable),
            "z_cut_0.001_to_0.050_step_0.001": int(z_stable),
        },
        "float_is_unmeasurable": {
            "max_C2_veh_zmin_rise_m": float(df["C2_veh_zmin_rise"].max()),
            "n_runs_with_positive_rise_above_1e-6": int((df["C2_veh_zmin_rise"] > 1e-6).sum()),
            "zmin_final_equals_3dx_max_abs_dev_m": float((df["C2_veh_zmin_final"] - 3 * df["dx"]).abs().max()),
        },
    }
    with open(a.out_json, "w") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload["baseline_counts"], indent=2))
    print("distinct outcomes:", json.dumps(payload["sweep_distinct_outcomes"]))
    print("float check:", json.dumps(payload["float_is_unmeasurable"]))
    print("wrote", os.path.abspath(a.out_pdf), os.path.abspath(a.out_json))


if __name__ == "__main__":
    main()
