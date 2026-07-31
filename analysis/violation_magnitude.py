import argparse
import json

import numpy as np
import pandas as pd

T_REF = 0.05
NEAR_FRAC = 0.10


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inventory", default="data/all_runs_inventory.csv")
    p.add_argument("--out-json", default="violation_magnitude.json")
    p.add_argument("--out-tex", default="table_violation_magnitude.tex")
    a = p.parse_args()

    df = pd.read_csv(a.inventory).copy()
    df["ratio_at_0.05"] = df["final_disp_mag_m"] / T_REF
    df["excess_pct_at_0.05"] = 100.0 * (df["ratio_at_0.05"] - 1.0)
    df["near_boundary_0.05"] = df["ratio_at_0.05"].between(1 - NEAR_FRAC, 1 + NEAR_FRAC)
    df = df.sort_values("final_disp_mag_m").reset_index(drop=True)

    t_grid = np.round(np.arange(0.01, 1.001, 0.01), 4)
    frac = {}
    for _, r in df.iterrows():
        frac[r["run"]] = [float(r["final_disp_mag_m"] / t) for t in t_grid]

    near_any = {}
    for _, r in df.iterrows():
        hits = [float(t) for t in t_grid if abs(r["final_disp_mag_m"] / t - 1.0) <= NEAR_FRAC]
        near_any[r["run"]] = [min(hits), max(hits)] if hits else None

    cols = ["run", "label", "requested_depth_m", "velocity_ms", "mass_kg", "n_grid",
            "final_disp_mag_m", "ratio_at_0.05", "excess_pct_at_0.05", "near_boundary_0.05"]
    tbl = df[cols]

    lines = [
        r"\begin{table}[t]",
        r"\caption{Violation magnitude at the $0.05$\,m L2 drift threshold. "
        r"Ratio is final drift divided by the threshold; no run falls within $\pm10\%$ of the "
        r"boundary. Reproduce with \texttt{python3 analysis/violation\_magnitude.py "
        r"--inventory data/all\_runs\_inventory.csv}.}",
        r"\label{tab:violation}",
        r"\centering",
        r"\begin{tabular}{lrrrrr}",
        r"\hline",
        r"Run & $D$ (m) & $V$ (m/s) & $m$ (kg) & drift (m) & drift$/t$ \\",
        r"\hline",
    ]
    for _, r in tbl.iterrows():
        lines.append(
            "%s & %.2f & %.1f & %.0f & %.4f & %.2f \\\\"
            % (str(r["run"]).replace("_", r"\_"), r["requested_depth_m"], r["velocity_ms"],
               r["mass_kg"], r["final_disp_mag_m"], r["ratio_at_0.05"])
        )
    lines += [r"\hline", r"\end{tabular}", r"\end{table}", ""]
    with open(a.out_tex, "w") as f:
        f.write("\n".join(lines))

    payload = {
        "threshold_m": T_REF,
        "near_boundary_fraction": NEAR_FRAC,
        "n_runs": int(len(df)),
        "n_within_10pct_at_0.05": int(df["near_boundary_0.05"].sum()),
        "min_ratio_at_0.05": float(df["ratio_at_0.05"].min()),
        "max_ratio_at_0.05": float(df["ratio_at_0.05"].max()),
        "closest_run": str(df.loc[df["ratio_at_0.05"].idxmin(), "run"]),
        "closest_excess_pct": float(df["excess_pct_at_0.05"].min()),
        "table": tbl.to_dict("records"),
        "t_where_each_run_is_within_10pct": near_any,
        "grid_convergence_at_d0.30_v1.5": {
            str(m): {
                str(int(g)): float(
                    df[(df["mass_kg"] == m) & (df["n_grid"] == g) & (df["sweep"] == "mass_grid")][
                        "final_disp_mag_m"
                    ].iloc[0]
                )
                for g in [48, 64, 96]
            }
            for m in sorted(df["mass_kg"].unique())
        },
    }
    gc = payload["grid_convergence_at_d0.30_v1.5"]
    payload["grid_spread_ratio"] = {
        m: float(max(v.values()) / min(v.values())) for m, v in gc.items()
    }
    with open(a.out_json, "w") as f:
        json.dump(payload, f, indent=2)

    pd.set_option("display.width", 200)
    print(tbl.to_string(index=False))
    print()
    print("within 10%% of 0.05 m boundary:", payload["n_within_10pct_at_0.05"])
    print("closest run:", payload["closest_run"], "at +%.1f%%" % payload["closest_excess_pct"])
    print("grid convergence (disp m) at D=0.30 V=1.5:", json.dumps(gc, indent=2))
    print("grid spread ratio (max/min):", json.dumps(payload["grid_spread_ratio"], indent=2))


if __name__ == "__main__":
    main()
