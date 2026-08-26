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
    out, kw, unresolved = {}, None, []
    for line in open(path, errors="replace"):
        if not line or line[0] == "$":
            continue
        if line[0] == "*":
            kw = line.strip().upper()
            continue
        if kw == "*ELEMENT_MASS_PART":
            # FIXED 2026-08-26. This read `if len(f) == 2` and therefore silently
            # skipped EVERY Rogue row. The Yaris deck writes two fields per row
            # (pid, addmass); the Rogue and Camry decks write four (pid, addmass,
            # finmass, lcid). A two-field test is a Yaris-shaped test, so the Rogue
            # returned 0.00 kg of added mass and READ AS A REAL ABSENCE. It is not:
            # set-rogue-v2.key carries a *ELEMENT_MASS_PART block.
            f = line.split()
            if len(f) < 2:
                continue
            pid_tok, mass_tok = f[0], f[1]
            # The Rogue writes `2001008&m1_1` for its two dummies and its payload:
            # an LS-DYNA *PARAMETER reference glued to the pid, which shifts the
            # field. No *PARAMETER card defining m1_1/m2_1/m3_1 exists anywhere in
            # the model directory, so these masses CANNOT be resolved from what
            # ships. Record them as unresolved rather than dropping them, so the
            # total is known to be a LOWER BOUND instead of looking complete.
            if "&" in pid_tok:
                try:
                    unresolved.append((int(pid_tok.split("&")[0]),
                                       pid_tok.split("&")[1]))
                except ValueError:
                    pass
                continue
            try:
                out[int(pid_tok)] = float(mass_tok) * 1000.0
            except ValueError:
                pass
    if unresolved:
        import sys
        print("SETFILE unresolved *PARAMETER addmass on %d part(s): %s"
              % (len(unresolved),
                 ", ".join("%d(&%s)" % u for u in unresolved)),
              file=sys.stderr)
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
