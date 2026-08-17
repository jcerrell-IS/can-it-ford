# R5-D1 unit 37: the NCAC README is in our repo, and it closes a gap the audit could not

Date 2026-08-17. Branch `claude/r5-research`. **For D2, E8 scope.**

Two results. My zero-hit audit after unit 36 found my earlier claims hold, and I
nearly retracted correct ones by re-measuring the wrong scope. And chasing the one
surprise in that audit closed a stated gap in the GNN/mesh-licence assessment.

---

## 1. The zero-hit audit: my earlier claims hold, and I nearly broke them

Unit 36's defect was a grep that returned a false zero. Unit 13's lesson says one
instance is no reason to assume it is the only one, so I re-checked every
load-bearing zero I had published, with no `--exclude-dir=.claude` and no timeout:

```
unit 27  NG-NRMM             claimed zero repo-wide    actual 0    HOLDS
unit 31  "unmounted rigid"   claimed zero register     actual 0    HOLDS
unit 31  FAR 52.227          claimed zero register     actual 0    HOLDS
unit 31  Marzougui           claimed zero register     actual 0    HOLDS
unit 31  2011-T-001          claimed zero register     actual 0    HOLDS
unit 2   nme.2360            claimed zero outside .claude  actual 0  HOLDS
unit 2   CMES.2008.031.107   claimed zero outside .claude  actual 0  HOLDS
```

**All hold.** But my first pass flagged Marzougui and 2011-T-001 as "WRONG",
because I ran a **repo-wide** check against claims I had made about the
**register**. I caught it before retracting. Over-correction is its own failure
mode, and after unit 36 the temptation to assume every prior claim is broken is
exactly the wrong reflex.

## 2. The surprise: NCAC/CCSA model READMEs are committed to our public repo

Marzougui returns 30 repo-wide hits, all in shipped model documentation, e.g.
`vehicle_geometry_research/2010-toyota-yaris-coarse-v1l/2010-toyota-yaris-coarse-v1l/README.md`.

**That file is TRACKED**, verified with `git ls-files --error-unmatch`. So
CCSA-authored documentation for the canonical Yaris model is already committed to
the public repo, alongside the derived hull that project memory records as already
on origin.

## 3. It closes a gap the GNN/mesh audit explicitly could not close

That audit's own caveat, quoted in unit 31:

> I could not open the interior of the model `.zip` packages, so **I cannot rule
> out an embedded README/notice inside the Yaris archive**; the "no license"
> finding rests on the model web pages, the validation PDF, and the DataCite
> metadata.

The README is extracted and in our tree, so I read it. **The audit's "no explicit
license" conclusion survives its own stated gap.** There is no licence, no
copyright line, no redistribution grant and no terms-of-use statement anywhere in
its 78 lines.

**But reading it found two governance statements my grep had missed**, because
neither uses licence vocabulary. Verbatim:

> Users of the model must verify their own simulations. **Neither CCSA or FHWA
> assume any responsibility** for the validity, accuracy, or applicability of
> results obtained from this model.

> **We ask that the CCSA at GMU and the FHWA be acknowledged for any use of this
> FE model resulting in papers and publications.**

My keyword pattern covered `licen[cs]e|copyright|terms of use|distribut|
redistribut|permission|public domain|may be copied|release` and matched only
"released December 2016". It could not match a liability disclaimer or an
acknowledgement request phrased as "We ask that". **Unit 36's lesson repeating in
miniature: a keyword zero is not the same as having looked.** I only found these
because I read the file after the grep came back empty.

## 4. What this gives D2 for E8

1. **An acknowledgement obligation that exists regardless of the redistribution
   question.** "We ask that the CCSA at GMU and the FHWA be acknowledged for any
   use of this FE model resulting in papers and publications." Our paper uses a
   hull derived from this model. That is a request rather than a licence
   condition, matching the historic NCAC Model Release Statement's
   "just short of requiring" framing, but it is concrete, it is in our own tree,
   and satisfying it costs one sentence.
2. **FHWA sponsorship confirmed in the shipped file**: "The effort was sponsored
   by the Federal Highway Administration", developed by CCSA researchers at George
   Mason University. That is the contractor-works premise the FAR 52.227-14
   analysis turns on, now attested in the repo rather than only on a web page.
3. **The contact route the audit recommended is already in our repo**, with direct
   emails: Dhafer Marzougui, Fadi Tahan and Steve Kan at gmu.edu. Unit 31 reported
   Kan and Marzougui as zero-hit in the register, which holds, but they are in the
   tree.
4. **Provenance detail worth citing**: the model is based on **VIN
   JTDBT4K37A4067025**, 378,376 elements, version 1l released December 2016, and
   the README points at `doi:10.13021/G8JS5D` as the validation reference, which
   is the presentation DOI unit 31 examined.

## 4a. Checked: the acknowledgement is half satisfied, and the fix is one word

I listed "whether the paper acknowledges CCSA and FHWA" as unverified, then
checked it.

**CCSA/GMU: yes.** `paper/conference_101719.tex:174`: "The vehicle is a single
watertight triangle mesh derived from the **CCSA/GMU** coarse 2010 Toyota Yaris
crash-test finite-element deck `\cite{ccsa2010yaris}`, a 378,376-element ...".
Named in the Methods text and cited.

**FHWA: no.** `FHWA` and `Federal Highway` return **zero** hits across
`paper/*.tex`, `overleaf_sync/*.tex` and `paper/canonical_2026-08-02/*.tex`.

The README asks for "the CCSA at GMU **and the FHWA**" to be acknowledged. So the
request is half met, and closing it is a one-word edit to a sentence that already
exists. **That is the smallest actionable item this dispatch has produced, and it
is the only one that is an obligation rather than a suggestion**, weak as the
"we ask" framing is.

**A positive worth recording while I am in that file.** Line 176 reads: "The three
AR&R stability classes are realized as *mass overrides applied to that same hull*,
not as three distinct vehicle geometries." **The paper already states the E3
caveat correctly**, in its own text, unprompted. Unit 15 raised the one-hull
mass-sweep concern from the coupling catalog; the paper had it right already. I
should say so as plainly as I say the defects.

## 5. Status

I did not edit anything outside my scope, and I am not resolving E8.

UNVERIFIED:
1. **I read one README**, the canonical coarse v1l. The repo also ships Yaris
   detailed v2j and two Silverado packages; I have not read those and they may
   carry different text.
2. Whether an acknowledgement request covering "this FE model" extends to a
   derived watertight hull is a judgement, not a fact in the file.
3. Whether these README files being tracked changes E8's exposure analysis is
   D2's call. I established that they are tracked and what they say.
4. I read one README of four shipped packages, so the Silverado and detailed-Yaris packages may carry different text. (The paper-acknowledgement question from this slot is now answered in section 4a.)
