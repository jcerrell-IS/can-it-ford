#!/usr/bin/env python3
"""Summarise a directory of run summary.json files into per-cell mean +/- sd.

Reports the KINEMATIC free-surface observables and the COUPLED-BODY observables
side by side, because MERGED_RESEARCH_READER_CORPUS_FINAL.md section 6.5 turns
on exactly that distinction: Zhao, Liang and Martinelli 2017 measured a flow
front and this project measures a rigid body, and the paper does not license
carrying its convergence across.
"""
import json, sys, os, re, math
from collections import defaultdict

KIN = ["local_depth_bow_peak", "local_depth_footprint_peak"]
BODY = ["final_disp_mag_m", "passthrough_max_frac", "C2_veh_zmin_rise",
        "final_roll_deg", "realized_rho", "dx", "water_layers", "hull_m3"]


def load(root):
    out = {}
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d, "summary.json")
        if os.path.isfile(p):
            try:
                out[d] = json.load(open(p))
            except Exception:
                pass
    return out


def stat(vals):
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan"), 0
    m = sum(vals) / n
    if n < 2:
        return m, 0.0, n
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (n - 1))
    return m, sd, n


def main():
    root = sys.argv[1]
    # cell key = label with the trailing repeat index stripped
    pat = re.compile(r"^(.*?)_?r?(\d+)$")
    cells = defaultdict(list)
    for label, s in load(root).items():
        m = pat.match(label)
        key = m.group(1) if m else label
        cells[key].append(s)
    cols = KIN + BODY
    print("%-22s %4s " % ("cell", "n") + " ".join("%22s" % c[:22] for c in cols))
    for key in sorted(cells):
        runs = cells[key]
        row = []
        for c in cols:
            vals = [r[c] for r in runs if isinstance(r.get(c), (int, float))]
            mu, sd, n = stat(vals)
            row.append("%11.6f+-%9.6f" % (mu, sd) if n else "%22s" % "-")
        print("%-22s %4d " % (key, len(runs)) + " ".join(row))


if __name__ == "__main__":
    main()
