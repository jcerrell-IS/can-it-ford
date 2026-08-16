# E8: public redistribution of NCAC/CCSA vehicle geometry. Decision document.

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.
**Diagnosis only. Nothing in this document has been executed.**

Every number and quotation below was **read directly** from `origin/main` blobs in
this session, via `git show origin/main:<path>` and `git ls-tree -r --long
origin/main`, unless tagged otherwise. Claims are tagged **[read]**, **[recalled]**
or **[inferred]**.

---

## 0. The headline, and why it changes the framing

E8 as written governs **derived** geometry: "do not commit any derived NCAC/CCSA
geometry to the public repo". The dispatch that commissioned this work scoped the
exposure as four `.ply` files plus fifteen renders.

**That scope is wrong, and it understates the exposure by an order of magnitude in
the direction that matters.** [read]

`vehicle_geometry_research/` on `origin/main` holds **176,252,809 bytes across 30
files (168.09 MB)**. Of that:

| Class | Bytes | MB | Files | Share |
|---|---|---|---|---|
| **Upstream CCSA material, verbatim** (4 `.zip`, 14 `.key`, 4 upstream `README.md`) | 160,322,098 | 152.90 | 22 | **91.0%** |
| Derived hulls (`.ply`) from CCSA decks | 13,422,794 | 12.80 | 2 | 7.6% |
| Reconstructions, not CCSA | 2,400,894 | 2.29 | 2 | 1.4% |
| Repo-authored docs | 107,023 | 0.10 | 4 | 0.1% |
| **Total** | **176,252,809** | **168.09** | **30** | 100% |

The public exposure is **not primarily derived geometry. It is verbatim
redistribution of the original CCSA FE models**, including the complete
`yaris-coarse-v1l.key` at 42,846,753 bytes and `silverado-coarse-v3a.key` at
28,611,724 bytes, plus all four release archives. [read]

This matters because every argument that softens a derived-work claim (transformation,
the hull being a lossy watertight remesh, de minimis) is **unavailable for a verbatim
copy**. The repo redistributes the artifact itself.

The commit that introduced them says so in its own subject line: `f85c385 Add
downloaded NCAC vehicle FE models, Silverado and Yaris, coarse and detailed`. [read]

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
- Verbatim upstream material (152.90 MB) is committed to the same public repo. Not
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

Ordered by increasing cost. **None has been executed.**

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
*Consequence:* the repo stops actively presenting the material. **It does not
unpublish it.** GitHub has served removed blobs by SHA after history rewrites in this
very account. **[recalled from project memory; the W&B key precedent]** Anyone with a
commit SHA retains access.
*Cost:* low. Breaks any script reading those paths (the hull is load-bearing: it is
the canonical mesh for all 17 gated runs).

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
Delete the 4 `.zip`, 14 `.key` and 4 upstream `README.md` (22 files, 152.90 MB);
retain the 2 derived `.ply` and the renders.
*Consequence:* removes 91.0% of the exposure and the entire indefensible verbatim
portion, while keeping every artifact the project actually needs to run and to
reproduce. The derived-hull question stays open under option 1.

---

## 6. Recommendation

**Do option 0 now, then option 4, then option 1. Do not do option 3.**

Reasoning, stated so it can be argued with:

1. **Option 0 first** because it is free, is correct under every scenario, and
   removes the assertion of ownership that would most damage a permission request.
   Doing it before writing to CCSA also means the email describes a repo that already
   attributes them properly.
2. **Option 4 next** because the verbatim 152.90 MB is the part with no defence and
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

- **Whether an NHTSA-hosted copy of this exact model exists.** Section 1 qualification
  1. Closing it requires the CCSA and NHTSA download pages, which were not fetched
  this session.
- **Whether the four `.zip` are byte-identical to the upstream releases.** They are
  named as upstream releases and contain upstream READMEs and decks, but no checksum
  was compared against a fresh download. **[inferred]**
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
