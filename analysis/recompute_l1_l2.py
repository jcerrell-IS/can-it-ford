import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L2_CSV = os.path.join(ROOT, "data", "phase_space_results.csv")
GRID_CSV = os.path.join(ROOT, "data", "scenario_sweep.csv")

DEPTH_CAP = 0.30
VEL_CAP = 3.0
DV_CAP = 0.30

SOURCE = ("AR&R small-passenger rule applied per Shand, Cox, Blacka and Smith 2011, "
          "AR&R Project 10 Stage 2, Report P10/S2/020, Table 3: depth <= 0.30 m AND "
          "velocity <= 3.0 m/s AND depth*velocity <= 0.30 m2/s")


def key(d, v):
    return (round(float(d), 6), round(float(v), 6))


def main():
    l2_rows = list(csv.DictReader(open(L2_CSV)))
    print(f"L2 source: {L2_CSV}")
    print(f"  raw rows: {len(l2_rows)}")

    dedup = {}
    for r in l2_rows:
        dedup[key(r["depth_m"], r["velocity_ms"])] = r
    surviving = list(dedup.items())
    n = len(surviving)
    print(f"  after dedup on (depth_m, velocity_ms), keep last: {n}")
    if n != 23:
        print(f"  ASSERTION FAILED: expected 23 surviving conditions, got {n}")
    else:
        print("  assertion OK: 23 deduplicated conditions")

    grid = {}
    for r in csv.DictReader(open(GRID_CSV)):
        grid[key(r["depth_m"], r["velocity_ms"])] = r
    print(f"\nL1 source: {GRID_CSV}")
    print(f"  grid rows: {len(grid)}")

    matched, unmatched = [], []
    for k, r in surviving:
        if k in grid:
            matched.append((k, r, grid[k]["L1_verdict_small_passenger"].strip().upper(), "COLUMN-READ"))
        else:
            d, v = k
            ford = (d <= DEPTH_CAP) and (v <= VEL_CAP) and (d * v <= DV_CAP)
            unmatched.append((k, r, "FORD" if ford else "NO-FORD", "RULE-APPLIED"))

    print(f"\n  matched by join, verdict COLUMN-READ : {len(matched)}")
    print(f"  unmatched, verdict RULE-APPLIED      : {len(unmatched)}")
    if unmatched:
        print(f"  {SOURCE}")
        for (d, v), _, verdict, _ in unmatched:
            print(f"    unmatched condition d={d:.2f} v={v:.2f} -> {verdict}")

    combined = matched + unmatched

    ford_agree = noford_agree = diverge = reverse = 0
    for k, r, l1, prov in combined:
        l2 = r["verdict"].strip().upper()
        if l2 == "FORD" and l1 == "FORD":
            ford_agree += 1
        elif l2 == "NO-FORD" and l1 == "NO-FORD":
            noford_agree += 1
        elif l2 == "NO-FORD" and l1 == "FORD":
            diverge += 1
        elif l2 == "FORD" and l1 == "NO-FORD":
            reverse += 1

    total = len(combined)
    agree = ford_agree + noford_agree
    pct = 100.0 * agree / total if total else 0.0

    print("\n=== CROSS-TABULATION, corrected L1 against L2 ===")
    print(f"  FORD_AGREE      (L2 FORD,    L1 FORD)    : {ford_agree}")
    print(f"  NOFORD_AGREE    (L2 NO-FORD, L1 NO-FORD) : {noford_agree}")
    print(f"  DIVERGE         (L2 NO-FORD, L1 FORD)    : {diverge}")
    print(f"  REVERSE_DIVERGE (L2 FORD,    L1 NO-FORD) : {reverse}")
    print(f"  total conditions                         : {total}")
    print(f"  agreement                                : {agree}/{total} = {pct:.1f} percent")

    print("\n=== OLD versus NEW ===")
    print(f"  {'quantity':<28} {'OLD (section 4.1)':>20} {'NEW (this run)':>20}")
    print(f"  {'conditions':<28} {'23':>20} {total:>20}")
    print(f"  {'divergences':<28} {'14':>20} {diverge:>20}")
    print(f"  {'agreement percent':<28} {'39.1':>20} {pct:>20.1f}")

    if diverge < 14:
        direction = "DIVERGENCE DECREASED and AGREEMENT INCREASED, matching the prediction"
    elif diverge > 14:
        direction = "DIVERGENCE INCREASED, CONTRADICTING the prediction"
    else:
        direction = "DIVERGENCE UNCHANGED at 14"
    print(f"\n  direction: {direction}")


main()
