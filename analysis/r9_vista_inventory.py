#!/usr/bin/env python3
"""Inventory every metrics.csv under $WORK and classify it for COMPARABILITY
with the 17 canonical gated runs. Emits TSV to stdout. Pure stdlib, read-only,
login-node safe: it opens each file's header and its sibling summary.json and
nothing else."""
import csv, json, os, sys

ROOT = "/work/11603/jcerrell0629"
FIELDS = ["path", "tree", "n_cols", "n_rows", "has_vel", "has_npz",
          "frames", "grid", "mass", "depth", "velocity", "eta",
          "floor_friction", "hull", "pinned", "noforce"]

def header_and_rows(p):
    try:
        with open(p, newline="", errors="replace") as fh:
            r = csv.reader(fh)
            hdr = next(r, [])
            n = sum(1 for _ in r)
        return [h.strip() for h in hdr], n
    except Exception:
        return [], -1

def summ(d):
    for name in ("summary.json",):
        p = os.path.join(d, name)
        if os.path.exists(p):
            try:
                return json.load(open(p))
            except Exception:
                return {}
    return {}

out = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
out.writerow(FIELDS)
n = 0
for base, dirs, files in os.walk(ROOT):
    if "metrics.csv" not in files:
        continue
    p = os.path.join(base, "metrics.csv")
    rel = os.path.relpath(p, ROOT)
    hdr, rows = header_and_rows(p)
    s = summ(base)
    low = rel.lower()
    # Provenance flags taken from the PATH as well as the summary, because a
    # control's identity is often only in its directory name and a summary can
    # be absent (the crashed-arm case: metrics.csv written, summary.json not).
    pinned = any(k in low for k in ("pin_", "_pin", "pinned"))
    noforce = "noforce" in low or "no_force" in low
    hull = ""
    for k in ("hull_source", "vehicle", "vehicle_key", "hull"):
        if isinstance(s.get(k), str):
            hull = os.path.basename(s[k]); break
    if not hull:
        for k in ("rogue", "silverado", "sphere", "yaris"):
            if k in low: hull = k + "(path)"; break
    out.writerow([
        rel, rel.split("/")[0], len(hdr), rows,
        int("vx" in hdr and "vmag" in hdr),
        int(os.path.exists(os.path.join(base, "rollout.npz"))),
        s.get("frames", ""), s.get("n_grid", s.get("grid", "")),
        s.get("mass_kg", s.get("mass", "")),
        s.get("requested_depth_m", s.get("depth", "")),
        s.get("velocity_ms", s.get("velocity", "")),
        s.get("eta", ""), s.get("floor_friction", ""),
        hull, int(pinned), int(noforce),
    ])
    n += 1
print(f"# rows: {n}", file=sys.stderr)
