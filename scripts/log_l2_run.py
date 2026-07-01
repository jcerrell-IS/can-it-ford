import wandb
import pandas as pd
import sys

# Usage: python scripts/log_l2_run.py 0.30 1.50 NO-FORD
depth    = float(sys.argv[1])
velocity = float(sys.argv[2])
l2       = sys.argv[3]  # FORD or NO-FORD
l1       = "FORD" if depth * velocity <= 0.60 else "NO-FORD"
haz      = round(depth * velocity, 3)

wandb.init(
    project = "can-it-ford",
    entity  = "jcerrell29-claremont-mckenna-college",
    name    = f"L2_d{depth}_v{velocity}",
    tags    = ["L2", "Genesis-MPM", "Vista"],
    config  = {
        "depth_m":      depth,
        "velocity_ms":  velocity,
        "l1_threshold": 0.60,
        "level":        "L2_Genesis_SPH",
        "compute":      "Vista_GH200",
    }
)

wandb.log({
    "depth_m":       depth,
    "velocity_ms":   velocity,
    "dv_product":    round(depth * velocity, 4),
    "l1_haz_score":  haz,
    "l1_verdict":    l1,
    "l2_verdict":    l2,
    "divergence":    l1 != l2,
})

wandb.finish()
print(f"Logged: d={depth}m, v={velocity}m/s | L1={l1} | L2={l2} | divergence={l1!=l2}")
