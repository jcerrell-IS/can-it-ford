# Semi-empirical baseline: citation retrieval and coefficient provenance

Date: 2026-08-13
Branch: `claude/semi-empirical-citations-fcc6f3`, cut from `main` at `1a868f3`
Dispatch: DP-7, "Retrieve Xia 2011 and Shu 2011"

This document was adversarially reviewed before commit. The review refuted the first
draft's central inference and found five further blocking defects. All are corrected
below and the withdrawals are recorded explicitly in section 5d rather than silently
edited out.

Anchors read live before any retrieval was attempted:

- `docs/semi_empirical_baseline_findings.md`, 297 lines, present on this branch.
  Landed in `91cf0a3`, confirmed an ancestor of HEAD by `git merge-base --is-ancestor`.
- `data/semi_empirical_baseline_2026-08-08.csv`, 2,661 bytes, 71 lines including header.
  **Read from the main tree at `/Users/josie/can-it-ford/`, not from this worktree**,
  where it does not exist. See section 9a for why that distinction matters.
- `scripts/semi_empirical_baseline.py`, 11,504 bytes.
- Register `G10`, `G10a` and the 2026-08-08 amendment, at
  `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md:285-295`.

**Claim tagging used throughout:** (READ) = read directly from a live file or a
publisher/registry record this session. (RECALLED) = carried from another document on
this machine, not independently re-derived here. (INFERRED) = reasoning from the above,
not observed. (SECONDARY) = from a search-engine summary or similar, provenance not
established, explicitly not to be relied on.

**Engine tag:** nothing in this document is a solver claim. The semi-empirical baseline
is a pure-Python analytic force balance in `scripts/semi_empirical_baseline.py`. It is
not warpmpm and not Genesis. Where `mu = 0.55` is discussed it is shared with the 17
canonical **warpmpm** runs, per register and CLAUDE.md item 3.

**Scope warning for anyone re-running the greps in this document:** several load-bearing
files live under `_inbox/`, which is gitignored (`.gitignore` carries an `_inbox/` rule,
re-derive the line number, do not cite it) and therefore **absent from git worktrees
entirely**. Every grep below must be run from `/Users/josie/can-it-ford/`. Running them
from a worktree silently omits `_inbox/`, `data/` and most of `renders/`. The first draft
of this document made exactly that error twice.

---

## 0. The acceptance criterion, fixed before retrieval

Per the dispatch: a PDF that does not contain these coefficients does not close this
item. Written from a live read of `scripts/semi_empirical_baseline.py:36-77` and
`docs/semi_empirical_baseline_findings.md:75-83`, before any search was run.

The local baseline needs a primary source for exactly one numeric coefficient, plus two
formula-level items:

| # | Item | Local value | Status going in |
|---|---|---|---|
| C1 | `C_D` drag coefficient band and point value | 1.22 to 6.82, midpoint 4.02 delivered | **UNVERIFIED**, the only unsourced number in the model |
| C2 | Published sliding-onset formula (Xia 2011) | not implemented | fallback used instead |
| C3 | Published sliding-onset formula (Shu 2011) | not implemented | fallback used instead |

Everything else in the model already traces to a repo primary source: `rho_w` 1000,
`g` 9.81, `m` 1100.0 (`vehicle_params.py`), `V_hull` 3.542739 m^3, `W_hull`/`H_hull`
1.7464/1.5180 m, `mu` 0.55. Those were not the subject of this dispatch and were not
re-derived, with one exception noted in section 6 item 6.

**The headline result of this dispatch is that C1 cannot be closed by C2 or C3.** See
section 4. That is a structural finding about the dispatch's own premise, not a retrieval
failure.

---

## 1. Which Xia paper this is (DoD item 5)

There are **three** distinct papers in play, not two, and not one paper with a year
error. All three resolved live against Crossref this session (READ), which is the
version-of-record registry:

| Short name | Title | Authors, in order | Journal | Print year | Online | DOI |
|---|---|---|---|---|---|---|
| **Xia 2011** | Formula of incipient velocity for flooded vehicles | Junqiang Xia, **Fang Yenn Teo**, Binliang Lin, Roger A. Falconer | Natural Hazards 58(1):1-14 | **2011** (July) | 2010-10-20 | `10.1007/s11069-010-9639-x` |
| **Shu 2011** | Incipient velocity for partially submerged vehicles in floodwaters | **Caiwen Shu**, Junqiang Xia, Roger A. Falconer, Binliang Lin | J. Hydraulic Research 49(6):709-717 | **2011** (Dec) | 2011-10-07 | `10.1080/00221686.2011.616318` |
| **Xia 2014** | Criterion of vehicle stability in floodwaters based on theoretical and experimental studies | Junqiang Xia, Roger A. Falconer, Xuanwei Xiao, **Yejiang Wang** | Natural Hazards 70(2):1619-1630 | **2014** | 2013-10-11 | `10.1007/s11069-013-0889-2` |

Resolution of the known traps:

1. **The 2013-vs-2014 trap applies only to Xia 2014.** Crossref gives print year 2014 and
   online-first 2013-10-11 for `10.1007/s11069-013-0889-2` (READ). The DOI string
   contains "013" because DOIs are minted at online-first. **Cite 2014.** This confirms
   the standing project note and the memory `xia-2014-not-2013-citation-trap`.
2. **Xia 2011 has its own, separate online-first offset**, 2010-10-20 against print 2011
   (READ). Both Xia papers carry a one-year online/print gap, in different years. This is
   the likeliest mechanism by which the two get conflated. Register `G10` already records
   the 2010-10-20 date and is correct (READ).
3. **The fourth-author question on Xia 2014 resolves to Yejiang Wang, on version-of-record
   evidence only.** Crossref gives Xia, Falconer, Xiao, Wang (READ), and the Cardiff ORCA
   record for the same DOI lists the same four (READ). The ORCA accepted manuscript's
   embedded document title is `Paper 158 JX_RAF_XX_YW Natural_Hazards_Journal_2014.doc`
   (READ, as the PDF's title metadata rendered in-browser), where **YW** = Yejiang Wang.
   **These are not three independent witnesses.** The first two are both version-of-record
   metadata, and the third is a filename from the same ORCA record as the second. **None
   of them is the post-print author list**, which is the only thing artifact `266e9a8a`
   actually disputes (RECALLED). The claimed "Caiwen Shu on the post-print" discrepancy is
   therefore **neither confirmed nor refuted here**. It can only be settled by opening the
   downloaded PDF's title page. **Cite Wang** regardless: that is the version of record.
4. **`docs/semi_empirical_baseline_findings.md` targeted Xia 2014, not Xia 2011.** Its
   section 1 table gives DOI `10.1007/s11069-013-0889-2` (READ). So the 2026-08-08
   baseline session tested retrieval of Xia **2014** and Shu **2011**, while this dispatch
   and register `G10` name Xia **2011** and Shu **2011**. The baseline doc is internally
   consistent (it refers to "the ground-slope term from the 2014 paper") but the pairing
   has been read as if it were G10's pair. It is not.

---

## 2. Per-coefficient provenance (DoD item 1)

| Coefficient | Value used locally | Source claimed locally | Primary record now confirms? | DOI | Retraction check |
|---|---|---|---|---|---|
| `C_D` band | 1.22 to 6.82 | "Journal of Hydrology 2023 flume study (PII S0022169423004675)" via a file that does not exist, `scripts/semi_empirical_baseline.py:54-61` (READ) | **YES, the band is confirmed verbatim** in the source abstract, as `1.22 ≤ CD ≤ 6.82`. But see section 5c: it is a joint envelope over **three vehicles and all flow directions**, so it does not license any single value for this hull | `10.1016/j.jhydrol.2023.129525` | **Clean.** Crossref reports no `update-to`/`updated-by` (READ) |
| `C_D` point | 4.02 | midpoint of the band, arithmetic confirmed: (1.22+6.82)/2 = 4.02 (READ) | **No, and it is not a meaningful statistic.** It is the midpoint of an envelope spanning three vehicle classes and every orientation from 0 to 180 degrees. See 5c | as above | as above |
| Xia 2011 sliding formula | not implemented | Xia 2011 | **No. Not retrieved.** See section 3 | `10.1007/s11069-010-9639-x` | **Clean.** Crossref: no updates (READ) |
| Shu 2011 sliding formula | not implemented | Shu 2011 | **No. Not retrieved.** See section 3 | `10.1080/00221686.2011.616318` | **Clean.** Crossref: no updates (READ) |
| Xia 2014 slope term | not implemented | Xia 2014 | **No. Not retrieved as a file**, but a legitimate green-OA copy was located and confirmed downloadable by a human. See section 3 | `10.1007/s11069-013-0889-2` | **Clean.** Crossref: no updates (READ) |

All four retraction checks were run against Crossref's `updated-by` graph, the same source
Scholar Sidekick's `checkRetraction` wraps and which mirrors Retraction Watch. Scholar
Sidekick itself returned `Too many requests` and `You are not subscribed to this API` this
session, the identical failure the 2026-08-08 session recorded, so Crossref was used
directly instead.

---

## 3. Retrieval outcome (DoD items 2 and 3)

### NOT RETRIEVED: Xia 2011, `10.1007/s11069-010-9639-x`

- **Unpaywall, direct** (`api.unpaywall.org/v2/`): `is_oa: false`, `oa_status: "closed"`,
  `oa_locations` **EMPTY**, `journal_is_oa: false` (READ). This is the independent
  open-access check the 2026-08-08 session attempted and could not complete. It now
  completes, and it **confirms** the Scite finding rather than contradicting it.
- **Cardiff ORCA**: no record located. ORCA's own search was reached in a browser but not
  exhaustively enumerated, and programmatic search is blocked (below), so this is "not
  located", **not** "does not exist".
- **ORCA eprint 54161**, which a search engine asserted was this paper, **is not this
  paper**. It is Teo, Fang Yenn (2010) PhD thesis (READ). See section 6 item 2.
- **academia.edu**, copy listed at `/1186497/`: gated behind a signed-in account (the
  sibling Shu copy returned HTTP 403). Not pursued: creating accounts is not something
  this session will do. A logged-in human can very likely get this one.
- **Publisher (Springer)**: paywalled. Purchase not attempted: real financial cost is a
  hard stop.
- **UT Austin library proxy / ILL**: **not attempted, and cannot be by this session.**
  Both require authenticating as the user. No ILL request was placed. This is the
  remaining live route and it needs a human.

### NOT RETRIEVED: Shu 2011, `10.1080/00221686.2011.616318`

- **Unpaywall, direct**: `is_oa: false`, `oa_status: "closed"`, `oa_locations` **EMPTY**
  (READ).
- **Cardiff ORCA, eprint 17057**: record exists and states **verbatim**: "Full text not
  available from this repository." Official URL points to the paywalled DOI. No download
  control and no request-a-copy control on the page (READ, in-browser).
- **IAHR society library**, `iahr.org/library/infor?pid=4653`: record exists for exactly
  this paper. Clicking Download "will only navigate to the article page"; full-article
  access requires "your institute or individual membership" (READ). A third independent
  confirmation of the paywall, after Scite and Unpaywall.
- **academia.edu** (`/1109743/`, second copy at `/8730767/`): HTTP 403 without a signed-in
  account. Not pursued, same reason as above. This is the route artifact `266e9a8a` says
  it used, so its copy is plausibly real and simply requires a logged-in human.
- **Publisher (Taylor & Francis / IAHR)**: paywalled. Not purchased.
- **UT Austin proxy / ILL**: not attempted, same reason as above.

### NOT RETRIEVED AS A FILE, but located and confirmed available: Xia 2014

- **Cardiff ORCA, eprint 54002**: carries "PDF - Accepted Post-Print Version,
  Download (227kB) | Preview", with the note "Pdf uploaded in accordance with publisher's
  policy at http://www.sherpa.ac.uk/romeo/issn/0921-030X/" (READ, in-browser). A
  legitimate green-OA deposit by the authors' own institution.
- Direct file URL: `https://orca.cardiff.ac.uk/id/eprint/54002/1/Xia%202014.pdf`
- **Automated download failed and was not forced.** `curl` with a normal browser
  user-agent returned a 50,883-byte HTML page titled "Verification | Cardiff University"
  containing a Cloudflare JavaScript challenge, not a PDF. That file was inspected,
  identified and deleted; nothing bogus was left in `citations/`. WebFetch returned HTTP
  403. The ORCA OAI-PMH harvesting endpoint (`/cgi/oai2`) is behind the same challenge.
  CORE returned a 308 redirect with no resolvable download id. **Cloudflare bot-detection
  was deliberately not worked around.**
- **Evidence caveat:** because every programmatic route is blocked, the three ORCA
  findings in this document rest on a **single browser witness each** and cannot be
  reproduced by command line. An independent reviewer confirmed `curl` returns HTTP 403
  with `<title>Verification | Cardiff University</title>`. Re-verify in a browser, not
  with `curl`, and do not record a `curl` failure as evidence the record is absent.
- **A human, in a normal browser, can download this file in one click.**

### NOT RETRIEVED: Hu et al. 2023, `10.1016/j.jhydrol.2023.129525`

The paper the `C_D` band traces to. See section 5.

- **Unpaywall, direct**: `is_oa: **true**`, `oa_status: "hybrid"`, license
  **`cc-by-nc-nd`**, best location the publisher, `publishedVersion` (READ). Legitimately
  free to read.
- **ScienceDirect**: Cloudflare "Just a moment..." interstitial on two separate attempts
  several minutes apart, in a real browser. Not worked around.
- **Scite full text**: metadata returned, but `contentDenied: true` and **zero**
  `fulltextExcerpts` across three differently-worded targeted queries.
- **The abstract, however, is already on disk** and was read (section 5c). The **body** is
  what remains unread, and the body is where the per-vehicle, per-direction coefficient
  table lives.
- **A human can open the DOI and read it for free.** This is the single highest-value
  five-minute action arising from this dispatch.

### Files written to `citations/`

**None.** No PDF retrieval succeeded, so nothing was added. `citations/` still holds its
21 pre-existing entries, unchanged (verified live). An honest empty result is preferred to
a file that is actually a challenge page, which is what the one automated attempt produced.

---

## 4. The structural finding: the named papers cannot close the C_D gap

This is the most important result in this document and it changes what "done" means for
register item J6.

Per the transcription in `docs/RESEARCH_ARTIFACT_INTEGRATION_2026-08-07.md` section 4.1
and its underlying artifact `~/Downloads/compass_artifact_wf-266e9a8a-...md`, read
directly this session (READ, of the artifact; the artifact's claims **about the papers**
are RECALLED, since the publisher PDFs remain unread):

Neither Xia 2011 nor Shu 2011 publishes a numeric `C_D`, `C_L` or `mu` inside the working
formula. All are folded into two lumped, flume-calibrated regression parameters: `a`/`b`
in Xia 2011, `alpha`/`beta` in Shu 2011. (Paraphrased, not quoted: the artifact's own
wording pairs the symbols as "α/a and β/b". The per-paper assignment above follows
artifact:96.) The artifact states the point three times, including in its recommendations:
"Do **not** attribute a numeric CD, CL, or mu to either final formula."

**Therefore:** retrieving the Xia 2011 and Shu 2011 publisher PDFs, which is what this
dispatch was commissioned to do, **cannot** supply a value for `C_D`, because those papers
deliberately do not contain one. The acceptance criterion set for this dispatch is not
satisfiable by the papers the dispatch names.

What retrieving them **would** legitimately close:

- C2 and C3, the published formulae, so the baseline could be re-implemented as published
  rather than as a first-principles fallback.
- Confirmation of the transcribed `a`/`b` and `alpha`/`beta` tables, which J6 correctly
  requires before the paper cites them.

What it would **not** close: C1.

One consequence worth stating plainly: the lumped parameters are calibration constants for
specific die-cast models (Pajero, BMW M5, Mini Cooper for Xia 2011; Ford Focus, Ford
Transit, Volvo XC90 for Shu 2011) (RECALLED, artifact:28 and :62), not transferable
physical constants. Implementing the published formulae for a Yaris hull would mean using
another vehicle's calibration, which is a different and arguably worse provenance problem
than the current fallback has. Decide that deliberately, not by default.

---

## 5. The C_D band: source, and what it actually spans

### 5a. The dangling PII resolves, but this is a re-discovery, not a discovery

`scripts/semi_empirical_baseline.py:54-61` attributes the band to "a Journal of Hydrology
2023 flume study (PII S0022169423004675)" cited in
`docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md`, a file that does not exist on disk
and has never existed in git history (re-confirmed live: `ls` fails, `git log --all`
returns empty) (READ).

The PII resolves, via Crossref's `alternative-id` index (READ):

> **Hu, Xiaozhe; Li, Junqi; Wang, Wenhai; Fang, Xing (2023).** "Experimental testing to
> determine stability thresholds for partially submerged vehicles at different flow
> orientations." *Journal of Hydrology* **620**, 129525.
> DOI `10.1016/j.jhydrol.2023.129525`. Open access, hybrid, CC-BY-NC-ND. No retraction,
> correction or expression of concern. Published 2023-04-18.

**This identification was already on disk and had been since 2026-07-20.** An earlier
draft of this document called it newly identified; that was a novelty overclaim and is
withdrawn. `_inbox/session_archive/LIVE_SESSION_LOG_2026-07-20.md:11873-11882` already
carries the paper's title, DOI, author list, publication date and **full abstract**, and
`_inbox/Can It Ford? - Comparative Engine, Model, and GH200 Build-Feasibility Sweep...md:82`
already summarises the band with its three vehicles, calling it "the most directly citable
coefficient set broken out by class and orientation" (both READ).

The real defect was never that the source was unknown. It was that the material sat in
gitignored `_inbox/` while the script pointed at a filename that had never existed, so
nobody could get from one to the other. **The pointer was broken, not the citation.**

### 5b. Corrections to the baseline findings doc, and to my own first draft

`docs/semi_empirical_baseline_findings.md:129` states the PII "appears **nowhere** in the
repository." **That is false.** Run from the main tree (READ), the PII appears at **five**
real sites:

```
_inbox/Can It Ford? - ...GH200 Build-Feasibility Sweep... .md:82
_inbox/session_archive/LIVE_SESSION_LOG_2026-07-23.md:13189
_inbox/session_archive/LIVE_SESSION_LOG_2026-07-23.md:19407
docs/semi_empirical_baseline_findings.md:129
scripts/semi_empirical_baseline.py:56
```

Likewise `6.82` appears in five files, not one: the two `_inbox/` logs, the `_inbox/`
sweep document, the findings doc and the baseline script.

**My own first draft reported two hits and one file, because I ran the grep from this
worktree, where `_inbox/` does not exist.** That is the identical failure mode section 9a
documents, committed in the same document that documents it. It is corrected here and
recorded rather than quietly fixed. Note this is **not** the CLAUDE.md H0 hazard: H0 is
the shell `grep` function skipping gitignored paths, whereas here `/usr/bin/grep` was
correct and the files were physically absent from the tree.

**A second year trap, newly found.** `LIVE_SESSION_LOG_2026-07-23.md:13189` and `:19407`
both cite this paper as **"Hu et al. (2024, *Journal of Hydrology*, article
S0022169423004675)"**. Crossref gives **2023**, volume 620, published 2023-04-18 (READ).
**The correct citation year is 2023.** This is a third instance of the project's recurring
year-drift pattern, after Xia 2014-vs-2013 and Xia 2011-vs-2010.

### 5c. What the band actually spans (this replaces the first draft's argument)

**Verbatim from the abstract** (READ, from
`_inbox/session_archive/LIVE_SESSION_LOG_2026-07-20.md:11873-11882`):

> "In this study a series of experiments were conducted with a small passenger vehicle,
> Polo GTI, a large passenger vehicle, Audi A6L, and a large four-wheel drive (4WD)
> vehicle, Range Rover models with a scale of 1:18. ... The drag forces and transverse
> forces at different flow orientations were determined experimentally using a hydraulic
> flume, and the drag coefficients (1.22 ≤ CD ≤ 6.82) and transverse force coefficients
> (0 ≤ CT ≤ 2.40) **of the three vehicles** were determined by fitting data from all
> experiments at the same flow direction (from 0° to 180°)."

So the band `1.22 ≤ C_D ≤ 6.82` is a **joint envelope over three vehicle classes and all
flow directions**. Four consequences:

1. **No endpoint can be assigned to "head-on compact sedan" from the abstract alone.**
   1.22 might be the Polo GTI head-on, or the Range Rover at some angle, or the Audi at
   180 degrees. Nothing published in the abstract assigns it.
2. **The delivered midpoint 4.02 is not an estimate of anything.** It is the arithmetic
   centre of an envelope spanning three vehicle classes and every orientation. It is not a
   central value for a Yaris-sized hull in head-on flow, and it was never claimed to be by
   the source. This criticism of 4.02 is **stronger and better founded** than the
   orientation argument the first draft made, and it does not depend on any unread text.
3. **Orientation alone cannot explain the spread.** Hull `L/W = 4.2826/1.7464 = 2.4522`,
   so switching from head-on to broadside buys about **2.45x** in projected area, against
   a band ratio of `6.82/1.22 = 5.59`. The residual factor of about 2.28 is the size of
   the three-vehicle span. Xia 2014's own fitted orientation constants move by 2.32x for
   the Honda but **0.84x for the Audi** (RECALLED, artifact:89), i.e. not even in a
   consistent direction across vehicles.
4. **The correct value to extract is the Polo GTI at 0/180 degrees**, that being the
   closest analogue to a Yaris, read from the body table together with the reference area
   it is normalised against. `C_D` and reference area are inseparable
   (`docs/semi_empirical_baseline_findings.md:145-146` already states this).

**Competing hypothesis, named rather than dismissed.** Arrighi et al. 2015, summarised at
`_inbox/...GH200 Build-Feasibility Sweep...md:81` (READ), reports CFD-derived drag and lift
coefficients that both **decrease with increasing Froude number**, for a single vehicle at
a single orientation. Since `C_D = 2F/(rho A V^2)`, any part of `F` that is a backwater
head difference scaling with `g*delta_h` inflates `C_D` without bound as `Fr` falls. Hu's
per-flow-direction fitting weakens this as an explanation of *this* band, but does not
eliminate a Froude contribution to its width. This is a live alternative to both the
orientation and the three-vehicle readings.

### 5d. Withdrawn from the first draft

Recorded rather than deleted, so the same reasoning is not re-derived later:

- **WITHDRAWN: "the band is almost certainly a band across orientation."** Refuted by the
  abstract's "of the three vehicles". It is a joint vehicle-and-direction envelope.
- **WITHDRAWN: "1.22 is the head-on value, so the baseline should use it."** Unsupported.
  No endpoint is assignable without the body text.
- **WITHDRAWN (SECONDARY, misattributed):** a quoted sentence that Hu "reports the highest
  drag force and displacement at 90 degree orientation", and the claim of "13 orientation
  angles". Both came from a search-engine summary, not from the abstract, and neither
  appears anywhere on disk. The first draft tagged them READ. They are **unsourced
  secondary material** and nothing may rest on them.
- **WITHDRAWN: the "1.10 below chassis / 1.15 above chassis, Keller and Mitsch 1993 after
  Gerhardt and Gross 1985" row**, presented as already in this repo. `/usr/bin/grep -rn
  "Gerhardt"` over the whole main tree including `_inbox/`, `data/` and `renders/` returns
  **only this document**. It has no in-repo origin and no primary source, so it is struck.
- **CORRECTED: register line 226.** The Keller and Mitsch material is at register **:257**,
  not :226; :226 is a blank line inside item E8. And :257 says Keller and Mitsch 1993 "was
  a **desk study with no physical test at all**, assuming mu = 0.3 and Cd = 1.1" (READ).
  So it is an *assumed* value, not a measured one, and it is not independent of the
  register's own `mu = 0.3` lineage.

### 5e. The sensitivity is one-sided, not a symmetric band

The first draft described an "8.57 point swing across the band". That understates the
structure. Recomputed live this session from
`data/semi_empirical_baseline_2026-08-08.csv` by rescaling the delivered incipient
velocity (`V_c` scales as `C_D^-1/2`, verified against the findings doc's own table to
four decimals):

| `C_D` | Overall agreement | Informative region, `d <= 0.4` |
|---|---|---|
| **1.22** (band low) | 61/70 = **87.14%** | 19/28 = **67.86%** |
| 1.38 (in-repo measured average) | 62/70 = 88.57% | 20/28 = 71.43% |
| **4.02** (delivered midpoint) | 67/70 = **95.71%** | 25/28 = **89.29%** |
| **6.82** (band high) | 67/70 = **95.71%** | 25/28 = **89.29%** |

**Agreement is completely flat from 4.02 to 6.82.** The entire sensitivity lives in the
low end of the band. So the only question that matters is whether the correct `C_D` for
this hull and this flow orientation is near 1.22, and if it is, the **informative-region
agreement collapses from 89.29 to 67.86 percent, a 21.43 point fall**, three times the
headline drop. That is the number to watch, not the 8.57 point headline change.

**Do not quote 95.71 percent in the paper or on the poster until the body table is read.**
The baseline doc already warned that 95.71 "is not a fitted optimum, but it is also not a
prediction that survived a test it could have failed." The flatness above makes that
sharper: 95.71 percent is what the entire upper half of the band produces, so it is
consistent with a wide range of wrong choices as well as the right one.

**Falsifying test, cheap:** open `https://doi.org/10.1016/j.jhydrol.2023.129525`, find the
`C_D` table broken out by vehicle and flow direction, read off the **Polo GTI at 0 and 180
degrees** and the reference area used. If that value is near the bottom of the band, the
delivered CSV is optimistic and must be regenerated. If it is mid-band, 4.02 is defensible
by accident and should be replaced by the actual figure anyway.

---

## 6. Corrections to the existing project record

Each verified live this session.

1. **The register's "UNSETTLED" contradiction in G10a is PARTLY resolved, and both sides
   were partly right.** The register records artifact `266e9a8a` claiming full-text
   retrieval from Cardiff ORCA against an independent 2026-08-08 check finding that ORCA
   record metadata-only, and says "Both cannot be right about the same repository."
   **They were not talking about the same record.** Three ORCA records exist:

   | ORCA eprint | Paper | Full text? |
   |---|---|---|
   | 17057 | **Shu 2011** | **No.** "Full text not available from this repository" (READ) |
   | 54002 | **Xia 2014** | **Yes.** Accepted post-print, 227kB, deposited per publisher policy (READ) |
   | 54161 | **Teo 2010 PhD thesis**, not a journal paper | **Yes.** Accepted post-print, 22MB (READ) |

   The artifact's *per-paper* ORCA claim sits under its **Xia 2014** heading (artifact:85)
   and is **correct**. The independent check landed on **Shu 2011** and is **also
   correct**. Both stand; neither needs deleting.
   **But this is not full resolution.** Artifact:4 says "**Both** papers' full text was
   successfully retrieved ... on academia.edu", and artifact:105 gives a blanket source
   line, "author-accepted manuscripts (**academia.edu / Cardiff ORCA**)", covering the
   report including Shu. Eprint 17057 contradicts any ORCA sourcing for Shu. So: the
   per-paper claim is reconciled, the blanket source line at :105 is still wrong for Shu.
   Always name the eprint id.

2. **ORCA 54161 is not a Xia paper.** It is Teo, Fang Yenn (2010), "Study of the
   hydrodynamic processes of rivers and floodplains with obstructions", PhD Thesis, Cardiff
   University, with a freely downloadable 22MB accepted post-print (READ). A web search
   asserted it was "Formula of incipient velocity for flooded vehicles"; that assertion is
   wrong and should not be propagated.

   **It is nonetheless a substantive lead.** Teo is the **second author of Xia 2011**
   (READ, Crossref). The thesis abstract describes "a series of experimental investigations
   ... on stationary scaled model vehicles in laboratory flumes, to study the effects of
   vehicles on flood flow propagation and, the influence of the flood flows on the
   stability of the vehicles" (READ). That is the Xia 2011 experimental programme, by one
   of its authors, freely available now. It is a thesis, not the version of record, so it
   cannot satisfy J6's "cite the published article" requirement, but it is the cheapest
   route to checking the section 4.1 transcription against author-written text.

3. **`docs/semi_empirical_baseline_findings.md:129` is wrong** about the PII appearing
   nowhere in the repository. See 5b. That file is outside this dispatch's write scope and
   was **not** edited.

4. **`docs/semi_empirical_baseline_findings.md` open item 1 still stands.**
   `docs/CANITFORD_RESEARCH_INTEGRATION_v2_2026-08-05.md` still does not exist and still
   has no git history (READ). CLAUDE.md continues to cite it as demoted-to-historical, so
   that pointer is still dangling. What this dispatch adds is that the **content** it was
   cited for is recoverable from `_inbox/` (5a), so the dangling pointer is no longer
   load-bearing for the `C_D` claim.

5. **`data/semi_empirical_baseline_2026-08-08.csv` is untracked and gitignored** under the
   `data/*` rule (`git check-ignore -v`; re-derive the `.gitignore` line number rather than
   citing it, per CLAUDE.md). It exists only in the main working tree and has no commit
   history. Any figure sourced from it currently has no provenance and it can change
   without trace. Consider a `!data/semi_empirical_baseline_*.csv` un-ignore pair, matching
   the existing `!data/track1_sweep_v2/` precedent.

6. **`docs/semi_empirical_baseline_findings.md:82` cites the wrong lines for `mu = 0.55`.**
   It gives `sim_standing.py:84 and :235`. Live (READ):

   | Copy | Lines |
   |---|---|
   | `renders/yaris_render_s1/sim_standing.py` (top-level) | **:154** `floor_friction=0.55`, **:309** `default=0.55` |
   | `renders/yaris_render_s1/_incoming/sim_standing.py` | **:76**, **:227** |

   Neither matches :84/:235. The **value** 0.55 is correct and is genuinely consumed as
   the floor friction, so no result changes; only the citation is stale. Register D4a makes
   `_incoming/` the canonical per-run tree, so a corrected citation must say which copy it
   means. Flagged for that file's owner.

---

## 7. Proposed G10a amendment (DoD item 4)

**Not applied here. DP-1 owns `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` and must
apply it.** Proposed text to append to G10a:

> **AMENDED 2026-08-13. The ORCA contradiction is partly resolved, and the C_D gap is
> proven not to be closable by G10's own papers.**
>
> **(a) The "one narrow contradiction" was largely a record mix-up.** Three separate
> Cardiff ORCA records were opened in a browser on 2026-08-13: eprint **17057** (Shu 2011)
> states verbatim "Full text not available from this repository", with no download and no
> request-a-copy control; eprint **54002** (Xia 2014) carries a downloadable 227kB accepted
> post-print deposited "in accordance with publisher's policy" per SHERPA/RoMEO; eprint
> **54161** is **not a Xia paper** but Teo, Fang Yenn (2010) PhD thesis, with a downloadable
> 22MB post-print. Artifact `266e9a8a`'s *per-paper* ORCA claim is filed under **Xia 2014**
> and is **correct**; the independent 2026-08-08 check landed on **Shu 2011** and is **also
> correct**. Both stand. **Residual, still open:** the artifact's blanket source line
> (academia.edu / Cardiff ORCA) covers Shu too, and eprint 17057 contradicts ORCA sourcing
> for Shu. Downgrade from UNSETTLED to PARTLY RESOLVED, do not close. Always name the
> eprint id. Note all three ORCA findings rest on a single browser witness: `curl` and
> WebFetch both receive a Cloudflare challenge, so a command-line failure is not evidence.
>
> **(b) Retrieving Xia 2011 and Shu 2011 cannot supply a numeric C_D, so it cannot close
> the semi-empirical baseline's only unsourced coefficient.** Both papers deliberately fold
> C_D, C_L and mu into two lumped flume-calibrated regression constants. This is already in
> G10a's load-bearing facts; the consequence had not been drawn. J6 stays open for the
> formulae and the alpha/beta tables, which retrieval **would** close. It must **not** be
> described as the blocker on C_D.
>
> **(c) The C_D band 1.22 to 6.82 is confirmed verbatim against its source, and the source
> was already on disk.** The dangling PII `S0022169423004675`, cited to a file that has
> never existed in git history, is **Hu, Xiaozhe; Li, Junqi; Wang, Wenhai; Fang, Xing
> (2023), "Experimental testing to determine stability thresholds for partially submerged
> vehicles at different flow orientations", Journal of Hydrology 620:129525, DOI
> 10.1016/j.jhydrol.2023.129525**, open access (hybrid, CC-BY-NC-ND), no retraction,
> correction or expression of concern (Crossref, 2026-08-13). Its **full abstract has been
> in `_inbox/session_archive/LIVE_SESSION_LOG_2026-07-20.md:11873-11882` since
> 2026-07-20**; the pointer was broken, not the citation. **Cite the year as 2023.** Two
> in-repo sites (`LIVE_SESSION_LOG_2026-07-23.md:13189` and `:19407`) call it "Hu et al.
> (2024)", which is wrong: a third year-drift instance after Xia 2014-vs-2013 and Xia
> 2011-vs-2010.
>
> **(d) The delivered midpoint C_D = 4.02 is not a defensible statistic, on the abstract's
> own wording.** The abstract states the coefficients "**of the three vehicles** were
> determined by fitting data from all experiments at the same flow direction (from 0° to
> 180°)", the vehicles being Polo GTI, Audi A6L and Range Rover at 1:18. The band is
> therefore a **joint envelope over three vehicle classes and all flow directions**, and
> 4.02 is the arithmetic centre of that envelope, not an estimate for any single vehicle at
> any single orientation. **No endpoint can be assigned to head-on compact-sedan flow
> without the body table**, and the required value is the Polo GTI at 0/180 degrees
> together with its reference area (C_D and reference area are inseparable). An earlier
> reading of this band as orientation-only is **withdrawn**: hull L/W is 2.45 against a band
> ratio of 5.59, so orientation cannot account for it alone. A Froude-dependence
> contribution (Arrighi et al. 2015) is a live alternative and is not excluded.
>
> **(e) The agreement figure is one-sidedly sensitive, so do not quote it yet.**
> Recomputed 2026-08-13 from `data/semi_empirical_baseline_2026-08-08.csv`: overall
> agreement is **95.71 percent (67/70) at both C_D = 4.02 and C_D = 6.82**, i.e. **flat
> across the whole upper half of the band**, but falls to **87.14 percent (61/70) at
> C_D = 1.22**. In the informative region (d <= 0.4 m) the fall is far larger, **89.29
> percent (25/28) down to 67.86 percent (19/28), a 21.43 point collapse**. **Do not quote
> 95.71 percent in the paper or on the poster** until the Polo GTI head-on coefficient is
> read. 95.71 percent is what the entire upper half of the band produces and so is
> consistent with many wrong choices as well as the right one.
>
> **(f) Retrieval status, so it is not re-attempted blindly.** Unpaywall, queried directly
> on 2026-08-13, independently confirms Xia 2011, Shu 2011 and Xia 2014 are all
> `is_oa: false`, `oa_status: closed`, with **zero** OA locations. This is the check the
> 2026-08-08 session could not complete, and it **confirms** G10's Scite finding rather than
> competing with it. The IAHR society library independently confirms the Shu paywall
> (membership required). academia.edu copies of both 2011 papers exist but are gated behind
> a signed-in account. Automated retrieval of the ORCA and ScienceDirect PDFs is blocked by
> Cloudflare bot-detection, which was deliberately not circumvented; **a human in a browser
> can download the Xia 2014 post-print and read the Hu 2023 OA article in one click each.**
> No ILL request has been placed as of 2026-08-13.

---

## 8. Open items this produced

1. **Read Hu et al. 2023 and settle the C_D value.**
   `https://doi.org/10.1016/j.jhydrol.2023.129525`, open access, free. Read the per-vehicle
   per-direction C_D table, take the **Polo GTI at 0/180 degrees** and its reference area.
   This decides whether the delivered CSV must be regenerated and whether the reportable
   informative-region agreement is 89.29 or 67.86 percent. **Highest value, lowest cost
   item in this document.**
2. **Download the Xia 2014 accepted post-print** from
   `https://orca.cardiff.ac.uk/id/eprint/54002/1/Xia%202014.pdf` (227kB, one browser click)
   into `citations/`. Closes the primary source for register **G9**, the "25 percent lower
   on a 1:50 slope" claim, currently cited without a local primary record.
3. **Download the Teo 2010 thesis** from ORCA eprint 54161 (22MB). Most likely
   freely-available author-written account of the Xia 2011 experiments. Use it to check
   `RESEARCH_ARTIFACT_INTEGRATION` section 4.1's transcribed a/b table. Not a substitute
   for the version of record.
4. **Place the ILL / UT Austin proxy requests for Xia 2011 and Shu 2011.** Still the only
   route to the versions of record, still requires a human. Nothing has been requested.
   Per section 4, this closes the formulae, **not** C_D.
5. **Resolve the Xia 2014 fourth-author question inside the post-print body.** All current
   Wang evidence is version-of-record metadata; the disputed object is the post-print
   author list. Check the title page of the downloaded PDF. Cite Wang regardless.
6. **Fix `docs/semi_empirical_baseline_findings.md`**: line 129 ("appears nowhere in the
   repository") and line 82 (`sim_standing.py:84 and :235`, actually :154/:309 top-level or
   :76/:227 in `_incoming/`). Owner of that file, not this dispatch.
7. **Consider tracking `data/semi_empirical_baseline_2026-08-08.csv`**, currently gitignored
   and untracked with no provenance.
8. **`.claude/checks/count_claims_check.py` is worktree-sensitive** and reports 25 spurious
   blocking defects from a worktree against 0 from the main tree. See section 9a. Either run
   it only from `/Users/josie/can-it-ford`, or make it detect
   `git rev-parse --git-common-dir != .git` and refuse.
9. **Correct the "Hu et al. (2024)" year** at `LIVE_SESSION_LOG_2026-07-23.md:13189` and
   `:19407`. The paper is 2023.

---

## 9. Scope and process notes

- Files written this session: this document only. Plus one transient download into
  `citations/` that proved to be a Cloudflare challenge page rather than a PDF; it was
  identified and deleted, leaving `citations/` at its original 21 entries.
- `docs/semi_empirical_baseline_findings.md`,
  `data/semi_empirical_baseline_2026-08-08.csv`,
  `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`, `CLAUDE.md` and all `.tex` files
  were **read only** and not modified, per dispatch scope.
- **Hard stop respected:** the publisher route for Xia 2011 (USD 37.95 buy / 19.00 rent)
  and Shu 2011 (USD 73.95 buy / 25.00 rent), per prices recorded in
  `docs/semi_empirical_baseline_findings.md`, was not taken. Real financial cost is not
  something this session will incur.
- **Bot-detection respected:** Cloudflare challenges on `orca.cardiff.ac.uk` and
  `sciencedirect.com` were encountered and not circumvented. Where a normal browser session
  reached a page in the ordinary way its rendered content was read; no challenge was
  solved, replayed or worked around. **Account creation declined** on academia.edu.
- **Adversarial review:** this document was reviewed by the `physics-skeptic` agent before
  commit. It refuted the first draft's central inference (section 5c) and found five
  further blocking defects. Every one of its blocking findings was **independently
  re-verified against primary files before being accepted**, and all are corrected above,
  with withdrawals recorded in 5d rather than silently removed.

### 9a. Pre-commit checks, and a tooling trap found while running them

`.claude/checks/register_integrity.py`: **0 blocking defects**, 106 items across 10
sections. This document adds no register item and declares no threshold literal, confirmed
by grep.

`.claude/checks/count_claims_check.py` **gives a different answer depending on which tree
you run it from**, a new instance of the hazard CLAUDE.md item 13 documents. Both runs
2026-08-13, same commit:

| Run from | Defensible totals | Blocking defects |
|---|---|---|
| `/Users/josie/can-it-ford` (main tree) | 22 / 23 / 24 | **0, passes** |
| this worktree | 16 / 17 | **25, fails** |

A git worktree does not carry untracked or gitignored files, so the `DRIFT_THRESHOLD`
declaration sites under `data/`, `renders/` and `archive/` are simply absent and the
checker correctly counts what it can see. The main-tree numbers are the real ones and
match register D7's total of **24, on the reading "gp_surrogate default included, archive/
included"** (stating the scope, per CLAUDE.md item 13, which forbids a bare total).

**Consequence for the "run the integrity check before any commit" rule:** running
`count_claims_check.py` from a worktree produces 25 spurious BLOCK lines and invites
someone to "correct" a total that is not wrong. Run it from the main tree. Filed as open
item 8.
