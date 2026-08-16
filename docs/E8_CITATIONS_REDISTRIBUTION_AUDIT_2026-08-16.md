# `citations/` redistribution audit

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.
**Diagnosis only. Nothing deleted, nothing untracked, nothing pushed.**

Same discipline as the `vehicle_geometry_research/` audit in
`E8_GEOMETRY_REDISTRIBUTION_DECISION_2026-08-16.md`: per file, read live off
`origin/main`. Claims tagged **[read]**, **[recalled]**, **[inferred]**.

Scope note: D1 mines the **content** of these files. This assesses their
**redistribution status**. No overlap.

> ### Read the `license` field, not `isOa`
> The single most misleading result in this document: **`isOa: true` is not
> permission.** Bronze open access means free to read on the publisher's site, under
> **no licence at all**, and it returns `isOa: true` with no `license` field. The next
> reader will reach for that boolean; it gives the wrong redistribution answer. See
> `E8_METHOD_LESSONS_2026-08-16.md` L-B.

> ### Where this sits among the three exposures
> They are **not equally serious, and they differ in kind, not just size.** Ranked on
> the evidence in these documents:
>
> | # | Exposure | Scale | Rights position | Public surface |
> |---|---|---|---|---|
> | 1 | **CCSA/NCAC geometry.** 4 original distribution archives (88,592,238 B) + 14 extracted decks (71,716,670 B), redistributed **intact**, not derived | 160,322,098 B | Licence **silent**: no grant, no licence name, no copyright statement | **30 of 30 branches** |
> | 2 | **Smith 2019 reproduction.** The complete 15-page article, page by page | 6,215,623 B | Licence **asserted**: "© 2019 CIWEM and John Wiley & Sons Ltd" legible in the copy itself | 1 tree, `main` |
> | 3 | The two CC-licensed PDFs | 10,884,441 B | **Licensed.** Housekeeping, not a problem | 1 tree, `main` |
>
> **1 is largest and most widespread; 2 is smallest of the three but the least
> ambiguous**, because silence leaves an open question and an explicit © does not.
> They need different remediation shapes and should not share a recommendation.
> The four `.ply` files that originally framed this whole thread are 15,823,688 B,
> **under 9% of the geometry tree**, and should stop being the headline.
>
> Separately, the credential FLAG document is public on **1 of 30** branches while the
> geometry is on **30 of 30**. Same reason: one remediation shape does not fit both.

---

## 1. The finding

> **UNITS. 1 MB = 1,000,000 bytes (decimal SI) throughout this document.**
> **CORRECTED 2026-08-16:** an earlier revision computed every size as
> bytes/1048576 (mebibytes) and labelled the result "MB", understating each headline
> figure by 4.6%. The byte counts were always right and every proportion was
> unaffected, but the labels were wrong and are reissued below. Exact bytes are given
> alongside each figure so nothing has to be taken on trust. The same defect in
> `E8_GEOMETRY_REDISTRIBUTION_DECISION_2026-08-16.md` is corrected there.

`citations/` **is tracked and public.** 38 files, **19,759,424 bytes (19.76 MB)** on
`origin/main`. There is **no `citations` rule in `.gitignore`**, so nothing was ever
intended to keep it out. [read]

**99.2% of it by bytes is third-party material**, not repo-authored work:

| Class | Bytes | MB | Files | Redistribution risk, AFTER the DOI lookups |
|---|---|---|---|---|
| Full-text publisher PDFs | 11,999,575 | 12.00 | 3 | **Mostly CLEARED.** 2 of 3 carry CC licences (10.88 MB). 1 undetermined |
| Reproductions of figures and tables | 7,213,546 | 7.21 | 20 | **HIGH, and now the largest real problem.** 15 of them reproduce a **bronze** article carrying no licence |
| Elicit exports | 350,369 | 0.35 | 2 | Medium, terms-of-service not copyright |
| Third-party code, `(kks32)` | 30,170 | 0.03 | 2 | Low, provenance unrecorded |
| Repo-authored notes | 165,764 | 0.17 | 11 | None |
| **Total** | **19,759,424** | **19.76** | **38** | |

**The lookups inverted the ranking.** Before them, the three PDFs looked like the worst
item and the screenshots like a secondary concern. After them, two of the three PDFs
are licensed for redistribution and **the screenshots are the problem**, because the
article they reproduce is bronze OA: free to read, no licence. Section 3.

This is the same family of problem as the CCSA decks, but it is **not** uniformly
"cleaner cut" as the first revision claimed. Journal licensing turned out to have three
distinct answers across three files from two publishers, and the single most important
one is the least visible: an `isOa: true` flag with no licence behind it.

---

## 2. Full-text PDFs, per file

**RESOLVED 2026-08-16 by DOI lookup (scite).** The three files have **three different
answers**, and none matches what my earlier probe suggested.

| File | Bytes | DOI | OA status | Licence | Redistribution |
|---|---|---|---|---|---|
| `J Flood Risk Management - 2025 - Dasallas - ...pdf` | 3,484,612 | **10.1111/jfr3.70154** | **gold** | **CC BY** | **PERMITTED** with attribution |
| `Water Resources Research - 2021 - Wang and Marsooli - ...pdf` | 7,399,829 | **10.1029/2020WR028616** | **hybrid** | **CC BY-NC-ND** | **PERMITTED** with attribution, **non-commercial, no derivatives** |
| `ARR_Project_10_Stage2_Report_Final.pdf` | 1,115,134 | n/a, report P10/S2/020 | n/a | **UNDETERMINED** | see flag file |

**Two of the three PDFs are cleared outright.** 10.88 MB of the 12.00 MB is licensed
for redistribution. That is the opposite of what section 1's risk table assumed, and
the risk table is corrected accordingly.

**The CC BY-NC-ND file is the one that proves the carve-out matters.** Wang and
Marsooli is **non-commercial** and **no-derivatives**, while the repo's root `LICENSE`
is BSD 3-Clause, which grants every recipient commercial rights and the right to
modify. The repo is therefore currently offering downstream users terms on this PDF
that its own licence forbids. This is no longer a hypothetical argument for the
carve-out in `E8_THIRD_PARTY_NOTICES_DRAFT_2026-08-16.md`: it is a concrete,
documented instance. Keeping the file is fine; keeping it under an unqualified BSD
grant is not.

### WITHDRAWN: my `strings` licence probe, in full

The earlier revision of this section reported a `strings` scan for CC markers, found
none in any of the three PDFs, and ran a control counting visible URLs. The control
showed 413 and 199 URLs in the two Wiley files and 0 in the AR&R report, and I
concluded the probe was **"valid"** for the two Wiley files and blind only for AR&R.

**That conclusion was wrong, and the whole probe is withdrawn.** The DOI lookup shows
both Wiley files carry Creative Commons licences, so the probe returned a **false
negative on both of the files where I had just declared it reliable**. It was 0 for 3.

The methodological error is worth stating, because the control looked rigorous and was
not: **I proved the probe could see URLs, then treated that as proof it would see a CC
licence URL if one existed. Those are two different propositions.** A control that
establishes a probe's *reach* does not establish its *sensitivity to the specific
thing being tested*. The correct control would have been to run the identical probe
against a PDF of known CC-BY status and confirm it fires. I did not do that.

No conclusion in this document now rests on that probe. The three rows above come from
DOI lookup only.

### Also found: a citation defect in `citations/README.md`

`README.md` gives DOI `10.1111/jfr3.12527` the title **"Full-scale testing of vehicle
floating and sliding in flowing floodwater"**. The DOI actually resolves to
**"Full-scale testing of stability curves for vehicles in flood waters"**, Smith,
Modra & Felder, *JFRM* 12(S2), 2019-03-05. [read, scite]

The DOI is right and the title is wrong. Worth fixing before the bibliography is
frozen, and worth checking whether the wrong title propagated into the paper's `.bib`.
That is D1's territory, not mine; flagging, not touching.

---

## 3. Reproductions of figures and tables, 20 files, 7,213,546 B (7.21 MB)

This is the class most likely to be overlooked, because a `.png` does not look like a
copy of a paper. Every one of these reproduces third-party expression verbatim.

**Counts corrected 2026-08-16**, by tab-aware re-parse of `git ls-tree` (these
filenames contain spaces, which silently broke the first pass and produced a
14-screenshot figure and two wrong subtotals):

| Group | Files | Bytes | MB | What it is |
|---|---|---|---|---|
| `Smith-Modra-Felder/Screenshot 2026-07-03 at 3.15-3.16 PM.png` | **15** | **5,846,160** | **5.85** | Screen captures taken in one 50-second burst, so a page-by-page capture of a single document **[inferred, from the timestamps]** |
| `Smith-Modra-Felder/smith2019_instability_table.png` | 1 | 369,463 | 0.37 | A table from the same paper |
| **Smith group, total** | **16** | **6,215,623** | **6.22** | |
| `WRL reports technical and Research/` Figure 5-5, Table 5-1, Table 5-2 | 3 | 760,091 | 0.76 | Figures and tables from a Water Research Laboratory, UNSW report |
| `ARR table 1 - guidelines and recommendations for limits for vehicle stability.png` | 1 | 237,832 | 0.24 | A table reproduced from AR&R |
| **All reproductions** | **20** | **7,213,546** | **7.21** | |

### RESOLVED, and it went the wrong way. Smith 2019 is BRONZE.

The earlier revision hoped this group might dissolve: JFRM publishes CC BY articles,
and a sibling JFRM paper (Azhar, Pauwels and Bui 2023, `10.1111/jfr3.12885`) is
recorded in the project's own skill file as "open access", so Smith 2019 might be
CC BY too, clearing the largest image group at a stroke.

**Checked. It is not.** `10.1111/jfr3.12527` returns `isOa: true`, **`oaStatus:
"bronze"`**, and **no `license` field at all**. [read, scite]

**Bronze open access is the trap in this whole exercise.** It means the publisher has
made the article free to *read* on their own site, at their discretion and revocably,
under **no open licence**. Contrast the two files resolved in section 2, which return
an explicit `license` of `cc-by` and `cc-by-nc-nd`. Bronze returns none, because there
is none.

So `isOa: true` is **not** a redistribution permission, and anything that reads only
that boolean will reach the wrong answer. Free to read is not free to republish.

**Consequence:** the 15 Smith-Modra-Felder screenshots (5,846,160 B, 5.85 MB), and the 1 table image beside them (369,463 B), are verbatim
reproductions of an article that carries no redistribution licence. This is the
**largest genuine problem in `citations/`**, and it is larger than the PDFs, two of
which turned out to be licensed.

**Warning for the sibling citation:** Azhar 2023 `10.1111/jfr3.12885` is described in
the repo as "open access" with no qualifier. Given that its sibling in the same
journal is bronze, **that description should not be trusted to mean CC BY** until its
`license` field is checked the same way. The repo's own notes do not distinguish
bronze from gold anywhere, so the same conflation may sit elsewhere in the
bibliography. [read / inferred]

The AR&R and WRL images remain undetermined; their source terms are unread and two
attempts to reach them failed, see the flag file.

### 3.1 Triage of the 16, by opening them. It is the COMPLETE ARTICLE.

Asked to sort the 16 into figures, tables, regenerable data and load-bearing items, I
opened them rather than inferring from filenames. The sort mostly dissolves, because
the answer is bigger than the question. **[read, direct inspection]**

| Opened | What it actually is |
|---|---|
| `Screenshot ... 3.15.26 PM.png` | **Page 1 of 15.** Title page. DOI 10.1111/jfr3.12527, authors, abstract, keywords, start of section 1 |
| `Screenshot ... 3.15.59 PM.png` | **Page 10 of 15.** Figure 7 and Figure 8, both **photographs**, plus two columns of body text |
| `smith2019_instability_table.png` | **Page 12 of 15.** Figure 10, a scatter plot. **Misnamed: it is a figure, not a table** |

15 screenshots, captured at 3-to-4-second intervals across 50 seconds, with confirmed
page markers at **1 of 15**, **10 of 15** and **12 of 15**.

**Conclusion: the 15 screenshots are pages 1 through 15. The entire article is
reproduced, complete, page by page.** Not a selection of figures. **[inferred from
three confirmed page markers plus the count and the interval; strong, and the
remaining 12 were not individually opened]**

**This is materially more serious than "screenshots of figures and tables", and it
changes the kind of problem, not just the size:**

1. It is a **complete verbatim copy of a copyrighted journal article**, republished on
   a public repository across, on current evidence, one branch surface.
2. Page 1 carries the publisher's own notice, legible in the reproduction:
   **"© 2019 The Chartered Institution of Water and Environmental Management (CIWEM)
   and John Wiley & Sons Ltd"**. So this is not licence-*silent* like the CCSA decks.
   The rights holder is named and the reservation is explicit, in the copied artifact
   itself. [read]
3. Page 10 is **photographs** (friction testing on sand and gravel; a model Yaris in a
   flume). Photographs are creative works and are the least defensible category here.
   They also cannot be regenerated by anyone.

**It also independently confirms the `README.md` title defect** from section 2: page 1
prints the title as **"Full-scale testing of stability curves for vehicles in flood
waters"**, and the DOI on the same page is 10.1111/jfr3.12527.

### 3.2 The remediation is easy, and nothing is lost

The regeneration idea is right in principle and turns out not to be needed, because
**the project does not use the pages. It uses four scalars.** Measured by searching
the repo for what is actually taken from this paper: [read]

| Value | Occurrences in repo | Nature |
|---|---|---|
| `C_D = 1.38` | 12 | Fact, not copyrightable |
| `Equation 6` (referenced, and recorded as NOT supporting the drift threshold) | 8 | Reference to a result |
| `mu = 0.78` (wet and dry concrete) | 3 | Fact |
| `mu = 0.3` (sand/gravel worst case, inherited convention) | 3 | Fact |

**Facts and measured values are not protected by copyright; the expression of them
is.** So the project can keep every number it relies on, cite them, and carry none of
the images. And because the article is **bronze OA, it is free to read at the DOI**,
so a reader following the citation gets exactly the access the screenshots provided.

**Recommended, and it requires no permission from anyone:**

1. Write the four values, with page or figure references, into a short grounding note
   beside the existing `citations/smith_modra_felder_2019_velocity_grounding.md`.
2. Untrack all 16 files (6,215,623 B).
3. Cite the DOI, which is free to read.

That removes the single least defensible item in `citations/` at **zero research
cost**. If a figure is ever genuinely needed in the paper, regenerate it from cited
values, or request permission from CIWEM/Wiley through the normal figure-reuse route,
which for a single figure in an academic paper is routine and usually free.

---

## 4. Elicit exports, and third-party code

**`Elicit - extract-results-review-5e368aae-...csv` (347,747 B) and
`Elicit - Flood-Crossing Tire-Ground Friction and Speed Evidence.bib` (2,622 B).**
These are machine extractions **derived from** other people's papers, produced by a
commercial service. The question is not classical copyright but Elicit's terms of
service on redistributing bulk extraction output, plus the residual question of how
much verbatim abstract text the CSV carries. Neither was checked. D1 is mining these
for content, so **coordinate before touching them**. **[not checked]**

**`citations/vehicle(kks32).py` (18,329 B) and `citations/splat_sim(kks32).py`
(11,841 B).** Third-party source attributed by filename to kks32 (Krishna Kumar),
sitting loose in `citations/` with **no licence header check, no upstream URL and no
pinned SHA**. Register E8 records `geoelements/gns` as MIT, but that does not
automatically cover these two files, which are not identified as being from that repo.
**[read / recalled]**

The fix here is already sitting in the repo, see section 5 of the notices draft: move
them under `third_party/` with the same `VENDORED.md` + `PINNED_SHA.txt` treatment
`mpm-engine` already has. That converts an unrecorded copy into a documented one.

---

## 5. Recommendation

Three of the four lookups are now done, so this is no longer speculative.

1. **KEEP, and add attribution:** `Dasallas 2025` (CC BY) and `Wang and Marsooli 2021`
   (CC BY-NC-ND). Both are licensed for redistribution. Record each licence in
   `THIRD_PARTY_NOTICES.md`, and note that the NC-ND terms on Wang and Marsooli are
   **narrower than the repo's BSD grant**, which is exactly what the carve-out clause
   is for.
2. **UNTRACK the 16 Smith-Modra-Felder files** (6,215,623 B, 6.22 MB: 15 screenshots plus 1 table image). Bronze OA
   gives no redistribution right. `git rm --cached` plus a `.gitignore` rule keeps the
   files on Josie's disk, where they are legitimately useful, and stops them being
   carried forward. As everywhere in this dispatch, it does **not** unpublish what is
   already public.
3. **Replace them with the citation and a link.** The article is free to read at the
   publisher, so a DOI link gives any reader the same access the screenshots do, at
   zero redistribution risk. `citations/README.md` already does this well for most
   entries and is the right long-term pattern: cite, do not carry.
4. **Resolve the AR&R and WRL terms** before deciding on those **4** images (3 WRL,
   1 AR&R table). Blocked twice, see `E8_FLAG_ARR_TERMS_UNRESOLVED_2026-08-16.md`.
   Until then, leave them: deleting on an unread licence is as unevidenced as keeping
   on one.

   **The AR&R PDF specifically must NOT be treated like the other two PDFs, because
   removing it has a research cost they do not carry.** It is load-bearing evidence,
   not just an exposure item:
   - D1 used it **tonight** as the primary source to refute a proposed `CLAUDE.md`
     amendment. **[relayed by the coordinator, not verified by me]**
   - Project memory records it as the primary PDF that prints the **verified AR&R
     ISBN and Table 3**, after an audit wrongly called both unverified and had them
     deleted. **[recalled]** That is a documented instance of this exact file being
     removed on a bad call and having to be restored.
   - `citations/README.md` sources the entire **L1 depth-velocity hazard threshold**
     to it, including the DV <= 0.60 m2/s figure and the report's own "draft, interim,
     informal" caveat. **[read]**

   So the ranking for the three PDFs is: Dasallas and Wang are **licensed, keep,
   attribute**; AR&R is **undetermined, and the highest-cost of the three to remove**.
   If its terms come back unfavourable, prefer untracking over deleting, and record
   the DOI and ISBN in `README.md` first so the evidence survives the file.
5. **Re-check Azhar 2023** `10.1111/jfr3.12885` and any other repo citation described
   as "open access" without a licence name, per the bronze warning in section 3.
6. **Move the two `(kks32)` files** under `third_party/` with `VENDORED.md`.
7. **Fix the `README.md` title mismatch** on `10.1111/jfr3.12527`, section 2.

**Do not bulk-delete `citations/`.** 11 files are repo-authored analysis, including
`README.md`, `drift_threshold_grounding.md` and
`smith_modra_felder_2019_velocity_grounding.md`, which are genuine project work and
some of the better provenance records in the repo.

---

## 6. What this did not establish

- **No DOI was resolved and no publisher page was fetched.** Every open-access
  statement above is a probe result or an inference, never a determination.
- **The AR&R probe was blind** and its negative is withdrawn, section 2.
- **The screenshots were not opened.** They are classified by filename, path and
  capture-timestamp clustering, not by viewing them. A file named as a figure could
  be something else.
- **Elicit's terms were not read.**
- **I did not check the other 29 public branches** for `citations/` variants. The
  geometry sweep showed the public surface is 30 branches, not one tree, and this
  audit covers `origin/main` only. A stale copy on another branch would not appear
  here.
- **physics-skeptic not run:** no physical claim in scope. Byte counts are arithmetic
  over `git ls-tree` and are reproducible from the command in section 1. Mark
  UNREVIEWED by scope, not by omission.
