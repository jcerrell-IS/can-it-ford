import csv

depths = [round(0.1*i, 1) for i in range(1, 11)]
vels = [round(0.5*i, 1) for i in range(0, 7)]
rows = []
for d in depths:
    for v in vels:
        l0 = "FORD" if d <= 0.15 else "NO-FORD"
        haz = round(d*v, 4)
        l1 = "FORD" if haz <= 0.60 else "NO-FORD"
        rows.append([d, v, l0, haz, l1])

out = "/Users/josie/can-it-ford/designsafe-staging/data/scenario_sweep.csv"
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["depth_m", "velocity_ms", "L0_verdict", "L1_haz", "L1_verdict"])
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to {out}")
