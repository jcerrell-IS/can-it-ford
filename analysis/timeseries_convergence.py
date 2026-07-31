import argparse
import glob
import json
import os

import numpy as np
import pandas as pd

ONSET_M = 0.01
TAIL_FRAC = 0.20
PLATEAU_TOL = 0.10
REVERSAL_TOL = 0.99


def analyse(path):
    d = pd.read_csv(path)
    n = len(d)
    dmag = d["dmag"].to_numpy()
    vmag = d["vmag"].to_numpy()
    t = d["t"].to_numpy()

    above = np.nonzero(dmag > ONSET_M)[0]
    onset = int(above[0]) if above.size else None

    peak_i = int(dmag.argmax())
    peak = float(dmag[peak_i])
    final = float(dmag[-1])
    final_over_peak = float(final / peak) if peak > 0 else float("nan")

    diffs = np.diff(dmag)
    n_down = int((diffs < 0).sum())

    tail_start = int(n * (1.0 - TAIL_FRAC))
    slope_tail = float((dmag[-1] - dmag[tail_start]) / (t[-1] - t[tail_start]))
    slope_max = float(np.max(np.abs(diffs / np.diff(t))))
    slope_ratio = float(slope_tail / slope_max) if slope_max > 0 else float("nan")
    plateaued = bool(abs(slope_ratio) < PLATEAU_TOL)

    post = vmag[peak_i:]
    v_min_post = float(post.min()) if post.size else float("nan")
    v_end = float(vmag[-1])
    reaccelerating = bool(v_end > 2.0 * v_min_post) if v_min_post > 0 else False

    return {
        "run": os.path.basename(os.path.dirname(path)),
        "n_frames": n,
        "t_end_s": float(t[-1]),
        "onset_frame": onset,
        "peak_frame": peak_i,
        "peak_dmag_m": peak,
        "final_dmag_m": final,
        "final_over_peak": final_over_peak,
        "understatement_pct": float(100.0 * (1.0 - final_over_peak)),
        "peak_is_interior": bool(peak_i < n - 1),
        "n_decreasing_steps": n_down,
        "monotonic": bool(n_down == 0),
        "tail_slope_over_max_slope": slope_ratio,
        "plateaued": plateaued,
        "terminal_speed_ms": v_end,
        "min_speed_after_peak_ms": v_min_post,
        "max_speed_ms": float(vmag.max()),
        "terminal_over_max_speed": float(v_end / vmag.max()),
        "reaccelerating_at_truncation": reaccelerating,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--incoming", default="renders/yaris_render_s1/_incoming")
    p.add_argument("--out-json", default="timeseries_convergence.json")
    a = p.parse_args()

    paths = sorted(glob.glob(os.path.join(a.incoming, "*", "metrics.csv")))
    rows = [analyse(q) for q in paths]
    df = pd.DataFrame(rows)

    payload = {
        "n_runs_with_metrics": len(rows),
        "columns_present": list(pd.read_csv(paths[0], nrows=1).columns),
        "criteria": {
            "onset_m": ONSET_M,
            "tail_fraction": TAIL_FRAC,
            "plateau_tol_abs_slope_ratio": PLATEAU_TOL,
            "reaccel_rule": "terminal speed > 2x minimum speed after peak",
        },
        "runs": rows,
        "summary": {
            "n_monotonic": int(df["monotonic"].sum()),
            "n_peak_interior": int(df["peak_is_interior"].sum()),
            "n_plateaued": int(df["plateaued"].sum()),
            "n_not_plateaued": int((~df["plateaued"]).sum()),
            "not_plateaued_runs": df.loc[~df["plateaued"], "run"].tolist(),
            "n_reaccelerating": int(df["reaccelerating_at_truncation"].sum()),
            "reaccelerating_runs": df.loc[df["reaccelerating_at_truncation"], "run"].tolist(),
            "max_understatement_pct": float(df["understatement_pct"].max()),
            "worst_understatement_run": str(df.loc[df["understatement_pct"].idxmax(), "run"]),
            "median_understatement_pct": float(df["understatement_pct"].median()),
            "onset_frame_range": [int(df["onset_frame"].min()), int(df["onset_frame"].max())],
            "peak_frame_range": [int(df["peak_frame"].min()), int(df["peak_frame"].max())],
        },
    }
    with open(a.out_json, "w") as f:
        json.dump(payload, f, indent=2)

    pd.set_option("display.width", 250)
    show = ["run", "onset_frame", "peak_frame", "peak_dmag_m", "final_dmag_m",
            "understatement_pct", "plateaued", "terminal_over_max_speed",
            "reaccelerating_at_truncation"]
    print(df[show].to_string(index=False))
    print()
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
