#!/usr/bin/env python3
"""
Compute rigid-body mass properties directly from an NCAC/CCSA LS-DYNA model:
total mass, centre of gravity, and the inertia tensor about the CG.

Method: LS-DYNA's own lumped-mass convention. Each shell element contributes
area * thickness * density, each solid element volume * density, and that mass
is split equally over the element's nodes. CG and inertia then follow from the
nodal point masses.

Unit system of these models is (mm, tonne, s), so density in the key file is
tonne/mm^3. 7.89e-9 tonne/mm^3 = 7890 kg/m^3, which is steel, and that is the
check that the unit assumption is right.
"""
import sys, math
from collections import defaultdict

MM = 0.001
RO_TO_SI = 1.0e12          # tonne/mm^3 -> kg/m^3

def fw(l, s, w):
    return l[s:s + w].strip()

def parse(path):
    nodes, part, sect, mat = {}, {}, {}, {}
    shells, solids, lumped = [], [], []
    kw, stage, title = None, 0, None
    title_pending = False
    sec_id = mat_id = None
    sec_line = mat_line = 0

    with open(path, errors='replace') as fh:
        for line in fh:
            if not line or line[0] == '$':
                continue
            if line[0] == '*':
                kw = line.strip().upper()
                # LS-DYNA _TITLE variants insert one title line before the data
                # card. The Rogue uses 37 *SECTION_SHELL_TITLE and 19
                # *MAT_..._TITLE cards; matching the bare keyword only skipped
                # 172,574 elements and under-counted mass by 15 percent.
                title_pending = kw.endswith('_TITLE')
                if title_pending:
                    kw = kw[: -len('_TITLE')]
                stage = 0
                sec_line = mat_line = 0
                sec_id = mat_id = None
                continue

            if kw == '*NODE':
                nid = fw(line, 0, 8)
                if nid:
                    try:
                        nodes[int(nid)] = (float(fw(line, 8, 16) or 0) * MM,
                                           float(fw(line, 24, 16) or 0) * MM,
                                           float(fw(line, 40, 16) or 0) * MM)
                    except ValueError:
                        pass

            elif kw == '*ELEMENT_SHELL':
                try:
                    shells.append((int(fw(line, 8, 8)),
                                   [int(fw(line, 16 + 8 * i, 8) or 0) for i in range(4)]))
                except ValueError:
                    pass

            elif kw == '*ELEMENT_SOLID':
                try:
                    solids.append((int(fw(line, 8, 8)),
                                   [int(fw(line, 16 + 8 * i, 8) or 0) for i in range(8)]))
                except ValueError:
                    pass

            elif kw == '*ELEMENT_MASS':
                try:                       # eid, nid, mass(tonne), pid
                    lumped.append((int(fw(line, 8, 8)), float(fw(line, 16, 16) or 0) * 1000.0))
                except ValueError:
                    pass

            elif kw == '*PART':
                if stage == 0:
                    title = line.strip(); stage = 1
                elif stage == 1:
                    try:
                        pid = int(fw(line, 0, 10))
                        part[pid] = (int(fw(line, 10, 10) or 0),
                                     int(fw(line, 20, 10) or 0), title)
                    except ValueError:
                        pass
                    stage = 2

            elif kw == '*SECTION_SHELL':
                if title_pending:
                    title_pending = False
                    continue
                sec_line += 1
                if sec_line == 1:
                    try: sec_id = int(fw(line, 0, 10))
                    except ValueError: sec_id = None
                elif sec_line == 2 and sec_id is not None:
                    try: sect[sec_id] = float(fw(line, 0, 10) or 0) * MM
                    except ValueError: pass

            elif kw and kw.startswith('*MAT_'):
                if title_pending:
                    title_pending = False
                    continue
                mat_line += 1
                if mat_line == 1:
                    try:
                        mat[int(fw(line, 0, 10))] = float(fw(line, 10, 10) or 0) * RO_TO_SI
                    except ValueError:
                        pass
    return nodes, part, sect, mat, shells, solids, lumped

def tri_area(a, b, c):
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    cx = u[1]*v[2] - u[2]*v[1]
    cy = u[2]*v[0] - u[0]*v[2]
    cz = u[0]*v[1] - u[1]*v[0]
    return 0.5 * math.sqrt(cx*cx + cy*cy + cz*cz)

def hex_volume(p):
    # decompose the hexahedron into 5 tetrahedra
    tets = ((0,1,3,4),(1,2,3,6),(1,3,4,6),(3,4,6,7),(1,4,5,6))
    tot = 0.0
    for t in tets:
        a, b, c, d = (p[i] for i in t)
        m = [[b[i]-a[i] for i in range(3)],
             [c[i]-a[i] for i in range(3)],
             [d[i]-a[i] for i in range(3)]]
        det = (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
             - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
             + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
        tot += abs(det) / 6.0
    return tot

def main(path):
    nodes, part, sect, mat, shells, solids, lumped = parse(path)
    print(f"parts {len(part)}  sections {len(sect)}  materials {len(mat)}  "
          f"shells {len(shells)}  solids {len(solids)}  lumped {len(lumped)}")
    ros = sorted(set(round(v) for v in mat.values()))
    print(f"density range kg/m^3: {ros[0]} .. {ros[-1]}  (steel 7890 expected present: "
          f"{7890 in ros})")

    nm = defaultdict(float)          # node -> lumped mass, kg
    m_shell = m_solid = 0.0
    skipped = 0

    for pid, ns in shells:
        p = part.get(pid)
        if not p: skipped += 1; continue
        t = sect.get(p[0]); ro = mat.get(p[1])
        if not t or not ro: skipped += 1; continue
        pts, uniq = [], []
        for n in ns:
            if n in nodes and n not in uniq:
                uniq.append(n); pts.append(nodes[n])
        if len(pts) < 3: skipped += 1; continue
        a = tri_area(*pts[:3])
        if len(pts) == 4:
            a += tri_area(pts[0], pts[2], pts[3])
        m = a * t * ro
        m_shell += m
        for n in uniq:
            nm[n] += m / len(uniq)

    for pid, ns in solids:
        p = part.get(pid)
        if not p: skipped += 1; continue
        ro = mat.get(p[1])
        if not ro: skipped += 1; continue
        pts = [nodes[n] for n in ns if n in nodes]
        if len(pts) != 8: skipped += 1; continue
        m = hex_volume(pts) * ro
        m_solid += m
        for n in ns:
            if n in nodes:
                nm[n] += m / 8.0

    m_lump = 0.0
    for nid, m in lumped:
        if nid in nodes:
            nm[nid] += m; m_lump += m

    M = sum(nm.values())
    cg = [sum(nm[n] * nodes[n][k] for n in nm) / M for k in range(3)]

    Ixx = Iyy = Izz = Ixy = Ixz = Iyz = 0.0
    for n, m in nm.items():
        x, y, z = (nodes[n][k] - cg[k] for k in range(3))
        Ixx += m * (y*y + z*z); Iyy += m * (x*x + z*z); Izz += m * (x*x + y*y)
        Ixy += m * x*y;         Ixz += m * x*z;         Iyz += m * y*z

    print()
    print(f"mass shells {m_shell:9.2f} kg")
    print(f"mass solids {m_solid:9.2f} kg")
    print(f"mass lumped {m_lump:9.2f} kg")
    print(f"TOTAL MASS  {M:9.2f} kg      (elements skipped for missing section/material: {skipped})")
    print(f"CG (m)      x {cg[0]:.4f}   y {cg[1]:.4f}   z {cg[2]:.4f}   -> CG height {cg[2]:.4f} m")
    print()
    print("Inertia about CG, kg m^2   (x = longitudinal, y = lateral, z = vertical)")
    print(f"  Ixx (roll)  {Ixx:9.1f}")
    print(f"  Iyy (pitch) {Iyy:9.1f}")
    print(f"  Izz (yaw)   {Izz:9.1f}")
    print(f"  products    Ixy {Ixy:8.1f}  Ixz {Ixz:8.1f}  Iyz {Iyz:8.1f}")

if __name__ == '__main__':
    main(sys.argv[1])
