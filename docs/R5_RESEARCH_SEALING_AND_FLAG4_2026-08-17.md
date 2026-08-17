# R5-D1 unit 40: the literature's sealing split, and FLAG-4 closed

Date 2026-08-17. Branch `claude/r5-research`.

> ## CORRECTED 2026-08-17 after physics-skeptic returned NINE BLOCKING issues
>
> **The headline claim of the first version was false, and it was false because I
> cut a quotation one clause short.** I wrote that vehicle sealing is "the recorded
> cause of the largest disagreement in the incipient-motion literature". The source
> sentence continues past where I stopped it and names a **different cause**.
> Section 2's framing was also structurally wrong: the fill is not a choice anyone
> makes. Both are corrected below; the original assertions are listed in section 5.
>
> **This is the second time in this dispatch I have truncated a quote at exactly
> the point where the next clause would refute me** (unit 36 was register B5's
> second sentence). Naming it as a pattern, not an incident.

---

## 0. Search scope

`corpus_inventory` reports the primary corpus root as
**PARTIAL/TCC-DENIED: 387 files, 308 readable**. The reviewer could not reproduce
387 by any filesystem probe (three attempts gave 131, 503 and 652, the 131 showing
the known TCC silent-zero mode), so **treat 387/308 as the connector's own
accounting, of undefined denominator, not as a filesystem fact.** The qualitative
point stands and is the one that matters: **part of the corpus is unreadable, so no
absence claim from it is complete.**

Source, previously unread:
`04_Validation_Literature_and_Citations/Experimental Configuration of the
Flood-Vehicle Stability Literature- What Was Physically Done.md`. It is a symlink
to a TCC-blocked `~/Downloads` path and has a byte-identical duplicate in the
corpus root (`md5 9ea16a6e67f4aa56d6e29a5e8e014711`).

## 1. The finding: the literature does not agree on vehicle sealing

**Abridged from the source's "Vehicle condition" column** (not verbatim: I have
dropped trailing clauses, and the source uses ONE row for Xia and Shu jointly,
which I split into two):

| Study | Vehicle condition | physical? |
|---|---|---|
| Bonham & Hattersley 1967 | Rigid model; results scaled to 7 car categories | yes |
| Gordon & Stone 1973 | Rigid model, front-wheel-drive weight distribution | yes |
| Keller & Mitsch 1993 [**YEAR DISPUTED: OpenAlex gives 1992 on an exact title match, unit 57**] | Sealed **assumption**; not validated | **NO, desk study** |
| Teo 2010 / 2012 | Die-cast; some scaled fully submerged | yes |
| **Xia et al. 2011** | **Water-filled models** (submerge before moving) | yes |
| **Shu et al. 2011** | **Foam-filled watertight** | yes |
| Toda et al. 2013 | **Deliberately allowed water ingress** (contrast Shu/Martinez-Gomariz) | yes |
| Xia et al. 2014 | Sealed models | yes |
| Arrighi et al. 2015 | Rigid CFD body, not free to move | **NO, CFD** |
| Kramer et al. 2016 | **Watertight models; prototype suffered water ingress** (noted by Smith) | yes |
| Martinez-Gomariz et al. 2017 | Foam-filled watertight (no ingress); model density set equal to prototype | yes |
| Smith, Modra & Felder 2019 | Rapidly filled to limit ingress (<50 L); sealed with silicone plus pump | yes |
| Shah et al. 2018/2020 | Scaled model, Froude similarity | yes |

**The treatments genuinely differ, and that much survives review.** But three
qualifications the first version omitted:

1. **Two of the "sealed" entries are not experiments.** Keller & Mitsch 1993 is a
   desk study and Arrighi 2015 is CFD. The source says so explicitly. An *assumed*
   seal in an analytical force balance is not a treatment applied to a test vehicle.
2. **Kramer 2016 belongs to both buckets** (watertight models, prototype with
   ingress). My first version's "roughly even" split silently assigned it to
   ingress. Put it in sealed and the ratio is 3:1, not roughly even. **I withdraw
   the split counts entirely**; they did not close over my own table (I listed 13
   rows and binned 12) and the binning was unreconstructable.
3. **My table is abridged, not verbatim**, as the header now says.

### 1a. THE CORRECTION THAT MATTERS: sealing is NOT the recorded cause

My first version quoted the source as far as "inconsistent with field footage" and
concluded sealing caused the discrepancy. **Read to the end of the sentence:**

> "Xia et al. (2011) did NOT correctly scale vehicle density/mass (they used a
> relative-density adjustment), producing results up to an order of magnitude off
> with vehicles submerging before moving, inconsistent with field footage;
> **Shu et al. (2011) corrected the scaling and obtained higher D×V values than
> older work, attributed to higher model friction (mu 0.39-0.68 vs 0.3).**"

So the source attributes:

| | to |
|---|---|
| the order-of-magnitude discrepancy | **incorrect density/mass scaling** |
| Shu's higher D×V values | **higher model friction**, 0.39-0.68 vs 0.3 |
| foam-filling | one of **two** components of Shu's fix, alongside density scaling |

**Sealing is named nowhere as the cause.** And "largest disagreement" was my own
superlative: the word "largest" does not appear in the source, whose own heading is
"Numerical-vs-physical disagreement".

**What survives:** the twelve studies genuinely do differ in sealing treatment, and
that variation is real and undocumented in our own write-ups. **What does not:** any
claim that this variation is the demonstrated driver of a headline disagreement.

Two source items that do survive intact:

- **Sealing has a scale effect.** Kramer 2016's prototype "floated deeper than the
  model", which the source attributes to sealing: model-scale watertight vehicles
  float too shallow.
- **Two direct buoyancy methods exist** in the whole table: Martinez-Gomariz's glass
  box (38.9 x 18.9 cm, filled until no wheel touched ground) and
  Smith/Modra/Felder's traction-reduction rig. Every other entry infers buoyancy.

## 2. WITHDRAWN AND REPLACED: what `vehicle.py:175` actually does

**Engine: WARPMPM** (`renders/yaris_render_s1/sim_standing.py:12` imports
`solidify_watertight` from `warpmpm.vehicle`). Genesis never loads a hull.
File cited: `/Users/josie/Downloads/mpm-engine-main/src/warpmpm/vehicle.py`, which
is byte-equivalent to `renders/yaris_render_s1/vehicle_live.py` at the same line.

My first version said our pipeline "picks it on one line" and that "no gate or
document records why that line reads as it does". **Both are wrong, and the second
is wrong three times over.**

**(a) It is not a choice. It is automatic dispatch on a mesh property:**

```python
# vehicle.py:175
if self.mesh is not None and bool(self.mesh.is_watertight):
    self.particles = solidify_watertight(self.mesh, h)
else:
    self.particles = solidify_columns(...)
```

`WATERTIGHT_HULL_TOOL_FINDINGS.md:159` records the canonical hull as watertight
**True**. **So `solidify_columns` is unreachable for our hull.** It is the documented
fallback "for holey splat shells" (`vehicle.py:95`), not an alternative treatment
of the same mesh.

**(b) The reason IS recorded, two lines above the line I cited.** `vehicle.py:93-94`:

> "Unlike solidify_columns this leaves genuine voids (ground clearance, wheel wells)
> empty, so the realized particle volume matches the hull volume and **buoyancy is
> unbiased**."

That is an explicit, buoyancy-based justification. My "nothing records why" was
false against a docstring in the same function I was quoting.

**(c) A guard would abort the run.** `sim_standing.py:381-383` raises `SystemExit`
if `fill_ratio` leaves `[0.5, 2.0]`. The column fill gives
`7.670671 / 3.542739 = 2.16518`, which is **outside the band**. So the alternative
would not silently change physics; it would stop the driver before the solver is
built. (In fairness to the code: `:379` says this tripwire is explicitly **not** a
physics gate.)

**What remains true and is worth one sentence in the limitations:** the sealing
treatment is a real axis of variation in the experimental literature, our hull is
deliberately built with underbody and wheel wells **open**
(`WATERTIGHT_HULL_TOOL_FINDINGS.md:162-163`), and no gate tests that choice against
any external measurement. That is a limitation, not a defect, and **it is not the
2.165x knob I described.**

**Physics note I got backwards.** I hedged that "bulk density is not the quantity
the thresholds turn on". That is true in general (onset depth is set by the
submerged-volume curve `rho_w . V_sub(h) . g = M . g`), but in this pipeline mass is
fixed and volume is derived at `sim_standing.py:170-171`, so a volume change *is* a
change in the governing quantity. The hedge argued against my own case. The correct
reason our configuration is defensible is (b): the watertight branch is the one that
makes realized volume match hull volume.

## 3. FLAG-4: the `martinezgomariz2018` referent

The DOI is confirmed. `verifyCitation` returns **`10.1111/jfr3.12262`**, title match
score 1, "Stability criteria for flooded vehicles: a state-of-the-art review",
Martinez-Gomariz, Gomez, Russo, Djordjevic. Crossref `issued` **2016-08-03**,
`published-print` **2018-02**, volume 11, issue S2.

**Correction: the bib entry is not contentless, and I should have reported that.**
`paper/can_it_ford_references_IEEE.bib:141-146` carries a `note`:

> `note = {Cited for: passenger vehicles fail via floating/sliding, not toppling. VERIFY full citation.}`

That note is a stronger constraint than the key's year, and **it does not obviously
favour the review**: the rival 2017 paper (`10.1080/1573062X.2017.1301501`) is the
experimental campaign over twelve car models that would physically observe floating
and sliding modes. `alqadami2022` at `:148-153` carries the **identical** note, so
the two form a citation pair for one claim.

**Correction: my "independent, decisive" confirmation was neither.** The Elicit
CSV's 2018 stamp derives from the same publisher metadata Crossref serves, so it is
one source cited twice, which this project's claim-discipline rule forbids counting
as corroboration. And the same CSV contains the **rival at row 31**, which I did not
disclose while attributing the 2017 candidate only to another session's handoff.

**Honest status: the DOI of the review is certain; the referent of the bib key is
NOT settled.** Both candidates are live, the note field fits either, and the year
match is weak evidence. Whoever owns the bibliography should decide from the citing
sentence. Note also that `martinezgomariz2018` is `\cite`d in **no `.tex` in this
checkout** (20 files checked), though the Overleaf head was not checked and project
memory records it as canonical.

## 4. Status

UNVERIFIED:
1. **I have read none of the twelve primary studies.** Section 1 is one corpus
   document's table.
2. **That source has a known-suspect claim.** Its line 11 says Al-Qadami 2021 tested
   a "Toyota Yaris"; standing check 11 records a **Perodua Viva**. Unresolved from
   open metadata, and section 1 rests on this document alone.
3. The `n=8890` particle count for `solidify_watertight` is **inherited, not mine**,
   and disagrees with register E3's **8,905** by -0.168%; the reviewer who produced
   it could not close that gap. Independent partial corroboration:
   `WATERTIGHT_HULL_TOOL_FINDINGS.md:159` gives 3.5427 m3 and 310.5 kg/m3.
4. The pagination **11(S2):S817-S826** comes from the corpus document only. Crossref,
   OpenAlex and doi.org content negotiation all return **no page data**, for this
   article and for every article in that issue. Do not upgrade it.
5. The corpus file counts (387/308) are the connector's, of undefined denominator,
   and did not reproduce against the filesystem.

## 5. Withdrawn from the first version

**W1.** "Sealing is the recorded cause of the largest disagreement in the
incipient-motion literature." **WITHDRAWN.** The source names density/mass scaling;
"largest" was mine and appears nowhere in it.
**W2.** "Transcribed verbatim across all twelve studies." **WITHDRAWN**: abridged,
condition column only, and I split the source's joint Xia/Shu row into two.
**W3.** The 5/3/3/1 split. **WITHDRAWN**: it binned 12 items over a 13-row table and
put Kramer, which the source records as both, into one bucket.
**W4.** "Our pipeline picks it on one line" and "no gate or document records why."
**WITHDRAWN**: automatic dispatch on `is_watertight`, `solidify_columns` unreachable
for a watertight hull, the reason recorded at `vehicle.py:93-94`, and a preflight
guard that would abort at fill_ratio 2.16518.
**W5.** "Independent confirmation ... and it is decisive" for FLAG-4. **DOWNGRADED
to consistent**: same-origin metadata, and the rival sits in the same CSV.
