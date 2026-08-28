# Poster and reconstruct-to-decide pipeline status, 2026-08-25

Read-only pass. Nothing staged, committed or pushed. HEAD `57db739` on `claude/add-ci-checks`.

**Tags**: [READ] = I ran the command or read the bytes in this session. [RECALLED] = from a
summary or memory, not re-derived. [INFERRED] = reasoned, not measured.

**Two incoming premises were wrong and are corrected here.**

1. `R9_LOOP_CLOSURE_2026-08-22.md` does **not** contain the drafted replacement text. At
   `:73-79` it states the two false statements and then points at "d8-naming's section 1.4".
   The drafted text lives in `docs/R8_DETERMINISM_RENAME_2026-08-18.md` section 1.4. I used
   that. [READ]
2. The prescribed `grep -rn ... renders/ --include="*.py"` uses the shell `grep`, which in this
   environment is ugrep with `--ignore-files` and skips gitignored paths (CLAUDE.md rule H0).
   I ran every sweep below with `/usr/bin/grep` or `git grep` instead. [READ]

One premise was **right**: `deliverables/poster/Cerrell_TACC_42x56.pdf` is 6,102,270 bytes with
MD5 `89240d2336bccbfceb8bf8b4f135279e`. [READ]

---

## 1. Has any gsplat reconstruction ever entered a simulation?

**No. Not once, at any date, including after the drainA job completed.**

The capability exists and was never fed a splat. `renders/yaris_render_s1/vehicle_live.py:184`
defines `def is_gaussian_ply(path: Path) -> bool`, and `:221` dispatches on it:
`if path.suffix.lower() == ".ply" and is_gaussian_ply(path):`. So a gsplat reader is wired into
the vehicle layer. [READ]

What the runs actually loaded is a watertight **mesh**, on every path:

| line | content |
|---|---|
| `sim_standing.py:15` | `YARIS = VEHICLE_DIR / "yaris_coarse_v1l_watertight.ply"` |
| `sim_standing.py:49` | rogue entry, `rogue_g96_pd8_coarse_watertight.ply` |
| `sim_standing.py:58` | silverado entry, `silverado_g96_pd8_coarse_watertight.ply` |
| `sim_standing.py:30` | the loader is `trimesh.load(force="mesh")`, "the loader the 17 gated runs actually ran" |

**The line that proves it could not have happened even by accident** is the preflight at
`renders/yaris_render_s1/sim_standing.py:364-366`:

> `if not hull_watertight:` `raise SystemExit("PREFLIGHT FAIL hull is not watertight: %s.
> Volume, and therefore buoyancy, is undefined for an open mesh." % vpath)`

A 3DGS export is a point cloud with no closed surface, so it fails this gate before the solver
is constructed. [READ], [INFERRED] only for the step that a 3DGS cloud is not watertight.

Three candidate paths that could have falsified this, all checked and all negative:

- **`scripts/export_drainA_ply.py`** is the only tracked code naming drainA. It is an
  **export**, not an input. Its own docstring records that job 3306077 trained to 30,000 steps
  but "its sbatch omitted `--save-ply`", so no PLY was written at step 29999, and "Anything
  downstream consuming 'the drainA splat' has been reading a 3k model". [READ]
- **`simulation/moving_vehicle_channel.py:195`** reads
  `if not hasattr(mod, "solidify_watertight") or not hasattr(mod, "is_gaussian_ply"):` followed
  by `raise SystemExit("loader at %s is not the as-ran patched copy")`. That is a **fingerprint
  assertion** confirming it loaded the right module, not a splat load. [READ]
- **`bridge/gaussian_io.py`** defines its own `is_gaussian_ply` at `:81` and has **zero
  importers** across `simulation/`, `renders/` and `analysis/`. It is dead to the simulation
  path. [READ]

Corroborating negative: `data/all_runs_inventory.csv` has no mesh or PLY column at all. Its
geometry columns are `hull_m3`, `solid_volume_m3` and `n_vehicle`, so the 17-run store records
no reconstruction provenance because there is none to record. [READ]

**The 2026-07-27 finding is confirmed and now extends past the event that was supposed to test
it.** drainA completing did not change the answer, because drainA's only appearance in code is
an exporter, and the 30k run wrote no PLY to export from in the first place.

### Correction to this section's own first verdict, same day

**This section originally ended "OPEN ... the paper's closed reconstruct-to-decide pipeline
claim is still unsupported by any run, and nobody has decided whether to close the loop or
reword the claim." The second half of that was wrong and is withdrawn.** Somebody did reword
it, thoroughly, and the wording is already shipped. Read live from
`overleaf/main:conference_101719_1.tex`, the paper discloses the gap **three times**: [READ]

- **Abstract**: "The splatting front end and PhysGaussian bridge are designed and not yet
  built, so every flood domain here is parametric."
- **Introduction**: "The Gaussian splatting front end reached structure-from-motion on one
  real scene but was not trained or coupled to any result reported here, so the flood domain
  in every result below is specified parametrically in depth and velocity rather than
  recovered from reconstruction."
- **Fig 1 caption**: "Dashed stages are conceptual, not the path used for any result reported
  here: the Gaussian-splat reconstruction and the PhysGaussian kernel-to-particle bridge are
  designed and not yet built."

So this is **not** an undisclosed claim, and it is not the poster's failure mode. The poster
asserts something false under a heading reading `ESTABLISHED`; the paper states the limitation
in its own abstract. Treating the two as the same defect would be wrong, and my first pass
came close to doing it.

**Trap worth recording for anyone re-checking this.** The sentence "no trained splat has
entered a simulation in this work" exists **only** in the working draft
`paper/conference_101719.tex` (md5 `15864610`). It is **absent** from
`paper/canonical_2026-08-02/conference_101719_1.tex` and from the shipped
`overleaf/main:conference_101719_1.tex` (md5 `c64d0d55`). Grepping the shipped file for that
sentence returns zero and reads as "the shipped paper hides it", which is the opposite of the
truth: the shipped paper discloses the same fact in different words, in three places. Grep the
concept, not the draft's phrasing. [READ]

**DONE on the factual question, OPEN on one narrow wording point.** No gsplat reconstruction
has ever entered a simulation, and the shipped paper already says so three times. The only
residue is that the abstract's closing sentence still reads "this work **delivers** a
reconstruct-to-decide pipeline" four sentences after saying the front end is not built. That is
a judgement call about emphasis, not a false statement, and changing it needs a decision plus
an Overleaf push, so it is flagged and not touched here.

---

## 2. The poster's real state

Nine poster PDFs exist outside `.claude/worktrees/`. Worktree copies are excluded and named
here so the scope is explicit: six worktrees each hold their branch's `public_release/` and
`figures/` copies, which are the same tracked blobs. [READ]

They are **three distinct documents**, not nine:

| # | MD5 | size B | mtime | paths | NSF | award 2447887 | Lorem |
|---|---|---|---|---|---|---|---|
| A | `89240d2336bccbfceb8bf8b4f135279e` | 6,102,270 | 2026-07-26 12:51 to 2026-08-04 | `public_release/`, `deliverables/poster/`, `deliverables/poster/atm ...`, `for_kumar/01_deliverables/`, `for_kumar 2/01_deliverables/` | yes | yes | **0** |
| B | `22a5514fbdc36f625ac291bfe0a70b91` | 6,101,491 | 2026-07-26 12:19 and 12:30 | `deliverables/poster/_pre_style3_2026-07-26/`, `deliverables/poster/Cerrell_TACC_42x56dup.pdf` | yes | yes | **0** |
| C | `ae91282a3c575c18a0980ac2d0dc199e` | 404,092 | 2026-07-25 23:13 | `figures/Cerrell_TACC_42x56.pdf` | yes | yes | **0** |
| D | `e43ca9603d724067f7677827a9edb69b` | 403,657 | 2026-08-22 12:41 | `_desktop_rescue_2026-08-22/Cerrell_TACC_42x56_NEWER_THAN_MAIN.pdf` | yes | yes | **0** |

**Every one of the nine carries the NSF acknowledgment and award #2447887.** Text extracted
with `pdftotext -layout` from each file. Document A's acknowledgment reads "NSF REU Site:
Cyberinfrastructure Research for Societal Advancement, Award #2447887". Documents C and D read
"This material is based upon work supported by the National Science Foundation under the NSF
REU Site: Cyberinfrastructure Research for Societal Advancement, Award # 2447887". [READ]

**There is no Lorem Ipsum document, and the search was exhaustive rather than narrow.** Zero
hits across: all nine extracted poster texts; both `Cerrell_TACC_42x56.pptx` files unzipped to
`ppt/slides/*.xml`; every `.pptx`, `.docx` and `.key` in the tree to depth 4, twenty-three files
in total; and `git grep -li lorem HEAD` across the whole tracked tree. `git log --all
--diff-filter=D` shows **no poster PDF was ever deleted** from history, so it did not exist and
get removed. [READ]

**The second poster document is real. It is document C, and it is not a draft.** This is the
thing the 2026-07-27 session could not identify. It is a **text-native rebuild** at one
fifteenth the size, carrying roughly twice the extractable text (23,183 characters against
11,159), and it is **tracked and on `origin/main`** as blob `5340f626`, byte-confirmed by
extracting the blob and matching MD5 `ae91282a` against the working file. So `origin/main`
publishes **two different posters under the same filename** at `public_release/` and
`figures/`. [READ]

**Document D is a newer revision of C that has never been committed.** It is untracked, sits in
`_desktop_rescue_2026-08-22/`, is named `_NEWER_THAN_MAIN`, and its content differs from C in
the headline result table: small passenger reads **14 FORD / 56 NO-FORD** against C's **12 /
58**, and large 4WD reads **26 / 44** against C's **24 / 46**. Two published-looking posters
disagree about the verdict counts, and the newer one is the uncommitted one. [READ]

**DONE.** All nine files fingerprinted, the award number is in every one, no Lorem Ipsum
document exists anywhere, and the unidentified second poster is pinned as the tracked 404 KB
text-native rebuild plus one newer untracked revision.

---

## 3. The drafted poster fix

**The two false statements**, quoted from `R8_DETERMINISM_RENAME_2026-08-18.md` section 1.1,
which extracted them from the committed blob. I re-extracted both from the blob myself in the
prior turn and both are present. [READ]

Statement A, the `Scope` panel under the sub-heading `ESTABLISHED`:

> ESTABLISHED 20 coupled runs. All 17 that carry a determinism record are bit-reproducible;
> the 3 dry-start runs record none. Mesh containment 100.00 pct of a 2000-particle subsample.
> DxV bit-identical across a 2.1x mass range.

Statement B, the Fig 2 caption:

> Fig 2. Final displacement against surge velocity at fixed realized depth 0.2944 m, grid 64,
> one hull at 1100 kg, all runs deterministic. Vertical rule marks v = 1.0189 m/s, where DxV
> crosses the AR&R small-passenger 0.30 m2/s cap.

**The drafted replacements**, verbatim from section 1.4:

Replacement for A:

> ESTABLISHED 20 coupled runs. Hull loading is bit-identical across all 17 that carry the
> record; their trajectories are not established to be. The summary field previously called
> `determinism_identical`, now `hull_load_identical`, only ever compared a particle count and a
> grid limit between two loads of the same hull. Mesh containment 100.00 pct of a
> 2000-particle subsample. DxV bit-identical across a 2.1x mass range.

Replacement for B:

> ... grid 64, one hull at 1100 kg. Hull loading is bit-identical across these runs; their
> trajectories are not. Vertical rule marks v = 1.0189 m/s ...

A standalone erratum paragraph also exists in the same section, for the case where the poster
is not re-issued. [READ]

**Was the fix ever applied? No.** Tested against the extracted text of every poster:

| document | "bit-reproducible" | "all runs deterministic" | replacement text present |
|---|---|---|---|
| A, 6,102,270 B, on `origin/main` at `public_release/` | **1** | **1** | 0 |
| B, 6,101,491 B | **1** | **1** | 0 |
| C, 404,092 B, on `origin/main` at `figures/` | 0 | 0 | **0** |
| D, 403,657 B, untracked | 0 | 0 | **0** |

**Seven of the nine files carry both false statements.** [READ]

**The zeros in rows C and D are not the fix landing, and reading them that way would be the
trap.** Neither document contains the drafted replacement text, and neither contains an
`ESTABLISHED` panel or any determinism token at all: a grep of document D for
`ESTABLISHED|determinis|bit-identical|reproducib` returns nothing. The claim is absent because
that whole panel does not exist in the text-native rebuild, not because anyone corrected it.
A reader of `figures/` never meets the false statement; a reader of `public_release/` does.
[READ]

Supporting state from the prior turn, unchanged: the field rename to `hull_load_identical`
landed in eleven files on `claude/add-ci-checks` but resolves in **zero files on
`origin/main`**; the poster blob was last touched by `b78bc1e` of 2026-08-02; and no erratum
has ever been committed under `public_release/` or `deliverables/`. [READ]

**OPEN.** The replacement text has existed since 2026-08-18 and appears in no poster, no
erratum was published, and the public 6.1 MB submission still carries both statements verbatim.

---

## What is not verified here

- **No adversarial review.** This pass was not checked by a second party.
- **"A 3DGS cloud is not watertight"** is the one [INFERRED] step in section 1. Every other
  claim there is a line I read. It could be made [READ] by running the preflight against a
  splat PLY, which nobody has done, which is the finding.
- **I did not determine which poster was actually submitted.** `docs/SUBMISSION_STATUS.md` is
  blank on that question, as recorded in `docs/R9_LOOP_CLOSURE_STATUS_2026-08-25.md`. Document
  A is the one on `origin/main` at `public_release/` and the one dated before the 2026-07-27
  09:00 CST deadline, but that is circumstantial, not a record.
- **Document D's provenance** is unestablished beyond its mtime and filename. Nothing says who
  built it or why it was never committed.

*Written 2026-08-25. Read-only: nothing staged, committed or pushed.*
