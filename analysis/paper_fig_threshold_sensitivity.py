import argparse
import json
import os

import matplotlib
matplotlib.use("PDF")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

T_GRID = np.round(np.arange(0.01, 1.001, 0.01), 4)


def l1_column_for(label):
    return "L1_verdict_%s" % label


def stratify_by_grid(mpm, inv):
    m = mpm.merge(inv[["run", "n_grid"]], on="run")
    out = {}
    for g, sub in m.groupby("n_grid"):
        w = full_agreement_window(sub)
        out[str(int(g))] = {
            "n": int(len(sub)),
            "full_agreement_window_m": w,
            "any_t_with_full_agreement": w is not None,
            "max_disp_among_L1_FORD_m": float(sub.loc[sub["l1_verdict"] == "FORD", "disp_m"].max()),
            "min_disp_among_L1_NOFORD_m": float(sub.loc[sub["l1_verdict"] == "NO-FORD", "disp_m"].min()),
        }
    wins = [v["full_agreement_window_m"] for v in out.values() if v["full_agreement_window_m"]]
    inter = None
    if len(wins) == len(out):
        lo = max(w[0] for w in wins)
        hi = min(w[1] for w in wins)
        inter = [lo, hi] if lo < hi else None
    out["_windows_intersect_across_grids"] = inter is not None
    out["_intersection_m"] = inter
    return out


def build_mpm(inventory, scenarios):
    inv = pd.read_csv(inventory)
    sc = pd.read_csv(scenarios)
    key = sc.set_index(["depth_m", "velocity_ms"])
    rows = []
    unmatched = []
    for _, r in inv.iterrows():
        k = (round(float(r["requested_depth_m"]), 6), round(float(r["velocity_ms"]), 6))
        if k not in key.index:
            unmatched.append({"run": r["run"], "requested_depth_m": k[0], "velocity_ms": k[1]})
            continue
        s = key.loc[k]
        rows.append(
            {
                "run": r["run"],
                "label": r["label"],
                "depth_m": k[0],
                "velocity_ms": k[1],
                "realized_depth_m": float(r["realized_depth_m"]),
                "disp_m": float(r["final_disp_mag_m"]),
                "l1_verdict": str(s[l1_column_for(r["label"])]),
                "l1_haz": float(s["L1_haz"]),
            }
        )
    return pd.DataFrame(rows), unmatched, len(inv), len(sc)


def build_sph(wandb_csv, phase_csv):
    w = pd.read_csv(wandb_csv)
    p = pd.read_csv(phase_csv)
    p = p.assign(disp_m=np.hypot(p["final_x_disp_m"], p["final_y_disp_m"]))
    g = p.groupby(["depth_m", "velocity_ms"])["disp_m"]
    uniq = g.nunique()
    mean = g.mean()
    rows = []
    ambiguous = []
    for _, r in w.iterrows():
        k = (round(float(r["depth_m"]), 6), round(float(r["velocity_ms"]), 6))
        if k not in mean.index:
            ambiguous.append({"cond": k, "why": "no displacement row"})
            continue
        if int(uniq.loc[k]) > 1:
            ambiguous.append({"cond": k, "why": "%d conflicting displacement rows" % int(uniq.loc[k])})
            continue
        rows.append(
            {
                "depth_m": k[0],
                "velocity_ms": k[1],
                "disp_m": float(mean.loc[k]),
                "l1_verdict": str(r["l1_verdict"]),
                "l2_verdict_logged": str(r["l2_verdict"]),
                "dv_product": float(r["dv_product"]),
            }
        )
    return pd.DataFrame(rows), ambiguous, len(w)


def agreement_curve(df):
    out = []
    l1_no = (df["l1_verdict"] == "NO-FORD").to_numpy()
    disp = df["disp_m"].to_numpy()
    for t in T_GRID:
        l2_no = disp > t
        out.append(float((l2_no == l1_no).mean()))
    return np.array(out)


def full_agreement_window(df):
    l1_no = (df["l1_verdict"] == "NO-FORD").to_numpy()
    disp = df["disp_m"].to_numpy()
    if l1_no.all() or (~l1_no).all():
        return None
    lo = disp[~l1_no].max()
    hi = disp[l1_no].min()
    if lo < hi:
        return [float(lo), float(hi)]
    return None


def summarize(df, name):
    cur = agreement_curve(df)
    win = full_agreement_window(df)
    peak = float(cur.max())
    peak_t = [float(t) for t, c in zip(T_GRID, cur) if c == peak]
    at05 = float(cur[np.isclose(T_GRID, 0.05)][0])
    near = [float(c) for t, c in zip(T_GRID, cur) if 0.03 <= t <= 0.07]
    return {
        "name": name,
        "n": int(len(df)),
        "agreement_at_0.05": at05,
        "peak_agreement": peak,
        "peak_t_range_m": [min(peak_t), max(peak_t)] if peak_t else None,
        "any_t_with_full_agreement": win is not None,
        "full_agreement_window_m": win,
        "agreement_0.03_to_0.07": near,
        "flatness_0.03_to_0.07_max_minus_min": float(max(near) - min(near)),
    }, cur


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inventory", default="data/all_runs_inventory.csv")
    p.add_argument("--scenarios", default="data/scenario_sweep.csv")
    p.add_argument("--sph-wandb", default="data/l2_results_from_wandb.csv")
    p.add_argument("--sph-phase", default="data/phase_space_results.csv")
    p.add_argument("--out-pdf", default="threshold_sensitivity.pdf")
    p.add_argument("--out-json", default="threshold_sensitivity.json")
    a = p.parse_args()

    mpm, unmatched, n_inv, n_sc = build_mpm(a.inventory, a.scenarios)
    sph, ambiguous, n_w = build_sph(a.sph_wandb, a.sph_phase)

    m_sum, m_cur = summarize(mpm, "MPM 17-run sweep")
    s_sum, s_cur = summarize(sph, "SPH pilot")

    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    ax.step(T_GRID, 100 * m_cur, where="post", color="#C44E52", lw=1.5,
            label="MPM (n=%d matched)" % len(mpm))
    ax.step(T_GRID, 100 * s_cur, where="post", color="#4C72B0", lw=1.5, ls="-",
            label="SPH pilot (n=%d)" % len(sph))
    ax.axvline(0.05, color="0.25", ls="--", lw=0.9)
    ax.annotate("0.05 m", xy=(0.05, 4), xytext=(0.062, 4), fontsize=7, color="0.25")
    if s_sum["full_agreement_window_m"]:
        lo, hi = s_sum["full_agreement_window_m"]
        ax.axvspan(lo, hi, color="#4C72B0", alpha=0.12, lw=0)
    ax.set_xscale("log")
    ax.set_xlim(0.01, 1.0)
    ax.set_ylim(0, 105)
    ax.set_xlabel(r"L2 drift threshold $t$ (m)", fontsize=8)
    ax.set_ylabel("L1 vs L2 agreement (%)", fontsize=8)
    ax.tick_params(axis="both", labelsize=7.5)
    ax.legend(fontsize=6.5, frameon=False, loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout(pad=0.4)
    fig.savefig(a.out_pdf, format="pdf", bbox_inches="tight")

    payload = {
        "matching": {
            "rule": "exact join on (requested_depth_m, velocity_ms) == (depth_m, velocity_ms)",
            "n_runs_total": n_inv,
            "n_scenarios_total": n_sc,
            "n_matched": int(len(mpm)),
            "unmatched_runs": unmatched,
            "distinct_matched_cells": sorted({(r.depth_m, r.velocity_ms) for r in mpm.itertuples()}),
        },
        "sph": {"n_logged": n_w, "n_usable": int(len(sph)), "excluded": ambiguous},
        "mpm_summary": m_sum,
        "mpm_by_grid": stratify_by_grid(mpm, pd.read_csv(a.inventory)),
        "sph_summary": s_sum,
        "mpm_rows": mpm.to_dict("records"),
        "sph_rows": sph.to_dict("records"),
        "curve_t": [float(t) for t in T_GRID],
        "curve_mpm": [float(c) for c in m_cur],
        "curve_sph": [float(c) for c in s_cur],
    }
    with open(a.out_json, "w") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload["matching"], indent=2, default=str))
    print(json.dumps({"mpm": m_sum, "sph": s_sum, "sph_excluded": ambiguous}, indent=2, default=str))
    print("BY GRID:", json.dumps(payload["mpm_by_grid"], indent=2, default=str))
    print("wrote", os.path.abspath(a.out_pdf))


if __name__ == "__main__":
    main()
