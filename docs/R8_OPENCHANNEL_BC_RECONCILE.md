# openchannel_bc.py: one lineage, two commits, and whether the older result still
# describes the newer code

Slot d4-bcmerge, branch `claude/r8-bc-merge`, worktree `.claude/worktrees/r8-bc-merge`,
2026-08-18. Every claim below is tagged READ (direct file or git object read), MEASURED
(a command was run and its output is quoted), or INFERRED. Nothing here is carried from a
summary, a handoff, or another session's conclusion without an independent check.

## 0. The premise this task was commissioned on was false, and that is the first result

The dispatch said `simulation/openchannel_bc.py` "was written TWICE, independently", that
the two `RecyclingChannelBC` bodies "differ by roughly 21 lines", and that a merge would be
"an add/add conflict at best and a silent overwrite at worst". It also asked which body is
correct where they differ.

There is no second body. MEASURED, `git ls-tree`:

```
be1b138  100644 blob 9a94e247c4a2fb674b5c8dda5fcc571a39a2f35b  simulation/openchannel_bc.py
5ecf725  100644 blob 9a94e247c4a2fb674b5c8dda5fcc571a39a2f35b  simulation/openchannel_bc.py
```

`be1b138` (branch `claude/add-ci-checks`, the commit that added the file, author date
2026-08-18T02:21:53+01:00) and `5ecf725` (branch `claude/r7-inflow`, 05:14:41+01:00) carry
the same blob, byte for byte. The 13725 B file is not a rival implementation, it is an
ancestor state of the 34941 B file, four commits earlier on one lineage.

Three independent confirmations, from genuinely separate origins:

1. MEASURED. The git object store returns the same blob sha1 for both commits, above.
2. READ. `claude/r7-inflow` says so itself, in
   `docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md:61`, "carried into this branch at its
   exact `be1b138` blob", and in `scripts/inflow_vehicle_wrapper.py:567`, which writes
   `"bc_module_provenance": "simulation/openchannel_bc.py, blob from commit be1b138"`.
   These two are ONE source, not two: same branch, same author, same session.
3. MEASURED. r7 stamps a content sha256 of the module into its run manifests,
   `bef123f947e3180e85bb8cbec61fe3ba0d6328f89382ae74bb2af49d2695272d`. Recomputing that
   hash myself over the bytes git returns for blob `9a94e247` reproduces it exactly. This
   is a different hash function over the same object, computed by me, so it confirms which
   bytes r7 actually ran rather than merely repeating r7's claim about them.

So the question "which body is correct" has no referent, and no line-by-line adjudication
was performed, because inventing one would have manufactured a disagreement that does not
exist. The real question, which nobody had asked, is in section 3.

## 1. The lineage, measured

MEASURED, `git cat-file -s` for sizes and `git cat-file blob | grep -c` for name presence.
Name counts are occurrences in the file, so a class definition plus its uses.

| commit | author date | blob | bytes | what appears for the first time |
|---|---|---|---|---|
| `be1b138` | 02:21:53 | `9a94e247` | 13725 | `tilted_gravity`, `RecyclingChannelBC`, `depth_profile`, `_selftest` |
| `7933f1e` | 02:44:29 | `a9f24a5e` | 20048 | `OverfallBC`, `overfall_metrics`, `discharge_per_width`, `clamped_y`/`clamped_z` |
| `89aae02` | 03:01:18 | `04ef8981` | 22952 | `_selftest_overfall_bc` |
| `1e6732b` | 03:15:20 | `53b4bef1` | 25895 | `inject_len`, `seed`, `self.rng` |
| `1315a4a` | 05:38:06 | `70946f61` | 34941 | `ReservePool`, `_selftest_reserve` |
| `5ecf725` | 05:14:41 | `9a94e247` | 13725 | nothing, this is `be1b138`'s blob on another branch |

`claude/add-ci-checks` is at `59234f9` and its working copy on disk in the main checkout
hashes to `70946f61`, so `70946f61` is the current tip content. MEASURED,
`git hash-object /Users/josie/can-it-ford/simulation/openchannel_bc.py`.

The `claude/r7-inflow` worktree's on-disk copy hashes to `9a94e247` with mtime 05:02, and
its tree is clean. MEASURED. That session is still pinned to the ancestor.

## 2. Every changed line inside the shared region, and what each one does

MEASURED, `git diff --no-index -U0` between the two blobs. Exactly five hunks fall inside
production code. Everything else is `_selftest` or the appended classes.

| # | ancestor `9a94e247` | current `70946f61` | change | verdict on the r7 path |
|---|---|---|---|---|
| H1 | `:103` | `:103` | `def __init__(..., prescribe="full")` gains `, inject_len=None, seed=0` | INERT |
| H2 | after `:126` | `:127-138` | 10 comment lines plus `self.inject_len = ...` and `self.rng = np.random.default_rng(seed)` | INERT |
| H3 | after `:128` | `:141-142` | `self.clamped_y = 0`, `self.clamped_z = 0` | INERT |
| H4 | `:160` | `:174-177` | the single injection line becomes `if self.inject_len is None:` / else | INERT ON THE DEFAULT BRANCH |
| H5 | after `:185` | `:203-206` | two comment lines plus `self.clamped_y += ...`, `self.clamped_z += ...` | INERT, AND OUTSIDE THE r7 SURFACE |

Reasons, one per hunk, all READ from the two files:

- H1. Both new parameters are keyword parameters with defaults, appended after the last
  existing parameter. Any caller that does not name them is unaffected. r7 constructs with
  all seven arguments named (`inflow_vehicle_wrapper.py:282-285`), so even a positional
  reordering could not have reached it, and there was none.
- H2. `self.inject_len` is `None` unless passed. `self.rng` is constructed unconditionally
  but is only drawn from inside the `else` branch of H4, so on the default path the
  generator is never advanced and cannot shift any stream. Cost is one PCG64 object per BC
  instance.
- H3. Two integer counters initialised to zero. The only subclass in the r7 path,
  `TrackedRecyclingBC` (`inflow_vehicle_wrapper.py:200-219`), adds one attribute, `ever`,
  so there is no name collision. READ, both files.
- H4. This is the only line in `apply` whose behaviour can differ. With `inject_len is
  None`, current `:175` is textually identical to ancestor `:160`, including the
  `np.mod(overshoot, L)` guard. The `else` at `:177` is reachable only by opting in.
- H5. The two `+=` read `out_lo` and `out_hi`, which were already computed one line above,
  and write only to the new counters. They do not touch `w`, `vw`, or the return value `n`.
  They now execute when `n == 0` as well, where they add zero. Separately, r7 never calls
  `project_cross_stream` at all: its scene uses its own `clamp_box`
  (`inflow_vehicle_wrapper.py:319`). So H5 is inert twice over.

## 3. Question 1: does anything between the two blobs alter the path r7 exercised?

No. Answered by test, not by reading.

The surface was enumerated by READING `claude/r7-inflow:scripts/inflow_vehicle_wrapper.py`,
not assumed: keyword construction (`:282-285`), a subclass that delegates through
`super().apply` (`:200-219`), one `apply` per frame (`:306`), `recycled_total` (`:573`),
`max_overshoot` (`:575`), and `depth_profile` (`:339`). `project_cross_stream` and
`tilted_gravity` are not in it.

`simulation/openchannel_bc.py` on this branch now carries that surface as an executable
pin. `_parity_digest(bc_cls, depth_profile_fn)` takes the class and the function as
arguments so the identical driver can be run against a different module object. The
digests in `ANCESTOR_PARITY` were produced by running that driver against the ancestor blob
loaded straight from git, never against the current module, so the test cannot degenerate
into asserting that the code equals itself.

MEASURED result, `uv run --with numpy python3 simulation/openchannel_bc.py`:

```
openchannel_bc selftest: 12 checks PASS
overfall selftest: 4 checks PASS (estimator recovers Rouse 1.4 exactly)
overfall BC selftest: 8 checks PASS (catch, reinject above the bed, no double-recycle)
reserve pool selftest: 8 checks PASS
ancestor parity selftest: 7 checks PASS (default path bit-identical to blob 9a94e247)
```

All 27 digested quantities match. The blocks are: A, one tick at `prescribe="full"`;
B, ten further ticks with a deterministic advection between them; C, the `streamwise`
branch; D, `depth_profile` edges and depths; E, `project_cross_stream`, kept under separate
keys because it is outside r7's surface; F, the `n == 0` early return; G, the `np.mod`
guard for an overshoot longer than the channel. Positions, velocities, `recycled_total`,
`recycled_last` and `max_overshoot` are digested wherever they can move.

### The fixture does work, which is the part that is usually missing

MEASURED: 103 of the 512 water rows start past the outflow plane, the ten-tick block
recycles 272 in total, the cross-stream fixture violates a wall 187 times, the F block
reaches the early return with `recycled_last` correctly reset to 0 while `recycled_total`
holds at 103, and the G block drives an overshoot of 10.660 m against a channel length of
8.20 m, landing the particle at 3.060 m through the modulo.

This matters because the ancestor's own `_selftest` is the cautionary case. It drew
positions from `uniform(0.6, 8.8)` against an outflow plane at `8.80`, numpy's `uniform` is
half open, and so it recycled nothing while printing "11 checks PASS". MEASURED by
reproducing that fixture exactly and instrumenting it: `n = 0`, maximum water x
`8.777121543884277`. Every check keyed on the crossing mask was running on empty arrays.
MEASURED per revision with `git cat-file blob`: the fixture fix and its `assert n >= 100`
first appear in blob `53b4bef1`, commit `1e6732b`, and not in the three revisions before it. The parity
fixture here carries the same guard, plus one on the cross-stream count.

The fixture uses no RNG at all. Every value is an integer scaled by a dyadic constant, so
the float64 intermediates and the float32 cast are bit-exact on any IEEE-754 platform. A
fixture built from `default_rng` would tie these digests to numpy's random stream and turn
a future numpy upgrade into a false parity failure.

### The control: can this test fail?

A passing equivalence test is worth nothing until it has been shown to fail on a real
change. MEASURED, three deliberate mutants of the current module, each run against the
ancestor goldens:

| mutant | edit | caught? | keys that fired |
|---|---|---|---|
| M1 | default injection shifted by `1e-6` m | yes | `A_x`, `B_x`, `C_x`, velocities untouched |
| M2 | crossing predicate `>=` becomes `>` | yes | `B_max_overshoot` 0.34375 to 0.35000, `B_x` |
| M3 | new counter leaks into the return, `return n + self.clamped_y` | yes | `E_n` 187 to 230 |
| M4 | `np.mod(overshoot, L)` guard removed | yes | `G_x0` 3.060 to 11.260, `G_x` |
| M5 | `recycled_last = n` moved below the early return | yes | `F_recycled_last` 0 to 103 |

M2 is the informative one. It fired ONLY in the ten-tick block: the one-tick digests
`A_n`, `A_x`, `C_x` were unchanged, because this fixture's crossing rows all sit strictly
beyond the plane and only later advection lands a particle exactly on it. A single-tick
harness would have passed M2 and reported parity. That is why the multi-tick block exists,
and it is a concrete instance of the rule that an extremal or single-sample quantity is not
a convergence check.

M5 is the one that corrected the harness rather than the code. The F block originally built
a FRESH instance and applied one non-crossing tick. That cannot catch M5, because a fresh
instance reports `recycled_last == 0` whether or not the empty path resets it. The block
was rebuilt to apply a crossing tick FIRST and the empty one second, which is also the
sequence r7's per-frame counter is read after, and M5 then failed on `F_recycled_last`
0 to 103. Recorded because the first version of that block would have shipped as a passing
test that could not fail, which is the same defect this document criticises in section 3.

## 4. Question 2: what actually is at risk, given the answer is "nothing moved"

The behavioural risk is closed. One real consequence survives, and it is a provenance
break, not a physics break.

r7 stamps `bc_module_sha256` into its run manifests and into its written result. That hash,
`bef123f9...`, is of the ancestor bytes. MEASURED sha256 values:

```
ancestor blob 9a94e247 : bef123f947e3180e85bb8cbec61fe3ba0d6328f89382ae74bb2af49d2695272d   (r7 ran this)
current tip  70946f61 : 70286d7fbcc217a14ced2580bd7e4ceace60b23f33721fae2d1b7bba9627ede5
this branch's file     : 598d1ccfea765a14d85b6084a6ecca63063fc81056446d1ab015799f15970ddb
```

So r7's artifacts point at a module version that is no longer the tip of the branch that
owns it, and after this branch lands, no branch tip will reproduce `bef123f9` at all. The
next person to re-run r7's grid on the current module would get, by the test above, the
same numbers, but they would have no recorded reason to expect that, and the mismatched
hash would look like drift. That is exactly the situation the parity test is meant to
convert from "unknown" into "checked".

### What the next person should stamp, so the break is repaired rather than recorded

Recommended, and NOT done here because `claude/r7-inflow` is outside this slot's write
scope. `bc_module_sha256` alone cannot survive a module edit, because it pins BYTES, and the
bytes are allowed to change. Stamp three fields instead of one, so an artifact names the
BEHAVIOUR it depends on:

```python
"bc_module_sha256":       sha256(REPO / "simulation" / "openchannel_bc.py"),  # as today
"bc_module_ancestor_blob": openchannel_bc.ANCESTOR_BLOB,                      # "9a94e247..."
"bc_module_parity_ok":     _selftest_ancestor_parity() ran without raising,   # True / False
```

Read that triple as: these exact bytes ran, they claim parity with blob `9a94e247`, and that
claim was checked at run time rather than asserted. An artifact carrying it stays comparable
with r7's existing ones, because the historical mapping is fixed and verified here: content
sha256 `bef123f9` IS git blob `9a94e247` IS the module r7 ran. So a future run whose
`bc_module_sha256` differs but whose `ancestor_blob` matches and whose `parity_ok` is True is
directly comparable to the published result, and one whose `parity_ok` is False is not, which
is the distinction the current single field cannot express.

If `_selftest_ancestor_parity` is ever removed or its goldens regenerated from the current
module rather than from the ancestor blob, `parity_ok` becomes decorative. Section 7's
re-derivation command is the check on the check.

r7's headline result is unaffected. READ from
`claude/r7-inflow:docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md`: three configurations, two
horizons, N=5 per arm, "Not one verdict moves, in either direction, at either horizon, in
any configuration" (`:324`), while displacement at the canonical horizon rises +35.4, +38.3
and +15.0 percent (`:37`) and at the later horizon +307, +521 and +88 percent (`:285`).
Note for anyone quoting this: "15 to 521 percent" spans TWO different horizons and is not a
single range. The canonical-horizon range is 15.0 to 38.3.

Out of scope but worth not inheriting: that document's reflection-frame figure of 112.3
frames is labelled by r7 itself as a reconstruction, and it reproduces only as a still-water
shallow-water round trip. `predict_reflection_frames` lives in the wrapper, not in this
module, so it is untouched by anything here.

## 5. Question 3: can the vehicle-scene port and the overfall/ReservePool extensions
coexist in one module, or do they genuinely need to fork?

They coexist. One module, no fork. The argument, from source rather than from the class
names:

1. The extensions are additive, and additive in the strict sense. `OverfallBC` is a
   subclass (`:350`), `overfall_metrics` and `discharge_per_width` are pure functions
   (`:415`, `:436`), and `ReservePool` (`:523`) inherits nothing and shares no state with
   the BC. READ. The only edits to the trunk are the five hunks in section 2, and section 3
   shows by test that none of them moves the default path.
2. The vehicle-scene port uses a strict subset of the trunk's API: two names imported, one
   method called per frame, two counters read. A fork would duplicate the trunk in order to
   give one consumer a subset of it.
3. A fork would delete the only place the invariant can live. The parity test is meaningful
   precisely because the overfall work and the vehicle work share a file: it is what makes
   a future overfall change that quietly moves `RecyclingChannelBC` fail loudly instead of
   silently invalidating r7's numbers. Two files, and nothing connects them again.
4. The stated reason for the extensions is a limitation the trunk names in its own first
   commit: one-in-one-out cannot express Zhao et al's non-uniform case, which needs a net
   flux imbalance. `ReservePool` is the piece that supplies it. Forking would put the
   limitation and its remedy in different files.

### The condition under which this flips

If a future change REQUIRES breaking the parity test to make the overfall or reserve path
correct, that is a genuine trunk conflict rather than an addition, and the answer changes
to either a versioned class or a fork. The test is what will detect that day. Nothing found
in the current tip meets that condition.

### Two hazards found while arguing this. One is a latent silent corruption

HAZARD 1, a parameter that will accept a value and ignore it. READ.
`OverfallBC.__init__` at `:383` assigns `self.rng = np.random.default_rng(seed)`,
overwriting the generator the parent constructed at `:147` from the parent's own `seed`.
Harmless today: `OverfallBC.apply` fully overrides and never reads `inject_len`, and
`OverfallBC.__init__` does not accept `inject_len`, so it cannot be reached by accident
now.

WHAT BREAKS. The obvious next edit is to let `OverfallBC` take `inject_len`, because a
spread inlet is exactly what an overfall inlet wants. The moment that passthrough is added,
the parent stores `self.inject_len` and the child's `apply` never consults it.

HOW IT PRESENTS. Not as an error. The caller sets an injection band, the run completes
normally, and the sheeting artifact the band exists to remove is still there at the same
magnitude. The natural conclusion is "the injection band does not help at an overfall",
which is a physics conclusion drawn from a parameter that was never read.

WHY NOTHING FIRES. Python stores an attribute whether or not anything reads it, and there
is no assertion anywhere that a constructor argument reaches a code path. The value is
present on the instance and simply unused.

THE FIX, one line, recommended and NOT applied: have `OverfallBC.__init__` either forward
`inject_len` to a path that honours it, or refuse it with a `TypeError`, so the parameter
cannot be silently inert. Reseeding `self.rng` is then a deliberate override rather than an
accident of ordering.

HAZARD 2, AND THIS ONE IS A LATENT CORRUPTION, NOT A FRICTION. MEASURED.
`ReservePool` writes to rows `[n_water, n_water + n_reserve)` (`self.lo = self.n_water`,
`:573`). In the water-only channel scenes those rows are spare particles. In the r7 VEHICLE
scene those rows ARE THE RIGID BODY: the wrapper reads the vehicle as `x[self.n_water:]`.
Constructing `ReservePool(n_water, 20, ...)` in a vehicle scene and calling `pin_parked`
teleports 20 of the 37 vehicle rows into the park box and raises nothing:

```
pin_parked pinned      : 20
VEHICLE rows displaced : 20 of 37
vehicle row 0 before   : [4.  4.  0.6] after: [1.0833334 1.0833334 1.0833334]
```

WHAT BREAKS, from the pinned solver rather than from a summary. READ,
`third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_solver_warp.py`: the rigid body's
centre of mass at `:857` is a mass-weighted mean of its particles' POSITIONS, and its
inertia tensor at `:864-869` is built from `r = x_np[idx] - x_cm` over those same positions,
with `:865` storing them as the body-frame reference the rigid update then places particles
from. Total mass at `:856` sums the particle MASSES and so is unchanged, since the parked
rows are still material 8. So the specific damage is: mass right, centre of mass dragged
toward the park box, inertia tensor inflated by the `r` squared term for every displaced
particle, and the body-frame reference geometry wrong. If the pin runs after
`finalize_rigid_bodies` instead, the host rewrite fights the rigid update every tick.

HOW IT PRESENTS. As physics. The run does not crash. It completes, it renders, it produces
a displacement and a verdict, and the vehicle it produces them for is a body with the right
mass, the wrong centre of mass and the wrong inertia. A CG error biases topple behaviour and
an inertia error biases rotational response, which are exactly the quantities this project
reports. Nothing in the output announces that a third of the hull was somewhere else.

WHY NOTHING FIRES. `ReservePool`'s only constructor guard (`:566-570`) validates the PARK
BOX against the P2G edge rule. It never validates the ROWS. Nothing anywhere asserts that
`[n_water, n_water + n_reserve)` contains water, and numpy fancy indexing into an existing
(N, 3) array is perfectly legal for those indices, because in a vehicle scene the vehicle
rows are what make N large enough. The write is in bounds, silent and complete.

THE FIX, recommended and NOT applied because `ReservePool` is production code outside this
slot's remit: have `ReservePool` take the TOTAL particle count or an explicit row range, and
raise if its block overlaps any non-water rows. Until that lands, anyone combining a reserve
pool with a vehicle must order the rows water, reserve, vehicle, and pass the BC an
`n_water` that excludes the reserve. This is a scene-layout contract rather than a module
conflict, so it does not argue for a fork, but it is the single most dangerous thing found
in this audit and it is dangerous precisely because it is quiet.

## 6. What this branch changed, exactly

MEASURED, `git diff --no-index -U0` against blob `70946f61`. Three hunks, zero of them in a
production code path:

```
@@ -48    +48,10   @@   __all__ corrected, with the reason recorded
@@ -709,0 +719,257 @@   the forward-compatibility parity section
@@ -714,0 +981    @@   one line, calling it from __main__
```

`__all__` had never grown past the three names `be1b138` shipped, while four public names
were added by `7933f1e` and `1315a4a`. MEASURED per revision with `git cat-file blob`, not
read off the commit subjects. No caller uses a star import today, so nothing was broken.

Nothing was pushed. `claude/add-ci-checks` and `claude/r7-inflow` were read with `git show`,
`git ls-tree` and `git cat-file` only, and neither was merged, rebased, cherry-picked or
written to.

## 7. Reproduce every number above

```
git -C /Users/josie/can-it-ford ls-tree be1b138 -- simulation/openchannel_bc.py
git -C /Users/josie/can-it-ford ls-tree 5ecf725 -- simulation/openchannel_bc.py
git -C /Users/josie/can-it-ford cat-file blob 9a94e247c4a2fb674b5c8dda5fcc571a39a2f35b | shasum -a 256
/Users/josie/.local/bin/uv run --with numpy python3 \
    /Users/josie/can-it-ford/.claude/worktrees/r8-bc-merge/simulation/openchannel_bc.py
```

The Mac has numpy in no system interpreter, so `uv` is required. No solver, no GPU, and no
network. Total runtime under a second after the environment is provisioned.

The goldens do not have to be trusted either. This re-derives them from the ancestor blob
and compares, so the claim "these digests describe the ancestor" is checkable by anyone
without reference to how they were produced:

```python
import subprocess, importlib.util, tempfile, os
REPO = "/Users/josie/can-it-ford"
MOD  = REPO + "/.claude/worktrees/r8-bc-merge/simulation/openchannel_bc.py"
anc = subprocess.check_output(["git", "-C", REPO, "cat-file", "blob",
                               "9a94e247c4a2fb674b5c8dda5fcc571a39a2f35b"])
d = tempfile.mkdtemp(); ap = os.path.join(d, "anc.py"); open(ap, "wb").write(anc)
def load(n, f):
    sp = importlib.util.spec_from_file_location(n, f)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
cur, anc = load("cur", MOD), load("anc", ap)
print(cur._parity_digest(anc.RecyclingChannelBC, anc.depth_profile) == cur.ANCESTOR_PARITY)
```

MEASURED output: `True`, over 27 keys, and the current module produces the same 27.

## 8. What this test cannot see

Stated plainly, because a parity test that is described as stronger than it is becomes the
next false premise.

1. It is ONE fixture, not a proof. It covers crossing, repeated crossing across ten ticks,
   the empty early return, an overshoot longer than the channel, both `prescribe` branches,
   the cross-stream clamp and `depth_profile`. It does not cover `n_water == 0`, non
   float32 or non-contiguous input arrays, NaN positions, or the `inject_len` band as a
   pinned behaviour (that appears only as a must-differ check). Scale is untested: 512
   water rows here against r7's 48367 (READ,
   `claude/r7-inflow:docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md:182`). The operations are
   vectorised and size-independent, so scale is a low risk, but low risk is not no risk.
2. It is a HOST-SIDE test. `RecyclingChannelBC` is pure numpy acting on arrays the caller
   hands it, so bit-identity is the correct and complete test OF THE MODULE. It says
   nothing about whether two full GPU runs agree. Identical BC output means identical
   inputs to the next solver step, not identical trajectories on hardware whose reduction
   order can vary. That is r7's own repeatability question, which is why they ran N=5 per
   arm rather than N=1, and it is untouched here.
3. Global state was checked, and is clean. MEASURED: importing the module prints nothing
   and constructs nothing, and building five `RecyclingChannelBC` instances leaves
   `np.random.get_state()` byte-identical, because `np.random.default_rng(seed)` returns a
   local Generator and never touches numpy's legacy global stream. So the added generator
   cannot shift any other component's random sequence.
4. Subclass safety was checked against the ONE subclass that exists in r7's path,
   `TrackedRecyclingBC`, which adds a single attribute, `ever`. Any subclass living
   somewhere I did not look is unchecked.
5. IT PINS BEHAVIOUR, NOT CORRECTNESS. Both blobs could be wrong in the same way, and this
   test would pass. Whether one-in-one-out recycling is a sound translation of Zhao,
   Bolognin, Liang, Rohe and Vardon 2019 is a separate question that nothing here touches;
   the module's own docstring already restricts the claim to their uniform-channel case and
   says the non-uniform case is not expressible without a spare-particle reservoir.

## 9. Review status: NOT reviewed by an independent adversary

The operating protocol for this session requires an adversarial check before finalising a
claim. It did not happen, and this section exists so that nobody reads its absence as
approval.

MEASURED, three attempts, all terminated with the same API error naming an unreachable
model, `deepseek-ai/DeepSeek-V4-Flash:deepinfra`:

| attempt | agent | model |
|---|---|---|
| 1 | `physics-skeptic` | agent default |
| 2 | `physics-skeptic` | explicit override, opus |
| 3 | `provenance-verifier` | explicit override, sonnet |

Slot d2-persist recorded the same failure on the shared board at 22:12 for `physics-skeptic`
alone and left open whether a model override would work. It does not: attempts 2 and 3
carried explicit overrides and failed identically, and the failure spans two different agent
types. So the subagent layer is unavailable session-wide, not specific to one agent
definition.

Every claim in this document is therefore UNREVIEWED. The substitute, which is weaker than
an adversary but stronger than assertion, is that each one is re-derivable by a named
command: section 7 reproduces the two central claims, and every number elsewhere is tagged
with the command that produced it. Nothing was reviewed by Wolfram or Scite either, and
nothing needed to be: this deliverable contains no physical parameter, no unit conversion
and no new citation. The one external reference, Zhao et al 2019, is carried verbatim from
the module's existing docstring and was not re-checked against the primary record here.

## 10. A tooling trap that nearly corrupted this audit, and the correction to my own
first account of it

MEASURED. In zsh 5.9, which is this project's shell, a git rev-and-path built from a
variable can be eaten by a history modifier, and QUOTING DOES NOT HELP:

```
for c in 1315a4a; do echo "[$c:simulation/openchannel_bc.py]"; done
[1315a4a                                      <- the path and the closing bracket are gone
git rev-parse "$c:simulation/openchannel_bc.py"   -> 1315a4a079...  (the COMMIT sha)
git rev-parse "${c}:simulation/openchannel_bc.py" -> 70946f61e7...  (the BLOB sha, correct)
```

CORRECTION, SAME SESSION, AND IT IS THE INTERESTING PART. My first write-up of this implied
the trap always fires. It does not, and the canary I originally put in this section, built
on `README.md`, DOES NOT FIRE AT ALL. I found that by running my own canary instead of
publishing it, which is the same lesson as M5 in section 3.

What actually governs it is the FIRST CHARACTER OF THE PATH, because that character decides
whether zsh sees a modifier. MEASURED over 19 literal prefixes with `c=HEAD`:

| altered | 11 prefixes, by first letter: `a c e g h l q r s t u` |
|---|---|
| unaffected | 8 prefixes: `d p x` and `README.md`, `CLAUDE.md`, `vehicle.py`, `notes.md`, `info.md` |

The modifiers do different damage. `:a` absolutises, `:h` takes a dirname, `:l` lowercases,
`:t` takes a basename, `:s` substitutes. So `renders/x` became `HEADenders/x` and
`analysis/x` became an absolute path with `HEADnalysis/x` glued on.

AND THIS IS WHY IT IS DANGEROUS IN EXACTLY ONE PLACE. Of the mangled prefixes I put through
git, four produced a string git REJECTED, which is loud and harmless:

```
git rev-parse "$c:renders/yaris_render_s1"  -> fatal: ambiguous argument 'HEADenders/...'
git rev-parse "$c:third_party/x"            -> fatal: ambiguous argument 'HEADhird_party/x'
git rev-parse "$c:analysis/x"               -> fatal: ambiguous argument '/Users/...'
git rev-parse "$c:scripts/check_claims.py"  -> fatal: ambiguous argument 'HEADk_claims.py'
```

One did not:

```
git rev-parse "$c:simulation/openchannel_bc.py"  -> 1aa4e19546bc54db9e8ac1bcee686aaa19aa9d6f
git rev-parse HEAD                               -> 1aa4e19546bc54db9e8ac1bcee686aaa19aa9d6f
```

The `:s` substitution consumed the whole path and left the bare rev intact, so git received a
valid commit-ish, resolved it happily, and returned COMMIT-level output with no error
anywhere. `git show` on that argument prints an entire commit diff, and a script that greps
it gets a confident wrong answer. That is precisely what happened here: two loops produced
wrong tables, one claiming `1315a4a` did not contain `inject_len` when its own blob contains
seven occurrences, caught only because a later result contradicted it.

So the live hazard for this repo is narrow and badly placed: `docs/`, `paper/` and `data/`
are safe, which is why this has never bitten before, and `simulation/` is the silent case.
`scripts/`, `renders/`, `analysis/` and `third_party/` are mangled but LOUD.

THE REMEDY, in copyable form. Any of these three is safe; the last two cannot be mangled at
all, because the path is a separate argument:

```sh
git show "${sha}:${path}"                 # brace it, quotes alone are NOT enough
git ls-tree "${sha}" -- "${path}"         # prints mode, type, BLOB sha, path
git cat-file blob "${blobsha}"            # pin by blob, immune to a branch moving
```

A canary that actually fires, unlike my first one. If your shell is safe these print the
same sha; if it is not, the first prints the sha of HEAD itself:

```sh
c=HEAD
git rev-parse "$c:simulation/openchannel_bc.py"
git rev-parse "${c}:simulation/openchannel_bc.py"
```

Interpolating a variable AFTER the colon also defends by accident, because `$` is not a
modifier character: `"$c:$path"` survives where `"$c:simulation/x"` does not. Do not rely on
that, it is a property of where the literal text sits, not a rule anyone will remember.
