---
name: overleaf-tex-is-canonical
description: "The paper's build source is conference_101719_1.tex on the overleaf remote with flat figure paths, NOT paper/conference_101719.tex; overleaf/main shares NO git ancestor with origin, so `git push overleaf main` is an overwrite and not a sync; head was 9a8561f on 2026-07-31"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5e98f138-df3e-4c0d-ab06-2315b13b24e3
  modified: 2026-07-31T21:14:11.945Z
---

The IEEE paper is built from `conference_101719_1.tex` on the `overleaf` remote
(`overleaf/main`), not from `paper/conference_101719.tex` in the working tree.
Overleaf uses a FLAT layout: figures sit at the repo root, so
`l0l1_two_rules_v2.pdf`, not `figures_review/l0l1_two_rules_v2.pdf`. On
2026-07-30 only 1 of the 6 local `\includegraphics` paths would have resolved
against the Overleaf file list.

Reconciliation was completed and pushed on 2026-07-30 at 15:31 CDT as commit
`94d4d4f`, "Reconcile onto Overleaf base: port mass-sweep paragraph and figure,
graft v2-exclusion and passthrough detail, apply 8 voice edits, resolve both
PLACEHOLDERs". It was built on branch `reconcile/overleaf-base` in the worktree
`.claude/worktrees/reconcile-overleaf`. After the push,
`git log overleaf/main..reconcile/overleaf-base` is empty.

A second commit `4e2fdbd` was pushed to `overleaf/main` on 2026-07-30 at 16:29
CDT: pipeline diagram swapped to `pipeline_diagram_v2.pdf` with the dashed-stage
caption, force-balance caption replaced with the buoyancy explanation, and
`l2_divergence_real_v2` converted from png to vector pdf. **`overleaf/main` head
is now `4e2fdbd`, not `94d4d4f`.** Verified live: all 6 `\includegraphics`
targets resolve on the remote, 10 live `\FLAG`, 0 live `\PLACEHOLDER`.

That second commit existed as *uncommitted* work in the worktree at 15:38, eight
minutes before this memory file was first written at 15:46, and this file did not
mention it. The memory was authored by session `5e98f138` while a different pane
held the edit uncommitted, so a sibling pane's working tree is invisible to a
memory write. Check `git status` in the worktree, not just the last commit
message, before recording anything as finished.

A third commit `92ce4de` ("add paper source") is the head as of 2026-07-30 18:00
CDT, verified live by `git fetch overleaf`. Note `conference_101719.pdf` on the
remote is the untouched 2019 IEEE template (3 pp, "Conference Paper Title*"), and
`conference_101719_preview.pdf` is a stale 2026-07-17 build: neither is the
current paper. Compile the tex yourself rather than reading either PDF.

A fourth commit `998074d` ("Update on Overleaf.") landed from the **browser**, not
from git, between 18:00 and 19:22 CDT on 2026-07-30. It changed exactly one line:
"Department of Integrated Sciences" to "**Kravis** Department of Integrated
Sciences" in the author block. Browser edits land on `overleaf/main` without any
local signal, so a branch that fast-forwarded an hour ago may not fast-forward
now. Re-check immediately before every push.

**Head is `ff22124` as of 2026-07-30 19:37 CDT**, pushed as a fast-forward from
`paper/final-graft`. Verified from the remote, not locally: `git ls-remote
overleaf main` returns `ff22124983af3eb2617fce56dfdcf335df3382b7`. State on the
remote now: **0 rendering `\FLAG`** (down from 10; the 3 remaining grep hits are
the `\newcommand` on line 16 plus 2 comment lines on 11 and 13), 0
`\PLACEHOLDER`, **7** `\includegraphics` all resolving, `paper_draft.md` still
present, bib reads "Modra, Benjamin D.", no "Eq.~6" anywhere, DataCite DOI
`10.13021/G8JS5D` present at bib line 103.

Two file-level changes in that push worth remembering: `force_balance.png` was
always **JPEG data carrying a `.png` extension**, which misdirects pdflatex's
driver selection, and is now `force_balance.jpg`; and `l0l1_two_rules_v2.pdf` and
`mass_grid_sweep_v2.pdf` were **JPEGs wrapped in PDF** (1 ImageXObject, 1
DCTDecode, 0 embedded fonts) and were replaced with true vector renders (133 and
88 embedded fonts, no raster XObject, ~37% of the former size). To test whether a
"PDF figure" is really vector, count `/Subtype/Image` and `/DCTDecode` against
`/Font`; file size alone is only a hint.

**The two repos share no git history.** `git merge-base overleaf/main HEAD` exits
1: verified live 2026-07-31. So **`git push overleaf main` is not a sync, it is an
unrelated-histories overwrite of the entire Overleaf project**, and any
instruction phrased as "just add the overleaf remote and push main" is wrong on
this repo even though the remote genuinely exists. The remote is *already*
configured and pre-authenticated, so there is nothing to set up and no GitHub
Sync or token step to perform. The only safe update path is: check out
`overleaf/main` into a temp branch or worktree, place the changed file at the
**root** under its flat name, commit, push that. One file per change.

Head was `9a8561f` ("pre-revision July 31") at 2026-07-31 15:42 CDT, past both
the `ff22124` above and the `bbd5bd8` written into the header comment of
`paper/conference_101719.tex`. Three separate records of the head disagreed at
once, which is the normal state, not an anomaly: always `git fetch overleaf` and
read the head yourself.

**Head is now `710ecf7`**, pushed 2026-07-31 16:10 CDT as a clean fast-forward
from `9a8561f`, changing exactly one binary file: `l0l1_two_rules_v2.pdf`
(103854 to 100554 bytes, sha256 `142a4d7b...`). The tex and the caption were
already correct and were not touched. Verified from the remote afterwards, and
the live remote tree compiles to 7 pages with 0 errors and 0 undefined refs.

Note the worktree `.claude/worktrees/overleaf-push`, branch `overleaf-edits`,
still sits at the superseded `9a8561f` with **staged** edits to
`conference_101719_1.tex` and `can_it_ford_references_IEEE.bib` and the **old**
Fig 2 PDF in its tree. It can no longer fast-forward, and a force-push from
there would silently revert the Fig 2 fix. Rebase that branch onto the new head
before it pushes anything.

**Why:** the direction was decided deliberately, not by default. Overleaf's III-C
and bib keys win; local's mass-sweep paragraph and figure were ported in. Editing
`paper/conference_101719.tex` and reporting it as done is a real failure mode: a
figure can be present locally and absent from the build. That exact thing happened
on 2026-07-30, when `mass_grid_sweep_v2.pdf` was present in the local tex and
uploaded to Overleaf as an asset, yet referenced by nothing in the Overleaf tex.

**How to apply:** before claiming any paper edit has landed, check it against
`git show overleaf/main:conference_101719_1.tex`, not the local file. Use flat
figure paths in anything destined for Overleaf. "Which tex is canonical" is
settled and should not be reopened. That is the only settled question here: it
does NOT mean the paper's content is finished, and it is not a reason to skip
checking the live remote head. Also note the `overleaf` remote URL in
`.git/config` embeds a plaintext Overleaf token, so never echo remote URLs
unredacted. Related: [[l0l1-divergence-pdf-not-a-7th-figure]].
