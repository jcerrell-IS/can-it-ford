# R5-D1 unit 31: the GNN/mesh-licence audit, a bibliography year error, and a third novelty candidate

Date 2026-08-17. Branch `claude/r5-research`. **Sections 2 and 3 are for D2**
(E8 scope). Section 4 is for whoever owns the novelty paragraph.

Second of the two documents unit 29 flagged: `GNN Surrogates for Fluid-Rigid
Coupling & NCAC/CCSA Vehicle-Mesh Reuse: A Provenance-Disciplined Assessment`.
Register checked first, per K0.

---

## 1. Already in the register, so not restated

Register **E8** already holds the licence conclusion, including the distinction
this document draws:

> **NCAC / CCSA vehicle-mesh redistribution rights are NOT established. Treat as a
> blocker, not a footnote.** ... **NHTSA-hosted** copies carry the "public
> information and may be distributed or copied" statement, whereas
> **CCSA-hosted** copies [do not] ... **Operative rule, unchanged and still
> conservative: do not commit any derived NCAC/CCSA geometry to the public repo,
> and do not include it in a DesignSafe DOI, without written permission or a
> confirmed licence.**

> ### CORRECTED 2026-08-17 (unit 43). FOR D2, THIS CHANGES WHAT CLEARS E8.
>
> **The clause "or a confirmed licence" was missing from this quotation until now,
> and I had closed the sentence with a full stop as though it ended there.** The
> register offers **two** routes to clearance, not one: written permission **or** a
> confirmed licence. My truncated version presented permission as the only route.
>
> **Why this matters operationally:** D2 is working E8. Under my version the only
> path is obtaining written permission from CCSA/GMU. Under the register's actual
> rule, **establishing a confirmed licence clears it equally**, which is a different
> and possibly cheaper line of enquiry given that unit 37 established all four
> shipped READMEs carry no licence text at all (a negative that is itself evidence
> about which route is available).
>
> Found by a systematic audit of all 81 block quotations across my 32 documents,
> run after I made the same class of error twice (unit 36, unit 40). **This is the
> third instance**, and unlike the first two it was affecting a sibling's live work
> rather than only my own conclusions.

GNS and Choi are also known: 5 and 2 register hits, 4 each in CLAUDE.md. None of
that is new.

## 2. FOR D2: this answers E8's own stated unresolved question

E8 says, verbatim:

> **UNRESOLVED and load-bearing: which side of that line the canonical Yaris falls
> on.** E1 sources the hull to DOI 10.13021/G8JS5D, which resolves to
> `ccsa.gmu.edu` ...

I queried DataCite directly. The record answers it:

```
title      : 2010 Toyota Yaris Finite Element Model Validation Coarse Mesh
publisher  : George Mason University      publicationYear : 2016
type       : Text / Presentation
rightsList : []                            <-- empty: NO licence statement
url        : https://www.ccsa.gmu.edu/wp-content/uploads/2016/11/
             2010-toyota-yaris-coarse-validation-v1.pdf
```

So the DOI our hull is sourced to is a **CCSA-hosted validation presentation with
an empty rights field**, not a model dataset and not an NHTSA-hosted copy. On
E8's own framing that places the canonical Yaris on the **non-permissive side of
the line**, and the audit's independent conclusion agrees: the DOI "carries an
*empty* rights field and points to a validation slide-deck PDF, not a CC0-waived
model dataset."

The audit adds that the George Mason Dataverse CC0 default does **not** apply,
because this is a University-Libraries-minted DOI on a PDF rather than a Dataverse
deposit, and that depositors can opt out of CC0 in any case.

**I am not resolving E8.** It is D2's item, the hull is already public on origin
per project memory, and deleting does not unpublish. What I am supplying is the
DataCite evidence for the question E8 itself flags as load-bearing.

Three further specifics with **zero** register hits, all actionable for D2:

- **FAR 52.227-14** is the governing data-rights clause the audit names. The
  register has one `17 U.S.C` hit but not the FAR clause. The audit's reasoning:
  contractor works are not automatically public domain under 17 U.S.C. 105, the
  government normally gets unlimited rights, but that is the *government's*
  licence and does not grant third parties redistribution.
- **The contact route**: Prof. Cing-Dao (Steve) Kan and Assoc. Prof. Dhafer
  Marzougui at CCSA/GMU, plus the FHWA/NHTSA Contracting Officer's
  Representative. Zero register hits for either name.
- **The citation the models' own pages list**: NCAC Working Paper **2011-T-001**,
  "Development & Validation of a Finite Element Model for the 2010 Toyota Yaris
  Passenger Sedan", GWU, June 2011. Zero register hits.

## 3. FOR D2: a year error in the paper's bibliography

`paper/can_it_ford_references_IEEE.bib`, entry `ccsa2010yaris`:

```bibtex
@misc{ccsa2010yaris,
  ...
  year = {2010},
  doi  = {10.13021/G8JS5D},
  note = {... Check distribution license terms before public release of derived meshes.}
}
```

**DataCite gives `publicationYear: 2016`.** The 2010 in our entry is the *vehicle
model year* (a 2010 Toyota Yaris), not the publication year of the cited item.

This is the **third** DataCite-registered deposit in this dispatch whose year was
wrong in our records, after `10.26190/unsworks/27433` (2024 to 2017) and
`10.4225/53/58e1dfd63f1f4` (2017 to 2015). Unit 14's refined rule predicted
exactly this: OpenAlex titles are reliable, but **years on DataCite-registered
repository deposits need checking against DataCite**. That rule now has a third
instance, and this one is in the paper's own bibliography rather than in my
working data.

Credit where due: the entry's `note` **already** says "Check distribution license
terms before public release of derived meshes", so the licence risk was flagged by
whoever wrote it. Only the year is wrong.

## 4. A third documented novelty candidate

The audit's Part 1 conclusion, and it is sharper than I expected:

> **GNN surrogate for fluid-rigid coupling: NOT demonstrated in Krishna Kumar's
> own published work.** The GeoElements GNS papers are validated only on granular
> self-interaction ... and, separately, fluid CFD past a *fixed* cylinder, never a
> freely-moving rigid body two-way-coupled to a fluid. Every published speedup
> number (300x to 5,000x) is granular-only or fixed-obstacle.

and its supporting external quote, from the NeurIPS 2025 ML4PS workshop, verbatim:

> "Despite these advancements, neural operators remain **underutilized for FSI
> scenarios involving unmounted rigid bodies**."

Zero register hits for "unmounted rigid" or "Vantassel". The audit calls this
"arguably the project's most defensible *novelty angle*".

**That makes three documented orphan areas surfaced in this dispatch**, all of
which survive the axis-closure of units 7, 16, 25 and 27:

| candidate | source | our existing work |
|---|---|---|
| reconstruction to collider with validated inertia | unit 16 section 2 | the gsplat-derived hull pipeline |
| viscoplastic mud bed coupled to a vehicle | unit 30 | `analysis/bingham_cfl_crossover.py`, a branch on origin |
| GNN surrogate for **free** rigid-body/fluid coupling | this unit | none found; GNS is MIT-licensed and reusable |

**Two cautions, both material.** The audit is explicit that a GNN speedup for
fluid-rigid coupling "has not been measured, by Kumar's group or by anyone I
located", so this is an **open hypothesis, not a result**, and any cited speedup
must be labelled granular-only. And the audit reports it could not find a
"Genesis/PVWM" Kumar paper, flagging that as not-found rather than non-existent,
which is a search miss on its part: arXiv **2607.00673** is exactly that paper and
is register G13. So this document is not infallible about the Kumar corpus.

## 5. Status

UNVERIFIED:
1. I have not read any GNS paper, the NeurIPS 2025 ML4PS benchmark, or NCAC
   2011-T-001. All are the audit's citations.
2. The audit could not open the model `.zip` interiors, so its "no licence"
   finding rests on web pages, the validation PDF and DataCite metadata. I
   confirmed only the DataCite half.
3. Whether the GNN direction is feasible or worth pursuing is a research-scope
   decision for Josie and Kumar, not a literature question.
4. The audit's own Kumar-corpus miss (section 4) means its Part 1 negative should
   be treated as bounded search, consistent with how it labels its other
   negatives.
