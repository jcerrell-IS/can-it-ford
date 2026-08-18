# E8: public redistribution of NCAC/CCSA vehicle geometry. Decision document.

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.
**Diagnosis only. Nothing in this document has been executed.**

Every number and quotation below was **read directly** from `origin/main` blobs in
this session, via `git show origin/main:<path>` and `git ls-tree -r --long
origin/main`, unless tagged otherwise. Claims are tagged **[read]**, **[recalled]**
or **[inferred]**.

> **UNITS. 1 MB = 1,000,000 bytes (decimal SI) throughout this document.**
> **CORRECTED 2026-08-16:** the first revision computed every size as bytes/1048576
> (mebibytes) and labelled the result "MB", understating each headline figure by
> 4.6%: the total was published as 168.09 MB when it is 176.25 MB, and the verbatim
> share as 152.90 MB when it is 160.32 MB. Byte counts were correct throughout and
> **the 91.0% proportion is unaffected**, being a ratio, which is why nothing
> downstream broke. Labels are reissued below and exact bytes accompany every figure.

---

## 0.0 E8 CLEARED on reported permission, 2026-08-18. Artifacts pending.

**Josie reports, 2026-08-18: permission for the NCAC/CCSA meshes has been obtained, it
applies globally, and it permits republication. Rights are likewise permitted on the
AR&R paper. She further reports, later the same day, that permission is BLANKET:
"everything is permitted and nothing prohibited", which she confirms extends to the
Wiley/CIWEM article and to the UNSW WRL figures.**

**How to state that outside this repo, and it matters.** The accurate form is *"the
project reports permission from each rights holder"*, **not** *"this material is
unrestricted"*. The four bodies (CCSA/GMU, Engineers Australia, Wiley/CIWEM, UNSW WRL)
granted separately; a blanket summary is a convenience for internal reading, and a
third party who redistributes CCSA material on the strength of a sentence in this repo
would be relying on something no licence file supports. Record the grants per body.** [**her report**, in session. **Artifact not yet filed, and not read by me
or by the coordinator.** A second report arriving later does not upgrade this one:
**two reports are still two reports.**]

**E8's operative rule is satisfied by its own terms.** The rule clears on "written
permission **or** a confirmed licence". This document establishes on three independent
sources that no licence exists to confirm. **Permission is the other route, and it has
been obtained.** Josie is the only person who could have obtained it, and her
confirmation is the primary source for it.

### What this closes

| Item | Status |
|---|---|
| CCSA/NCAC archives and decks, 160,322,098 B, on **every public branch** | **CLEARED for republication** |
| Derived hulls, 2 `.ply` | **CLEARED**, they inherit component 1's position |
| The 6 renders depicting the hull | **CLEARED**, same |
| AR&R report + 4 AR&R/WRL images | **CLEARED**, rights permitted |
| **Section 5's remediation options** | **MOOT. Withdrawn. Do not execute any of them.** |

**No file is to be removed, untracked or history-rewritten on E8 grounds.** Options 1
through 4 in section 5 existed only for the no-permission case, which no longer
obtains. They are retained below as a record of what was considered, clearly marked as
superseded, not as pending work.

### What this does NOT close, and it is one item

**The 16 Smith-Modra-Felder files remain unresolved.** That is a *Wiley / CIWEM*
article carrying an explicit "© 2019 The Chartered Institution of Water and
Environmental Management (CIWEM) and John Wiley & Sons Ltd", legible inside the
reproduction. **A permission from the mesh rights holders does not reach a different
publisher's article.** See `E8_CITATIONS_REDISTRIBUTION_AUDIT_2026-08-16.md` §3, where
the recommendation is unchanged and costs nothing: keep four scalars, cite the DOI,
untrack the images.

### Two housekeeping items, neither of them a doubt

1. **File the permission artifact** at `docs/E8_PERMISSION_<body>_<date>`. Not because
   the permission is in question, but because **a DesignSafe DOI is gated on it**
   (register item 10) and a reviewer will ask for the document. Filing it also means
   the next audit finds the authority in the repo rather than having to re-derive it,
   which is exactly the failure that forced the AR&R ISBN to be re-established this
   round.
2. **Record the granting body and date in `THIRD_PARTY_NOTICES.md`**, which is now the
   place a reader looks to find out that permission exists. That file changes from a
   description of an unpermitted redistribution into a record of the authority the
   redistribution rests on, which is a better document and an easier one to write.

### What the analysis below is still for

It is no longer a case for removal. It remains the **provenance record**: what the
material is, where it came from, that the archives are byte-identical to the upstream
releases by SHA384, that the models are CCSA-authored and CCSA-hosted, and that the
material carries no licence of its own. **That last point is precisely why permission
was the right thing to obtain**, and it is what a reviewer will want to see behind the
permission. None of it is wasted by the clearance; it is the evidence the clearance
rests on.

---

## 0. The headline, and why it changes the framing

E8 as written governs **derived** geometry. Its operative rule, quoted in full because
an earlier revision of this line truncated it (see the correction immediately below):

> "do not commit any derived NCAC/CCSA geometry to the public repo, and do not include
> it in a DesignSafe DOI, **without written permission or a confirmed licence**."

The dispatch that commissioned this work scoped the exposure as four `.ply` files plus
fifteen renders.

> **CORRECTED 2026-08-17, caught by D1 and it was my defect.** This line previously
> quoted only "do not commit any derived NCAC/CCSA geometry to the public repo" and
> stopped there, dropping both the DesignSafe clause and the whole conditions clause.
> That made the prohibition read as **unconditional** in the most-read section of this
> document, when the register makes it conditional. Section 4 quoted the sentence
> correctly throughout, so the argument never depended on the short version, but the
> headline is what gets read.
>
> **Note this is a different truncation from D1's own**, of the same sentence: D1 had
> dropped "or a confirmed licence" and so presented permission as the only route,
> whereas I dropped the conditions entirely. Two sessions truncated one sentence in two
> different places, which is why the full text is now block-quoted rather than inlined.

### The rule offers TWO routes to clearance, and my evidence closes one of them

Written permission **or** a confirmed licence. They are alternatives, not a sequence.
That is D1's substantive point and it is correct.

**It changes nothing about the recommendation, but it changes the reason, which is
worth having right.** The second route is not merely unexplored here; it is **closed by
evidence**, on three independent sources:

| Source | Finding | Origin |
|---|---|---|
| The upstream README bundled in the repo's own copy | No licence text, no copyright statement, no grant | Mine, `git show origin/main` |
| Both `ccsa.gmu.edu` model download pages | No licence, copyright, terms-of-use or redistribution statement | Mine, fetched; **independently refetched by the coordinator** |
| DOI 10.13021/G8JS5D metadata | `rightsList` is **empty**; the DOI points to a validation slide-deck PDF, and the GMU Dataverse CC0 default does not reach it | **D1**, separate method |

**There is no licence to confirm.** So written permission is the only remaining route,
for an evidentiary reason rather than because the rule was misquoted. A reader who only
saw my truncated line would have reached the same destination by the wrong road.

This also means E8's central question now rests on **three independent origins**, not
one cited three times: a bundled file, two live web pages, and DOI metadata, gathered
by two sessions using different methods.

### The commissioned scope understated the exposure by an order of magnitude

The dispatch scoped this as four `.ply` files plus fifteen renders (see the top of this
section). **That scope is wrong, and it is wrong in the direction that matters.** [read]

`vehicle_geometry_research/` on `origin/main` holds **176,252,809 bytes across 30
files (176.25 MB)**. Of that:

| Class | Bytes | MB | Files | Share |
|---|---|---|---|---|
| **Upstream CCSA material, verbatim** (4 `.zip`, 14 `.key`, 4 upstream `README.md`) | 160,322,098 | 160.32 | 22 | **91.0%** |
| Derived hulls (`.ply`) from CCSA decks | 13,422,794 | 13.42 | 2 | 7.6% |
| Reconstructions, not CCSA | 2,400,894 | 2.40 | 2 | 1.4% |
| Repo-authored docs | 107,023 | 0.11 | 4 | 0.1% |
| **Total** | **176,252,809** | **176.25** | **30** | 100% |

The public exposure is **not primarily derived geometry. It is verbatim
redistribution of the original CCSA FE models**, including the complete
`yaris-coarse-v1l.key` at 42,846,753 bytes and `silverado-coarse-v3a.key` at
28,611,724 bytes, plus all four release archives. [read]

This matters because every argument that softens a derived-work claim (transformation,
the hull being a lossy watertight remesh, de minimis) is **unavailable for a verbatim
copy**. The repo redistributes the artifact itself.

The commit that introduced them says so in its own subject line: `f85c385 Add
downloaded NCAC vehicle FE models, Silverado and Yaris, coarse and detailed`. [read]

### And it is on every branch, not one

Raised by D3, and **verified independently here** rather than taken on report, by
walking `git ls-remote --heads origin` and counting `.key` blobs in each tree:

**Every public branch carries exactly 14 CCSA `.key` decks. No branch deviates, and
no branch tree was missing.** Stated as an invariant rather than a count, because the
count keeps moving: 30 on 2026-08-16, 35 on 08-18, **36 on 08-19**. Re-checked by
`E8_VERIFY_FIGURES.py`, which tests the relation rather than a hardcoded number.

> **The public surface GREW while this dispatch ran: 30 branches to 35, and all five
> new ones carry the decks too.** First measured at 30 of 30 on 2026-08-16;
> re-measured at 35 of 35 on 2026-08-18, and again at **36 of 36 on 2026-08-19**. **This is the substantive point, not the
> renumbering:** the exposure tracked the branch count automatically, because every
> branch off `main` inherits the whole tree. Now that permission is reported the growth
> is harmless, but it is worth recording that **any removal-based remediation would
> have been chasing a moving target**, which is a further argument against the option
> 2 and 4 routes that are now withdrawn.

So the exposure is not "a tree on `main`". It is the upstream LS-DYNA **source decks
on the entire public branch surface**. This is the same lesson the credential
correction produced (`5f01dd2`): a one-tree measurement is not a public-surface
measurement, and I made that error in both documents before catching it in neither.

For proportion, the `.ply` files that the original dispatch scoped this task around
are **15,823,688 B (15.82 MB), 9.0% of the tree**, all four of them together. The
`.key` decks and archives are the other 91.0%.

### Coverage: this audit measured what is PUBLIC, and the local tree holds more

**Prompted by D1 and D3, who both found gitignored authored content as a coverage
hole in their own scopes. Checked here, and the same hole exists.** [read, 2026-08-19]

Every figure in this document is measured with `git ls-tree origin/main`, which sees
**tracked files only**. That is the correct scope for an exposure question, because
gitignored means not committed, not pushed, and therefore **not public**. No figure
above changes.

**But the local working tree holds substantially more CCSA material than the public
repository does**, and that is worth stating rather than leaving to be rediscovered:

| | Bytes |
|---|---|
| Public, tracked on `origin/main` | 160,322,098 |
| **Local only, gitignored** | **274,822,319** |
| Local total | 435,144,417 |

The two excluded files are the **detailed** decks:
`silverado-detailed-v3e.key` (105,761,312 B) and `yaris-detailed-v2j.key`
(169,061,007 B).

> **CORRECTED 2026-08-19, caught by D3 within minutes of my publishing it.** I wrote
> *"the unpublished portion is larger than the published portion."* **That is wrong and
> is withdrawn.** D3 pointed out the 275 MB is recoverable from the committed zips, and
> verified here by listing the tracked blobs: `2010-toyota-yaris-detailed-v2j.zip`
> contains `yaris-detailed-v2j.key` at **169,061,007 B** and
> `2007-chevrolet-silverado-detailed-v3e.zip` contains `silverado-detailed-v3e.key` at
> **105,761,312 B**, byte-for-byte the sizes of the local files. [read]
>
> **So nothing is "unpublished". The local files are extracted duplicates of content
> that is already public inside the tracked archives.** The gitignore rule is not
> withholding anything; it is declining to store a second, uncompressed copy.
>
> **This makes the exposure finding stronger, not weaker.** All four CCSA models are
> fully public including both detailed decks, and the two largest single artifacts in
> the whole set, at 169.1 MB and 105.8 MB uncompressed, reach the public repository
> inside the archives. The 160,322,098 B figure is **stored** size; the **content**
> made available is considerably larger, because the archives are compressed.
>
> My error was inferring "not in the tree" meant "not available", without opening the
> archives that were sitting in the tree. That is the partial-view rule again, and I
> had cited it against D1 two hours earlier.

### The rule keeping them out is a credential rule, and it is holding by accident

`git check-ignore -v` gives **`.gitignore:63: *.key`**. That pattern is a
credential-hygiene rule, the kind written to stop private keys reaching a repo. It
catches **LS-DYNA keyword decks** because they share the extension, and nothing about
its intent has anything to do with vehicle geometry.

Two consequences, both worth carrying:

1. **14 `.key` decks are tracked anyway.** `.gitignore` only governs untracked files,
   so those were added before the rule existed or force-added past it. The rule is not
   a guard that held; it is a guard 14 files already bypassed.
2. **Tightening the rule would add 274.8 MB of redundant storage.** If someone narrows
   `*.key` to target credentials precisely, which is a reasonable hygiene improvement,
   these two decks stop being ignored and the next broad `git add` commits them.
   **Corrected per the note above: that publishes no new content**, since both decks are
   already public inside the tracked archives. It would commit a second uncompressed
   copy of material the repo already carries, roughly tripling the size of
   `vehicle_geometry_research/` for nothing.

**Anyone editing `.gitignore:63` should know it is load-bearing for something other
than what it was written for.**

### Reconciling three independent counts of the same tree

D3, the coordinator and I each measured this separately and got **160,308,908 B**
(D3, coordinator) against **160,322,098 B** (me). Verified here: the difference is
**exactly 13,190 B, which is the 4 upstream `README.md` files** (3,465 + 3,324 +
3,281 + 3,120). I counted them as CCSA material, because CCSA authored them; the
others counted only `.zip` + `.key`. **Neither is wrong; the scopes differ, and both
give 91.0%.**

Recorded because `CLAUDE.md`'s `DRIFT_THRESHOLD` item warns that a bare total without
its scope is what goes stale, and because this is the mirror case: two totals that
*differ* while measuring the same thing correctly. State the scope with the number.

The coordinator's finer split reproduces exactly against my own measurement:
**4 original distribution archives = 88,592,238 B**, **14 extracted decks =
71,716,670 B**. [read, recomputed this session]

### CLOSED 2026-08-17: verbatim redistribution is now PROVEN, and the licence silence is confirmed at the source

Two items this document previously listed as unestablished are now established. Both
CCSA download pages were fetched, and the archives were checksummed against them.

**(1) All four archives are byte-identical to the CCSA published releases.** CCSA
publishes a SHA384 per download. Computed locally and compared: [read]

| Archive | Bytes | SHA384 vs CCSA |
|---|---|---|
| `2010-toyota-yaris-coarse-v1l.zip` | 11,228,299 | **IDENTICAL** |
| `2010-toyota-yaris-detailed-v2j.zip` | 42,113,905 | **IDENTICAL** |
| `2007-chevrolet-silverado-coarse-v3a.zip` | 7,384,870 | **IDENTICAL** |
| `2007-chevrolet-silverado-detailed-v3e.zip` | 27,865,164 | **IDENTICAL** |

**4 of 4, 88,592,238 bytes.** Section 7 previously recorded this as `[inferred]` from
filenames and contents. It is now **cryptographically established**.

**The reference values are recorded, so this is reproducible offline.** CCSA's
published SHA384s are transcribed into `docs/E8_VERIFY_FIGURES.py` (`CCSA_SHA384`),
and the script recomputes each archive's hash from `origin/main` and compares. Run
`./docs/E8_VERIFY_FIGURES.py` and this claim re-verifies in seconds with no network.

That matters because it was, until 2026-08-19, the one finding here that could only be
re-checked by re-fetching a `ccsa.gmu.edu` page. **The strongest claim in this document
rested on a webpage that can change or disappear.** Recording the upstream constants is
what turns it from a conclusion you have to trust into one you can run. The repo does not
merely host things that resemble the upstream releases; it hosts **the upstream
releases, bit for bit**.

This closes the last route by which the verbatim half could have been argued down. A
transformation or derived-work defence is unavailable against an exact-hash match.

**(2) The licence silence is confirmed on the download pages themselves, which is a
genuine second source.** Section 1 established it from the README bundled inside the
repo's own copy. That could be called one source read twice. It is not: both
`ccsa.gmu.edu` model pages were fetched independently and **neither contains any
licence, copyright, terms-of-use or redistribution statement**. [read]

**(3) The NHTSA hypothesis is refuted for these models.** Downloads are served from
**`media.ccsa.gmu.edu`**. These are **CCSA-hosted**, so they fall on the licence-silent
side of `b0d2664f`'s distinction and not in the NHTSA "public information and may be
distributed or copied" safe set. Section 1's qualification 1 is discharged.

Both pages also state the models were developed **"under a contract with the Federal
Highway Administration"**, and the Silverado page adds that this was **for research
purposes**. That independently confirms the contractor relationship that makes
17 U.S.C. 105 inapplicable.

**Quote that phrase as context, never as permission.** "Developed under contract with
the FHWA for research purposes" describes **why the model was made**, not **what you
may do with it**. It is the most quotable sentence on either page and the easiest to
misread as a grant, so it should always travel with this caveat. A statement of
purpose by the author is not a licence to the reader, and the same page that carries it
carries no licence at all. Funding is not a grant; neither is a stated research
purpose, and now neither the distributor's page nor the bundled README says otherwise.

**Severity therefore follows bytes and rights-holder clarity, not file type:**

| Rank | What | Bytes | Rights holder | Why it ranks here |
|---|---|---|---|---|
| 1 | CCSA `.key` decks and `.zip` archives, on **every public branch** | 160,322,098 | CCSA/GMU, unambiguous author, silent licence | Verbatim redistribution, largest by far, no transformation argument available |
| 2 | Derived hulls, 2 `.ply` | 13,422,794 | Derived from rank 1 | Inherits rank 1's status, but a genuine derived-work argument exists |
| 3 | Renders depicting the hull, 6 files | see section 3 | Derived from rank 2 | Two steps removed, lowest-resolution depiction |
| 4 | `car_mesh*.ply`, 2 files | 2,400,894 | Not CCSA at all | Outside E8. Do not remediate under it |

The original framing had rank 4 and rank 2 in scope and rank 1 entirely absent.

---

## 1. E8's open question is now RESOLVED, against us

Register E8 records the load-bearing unknown:

> **UNRESOLVED and load-bearing: which side of that line the canonical Yaris falls
> on.** E1 sources the hull to DOI 10.13021/G8JS5D, which resolves to `ccsa.gmu.edu`,
> yet `b0d2664f` lists "older Yaris" among the NHTSA-hosted safe set.

**Resolved for the copy actually in this repository: it is the CCSA-hosted,
licence-silent side.** [read]

The evidence is the upstream README that ships inside the repo's own copy, at
`vehicle_geometry_research/2010-toyota-yaris-coarse-v1l/2010-toyota-yaris-coarse-v1l/README.md`.
Read in full this session. It establishes, in its own words:

- Authorship: "developed by [Center for Collision Safety and Analysis][CCSA]
  researchers at George Mason University. The effort was sponsored by the Federal
  Highway Administration."
- Links to `https://www.ccsa.gmu.edu/` and to `doi:10.13021/G8JS5D`.
- CCSA/GMU staff as the named contacts.
- The only obligation it states: "We ask that the CCSA at GMU and the FHWA be
  acknowledged for any use of this FE model resulting in papers and publications."
- A warranty disclaimer.

**What it does NOT contain, and this is the finding:** no redistribution grant, no
licence name, no copyright statement, and **no NHTSA "public information and may be
distributed or copied" statement.** That statement is the entire basis on which
`b0d2664f` classes some models as safe, and it is absent here. [read]

This is direct evidence about **the artifact that is actually public**, which is the
only object the exposure question is about. It does not depend on the DOI, and does
not need the download page to settle it.

Two qualifications, stated rather than glossed:

1. It does not prove no NHTSA-hosted equivalent of this model exists. `b0d2664f`
   naming "older Yaris" as NHTSA-hosted may well be true of a **different** model
   (the CCSA 2010 Yaris here was released December 2016). If an NHTSA-hosted copy of
   *this* model with the distribution statement exists, the answer changes. That is a
   cheap, checkable follow-up. **[inferred]**
2. FHWA sponsorship does **not** confer public-domain status. 17 U.S.C. 105 reaches
   works of US Government *employees*, not contractors. `b0d2664f` already states
   this. Sponsorship is not a grant. **[recalled from register E8, which quotes the
   report directly]**

---

## 2. A compounding problem the register has not recorded: the repo LICENSE

`origin/main:LICENSE` is **BSD 3-Clause, "Copyright (c) 2026, Josie Cerrell"**, with
no third-party carve-out and no exception for `vehicle_geometry_research/`. [read]

So the repository currently does two things it has no authority to do:

- **Asserts copyright** over a tree that is 91.0% CCSA-authored material.
- **Sublicenses it onward.** BSD 3-Clause grants every downstream recipient the right
  to redistribute. The repo is handing third parties a permission Josie cannot grant.

This is a materially worse posture than redistribution alone, and it is cheap to
improve independently of the geometry decision (see option 0 below). It is also the
single most likely thing to be read as bad faith rather than oversight, which is
exactly the wrong impression for a licence conversation that may need to be friendly.

---

## 3. Per-file provenance. They do not share one answer.

The dispatch's first step was per-file provenance because the four `.ply` might
differ. **They do differ, and the split is two and two.** [read]

| # | File | Verts / faces | Origin | Licence reaching it | Violates E8? |
|---|---|---|---|---|---|
| 1 | `yaris_coarse_v1l_watertight.ply` (12,445,769 B) | 327,212 / 655,308 | mesh2sdf watertight remesh of `yaris-coarse-v1l.key` | **CCSA, licence-silent** | **Yes** |
| 2 | `yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` (977,025 B) | 25,663 / 51,450 | mesh2sdf from a CCSA deck, 2026-07-17, superseded 07-19 | **CCSA, licence-silent** | **Yes** |
| 3 | `failed_reconstructions_2026-07-25/car_mesh.ply` (1,200,447 B) | 31,574 / 63,180 | open3d Poisson reconstruction, `reconstruct_car.py` | **Not CCSA. Source cloud unidentified** | **No** |
| 4 | `failed_reconstructions_2026-07-25/car_mesh_rescaled.ply` (1,200,447 B) | 31,574 / 63,180 | file 3 scaled uniformly by 13.9887 | same as 3 | **No** |

Sources for the origin column, all read this session:

- Files 1 and 2: `vehicle_geometry_research/WATERTIGHT_HULL_TOOL_FINDINGS.md` records
  the sedan hull produced by mesh2sdf on 2026-07-17 (volume 6.8185 m3), superseded by
  the coarse_v1l hull (3.5427 m3), and names the "Four GMU/CCSA LS-DYNA crash FE
  models" as the source geometry. Register E1 independently sources the canonical hull
  to the NCAC/CCSA 2010 Yaris coarse deck.
- Files 3 and 4: `kumar_july9_update/STATUS.md:126` records "Poisson reconstruction,
  `open3d`, `reconstruct_car.py`" and concludes "the source point cloud was never
  car-sized to begin with, **likely a small tutorial demo asset**". Their own README
  measures 0.017291 m3 against the canonical 3.542739 m3, so they are not a
  reduction of the CCSA deck by any route.

**Consequence: E8 does not reach files 3 and 4 at all.** They carry a separate, much
smaller open question (the unidentified demo point cloud's own licence, plausibly the
Open3D bundled demo data, which is MIT). Do not remediate them under E8; it would be
deleting evidence of a documented failure for no licence benefit, and their README is
a genuinely useful record.

### The renders: 6 of 15, not 15

The hull first reaches `origin/main` on **2026-07-18** (`4db2789`). Classifying the
15 tracked `.mp4`/`.gif` by the date each was added: [read]

- **9 are pre-hull and cannot depict CCSA geometry.** The five `kumar_july9_update/`
  SPH renders (2026-07-09), and four added 2026-07-20 whose filenames carry
  2026-07-07 and 2026-07-09 generation timestamps, plus
  `renders/mpm-engine-out/flood_vehicle/flood_vehicle.mp4`, which is the bundled
  model-scale truck splat, not the Yaris. **[the truck identification is recalled,
  not re-verified this session]**
- **6 are post-hull and consistent with depicting the CCSA-derived hull:**
  `figures/hero_g64_m1100.mp4` (07-27), `figures/yaris_flood.{mp4,gif}` and
  `figures/yaris_flood_standing.{mp4,gif}` (07-29),
  `renders_preview/g64_m1100_live_2026-08-07.mp4` (08-08).

Date plus filename is strong but not conclusive. The definitive test is per-file
inspection of the generating script. Treat 6 as the working figure and 15 as refuted.
**[inferred, method stated so it can be re-run]**

---

## 4. Does the current public state violate E8?

**Yes, on E8's own operative wording, and by a wider margin than E8 contemplates.**

E8's rule: "do not commit any derived NCAC/CCSA geometry to the public repo, and do
not include it in a DesignSafe DOI, without written permission or a confirmed
licence."

- Derived geometry (2 `.ply` hulls, 6 renders) is committed to a public repo. Direct
  violation.
- Verbatim upstream material (160.32 MB) is committed to the same public repo. Not
  contemplated by E8's wording, and strictly harder to defend.
- Written permission: none exists. **[recalled: register item 11 lists establishing
  these rights as still open, and nothing in this session found a grant]**

Repository visibility verified live this session: `gh repo view` returns
`"visibility":"PUBLIC"` for `jcerrell-IS/can-it-ford`, with **0 forks and 0
stargazers**. [read]

The zero fork count is the one genuinely good fact in this document, and it is
perishable. It means no third party has yet taken a copy through GitHub's fork graph,
which is the mechanism that would put this permanently beyond reach.

---

## 5. Remediation options, with consequences

> **SUPERSEDED 2026-08-18. Do not execute any option below.** Permission has been
> obtained and it permits republication, so the no-permission case these options were
> written for no longer obtains. They are kept as a record of what was considered and
> why, which is useful if the scope of the permission is ever narrowed. **Nothing here
> is pending work.**

Ordered by increasing cost. **None has been executed, and none is now to be.**

**Option 0. Fix the LICENSE misstatement. (Independent of everything else.)**
Add a third-party notice excluding `vehicle_geometry_research/` from the BSD grant,
and reproduce the CCSA attribution the upstream README requests.
*Consequence:* stops the repo asserting copyright over, and sublicensing, CCSA
material. Does not reduce the redistribution itself.
*Cost:* one file. No history change. No coordination.
**This is strictly positive under every other option below, including "leave".**

**Option 1. Leave it, and seek permission.**
Email the three named CCSA contacts (they are published in the upstream README),
describe the use, request written redistribution permission.
*Consequence:* if granted, the entire item closes cleanly and E8 is resolved by the
only route that actually resolves it. If refused or unanswered, the exposure has been
knowingly continued, which is worse than the current position of not having asked.
*Cost:* one email, plus latency measured in weeks with no guaranteed reply.

**Option 2. Remove from HEAD, keep history.**
`git rm` the 22 upstream files, keep the 2 derived hulls or remove them too.
*Consequence:* the repo stops actively presenting the material on `main`. **It does
not unpublish it**, on two independent grounds now. First, GitHub has served removed
blobs by SHA after history rewrites in this very account. **[recalled from project
memory; the W&B key precedent]** Second, and this is the newer and larger point,
**the decks are on all 36 public branches** (re-measured 2026-08-19; 30 on 08-16,
35 on 08-18), so removing them from `main` leaves 35 branches still serving them. A `main`-only removal would look like remediation and
achieve close to none of it.
*Cost:* low, and the benefit is correspondingly low unless every branch is handled.
Breaks any script reading those paths (the hull is load-bearing: it is the canonical
mesh for all 17 gated runs).

**Option 3. History rewrite with `git filter-repo`, then force-push.**
*Consequence:* the only option that materially reduces public availability, and it
still does not guarantee removal, because GitHub retains unreferenced objects until
garbage collection and has served them by SHA regardless. Requires GitHub Support
contact to actually purge. Rewrites every SHA in the repo, which **invalidates every
commit SHA cited in the register, in CLAUDE.md and in the paper**, and this project
cites SHAs as primary provenance throughout.
*Cost:* high, and the collateral damage to provenance citations is severe and
irreversible. The `git-history-rewrite` skill exists and must be loaded first.

**Option 4. Remove the verbatim upstream material only, keep the derived hull.**
Delete the 4 `.zip`, 14 `.key` and 4 upstream `README.md` (22 files, 160.32 MB);
retain the 2 derived `.ply` and the renders.
*Consequence:* removes 91.0% of the exposure and the entire indefensible verbatim
portion, while keeping every artifact the project actually needs to run and to
reproduce. The derived-hull question stays open under option 1.
*Scope requirement, from the 30-branch finding:* this has to be applied **across all
36 branches**, or it is cosmetic. Most of the 35 non-`main` branches are finished or
abandoned work; the cheapest honest route is to delete the stale ones outright rather
than rewrite each, which is a decision about branch hygiene as much as licensing.
Enumerate them before acting: several are named in D3's branch taxonomy.

---

## 6. Recommendation

**Do option 0 now, then option 4, then option 1. Do not do option 3.**

Reasoning, stated so it can be argued with:

1. **Option 0 first** because it is free, is correct under every scenario, and
   removes the assertion of ownership that would most damage a permission request.
   Doing it before writing to CCSA also means the email describes a repo that already
   attributes them properly.
2. **Option 4 next** because the verbatim 160.32 MB is the part with no defence and
   no project need. The pipeline consumes the derived `.ply` hull, not the `.key`
   decks. Removing them costs the project nothing operationally and removes the
   overwhelming majority of the exposure. Anyone reproducing the work can download the
   decks from CCSA themselves, which is what the upstream expects.
3. **Option 1 last but genuinely** because it is the only path that closes E8 rather
   than shrinking it, and because the acknowledgement request in the README is a
   strong signal that CCSA's posture is academic-friendly. A group that asks only to
   be cited is not a group likely to refuse a research use. The request costs one
   email and the downside of asking is small.
4. **Not option 3**, because the provenance cost is certain and the benefit is not.
   Rewriting history invalidates the SHA citations this project's entire correctness
   argument rests on, in exchange for a removal GitHub does not actually guarantee.
   If CCSA refuses permission and demands takedown, revisit. Not before.

**Sequencing constraint:** option 4 deletes files. Per the standing rules that is a
destructive action requiring explicit confirmation, and it should not happen while
other sessions hold unpushed commits touching those paths. Check first.

---

## 7. What this document did not establish

Stated so the gaps are not read as covered.

- ~~Whether an NHTSA-hosted copy of this exact model exists.~~ **CLOSED 2026-08-17.**
  The CCSA pages were fetched: downloads are served from `media.ccsa.gmu.edu`, so these
  are CCSA-hosted and licence-silent. `nhtsa.gov` itself returned 403 to an automated
  fetch, so the narrower question of whether NHTSA hosts *some other* copy of *some
  other* Yaris model is still open, but it no longer bears on the artifacts in this
  repo, whose origin is now positively identified rather than inferred.
- ~~Whether the four `.zip` are byte-identical to the upstream releases.~~
  **CLOSED 2026-08-17, and it went the worse way.** All four match CCSA's published
  SHA384 exactly. **[read, computed locally and compared]** No longer inferred.
- **The 6-of-15 render classification** rests on commit date and filename, not on
  reading each generating script. Section 3.
- **The source point cloud behind `car_mesh.ply`.** "Likely a small tutorial demo
  asset" is the repo's own words, not an identification.
- **No legal advice is offered or implied.** This is a factual provenance record. The
  characterisations of 17 U.S.C. 105 and of BSD 3-Clause are the register's and the
  licence text's own, restated.
- **physics-skeptic was not run.** It is scoped to physical and structural claims;
  this document contains no percentage, force, verdict count or distance of that kind.
  The byte counts and file counts here are arithmetic over `git ls-tree` output and
  are reproducible with the command in section 0. **Mark this document UNREVIEWED by
  that agent, by scope rather than by omission.**
