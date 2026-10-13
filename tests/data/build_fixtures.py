#!/usr/bin/env python3
"""Rebuild the small test fixtures in tests/data/ from the full run outputs.

The full outputs are not in this repository (each particle rollout is 23 to 232 MB). This script
copies or summarizes the parts the tests need, so CI can run the data tests on a clean checkout:

    runs/<run>/metrics.csv        byte-for-byte copy of each of the 17 gated runs' per-frame record
    rollout_shapes.json           array shapes read from the .npy headers inside each rollout.npz
    stage1e_matched_window.json   grid spacing, mean streamwise force and its standard error for the
                                  three Stage 1e grid levels (the drag coefficients are left out on
                                  purpose: none of them is valid, see the steady-force dataset card)
    SHA256SUMS                    hashes of every source file read and every fixture written

Usage
    python3 tests/data/build_fixtures.py --runs <dir holding the 17 run folders> \
        --stage1e <path to stage1e_data.json>

Standard library only.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
INVENTORY = os.path.join(REPO, "data", "all_runs_inventory.csv")
STAGE1E_RUNS = ("Pf_d030_u150_W20_dx0375_fo005_t30", "Pf_d030_u150_W20_dx050_fo005",
                "Pf_d030_u150_W20_dx075_fo005")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def npz_shapes(path: str) -> dict[str, list[int]]:
    """Shapes of every array in an .npz, read from the .npy headers without loading the data."""
    out = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.endswith(".npy"):
                continue
            with z.open(name) as f:
                if f.read(6) != b"\x93NUMPY":
                    continue
                major = f.read(2)[0]
                hlen = int.from_bytes(f.read(2 if major == 1 else 4), "little")
                hdr = ast.literal_eval(f.read(hlen).decode("latin1").strip())
                out[name[:-4]] = list(hdr["shape"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Rebuild the small test fixtures in tests/data/.")
    ap.add_argument("--runs", required=True, help="directory holding one folder per gated run")
    ap.add_argument("--stage1e", required=True, help="path to stage1e_data.json")
    a = ap.parse_args()

    with open(INVENTORY, newline="", encoding="utf-8") as fh:
        runs = sorted(r["run"] for r in csv.DictReader(fh))
    sums: list[tuple[str, str]] = []
    shapes = {}
    for run in runs:
        src_dir = os.path.join(a.runs, run)
        src = os.path.join(src_dir, "metrics.csv")
        dst_dir = os.path.join(HERE, "runs", run)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, "metrics.csv")
        shutil.copyfile(src, dst)
        if sha256(src) != sha256(dst):
            print("copy mismatch:", run, file=sys.stderr)
            return 1
        sums.append((sha256(dst), "runs/%s/metrics.csv" % run))
        rollout = os.path.join(src_dir, "rollout.npz")
        shapes[run] = {"source_sha256": sha256(rollout), "arrays": npz_shapes(rollout)}

    out = os.path.join(HERE, "rollout_shapes.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(shapes, fh, indent=1, sort_keys=True)
        fh.write("\n")
    sums.append((sha256(out), "rollout_shapes.json"))

    with open(a.stage1e, encoding="utf-8") as fh:
        d = json.load(fh)
    s1e = {"source_sha256": sha256(a.stage1e), "runs": {}}
    for run in STAGE1E_RUNS:
        mw = d[run]["matched_window"]
        s1e["runs"][run] = {"dx": d[run]["dx"], "Fx": mw["Fx"], "Fx_se_eff": mw["Fx_se_eff"]}
    out = os.path.join(HERE, "stage1e_matched_window.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(s1e, fh, indent=1, sort_keys=True)
        fh.write("\n")
    sums.append((sha256(out), "stage1e_matched_window.json"))

    with open(os.path.join(HERE, "SHA256SUMS"), "w", encoding="utf-8") as fh:
        for h, name in sums:
            fh.write("%s  %s\n" % (h, name))
    print("wrote %d run records, rollout_shapes.json, stage1e_matched_window.json, SHA256SUMS" % len(runs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
