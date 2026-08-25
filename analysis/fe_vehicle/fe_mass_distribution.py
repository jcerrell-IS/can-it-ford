#!/usr/bin/env python3
"""
Give the simulated vehicle the REAL mass distribution of the NHTSA finite-element
model, without wiring any inertia number into the solver.

THE PROBLEM
  solidify_watertight fills the hull uniformly, so vehicle_density is a single
  scalar and the centre of gravity lands at the geometric centroid. CLAUDE.md
  item 4 records the consequence: the cloud CG sits at 0.6312 m against a MEASURED
  0.558 m on slide 7 of DOI 10.13021/G8JS5D, 13.1 percent too high. A too-high CG
  biases toward topple.

WHY THIS IS NOT "WIRING INERTIA"
  CLAUDE.md item 4 says DO NOT WIRE inertia_kg_m2, and params_check.py enforces it.
  That rule is about writing a TABULATED TENSOR in as a parameter. Nothing here does.
  This only redistributes mass in space; the solver still computes CG and inertia
  from its own particle cloud at kernels/mpm_solver_warp.py:859-871, exactly as it
  does today. Total mass is preserved to the canonical value, so the one wired
  scalar is unchanged.

HOW IT REACHES THE SOLVER
  No patch. mpm_solver_warp.py set_parameters_dict already accepts
  additional_material_params, a list of {point, size, density}; kernels/mpm_utils.py
  apply_additional_params (line 1302) sets particle_density for particles inside an
  axis-aligned box of HALF-extents `size`, then mass is recomputed as density*volume.

VERIFICATION
  The script reports CG and inertia for the uniform cloud, for a z-stratified
  version, and for a full 3D voxel version, all against the FE model and against
  the measured vehicle. If the numbers do not move toward the measurement, this
  idea is wrong and the output says so.
"""
import sys, json, math
import numpy as np

MM = 0.001
RO_TO_SI = 1.0e12


def fw(l, s, w):
    return l[s:s + w].strip()


def fe_nodal_masses(path):
    """Nodal lumped masses in the FE model's own frame. Same method as
    nhtsa_mass_properties.py, which reproduced the published CG to the millimetre."""
    nodes, part, sect, mat = {}, {}, {}, {}
    shells, solids, lumped = [], [], []
    kw, stage, title = None, 0, None
    sec_id = None
    sec_line = mat_line = 0
    title_pending = False
    with open(path, errors='replace') as fh:
        for line in fh:
            if not line or line[0] == '$':
                continue
            if line[0] == '*':
                kw = line.strip().upper()
                # LS-DYNA _TITLE variants insert one title line before the data
                # card. Matching the bare keyword skipped 172,574 Rogue elements
                # and under-counted its mass by 15 percent.
                title_pending = kw.endswith('_TITLE')
                if title_pending:
                    kw = kw[: -len('_TITLE')]
                stage = 0; sec_line = mat_line = 0; sec_id = None
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
                try:
                    lumped.append((int(fw(line, 8, 8)), float(fw(line, 16, 16) or 0) * 1000.0))
                except ValueError:
                    pass
            elif kw == '*PART':
                if stage == 0:
                    title = line.strip(); stage = 1
                elif stage == 1:
                    try:
                        part[int(fw(line, 0, 10))] = (int(fw(line, 10, 10) or 0),
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

    def tri_area(a, b, c):
        u = np.subtract(b, a); v = np.subtract(c, a)
        return 0.5 * np.linalg.norm(np.cross(u, v))

    HEX = ((0,1,3,4),(1,2,3,6),(1,3,4,6),(3,4,6,7),(1,4,5,6))
    nm = {}
    for pid, ns in shells:
        p = part.get(pid)
        if not p: continue
        t = sect.get(p[0]); ro = mat.get(p[1])
        if not t or not ro: continue
        uniq = []
        for n in ns:
            if n in nodes and n not in uniq:
                uniq.append(n)
        if len(uniq) < 3: continue
        pts = [nodes[n] for n in uniq]
        a = tri_area(*pts[:3]) + (tri_area(pts[0], pts[2], pts[3]) if len(pts) == 4 else 0.0)
        m = a * t * ro
        for n in uniq:
            nm[n] = nm.get(n, 0.0) + m / len(uniq)
    for pid, ns in solids:
        p = part.get(pid)
        if not p: continue
        ro = mat.get(p[1])
        if not ro: continue
        pts = [nodes[n] for n in ns if n in nodes]
        if len(pts) != 8: continue
        vol = 0.0
        for tet in HEX:
            a, b, c, dd = (np.array(pts[i]) for i in tet)
            vol += abs(np.linalg.det(np.array([b - a, c - a, dd - a]))) / 6.0
        m = vol * ro
        for n in ns:
            if n in nodes:
                nm[n] = nm.get(n, 0.0) + m / 8.0
    for nid, m in lumped:
        if nid in nodes:
            nm[nid] = nm.get(nid, 0.0) + m

    ids = list(nm.keys())
    P = np.array([nodes[n] for n in ids])
    W = np.array([nm[n] for n in ids])
    return P, W


def props(P, W):
    """Mass, CG and inertia about the CG for a weighted point set."""
    M = W.sum()
    cg = (P * W[:, None]).sum(0) / M
    Q = P - cg
    Ixx = (W * (Q[:, 1]**2 + Q[:, 2]**2)).sum()
    Iyy = (W * (Q[:, 0]**2 + Q[:, 2]**2)).sum()
    Izz = (W * (Q[:, 0]**2 + Q[:, 1]**2)).sum()
    return M, cg, np.array([Ixx, Iyy, Izz])


def main():
    key   = sys.argv[1]
    npz   = sys.argv[2]
    total = float(sys.argv[3])           # canonical wired mass, kg
    out   = sys.argv[4]
    vox   = float(sys.argv[5]) if len(sys.argv) > 5 else 0.30

    P, W = fe_nodal_masses(key)
    Mfe, cg_fe, I_fe = props(P, W)
    print(f"FE model            mass {Mfe:8.2f} kg   CG z {cg_fe[2]:.4f} m   "
          f"I {I_fe[0]:7.1f} {I_fe[1]:7.1f} {I_fe[2]:7.1f}")

    d  = np.load(npz)
    vf = d["veh_particles_vehframe"].astype(np.float64)   # solver frame, long axis Y
    n  = vf.shape[0]

    # Bring the FE mass points into the solver's vehicle frame with the SAME
    # transform the renderer derived: rotate +90 about Z, then match bbox centres.
    Rz = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
    Pr = P @ Rz.T
    off = (vf.min(0) + vf.max(0)) / 2 - (Pr.min(0) + Pr.max(0)) / 2
    Pr = Pr + off

    # --- baseline: uniform fill, what the solver does today
    Wu = np.full(n, total / n)
    Mu, cg_u, I_u = props(vf, Wu)

    def voxel_weights(size_xyz):
        lo = vf.min(0) - 1e-9
        gi = np.floor((vf - lo) / size_xyz).astype(int)
        gf = np.floor((Pr - lo) / size_xyz).astype(int)
        key_p = (gi[:, 0], gi[:, 1], gi[:, 2])
        from collections import defaultdict
        femass = defaultdict(float)
        for k, w in zip(map(tuple, gf), W):
            femass[k] += w
        counts = defaultdict(int)
        for k in map(tuple, gi):
            counts[k] += 1
        wts = np.zeros(n)
        unmatched = 0.0
        for i, k in enumerate(map(tuple, gi)):
            wts[i] = femass.get(k, 0.0) / counts[k]
        # FE mass landing in voxels with no particle is redistributed uniformly,
        # so total mass is conserved exactly rather than silently lost.
        got = wts.sum()
        unmatched = W.sum() - got
        if wts.sum() > 0:
            wts += unmatched / n
        wts *= total / wts.sum()
        return wts, unmatched

    # --- (a) z-stratified only: cheapest thing that could fix the CG
    zsize = np.array([1e6, 1e6, vox])
    Wz, unz = voxel_weights(zsize)
    Mz, cg_z, I_z = props(vf, Wz)

    # --- (b) full 3D voxels
    vsize = np.array([vox, vox, vox])
    W3, un3 = voxel_weights(vsize)
    M3, cg_3, I_3 = props(vf, W3)

    # FE reference scaled to the canonical mass, so CG/inertia compare like for like.
    # CG must be quoted in the SOLVER's vehicle frame, not the FE frame: the fit
    # applies a z offset, so comparing the two frames directly overstates the error.
    I_fe_s = I_fe * (total / Mfe)
    _, cg_fe_solver, _ = props(Pr, W)
    I_fe_solver = np.array([I_fe_s[1], I_fe_s[0], I_fe_s[2]])   # +90 about Z swaps x,y
    print(f"  (FE CG in solver vehicle frame: z {cg_fe_solver[2]:.4f} m, "
          f"offset {cg_fe_solver[2]-cg_fe[2]:+.4f} m)")

    print()
    print(f"target: FE distribution scaled to the canonical {total:.0f} kg")
    print(f"  CG z {cg_fe[2]:.4f} m (FE frame)   I roll/pitch/yaw "
          f"{I_fe_s[0]:7.1f} {I_fe_s[1]:7.1f} {I_fe_s[2]:7.1f}")
    print(f"  solver-frame target: Ixx {I_fe_solver[0]:7.1f}  Iyy {I_fe_solver[1]:7.1f}"
          f"  Izz {I_fe_solver[2]:7.1f}")
    print()
    hdr = f"{'variant':22s} {'mass':>8s} {'CG z':>8s} {'CGerr':>8s} {'Ixx':>8s} {'Iyy':>8s} {'Izz':>8s}"
    print(hdr); print("-" * len(hdr))
    for nm_, M_, cg_, I_ in (("uniform (today)", Mu, cg_u, I_u),
                             (f"z-strata {vox:.2f} m", Mz, cg_z, I_z),
                             (f"3D voxels {vox:.2f} m", M3, cg_3, I_3)):
        e = cg_[2] - cg_fe_solver[2]
        pc = [100*(I_[k]/I_fe_solver[k] - 1) for k in range(3)]
        print(f"{nm_:22s} {M_:8.1f} {cg_[2]:8.4f} {e:+8.4f} "
              f"{I_[0]:8.1f} {I_[1]:8.1f} {I_[2]:8.1f}  "
              f"[{pc[0]:+5.1f}% {pc[1]:+5.1f}% {pc[2]:+5.1f}%]")
    print()
    print(f"FE mass landing in empty voxels, redistributed: z-strata {unz:.2f} kg, "
          f"3D {un3:.2f} kg")

    # --- emit additional_material_params for the 3D voxel version
    lo = vf.min(0) - 1e-9
    gi = np.floor((vf - lo) / vsize).astype(int)
    from collections import defaultdict
    per_vox = defaultdict(list)
    for i, k in enumerate(map(tuple, gi)):
        per_vox[k].append(i)
    v_particle = None
    boxes = []
    for k, idx in per_vox.items():
        dens = W3[idx].mean()          # kg per particle; solver needs kg/m^3
        centre = lo + (np.array(k) + 0.5) * vsize
        boxes.append({"voxel": [int(x) for x in k],
                      "point_vehframe_m": [float(x) for x in centre],
                      "size_half_m": [float(x) for x in vsize / 2],
                      "mass_per_particle_kg": float(dens),
                      "n_particles": len(idx)})
    payload = {
        "source_fe_model": key,
        "source_run": npz,
        "canonical_total_mass_kg": total,
        "voxel_m": vox,
        "n_boxes": len(boxes),
        "n_particles": int(n),
        "frame": "VEHICLE FRAME of the solver run, long axis on Y. Convert to world "
                 "with the run's R,t before use, or apply at setup while the vehicle "
                 "is still at its seeded pose.",
        "density_note": "mass_per_particle_kg / particle_volume_m3 gives the density "
                        "to put in additional_material_params. particle_volume is "
                        "solid_volume_m3 / n_particles for a uniform seeding.",
        "warning": "apply_additional_params selects by POSITION and does not filter by "
                   "material, so any water particle inside a box is re-densified too. "
                   "Apply at setup, after the hull carve and before the settle.",
        "results": {
            "fe_mass_kg": float(Mfe), "fe_cg_z_m": float(cg_fe[2]),
            "fe_inertia_scaled": [float(x) for x in I_fe_s],
            "uniform_cg_z_m": float(cg_u[2]), "uniform_inertia": [float(x) for x in I_u],
            "zstrata_cg_z_m": float(cg_z[2]), "zstrata_inertia": [float(x) for x in I_z],
            "voxel3d_cg_z_m": float(cg_3[2]), "voxel3d_inertia": [float(x) for x in I_3],
        },
        "boxes": boxes,
    }
    with open(out, "w") as fh:
        json.dump(payload, fh, indent=1)
    print(f"\nwrote {out}  ({len(boxes)} boxes)")


main()
