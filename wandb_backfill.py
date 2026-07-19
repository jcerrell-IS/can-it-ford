import wandb
import pandas as pd

df = pd.read_csv("data/scenario_sweep.csv")

for _, row in df.iterrows():
    run = wandb.init(project="can-it-ford", tags=["l0-l1-pilot"], reinit=True)
    run.config.update({
        "depth_m": row["depth_m"],
        "velocity_ms": row["velocity_ms"]
    })
    run.summary.update({
        "L0_verdict": row["L0_verdict"],
        "L1_haz": row["L1_haz"],
        "L1_verdict": row["L1_verdict"]
    })
    run.finish()

print("Backfill complete:", len(df), "runs logged.")
