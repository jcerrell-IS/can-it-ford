# R5-D1 unit 11: the Nihei corrigendum after ten routes, and an author-name trap

Date 2026-08-17 (work continues from the 2026-08-16 session). Branch
`claude/r5-research`.

Two results. The corrigendum stays blocked after two further routes, and a
hypothesis I formed about it was tested and refuted. Along the way I found a
citation defect in the highest-value paper this dispatch identified.

---

## 1. Two more routes tried, both fail. Total is now ten.

Previously tried and recorded in unit 4: `doi.org`, ScienceDirect direct,
`linkinghub`, DOAJ, Unpaywall, OpenAlex, Semantic Scholar, Europe PMC. Eight.

**Route 9, the scite connector.** scite holds the record and independently
confirms the relationship: `editorialNotices: [{status: "has erratum", noticeDoi:
"10.1016/j.rineng.2025.107527", date: "2025-12-1"}]` on the original. But it
returns **no abstract and no `fulltextExcerpts`**, and a targeted full-text query
for the corrected values scored `relevancyScore: 0.0` on both records. scite has
the metadata, not the text.

**Route 10, scite's licensed access link.** scite supplies a signed
`ct.prod.getft.io` access URL. It 302-redirects to
`sciencedirect.com/science/article/pii/S2590123025035820?pes=vor&utm_source=scite`,
which is the same host and the same path that already returned 403, now with
tracking parameters. Same wall.

**Status: still OPEN, and still not blocked on effort.** The Elsevier landing
page carries `tdm-reservation: 1`, a machine-readable opt-out from automated
retrieval. Ten routes is enough to establish that no licensed intermediary
exposes the text. The remaining route is a human opening
`https://doi.org/10.1016/j.rineng.2025.107527` in a browser. It is CC-BY once
open. **Until then, treat 0.0250 and 0.0242 as provisional.**

## 2. A hypothesis about the corrigendum, tested and refuted

Corrigenda on multi-author papers are frequently author-name or affiliation
fixes. Given that I had just found the aggregators disagreeing with the publisher
on one author's given name (section 3), the obvious hypothesis was: **the
corrigendum corrects an author name, and therefore touches no numeric value.**
That would have been convenient, because it would have made the friction figures
safe to use.

**The test:** compare the author lists Crossref holds for the original and for
the corrigendum. If the corrigendum were an author fix, the two deposits should
differ.

**The result:** they are **identical**, all seven authors, same given names, same
order, in both records.

```
10.1016/j.rineng.2025.107189   Yasuo Nihei, Shiho Onomura, Yu Bando, Takashi Inoue,
                               Jin Kashiwada, Yasuhiro Yoshikawa, Mamoru Tanaka
10.1016/j.rineng.2025.107527   Yasuo Nihei, Shiho Onomura, Yu Bando, Takashi Inoue,
                               Jin Kashiwada, Yasuhiro Yoshikawa, Mamoru Tanaka
```

**Hypothesis refuted.** The corrigendum is not an author-list correction, so the
convenient conclusion is unavailable and the numeric values remain provisional. I
am recording the refuted hypothesis rather than deleting it, because the next
person to look at this will form the same one.

Note the limit of this test: it shows the *deposited metadata* is unchanged. A
corrigendum could still correct an author name in the article body without
Elsevier redepositing the author list. So this lowers the probability, it does not
drive it to zero.

## 3. An author-name trap in the highest-value paper found this dispatch

Three sources disagree on one author of `10.1016/j.rineng.2025.107189`:

| source | given name |
|---|---|
| Crossref (publisher deposit), original **and** corrigendum | **Yu** Bando |
| OpenAlex | **Yoshinori** BANDO |
| scite | **Yoshinori** BANDO |

This is not a publisher disagreement. OpenAlex's own record carries both fields
and shows exactly where the divergence enters:

```
raw_author_name : "Yu Bando"          <- what the publisher deposited
display_name    : "Yoshinori BANDO"   <- OpenAlex's disambiguated author profile
author id       : https://openalex.org/A5015524040
institution     : Tokyo University of Science
```

So OpenAlex's author-disambiguation step has mapped the deposited string
"Yu Bando" onto a profile displayed as "Yoshinori BANDO", and scite reproduces
the same display name. The publisher deposit is consistent across both DOIs and
says **Yu**.

**Cite this paper as Bando, Y. (or Bando, Yu). Do not write Yoshinori.** More
generally: **do not take author given names from OpenAlex or scite for this
corpus.** Their `display_name` is a disambiguation product, not a transcription,
and this dispatch has now been bitten by name-variant problems twice, the other
being the Hamid versus Muzzamil Shah collision in unit 3 that would have produced
a wrong scale factor.

This matters here specifically because I ranked Nihei 2025 the single
highest-value citation found in this dispatch (unit 3 section 5), so it is the
one most likely to reach the bibliography.

**UNVERIFIED:** I could not fetch the OpenAlex author profile itself, which
returned HTTP 403, so I have not confirmed whether A5015524040 is a false merge
with a different researcher or simply a display-name choice. The actionable part
does not depend on that: the publisher deposit says Yu, twice, and that is what a
citation should follow.

## 4. Status

No project simulation number is asserted here. Nothing outside
`docs/R5_RESEARCH_*` and `data/r5_citation_*` was touched.

Open, unchanged: the corrigendum content, and the three closed-access full texts
(He 2026, Zhang 2023, Lyu 2023). All four are access-blocked, not effort-blocked.
