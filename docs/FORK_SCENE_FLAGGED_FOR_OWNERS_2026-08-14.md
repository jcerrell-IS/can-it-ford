# Flagged for other owners, from Dispatch 10

2026-08-14, branch `claude/fork-scene`. Written per the operating protocol's
flag rule 3: *"You are about to edit a canonical file outside your declared
scope."* Each item below is a change Dispatch 10 believes is correct and has
**deliberately not made**. Dispatch 10's declared write scope is
`simulation/fork_scene/`, `tests/test_fork_scene_domain.py`,
`scripts/fork_scene_crossslope.sbatch` and this `docs/` pair, on this branch
only.

Each item states what to change, where, the evidence, and how to falsify it.

---

## F-1. CLAUDE.md item 3: the word "unconditionally" is false

**Owner:** whoever owns CLAUDE.md. Relayed to **D4** (register) by the
coordinator, who verified it independently before relaying.
**Severity:** low for any published number, high for anyone deciding whether a
formulation is reachable without patching a vendored engine.

**Current text**, CLAUDE.md AUGUST 4 2026 AUDIT item 3:

> `core/solver.py:167-169` hardcodes `g=[0,0,-9.81]` inside
> `Solver.set_material()` **unconditionally**, not a library default, this
> wrapper's own hardcoded value.

**What the source actually says.** `[read]`
`third_party/mpm-engine-544c93dd-solver-core/core/solver.py:166-169`:

```python
params = {**params, **overrides}
self._sim.set_parameters_dict(
    {"material": name, "g": [0.0, 0.0, -9.81], **params}, device=self.device
)
```

`**params` is expanded **after** the `"g"` key in the dict literal, and later
keys win in a Python dict display. `:166` funnels `**overrides` into `params`.
So `set_material(material, g=[gx, gy, gz])` **overrides the hardcoded vector**.
It is a **default**, not an unconditional assignment.

The value then reaches the kernels: `[read]`
`kernels/mpm_solver_warp.py:742-743`:

```python
if "g" in kwargs:
    self.set_gravity(kwargs["g"])
```

**The conclusion of item 3 is unaffected and should be kept.** The same item
already states that `newtonian()` carries no `g` key and that the canonical
driver passes no override. Both remain true, so **all 17 gated runs did run at
exactly 9.81 m/s² in -z**. The defect is that the word "unconditionally"
contradicts the next sentence of its own item.

**Suggested minimal edit:** replace "unconditionally, not a library default"
with "as a DEFAULT that a caller-supplied `g=` override wins, because `**params`
expands after the key; `newtonian()` carries no `g` key and the canonical driver
passes no override, so all 17 gated runs ran at exactly 9.81".

**How to falsify this in one line, no GPU:**

```python
python3 -c 'p={"density":1000.0}; o={"g":[0.0,0.1712,-9.8085]}; p={**p,**o}; print({"material":"newtonian","g":[0.0,0.0,-9.81],**p}["g"])'
```

Prints the override if F-1 is right, `[0.0, 0.0, -9.81]` if it is wrong.

**Why it matters beyond pedantry.** It is what makes the bed-aligned-frame
cross-slope formulation reachable without patching a vendored engine at a pinned
SHA. Under the "unconditional" reading, the only way to express a cross-slope is
a tilted floor plane, which loses the solver's restricted-launch fast path and
spends 64% of the water depth on tilt at a 2% slope. See
`docs/FORK_SCENE_DESIGN_2026-08-14.md` section 4.2.

---

## F-2. `sim_standing.py:82` resolves in only one of two copies

**Owner:** anyone citing the canonical driver. Affects the dispatch text itself,
CLAUDE.md, and `analysis/verify_cpic_ground_clearance.py:48` and `:176`.
**Severity:** low now, rising, and it is the class of defect register D8c
already had to reverse once by hand.

`[run]` Two copies exist and they have diverged:

| path | lines | sha256 head | domain rule at |
|---|---|---|---|
| `renders/yaris_render_s1/_incoming/sim_standing.py` | 389 | `5215c38bed607ef6` | **:82** |
| `renders/yaris_render_s1/sim_standing.py` | 564 | `4696c3b2d39f4e28` | **:160** |

Register D4a records `_incoming/` as the canonical per-run tree, and the
dispatch's own parameter block names the 389-line sha256 `5215c38b` copy as the
gated driver. So `:82` is correct **for that copy** and wrong for the top-level
one.

**Suggested edit:** cite as `_incoming/sim_standing.py:82` wherever `:82`
appears alone. Do **not** repoint to `:160`: that would silently switch the
citation to a different, longer, non-canonical file. This is the same shape as
the refused `:132-137` → `:210-211` repoint that D8c reversed on evidence.

**How to falsify:** `wc -l` and `shasum -a 256` on both paths.

---

## F-3. The "18 cells across the depth" figure is not a validated regime

**Owner:** whoever maintains the resolution guidance. Relayed to **D13**
(engine go/no-go) by the coordinator, since it is an input to the engine
tradeoff. Appears in the Dispatch 10 text itself.
**Severity:** high for any feasibility argument built on it.

**Claim as circulated:** *"The validated near-floor regime is about 18 cells
across that depth, so dz = 0.01636 m."*

**What the record says.** `[read]` `docs/C1_ROOT_CAUSE_2026-08-07.md:337-347`:

> **But the fix in `20dd999` was already tested and did not work.** `20dd999`
> deepened C2 to 18 cells on the argument that the box grounded out for lack of
> clearance... `scripts/c2only.sbatch:19-20` on Vista passes `--depth-cells 18`
> explicitly, and that is job `894676`, whose four C2 arms all crashed at the
> same guard anyway. `run_c2`'s own default is still `depth_cells=10`.

So 18 is a **proposed fix in a validation arm that failed**, not a validated
regime. No cells-per-depth figure has been validated in this project. What has
been *run* is 2 cells per depth at g64 and 3 at g96, which CLAUDE.md L-3 already
records as a stated limitation.

**What this does and does not change.** `[run]` The dispatch's downstream
arithmetic reproduces **exactly** (246,772,943 cells; 884,736; 278.9x;
10,316,563 anisotropic; 23.9x), so the figures are auditable. What changes is
the conclusion drawn from them. Recomputed across the range, with the resolution
stated beside each figure:

- the cubic waste factor for a 30 x 12 x 3 m road is **25.0x**, from aspect
  ratio alone, at **no assumed resolution**;
- the forced cube is **10x** the canonical g96 tank in cells **at 2 cells across
  the depth** (the as-run g64 resolution), against **6,984x** **at 18 cells**.

**Suggested wording:** *"road scale is reachable only at a resolution this
project has already labelled a limitation"*, not *"road scale is impossible"*.

**How to falsify:** `python simulation/fork_scene/resolution_extent.py`. It
prints the dispatch's own figures and the swept table, and refuses to continue
if its CFL model fails to reproduce the recorded `substeps` of 11 and 16.

---

## F-5. REQUEST TO D13: three measurements on GH200 that decide the scene design

**Owner: D13.** Written per the coordinator's instruction to route node requests
through a findings doc rather than touching Vista JobId 911518 / c642-011, which
D13 owns. Dispatch 10 has **not** ssh'd to that node.

The coordinator's own three targets already cover most of this. What follows is
the part that is specific to Dispatch 10's arithmetic, phrased so the answer
maps directly onto a column of the table in
`docs/FORK_SCENE_DESIGN_2026-08-14.md` section 2.3.

### UPDATE 2026-08-14: what the FOSS assessment already answered, so node time is not wasted

`[inherited, documentation]` A documentation-based engine assessment was relayed
after this request was written. It **closes the terrain-ingest question** and
**partly** addresses domain shape. It does **not** touch the other three asks.
Revised status:

| ask | status after the assessment |
|---|---|
| terrain ingest (OBJ / heightfield) | **ANSWERED from docs.** `RigidTerrain::AddPatch` takes a Wavefront OBJ for both contact and visualisation; `SCM` initialises from a height-map image or OBJ. No node time needed. |
| domain **SHAPE** | **PARTLY.** No cubic or aspect-ratio constraint is *documented*, and BCE markers update rigidly from body pose with no single-scalar grid limit described. Absence of a documented limit is not proof, so **still worth one direct check**. |
| cell/particle **SPACING**, per-axis or single scalar | **UNTOUCHED.** Still Q1 below, and it is the half that decides whether the resolution story changes at all. |
| explicit timestep vs smallest spacing | **UNTOUCHED.** Still Q2. |
| fluid particles across a 0.2944 m depth | **UNTOUCHED.** Still Q3. |

**The SPACING half is now the highest-value single measurement**, because the
shape half has a documented presumptive answer and the spacing half has none, and
they buy completely different things (see the table below).

`[inherited]` **One further item worth carrying into any Chrono writeup, not a
request:** semi-empirical tyre models (Fiala, LuGre, Pacejka) query `GetHeight`
and `GetNormal`, which may be incomplete for an arbitrary rigid mesh, while rigid
and FEA tyres go through the contact engine and are unaffected. So the **terrain
representation constrains the tyre model, and the tyre model is where μ comes
from**. That lands directly on Dispatch 10's traction closed form; see
`docs/FORK_SCENE_DESIGN_2026-08-14.md` section 4.4. A cross-slope is a
heightfield and needs no arbitrary OBJ, so staying on a heightfield keeps the
semi-empirical tyre path and keeps μ a cited parameter rather than a contact-model
output.

### The distinction that decides it, and it is routinely conflated

Two *different* capabilities get talked about as one:

1. **Domain SHAPE** — can the computational domain have three independent
   extents (a 30 x 12 x 3 m box), or must the edges be equal (a 30 m cube)?
2. **Cell/particle SPACING** — is resolution a single isotropic scalar, or can
   it be graded per axis?

warpmpm fails **both**: `GridConfig` is one scalar for the edge and `dx` is
derived from it. `[read] core/solver.py:48-54`.

The two capabilities buy completely different things:

| what Chrono turns out to have | what switching buys Dispatch 10 |
|---|---|
| box shape + isotropic spacing | **~25x, and nothing else.** Operative column becomes `ROI box cells`. Road scale becomes runnable at 5 cells across the depth (9.7x g96 work) and stays out of reach at 10 and 18 (155.8x, 1,645.7x). |
| cube/shape-constrained + isotropic | **nothing here.** Finding becomes "neither engine expresses a long shallow channel." |
| per-axis gradeable spacing | **the resolution story changes**, which is the only outcome that reopens fine near-floor resolution at road scale. |

### Q1 (highest value). Domain shape and spacing, separately

In whatever call sets up the FSI domain (`SetComputationalDomain` /
`SetBoundaries` / the JSON `physics` block, whichever it actually is):

- can the three extents be set **independently**, or does anything force them
  equal or to a fixed ratio?
- is the SPH `initSpacing` / kernel `h` **one scalar**, or per-axis?
- is the **neighbour-search grid** cubic-celled? A box domain with a cubic
  search cell still gives isotropic resolution, which is answer row 1, not row 3.

Please answer shape and spacing as **two separate answers**, even if the API
couples them. Conflating them is the specific failure mode this request exists
to prevent.

### Q2. Does Chrono's explicit timestep also follow the smallest spacing?

Dispatch 10's cost model for warpmpm is `work ~ n_grid^4 / lim`, i.e. **a 2x
refinement costs 16x, not 8x**, because the acoustic CFL substep count scales as
`1/dx`. `[run]` That model was validated against the two recorded as-run substep
counts (11 at g64, 16 at g96) before use.

If Chrono::FSI-SPH is explicit WCSPH with `dt ~ CFL * h / c`, the same 4th-power
scaling applies and **the resolution half of this argument is
engine-independent**. Worth one line from the config or the docs. If Chrono
offers an implicit or dual-timestep option that breaks it, that is a much bigger
deal than the domain shape and should be reported loudly.

### Q3. Near-floor budget, in the units Dispatch 10 uses

The coordinator already asked for BCE marker spacing versus SPH spacing. The
number Dispatch 10 needs downstream is: **given `initSpacing` and the number of
BCE layers under a rigid floor, how many FLUID particles sit across a 0.2944 m
water depth?** That is the direct counterpart of this project's
`water_layers = 4` and `depth/dx = 2.000` at the g64 baseline (CLAUDE.md L-3),
and it is what makes a Chrono run comparable to the 17 gated runs at all.

### What Dispatch 10 does NOT need

- Any fording-validation claim. `docs/CHRONO_GH200_GO_NO_GO_2026-08-14.md`
  already records that Chrono's fording capability is demo-level, not validated
  against experimental fording data, and Dispatch 10 makes no use of it.
- Any performance benchmark. The cost model above is analytic and does not need
  a timing run to be useful.

### Handled without the node, so nobody spends time on it

Dispatch 10's cross-slope result is **statics** and is engine-independent:
`ΔM = -(W-B)[sin θ + μ(1-cos θ)]`, drag-independent, giving a vehicle-independent
`≈ S/μ` fractional traction loss. It transfers to Chrono unchanged and needs no
measurement on any node.

---

## F-4. Not a correction: a request, if anyone is editing `.gitignore`

**Owner:** nobody in particular; **D8** if it rescues `renders/`.
**Not urgent, and explicitly NOT a request to add a carve-out.**

`renders/` being ignored means `_incoming/sim_standing.py`, the canonical 389
line driver that four separate documents cite by line number, is **absent from
every worktree and from the LS6 clone** (checked live: the file does not exist
at `/work/11603/jcerrell0629/vista/can-it-ford/renders/...`). Dispatch 10's
runner therefore **reproduces** the canonical scene rather than importing it,
and asserts the result against `data/all_runs_inventory.csv` instead.

That turned out to be the stronger design, so this is recorded as context rather
than as a problem to fix. CLAUDE.md's own history says the walk-down carve-out
pattern has gone wrong three times and `.gitignore` line numbers have been wrong
three times in one day, so **do not add a carve-out on Dispatch 10's account**.
