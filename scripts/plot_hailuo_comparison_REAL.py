import argparse
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCES = {
    "track1_v1_sedan": os.path.join(
        REPO, "data", "track1_sweep_v1",
        "veh-sedan_dep-0p30_vel-1p50_idx-0004_timeseries.csv"),
    "metrics_check": os.path.join(
        REPO, "data", "metrics_d0p30_v1p5_check.csv"),
    "flood_vehicle": os.path.join(
        REPO, "data", "flood_vehicle_metrics_d0p3_v1p5.csv"),
}

L2_PILOT_CSV = os.path.join(REPO, "data", "l2_results_from_wandb.csv")

DRIFT_THRESHOLD_M = 0.05
DEPTH_M = 0.30
VELOCITY_MS = 1.5


def load_series(path):
    t, dmag = [], []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            t.append(float(row["t"]))
            dmag.append(float(row["dmag"]))
    return t, dmag


def load_pilot_verdict(path, depth, velocity):
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        for row in csv.DictReader(fh):
            if (abs(float(row["depth_m"]) - depth) < 1e-9
                    and abs(float(row["velocity_ms"]) - velocity) < 1e-9):
                return row
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=sorted(SOURCES), default="track1_v1_sedan")
    ap.add_argument("--out", default=os.path.join(
        REPO, "figures", "baseline_comparison_REAL.png"))
    args = ap.parse_args()

    path = SOURCES[args.source]
    if not os.path.exists(path):
        sys.exit("ABSENT: %s" % path)

    t, dmag = load_series(path)
    peak = max(dmag)
    final = dmag[-1]

    pilot = load_pilot_verdict(L2_PILOT_CSV, DEPTH_M, VELOCITY_MS)

    print("SOURCE FILE      %s" % os.path.relpath(path, REPO))
    print("SAMPLES          %d, t = 0 to %.3f s" % (len(t), t[-1]))
    print("PEAK dmag        %.6f m" % peak)
    print("FINAL dmag       %.6f m" % final)
    print("DRIFT_THRESHOLD  %.2f m (solver-internal onset-of-motion detector)" % DRIFT_THRESHOLD_M)
    for key in sorted(SOURCES):
        if key == args.source or not os.path.exists(SOURCES[key]):
            continue
        _, other = load_series(SOURCES[key])
        print("DISPUTED         %s reports peak %.6f m at the same (d, v)"
              % (key, max(other)))
    if pilot is None:
        print("PILOT ROW        none at d=%.2f v=%.2f in %s"
              % (DEPTH_M, VELOCITY_MS, os.path.relpath(L2_PILOT_CSV, REPO)))
    else:
        print("PILOT ROW        level=%s l1=%s l2=%s"
              % (pilot["level"], pilot["l1_verdict"], pilot["l2_verdict"]))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(t, dmag, lw=2.0, color="#1f4e79",
            label="measured |displacement|, %s" % args.source)
    ax.axhline(DRIFT_THRESHOLD_M, ls="--", lw=1.4, color="#b00020",
               label="DRIFT_THRESHOLD = %.2f m" % DRIFT_THRESHOLD_M)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("displacement magnitude (m)")
    ax.set_title("Coupled-run drift at d = %.2f m, v = %.1f m/s\n"
                 "source: %s" % (DEPTH_M, VELOCITY_MS,
                                 os.path.relpath(path, REPO)), fontsize=10)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)

    note = ("Peak %.4f m, final %.4f m, read from the CSV at run time.\n"
            "This trace is NOT the Genesis SPH pilot: that pilot has only a\n"
            "9-row summary (data/l2_results_from_wandb.csv) and no time series.\n"
            "No artifact in figures/hailuo/ records a Hailuo verdict."
            % (peak, final))
    ax.text(0.02, 0.97, note, transform=ax.transAxes, va="top", fontsize=7.5,
            bbox=dict(boxstyle="round", fc="#fff8e1", ec="#c8a415", alpha=0.95))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fig.tight_layout()
    fig.savefig(args.out, dpi=200)
    print("WROTE            %s" % os.path.relpath(args.out, REPO))


if __name__ == "__main__":
    main()
