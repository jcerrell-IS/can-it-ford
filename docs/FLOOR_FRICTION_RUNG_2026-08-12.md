# Floor-friction rung, 2026-08-12

Executes the rung `docs/REGIME_LADDER_RESULTS_2026-08-07.md` section 8 names and did not
run. **Rung (b) was NOT re-run**, because it is already done; see section 0.

## 0. Why this is not a rung (b) re-run

The dispatch that commissioned this work asked for rung (b), partially submerged, still
water, no planes, as an untested experiment needing a new script and about 1 GPU-hour.
All three premises are false, verified live 2026-08-12:

| premise | live state |
|---|---|
| rung (b) untested | run 2026-08-07, job `895653`, Vista `c609-141`, COMPLETED `00:01:38`, exit `0:0` |
| needs a new script | `simulation/validate_coupling_force_ladder.py:6-7` names rung (b) as "here"; `run_rung()` takes `b`, `c`, `d` |
| about 1 GPU-hour | the whole six-arm ladder cost **0.056 node-hours** |

Its result is on record at section 5.2: rung (b) g96 reads `a_late_window` **+0.608004**
against an analytic **-6.5713**, so **-9.25 percent with the sign inverted**, and its g64
arm is a discard. Re-running would re-measure a known number.

What is not known is whether that defect moves the **17 gated verdicts**. Section 8 gives
three reasons the ladder cannot yet say: ground clearance, rotation, and floor friction.
Only friction is cheap, and only friction has a stated mechanism reaching the verdicts:
section 5.3 puts any buoyancy error in this regime into the **normal force**, sliding
resistance is `mu*N`, and **16 of the 17 published verdicts are SLIDE**. With `mu = 0`
the existing ladder short-circuits exactly that route, so it could not have observed the
effect even in principle.

## 1. What was run

`simulation/coupling_validation/rung_e_floor_friction.py`, new and additive. It imports
`validate_coupling_force_ladder` read-only and swaps one module attribute so that
`enable_floor_restitution` is called with `friction=0.55` (`sim_standing.py:132`) instead
of its default `0.0`. **No ladder source was edited.** The ladder's own docstring at
`:186-188` already flagged this as the untouched third variable.

Vista node `c642-031`, 2026-08-12, on an allocation already running, so marginal SU cost
was zero. Ten arms, all `rc=0`, about 90 s of stepping total. Ladder md5
`f650d762635fb3415d2cf202f5a5c979`, **byte-identical to the revision that produced the
2026-08-07 rung b/c/d results**, so these arms and those are the same code.

Every `mu=0.55` arm is paired with a `mu=0.0` control **in the same job, same node, same
revision**. The 2026-08-07 numbers are deliberately not used as the control, because
section 5.5 records g64 settle non-determinism and a cross-job comparison could not
separate a friction effect from a settle draw.

## 2. Results

| tag | mu | grid | seed | settled | `a_late_window` | travel (dx) | sub frac end |
|---|---|---|---|---|---|---|---|
| `fric_c_g64_mu000_s0` | 0.00 | 64 | 0 | **False, discard** | +0.071557 | -0.24890 | 0.21059 |
| `fric_e_g64_mu055_s0` | 0.55 | 64 | 0 | **False, discard** | +0.002248 | -0.24903 | 0.21064 |
| `fric_c_g64_mu000_s1` | 0.00 | 64 | 1 | **False, discard** | +0.003186 | -0.24914 | 0.21034 |
| `fric_e_g64_mu055_s1` | 0.55 | 64 | 1 | **False, discard** | +0.043383 | -0.24908 | 0.21082 |
| `fric_c_g64_mu000_s2` | 0.00 | 64 | 2 | True | -0.005596 | -0.24917 | 0.21064 |
| `fric_e_g64_mu055_s2` | 0.55 | 64 | 2 | **False, discard** | +0.028791 | -0.24853 | 0.21050 |
| `fric_c_g96_mu000_s0` | 0.00 | 96 | 0 | True | +0.0016656 | -0.24925 | 0.21414 |
| `fric_e_g96_mu055_s0` | 0.55 | 96 | 0 | True | -0.0010307 | -0.24923 | 0.21415 |
| `fric_d_g96_mu000_s0` | 0.00 | 96 | 0 | True | +0.012098 | -0.00008 | 0.25440 |
| `fric_f_g96_mu055_s0` | 0.55 | 96 | 0 | True | -0.0072401 | -0.00062 | 0.26193 |

Rungs c/e are still water; d/f add sustained inflow at 1.5 m/s and are the closest arms
to a gated run. `travel` is **vertical**; see the limitation in section 4.

## 3. What these say

**Friction does not perturb the vertical channel.** At g96 still water, the settled pair
`fric_c_g96_mu000_s0` and `fric_e_g96_mu055_s0` agree to 5 significant figures on both
vertical travel (**-0.24925 vs -0.24923 dx**) and final submerged fraction (**0.21414 vs
0.21415**). That is the expected direction, friction being tangential, and it is a clean
null: the buoyancy error documented at section 5.2 is neither amplified nor altered by
adding the gated `mu`.

**With inflow, friction moves the resting draft by about 3 percent.** `fric_d` to
`fric_f` takes final submerged fraction from **0.25440 to 0.26193**, +2.96 percent, the
largest `mu` effect anywhere in these ten arms. Direction is worth stating because it is
not neutral for the verdicts: a deeper-sitting body has more buoyancy, therefore less
normal force, therefore less `mu*N` sliding resistance. That is a hint toward SLIDE being
easier, **not** a measurement of it. `a_late_window` also flips sign between the pair,
+0.012098 to -0.0072401, but both are within 0.2 percent of an analytic -6.44 and the
body is resting, where the correct vertical acceleration is zero, so neither number
carries weight on its own (section 5.3's caveat applies unchanged).

**The g64 settle non-determinism is now quantified, which section 8 explicitly asked
for.** Across six g64 arms at three seeds, **only one settled** (`fric_c_g64_mu000_s2`).
The gate outcome is seed-dependent at fixed configuration, and it failed for all three
`mu=0.55` seeds and two of three `mu=0.0` seeds. Section 8 asked that any g64 number be
re-run several times and the spread reported before promotion. It has been, and the
answer is that **no single g64 arm of this ladder is quotable**, including the ones in
the 2026-08-07 table. g96 settled in every arm.

## 4. The limitation that bounds every claim above, stated plainly

**This harness records vertical motion only.** Verified 2026-08-12 by listing all 52 keys
of `fric_f_g96_mu055_s0.json`: `box_bottom_travel_m` and `box_bottom_travel_dx` are the
box bottom's **z** displacement (`box_bottom_at_release` 0.4173370548815001 to
`box_bottom_at_end` 0.41727590051596053), and **no horizontal displacement field exists**.

SLIDE is a horizontal criterion, `surge_drift >= slide_m` jointly with
`surge_speed >= slide_speed_ms` (`failure_modes.py:179-181`). **So this rung cannot yet
say whether the coupling defect moves a SLIDE verdict**, and nothing here should be
written up as if it could. What it establishes is narrower and still useful: adding the
gated `mu` leaves the vertical channel unchanged, and changes the resting draft under
inflow by about 3 percent.

Closing the remaining step is small and is the obvious next dispatch: record the body's
**x** displacement and speed over the measurement window, then compare the `mu=0.55` and
`mu=0.0` arms against `slide_m = 0.05 m` and `slide_speed_ms = 0.05 m/s`. Until that
exists, the SLIDE question stays open, and section 8's other two gaps, ground clearance
and rotation, stay open regardless.

## 5. Artifacts

`$WORK/can-it-ford/data/coupling_validation/` on Vista, which is persistent Lustre and
not node-local: `fric_index.json` (all ten arms), `fric_{c,e,d,f}_g{64,96}_mu*_s*.json`
(52 keys each), `fric_run.log`. Not copied into the repo; `data/` is gitignored except
for the explicitly un-ignored stores.
