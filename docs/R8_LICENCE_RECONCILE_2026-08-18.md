# Licence reconciliation, R8 slot d10-licence, 2026-08-18

Author: Claude Code session d10-licence, branch `claude/r8-licence`.
Every figure and quotation below was read live from a primary artefact on this date. Where a
claim could not be settled against a primary source it is marked **UNRESOLVED** and the routes
tried are named. Nothing in this document was carried from a prior summary, a register entry, or
another session's claim.

Repository state at time of measurement: `origin/main` at `c7f0a16`.

---

## 0. Summary for someone with two minutes

1. The upstream vehicle meshes carry **no licence and no redistribution grant**. They carry one
   explicit obligation: acknowledge CCSA at GMU and the FHWA in publications. That obligation is
   currently **unmet**. Section 2 has the sentence ready to paste.
2. **168.09 and 176 are the same number.** See section 3 before anyone re-opens this.
3. The root `LICENSE` claims BSD-3 over the entire repository, including third-party material the
   project does not own. Section 6 drafts a scope carve-out. **It awaits Josie's sign-off.**
4. `citations/` publishes a **CC BY-NC-ND** article and 16 screen captures of a **closed-access**
   article, under that same unrestricted BSD-3 claim. Section 7.
5. `bridge/` was checked for redistributed PhysGaussian source. **It is clean, measured, not
   judged.** Section 8.
6. One question is blocked on Krishna Kumar and is written out, not resolved, in section 9.

---

## 1. Method, and what would falsify each claim

| Claim type | How it was established | What would falsify it |
|---|---|---|
| Upstream terms | Full read of all four upstream `README.md` files on disk | A licence file inside any upstream archive |
| Byte totals | `git ls-tree -r -l origin/main`, summed with awk | A different commit, or a different path scope |
| Declaration sites | `git ls-tree` name scan plus `git show` of each candidate | A declaration in an untracked or ignored file |
| Article licences | Unpaywall via `scholar-sidekick checkOpenAccess`, per DOI | The publisher landing page disagreeing with Unpaywall |
| `bridge/` derivation | Token and line diff against fetched upstream source | A match against an upstream file not compared |

**Scope statement, which every count below is relative to and without which no count means
anything:** tracked files on `origin/main` at `c7f0a16`; declaration sites only, not prose
mentions; untracked and gitignored paths excluded. This project has already had one count move
three times in a day for want of a stated scope (CLAUDE.md August 4 audit, item 13). A bare
number is the defect, not any particular value.

---

## 2. The one explicit obligation anybody has quoted, and it is unmet

**Source, read directly, 2026-08-18:**
`vehicle_geometry_research/2010-toyota-yaris-coarse-v1l/2010-toyota-yaris-coarse-v1l/README.md`,
lines 14 to 20 of 78, 3,324 bytes. This is the README shipped inside the upstream archive for the
canonical hull.

> Users of the model must verify their own simulations. Neither CCSA or FHWA
> assume any responsibility for the validity, accuracy, or applicability of
> results obtained from this model.
>
> We ask that the CCSA at GMU and the FHWA be acknowledged for any use of this FE
> model resulting in papers and publications.

Attribution context, same file, lines 4 to 7:

> The Toyota Yaris finite element (FE) model was developed by [Center for
> Collision Safety and Analysis][CCSA] researchers at George Mason University. The
> effort was sponsored by the Federal Highway Administration.

**The paragraph is uniform across all four upstream models**, verified by reading each:
Yaris coarse v1l, Yaris detailed v2j, Silverado coarse v3a, Silverado detailed v3e. The only
variation is the vehicle name and the version string.

**What is NOT in any of them.** A `/usr/bin/grep -r -i -E "licen|distribut|copyright|public
domain|permission|all rights|redistribut"` across all four READMEs returns **zero hits**.
`find` for any `*licen*` or `*copying*` file across the four extracted trees returns nothing,
and `unzip -l` on each of the four archives finds no licence file inside any of them. There is no
licence, no copyright notice, no redistribution grant, and no public-domain statement anywhere in
the upstream material as shipped.

This is the primary-artefact confirmation of register E8. E8 was previously established through
research reports about the CCSA website. It is now confirmed from the material itself.

**Silence is not permission.** The absence of a prohibition is not a grant. The only thing the
upstream authors did state is what they ask for, and that ask is cheap and currently unhonoured.

### THE ACKNOWLEDGEMENT, READY TO PASTE

**For d5-priorart, owner of `paper/` on `claude/r8-priorart`.** This slot did not write into
`paper/`. Drop this into the paper's acknowledgements section. It is the one obligation the
upstream README actually states.

> The 2010 Toyota Yaris finite element model used in this work was developed by researchers at
> the Center for Collision Safety and Analysis (CCSA) at George Mason University, under
> sponsorship of the Federal Highway Administration (FHWA). We acknowledge CCSA at GMU and the
> FHWA, as requested by the model distributors. Neither CCSA nor FHWA assumes any responsibility
> for the validity, accuracy, or applicability of the results presented here.

If any Silverado-derived result is reported, replace the first sentence with:

> The 2010 Toyota Yaris and 2007 Chevrolet Silverado finite element models used in this work were
> developed by researchers at the Center for Collision Safety and Analysis (CCSA) at George Mason
> University, under sponsorship of the Federal Highway Administration (FHWA).

The second sentence of the drafted text discharges the acknowledgement request. The third
reproduces the upstream disclaimer, which the upstream README states but does not require be
reprinted; it is included because it is true and because reprinting it costs one line.

Companion citation for the validation record, which the upstream README itself points to:
DOI `10.13021/G8JS5D`. Note the standing caveat in register E8 that this DOI has an empty
`rightsList` and was minted on a validation presentation rather than a data deposit, so citing it
is attribution, not evidence of a licence.

---

## 3. What is public, re-derived, and why two different numbers are not a contradiction

Measured live, `git ls-tree -r -l origin/main -- vehicle_geometry_research/` at `c7f0a16`:

```
files                 30
bytes        176,252,809
```

**176,252,809 bytes is 168.09 MiB and 176.25 MB. These are the same measurement in two units.**
`176252809 / 1048576 = 168.088`, and `176252809 / 1000000 = 176.25`. Earlier notes recorded
"176 MB" in one place and "168.09 MB" in another, which reads as a disagreement to anyone meeting
it later, and it is not one. There was never anything to adjudicate. This paragraph exists so
that the apparent conflict is not re-opened a third time. **State the byte count when it matters.**

Split by origin:

| Class | Files | Bytes | MiB | Share |
|---|---|---|---|---|
| Verbatim upstream (4 archives plus their extracted `.key` and `README.md`) | 22 | 160,322,098 | 152.90 | **91.0 percent** |
| Project-derived and project-authored | 8 | 15,930,711 | 15.19 | 9.0 percent |
| **Total** | **30** | **176,252,809** | **168.09** | 100 percent |

`160322098 / 176252809 = 0.9096`.

All four original upstream archives are tracked and public: `2010-toyota-yaris-coarse-v1l.zip`,
`2010-toyota-yaris-detailed-v2j.zip`, `2007-chevrolet-silverado-coarse-v3a.zip`,
`2007-chevrolet-silverado-detailed-v3e.zip`.

### Correction to the memory index, stated with both numbers

A standing memory note records the public exposure as "4 .ply including the canonical 12.4 MB
Yaris hull, plus 15 renders", that is, as **derived geometry**. That description is not wrong
about the `.ply` files, and the derived hull is indeed public. It is **incomplete in a way that
understates the problem by an order of magnitude**:

- derived and project-authored content is **9.0 percent** of the bytes (15,930,711),
- **91.0 percent** is **verbatim upstream content** (160,322,098).

The exposure is not primarily "we published a hull we derived". It is "we published the upstream
distribution". Both numbers are recorded here so the correction can be checked rather than
believed. **Deleting the derived hull would address 7.1 percent of the byte total** (the
12,445,769-byte `yaris_coarse_v1l_watertight.ply`) and would leave the verbatim upstream material
untouched. That is one reason removal is not the remedy. The other is that deletion does not
unpublish: this repository is public and GitHub has served removed blobs by SHA in this account.

### Duplication worth recording

`vehicle_geometry_research/2010-toyota-yaris-coarse-v1l/2010-toyota-yaris-coarse-v1l/yaris-coarse-v1l.key`,
42,846,753 bytes, is the single largest verbatim upstream artefact in the repository. It is public
**twice**: once as that extracted file, and once again inside
`vehicle_geometry_research/2010-toyota-yaris-coarse-v1l.zip` (11,228,299 bytes compressed). The
same is true structurally for the Silverado coarse deck. This is recorded in
`THIRD_PARTY_NOTICES.md` beside the file itself. It is noted as a fact about the current state,
not as a proposal to delete either copy.

---

## 4. Licence declarations: six sites, three assertions

**Previously recorded as "four mutually inconsistent declarations". That was a site count
presented as an assertion count, and two of the four were the same file.** `CITATION.cff` and
`citations/CITATION.cff` are the identical blob `b17c8a629170de53b9377479c51cb4314e7d2353`,
verified by `git ls-tree`. One declaration at two paths is one declaration.

Scope as stated in section 1. Verbatim quotations, each read via `git show origin/main:<path>`.

| # | Path | Verbatim | Asserts |
|---|---|---|---|
| 1 | `LICENSE` | `BSD 3-Clause License` / `Copyright (c) 2026, Josie Cerrell` | BSD-3 over everything, no scope limit |
| 2 | `CITATION.cff` | `license: ODC-By-1.0`, `type: dataset` | ODC-By-1.0 |
| 3 | `citations/CITATION.cff` | identical blob to #2 | ODC-By-1.0 |
| 4 | `README.md:163-165` | "Code is released under the **[BSD 3-Clause License](LICENSE)** ... The associated dataset is released under ODC-By-1.0" | split: code BSD-3, data ODC-By |
| 5 | `designsafe-staging/docs/README_designsafe.md:6` | "**License:** Open Data Commons Attribution License (ODC-By 1.0)" | ODC-By-1.0 |
| 6 | `hf_space/README.md` front matter | `license: bsd-3-clause` | BSD-3 |

**Six sites. Three distinct assertions:** BSD-3 (sites 1, 6), ODC-By-1.0 (sites 2, 3, 5), and the
code/data split (site 4).

### Which governs

**Site 4, `README.md:163-165`, is the only site that reconciles the other five**, and it is the
intended reading: BSD-3 for the code, ODC-By-1.0 for the dataset. Sites 1 and 6 are the code half
stated without its qualifier; sites 2, 3 and 5 are the data half stated without its qualifier.
Read that way the six sites are not in conflict with each other.

**They are all in conflict with something else: none of them carves out third-party material.**
The governing instrument for redistribution purposes is `LICENSE`, because that is the file a
downstream user and GitHub's own licence detection both read, and `LICENSE` states BSD-3 with no
scope limit at all. A README sentence does not narrow a licence file.

One precision, because the stronger version of this claim is falsifiable by a single grep: it is
**not** true that the repository contains no scope statement anywhere. `README.md:163-165` does
distinguish code from dataset. What no site does is carve out **third-party** content. That is the
defect, and section 6 addresses it.

---

## 5. Why the current state is the risky one

`LICENSE` says, verbatim:

> Copyright (c) 2026, Josie Cerrell
>
> Redistribution and use in source and binary forms, with or without
> modification, are permitted provided that the following conditions are met:

Applied without a scope limit to a repository that is 91.0 percent verbatim third-party content,
this asserts Josie's copyright over, and grants the world BSD-3 rights in:

- CCSA/GMU FE models sponsored by FHWA, which carry no licence at all (section 2),
- a CC BY-NC-ND journal article, whose licence forbids commercial use and derivatives (section 7),
- 16 screen captures of a closed-access, all-rights-reserved journal article (section 7),
- two MIT-licensed source files whose own headers name a different copyright holder (section 7).

BSD-3 permits commercial use, modification and sublicensing. For every item above, the project
does not hold the rights it is purporting to grant. **This is a broader claim than any of the
underlying licences allow, and it is made in the project's own name.** An imperfect carve-out is
strictly better than this.

---

## 6. Drafted `LICENSE` carve-out. AWAITING JOSIE'S SIGN-OFF

**Josie decides the final wording. This slot is drafting, not deciding. The edit below is applied in branch `claude/r8-licence` and is NOT pushed; it reaches nobody until she signs off and it is merged.** The change is additive:
**not one character of the existing BSD-3 text is altered, reordered, or removed.** The 28 lines of
BSD-3 remain byte-identical; a scope header is added above them and a notices pointer below.

### Before, in plain terms

The file contains exactly one thing: the BSD-3 licence text, opening with
`BSD 3-Clause License`, then `Copyright (c) 2026, Josie Cerrell`, then the three conditions and
the warranty disclaimer. Nothing states what the licence covers. By default, it reads as covering
the whole repository.

### After, in plain terms

The same BSD-3 text, unchanged, preceded by a short paragraph saying it applies to the code and
documentation Josie wrote, and does not apply to third-party material, which keeps its own terms
and is listed in `THIRD_PARTY_NOTICES.md`.

### The exact diff, readable without knowing git

The change is **14 lines added, 0 lines removed**, confirmed by `git diff --numstat -- LICENSE` returning `14 0 LICENSE`. The original file is 28 lines and all 28 survive unchanged; `git diff` shows no `-` line at all.

Nine lines are **added at the top**:

```
+ Can It Ford
+
+ SCOPE. The BSD 3-Clause License below applies to the original code and
+ documentation authored for this project. It does NOT apply to third-party
+ material redistributed in this repository, which remains under its own terms
+ and, in several cases, under terms that have not been established. No licence
+ is granted here in any third-party material, and no claim of copyright is made
+ over it. See THIRD_PARTY_NOTICES.md for the per-asset inventory.
+
```

then the existing text, **completely unchanged**:

```
  BSD 3-Clause License

  Copyright (c) 2026, Josie Cerrell
  ... (all 28 lines of BSD-3, byte-identical) ...
  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

and five lines **added at the bottom**:

```
+
+ ---
+
+ Third-party components and their licences, including components whose licence
+ status is UNRESOLVED, are listed in THIRD_PARTY_NOTICES.md.
```

### What this does and does not do

It **does** stop the repository from asserting rights it does not hold, which is the whole point.
It **does not** resolve any underlying licence question; section 2 and section 7 stay open, and
`THIRD_PARTY_NOTICES.md` records them as UNRESOLVED rather than papering over them. It **does not**
remove anything from the repository or from the public record.

Two things Josie may want to change, flagged rather than decided:
1. Whether to name the CCSA material explicitly in `LICENSE` itself rather than only by pointer.
   A pointer keeps `LICENSE` conventional and machine-readable; naming it in place is louder.
2. Whether "authored for this project" should instead read "authored by Josie Cerrell". The
   former covers contributions; the latter is narrower and matches the copyright line as it stands.

---

## 7. `citations/` publishes third-party publisher content with no rights record

`citations/README.md` is a bibliography. It records what each source establishes and does not
record the rights status of a single one of the files sitting next to it. Inventory, tracked on
`origin/main`: 3 publisher PDFs, 20 image reproductions, 2 third-party source files, plus the
project's own notes.

Licences resolved per DOI through Unpaywall (`scholar-sidekick checkOpenAccess`), 2026-08-18:

| Item | DOI | OA status | Licence | Consequence |
|---|---|---|---|---|
| Wang and Marsooli 2021, WRR, 7,399,829 bytes | `10.1029/2020WR028616` | hybrid | **CC BY-NC-ND** | NonCommercial and NoDerivatives. **Directly contradicted** by the unrestricted BSD-3 claim, which grants commercial use and modification. |
| Dasallas 2025, JFRM, 3,484,612 bytes | `10.1111/jfr3.70154` | gold | **CC BY** | Redistribution is permitted with attribution. Clean, but attribution is not recorded anywhere. |
| Smith, Modra and Felder 2019, JFRM | `10.1111/jfr3.12527` | **closed** | all rights reserved (Wiley `termsAndConditions#vor`) | **16 screen captures** of this article are published in `citations/Smith-Modra-Felder/`. This is the most exposed item in `citations/`. |
| AR&R Project 10 Stage 2, 1,115,134 bytes | none (ISBN 978-0-85825-948-5) | n/a | **UNRESOLVED** | See below. |
| `citations/vehicle(kks32).py`, `citations/splat_sim(kks32).py` | n/a | n/a | **MIT**, header present in-file | Clean. Copyright line reads "The mpm-engine authors", not Josie Cerrell. |

**The CC BY-NC-ND finding was previously asserted without a named article.** It is now identified:
it is Wang and Marsooli 2021, not either of the other two PDFs. This matters because the remedy
differs per article and a general worry is not actionable.

**Method note on how that was established, because the obvious route fails.** `strings` over both
Wiley PDFs returns zero Creative Commons matches and their XMP carries only Adobe and iText
producer metadata, so the PDF byte stream proves nothing either way. A Wiley licence statement
frequently lives only on the article landing page. The DOI record via Unpaywall is the route that
answered. Recorded so the null PDF result is not mistaken for evidence of absence by whoever
checks next.

**AR&R report, UNRESOLVED, with the routes named.** The PDF was read in full with `pypdf`: 29
pages, and a case-insensitive scan for `copyright|©|licen[cs]|all rights reserved|may be
reproduced|permission` returns **zero matches on every page**. Page 2 gives the imprint:
Engineers Australia, Engineering House, Barton ACT; AR&R Report Number P10/S2/020; ISBN
978-0-85825-948-5; contractor Water Research Laboratory; authors T D Shand, R J Cox, M J Blacka,
G P Smith. Routes tried: (1) full-text scan of the document itself, no rights statement; (2) no
DOI is printed in the report, so the Unpaywall route used for the other three is unavailable. A
standing project note records that `arr.ga.gov.au` returns 403, so the publisher's own terms page
has not been read. **Status: UNRESOLVED.** Same shape as the CCSA case: the document is silent,
and silence is not permission.

**A citation error found while checking, and fixed in this round.** `citations/README.md` cited
Smith, Modra and Felder 2019 as *"Full-scale testing of vehicle floating and sliding in flowing
floodwater"*. The DOI `10.1111/jfr3.12527` resolves via Crossref to *"Full-scale testing of
stability curves for vehicles in flood waters"*. Authors (Smith, Modra, Felder), year (2019),
journal and volume all match, so this is a citation error, not a fabricated reference. It is
nonetheless the exact surface signature of the dominant fabrication pattern (a real DOI paired
with a title that is not the resolved title), so it would fail any bibliography audit. The title
has been corrected in `citations/README.md` in this commit. **Anywhere else this title appears,
including the paper and its `.bib`, is outside this slot's scope and needs the same fix.**

---

## 8. `bridge/` and PhysGaussian: checked, measured, clean

**Why this was checked.** `README.md:167` states: "PhysGaussian has no detected license in its
GitHub metadata. Any PhysGaussian-derived bridge code must have its licensing resolved before
being committed here or submitted to DesignSafe." A tracked `bridge/` directory exists on
`origin/main` with 8 files. If upstream source had been copied into it, that would be public
redistribution of unlicensed third-party code, and it would outrank everything else in this
document.

**PhysGaussian is confirmed unlicensed, today, by three independent routes:**

1. GitHub API `repos/XPandora/PhysGaussian` returns `"license": null`.
2. The repository root contents listing contains no `LICENSE`, `LICENCE` or `COPYING` file.
3. `raw.githubusercontent.com/.../main/LICENSE` returns HTTP 404.

So `README.md:167` is accurate and current as of 2026-08-18, not stale.

**The derivation check, measured rather than judged.** Upstream `particle_filling/filling.py`
(446 lines) and `gs_simulation.py` (379 lines) were fetched and compared against
`bridge/filling.py` and `bridge/extract.py` after stripping comments and normalising whitespace:

| Comparison | Shared function names | Longest identical run | Line similarity |
|---|---|---|---|
| `bridge/filling.py` (85 code lines) vs upstream `filling.py` (381) | **none** | **1 line** | **0.0215** |
| `bridge/extract.py` (95 code lines) vs upstream `gs_simulation.py` (311) | **none** | **1 line** | **0.0099** |

The implementations differ in framework (upstream is Taichi kernels plus PyTorch and `mcubes`;
`bridge/` is pure NumPy) and in algorithm: upstream detects interiors by ray casting
(`collision_search`, `collision_times`), while `bridge/` uses six-direction prefix-max scans
(`np.maximum.accumulate`). Shared identifiers are generic (`numpy`, `astype`, `reshape`) or are
parameter names the published paper itself defines (`opacity_threshold`, `grid_lim`, `sim_area`).

**Verdict: no PhysGaussian source is redistributed in `bridge/`.** It is an independent
reimplementation of a published algorithm (Xie et al., arXiv:2311.12198), which is exactly the
policy `bridge/README.md` sets for itself. Reimplementing a published algorithm is not
infringement; copying unlicensed source would have been.

**Limit of this check, stated so it is not over-read.** Two upstream files were compared, chosen
because `bridge/README.md` names them as the ones not to copy. The other nine upstream Python
files were not diffed. This clears the specific risk that was flagged; it is not a clean-room
audit of the whole directory.

**A separate defect found, outside this slot's write scope.** `bridge/README.md` is stale against
its own code. It describes `filling.py` as "stub (TODO-5)" and lists TODO-5 as "License-gated, do
not copy PhysGaussian", but `filling.py` on `origin/main` is fully implemented. The README's
licence instruction was therefore standing over code that has since been written, and nobody had
recorded verifying compliance. That verification is the table above. **`bridge/README.md` needs
its status column updated; this slot did not write to it.**

---

## 9. Question for Krishna Kumar. BLOCKED ON KUMAR, NOT RESOLVED HERE

`CITATION.cff`, tracked and public on `origin/main`, and its byte-identical copy at
`citations/CITATION.cff`, read verbatim:

```yaml
title: "Can It Ford? Query-Conditioned World Models for Autonomous Vehicle Flood Traversability"
type: dataset
authors:
  - given-names: Josie
    family-names: Cerrell
    affiliation: Claremont McKenna College
  - given-names: Krishna
    family-names: Kumar
    affiliation: University of Texas at Austin
license: ODC-By-1.0
```

`designsafe-staging/docs/README_designsafe.md` lines 3 to 6 give a different arrangement of the
same two people, "**Author:** Josie Cerrell", "**PI:** Krishna Kumar", with the same ODC-By-1.0.

**No record exists anywhere in this repository of Kumar being asked about, or agreeing to,
either the co-authorship or the licence.** A search of the corrections register and CLAUDE.md
returns nothing on the point. This slot is not able to resolve it and has not tried.

### The question, as it should be put

> The repository's `CITATION.cff` lists you as a co-author of a dataset titled "Can It Ford?
> Query-Conditioned World Models for Autonomous Vehicle Flood Traversability" and releases that
> dataset under ODC-By-1.0. Two questions, and I would rather fix this before the DesignSafe
> deposit than after:
>
> 1. Are you content to be listed as a dataset co-author on that record, and is the ordering and
>    affiliation right?
> 2. Was ODC-By-1.0 chosen deliberately for the dataset? I cannot find any record of the choice
>    being discussed, and I do not want a licence attributed to you that you did not pick.
>
> Related and more urgent: the dataset as currently published is 91 percent verbatim CCSA/GMU FE
> model content, which carries no licence and no redistribution grant, only a request for
> acknowledgement. Any DesignSafe deposit that includes it inherits that problem, so I have
> flagged it rather than proceeding.

### Why this is load-bearing rather than tidy-up

Register item 10 records the DesignSafe DOI as pending Kumar sign-off and additionally gated on
E8. Sign-off does not resolve a licence question, and a licence question does not resolve
authorship. These are two separate consents and neither has been recorded. The DesignSafe deposit
needs both.

---

## 10. What remains UNRESOLVED after this round

| # | Item | Why it is not closed | Who can close it |
|---|---|---|---|
| 1 | CCSA/GMU/NCAC redistribution rights | Upstream ships no licence at all. Confirmed from the artefacts, not merely from reports about them. | CCSA at GMU, in writing. Contacts are printed in the upstream README. |
| 2 | Whether the canonical Yaris is NHTSA-hosted or CCSA-hosted | Register E8 records this as the load-bearing sub-question and it is still open. Not settleable from disk. | Whoever can reach the actual download page. |
| 3 | AR&R report redistribution status | Document is silent across all 29 pages; no DOI; publisher terms page returns 403. | Engineers Australia, or a working route to the AR&R terms. |
| 4 | 16 screen captures of a closed-access article | Published under an unrestricted BSD-3 claim. The carve-out stops the false grant; it does not create permission. | Josie's call, informed by Wiley's terms. |
| 5 | Kumar dataset co-authorship and ODC-By-1.0 choice | Blocked on Kumar. Section 9. | Kumar. |
| 6 | `bridge/README.md` stale status column | Outside this slot's write scope. | Whichever slot owns `bridge/`. |
| 7 | Smith 2019 title elsewhere | Corrected in `citations/README.md` only. The paper and `.bib` are outside this slot's scope. | d5-priorart. |

---

## 11. What this slot did not do, deliberately

- **Deleted nothing.** Removal is not the remedy and no go-ahead was given. Deletion does not
  unpublish: this repository is public and GitHub has served removed blobs by SHA in this account.
  Removing the derived hull would in any case address 7.1 percent of the byte total and leave the
  91.0 percent of verbatim upstream content in place.
- **Pushed nothing.**
- **Did not touch `vehicle_geometry_research/`**, not even to read-modify. Every quotation from it
  above is a read.
- **Did not write into `paper/`**, which belongs to slot d5-priorart on `claude/r8-priorart`. The
  acknowledgement text is in section 2 for that slot to paste.
- **Did not resolve the Kumar question**, only wrote it down.
