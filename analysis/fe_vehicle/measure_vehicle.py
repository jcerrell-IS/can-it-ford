#!/usr/bin/env python3
"""Wheelbase, track, tire radius and ground clearance from a converted NHTSA OBJ.

Wheels are found by name-classification and then clustered by which quadrant of
the vehicle they sit in, so this works across NCAC naming vocabularies rather
than being tuned to one model.
"""
import sys, re
from collections import defaultdict

TIREY   = re.compile(r'(tire|tyre)', re.I)
NOTTIRE = re.compile(r'(rim|mount|wheelwell|hub|disk|carrier|brkt|spare)', re.I)
SKIPLOW = ("tire", "tyre", "rim", "hub", "disk", "wheel")

def load(obj):
    verts, cur, ov = [], None, defaultdict(set)
    for line in open(obj):
        if line.startswith('v '):
            verts.append(tuple(float(x) for x in line.split()[1:4]))
        elif line.startswith('o '):
            cur = line[2:].strip()
        elif line.startswith('f ') and cur:
            for tok in line.split()[1:]:
                ov[cur].add(int(tok.split('/')[0]) - 1)
    return verts, ov

def main(obj, name):
    verts, ov = load(obj)
    xs = [p[0] for p in verts]; ys = [p[1] for p in verts]; zs = [p[2] for p in verts]
    mx, my = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2

    quad = defaultdict(list)
    for n, idx in ov.items():
        if not (TIREY.search(n) and not NOTTIRE.search(n)):
            continue
        pts = [verts[i] for i in idx]
        cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
        quad[(cx > mx, cy > my)].append((cx, cy, pts))

    cent = {}
    for k, group in quad.items():
        allp = [p for _, _, pts in group for p in pts]
        cent[k] = (sum(p[0] for p in allp)/len(allp),
                   sum(p[1] for p in allp)/len(allp),
                   (max(p[2] for p in allp) - min(p[2] for p in allp)) / 2)

    print(f"### {name}")
    print(f"parts_with_faces  {len(ov)}")
    print(f"overall L W H     {max(xs)-min(xs):.4f} x {max(ys)-min(ys):.4f} x {max(zs)-min(zs):.4f} m")
    print(f"wheel clusters    {len(cent)}")
    if len(cent) == 4:
        fx = [c[0] for k, c in cent.items() if k[0]]
        rx = [c[0] for k, c in cent.items() if not k[0]]
        wb = abs(sum(fx)/len(fx) - sum(rx)/len(rx))
        trf = abs(cent[(True, True)][1] - cent[(True, False)][1])
        trr = abs(cent[(False, True)][1] - cent[(False, False)][1])
        rad = sum(c[2] for c in cent.values())/4
        print(f"wheelbase         {wb:.4f} m")
        print(f"track front/rear  {trf:.4f} / {trr:.4f} m")
        print(f"tire radius       {rad:.4f} m  (diameter {2*rad:.4f} m)")
        lo_x, hi_x = min(min(fx), min(rx)), max(max(fx), max(rx))
    else:
        print("  wheel clustering incomplete, clearance measured over the middle 60% of length")
        span = max(xs) - min(xs)
        lo_x, hi_x = min(xs) + 0.2*span, max(xs) - 0.2*span

    best = (1e9, None)
    for n, idx in ov.items():
        if any(t in n.lower() for t in SKIPLOW):
            continue
        for i in idx:
            x, y, z = verts[i]
            if lo_x < x < hi_x and z < best[0]:
                best = (z, n)
    print(f"ground clearance  {best[0]:.4f} m ({best[0]*1000:.1f} mm)  lowest: {best[1]}")
    print()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
