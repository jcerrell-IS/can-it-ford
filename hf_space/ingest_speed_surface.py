"""Ingest d17-moving's (v_car x v_water) load surface into the Space / dataset table.

WHY THIS FILE EXISTS
The Space shipped with `data/load_surface.csv` containing a header and ZERO data
rows, so it had a renderer and nothing to render. This builds the real table.

SOURCE, PINNED, NOT A LIVE PATH
The source is a git blob, addressed by content, not a working-tree file:

    data/r9_speed_surface.tsv  at  98d4d9d  on  claude/r9-moving-vehicle
    blob 36631462d01e2c85af035fa67ae923e4be1192ad

d17 was still running when this was written, so a live path would have moved
under us. Two further reasons to use the blob rather than the worktree copy:

  1. The worktree copy is CRLF and the blob is LF. Verified with cmp: first
     differing byte is 513, 012 against 015, and the size delta is exactly 163
     bytes, one per line. The DATA is identical; only the line endings differ.
     A naive split('\t') on the CRLF copy leaves a trailing '\r' on the last
     field of every row, which float() happens to tolerate and str() does not.
  2. A blob SHA can be re-resolved by anyone later. A worktree path cannot.

Pass --source to read some other file, and --expect-sha '' to skip the pin, but
both are deliberate overrides and both are recorded in the output manifest.

WHAT THE LABELS MEAN
Derived here from the data and CHECKED against d17's prose in
docs/R9_MOVING_VEHICLE_2026-08-19.md, which was written independently of this
script. Where the two agree that is corroboration from separate origins; where
this file states something d17 does not, it is marked DERIVED.

    c3full   20 cells, frames=60  discard=20   the TRANSIENT surface. This is
                                               d17's published R5 table.
    L2full   20 cells, frames=400 discard=250  the SETTLED surface. Present in
                                               the data, absent from the doc.
    U1s0..4  iso-|v_rel| arc, 5 seeds, settled, bc_per_frame forced to 2.
                                               The CANONICAL arc.
    L1s0..4  same arc and seeds, bc_per_frame on auto, so the -45 deg cell got
                                               1 application per frame. Superseded
                                               by U1s*, kept because the pair is
                                               what measures the effect (-1.07
                                               percent on that one cell, under
                                               0.01 percent on the other four).
    seed0..4 the same arc in the TRANSIENT window.
    c1ctrl   no-forcing control, v_car=0 and v_water=0, three fixed-seed repeats.
    c0wrongdt  trap-1 detector, wrench_dt_mode=substep, committed deliberately.
    c4ground / c4rest   the reference-frame test.
    fidC / fidF   MESH FIDELITY, and NOT THE SAME VEHICLE AS EVERYTHING ELSE.
                  These are Silverado hulls (analytic buoyancy 2529.5 N and
                  2476.0 N against the Yaris 4468.622 N). They must never be
                  averaged into a Yaris surface.
    L3res / c3res  the arc at n_grid=96.
    q_*      sign and quadrant checks, carrying negative velocities.
    f1/f2/f4g/f4r  placement and duration probes.

A CHECK THAT CANNOT FAIL IS NOT A CHECK
Every guard here distinguishes "measured zero" from "could not evaluate", and
says which. An empty result is an error, not a quiet success.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

REPO = "/Users/josie/can-it-ford"
# RE-PINNED. The first pin was blob 36631462 at commit 98d4d9d, 162 rows. d17
# then committed 159bf7d and the table grew to 348 rows, adding the five-seed
# surface (M1s*) that this dataset is now built around. Re-pin deliberately and
# re-run; do not let the pin drift silently.
SOURCE_BLOB = "9afb3c7433ccac366e7658ea5a8e4432cfea5bfc"
SOURCE_COMMIT = "498f1ad"
SOURCE_BRANCH = "claude/r9-moving-vehicle"
SOURCE_PATH = "data/r9_speed_surface.tsv"

# Analytic buoyancy is the hull discriminator. It is a function of displaced
# volume, so it separates meshes that no column in the TSV names. Values read
# from the data; the vehicle NAMES come from d17 R9, which states the fidC/fidF
# pair are Silverado hulls 23x apart in vertex count.
HULL_BY_BUOYANCY = {
    4468.622: "yaris_coarse_v1l_watertight",
    2529.508: "silverado_coarse_2108v",
    2476.005: "silverado_fine_48706v",
}

# Windows, keyed by (frames, discard) exactly as recorded.
WINDOWS = {
    ("60", "20"): "transient_f20_60",
    ("400", "250"): "settled_f250_400",
}

FAMILY_ROLE = {
    "M1s": ("surface", "settled 20-cell surface, FIVE SEEDS, g64, THE CANONICAL SURFACE"),
    "M2s": ("surface", "settled 20-cell surface at n_grid=96, resolution check"),
    "M3m": ("arc", "iso-|v_rel| arc at a stated magnitude, nine splits, settled"),
    "M4c": ("cell", "single surface cell repeated over five seeds, settled"),
    "c3full": ("surface", "transient surface, published as d17 R5"),
    "L2full": ("surface", "settled surface, single seed, absent from d17's doc"),
    "U1s": ("arc", "iso-|v_rel| arc, settled, bc_per_frame uniform, CANONICAL"),
    "L1s": ("arc", "iso-|v_rel| arc, settled, bc_per_frame auto, superseded by U1s"),
    "seed": ("arc", "iso-|v_rel| arc, transient window"),
    "c2arc": ("arc", "iso-|v_rel| arc, transient, single draw"),
    "L3res": ("arc", "iso-|v_rel| arc at n_grid=96, settled"),
    "c3res": ("arc", "iso-|v_rel| arc at n_grid=96, transient"),
    "c1ctrl": ("control", "no-forcing gate, v_car=0 and v_water=0, fixed-seed repeats"),
    "c0wrongdt": ("control", "trap-1 detector, wrench_dt_mode=substep, deliberate"),
    "c4ground": ("control", "reference-frame test, ground frame"),
    "c4rest": ("control", "reference-frame test, vehicle-rest frame"),
    "fidC": ("fidelity", "SILVERADO coarse mesh, NOT the Yaris"),
    "fidF": ("fidelity", "SILVERADO fine mesh, NOT the Yaris"),
    "f1": ("probe", "hull placement along y"),
    "f2": ("probe", "long-duration probe"),
    "f4g": ("probe", "ground-frame speed probe"),
    "f4r": ("probe", "rest-frame speed probe"),
    "q": ("probe", "sign and quadrant check, negative velocities"),
}

OUT_COLUMNS = [
    "record_id", "family", "family_role", "family_note",
    "hull", "reference_frame", "window", "frames", "discard",
    "seed_index", "n_grid", "dx_m", "depth_m", "depth_cells",
    "v_car_ms", "v_water_ms", "v_rel_mag_ms", "v_rel_angle_deg_from_broadside",
    "force_horiz_mag_N", "force_mean_x_N", "force_mean_y_N", "force_mean_z_N",
    "torque_note",
    "fz_settle_N", "f_buoy_analytic_N", "fz_settle_over_analytic_diagnostic",
    "stream_established_frac", "bc_per_frame", "bc_per_frame_auto",
    "wrench_dt_mode", "n_water", "water_layers", "substeps_effective",
    "engine", "body_is_free", "verdict_reportable",
]

TORQUE_NOTE = "torque is about the collider centre, not the CG; not carried in this table"


class IngestError(RuntimeError):
    """Raised when the ingest cannot evaluate, as distinct from finding nothing."""


def read_source(source: str | None, expect_sha: str | None) -> tuple[str, dict]:
    """Return (text, provenance). Raises IngestError rather than returning empty."""
    prov: dict = {}
    if source:
        if not os.path.exists(source):
            raise IngestError(f"--source given but does not exist: {source}")
        with open(source, "r", newline="") as fh:
            text = fh.read()
        prov = {"mode": "file", "path": source,
                "note": "OVERRIDE: not the pinned blob"}
    else:
        cmd = ["git", "-C", REPO, "cat-file", "-p", SOURCE_BLOB]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise IngestError(
                f"could not read pinned blob {SOURCE_BLOB}: {proc.stderr.strip()}")
        text = proc.stdout
        prov = {"mode": "git-blob", "repo": REPO, "blob": SOURCE_BLOB,
                "commit": SOURCE_COMMIT, "branch": SOURCE_BRANCH,
                "path": SOURCE_PATH}

    if not text.strip():
        raise IngestError("source read but is empty; that is a failure, not zero rows")

    sha = hashlib.sha256(text.encode()).hexdigest()
    prov["sha256_of_text"] = sha
    prov["crlf"] = "\r\n" in text
    if expect_sha:
        if sha != expect_sha:
            raise IngestError(
                f"source sha256 {sha} does not match --expect-sha {expect_sha}")
        prov["sha_pinned"] = True
    else:
        prov["sha_pinned"] = False
    return text, prov


def parse_rows(text: str) -> list[dict]:
    # splitlines() handles LF and CRLF alike, so a CRLF source cannot leave a
    # stray carriage return on the last field.
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < 2:
        raise IngestError(f"source has {len(lines)} non-empty lines, need header + data")
    header = lines[0].split("\t")
    rows = []
    for i, ln in enumerate(lines[1:], start=2):
        parts = ln.split("\t")
        if len(parts) != len(header):
            raise IngestError(
                f"line {i} has {len(parts)} fields, header has {len(header)}")
        rows.append(dict(zip(header, parts)))
    return rows


def _f(row: dict, key: str):
    v = row.get(key, "")
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


PREFIXES = ("U1s", "L1s", "seed", "M1s", "M2s", "M3m", "M4c")


def family_role(label: str) -> tuple[str, str]:
    if label in FAMILY_ROLE:
        return FAMILY_ROLE[label]
    for prefix in PREFIXES:
        if label.startswith(prefix):
            return FAMILY_ROLE[prefix]
    return ("unclassified", "no role assigned by the ingest")


def seed_index(label: str):
    """Seed index where the family name encodes one, else None.

    M3m carries a |v_rel| MAGNITUDE, not a seed, so it must return None. A
    label like M3m3.0 would otherwise parse a '3' out of the middle and
    fabricate a seed that does not exist.
    """
    if label.startswith("M3m"):
        return None
    if label.startswith("M4c"):
        # M4c{cell}s{seed}
        tail = label[3:]
        if "s" in tail:
            seed = tail.split("s", 1)[1]
            if seed.isdigit():
                return int(seed)
        return None
    for prefix in ("U1s", "L1s", "seed", "M1s", "M2s"):
        if label.startswith(prefix):
            tail = label[len(prefix):]
            if tail.isdigit():
                return int(tail)
    return None


def hull_of(row: dict) -> str:
    fb = _f(row, "f_buoy_analytic_N")
    if fb is None:
        return "UNKNOWN, f_buoy_analytic_N absent"
    for known, name in HULL_BY_BUOYANCY.items():
        if abs(fb - known) < 0.01:
            return name
    return f"UNKNOWN, f_buoy_analytic_N={fb}"


def window_of(row: dict) -> str:
    key = (row.get("frames", ""), row.get("discard", ""))
    if key in WINDOWS:
        return WINDOWS[key]
    return f"other_f{key[0]}_d{key[1]}"


def transform(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        if r.get("status") != "OK":
            continue
        role, note = family_role(r["label"])
        rec = {
            "record_id": r["tag"],
            "family": r["label"],
            "family_role": role,
            "family_note": note,
            "hull": hull_of(r),
            "reference_frame": r.get("frame", ""),
            "window": window_of(r),
            "frames": r.get("frames", ""),
            "discard": r.get("discard", ""),
            "seed_index": seed_index(r["label"]),
            "n_grid": r.get("n_grid", ""),
            "dx_m": r.get("dx_m", ""),
            "depth_m": r.get("depth_m", ""),
            "depth_cells": r.get("depth_cells", ""),
            "v_car_ms": r.get("v_car_ms", ""),
            "v_water_ms": r.get("v_water_ms", ""),
            "v_rel_mag_ms": r.get("v_rel_mag_ms", ""),
            "v_rel_angle_deg_from_broadside": r.get("v_rel_angle_deg_from_broadside", ""),
            "force_horiz_mag_N": r.get("force_horiz_mag_N", ""),
            "force_mean_x_N": r.get("force_mean_x_N", ""),
            "force_mean_y_N": r.get("force_mean_y_N", ""),
            "force_mean_z_N": r.get("force_mean_z_N", ""),
            "torque_note": TORQUE_NOTE,
            "fz_settle_N": r.get("fz_settle_N", ""),
            "f_buoy_analytic_N": r.get("f_buoy_analytic_N", ""),
            "fz_settle_over_analytic_diagnostic": r.get("fz_settle_over_analytic", ""),
            "stream_established_frac": r.get("stream_established_frac", ""),
            "bc_per_frame": r.get("bc_per_frame", ""),
            "bc_per_frame_auto": r.get("bc_per_frame_auto", ""),
            "wrench_dt_mode": r.get("wrench_dt_mode", ""),
            "n_water": r.get("n_water", ""),
            "water_layers": r.get("water_layers", ""),
            "substeps_effective": r.get("substeps_effective", ""),
            "engine": "warpmpm",
            "body_is_free": "no, prescribed SDF collider",
            "verdict_reportable": "no FORD or NO-FORD verdict is reportable",
        }
        out.append(rec)
    if not out:
        raise IngestError("transform produced zero records; refusing to write an empty table")
    return out


def check_force_consistency(rows: list[dict]) -> tuple[int, float]:
    """|F_horiz| must be hypot(mean Fx, mean Fy). Returns (n_checked, worst_rel)."""
    n, worst = 0, 0.0
    for r in rows:
        fx, fy = _f(r, "force_mean_x_N"), _f(r, "force_mean_y_N")
        fh = _f(r, "force_horiz_mag_N")
        if fx is None or fy is None or fh is None or fh == 0.0:
            continue
        n += 1
        worst = max(worst, abs(math.hypot(fx, fy) - fh) / abs(fh))
    if n == 0:
        raise IngestError("force consistency check evaluated ZERO rows; it could not fire")
    return n, worst


def write_table(recs: list[dict], prov: dict, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "load_surface.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLUMNS)
        w.writeheader()
        for rec in recs:
            w.writerow({k: ("" if rec.get(k) is None else rec.get(k)) for k in OUT_COLUMNS})

    n_checked, worst = check_force_consistency(recs)
    manifest = {
        "source": prov,
        "records": len(recs),
        "families": sorted({r["family"] for r in recs}),
        "windows": sorted({r["window"] for r in recs}),
        "hulls": sorted({r["hull"] for r in recs}),
        "force_magnitude_consistency": {
            "rows_checked": n_checked,
            "worst_relative_mismatch": worst,
            "meaning": "force_horiz_mag_N vs hypot(force_mean_x_N, force_mean_y_N)",
        },
        "engine": "warpmpm",
        "not_claimed": [
            "no FORD or NO-FORD verdict; the body is prescribed and cannot be swept away",
            "torque in the source is about the collider centre, not the CG",
            "fz_settle_over_analytic is a diagnostic, not a buoyancy validation",
        ],
    }
    mpath = os.path.join(out_dir, "load_surface_manifest.json")
    with open(mpath, "w") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    return manifest


def self_test() -> int:
    """Checks that would FAIL if the ingest were broken. Not a smoke test."""
    failures = []

    # 1. window_of must not silently bucket an unknown window as a known one.
    got = window_of({"frames": "999", "discard": "1"})
    if got != "other_f999_d1":
        failures.append(f"window_of unknown -> {got!r}, expected other_f999_d1")

    # 2. hull_of must refuse to name a hull it cannot identify.
    got = hull_of({"f_buoy_analytic_N": "1234.5"})
    if not got.startswith("UNKNOWN"):
        failures.append(f"hull_of unknown buoyancy -> {got!r}, expected UNKNOWN")
    got = hull_of({"f_buoy_analytic_N": ""})
    if not got.startswith("UNKNOWN"):
        failures.append(f"hull_of missing buoyancy -> {got!r}, expected UNKNOWN")

    # 3. seed_index must not invent an index for a non-seed family. M3m3.0 is
    #    the trap: it carries a |v_rel| magnitude and a naive digit scan
    #    fabricates seed 3 from it.
    for lab, want in [("U1s3", 3), ("L1s0", 0), ("seed4", 4),
                      ("M1s2", 2), ("M2s0", 0), ("M4c3s1", 1),
                      ("M3m3.0", None), ("M3m4.5", None),
                      ("c3full", None), ("L2full", None), ("fidC", None)]:
        if seed_index(lab) != want:
            failures.append(f"seed_index({lab}) -> {seed_index(lab)}, expected {want}")

    # 3b. Every family prefix must resolve to a role, or new data lands as
    #     "unclassified" and nobody notices.
    for lab in ("M1s0", "M2s0", "M3m6.0", "M4c4s4", "U1s1", "seed0"):
        role, _ = family_role(lab)
        if role == "unclassified":
            failures.append(f"family_role({lab}) is unclassified")

    # 4. The empty-result guard must actually raise, not return [].
    try:
        transform([{"status": "FAILED", "label": "x", "tag": "t"}])
        failures.append("transform([]) returned instead of raising IngestError")
    except IngestError:
        pass

    # 5. The consistency check must raise when it cannot fire, rather than
    #    reporting a perfect score from zero rows. This is the defect that
    #    makes an error path indistinguishable from a pass.
    try:
        check_force_consistency([{"force_mean_x_N": "", "force_mean_y_N": "",
                                  "force_horiz_mag_N": ""}])
        failures.append("check_force_consistency on 0 usable rows did not raise")
    except IngestError:
        pass

    # 6. A CRLF source must parse to the same values as an LF source.
    lf = "a\tb\n1\t2\n"
    crlf = "a\tb\r\n1\t2\r\n"
    if parse_rows(lf) != parse_rows(crlf):
        failures.append("CRLF and LF sources parse differently")

    for f in failures:
        print(f"  FAIL {f}")
    print(f"self_test: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--source", default=None,
                    help="override the pinned blob with a file (recorded in the manifest)")
    ap.add_argument("--expect-sha", default=None,
                    help="require this sha256 of the source text")
    ap.add_argument("--out", default=DATA_DIR)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    try:
        text, prov = read_source(args.source, args.expect_sha)
        rows = parse_rows(text)
        recs = transform(rows)
        manifest = write_table(recs, prov, args.out)
    except IngestError as exc:
        print(f"INGEST FAILED (could not evaluate): {exc}", file=sys.stderr)
        return 2

    print(f"wrote {manifest['records']} records to {args.out}/load_surface.csv")
    print(f"  source     {prov.get('mode')} {prov.get('blob', prov.get('path'))}")
    print(f"  sha256     {prov['sha256_of_text'][:16]}...  crlf={prov['crlf']}")
    print(f"  families   {len(manifest['families'])}")
    print(f"  windows    {manifest['windows']}")
    print(f"  hulls      {manifest['hulls']}")
    c = manifest["force_magnitude_consistency"]
    print(f"  |F| check  {c['rows_checked']} rows, worst rel mismatch {c['worst_relative_mismatch']:.3e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
