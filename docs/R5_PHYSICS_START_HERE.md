# D4 START HERE: fire the queue without re-deriving anything

2026-08-17, 21:15 UTC. Branch `claude/r5-physics`, HEAD `b82b335`, **35 commits authored,
36 ahead of `main`, none pushed.** Nothing on this branch has ever executed on a GPU.

**This is the single entry point.** Everything below is a pointer plus the one fact you
need to act. Timestamps here are UTC; the machine's local zone shifted CEST to BST
mid-session, so local labels either side of that are an hour inconsistent.

---

## 1. The two blockers are CLOSED. One was never open.

**Updated 2026-08-17 ~21:30 UTC. Full account: `R5_PHYSICS_BENCHMARK_UNBLOCKED.md`.**

| was blocking | state now |
|---|---|
| **TACC socket cold**, `Permission denied (keyboard-interactive)` | **CLEAR, and already was.** Live typed command returns `login1.vista.tacc.utexas.edu`, 627 SU, queue empty. Nobody ran `ssh vista`; it warmed and no one re-tested. A blocker recorded once is not a blocker now |
| **Kramer `/s1` supplementary** unfetchable | **CLOSED.** `can-it-ford-refs/2026-08-16/energies-14-00269-s001.zip`, sha256 `04c4d78d...7623f`. Fetched by driving a **real browser**; curl, WebFetch and the scite resolver all get 403 from MDPI |

**Still open, the only one:** the Nihei corrigendum `10.1016/j.rineng.2025.107527`, gold
OA, gates the brake-state numbers. The browser route that worked for Kramer has not been
tried on it.

**Clearing them was not sufficient.** Two run-blocking defects sat behind the flags; both
are fixed, see section 2.

## 2. Preflight. It now actually runs, and it used to not.

```
bash simulation/r5_physics/prestage_jobs.sh --preflight     # exits non-zero on failure
bash simulation/r5_physics/prestage_jobs.sh --stage         # only if the scene check fails
```

`preflight()` previously **echoed** its checks as strings for a human to paste, while this
section and the script's own usage text both described it as performing them. It always
exited 0. **A check that cannot fail is not a check.** Run against the original paths it
now reports two failures, both real and both fixed:

1. **Job A's driver path did not exist.** The engine and the driver live in **different
   roots**: `can-it-ford/` has `mpm-engine` and the hull but no driver; the expected
   `4696c3b2...` is in **`can-it-ford-track1-6dof/`**. `cd $REPO` stays `can-it-ford`,
   which is correct, because `sim_standing.py:14` hardcodes `VEHICLE_DIR` absolutely.
2. **Jobs B and C ran a file that was never staged.** `find $WORK -name sphere_heave.py`
   returned nothing; this branch is unpushed and Vista sits on `main`. The scene now lives
   at `$WORK/d4_scene` and is referenced **absolutely**, not relative to a `cd`.

Current state: **rc=0.** Driver sha matched, scene staged and sha-verified byte-identical,
engine imports, and `test_sphere_geometry.py` runs on **Vista's own interpreter** with
ALL PASS. `nvidia-smi: command not found` on the login node is expected, not a gate.

## 3. Fire order, and the drop rule

Batch via `tacc_submit`. **Never idev** (interactive burned 98.5-99.1% of Vista node-hours,
95 of 184 runs TIMEOUT).

| # | job | node-h | pass criterion, fixed in advance | drop rank |
|---|---|---|---|---|
| 1 | **A1** brake sweep, mu = 0.55 / 0.30 / 0.0250 on `sweepV_g64_v0p5`, 250 frames | **0.012** | mu = 0.55 **must** reproduce STUCK or the whole job is void. mu = 0.0250 tests the INFERRED flip. **mu = 0.30 is logged INDETERMINATE in advance**, because the bracket (0.369, 0.739] straddles the run's 0.5 m/s, so neither outcome confirms anything | **never drop** |
| 2 | **A2** repeats n=10 on `g96_m2337` and `sweepV_g64_v0p5`, 250 frames | 0.265 | report **divergence-onset frame**, spread of `max_surge_drift_m` with N and range, and **gate-pass frequency out of 10, never pass/fail** | n=10 to n=5 |
| 3 | **B** sphere `--fixed`, lim 1.2, 200 frames | 0.309 | steady reaction vs **69.2180 N** with a **blocked** SE, not a raw std. **Within 10% PASS, 10-25% REPORTABLE PARTIAL, beyond 25% FAIL.** Bands set now and not to be moved | 200 to 120 frames |
| 4 | **C** sphere free decay x3, lim 2.2, 200 frames | **3.679** | **NOW QUANTITATIVELY GRADEABLE**, `/s1` is on disk. Measured first damped periods, N=4 each: **0.7869 / 0.8093 / 0.8671 s** for 0.1D / 0.3D / 0.5D, spreads 0.0010 / 0.0012 / 0.0029 s. Published tolerance is per drop, **0.096 / 0.239 / 0.435 mm**, not a flat 0.3%. Reduce with `kramer_benchmark.py` | **drop first** |

`bash simulation/r5_physics/prestage_jobs.sh --go A` (then `B`, `C`) emits each job script
and its `tacc_submit` line.

**A1 is 0.012 node-hours and is the only item that converts an INFERRED claim into a
measurement. If exactly one thing runs, run A1.** Everything gradeable today is
A1 + A2 + B = **0.587 node-h**.

**SU:** full queue 4.27 node-h. No primary source for the rate, so: it exceeds 629 SU only
above **147 SU per node-hour** (1,072 without C). Confirm with `tacc_alloc_status` and
multiply. Detail: `R5_PHYSICS_SU_TRIAGE.md`.

## 4. Safe to cite

Only what is in section 1 of `R5_PHYSICS_WHAT_SURVIVES.md`, **and read the corrections
attached to each row**, because a fifth review broke 7 of those 10 and they are corrected in place,
not deleted. The three that came through unbroken: **no outflow BC in the canonical scene**,
**the STUCK deceleration mechanism**, and **the layer counts**.

**15 distinct claims are withdrawn.** They are listed by name in section 2 and section 3 of
that file. **Never cite one.** The ones most likely to be repeated from memory: "41% cap
hit", "14/17 never stationary", "the velocity sweep varies depth 2.6x", "depth explains 15%
of the P-2 trend", and "the BC was validated 3/3 then the level did not hold" (that event
never happened).

## 5. Traps that cost me time, so they do not cost you any

1. **Cite `_incoming/sim_standing.py`, not the tracked top-level copy.** Different files,
   md5 `a3f7a0f3...` against `5ca372e4...`. CLAUDE.md item 2's own line numbers are the
   `_incoming` ones.
2. **`particle_selection` FREEZES a particle; it does not delete it.** And no diagnostic in
   the repo filters frozen ghosts, so an unfiltered depth reading from a retirement run is
   dead water. `depth_station.py` and `spin_down.py` now filter; `local_depth_footprint`
   does not.
3. **A licence status is not a fetch status.** Three documents were recorded as
   access-barred that were openly licensed and merely bot-blocked, and one was served by a
   publisher's backend while its front end refused.
4. **`sdf_wrench` takes the TICK, not the substep.** Getting it wrong inflates force by
   exactly `substeps` = 82, plausibly.
5. **L-3's floor is ~10 particles per flow depth**, not "4 layers / 2 cells". Against the
   actual floor, 17 of 17 runs fail.

## 6. Two standing rules earned this round

- **An argument that reaches the right answer without engaging the refuting mechanism is
  not verified.** Name the mechanism that would refute you, then show it does not fire.
- **Two readers independently choosing the same reading of an ambiguous phrase is one
  guess, not corroboration.**

## 7. Status

**Superseded 2026-08-17 ~21:30 UTC.** The old text read "scope complete pending the
socket", and that was wrong in both directions: the socket was **already clear**, and
clearing it would not have been enough, because job A pointed at a nonexistent driver and
jobs B and C ran an unstaged file.

**State now: the queue is fireable and verified.** `--preflight` exits 0, the scene is
staged and sha-verified on Vista, and the geometry suite passes on Vista's own
interpreter. The Kramer series is on disk, so **job C is quantitatively gradeable** and
`sphere_heave.py`'s `a33/m = 0.5` sizing assumption is now measured against data: the
implied ratios are **0.540 / 0.629 / 0.870**, so 0.5 is low everywhere and 42% low at the
nonlinear drop.

**Nothing has run on a GPU, and nothing has been submitted.** That is a live 627 SU
allocation and the call to spend it is Josie's. Docs remain
**REVIEWED-WITH-CORRECTIONS**; the STUCK flip stays **INFERRED** until A1 measures it; the
benchmark reduction in section 3 of `R5_PHYSICS_BENCHMARK_UNBLOCKED.md` is
**UNREVIEWED** by the physics-skeptic.
