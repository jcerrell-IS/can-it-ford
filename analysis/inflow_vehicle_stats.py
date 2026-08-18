#!/usr/bin/env python3
"""
inflow_vehicle_stats.py  --  reduce the recycling-in/outflow vehicle runs and print
every number the write-up quotes, with its enumeration rather than a bare total.

INPUT is a directory of run directories produced by scripts/inflow_vehicle_wrapper.py.
Each run directory must hold metrics.csv and summary.json (written by the canonical
driver) and, for wrapped runs, inflow_summary.json and inflow_instrument.npz.

The run directory NAME carries the arm: <config>__<arm>__rep<N>. arm is one of
  bare      the unwrapped canonical driver, the wrapper-inertness control
  closed    wrapped, streamwise walls present, x clamped   (matched control)
  recycle   wrapped, streamwise walls dropped, outflow recycles to inflow
  recycnb   as recycle but with sim_standing's upstream velocity band removed

WHAT IT REFUSES TO DO
It does not average a verdict. Verdicts are tallied, never meaned. It does not quote a
magnitude without the profile row window it was taken over, because the closed arm is
contaminated by its own wall reflection from about frame 112 and the recycle arm is not.

Usage
  /opt/homebrew/bin/uv run --with numpy python3 analysis/inflow_vehicle_stats.py \
      --runs <dir> [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "simulation"))
sys.path.insert(0, str(REPO))

import failure_modes as FM  # noqa: E402
from vehicle_params import get_vehicle  # noqa: E402

SSF = float(get_vehicle("compact_sedan")["ssf"])
ARMS = ("bare", "closed", "recycle", "recycnb")


def classify_at(metrics_csv, mass_kg, last_row):
    """Verdict using only metrics rows 0..last_row inclusive.

    Truncate BEFORE differentiating, not after: np.gradient over the full series would
    let post-horizon frames influence the accelerations inside the horizon, and TOPPLE is
    scored on acceleration.
    """
    cols = FM.load_timeseries(metrics_csv)
    n = len(cols["t"])
    k = min(int(last_row), n - 1)
    cut = {name: np.asarray(v)[: k + 1] for name, v in cols.items()}
    kin = FM.kinematics_from_columns(cut, mass_kg)
    res = FM.classify_kinematics(kin, SSF)
    return res, k, n, kin


def summarize(run_dir: Path):
    s = json.loads((run_dir / "summary.json").read_text())
    iw_path = run_dir / "inflow_summary.json"
    iw = json.loads(iw_path.read_text()) if iw_path.exists() else None
    mass = float(s["mass_kg"])
    metrics = run_dir / "metrics.csv"

    row = {
        "_dir": str(run_dir),
        "run": run_dir.name,
        "arm": run_dir.name.split("__")[1] if "__" in run_dir.name else "?",
        "config": run_dir.name.split("__")[0],
        "n_grid": s["n_grid"], "mass_kg": mass,
        "velocity_ms": s["velocity_ms"], "depth_m": s["depth_m"],
        "realized_depth_m": None,
        "frames": s["frames"],
        "final_disp_mag_m": s["final_disp_mag_m"],
        "local_depth_bow_peak": s["local_depth_bow_peak"],
        "local_depth_bow_peak_frame": s["local_depth_bow_peak_frame"],
        "local_depth_footprint_peak": s["local_depth_footprint_peak"],
        "passthrough_max_frac": s["passthrough_max_frac"],
        "leaked_particle_frames": s["leaked_particle_frames"],
        "C2_veh_zmin_rise": s["C2_veh_zmin_rise"],
        "C3_oob_particle_frames": s["C3_oob_particle_frames"],
        "n_water": s["n_water"],
        "determinism_identical": s["determinism_identical"],
    }

    for horizon, tag in ((90, "h90"), (10 ** 9, "hend")):
        res, k, n, kin = classify_at(metrics, mass, horizon)
        row["metrics_rows"] = n
        row["verdict_" + tag] = res.mode.value
        row["row_" + tag] = k
        # Full 3-vector norm, the same statistic the driver writes as final_disp_mag_m.
        row["dmag_" + tag] = float(np.linalg.norm(kin.disp[k]))
        row["max_surge_drift_" + tag] = float(res.max_surge_drift_m)
        row["max_vertical_lift_" + tag] = float(res.max_vertical_lift_m)
        idx = res.first_index.get(FM.FailureMode.SLIDE)
        row["onset_slide_" + tag] = (None if idx is None or idx < 0 else int(idx))
        row["sustained_" + tag] = {m.value: bool(v) for m, v in res.sustained.items()}

    if iw is not None:
        row["realized_depth_m"] = iw["realized_depth_m"]
        row["bc"] = iw["bc"]
        row["band"] = iw["band"]
        row["n_dropped_planes"] = iw["n_dropped_planes"]
        row["recycled_total"] = iw["recycled_total"]
        row["tagged_frac_final"] = iw["tagged_frac_final"]
        row["first_tagged_near_vehicle_frame"] = iw["first_tagged_near_vehicle_frame"]
        row["max_overshoot_m"] = iw["max_overshoot_m"]
        row["stream_reflection_frame"] = iw["reflection_prediction"]["stream_reflection_frame"]
        row["cross_reflection_frame"] = iw["reflection_prediction"]["cross_reflection_frame"]
        for wname, w in iw["free_surface_slope"].items():
            row["slope_" + wname] = w["slope_m_per_m"]
            row["spread_" + wname] = w["spread_m"]
            row["drained_" + wname] = w["drained_bins"]
        for k2, v in iw["budget_final_pct_of_water"].items():
            row["pct_" + k2] = v
        row["min_z_ever"] = iw["min_z_ever"]
        row["floor_m"] = iw["floor_m"]
        row["floor_penetration_final_m"] = iw["floor_m"] - iw["min_z_ever"]
    return row


def reflection_arrivals(prof, fit_lo=40, fit_hi=90, start=90, k=4.0, sustain=3):
    """Per-bin first row at/after `start` whose depth departs from the rows fit_lo..fit_hi
    linear trend by more than k residual sigmas for `sustain` consecutive rows.

    Returns a list with one entry per bin, None where the bin never departs or holds too
    few finite rows to fit. The DETREND is the load-bearing part: a closed box piles water
    downstream steadily, so an undetrended threshold fires on the pile-up rather than on
    the reflection and would report an arrival in both arms.
    """
    out = []
    n = prof.shape[0]
    for b in range(prof.shape[1]):
        y = prof[:, b]
        rows = np.arange(n, dtype=float)
        m = np.isfinite(y)
        base = m.copy(); base[:fit_lo] = False; base[fit_hi:] = False
        if base.sum() < 10:
            out.append(None); continue
        c = np.polyfit(rows[base], y[base], 1)
        resid = y - np.polyval(c, rows)
        sig = float(np.std(resid[base]))
        if not np.isfinite(sig) or sig <= 0:
            out.append(None); continue
        hit = np.zeros(n, dtype=bool)
        idx = np.arange(start, n)
        hit[idx] = np.isfinite(y[idx]) & (np.abs(resid[idx]) > k * sig)
        found = None
        run = 0
        for r in range(start, n):
            run = run + 1 if hit[r] else 0
            if run >= sustain:
                found = r - sustain + 1
                break
        out.append(found)
    return out


def slope_series(prof, centres):
    """Free-surface slope, m/m, fitted independently at EVERY profile row.

    This is the discriminator that survived. The residual-based arrival detector above
    fires at row 91 in both arms, i.e. immediately at the start of its search window,
    because a line fitted over rows 40..89 does not extrapolate past 89 in either arm; it
    therefore separates nothing and is reported, not deleted, so the failure is on record.
    A slope fitted per row needs no model of what the series should have been doing.
    """
    n = prof.shape[0]
    out = np.full(n, np.nan)
    for r in range(n):
        y = prof[r]
        fin = np.isfinite(y)
        if fin.sum() >= 3:
            out[r] = float(np.polyfit(centres[fin], y[fin], 1)[0])
    return out


def first_sign_change(sl, start=40):
    """First row at or after `start` where the slope changes sign and STAYS changed for 5
    rows. In a closed basin this is the moment the water that piled downstream has come
    back; there is no equivalent event in an open channel."""
    n = len(sl)
    ref = None
    for r in range(start, n):
        if not np.isfinite(sl[r]):
            continue
        if ref is None:
            ref = np.sign(sl[r])
            continue
        if np.sign(sl[r]) != ref and ref != 0:
            seg = sl[r:r + 5]
            seg = seg[np.isfinite(seg)]
            if len(seg) >= 3 and np.all(np.sign(seg) != ref):
                return r
    return None


def agg(values):
    v = [x for x in values if x is not None and np.isfinite(x)]
    if not v:
        return None
    if len(v) == 1:
        return {"n": 1, "mean": float(v[0]), "sd": None,
                "min": float(v[0]), "max": float(v[0])}
    return {"n": len(v), "mean": float(statistics.mean(v)),
            "sd": float(statistics.stdev(v)),
            "min": float(min(v)), "max": float(max(v))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--npz", default=None,
                    help="consolidate every run's per-frame depth profile, water budget "
                         "and recycle trace into ONE npz small enough to commit, so the "
                         "evidence behind the tables is git-visible rather than living "
                         "only on Vista")
    a = ap.parse_args()

    root = Path(a.runs)
    dirs = sorted(d for d in root.iterdir()
                  if d.is_dir() and (d / "summary.json").exists()
                  and (d / "metrics.csv").exists())
    if not dirs:
        raise SystemExit("no complete run directories under %s" % root)
    rows = [summarize(d) for d in dirs]

    print("=" * 100)
    print("RUNS FOUND: %d under %s" % (len(rows), root))
    for r in rows:
        print("  %-46s arm=%-8s rows=%4d  verdict@90=%-6s verdict@end=%-6s"
              % (r["run"], r["arm"], r["metrics_rows"], r["verdict_h90"], r["verdict_hend"]))

    by = defaultdict(list)
    for r in rows:
        by[(r["config"], r["arm"])].append(r)

    print()
    print("=" * 100)
    print("1. WRAPPER INERTNESS. bare (unwrapped canonical driver) vs closed (wrapped).")
    print("   These must agree to within the run-to-run spread; the wrapper adds only")
    print("   read-only instrumentation in the closed arm.")
    for cfgname in sorted({r["config"] for r in rows}):
        b = by.get((cfgname, "bare"), [])
        c = by.get((cfgname, "closed"), [])
        if not b or not c:
            continue
        print("  %s" % cfgname)
        for field in ("final_disp_mag_m", "local_depth_bow_peak", "passthrough_max_frac",
                      "leaked_particle_frames", "n_water"):
            print("    %-26s bare %s   closed %s"
                  % (field, agg([x[field] for x in b]), agg([x[field] for x in c])))
        print("    verdicts@90        bare %s   closed %s"
              % ([x["verdict_h90"] for x in b], [x["verdict_h90"] for x in c]))

    print()
    print("=" * 100)
    print("2. VERDICT TALLY. Never meaned. SSF=%.2f, classifier G=%.5f, stock thresholds "
          "(slide_m %.2f, slide_speed_ms %.2f, sustain_frames %d)."
          % (SSF, FM.G, FM.FailureThresholds().slide_m,
             FM.FailureThresholds().slide_speed_ms, FM.FailureThresholds().sustain_frames))
    for key in sorted(by):
        rs = by[key]
        t90 = defaultdict(int)
        tend = defaultdict(int)
        for r in rs:
            t90[r["verdict_h90"]] += 1
            tend[r["verdict_hend"]] += 1
        print("  %-38s N=%d   @row90 %s   @end(row %s) %s"
              % ("/".join(key), len(rs), dict(t90), rs[0]["row_hend"], dict(tend)))

    print()
    print("=" * 100)
    print("3. FREE-SURFACE SLOPE, m/m, by window. The closed-box artifact the channel")
    print("   measured at +0.09268 water-only is the number to compare against.")
    for key in sorted(by):
        rs = by[key]
        if "slope_pre_reflection_f60_89" not in rs[0]:
            continue
        line = ["  %-38s" % "/".join(key)]
        for w in ("pre_reflection_f60_89", "post_reflection_f120_149", "late_f220_249"):
            k = "slope_" + w
            line.append("%s %s" % (w.split("_f")[0], agg([r.get(k) for r in rs])))
        print("\n      ".join(line))

    print()
    print("=" * 100)
    print("4. WATER BUDGET, percent of water outside the CANONICAL box, final frame.")
    print("   Measured pre-clamp on the same reference box in both arms, so the numbers")
    print("   are commensurable even though the recycle arm no longer walls the x faces.")
    for key in sorted(by):
        rs = by[key]
        if "pct_n_below_floor" not in rs[0]:
            continue
        print("  %-38s below_floor %s" % ("/".join(key),
                                          agg([r["pct_n_below_floor"] for r in rs])))
        print("      %-34s out_y       %s" % ("", agg(
            [r["pct_n_out_ylo"] + r["pct_n_out_yhi"] for r in rs])))
        print("      %-34s out_x       %s" % ("", agg(
            [r["pct_n_out_xlo"] + r["pct_n_out_xhi"] for r in rs])))
        print("      %-34s floor_pen_m %s" % ("", agg(
            [r["floor_penetration_final_m"] for r in rs])))

    print()
    print("=" * 100)
    print("5. RECYCLING AND RECIRCULATION CONTAMINATION.")
    for key in sorted(by):
        rs = by[key]
        if not rs[0].get("recycled_total"):
            continue
        onsets = [r["first_tagged_near_vehicle_frame"] for r in rs]
        print("  %-38s recycled_total %s" % ("/".join(key),
                                             agg([r["recycled_total"] for r in rs])))
        print("      %-34s tagged_frac_final %s" % ("", agg(
            [r["tagged_frac_final"] for r in rs])))
        print("      %-34s first tagged particle inside the vehicle window, per rep: %s"
              % ("", onsets))
        print("      %-34s max single-tick overshoot %s"
              % ("", agg([r["max_overshoot_m"] for r in rs])))

    print()
    print("=" * 100)
    print("6. MAGNITUDES, with the window named. dmag is the surge/sway displacement")
    print("   magnitude at that row. Row 90 is the canonical horizon.")
    for key in sorted(by):
        rs = by[key]
        print("  %-38s dmag@90 %s" % ("/".join(key), agg([r["dmag_h90"] for r in rs])))
        print("      %-34s dmag@end %s" % ("", agg([r["dmag_hend"] for r in rs])))
        print("      %-34s bow_depth_peak %s" % ("", agg(
            [r["local_depth_bow_peak"] for r in rs])))
        print("      %-34s bow_peak_frame %s" % ("", agg(
            [float(r["local_depth_bow_peak_frame"]) for r in rs])))

    print()
    print("=" * 100)
    print("7. REFLECTION ARRIVAL, from the streamwise free-surface record itself.")
    print("   DETECTOR, parameters stated so it can be argued with: per streamwise bin,")
    print("   fit depth linearly in time over profile rows 40..89, which is after the")
    print("   startup transient and before the predicted first return; arrival is the")
    print("   first row at or after 90 whose residual exceeds 4 sigma of that fit's own")
    print("   residuals for 3 consecutive rows. The linear detrend is what stops the")
    print("   closed box's steady downstream pile-up from firing the detector on its own.")
    for key in sorted(by):
        rs = by[key]
        npzs = [Path(r["_dir"]) / "inflow_instrument.npz" for r in rs]
        npzs = [q for q in npzs if q.exists()]
        if not npzs:
            continue
        first_arrivals, speeds = [], []
        for q in npzs:
            z = np.load(q)
            prof = np.asarray(z["depth_profile"], dtype=float)
            centres = np.asarray(z["bin_centres"], dtype=float)
            arr = reflection_arrivals(prof)
            fin = [(centres[b], arr[b]) for b in range(len(arr))
                   if arr[b] is not None]
            if fin:
                first_arrivals.append(min(f for _, f in fin))
            if len(fin) >= 4:
                xs = np.array([c for c, _ in fin]); ts = np.array([f for _, f in fin]) / 30.0
                # upstream-propagating front: dx/dt negative. Report |speed|.
                sl = np.polyfit(ts, xs, 1)[0]
                speeds.append(abs(float(sl)))
        print("  %-38s earliest arrival row per rep: %s"
              % ("/".join(key), first_arrivals if first_arrivals else "none detected"))
        if speeds:
            print("      %-34s implied front speed |dx/dt| %s m/s (sqrt(g*d) = %.4f)"
                  % ("", agg(speeds), float(np.sqrt(9.81 * (rs[0]["realized_depth_m"] or 0.2944294)))))
        print("      %-34s predicted stream return row %.1f, cross-stream %.1f"
              % ("", rs[0].get("stream_reflection_frame", float("nan")),
                 rs[0].get("cross_reflection_frame", float("nan"))))

    print()
    print("=" * 100)
    print("8. FREE-SURFACE SLOPE AS A TIME SERIES. Fitted independently at every profile")
    print("   row, so it assumes nothing about what the series should have been doing.")
    print("   A closed basin conserves volume, so water piled downstream must come back and")
    print("   the slope must reverse sign. An open channel has no such obligation.")
    for key in sorted(by):
        rs = by[key]
        rows_sl = []
        for r in rs:
            q = Path(r["_dir"]) / "inflow_instrument.npz"
            if not q.exists():
                continue
            z = np.load(q)
            sl = slope_series(np.asarray(z["depth_profile"], dtype=float),
                              np.asarray(z["bin_centres"], dtype=float))
            rows_sl.append(sl)
        if not rows_sl:
            continue
        at = lambda i: agg([sl[i] for sl in rows_sl if i < len(sl)])
        print("  %-38s slope@row89  %s" % ("/".join(key), at(89)))
        print("      %-34s slope@row149 %s" % ("", at(149)))
        print("      %-34s slope@row249 %s" % ("", at(249)))
        print("      %-34s max slope    %s" % ("", agg([float(np.nanmax(sl)) for sl in rows_sl])))
        print("      %-34s min slope    %s" % ("", agg([float(np.nanmin(sl)) for sl in rows_sl])))
        print("      %-34s first sustained sign reversal, per rep: %s"
              % ("", [first_sign_change(sl) for sl in rows_sl]))

    if a.json:
        Path(a.json).write_text(json.dumps({"rows": rows, "ssf": SSF, "G": FM.G}, indent=2))
        print("\nwrote %s" % a.json)

    if a.npz:
        # The rollout.npz files are 170 to 650 MB each and stay on Vista under the
        # job-id-keyed path. Everything the tables above are computed from is small and
        # goes here instead, so a reader can recompute rather than trust.
        bundle = {}
        for r in rows:
            q = Path(r["_dir"]) / "inflow_instrument.npz"
            if not q.exists():
                continue
            z = np.load(q)
            for k in ("depth_profile", "bin_centres", "recycled_per_frame",
                      "tagged_near_vehicle", "tagged_total", "water_x_span",
                      "budget_n_below_floor", "budget_n_out_xlo", "budget_n_out_xhi",
                      "budget_n_out_ylo", "budget_n_out_yhi", "budget_min_z"):
                if k in z:
                    bundle["%s|%s" % (r["run"], k)] = z[k]
        np.savez_compressed(a.npz, **bundle)
        print("wrote %s (%d arrays from %d runs)"
              % (a.npz, len(bundle), len({k.split("|")[0] for k in bundle})))


if __name__ == "__main__":
    main()
