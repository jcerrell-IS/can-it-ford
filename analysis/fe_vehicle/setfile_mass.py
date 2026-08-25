"""Parse *ELEMENT_MASS_PART added mass from an NCAC companion set file.

WHY THIS IS NOT OPTIONAL. The main deck of the Yaris gives 867.81 kg. The CCSA
validation report (DOI 10.13021/G8JS5D, slide 7 "Inertia Comparisons") declares
its FE model at 1101 kg. The 233 kg difference is *ELEMENT_MASS_PART in
set-yaris-coarse-v1l.key: 867.81 + 228.50 = 1096.31, a 0.43 percent match.

The block is captioned "Rear Payload" and that caption is WRONG. The 28 entries
are non-structural mass lumped onto the parts it attaches to, spanning the full
height of the car: 30.0 kg on the gas tank, 17.5 on the IP beam, 16.0 on the
ROOF, 11.5 each on three chassis rails. Omitting it does not just lose 21 percent
of the mass, it biases the vertical distribution, which is the one thing a
density profile exists to get right.
"""
import re


def element_mass_part(path):
    """Return {pid: added_mass_kg}. Units are tonne in the deck."""
    out, kw = {}, None
    for line in open(path, errors="replace"):
        if not line or line[0] == "$":
            continue
        if line[0] == "*":
            kw = line.strip().upper()
            continue
        if kw == "*ELEMENT_MASS_PART":
            f = line.split()
            if len(f) == 2:
                try:
                    out[int(f[0])] = float(f[1]) * 1000.0
                except ValueError:
                    pass
    return out


def part_nodes(key_path):
    """Return {pid: set(node ids)} from shell and solid connectivity."""
    from collections import defaultdict
    pn = defaultdict(set)
    kw = None
    def fw(l, s, w):
        return l[s:s + w].strip()
    for line in open(key_path, errors="replace"):
        if not line or line[0] == "$":
            continue
        if line[0] == "*":
            kw = line.strip().upper()
            if kw.endswith("_TITLE"):
                kw = kw[:-6]
            continue
        if kw == "*ELEMENT_SHELL":
            try:
                pid = int(fw(line, 8, 8))
                for i in range(4):
                    n = fw(line, 16 + 8 * i, 8)
                    if n:
                        pn[pid].add(int(n))
            except ValueError:
                pass
        elif kw == "*ELEMENT_SOLID":
            try:
                pid = int(fw(line, 8, 8))
                for i in range(8):
                    n = fw(line, 16 + 8 * i, 8)
                    if n:
                        pn[pid].add(int(n))
            except ValueError:
                pass
    return pn
