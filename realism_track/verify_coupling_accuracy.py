from __future__ import annotations

import argparse
import glob
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIXED_SDF_KEYS = ("err_steady_vs_analytic_pct", "err_first3_vs_analytic_pct")
FREE_RIGID_KEYS = ("err_F_pct", "err_headline_vs_ideal_pct")


def load(pattern):
    out = []
    for path in sorted(glob.glob(os.path.join(REPO_ROOT, pattern), recursive=True)):
        try:
            with open(path) as fh:
                doc = json.load(fh)
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict):
            out.append((os.path.relpath(path, REPO_ROOT), doc))
    return out


def num(value):
    return isinstance(value, (int, float)) and value == value


def collect(docs):
    fixed, free = [], []
    for rel, doc in docs:
        variant = str(doc.get("variant", ""))
        geom = doc.get("geometry") or {}
        n_grid = geom.get("n_grid")
        collider = doc.get("collider_kind")
        row = {"file": rel, "variant": variant, "n_grid": n_grid, "collider": collider}
        if any(num(doc.get(k)) for k in FIXED_SDF_KEYS):
            row = dict(row, **{k: doc.get(k) for k in FIXED_SDF_KEYS})
            fixed.append(row)
        elif any(num(doc.get(k)) for k in FREE_RIGID_KEYS):
            row = dict(row, **{k: doc.get(k) for k in FREE_RIGID_KEYS})
            free.append(row)
    return fixed, free


def fmt(value):
    return f"{value:9.2f}" if num(value) else f"{'-':>9s}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="data/coupling_validation*/**/*.json")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    docs = load(args.glob)
    if not docs:
        print(f"no manifests matched {args.glob}", file=sys.stderr)
        return 1
    fixed, free = collect(docs)

    print(f"manifests parsed: {len(docs)}")

    print("\nFIXED SDF / BOX COLLIDER, force vs analytic buoyancy (percent error)")
    print(f"{'file':44s} {'grid':>5s} {'collider':>9s} {'steady':>9s} {'first3':>9s}")
    for r in sorted(fixed, key=lambda r: (str(r.get("collider")), r.get("n_grid") or 0)):
        print(f"{r['file'].replace('data/', ''):44s} {str(r['n_grid']):>5s} "
              f"{str(r['collider']):>9s} {fmt(r.get(FIXED_SDF_KEYS[0]))} "
              f"{fmt(r.get(FIXED_SDF_KEYS[1]))}")

    print("\nFREE-RIGID (material-8) PATH, force error (percent)")
    print(f"{'file':44s} {'grid':>5s} {'err_F_pct':>9s} {'headline':>9s}")
    for r in sorted(free, key=lambda r: (r.get("n_grid") or 0, r["file"])):
        print(f"{r['file'].replace('data/', ''):44s} {str(r['n_grid']):>5s} "
              f"{fmt(r.get(FREE_RIGID_KEYS[0]))} {fmt(r.get(FREE_RIGID_KEYS[1]))}")

    sdf = [r for r in fixed if str(r.get("collider")) == "sdf"
           and num(r.get(FIXED_SDF_KEYS[0]))]
    box = [r for r in fixed if str(r.get("collider")) == "box"
           and num(r.get(FIXED_SDF_KEYS[0]))]
    freev = [r for r in free if num(r.get(FREE_RIGID_KEYS[0]))]

    print("\nSUMMARY, absolute steady-state error vs analytic buoyancy")
    for label, rows, key in (("fixed SDF collider", sdf, FIXED_SDF_KEYS[0]),
                             ("fixed box collider", box, FIXED_SDF_KEYS[0]),
                             ("free-rigid material-8", freev, FREE_RIGID_KEYS[0])):
        if not rows:
            print(f"  {label:24s} no usable runs")
            continue
        mags = [abs(r[key]) for r in rows]
        print(f"  {label:24s} n={len(rows)}  |err| min={min(mags):.2f}%  "
              f"max={max(mags):.2f}%")

    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump({"fixed_collider": fixed, "free_rigid": free}, fh, indent=2)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
