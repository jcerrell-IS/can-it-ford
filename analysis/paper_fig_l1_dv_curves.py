import argparse
import hashlib
import json
import os
import time

import matplotlib
matplotlib.use("PDF")
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CLASSES = [
    ("small_passenger", "Small passenger", 0.30, 0.30, "#0072B2", "-", 1.7),
    ("large_passenger", "Large passenger", 0.40, 0.45, "#D55E00", "--", 1.7),
    ("large_4wd", "Large 4WD", 0.50, 0.60, "#009E73", "-.", 1.7),
]
V_LIMIT = 3.0
EXPECTED_FORD = {"small_passenger": 14, "large_passenger": 19, "large_4wd": 26}
EXPECTED_SENSITIVE = 12
HULL_LENGTH_M = 4.2826
FLOAT_TRAP = {}


def boundary(depth_cap, haz_cap, n=600):
    d = np.linspace(1e-4, depth_cap, n)
    v = np.minimum(haz_cap / d, V_LIMIT)
    return np.concatenate([d, [depth_cap]]), np.concatenate([v, [0.0]])


def verify(df):
    problems = []
    for key, _, dcap, hcap, _, _, _ in CLASSES:
        col = "L1_verdict_%s" % key
        stored_ford = (df[col] == "FORD")
        n = int(stored_ford.sum())
        if n != EXPECTED_FORD[key]:
            problems.append("%s FORD count %d, expected %d" % (col, n, EXPECTED_FORD[key]))
        implied = (df["depth_m"] <= dcap) & (df["L1_haz"] <= hcap)
        bad = int((implied != stored_ford).sum())
        if bad:
            problems.append("%s: drawn boundary disagrees with stored column on %d of %d rows"
                            % (col, bad, len(df)))
        naive = (df["depth_m"] <= dcap) & (df["depth_m"] * df["velocity_ms"] <= hcap)
        FLOAT_TRAP[key] = int((naive != stored_ford).sum())
    n_sens = int(df["L1_class_sensitive"].sum())
    if n_sens != EXPECTED_SENSITIVE:
        problems.append("L1_class_sensitive %d, expected %d" % (n_sens, EXPECTED_SENSITIVE))
    s = (df["L1_verdict_small_passenger"] == "FORD")
    l = (df["L1_verdict_large_passenger"] == "FORD")
    w = (df["L1_verdict_large_4wd"] == "FORD")
    if not bool((s <= l).all()) or not bool((l <= w).all()):
        problems.append("class nesting small subset-of large subset-of 4wd is violated")
    if problems:
        raise SystemExit("VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    return {"ford": {k: int((df["L1_verdict_%s" % k] == "FORD").sum()) for k in EXPECTED_FORD},
            "class_sensitive": n_sens}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenarios", default="data/scenario_sweep.csv")
    p.add_argument("--out-pdf", default="l1_dv_curves.pdf")
    p.add_argument("--out-json", default="l1_dv_curves.json")
    a = p.parse_args()

    raw = open(a.scenarios, "rb").read()
    md5 = hashlib.md5(raw).hexdigest()
    st = os.stat(a.scenarios)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))

    df = pd.read_csv(a.scenarios)
    counts = verify(df)

    fig, ax = plt.subplots(figsize=(3.5, 2.95))

    sens = df["L1_class_sensitive"].astype(bool)
    ax.scatter(df.loc[~sens, "depth_m"], df.loc[~sens, "velocity_ms"], s=5.5,
               c="#8A8A8A", marker="o", linewidths=0, zorder=2, label="scenario grid (70)")
    ax.scatter(df.loc[sens, "depth_m"], df.loc[sens, "velocity_ms"], s=42,
               facecolors="none", edgecolors="#222222", linewidths=1.0, zorder=4,
               label="class-sensitive (%d)" % counts["class_sensitive"])

    for key, name, dcap, hcap, colour, style, lw in CLASSES:
        d, v = boundary(dcap, hcap)
        ax.plot(d, v, color=colour, ls=style, lw=lw, zorder=3, solid_capstyle="round",
                label="%s (%d ford)" % (name, counts["ford"][key]))

    ax.set_xlim(0.0, 1.05)
    ax.set_ylim(0.0, 3.15)
    ax.set_xlabel("Floodwater depth $D$ (m)", fontsize=8)
    ax.set_ylabel("Flow velocity $V$ (m/s)", fontsize=8)
    ax.tick_params(axis="both", labelsize=7.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, lw=0.3, color="0.88", zorder=0)
    ax.set_axisbelow(True)
    leg = ax.legend(fontsize=5.9, frameon=True, loc="upper right",
                    handlelength=2.4, borderaxespad=0.35, labelspacing=0.32,
                    facecolor="white", edgecolor="#CCCCCC", framealpha=0.96)
    leg.get_frame().set_linewidth(0.4)
    leg.set_zorder(6)
    for t in leg.get_texts():
        t.set_color("#1A1A1A")

    ax.text(0.0, -0.185,
            "Caps: Shand, Cox, Blacka and Smith 2011, AR&R P10/S2/020, Table 3, p.14. "
            "Draft interim values, not a safety standard.\n"
            "Formula evaluation, not simulation output. "
            "Data: %s, md5 %s, %d bytes, %s."
            % (os.path.basename(a.scenarios), md5[:12], len(raw), stamp),
            transform=ax.transAxes, fontsize=4.5, color="#3A3A3A", va="top")

    fig.savefig(a.out_pdf, format="pdf", bbox_inches="tight")

    payload = {
        "source": os.path.abspath(a.scenarios),
        "md5": md5,
        "bytes": len(raw),
        "mtime": stamp,
        "ford_counts": counts["ford"],
        "class_sensitive": counts["class_sensitive"],
        "caps": {k: {"depth_cap_m": dc, "hazard_cap_m2s": hc, "limiting_velocity_ms": V_LIMIT}
                 for k, _, dc, hc, _, _, _ in CLASSES},
        "arr_length_criterion_m": {"small_passenger": "< 4.3", "large_passenger": "> 4.3",
                                   "large_4wd": "> 4.5"},
        "hull_length_m": HULL_LENGTH_M,
        "hull_class_match": {"small_passenger": HULL_LENGTH_M < 4.3,
                             "large_passenger": HULL_LENGTH_M > 4.3,
                             "large_4wd": HULL_LENGTH_M > 4.5},
        "float_trap_cells_if_product_recomputed_inline": FLOAT_TRAP,
    }
    with open(a.out_json, "w") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload, indent=2))
    print("wrote", os.path.abspath(a.out_pdf))


if __name__ == "__main__":
    main()
