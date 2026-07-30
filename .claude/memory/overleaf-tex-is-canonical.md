---
name: overleaf-tex-is-canonical
description: "The paper's build source is conference_101719_1.tex on the overleaf remote with flat figure paths, NOT paper/conference_101719.tex; overleaf/main head is 92ce4de as of 2026-07-30 18:00 CDT"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5e98f138-df3e-4c0d-ab06-2315b13b24e3
  modified: 2026-07-30T23:13:31.211Z
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
