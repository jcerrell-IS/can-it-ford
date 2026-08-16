# D4: brake state cannot overturn a SLIDE verdict, and it destroys the only STUCK one

2026-08-16. Branch `claude/r5-physics`. Mac only, no GPU.

Claim tags: **[read]** primary source this session, **[measured]** computed here from local
data, **[derived]** algebra from tagged inputs, **[recalled]** from memory, the register or
a sibling's commit, **[inferred]** reasoning that a re-run would be needed to confirm,
**[unreviewed]** no physics-skeptic pass.

---

## 1. The finding, stated first

**Brake state cannot flip any of the 16 SLIDE verdicts. It threatens exactly one verdict,
the single STUCK, and it threatens it in the direction of SLIDE.**

> **ARGUMENT CORRECTED 2026-08-16 by adversarial review; the conclusion survives on a
> different warrant. See `R5_PHYSICS_SKEPTIC_CORRECTIONS.md` B2.** The version below argued
> only about sliding. But `simulation/failure_modes.py:33` and `:230-234` make the reported
> mode a **severity-ranked competition**, `MODE_SEVERITY = (SLIDE, TOPPLE, FLOAT)` with
> `mode = reached[-1]`. **A SLIDE verdict does not need sliding to stop in order to flip;
> it only needs a higher-ranked mode to trigger**, and lower friction raises surge
> acceleration, which is what TOPPLE gates on. My argument never addressed the only
> mechanism that could refute it.
>
> **The bound that actually settles it**, computed in review: every run's peak surge
> acceleration is a 1- or 2-frame spike, and the sustained 3-frame level is 0.08 to 0.51 of
> `ssf`, worst case `sweepV_g64_v3p0` at `T3 = 0.721`. Removing friction entirely can add
> at most `mu*(1+e) = 0.55 x 1.05 = 0.578 g`. Then `0.721 + 0.578 = 1.299 < 1.42 = ssf`, so
> **no run can reach TOPPLE by friction removal alone**. FLOAT is further still: only
> `sweepV_g64_v3p0` clears the lift gate at all, with zero frames where lift and vertical
> speed hold together, and friction is tangential so there is no first-order lift path.
>
> Read the section below as **the direction, plus that bound**. The direction alone was not
> sufficient, and an argument that reaches the right answer without engaging the refuting
> mechanism is not a verified argument.

The direction is the whole answer and it is the opposite of what "could this flip our
verdicts?" first suggests. Releasing the brake *lowers* the effective friction, which
*increases* sliding. A verdict that already says SLIDE cannot be undone by making sliding
easier. So:

- the 16 SLIDE verdicts are **robust to brake state** and become more robust, not less;
- `sweepV_g64_v0p5`, the one STUCK run, is the only verdict at risk, and it goes
  **STUCK -> SLIDE**;
- `g96_m2337`, the fragile one at a **one-frame** margin **[recalled]**, is fragile toward
  *becoming* STUCK, so lowering friction moves it **away** from its boundary. The most
  fragile verdict in the set is fragile in the direction brake state does not push.

That last point matters: the run everyone worries about and the run brake state endangers
are different runs.

## 2. What the source says, and whose reading it is

> **CAVEAT ADDED 2026-08-16, and it was missing from the version below.** D1's own source
> record says verbatim: "**Status: OPEN.** Do not treat the numbers below as final until
> someone with publisher access reads the corrigendum." The corrigendum
> `10.1016/j.rineng.2025.107527` exists and is **unread**. Every quantitative row in this
> section inherits that. Separately, "0.3x lower" is **ambiguous** between a factor of 0.3
> and a 30% reduction; D1 and I independently chose the same reading, and one source read
> twice is not corroboration.

From Nihei 2025, quoted verbatim in D1's `13f7a2d` from the abstract **[recalled from D1's
commit; I have not read the abstract myself, so this is second-hand and tagged as such]**:

> handbrake disengagement reduces the rolling resistance coefficient (=0.0250 and 0.0242)
> by approximately an order of magnitude than the typical static friction coefficient
> (approximately 0.30)

> Critical sliding velocity approximately 0.3x lower for unbraked vs. braked

So 0.0250 and 0.0242 are **rolling resistance**, contrasted against a static friction of
about 0.30. That closes the unit question D1 had previously only inferred.

**The 0.3x factor has a mechanism, and checking it is what makes the rest of this
trustworthy.** Balancing hydrodynamic drag, which goes as `v^2`, against Coulomb friction
`mu*N`, which does not depend on `v`, gives `v_crit ~ sqrt(mu)`. Then **[derived]**:

```
sqrt(0.0250 / 0.30) = 0.2887
```

which reproduces the paper's reported ~0.3x. The scaling law and the published number
agree without being fitted to each other, so `v_crit ~ sqrt(mu)` is the right lever and I
can use it below. Had they disagreed I would have had no basis for section 4.

## 3. Our model implicitly assumes a braked vehicle, and a more braked one than AR&R's

`sim_standing.py:154` sets `floor_friction=0.55` as the default and `:210` applies it to
the single floor plane; the four walls are `friction=0.0` at `:214` **[measured, read
live]**. That is the only frictional contact in the scene.

Two consequences, and the second is the sharper one:

1. **The model has no rolling degree of freedom at all.** The hull is a rigid particle
   cloud with no wheels, so it can only slide, never roll **[recalled]**. Brake state is
   therefore not representable in the current setup except through the single
   `floor_friction` scalar. There is nothing in the scene that *could* roll.
2. **0.55 is not merely "braked", it is the most sliding-resistant assumption in play.**
   It is **1.83x** AR&R's own assumed 0.30 **[derived]**, and AR&R concedes in its own
   words that 0.30 is "the assumed" value **[recalled from D1's `13f7a2d`]**. So the
   canonical runs sit at the far end of the friction range, the end most favourable to a
   vehicle staying put.

## 4. Why the STUCK verdict is the one that breaks, with its mechanism

`sweepV_g64_v0p5` is STUCK not because the vehicle never moved, but because it moved and
then **stopped**. Measured directly from its `metrics.csv` **[measured]**:

| | value |
|---|---|
| frames with `abs(dx) >= 0.05 m` | 54, first at frame **37** |
| frames with `abs(vx) >= 0.05 m/s` | 8, last at frame **8** |
| frames satisfying **both** | **0** |
| `max abs(dx)` | 0.05678 m, at frame 63 |
| `max abs(vx)` | 0.26437 m/s, at frame 2 |
| speed at the first frame drift clears its gate | 0.00642 m/s, **0.128x** the gate |

The two gates are never open at the same time. The speed gate shuts at frame 8; the drift
gate does not open until frame 37. In between, the vehicle decelerated by a factor of
about 40. **Floor friction is precisely what decelerates it.** So the STUCK verdict is not
a statement that the flow was too weak to move the vehicle; it is a statement that friction
stopped the vehicle before it drifted far enough, and friction is exactly the term brake
state controls.

This also shows why `ratio_slide = 1.1356` for this run must not be read as a near-miss on
magnitude alone: the verdict turns on **simultaneity**, not on peak size. That is CLAUDE.md
item 12(a)'s trap, and it applies here in a form worth restating: `ratio_slide >= 1` on a
STUCK run does not mean it nearly slid.

## 5. How far the threshold moves

The velocity sweep brackets the critical velocity directly: `v = 0.5` is STUCK and
`v = 1.0` is SLIDE, so `v_crit(mu=0.55)` lies in **(0.5, 1.0]** m/s **[measured]**. Scaling
by `sqrt(mu)` **[derived]**:

| assumption | mu | factor | implied `v_crit` | effect on the STUCK run at v = 0.5 |
|---|---|---|---|---|
| ours, canonical | 0.55 | 1.0000 | (0.500, 1.000] | STUCK, as observed |
| AR&R / Nihei braked | 0.30 | 0.7385 | (0.369, 0.739] | **straddles 0.5, INDETERMINATE** |
| Nihei unbraked | 0.0250 | 0.2132 | (0.107, 0.213] | **entirely below 0.5, flips to SLIDE** |
| Nihei unbraked | 0.0242 | 0.2098 | (0.105, 0.210] | **entirely below 0.5, flips to SLIDE** |

Two readings, and I want both on the record:

- **Unbraked: the STUCK verdict does not survive.** The whole implied `v_crit` interval
  sits below the run's 0.5 m/s, so this does not depend on where in the bracket the true
  value lies **[derived, but the flip itself is [inferred]: confirming it needs a re-run at
  a rolling-resistance floor friction]**.
- **Even at AR&R's own 0.30 the answer is indeterminate**, because the interval straddles
  0.5. That is a weaker claim than the unbraked one and I am not going to state it more
  strongly than "cannot be resolved without a run".

**What this is worth for the paper.** The project's question is whether it is safe to
attempt a crossing, and a SLIDE verdict is the cautious answer. The single run in the
canonical set that says *the vehicle stays put* is the one that assumes the handbrake is
on, and it is the one that does not survive the handbrake being off. **The canonical set's
one reassuring result is its least robust one.** That should be said plainly rather than
left for a reviewer to find.

## 6. What it would take to test, and it is cheap

One parameter. `--floor-friction` already exists at `sim_standing.py:309` **[measured]**,
so representing an unbraked vehicle needs no code change at all: re-run `sweepV_g64_v0p5`
at `floor_friction = 0.0250` and at `0.30`, and read the verdict. No solver edit, no new
geometry, and `sim_standing.py` stays untouched so its sha256 still stamps the run.

**Queued behind the TACC socket, not started.** Both sockets were cold again at 21:12 by
typed return. When they warm: batch via `tacc_submit`, never idev, on the same evidence as
before, 629 SU remaining **[recalled]**. This is a two-run job and belongs in the same
batch as the repeat runs already queued for the N = 1 peak-uncertainty problem, because
both want repeats at the same configuration.

A caveat that limits the whole section: the friction scalar stands in for a wheel that does
not exist in the model. Setting `floor_friction = 0.025` simulates *a body sliding on a
very slippery floor*, not *a car rolling*. Those coincide in the force balance that sets
`v_crit`, which is why the substitution is defensible for this question, but they do not
coincide in general and the substitution should not be reused for anything involving
rotation or wheel dynamics.

---

## 7. Citation hygiene: the two-Steffen trap, spelled out

Recorded here as well as in `R5_PHYSICS_SETTLE_AND_UNCERTAINTY.md` section 6, because
CLAUDE.md L-5 and the register both name "Steffen" with **no identifier**, and a future
reader will hit the name before they hit either document.

**There are two different 2008 MPM papers by overlapping author groups. Do not merge
them.**

| | authors | identifier | what it is |
|---|---|---|---|
| **the one this project relies on** | Steffen, Kirby, Berzins (**three**) | `10.1002/nme.2360` | "Analysis and reduction of quadrature errors in the material point method (MPM)" **[read, title confirmed via Unpaywall]**. Closed access. Quadrature error growing under grid refinement at fixed particles-per-cell, which is the mechanism CLAUDE.md item 5's g48/g64/g96 non-monotonicity needs. |
| the other one | Steffen, Wallstedt, Guilkey, Kirby, Berzins (**five**) | `10.3970/CMES.2008.031.107` | implementation choices, CMES. **Title not asserted here**: Unpaywall returns no record for this DOI, so I could not confirm it from a primary source. |

CLAUDE.md L-5 names "Steffen, Kirby and Berzins 2008", which is the **three**-author paper,
so L-5 already points at `10.1002/nme.2360` by its author list even though it gives no DOI.
Neither DOI, and not the name "Steffen", appears in any of the repository's 9 `.bib` files
or in any `.tex` **[measured]**. Adding the identifier to CLAUDE.md L-5 and to the register
is a coordinator action; neither is in my scope.

---

## 8. Status

Everything above is **[unreviewed]**: no physics-skeptic pass has run. The one claim that
needs a run rather than an argument is the STUCK flip, and it is labelled **[inferred]**
throughout rather than reported as a result.
