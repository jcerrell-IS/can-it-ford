# The unseeded 60,000-sample draw: what it actually costs, and where the fix breaks

Dispatch 12 Part B, 2026-08-14, branch `claude/fork-protocol`.

Tags: **[read]** direct source read, **[measured]** run live today, **[cited]** carried
from the dispatch and not independently re-derived, **[inferred]**.

Engine scope: **warpmpm only**. Nothing here applies to Genesis or Chrono.
Audit: `analysis/seeding_audit.py`, which loads the **real upstream `load_vehicle`** by
path (stubbing the two solver imports that drag in torch) rather than reimplementing it,
so the audit cannot drift from the source it audits.

---

## The claim under test

> "the SDF cache never hits because `load_vehicle` draws 60,000 RANDOM surface samples,
> so back-to-back loads differ by 2.22e-16 m, one ULP, which changes
> `build_sdf_cached`'s content hash and forces a rebuild every run. Seed that sampling."
> **[cited]**

and the narrowed follow-up: *does the canonical `sim_standing.py` also call
`load_vehicle` without seeding first? If so, every canonical run has been rebuilding the
SDF unnecessarily.* **[cited]**

## Answer 1: yes it is unseeded, and no, that costs the canonical runs nothing

**[read, `renders/yaris_render_s1/sim_standing.py`]** and **[measured, static audit]**:

- `load_vehicle` is called **twice**, at lines **332 and 333**, for the determinism
  probe. That is **120,000 surface samples per run**.
- There is **no `np.random.seed` anywhere in the file**. The only RNG is
  `np.random.default_rng(seed)` at line **165**, which is a *local* Generator, is not
  the legacy global state, and lives inside `StandingFloodScene.__init__`, which is not
  reached until line 397, after both loads. It cannot affect them.
- **The file contains zero SDF references.** No `add_sdf_collider`, no
  `build_sdf_cached`, nothing. The canonical path is the free-rigid material-8 path
  (`set_material_range(..., "rigid", ...)` then `finalize_rigid_bodies()`) plus analytic
  planes.

So the answer to the narrowed question is: **the driver is unseeded, but there is no SDF
cache to miss, so the "every canonical run has been rebuilding the SDF" cost does not
apply to the 17 gated runs.** The mechanism is real; its stated consequence lands on the
SDF-collider path, not on the canonical one. This should not be written up as a cost
already paid by the published runs.

## Answer 2: the magnitude, measured

Two back-to-back unseeded loads of the canonical Yaris hull, 327,212 vertices
**[measured]**:

| Quantity | Value |
|---|---|
| extent delta, **before** `canonicalize()` | [1.46e-05, 1.06e-05, **1.85e-04**] m |
| max vertex delta, **before** `canonicalize()` | **2.67e-04 m** |
| max vertex delta, **after** `canonicalize()` | **5.55e-17 to 1.11e-16 m** |
| vertices differing after | 179,690 of 327,212 |
| particle count (load-time spacing) | 1563 both loads, stable |

The pre-canonicalize perturbation is **2.67e-04 m**, not a rounding artifact: it is the
real spread of a 60,000-point surface sample's bounding box. `canonicalize()`
(`sim_standing.py:96-105`) then recomputes the shift from the **mesh vertices**, which
cancels the sample dependence exactly in real arithmetic and to within half an ULP in
float64 **[read + measured]**.

So the surviving residue is **1.11e-16 m at most**, which is **half** of float64 eps
(2.22e-16), not one ULP of it. The dispatch's "2.22e-16, one ULP" is the right order of
magnitude and the right mechanism; the measured value is a factor of two smaller. This
matters only because it is the kind of number quoted from memory rather than measured.

## Answer 3: the cache really does miss, but not on every run

`_hashkey` (`warpmpm/geometry/mesh_sdf.py:520-535`) is a SHA1 over the raw float64 bytes
of the vertex array **[read]**, so a single differing bit changes the key. Structurally
the miss is certain given any difference at all.

**20 unseeded loads produced 13 distinct cache keys**, with the most common key
recurring 7 times **[measured]**. So on a persistent cache the miss rate is roughly
**two thirds**, not 100 percent. "Forces a rebuild every run" is close but slightly
overstated; "misses about two runs in three" is what was measured.

A caution against my own first pass, recorded because it is the same trap twice: an
initial 8-load probe returned only **2** distinct keys and I very nearly wrote up "the
cache costs about two builds ever". Widening to 20 loads refuted that outright. Eight
draws could not distinguish a binary outcome from a heavy-tailed one.

## Answer 4: the written fix works today on LS6 and is inert on trimesh 5

This is the finding that matters most, because the failure is **silent**.

The fix already written into `simulation/moving_vehicle_sdf_exploratory.py` is
`np.random.seed(args.mesh_seed)` immediately before the load **[cited]**. Whether that
works depends entirely on the trimesh version, and trimesh changed its RNG source:

| Where | trimesh | `seed=` kwarg on `sample()` | `np.random.seed()` reproduces? |
|---|---|---|---|
| **LS6 login node** | **4.12.2** | **absent** | **YES** **[measured on LS6]** |
| This Mac | 5.0.0 | present and works | **NO**, 0 of 5 repeats **[measured]** |

On trimesh 5.0.0 two `np.random.seed(7)`-preceded draws differ by **4.17 m** in the
worst coordinate, i.e. they are entirely independent samples; the version uses
`np.random.default_rng` internally and ignores the legacy global state **[measured]**.

**Consequence.** The written fix is correct on LS6 *today* and becomes a **no-op the
moment trimesh is upgraded to 5.x**, with no error and no warning. The runs simply stop
being reproducible while the seeding line still sits there looking correct. That is a
worse failure than having no fix, because the line is load-bearing evidence in a
reproducibility claim.

**Durable form**, implemented as `seed_mesh_sampling()` in `analysis/seeding_audit.py`
for reference: try `mesh.sample(count, seed=k)` and fall back to `np.random.seed(k)`
before `mesh.sample(count)` on a `TypeError`. That survives both versions.

**Request, not an edit.** `simulation/moving_vehicle_sdf_exploratory.py` and the SDF
driver are **D9's files** and the sampling call itself is upstream at
`warpmpm/vehicle.py:234` **[read]**. This dispatch does not touch either. The requested
change is: replace the bare `np.random.seed(...)` with the two-branch form above, or
pin trimesh and record the pin. **Owner: D9.**

## Answer 5: a demonstrated cache hit

With the sampling genuinely seeded (monkeypatched for the duration, which emulates the
corrected upstream line without editing upstream), **3 consecutive loads produced 1
distinct cache key**, `3e7495763cc41b8f` **[measured]**. Unseeded, the same test
produces a different key most times. That is the demonstrated hit the dispatch asked
for, and it confirms the fix mechanism is real once the seed actually takes effect.

Control included: seeding with *different* seeds must produce *different* keys, and does.
Without that control, "identical keys" would also be consistent with the seed being
ignored and the loads coinciding by chance.

## A methodological correction to this audit itself

The first version of this audit inferred "does `np.random.seed` control trimesh?" from a
**single** same-seed load pair compared through `canonicalize()`. That inference is
unsound and was measured to be unsound: because `canonicalize()` collapses the outcome
onto a small set of nearby float64 values, two *independent* unseeded loads land on the
same value a fair fraction of the time. Back-to-back runs of the audit reported
`bitwise_identical` **True** and **False** for the same trimesh version. The verdict now
comes from `q3_direct_seed_control()`, which tests `mesh.sample()` **directly with 5
repeats**, where two draws from different RNG states differ by metres rather than ULPs
and no degeneracy exists.

## What was NOT tested

The dispatch's Part B also cites a non-determinism symptom: three runs at identical
configuration giving `settle_vmax_final` 0.865234, 0.861557 and 0.594807, two failing
the settle gate and one meeting it **[cited]**. That is attributed to non-associative,
order-dependent GPU reductions **[cited]**. **This audit does not test that**, and the
two mechanisms must not be conflated: the sampling non-determinism documented here is a
CPU-side, pre-solver geometry perturbation of at most 1.11e-16 m in vertex position,
whereas an order-dependent reduction acts inside the solver every substep. Seeding the
sampling would not fix a reduction-order symptom.

The recommended practice for that separate issue stands as cited and unimplemented here:
report **outcome spread** and **gate-pass frequency** across repeats rather than a single
run; no universal repeat count exists; independent-start ensembles are the stronger
convergence check **[cited]**. `analysis/stationarity.py`'s `verdict_probability()`
provides the reporting form for it once repeats exist.

Also untested: whether `determinism_identical` in the canonical summaries can see any of
this. It compares `n_particles` and `lim` only **[read, `sim_standing.py:387-390`]**, and
the particle count was stable across loads here **[measured]**, which is consistent with
the standing observation that the flag reports True while `metrics.csv` files differ.

## Addendum, same day: the `interior_probe` question, and three claims corrected

### `interior_probe` is real. DeepWiki was right and the grep was a false negative.

A check reported that `grep -rn "interior_probe"` against the pinned tree "returned
NOTHING, so that answer is stale relative to 544c93dd". The grep result is accurate; the
inference from it is not, for **two independent reasons**, either of which alone would
invalidate it.

**Reason 1: `geometry/mesh_sdf.py` is not vendored at all.** The pinned tree
`third_party/mpm-engine-544c93dd-solver-core/` contains exactly **four `.py` files**
**[measured]**: `core/solver.py`, `kernels/mpm_solver_warp.py`, `kernels/mpm_utils.py`,
`materials/__init__.py`. Its own `VENDORED.md` says so, and the companion tree
`third_party/mpm-engine-544c93dd/` is described there as "a partial pull for render". A
combined walk of both trees returns **0 hits** for `_hashkey`, `build_sdf_cached` and
`interior_probe` **[measured]** — because the entire SDF cache module is absent from the
repo, not because the symbol is absent from the engine. Searching a partial vendoring
for a symbol it never contained cannot date anything.

**Reason 2: the upstream copy is now unreadable, and the recursive form fails
silently.** `~/Downloads/mpm-engine-main/` became TCC-blocked partway through this
session (it was readable earlier: `warpmpm/vehicle.py` and `geometry/mesh_sdf.py` were
both read directly, and `vehicle.py` was imported successfully). After the block:

```
grep -rn "interior_probe" <dir>/   ->  0 hits, exit folded into the pipe   <-- LOOKS ABSENT
grep -n  "interior_probe" <file>   ->  "Operation not permitted"           <-- HONEST ERROR
```

**[measured]** The recursive form needs directory enumeration, which is what TCC blocks,
so it reports zero rather than failing. A Python `re` walk behaves the same way and
worse: `Path.rglob("*.py")` returned **0 files** for a tree that has dozens, with
`exists()` still True. **On this Mac, "a recursive search returned nothing" under
`~/Downloads` is not evidence of absence.** That is the H0 rule again in a new place:
the blind spot is now TCC, not `.gitignore`, and the standard H0 fix (`/usr/bin/grep`)
does **not** help because the block is per-directory, not per-tool.

**What `interior_probe` actually is**, read directly from
`warpmpm/geometry/mesh_sdf.py:520-535` while the tree was still readable **[read]**:
it is the fifth parameter of `_hashkey`, and when it is `None` it defaults to
`0.5 * (verts64.min(axis=0) + verts64.max(axis=0))`, the vertex bounding-box midpoint.
So it is a **function of `verts`**, not an independent input. It therefore adds no
variation of its own, and **the Part B conclusion is unchanged**: the key moves because
the vertices move.

### The RNG, cited from a path that is actually in the repo

`third_party/mpm-engine-544c93dd/vehicle_main.py:134` **[read]**:

```python
pos = np.asarray(mesh.sample(60_000), dtype=np.float64)
```

That is an in-repo, readable, pinned-SHA confirmation of the 60,000-sample draw, and it
should be the citation from now on rather than a `~/Downloads` path that may be blocked.

**But do not cite it as the code the canonical runs ran.** `sim_standing.py:12` imports
`solidify_watertight` **[read]**, and `vehicle_main.py` contains **zero** occurrences of
that name **[measured]**, so this vendored copy is an earlier or partial variant of
`warpmpm/vehicle.py` despite carrying the same pinned SHA in `PINNED_SHA.txt`. It
corroborates the *mechanism*; it is not the gated code path.

### Three claims corrected against measurement

| Claim as received | Measured here | Status |
|---|---|---|
| "differs by one ULP (2.22e-16 m) between back-to-back calls" | The **draw** differs by **2.67e-04 m**. Only *after* `canonicalize()` does it collapse to **5.55e-17 to 1.11e-16 m**, which is a **half** of float64 eps, not one eps. | Right mechanism, wrong number, and the 2.67e-04 m is the physically meaningful one |
| "the SDF cache never hits and every run pays a full rebuild" | **20 unseeded loads gave 13 distinct keys**, most common recurring 7 times, so a persistent cache misses about **two runs in three**. | Overstated |
| "This is your Part B item and it is now measured" (in canonical) | The **unseeded double load** is confirmed in canonical, exactly as described. But `sim_standing.py` contains **zero SDF references**, so the canonical runs build no SDF and pay **no** rebuild. | Half confirmed: the driver defect is real, the cost lands on the SDF-collider path only |

The distinction in the third row is the one that matters for a write-up: **the 17 gated
runs did not pay this cost**, and saying they did would be a claim about published runs
that the source refutes.

## Reproduce

```
python analysis/seeding_audit.py \
    --src   /Users/josie/Downloads/mpm-engine-main/src \
    --hull  vehicle_geometry_research/yaris_coarse_v1l_watertight.ply \
    --out   data/seeding_audit_2026-08-14
```

Needs numpy and trimesh; no warp, no torch, no GPU.
