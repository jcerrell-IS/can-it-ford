# `citations/` redistribution audit

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.
**Diagnosis only. Nothing deleted, nothing untracked, nothing pushed.**

Same discipline as the `vehicle_geometry_research/` audit in
`E8_GEOMETRY_REDISTRIBUTION_DECISION_2026-08-16.md`: per file, read live off
`origin/main`. Claims tagged **[read]**, **[recalled]**, **[inferred]**.

Scope note: D1 mines the **content** of these files. This assesses their
**redistribution status**. No overlap.

---

## 1. The finding

`citations/` **is tracked and public.** 38 files, **19,759,424 bytes (18.84 MB)** on
`origin/main`. There is **no `citations` rule in `.gitignore`**, so nothing was ever
intended to keep it out. [read]

**99.2% of it by bytes is third-party material**, not repo-authored work:

| Class | Bytes | MB | Files | Redistribution risk |
|---|---|---|---|---|
| Full-text publisher PDFs | 11,999,575 | 11.44 | 3 | **HIGH** |
| Screenshots of copyrighted figures and tables | 7,213,546 | 6.88 | 20 | **HIGH** |
| Elicit exports | 350,369 | 0.33 | 2 | Medium, terms-of-service not copyright |
| Third-party code, `(kks32)` | 30,170 | 0.03 | 2 | Low, provenance unrecorded |
| Repo-authored notes | 165,764 | 0.16 | 11 | None |
| **Total** | **19,759,424** | **18.84** | **38** | |

This is the same family of problem as the CCSA decks, and in one respect it is
**cleaner cut**: CCSA is licence-*silent*, which leaves a genuine open question,
whereas a subscription-journal PDF has an unambiguous copyright holder and an
unambiguous answer.

---

## 2. Full-text PDFs, per file

| File | Bytes | Source | Status |
|---|---|---|---|
| `Water Resources Research - 2021 - Wang and Marsooli - Physical Instability of Individuals Exposed to Storm-Induced Coastal Flooding.pdf` | 7,399,829 | AGU / Wiley | **Probably not OA. See probe below.** |
| `J Flood Risk Management - 2025 - Dasallas - Integration of Stability Functions Into a Transport Flood Risk Modelling.pdf` | 3,484,612 | Wiley | **Probably not OA. See probe below.** |
| `ARR_Project_10_Stage2_Report_Final.pdf` | 1,115,134 | Shand, Cox, Blacka & Smith (2011), AR&R Report P10/S2/020, Water Research Laboratory, UNSW | **UNDETERMINED, probe was blind** |

The first two filenames follow the **Wiley Online Library download convention**
(`Journal - Year - FirstAuthor - Title.pdf`), which is what a logged-in subscriber
download produces. **[inferred, from filename form]**

### The licence probe, and why it is valid for two files and void for the third

I scanned each PDF with `strings` for `creativecommons.org/licenses/...`, `CC BY`,
"open access article", and copyright lines. **All three returned zero matches.**

That negative is worthless without a control, because PDF text is usually inside
compressed streams that `strings` cannot read. So I ran one: count any `http(s)://`
URL and any Wiley/DOI marker in each file.

| File | URLs visible | Wiley/DOI markers | Probe verdict |
|---|---|---|---|
| Wang and Marsooli 2021 | **413** | 3 | **Valid.** A CC licence URL would very likely have appeared. Absence is real evidence. |
| Dasallas 2025 | **199** | 3 | **Valid.** Same reasoning. |
| ARR Project 10 | **0** | 0 | **BLIND. The negative for this file is void and is withdrawn.** |

So: for the two Wiley PDFs, "no CC licence marker" is meaningful evidence they are
not open-access. For the AR&R report the probe saw nothing at all, so it establishes
nothing either way. **[read]**

**Neither result is a licence determination.** The decisive check is each DOI's
open-access status at the publisher, which was not performed this session (no
DOI-resolution tool was invoked). Two of the three DOIs are already recorded in
`citations/README.md`; the WRR one is not. **This is the single cheapest open item in
this document.**

Note in AR&R's favour: it is a publicly funded Australian government engineering
guideline programme, and such reports are often freely distributable. But
`~/can-it-ford` memory records that `arr.ga.gov.au` returns 403 and that the
obtainable mirror is a different report, so its terms have not actually been read.
**[recalled]** Do not assume "government report" means "redistributable".

---

## 3. Screenshots, 20 files, 6.88 MB

This is the class most likely to be overlooked, because a `.png` does not look like a
copy of a paper. Every one of these reproduces third-party expression verbatim.

| Group | Files | Bytes | What it is |
|---|---|---|---|
| `Smith-Modra-Felder/Screenshot 2026-07-03 at 3.15-3.16 PM.png` | 14 | 5,428,911 | Screen captures taken in one 50-second burst, so a page-by-page capture of a single document **[inferred, from the timestamps]** |
| `Smith-Modra-Felder/smith2019_instability_table.png` | 1 | 369,463 | A table from the same paper |
| `WRL reports technical and Research/` Figure 5-5, Table 5-1, Table 5-2 | 3 | 760,715 | Figures and tables from a Water Research Laboratory, UNSW report |
| `ARR table 1 - guidelines and recommendations for limits for vehicle stability.png` | 1 | 237,832 | A table reproduced from AR&R |

`citations/README.md` identifies the Smith-Modra-Felder source as Smith, G., Modra, B.,
& Felder, S. (2019), *Journal of Flood Risk Management*, **DOI 10.1111/jfr3.12527**,
and says "Source in `citations/Smith-Modra-Felder/`". [read]

**That DOI is worth checking first, because it may dissolve this whole group.** JFRM
publishes open-access articles under CC BY, and the project's own skill file records a
sibling JFRM paper, Azhar, Pauwels and Bui 2023, DOI 10.1111/jfr3.12885, explicitly as
"**open access**". **[read, from
`vehicle_geometry_research/flood-mpm-debugging-reference_SKILL_v3_friction_corrected.md:58`]**
If Smith 2019 is likewise CC BY, then the 15 Smith-Modra-Felder files are fine to
redistribute **with attribution**, and 5.80 MB of the 6.88 MB problem disappears. If it
is not, they are 15 verbatim reproductions of a paywalled paper.

**One DOI lookup decides the largest single group here.** Do that before any removal.

The AR&R and WRL images do not have that escape route available as cheaply, since
their source terms have not been read.

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

Ordered, and deliberately cheap-first, because three lookups may shrink the problem
before anything is removed.

1. **Resolve four DOIs.** Smith 2019 `10.1111/jfr3.12527` first, since it governs 15
   of the 20 screenshots. Then Dasallas 2025, Wang and Marsooli 2021, and the AR&R
   report's terms. Anything CC BY is **keep, with attribution added**.
2. **For whatever is confirmed not open-access: untrack, do not delete.** These are
   the working sources for the paper and Josie needs them locally. `git rm --cached`
   plus a `.gitignore` rule keeps the files on disk and removes them from future
   commits. It does **not** unpublish what is already public, for the same reason
   given in the geometry document.
3. **Replace each removed PDF with its citation and DOI**, which `citations/README.md`
   already does well for most entries and is the correct long-term pattern: cite, do
   not carry.
4. **Move the two `(kks32)` files** under `third_party/` with `VENDORED.md`.
5. **Add `citations/` to the notices file** once 1 is done.

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
