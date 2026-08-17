# R5-D1 unit 39: I measured the flood fill, and the review broke most of what I built on it

Date 2026-08-17. Branch `claude/r5-research`.

**REVISED after physics-skeptic returned SEVEN BLOCKING issues.** The six measured
numbers reproduce exactly and independently. **Every interpretation I layered on
them was wrong**, and three claims are withdrawn outright. This document is the
corrected version; section 6 lists what was withdrawn and why, because the errors
are more instructive than the result.

**What survives, in one line:** the audit's 4.5628 m3 does not reproduce, the
comparable quantity is the **sealed cavity** rather than the filled volume, and
two implementations disagree on it by **2.1x** while the operation itself is
**bistable and grid-phase fragile**, so "flood fill at 25 mm" does not name a
result.

---

## 1. Provenance, which the audit lacks and which I nearly failed to supply too

```
input   vehicle_geometry_research/yaris_coarse_v1l_watertight.ply
sha256  b379fa4472c6806515d2145fb721de0f2ab9e0b8b042c01b93f4be34e9949a95
env     ~/Downloads/vehicle_meshes/mesh_venv   trimesh 4.12.2  numpy 2.5.1  scipy 1.18.0
```

Calibration: `trimesh` gives volume **3.5427387900160743 m3**, `is_watertight`
**True**, `euler_number` **-442**, and **`body_count` 1**, which is the condition
that makes genus 222 a valid reading and which my first draft never stated.
`1100 / 3.542739 = 310.4942` reproduces CLAUDE.md's canonical **310.494**.

**The script, in full, because the audit's original sin was shipping none and my
first draft repeated it:**

```python
import trimesh, numpy as np
from scipy import ndimage
m = trimesh.load(PLY, force='mesh')
vox = m.voxelized(pitch=p)
d   = np.pad(np.asarray(vox.matrix, dtype=bool), 1, constant_values=False)
st  = ndimage.generate_binary_structure(3, 1)     # 6-CONNECTED, see section 3
filled = ndimage.binary_fill_holes(d, structure=st).sum() * p**3
surf   = d.sum() * p**3
sealed = (filled - 0.5*surf) - m.volume           # shell-corrected cavity
```

## 2. The measured numbers

All twelve reproduce to four decimals under independent re-execution.

| pitch (m) | surface (m3) | filled (m3) | shell-corrected | sealed cavity |
|---:|---:|---:|---:|---:|
| 0.050 | 3.8653 | 7.3189 | 5.3863 | 1.8435 |
| 0.035 | 2.9074 | 7.0019 | 5.5482 | 2.0055 |
| **0.025** | 2.0734 | **6.7402** | **5.7035** | **2.1608** |
| 0.020 | 1.6931 | 4.3839 | 3.5373 | -0.0054 |
| 0.015 | 1.2608 | 4.1758 | 3.5454 | +0.0027 |
| 0.010 | 0.8571 | 3.9728 | 3.5443 | +0.0016 |

**The audit's 4.5628 m3 at 25 mm does not reproduce. I get 6.7402, +47.72%.**

## 3. Connectivity is a free parameter worth 3.25x, and I committed the audit's own sin

`scipy.ndimage.binary_fill_holes` defaults to `generate_binary_structure(3,1)`,
which is **6-connectivity** for the background flood. My first draft never said so.
Measured at 25 mm:

```
6-connected    6.740203 m3
18-connected   2.073906 m3
26-connected   2.073469 m3      (surface alone = 2.073 m3, i.e. nothing sealed)
```

**A factor of 3.25 on an undocumented default.** Under 18- or 26-connectivity the
voxelized shell leaks through diagonal-only seams and nothing is enclosed at all.
6-connectivity is the physically defensible choice, because a 26-connected leak
passes through a zero-area diagonal seam no fluid can cross, but that is an
argument I owed the reader and did not give.

My first draft criticised the audit at section 3(b) for "parameter-free apart from
pitch" being "literally true and materially misleading". **I had done the identical
thing one paragraph earlier.**

## 4. The real finding: the sealed cavity, not the filled volume

Filled volume is not comparable across implementations, because it carries a
voxel-shell term that scales with pitch. **Shell-corrected**, the fine pitches are
decisive:

```
p=0.010  ->  3.5443   vs mesh 3.542739   +0.04%
p=0.015  ->  3.5454                      +0.08%
p=0.020  ->  3.5373                      -0.15%
```

**At 10, 15 and 20 mm the fill seals nothing whatsoever.** It recovers the trimesh
volume to within 0.15%. So the comparable quantity is the cavity actually enclosed:

| | sealed cavity |
|---|---:|
| the audit, 4.5628 - 3.5427 | **1.020 m3** |
| this work at 25 mm, shell-corrected | **2.161 m3** |

and an independent connected-component measurement of the new cavity gives
**2.1743 m3**, agreeing with the subtraction to 0.6%.

> **NUMERAL COLLISION, read the unit.** This document contains **2.1743 m3**, a
> sealed cavity **volume**, and separately **2.165x**, the retired `solidify_columns`
> **fill ratio** (section 7). They are different quantities in different units and
> their numerals nearly coincide. The `check_claims` guard flagged the first as if
> it were the second, which is a false positive on the digits but a true warning
> about the hazard. CLAUDE.md item 13 records the same trap costing a real error
> when three `0.05` literals carrying two different units were treated as one value.
> **Deduplicate by name and unit, never by value.**

**The two implementations
disagree by 2.1x on how much void they seal.** That is the publishable result, and
it is a much stronger statement than "the number did not reproduce", because both
operations sit between the same two anchors and still differ by a factor of two.

## 5. The operation is bistable and grid-phase fragile, not "unconverged"

A 0.5 mm scan through the transition:

```
22.0 mm OPEN | 22.5 SEALED | 23.0 OPEN | 23.5 SEALED | 24.0 SEALED | 25.0 SEALED
```

and at 23.0 mm, **7 of 8 random sub-voxel grid phases seal**: the default phase is
the outlier. So the switch sits near **22.2 mm** and is **fragile to where the grid
origin happens to fall**, not a clean threshold.

Within each branch the quantity is stable, not scattered: the open branch is
converged to 0.15%, the sealed branch varies smoothly. **So "not converged, spans a
factor of 1.84" was the wrong description.** The correct one is a bistable
operation with a phase-sensitive branch selector, which is worse for
reproducibility than mere scatter, because two people running "the same" 22-to-23 mm
flood fill can land on branches differing by 2.1 m3.

**Aperture, measured rather than assumed:** dilating the 20 mm shell by a single
voxel (+20 mm) and refilling takes 4.3839 to 7.2556, so the leak closes at
**≲40 mm**. A Yaris window is several hundred mm. The leaks are **20-40 mm seams**
left by the mesh2sdf 256^3 reconstruction at +17 mm offset, and my "voxels bridge
the window openings" story was invention.

Where the cavity actually is, by connected component: the new component at 25 mm is
**2.1743 m3**, spanning x[-4.10,-0.97] and z[0.23,1.43]. Of the volume I could bin,
**82.7% lies above z = 0.65 m** and 17.3% below, reaching down to z = 0.25 m. So it
is cabin-dominant but not cabin-only, and it runs 3.6 m of a 4.28 m car.

## 6. What I withdraw

**W1. "My 6.7402 lands on the audit's own ~6.8 upper bound, so this is an
implementation difference rather than an audit error." WITHDRAWN.** The audit's 6.8
is `yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` at **6.8185 m3, genus
32, 25,663 verts**, a *different and deprecated* mesh which the audit itself calls
"the misleading one, not a point in its favour". Three reasons the agreement was
spurious: different object; it seals the **underbody** where 82.7% of mine is
**above z = 0.65 m**; and shell-corrected I have 5.7035, which is **-16.35%** from
6.8185, not "almost exactly". I reached for a reconciliation that let both parties
be right and did not check what the number referred to.

*One partial defence of the audit, which the review did not credit and I should:*
the same sentence gives an independent physical anchor, "a real sedan displaces
~55-60% of its bbox, i.e. ~6.2-6.8 m3". My shell-corrected 5.7035 against bbox
11.3533 is **50.2%**, which sits *below* that band, so this second anchor does not
rescue my claim either. It is worth recording that the audit had a physical
rationale and not only a bad mesh.

**W2. "35% discontinuity." WITHDRAWN, the figure is +53.75%.** 4.3839 to 6.7402 is
a 53.75% rise; 35.0% is the *fall* measured from the larger value. I switched
denominator between two claims in the same document and, in doing so, understated
my own headline.

**W3. "Flood filling lowers the canonical density by 11% to 52%." WITHDRAWN.** At
10, 15 and 20 mm it lowers it by **nothing**; the apparent drop is half-voxel shell
overhang with a known sign and a known correction (section 4). Only the sealed
branch moves the density at all. This was the claim I was most confident about and
it was measuring my own discretization.

**W4. The cabin/window mechanism. WITHDRAWN**, see section 5.

## 7. The question that actually matters, which my first draft missed

The mesh volume does **not** set the solver density. `sim_standing.py:170-171`
(**WARPMPM**, not Genesis):

```python
solid_volume = vehicle.n_particles * h ** 3
vehicle_density = vehicle_mass / solid_volume
```

`hull_m3` is only a preflight abort tripwire. So on its face none of this reaches a
gated run.

**But the enclosed-volume question reaches the solver by a different door, and I
never named it.** `warpmpm/vehicle.py:176` and `:179` choose between two fills, and
`solidify_columns`' own docstring at `:64-71` says it merges "wheel wells and
window openings into the solid", which is itself a bridging fill already shipped in
the repo. At the gated `h = 0.0736073618`:

```
solidify_watertight   n=8890    V=3.545402 m3   fill_ratio 1.0008   rho 310.26
solidify_columns      n=19234   V=7.670671 m3   = 2.165x hull       rho 143.40
```

**Those column-fill numbers are the 2.17x / ~7.7 m3 / 143 kg/m3 family that project
memory records as already RETIRED.** So my coarse-pitch values were re-deriving a
retired family by a third route without noticing. **A one-line change at
`vehicle.py:175` moves `solid_volume` by 2.165x**, which is the operationally
relevant version of this question and belongs to D4, not to me.

Note the reviewer's own disclosed non-reproduction: their `solidify_watertight` at
the gated h gives **8890** particles against the inventory's **8905** (register E3),
a -0.168% gap they could not close. Do not inherit 8890 as exact.

## 8. On the density band, and a guard that did its job

My first draft concluded the audit's qualitative claim survived because every pitch
landed inside the project's 100-300 kg/m3 range. The `check_claims` hook blocked it
against CLAUDE.md item 9: **that band is STALE.** The canonical hull is 310.494 and
all 17 gated runs realise 302.55 to 663.58, every one above it. Landing inside a
retired range validates nothing. Recorded because an automated guard caught a
reasoning error a human reviewer might have waved through.

## 9. Status

**Measurement: VERIFIED**, reproduced independently, twice, with the script above
and a hashed input. **Interpretation: heavily revised**, four claims withdrawn.

UNVERIFIED:
1. The shell correction `filled - 0.5*surf` is a first-order heuristic. It was
   validated on an icosphere (errors +0.56 / +0.19 / +0.01% at 50/25/10 mm) and it
   recovers this hull to 0.15% on the open branch, but it is not exact on the
   sealed branch, where I use it to derive 2.161.
2. I did not implement the audit's actual method (SDF grid plus marching cubes), so
   section 4 shows two implementations disagreeing, not one being correct.
3. Rogue and Silverado are untested, so the audit's 6.0985 and 9.2623 stand
   unexamined.
4. The 22.2 mm switch is located on this hull, this reconstruction and this
   voxelizer only. It is a property of the mesh's seams, so it will not transfer.
5. Whether any of this changes a gated verdict is D4's question. The mechanism is
   the `vehicle.py:175` fill choice, not anything measured here.
