# THIRD-PARTY NOTICES, draft, plus a LICENSE carve-out clause

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.
**This is a DRAFT for review. Nothing has been written to `LICENSE`, and no
`THIRD_PARTY_NOTICES.md` has been created at the repo root.**

Follows from `E8_GEOMETRY_REDISTRIBUTION_DECISION_2026-08-16.md` section 2, which
found that `LICENSE` is repo-wide BSD 3-Clause under Josie's copyright with no
third-party carve-out.

---

## 0. Read this before adopting it: what a notices file does and does not do

**It fixes two real problems:**

1. The repo currently **asserts copyright** over material it did not author.
2. The repo currently **sublicenses** that material onward, because BSD 3-Clause
   grants every recipient the right to redistribute.

**It does NOT fix the third problem, and must not be allowed to look as if it does:**

3. **Redistribution itself.** A notice saying "this material belongs to CCSA and is
   licence-silent" is an accurate description of an unpermitted redistribution. It is
   honest, it is better than the current state, and it is **not permission**.

So adopt this **and** keep the geometry decision open. The correct reading is
"attribution corrected, redistribution still unresolved", never "licensing handled".

**Severity is not uniform across the components below and should not be flattened:**

| Component | Actual violation today? |
|---|---|
| ambientCG textures, Poly Haven HDRI | **No.** CC0. Attribution is courtesy, not obligation |
| `third_party/mpm-engine`, MIT | **No.** Already fully compliant |
| CCSA decks and derived hulls | **Unresolved**, and the notice does not resolve it |
| `citations/` PDFs and screenshots | **Probable**, see the citations audit |

Two of the four components need nothing but a courtesy line. Do not let the notices
file imply the repo was broadly non-compliant; it was not.

---

## 1. The repo already contains the right pattern. Extend it, do not invent one.

`third_party/mpm-engine-544c93dd/` carries `LICENSE`, `PINNED_SHA.txt` and a
`VENDORED.md` that records upstream repo, pinned SHA, the licence **confirmed by
fetching `LICENSE` at that SHA**, the raw-URL pattern, a per-file table of what came
from where, and an explicit **provenance caveat** naming which files were pulled
before the SHA was pinned. [read]

That is a better vendoring record than most production repos have. Every component
below should be brought up to that standard rather than to some new one.

---

## 2. Draft `THIRD_PARTY_NOTICES.md`, for the repo root

Everything in fenced blocks is proposed file content.

**All source attributions are now verified against the publishers' own pages, fetched
2026-08-17. Nothing below is inferred from a filename.** The earlier draft carried two
`[CONFIRM]` markers on the ambientCG and Poly Haven components; both are cleared, and
the filename-convention inference proved correct in all three cases. It was still an
inference until fetched, which is why it was marked. A notices file that misattributes
is worse than none.

```markdown
# Third-party notices

This repository contains material authored by third parties. That material is NOT
covered by the BSD 3-Clause licence in `LICENSE`, which applies only to the original
work of this project. Each component below is listed with its origin and the terms
under which it is included.

## 1. CCSA / NCAC finite element vehicle models

Location: `vehicle_geometry_research/`
Files: 4 release archives (`.zip`), 14 LS-DYNA decks (`.key`), 4 upstream `README.md`
Size: 160,322,098 bytes

Developed by the Center for Collision Safety and Analysis (CCSA) at George Mason
University, sponsored by the Federal Highway Administration. Not authored by this
project. Redistributed here without a licence grant, see the status note below.

- 2010 Toyota Yaris, coarse v1l, released December 2016. DOI 10.13021/G8JS5D
- 2010 Toyota Yaris, detailed v2j, released October 2016. DOI 10.13021/G8CC7G
- 2007 Chevrolet Silverado, coarse v3a, released December 2016. DOI 10.13021/G8SC8K
- 2007 Chevrolet Silverado, detailed v3e, released November 2016. DOI 10.13021/G8F312

Contacts, as published in the upstream READMEs: Dhafer Marzougui, Fadi Tahan,
Steve Kan, Rudolf Reichert (George Mason University).

As the upstream READMEs request: **the CCSA at GMU and the FHWA are acknowledged for
use of these FE models in this work.**

**Licence status: UNRESOLVED.** The upstream READMEs grant no redistribution right,
state no licence, and carry no copyright statement. They request acknowledgement and
disclaim warranty. The CCSA-hosted distribution is licence-silent, and DOI
10.13021/G8JS5D has an empty rights field. Sponsorship by a federal agency does not
place contractor-authored work in the public domain. Redistribution permission has
been neither granted nor refused; it has not been sought.

## 2. Geometry derived from component 1

Location: `vehicle_geometry_research/`
- `yaris_coarse_v1l_watertight.ply` (12,445,769 bytes)
- `yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` (977,025 bytes)

Watertight hulls produced by this project from the CCSA Yaris decks using mesh2sdf
(MIT). The *process* is this project's work; the *underlying geometry* is CCSA's.
The status note in component 1 applies equally here.

Renders depicting this geometry are derived works of it. See
`docs/E8_GEOMETRY_REDISTRIBUTION_DECISION_2026-08-16.md`.

## 3. Surface textures, ambientCG **[CONFIRMED 2026-08-17]**

Location: `assets/`
- `Asphalt015_1K-JPG_Color.jpg`, `Asphalt015_1K-JPG_NormalGL.jpg`,
  `Asphalt015_1K-JPG_Roughness.jpg`, `Asphalt015.png`
- `DaySkyHDRI002A_1K_HDR.exr`

Source: **ambientCG** (ambientcg.com). Both asset pages were fetched on 2026-08-17
and both are released under **Creative Commons CC0**. ambientCG states its assets are
"free to use without attribution, even in commercial circumstances", so **attribution
is neither required nor requested**. It is recorded here anyway, because an
unattributed asset is indistinguishable from an unlicensed one to anyone auditing the
repo.

Precision note: the ambientCG pages state "CC0" without a version number, so this
notice says CC0 rather than CC0 1.0 Universal. An earlier draft asserted the version;
that was not on the page.

## 4. Environment HDRI, Poly Haven **[CONFIRMED 2026-08-17]**

Location: `assets/hdri/kloofendal_43d_clear_puresky_2k.hdr` (4,624,289 bytes)

Source: **Poly Haven** (polyhaven.com). **Author: Greg Zaal.** Released under
**CC0**, page fetched 2026-08-17. No attribution required or requested; the author is
named here as a courtesy and because it is the one piece of provenance the filename
does not carry.

## 5. kks32/mpm-engine

Location: `third_party/mpm-engine-544c93dd/`, `third_party/mpm-engine-544c93dd-solver-core/`

MIT License, "Copyright (c) 2026 The mpm-engine authors (see AUTHORS.md)", confirmed
by fetching `LICENSE` at pinned SHA `544c93dd02cb9c7ead89e1155a62967243244fce`.
Full provenance, including which files were fetched before the SHA was pinned, is in
each directory's `VENDORED.md`. The MIT licence text is retained at
`third_party/mpm-engine-544c93dd/LICENSE` as that licence requires.

**This component is already compliant. No action needed.**

## 6. Cited literature

Location: `citations/`

Third-party papers, reports, and reproductions of their figures and tables, retained
as working sources. Redistribution status is assessed per file in
`docs/E8_CITATIONS_REDISTRIBUTION_AUDIT_2026-08-16.md`. Items confirmed to be
non-open-access are to be untracked and replaced by their citation and DOI.

## 7. Unidentified reconstruction

Location: `vehicle_geometry_research/failed_reconstructions_2026-07-25/`
`car_mesh.ply`, `car_mesh_rescaled.ply`

Open3D Poisson reconstructions of a source point cloud recorded in this repo as
"likely a small tutorial demo asset". The source is unidentified, so the applicable
terms are **indeterminate**. These are not CCSA-derived and are retained only as
documentation of a failed approach.
```

---

## 3. Draft `LICENSE` carve-out clause

Add immediately below the existing copyright line, before "Redistribution and use".
Minimal, and it does not alter the BSD grant over the project's own work.

```
-------------------------------------------------------------------------------
SCOPE

The licence below applies to the original work of this project only. It does NOT
apply to third-party material redistributed in this repository, including but not
limited to the contents of `vehicle_geometry_research/`, `third_party/`,
`citations/` and `assets/`. Each such component, its origin and its own terms are
listed in `THIRD_PARTY_NOTICES.md`. Where a component's terms are unresolved, no
licence to it is granted or implied by this file.

No copyright is asserted by this project over any third-party material.
-------------------------------------------------------------------------------
```

The last sentence is the one that does the real work: it retracts the implied
ownership claim, which is the part most likely to be read as bad faith.

---

## 4. Recommendation

**Adopt sections 2 and 3. Both [CONFIRM] items are now cleared** (section 5). This is the most
actionable item in D2's scope precisely because, unlike the geometry question, **it
requires permission from nobody**. It is a strict improvement under every outcome of
the CCSA conversation, and it is the right thing to have in place *before* writing to
CCSA rather than after.

Do it before, not after, the removal in the geometry document's option 4: attribution
should be correct at the moment anyone looks, and removals change paths this file
cites.

**Not executed.** Writing `LICENSE` and creating a root-level `THIRD_PARTY_NOTICES.md`
are changes to the repo's legal surface, so they are Josie's call, not mine.

## 5. What is unverified here

- **The ambientCG and Poly Haven attributions are now CONFIRMED, 2026-08-17**, and
  are no longer inferred from filename convention. All three source pages were
  fetched: `Asphalt015` and `DaySkyHDRI002A` on ambientCG, both **CC0, attribution
  not required**; `kloofendal_43d_clear_puresky` on Poly Haven, **CC0, author Greg
  Zaal**. The filename-convention inference turned out to be correct in all three
  cases, but it was still an inference until fetched.
  The related finding stands unchanged: **no licence file for any of them ships in
  the repo**, and a repo-wide search for "ambientcg" returns zero hits. The assets are
  present and the attribution is absent. Because all three are CC0 this was never a
  compliance problem, only an accuracy one, which is why it ranked last.
- **The four CCSA DOIs are transcribed from the upstream READMEs in the repo**, read
  live. They were not resolved against doi.org this session.
- **`citations/` is covered by reference**, not re-audited here.
- No legal advice is offered or implied. This is a provenance record and a drafting
  proposal.
