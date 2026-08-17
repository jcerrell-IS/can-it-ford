# D4 START HERE: fire the queue without re-deriving anything

2026-08-17, 21:15 UTC. Branch `claude/r5-physics`, HEAD `b82b335`, **35 commits authored,
36 ahead of `main`, none pushed.** Nothing on this branch has ever executed on a GPU.

**This is the single entry point.** Everything below is a pointer plus the one fact you
need to act. Timestamps here are UTC; the machine's local zone shifted CEST to BST
mid-session, so local labels either side of that are an hour inconsistent.

---

## 1. Two human blockers. Nothing runs until one of them clears.

| blocker | one-line fix | unblocks |
|---|---|---|
| **TACC socket cold**, all session, `Permission denied (keyboard-interactive)` | `ssh vista`, password + 6-digit token | **every GPU job** |
| **Kramer `/s1` supplementary** unfetchable (bot-blocked, not paywalled) | open `https://www.mdpi.com/article/10.3390/en14020269/s1` in a browser, save to `can-it-ford-refs/` **outside the repo** | **half of Option B's definition of done** |

A third, smaller: the Nihei corrigendum `10.1016/j.rineng.2025.107527` is **gold OA** and
gates the brake-state numbers. One browser fetch. It is not an access problem; earlier
records saying "publisher access" overstate it.

Detail: `R5_PHYSICS_BLOCKED_FLAGS.md`.

## 2. Preflight, costs nothing, do it first

```
ls -l     /work/11603/jcerrell0629/vista/can-it-ford/renders/yaris_render_s1/sim_standing.py
sha256sum /work/11603/jcerrell0629/vista/can-it-ford/renders/yaris_render_s1/sim_standing.py
```

**Expect `4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9`.** If it differs,
**stop and report** rather than run: Vista's driver would not be the one that stamped the
published runs. Or just:

```
bash simulation/r5_physics/prestage_jobs.sh --preflight
```

## 3. Fire order, and the drop rule

Batch via `tacc_submit`. **Never idev** (interactive burned 98.5-99.1% of Vista node-hours,
95 of 184 runs TIMEOUT).

| # | job | node-h | pass criterion, fixed in advance | drop rank |
|---|---|---|---|---|
| 1 | **A1** brake sweep, mu = 0.55 / 0.30 / 0.0250 on `sweepV_g64_v0p5`, 250 frames | **0.012** | mu = 0.55 **must** reproduce STUCK or the whole job is void. mu = 0.0250 tests the INFERRED flip. **mu = 0.30 is logged INDETERMINATE in advance**, because the bracket (0.369, 0.739] straddles the run's 0.5 m/s, so neither outcome confirms anything | **never drop** |
| 2 | **A2** repeats n=10 on `g96_m2337` and `sweepV_g64_v0p5`, 250 frames | 0.265 | report **divergence-onset frame**, spread of `max_surge_drift_m` with N and range, and **gate-pass frequency out of 10, never pass/fail** | n=10 to n=5 |
| 3 | **B** sphere `--fixed`, lim 1.2, 200 frames | 0.309 | steady reaction vs **69.2180 N** with a **blocked** SE, not a raw std. **Within 10% PASS, 10-25% REPORTABLE PARTIAL, beyond 25% FAIL.** Bands set now and not to be moved | 200 to 120 frames |
| 4 | **C** sphere free decay x3, lim 2.2, 200 frames | **3.679** | **not gradeable until `/s1` exists.** Self-consistency only: reflection window respected, period rising with drop height, Mach reported per drop | **drop first** |

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

**Scope complete pending the socket.** Both dispatch options have runnable, dry-run-tested
code with guards that can fire. Everything remaining needs a human, not more analysis.
Docs are **REVIEWED-WITH-CORRECTIONS**; the STUCK flip stays **INFERRED** until A1 measures
it.
