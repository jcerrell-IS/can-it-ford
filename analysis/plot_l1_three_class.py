import argparse
import csv
import hashlib
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[1]

CLASS_ORDER = ("small_passenger", "large_passenger", "large_4wd")
CLASS_LABEL = {
    "small_passenger": "Small passenger",
    "large_passenger": "Large passenger",
    "large_4wd": "Large 4WD",
}
DEPTH_CAP = {"small_passenger": 0.30, "large_passenger": 0.40, "large_4wd": 0.50}
HAZ_CAP = {"small_passenger": 0.30, "large_passenger": 0.45, "large_4wd": 0.60}

EXPECTED_FORD = {"small_passenger": 14, "large_passenger": 19, "large_4wd": 26}
EXPECTED_SENSITIVE = 12
EXPECTED_ROWS = 70

FILL = ["#F4F3EE", "#AECDE5", "#6B99C0", "#33587C"]
INK = "#1F2933"
MUTED = "#5A6472"
SURFACE = "#FFFFFF"
CAP_COLOR = {
    "small_passenger": "#A8322A",
    "large_passenger": "#B36B00",
    "large_4wd": "#1D6B45",
}
CAP_DASH = {"small_passenger": "solid", "large_passenger": (0, (7, 4)),
            "large_4wd": (0, (10, 3, 2, 3))}

DEPTH_STEP = 0.1
VEL_STEP = 0.5


def load_rows(csv_path):
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"STOP: {csv_path} has no data rows")
    return rows


def verify(rows, csv_path):
    problems = []
    if len(rows) != EXPECTED_ROWS:
        problems.append(f"row count {len(rows)}, expected {EXPECTED_ROWS}")
    for c in CLASS_ORDER:
        col = f"L1_verdict_{c}"
        if col not in rows[0]:
            problems.append(f"missing column {col}")
            continue
        n = sum(1 for r in rows if r[col] == "FORD")
        if n != EXPECTED_FORD[c]:
            problems.append(f"{col} FORD={n}, expected {EXPECTED_FORD[c]}")
    if "L1_class_sensitive" not in rows[0]:
        problems.append("missing column L1_class_sensitive")
    else:
        n = sum(1 for r in rows if r["L1_class_sensitive"] == "True")
        if n != EXPECTED_SENSITIVE:
            problems.append(f"L1_class_sensitive True={n}, expected {EXPECTED_SENSITIVE}")
    if problems:
        raise SystemExit(
            "STOP: " + csv_path + " does not match the verified schema:\n  "
            + "\n  ".join(problems)
        )


def cell_records(rows):
    out = []
    for r in rows:
        verdicts = [r[f"L1_verdict_{c}"] for c in CLASS_ORDER]
        n_ford = sum(1 for v in verdicts if v == "FORD")
        ford_set = {c for c, v in zip(CLASS_ORDER, verdicts) if v == "FORD"}
        nested = ford_set in (
            set(),
            {"large_4wd"},
            {"large_4wd", "large_passenger"},
            set(CLASS_ORDER),
        )
        if not nested:
            raise SystemExit(
                f"STOP: non-nested class verdicts at depth={r['depth_m']} "
                f"velocity={r['velocity_ms']}: {sorted(ford_set)}"
            )
        out.append({
            "depth": float(r["depth_m"]),
            "vel": float(r["velocity_ms"]),
            "n_ford": n_ford,
            "sensitive": r["L1_class_sensitive"] == "True",
        })
    return out


def provenance(csv_path):
    p = Path(csv_path)
    data = p.read_bytes()
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "bytes": len(data),
        "mtime": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }


def build(cells, prov, out_path):
    plt.rcParams.update({
        "pdf.fonttype": 42,
        "font.family": "DejaVu Sans",
        "hatch.linewidth": 2.2,
    })

    fig = plt.figure(figsize=(18.667, 13.6), facecolor=SURFACE)
    ax = fig.add_axes([0.095, 0.185, 0.880, 0.640])
    ax.set_facecolor(SURFACE)

    depths = sorted({c["depth"] for c in cells})
    vels = sorted({c["vel"] for c in cells})

    for c in cells:
        x = c["depth"] - DEPTH_STEP / 2
        y = c["vel"] - VEL_STEP / 2
        if c["sensitive"]:
            ax.add_patch(Rectangle(
                (x, y), DEPTH_STEP, VEL_STEP,
                facecolor=FILL[c["n_ford"]], edgecolor=INK,
                linewidth=3.0, hatch="//", zorder=2))
        else:
            ax.add_patch(Rectangle(
                (x, y), DEPTH_STEP, VEL_STEP,
                facecolor=FILL[c["n_ford"]], edgecolor=SURFACE,
                linewidth=2.0, zorder=1))

    halo = [pe.Stroke(linewidth=7.5, foreground=SURFACE, alpha=0.95), pe.Normal()]
    xs = [0.05 + i * (1.0 / 900) for i in range(901)]
    for c in CLASS_ORDER:
        ax.axvline(DEPTH_CAP[c], color=CAP_COLOR[c], linestyle=CAP_DASH[c],
                   linewidth=3.4, zorder=4, path_effects=halo)
        hx, hy = [], []
        for x in xs:
            v = HAZ_CAP[c] / x
            if v <= 3.28:
                hx.append(x)
                hy.append(v)
        ax.plot(hx, hy, color=CAP_COLOR[c], linestyle=CAP_DASH[c],
                linewidth=3.4, zorder=4, path_effects=halo)

    ax.set_xlim(0.05, 1.05)
    ax.set_ylim(-0.25, 3.25)
    ax.set_xticks(depths)
    ax.set_xticklabels([f"{d:.1f}" for d in depths])
    ax.set_yticks(vels)
    ax.set_yticklabels([f"{v:.1f}" for v in vels])
    ax.tick_params(axis="both", labelsize=26, length=8, width=1.6,
                   colors=INK, pad=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
        ax.spines[s].set_linewidth(1.6)

    ax.set_xlabel("Floodwater depth (m)", fontsize=30, color=INK, labelpad=16)
    ax.set_ylabel("Floodwater flow velocity (m/s)", fontsize=30, color=INK, labelpad=16)

    fig.text(0.095, 0.968,
             "Vehicle class decides the verdict in 12 of 70 scenarios",
             fontsize=34, color=INK, ha="left", va="top", weight="bold")
    fig.text(0.095, 0.916,
             "L1 AR&R stationary-vehicle stability screening over a 10 × 7 "
             "depth and velocity grid",
             fontsize=24, color=MUTED, ha="left", va="top")

    counts = {n: sum(1 for c in cells if c["n_ford"] == n) for n in range(4)}
    fill_handles = [
        Patch(facecolor=FILL[3], edgecolor=MUTED, linewidth=1.2,
              label=f"All three classes ford ({counts[3]} cells)"),
        Patch(facecolor=FILL[2], edgecolor=INK, linewidth=2.4, hatch="//",
              label=f"4WD + large passenger ({counts[2]} cells)"),
        Patch(facecolor=FILL[1], edgecolor=INK, linewidth=2.4, hatch="//",
              label=f"Large 4WD only ({counts[1]} cells)"),
        Patch(facecolor=FILL[0], edgecolor=MUTED, linewidth=1.8,
              label=f"No class fords ({counts[0]} cells)"),
        Patch(facecolor=SURFACE, edgecolor=INK, linewidth=3.0, hatch="//",
              label="Hatched: class-sensitive (12)"),
    ]
    line_handles = [
        Line2D([0], [0], color=CAP_COLOR[c], linestyle=CAP_DASH[c], linewidth=3.4,
               label=(f"{CLASS_LABEL[c]} caps: {DEPTH_CAP[c]:.2f} m, "
                      f"{HAZ_CAP[c]:.2f} m²/s"))
        for c in CLASS_ORDER
    ]

    leg = ax.legend(handles=fill_handles + line_handles, loc="upper left",
                    bbox_to_anchor=(0.500, 0.985), bbox_transform=ax.transAxes,
                    fontsize=22, frameon=True, facecolor=SURFACE,
                    edgecolor="#D6D6D0", framealpha=1.0,
                    handlelength=2.6, handleheight=1.6,
                    labelspacing=0.72, borderpad=0.85)
    leg.set_zorder(6)
    for t in leg.get_texts():
        t.set_color(INK)

    fig.text(0.095, 0.045,
             "Caps: Shand, Cox, Blacka and Smith 2011, AR&R Project 10 Stage 2, "
             "P10/S2/020, Table 3, page 14. Draft interim values, not a safety standard.",
             fontsize=16, color=MUTED, ha="left", va="bottom")
    fig.text(0.095, 0.018,
             f"Data: data/scenario_sweep.csv, md5 {prov['md5'][:12]}, "
             f"{prov['bytes']} bytes, {prov['mtime']} CDT.",
             fontsize=16, color=MUTED, ha="left", va="bottom")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf", facecolor=SURFACE)
    plt.close(fig)
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(REPO_ROOT / "data" / "scenario_sweep.csv"))
    ap.add_argument("--out", default=str(REPO_ROOT / "figures" / "L1_three_class_corrected.pdf"))
    args = ap.parse_args()

    rows = load_rows(args.csv)
    verify(rows, args.csv)
    cells = cell_records(rows)
    prov = provenance(args.csv)
    counts = build(cells, prov, Path(args.out))

    print(f"verified: {EXPECTED_ROWS} rows, "
          f"small_passenger={EXPECTED_FORD['small_passenger']}, "
          f"large_passenger={EXPECTED_FORD['large_passenger']}, "
          f"large_4wd={EXPECTED_FORD['large_4wd']}, "
          f"class_sensitive={EXPECTED_SENSITIVE}")
    print(f"cells by classes-that-ford: {counts}")
    print(f"source md5={prov['md5']} bytes={prov['bytes']} mtime={prov['mtime']}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
