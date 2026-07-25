import argparse
import csv
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
from vehicle_params import AR_R_CLASS_ORDER, AR_R_STABILITY_LIMITS, L1_verdict

L1_HAZ_PRODUCT_ONLY_THRESHOLD = 0.60

ap = argparse.ArgumentParser()
ap.add_argument("--vehicle-class", default="small_passenger",
                choices=sorted(AR_R_STABILITY_LIMITS))
ap.add_argument("--out", default=str(REPO_ROOT / "data" / "scenario_sweep.csv"))
args = ap.parse_args()

depths = [round(0.1*i, 1) for i in range(1, 11)]
vels = [round(0.5*i, 1) for i in range(0, 7)]
rows = []
for d in depths:
    for v in vels:
        l0 = "FORD" if d <= 0.15 else "NO-FORD"
        haz = round(d*v, 4)
        l1_haz_product_only = "FORD" if haz <= L1_HAZ_PRODUCT_ONLY_THRESHOLD else "NO-FORD"
        l1 = L1_verdict(d, v, vehicle_class=args.vehicle_class)
        per_class = [L1_verdict(d, v, vehicle_class=c) for c in AR_R_CLASS_ORDER]
        sensitive = len(set(per_class)) > 1
        rows.append([d, v, l0, haz, l1_haz_product_only, l1] + per_class + [sensitive])

header = ["depth_m", "velocity_ms", "L0_verdict", "L1_haz",
          "L1_haz_product_only", "L1_verdict"]
header += [f"L1_verdict_{c}" for c in AR_R_CLASS_ORDER]
header += ["L1_class_sensitive"]

with open(args.out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(rows)

changed = sum(1 for r in rows if r[4] != r[5])
sensitive_n = sum(1 for r in rows if r[-1])
print(f"Wrote {len(rows)} rows to {args.out}")
print(f"L1_verdict column reflects vehicle_class={args.vehicle_class}")
print(f"{changed} rows changed verdict vs product-only baseline")
print(f"{sensitive_n} rows class-sensitive")
for i, c in enumerate(AR_R_CLASS_ORDER):
    print(f"  {c}: FORD={sum(1 for r in rows if r[6+i] == 'FORD')}")
