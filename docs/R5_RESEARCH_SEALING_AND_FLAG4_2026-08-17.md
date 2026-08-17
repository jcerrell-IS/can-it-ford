# R5-D1 unit 40: the literature's sealing split, and FLAG-4 closed

Date 2026-08-17. Branch `claude/r5-research`.
**Section 2 is for D4.** Section 3 closes a flag I had carried since unit 7.

Unit 39 measured that the enclosed-volume choice moves `solid_volume` by **2.165x**
and handed the decision to D4 without saying what the literature does. This is that
answer, mined from an unread corpus document.

---

## 0. Search scope, stated because a negative from it would be bounded

`corpus_inventory` reports the primary corpus root
`/Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13` as
**PARTIAL/TCC-DENIED: 387 files, 308 readable**. **79 files, 20.4% of that root,
are invisible to every search I ran.** The connector's own rule says a partial
count is a broken probe, not evidence of absence. Totals across all six roots:
1,614 files, 1,535 readable.

Source document, previously unread:
`04_Validation_Literature_and_Citations/Experimental Configuration of the
Flood-Vehicle Stability Literature- What Was Physically Done.md`, 69 lines.

## 1. The finding: the literature does not agree on whether the test vehicle was sealed

That document carries a **"Vehicle condition"** column that nobody has pulled out.
Transcribed verbatim across all twelve studies:

| Study | Vehicle condition |
|---|---|
| Bonham & Hattersley 1967 | Rigid model |
| Gordon & Stone 1973 | Rigid model, front-wheel-drive weight distribution |
| Keller & Mitsch 1993 | **Sealed assumption; not validated** against experimental data |
| Teo 2010 / 2012 | Die-cast; some scaled fully submerged |
| **Xia et al. 2011** | **Water-filled models** (submerge before moving) |
| **Shu et al. 2011** | **Foam-filled watertight** |
| Toda et al. 2013 | **Deliberately allowed water ingress** |
| Xia et al. 2014 | **Sealed models** |
| Arrighi et al. 2015 | Rigid CFD body, not free to move |
| Kramer et al. 2016 | Watertight models; **prototype suffered water ingress** |
| Martinez-Gomariz et al. 2017 | **Foam-filled watertight** (no ingress) |
| Smith, Modra & Felder 2019 | Rapidly filled to limit ingress (<50 L pooling); **sealed with silicone** plus pump in deep tests |
| Shah et al. 2018/2020 | Scaled model, Froude similarity |

**The treatments are mutually incompatible and the split is roughly even:** sealed
or foam-filled in five studies, water-filled or ingress-permitted in three, solid
rigid in three, unstated in one.

**And the split is documented as first-order, not a detail.** The same document
records that Xia et al. 2011's water-filled models "differed significantly from
other studies (by up to an order of magnitude) with vehicles becoming submerged
before moving," inconsistent with field footage, and that **Shu et al. 2011
corrected this by scaling density and foam-filling the models.** So a change in
exactly this treatment is the recorded cause of the largest disagreement in the
incipient-motion literature.

Two further items worth having:

- **Sealing has a scale effect.** Kramer 2016's full-scale prototype "floated
  deeper than the model", and the document attributes it to sealing: model-scale
  watertight vehicles float too shallow. So a sealed *model* result does not
  transfer to full scale unchanged.
- **A citable direct method exists.** Martinez-Gomariz 2017 measured buoyancy
  directly with a "glass box 38.9 x 18.9 cm filled until no wheel touched ground,
  plus displaced-volume check, plus formula hb = Mc/(rho_f . lc . bc) + GC". That is
  a measured displaced volume rather than an assumed one, and it is the only such
  method named in the table besides Smith/Modra/Felder's traction-reduction rig.

## 2. FOR D4: what this does and does not say about `vehicle.py:175`

Unit 39 measured, at the gated `h = 0.0736073618`:

```
solidify_watertight   n=8890    V=3.545402 m3   rho 310.26
solidify_columns      n=19234   V=7.670671 m3   rho 143.40      = 2.165x
```

and `solidify_columns`' own docstring says it merges "wheel wells and window
openings into the solid", which is a **sealing** operation in exactly the sense
the table above splits on.

**What the literature establishes:** this choice is not a numerical detail. It is
the axis on which Xia 2011 and Shu 2011 disagree by up to an order of magnitude,
and the correction went **toward** the filled/sealed treatment.

**What I am NOT claiming, and D4 should not read in:** I am not saying our
canonical configuration is wrong, nor that `solidify_columns` is the right choice.
Two reasons to be careful. First, bulk density is not the quantity the thresholds
turn on: flotation depends on submerged volume as a function of depth and on
underbody shape, so a single `rho` does not settle it. Second, the hull is
documented at `vehicle_geometry_research/WATERTIGHT_HULL_TOOL_FINDINGS.md:162` as
"underbody and wheel wells **kept open**" by deliberate design, so the low enclosed
volume is a choice someone made, not an accident I have caught.

**The actionable item is narrow:** the sealing treatment is a first-order
literature variable, our pipeline picks it on one line, and no gate or document
records *why* that line reads as it does. That is worth a sentence in the paper's
limitations regardless of which way it is decided.

## 3. FLAG-4 CLOSED: the `martinezgomariz2018` referent

FLAG-4 has been open since unit 7: `paper/can_it_ford_references_IEEE.bib` carries
`martinezgomariz2018` with **no title, no DOI and no journal**, so its referent was
unresolvable and I refused to guess it.

The corpus document names it, and I verified the citation independently rather than
taking the document's word:

```
verifyCitation -> DOI 10.1111/jfr3.12262    score 1, exact title match
  "Stability criteria for flooded vehicles: a state-of-the-art review"
  Martinez-Gomariz E., Gomez M., Russo B., Djordjevic S.
  Journal of Flood Risk Management
  Crossref issued year: 2016        <- NOT 2018
```

**The bib key's year is the trap, and it is the same trap for the fourth time in
this dispatch.** Crossref's `issued` is **2016**, the online-first date; the print
issue is **11(S2):S817-S826, 2018**. The verifier returned `mismatch / low
confidence` on the year alone, with the title matching at score 1.

**Independent confirmation from a second artifact, and it is decisive.** The Elicit
CSV holds *both* versions as separate rows, which is the duplicate unit 12 found
and could not then explain:

```
row  6   year 2016   DOI (none)              "Stability criteria for flooded vehicles : A state-ofthe-art review"
row 16   year 2018   DOI 10.1111/jfr3.12262  "Stability criteria for flooded vehicles: a state-of-the-art review"
```

Same paper, two rows, two years, and only the 2018 row carries the DOI. **So unit
12's unexplained duplicate and unit 7's unresolvable bib entry are the same
object**, and both close together.

**Residual ambiguity, stated rather than hidden.** There are two plausible
`martinezgomariz2018` referents, because a *different* Martinez-Gomariz
first-author paper is also live in this project:

| candidate | DOI | year | why it might be the referent |
|---|---|---|---|
| **state-of-the-art review** | `10.1111/jfr3.12262` | 2016 online / **2018 print** | **year matches the bib key exactly** |
| new experiments-based methodology | `10.1080/1573062X.2017.1301501` | 2017 | it is the one another session's handoff asks to be read |

**I recommend the review (`jfr3.12262`)** because the key says 2018 and the review's
print year is 2018, while the methodology paper is 2017 on every record. But
whoever owns the bibliography should confirm against the citation context, because
a key's year is weak evidence and I have now watched a year mislead four times in
this dispatch.

## 4. Status

I did not edit the bibliography or any file outside `docs/R5_RESEARCH_*`.

UNVERIFIED:
1. **I have read none of the twelve primary studies.** Section 1 is a transcription
   of one corpus document's table. The "order of magnitude" and the Xia/Shu
   correction are that document's characterisations, not my reading of Xia or Shu.
2. The corpus search reached **308 of 387** files in the main root, so a
   contradicting document may exist in the 79 I cannot open.
3. Whether `solidify_columns` or `solidify_watertight` is correct for our scene is
   a physics decision for D4. I supply the literature context only.
4. The mapping from a flume model's "foam-filled watertight" to an MPM particle
   fill is an analogy, not an equivalence. Nobody has shown the two produce the
   same displaced volume as a function of depth.
5. The 11(S2):S817-S826 pagination comes from the corpus document, not from
   Crossref, which returned no page range in the record I read.
