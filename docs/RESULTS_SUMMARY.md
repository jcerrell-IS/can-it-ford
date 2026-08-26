# Four findings worth defending, each with its number, its command, and its limitation

Written 2026-08-26. Three of the four were re-measured today and one was not; the difference is
marked on each. If you are preparing to defend this work in an interview, these are the four, and
the limitation matters as much as the number.

---

## 1. CORRECTED. The verdict is grid-invariant only inside the published ladder, and it breaks outside it.

**This section said "the binary verdict is grid-invariant" on 2026-08-26 and that was an
overclaim.** It was true of the nine published runs and false of the ladder that has since been
run. Corrected the same day against `docs/HANDOFF_ROUND_7_2026-08-18.md` and commit `ef92709`.

**What is still true.** Across n_grid 48, 64 and 96 at fixed depth and velocity,
`final_disp_mag_m` moves non-monotonically and the direction depends on mass, and **all nine of
those runs return NO-FORD**. [CONFIRMED 2026-08-26]

| mass | g48 | g64 | g96 | 48 to 64 | 64 to 96 |
|---|---|---|---|---|---|
| 1100 kg | 0.350717 | 0.658537 | 0.268638 | **+87.8%** | **-59.2%** |
| 1609 kg | 0.256830 | 0.314076 | 0.155959 | +22.3% | -50.3% |
| 2337 kg | 0.187542 | 0.135559 | 0.089439 | -27.7% | -34.0% |

**What breaks it, and it is the most important result in the project.** Job 918350 extended the
ladder for the heaviest vehicle, five repeats per rung, all bit-distinct:

| grid | water layers | verdict (N=5) | margin |
|---|---|---|---|
| g48 | 3 | SLIDE 5/5 | 8 |
| g64 | 4 | SLIDE 5/5 | 6 |
| g96 | 6 | SLIDE 5/5 | 0 to 1 |
| g128 | 8 | SLIDE 5/5 | 0 |
| **g160** | **10** | **STUCK 5/5** | **-3** |

`dx` 0.05889 m, `n_water` 906,806. **g160 is the first grid reaching about 10 particle layers
across the flow depth, which is the only depth-based convention the literature offers** (Reis et
al. 2021, `10.1016/j.engstruct.2021.113280`). The flip lands exactly there, and **the prediction
was written into the job's own sbatch header before the run.**

`g192` is a second STUCK (`5c32ff9`), so the flip is not a single rung.

**So the published 16 SLIDE / 1 STUCK headline does not survive refinement to the resolution the
literature asks for**, at least for m2337, which was already the most fragile case.

**A second thing the flip fixes.** The `sustain_frames` fragility vanishes at g160: with 0 joint
frames it is STUCK at every threshold tested. Under-resolved gives a fragile SLIDE that a
one-integer threshold change can flip; resolved gives a robust STUCK.

**The confound, and how far it has been closed.** The ladder is a sequence of different tanks:
`span = lim*(1 - 8/n)` gives 7.8515 m at g48 against 8.9506 m at g160, so the tank is **largest
exactly where the flip happens**, and tank growth and resolution are co-directional. The
pinned-span control (`27f9b58`) bounds the tank effect by exact permutation over all C(10,5)=252
splits: at +32.94 percent tank the drift difference is **+3.5 percent, p=0.0079**, and at
+21.7 percent tank it is indistinguishable from zero, with the same-tank null control behaving
correctly at p=0.9206. **+3.5 percent against a 5.14x resolution effect**, so the confound is
real, bounded and small.

**The bound does not fully discharge the caveat, and do not pretend it does.** The control bounds
the tank effect on **drift**, and that commit says plainly that drift does not order the verdict.
Until a pinned-span run reproduces the verdict flip itself, write **"the verdict flips under a
refinement that also enlarges the tank"**, never "the verdict flips under refinement".

---

## 2. Fifteen of seventeen runs violate the weak-compressibility rule they are built on

**The number.** Every gated run uses a single artificial sound speed, **12.845 m/s**. The
weak-compressibility convention is that sound speed should be at least 10x the flow velocity, so
that the Mach number stays near 0.1. **15 of 17 runs fail that**. [CONFIRMED 2026-08-26]

```bash
python -c "
import csv
r=list(csv.DictReader(open('data/all_runs_inventory.csv')))
print(sorted({float(x['sound_speed_ms']) for x in r}))
print(sum(1 for x in r if float(x['sound_speed_ms']) < 10*float(x['velocity_ms'])), 'of', len(r))"
```

**Why it is defensible.** This is a disclosed limitation with an automated gate, not a discovered
error. Isik and He 2022 show artificial sound speed can qualitatively flip a rigid-body outcome,
which makes this the single most consequential unswept parameter in the study, and it is named as
such rather than buried.

**The limitation.** Naming a limitation is not bounding it. Nothing here establishes which way the
outcome would move at a higher sound speed, and the sweep that would answer it has not been run at
the gated configuration.

---

## 3. Twelve of seventy L1 cells change verdict on the class label alone, and some land exactly on the cap

**The number.** In the 70-condition analytical sweep, **12 cells** return different verdicts under
the small-passenger, large-passenger and large-4WD limit sets. FORD counts are 14, 19 and 26
respectively. [CONFIRMED 2026-08-26]

```bash
python -c "
import csv
s=list(csv.DictReader(open('data/scenario_sweep.csv')))
print(sum(1 for r in s if len({r['L1_verdict_small_passenger'],
      r['L1_verdict_large_passenger'],r['L1_verdict_large_4wd']})>1), 'of', len(s))"
```

**The sharper version, measured today.** Several cells land on a class cap with a margin of
**exactly 0.000000 m2/s**: depth 0.1 at v 3.0 and depth 0.2 at v 1.5 both give `L1_haz` = 0.300000
against the 0.30 small-passenger cap; depth 0.3 at v 1.5 gives 0.450000 against the 0.45 cap; depth
0.2 at v 3.0 gives 0.600000 against the 0.60 cap. **At those cells the verdict is decided by the
direction of a floating-point comparison, not by physics.**

**Why it is defensible.** It shows the criterion's own class assignment, not the physics, produces
a large share of the disagreement, and the project caught this in its own poster: 12 of the 23
reclassified cells came from evaluating a 1100 kg car against its published class rather than the
Large 4WD limits.

**The limitation.** **[UNVERIFIED]** A margin of `0.0084 m2/s` appears in earlier write-ups as the
tightest class-label flip. It does **not** reproduce from `data/scenario_sweep.csv`, where the
tightest margins are exactly zero. Either it comes from a different dataset or it is stale. Do not
quote it until its source is found.

---

## 4. The project's own settle length is contradicted by all of its own runs

**The number.** `sim_standing.py` uses `settle_frames=8`. Applying a stationarity test to all 25
local runs, **25 of 25 need more than 8 frames discarded**: minimum 29, median 48, maximum 80, out
of 91 total frames. Effective sample size is 2.9 to 11.0, so any uncertainty computed from N=91 is
overstated by roughly 3x to 5x. **[DOC, from CLAUDE.md, NOT re-run in this session.]**

```bash
python analysis/settle_audit.py      # re-run before quoting; no GPU needed
```

**Why it is defensible.** It is a self-audit that contradicts a published choice, reached by a
different route from the earlier settle-length sweep, so the two corroborate rather than repeat.
Use `effective_sample_size`, never the frame count.

**The limitation, and it is the interesting part.** **Do not remove the transient before a SLIDE
verdict.** Incipient motion is an event, not a steady state. Removing the transient drops SLIDE
from 21 of 24 runs to 5 of 24 and would silently contradict the published 16 SLIDE / 1 STUCK. So
the correct settle length for a *mean* is the wrong one for an *event*, and the published verdicts
use the full record deliberately.

---

## 5. The settled vertical force is about 1.8x analytic buoyancy, it is grid-converged, and it is not a misread

**The number.** In the moving-vehicle speed surface, `fz_settle_over_analytic` by grid
[CONFIRMED 2026-08-26, `data/r9_speed_surface.tsv`, 1251 rows]:

| n_grid | rows | min | max | mean |
|---|---|---|---|---|
| 64 | 1039 | 0.1476 | 22.5218 | 2.0994 |
| 96 | 131 | 1.6771 | 1.6899 | **1.6823** |
| 128 | 63 | 1.7581 | 1.7729 | **1.7662** |
| 160 | 18 | 1.7898 | 1.7990 | **1.7944** |

```bash
python3 -c "
import csv,collections
rows=list(csv.DictReader(open('data/r9_speed_surface.tsv'),delimiter='\t'))
by=collections.defaultdict(list)
for r in rows:
    try: by[r['n_grid']].append(float(r['fz_settle_over_analytic']))
    except ValueError: pass
for g in sorted(by,key=int):
    v=by[g]; print(g,len(v),min(v),max(v),sum(v)/len(v))"
```

**Read this carefully, because the obvious reading is wrong.** At g64 the ratio is scattered over
two orders of magnitude, which is the under-resolved regime. From g96 up the spread collapses to
under one percent within a rung, so the quantity **is grid-converged**. It converges to about
1.8, not to 1.0.

**It is not an instrument error.** Commit `3f8fa42` closes that family: a third accessor,
`control_volume_force`, reads `cauchy()` and `vol()` only and shares no code, no grid nodes and no
knowledge of the collider with `sdf_wrench`. Three well-conditioned boxes agree with `sdf_wrench`
to **0.9 to 1.9 percent** against a verdict pre-registered before the run. The accessor is
exonerated, and **the fluid really is pushing that hard**.

**It is not volumetric locking either.** That hypothesis had a named falsifier and the falsifier
fired: a particles-per-cell sweep over a 19x span returned a log-log slope flat at 0.41 sigma,
where locking would demand `PPC^-2`. Refuted on its own signature (`3f4c1ec`). **Anyone
reintroducing the locking explanation must carry that refutation with it.**

**Where the excess actually lives.** The disturbance is confined to the floor; the bulk pressure
field is hydrostatic. Read from the pinned solver rather than from the literature (`c621539`):
`add_plane` registers a **grid** collider, and the boundary kernel projects out the normal
velocity component and writes it back to a grid node. **It writes velocity onto a grid node. It
never writes pressure, and there is no boundary particle of any kind.** A whole-tree search for
dummy particles, ghost particles, mirror particles, pressure extrapolation or any free-surface
test returns nothing.

**So what is the honest claim?** Three things, and they must travel together:

1. The force is measured correctly. Three independent accessors agree.
2. The comparison denominator is a **static Archimedes value**. Comparing a dynamic,
   floor-bounded, flowing case against it is not a validation, and a ratio of 1.8 is not by
   itself an error.
3. The excess sits in a floor boundary treatment that writes velocity and not pressure, and
   **whether that treatment is physically correct is open.** It is not resolved by refinement,
   because the ratio is already converged.

**The contrast that matters.** The SDF-collider coupling path validates against analytic
buoyancy to **7.3 to 7.7 percent** (`c1sdf_sdf_g64` at -7.67, `c1sdf_sdf_g96` at +7.28). The
free-rigid material-8 path, which is what **all 17 gated runs use**, is the one showing the 1.8x
ratio. Those are two different coupling architectures in the same solver, and the validated one
is not the one the published results run on.

---

## The finding that is not here

**No reconstruction has ever entered a simulation.** The reconstruct-to-decide front end is
designed and not built. Do not present the splat work and the simulation work as one pipeline.
They are two stages that are not connected, and the poster says exactly that under Scope.
