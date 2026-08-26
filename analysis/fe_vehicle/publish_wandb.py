#!/usr/bin/env python3
"""Log a directory of warpmpm summary.json files to W&B, matching this project's
existing run conventions (name = label, tags carry the sweep and engine, config
carries provenance, summary carries the gated observables).

HONESTY REQUIREMENT, and it is not decorative. Every one of the 17 gated runs
already on this dashboard was logged by a Mac BACKFILL script, so they read
Runtime 0 s and GPU null and the dashboard number is the backfill, not the sim.
These runs are backfills too. They are tagged `backfill` and carry
`compute_host` naming the cluster that actually ran them, so nobody reads a W&B
runtime as a simulation runtime.
"""
import json, os, sys, argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--project", default="can-it-ford")
    p.add_argument("--entity", default="jcerrell29-claremont-mckenna-college")
    p.add_argument("--group", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--compute-host", required=True)
    p.add_argument("--slurm-job", default="")
    p.add_argument("--engine-sha", default="")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    import wandb
    tags = [t for t in a.tags.split(",") if t] + ["backfill", "warpmpm"]

    labels = sorted(d for d in os.listdir(a.root)
                    if os.path.isfile(os.path.join(a.root, d, "summary.json")))
    print(f"{len(labels)} run(s) under {a.root}")
    if a.dry_run:
        for l in labels:
            print("  would log:", l)
        return

    for label in labels:
        s = json.load(open(os.path.join(a.root, label, "summary.json")))
        cfg = {k: v for k, v in s.items()
               if isinstance(v, (int, float, str, bool)) or v is None}
        cfg.update({"compute_host": a.compute_host, "slurm_job": a.slurm_job,
                    "engine_sha": a.engine_sha, "logged_by": "publish_wandb.py",
                    "runtime_is_backfill": True})
        run = wandb.init(entity=a.entity, project=a.project, name=label,
                         group=a.group, tags=tags, config=cfg,
                         reinit=True, settings=wandb.Settings(silent=True))
        for k in ("final_disp_mag_m", "passthrough_max_frac", "C2_veh_zmin_rise",
                  "final_roll_deg", "final_pitch_deg", "final_yaw_deg",
                  "realized_rho", "dx", "water_layers", "hull_m3",
                  "local_depth_bow_peak", "local_depth_footprint_peak",
                  "n_water", "n_vehicle", "n_carved"):
            if isinstance(s.get(k), (int, float)):
                run.summary[k] = s[k]
        run.finish()
        print("  logged", label)


if __name__ == "__main__":
    main()
