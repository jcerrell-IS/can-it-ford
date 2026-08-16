# R5-D1 index and errata: read this before using any number I produced

Date 2026-08-16. Branch `claude/r5-research`, 14 commits from `777567a` to
`66f7427`. Eight documents, five data files.

**Why this file exists.** I corrected myself fourteen times across nine units.
Anyone opening a single document can act on a number I later withdrew. Section 1
is the errata: every superseded claim, what replaced it, and where. Section 2 is
the current best value of every headline number. **If a number below disagrees
with a number in an earlier unit, the number below wins.**

---

## 1. ERRATA. Every claim of mine that was corrected or withdrawn

| # | claim as first written | where | status now | authority |
|---|---|---|---|---|
| 1 | jfr3.12885 appears in 27 files | unit 1 §4a | **25** by the stated method, 26 counting catalogs | `cf9edab`, transposed from another DOI |
| 2 | row 7 is "roughly twenty times below" the other thresholds | unit 1 §3 | **~118x** under Froude, and it is 1:24 not the remembered 1:10 | unit 3 §6 |
| 3 | jfr3.12551 makes the 3.0 m/s cap vehicle-derived, so amend L-2 | unit 1 §3 | **REFUTED.** AR&R says it exists for human stability and occupant egress. **L-2 is correct; do not amend** | unit 3 §4, AR&R primary source |
| 4 | 8 catalogued DOIs are cited in the paper | unit 1 §6 | **3** are `\cite`d; 7 have a real `doi=` field; 8 was string presence | unit 7 §5 |
| 5 | caveat: divergent catalog copies may hide DOIs | unit 1 §8 | **closed at zero**, all five pairs have identical DOI sets | unit 3 §7 |
| 6 | Nihei brake state "bears on our 16 SLIDE verdicts" | unit 3 §5c | **direction wrong.** Lower friction increases sliding, so SLIDEs get *more* robust; the single STUCK run is what is endangered | D4 `cf9e85c`, recorded unit 4 §5 |
| 7 | three novelty axes survive: full scale, particle method, stability verdict | unit 4 §1 | **all occupied.** Only MPM-vs-SPH and geometry provenance remain | unit 4 §1a, then unit 7 §3 |
| 8 | we already cite Al-Qadami 2023 | unit 4 §1a | **WITHDRAWN.** The DOI is in a `note` of a stub entry titled `{{VERIFY: exact title}}`, cited in zero `.tex` | unit 7 §4 |
| 9 | the fix is to iterate the citation graph to fixpoint | unit 4 §3 | **not achievable.** Frontier grew 32→92→174; I stopped it | unit 5 §1 |
| 10 | strict class: 15 found, 8 missed | unit 5 §3 | **14 found, 7 missed** after the borderline was excluded | unit 6 §4 |
| 11 | 85 simulations, catalog recall 27.1% | unit 5 working | **WITHDRAWN.** Contaminated with aircraft, water-exit, deep-sea and waterjet papers. Never quote it | unit 5 §2b |
| 12 | draft resolution claim, "3.8x better resolved", 7.6 vs 2.000 cells per depth | unit 8, never published | **NOT CLEAN, 6 blocking issues.** Rewritten to cell size only | unit 8 §1 |
| 13 | Al-Qadami Table 1 series, carried from the review | unit 8 §4 | **independently verified**, review reproduces exactly | `4140127` |
| 14 | "state the model scale" is the rule | unit 9 §2 | **insufficient.** Needs a second label, `value_basis`, or Azhar 2026 gets inflated 52x | `66f7427`, unit 9 §2b |
| 15 | the CSV holds 42 unique papers; yields are 10/42 and 9/42 | units 1, 9 | **41 unique papers.** Rows 6 and 16 are the same paper (`10.1111/jfr3.12262`, online 2016 vs print 2018). Yields are **10/41** and **9/41**; numerators unchanged | unit 12 §2 |
| 16 | `10.26190/unsworks/27433` is dated 2024 | unit 6, and `data/r5_citation_noncatalog_union.tsv` | **2017.** OpenAlex was wrong; DataCite is the registering agency. **Superseded by erratum 17: it was not the only one, and the TSV is now fixed** | unit 12 §3, then unit 13 |
| 17 | one wrong year, documented but left in the data file | erratum 16 | **two wrong years, both now CORRECTED in the TSV.** `10.26190/unsworks/27433` 2024→**2017** and `10.4225/53/58e1dfd63f1f4` 2017→**2015**. All 28 union rows re-checked against the registering agency: **0 errors in the 25 Crossref-registered DOIs, 2 errors in the 3 DataCite-registered ones** | unit 13 |

**Three of these matter most.** #3, because I proposed the L-2 amendment and my
own test killed it. #8, because it means the paper does not cite its closest
comparator at all. #11, because a contaminated percentage is exactly the kind of
number that survives into a draft if nobody writes down that it was withdrawn.

**A standing caution that came out of #16 and #17.** Four separate metadata
defects in this dispatch all came from bibliographic aggregators rather than from
publishers: the Bando given name (OpenAlex and scite say "Yoshinori", the
publisher deposit says "Yu" in both DOIs), the Azhar subtitle that
`auditBibliography` passed as `matched` while the trailing phrase differed, and
two wrong publication years. The years split cleanly by registering agency:
**0 wrong in 25 Crossref-registered DOIs, 2 wrong in 3 DataCite-registered
ones.** N is only 3 on the DataCite side, so treat that as a signal to check
repository deposits against DataCite directly, not as a rate. General rule:
**for any citation that will reach the paper, take author names, titles and years
from the registering agency (Crossref or DataCite), never from OpenAlex, scite or
Semantic Scholar.** Those are excellent for discovery and unreliable for
transcription.

## 2. Current best value of every headline number

All read live this session. Denominators stated, as required.

**The Elicit outputs**
```
.bib entries                                            8
CSV: data rows 42, columns 27, every row well formed at 27 fields
CSV UNIQUE PAPERS                                      41   (rows 6 and 16 are one paper)
rows carrying a real threshold value          10 / 41   (9 in the summary column, +1 recovered from quotes)
rows carrying a real friction value            9 / 41   (0 hidden in quote columns)
rows carrying RAW MODEL-SCALE values           2 / 12   (rows 7 at 1:24, 23 at 1:10)
motion state                          18 stationary / 14 self-propelled / 10 unstated / 0 towed
copies of each Elicit file on this machine    >=7 and >=6, including inside the repo at citations/
```
Both yields are **lower bounds**, not point values: the duplicated paper was
extracted twice and returned a full threshold set in one row and "Not mentioned"
in the other, so the extraction demonstrably misses values it elsewhere finds.
The "1,345 rows" figure is a `wc -l` artifact of newlines inside quoted fields.
Never use it.

**The catalogs**
```
distinct paper catalogs                        14   (not 6)
papers they claim between them                738
unique DOIs they yield                        472   (union over divergent copies; identical sets)
unique DOIs incl. both Elicit outputs         489
  cited anywhere in the repo                   37
  in a real doi= field of the paper bib         7
  actually \cited in a .tex                     3
```

**Coverage, the load-bearing methodological result**
```
works found by non-catalog routes, absent from all 14 catalogs   28
  found by more than one route                                    5   (routes are complementary)
catalog recall, loose class, 1-hop graph                        16 / 32
catalog recall, strict class, 2-hop graph                        7 / 14
```
Both land at exactly one half, under different class definitions and different
depths. **No catalog-based or keyword-based search can bound this literature, and
that includes the keyword filters I wrote.** Any "N fording simulations exist"
figure is a floor.

**Vehicle-in-water simulations**: at least 16 from the catalogs, plus 16 more from
one graph hop, plus 8 from the author sweep. Treat as a floor, never a total.

## 3. The four papers that actually matter

Everything else widens the field. These bear on the contribution.

| paper | status | what it takes |
|---|---|---|
| `10.3390/su151713262` Al-Qadami 2023 | **full text READ** (CC-BY via UPCommons) | full scale, 6DOF fully coupled, stability thresholds, validated vs AR&R + theory + own experiments. **We do not cite it.** |
| `10.1111/jfr3.12885` Azhar 2023 | abstract read; **we DO cite it** | SPH particle method, validated against a physical model study, confirms AR&R for stationary vehicles. Also the source of our 0.55 friction |
| `10.1115/1.4071177` He 2026 | abstract only, **closed access** | experimental validation of a coupled vehicle-water model, free-running pool + flume |
| `10.1007/s11433-023-2137-5` Zhang 2023 and `10.1016/j.compfluid.2023.106144` Lyu 2023 | abstract/TLDR only, **closed access** | GPU SPH vehicle wading |

Add `10.1111/jfr3.70181` Azhar 2026 as a fourth particle-method paper, and
`10.2208/jscejj.24-16110` (2025 Nihei, small-car drifting from real vehicle data)
as the highest-priority unread item.

## 4. Blocked, and exactly what would unblock each

1. **Nihei 2025 corrigendum** `10.1016/j.rineng.2025.107527`. Eight routes tried.
   The Elsevier landing page carries `tdm-reservation: 1`, a machine-readable
   opt-out from automated retrieval, so I stopped on principle rather than work
   around it. **Unblocks in about a minute**: open
   `https://doi.org/10.1016/j.rineng.2025.107527` in a browser. It is CC-BY once
   open. Until then treat 0.0250 and 0.0242 as provisional.
2. **He 2026, Zhang 2023, Lyu 2023 full texts.** All `oa_status: closed`, no OA
   location in Unpaywall or OpenAlex, no repository deposit. **Unblocks with
   institutional access only.**
3. **`martinezgomariz2018` bib entry.** Has no title, DOI or journal, so its
   intended referent is genuinely ambiguous. I refused to guess. **Unblocks by
   asking whoever wrote the entry.**
4. **The 28 non-catalog works.** Titles and DOIs only, none read. Unblocks with
   time; unit 6 judged the yield low relative to reading the four above.

## 5. Recommendations, none of which I acted on

- **L-2: do not amend.** Attach Cox, Shand and Blacka (2010) as its source. My
  own proposal to amend it was refuted by the primary source.
- **L-7: amend**, per unit 4 §1 as narrowed by unit 4 §1a and unit 7 §3. Do not
  claim full scale, a stability verdict, or "a particle method" as novel.
- **L-5: add a DOI.** Neither Steffen 2008 DOI appears anywhere in the repo
  outside `.claude/`, and neither is in the paper bibliography.
- **Bibliography**: 9 of 21 entries carry a `VERIFY` marker and two have literal
  placeholder titles. Latent, not live, because both are cited nowhere.
- **Threshold table**: use the rebuilt `data/r5_citation_thresholds.tsv` with its
  `model_scale` and `value_basis` columns, never unit 1 §3's table.

I edited no file outside `docs/R5_RESEARCH_*` and `data/r5_citation_*`. I did not
touch `CLAUDE.md`, the register, the bibliography, or any solver file. Nothing is
pushed.

## 6. Consolidated UNVERIFIED

1. Nihei corrigendum content, and therefore whether 0.0250 / 0.0242 are final.
2. He 2026, Zhang 2023, Lyu 2023 full texts. Zhang 2023's "validates code-to-code
   not experimentally" is MEDIUM confidence on a search-engine rendering.
3. None of the 28 non-catalog works has been read.
4. The three model scales 1:14, 1:18, 1:43 are second-hand from a quote column.
5. Their vehicle mass (Perodua Viva) is unpublished; no mass normalisation.
6. Al-Qadami's reported 25% gap against Martinez-Gomariz does not reproduce
   (23.40 / 26.51 / 30.56 depending on denominator).
7. Whether MPM versus SPH is a defensible novelty axis is a physics judgement for
   D4, not a bibliographic one.
8. My author clusters were drawn from authorships I had already seen, so a group
   absent from my set stays invisible and I cannot measure that from inside.
