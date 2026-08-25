#!/usr/bin/env python3
"""
Convert an NCAC/CCSA LS-DYNA vehicle keyword file into a Wavefront OBJ,
one OBJ object per *PART, so Blender imports the vehicle as separate,
named components.

Reads:  *NODE, *PART, *ELEMENT_SHELL, *ELEMENT_SOLID
Skips:  *ELEMENT_BEAM, *ELEMENT_DISCRETE, *ELEMENT_MASS  (no surface area)

LS-DYNA fixed-width fields are used, not whitespace splitting, because the
format defines them that way and a blank field is legal (nodes may be
declared with an id and no coordinates).

Units: NCAC vehicle models are in millimetres. Output is metres.
"""
import sys, os, re, time
from collections import defaultdict

MM_TO_M = 0.001

def fw(line, start, width):
    return line[start:start + width].strip()

def parse_key(path):
    nodes = {}                      # nid -> (x, y, z) in metres
    part_title = {}                 # pid -> title
    shells = defaultdict(list)      # pid -> [ (n1,n2,n3,n4), ... ]
    solids = defaultdict(list)      # pid -> [ (n1..n8), ... ]

    kw = None
    part_stage = 0                  # 0 = expecting title, 1 = expecting pid line
    pending_title = None

    with open(path, 'r', errors='replace') as fh:
        for line in fh:
            if not line or line[0] == '$':
                continue
            if line[0] == '*':
                kw = line.strip().upper()
                if kw == '*PART':
                    part_stage = 0
                    pending_title = None
                continue

            if kw == '*NODE':
                nid = fw(line, 0, 8)
                if not nid:
                    continue
                x = fw(line, 8, 16) or '0'
                y = fw(line, 24, 16) or '0'
                z = fw(line, 40, 16) or '0'
                try:
                    nodes[int(nid)] = (float(x) * MM_TO_M,
                                       float(y) * MM_TO_M,
                                       float(z) * MM_TO_M)
                except ValueError:
                    continue

            elif kw == '*ELEMENT_SHELL':
                pid = fw(line, 8, 8)
                if not pid:
                    continue
                try:
                    n = [int(fw(line, 16 + 8 * i, 8) or 0) for i in range(4)]
                    shells[int(pid)].append(tuple(n))
                except ValueError:
                    continue

            elif kw == '*ELEMENT_SOLID':
                pid = fw(line, 8, 8)
                if not pid:
                    continue
                try:
                    n = [int(fw(line, 16 + 8 * i, 8) or 0) for i in range(8)]
                    solids[int(pid)].append(tuple(n))
                except ValueError:
                    continue

            elif kw == '*PART':
                if part_stage == 0:
                    pending_title = line.rstrip('\n').strip()
                    part_stage = 1
                elif part_stage == 1:
                    pid = fw(line, 0, 10)
                    if pid:
                        try:
                            part_title[int(pid)] = pending_title or ''
                        except ValueError:
                            pass
                    part_stage = 2

    return nodes, part_title, shells, solids

# The 6 faces of an LS-DYNA hexahedron, outward winding.
HEX_FACES = ((0,1,2,3), (4,7,6,5), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0))

def solid_skin(elements):
    """Return only the hex faces that appear once: the outer surface."""
    seen = {}
    for e in elements:
        for f in HEX_FACES:
            face = tuple(e[i] for i in f)
            key = tuple(sorted(face))
            if key in seen:
                seen[key] = None
            else:
                seen[key] = face
    return [f for f in seen.values() if f is not None]

def clean_face(face):
    """Drop repeated node ids (collapsed quads become triangles)."""
    out = []
    for n in face:
        if n and n not in out:
            out.append(n)
    return out if len(out) >= 3 else None

SAFE = re.compile(r'[^A-Za-z0-9_.-]+')

def main(key_path, obj_path, model_name):
    t0 = time.time()
    nodes, part_title, shells, solids = parse_key(key_path)
    print(f"parsed  {len(nodes):,} nodes  {len(part_title):,} parts  "
          f"{sum(len(v) for v in shells.values()):,} shells  "
          f"{sum(len(v) for v in solids.values()):,} solids  "
          f"({time.time() - t0:.1f}s)")

    pids = sorted(set(shells) | set(solids))

    # Collect faces per part first, so we only emit vertices actually used.
    faces_by_pid = {}
    used = set()
    for pid in pids:
        faces = []
        for e in shells.get(pid, ()):
            f = clean_face(e)
            if f:
                faces.append(f)
        if pid in solids:
            for e in solid_skin(solids[pid]):
                f = clean_face(e)
                if f:
                    faces.append(f)
        faces = [f for f in faces if all(n in nodes for n in f)]
        if faces:
            faces_by_pid[pid] = faces
            for f in faces:
                used.update(f)

    order = sorted(used)
    index = {nid: i + 1 for i, nid in enumerate(order)}   # OBJ is 1-based

    nf = sum(len(v) for v in faces_by_pid.values())
    xs = [nodes[n][0] for n in order]
    ys = [nodes[n][1] for n in order]
    zs = [nodes[n][2] for n in order]

    os.makedirs(os.path.dirname(obj_path), exist_ok=True)
    with open(obj_path, 'w') as out:
        out.write(f"# {model_name}\n# converted from {os.path.basename(key_path)}\n")
        out.write(f"# {len(order)} vertices, {nf} faces, {len(faces_by_pid)} parts, metres\n")
        for nid in order:
            x, y, z = nodes[nid]
            out.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
        for pid in sorted(faces_by_pid):
            title = part_title.get(pid, '')
            name = SAFE.sub('_', f"{pid}_{title}")[:63] or str(pid)
            out.write(f"o {name}\ng {name}\n")
            for f in faces_by_pid[pid]:
                out.write("f " + " ".join(str(index[n]) for n in f) + "\n")

    print(f"wrote   {obj_path}")
    print(f"        {len(order):,} vertices, {nf:,} faces, {len(faces_by_pid):,} objects")
    print(f"bbox_m  x {min(xs):8.3f} .. {max(xs):8.3f}  span {max(xs)-min(xs):.3f}")
    print(f"        y {min(ys):8.3f} .. {max(ys):8.3f}  span {max(ys)-min(ys):.3f}")
    print(f"        z {min(zs):8.3f} .. {max(zs):8.3f}  span {max(zs)-min(zs):.3f}")
    print(f"total   {time.time() - t0:.1f}s")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'vehicle')
