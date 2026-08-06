#!/usr/bin/env python3

import argparse
import csv
import os
import sys

CAL = {
    "feature": "Drain A curb inlet, concrete top slab, front edge corner to corner",
    "source_image": "c2955_0001.jpg",
    "model_units": 0.8037,
    "pick_uncertainty_pct": 0.72,
}

REF = {
    "ply_extent_full": (38.8924, 22.9618, 8.7600),
    "ply_extent_robust": (28.4714, 16.4015, 4.1864),
    "camera_height": 0.4094,
    "inlet_lid_diameter": 0.1388,
    "camera_standoff_to_inlet": 1.9217,
    "colmap_to_model": 0.30827678832280847,
}

BANDS = [
    ("camera height above road", "camera_height", 1.20, 1.90, "handheld camera"),
    ("inlet access lid diameter", "inlet_lid_diameter", 0.35, 0.80, "cast access cover"),
    ("camera standoff to inlet", "camera_standoff_to_inlet", 4.0, 10.0, "street width standoff"),
]

SCALE_COLUMNS = ("depth_m", "velocity_ms")


def scale_factor(real_m, model_units):
    if model_units <= 0:
        raise SystemExit("model distance must be positive")
    if real_m <= 0:
        raise SystemExit("real distance must be positive")
    return real_m / model_units


def fmt(x):
    return "{:.6g}".format(x)


def read_csv(path):
    with open(path, newline="") as fh:
        rdr = csv.DictReader(fh)
        return list(rdr), list(rdr.fieldnames or [])


def is_nominal_grid(rows):
    try:
        d = [float(r["depth_m"]) for r in rows]
        v = [float(r["velocity_ms"]) for r in rows]
    except (KeyError, ValueError, TypeError):
        return False
    du, vu = sorted(set(d)), sorted(set(v))
    if len(du) < 3 or len(vu) < 3:
        return False
    if len(rows) != len(du) * len(vu):
        return False
    return len(set(zip(d, v))) == len(rows)


def rescale(rows, sf, vel_exp):
    out = []
    n_d = n_v = 0
    for row in rows:
        r = dict(row)
        val = r.get("depth_m", "")
        if val not in ("", None):
            r["depth_m"] = fmt(float(val) * sf)
            n_d += 1
        val = r.get("velocity_ms", "")
        if val not in ("", None):
            r["velocity_ms"] = fmt(float(val) * (sf ** vel_exp))
            n_v += 1
        out.append(r)
    return out, n_d, n_v


def report_scale(sf, real_m, model_units):
    print("=" * 68)
    print("SCALE CALIBRATION")
    print("=" * 68)
    print("  calibration feature : {}".format(CAL["feature"]))
    print("  measured in         : {}".format(CAL["source_image"]))
    print("  real distance       : {:.4f} m".format(real_m))
    print("  model distance      : {:.4f} model units".format(model_units))
    print()
    print("  SCALE FACTOR        : {:.6f} metres per model unit".format(sf))
    print("  inverse             : {:.6f} model units per metre".format(1.0 / sf))
    print("  COLMAP -> metres    : {:.6f}".format(sf * REF["colmap_to_model"]))
    print()


def report_sanity(sf):
    print("-" * 68)
    print("SANITY CHECK: does the rescaled scene look like a real street?")
    print("-" * 68)
    ex = REF["ply_extent_full"]
    exr = REF["ply_extent_robust"]
    print("  reconstruction bounding box, all gaussians")
    print("    {:8.2f} x {:8.2f} x {:8.2f} m".format(*[e * sf for e in ex]))
    print("  reconstruction bounding box, 0.5-99.5 pct (floaters removed)")
    print("    {:8.2f} x {:8.2f} x {:8.2f} m".format(*[e * sf for e in exr]))
    print()
    worst = 0
    for label, key, lo, hi, why in BANDS:
        val = REF[key] * sf
        ok = lo <= val <= hi
        flag = "ok  " if ok else "CHECK"
        if not ok:
            worst += 1
        print("  [{}] {:<28} {:7.3f} m   expect {:.2f}-{:.2f} ({})".format(
            flag, label, val, lo, hi, why))
    print()
    err = CAL["pick_uncertainty_pct"]
    print("  pixel-pick uncertainty on the model distance: +/- {:.2f} %".format(err))
    print("    -> scale factor {:.4f} .. {:.4f} m/unit".format(
        sf * (1 - err / 100.0), sf * (1 + err / 100.0)))
    print()
    if worst == 0:
        print("  VERDICT: all independent checks land in physically real bands.")
    else:
        print("  VERDICT: {} check(s) outside band. The real distance, the model".format(worst))
        print("           distance, or the feature correspondence is wrong.")
    print()
    return worst


def report_stale(fieldnames):
    derived = [c for c in fieldnames if c not in SCALE_COLUMNS]
    if not derived:
        return
    print("-" * 68)
    print("STALE COLUMNS after rescaling")
    print("-" * 68)
    print("  Columns carried through untouched. Any of these that were derived")
    print("  from depth_m or velocity_ms are now stale:")
    for c in derived:
        print("    {}".format(c))
    print("  Recompute them from the rescaled columns before using this file.")
    print()


def main():
    p = argparse.ArgumentParser(
        description="Derive metric scale for the Drain A gsplat reconstruction "
                    "and rescale depth/velocity columns.")
    p.add_argument("--real-m", type=float, required=True,
                   help="tape-measured real-world length of the feature, metres")
    p.add_argument("--model-units", type=float, default=CAL["model_units"],
                   help="same feature measured in the reconstruction")
    p.add_argument("--csv", default=None,
                   help="CSV whose depth_m and velocity_ms columns to rescale")
    p.add_argument("--out", default=None, help="output CSV path")
    p.add_argument("--in-place", action="store_true",
                   help="overwrite --csv instead of writing --out")
    p.add_argument("--velocity-exponent", type=float, default=1.0,
                   help="1.0 for a unit conversion; 0.5 for Froude scaling")
    p.add_argument("--force", action="store_true",
                   help="rescale even if the CSV looks like a nominal input grid")
    p.add_argument("--dry-run", action="store_true",
                   help="report only, write nothing")
    a = p.parse_args()

    sf = scale_factor(a.real_m, a.model_units)
    report_scale(sf, a.real_m, a.model_units)
    bad = report_sanity(sf)

    if a.csv is None:
        print("No --csv given, scale factor only.")
        return 0 if bad == 0 else 2

    if not os.path.exists(a.csv):
        raise SystemExit("no such CSV: {}".format(a.csv))

    rows, fieldnames = read_csv(a.csv)
    have = [c for c in SCALE_COLUMNS if c in fieldnames]
    if not have:
        raise SystemExit("{} has neither depth_m nor velocity_ms".format(a.csv))

    print("-" * 68)
    print("TARGET: {}  ({} rows, columns to scale: {})".format(
        a.csv, len(rows), ", ".join(have)))
    print("-" * 68)

    if is_nominal_grid(rows) and not a.force:
        print("  REFUSING TO WRITE.")
        print("  depth_m x velocity_ms is a complete cartesian product, which")
        print("  means this file is a nominal parameter grid that was already")
        print("  authored in SI units. It carries no reconstruction geometry,")
        print("  so there is nothing here for a model-unit scale factor to fix.")
        print("  Rescaling it would silently corrupt the sweep inputs.")
        print("  Point --csv at the measured L2 output, or pass --force.")
        print()
        return 3

    scaled, n_d, n_v = rescale(rows, sf, a.velocity_exponent)
    print("  depth_m rescaled   : {} values x {:.6f}".format(n_d, sf))
    print("  velocity_ms rescaled: {} values x {:.6f}".format(
        n_v, sf ** a.velocity_exponent))
    print()
    report_stale(fieldnames)

    dest = a.csv if a.in_place else a.out
    if a.dry_run or dest is None:
        if dest is None and not a.dry_run:
            print("  no --out and no --in-place, nothing written.")
        else:
            print("  dry run, nothing written.")
        for r in scaled[:5]:
            print("    {}".format({k: r[k] for k in have}))
        return 0

    with open(dest, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(scaled)
    print("  wrote {}".format(dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
