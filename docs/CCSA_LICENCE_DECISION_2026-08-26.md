# The CCSA finite element models: what is published, what is owed, and what each option costs

Written 2026-08-26. Every number below was measured live in this session against `origin/main`,
not carried from a summary. This document exists so the decision is recorded rather than
rediscovered.

## What is on the public repository right now

`git ls-tree -r -l origin/main -- vehicle_geometry_research` returns **30 files,
176,252,809 bytes**. Of that, **22 files and 160,322,098 bytes** are verbatim third-party finite
element vehicle models from the Center for Collision Safety and Analysis at George Mason
University, sponsored by the Federal Highway Administration. That is 91.0 percent of the
directory's tracked bytes.

The repository is public. Every one of those bytes is world-readable and has been since it was
pushed.

## What licence they carry

**None.** Not a permissive licence, not a restrictive one, not a public-domain dedication. A
`/usr/bin/grep -r -i -E "licen|distribut|copyright|public domain|permission|all rights|redistribut"`
across all four upstream `README.md` files returns zero hits, `find` for `*licen*` or `*copying*`
across the four extracted trees returns nothing, and `unzip -l` finds no licence file inside any
archive.

**Absence of a licence is not permission.** Silence from a rights holder is not a grant. This is
the whole difficulty: there is nothing to comply with and nothing to rely on.

## The one thing the upstream authors did state, verbatim

> We ask that the CCSA at GMU and the FHWA be acknowledged for any use of this FE
> model resulting in papers and publications.

That is an acknowledgement request about **papers and publications**. It says nothing about
redistributing the model files, and **acknowledgement is not a licence**. Honouring it is
necessary and it is not sufficient.

**Status as of this document: honoured in this repository, outstanding on the paper, and
permanently outstanding on the poster,** which is already printed and submitted. See
`THIRD_PARTY_NOTICES.md` for the per-surface table.

## The options, and what each actually costs

### A. Leave it, acknowledgement met, redistribution question open

Cost: the repository keeps redistributing 160 MB for which no permission has been established.
For an unfunded student research project this is low-risk in practice and it is still an
unresolved rights question sitting on a public repository. Benefit: nothing breaks, and the hull
provenance stays reproducible end to end.

### B. Remove from `HEAD` only

Cost: **this does not unpublish anything.** Git history still serves every old revision, and
GitHub's own cached views serve them too. Anyone with a clone or a commit SHA keeps the files.
It also breaks the provenance chain for `yaris_coarse_v1l_watertight.ply`, which is the canonical
hull every gated run uses. Benefit: close to zero. **This is the option that looks like a fix and
is not one.**

### C. Remove from history with `git filter-repo`, then force-push

Cost: high, and mostly not technical. It rewrites every commit SHA after the first touch, which
invalidates **every file:line and commit citation** in `CLAUDE.md`, the corrections register and
the docs tree, across 97 remote branches and a Vista clone that is 14 commits ahead on its own
`main`. Load the `git-history-rewrite` skill before attempting it. Benefit: it is the only option
that actually removes the bytes from the public surface. Even then it does not reach forks or
third-party mirrors.

### D. Ask CCSA for permission

Cost: one email and an unknown wait. Benefit: it is the only option that can convert UNRESOLVED
into RESOLVED rather than merely reducing exposure. A drafted request is at
`docs/CCSA_PERMISSION_REQUEST_DRAFT.md`. **It has not been sent.**

## What is not affected

The `drainA` Gaussian splat is reconstructed from Josie's own video and carries no CCSA
dependency. This question does not bear on publishing it.

## Recommendation

Send D, hold at A while it is outstanding. B is not worth doing, and C should not be attempted
while the answer to D is unknown, because C is irreversible and D may make it unnecessary.

## Open sub-question, not settled

Whether the canonical Yaris model is NHTSA-hosted or CCSA-hosted. NHTSA copies carry a "public
information and may be distributed or copied" statement; CCSA copies are licence-silent. This
cannot be settled from the files on disk. **Do not assume the favourable branch.**
