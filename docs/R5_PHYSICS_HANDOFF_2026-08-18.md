# D4 HANDOFF, 2026-08-18 ~03:00 BST. Read this before `R5_PHYSICS_START_HERE.md`.

61 commits on `claude/r5-physics`, none pushed. Worktree clean at `4038ad4`.

## 1. The one thing to know

**Three of my headline claims were overturned by adversarial review in a single session,
and every time the mechanism was identical: I compared two things that were not the same
quantity.** The tables were right each time; the sentence on top of them was not.

- section 7: "a stable +60.8% remains unexplained" -> it was the contact band
- section 9: "a hit to 0.4 percentage points" -> the prediction was evaluated at a
  submergence outside its own comparison window; the real miss was 3.06 points
- the grader: reported PASS at -9.8% on a series that decays 343 N -> 48 N

Run the physics-skeptic on anything before it travels. It earned its keep four times.

## 2. State of the physics

**Established.** The dominant O(dx) inflation in the sphere scene is the SDF collider's
contact band (`mpm_solver_warp.py:2627`, gated `:2711`). Band sweep at FIXED dx, g64,
300 frames: excess **+19.89 / +51.28 / +120.66%** at band_mult 0.5 / 1.0 / 2.0, a
**100.77 point** move. Rivals predict no band dependence. **UNREVIEWED**, a skeptic pass
was commissioned and had not returned.

**Not established.** The magnitude model: `R + band` over-predicts by 12 to 28%
(measured/predicted 0.718 / 0.861 / 0.884). Do not use it as a correction factor.

**Unchanged.** No job B run is stationary. The nominal criterion refuses every run and the
pre-registered measured-surface criterion reports **FAIL**. Per CLAUDE.md item 6 this
scene is a self-consistency check against its own closed form, **not** the Kramer
comparison. That is job C, which has never run.

## 3. Highest-value next item: JOB C

It is now fully gradeable and was not before. `/s1` is on disk and reduced:
measured first damped periods **0.7869 / 0.8093 / 0.8671 s** (N=4 each, spreads
0.0010 / 0.0012 / 0.0029), per-drop tolerances **0.096 / 0.239 / 0.435 mm**. Reduce with
`simulation/r5_physics/kramer_benchmark.py`; it recomputes from the raw files every run.

Job C needs `--free` (not `--fixed`) at h0/D = 0.1 / 0.3 / 0.5, lim 2.2. The SDF cache
makes repeats cheap.

## 4. Traps that cost me time tonight

1. **`tacc_submit` auto-picks a running job.** With two allocations live it chose the
   batch job, not the idev, with `overlap_injected: false`, and the step died when that
   job ended. Target explicitly: `srun --jobid=<idev> --overlap -p gh-dev -N1 -n1 -t ...`,
   detached with `setsid nohup`.
2. **`tacc_submit` resolves its logfile path BEFORE the command runs**, so a `mkdir -p`
   inside the command cannot create its own log directory. It returns rc=0 with the real
   error only in stderr. Create directories first.
3. **`rc=124` from tacc_submit is the wrapper's 180 s timeout, not the job.** The job is
   detached and keeps running.
4. **The engine and the driver live in different roots on Vista.** `can-it-ford/` has
   `mpm-engine` and the hull but NO driver; the published `sim_standing.py` is in
   `can-it-ford-track1-6dof/`. And `can-it-ford/mpm-engine/src` is a STALE build missing
   `solidify_watertight`: the live engine is `$WORK/mpm-engine/src`, git `627367e`.
5. **trimesh is not in either engine venv.** Append
   `$WORK/.venv/lib/python3.12/site-packages` to `PYTHONPATH`; never install into it,
   it is shared.
6. **`find_stationary_window` returns a TUPLE, not a dict.** Reading it as a dict silently
   yields frame 0 and grades the whole transient.

## 5. Open defects I did not fix

- **The floor BC is one cell low.** `FLOOR = 0.075` is exactly 4 dx and the plane kernel
  gates on `dotproduct < 0.0`, so the node ON the plane gets no boundary condition. Worth
  1.829 cm of the 7.16 cm surface drop. Real, independent of everything else.
- **`WALL = 0.100` is 5.333 dx at g64 but exactly 8.000 dx at g96**, so cross-resolution
  runs do not have identical tank footprints (+2.48% at g96).
- **Dead literal** `RHO_W = 1000.0` at `sphere_heave.py:136`, read by nothing.
- **The sphere JSONs carry no job id, wall clock or scene commit.** Timing claims are
  unverifiable from the artifact. `band_mult` and `band_m` are now recorded; the rest is not.
- **The heave-stiffness fork**: 692.180 N/m at engine g vs 692.885 at benchmark g, in
  different D4 docs. Name the constant whenever quoting it.

## 6. Do not pool these

`measure_surface` gained a **+h/2** correction partway through the session. Runs before it
are biased LOW on surface and HIGH on `fz_over_analytic_measured`. Retro-corrected g64
600f is +47.41%, not the +63.20% published earlier.
