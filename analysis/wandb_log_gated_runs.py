#!/usr/bin/env python3
"""Log the 17 canonical gated runs to W&B with full provenance config.

WHY THIS EXISTS. The repeated failure mode in this project is a headline
number that cannot be traced back to the configuration it was measured at.
The settle-frame case is the worked example: a 60-frame settle was shown to
be inadequate, 250 was needed, and an ordering INVERTED between them. If
settle_frames and the driver hash are logged as run config, "was this
measured at an 8-frame settle?" becomes a filter in the W&B UI instead of an
archaeology dig through directories.

WHAT IT DOES NOT DO. It does not re-derive any verdict. Verdicts come from
the canonical stores, and the L1 verdict is imported from vehicle_params
rather than reimplemented, because a second copy of a threshold is how the
0.60-vs-0.30 defect reached the public demo.

TWO TRAPS THIS SCRIPT RESPECTS (CLAUDE.md item 12):
  1. `triggered_*` is the verdict; `ratio_*` is a peak magnitude. They
     disagree. Filtering on ratio >= 1 reports 13 topples that never
     happened. Both are logged, under names that cannot be confused.
  2. STUCK is the none-sustained case, not a fourth mode on its own scale.
     Its winning-mode columns are empty BY DESIGN, not missing.

Usage:
    python analysis/wandb_log_gated_runs.py --dry-run
    python analysis/wandb_log_gated_runs.py
"""
import argparse
import csv
import hashlib
import importlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from vehicle_params import L1_verdict  # noqa: E402  single source of truth

ENTITY = "jcerrell29-claremont-mckenna-college"
PROJECT = "can-it-ford"
GROUP = "gated-17"

INVENTORY = os.path.join(REPO, "data", "all_runs_inventory.csv")
FAILURE_MODES = os.path.join(REPO, "data", "failure_modes_by_run_classified.csv")
DRIVER = os.path.join(REPO, "renders", "yaris_render_s1", "sim_standing.py")

# The Yaris maps to the AR&R Small passenger class (vehicle_params.py:121-122).
# The 1609 kg and 2337 kg arms have no sourced vehicle class, so the class is
# recorded explicitly per run rather than assumed to apply to all of them.
YARIS_CLASS = "small_passenger"

FLOAT_METRICS = [
    "final_disp_mag_m", "passthrough_max_frac", "realized_rho",
    "realized_depth_m", "velocity_ms", "dx", "hull_m3", "solid_volume_m3",
]


def driver_sha256():
    with open(DRIVER, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_rows():
    with open(INVENTORY) as f:
        inv = {r["run"]: r for r in csv.DictReader(f)}
    with open(FAILURE_MODES) as f:
        modes = {r["run"]: r for r in csv.DictReader(f)}
    missing = set(inv) ^ set(modes)
    if missing:
        raise SystemExit(f"inventory and failure-mode stores disagree on: {sorted(missing)}")
    return inv, modes


def build(run, inv_row, mode_row, sha):
    depth = as_float(inv_row.get("realized_depth_m"))
    vel = as_float(inv_row.get("velocity_ms"))
    mass = as_float(inv_row.get("mass_kg"))

    l1 = None
    if depth is not None and vel is not None:
        l1 = L1_verdict(depth, vel, YARIS_CLASS)

    config = {
        "run": run,
        "engine": "warpmpm",          # NOT Genesis. CLAUDE.md item 1.
        "scenario": inv_row.get("scenario"),
        "sweep": inv_row.get("sweep"),
        "n_grid": int(inv_row["n_grid"]) if inv_row.get("n_grid") else None,
        "mass_kg": mass,
        "water_layers": inv_row.get("water_layers"),
        "vehicle_asset": "yaris_coarse_v1l_watertight.ply",
        "arr_class_used_for_l1": YARIS_CLASS,
        "arr_class_is_sourced": mass == 1100.0,
        # provenance: the whole point of this script
        "driver": "renders/yaris_render_s1/sim_standing.py",
        "driver_sha256": sha,
        "settle_frames": 8,
        "settle_frames_source": "sim_standing.py:154 driver default, not recorded per-run",
        "floor_friction": 0.55,
        "gravity_ms2": 9.81,
    }
    for key in FLOAT_METRICS:
        config[key] = as_float(inv_row.get(key))

    metrics = {
        # verdict, authoritative
        "failure_mode": mode_row.get("mode"),
        "triggered_slide": mode_row.get("triggered_slide") == "True",
        "triggered_topple": mode_row.get("triggered_topple") == "True",
        "triggered_float": mode_row.get("triggered_float") == "True",
        # peak magnitude, NOT a verdict. Never threshold these at 1.0.
        "peak_ratio_slide": as_float(mode_row.get("ratio_slide")),
        "peak_ratio_topple": as_float(mode_row.get("ratio_topple")),
        "peak_ratio_float": as_float(mode_row.get("ratio_float")),
        "onset_frame_slide": as_float(mode_row.get("onset_frame_slide")),
        "final_disp_mag_m": as_float(inv_row.get("final_disp_mag_m")),
        "passthrough_max_frac": as_float(inv_row.get("passthrough_max_frac")),
        "l1_verdict_joint_rule": l1,
    }
    return config, metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print, do not write to W&B")
    ap.add_argument("--project", default=PROJECT)
    args = ap.parse_args()

    sha = driver_sha256()
    inv, modes = load_rows()
    print(f"driver sha256: {sha}")
    print(f"runs to log  : {len(inv)}")

    # Imported lazily so --dry-run works on a machine without wandb installed.
    wandb = importlib.import_module("wandb") if not args.dry_run else None

    for run in sorted(inv):
        config, metrics = build(run, inv[run], modes[run], sha)
        if args.dry_run:
            print(f"\n--- {run} ---")
            print(f"  n_grid={config['n_grid']} mass={config['mass_kg']} "
                  f"depth={config['realized_depth_m']} vel={config['velocity_ms']}")
            print(f"  mode={metrics['failure_mode']} "
                  f"triggered_slide={metrics['triggered_slide']} "
                  f"peak_ratio_slide={metrics['peak_ratio_slide']}")
            print(f"  l1_joint={metrics['l1_verdict_joint_rule']} "
                  f"settle_frames={config['settle_frames']}")
            continue

        r = wandb.init(
            project=args.project,
            entity=ENTITY,
            name=run,
            group=GROUP,
            job_type="gated-backfill",
            tags=["L2", "warpmpm", "gated-17", f"n_grid_{config['n_grid']}"],
            config=config,
            reinit=True,
        )
        wandb.log({k: v for k, v in metrics.items() if v is not None})
        r.finish()
        print(f"logged {run}")

    if args.dry_run:
        print("\ndry run only, nothing written to W&B")


if __name__ == "__main__":
    main()
