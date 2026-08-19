# Round 9 session titles, 2026-08-19

Overarching title: **The Round That Refuted Itself.**

Eleven parallel sessions, 96 distinct commits in one day, and the through-line was
not what any of them set out to find. Five killed their own headline, one rejected
its own passing grade, and one declined a job it had been asked to run. The
refutations are the result, not a detour from it.

Viewable board: https://claude.ai/code/artifact/2cc7e265-e85b-4a05-b6ec-ad27d774186f

Every title below is named from that branch's own commits, read live on 2026-08-19,
not assigned in advance. Commit counts are `git rev-list --count --since='2026-08-19'`.

THE TMUX WINDOWS KEEP THEIR SLOT NAMES AND MUST. `scripts/r8/r8_send.py` resolves a
target with `name == f"{TMUX_SESSION}:{a.slot}"`, an exact match on the tmux window
name, so renaming a window to its title here would break every future follow-up to
that session. Titles are for reading; slot ids are the address.

| slot | title | branch | commits | what it did to a claim already on the record |
|---|---|---|---|---|
| d11-accessor | The Floor Leaks Without a Body | claude/r9-accessor | 8 | rejected its own PASS |
| d12-kramerdata | The Job That Wasn't Run | claude/r9-kramer-extract | 5 | declined the dispatch |
| d13-renders | Photoreal, and What It Exposes | claude/r9-renders | 10 | built |
| d14-corpusbib | The Index That Couldn't See Itself | claude/r9-corpus-bib | 6 | refuted its own headline |
| d15-settle | Fixing the Band Before the Run | claude/r9-settle | 7 | pre-registered |
| d16-landing | Which Side Wins the Merge | claude/r9-landing | 6 | directed the merge |
| d17-moving | The Car That Actually Drives | claude/r9-moving-vehicle | 14 | corrected the record |
| d18-platform | Live, and the 1024-Byte Splice | claude/r9-platform | 11 | published |
| d19-priorcode | Four Codes, One Taxonomy | claude/r9-priorcode | 10 | refuted its own headline |
| d20-reader | Nobody Had Read the Round | claude/r9-reader | 5 | audited the round |
| d21-jobb | E1 Dies at Two Resolutions | claude/r9-jobb-route | 5 | refuted its own hypothesis |

## The one line each title stands on

- **d11-accessor.** The column returned `"band": "PASS"` at -0.7295 percent and the
  author refused it: std 12.519 percent, graded window spanning 34.528 points against
  a 5 point band, so the mean lands near zero by cancellation. Underneath it,
  `n_below_floor` climbs 0 to 46,926 across 180 frames with NO body, NO SDF collider
  and NO contact band, which localises the loss to the floor plane BC.
- **d12-kramerdata.** Read the manifest, found "Job C must NOT proceed on an
  assumption that job B passed", and refused. No job submitted, no SUs spent. The
  dispatch it declined was the coordinator's.
- **d13-renders.** Cycles replaces a `Poly3DCollection` painter's-algorithm plotter,
  so water refracts. `pysplashsurf.reconstruct_surface`'s own docstring is wrong about
  its units, which silently yields an invisible surface. Paint held fixed across the
  comparison set because dark paint made mesh noise read as a vehicle-quality
  difference.
- **d14-corpusbib.** The index builder cannot see 12 of the project's 20 deep searches
  and never could. 332 records are 319 distinct works.
- **d15-settle.** Criterion committed before the job existed. The job returned 400
  frames in 21 seconds, 0.052 s/frame, so the short-record problem was never blocked
  on allocation.
- **d16-landing.** The union merge must be DIRECTED: `add-ci-checks` is wrong on all
  four contested facts. CI green for two days with a check exiting 1 inside the green
  job.
- **d17-moving.** Ground-frame translation so the hull moves rather than the water.
  Every number marked UNREVIEWED rather than fake a review the dead fleet-wide
  reviewer could not give.
- **d18-platform.** Dataset, Space and W&B live. Overwrote a published physics fix on
  a PUBLIC page and was caught by d16, then built a splice detector that names the
  input making it fail and what it cannot see.
- **d19-priorcode.** Its own "does not converge" refuted by four points. An
  independent SPH code misses buoyancy by 48 percent and refining made it worse.
  P-2's zero-penetration floor is 7.9 to 10.0 percent against a 10 percent gate.
- **d20-reader.** The index of the round covers 38.7 percent of it. The adversarial
  reviewer had a zero percent success rate all round, and the only lane violation was
  the coordinator's.
- **d21-jobb.** E1 predicted the near-field offset falling 26.02 to 17.34 mm; measured
  +0.98, +0.07 and -1.14 mm across three arms, a 2.1 mm span straddling zero, and at
  g96 the sign reverses so the correction makes the ratio worse.

## State at the time of writing

All eleven branches sit 69 to 81 commits ahead of `origin/main` and NONE has been
pushed. 597 SU remain on BCS20003, expiring 2026-09-30.
