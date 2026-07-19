# Can It Ford — July 12 Session Audit + Panel Task Assignments

Built by reading `session_log.txt` line by line across all 7 tmux panes (0.0–0.6), cross-referenced against `2026-07-10_session-summary.md`, `CLAUDE.md`, `PROJECT_FILE_MAP.md`, the mpm-render-pipeline skill, the Genesis/GH200 deep-reference doc, and `drift_threshold_citation_research.md`.

---

## 1. Three things I found that change the whole picture

### 1a. The argparse bug retroactively invalidates most of the last 3 days of crash "isolation" work

Before tonight's fix (commit `69d27af`), `can_it_ford_L2_mpm.py`'s parameter parsing was:

```python
water_depth    = float(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 0.30
water_velocity = float(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith('-') else 0.0
```

Every command tonight and in the July 10–11 crash logs used `--depth X --velocity Y` syntax. With that syntax, `sys.argv[1]` is literally the string `"--depth"`, which starts with `-`, so `water_depth` **always fell through to the 0.30 default**, no matter what depth was requested. Worse, `sys.argv[2]` was the *value* of `--depth` (e.g., `"0.3"`), which does **not** start with `-`, so it got assigned to `water_velocity` instead. A call like `--depth 0.3 --velocity 1.5` was silently running as **depth=0.30, velocity=0.3** — you can see this exact artifact in `mpm_crash_july12_smallcase.txt`, which prints `"--- Running L2 MPM: depth=0.3m, velocity=0.3m/s ---"` even though `--velocity 1.5` was passed.

**What this means:** every crash log from July 10–12 that claims to have "isolated" the cause by varying depth/velocity/box size was almost certainly running the same effective (0.30, requested-depth-value) pair every time. The crash is real and still reproduces post-fix (confirmed tonight at both `depth=0.30 v=0.0` and `depth=0.60 v=2.0`), so the bug itself isn't an artifact — but the *isolation logic* ("ruled out inflow velocity, box size, and domain bounds") drafted for Kumar tonight is not actually supported by real evidence yet. Don't say that to Kumar until it's re-tested with the fix in place.

### 1b. The vehicle in `can_it_ford_L2_mpm.py` is ~5x too heavy, and I think I know why the crash is immediate

`CLAUDE.md` documents that `rho=604` was calibrated for a `1.0 × 1.6 × 1.5 m` placeholder box to hit a validated **~1,450 kg** target. Commit `67915be` resized the vehicle to the real sedan bbox (`4.66 × 1.79 × 1.44 m`) but **kept `rho=604` unchanged**:

```
sedan box volume = 4.66 × 1.79 × 1.44 = 12.012 m³
current mass = 604 × 12.012 = 7,255 kg   (should be ~1,450 kg)
correct rho for 1,450 kg target = 120.7   (currently 604, ~5x too high)
```

### 1c. The vehicle and water boxes geometrically overlap at t=0 — new leading hypothesis for the CUDA crash

From the live script (grep'd tonight, confirmed twice):
```python
water   pos=(0.275, 0.0, water_depth/2.0), size=(0.35, 1.8, water_depth)
vehicle pos=(1.0,   0.0, 0.755),           size=(4.66, 1.79, 1.44)
```
At `water_depth=0.30`: water spans x∈[0.10,0.45], y∈[-0.90,0.90], z∈[0,0.30]. Vehicle spans x∈[-1.33,3.33], y∈[-0.895,0.895], z∈[0.035,1.475]. **These overlap in all three axes** — the vehicle's underbody (z from 0.035 to 0.30) sits inside the same volume the water box occupies, and the vehicle's z-position is a hardcoded constant that never adjusts for `water_depth`, so this happens at every tested depth.

A car's underbody being wet during fording is physically correct — but nothing in the script excludes the vehicle's footprint before MPM water particles are seeded into the water box, which means water particles are very likely being initialized **literally inside the same space as the rigid body** at frame 0. This is a textbook double-occupancy initialization problem, and it fits every symptom seen tonight: crash is immediate (step 0 for small cases), happens even at `velocity=0.0` (rules out flow-induced instability), and was untouched by `grid_density=64→128`, `dt`, `substeps`, or domain-bound changes — because none of those touch the initialization overlap. Genesis's own issue tracker (`#2071`, discussion `#1291`) documents MPM-rigid coupling failing specifically around thin/overlapping-at-init geometry, which is consistent with this.

**This is a new, testable hypothesis, not yet confirmed.** Test it before doing anything else — see Pane 0.0, Task 1–2 below.

---

## 2. July 10 known-bugs checklist — status as of tonight

From `kumar_july9_update/STATUS.md` (Open Questions + Next Steps), read directly off Vista tonight in Pane 0.4:

| Item | Status tonight |
|---|---|
| Root cause of `CUDA_ERROR_ILLEGAL_ADDRESS` | **Still open.** Reproduced again post-argparse-fix at two different (depth, velocity) pairs. Two new hypotheses (1b, 1c above) not yet tested. |
| Root cause of water drift in `box_sdf_collider_setup.py` | **Not worked on tonight at all.** Track 1 has moved to `flood_vehicle.py`/`FloodScene` instead (see §3). Worth deciding explicitly whether `box_sdf_collider_setup.py` is retired. |
| Whether CoRL 2026 truck mesh is reusable | Not addressed tonight. |
| Source for `DRIFT_THRESHOLD = 0.05 m` | **Solved, not yet applied.** `drift_threshold_citation_research.md` already has the exact wording (Xia et al. 2014 + Shah et al. 2018, ~2.5–3.4% of vehicle body width, framed as a conservative onset-of-motion detector, not a published criterion). Nobody applied it tonight. |
| Whether the two tracks should be reconciled | **More urgent now, not less** — there are effectively three vehicle representations in play now (see §3). |
| Debug the CUDA crash; capture full traceback | Done again tonight (`CUDA_LAUNCH_BLOCKING=1`, multiple `logs/mpm_crash_july12_*.txt` files), root cause still not found. |
| Debug water drift in `box_sdf_collider_setup.py` | Not touched. |
| Push `box_sdf_collider_setup.py` to repo | Unverified tonight — didn't come up. |
| Update `can_it_ford_L2_mpm.py` to real sedan box dims | **Done** (commit `67915be`), but see 1b — the mass wasn't recalculated when the box changed. |
| Fix stale `run_tag` naming | Appears done (`67915be` commit message covers CSV path). |
| Resolve vehicle mesh (CoRL truck / CC0 / box proxy) | **Partially resolved by accident** — `flood_vehicle.py` is loading *some* real mesh via `plyfile` (not a box), but which mesh is unconfirmed (see §3, Pane 0.4 task 4). |
| Resolve `DRIFT_THRESHOLD` citation | Solved in research, not applied to code/docs. |

---

## 3. Bugs and gaps not on the July 10 list (found tonight)

1. **The argparse bug itself (§1a)** — a real, previously-undiagnosed bug that was silently breaking every `--depth`/`--velocity` CLI call on `can_it_ford_L2.py`, `can_it_ford_L2_mpm.py`, and `can_it_ford_L2_mpm_ytest.py`. Fixed tonight (`69d27af`), confirmed scoped to exactly those 3 files, L0/L1 unaffected.
2. **Vehicle mass ~5x too heavy in `can_it_ford_L2_mpm.py` post-sedan-resize (§1b).** Not previously flagged anywhere.
3. **Water/vehicle box geometric overlap at t=0 (§1c).** New leading hypothesis for the crash; not previously investigated from this angle.
4. **`ffmpeg` is not on PATH in the `mpm-engine` uv environment** — `flood_vehicle.py`'s render step fails with `subprocess.CalledProcessError ... returned non-zero exit status 127` (command not found) when assembling the MP4. `mpm_render_report.md` already has the fix researched: install `imageio-ffmpeg` (`uv add imageio-ffmpeg`), which ships its own ffmpeg binary and is the documented "primary path" for headless Vista rendering — nobody applied it tonight.
5. **`flood_vehicle.py`'s vehicle geometry is a small-scale model (~0.45 m long), not the full-scale sedan.** Tonight's runs mixed this small model with (a) an arbitrary default mass (~28.7–29.5 kg), then (b) a direct `--vehicle-mass 1390` override on the *same small geometry* — neither is dynamically consistent. The script itself documents the fix: `load_vehicle(target_length=...)` runs at full scale directly. This was never tried.
6. **The `bridge/` scaffold (PhysGaussian → Genesis MPM particle bridge) from July 10 was not touched, mentioned, or referenced once in ~11,500 lines of logs tonight.** Two local commits (`3d3ebbc`, `c97767f`) were pending push as of July 10; none of tonight's `git log` output (which only ever showed the 5 most recent commits) confirms whether those are still in history. Needs an explicit check — this is Piece 2 of the master rebuild plan and is currently invisible.
7. **Three separate, slightly different Kumar-update messages were drafted tonight (Panes 0.3, 0.4, 0.6) and none were actually sent** — all three were `echo`'d to a local terminal, not sent via Slack.
8. **The local Mac `can-it-ford` conda env is broken for `trimesh`**: `conda install` succeeded and `python3 -c "import trimesh"` worked when invoked with the env's literal interpreter path, but `conda run -n can-it-ford python3 -c "import trimesh"` still fails with `ModuleNotFoundError`. Env activation path issue, not a missing-package issue.
9. **`~/.zshrc` now has 2–3 overlapping, redundantly-appended copies of `update_log`/`clean_logs` shell functions** from repeated `cat >> ~/.zshrc << 'EOF'` calls across panes — this is exactly the kind of thing that silently breaks in a future session.
10. **`can_it_ford_L2_mpm_ytest.py` was newly created tonight** (168 lines, in the argparse-fix commit) and its purpose relative to `can_it_ford_L2_mpm.py` was never stated in any pane. Needs a one-line clarification or it'll be a mystery file in a month.

---

## 4. Is tonight's work actually what Kumar wants?

Yes, mostly — with one important nuance. `CLAUDE.md` records Kumar's **verbatim** instruction: *"can you run what Cheng-Hsi has first? https://github.com/kks32/mpm-engine is the MPM engine,"* wanting a **real car** in a **real MPM sim** with **real SDF/mesh-to-rigid coupling**, explicitly *not* a placeholder box and *not* the SPH pipeline (`can_it_ford_L2.py`).

That means **Track 1 (`flood_vehicle.py`/`FloodScene`) is the track that actually matters most to Kumar right now** — more than the Genesis-native `can_it_ford_L2_mpm.py` crash, which is a real open GitHub issue (`#1`) but is Josie's own parallel effort, not Kumar's literal ask. Tonight's FloodScene work is well-aligned (it already gets full 6-DOF yaw/roll/lateral output that the old kinematic-only `box_sdf_collider_setup.py` architecture couldn't produce), but it isn't yet using a full-scale, correctly-massed vehicle, which is the last gap between tonight's output and something genuinely presentable to Kumar as "run what Cheng-Hsi has."

**Recommended framing if this comes up tonight or in the next update: the CUDA crash isolation and the FloodScene mass/scale fix are not equally urgent. FloodScene-at-full-scale is the higher-value target because it's what Kumar literally asked for.**

---

## 5. Panel-by-panel task assignments (5+ each, excluding troubleshooting)

### Pane 0.0 — primary crash-repro + mass-discovery pane (currently on c642-091, mid-crash-retest)
1. **Test the overlap hypothesis (§1c) in isolation:** temporarily shift the vehicle box downstream (e.g., `pos=(6.0, 0, 0.755)`, fully clear of the water box's x-range) and rerun the exact failing case (`depth=0.30 velocity=0.0`). If the crash disappears, the overlap is confirmed as (at least part of) the cause.
2. **Fix the mass (§1b):** change `rho=604` → `rho=120.7` (or the load-bearing constant, computed from the live box volume) in `can_it_ford_L2_mpm.py`, and rerun the same case to see if mass alone changes the crash behavior.
3. If either #1 or #2 changes the outcome, combine both fixes and rerun the full `depth=0.30, velocity=1.5` reference condition end to end.
4. Re-run the `--vehicle-mass` FloodScene test from earlier tonight, but this time at **full scale** via `load_vehicle(target_length=4.66)` instead of the default small model, so mass and geometry are finally consistent.
5. Write whichever result comes out of #1–#3 directly into `kumar_july9_update/STATUS.md`'s Open Questions list — check off "Root cause of CUDA_ERROR_ILLEGAL_ADDRESS" if resolved, or record the negative result precisely if not.

### Pane 0.1 — FloodScene depth/velocity sweep pane (currently on c642-091, just finished depth=0.38)
1. Re-run the full depth sweep (0.15, 0.22, 0.30, 0.38, 0.45, 0.60) at `velocity=1.5` with **one consistent, deliberate mass/scale choice** — tonight's sweep mixed model-scale-default-mass and model-scale-28.7kg runs, so the "crossover" claim needs reconfirming under consistent physics, not assumed to survive the mass fix.
2. Regenerate the yaw-vs-depth / roll-vs-depth crossover plot from the corrected sweep and confirm (or revise) the `depth≈0.30m` crossover claim.
3. Determine what `can_it_ford_L2_mpm_ytest.py` actually is (new file tonight, purpose never stated) — duplicate, Y-axis-specific variant, or leftover scaffolding to delete.
4. Copy the completed sweep CSVs into `data/` in the repo and commit them — right now they only exist on a Vista compute node that disappears when the idev job ends.
5. Write a one-page `data/floodscene_sweep_README.md` stating exactly which mass/geometry combination each CSV used — tonight's mixed-mass runs are otherwise indistinguishable from each other by filename alone.

### Pane 0.2 — citation-fix panel / "Panel D" (currently on c642-091, just finished depth=0.30 v=2.5)
1. Check whether the July 10 `bridge/` scaffold (PhysGaussian→Genesis bridge, commits `3d3ebbc`/`c97767f`) survived into current git history: `git log --all --oneline | grep -i bridge` and `ls bridge/` on Vista. This hasn't been mentioned once tonight and needs an explicit yes/no.
2. Apply the already-researched `DRIFT_THRESHOLD` citation fix from `drift_threshold_citation_research.md` to `kumar_july9_update/STATUS.md`'s citation table and any poster/paper text that still says "not cited anywhere."
3. Confirm `can_it_ford_L2.py` (the SPH pipeline — explicitly off-limits per `CLAUDE.md` for tonight's task) wasn't touched by the argparse-fix commit's changes to its own CLI parsing logic; verify its SPH output is unaffected.
4. Check whether `can_it_ford_validation.png` (dated Jul 10, sitting next to the freshly-regenerated phase-space figure) also needs regenerating — confirm whether its source script references the debunked Smith 2019 citation too.
5. Do a final README.md audit pass against Part 3b of the master instructions doc (GitHub repo audit) — confirm no other stale MPM-vs-SPH claims remain outside the two lines already checked tonight.

### Pane 0.3 — MacBook orchestration / Kumar-draft pane
1. **Actually send** one Kumar update via Slack — three were drafted tonight (`echo`'d locally, never sent) and none reflect the mass bug or the retracted "ruled out" claim from §1a. Write one accurate version and send it.
2. Download the remaining sweep CSVs from Vista that haven't been scp'd to `~/can-it-ford/data/` yet (only d0p15 and d0p45 were confirmed pulled tonight; d0p22, d0p30-check, d0p38, d0p60-v2p5 are still stranded on the compute node).
3. Fix the local conda env activation issue: `conda run -n can-it-ford python3 -c "import trimesh"` fails even after a clean reinstall, while the same import works when the env's literal interpreter path is called directly — diagnose (`which python3`, `conda env list`, shell rc activation order).
4. Consolidate the 2–3 overlapping `update_log`/`clean_logs` function definitions that got appended to `~/.zshrc` tonight into one clean version.
5. Confirm whether `wandb_backfill.py` (untracked, root-level, reads `data/scenario_sweep.csv`) is unblocked to run — it's already key-free/env-var-based, so check whether it's only gated on confirming the historical key rotation, and if so, run it (Priority Build Order item #9).

### Pane 0.4 — STATUS.md review / citation pane
1. Update `kumar_july9_update/STATUS.md`'s checklist directly — several "Next Steps" items are functionally done tonight (sedan box dims, CSV path/run_tag fix) but the file still reads as untouched since July 9.
2. Redo the Al-Qadami citation search that came up empty tonight — it searched `citations/*.md` on Vista, but the answer is already sitting in the local project file `Smith__Modra_and_Felder__2019...md` (Al-Qadami et al., Engineering Letters 29(3), d×v=0.3 m²/s sliding-instability limit for the Toyota Yaris model).
3. Write an explicit decision on "reconcile the two tracks" — there are now effectively three vehicle representations (box+SDF, box-only, mesh-based-MPM-particles); recommend retiring `box_sdf_collider_setup.py` given `flood_vehicle.py` already delivers the full 6-DOF output the older architecture structurally couldn't.
4. Confirm which mesh `flood_vehicle.py` is actually loading by default — is it `truck_trimmed.ply` (47.4 MB, already in `~/can-it-ford/data/`) or something else bundled with the script? This determines whether tonight's "vehicle" was ever a car at all.
5. Merge the three independently-drafted Kumar update messages (Panes 0.3, 0.4, 0.6) into the single one Pane 0.3 sends, so there's one source of truth instead of three inconsistent drafts.

### Pane 0.5 — env-troubleshooting / verification pane
1. Re-confirm the argparse-fix scope post-merge: `grep -c "startswith" simulation/*.py` across the full `simulation/` folder (including L0/L1) one more time now that the fix is on `main`, and log the confirmation.
2. Write down the root cause of tonight's `ModuleNotFoundError: No module named 'warpmpm'` (missing `.venv`, fixed by switching to `uv run`) so it doesn't get re-debugged from scratch next session.
3. Pull the full `git log --oneline --since="2026-07-09"` list (only counted 18 commits tonight without listing them) and map each commit to a STATUS.md checklist item it closes.
4. Diff the untracked root `wandb_backfill.py` against the tracked `analysis/wandb_backfill.py` to confirm which is current before Pane 0.3 runs one of them.
5. Produce one clean `git status` / `git log -10` / `git diff HEAD~5` summary block Kumar's update and `SESSION_STATE.md` can both quote directly.

### Pane 0.6 — output-pulling / final-state pane
1. Download all of tonight's remaining PNG/CSV outputs from Vista before more idev sessions expire — only the `d0p3_v1p5` pair is confirmed pulled.
2. Open `flood_vehicle_d0p3_v1p5.png` and check it against Kumar's documented visualization conventions (viridis colormap, particles visible not smooth surface, fixed camera/colorbar) from the mpm-render-pipeline skill; flag for re-render if it doesn't match.
3. Confirm `SESSION_STATE.md` (the cross-terminal handoff file from July 10) still exists and actually reflects tonight's end state — none of the 7 panes touched it tonight.
4. Update `PROVISIONAL_STATUS.md`'s existing correction banner with tonight's real MPM-attempt status (still crashing, two new untested hypotheses) — keep the same "verify before trusting" discipline that caused that banner to exist.
5. Once Pane 0.0's hypothesis test returns a result, write the definitive "crash: root cause found / ruled out" entry into `logs/` and `STATUS.md`.

---

## 6. Should you open another panel?

**Yes — one, not more.** Open a Pane 0.7 dedicated *only* to the mass+overlap hypothesis test (Pane 0.0, Tasks 1–3 above). It's fast, cheap, and fully independent of the ongoing FloodScene sweep in Pane 0.1 — running it in its own panel means it won't get buried in Pane 0.0's existing back-and-forth between the two tracks, and it's the one test tonight that could actually close GitHub issue #1.

Don't open more than that. The real bottleneck tonight isn't panel count — it's that three panes (0.3, 0.4, 0.6) independently redid overlapping work (drafting near-identical Kumar messages, rediscovering the same argparse scope) that one clear owner could have done once.

## 7. Fastest path from here

1. **Pane 0.7 (new): test rho fix + overlap fix on the exact failing case.** Highest expected value — could close the #1 open GitHub issue tonight.
2. **Pane 0.0/0.1: get one FloodScene run at true full scale** (`load_vehicle(target_length=4.66)`, correct mass) at the reference condition. This is literally what Kumar asked for.
3. **Pane 0.3: send the Kumar update — for real this time.** It's been written three times and sent zero.
4. **Pane 0.2: apply the DRIFT_THRESHOLD citation fix.** Already researched, zero new research needed, five minutes of editing.
5. Everything else in the panel list above is real and worth doing, but none of it blocks tonight's highest-value outcome the way 1–4 do.

## STATUS UPDATE — July 13, later pass

Section 1c's overlap hypothesis: TESTED (box reverted to old size, domain kept
widened) and RULED OUT as the sole cause, along with box size independently.
Live suspect is now the domain-widening commit's bounds themselves, not overlap
or geometry. Don't re-run the Pane 0.0 overlap isolation test as originally
specified — it's already answered.

Section 1b's mass fix: target confirmed as 1390kg (not the 1450kg alternative
mentioned). Correct rho = 115.7. Applied-to-live-file status still unconfirmed
as of this update — check before assuming done.

Pane assignments in Section 5: Panes 0.2, 0.5, and 0.6's task lists were never
confirmed as executed. Panes 0.0/0.1/0.3 show partial completion. See
master_outstanding_tasks_audit_july13.md for the full per-pane breakdown.

New finding not in the original document: viability_audit.py globs
particles_d*.npz, which does not match particles_mpm_*.npz output files —
every MPM-track run has been invisible to this audit script.
