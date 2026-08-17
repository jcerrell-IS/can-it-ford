# R5-D1 unit 17: I resolved my own best finding's references and it did not survive

Date 2026-08-17. Branch `claude/r5-research`.

Unit 16 called the FORD/NO-FORD evidentiary asymmetry "the single most valuable
thing found in this whole dispatch", and listed as UNVERIFIED that it rested on
my plain reading of one catalog sentence whose references I had not resolved. I
resolved them. **It does not survive.**

What came out of the same read is smaller, solid, and primary-sourced, so this is
a downgrade rather than a loss.

---

## 1. The three references, resolved and verified

The sentence in `Physics Simulation Validation Protocol` cites [2, 3, 17]. From
that catalog's own table, with all three DOIs verified live against Crossref:

| ref | paper | DOI | access |
|---|---|---|---|
| [2] | Oberkampf, Trucano and Hirsch 2004, "Verification, validation, and predictive capability in computational engineering and physics", *Applied Mechanics Reviews* | `10.1115/1.1767847` | **closed** |
| [3] | Eca, Dowding and Roache 2020, "On the Interpretation and Scope of the V&V 20 Standard ...", ASME V&V Symposium | `10.1115/vvs2020-8826` | green OA via OSTI, **but no abstract exposed** |
| [17] | Easterling 2001, "Measuring the Predictive Capability of Computational Models", Sandia | `10.2172/780290` | green OA via OSTI, **readable** |

These are foundational V&V methodology sources, not flood or vehicle papers. That
alone is a qualification unit 16 did not make: **the asymmetry was never a claim
any flood-vehicle paper makes.** It is the catalog's application of general V&V
principles to the FORD decision.

## 2. The one I could read does not support it

Easterling 2001's abstract, READ DIRECTLY and in full from OSTI, lists eight
"primary messages". **None is an asymmetry between accepting and rejecting a
prediction, and none is a decision rule for uncertainty spanning a threshold.**
Asked directly whether it addresses either, the answer from the text is no.

So the position is:

```
asymmetry claim, references supporting it :  0 of 3
references checked                        :  1 of 3
that one                                  :  does NOT support it
remaining                                 :  [2] closed access, [3] no abstract exposed
```

**Do not put the asymmetry in the paper on this evidence.** It may still be
defensible from the bodies of [2] and [3], which I could not read, but as it
stands it is a synthesis sentence I cannot trace. Unit 16's section 1 is marked
down in place rather than deleted, so the reasoning stays visible.

I want to be plain about the shape of this error: I found a sentence that was
strongly favourable to the project, flagged it correctly as needing verification,
called it the best finding of the dispatch **before** verifying it, and it then
failed the first check. The flag was right; the billing was premature.

## 3. What the same read did produce, and it is better sourced

Easterling's message (4), verbatim from the abstract:

> **Model validation is not binary. Passing a validation test does not mean that
> the model can be used as a surrogate for nature.**

That is a primary-source statement of a principle this project already holds but
has been asserting on its own authority:

- CLAUDE.md item 6: "No gate is a physics validation. Every gate is a
  self-consistency or numerical-containment check."
- Project memory, the at-rest gate: every resolution contains a band width that
  passes the 10% gate, "so a PASS is not validation".

Both now have an external, citable, foundational source. That is worth more to a
Limitations section than an unsupported asymmetry would have been, because it can
actually be cited.

Two further messages from the same abstract bear directly on open project
questions:

> (6) **Code uncertainty-propagation analyses do not (and cannot) characterize
> prediction error** (nature vs. computational prediction).

That constrains what the project's own uncertainty reporting can claim:
propagating parameter uncertainty through the solver does not produce a bound on
error against reality. It pairs with unit 16 section 3's "report experimental,
parameter and discretization uncertainty separately".

> (3) A critical inferential link is required to connect observed prediction
> errors in experimental contexts to bounds on prediction errors in **untested
> applications**.

Our canonical runs are a single vehicle, single orientation, single bed
condition. Every extrapolation beyond that needs this link stated, which is the
same gap unit 15's coupling catalog listed as "extrapolation beyond measured
depth, velocity, orientation and bed conditions".

## 4. A third same-author citation trap

The project already uses this literature, which unit 16 did not notice:

- `docs/GATES.md:20` and `docs/GATES_GRIDAWARE.md:20` invoke "a verification
  result in the **ASME V&V 20** sense".
- CLAUDE.md **L-6** names **ASME V&V 40**.
- Register **G11** cites "**Oberkampf and Roy 2010**" for VVUQ
  adequacy-for-purpose.

Two things follow. **V&V 20 and V&V 40 are different ASME standards** (CFD
verification and validation with uncertainty, versus computational model
credibility), and the project cites both for different purposes. That is
legitimate but should be deliberate, because they are one digit apart.

And **"Oberkampf and Roy 2010" is not "Oberkampf, Trucano and Hirsch 2004"**.
Same lead author, different works, different years, different coauthors. This is
the **third** same-author-different-work trap in this dispatch, after the two
Steffen 2008 papers (unit 2) and the Hamid versus Muzzamil Shah collision (unit
3). The pattern is consistent enough to be worth a standing rule: **in this
corpus, an author surname plus a year is not an identifier. Always carry the
DOI.**

None of the three V&V DOIs above is cited anywhere in the repo outside
`.claude/`.

## 5. Status

UNVERIFIED:
1. Whether [2] Oberkampf 2004 or [3] Eca 2020 support the asymmetry in their
   bodies. [2] is closed access; [3] is green OA at
   `https://www.osti.gov/biblio/1774746` but that record exposes no abstract, so
   it needs the actual conference paper.
2. I read Easterling's abstract, not its body. An abstract listing eight primary
   messages is strong evidence about what the paper argues, but it is not proof
   that no asymmetry discussion appears inside.
3. Whether the project's V&V 20 usage in `GATES.md` is consistent with the
   standard's actual scope. Not checked, and outside my scope.
