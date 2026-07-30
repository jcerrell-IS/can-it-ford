# Lane V, geometry and coupling read, 2026-07-25

Source file: `/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py`, 412 lines, read live on Vista this session. Solver quotes from `/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/kernels/mpm_solver_warp.py`. No code changed.

## Q1. Buoyancy is emergent, not analytic

There is no analytic buoyancy term anywhere in the file. The vehicle is loaded into the same particle array as the water and tagged as a rigid material range.

`vehicle.py:300-310`
```
300	        pos = np.concatenate([water, truck])
301	        vol = np.full(len(pos), h ** 3, dtype=np.float32)
305	        s = Solver(grid=self.grid, device=device).load_particles(pos, vol)
306	        s.set_material(newtonian(eta=water_eta, density=water_density,
307	                                 bulk_modulus=bulk_modulus))
308	        s.set_material_range(self.n_water, self.n_total, "rigid", obj_id=0,
309	                             density=vehicle_density)
310	        s.finalize_rigid_bodies()
```

`vehicle.py:5-7` states the mechanism: the particle set is registered with the rigid-body system "so per substep the fluid's grid momentum accumulates into a body force and torque and the body translates and rotates as one piece." `vehicle.py:248-250` repeats it: "the fluid's grid momentum accumulates into its force and torque each substep, so sliding, floating, and overturning come out of the coupling."

So buoyancy emerges from the MPM pressure field acting on the solidified particle set. This is why the column-fill over-fill measured at A9 biases buoyancy directly: every extra solid particle is an extra site where fluid grid momentum transfers into the body.

## Q2. What `vehicle_mass` sets

`vehicle.py:276-279`
```
276	        solid_volume = vehicle.n_particles * h ** 3
277	        if vehicle_mass is not None:
278	            vehicle_density = vehicle_mass / solid_volume
279	        self.vehicle_mass = vehicle_density * solid_volume
```

It sets `vehicle_density` only. That value reaches the solver once, as the `density=` argument at `vehicle.py:309`. It is not a per-particle mass assignment at this level.

It does **not** touch displaced volume. `solid_volume` is fixed at `:276` from `n_particles * h**3` before mass is read, so displaced volume depends only on the solidified particle count and the grid pitch. Mass and displaced volume are independent inputs, and passing `vehicle_mass` cannot correct a volume error.

## Q3. `grid_lim` formula

`vehicle.py:265-266`
```
265	        lim = float(max(2.2 * ext[1], 3.5 * ext[0], 6.0 * depth))
266	        self.grid = GridConfig(n_grid=n_grid, grid_lim=lim)
```

## Q4. `mesh.sample` is not seeded, and that is a reproducibility defect

`vehicle.py:162`
```
162	        pos = np.asarray(mesh.sample(60_000), dtype=np.float64)
```

The only seeding in the file is `vehicle.py:260` (`seed: int = 0` on `FloodScene.__init__`) feeding `vehicle.py:270` (`rng = np.random.default_rng(seed)`), which is used at `:298` to jitter **water** particle positions. That RNG never reaches `load_vehicle`, and `load_vehicle` contains no seeding of its own.

Confirmed defect: two `load_vehicle` calls on the same mesh return different surface point sets, so solidified particle counts and every derived volume are not reproducible run to run. Any resolution study must load once and re-solidify, not reload per resolution.

## The 100 to 300 kg/m3 band has no cited source

Origin is a docstring assertion, `vehicle.py:250-252`:
```
250	    and overturning come out of the coupling. vehicle_density is the body's effective
251	    density (vehicles are mostly air; a car is roughly 100 to 300 kg/m^3 spread over
252	    its volume, which is why they float); vehicle_mass, if given, overrides it with a
```

No citation, no DOI, no reference. Every downstream use restates it without adding a source: `CLAUDE.md:15` lists it as a physical anchor, `paper_draft.md:24` calls it a "fill-quality band", `paper_draft.md:125` calls it "the sweep's own density-plausibility gate", `analysis/gp_surrogate_results.md:54` calls it "the driver's 100 to 300 band", and `analysis/build_poster_phase_space.py:90` filters on the derived boolean.

**Report: there is no source.** It is a self-consistent internal convention traceable to one uncited docstring sentence. It should not be described in the paper as a published or standard band.

## Floor collider and vertical motion

**Floor plane, `vehicle.py:311-314`**
```
311	        # restitution > 0 makes each plane a rigid-body contact surface as well; the
312	        # grid BC alone holds only the water, and the body would sink through the floor
313	        s.add_plane((0, 0, floor), (0, 0, 1), "slip", friction=floor_friction,
314	                    restitution=0.05)
```
Surface string is `"slip"`. `mpm_solver_warp.py:2627` maps `{"sticky": 0, "slip": 1, "separable": 2}`, so slip is surface_type 1. Friction is `floor_friction` (default `0.5`, `vehicle.py:259`), restitution `0.05`. The four side walls at `vehicle.py:315-317` are also `"slip"`, with `friction=0.0`.

**No independent z constraint exists.** Grepping `vehicle.py` for `freeze`, `dof`, `DOF`, `clamp`, `[2] = 0`, `z_lock`, `fix_z`, `constrain` returns nothing (exit 1). The floor plane is the only mechanism acting on the body's vertical motion.

**dz is computed live**, `vehicle.py:208-210`:
```
208	    def append(self, t: float, state: dict, com0: np.ndarray) -> None:
209	        self.t.append(t)
210	        self.displacement.append(state["com"] - com0)
```
`FloodHistory` has no field named `dz`; it stores a 3-vector `displacement`, of which z is the third component, recomputed from live `rigid_state()` on every append. It is not initialized-and-never-updated.

## Why dz = 0.0000, and one correction to the premise

`mpm_solver_warp.py:1973-1988`
```
1973	                        v = state.grid_v_out[grid_x, grid_y, grid_z]
1974	                        normal_component = wp.dot(v, n)
1975	                        if param.surface_type == 1:
1976	                            v = (
1977	                                v - normal_component * n
1978	                            )  # Project out all normal component
1979	                        else:
1980	                            v = (
1981	                                v - wp.min(normal_component, 0.0) * n
1982	                            )  # Project out only inward normal component
1983	                        if normal_component < 0.0 and wp.length(v) > 1e-20:
1984	                            v = wp.max(
1985	                                0.0, wp.length(v) + normal_component * param.friction
1986	                            ) * wp.normalize(
1987	                                v
1988	                            )  # apply friction here
```

Confirmed: for the floor with `n = (0, 0, 1)`, surface_type 1 projects out the **entire** normal component at `:1976-1978`, in both directions. Upward grid velocity at floor-adjacent nodes is removed just as inward velocity is, so the body cannot lift. Combined with the absence of any other z constraint, that fully explains dz = 0.0000.

**Correction to the stated premise.** The claim that switching to separable "makes the friction term at 1985 live for the first time" is **false**. `normal_component` is captured at `:1974` *before* the projection and is never recomputed, so the guard at `:1983` tests the pre-projection value. Friction at `:1985` is already live under slip. This is consistent with the retraction register entry that friction is not silently ignored for slip; the friction block sits at the same indentation as the if/else and applies to both branches.

So the case for separable is that the body can lift and buoyancy can act vertically, not that friction starts working.

**What could break.** The comment at `vehicle.py:311-312` is the explicit warning: restitution is what makes the plane a rigid-body contact surface, because "the grid BC alone holds only the water, and the body would sink through the floor." Under separable the grid BC stops removing outward normal velocity, so the body's vertical support depends entirely on the restitution contact path. If that path is weaker than the grid BC, the vehicle sinks through the floor rather than floating.

I checked `vehicle.py` only. The four side walls at `:315-317` are independently `"slip"` and would be unaffected by a floor-only change. I did **not** audit whether any other module assumes the floor is surface_type 1, so that part of the question is unresolved rather than answered.
