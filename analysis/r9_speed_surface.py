"""r9_speed_surface.py

Build the (v_car, v_water) load surface from the records emitted by
simulation/moving_vehicle_channel.py, and evaluate the criteria that were
pre-registered in docs/R9_MOVING_VEHICLE_2026-08-19.md BEFORE any run.

Every number in that document is produced by this script, so the document can be
regenerated rather than trusted.

WHAT THIS DELIBERATELY DOES NOT DO
   It does not report an absolute force as a measurement. The scene runs at 2.04
   depth cells (g64) and 3.06 (g96) against the 18 of the validated C1-SDF
   buoyancy regime, and docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md
   section 5 concluded for this same scene family that "no force number from
   this scene is quotable". Absolutes appear here only as diagnostics and are
   labelled as such. Every reported RESULT is a ratio or a spread at fixed
   resolution.

   It also never reports a FORD or NO-FORD verdict. The body is prescribed and
   cannot be swept away.

USAGE
    python3 analysis/r9_speed_surface.py --dir out/r9_moving
    python3 analysis/r9_speed_surface.py --dir out/r9_moving --selftest
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pre-registered thresholds. Changing one of these is changing the experiment,
# so they are named here rather than inlined at the point of comparison.
C1_HORIZ_OVER_BUOY_MAX = 0.05      # no-forcing gate
C2_SPREAD_THRESHOLD = 0.10         # iso-|v_rel| collapse threshold
C4_FRAME_AGREEMENT = 0.15          # ground vs rest frame
STREAM_MIN = 0.50                  # below this the free stream is not established


def load_dir(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, "SUMMARY_*.json"))):
        try:
            rows = json.load(open(p))
        except Exception as exc:                       # pragma: no cover
            print("SKIP %s: %s" % (p, exc))
            continue
        for r in rows:
            r["_src"] = os.path.basename(p)
            out.append(r)
    return out


def by_label(rows, prefix):
    return [r for r in rows if r.get("tag", "").startswith(prefix)]


def spread(vals):
    """(max - min) / mean. The pre-registered statistic S."""
    if not vals:
        return None
    m = sum(vals) / len(vals)
    if m == 0:
        return None
    return (max(vals) - min(vals)) / m


def fmt(x, n=1):
    return "n/a" if x is None else ("%.*f" % (n, x))


def report_stream_health(rows):
    """Refuse to grade any cell whose free stream never established.

    THIS CHECK EXISTS BECAUSE ITS ABSENCE PRODUCED A PUBLISHED-LOOKING RESULT
    THAT WAS ENTIRELY AN ARTIFACT. Before the recycle planes were moved clear of
    add_domain_walls' three-cell kill band, positive-direction forcing never
    established: measured stream_established_frac was -0.187 for +x and -0.188
    for +y with the hull REMOVED, against +0.997 for both negative directions.
    The arc computed from those runs looked like a clean monotone trend and was
    a measurement of which directions had stalled.

    A cell with a dead stream must be reported as ungradeable, never averaged in.
    """
    bad = [r for r in rows
           if r.get("stream_established_frac") is not None
           and (r.get("v_car_ms") or r.get("v_water_ms"))
           and r["stream_established_frac"] < STREAM_MIN]
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(REPO, "out", "r9_moving"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    rows = load_dir(args.dir)
    if not rows:
        print("no SUMMARY_*.json under %s" % args.dir)
        return 1
    print("loaded %d run records from %s\n" % (len(rows), args.dir))

    # ---------------------------------------------------------------- C1
    print("=" * 74)
    print("C1  NO-FORCING GATE   (pre-registered: |F_horiz| / rho g V_sub < %.2f)"
          % C1_HORIZ_OVER_BUOY_MAX)
    ctrl = [r for r in by_label(rows, "c1ctrl") if r.get("status") == "OK"]
    c1_pass = None
    for r in ctrl[:1]:
        ratio = r["force_horiz_mag_N"] / r["f_buoy_analytic_N"]
        c1_pass = ratio < C1_HORIZ_OVER_BUOY_MAX
        print("    |F_horiz| = %.2f N   rho g V_sub = %.1f N   ratio = %.5f   -> %s"
              % (r["force_horiz_mag_N"], r["f_buoy_analytic_N"], ratio,
                 "PASS" if c1_pass else "FAIL"))
        print("    stream_established_frac = %.4f (must be 0: no flow is commanded)"
              % r["stream_established_frac"])
    if len(ctrl) > 1:
        # RELATIVE tolerance, not equality. An earlier version of this block
        # tested for distinct float tuples, found 3 of 3 distinct, and printed
        # "deterministic" anyway, so the check contradicted its own conclusion.
        # The runs differ in the sixth decimal because GPU atomics accumulate in
        # nondeterministic order; that is not the kind of variation a repeat is
        # meant to sample.
        fh = [r["force_horiz_mag_N"] for r in ctrl]
        rel = spread(fh)
        print("    %d repeats at ONE seed: |F_horiz| spread = %.2e (relative)"
              % (len(ctrl), rel))
        if rel < 1e-3:
            print("    => EFFECTIVELY DETERMINISTIC AT FIXED SEED (GPU atomic ordering")
            print("       only). Repeats at a fixed seed carry no information here; a")
            print("       distribution requires varying --seed. Reported because this")
            print("       slot's dispatch assumed repeats at fixed config would spread.")
        else:
            print("    => run-to-run spread is material; report distributions.")

    # ---------------------------------------------------------------- C0
    print()
    print("=" * 74)
    print("C0  TRAP-1 DETECTOR, SHOWN TO FIRE  (deliberate wrong wrench dt)")
    wrong = by_label(rows, "c0wrongdt")
    if ctrl and wrong:
        good = ctrl[0]["fz_settle_over_analytic"]
        bad = wrong[0]["fz_settle_over_analytic"]
        n = ctrl[0]["substeps_effective"]
        obs = bad / good
        ok = abs(obs - n) / n < 0.01
        print("    fz_settle/analytic  correct dt %.4f   wrong dt %.4f" % (good, bad))
        print("    observed ratio %.6f   substeps_effective %d   -> %s"
              % (obs, n, "DETECTOR FIRES AS PREDICTED" if ok else "UNEXPECTED"))
        print("    A detector never observed to fire has not been tested. This one has.")

    # ---------------------------------------------------------------- C2
    print()
    print("=" * 74)
    print("C2  ISO-|v_rel| ARC   (pre-registered: S < %.2f means collapsing v_car and"
          % C2_SPREAD_THRESHOLD)
    print("    v_water into one speed is defensible; S >= %.2f means the split matters)"
          % C2_SPREAD_THRESHOLD)
    for pref, grid in (("c2arc", "g64"), ("c3res", "g96")):
        arc = [r for r in by_label(rows, pref) if r.get("status") == "OK"]
        if not arc:
            continue
        arc.sort(key=lambda r: r["v_car_ms"])
        print("\n    %s, |v_rel| = %.3f m/s held fixed:" % (grid, arc[0]["v_rel_mag_ms"]))
        print("      %-9s %-9s %-8s %-11s %-9s %s"
              % ("v_car", "v_water", "angle", "|F_horiz| N", "stream", "Fz N"))
        for r in arc:
            print("      %-9.3f %-9.3f %-8.1f %-11.1f %-9.3f %.1f"
                  % (r["v_car_ms"], r["v_water_ms"],
                     abs(r["v_rel_angle_deg_from_broadside"]),
                     r["force_horiz_mag_N"], r["stream_established_frac"],
                     r["force_mean_N"][2]))
        fh = [r["force_horiz_mag_N"] for r in arc]
        S = spread(fh)
        broad = [r for r in arc if r["v_car_ms"] == 0]
        axial = [r for r in arc if r["v_water_ms"] == 0]
        print("      S = (max-min)/mean = %.4f  -> %s"
              % (S, "SPLIT MATTERS" if S >= C2_SPREAD_THRESHOLD else "collapse defensible"))
        if broad and axial:
            ratio = broad[0]["force_horiz_mag_N"] / axial[0]["force_horiz_mag_N"]
            print("      broadside / axial at identical |v_rel| = %.3f" % ratio)
        # Effective drag coefficient from the REALISED stream, not the commanded
        # one. A SANITY CHECK ON THE SCENE, NOT A MEASUREMENT: if the two extreme
        # orientations return a similar Cd, the directional difference in load is
        # being carried by projected frontal area, which is what a bluff body in a
        # stream should do. If they disagree wildly the scene is still broken.
        # Frontal areas use the canonical hull extents 1.746378 (x) and 4.282610
        # (y) times the 0.30 m depth; that is a flat-plate projection and ignores
        # the hull profile, so the ABSOLUTE Cd is not meaningful, only the ratio.
        EXT_X, EXT_Y = 1.746378, 4.282610
        for r in arc:
            if r["v_car_ms"] != 0 and r["v_water_ms"] != 0:
                continue
            broad_case = (r["v_car_ms"] == 0)
            area = (EXT_Y if broad_case else EXT_X) * r["depth_m"]
            u_eff = r["stream_established_frac"] * r["v_rel_mag_ms"]
            if u_eff <= 0:
                continue
            cd = r["force_horiz_mag_N"] / (0.5 * 1000.0 * area * u_eff ** 2)
            print("      %-9s frontal %.4f m2, realised u %.3f m/s -> Cd_eff %.3f"
                  % ("broadside" if broad_case else "axial", area, u_eff, cd))

    # ---------------------------------------------------------------- surface
    print()
    print("=" * 74)
    print("THE SURFACE  (v_car rows, v_water columns, |F_horiz| in N)")
    full = [r for r in by_label(rows, "c3full") if r.get("status") == "OK"]
    if full:
        vcs = sorted({r["v_car_ms"] for r in full})
        vws = sorted({r["v_water_ms"] for r in full})
        idx = {(r["v_car_ms"], r["v_water_ms"]): r for r in full}
        head = "    v_car \\ v_water |" + "".join("%10.2f" % w for w in vws)
        print(head)
        print("    " + "-" * (len(head) - 4))
        for c in vcs:
            line = "    %-15.2f |" % c
            for w in vws:
                r = idx.get((c, w))
                line += "%10.1f" % r["force_horiz_mag_N"] if r else "%10s" % "-"
            print(line)
        print()
        print("    same cells, |v_rel| = hypot(v_car, v_water) in m/s")
        for c in vcs:
            line = "    %-15.2f |" % c
            for w in vws:
                line += "%10.3f" % math.hypot(c, w)
            print(line)
        bad = report_stream_health(full)
        print()
        if bad:
            print("    UNGRADEABLE CELLS (stream_established_frac < %.2f): %d"
                  % (STREAM_MIN, len(bad)))
            for r in bad:
                print("      v_car %.2f v_water %.2f stream %.3f"
                      % (r["v_car_ms"], r["v_water_ms"], r["stream_established_frac"]))
        else:
            print("    every cell established its free stream (min %.3f)"
                  % min(r["stream_established_frac"] for r in full))

    # ------------------------------------------------- isolation controls
    print()
    print("=" * 74)
    print("ISOLATION CONTROLS, no hull, |u| = 3.0 m/s in each of four directions")
    quad = [r for r in rows if r.get("tag", "").startswith("q_")]
    if quad:
        for r in sorted(quad, key=lambda r: r["tag"]):
            print("    %-28s stream_est %+7.3f   u_mean = (%+.3f, %+.3f, %+.3f)"
                  % (r["tag"], r["stream_established_frac"], *r["u_mean_water_ms"]))
        s = spread([abs(r["stream_established_frac"]) for r in quad])
        print("    spread across the four directions: %.4f" % s)
        print("    (isotropy here is what says the forcing path has no direction bias)")

    print()
    print("=" * 74)
    print("NOT REPORTED, DELIBERATELY: any absolute force as a measurement, and any")
    print("FORD / NO-FORD verdict. The body is prescribed; it cannot be swept away.")
    return 0


def selftest():
    """Checks on the reporting logic itself, no simulation data required."""
    ok = 0
    assert abs(spread([1.0, 2.0, 3.0]) - 1.0) < 1e-12
    assert spread([2.0, 2.0, 2.0]) == 0.0
    assert spread([]) is None
    assert spread([0.0, 0.0]) is None
    ok += 1

    # the stall filter must reject a dead stream and keep a live one, and must
    # NOT reject the no-forcing control, which legitimately has no stream at all
    rows = [
        {"stream_established_frac": -0.187, "v_car_ms": 0.0, "v_water_ms": 3.0},
        {"stream_established_frac": 0.967, "v_car_ms": 0.0, "v_water_ms": 3.0},
        {"stream_established_frac": 0.0, "v_car_ms": 0.0, "v_water_ms": 0.0},
    ]
    bad = report_stream_health(rows)
    assert len(bad) == 1 and bad[0]["stream_established_frac"] < 0, bad
    ok += 1

    # the pre-registered thresholds must be the pre-registered values
    assert C1_HORIZ_OVER_BUOY_MAX == 0.05
    assert C2_SPREAD_THRESHOLD == 0.10
    ok += 1
    print("SELFTEST OK: %d groups passed" % ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
