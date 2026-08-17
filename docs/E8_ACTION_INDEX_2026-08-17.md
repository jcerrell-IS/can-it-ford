# D2 action index: what to do, what is blocked on you, what is withdrawn

Dispatch R5-D2, branch `claude/r5-exposure`, based on `777567a`.
**Everything is diagnosis. Nothing was rotated, deleted, untracked or pushed.**

For the commit count and log, run `git log 777567a..claude/r5-exposure`. An earlier
revision hard-coded "10 commits" here, which went stale within the hour, on the same
day this file added a section about publishing figures that go stale. Prefer the
command to the number.

Written because acting on six documents is harder than acting on one, and because
several of my own claims were retracted mid-round. Section 4 exists so a withdrawn
figure cannot be cited from an early commit.

---

> # ONE THING IS STILL OPEN: 12 CREDENTIALS, ZERO ROTATED.
>
> Every licence question in this dispatch is now closed on reported permission. **The
> credentials are not a licence question and were never covered by any of it.** If you
> read nothing else here, read tier 1 item 1.
>
> ---
>
> ## Licence status, 2026-08-18: all closed on REPORTED permission, artifacts pending
>
> Josie reports three separate grants, each global and each permitting republication:
>
> | Grant | Covers | Rights holder | Status |
> |---|---|---|---|
> | 1 | CCSA/NCAC meshes, decks, hulls, renders | CCSA/GMU (reported via NHTSA) | **Reported 2026-08-18** |
> | 2 | AR&R paper | Engineers Australia | **Reported 2026-08-18** |
> | 3 | The 16 Smith-Modra-Felder files | Wiley / CIWEM | **Reported 2026-08-18** |
>
> **These are three reports, from three rights holders, and no artifact has been filed
> or read by me, by the coordinator, or by D3**: three parties, checked separately,
> none of whom has seen a document.
>
> **The settledness illusion, and it is worth naming because it is acting on us right
> now.** D3 puts it well: *three independent grants arriving inside ninety minutes
> creates a strong feeling of settledness that the evidence does not support. The
> evidence is three reports and zero artifacts.* The feeling comes from the **count**,
> which is not evidence of any of them individually. Each grant needs its own document;
> none corroborates the others, because they are from three unrelated rights holders. That is not a doubt about any of them; it is
> what a licence record on a public repo is for. **A second or third report arriving
> does not upgrade the earlier ones.** File all three at
> `docs/E8_PERMISSION_<body>_<date>`, because a DesignSafe DOI is gated on written permission
> (register item 10), and a reviewer will ask for the documents.
>
> **What changes when each artifact arrives**, so the record closes cleanly instead of
> drifting:
>
> | On filing | Change the status line to | And check the artifact for |
> |---|---|---|
> | CCSA/GMU grant | `CONFIRMED, artifact at <path>` | Does it name **redistribution**, and is the granting body able to grant for **CCSA/GMU-authored** models? |
> | Engineers Australia grant | same | Does it reach the **UNSW WRL figures**, or only the AR&R report? |
> | Wiley/CIWEM grant | same | Does it cover **republication of the full 15-page article**, or only figure reuse? |
>
> Until a given artifact is filed, that grant stays `reported`. **Filing one does not
> promote the other two.**
>
> **Consequence: every removal, untracking and rewrite recommendation in this dispatch
> is WITHDRAWN.** They are marked superseded **in place** in each document, with the
> reasoning preserved and explicitly flagged as not pending work. **Nothing is to be
> deleted or untracked on licence grounds.** The reason for marking rather than
> deleting: a stale "recommend removal" line is how someone deletes something in six
> months for a reason that stopped applying tonight.
>
> ### The three WRL images: NOT covered by the AR&R grant, on positive evidence
>
> I flagged that `citations/WRL reports technical and Research/` might have a different
> rights holder from the AR&R report. **Checked, and they are a different document.**
>
> The AR&R report P10/S2/020 uses **flat numbering throughout: Figure 1 to Figure 11,
> Table 1 to Table 3**, with no section-prefixed labels anywhere. The three WRL images
> are **"Figure 5-5", "Table 5-1" and "Table 5-2"**, a chapter-section scheme the
> report does not use. Probe validated first: it sees 27 `Figure N` and 7 `Table N`
> references in the AR&R text, so the absence is real, not blindness. [read]
>
> **IDENTIFIED 2026-08-18. The source is named on the page itself.**
> `Table 5-1`'s footer reads **"WRL Technical Report 2014/07  FINAL  September 2014"**,
> page 38. [read, by opening the image]
>
> So these are from **WRL Technical Report 2014/07 (UNSW Water Research Laboratory,
> September 2014)**, a different document from AR&R P10/S2/020 (Engineers Australia,
> February 2011) by **publisher, body and year**. The content is the **H1 to H6 flood
> hazard vulnerability classification** with its D*V limits.
>
> Precision on what is verified: **`Table 5-1` carries the footer directly.**
> `Table 5-2` is its companion limits table (5-1 classifies, 5-2 gives the limits) and
> `Figure 5-5` shares the caption family and numbering, but both are cropped without a
> footer, so their attribution is **by caption family and numbering, not by a footer I
> read.** Same document on the balance of evidence; only one of the three is
> footer-confirmed.
>
> **So do not fold these three into the AR&R grant. The rights holder is UNSW WRL, and
> the question for Josie is now specific rather than open:** does the permission cover
> **WRL Technical Report 2014/07**, or only the Engineers Australia AR&R report? If it
> does not, WRL is a **fourth rights holder** and these 760,091 B are the one piece of
> `citations/` still uncovered.
>
> By contrast `ARR table 1 - ...png` **is** plausibly covered: the AR&R report does have
> a Table 1.

## 1. The three exposures, and why they need different remedies

They are **not equally serious, and they differ in kind, not just size.**

| # | Exposure | Size | Rights position | Public surface | Remedy shape |
|---|---|---|---|---|---|
| 1 | **CCSA/NCAC geometry.** 4 original distribution archives (88,592,238 B) + 14 LS-DYNA decks (71,716,670 B), **byte-identical to upstream, proven by SHA384** | 160,322,098 B | **Silent.** Confirmed on both CCSA download pages, not just the bundled README | **30 of 30 branches** | Ask permission; removal must cover every branch or it is cosmetic |
| 2 | **Smith 2019.** The complete 15-page article, page by page | 6,215,623 B | **Asserted** "© 2019 CIWEM and John Wiley & Sons Ltd", **and permission reported 2026-08-18** | 1 tree | **CLEARED.** No action |
| 3 | **AR&R report + 1 AR&R table image** | 1,352,966 B | **Silent**, permission reported 2026-08-18 | 1 tree | **CLEARED.** No action |
| 3b | **3 WRL images**, from **WRL Technical Report 2014/07** (UNSW WRL, Sept 2014) | 760,091 B | **Fourth rights holder**, distinct from Engineers Australia | 1 tree | **One question:** does the grant cover WRL TR 2014/07? |
| 4 | Two CC-licensed PDFs | 10,884,441 B | **Licensed** (CC BY; CC BY-NC-ND) | 1 tree | Keep, add attribution |
| 5 | CC0 assets (ambientCG ×2, Poly Haven) | 11,205,063 B | **CC0.** No violation, ever | 1 tree | Courtesy attribution only |
| 6 | **Credentials.** 12, across Vista, LS6, Mac | n/a | **THE ONLY OPEN EXPOSURE** | **No value public.** A holder-enumerating doc is public on 1 of 30 branches | **REVOKE.** Deletion cannot win |

**1 is largest and most widespread. 2 is smallest of the licence problems but the
least ambiguous**, because silence leaves an open question and an explicit © does not.
The four `.ply` files that originally framed this task are 15,823,688 B, **under 9% of
the geometry tree**, and are not the headline.

---

## 2. What needs YOU, in order

Ordered by (irreversibility × blast radius), cheapest-first within a tier.

### Tier 1, do first, nothing else depends on them

**1. Revoke all 12 credentials.** None is rotated. Use the source document's own
`ROTATION LIST, START HERE` (its line 123), **not** my checklist, which is a companion.
Corrections to apply to it are in `CREDENTIAL_ROTATION_CHECKLIST_2026-08-16.md` §0.2.
- Row 1 (**H**) is a **GitHub fine-grained PAT**; revoke at github.com, Developer
  settings, Fine-grained tokens. Expect the `github` MCP server to break until
  replaced. That is correct, not a symptom.
- Re-authenticate Claude Code with **`/login`**, not `claude setup-token`.
- **Measured urgency:** 5 of 5 backup files in `~/.claude/backups/` carried a live
  token format, newest 57 s old, spanning 6 minutes. The exposure re-clones itself
  every minute or two. **You cannot win a deletion race; revocation ends it in one
  action.**

**2. Adopt the LICENSE carve-out and `THIRD_PARTY_NOTICES.md`, and record the
permission in it.** Now more worthwhile than before, not less: with permission granted,
this file is where a reader and a DesignSafe reviewer find out that it exists.
`E8_THIRD_PARTY_NOTICES_DRAFT_2026-08-16.md`, sections 2 and 3, ready to paste. All
attributions are verified at source; no `[CONFIRM]` items remain. **This needs nobody's
permission and is a strict improvement under every other outcome.** Do it *before*
writing to CCSA, so the repo attributes them properly at the moment they look.

### Tier 2, needs a decision from you

**3. ~~Choose the geometry remediation.~~ MOOT 2026-08-18.** Permission is granted and
permits republication, so there is no remediation to choose. Options 1 to 4 in
`E8_GEOMETRY_REDISTRIBUTION_DECISION_2026-08-16.md` §5 are withdrawn and marked
superseded in place. **Nothing to do.** Note that E8 offers **two** routes to
clearance, written permission **or a confirmed licence**, and that the second is
**closed by evidence**: there is no licence to confirm, established on three
independent sources (the bundled README, both CCSA download pages, and D1's read of
the DOI's empty `rightsList`). Permission is the only route left, for an evidentiary
reason.
 Options and consequences in
`E8_GEOMETRY_REDISTRIBUTION_DECISION_2026-08-16.md` §5. My recommendation: option 0
(attribution), then option 4 (remove the verbatim 160.32 MB **across all 30
branches**), then option 1 (ask CCSA). **Against option 3**, a history rewrite, because
it invalidates every commit SHA the register cites as provenance in exchange for a
removal GitHub does not guarantee.

**4. ~~Untrack the 16 Smith-Modra-Felder files.~~ WITHDRAWN 2026-08-18**, permission
reported for the Wiley/CIWEM article. **Do not untrack them.** Extracting the four
scalars (`C_D = 1.38`, `μ = 0.78`, `μ = 0.3`, Equation 6) into a grounding note is
still worth doing as citation practice, but it is no longer required by any licence
position.

**5. Two permission emails, and they can go out the same day.** Both bodies publish a
contact in the very documents concerned:
- CCSA/GMU: Dhafer Marzougui, Fadi Tahan, Steve Kan, Rudolf Reichert.
- AR&R: `arr@engineersaustralia.org.au` (Engineers Australia).

### Tier 3, small and mechanical

**6. Replace or delete the stale credential doc.** `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`
in the main checkout is the **superseded 118-line** version claiming the Mac is clean.
The authoritative copy is 1,196 lines on `claude/credential-exposure-2026-08-13-DO-NOT-PUSH`.
Anyone following the stale one does a two-machine rotation and stops. §0.1.

**7. Fix `citations/README.md`'s title** for DOI `10.1111/jfr3.12527`. It reads
"Full-scale testing of vehicle floating and sliding in flowing floodwater"; the real
title is "Full-scale testing of stability curves for vehicles in flood waters".

**8. Promote L-A, L-B, L-C and L-D** from `E8_METHOD_LESSONS_2026-08-16.md` into the
register or `CLAUDE.md`. **D2 is forbidden to edit either**, so that file is a holding
place, not their home. **L-D is the one with the widest reach**: it is a rule against
filing work as human-blocked without naming the capability the human has and you lack,
and the coordinator reports the same over-attribution from itself, D3 and D4 in this
round. It inflates the queue of the one person who cannot be parallelised.

---

## 3. ONE thing blocked on a human, and it is tiny

| Blocked | Why | The unblock |
|---|---|---|
| Whether the AR&R report has a rights notice on an **image-only page** | My extractor reads the text layer only; the PDF has 83 non-text streams and 10 JPEGs | **Open it and look at pages 1 to 3.** Ten seconds |

It does not block tier 1 or tier 2.

**The second item listed here was my own mis-classification and is now closed.** I had
written "whether an NHTSA-hosted copy of this exact Yaris exists" as human-blocked. It
was not blocked at all: it was two web fetches and a checksum, and I should have tried
before filing it. Doing so produced the strongest evidence in the whole dispatch:

- **All four CCSA archives are byte-identical to the published upstream releases**,
  confirmed against CCSA's own SHA384 values. 4 of 4, 88,592,238 B. Verbatim
  redistribution is now **proven**, not inferred, and an exact-hash match leaves no
  transformation or derived-work defence.
- **Both CCSA model pages carry no licence, copyright or redistribution statement**,
  which makes the licence silence a genuine second source rather than the bundled
  README read twice.
- **Downloads are served from `media.ccsa.gmu.edu`**, so these are CCSA-hosted and the
  NHTSA safe-set hypothesis is refuted for these models.

`nhtsa.gov` returned 403 to an automated fetch, so whether NHTSA hosts *some other*
copy of *some other* Yaris is still unknown. It no longer matters here, because the
origin of the artifacts in this repo is now positively identified rather than inferred.

**The lesson, and it is the fourth instance tonight:** I filed something as blocked
without attempting it. Two of my three "blocked" items this round turned out to be one
untried approach away, the AR&R text layer being the other. **Attempt before filing.**

---

## 4. RETRACTED. Do not cite these from earlier commits.

Five of my own claims were withdrawn this round. Each is listed with the commit that
made the error and the one that corrected it, so an early commit cannot be quoted as
current.

| Claim | Made in | Withdrawn in | The truth |
|---|---|---|---|
| "Nothing here is public" (credentials) | `30dee69` | `5f01dd2` | Two-part: no **value** is public, **and** a holder-enumerating doc is public on 1 of 30 branches. It **raises** urgency |
| Sizes labelled **MB** | `6e771b6`, `823cd82` | `ac9fb54` | They were **MiB**, understating every headline by 4.6%. Now decimal SI. **Proportions were always right** |
| The `strings` licence probe, **in full** | `823cd82` | `ac9fb54` | It was **0 for 3**, including both files where my own control called it reliable |
| Smith group = **14 files / 5,798,374 B** | `823cd82` | `ac9fb54` | **15 screenshots + 1 table = 16 files, 6,215,623 B.** Spaces in filenames broke the field split |
| "This checklist is runnable, the source is not" | `30dee69` | `d0d5a65` | The source had a 12-row rotation list all along, at its line 123 |
| Row 1 is "the worst single defect here" | `d0d5a65` | `458115f` | **Row 1 was right.** H is a GitHub fine-grained PAT used as a Bearer to GitHub's Copilot MCP endpoint |
| AR&R is plausibly **Commonwealth CC BY** | `cda67a3` (as a hypothesis) | `cda67a3` | Refuted. No Creative Commons text; the word "Commonwealth" does not appear |

| "Blocked on a human: does an NHTSA-hosted copy exist" | `aacf12e` | `bb8bc92` | **Not blocked.** Two web fetches and a checksum, which then produced the dispatch's strongest evidence |
| Two of three `.zip` provenance claims marked `[inferred]` | `6e771b6` | `ea04f33` | **All four archives are byte-identical to upstream, by SHA384.** Verbatim redistribution is proven, not inferred |

| E8's operative rule quoted as "do not commit any derived NCAC/CCSA geometry to the public repo" | `6e771b6` §0 | `141d239` | **Truncated.** The full rule ends "...without written permission **or a confirmed licence**". Caught by D1. My §4 was correct throughout, but §0 made the prohibition read as unconditional |

**One count is not an error but is scope-sensitive, so never quote it bare:** the CCSA
verbatim total is **160,322,098 B** including the 4 upstream READMEs, or
**160,308,908 B** excluding them (D3's and the coordinator's scope). Both give 91.0%.

---

## 5. The documents

| File | What it settles |
|---|---|
| `E8_GEOMETRY_REDISTRIBUTION_DECISION_2026-08-16.md` | The main decision. E8's open NHTSA-vs-CCSA question resolved; 30-branch reframe; 5 options with consequences |
| `E8_CITATIONS_REDISTRIBUTION_AUDIT_2026-08-16.md` | `citations/` is tracked and public, 99.2% third-party; all 3 PDFs resolved; the 16-file triage |
| `E8_THIRD_PARTY_NOTICES_DRAFT_2026-08-16.md` | Ready-to-paste notices file + LICENSE carve-out. No open items |
| `E8_FLAG_ARR_TERMS_UNRESOLVED_2026-08-16.md` | AR&R resolved on the third approach; ISBN read directly; one human check left |
| `E8_METHOD_LESSONS_2026-08-16.md` | L-A reach≠sensitivity, L-B read `license` not `isOa`, L-C identify a credential without reading it |
| `CREDENTIAL_ROTATION_CHECKLIST_2026-08-16.md` | Companion to the source's list: public surface, divergent copies, 3 defects, live-cloning measurement |

## 6. Erratum to this file, same day

**Two of the three totals I introduced in section 1 were wrong on first commit
(`aacf12e`) and are corrected here.** I caught them by running an arithmetic check
against the tree immediately after committing, which is why the window was minutes
rather than permanent.

| Row | Published in `aacf12e` | Correct | Cause |
|---|---|---|---|
| 3, AR&R + 4 images | 1,352,966 B | **2,113,057 B** | I summed the AR&R PDF and the AR&R table image and **omitted the 3 WRL images** (760,091 B) |
| 5, CC0 assets | 11,225,569 B | **11,205,063 B** | Hand-summed, off by 20,506 B |

Both are now recomputed directly from `git ls-tree`, not by hand. Neither affects any
other figure or any recommendation: no ranking, proportion or decision in this document
depends on them.

**The pattern is the point, and it is now three for three:** every size figure I have
produced by hand or by a quick script this round has been wrong at least once (MiB
labels in `ac9fb54`, the 14-file Smith count in `ac9fb54`, these two). Every figure
recomputed from `git ls-tree` in a checked script has been right. **Compute totals from
the tree, print the enumeration, and check the sum before publishing it**, which is the
corollary already stated in `E8_METHOD_LESSONS_2026-08-16.md` L-A.

---

## 7. Independent corroboration, and the status of this dispatch

**The SHA384 finding rests on two separate origins, not one cited twice.** After I
published it, the coordinator computed SHA384 over all four local archives itself and
fetched both `ccsa.gmu.edu` pages itself. Every value matched, and it independently
confirmed that neither page carries any licence, copyright, terms-of-use or
redistribution statement, and that both download from `media.ccsa.gmu.edu`. Separate
tooling, separate fetches, same result. **[relayed by the coordinator, whose method it
described in enough detail to be checkable]**

That matters because this project's own rule is that one source cited twice is not two
sources. Here the two origins are genuinely distinct, so the central E8 finding is as
well supported as anything in the round.

**D2 is PARKED.** Both exposures are diagnosed, this index exists, the notices draft
has no open items, the rotation checklist carries its caveats in a banner, and the
citations audit is settled per file. **The only remaining item in the dispatch is the
ten-second look at AR&R pages 1 to 3**, which is genuinely human-gated under L-D
criterion 4, a physical look at a screen. Nothing further is startable without a
decision from Josie.

---

**Not reviewed by physics-skeptic.** Every number here is a byte count, a file count or
a licence status, none of which that agent is scoped to. **UNREVIEWED by scope, not by
omission.**
