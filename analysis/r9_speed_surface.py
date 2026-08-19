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
import re
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
    """(max - min) / mean. The pre-registered statistic S.

    THE TYPE CHECK BELOW IS NOT DEFENSIVE PADDING, IT IS A MEASURED BUG.
    Passing a dict here reduces over its KEYS, silently and without error. That
    happened on 2026-08-19 in an ad-hoc analysis of this very arc: a per-seed
    spread was reported as 1.6591 for all five seeds, sd exactly 0.0000, and
    1.6591 is (3.0 - 0.0) / mean(0, 1.148, 2.121, 2.772, 3.0), the spread of the
    SWEEP AXIS itself. It was computed without touching a single force, and it
    was reported next to a correct aggregate of 1.1776 without the contradiction
    being noticed at first. The sd of exactly zero is what gave it away.

    A statistic that cannot tell the measurement from the axis it was swept over
    is the same class of defect as a test that passes on its own source text.
    """
    if isinstance(vals, dict):
        raise TypeError(
            "spread() got a dict; it would reduce over KEYS and return a number "
            "derived from the sweep axis rather than from any measurement. "
            "Pass list(d.values()).")
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


TIDY_COLS = [
    "tag", "status", "frame", "no_hull", "hull_y_m",
    "v_car_ms", "v_water_ms", "v_rel_mag_ms", "v_rel_angle_deg_from_broadside",
    "n_grid", "dx_m", "lim_m", "depth_m", "depth_cells", "band_over_depth",
    "n_water", "water_layers", "substeps", "substeps_effective",
    "bc_per_frame", "bc_per_frame_auto", "wrench_dt_s", "wrench_dt_mode",
    "frames", "discard", "settle_frames", "stream_established_frac",
    "fz_settle_N", "f_buoy_analytic_N", "fz_settle_over_analytic",
    "force_horiz_mag_N", "recycled_x", "recycled_y", "floor_clamps", "wall_s",
]


def export_tidy(rows, out_path):
    """One row per run, no per-frame series.

    `out/` is gitignored, so these records exist only on an idev node unless they
    are promoted, and an idev node is not storage. This writes the TIDY record
    and the derived quantities only: the per-frame series is ~400 rows per run,
    it is a working artifact rather than a result, and it stays on the node.

    `label` is derived from the tag prefix rather than stored, so the arm a run
    belongs to (control, arc, matrix, frame test, fidelity) is recoverable
    without consulting the script that generated it.
    """
    import csv
    with open(out_path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["label"] + TIDY_COLS
                   + ["force_mean_x_N", "force_mean_y_N", "force_mean_z_N",
                      "u_mean_x_ms", "u_mean_y_ms", "u_mean_z_ms"])
        for r in sorted(rows, key=lambda r: (r.get("tag") or "")):
            tag = r.get("tag") or ""
            line = [tag.split("_")[0]] + [r.get(c) for c in TIDY_COLS]
            fm = r.get("force_mean_N") or [None] * 3
            um = r.get("u_mean_water_ms") or [None] * 3
            w.writerow(line + list(fm) + list(um))
    return out_path


# ---------------------------------------------------------------------------
# SEEDED-SURFACE ANALYSIS. Added in the second session, after the crash.
#
# The first session established that the load at a FIXED relative speed depends
# strongly on how that speed is split between vehicle and water. It established
# that on ONE arc, at ONE magnitude, with the ensemble coming from five seeds.
# Two questions were left open and both are answered by the arms this block
# reads: does every cell of the full surface carry a distribution rather than a
# single point, and is the split-dependence itself a function of |v_rel|.
# ---------------------------------------------------------------------------

def load_tsv(path):
    """Read a tidy TSV back into run records.

    WHY THIS EXISTS AND WHY IT IS NOT REDUNDANT WITH load_dir(). load_dir reads
    SUMMARY_*.json out of `out/`, which lives on an idev node. The allocation
    ends and the JSON ends with it, so an analysis that can only read `out/` is
    an analysis nobody can re-run once the node is gone. The TSV is the artifact
    that is actually committed, so reading it back makes every number below
    reproducible from the repository alone, with no GPU and no allocation.

    Types are recovered by trial, not by a column whitelist, because a whitelist
    goes stale the moment the driver gains a column and then silently yields
    strings that compare as strings.
    """
    import csv
    out = []
    with open(path, newline="") as fh:
        for raw in csv.DictReader(fh, delimiter="\t"):
            rec = {}
            for k, v in raw.items():
                if v is None or v == "" or v == "None":
                    rec[k] = None
                elif v in ("True", "False"):
                    rec[k] = (v == "True")
                else:
                    try:
                        rec[k] = int(v)
                    except ValueError:
                        try:
                            rec[k] = float(v)
                        except ValueError:
                            rec[k] = v
            # REBUILD THE COMPOSITE FIELDS THE TSV FLATTENED.
            # export_tidy() writes force_mean_N as three scalar columns and
            # u_mean_water_ms likewise. Every report section downstream was
            # written against the JSON records and indexes the LIST forms, so a
            # loader that stops at the flat columns produces records that are
            # not interchangeable with load_dir()'s. That is not hypothetical:
            # the first version of this function did stop there, and the C2
            # section raised KeyError('force_mean_N') on the fourth print. It
            # failed loudly only because that section indexes rather than .get()s;
            # a section using .get() would have printed None as a measurement.
            for name, cols in (("force_mean_N",
                                ("force_mean_x_N", "force_mean_y_N", "force_mean_z_N")),
                               ("u_mean_water_ms",
                                ("u_mean_x_ms", "u_mean_y_ms", "u_mean_z_ms"))):
                if all(c in rec for c in cols):
                    rec[name] = [rec[c] for c in cols]
            out.append(rec)
    return out


def seed_of(label):
    """Recover (arm, seed) from a run label such as 'M1s3'.

    THE SEED IS NOT A FIRST-CLASS FIELD, AND THAT IS A DEFECT WORTH STATING
    RATHER THAN PAPERING OVER. The driver never writes the seed into the record,
    so it survives only inside the label string. Every seeded arm in this project
    happens to be named <arm>s<seed>, so the parse is exact for the runs that
    exist, but an arm named any other way returns (None, None) and would be
    dropped from an ensemble SILENTLY. That is why every ensemble printed below
    reports its own n: a silent drop then shows up as a wrong count, which is
    visible, instead of as a wrong mean, which is not.
    """
    m = re.match(r"^(.*?)s(\d+)$", str(label or ""))
    if not m:
        return None, None
    return m.group(1), int(m.group(2))


def _cells(rows):
    """Group OK rows by (v_car, v_water), rounded to the mHz the driver emits."""
    g = {}
    for r in rows:
        if r.get("status") != "OK":
            continue
        k = (round(float(r["v_car_ms"]), 4), round(float(r["v_water_ms"]), 4))
        g.setdefault(k, []).append(r)
    return g


def report_seeded_surface(rows, arm, label=""):
    """The (v_car, v_water) load surface with a DISTRIBUTION in every cell.

    Returns (cells, noise) where noise is the largest within-cell relative
    spread seen across the surface. That number is the one the headline has to
    beat: a variation across cells is only a result if it is bigger than the
    variation the same cell shows when nothing physical changed.
    """
    # PREFIX match, not equality. A cell whose record would otherwise collide
    # has to be given its own label, because the driver names its record
    # SUMMARY_<label>_g<n_grid>.json and same-label runs overwrite each other
    # silently, keeping only the last cell. The still-water edge is therefore
    # labelled M4c0..M4c4, five arm names for one surface, and equality would
    # find none of them. Prefix matching is also what lets an arm be extended
    # later without renaming the runs already on disk.
    sel = [r for r in rows
           if (seed_of(r.get("label"))[0] or "").startswith(arm)]
    cells = _cells(sel)
    if not cells:
        print("    no OK rows for arm %r" % arm)
        return {}, None
    seeds = sorted({seed_of(r.get("label"))[1] for r in sel})
    print("    arm %-6s  %d cells, seeds %s, %d OK runs %s"
          % (arm, len(cells), seeds, len(sel), label))
    print()
    print("    v_car   v_water  |v_rel|   n   mean |F_h| N     sd N    within-cell S")
    print("    " + "-" * 70)
    noise = None
    for k in sorted(cells):
        rs = cells[k]
        fh = [float(r["force_horiz_mag_N"]) for r in rs]
        m = sum(fh) / len(fh)
        sd = (sum((x - m) ** 2 for x in fh) / (len(fh) - 1)) ** 0.5 if len(fh) > 1 else 0.0
        s = spread(fh)
        # A NO-FORCING CELL MUST NOT SET THE NOISE FLOOR.
        # spread() is (max - min) / mean, so on a cell where nothing is
        # commanded and the whole point is that |F_h| goes to zero, it divides
        # by a number the experiment worked to make negligible. Measured here:
        # the (0, 0) cell returned 0.57, 1.59 and 1.70 N, all of them ~0.03
        # percent of analytic buoyancy and all of them a PASS, yet their
        # relative spread is 0.874, which is a hundred times the floor of every
        # forced cell and would have been reported as the surface's noise. That
        # is the same failure the spread() docstring already records: a
        # statistic that cannot tell a measurement from the axis it sits on.
        # The cell is still printed, it just cannot set the floor.
        forced = (abs(k[0]) > 1e-9) or (abs(k[1]) > 1e-9)
        if s is not None and forced:
            noise = s if noise is None else max(noise, s)
        vrel = (k[0] ** 2 + k[1] ** 2) ** 0.5
        print("    %6.3f  %6.3f  %7.4f  %2d  %12.1f  %8.1f    %s"
              % (k[0], k[1], vrel, len(rs), m, sd, fmt(s, 5)))
    print()
    if max(len(v) for v in cells.values()) < 2:
        # A SPREAD OF ZERO FROM ONE SAMPLE IS NOT A NOISE FLOOR OF ZERO.
        # Printing it as one would let a single-seed arm appear infinitely
        # precise and make every across-cell difference look significant.
        print("    single seed per cell: NO noise floor is measurable here.")
        print("    The 0.00000 above is the spread of one number, not evidence")
        print("    of precision. Nothing below may be graded against it.")
        return cells, None
    print("    LARGEST within-cell spread across FORCED cells: %s" % fmt(noise, 5))
    print("    (a no-forcing cell is excluded from this: see the comment in")
    print("     report_seeded_surface, its relative spread divides by ~0)")
    print("    This is the seed noise floor. Any claim about how the load varies")
    print("    ACROSS cells has to clear it to be a measurement rather than scatter.")
    return cells, noise


def report_split_vs_noise(cells, noise):
    """THE DECISIVE TEST. Split-dependence at fixed |v_rel| against seed noise.

    The headline is that the load at a fixed relative speed depends on how the
    speed is split. The obvious way for that to be an artifact is for it to be
    smaller than, or comparable to, the run-to-run scatter. This groups cells by
    |v_rel| and compares the two directly, so the comparison is forced rather
    than left to the reader.

    Cells are grouped on |v_rel| rounded to 3 decimals. The full matrix is a
    PRODUCT grid, not an arc, so exact iso-|v_rel| coincidences are rare; groups
    of one carry no split information and are skipped, and the skip is counted
    and printed rather than hidden, because a silent skip would let this print a
    confident verdict from two cells out of twenty.
    """
    by_rel = {}
    for (vc, vw), rs in cells.items():
        fh = [float(r["force_horiz_mag_N"]) for r in rs]
        by_rel.setdefault(round((vc ** 2 + vw ** 2) ** 0.5, 3), []).append(
            ((vc, vw), sum(fh) / len(fh)))
    usable = {k: v for k, v in by_rel.items() if len(v) > 1}
    print("    %d distinct |v_rel| values, %d of them carry more than one split"
          % (len(by_rel), len(usable)))
    if not usable:
        print("    NO ISO-|v_rel| GROUP ON THIS GRID. The product matrix rarely")
        print("    lands two cells on the same |v_rel|; that is what the arc arm")
        print("    is for. Reporting no verdict rather than inventing one.")
        return None
    print()
    print("    |v_rel|   n splits   min |F_h| N    max |F_h| N   across-split S   vs noise")
    print("    " + "-" * 76)
    worst = None
    for rel in sorted(usable):
        vals = [m for _, m in usable[rel]]
        s = spread(vals)
        ratio = (s / noise) if (s is not None and noise) else None
        if s is not None:
            worst = s if worst is None else max(worst, s)
        print("    %7.3f   %6d    %11.1f    %11.1f   %13s   %sx"
              % (rel, len(vals), min(vals), max(vals), fmt(s, 4), fmt(ratio, 1)))
    print()
    print("    largest across-split spread %s against seed noise %s"
          % (fmt(worst, 4), fmt(noise, 5)))
    return worst


def report_bc_guard_control(rows, suspect="M1", control="M7"):
    """Did the silently-violated bc guard change the answer?

    THE DEFECT. MovingVehicleChannelScene refuses a bc_per_frame coarser than
    its CFL-style auto rule, then AFTERWARDS snaps the value so it divides the
    substeps. The check happens before the snap, so the snap can push the
    applied value back under the rule with no error. Measured on the committed
    records at g64, substeps 11:

        pass 4  ->  4 < auto 5  ->  ValueError, the run aborts
        pass 5  ->  5 >= auto 5 ->  snap to 4  ->  APPLIED 4 < auto 5, silent

    The exact condition that aborts one run is reached quietly by another, and
    it caught the four v_car = 8.9 m/s cells of the main surface.

    THE CONTROL holds the physics fixed and moves only the suspect quantity.
    Passing 6 gives sub_per_tick 2 and applied bc 6, which satisfies the rule,
    while substeps_effective stays 12 exactly as in the suspect runs. So dt and
    the frame duration are IDENTICAL and only the BC application count differs.
    A difference here is the defect; no difference bounds it as harmless at
    these settings, which is a weaker and more honest claim than "it is fine".
    """
    a, b = _cells_mean(rows, suspect), _cells_mean(rows, control)
    common = sorted(set(a) & set(b))
    if not common:
        print("    no shared cells between %s and %s yet" % (suspect, control))
        return None
    print("    v_car v_water   suspect N (bc 4)   control N (bc 6)   rel diff")
    print("    " + "-" * 66)
    ds = []
    for k in common:
        d = (b[k] - a[k]) / a[k]
        ds.append(abs(d))
        print("    %5.1f %6.1f   %15.1f   %16.1f   %+7.3f%%"
              % (k[0], k[1], a[k], b[k], 100 * d))
    worst = max(ds)
    print("    " + "-" * 66)
    print("    worst absolute difference: %.3f%% over %d cells" % (100 * worst, len(common)))
    return worst


def report_grid_compare(rows, arm_lo, arm_hi):
    """Compare the SAME surface at two resolutions, on shape as well as level.

    The absolute force and the ORDERING of the surface are two different claims
    and they do not stand or fall together. Grid refinement is known in this
    project to move an instantaneous magnitude a long way while leaving the
    verdict alone (CLAUDE.md August 4 audit item 5, and Syamlal, Celik and
    Benyahia 2017 for why a transient quantity need not converge at all). So
    this reports the per-cell level change AND the number of inverted rank
    pairs, because a surface whose cells keep their order is still usable for
    "which conditions are worse" even when no single number is converged.

    This is NOT a GCI and must not be quoted as one: n_grid, dt and
    bc_per_frame move together between the arms, so it bounds sensitivity to a
    bundle of changes, not to resolution alone.
    """
    lo, hi = _cells_mean(rows, arm_lo), _cells_mean(rows, arm_hi)
    common = sorted(set(lo) & set(hi))
    if len(common) < 2:
        print("    fewer than 2 shared cells between %s and %s" % (arm_lo, arm_hi))
        return None
    ds = [(hi[k] - lo[k]) / lo[k] for k in common]
    n = len(common)
    pairs = n * (n - 1) // 2
    inv = sum(1 for i in range(n) for j in range(i + 1, n)
              if (lo[common[i]] - lo[common[j]]) * (hi[common[i]] - hi[common[j]]) < 0)
    print("    %d shared cells" % n)
    print("    per-cell level change: mean %+.2f%%, min %+.2f%%, max %+.2f%%, mean|.| %.2f%%"
          % (100 * sum(ds) / n, 100 * min(ds), 100 * max(ds),
             100 * sum(abs(x) for x in ds) / n))
    print("    rank inversions: %d of %d pairs (%.1f%%)"
          % (inv, pairs, 100.0 * inv / pairs))
    print("    Read as: the LEVEL is resolution-sensitive, the ORDER is much less so.")
    return {"n": n, "mean_abs_pct": 100 * sum(abs(x) for x in ds) / n,
            "inv": inv, "pairs": pairs}


def _cells_mean(rows, arm):
    d = {}
    for r in rows:
        if r.get("status") != "OK":
            continue
        if not (seed_of(r.get("label"))[0] or "").startswith(arm):
            continue
        k = (round(float(r["v_car_ms"]), 3), round(float(r["v_water_ms"]), 3))
        d.setdefault(k, []).append(float(r["force_horiz_mag_N"]))
    return {k: sum(v) / len(v) for k, v in d.items()}


def report_arc_magnitudes(rows, prefix="M3m"):
    """Is the split-dependence a property of 3.0 m/s, or general?

    Each arc holds |v_rel| fixed and sweeps the angle from pure broadside to
    pure axial, so the spread of |F_h| along one arc IS the split-dependence at
    that magnitude. Sweeping the magnitude turns a single headline number into a
    trend, and a trend is falsifiable in a way a single number is not: if S
    collapsed toward zero at low speed the effect would be a large-speed
    artifact, and if it were flat the effect would be a property of the geometry.
    """
    arms = sorted({r["label"] for r in rows
                   if str(r.get("label", "")).startswith(prefix)})
    if not arms:
        print("    no runs with label prefix %r" % prefix)
        return {}
    print("    |v_rel|   n angles   min |F_h| N    max |F_h| N    mean N   split S   peak angle")
    print("    " + "-" * 88)
    out = {}
    for a in arms:
        rs = [r for r in rows if r.get("label") == a and r.get("status") == "OK"]
        if not rs:
            continue
        fh = [float(r["force_horiz_mag_N"]) for r in rs]
        mag = max(float(r["v_rel_mag_ms"]) for r in rs)
        peak = max(rs, key=lambda r: float(r["force_horiz_mag_N"]))
        s = spread(fh)
        out[mag] = s
        print("    %7.3f   %7d    %11.1f    %11.1f  %9.1f   %7s   %7.2f deg"
              % (mag, len(rs), min(fh), max(fh), sum(fh) / len(fh), fmt(s, 4),
                 float(peak["v_rel_angle_deg_from_broadside"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(REPO, "out", "r9_moving"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--from-tsv", default=None,
                    help="read the committed tidy TSV instead of out/*.json. "
                         "out/ dies with the idev allocation; the TSV does not, "
                         "so this is what makes the surface re-derivable later.")
    ap.add_argument("--surface-arm", default="M1",
                    help="label prefix of the seeded full-matrix arm")
    ap.add_argument("--arc-prefix", default="M3m",
                    help="label prefix of the magnitude-swept arcs")
    ap.add_argument("--export", default=None,
                    help="write the tidy one-row-per-run table to this TSV path. "
                         "out/ is gitignored, so this is how records leave the node.")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    if args.from_tsv:
        rows = load_tsv(args.from_tsv)
        if not rows:
            print("no rows in %s" % args.from_tsv)
            return 1
        print("loaded %d run records from TSV %s\n" % (len(rows), args.from_tsv))
    else:
        rows = load_dir(args.dir)
        if not rows:
            print("no SUMMARY_*.json under %s" % args.dir)
            return 1
        print("loaded %d run records from %s\n" % (len(rows), args.dir))
    if args.export:
        export_tidy(rows, args.export)
        print("wrote tidy table (%d rows, no per-frame series) -> %s\n"
              % (len(rows), args.export))

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

    # ------------------------------------------------------------ S1 surface
    print()
    print("=" * 74)
    print("S1  THE SEEDED LOAD SURFACE  (arm %s: every cell a distribution)" % args.surface_arm)
    cells, noise = report_seeded_surface(rows, args.surface_arm)

    # ------------------------------------------------------------ S2 the test
    if cells:
        print()
        print("=" * 74)
        print("S2  SPLIT-DEPENDENCE AGAINST SEED NOISE  (the decisive comparison)")
        report_split_vs_noise(cells, noise)

    # ------------------------------------------------------------ S3 arcs
    print()
    print("=" * 74)
    print("S3  IS THE SPLIT-DEPENDENCE A PROPERTY OF 3.0 m/s, OR GENERAL?")
    report_arc_magnitudes(rows, args.arc_prefix)

    # ------------------------------------------------------------ S4 grid
    print()
    print("=" * 74)
    print("S4  THE SAME SURFACE AT A DIFFERENT RESOLUTION")
    print("    Not a like-for-like numerical comparison: n_grid, dt and")
    print("    bc-per-frame all move together, so the claim this can support is")
    print("    directional (does the split still matter), never absolute.")
    hi, hinoise = report_seeded_surface(rows, "M2", "[higher resolution]")
    if hi:
        print()
        report_grid_compare(rows, args.surface_arm, "M2")

    # ------------------------------------------------------------ S6 guard
    print()
    print("=" * 74)
    print("S6  THE bc GUARD WAS SILENTLY VIOLATED: DID IT MATTER?")
    report_bc_guard_control(rows)

    # ------------------------------------------------------------ S5 edge
    print()
    print("=" * 74)
    print("S5  THE STILL-WATER EDGE  (v_water = 0: pure vehicle motion)")
    report_seeded_surface(rows, "M4", "[still water]")

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
    # a dict must RAISE, not silently reduce over keys. See spread()'s docstring:
    # this exact mistake produced a plausible 1.6591 that was the spread of the
    # sweep axis, not of any force.
    try:
        spread({0.0: 10.0, 3.0: 20.0})
    except TypeError:
        pass
    else:
        raise AssertionError("spread() must refuse a dict")
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
