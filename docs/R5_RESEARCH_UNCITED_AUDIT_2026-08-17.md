# R5-D1 unit 28: auditing my own "uncited" determinations for a method hole

Date 2026-08-17. Branch `claude/r5-research`.

Unit 27's lesson was that the register can already hold what a corpus artifact
appears to reveal. That prompts an obvious question about my own central
deliverable: **my "uncited" determinations are DOI-string matches, but the
register cites plenty of work by author and year with no DOI at all.** If that is
a hole, `data/r5_citation_xref.tsv`'s 452-uncited figure overstates.

**Result: the method mostly holds. One nuance, no retraction.**

---

## 1. The test

For every paper I actually made a claim about, check whether its author surname
appears in the two canonical files, `CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`
and `CLAUDE.md`, independent of any DOI.

| author | DOI I called uncited | name-hits in the canonical files |
|---|---|---:|
| Varshney | `10.4271/2021-01-0205` | **0** |
| Nihei | `10.1016/j.rineng.2025.107189` | **0** |
| Remmerswaal | `10.1016/j.compgeo.2024.106494` | **0** |
| Canelas | `10.1016/j.apor.2018.04.015` | **0** |
| Lyu | `10.1016/j.compfluid.2023.106144` | **0** |
| Yamashita (He 2026) | `10.1115/1.4071177` | **0** |
| Sugiyama (He 2026) | `10.1115/1.4071177` | **0** |
| Allen | `10.4271/2003-01-0966` | 2 |
| Zhao | `10.1016/j.compfluid.2018.10.007` | 4 |
| Al-Qadami | `10.3390/su151713262` | 3 |

Seven of ten return zero, so those uncited calls survive a check that does not
depend on DOIs at all. The three non-zero cases were already known to me and were
already stated: Allen 2003 is named in CLAUDE.md A-3 (unit 25 recorded that its
only repo appearance is inside a catalog file, not as a citation), and Zhao 2019
is CLAUDE.md's named in/outflow BC source and **is** cited by DOI in 10 files
(unit 21).

## 2. The one nuance, on Al-Qadami

Al-Qadami returns 3 hits, so it is worth being precise about what I claimed.
The register's mentions, read live:

- **G5**: "Al-Qadami tested a PERODUA VIVA, not a Toyota Yaris. Any claim that
  Al-Qadami found a Yaris floating at 0.40 m ... is a MISATTRIBUTION."
- **G8**: a negative finding about resolution and thresholds.
- A lookup row repeating the G5 misattribution.

So the register knows the name, and it knows it primarily as a **misattribution
hazard**. It does not record the 2023 paper as the nearest comparator with full
scale, six-degree-of-freedom coupled motion, and both instability thresholds.

My unit 7 wording was "**the paper** does not cite the closest comparable study at
all", which is about the bibliography and is accurate: the DOI appears only inside
a `note` of a stub entry cited in zero `.tex` files. **But I have used the looser
word "project" when relaying this to the board, and that is wrong.** The project
plainly knows the name. The precise statement is:

> The bibliography does not cite Al-Qadami 2023, and the register frames
> Al-Qadami primarily as a misattribution hazard rather than as the nearest
> comparator.

That is what should be repeated, not the looser version.

## 3. What this does and does not establish

**Does:** the DOI-string method is not systematically blind for the papers I built
arguments on. Seven of ten are absent by name as well as by DOI.

**Does not:** validate the full 452. I checked the ten I made claims about, not
the whole set. A DOI in the xref marked uncited could still be a work the register
names by author and year, and for 452 rows that is unmeasured. The honest label
for the 452 is **"no DOI-string match in the repo"**, which is what the column
header says, and not "unknown to the project".

I have not changed `data/r5_citation_xref.tsv`. Its column is `cited_anywhere_in_repo`
and it means what it says.

## 4. Status

UNVERIFIED:
1. The other 442 uncited DOIs have not had an author-name check. The
   ten tested were selected because I made claims about them, which is a biased
   sample in exactly the direction that matters, but it is a biased sample.
2. Surname matching is crude: a common surname would produce false hits, and a
   register entry using initials or a different transliteration would produce
   false misses. Zero hits for seven distinct surnames is nonetheless a reasonable
   signal.
3. This audit covers only the two canonical files. Unit 1's xref already covers
   the whole repo by DOI, so the two methods are complementary rather than
   nested.
