# D4 job A: the brake-state flip is MEASURED, and the repeats are not deterministic

2026-08-17. Branch `claude/r5-physics`. **Job 917797**, `SUMMARY runs=23 failed=0`,
`ALLDONE`, stderr **0 bytes**, elapsed 00:10:11 on one `gh-dev` node (`c642-032`).
This is the first GPU physics ever produced on this branch.

Claim tags: **[read]** live from a primary source, **[derived]** computed here,
**[unreviewed]** not yet adversarially checked.

Every number below was measured at **250 frames**, settle **8** (constructor-only, there
is no `--settle-frames` flag), **trimesh 4.12.2**, runtime engine git **627367e**, driver
`sim_standing.py` sha256 `4696c3b2...10d9`.

---

## 1. Attribution, because three jobs shared one output directory

| id | outcome |
|---|---|
| 917786 | dead in 3 s, all 23 runs `ModuleNotFoundError: trimesh`, **wrote no run directories** |
| 917796 | dead, all 23 runs `cannot import name 'solidify_watertight'`, cancelled 16:44:27, **wrote no run directories** |
| **917797** | **COMPLETED, 23/23 succeeded** |

All three targeted a fixed `d4_jobA`, which was a genuine silent-overwrite hazard. It did
not fire, and that is checkable rather than asserted **[read]**: 917796 ended at
**16:44:27** and every byte in the directory was written from **16:45** onward; `jobA.err`
is 0 bytes so none of 917796's ImportError text survives; and both dead jobs produced zero
run directories because every run exited 1 before writing. **Everything here is 917797.**
`OUT` is now keyed by `${SLURM_JOB_ID}` so the hazard cannot recur.

## 2. A1: the control holds and the inferred flip is now measured

Graded with `simulation/failure_modes.py`, **not** by displacement magnitude. SLIDE
requires `(surge_drift >= 0.05 m) AND (surge_speed >= 0.05 m/s)` sustained over
`sustain_frames = 3`. Classified at `mass_kg = 1100.0`, `ssf = 1.42` **[read]**.

| mu | classifier verdict | onset | `final_disp_mag_m` | wall |
|---|---|---|---|---|
| **0.55** | **STUCK (stable)**, no criterion tripped | n/a | 0.028966 | 43 s |
| 0.30 | SLIDE, +128.23% past criterion | frame 8 (t=0.2667 s) | 0.072001 | 16 s |
| **0.0250** | **SLIDE**, +1329.06% past criterion | frame 6 (t=0.2000 s) | 0.137869 | 15 s |

- **The control holds.** mu = 0.55 reproduces **STUCK**, so the job is not void.
- **The flip is MEASURED, not inferred.** mu = 0.0250 gives SLIDE. The branch has carried
  this as INFERRED throughout; it can now be stated as measured, with the caveats below.
- **mu = 0.30 confirms nothing and is reported as such.** It was logged INDETERMINATE
  **in advance** because the bracket (0.369, 0.739] straddles this run's 0.5 m/s. It came
  out SLIDE. That does not promote it, and the whole reason for fixing criteria
  beforehand is that this outcome cannot be narrated into agreement afterwards.

**Displacement is not the verdict, and mu = 0.55 proves it.** Its max surge drift is
**0.0569 m**, which *exceeds* the 0.05 m `slide_m` threshold, yet the verdict is STUCK
because the sustained-speed conjunction never fired **[derived]**. Anyone grading these
runs on `final_disp_mag_m` would have called it the other way.

**Not a like-for-like reproduction of the published STUCK:** these are 250-frame runs and
the canonical run is 91 frames.

## 3. A2: ten repeats, and they are not deterministic

Fixed configuration, no seed flag exists, N = 10 per case **[derived]**:

| case | max drift mean | range | spread | final drift spread | divergence onset |
|---|---|---|---|---|---|
| `g96_m2337` | 0.086249 m | [0.085223, 0.087426] | **2.203e-03 m** | 3.079e-03 m | **frame 1** |
| `sweepV_g64_v0p5` | 0.058910 m | [0.057807, 0.059860] | **2.052e-03 m** | 2.793e-03 m | **frame 1** |

Reported as the manifest requires: N and range, never a single draw, and **frequency, not
pass/fail**. Against `slide_m = 0.05 m`, max drift falls below it in **0/10** repeats for
both cases.

**Divergence begins at frame 1 in both cases**, growing from 2.6e-05 m to 3.1e-03 m
(`g96_m2337`) and from 4.9e-07 m to 2.8e-03 m (`v0p5`). So the runs are reproducible to
about **2 to 3 millimetres over 250 frames**, not bitwise.

**Do NOT compare this to the 0.52 to 1.69 m determinism floor** in the R7 record. That
floor was measured at g128 in a different scene with a rigid particle body; these are g96
and g64 with the canonical driver. Different scene, different resolution, and the
comparison would be the exact "one source cited twice" error the project's rules forbid.

**`sweepV_g64_v0p5`'s mean max drift is 0.0589 m, above the 0.05 m threshold in all ten
repeats**, which is consistent with A1's mu = 0.55 STUCK at 0.0569 m and reinforces
section 2: this STUCK verdict lives entirely on the sustained-speed conjunction, not on
displacement staying small.

## 4. `determinism_identical` is a load-time check, and its name oversells it

Every `summary.json` in all 23 runs carries `"determinism_identical": true`, while
section 3 shows the trajectories diverging from frame 1. **That is not a contradiction**,
and it was checked before being reported as one **[read]**, `sim_standing.py:389`:

```python
det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
```

It loads the hull twice and compares particle count and `grid_lim`. It is a **mesh-load
reproducibility check** and says nothing whatever about the simulation trajectory.

It is still a trap, and the same one this branch keeps finding: **a field whose name
promises more than it measures.** A reader of `summary.json` would reasonably conclude the
runs are deterministic. They are reproducible to millimetres, and the field cannot see the
difference. This is the sixth instance of the pattern collected in `START_HERE` 5b.

**trimesh 4.12.2 is load-bearing for exactly this field**: `np.random.seed` still controls
sampling on 4.x and is a **silent no-op** on 5.x. On an upgrade `det_ok` would start
failing, or worse, keep passing while the sampling drifted. State the trimesh version
beside any A2 spread, as with settle length.

## 5. Job C, re-costed as instructed

**The drop rule is retired because its premise was removed, not because I changed my
mind.** C was dropped because "its primary criterion cannot be evaluated until the Kramer
`/s1` supplementary exists". That supplementary is now on disk, and C's criteria are
quantitative: measured first damped periods **0.7869 / 0.8093 / 0.8671 s** (N = 4 each,
spreads 0.0010 / 0.0012 / 0.0029 s) with per-drop tolerances **0.096 / 0.239 / 0.435 mm**.

**The triage order does not change.** A, then B, then C last. What changes is C's drop
*reason*: from "ungradeable" to "cost only".

**The cost cannot yet be settled from the meter, and this is a measurement failure worth
recording.** `taccinfo` reported **627 SU before and after** job 917797's completed
10:11 run, and after both dead jobs. The balance is **not a live meter**; it lags. Three
jobs including a ten-minute one did not move it, which is evidence of lag, not of free
compute. **Nobody should quote a measured SU rate from this session.**

What can be said, and it is **[derived, unreviewed]**: `sacct` reports
`AllocTRES billing=72, node=1` for 917797 at 00:10:11. If SU is charged as
`billing x hours`, that is about **12.2 SU** for job A, which would put the full 4.27
node-h queue near 307 SU and C alone near 265 SU, comfortably inside 627. That is an
inference from the TRES billing field, **not** a confirmed rate, and it should be checked
against the meter once accounting catches up.

## 6. Review status

Section 2's verdicts have been submitted to the physics-skeptic; sections 3 to 5 are
**UNREVIEWED**. The most attackable points, named so they are not skipped: whether
mu = 0.55's STUCK survives truncation to the canonical 91 frames; how close it comes to
the 3-frame sustain requirement; and whether the SLIDE onsets at frames 6 and 8 sit inside
or adjacent to the 8-frame settle transient, which if true would undermine section 2
entirely.
