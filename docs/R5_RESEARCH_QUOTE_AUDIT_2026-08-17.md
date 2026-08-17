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

## 4. Status

UNVERIFIED:
1. **Half my quotations are unaudited.** 40 of 81 were not locatable in a local
   source. External-paper quotes are unchecked by this method.
2. The benign/needing-judgement split is my classification, applied by inspecting
   the 18 continuations. Someone else might rule differently on borderline cases;
   the 17 I called benign all continue into a citation marker, a parenthetical or a
   list item.
3. I did not check for the **opposite** error, a quotation that begins mid-sentence
   and so drops a qualifying subject or condition. That would need a different test.
4. Whether the confirmed-licence route is actually available for the NCAC/CCSA
   meshes is **D2's question**, not mine. I establish only that the register offers
   it and that I had hidden it.
