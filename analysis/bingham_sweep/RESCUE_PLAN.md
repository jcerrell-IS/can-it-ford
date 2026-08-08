# Bingham sweep, rescue plan

Written 2026-08-07 18:1x. **Nothing in this plan has been executed.** No commit, no
staging, no `.gitignore` edit, no delete. This file is the preparation only.

Every number below was verified live on 2026-08-07 against the files in this directory,
not carried from a summary. Where a value came from another file, the file and line are
named so it can be re-checked.

---

## 1. What is being rescued

The sweep is **complete and internally consistent**, and it currently exists in exactly
one place: an untracked worktree on a branch that has never been committed. If the
worktree is pruned or the branch dropped, all of it disappears.

**The headline result, verified from `bingham_sweep_results.csv`:**

- **All 11 ladder points return NO-FORD.** `verdicts: ['NO-FORD']`, one distinct value.
- `final_disp_mag_m` spans **0.519301 to 0.659482 m**.
- The minimum is **10.39x** the 0.05 m DRIFT_THRESHOLD.
- The largest rheology effect is **-21.26 percent** at `tau_y = 100 Pa`.

**Read this claim precisely.** The verdict is invariant across the ladder *because the
operating point sits an order of magnitude away from the threshold*, not because
rheology is negligible. Displacement moves 21 percent at the extreme. The correct
statement is "Newtonian water is the simplest sufficient model **for this verdict at
this operating point**". It does **not** transfer to an operating point near the
threshold, and it must never be written as "rheology does not matter".

## 2. Two results not in `bingham_sweep_results.csv`

Both are worth preserving in text, because both survive even if the `.npz` files are
excluded from the commit.

**(a) The Mac run is bit-exact deterministic.** `_replicate/` is a re-run of the control
and is absent from `collect_bingham_sweep.py`'s `ORDER`, so it never reaches the table.
Compared live:

```
final_disp_mag_m   control   = 0.6594815254211426
                   replicate = 0.6594815254211426     identical to all 16 digits
```

Every physics field matches (`tau_y_pa`, `water_eta`, `mass_kg`, `depth_m`,
`velocity_ms`, `n_grid`, `frames`, `n_water`, `n_vehicle`, `substeps`). Only `label`
differs. `determinism_identical` is `True` in both.

**(b) Cross-venue fidelity is better than the canonical run's own internal agreement.**

| comparison | value |
|---|---|
| control vs canonical `summary.json` (0.6585370302200317) | **+0.1434 percent** |
| control vs canonical `rollout.npz` (0.637019) | +3.5262 percent |
| canonical `summary.json` vs its own `rollout.npz` | +3.3779 percent |

The last row is CLAUDE.md item 5: the canonical g64_m1100 run **disagrees with itself**
by 3.38 percent between its two stored displacement measures. The Mac control reproduces
the canonical `summary.json` measure to 0.14 percent, roughly **24x tighter than the
canonical run's own internal inconsistency**. State it against `summary.json` and say so
explicitly; do not write "reproduces the canonical run" without naming which of the two
canonical numbers is meant.

## 3. A new observation: P-2 is rheology-sensitive even though the verdict is not

Gate limit read live from `renders/yaris_render_s1/gates.py:147-148`, which tests
`s["passthrough_max_frac"] < 0.10` (strict `<`).

```
tau0p0_control    tau_y=  0.0   0.10646  FAIL
tau0p1            tau_y=  0.1   0.10683  FAIL
tau1p0            tau_y=  1.0   0.10660  FAIL
tau3p0            tau_y=  3.0   0.10660  FAIL
tau10p0           tau_y= 10.0   0.10584  FAIL
tau30p0           tau_y= 30.0   0.10232  FAIL
tau100p0          tau_y=100.0   0.08741  PASS
etacoup_tau3p1    tau_y=  3.1   0.10664  FAIL
etacoup_tau40p0   tau_y= 40.0   0.09719  PASS
hb_tau10_K5_n0p8  tau_y= 10.0   0.10573  FAIL
hb_tau0_K5_n0p8   tau_y=  0.0   0.10592  FAIL
                                          2 pass / 9 fail
```

The control's 0.10646 is consistent with CLAUDE.md item 7, which records g64_m1100 as one
of the seven canonical runs that fail P-2, and with `collect_bingham_sweep.py:23`
(`CANON_PASSTHROUGH = 0.10670498480368847`, a -0.23 percent difference).

So raising yield stress **monotonically reduces water passthrough** and pushes two points
across the containment gate, while leaving the FORD/NO-FORD verdict untouched. That is a
statement about the numerical containment gate, not about physics, and P-2 is a
self-consistency check rather than a physics validation (CLAUDE.md item 6). Do not
present it as evidence that a yield-stress model is more physically correct.

## 4. Why a rescue is needed: the size problem

```
13 .npz files                     769.4 MB      12 rollout.npz + 1 combined.npz
everything else (40 files)          1.17 MB     <- the entire scientific content
total                             770.6 MB
```

`git check-ignore` confirms **nothing here is ignored**. `.gitignore:14` covers
`renders/`, which does not match `analysis/bingham_sweep/`, and there is no `*.npz` rule
anywhere in the repo. A commit of this directory puts **771 MB into history permanently**,
removable only by a filter-repo pass.

Note the asymmetry: **99.85 percent of the bytes carry none of the conclusions.** Every
number in sections 1 to 3 above comes from `summary.json`, `metrics.csv` and
`bingham_sweep_results.csv`. Measured live: the text-only payload is **0.47 MB across 39
files**, and the mp4 is a further 0.69 MB on its own. The `.npz` rollouts are raw particle
trajectories, needed only to re-render or re-derive.

## 5. Proposed split

**Preserve (about 1.17 MB, 40 files + 2 scripts + 1 doc edit):**

- `<tag>/summary.json` and `<tag>/metrics.csv` for all 12 run directories
- `<tag>.log` for all 11 logged points, plus `_sweep_driver.log`
- `bingham_sweep_results.csv`, `README.md`, this file
- `analysis/collect_bingham_sweep.py`, `analysis/run_bingham_sweep.sh`
- the modified `docs/limitations.md` (+41 lines, the L-11 CPIC negative result)
- `tau0p0_control/tau0p0_control.mp4` (0.69 MB), **but see the fps defect in section 8**

**Exclude (769.4 MB, 13 files):** every `.npz`.

## 6. Proposed mechanism, and why not the obvious one

**Do NOT edit root `.gitignore`.** It is a tracked file, it is shared across every
branch, and the live-state hook reports 3 concurrent sessions in this repo. CLAUDE.md
records an active breach on 2026-08-07 in which one session committed another's
uncommitted edits. A dirty tracked `.gitignore` is exactly the file that gets swept up.

**Use a scoped `.gitignore` inside this directory instead:**

```
analysis/bingham_sweep/.gitignore
--------------------------------
# Raw particle rollouts, 59.2 MB each, 769.4 MB total. Regenerable, see RESCUE_PLAN.md.
# The conclusions live in summary.json / metrics.csv / bingham_sweep_results.csv.
*.npz
```

Verified safe: no `.gitignore` currently exists under `analysis/` or
`analysis/bingham_sweep/`, and no `*.npz` rule exists anywhere in the repo, so there is
nothing to conflict with and no negation to override. It is a **new untracked file**, so
there is no overwrite risk. It is scoped to this directory only, so it cannot affect any
other workstream. And it travels with the branch when committed, unlike a local exclude.

If you want the 771 MB neutralised **right now** without creating any file that could be
committed, the alternative is `.git/info/exclude`, which is never tracked. Confirmed it
lives at `/Users/josie/can-it-ford/.git/info/exclude` (shared common git dir) and already
carries `.claude/worktrees/`, which is why root's `git status` never showed any of this.
That pattern does not fire inside the worktree, where paths are relative to the worktree
root. A local exclude does not travel to Vista, LS6 or the branch, so it is a stopgap,
not the answer.

## 7. Exact commands, to run only after approval

Never `git add -A`, `git add .`, or `git commit -a` in this repo (CLAUDE.md standing
rule). Stage explicit paths.

```bash
cd /Users/josie/can-it-ford/.claude/worktrees/bingham-sweep-2026-08-07

# 1. scoped ignore
printf '%s\n' \
  '# Raw particle rollouts, 59.2 MB each, 769.4 MB total. Regenerable, see RESCUE_PLAN.md.' \
  '# The conclusions live in summary.json / metrics.csv / bingham_sweep_results.csv.' \
  '*.npz' > analysis/bingham_sweep/.gitignore

# 2. prove the exclusion works BEFORE staging anything
git status --porcelain -uall | grep -c '^??'          # expect 43, was 55
git check-ignore -v analysis/bingham_sweep/tau0p0_control/rollout.npz   # expect a match

# 3. stage explicit paths only
git add analysis/bingham_sweep/.gitignore
git add analysis/bingham_sweep/README.md analysis/bingham_sweep/RESCUE_PLAN.md
git add analysis/bingham_sweep/bingham_sweep_results.csv
git add analysis/bingham_sweep/*.log
git add analysis/bingham_sweep/*/summary.json analysis/bingham_sweep/*/metrics.csv
git add analysis/collect_bingham_sweep.py analysis/run_bingham_sweep.sh
git add docs/limitations.md

# 4. prove no large binary is staged
git diff --cached --numstat | awk '$1=="-"{print "BINARY: "$3}'
git diff --cached --name-only | while read -r f; do
  [ -f "$f" ] && stat -f "%z %N" "$f"; done | sort -rn | head -5
```

Step 4 is the gate. If anything above ~1 MB appears other than the mp4, stop.

## 8. Two defects to resolve before committing, not after

**(a) The mp4 has the wrong frame rate.** Both `.npz` files record `fps = 30`.
`ffprobe` reports the mp4 at `r_frame_rate=24/1`, `duration=3.750000`, 90 frames.
`render_frames.py:232` defaults `--fps` to 24 and was left at default. The preview
therefore plays 25 percent slow, and anything timed off it is wrong. Re-render at 30 fps
before committing, or do not commit the mp4. The source `combined.npz` is still on disk,
so this is cheap now and impossible once the npz is dropped.

**(b) Decide whether the mp4 belongs in git at all.** It is 0.69 MB, which is 60 percent
of the entire preserved payload. It is regenerable from `combined.npz`, which is itself
regenerable from `rollout.npz`. Committing it is defensible as the one visual artifact;
excluding it is equally defensible. This is a judgement call, not a correctness issue.

## 9. Regenerating what gets excluded

`combined.npz` is fully reconstructable from `rollout.npz` and is a render cache, not a
result. Verified by shape arithmetic:

```
rollout.npz  water                 (90, 48367, 3)
rollout.npz  veh_particles_scene0      (8905, 3)   rest pose
rollout.npz  R                      (90, 3, 3)     per-frame rotation
rollout.npz  t                         (90, 3)     per-frame translation
                                   ------------
combined.npz positions            (90, 57272, 3)   48367 + 8905 = 57272 exactly
combined.npz is_vehicle              (57272,) bool
```

The `rollout.npz` files themselves regenerate from
`renders/yaris_render_s1/run_bingham.py` via `analysis/run_bingham_sweep.sh`, on Mac
CPU-ARM, warp 1.16.0, no CUDA. Wall-clock from the log mtimes is roughly 1 to 2 minutes
per ladder point.

**Caveat on regeneration:** re-running reproduces these numbers only on the same venue.
`README.md` records that the pip-installed `warpmpm` is **not** the code that produced the
17 gated runs (three divergences in the vehicle path), and that `run_bingham.py` binds
`renders/yaris_render_s1/vehicle_live.py` as `warpmpm.vehicle` to compensate. That binding
is load-bearing. A regeneration without it will not reproduce these results.

## 10. Caveats that must travel with any use of these numbers

Carried forward from `README.md` because they constrain what may be written:

- **These are NOT canonical.** Never merge into `data/all_runs_inventory.csv`,
  `renders/yaris_render_s1/gates_results_all_runs.json`, or any figure describing the
  17 gated runs.
- **The sound speed is wrong by two orders of magnitude.** `bulk_modulus = 1.5e5` gives
  `c = 12.845 m/s` against water's 1481 m/s, and `tau_y_crit` scales linearly with sound
  speed, so every threshold here shifts under a physical sound speed. Isik and He 2022 is
  the citable result that artificial sound speed can qualitatively flip a rigid-body
  outcome. Never swept here.
- **Regime labels are uncited.** "turbid", "hyperconcentrated", "mud flow" in
  `analysis/bingham_cfl_crossover.py` are indicative only. They need a citation pass
  before entering the paper.
- **A tau_y-only sweep at fixed eta is not fully physical.** Real sediment loading raises
  both. The two `etacoup_*` points address this, but the pairing itself is unsourced.
- **Resolution is unconverged.** 4 water particle layers, 2 grid cells per flow depth,
  against a rule of thumb of about 10 particles per depth. CLAUDE.md L-3.
- **Whether Vista's solver matched this one is not established from this machine.** The
  solver path is byte-identical between the local install and
  `third_party/mpm-engine-544c93dd-solver-core/`, but Vista was not checked. Open.

## 11. What was deliberately not done

- Nothing committed, staged, or pushed.
- Root `.gitignore` not touched, for the concurrency reason in section 6.
- `analysis/bingham_sweep/.gitignore` **not created**; it is drafted in section 6 only.
- No `.npz` deleted. The 771 MB is still on disk and must stay there until the mp4 fps
  defect in section 8 is resolved, because the source data is needed to re-render.
- The empty `renders_preview/` directory left behind in this worktree by the 18:03
  reconciliation was not removed; removing it is a delete and needs explicit confirmation.
