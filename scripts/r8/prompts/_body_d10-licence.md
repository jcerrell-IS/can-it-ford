# SLOT d10-licence

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-licence, branch claude/r8-licence
(off origin/main).

You may write ONLY:
  LICENSE
  THIRD_PARTY_NOTICES.md                    (new)
  citations/README.md
  docs/R8_LICENCE_RECONCILE_2026-08-18.md   (new)

NEVER TOUCH: anything under vehicle_geometry_research/; any other branch. NO deletions, NO
history rewrite, NO push without an explicit go-ahead.
DELETION DOES NOT UNPUBLISH. GitHub has served removed blobs by SHA in this account.

## WHERE THIS LEFT OFF
Register E8 was resolved AGAINST the project by the upstream repo's own README: no distribution
statement, and the root LICENSE is BSD-3-Clause with NO third-party carve-out, so this repo
affirmatively re-licenses CCSA/GMU material under Josie's copyright.

WHAT IS ALREADY PUBLIC is more than derived geometry: reportedly 176 MB including the complete
42.8 MB Yaris LS-DYNA deck and all four original upstream zips, i.e. VERBATIM upstream content.
An earlier measurement put it at 168.09 MB / 30 files of which 152.90 MB (91.0 percent) is
verbatim. RE-DERIVE THE FIGURE YOURSELF and state which it is.

THE ONE EXPLICIT OBLIGATION NOBODY HAS QUOTED: the CCSA mesh ships its own terms paragraph in a
README requiring acknowledgement of CCSA/GMU and FHWA in publications. The paper does not
acknowledge them. Cheapest clearly-owed fix in the project.

FOUR MUTUALLY INCONSISTENT LICENCE DECLARATIONS exist for the same public repo, and one names
Krishna Kumar as co-author of a dataset released under a licence nobody has recorded discussing.
Enumerate all four, quote each verbatim with its path, say which governs. The Kumar authorship
half is BLOCKED ON Kumar: write the question down, do not resolve it.

ALSO: citations/ publishes third-party publisher PDFs and 16 screen captures of a published paper
to the public remote, and its README records no licence status for any of them. The tree also
contains a CC BY-NC-ND article, which the root BSD-3 LICENSE directly contradicts.

## CLEAN, DO NOT RE-OPEN
third_party/mpm-engine-544c93dd and its -solver-core sibling both carry an MIT LICENSE fetched at
the pinned SHA. The asphalt PBR set is ambientCG CC0. The sync-to-hub.yml full-repo mirror risk is
already closed on origin/main (sparse-checkout of hf_space only, paths filter). hf_space/ is about
4 KB of README, app.py and requirements.txt, no mesh, no data.

## FIRST STEP
Quote the CCSA terms paragraph verbatim from the upstream README on disk, with its path, before
writing anything else. If you cannot find it, say so and stop that limb. Do not paraphrase a
licence from memory or from a publisher's general reputation.

## DEFINITION OF DONE
1. THIRD_PARTY_NOTICES.md naming every third-party asset, its upstream, its licence AS YOU FOUND
   IT, and UNRESOLVED where you could not find one.
2. A LICENSE scope carve-out so the root BSD-3 no longer claims third-party content.
3. The CCSA/GMU/FHWA acknowledgement drafted for the paper, ready to paste.
4. A written question for Kumar on the dataset co-authorship, in a named file.
5. NOTHING deleted and NOTHING pushed. Removal is not the remedy and you have no go-ahead.
