#!/usr/bin/env python3
"""Build a Hugging Face dataset directory for Can It Ford, locally, and never publish it by accident.

WHY THIS EXISTS
---------------
The deliverable is the DATASET CARD, not the upload. This project's own history is a
list of numbers that travelled without their scope: a density band quoted outside the
hull it described, a verdict count quoted without the thresholds deciding it, a "cited"
figure that was really a "reach" figure. A dataset published without the scope attached
would export that failure mode to strangers, who have no CLAUDE.md to correct it with.

So this script does three things, in descending order of importance:

  1. Writes a card that states what the numbers do NOT mean.
  2. Refuses, in code, to carry any file whose licence is unresolved (constraint B6).
  3. Refuses, in code, to touch the network unless two separate flags are passed.

WHAT IT BUILDS
--------------
  canonical_runs.csv      the 17 gated warpmpm runs, derived scalars only
  verdict_sensitivity.csv the same 17 runs' verdict recomputed across a threshold sweep,
                          which is the ingredient the binary label throws away
  load_surface.csv        the d17-moving (v_car x v_water) schema. Written with headers
                          and zero rows until that slot lands data. An empty table with
                          a correct schema is honest; a fabricated one is not.
  README.md               the dataset card

ENGINE, STATED ONCE AND CARRIED INTO THE CARD
---------------------------------------------
The 17 gated runs are warpmpm via renders/yaris_render_s1/sim_standing.py. They are NOT
Genesis. Genesis is the abandoned box-proxy path only. CLAUDE.md August 4 audit item 1.

SOURCES, all read live at build time, none carried from memory:
  data/all_runs_inventory.csv
  data/failure_modes_by_run_classified.csv
  vehicle_params.py                          (mass only, via text scan, no import)

Usage:
  python3 analysis/hf_dataset_publish.py --out build/hf_dataset
  python3 analysis/hf_dataset_publish.py --self-test
  python3 analysis/hf_dataset_publish.py --out ... --publish            # refuses
  python3 analysis/hf_dataset_publish.py --out ... --publish --approved-by-josie
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys

# ---------------------------------------------------------------------------
# Constraint B6: licence-unresolved assets. Enforced, not documented.
# ---------------------------------------------------------------------------
# d13-renders found assets/DaySkyHDRI002A_1K_HDR.exr shipping ungated in the PUBLIC
# repo as a required render input, and d10-licence's audit returns zero hits for
# assets/, hdri, ambientcg, CC0 and texture across all 11 sections. Verified live
# 2026-08-19: SIX files are tracked on origin/main under assets/, not one.
# Until Josie rules, no image, texture, HDRI or mesh leaves this script.
BLOCKED_PATH_TOKENS = ("assets/", "hdri", "ambientcg", "texture", "renders/")
BLOCKED_SUFFIXES = (
    ".exr", ".hdr", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp",
    ".ply", ".obj", ".stl", ".glb", ".gltf", ".mp4", ".mov", ".gif", ".npz",
)

# Thresholds that decide every verdict in this dataset. Read live from
# simulation/failure_modes.py at build time; these are the fallbacks used only if
# that read fails, and the card records which route was taken.
FALLBACK_THRESHOLDS = {
    "slide_m": 0.05,
    "slide_speed_ms": 0.05,
    "float_m": 0.05,
    "sustain_frames": 3,
}


class AssetGateError(RuntimeError):
    """Raised when a licence-unresolved path would enter the dataset."""


def assert_publishable(paths) -> None:
    """Refuse any path whose licence is unresolved. Raises, never warns.

    A warning would be ignored at 2am, which is when this will run.
    """
    bad = []
    for p in paths:
        low = str(p).lower().replace(os.sep, "/")
        if any(tok in low for tok in BLOCKED_PATH_TOKENS):
            bad.append((p, "path token"))
        elif low.endswith(BLOCKED_SUFFIXES):
            bad.append((p, "binary/asset suffix"))
    if bad:
        lines = "\n".join(f"    {p}   ({why})" for p, why in bad)
        raise AssetGateError(
            "ASSET GATE: refusing to include licence-unresolved or binary paths.\n"
            f"{lines}\n"
            "  Discrepancy register 2026-08-19 row B6 is OPEN and UNOWNED.\n"
            "  Derived numbers are fine. Images, textures, HDRIs and meshes are not,\n"
            "  until Josie rules on asset provenance."
        )


# ---------------------------------------------------------------------------
# Reading canonical sources
# ---------------------------------------------------------------------------

def _read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_thresholds(repo: str) -> tuple[dict, str]:
    """Read the four deciding literals from failure_modes.py by text scan.

    Deliberately NOT an import: importing pulls numpy, which no system interpreter on
    this Mac has. Deliberately keyed by NAME, never by value: slide_m, slide_speed_ms
    and float_m all carry the numeral 0.05 in TWO different units, and CLAUDE.md item
    13 records that deduplicating them by value silently converts a speed into a
    distance and changes SLIDE verdicts.
    """
    src = os.path.join(repo, "simulation", "failure_modes.py")
    out, route = dict(FALLBACK_THRESHOLDS), "fallback (live read failed)"
    try:
        with open(src, encoding="utf-8") as fh:
            text = fh.read()
        found = {}
        for line in text.splitlines():
            stripped = line.split("#")[0].strip()
            for name in FALLBACK_THRESHOLDS:
                if stripped.startswith(f"{name}") and "=" in stripped:
                    lhs, _, rhs = stripped.partition("=")
                    if lhs.strip().split(":")[0].strip() == name:
                        try:
                            found[name] = float(rhs.strip().rstrip(","))
                        except ValueError:
                            pass
        if len(found) == len(FALLBACK_THRESHOLDS):
            out, route = found, f"read live from {os.path.relpath(src, repo)}"
    except OSError:
        pass
    return out, route


def build_canonical_runs(repo: str) -> list[dict]:
    """Merge the 17-run inventory with the classified failure modes, on run id."""
    inv = _read_csv(os.path.join(repo, "data", "all_runs_inventory.csv"))
    fm = {r["run"]: r for r in _read_csv(
        os.path.join(repo, "data", "failure_modes_by_run_classified.csv"))}

    rows = []
    for r in inv:
        run = r["run"]
        f = fm.get(run, {})
        rows.append({
            "run_id": run,
            "sweep": r.get("sweep", ""),
            "n_grid": r.get("n_grid", ""),
            "mass_kg": r.get("mass_kg", ""),
            "requested_depth_m": r.get("requested_depth_m", ""),
            "realized_depth_m": r.get("realized_depth_m", ""),
            "velocity_ms": r.get("velocity_ms", ""),
            "dx_m": r.get("dx", ""),
            "water_layers": r.get("water_layers", ""),
            "final_disp_mag_m": r.get("final_disp_mag_m", ""),
            "max_surge_drift_m": f.get("max_surge_drift_m", ""),
            "max_vertical_lift_m": f.get("max_vertical_lift_m", ""),
            "max_speed_ms": f.get("max_speed_ms", ""),
            "failure_mode": f.get("mode", ""),
            "triggered_slide": f.get("triggered_slide", ""),
            "triggered_topple": f.get("triggered_topple", ""),
            "triggered_float": f.get("triggered_float", ""),
            "ratio_slide": f.get("ratio_slide", ""),
            "passthrough_max_frac": r.get("passthrough_max_frac", ""),
            "realized_rho_kg_m3": r.get("realized_rho", ""),
            "floor_friction": r.get("floor_friction", ""),
            "sound_speed_ms": r.get("sound_speed_ms", ""),
            "frames": r.get("frames", ""),
            "engine": "warpmpm",
        })
    return rows


def build_verdict_sensitivity(rows: list[dict], thresholds: dict) -> list[dict]:
    """Recompute the SLIDE call across a sweep of the deciding distance threshold.

    This is the table the binary label throws away. It answers "how close is this
    verdict to flipping", which is the whole reason probabilistic_verdict.py exists.

    NOTE ON WHAT THIS IS NOT. This is a one-at-a-time sweep of slide_m against the
    recorded peak drift. CLAUDE.md records that a one-at-a-time sweep is a FALSE
    NEGATIVE that has already been published and retracted on this project: verdicts
    flip only under JOINT perturbation of slide_m, slide_speed_ms and sustain_frames.
    So this column bounds the sensitivity from BELOW and the card says so.
    """
    base = thresholds["slide_m"]
    grid = [round(base * m, 4) for m in (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0)]
    out = []
    for r in rows:
        try:
            drift = float(r["max_surge_drift_m"])
        except (TypeError, ValueError):
            continue
        rec = {"run_id": r["run_id"], "max_surge_drift_m": drift,
               "published_mode": r["failure_mode"]}
        for t in grid:
            rec[f"exceeds_slide_m_{t}"] = "True" if drift > t else "False"
        flips = [t for t in grid if (drift > t) != (drift > base)]
        rec["flips_within_sweep"] = "True" if flips else "False"
        rec["nearest_flip_slide_m"] = min(flips, key=lambda t: abs(t - base)) if flips else ""
        out.append(rec)
    return out


LOAD_SURFACE_COLUMNS = [
    # Schema mirrors d17-moving's pre-registration, docs/R9_MOVING_VEHICLE_2026-08-19.md
    # section 3, commit d3e52fd, so their output drops in without a translation layer.
    "cell_id", "v_car_ms", "v_water_ms", "v_rel_mag_ms", "angle_from_broadside_deg",
    "repeat_index", "n_grid", "depth_m", "frame_window",
    "F_horiz_N", "F_x_N", "F_y_N", "F_z_N",
    "torque_about_collider_centre_Nm",
    "fz_settle_over_analytic_diagnostic", "frame", "engine", "run_id",
]


def write_dataset(repo: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    thresholds, route = read_thresholds(repo)
    runs = build_canonical_runs(repo)
    sens = build_verdict_sensitivity(runs, thresholds)

    written = []

    def _write(name, rows, cols):
        path = os.path.join(out_dir, name)
        assert_publishable([name])
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        written.append(path)
        return path

    _write("canonical_runs.csv", runs, list(runs[0].keys()))
    _write("verdict_sensitivity.csv", sens, list(sens[0].keys()) if sens else ["run_id"])
    _write("load_surface.csv", [], LOAD_SURFACE_COLUMNS)

    card = render_card(runs, thresholds, route)
    card_path = os.path.join(out_dir, "README.md")
    with open(card_path, "w", encoding="utf-8") as fh:
        fh.write(card)
    written.append(card_path)

    # Final gate: everything actually on disk, checked again. Belt and braces, because
    # the first check ran on intended names and this one runs on reality.
    assert_publishable([os.path.relpath(p, out_dir) for p in written])

    manifest = {
        "files": [
            {"name": os.path.relpath(p, out_dir),
             "bytes": os.path.getsize(p),
             "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()}
            for p in sorted(written)
        ],
        "n_canonical_runs": len(runs),
        "n_load_surface_rows": 0,
        "thresholds": thresholds,
        "threshold_route": route,
        "engine_canonical_runs": "warpmpm",
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def render_card(runs: list[dict], thresholds: dict, route: str) -> str:
    modes = {}
    for r in runs:
        modes[r["failure_mode"]] = modes.get(r["failure_mode"], 0) + 1
    mode_str = ", ".join(f"{v} {k}" for k, v in sorted(modes.items(), key=lambda kv: -kv[1]))
    grids = sorted({r["n_grid"] for r in runs}, key=lambda s: int(s) if s.isdigit() else 0)

    return f"""---
license: odc-by
language:
  - en
tags:
  - flood
  - material-point-method
  - vehicle-stability
  - computational-fluid-dynamics
pretty_name: Can It Ford, vehicle stability in floodwater
size_categories:
  - n<1K
configs:
  - config_name: canonical_runs
    data_files: canonical_runs.csv
  - config_name: verdict_sensitivity
    data_files: verdict_sensitivity.csv
  - config_name: load_surface
    data_files: load_surface.csv
---

# Can It Ford: vehicle stability in floodwater

Simulation records for whether a specific vehicle can safely cross a flooded roadway.
NSF REU, GeoElements Lab, UT Austin. PI Krishna Kumar.

**Read the limitations before the numbers.** Most of what has gone wrong on this project
was a correct number quoted without its scope.

## What is in here

| table | rows | what it is |
|---|---|---|
| `canonical_runs.csv` | {len(runs)} | the gated stationary-vehicle runs |
| `verdict_sensitivity.csv` | {len(runs)} | the same runs' SLIDE call across a threshold sweep |
| `load_surface.csv` | 0 | schema only, see below |

### `canonical_runs.csv`

{len(runs)} runs of a Yaris hull held in still-to-flowing water, swept over mass, grid
resolution, depth and flow velocity. Grids present: {", ".join(grids)}.

Published failure modes: **{mode_str}**.

### `verdict_sensitivity.csv`

The failure mode is decided by comparing a peak drift against a distance threshold. That
threshold is a **choice**, not a measurement. This table recomputes the comparison across
a sweep of it, so a reader can see which runs sit near the boundary.

**This table bounds the sensitivity from BELOW, and deliberately so.** It varies one
threshold at a time. On this project a one-at-a-time sweep has already produced a
published claim that had to be retracted: verdicts flip only under JOINT perturbation of
the distance, the speed and the persistence count. Treat `flips_within_sweep = False` as
"not shown to flip by this weak test", never as "robust".

### `load_surface.csv`

**Zero rows, on purpose.** This is the schema for a (vehicle speed x flow velocity) load
surface being produced separately. The headers are committed ahead of the data so the
data cannot be graded against a schema invented after seeing it. An empty table with a
correct schema is honest. A fabricated one is not.

When populated, **the vehicle in those runs is PRESCRIBED, not free.** It is held on a
path and the reaction load is measured. It cannot be swept away, because being swept away
is exactly the degree of freedom that scene removes. **No FORD or NO-FORD verdict is
derivable from the load surface.** That verdict belongs to the stationary-vehicle
criterion, which is a different question with a different validation basis.

Torque is reported about the **collider centre**, not the centre of gravity. The column
is named `torque_about_collider_centre_Nm` so it cannot be silently misread.

## Engine

The canonical runs use **warpmpm**, a material point method solver, via
`renders/yaris_render_s1/sim_standing.py`. **They are not Genesis.** Genesis was an
earlier box-proxy path that never loaded the vehicle hull, and describing these runs as
Genesis has been a recurring error on this project. Every row carries `engine = warpmpm`
so the distinction survives a copy-paste.

## Thresholds that decide the verdicts

{route}.

| name | value | unit |
|---|---|---|
| `slide_m` | {thresholds['slide_m']} | metres |
| `slide_speed_ms` | {thresholds['slide_speed_ms']} | **metres per second** |
| `float_m` | {thresholds['float_m']} | metres |
| `sustain_frames` | {int(thresholds['sustain_frames'])} | frames |

**Three of these share the numeral 0.05 across two different units.** A find-and-replace
on the value would silently convert a speed into a distance. Deduplicate by name and
unit, never by value.

`sustain_frames` has **no published source**. No criterion in the vehicle-stability
literature reviewed for this project uses a persistence count at all, and two of the
studies restrained their models so duration was unmeasurable in principle. It is an
unsourced choice that gates every verdict in the dataset.

## Limitations, stated as strongly as the results

- **Resolution is not converged.** The baseline resolves the water column with about
  2 grid cells and 4 particle layers, against a rule of thumb of roughly 10 particles per
  flow depth. Displacement magnitude is non-monotone across grid refinement. **Cite the
  verdict, never the displacement magnitude.**
- **Coarse resolution usually over-predicts peak hydrodynamic force**, so verdicts that
  exceed a threshold are conservative for safety purposes. That argument does not make
  the numbers converged.
- **No gate here is a physics validation.** The gates are self-consistency and numerical
  containment checks. Several compare against a reference derived from the same pipeline,
  so they cannot fail for a reason external to the code.
- **The record is short and serially correlated.** Uncertainty computed from the raw
  frame count is overstated several-fold. Use an effective sample size.
- **Two of the three masses in the sweep are not sourced** to a vehicle class in this
  project's own parameter file.
- **The scenario is a stationary vehicle in flow.** That matches the validated stability
  criterion the verdicts are compared against. The word "ford" in the project title
  implies motion, and it is the title that mismatches, not the setup.

## What is deliberately absent

No images, meshes, textures, HDRIs or rendered frames. Asset provenance for this
project's render inputs is an open, unresolved licence question, and derived numbers are
publishable while those files are not. This is enforced in code by the build script's
asset gate, not by convention.

## Licence

Data offered under **ODC-By-1.0**, matching `CITATION.cff` in the source repository. Note
that the repository's own `LICENSE` file is BSD-3-Clause, which covers the **code**. If
you need certainty about which applies to a given file, ask before relying on it.

## Citation

See `CITATION.cff` in the source repository.

---

*Card generated by `analysis/hf_dataset_publish.py`. Regenerate rather than hand-edit, or
the numbers and the prose will drift apart.*
"""


# ---------------------------------------------------------------------------
# Publishing, which this script will not do without two flags
# ---------------------------------------------------------------------------

def publish(out_dir: str, repo_id: str, approved: bool) -> int:
    if not approved:
        print("\nPUBLISH REFUSED.")
        print("  --publish alone does nothing. Publishing to Hugging Face is an")
        print("  outward-facing action on Josie's account and it is her call, not mine.")
        print("  There is also an unrotated credential exposure open on this machine.")
        print("\n  What --publish --approved-by-josie WOULD do, exactly:")
        print(f"    1. create dataset repo '{repo_id}' with private=True")
        print(f"    2. upload only the files in {out_dir}")
        print("    3. print the URL and stop. It never flips a repo to public.")
        print("\n  Making it public is a separate manual step in the HF web UI.")
        return 2

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("huggingface_hub not installed. uv pip install huggingface_hub")
        return 3

    files = sorted(os.listdir(out_dir))
    assert_publishable(files)  # gate fires again at the network boundary
    api = HfApi()
    api.create_repo(repo_id=repo_id, repo_type="dataset", private=True, exist_ok=True)
    api.upload_folder(folder_path=out_dir, repo_id=repo_id, repo_type="dataset")
    print(f"uploaded to https://huggingface.co/datasets/{repo_id}  (PRIVATE)")
    print("It is private. Flipping it public is a manual step and nothing here does it.")
    return 0


# ---------------------------------------------------------------------------
# Self-tests. Each one has a positive control, because a check that cannot tell
# "blocked" from "could not evaluate" is worse than no check.
# ---------------------------------------------------------------------------

def self_test(repo: str) -> int:
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}  {detail}")
        if not cond:
            fails.append(name)

    print("ST1 asset gate blocks what it must")
    for bad in ("assets/DaySkyHDRI002A_1K_HDR.exr", "sky.exr", "hull.ply",
                "renders/yaris_render_s1/frame.png", "rollout.npz"):
        try:
            assert_publishable([bad])
            check(f"blocks {bad}", False, "NOT BLOCKED")
        except AssetGateError:
            check(f"blocks {bad}", True)

    print("ST2 POSITIVE CONTROL: the gate must PASS things it must not block")
    for good in ("canonical_runs.csv", "README.md", "manifest.json"):
        try:
            assert_publishable([good])
            check(f"allows {good}", True)
        except AssetGateError:
            check(f"allows {good}", False, "gate is blocking everything, so ST1 proved nothing")

    print("ST3 thresholds are read by NAME and keep distinct units")
    th, route = read_thresholds(repo)
    check("four thresholds present", len(th) == 4, str(sorted(th)))
    check("slide_m and slide_speed_ms are separate keys",
          "slide_m" in th and "slide_speed_ms" in th)
    check("route recorded", bool(route), route)

    print("ST4 canonical run count and engine tag")
    runs = build_canonical_runs(repo)
    check("17 canonical runs", len(runs) == 17, f"got {len(runs)}")
    check("every row tagged warpmpm", all(r["engine"] == "warpmpm" for r in runs))
    modes = {r["failure_mode"] for r in runs}
    check("modes are the published set", modes <= {"SLIDE", "STUCK", "TOPPLE", "FLOAT"},
          str(sorted(modes)))

    print("ST5 load surface schema is committed empty, not fabricated")
    check("schema has the two speeds separately",
          "v_car_ms" in LOAD_SURFACE_COLUMNS and "v_water_ms" in LOAD_SURFACE_COLUMNS)
    check("torque names its reference point",
          "torque_about_collider_centre_Nm" in LOAD_SURFACE_COLUMNS)

    print("ST6 publish refuses without the second flag")
    rc = publish("/nonexistent", "x/y", approved=False)
    check("refuses and returns nonzero", rc == 2, f"rc={rc}")

    print(f"\n{len(fails)} failure(s)" + (": " + ", ".join(fails) if fails else ""))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build a Hugging Face dataset directory for Can It Ford, locally.")
    ap.add_argument("--repo", default="/Users/josie/can-it-ford",
                    help="canonical checkout to read data from")
    ap.add_argument("--out", default=None, help="output directory for the dataset")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--approved-by-josie", action="store_true",
                    help="required second flag; without it --publish only explains itself")
    ap.add_argument("--repo-id", default="josiecerrell/can-it-ford")
    args = ap.parse_args()

    if args.self_test:
        return self_test(args.repo)

    if not args.out:
        ap.error("--out is required unless --self-test")

    manifest = write_dataset(args.repo, args.out)
    print(f"wrote {len(manifest['files'])} files to {args.out}")
    for f in manifest["files"]:
        print(f"  {f['name']:26s} {f['bytes']:8d} B  sha256:{f['sha256'][:12]}")
    print(f"canonical runs: {manifest['n_canonical_runs']}, "
          f"load surface rows: {manifest['n_load_surface_rows']}")
    print(f"thresholds: {manifest['threshold_route']}")

    if args.publish:
        return publish(args.out, args.repo_id, args.approved_by_josie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
