import wandb

API_KEY = "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"
ORG = "jcerrell29-claremont-mckenna-college"

runs = [
    {"depth_m":0.15,"velocity_ms":0.0,"verdict":"FORD"},
    {"depth_m":0.30,"velocity_ms":0.0,"verdict":"FORD"},
    {"depth_m":0.60,"velocity_ms":0.0,"verdict":"FORD"},
    {"depth_m":0.15,"velocity_ms":1.5,"verdict":"NO-FORD"},
    {"depth_m":0.30,"velocity_ms":1.5,"verdict":"NO-FORD"},
    {"depth_m":0.45,"velocity_ms":1.5,"verdict":"NO-FORD"},
    {"depth_m":0.60,"velocity_ms":1.5,"verdict":"NO-FORD"},
    {"depth_m":0.30,"velocity_ms":1.0,"verdict":"NO-FORD"},
    {"depth_m":0.30,"velocity_ms":2.0,"verdict":"NO-FORD"},
]

wandb.login(key=API_KEY)

for r in runs:
    l1_haz = round(r["depth_m"] * r["velocity_ms"], 3)
    l1_verdict = "NO-FORD" if l1_haz > 0.60 else "FORD"
    divergence = (r["verdict"] == "NO-FORD" and l1_verdict == "FORD")

    run = wandb.init(
        project="can-it-ford",
        entity=ORG,
        name=f"d{r['depth_m']}_v{r['velocity_ms']}",
        config={
            "depth_m": r["depth_m"],
            "velocity_ms": r["velocity_ms"],
            "vehicle_class": "4WD",
            "drift_threshold_m": 0.05,
        },
        reinit=True
    )
    wandb.log({
        "L2_verdict": 1 if r["verdict"]=="FORD" else 0,
        "L1_verdict": 1 if l1_verdict=="FORD" else 0,
        "L1_hazard": l1_haz,
        "depth_m": r["depth_m"],
        "velocity_ms": r["velocity_ms"],
        "L1_L2_divergence": int(divergence),
    })
    wandb.summary.update({
        "verdict": r["verdict"],
        "L1_verdict": l1_verdict,
        "divergence": divergence,
    })
    run.finish()
    print(f"Logged d={r['depth_m']} v={r['velocity_ms']} → {r['verdict']} | divergence={divergence}")

print("\nDone. Go to: https://wandb.ai/jcerrell29-claremont-mckenna-college/can-it-ford")
