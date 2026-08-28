## YOUR SLOT: d17-moving, branch `claude/r9-moving-vehicle`, worktree `.claude/worktrees/r9-moving-vehicle`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d17-moving` first.

## YOU HAVE A LIVE GPU NODE AND A CLOCK

Vista idev job **920452 on c642-071**, started 23:51, **two hours**. 609 SUs remain on BCS20003. Reach it with:

```
ssh -o BatchMode=yes vista "srun --overlap --jobid=920452 --pty <cmd>"
```

`--overlap` is mandatory. Without it a step into a live idev dies. Submit work EARLY and analyse while it runs. Josie has authorised installing whatever is needed.

## THE RESEARCH QUESTION YOU ARE ACTUALLY ANSWERING

Every one of this project's 17 canonical runs is a **stationary** vehicle in moving water. That is correct for the AR&R and Shand thresholds, which describe a stationary vehicle, and it is why the project's own notes say the word "ford" in the title is what mismatches, not the setup.

**Nobody in the literature outputs a graded safe crossing speed as a function of both depth and flow velocity.** The field is entirely binary thresholds and incipient-motion curves. Pregnolato et al. 2017 (`10.1016/j.trd.2017.06.020`, open access) is the closest and it is depth-only, `v(w) = 0.0009w^2 - 0.5529w + 86.9448`, and it declares 30 cm impassable so it collapses to binary exactly where stability matters. Al-Qadami et al. 2022 full-scale (`10.1007/s11069-021-04949-6`) found drag "increased significantly with the increment of flow velocity, Froude number, and vehicle speed", which is the clearest published evidence that vehicle speed raises destabilising load, but their output is forces and a critical depth near 0.38 to 0.40 m, NOT a speed function.

So: **v_car and v_water are separate physical variables and the literature conflates or omits the second. Distinguishing them is itself the contribution.** Report v_car in the ground frame, v_water in the ground frame, and v_relative, and never let a reader collapse them.

## WHAT ALREADY EXISTS, VERIFIED LIVE BY THE COORDINATOR TONIGHT. DO NOT REBUILD ANY OF IT.

**1. The moving-body API is already in warpmpm. NO SOLVER CHANGE IS NEEDED.** Confirmed against the LIVE install on Vista at `/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/core/solver.py`, warp 1.15.0:

```
:93   periodic_x
:324  add_sdf_collider(sdf, center, quat=(0,0,0,1), ...)
:339  set_sdf_pose(handle, center=, quat=, velocity=, omega=)
:348  reset_sdf_force(handle)
:354  sdf_wrench(handle, dt)
:379  the periodic_x guard, which exists on add_cdf_collider only
```

Driver loop per tick: `reset_sdf_force` then `step` then `sdf_wrench(handle, dt=n_substeps*dt_sub)` then integrate then `set_sdf_pose`.

**2. The flooded roadway channel already exists.** `simulation/openchannel_bc.py` on your base branch, 714 lines, implements Zhao, Bolognin, Liang, Rohe and Vardon 2019 (`10.1016/j.compfluid.2018.10.007`), the correct citation for MPM in/outflow, NOT Kumar. It gives you `RecyclingChannelBC` (velocity-controlled inflow, pressure-controlled outflow), `tilted_gravity(grade_deg)` for a graded roadway, `OverfallBC`, and self-tests. USE IT.

## FIVE SILENT TRAPS, EVERY ONE MEASURED ON THIS PROJECT

1. `sdf_wrench` divides accumulated impulse by whatever dt it is handed. Passing `dt_sub` instead of the **tick** duration inflates force by exactly n, plausibly and without error.
2. The engine never zeroes `param.force` on the SDF path, so a naive read is the run-to-date total, not the tick's. Call reset every tick.
3. Quaternion order differs WITHIN the same file: `solver.py:324` defaults xyzw `(0,0,0,1)`, while `add_cup` at `:256` documents wxyz `(1,0,0,0)`.
4. **COM offset is a hard blocker.** `RigidBody6DOF` raises `NotImplementedError` on non-zero COM offset, because the SDF collider rotates about its centre and `sdf_wrench` reports torque about that same centre. The Yaris cloud CG sits 0.6312 m above the floor against bbox mid-height 0.7427 m.
5. **Never combine `periodic_x` with an SDF vehicle.** `add_cdf_collider` guards it at `:379`; `add_sdf_collider` has NO equivalent guard.

**Because of trap 4, PRESCRIBE the vehicle motion and MEASURE the wrench. Do not attempt free 6DOF tonight.** Commanding v_car and reading the hydrodynamic load is the scientifically correct first experiment: it is exactly Al-Qadami's measurement extended into a surface, it is a held-fixed comparison, and it sidesteps the blocker entirely rather than pretending it is solved. Evaluate stability afterwards by comparing the measured wrench against the project's existing criteria. Say plainly in the write-up that the body is prescribed, so nobody reads it as a free-body result.

## ALSO TRUE AND EASY TO GET WRONG

- **The grid is forced cubic.** `GridConfig(n_grid, grid_lim)` takes one scalar, so a long shallow channel costs cubically and anisotropic grading cannot be expressed. Keep the domain as short as the physics allows.
- **Domain rule that reproduces canonical exactly**, from `renders/yaris_render_s3_enhanced/hull_sweep.sbatch:38-42`: `lim = max(2.2*ext_long, 3.5*ext_short, 6.0*depth)`, giving the Yaris 9.421742314.
- **Axis trap:** `sim_standing.py:82` uses `ext[1]` AFTER `load_vehicle(up='z')` permutes axes. Taking the PLY axes at face value gives 14.989 m instead of 9.4217 m, a 59 percent error.
- **`ReservePool` in openchannel_bc.py has a known row-collision defect** that silently corrupts CG and inertia and presents as physics. It is one of nine items awaiting Josie's decision. Use `RecyclingChannelBC`, not `ReservePool`, unless you verify the defect is fixed. If you must use it, verify first and say so.
- **Engine limitation, state it, do not overstate it:** `mpm_utils.py:1100` sets rigid particle stress to a zero mat33 and material 8 is excluded from the SVD, so the hull exerts no pressure on the water. But `_apply_rigid_restitution` IS live at restitution 0.05, so "no force is ever formed" is FALSE. The real limitation is that the net force cannot be decomposed.

## YOUR UNIT

1. Build `simulation/moving_vehicle_channel.py`: the Yaris hull as a moving SDF collider at a prescribed v_car, inside a `RecyclingChannelBC` flooded roadway, with the wrench measured per tick and all five traps handled explicitly in code with a comment naming each.
2. **Write a falsifiable self-test BEFORE any GPU run.** At minimum: v_car = 0 and v_water = 0 must give zero net streamwise wrench to within noise, and the wrench at v_car = 0 must reproduce the canonical stationary case's order of magnitude. A driver that cannot pass a no-forcing control is not measuring anything.
3. Run the matrix. Suggested and adjust to fit the clock: **v_car in {0, 2.2, 4.5, 6.7, 8.9} m/s** (0, 5, 10, 15, 20 mph) crossed with **v_water in {0.5, 1.0, 2.0, 3.0} m/s** at fixed depth 0.30 m, which is the project's canonical depth and near Al-Qadami's 0.38 m critical depth. That is 20 cells. Add repeats where the clock allows, because this project's runs are NON-DETERMINISTIC and a single draw is not a result.
4. Emit a tidy per-run record and build the (v_car, v_water) load surface in `analysis/r9_speed_surface.py`. Report distributions, not single points, wherever you have repeats.

## DISCIPLINE

Pre-register the matrix and the pass criteria in a commit BEFORE the first run, as slot d3-force did last night. That commit is what makes the result trustworthy. Log to Weights and Biases if it costs you nothing; the project already has 105 runs there and every run is already linked to its GitHub commit.

Nothing is pushed. Stage explicit paths. Append your board row. If the node dies, say what completed and what did not rather than reporting the matrix as done.
