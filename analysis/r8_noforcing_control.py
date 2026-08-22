#!/usr/bin/env python3
"""Grade the R8-d3 no-forcing control against its forced counterpart.

Executes the pass/fail rule pre-registered in docs/R8_FORCE_ROUTE_2026-08-18.md
section 5, which was committed (205f376) BEFORE any zero-velocity run was
submitted. This script does not restate that rule from memory: the thresholds
are the module constants below and they must match section 5.

WHAT THIS GRADES, AND WHAT IT REFUSES TO GRADE
----------------------------------------------
The observable is the hull's SURGE DISPLACEMENT, final_disp_m[SURGE_AXIS].

It is NOT peak_surge_force_n, peak_vertical_force_n or peak_surge_accel_g.
Those are M*dv_cm/dt, and on the free-rigid material-8 path v_cm is OVERWRITTEN,
not integrated (pinned engine kernels/mpm_utils.py:1434,
`v_cm_new = rigid_linear_mom[b] / M`, an assignment with no force term). No force
accumulator exists for the body. Register D6f condemns peak_surge_accel_g by name.
Grading this control with any of them would reintroduce the route R5 retracted, so
BARRED_FIELDS below makes that an error rather than a judgement call.

ENGINE: warpmpm throughout. No Genesis run is involved anywhere in this control.

NO THIRD-PARTY DEPENDENCIES. Standard library only, so it runs on the Mac with the
system python3 and needs no uv/numpy provisioning. Verified by running it.

USAGE
-----
    python3 analysis/r8_noforcing_control.py --selftest
    python3 analysis/r8_noforcing_control.py --forced FORCED.txt --control CONTROL.txt

Both inputs are files containing the driver's own `SUMMARY {json}` lines (the
format sim_standing.py emits, one per run). Lines that are not SUMMARY lines are
ignored, so raw job .out files can be passed directly.
"""

import argparse
import json
import statistics
import sys

# --- pre-registered constants, docs/R8_FORCE_ROUTE_2026-08-18.md section 5 -------
SURGE_AXIS = 0

R_CLEAN = 0.10          # level contamination below this is CLEAN
C_CLEAN = 0.10          # trend contamination below this is CLEAN
C_CONTAMINATED = 0.35   # at or above this the resolution effect is CONTAMINATED
C_MASQUERADE = 0.20     # same-sign trend at or above this forces MARGINAL at minimum

# Forced repeat spreads, metres, measured live 2026-08-18 from the R6 repeats on
# Vista ($WORK/r6_rep_g{48,64,96,128}_*/, 5 draws each). Per W3 these are GPU
# floating-point non-determinism in atomic P2G accumulation, not physical
# uncertainty: seed=0 is hard-coded and no --seed flag exists. Used only for the
# indistinguishable-from-nothing test.
FORCED_SPREAD_M = {48: 0.000658, 64: 0.001392, 96: 0.001079, 128: 0.002877,
                   160: 0.003102, 192: 0.001760}

BARRED_FIELDS = (
    "peak_surge_force_n",
    "peak_vertical_force_n",
    "peak_surge_accel_g",
)


def parse_summaries(path):
    """Pull every `SUMMARY {json}` line out of a driver .out file."""
    runs = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("SUMMARY "):
                continue
            runs.append(json.loads(line[len("SUMMARY "):]))
    return runs


def group_by_grid(runs, expect_velocity=None):
    """Group runs by n_grid, asserting the velocity is what the caller expects."""
    out = {}
    for r in runs:
        for bad in BARRED_FIELDS:
            if bad in r:
                raise SystemExit(
                    "REFUSING TO GRADE: run %r carries %r. That is M*dv/dt, the "
                    "quantity R5 retracted and register D6f condemns. The observable "
                    "for this control is final_disp_m[%d]." % (r.get("label"), bad, SURGE_AXIS)
                )
        v = float(r["velocity_ms"])
        if expect_velocity is not None and abs(v - expect_velocity) > 1e-12:
            raise SystemExit(
                "VELOCITY MISMATCH: run %r has velocity_ms=%r, expected %r. Refusing "
                "to mix forced and control runs." % (r.get("label"), v, expect_velocity)
            )
        out.setdefault(int(r["n_grid"]), []).append(r)
    return out


def surge_stats(runs):
    vals = [float(r["final_disp_m"][SURGE_AXIS]) for r in runs]
    return {
        "n": len(vals),
        "mean": statistics.fmean(vals),
        "spread": (max(vals) - min(vals)) if len(vals) > 1 else 0.0,
        "vals": vals,
        "substeps": sorted({int(r["substeps"]) for r in runs}),
    }


def grade(forced_by_grid, control_by_grid):
    grids = sorted(set(forced_by_grid) & set(control_by_grid))
    missing = sorted(set(forced_by_grid) ^ set(control_by_grid))

    rows = []
    for g in grids:
        f = surge_stats(forced_by_grid[g])
        c = surge_stats(control_by_grid[g])
        r = abs(c["mean"]) / abs(f["mean"]) if f["mean"] else float("inf")
        floor = FORCED_SPREAD_M.get(g)
        rows.append({
            "grid": g, "forced": f, "control": c, "R": r,
            "indistinguishable": floor is not None and abs(c["mean"]) < floor,
            "substeps_match": f["substeps"] == c["substeps"],
        })

    pairs = []
    for a, b in zip(grids, grids[1:]):
        d1 = forced_stats_mean(forced_by_grid, b) - forced_stats_mean(forced_by_grid, a)
        d0 = forced_stats_mean(control_by_grid, b) - forced_stats_mean(control_by_grid, a)
        c_val = abs(d0) / abs(d1) if d1 else float("inf")
        pairs.append({
            "pair": (a, b), "dD1": d1, "dD0": d0, "C": c_val,
            "same_sign": (d0 > 0) == (d1 > 0) and d0 != 0 and d1 != 0,
        })

    # --- verdict, exactly the section 5 rule ---------------------------------
    notes = []
    if len(grids) < 3:
        notes.append(
            "FEWER THAN THREE RUNGS RETURNED (%d). Per section 5 the trend tests C are "
            "NOT computed and the level test R is reported alone. Missing: %s"
            % (len(grids), missing or "none")
        )
        verdict = "INCOMPLETE"
        pairs = []
    else:
        worst_c = max((p["C"] for p in pairs), default=0.0)
        worst_r = max((row["R"] for row in rows), default=0.0)
        all_same_sign = bool(pairs) and all(p["same_sign"] for p in pairs)

        if worst_c >= C_CONTAMINATED:
            verdict = "CONTAMINATED"
        elif worst_c >= C_CLEAN or worst_r >= R_CLEAN:
            verdict = "MARGINAL"
        else:
            verdict = "CLEAN"

        if all_same_sign and worst_c >= C_MASQUERADE and verdict == "CLEAN":
            verdict = "MARGINAL"
            notes.append(
                "MASQUERADE TRIGGER fired: the no-forcing trend has the SAME SIGN as the "
                "forced trend at every successive pair and worst C = %.4f >= %.2f."
                % (worst_c, C_MASQUERADE)
            )
        elif all_same_sign:
            notes.append(
                "The no-forcing trend has the same sign as the forced trend at every "
                "successive pair (worst C = %.4f, below the %.2f masquerade threshold)."
                % (worst_c, C_MASQUERADE)
            )
    return rows, pairs, verdict, notes, missing


def forced_stats_mean(by_grid, g):
    return surge_stats(by_grid[g])["mean"]


def report(rows, pairs, verdict, notes, missing):
    print("=" * 78)
    print("R8-d3 NO-FORCING CONTROL, graded against the pre-registration in")
    print("docs/R8_FORCE_ROUTE_2026-08-18.md section 5 (committed 205f376, before data).")
    print("Observable: final_disp_m[%d], surge displacement. Engine: warpmpm." % SURGE_AXIS)
    print("=" * 78)
    print()
    print("LEVEL TEST   R(g) = |D0| / |D1|,  CLEAN if R < %.2f at every rung" % R_CLEAN)
    print()
    hdr = "%6s %4s %14s %14s %9s %11s %s" % (
        "grid", "n", "D1 forced (m)", "D0 control(m)", "R", "substeps", "note")
    print(hdr)
    print("-" * len(hdr))
    for row in rows:
        note = []
        if row["indistinguishable"]:
            note.append("< forced repeat spread, indistinguishable from round-off")
        if not row["substeps_match"]:
            note.append("SUBSTEP MISMATCH %s vs %s" % (row["forced"]["substeps"], row["control"]["substeps"]))
        print("%6d %4d %14.6f %14.6f %9.4f %11s %s" % (
            row["grid"], row["control"]["n"], row["forced"]["mean"], row["control"]["mean"],
            row["R"], ",".join(str(s) for s in row["control"]["substeps"]),
            "; ".join(note)))
    print()

    if pairs:
        print("TREND TEST   C = |dD0| / |dD1|,  the fraction of the resolution effect")
        print("             reproduced with the flow switched OFF.")
        print("             CLEAN C < %.2f, MARGINAL %.2f to %.2f, CONTAMINATED >= %.2f"
              % (C_CLEAN, C_CLEAN, C_CONTAMINATED, C_CONTAMINATED))
        print()
        hdr2 = "%12s %14s %14s %9s %s" % ("pair", "dD1 forced", "dD0 control", "C", "same sign")
        print(hdr2)
        print("-" * len(hdr2))
        for p in pairs:
            print("%12s %14.6f %14.6f %9.4f %s" % (
                "g%d->g%d" % p["pair"], p["dD1"], p["dD0"], p["C"],
                "yes" if p["same_sign"] else "no"))
        print()

    for n in notes:
        print("NOTE: %s" % n)
    if missing:
        print("NOTE: grids present in only one of the two sets: %s" % missing)
    print()
    print("VERDICT: %s" % verdict)
    return verdict


# --------------------------------------------------------------------------
# Self-test. Runs with no data files and no network, and checks the metric
# behaves correctly on cases whose answer is known by construction.
# --------------------------------------------------------------------------
FORCED_ANCHORS = {   # measured live 2026-08-18, $WORK/r6_rep_g*_*.out, 5 draws each
    48:  [0.180809, 0.181400, 0.181193, 0.181058, 0.181467],
    64:  [0.132721, 0.131341, 0.132231, 0.132733, 0.131416],
    96:  [0.085329, 0.085722, 0.085480, 0.085420, 0.084643],
    128: [0.067610, 0.068758, 0.065881, 0.066350, 0.067707],
}
FORCED_SUBSTEPS = {48: 8, 64: 11, 96: 16, 128: 21, 160: 26, 192: 32}


def _synth(vals_by_grid, velocity):
    out = {}
    for g, vals in vals_by_grid.items():
        out[g] = [{"label": "synth_g%d_%d" % (g, i), "n_grid": g,
                   "velocity_ms": velocity, "substeps": FORCED_SUBSTEPS[g],
                   "final_disp_m": [v, 0.0, 0.0]} for i, v in enumerate(vals)]
    return out


def selftest():
    ok = True

    # 1. The embedded forced anchors must reproduce the means and spreads quoted
    #    in section 3a of the pre-registration.
    expect = {48: (0.1811854, 0.000658), 64: (0.1320884, 0.001392),
              96: (0.0853188, 0.001079), 128: (0.0672612, 0.002877)}
    for g, (mean, spread) in expect.items():
        s = surge_stats(_synth(FORCED_ANCHORS, 1.5)[g])
        if abs(s["mean"] - mean) > 5e-7 or abs(s["spread"] - spread) > 5e-7:
            print("SELFTEST FAIL: g%d mean/spread %.7f/%.6f != doc %.7f/%.6f"
                  % (g, s["mean"], s["spread"], mean, spread))
            ok = False
    print("selftest 1 forced anchors reproduce section 3a: %s" % ("PASS" if ok else "FAIL"))

    forced = _synth(FORCED_ANCHORS, 1.5)

    # 2. NULL, total contamination: control identical to forced. Every difference
    #    is reproduced with no flow, so C must be exactly 1 and the verdict
    #    CONTAMINATED. If the metric cannot detect this it detects nothing.
    ctrl = _synth(FORCED_ANCHORS, 0.0)
    _, pairs, verdict, _, _ = grade(forced, ctrl)
    c_ok = all(abs(p["C"] - 1.0) < 1e-9 for p in pairs) and verdict == "CONTAMINATED"
    print("selftest 2 identical-to-forced gives C=1 and CONTAMINATED: %s"
          % ("PASS" if c_ok else "FAIL C=%s verdict=%s" % ([p["C"] for p in pairs], verdict)))
    ok = ok and c_ok

    # 3. NULL, zero contamination: a control that is flat and tiny at every grid.
    #    No trend at all, so C = 0 and the verdict is CLEAN.
    flat = {g: [1e-6] * 5 for g in FORCED_ANCHORS}
    _, pairs, verdict, _, _ = grade(forced, _synth(flat, 0.0))
    z_ok = all(p["C"] < 1e-9 for p in pairs) and verdict == "CLEAN"
    print("selftest 3 flat tiny control gives C=0 and CLEAN: %s"
          % ("PASS" if z_ok else "FAIL C=%s verdict=%s" % ([p["C"] for p in pairs], verdict)))
    ok = ok and z_ok

    # 4. The masquerade trigger must fire: a control that is 25 percent of the
    #    forced trend, same sign, passes the level test at some rungs but must
    #    still be downgraded to MARGINAL rather than reported CLEAN.
    masq = {g: [v * 0.25 for v in vals] for g, vals in FORCED_ANCHORS.items()}
    _, pairs, verdict, notes, _ = grade(forced, _synth(masq, 0.0))
    m_ok = verdict in ("MARGINAL", "CONTAMINATED")
    print("selftest 4 same-sign 25pc control is not reported CLEAN: %s (verdict %s)"
          % ("PASS" if m_ok else "FAIL", verdict))
    ok = ok and m_ok

    # 5. Barred-accessor guard: a run carrying the retracted force field must be
    #    rejected outright, not silently graded.
    bad = [{"label": "x", "n_grid": 64, "velocity_ms": 0.0, "substeps": 11,
            "final_disp_m": [0.0, 0.0, 0.0], "peak_surge_force_n": 31240.5}]
    try:
        group_by_grid(bad)
        print("selftest 5 barred accessor rejected: FAIL (it was accepted)")
        ok = False
    except SystemExit:
        print("selftest 5 barred accessor rejected: PASS")

    # 6. Fewer than three rungs must refuse to compute C rather than guess.
    two = {g: FORCED_ANCHORS[g] for g in (48, 64)}
    _, pairs, verdict, notes, _ = grade(_synth(two, 1.5), _synth({g: [1e-6] * 5 for g in two}, 0.0))
    t_ok = verdict == "INCOMPLETE" and not pairs
    print("selftest 6 two rungs gives INCOMPLETE and no C: %s" % ("PASS" if t_ok else "FAIL"))
    ok = ok and t_ok

    print()
    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forced", nargs="*", default=[],
                    help="driver .out file(s) containing the FORCED SUMMARY lines")
    ap.add_argument("--control", nargs="*", default=[],
                    help="driver .out file(s) containing the velocity-0 SUMMARY lines")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.forced or not a.control:
        ap.error("need --forced and --control, or --selftest")

    forced, control = [], []
    for p in a.forced:
        forced += parse_summaries(p)
    for p in a.control:
        control += parse_summaries(p)
    if not forced or not control:
        raise SystemExit("no SUMMARY lines parsed (forced=%d control=%d)"
                         % (len(forced), len(control)))

    fg = group_by_grid(forced, expect_velocity=None)
    cg = group_by_grid(control, expect_velocity=0.0)
    verdict = report(*grade(fg, cg))
    return 0 if verdict in ("CLEAN", "MARGINAL", "INCOMPLETE") else 1


if __name__ == "__main__":
    sys.exit(main())
