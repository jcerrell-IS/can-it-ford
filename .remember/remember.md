# Handoff

## State
The realism track's central negative result was **overturned**: the SDF collider wrench is accurate to **+1.00% / +1.28%** (two g64 geometries), not -50%. The whole -7.67% to +115% spread was a free-surface reference error. Chain, confirmed by intervention (bulk 1.5e5 to 1.5e7 kills it): soft water leaks through the floor, `project_water` clamps it to one z plane and deletes downward momentum, ~20% of particles pile there, `column_surface` sums *bookkept* volume so it cannot see the collapse, the reported surface is ~0.57 m too high, and every analytic built on it is inflated. Correct estimator is mass above the face: `h_eff = (particles above box bottom) / (bulk linear particle density)`. Committed through `a6b66b6`, not pushed. Full narrative in `realism_track/FINDINGS.md` (chronological, retractions marked in place).

## Next
1. Read jobs **3362516** (F: g96 partial, cap 1800) and **3362547** (H/I: g64 repeats for an error bar; G: g96 full, cap 2400, aiming for a gate-met g96 point). The 1% result is g64-only until G or F lands gate-met.
2. **The one open defect**: the moving collider reads 6,164 N high vs corrected static buoyancy. Not added mass (would need 7,731 kg = 2.42x the *whole* cube's displaced mass at 37% submersion). Suspect the velocity handed to `set_sdf_pose`: for a separable collider the impulse is `m*(v_free - v_surf - v_tan)`, so every contact-band node contributes once `v_surf` is nonzero, which a fixed collider never exercises. Test: drive the collider at prescribed constant velocities, see whether the wrench scales like drag or like a node count.
3. A bulk sweep **cannot** use the existing settle gate: `c/vmax >= 20` scales with c, so stiffer runs stop *earlier* (354, 62, 20 frames). Needs an absolute criterion, e.g. `vmax < 0.05 m/s`.

## Context
- **Shell is on a CPU-only idev node** (job 3362478, c307-006, partition `development`, no nvidia-smi). `sbatch` is refused there; submit via `ssh -o BatchMode=yes login1 "cd $REPO && sbatch ..."`, key auth works despite the MFA banner text.
- **g96 settle is not reproducible**: byte-identical configs gave 776 / 777 / >900 frames. Any single-run g96 validation number needs repeats and an error bar, including the project's own 7.3-7.7% figure.
- **Trap**: `sound_speed()` and `substeps_and_dt()` bind `bulk` as a *default arg* at def time while `set_material` reads the global, so patching `BULK` alone desynchronizes dt and the gate. `surface_and_leak.py` patches both and aborts unless `tank.sound_speed` matches.
- Writing `particle_F` does nothing for fluids: `mpm_utils.py:1086-1089` rebuilds it from `particle_F_trial`, which has no importer.
- Runs go on LS6 A100 via `/scratch/11603/jcerrell0629/warpmpm_ls6_env`; needs `PYTHONPATH=$REPO/mpm-engine/src:$REPO`. Never `git add -A`; Vista's 3 dirty tracked files stay unstaged; `renders/yaris_render_s1/` off limits.
