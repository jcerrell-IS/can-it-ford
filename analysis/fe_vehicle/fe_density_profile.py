#!/usr/bin/env python3
"""
Emit a height-resolved density profile for the vehicle particle cloud, taken from
the NHTSA finite-element model, so the simulated vehicle carries the real
vehicle's centre of gravity instead of its hull's geometric centroid.

WHY A PROFILE AND NOT BOXES
  mpm_solver_warp.py exposes two ways to vary density.
    additional_material_params selects particles by POSITION inside an axis-aligned
    box and does not filter by material (kernels/mpm_utils.py apply_additional_params,
    line 1302). Any water particle in the box is re-densified too, and there IS water
    inside the vehicle bounding box: under the 147 mm ground clearance and in the
    wheel wells. That path is unsafe here.
    reset_densities_and_update_masses(all_particle_densities) takes a FULL
    per-particle density tensor and recomputes mass = density * volume. It is exact,
    touches only the particles you choose, and needs no solver patch. Use that.

WHY THIS IS NOT WIRING INERTIA
  CLAUDE.md item 4 forbids writing the tabulated inertia tensor in as a parameter,
  and params_check.py check_inertia_wired() enforces it. No tensor is written here.
  Only mass-per-unit-volume as a function of height is set; the solver still derives
  CG and inertia from its own particle cloud at mpm_solver_warp.py:859-871. Total
  mass stays at the canonical wired value.
"""
import sys, json
import numpy as np

sys.path.insert(0, "/Users/josie/blender_nhtsa")
exec(open("/Users/josie/blender_nhtsa/fe_mass_distribution.py").read().split("def main()")[0])




def _reparse_nodes(key):
    """Node id -> (x, y, z) in metres. Needed because fe_nodal_masses returns
    arrays without ids, and set-file mass is addressed by part, then by node."""
    nodes, kw = {}, None
    def fw(l, s, w):
        return l[s:s + w].strip()
    for line in open(key, errors="replace"):
        if not line or line[0] == "$":
            continue
        if line[0] == "*":
            kw = line.strip().upper()
            if kw.endswith("_TITLE"):
                kw = kw[: -len("_TITLE")]
            continue
        if kw == "*NODE":
            nid = fw(line, 0, 8)
            if nid:
                try:
                    nodes[int(nid)] = (float(fw(line, 8, 16) or 0) * 0.001,
                                       float(fw(line, 24, 16) or 0) * 0.001,
                                       float(fw(line, 40, 16) or 0) * 0.001)
                except ValueError:
                    pass
    return nodes


def profile_from_fe(key, npz, total, dz=0.10, min_frac=0.005, setfile=None):
    P, W = fe_nodal_masses(key)
    m_struct = float(W.sum())
    # *ELEMENT_MASS_PART in the companion set file is NOT optional. For the Yaris
    # it is 228.50 kg, 20.8 percent of the model, and it is lumped onto specific
    # parts spanning the full height (30.0 kg gas tank, 16.0 kg ROOF, 11.5 kg on
    # each of three chassis rails). Omitting it biased the vertical distribution
    # this profile exists to reproduce. With it, the computation matches the CCSA
    # validation report's own FE column to 0.43 percent on mass and 0.6 mm on CG.
    m_added = 0.0
    if setfile:
        import os as _os, sys as _sys
        _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
        from setfile_mass import element_mass_part, part_nodes
        add = element_mass_part(setfile)
        if add:
            pn = part_nodes(key)
            nodes = _reparse_nodes(key)
            eP, eW = [], []
            for pid, m in add.items():
                ns = [n for n in pn.get(pid, ()) if n in nodes]
                if not ns:
                    continue
                per = m / len(ns)
                for n in ns:
                    eP.append(nodes[n]); eW.append(per)
            if eP:
                P = np.vstack([P, np.asarray(eP)])
                W = np.concatenate([W, np.asarray(eW)])
                m_added = float(np.asarray(eW).sum())
    Mfe, cg_fe, I_fe = props(P, W)

    d = np.load(npz)
    vf = d["veh_particles_vehframe"].astype(np.float64)
    n = vf.shape[0]

    # Orientation is DETECTED, not assumed: the FE long axis is X and the solver
    # vehicle frame puts it on Y, but the sign is decided by matching the height
    # profile along the long axis, the same test the renderer uses. Assuming +90
    # worked for the Yaris and must not be carried to another vehicle unchecked.
    def _prof(Q, axis, nb=24):
        a = Q[:, axis]
        e = np.linspace(a.min(), a.max(), nb + 1)
        z0v, z1v = Q[:, 2].min(), Q[:, 2].max()
        out = np.zeros(nb)
        for i in range(nb):
            m = (a >= e[i]) & (a <= e[i + 1])
            out[i] = (Q[m, 2].max() - z0v) if m.any() else 0.0
        return out / (z1v - z0v)
    long_fe = int(np.argmax(P.max(0) - P.min(0)))
    long_sv = int(np.argmax(vf.max(0) - vf.min(0)))
    pv, pn = _prof(vf, long_sv), _prof(P, long_fe)
    ep, em = float(np.abs(pn - pv).mean()), float(np.abs(pn[::-1] - pv).mean())
    sgn = 1 if ep < em else -1
    th = np.pi / 2 * sgn if long_fe != long_sv else 0.0
    Rz = np.array([[np.cos(th), -np.sin(th), 0.],
                   [np.sin(th),  np.cos(th), 0.], [0., 0., 1.]])
    print(f"orientation: FE long axis {long_fe}, solver long axis {long_sv}, "
          f"rotation {np.degrees(th):+.0f} deg  (profile err {ep:.5f} vs {em:.5f})")
    Pr = P @ Rz.T
    Pr = Pr + ((vf.min(0) + vf.max(0)) / 2 - (Pr.min(0) + Pr.max(0)) / 2)

    z0, z1 = vf[:, 2].min(), vf[:, 2].max()
    H = z1 - z0
    nb = max(1, int(np.ceil(H / dz)))
    edges = np.linspace(z0, z1, nb + 1)

    fe_bin = np.zeros(nb)
    ib = np.clip(np.digitize(Pr[:, 2], edges) - 1, 0, nb - 1)
    for i, w in zip(ib, W):
        fe_bin[i] += w
    pb = np.clip(np.digitize(vf[:, 2], edges) - 1, 0, nb - 1)
    cnt = np.bincount(pb, minlength=nb).astype(float)

    # FE mass in a band with no particles cannot be represented; fold it into the
    # nearest populated band rather than losing it, and report how much moved.
    orphan = float(fe_bin[cnt == 0].sum())
    pop = np.where(cnt > 0)[0]
    for i in np.where(cnt == 0)[0]:
        if fe_bin[i] > 0 and len(pop):
            fe_bin[pop[np.argmin(np.abs(pop - i))]] += fe_bin[i]
            fe_bin[i] = 0.0

    # THIN-BAND GUARD. A band holding almost no particles concentrates real FE
    # mass onto a handful of them. The Rogue's lowest band held 47 particles,
    # 0.11 percent of the cloud, at 7.15x uniform density. Merge any band under
    # min_frac of the cloud into its larger neighbour, keeping bands contiguous
    # in z so each still maps to one set_material_range index range.
    thresh = max(1.0, min_frac * n)
    group = list(range(nb))                      # bin -> band id
    while True:
        tot_cnt = {}
        for b_, c_ in zip(group, cnt):
            tot_cnt[b_] = tot_cnt.get(b_, 0.0) + c_
        ids = sorted(tot_cnt)
        small = [g for g in ids if 0 < tot_cnt[g] < thresh]
        if not small:
            break
        g = min(small, key=lambda x: tot_cnt[x])
        pos = ids.index(g)
        nbrs = [ids[pos - 1]] if pos > 0 else []
        if pos < len(ids) - 1:
            nbrs.append(ids[pos + 1])
        if not nbrs:
            break
        tgt = max(nbrs, key=lambda x: tot_cnt[x])
        group = [tgt if x == g else x for x in group]
    merged = sorted(set(group))
    n_merged = nb - len(merged)

    band_mass = {g: 0.0 for g in merged}
    band_cnt = {g: 0.0 for g in merged}
    for i in range(nb):
        band_mass[group[i]] += fe_bin[i]
        band_cnt[group[i]] += cnt[i]

    w_particle = np.zeros(n)
    for i in range(nb):
        g = group[i]
        if band_cnt[g] > 0:
            w_particle[pb == i] = band_mass[g] / band_cnt[g]
    w_particle *= total / w_particle.sum()

    Mp, cg_p, I_p = props(vf, w_particle)
    Wu = np.full(n, total / n)
    Mu, cg_u, I_u = props(vf, Wu)
    _, cg_fe_s, _ = props(Pr, W)
    I_fe_s = I_fe * (total / Mfe)
    I_target = np.array([I_fe_s[1], I_fe_s[0], I_fe_s[2]])

    # per-particle volume implied by the canonical seeding
    # solid volume from THIS run, never the Yaris HULL literal at
    # sim_standing.py:15, which prints regardless of which hull was loaded.
    h_run = float(d["h"]) if "h" in d else float(d["dx"]) / 2.0
    v_p = h_run ** 3
    solid_vol = v_p * n
    dens = w_particle / v_p

    bands = []
    for g in merged:
        bins = [i for i in range(nb) if group[i] == g]
        if band_cnt[g] == 0:
            continue
        lo_e, hi_e = edges[min(bins)], edges[max(bins) + 1]
        sel = np.isin(pb, bins)
        bands.append({
            "band": int(g),
            "merged_from_bins": len(bins),
            "z_lo_vehframe_m": float(lo_e),
            "z_hi_vehframe_m": float(hi_e),
            "z_frac_lo": float((lo_e - z0) / H),
            "z_frac_hi": float((hi_e - z0) / H),
            "n_particles": int(sel.sum()),
            "mass_kg": float(w_particle[sel].sum()),
            "density_kg_m3": float(dens[sel][0]),
            "density_ratio_vs_uniform": float(dens[sel][0] / (total / solid_vol)),
        })
    return dict(
        dz_m=dz, min_frac=min_frac,
        mass_structural_kg=m_struct, mass_setfile_added_kg=m_added, n_bins_merged_away=int(n_merged),
        n_bands_populated=len(bands), n_particles=int(n),
        total_mass_kg=float(total), uniform_density_kg_m3=float(total / solid_vol),
        particle_volume_m3=float(v_p), orphan_mass_kg=orphan,
        fe_mass_kg=float(Mfe), fe_cg_z_feframe_m=float(cg_fe[2]),
        cg_target_solverframe_m=float(cg_fe_s[2]),
        cg_uniform_m=float(cg_u[2]), cg_profiled_m=float(cg_p[2]),
        inertia_target=[float(x) for x in I_target],
        inertia_uniform=[float(x) for x in I_u],
        inertia_profiled=[float(x) for x in I_p],
        bands=bands)


if __name__ == "__main__":
    r = profile_from_fe(sys.argv[1], sys.argv[2], float(sys.argv[3]),
                        float(sys.argv[4]) if len(sys.argv) > 4 else 0.10,
                        float(sys.argv[6]) if len(sys.argv) > 6 else 0.005,
                        sys.argv[7] if len(sys.argv) > 7 else None)
    print(f"mass structural {r['mass_structural_kg']:.2f} kg + setfile "
          f"{r['mass_setfile_added_kg']:.2f} kg = {r['mass_structural_kg']+r['mass_setfile_added_kg']:.2f} kg")
    print(f"bands populated {r['n_bands_populated']}  dz {r['dz_m']} m  "
          f"orphan {r['orphan_mass_kg']:.2f} kg  thin bins merged {r['n_bins_merged_away']}")
    print(f"CG target (solver vehicle frame) {r['cg_target_solverframe_m']:.4f} m")
    print(f"CG uniform  {r['cg_uniform_m']:.4f} m   error {r['cg_uniform_m']-r['cg_target_solverframe_m']:+.4f} m")
    print(f"CG profiled {r['cg_profiled_m']:.4f} m   error {r['cg_profiled_m']-r['cg_target_solverframe_m']:+.4f} m")
    t = r["inertia_target"]
    for nm, I in (("uniform ", r["inertia_uniform"]), ("profiled", r["inertia_profiled"])):
        print(f"I {nm} {I[0]:8.1f} {I[1]:7.1f} {I[2]:8.1f}   "
              f"[{100*(I[0]/t[0]-1):+5.1f}% {100*(I[1]/t[1]-1):+5.1f}% {100*(I[2]/t[2]-1):+5.1f}%]")
    print(f"density ratio range {min(b['density_ratio_vs_uniform'] for b in r['bands']):.3f}"
          f" .. {max(b['density_ratio_vs_uniform'] for b in r['bands']):.3f}")
    with open(sys.argv[5] if len(sys.argv) > 5
              else "/Users/josie/blender_nhtsa/yaris_density_profile.json", "w") as fh:
        json.dump(r, fh, indent=1)
    print("wrote profile json")
