# R5-D1 unit 71: the force-versus-resolution curve, and it does not converge

Date 2026-08-19. Branch `claude/r5-research`. Engine: **WARPMPM**
(`renders/yaris_render_s1/sim_standing.py:10-12`), not Genesis.

**Result: surge force does not converge to any tolerance the literature would
accept, and the within-grid noise floor is small enough to prove that is real
rather than scatter.**

---

## 0. TWO CORRECTIONS TO THE TASK PREMISE, both READ

**(1) It is FOUR grids, not six.** `sacct -j 918350,918351` returns:

```
918350   r6rep_g160   PENDING   00:00:00   Unknown
918351   r6rep_g192   PENDING   00:00:00   Unknown
```

The g160 and g192 sbatch files exist (`$WORK/sb_r6_g160.sbatch`,
`sb_r6_g192.sbatch`) but **have not run**, and no output directory exists for
either. The completed set is **g48, g64, g96, g128**, jobs 918250/918249/918248/918247.

**(2) The runs are at mass 2337 kg, not the canonical 1100 kg.** Every
`summary.json` carries `"label": "rep_g<N>_m2337_<r>"` and `mass_kg: 2337.0`.
That is the *heaviest* AR&R class, so this curve is not directly comparable to the
canonical `g*_m1100` block.

**Nothing else confounds.** All 20 runs are identical in mass, depth, velocity and
length: `mass=2337.0  depth=0.3  vel=1.5  frames=90`, verified across all 20
summaries.

## 1. Method

**Force is not stored.** No `metrics.csv` in this repo or on Vista carries a force
column; the header is
`t,dx,dy,dz,dmag,yaw_deg,pitch_deg,roll_deg,vx,vy,vz,vmag,wx,wy,wz` (READ). So
surge force is derived from rigid-body kinematics:

```
F_surge(t) = mass_kg * d(vx)/dt      via np.gradient(vx, t)
impulse    = integral |F_surge| dt   via np.trapezoid
```

This is the same construction `simulation/failure_modes.py:127-128` already uses
(`force = mass_kg * accel`, `accel = np.gradient(vel, t)`), so it is the project's
own convention, not one I invented (READ).

**SETTLE LENGTH: 8 frames, and they are PRE-ROLL.** `sim_standing.py:235-237` runs
`for _ in range(settle_frames): ... s.step(...)`, and only *afterwards* does `:240`
apply the velocity kick, `:244` set `time = 0.0`, and `:246` append frame 0 (READ).
**So all 90 recorded frames are post-settle** and the settle transient is not inside
this measurement window.

**The startup spike is excluded, and the exclusion is measured, not assumed.**
`peak |F|` over all frames occurs at **frame 0 in 20 of 20 runs**. That is the
impulsive kick at `:240` differentiated at the array boundary, not a flood load. It
decays about 90% by frame 2:

```
g48   32552  19610   3668   1043   3296   3631      (frames 0-5, |F| in N)
g64   31240  16091   1564   3487   2516   2003
g96   26779  14487   1068   4516   4682   4638
g128  20469  10013    425   1209   2791   3468
```

The physical first peak lands at **frames 3 to 7**. So I report both, and the
startup-excluded column is the physically meaningful one.

## 2. The curve, N = 5 per grid

```
 grid    dx (m)      peak |F| all (N)     peak |F| ex-startup (N)      impulse (N.s)
   48   0.19629    32551.7 +/-     0.0        4674.0 +/-     0.1    3040.0 +/-  27.7
   64   0.14721    31240.3 +/-     0.2        3498.1 +/-    25.8    2553.2 +/-  47.5
   96   0.09814    26808.3 +/-    27.2        4725.2 +/-    93.1    2247.4 +/-  30.4
  128   0.07361    21027.7 +/-   538.6        3778.5 +/-    35.5    1731.3 +/-  49.0
```

**Percentage change between successive levels**, which is what the review asks for
and says is rarely reported:

```
     step        peak all    peak ex-startup    impulse
 g48 -> g64        -4.0%          -25.2%        -16.0%
 g64 -> g96       -14.2%          +35.1%        -12.0%
 g96 -> g128      -21.6%          -20.0%        -23.0%
```

**Within-grid spread as a percentage of the mean, N = 5. This is the noise floor:**

```
 g48    peak_all 0.0%    peak_ex 0.0%    impulse 0.9%
 g64    peak_all 0.0%    peak_ex 0.7%    impulse 1.9%
 g96    peak_all 0.1%    peak_ex 2.0%    impulse 1.4%
 g128   peak_all 2.6%    peak_ex 0.9%    impulse 2.8%
```

## 3. Verdict: it does not converge, and the noise floor is what makes that a result

**Against the review's stated 5-10% tolerance: 8 of the 9 successive changes exceed
10%.** The single exception is `peak all, g48 -> g64` at -4.0%, and it is immediately
followed by changes **3.5x and 5.4x larger**. A converging sequence has *shrinking*
successive differences; this one grows.

- **peak, all frames:** monotone decreasing, but the step size **increases**
  (-4.0, -14.2, -21.6). Diverging, not converging.
- **peak, startup excluded:** **non-monotone**, -25.2 then **+35.1** then -20.0. It
  does not even have a consistent sign.
- **impulse:** monotone decreasing with no shrinkage (-16.0, -12.0, -23.0).

**The reason this is publishable rather than merely negative:** the within-grid
spread over N = 5 is **0.0% to 2.8%**, while the between-grid changes are **4% to
35%**. The signal is **5x to 12x the noise floor**, so the non-convergence is a
property of the discretisation, not repeat scatter. **That is a clean negative with
error bars**, which is exactly what recommendation 3 of the review says is currently
rare.

**No GCI or observed order can be computed from this ladder either**, and for a
reason independent of the above: the refinement ratio is **not constant**
(0.19629/0.14721 = 1.333, 0.14721/0.09814 = 1.500, 0.09814/0.07361 = 1.333). An
apparent order `p` requires a constant ratio. This matches
`.claude/checks/physics_gates_literature.py:60-64`, which returns "cannot compute
apparent order p" for exactly this reason (READ).

## 4. What this does and does not support

**Supports (READ):** at 2337 kg, 0.30 m, 1.5 m/s, with 8 pre-roll settle frames, the
surge force extracted from rigid-body kinematics changes by more than 10% between
every successive grid pair but one, in a direction that is monotone for two measures
and sign-changing for the third, with a repeat noise floor under 3%.

**Does NOT support (INFERRED, and I am not claiming it):** that the *verdicts* are
unconverged. Register item 5 already records the binary verdict as grid-invariant
across g48/g64/g96 while displacement is not, and this curve is about force, not
verdict. A force that is unconverged and a verdict that is stable are compatible.

**Does NOT support:** any statement about the canonical 1100 kg configuration. This
is 2337 kg (section 0).

## 5. Status

UNVERIFIED:
1. **I did not open a single `rollout.npz`.** Everything here is from `metrics.csv`
   and `summary.json`. The solver's `sdf_wrench` accessor, which would give a
   *directly computed* contact force rather than one differentiated from velocity,
   is **not used**. That is the obvious next step and it would be a genuinely
   independent second measurement of the same quantity.
2. `F = m dv/dt` gives the **net** force on the rigid body, which includes buoyancy,
   contact and gravity, not the isolated hydrodynamic drag the review discusses.
   The two are not the same quantity and I have not decomposed them. Project memory
   records that this net force **cannot** be decomposed in this coupling path.
3. Lift and moment are **not** reported. The review asks for drag, lift and moment;
   I have surge only. `vz` and the `wx,wy,wz` columns would give the other two.
4. N = 5 at four grids is a small sample; the spreads are `ddof=1` sample standard
   deviations, not confidence intervals.
5. The startup-exclusion cut at frame 2 is justified by the decay profile in
   section 1 but is still a choice; peak_ex would move if the cut moved.

## 6. Reproduce

```python
import numpy as np, json, glob
for s in sorted(glob.glob("r6_rep_g*/rep_*/summary.json")):
    d = json.load(open(s))
    a = np.genfromtxt(s.replace("summary.json","metrics.csv"), delimiter=",", names=True)
    F = d["mass_kg"] * np.gradient(a["vx"], a["t"])
    peak_all, peak_ex = np.max(np.abs(F)), np.max(np.abs(F[2:]))
    impulse = np.trapezoid(np.abs(F), a["t"])
```

Inputs pulled read-only from Vista `$WORK/r6_rep_g{48,64,96,128}_*/rep_*/`:
20 `metrics.csv` + 20 `summary.json`, 295,974 bytes tarred. **No run was executed
and nothing on Vista was modified.**
