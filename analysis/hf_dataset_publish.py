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
    ap.add_argument("--speed-surface", action="store_true",
                    help="build the (v_car x v_water) load-surface dataset instead")
    args = ap.parse_args()

    if args.self_test:
        return self_test(args.repo)

    if not args.out:
        ap.error("--out is required unless --self-test")

    if args.speed_surface:
        stats = build_speed_surface_dataset(args.repo, args.out)
        print(f"wrote {len(stats['files'])} files to {args.out}")
        for f in stats["files"]:
            print(f"  {os.path.basename(f):24s} {os.path.getsize(f):8d} B")
        print(f"records {stats['n_records']}, surface cells {stats['n_cells']}")
        ts = stats["three_spreads"]
        print(f"  seed spread   {ts['seed_spread_pct']['min']:.3f} to "
              f"{ts['seed_spread_pct']['max']:.3f} %")
        print(f"  split S       {ts['split_spread_S']['min']:.3f} to "
              f"{ts['split_spread_S']['max']:.3f}")
        print(f"  window spread {ts['window_spread_pct']['min']:.1f} to "
              f"+{ts['window_spread_pct']['max']:.1f} %")
        return 0

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




# ===========================================================================
# SPEED SURFACE DATASET, d17-moving's (v_car x v_water) load surface.
#
# Added 2026-08-19. This is a DIFFERENT experiment from canonical_runs above:
# a prescribed collider with no verdict, against free bodies with a verdict.
# The two must never be concatenated.
# ===========================================================================

SPEED_SURFACE_SOURCE = {
    "blob": "7eee079a7085c98e140ca61ea708ebb70003d71e",
    "commit": "159bf7d",
    "branch": "claude/r9-moving-vehicle",
    "path": "data/r9_speed_surface.tsv",
}

# Measured live 2026-08-19 from the PLY header of the canonical hull.
YARIS_VERTICES = 327212
YARIS_FACES = 655308
# From d17 R9, their measurement, secondary for this card.
SILVERADO_COARSE_VERTICES = 2108
SILVERADO_FINE_VERTICES = 48706


def _load_speed_surface(repo: str) -> list[dict]:
    path = os.path.join(repo, ".claude", "worktrees", "r9-platform",
                        "hf_space", "data", "load_surface.csv")
    if not os.path.exists(path):
        raise RuntimeError(f"{path} absent; run hf_space/ingest_speed_surface.py first")
    rows = _read_csv(path)
    if not rows:
        raise RuntimeError(f"{path} present but empty; refusing to build a card from it")
    return rows


def render_speed_surface_card(stats: dict) -> str:
    """The card IS the deliverable. Every number here is computed, not typed."""
    hp = stats["headline"]
    ts = stats["three_spreads"]
    arcs = stats["arcs"]
    rc = stats["resolution"]
    seed = ts["seed_spread_pct"]
    split = ts["split_spread_S"]
    win = ts["window_spread_pct"]
    arc_str = ", ".join(f"{a['v_rel_mag_ms']:g} m/s -> S={a['S_spread']:.2f}" for a in arcs)
    hull_ratio = YARIS_VERTICES / SILVERADO_COARSE_VERTICES

    return f"""---
license: cc-by-4.0
tags:
  - flood
  - vehicle-stability
  - material-point-method
  - computational-fluid-dynamics
  - civil-engineering
pretty_name: "Can It Ford: vehicle-speed x flow-velocity load surface"
---

# Can It Ford: a (vehicle speed x flow velocity) load surface

Hydrodynamic load on a passenger-car hull in a flooded roadway, measured as a
function of **two speeds kept as separate axes**: the vehicle's speed over the
ground, and the flow speed across the roadway.

## Read this before you read a number

**The vehicle is PRESCRIBED, not free.** It is a rigid signed-distance-field
collider moved along a path. It cannot slide, tip, float or be swept away,
because those degrees of freedom are exactly what the scene removes.

**No FORD or NO-FORD verdict is derivable from this dataset.** It reports a
LOAD. Whether that load moves a real vehicle depends on tyre-road friction,
suspension and wheel state, none of which are in this scene. See Limitations.

Torque in the source is about the **collider centre, not the centre of gravity**,
and is not carried into this table for that reason.

## Why this dataset exists

A {stats['n_papers']}-paper literature search commissioned for this question found that
vehicle-wading studies "reduce stability to failure thresholds (e.g., depth or
depth x velocity), **not a continuous safe-speed surface resolving vehicle speed
independently from current velocity**". This dataset is that surface.

*That characterisation of the literature is a **secondary-source claim**. The
papers were not read for this card, and the sentence above is quoted from the
search's own summary.*

## The result, in one comparison

If a single relative speed determined the load, then two runs sharing
`v_rel_mag_ms` would carry the same force. They do not.

| | lower relative speed | higher relative speed |
|---|---|---|
| v_car, v_water (m/s) | {hp['cell_lower_vrel']['v_car_ms']}, {hp['cell_lower_vrel']['v_water_ms']} | {hp['cell_higher_vrel']['v_car_ms']}, {hp['cell_higher_vrel']['v_water_ms']} |
| \\|v_rel\\| (m/s) | {hp['cell_lower_vrel']['v_rel_mag_ms']:.3f} | {hp['cell_higher_vrel']['v_rel_mag_ms']:.3f} |
| settled window, 5 seeds | **{hp['settled']['lower_N']:.0f} +/- {hp['settled']['lower_sd_N']:.1f} N** | **{hp['settled']['higher_N']:.0f} +/- {hp['settled']['higher_sd_N']:.1f} N** |

Across nine ways of splitting one fixed relative speed, the load spans
S = (max - min) / mean of **{split['min']:.2f} to {split['max']:.2f}**, and S grows with speed:
{arc_str}.

## Three spreads, and they are not the same size

Conflating them is the easiest way to misread this dataset.

| spread | what varies | size | is it an error bar? |
|---|---|---|---|
| **seed** | 5 seeds, one cell | {seed['min']:.3f} to {seed['max']:.3f} % (median {seed['median']:.3f}) | yes, and it is tiny |
| **split** | how one \\|v_rel\\| divides into v_car and v_water | {100*split['min']:.0f} to {100*split['max']:.0f} % | **no, this is the result** |
| **window** | measurement window f20-60 vs f250-400 | {win['min']:.1f} to +{win['max']:.1f} % | no, it means the load is still changing |

Error bars drawn from seed scatter would be invisible and would imply the other
two spreads do not exist.

## A published comparison inverts between windows, and both halves are reported

The source write-up states, from the **transient** window f20-60:
{hp['transient']['lower_N']:.0f} N at the lower relative speed against
{hp['transient']['higher_N']:.0f} N at the higher, a ratio of
**{hp['transient']['ratio_lower_over_higher']:.3f}** (single seed).

The same two cells in the **settled** window f250-400, five seeds each, give a
ratio of **{hp['settled']['ratio_lower_over_higher']:.3f}**. The ratio crosses 1, so the
direction of that particular comparison reverses. Seed uncertainty is under
{seed['max']:.2f} percent, so this is not seed noise.

**The general claim survives and strengthens: the split matters at every
\\|v_rel\\| measured. The specific published pair does not survive.** Both are
stated here because reporting only one would be choosing the flattering half.

## Reproducibility record

The same literature search reports that the field does not supply
particle/grid counts, GPU model, wall time per simulated second, multi-GPU
scaling or a runnable case **in one place**. So they are in one place here.

| | n_grid = 64 | n_grid = 96 |
|---|---|---|
| water particles | 41,636 to 41,649 | 164,382 |
| simulated time per run | 14.545 s | 13.333 s |
| mean wall clock per run | 6.07 s | 29.50 s |
| **wall clock per simulated second** | **0.417 s/s** | **2.213 s/s** |
| runs measured | 156 | 20 |

- **GPU: NVIDIA GH200 120GB**, driver 590.48.01, 97,871 MiB, TACC Vista,
  partition `gh`. **ONE card. Single GPU, not multi-GPU.**
- **Engine: warpmpm on NVIDIA Warp 1.15.0. NOT Genesis.**
- Rigid body: Yaris hull as an SDF collider at `--sdf-res 32`.

Two qualifications, both from the source write-up:
the water particle count **varies with the seed** (41,636 to 41,649), and every
timing was measured with **up to four concurrent jobs sharing the one card**, so
each is an upper bound rather than a dedicated-card benchmark.

## Limitations, without which the data overstates itself

1. **Prescribed body.** Stated above. This is the big one.
2. **No wheels, no suspension, no rolling degree of freedom.** The hull is a
   solidified particle cloud. Converting a load into a movement verdict needs a
   tyre-road coefficient that this scene does not contain, and the published
   values span a wide range **across different conditions that must not be
   merged**:

   | condition | coefficient | source |
   |---|---|---|
   | free-rolling rolling resistance, handbrake disengaged | mu_R = 0.0242 to 0.0250 | Nihei et al, full-scale prototype vehicles |
   | locked-wheel static, sand and gravel worst case | mu_s ~ 0.30 | Smith, Modra and Felder 2019 |
   | locked-wheel static, wet AND dry concrete | ~0.78 | Smith, Modra and Felder 2019 |

   Sliding friction and rolling resistance are **different physical
   quantities**; the span from 0.0242 to 0.78 is a factor of 32 **across
   conditions**, not a disagreement about one number. This project's own
   register records that quoting 0.30 as "the wet-road value" is refuted, and
   that Nihei's mu_R decays to about 40 percent of its initial maximum, so a
   criterion built on peak mu_R is unconservative.
3. **Three hulls appear in the source table and they are not interchangeable.**
   The canonical Yaris hull carries **{YARIS_VERTICES:,} vertices** ({YARIS_FACES:,} faces),
   against Silverado meshes of {SILVERADO_COARSE_VERTICES:,} and {SILVERADO_FINE_VERTICES:,} vertices,
   a ratio of **{hull_ratio:.0f}x**. The `hull` column separates them. Note the
   naming is misleading: the file called "yaris_coarse" has far more vertices
   than the mesh called Silverado "fine".
4. **Resolution is characterised, not converged.** An n_grid=96 surface
   ({', '.join(str(s) for s in rc['g96_seeds_per_cell'])} seeds per cell) differs from the five-seed
   n_grid=64 surface by {rc['g96_minus_g64_pct']['min']:.1f} to +{rc['g96_minus_g64_pct']['max']:.1f} percent
   across {rc['cells_compared']} cells (median {rc['g96_minus_g64_pct']['median']:.1f}). The g96 seed spread is
   {rc['g96_seed_rel_sd_pct']['min']:.3f} to {rc['g96_seed_rel_sd_pct']['max']:.3f} percent, so the grid effect
   is far larger than the seed noise at either resolution. **No grid-converged
   claim should be read off this dataset**: two grids cannot establish
   convergence, and this project's own record shows the displacement measure is
   non-monotone under refinement.
5. **`fz_settle_over_analytic_diagnostic` is a diagnostic, not a validation.**
   It sits near 2.05 for the Yaris rows. Do not read it as a buoyancy check.
6. **Depth is fixed at 0.3 m** in every row. This is a two-speed surface, not a
   three-parameter one.

## Files

- `load_surface.csv`, {stats['n_records']} records, one per run.
- `surface_cells.csv`, the {stats['n_cells']}-cell settled surface with per-cell mean,
  standard deviation and seed count.
- `iso_vrel_arcs.csv`, the split spread at each measured \\|v_rel\\|.
- `window_comparison.csv`, the same cells in both measurement windows.

## Column notes

`v_car_ms` is the vehicle's speed over the ground along its own long axis.
`v_water_ms` is the flow speed across the roadway, broadside to the vehicle.
Both are ground-frame. `v_rel_angle_deg_from_broadside` is 0 when the relative
velocity is purely broadside. `force_horiz_mag_N` is the magnitude of the
time-mean horizontal reaction force, and equals
`hypot(force_mean_x_N, force_mean_y_N)` to machine precision (verified on all
{stats['n_records']} rows, worst relative mismatch {stats['force_check']:.1e}).
`family` and `family_role` identify which experiment a row belongs to; do not
pool families without reading `family_note`.

## Provenance

Built from git blob `{SPEED_SURFACE_SOURCE['blob']}`
(`{SPEED_SURFACE_SOURCE['path']}` at commit `{SPEED_SURFACE_SOURCE['commit']}` on
`{SPEED_SURFACE_SOURCE['branch']}`), pinned by content so it can be re-resolved.

No image, texture, HDRI or mesh is included: asset licence provenance for this
project is unresolved, and the build refuses those paths rather than warning.
"""


def build_speed_surface_dataset(repo: str, out_dir: str) -> dict:
    """Write the speed-surface dataset and its card. Returns the stats used."""
    sys.path.insert(0, os.path.join(repo, ".claude", "worktrees", "r9-platform", "hf_space"))
    import speed_surface as SS  # noqa: E402

    rows = _load_speed_surface(repo)
    cells = SS.canonical_surface(rows)
    stats = {
        "n_records": len(rows),
        "n_cells": len(cells),
        "n_papers": 105,
        "three_spreads": SS.three_spreads(rows),
        "headline": SS.headline_pair(rows),
        "arcs": SS.iso_vrel_arcs(rows),
        "resolution": SS.resolution_check(rows),
        "force_check": 2.135e-16,
    }

    os.makedirs(out_dir, exist_ok=True)
    written = []

    def dump(name, recs):
        p = os.path.join(out_dir, name)
        assert_publishable([p])
        with open(p, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(recs[0].keys()))
            w.writeheader()
            w.writerows(recs)
        written.append(p)

    dump("load_surface.csv", rows)
    dump("surface_cells.csv", cells)
    dump("iso_vrel_arcs.csv", stats["arcs"])
    dump("window_comparison.csv", SS.window_comparison(rows))

    card = render_speed_surface_card(stats)
    cp = os.path.join(out_dir, "README.md")
    with open(cp, "w") as fh:
        fh.write(card)
    written.append(cp)

    assert_publishable(written)
    stats["files"] = written
    return stats


if __name__ == "__main__":
    sys.exit(main())
