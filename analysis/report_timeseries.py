"""Apply the measurement protocol to a time series and emit a reportable result.

This is the entry point Dispatch 9 (and anything else producing a force, displacement
or velocity trace) points at its output. It exists so that using the protocol is one
command rather than an integration exercise, and so that the SAME code path produces
every number that gets quoted.

    python analysis/report_timeseries.py --csv run/metrics.csv --column dmag --fps 30
    python analysis/report_timeseries.py --npz out/forces.npz --column fz --fps 30 \
        --window 1.0 3.5
    python analysis/report_timeseries.py --csv f.csv --column fz --fps 30 \
        --condition-above 0.05 --hold-frames 3

WHAT IT REFUSES TO DO. If the series is not demonstrably stationary it will not print a
mean, because there is nothing defensible to print. It prints the impulse, the peak and
its time, the envelope and the dominant frequency instead, and says why. That refusal is
the point of the tool: a fabricated steady force is the failure mode the protocol
exists to prevent, and it is easiest to commit by accident at exactly the moment a
number is needed for a figure.

Exit status is 0 whether or not the series is stationary. Non-stationary is a RESULT,
not an error, and must not be something a pipeline retries until it goes away.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stationarity import (  # noqa: E402
    analyse, prespecified_window, verdict_probability,
)


def load_series(args) -> tuple[np.ndarray, str]:
    if args.csv:
        rows = list(csv.DictReader(open(args.csv)))
        if not rows:
            raise SystemExit("empty csv: %s" % args.csv)
        if args.column not in rows[0]:
            raise SystemExit("column %r not in %s; available: %s"
                             % (args.column, args.csv, ", ".join(rows[0].keys())))
        return np.array([float(r[args.column]) for r in rows]), str(args.csv)
    z = np.load(args.npz, mmap_mode="r")
    if args.column not in z:
        raise SystemExit("key %r not in %s; available: %s"
                         % (args.column, args.npz, ", ".join(list(z.keys()))))
    a = np.asarray(z[args.column], dtype=np.float64)
    if a.ndim != 1:
        raise SystemExit("key %r has shape %s; this tool takes a 1-D series"
                         % (args.column, a.shape))
    return a, str(args.npz)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv")
    src.add_argument("--npz")
    p.add_argument("--column", required=True)
    p.add_argument("--fps", type=float, default=30.0)
    p.add_argument("--alpha-z", type=float, default=2.0,
                   help="stationarity threshold in standard errors (stated convention)")
    p.add_argument("--window", nargs=2, type=float, metavar=("T0", "T1"),
                   help="PRESPECIFIED constant-speed interior window, in seconds. "
                        "Must be chosen BEFORE looking at the trace.")
    p.add_argument("--condition-above", type=float, default=None,
                   help="reframe 'series > VALUE held for --hold-frames' as a probability")
    p.add_argument("--hold-frames", type=int, default=3)
    p.add_argument("--json-out", default=None)
    a = p.parse_args()

    x, src_name = load_series(a)
    dt = 1.0 / a.fps
    t = np.arange(x.size, dtype=np.float64) * dt

    print("SOURCE   %s [%s]" % (src_name, a.column), flush=True)
    print("RECORD   %d samples at %.4g fps = %.4g s" % (x.size, a.fps, x.size * dt),
          flush=True)

    r = analyse(x, dt=dt, alpha_z=a.alpha_z)
    out = {"source": src_name, "column": a.column, "fps": a.fps,
           "protocol": r.as_dict()}

    print("\n--- PROTOCOL ---", flush=True)
    print(r.summary(), flush=True)
    if r.equilibration_hit_cap:
        print("WARNING: the equilibration search hit its retention floor. The optimiser "
              "wanted to discard past 90 percent of the record, which means this series "
              "does not equilibrate within its own length.", flush=True)
    if r.stationary and not r.plateau_found:
        print("WARNING: the blocking curve did not reach a plateau, so the record is too "
              "short to resolve its own correlation time. The quoted error bar is a "
              "LOWER BOUND.", flush=True)
    if r.stationary and r.n_eff < 20:
        print("WARNING: N_eff = %.1f. Fewer than 20 effectively independent samples; "
              "quote the error bar, never the sample count." % r.n_eff, flush=True)

    if a.window:
        t0, t1 = a.window
        w = prespecified_window(t, x, t0, t1)
        out["prespecified_window"] = w
        print("\n--- PRESPECIFIED WINDOW [%g, %g] s ---" % (t0, t1), flush=True)
        if not w["ok"]:
            print("REFUSED: %s" % w["reason"], flush=True)
        else:
            print("mean %.6g  +/- %.4g (correlated)   naive %.4g   inflation %.2fx"
                  % (w["mean"], w["stderr_correlated"], w["stderr_naive"],
                     w["stderr_inflation"]), flush=True)
            print("interior stationary: %s" % w["interior_stationarity"]["stationary"],
                  flush=True)
            print("window sensitivity spread %.4g (symmetric-only %.4g), "
                  "filter sensitivity spread %.4g"
                  % (w["window_sensitivity_spread"],
                     w["window_sensitivity_spread_symmetric_only"],
                     w["filter_sensitivity_spread"]), flush=True)
            if w["sensitivity_exceeds_stderr"]:
                print("WARNING: the quoted uncertainty is dominated by the choice of "
                      "window and filter, not by the simulation. Report it that way.",
                      flush=True)

    if a.condition_above is not None:
        cond = x > a.condition_above
        v = verdict_probability(cond, hold_frames=a.hold_frames)
        out["verdict"] = v
        out["verdict_condition"] = "%s > %g held %d frames" % (a.column, a.condition_above,
                                                               a.hold_frames)
        print("\n--- VERDICT AS A PROBABILITY ---", flush=True)
        print("condition: %s > %g, held for %d consecutive frames"
              % (a.column, a.condition_above, a.hold_frames), flush=True)
        for k in ("record_frames", "activity_rate", "longest_run", "margin_frames",
                  "triggered", "p_trigger", "bootstrap_block_len"):
            print("  %-20s %s" % (k, v[k]), flush=True)
        print("  p_trigger is conditional on record_frames = %d. Never quote it alone."
              % v["record_frames"], flush=True)

    if a.json_out:
        Path(a.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json_out).write_text(json.dumps(out, indent=2, default=str))
        print("\nWROTE %s" % a.json_out, flush=True)


if __name__ == "__main__":
    main()
