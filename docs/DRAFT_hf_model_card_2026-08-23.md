# DRAFT: model-card-style README for the Can It Ford HF repos

Status: DRAFT, nothing pushed to the Hub. Written 2026-08-23.
All repo state below was read live from the Hub today.

## First: the precondition in the prompt is not met yet

The task said "once the 4 HF repos are private". Live today, `hf repo list`
returns **ten** repos under `josiecerrell`, of which **three** are private:

| Repo | Type | Visibility |
|---|---|---|
| can-it-ford-page | space | **private** |
| can-it-ford-lab | space | **private** |
| can-it-ford-results | dataset | **private** |
| can-it-ford | space | public |
| can-it-ford-demo | space | public |
| can-it-ford-speed-surface | dataset | public |
| can-it-ford-sweep-v1 | dataset | public |
| can-it-ford-sweep-v1 | model | public |
| hicss-splat-bucket | bucket | public (588 MB) |
| can-it-ford-scratch | bucket | public |

So I do not know which four you mean, and which of them is the fourth changes
what the card should say. I have drafted against the three that are actually
private plus the two public data repos that most plausibly sit in that set.
**Tell me the fourth and I will re-point it.**

One correction while I was in there: the memory note saying the `sweep-v1`
**model** repo carries no licence is now **stale**. Read live today it has
`license:cc-by-4.0` and a `superseded` tag, updated 21 Aug 2026.

## The thing to fix before anything goes public again

All of these repos are tagged **`cc-by-4.0`, blanket**. The GitHub `LICENSE` in
this project is not blanket: it opens with a SCOPE clause saying BSD-3 covers
original code and docs and explicitly does **not** cover redistributed
third-party material, some of it "under terms that have not been established".

A `cc-by-4.0` tag on a Hub repo is an affirmative grant to the whole contents.
If any of these repos carries the derived Yaris hull, splat data, or anything
else in the unresolved column of `THIRD_PARTY_NOTICES.md`, that tag is granting
a licence that may not be yours to grant. The GitHub side already says so
carefully; the Hub side currently does not say it at all.

This is the one blocking item I would fix before flipping anything back public.
It is not a formatting nit.

## Template (drop in as the card, fill the bracketed fields)

```markdown
---
license: cc-by-4.0
language: en
pretty_name: [Pretty name]
tags:
  - flood
  - vehicle-stability
  - material-point-method
  - civil-engineering
size_categories:
  - n<1K
---

# [Repo name]

[One sentence: what is in here and what question it answers.]

*Can It Ford, NSF SCIPE REU 2026, GeoElements Lab, UT Austin (PI: Krishna Kumar).*
*Author: Josie Cerrell.*

## Licence scope, read this before reuse

The CC-BY-4.0 tag on this repo covers **the original simulation output and
documentation authored for this project**. It does not cover third-party
material that may be redistributed here, which stays under its own terms, and
in some cases under terms that have not been established. See
`THIRD_PARTY_NOTICES.md` in the source repository for the per-asset inventory.
No licence is granted here in any third-party material.

## What this is

- **Provenance:** every file read from commit `[SHA]` of
  `github.com/jcerrell-IS/can-it-ford`.
- **Contents:** [N files, M MB, folder breakdown].
- **Solver:** warpmpm. [State the engine plainly. Genesis is the abandoned
  box-proxy path and no Genesis scene has ever loaded the Yaris hull.]

## Intended use

Reproducing and re-analysing the published figures and verdicts. Method
comparison against other flood-vehicle stability work.

## Out of scope, explicitly

**Do not use this to decide whether a real vehicle can cross a real flooded
road.** The verdicts here are a necessary condition, not a sufficient one.
Specifically:

- The vehicle is **stationary**. The AR&R and Shand et al. thresholds this is
  graded against describe a stationary vehicle subjected to flow. The word
  "ford" in the project name is the mismatch, not the setup.
- The **3.0 m/s velocity cap is administrative**, set to stay below
  human-stability curves. It is not a vehicle-derived limit.
- Verdict counts are **threshold-dependent**. Quote the thresholds with the
  count or the count is not interpretable.

## Known limitations

- **Grid convergence is not demonstrated.** Displacement magnitude across the
  g48/g64/g96 ladder is non-monotone. The binary verdict is grid-invariant;
  the displacement magnitude is not. Cite the verdict, never the magnitude.
- **Resolution is coarse.** Roughly 2 grid cells across the flow depth against
  a rule of thumb near 10 particles per depth.
- **No gate here is a physics validation.** Every gate is a self-consistency or
  numerical-containment check; G-3 compares against a constant derived from the
  same pipeline, so it cannot fail for a reason external to the code, and G-6,
  P-4 and P-5 print with no pass criterion at all.
- **Inertia and CG are not prescribed**; they are whatever the solidified
  particle cloud implies. This is deliberate, not a gap.

## Citation

[BibTeX]
```

## Per-repo notes for filling it in

**`can-it-ford-results`** (dataset, private) is the strongest candidate for a
public release and already has a good description: 107 files, 1.76 MB, all read
from commit `c7f0a16ace0b`, foldered as `01_canonical_17_runs/`,
`02_l1_scenario_sweep/`, `03_multivehicle_grid_sweep/`. Two things to fix:
- Its **Dataset Viewer is broken** ("cast error", 1 failed parquet job, 0 rows).
  A public release with a red viewer banner looks worse than no viewer. Either
  fix the cast or add `configs:` frontmatter pinning only the well-formed CSVs.
- It has no Uses / Limitations sections at all. The template above supplies them.

**`can-it-ford-speed-surface`** (dataset, public) is in the best shape already:
4 configs, 413 rows, viewer works, and the card is honest that it is
PROVISIONAL and not frozen. It needs only the licence-scope paragraph.

**`can-it-ford-sweep-v1`** (dataset, public) is **empty by design** and already
carries an excellent card explaining that it holds no data and is labelled
rather than deleted because it accumulated 56 downloads while empty. Leave it
alone apart from the licence-scope paragraph.

**`can-it-ford-sweep-v1`** (model, public) is tagged `superseded` and has no
card body. It should get a two-line stub pointing at whatever superseded it.

**`hicss-splat-bucket`** (bucket, public, 588 MB) is the one I would look at
hardest before any public pass. It is by far the largest artifact, it is splat
data, and splat provenance is exactly the unresolved-licence category. I have
not inspected its contents.

## Also worth knowing before flipping visibility

Making a repo private does **not** unpublish what was already served. The
project's own record shows HF and GitHub both continue to serve old revisions,
and that removing files from HEAD did not remove them from history. If the
reason for going private is that something should not have been published,
visibility alone does not fix it, and the two hosts need separate remediation.
