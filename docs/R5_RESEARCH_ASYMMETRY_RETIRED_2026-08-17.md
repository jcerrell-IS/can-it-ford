# R5-D1 unit 18: the asymmetry claim is retired, and V&V 20 has a scope limit we should note

Date 2026-08-17. Branch `claude/r5-research`. Closes unit 17's UNVERIFIED #1.

Unit 17 downgraded the FORD/NO-FORD asymmetry to "0 of 3 supported, 1 of 3
checked". I have now read the **full text** of a second reference. It does not
support the claim either, and it says something stronger: the standard it
describes **explicitly excludes** the accept/reject aspect the claim rests on.

**Retire the asymmetry claim. Do not downgrade it further, retire it.**

---

## 1. Both readable references now checked, both negative

Both PDFs pulled from OSTI's full-text route (`osti.gov/servlets/purl/<id>`),
which serves the document even where the bibliographic record shows no abstract.

**[17] Easterling 2001, `10.2172/780290`, 2,818 lines extracted.** A search across
the entire text for asymmetry, burden of proof, accept/reject, conservative
decision, and threshold-spanning language returns **zero hits**. My unit-17
reading from the abstract is confirmed against the full document.

**[3] Eca, Dowding and Roache 2020, `10.1115/vvs2020-8826`, 716 lines.** One hit,
and it goes the wrong way for the claim. Verbatim, with the line breaks of the
two-column extraction removed:

> the need to make decisions about the model adequacy in the hierarchical
> validation procedure proposed in [8] requires the definition of validation
> requirements (step 1) and validation comparisons (step 3) to accept/reject the
> model components (and the complete model). **This pass/fail aspect of validation
> implied in [8] is not included in V&V20-2009**, that presents validation as step
> 2 of the V&V 10 framework.

So the paper cited for an accept/reject asymmetry states that the pass/fail aspect
**is not in the standard it is interpreting**. It also fixes the scope narrowly:

> The scope of the V&V 20 Standard is to estimate the accuracy of a mathematical
> model for a validation variable at **a single validation set point**.

**Status of the asymmetry claim:**

```
references                    3
checked                       2   (Easterling full text; Eca full text)
supporting                    0
actively contrary             1   ([3] says the pass/fail aspect is not in V&V 20)
unchecked                     1   ([2] Oberkampf 2004, closed access)
```

This is no longer "unverified". It is contradicted by one of its own cited
sources. Unit 16 section 1 should be read as retired, and I have said so there.

## 2. A scope limit worth recording, independent of the asymmetry

From the same paper, verbatim:

> Assessment of model accuracy at points within a domain other than the selected
> validation points (e.g., **interpolation/extrapolation in a domain of
> validation**) is **beyond the scope of the V&V 20-2009 Standard**. This topic is
> also not addressed in the V&V 10 documents.

Our canonical runs are a single vehicle, a single orientation and a single bed
condition, and every claim beyond those conditions is an extrapolation. So
neither V&V 20 nor V&V 10 supplies a framework for the step the project most
needs to justify. That is not a defect in our work; it is a statement about what
those standards can be cited for. It matches, from a second direction, unit 15's
coupling-catalog item "extrapolation beyond measured depth, velocity, orientation
and bed conditions" and Easterling's message (3) about the "critical inferential
link" required to reach untested applications.

## 3. A possible imprecision in `docs/GATES.md`, flagged not asserted

`docs/GATES.md` and `docs/GATES_GRIDAWARE.md` both say, at line 20:

> This is a **code verification** result in the **ASME V&V 20 sense**: the solver
> reproduces an analytic solution with a known answer.

Against the interpretive paper above, V&V 20's scope is estimating model accuracy
against **physical experimental data** at a validation set point. Reproducing a
closed-form analytic solution is code verification, which is a different activity
in the same family of standards. The GATES.md sentence itself calls it code
verification, correctly, and then attributes it to the standard whose described
scope is validation.

**I am flagging this, not asserting it, and the limit matters:** I have read
Eca, Dowding and Roache's *interpretation* of ASME V&V 20, not the standard
itself. ASME V&V 20's own title covers "Verification and Validation", so the
attribution may be defensible in a broader sense than this paper's scope
sentence. Someone with the standard should decide. If it does need changing, the
change is one clause in two files and neither is mine.

What is not in doubt on this evidence: **the pass/fail and the extrapolation
aspects are outside V&V 20**, so neither should be attributed to it.

## 4. What survives from this whole thread

The thread began as the dispatch's most favourable finding and ends as a retired
claim. Two things survive it, both primary-sourced this session:

1. **Easterling 2001, message (4), verbatim:** "Model validation is not binary.
   Passing a validation test does not mean that the model can be used as a
   surrogate for nature." A citable source for CLAUDE.md item 6 and for the
   at-rest-gate finding that a PASS is not validation.
2. **The V&V 20 extrapolation scope limit** in section 2, which constrains what
   the project may cite that standard for.

Both are smaller than the asymmetry would have been and both are real.

## 5. Status

UNVERIFIED:
1. **[2] Oberkampf, Trucano and Hirsch 2004** remains unread, closed access, no
   OA location. It is the only remaining route by which the asymmetry could be
   partially rehabilitated, and on 2 of 2 checked I would not expect it to.
2. Whether `GATES.md`'s V&V 20 attribution is wrong requires the ASME standard
   itself, which I do not have.
3. I searched Easterling by keyword rather than reading all 2,818 lines. A
   discussion of decision asymmetry that uses none of accept, reject, asymmetry,
   burden, conservative or threshold-spanning language would have been missed,
   which I judge unlikely but have not excluded.
