# R5-D1 unit 43: I audited my own quotations, and found a third truncation

Date 2026-08-17. Branch `claude/r5-research`. **Section 2 is for D2, and it changes
what clears E8.**

Unit 42 recorded that I had truncated a source quotation one clause short twice
(unit 36's register B5, unit 40's Xia causal clause). **My own unit-13 lesson says
finding one instance is no reason to assume it is the only one.** I applied it to
grep zeros in unit 37 and had not applied it to my quotations. This is that audit.

---

## 1. Method and result

Every contiguous `>` block in all 32 of my documents was joined into a passage, its
last 46 characters taken as a distinctive tail, and that tail searched across an
in-memory index of the repo and the corpus (`.md .py .bib .tex .txt .tsv`, under
2 MB, `.git`/`.claude` excluded). Where the tail was found, I checked **what the
source says next**. If the next non-space character is not sentence-ending
punctuation, the quotation stopped mid-sentence.

```
block-quote passages in my 32 docs : 82
testable (>=45 chars, no ellipsis) : 81
  located in a local source        : 41
  not locatable locally            : 40    <- external papers or paraphrase
  ending mid-sentence              : 18
    citation marker or list        : 17    benign
    NEEDING JUDGEMENT              :  1
```

**Seventeen of the eighteen are benign.** They stop before a bracketed citation
marker (`\[2, 3, 17\]`), a parenthetical, or the next item in a list. Stopping a
quote before a citation number is normal practice and changes no meaning.

**One is not benign, and it is the worst-placed of the three I have now made.**

**The audit's own limit, stated plainly: 40 of 81 passages could not be located
locally**, because they quote external papers or because I paraphrased rather than
quoted. **So this covers half my quotations, not all of them.** A truncation in an
external-paper quote would not be caught by this method, and unit 40's error was in
a corpus document that *was* locatable, so the method does work where it reaches.

## 2. FOR D2: the E8 operative rule has TWO routes, and I published one

`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`, verbatim and complete:

> "Operative rule, unchanged and still conservative: do not commit any derived
> NCAC/CCSA geometry to the public repo, and do not include it in a DesignSafe DOI,
> **without written permission or a confirmed licence**."

What `R5_RESEARCH_GNN_AND_MESH_LICENCE_2026-08-17.md:22` said until today:

> "...and do not include it in a DesignSafe DOI, without written permission."

**I dropped "or a confirmed licence" and closed the sentence with a full stop**, so
it reads as complete. `or a confirmed licence` appeared in **zero** of my 32
documents.

**Why this is operational rather than cosmetic.** Under my version, the only path
that clears E8 is obtaining written permission from CCSA/GMU: a slow, human,
possibly unanswerable request. Under the register's actual rule, **a confirmed
licence clears it equally.** Those are different lines of enquiry with different
costs, and D2 is working E8 now.

**It also connects to a finding of mine that points the other way.** Unit 37
established that all four shipped NCAC/CCSA packages carry an acknowledgement
request and a liability disclaimer but **no licence word at all**, and unit 31
established the DataCite record has an **empty `rightsList`**. So the
confirmed-licence route currently has no evidence supporting it either. **That does
not make my truncation harmless**: it means D2 should know both routes exist and
that one of them currently has a documented absence of evidence, rather than being
told only one route exists. The conclusion may end up the same; the reasoning
available to reach it should not have been narrowed by me.

Corrected in place at `GNN_AND_MESH_LICENCE:20-23` with a correction block, per the
in-place-marking rule from unit 23.

## 3. The pattern, named

| # | unit | what I cut | what the cut clause said |
|---|---|---|---|
| 1 | 36 | register **B5**'s second sentence | that realized density is grid-coupled by construction, which **agreed with me** and made my escalation unnecessary |
| 2 | 40 | the Xia sentence's causal clause | "**because model density/mass was not correctly scaled**", naming a different cause than the one I claimed |
| 3 | 43 | E8's alternative route | "**or a confirmed licence**", a second way to clear a blocker |

The common shape is not carelessness about length. **In all three I stopped at the
point where the sentence stopped being simple**, and in two of three the omitted
clause worked against the claim I was making. That is a bias with a direction, not
random error.

**The cheap mechanical guard**, which I now have and will keep using: take the
quote's tail, find it in the source, print the next 90 characters. It runs in under
a minute over all 32 documents.

## 4. The opposite error: tested, and a clean negative

Item 3 of my first status list said I had not tested whether any quotation *begins*
mid-sentence, dropping a qualifying subject, condition or negation. **That gap is
now closed.** Same index, leading context instead of trailing:

```
testable passages          : 81
located in a local source  : 43
BEGIN mid-sentence         : 15
  dropping a condition or negation : 0
```

**I did not stop at the mechanical zero.** My own unit-37 lesson is that a keyword
zero is not the same as having looked, and unit 36's failure was a false zero, so I
read all fifteen. The result holds:

- **Thirteen of fifteen begin immediately after a markdown header, a bullet, or a
  semicolon in an enumerated list.** The mechanical test fires because the preceding
  character is not sentence-ending punctuation, but those are **structural**
  boundaries, not sentential ones. Quoting a list item from its start is correct.
- **One is my own quotation of the E8 rule in this document**, deliberately split
  across lines in section 2 to show the truncation. Self-referential.
- **One is mildly lossy and not material:** in
  `KRAMER_CONFIRMED_MODE_DEPENDENT:20` I begin at "experimental investigations on
  the stability of..." where the source reads "In order to determine those criteria,
  experimental investigations...". I dropped a **purpose clause**, which carries no
  condition and reverses nothing.

**So the bias runs one way.** I truncate at the end, where a sentence gets
complicated; I do not truncate at the start. That is consistent with the mechanism
proposed in section 3: the error is stopping when the text stops being convenient,
not carelessness about quotation boundaries in general.

## 5. Status

UNVERIFIED:
1. **Half my quotations are unaudited.** 40 of 81 were not locatable in a local
   source. External-paper quotes are unchecked by this method, and both tests share
   that limit.
2. The benign/material split is my classification, applied by inspecting all 18
   trailing and all 15 leading cases by eye. Someone else might rule differently on
   the borderline ones; I have named every case I set aside and why.
3. Whether the confirmed-licence route is actually available for the NCAC/CCSA
   meshes is **D2's question**, not mine. I establish only that the register offers
   it and that I had hidden it.
4. Neither test catches a quotation that is accurate at both ends but **omits an
   interior clause** with an ellipsis. Several of my quotes do that legitimately;
   verifying them would require reading each source passage in full.

---

## 7. Unit 53: em-dash compliance, and a broken test that printed a clean pass

D2 found four em-dashes in its own entry-point document, against the standing global
rule ("No em-dashes, anywhere, in any response, in any file written"). I had never
run that check on my own files.

**Result, across all 43 of my files (37 documents plus the data TSVs):**

```
em-dash U+2014 : 0      CLEAN, the rule holds
en-dash U+2013 : 13     all in data TSVs, all verbatim source data
detector sanity check on a known em-dash string: 1   (proves the test fires)
```

**The 13 en-dashes stay, and changing them would be an error.** They are:
paper titles (`Vehicle-Water Interaction`, `fluid-structure interaction problems`,
`Fluid-Rigid Coupling`), year ranges from reference records (`2001-2017`,
`1950-2004`), and **six occurrences inside a real filename on disk**. Editing a
title corrupts a citation; editing the filename breaks the path. The standing rule
governs prose I write, not metadata I transcribe.

### 7a. The near-miss, which is the part worth keeping

**My first attempt printed `TOTAL em-dash lines: 0` and was completely broken.**
`/usr/bin/grep -c` exits **1** when the count is zero, so my `|| echo 0` fallback
appended a second zero, every `[ "$n" -gt 0 ]` comparison failed with
`integer expression expected: 0\n0`, and **no file could ever have been reported**.
The totals were structurally incapable of being non-zero.

It looked exactly like a clean pass.

**This is the third false-zero-shaped event in this dispatch**: unit 36's was real
and cost five retracted claims, unit 43's grep-vs-source check needed a control to
trust, and this one was caught only because the error text scrolled past above the
reassuring total. The rule I keep re-learning: **a zero is worth nothing without a
positive control proving the detector fires.** The re-run includes one, which is why
its zero is reportable and the first one is not.
