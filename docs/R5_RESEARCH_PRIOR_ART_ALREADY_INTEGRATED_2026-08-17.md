# R5-D1 unit 27: I found the prior-art assessment, and the register had already digested it

Date 2026-08-17. Branch `claude/r5-research`.

**Lead finding: this was not a new find, and I nearly reported it as one.**

Mining the corpus directory I had never opened,
`05_Abstraction_Ladder_Framing_and_Positioning`, surfaced a document that is
precisely my dispatch's deliverable (b) done properly: "Reconstruction-to-Decision
Pipelines: Prior-Art Assessment". The register already carries its conclusions as
**G12 and G13**, and register **K0 explicitly warns** that this class of report
was already integrated and that the register should be checked "before treating
any report finding as new". I read the document first and the register second.

Three things survive that check, and they are worth the unit.

---

## 1. What the register already has, so nobody re-derives it

`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`, verbatim:

> **G12. The pipeline shape is also prior art**, as the digital twin decision
> pipeline (NASEM 2024, doi:10.17226/26894). Full four-criteria exemplars: Cadia
> tailings dam (doi:10.1680/jgeot.21.00399), rockfall runout back-analysis. It has
> not been transferred to vehicle flood traversability with external empirical
> validation. **That fourth criterion is the differentiator.**

> **G13. `arXiv 2607.00673`** ... satisfies reconstruction, simulation and decision
> but explicitly NOT external empirical validation.

That is the assessment's core conclusion, already canonical. The source document
adds detail the register compresses (the rockfall and tunnel-collapse exemplars,
the terminology survey, the exclusion of PhysGaussian-class work as content
generation) but nothing that changes G12 or G13.

## 2. A reconciliation with my own unit 7, and it goes in my favour

Unit 7 concluded that "every novelty axis I proposed is occupied", on the
strength of He 2026 validating a coupled vehicle-water model against physical
experiment. Set against G12, **I conflated two different validations**:

| | what is validated | against what |
|---|---|---|
| He 2026, Azhar 2023 | a **solver** | physical experiments (flume loads, pool trials, a physical model study) |
| G12 criterion 4 | a **reconstruction-to-decision pipeline's verdict** | independent published criteria (AR&R, Smith-Modra-Felder, or a physical crossing test) |

Those are different claims. A solver validated against a flume does not close
criterion 4 for a pipeline that starts at sensor reconstruction and ends at a
go/no-go. **So G12's differentiator survives He 2026**, and unit 7 was too
pessimistic on that specific point.

Unit 7's substantive findings stand unchanged: Al-Qadami 2023 does occupy full
scale and stability thresholds, Azhar 2023 does occupy the particle-method axis,
and the paper does not cite either. What I withdraw is the implication that the
validation axis is occupied **in the sense G12 means**. It is not.

This also fits unit 16 section 2 from the other direction: the reconstruction
literature has "little vehicle-specific end-to-end work linking reconstruction,
collision-proxy repair, and validated inertial properties". Same gap, reached by
a different route.

## 3. Two things that are genuinely NOT in the canonical files

Both appear only in `_inbox/CAN_IT_FORD_PROJECT_INSTRUCTIONS_v8.md`, which is not
on CLAUDE.md's canonical-file list, and in a `.remember` note.

**(a) US Army FM 90-13 and TM 9-238. Zero hits in the register and zero in
CLAUDE.md**, checked live. The assessment quotes FM 90-13, River-Crossing
Operations, Appendix C:

> Fording is possible for current velocities that are **less than 1.5 MPS**.
> Riverbeds at fording sites must be firm and free of large rocks and other
> obstructions. Vehicle-operator manuals contain specific depth capabilities and
> required adaptations.

**Why this matters and is not a duplicate of anything we hold.** CLAUDE.md L-2
records that the AR&R 3.0 m/s cap is administrative and human-derived, which I
verified at the AR&R primary source in unit 3. FM 90-13's **1.5 m/s** is a
different number from a different basis: an operational fording limit for
vehicles, at half the AR&R cap. If the project wants a vehicle-derived velocity
criterion, and L-2 establishes that AR&R's is not one, this is the closest
candidate found in this dispatch. It is exactly the sort of independent published
criterion G12's criterion 4 calls for.

I am **not** proposing it be adopted. It is a field manual, its basis is
unstated in the quoted passage, and I have not seen the manual. I am proposing it
be recorded, because at present it lives only in a non-canonical inbox file.

**(b) NG-NRMM. Zero hits anywhere in the repo**, checked live. The NATO
Next-Generation NATO Reference Mobility Model and AMSP-06, with Project Chrono
terramechanics plus SPH, is named in the assessment as the closest defence-side
partial match: mobility go/no-go maps, empirically benchmarked, with **water
fording a known gap**. Given CLAUDE.md L-8's engine decision and the Chrono work
already in this project, that this framework appears nowhere is a genuine
omission.

## 4. The process lesson, which is mine

Register K0 says, verbatim: "several reports turned out to be already integrated
(G11, G12, G13, G1, G2, G6, G7, G8), so **check this register before treating any
report finding as new**."

I did the opposite: read the artifact, drafted the excitement, then checked. The
check took two minutes and moved this from "major discovery" to "already
canonical, plus two gaps". Both orders find the same truth; only one of them
risks a wrong claim reaching the board. This is the same shape as unit 25, where
I propagated a figure before re-deriving it.

## 5. Status

UNVERIFIED:
1. **I have not read FM 90-13 or TM 9-238.** The 1.5 m/s quotation is from the
   assessment document, which is itself a secondary source. Before that number is
   used anywhere, someone should open the manual.
2. The assessment's own caveats apply and are worth carrying: its confidence is
   "no evidence found despite a thorough search, not confirmed absence", several
   key sources were read via abstracts, and it flags distribution-restricted
   DTIC/NATO reports as the main residual risk to any absolute novelty claim.
3. I read one of the 17 files in that directory in full. Four of the 17 are broken
   symlinks pointing at a `/sessions/.../mnt/` path that does not exist here, but
   all four are `" 2"` duplicates of files that do resolve, so no unique content
   is lost.
4. 245 non-catalog research documents remain unread across the corpus.
