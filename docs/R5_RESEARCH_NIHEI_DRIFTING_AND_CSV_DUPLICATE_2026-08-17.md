# R5-D1 unit 12: the highest-priority unread paper, and a duplicate in the CSV

Date 2026-08-17. Branch `claude/r5-research`.

Three results: the paper I ranked highest-priority-unread is now read at abstract
level and it is important; the Elicit CSV contains a duplicate, so my published
denominator of 42 was wrong; and all eight author-sweep DOIs are verified.

---

## 1. Nihei group 2025, small-car drifting from actual vehicle experiments

`10.2208/jscejj.24-16110`, *Japanese Journal of JSCE*, 2025. Authors Onomura,
Inoue, Kashiwada, Yoshikawa, Nihei. `oa_status: closed`, no OA copy, but OpenAlex
exposes the Japanese abstract in full, which I read directly.

**Translation is mine and is tagged as such.** I am not a certified translator;
the technical content is unambiguous but the wording below is my rendering, not a
published English abstract.

The setup, from the abstract: an **outdoor open channel**, slope 1/100, width
2 m, with asphalt paving laid from 16 m downstream of the upstream end, and an
**actual small vehicle** placed on it facing upstream. Discharge was increased
stepwise and the flow conditions at the onset of drifting were measured.

**Three cases: two with the handbrake released, one with the brake applied.**

Two findings, both directly load-bearing for this project:

**(a) Full-scale confirmation of the brake-state result.** In both
handbrake-released cases the vehicle drifted. In the braked case **the vehicle did
not move even at the maximum discharge**. The abstract concludes that the
presence or absence of the brake contributes greatly to whether drifting occurs.

This is an independent, full-scale, physical confirmation of what D4 derived
analytically in `cf9e85c` from the Nihei 2025 rolling-resistance figures. **N = 3
cases**, 2 unbraked and 1 braked, so it is a small sample and a demonstration
rather than a curve.

**(b) The model-scale literature is optimistic, and this is the more important
finding.** My rendering of the closing sentence: compared with previous model
experiment results, the water depth and flow velocity at which drifting occurred
were **somewhat smaller**, showing there is a danger of being washed away even in
gentler flow conditions.

So a real car at full scale drifts at **lower** depth and velocity than
model-derived thresholds predict. That is a direction that matters:

- It compounds my unit 9 scale trap. The problem with model-scale thresholds is
  not only that they need a `lambda^1.5` conversion; it is that even correctly
  converted they appear to be **non-conservative**.
- It sits against CLAUDE.md L-4, which reasons that coarse resolution
  over-predicts peak force and therefore that over-threshold NO-FORD verdicts are
  conservative. L-4 is about *our numerical* conservatism and is untouched by
  this. But the *experimental* literature the thresholds come from now has a
  full-scale result saying those thresholds are on the optimistic side. Those are
  two different conservatism arguments and they should not be merged.

I have not opened the paper body, so the actual depth and velocity values at
drifting are UNVERIFIED. Getting them would be worth more than most of what
remains on my list.

## 2. The Elicit CSV contains a duplicate: 41 unique papers, not 42

Pairwise title similarity across all 42 rows, normalised for hyphenation and
punctuation, at threshold 0.85. Exactly one pair fires:

```
sim 0.992
  row  6  [2016]  doi=(none)                  Stability criteria for flooded vehicles : A state-ofthe-art review
  row 16  [2018]  doi=10.1111/jfr3.12262      Stability criteria for flooded vehicles: a state-of-the-art review
```

Row 6 has no DOI; a Crossref bibliographic search on its title returns
`10.1111/jfr3.12262` at 0.95 similarity, which is row 16's DOI. The two years are
the classic online-first (2016) versus print-issue (2018) split for the same
article.

**So the corpus is 41 unique papers across 42 rows, and my denominator of 42 was
wrong.** Corrected:

```
rows carrying a real threshold value    10 / 41 unique papers   (was stated as 10/42)
rows carrying a real friction value      9 / 41 unique papers   (was stated as  9/42)
```

The duplicate does not change either numerator: row 16 carries the data and row 6
reads "Not mentioned" for both fields.

**And that last sentence is the finding worth keeping.** Elicit extracted the
*same paper twice and returned different answers*: one row with a full set of
thresholds and four friction ranges, one row with "Not mentioned" for both. That
is a direct measurement of the extraction's variance on this dataset, and it is
large. It also means the 10/41 and 9/41 yields are lower bounds: a paper can be
in this CSV with its values silently unextracted, and here is a case where the
same paper both was and was not.

## 3. DOI coverage improved, and an aggregator year error

Eight of the 42 rows carry no DOI. Three are now resolved:

| row | year | resolved DOI | route |
|---|---|---|---|
| 6 | 2016 | `10.1111/jfr3.12262` | Crossref title search, 0.95; it is row 16's paper |
| 18 | 2023 | `10.5194/nhess-2023-130` | Crossref title search, 1.00 |
| 28 | 2017 | `10.26190/unsworks/27433` | DataCite, see section 4 |

The other five (rows 14, 21, 24, 29, 36) returned no confident match, best
similarities 0.22 to 0.65. Row 24, "Development of Appropriate Criteria for the
Safety and Stability of Persons and Vehicles", 2011, is very probably the AR&R
Project 10 material already in the repo at
`citations/ARR_Project_10_Stage2_Report_Final.pdf` and cited as `shand2011`, but
the title does not match closely enough to assert it and I am not guessing.

**Aggregator year error, worth recording as a third metadata trap.** My unit 6
author sweep reported `10.26190/unsworks/27433` as **2024**, taking the year from
OpenAlex. DataCite, which is the registering agency for that DOI, gives
`publicationYear: 2017` and `resourceTypeGeneral: ConferencePaper`, publisher
UNSW Sydney. 2017 is also consistent with Elicit row 28's year. **Treat the 2024
in `data/r5_citation_noncatalog_union.tsv` as wrong.** This is the third
aggregator metadata defect this dispatch has hit, after the Bando given name and
the Azhar subtitle.

## 4. All eight author-sweep DOIs verified, 8 of 8

Unit 6 listed these as unverified. Closed:

```
Crossref-resolvable   5 / 8
DataCite-resolvable   3 / 8   (10.26190/unsworks/27433, 10.4225/53/58e1dfd63f1f4,
                               10.24355/dbbs.084-201611141038-0)
combined              8 / 8
```

The three Crossref failures were not bad DOIs. They are repository and report
DOIs registered with **DataCite**, not Crossref: two UNSW Sydney deposits (a
conference paper and a report) and one Universitätsbibliothek Braunschweig
deposit. **A Crossref miss is not evidence a DOI is invalid**, which is the same
shape as every other false-negative in this dispatch.

## 5. Status

UNVERIFIED:
1. The depth and velocity values in `10.2208/jscejj.24-16110`. Abstract only,
   closed access, Japanese-language journal.
2. My translation of that abstract is my own rendering.
3. Rows 14, 21, 24, 29, 36 still have no DOI. Row 24's likely identity as the
   AR&R Project 10 material is a suspicion, not a match.
4. Whether other duplicate pairs exist below the 0.85 similarity threshold. One
   pass, one threshold.
5. Everything in `FLAG_BLOCKED_2026-08-17.md`.
