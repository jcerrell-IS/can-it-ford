# R5-D1 unit 8: the resolution comparison, after an adversarial review killed my first version

Date 2026-08-16. Branch `claude/r5-research`.

I drafted a resolution comparison against Al-Qadami et al. 2023, did **not**
publish it, and sent it to the physics-skeptic subagent first. It came back
**NOT CLEAN with six blocking issues**. Three were substantive errors of mine and
one of them understated the other study's resolution by a factor of two, i.e. it
was wrong *against* my own argument. I re-verified every finding myself against
the PDF and the repo before accepting it. This document is the corrected version
plus the record of what was wrong.

---

## 1. What I was going to write, and why it was wrong

Draft sentence, never published:

> The closest comparable published study resolves the water depth about 3.8x
> better than our canonical g64 runs. They use a FLOW-3D finite-volume cell size
> of 0.05 m against a floating-instability depth of 0.38 m, which is 7.6 cells per
> depth. Our g64 runs sit at dx = 0.1472 m with realized depth 0.2944 m, which is
> exactly 2.000 cells per depth. [...] whereas our g48/g64/g96 study is recorded
> in CLAUDE.md item 5 as non-monotone and unconverged.

Five defects, each re-verified by me against the primary source:

**(a) "cell size of 0.05 m" is wrong for the vehicle.** They use two nested
blocks. Verbatim, p.7: "Two mesh blocks were used, namely (i) containing mesh
block and (ii) nested mesh block ... The containing mesh block captured both the
fluid and geometry domains with a cell size of 0.05 m". And p.6: "the mesh block
with a cell size of 0.05 m could not capture the car model details accurately.
Therefore, **a nested mesh block was defined with a cell size of 0.025 m to only
capture the vehicle domain**." So in the region that decides the stability
verdict their cell is 0.025 m. My draft understated their resolution 2x.

**(b) "3.8x" conflates two different things.** It decomposes exactly:
`2.9443 (cell-size ratio) x 1.2906 (depth ratio) = 3.800`, computed by me. Twenty-nine
percent of the headline was the fact that they floated at a deeper depth than we
ran, which is not resolution at all.

**(c) The "whereas ours is non-monotone" contrast is false.** Their own Table 1
mesh-independence series, now **independently extracted by me from page 6 of the
PDF** (see section 4, this is no longer carried from the review):

| cell size (m) | 0.100 | 0.075 | 0.05 | 0.025 |
|---|---|---|---|---|
| flow velocity (m/s) | 1.84 | 1.74 | 1.61 | **1.63** |
| step change | | -5.43% | -7.47% | **+1.24%** |
| Froude number (-) | 1.17 | 1.04 | 0.98 | **0.99** |
| step change | | -11.11% | -5.77% | **+1.02%** |

The final refinement **reverses sign in both series**. Theirs is non-monotone
too. Publishing that contrast would have been a falsifiable error any reviewer
holding the PDF catches immediately.

**(d) "selected 0.05 m on that basis" is not what they say.** Verbatim: "by
considering the **computational time and system capabilities**, a mesh block with
a cell size of 0.05 m was chosen to capture the fluid domain." Compute cost is
co-equal with convergence in their selection, and the two finest agree to "an
average percentage difference of 1%".

**(e) Cells-per-depth is the wrong instrument entirely.** A FLOW-3D cell resolves
the free surface sub-cell through the VOF fraction and the vehicle sub-cell
through FAVOR area and volume fractions. Our MPM background cell does neither:
the surface is wherever the particles are. Worse, "more cells per depth is
better" is finite-volume intuition, and CLAUDE.md L-5 records Steffen, Kirby and
Berzins 2008 as the citable mechanism for MPM **losing** convergence under grid
refinement at fixed particles per cell, which is our case. Our own g48/g64/g96
non-monotonicity is the local proof. The framing imports an ordering known to
fail in our own method.

Also flagged and accepted: my draft named neither the engine nor the vehicle.
Ours is **warpmpm** via `renders/yaris_render_s1/sim_standing.py`, never Genesis.
Theirs is a **Perodua Viva**, not a Yaris, and their 0.38 m and 0.36 m2/s are
Viva results. Register G5 and G8 already bear on both points.

## 2. The comparison I am entitled to make

Cell size only. No depth normalisation. No cells-per-depth.

> Al-Qadami et al. 2023 (`10.3390/su151713262`, *Sustainability* 15(17):13262) is
> the nearest published comparator **on vehicle scale and instability mode**, and
> not on vehicle, solver family or boundary conditions. It is a full-scale
> Perodua Viva in FLOW-3D v11.2, finite-volume VOF with FAVOR, under six-degree-
> of-freedom coupled motion, in an open channel with an inlet face and a pressure
> outlet. They discretise with two nested Cartesian blocks: 0.05 m in the
> containing block and 0.025 m around the vehicle. Our canonical g64 runs
> (**warpmpm**, via `renders/yaris_render_s1/sim_standing.py`) use a single cubic
> background grid at dx = 0.1472147236519959 m, so **their vehicle-region cell is
> 5.89x finer than ours and their far-field cell 2.94x finer**. We do not convert
> this to cells per depth, because the two studies report different depths and
> because MPM background-grid refinement at fixed particles per cell is not
> monotonically convergent (Steffen, Kirby and Berzins 2008). Their
> mesh-independence study tested 0.1, 0.075, 0.05 and 0.025 m and reported about
> 1% agreement between the two finest, in probe Froude number and flow velocity
> measured 3 m upstream of the vehicle. That is a flow-field check, not a check on
> the reported stability thresholds, and their Table 1 reverses direction at the
> final refinement. Our g48/g64/g96 study is likewise non-monotone, with larger
> swings and unconverged displacement magnitude, though all nine cases return the
> same NO-FORD verdict.

Ratios computed by me, from values read live on both sides:

```
our g64 dx                       0.1472147236519959 m   (data/all_runs_inventory.csv)
their containing block           0.05  m   -> ours 2.944x coarser
their vehicle-region nested block 0.025 m  -> ours 5.889x coarser
```

**And resolution is not the leading-order difference.** Our artificial sound speed
is 12.84523257866513 m/s against roughly 1481 m/s in water, our coupling is the
free-rigid velocity-averaging path, and our floor friction is 0.55 against their
stated 0.30. Each of those is a larger discrepancy than the mesh. A paragraph
that leads with resolution implies otherwise and would be misleading.

Two further disclosures the review required, both verified live in
`data/all_runs_inventory.csv`: the very run I am citing, g64_m1100, has
`passthrough_max_frac = 0.10670498480368847` and therefore **fails** gate P-2's
0.10 limit at `gates.py:147-148`
(**but see the qualifier below: that "failure" is not evidence of hull leakage**); and their vehicle mass is never published, so
no mass normalisation against our 1100 kg is possible. Do not infer their mass
from the 2021 companion's 9.2 kN buoyancy figure.

> **QUALIFIER on the P-2 disclosure, added after D4's `26971c0`, verified by me at
> source.** I disclosed the P-2 failure as if it were a leakage defect. It is not.
> `sim_standing.py:463-465` computes `lo_v, hi_v = veh.min(0), veh.max(0)` and then
> the fraction of water particles inside that **axis-aligned bounding box**, so
> `passthrough_max_frac` counts water in the *box*, not water inside the *hull*.
> CLAUDE.md item 4b independently records that the hull fills only **33.2%** of its
> own bounding box, so most of the box is void by construction. D4 measured the
> transparent-box null baseline, what P-2 reads if the vehicle displaced nothing at
> all, at **10.3 to 11.0%** for every run, against a gate set at 0.10. **The gate
> therefore sits essentially on its own null baseline and behaves as a pile-up
> test, not a leakage test.** The disclosure above stands as a fact about the gate;
> it should not be read as evidence that water passes through the hull.

## 3. The result worth leading with instead

The review's most useful contribution was not a correction. It was pointing out
that I was sitting on a better result and not using it.

| | depth | velocity | D x V | verdict |
|---|---|---|---|---|
| Al-Qadami 2023, Table 2 case 11 | 0.30 m | 1.35 m/s | 0.405 m2/s | **Sliding** |
| ours, g64_m1100 | 0.2944294473039918 m | 1.5 m/s | 0.4416 m2/s | **SLIDE** |

Both read live: theirs from the Table 2 run matrix in the PDF, ours from
`data/failure_modes_by_run_classified.csv` (`mode = SLIDE`,
`triggered_slide = True`, `triggered_float = False`) and
`data/all_runs_inventory.csv` (`velocity_ms = 1.5`).

Near-matched hydraulics, wholly independent method (FLOW-3D finite-volume VOF
against warpmpm MPM), wholly independent implementation, **same instability
mode**. That is a genuine cross-method agreement on the outcome that matters, and
it is worth more than any mesh ratio. It also sits comfortably with the fact that
our grid is coarser: the verdict agrees even though the discretisation does not,
which is the same shape as CLAUDE.md item 5's finding that the binary verdict is
grid-invariant while the displacement magnitude is not.

**Do not overstate it.** It is one case against one run, N = 1 on each side, with
different vehicles, different friction (0.55 against 0.30), different boundary
conditions and a 4.4% depth difference and an 11% velocity difference. It is an
agreement, not a validation.

## 4. Status

The six blocking issues are resolved by deletion or rewrite, not by argument. I
re-verified independently, and confirmed against the primary source or the repo:
the nested 0.025 m block, the compute-cost selection wording, the 3.8x
decomposition, our SLIDE verdict and velocity, and both cell-size ratios.

**Table 1 is now closed too.** It was tagged as carried from the review because
`pdftotext -layout` interleaves that table. Re-extracted page 6 on its own with
both `-layout` and raw mode and recovered the full series independently: velocity
1.84, 1.74, 1.61, 1.63 m/s and Froude 1.17, 1.04, 0.98, 0.99 across cell sizes
0.100, 0.075, 0.05, 0.025 m. Step changes computed by me: -5.43%, -7.47%,
**+1.24%** and -11.11%, -5.77%, **+1.02%**. The reversal at the final refinement
is real and is now READ DIRECTLY, not carried. The review's figures reproduce
exactly.

UNVERIFIED:
1. Their vehicle mass, unpublished. No mass normalisation against our 1100 kg is
   possible, and their 2021 companion's 9.2 kN buoyancy figure must not be used
   to infer one.
2. Whether MPM versus SPH or FVM is a defensible novelty axis remains a physics
   judgement for D4, not a bibliographic one.
3. Their reported 25% gap against Martinez-Gomariz Eq 12 does not reproduce
   cleanly (23.40, 26.51 or 30.56% depending on denominator). Do not repeat their
   25%. I have not resolved which denominator they intended.

Every number in section 2 and section 3 was read live this session from a named
file or the PDF. The comparison in section 3 states N on both sides, as required.
