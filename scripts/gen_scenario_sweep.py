import csv
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
from vehicle_params import L1_verdict

L1_HAZ_PRODUCT_ONLY_THRESHOLD = 0.60

depths = [round(0.1*i, 1) for i in range(1, 11)]
vels = [round(0.5*i, 1) for i in range(0, 7)]
rows = []
for d in depths:
    for v in vels:
        l0 = "FORD" if d <= 0.15 else "NO-FORD"
        haz = round(d*v, 4)
        l1_haz_product_only = "FORD" if haz <= L1_HAZ_PRODUCT_ONLY_THRESHOLD else "NO-FORD"
        l1 = L1_verdict(d, v, vehicle_class="small_car")
        rows.append([d, v, l0, haz, l1_haz_product_only, l1])

out = str(REPO_ROOT / "data" / "scenario_sweep.csv")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["depth_m", "velocity_ms", "L0_verdict", "L1_haz", "L1_haz_product_only", "L1_verdict"])
    w.writerows(rows)

changed = sum(1 for r in rows if r[4] != r[5])
print(f"Wrote {len(rows)} rows to {out}")
print(f"{changed} rows changed verdict")
