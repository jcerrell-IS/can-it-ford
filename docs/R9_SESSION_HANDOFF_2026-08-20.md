# R9/R10 HANDOFF, night of 2026-08-19 into 2026-08-20

Written by the coordinating session, closing at 01:55. This supersedes every earlier handoff.
It is written to be the ONLY document a successor needs to read before acting.

**How to read this.** Every number was read live or is attributed to the commit that measured
it. Claims that were relayed rather than read say so. That distinction is not politeness: the
coordinator relayed five claims tonight that the receiving sessions then refuted, and every one
distorted toward the stronger version. Section 12 lists them.

**Start here if you read nothing else.** Sections 1, 2, 11 and 13. Section 1 is the physics
result. Section 2 is the pattern that explains why the round went the way it did. Section 11 is
Claude Code operational knowledge that is worth more than any single finding. Section 13 is the
per-slot prompts, ready to send.

---

# 1. THE RESULT: JOB B IS SOLVED, AND THE ANSWER IS UNCOMFORTABLE

**WITHDRAWN AT 02:10 BY ITS OWN AUTHOR, commit `87ae518`. Read this before anything else in
the section.** The heading of this section as first written was "the force accessor is
exonerated". **IT IS NOT.** d21-jobb ran both adversarial attacks itself, after three subagent
reviews died (two on process crashes, one on the weekly limit), and BOTH LAND.

**What survives, verified by source read.** The NARROW independence claim holds: no collider
path writes particle stress or `particle_F` anywhere, a grep returns NOTHING, and every collider
writes `state.grid_v_out` and only that. The two readers genuinely share no code and no node set.

**What fails.** The p2g2p substep order is `compute_stress_from_F_trial`, then p2g, then GRID OPS
INCLUDING THE COLLIDER'S PROJECTION onto `grid_v_out`, then g2p. So particle F at substep n+1
comes from a grid velocity the collider modified, and `cauchy()` is `stress()/det(F)`.
**PARTICLE STRESS IS CAUSALLY DOWNSTREAM OF THE COLLIDER.** Worse for the framing: in a steady
state, **momentum conservation makes the two readings approximately equivalent BY CONSTRUCTION**,
because the control-volume balance is the same bookkeeping read at a different surface.

**WITHDRAWN: "the accessor is exonerated" and "the whole force-is-mis-read family is closed".**

**WHAT STILL SURVIVES, AND IT IS NOT NOTHING.** Agreement to under 2 percent excludes every
defect that would BREAK the momentum balance, which is most of the ways an accessor is actually
wrong: a bad `dt`, a sign error, a double count, a missing or duplicated node set, a wrong mass.
**Not excluded is a fluid state that is itself biased, which is a PHYSICS problem and not an
ACCESSOR problem.**

**The correct sentence, and the one to quote:** `sdf_wrench`'s momentum bookkeeping is
self-consistent to under 2 percent against an independent surface, which is what a
momentum-conserving solver forces.

**So the standing position is:** the fluid appears to push about 35 percent harder than analytic
buoyancy, the disturbance is confined to the floor, and the measurement chain is
self-consistent but NOT independently validated. Treat the 1.35x as a property of the simulated
fluid state, whose correctness is the open question.

## 1.1 The chain, each link killing a hypothesis

| # | hypothesis | how it died | commit |
|---|---|---|---|
| 1 | near-field surface-offset (E1) | predicted 26.02 mm at g64 falling to 17.34 at g96; measured +0.98, +0.07, -1.14 mm, a 2.1 mm span straddling zero, and at g96 the SIGN REVERSES so the correction makes the ratio worse, 1.310 to 1.342 | `054594d` |
| 2 | static pressure bias | mean gradient right to -0.67 +/- 3.31 pct, Job B 10 to 19 blocked SE away, so a MEAN-GRADIENT error is excluded. Narrowed by its own author when the column was found never to quiet | `1f98170`, `f673c45` |
| 3 | volumetric locking | PPC sweep at fixed grid, 3.375 to 64 per cell, up to 4,784,798 particles: k_fit 0.687, 0.726, 0.727, 0.829, log-log slope +0.0596 where PPC^-2 predicts a 98.4 pct fall. FLAT. Locking requires a RISE | `3f4c1ec` |
| 4 | quadrature error | excluded TWICE independently: Steffen 2008 reports no one-signed bias, and KE/PE RISES with ppc at 9.89 sigma where quadrature predicts a fall | `03cd132` |
| 5 | "the two accessors disagree" | THEY SHARE A NUMERATOR. `sphere_heave.py:782` takes ONE `fz`; `:818` and `:819` divide THAT SAME `fz` by two denominators. Criterion 3 never graded a force, it graded a normalisation | `ea1d385`, `f0bdb0f` |

## 1.2 The measurement that closed it

`control_volume_force` reads `cauchy()` and `vol()` only: fluid state, sharing no code, no grid
nodes and no knowledge of the collider with `sdf_wrench`. Top face above the free surface so its
traction is zero, side faces the slip walls at friction 0.0, bottom face clear of the floor,
shear COMPUTED not assumed away.

g64 bcfix, sub 113.77 mm, analytic 44.630 N, `sdf_wrench` 60.476 N, ratio 1.3551:

| box | Fz_cv | ratio | conditioning |
|---|---|---|---|
| L=0.18 z=0.38 | 61.373 | 1.3752 | 21.94 pct |
| L=0.22 z=0.38 | 61.613 | 1.3805 | 14.68 pct |
| L=0.22 z=0.30 | 61.009 | 1.3670 | 9.75 pct |
| L=0.30 z=0.30 | 66.402 | 1.4878 | 5.22 pct, worst conditioned |

Three well-conditioned boxes agree with `sdf_wrench` to **0.9 to 1.9 percent**, against a verdict
written into `run_r9g.sh` BEFORE the run: "cv_fz also ~1.35x means THE FLUID REALLY IS PUSHING
THAT HARD and the accessor is sound". Commit `f7f0c89`.

## 1.3 THE REVIEW HAPPENED, AND THE AUTHOR RAN IT ON THEMSELVES

**Resolved at 02:10.** The two attacks below were run by d21-jobb after every subagent route
failed, and both landed. See the withdrawal at the top of section 1. This subsection is kept
because the attacks are the reusable part, and because the sequence, three failed reviews then a
self-run one that overturned the author's own headline, is the strongest single argument in this
document for keeping an adversarial pass in the loop.

Three adversarial reviews were launched tonight. The first two were killed by parent-process
crashes. The third died on the account's **weekly limit**, having got as far as writing
"Now the solver internals. This is where the independence claim lives or dies."

The two attacks it had not finished, and they are the right two:

1. **Are the accessors genuinely independent, or two readings of the SAME corrupted fluid
   state?** `control_volume_force` reads `cauchy()`, which is particle stress. If the coupling
   wrote that stress, the two readings share an upstream quantity and agreement proves nothing.
   **This is the single question that can void the night's headline result.**
2. **Was "well-conditioned" defined before or after the four box numbers were seen?** If after,
   excluding the 5.22-percent box is post hoc and the honest spread is **1.367 to 1.488**, not
   0.9 to 1.9 percent.

## 1.4 The next measurement, and the literature now names its mechanism

The bulk pressure field is hydrostatic and the anomaly sits at the bottom boundary. Tonight's
deep-research run returned three CONFIRMED claims that land exactly there. See section 5.2.

---

# 2. THE PATTERN: TWELVE INSTRUMENT FAILURES IN ONE NIGHT

**Every one is the same shape: a code path that returns a value indistinguishable from a
measurement when it could not measure.**

| # | instrument | how it failed toward looking correct | found by |
|---|---|---|---|
| 1 | `stationarity.py` | `n < 10` returned 0.0, and 0.0 is the pass value | d15, own |
| 2 | `grep -c ... \|\| echo 0` | "0\n0" is not an integer, comparison errored, fell to else | d18, own |
| 3 | `all([])` | verdict True over zero data | d12, own |
| 4 | add/add merge control | both arms returned 1 because the branch did not exist | d16, own |
| 5 | `--query` | matched title and abstract, NEVER authors, so 0 was unreachable-not-absent | d14, own |
| 6 | `r8_preflight.sh` | checked CLAUDE.md drift, silently ignored the authority skill | d20 |
| 7 | `gh run view --json` | `conclusion: success` on a step that exited 1 | d16, own |
| 8 | mesh acceptance checks | watertight, manifold, right bbox, 10x triangles, all on a one-blob-per-particle mesh enclosing 0.0002 m3 instead of 1.457 | d13, own |
| 9 | caption strip | CLIPPED the very number it was asked to carry, silently | d13, own |
| 10 | WebSearch | returned zero on a dead model pin, reading exactly like absence | d22 |
| 11 | control-volume synthetic check | pressure and weight consistent BY CONSTRUCTION, blind to conditioning | d21, own |
| 12 | PDF scrape by filename | 2 wrong files in 13 scraped, a 15 pct error rate, one a website Terms and Conditions page | d22, own |

**Number 11 is the one to carry into any future numerical work.** The tank-wide control volume
returned **-162.6 N against 44.6 analytic**, and it was not an algebra bug: `p_face*A = 4254.85`
against `W = 4417.45`, so the answer is **1.05 percent of either term**, and a 1 percent error
anywhere becomes a 95 percent error in the result. Its synthetic check passed at -1.38 percent
because its pressure field and weight were consistent by construction.

**The general rule: report a conditioning number beside every differenced quantity.** Shrinking
the box moved conditioning 1.05 to 21.94 percent, a factor of 21, with the answer unchanged.

**And the meta-fact: eight of twelve were caught by their OWN AUTHORS, after publication. The
review layer caught none, because it was dead all round.**

---

# 3. WHAT EACH SESSION ESTABLISHED

155 distinct commits since 17:00 across fourteen branches. Context pressure at 01:48 in
brackets, because the high ones will compact and lose working state first.

- **d11-accessor** `claude/r9-accessor` [55 pct]. Pre-registered a hydrostatic column BEFORE the
  run. Rejected its own PASS on dispersion, then found the rejection was itself an
  over-correction because it used a raw std where criterion 3 mandates a BLOCKED SE. Diagnosed
  the scatter as ACOUSTIC RINGING and proved it: tau_int 1.78 and 2.51 frames against a
  2.447-frame one-way acoustic transit at c = sqrt(K/rho) = 12.2585 m/s. Found **the column
  drains with NO BODY in it**, `n_below_floor` 0 to 46,926 over 180 frames. A ONE-LINE engine
  A/B (`if dotproduct < 0.0` against `<= 0.0` at `mpm_solver_warp.py:1955`) fixed **96.40
  percent** of the leak. Then found the column NEVER GOES QUIET, KE/PE growing to 11 orders
  above Quinlan's machine-zero standard, and corrected its own exoneration. Committed the run
  JSONs and a reduction script after an audit found the headline lived in a scratchpad one-liner.
- **d12-kramerdata** `claude/r9-kramer-extract` [42 pct]. **REFUSED to submit Job C** on the
  recorded ladder-stop, spending zero SUs, and was right. Established from source that criterion
  3 grades a normalisation, not a force. Pre-registered FOUR criteria against FOUR outcomes so
  the measurement picks the answer rather than the author. Caught its own `CODE_META` claiming
  nothing was transcribed while being hand-transcribed. Corrected a coordinator citation: the
  impulse is at `mpm_solver_warp.py:2733`, not `:2732`, which is the `grid_m` fetch.
- **d13-renders** `claude/r9-renders` [69 pct, HIGHEST]. Cycles path tracing replaced a
  painter's-algorithm plotter. Found `pysplashsurf.reconstruct_surface`'s docstring **wrong about
  its units**. Priced the mesh swap and REFUSED it with numbers: the waterline crosses the
  ROCKER, so a substituted body moves the drawn waterline **1.78x at the median, 4.08x at p25,
  27x at p5**, and 45.2 pct of waterline contact is shallower than 30 degrees. **The smoothest
  Rogue on disk is missing 47.6 percent of the car**, which closes the free-fix route. Held paint
  FIXED across the comparison set because dark paint made mesh noise read as a quality difference.
- **d14-corpusbib** `claude/r9-corpus-bib` [42 pct]. **The corpus index holds NO FULL TEXT**: 15
  fields, none a body or PDF, largest text blob 3,477 characters, 110 of 332 records with no
  abstract, built from 8 of 21 deep searches. `--query` matched title and abstract, NEVER authors.
  Then ABSORBED 75 lines to turn the hardest merge in the landing sequence into a fast-forward,
  and said plainly it had invalidated another session's measurement in doing so.
- **d15-settle** `claude/r9-settle` [46 pct]. **Velocity equilibrates and displacement CANNOT**,
  because displacement integrates velocity, so no window of it is stationary at any length.
  400 frames costs 21 seconds. **The terminal-frame problem demonstrated**: distance peaks
  0.667127 m and ends 0.290845 m, **43.6 percent of its own peak**, which gives CLAUDE.md item 5
  a MECHANISM. Found 35 comparable long records already existed, so a claim that needed new runs
  did not. Wrote the third-class rule: classify the quantity before choosing a window.
- **d16-landing** `claude/r9-landing` [39 pct]. The branch is **5 BEHIND as well as ahead**, and
  the behind count has been stable at 5 at every measurement while ahead moved 64 to 82. CI green
  for two days with a check exiting 1 inside it. Refuted the coordinator's register row C1 with a
  two-arm control. Produced an **execution card**: one merge, seven files, zero decisions, and
  "read nothing above it".
- **d17-moving** `claude/r9-moving-vehicle` [57 pct]. Ground-frame moving vehicle, two videos
  delivered and frame-counted FIVE ways. Closed C-1, the only item the readout listed as unowned.
  The crowned road cuts load **36.5 percent** level-fixed, but the depth-matched difference
  **REVERSES SIGN** between 2 and 4 percent camber, -18.6 to +6.0. Three of its encode failures
  printed success, including `which ffmpeg` passing on a binary that cannot load.
- **d18-platform** `claude/r9-platform` [52 pct]. Dataset, Space and W&B live. Caught its own
  overwrite of a published physics fix. **The whole r9 wave is invisible to W&B except one run
  pushed by hand.** Refuted the coordinator's HF claims twice.
- **d19-priorcode** `claude/r9-priorcode` [42 pct]. Prior art is **at least fourteen works**,
  every DOI resolved against Crossref, and **the shipped paper cites ONE**. Found `alqadami2022`
  resolving to TWO DIFFERENT PAPERS in two bib copies. Refuted its own "does not converge"
  headline on four points. Established the Zhao 2019 in/outflow BC is **absent from all 16 remote
  heads of public Anura3D**.
- **d20-reader** `claude/r9-reader` [67 pct]. Read **18 transcripts totalling 42,021,315 bytes**
  and 42 commit bodies in full. Found the research-corpus skill in **FOUR states across nine
  worktrees**, with eight of nine sessions unable to see a night of corrections, and the
  propagation damage timed to the minute: fix at 00:21, sibling committed the pre-fix claim at
  00:43. **Every dispatching session has 76 MCP connectors and every dispatched session has 17,
  with ZERO bridged claude.ai connectors.**
- **d21-jobb** `claude/r9-jobb-route` [68 pct]. E1 refuted at two resolutions. Locking refuted on
  its PPC signature. Withdrew its own non-convergence claim after finding the ladder's operating
  point moved with resolution. Built the third accessor AND `docs/CANDIDATE_PAPER_SCOPE_TEST.md`.
- **d22-gapscan** `claude/r9-gapscan` [47 pct]. Want list **261 distinct works**; 68 reachable,
  162 not; barriers counted at 105 closed, 49 no-DOI, 57 OA-but-host-refuses. Found WebSearch
  dead on the same model pin as the Agent path. **Two wrong files in thirteen scraped, a 15
  percent error rate.** Built `docs/r10/pdftext.swift`, a PDFKit text extractor, because this Mac
  has no pdftotext, no numpy and no PyObjC. Then found **26 of the 49 "no DOI" works DID have
  DOIs**, one of them sitting in this project's own register while its resolver called it
  unfindable.
- **d23-overleaf** `claude/r9-overleaf` [25 pct]. Confirmed the paper's class claim fails the axis
  it claims to pass. Found the paper falls back on displacement magnitude, **the one quantity its
  own data shows is unconverged**, and that at 2337 kg the sequence falls on BOTH resolution legs
  so the SIGN is not consistent across masses. Audited all seven figures: build sound, flat paths
  resolve, and **the one figure the paper calls pinned to primary sources is the one figure no
  script in the repository produces**.

---

# 3A. THE COMPLETE COMMIT RECORD, EVERY SESSION, IN ORDER

Section 3 gives one paragraph per session. This is the full record: every commit each slot
landed tonight, oldest first, so the SEQUENCE of self-correction is visible. That sequence is
the actual finding. Read a session's list top to bottom and you can watch it build a claim,
test it, and in most cases overturn it.

Commits on `claude/r9-overleaf` before 02:0x are inherited from its base branch and are the
coordinator's; that slot launched at 01:18.


## d11-accessor, `claude/r9-accessor` — 17 commits

- `8f978c1` Job B FAILS at every window, and I retracted my own answer to the floor question
- `05fb6db` The floor question is OPEN and my retraction did not close it, said plainly
- `e4e05a8` Downstream enumeration completed: 13 sites not 6, and my "same content" claim was wrong
- `0e8ef48` LADDER STOPPED. Decision recorded, three items left open, and no window avoids the FAIL
- `61197f9` The 0.3 percent is a MOTION tolerance, so reason 3 of the ladder decision is withdrawn
- `da438d7` PRE-REGISTRATION: hydrostatic column, bands fixed before the run exists
- `7ab303a` The column PASSED and the PASS is worthless, because my own criterion had no drift gate
- `1f98170` Gates added, and my NOT-GRADEABLE retraction was itself an over-correction
- `cff4ec6` The floor leak is a floor-plane defect: 96.40 pct fixed with no body in the domain
- `c692b21` Well-balancedness diagnostics, and I could NOT do this from the files I had
- `f673c45` The column never goes quiet, which WEAKENS my own exoneration of the solver
- `347f4ad` My 285 Pa "sits between" was wrong, and a locking test that needs no engine change
- `9d82ed2` Grading rule amended BEFORE any result was read: three candidates, and the 8-to-27 leg
- `03cd132` KE/PE RISES with particles per cell at 9.89 sigma: quadrature and sampling both excluded
- `3a6c9b3` Audit upheld the direction and broke my provenance: the reduction is now a committed script
- `2d472ba` B2 is one instrument with two normalisations, and I am NOT respecifying it yet
- `c621539` The floor writes VELOCITY not pressure: neither SPH fix has an analogue, and that is the finding

## d12-kramerdata, `claude/r9-kramer-extract` — 7 commits

- `94b56b8` The 0.3 percent is the paper's own abstract, not corroboration, and the threshold I added is the one that turned out to be load bearing
- `46929a1` The dependency map, because an over-broad correction is still an error: the laminar finding never routed through the transcription
- `09336b8` I did not submit Job C, and BLOCKER-B1 is resolved: the artifact that unblocks it is the archive I spent the round extracting
- `d9dfb0e` B3 closed at its source, and writing the failing input proved my own gate did not catch it
- `f0bdb0f` Criterion 3 never graded a force, it graded a normalisation, and the period is the probe that separates the cases
- `8c2acbb` Four outcomes, four criteria, bound before the number exists so the measurement picks and not the author
- `0024ac1` Outcome B, adopted verbatim, and the measurement broke two of my own clauses on the way in

## d13-renders, `claude/r9-renders` — 17 commits

- `256d013` Half the car was one clamp away from rendering as sky, and there was no ground at all
- `d55ac14` RECOVERED from a crashed session: the Blender Cycles path, untested
- `3d01611` The water was one blob per particle because the library's docstring is wrong
- `c0fa82b` Both surround failures looked like lighting and both were meshing
- `4026760` My own docstring claimed a default the code did not have
- `52dcf9a` The road and the flood were one mirror because nothing in frame was ever dry
- `0051379` The hulls melt because of their own meshes, and the larger-domain run needs 3 lines
- `6a0b52f` I ran every guard against the input that should break it, and one order matters
- `cd52357` A still asserts the SLIDE verdict; 45 frames show it
- `21bfca3` Dark paint exposes the mesh, so varying it across a comparison is a confound
- `03df8f4` The 9 cm step is real and is not the seam; the seam is a 40 cm wavy edge
- `cdcc4a0` Swapping the body moves the waterline 1.78x, and 27x over the shallowest 5 percent
- `bd278a2` B6 closes: the HDRI is ambientCG CC0, and the same commit that shipped it gitignored the meshes
- `ca5d906` The corpus does hold the prior art; the query predicate cannot see authors
- `24c707d` The smoothest Rogue on disk is missing 47.6 percent of the car
- `48d7063` The caption clipped the very number it was asked to carry
- `733c149` A 22 m domain deletes the surround, the taper and the patch rectangle together

## d14-corpusbib, `claude/r9-corpus-bib` — 9 commits

- `026f931` The skill said the physics test does not exist while recommending someone build it
- `7647e6d` An absence found by a search that cannot match is not an absence, including mine
- `6ecf4e5` The builder cannot see 12 of the project's 20 deep searches, and never could
- `5680a20` The adapter reproduces the markdown route exactly, and 332 records are 319 works
- `849a07f` My own headline was an absence found by a search that could not match
- `6ff3f14` The index holds no full text, and wiring the ingest path found a duplication bug first
- `d659169` Both reader findings were false positives, and the second one inverted the truth
- `77994af` The union merge is now a take-mine, because I made d16's measurement false
- `de18180` The amplifier was the relay, and a half-fixed tool is worse than a missing one

## d15-settle, `claude/r9-settle` — 12 commits

- `e50191b` The asymmetric rule costs 16 verdicts one way and every error bar the other
- `836ea52` 16 SLIDE / 1 STUCK was computed under the correct rule, and a third class obeys neither
- `404543b` 5 of 24 is channel-invariant member-for-member, and it is the only bare-quotable number
- `304b6bb` I reported a tautology as a measurement, and the corrected claim is stronger
- `ee6a0bc` Pre-registration for the long-record test, committed before the job is submitted
- `da0e8ce` Velocity equilibrates and displacement cannot, and 400 frames costs 21 seconds
- `46f73ed` B4: the population was 21, not 25, and no conclusion moves. Item 5 gets a mechanism.
- `0734dcb` d21's test refutes my own Q2 magnitude: direction survives 8 of 8, size does not
- `aa6684a` Section 19 was false: 35 comparable long records already existed, and the split replicates on them
- `27b83c2` The third class becomes a rule: classify the quantity before choosing a window
- `bed9d35` The paper's safest-looking quantity is its least defensible, and item 5 understates why
- `1ea9f49` Item 5 is missing its third mass row, in liftable form

## d16-landing, `claude/r9-landing` — 8 commits

- `8c07765` The add/add conflict is real: content ancestry and merge behaviour are independent
- `61104f7` The CI has been green for two days with a check exiting 1 inside it, and there are five conflicting files not one
- `ca45222` Two public writes landed before their decision, and the one I called a revert was not one
- `293ee21` The union merge must be directed: add-ci-checks is wrong on all four contested facts
- `8c03f32` The behind count has been 5 at every measurement while the ahead count moved 64 to 82
- `179e9e5` The sequence: phase 1 first, and the register conflict is the only one still growing
- `be69592` Execution card: one merge, seven files, zero decisions, and read nothing above it
- `6719728` The card holds after the push, and the masked-failure prediction was tested in advance and held

## d17-moving, `claude/r9-moving-vehicle` — 21 commits

- `98d4d9d` RECOVERED from a crashed session: speed-surface work as it stood
- `159bf7d` The split-dependence is general, grows with speed, and its worst case moves
- `498f1ad` All four arms completed: g96 now has a floor, and the grid result held
- `c94f3f8` Fixed-seed determinism holds only near rest, and the bc guard was self-bypassing
- `519362a` g128 cuts the load 43 percent and halves S, so one of my own claims is withdrawn
- `edc4447` I proposed a confound for my own g128 result and a held-fixed control refuted it
- `9990644` The g128 collapse reproduces on a second seed, 0.18 percent apart
- `050ff22` The headline pair belongs to the late window and is 2.24x, and it does not invert
- `51c158b` C-1 RESOLVED: the pair inverts because the two numbers are different windows
- `b65dc0d` A moving car for the render, plus C-16 fixed and C-19's name corrected in place
- `456578c` A crowned road against a flat plane, with the equivalence gate as phase 0
- `4d4b57d` Mark every number UNREVIEWED, and correct the record: the bc guard is NOT fixed
- `1f880ac` The video: frames verified from the arrays, and the picture was wrong not the physics
- `23bc800` The videos are delivered, and two of the three encode failures looked like success
- `4120e99` The crowned road IS the paired comparison, and it cuts the load 36.5 percent
- `9ad7a98` Correct "actually drove" at the root, and write the crowned road up as novelty
- `136fff9` The crown decomposition ran, and the depth-matched difference FLIPS SIGN
- `f939d05` C-1 finished: placement confound CLOSED by measurement, and the rule it needed
- `38e6802` The general form of the moved-operating-point failure, with camber as its example
- `a0c4c96` The sign reversal is the finding, and it is 194 and 41 standard errors from zero
- `c1dad7f` Actually put the significance in T36: a0c4c96's message claimed it and it did not

## d18-platform, `claude/r9-platform` — 16 commits

- `6d761e7` The Space claimed Genesis, a superseded density and no verdict, and all three were wrong
- `c7000ea` Zenodo mints a DOI for a RESTRICTED record, so citability does not require publishing
- `a08b6eb` I cast a doubt I had not tested, and testing it took one command and refuted it
- `3016b16` A PUBLIC EMPTY DATASET ALREADY SITS ON THE HUB UNDER THIS PROJECT'S NAME
- `f988882` Eleven live worktrees never see the CI warning, and my own test for it answered from an error
- `866238a` The published surface is the transient one, and the settled one inverts its headline pair
- `e0eabac` PUBLISHED. Dataset, Space and W&B are live, and two checks that could never fire now can
- `bef6da0` I overwrote a published physics fix on a PUBLIC page, and d16-landing caught it
- `abac36f` Read before you write to a public target, and the CI is instance six
- `5692f1e` The board's append pattern splices rows above 1024 bytes, and 64 percent of ours are
- `ce730c3` A splice detector that names the input making it fail, and names what it cannot see
- `83e99f5` "Six public empty shells" is refuted: usedStorage counts LFS only, and the populated repo is the model
- `e11db07` The sweep-v1 pair is a split, not a double creation, and the landing hazard is closed
- `f07b174` The whole r9 wave is invisible to W&B except one run I pushed by hand
- `e44b22e` Fill can-it-ford-results: 107 files, ten sections, every file read from a commit
- `3f66ba1` Offline-then-sync is right either way; the viewer was dark; and I published a third licence

## d19-priorcode, `claude/r9-priorcode` — 16 commits

- `a863ee7` P-2's zero-penetration floor is 7.9 to 10.0 percent against a 10 percent gate, measured on all 17 runs
- `f31a71f` An independent SPH code misses buoyancy by 48 percent and refining made it worse
- `0a83b75` The vehicle-fording case is one build target away, and the review failed twice
- `4d7c2c1` A fourth code refutes my own headline: the dt is what the formulation implies
- `2f3a4a9` Three families of force extraction, and why nobody could see the P-2 write-up
- `bd2ef56` The dt confound was mine to raise and mine to kill: the divergence is real
- `1419994` IBAMR settles the taxonomy by implementing both behaviours in one codebase
- `d4369c3` Chrono ships the body-following domain the render needs and forbids it for water
- `a720fea` The ladder converges, so my own "does not converge" is refuted by four points
- `ccca082` A quantity can fail to converge because of what it IS, and the vehicle target built
- `bdb86cb` One bib key points at two different papers, and the prior art is 14 works not four
- `9910cb8` Lyu 2024 is in neither container, and two of my three predicates were wrong
- `705a960` The shipped paper cites ONE of fourteen, and the key collision is not in it
- `0bcacfa` RTF 92.4 for a vehicle on SPH terrain, and I searched for a DOI I had just written
- `89bd57f` A count that grows while you measure it is measuring your own activity
- `dc1a949` Neither candidate bib is authoritative, and the novelty claim is papers-only

## d20-reader, `claude/r9-reader` — 4 commits

- `faf53d1` The research index never contained the project's own deep searches, and the skill said so wrongly
- `7a0d08a` Register C1 was wrong about git: content ancestry and merge behaviour are independent
- `a6e9f56` Nobody had read the whole round, and the index of it covers 38.7 percent
- `9c19364` The reviewer had a zero percent success rate, and the only lane violation was the coordinator's

## d21-jobb, `claude/r9-jobb-route` — 14 commits

- `0ed6bcb` The estimator hypothesis is not a long shot: it fits BETTER than the band
- `77c274c` E1 is now ONE hypothesis, not three, and my own test bit before the GPU did
- `21dbbee` A ceiling on E1 was already in the payloads, and the 2h job was the wrong shape
- `d363a1d` E1 IS REFUTED. The FAIL is a solver defect, not an instrument artifact
- `054594d` The g96 arm could have rescued E1 and it did the opposite: the sign reverses
- `7391ef9` 918450 is a ONE-CHARACTER ENGINE FORK, and the leak explains a third
- `bb46996` The 2x2 refuted half my own pre-registration, and that half is the finding
- `d826c8a` FLAT in PPC over 8x: the plateau signature holds, and two relayed claims do not
- `3f4c1ec` Locking refuted on its own PPC signature, and I withdraw my own convergence claim
- `9e4d72a` Second correction to the same claim: the direction survives, the magnitude does not
- `aa20be2` Amicarelli read in full: half the relayed claim holds and it is the wrong half
- `ea1d385` A THIRD accessor that never touches the body, and the scope test as a reusable file
- `f7f0c89` A THIRD accessor confirms the force to under 2 percent: the accessor is exonerated
- `87ae518` Both attacks on f7f0c89 land. "The accessor is exonerated" is WITHDRAWN

## d22-gapscan, `claude/r9-gapscan` — 22 commits

- `faf53d1` The research index never contained the project's own deep searches, and the skill said so wrongly
- `7a0d08a` Register C1 was wrong about git: content ancestry and merge behaviour are independent
- `c621931` The corpus counts were wrong, the reviewer has been dead all round, and the preflight could not see a stale skill
- `e81bc9c` The banner told every session a false thing, and the register served a claim its author had withdrawn
- `95167b0` The round's only coordination artifact was in no commit, and its append pattern corrupts above 1024 bytes
- `88cba09` Two HPC bugs the project had solved and filed where no session loads them, and a refuted novelty claim
- `505aef7` Every session ran the whole round in bypass and none ever entered plan, because one line said so
- `854d164` The constitution now says where a finding goes, and @import stayed out because I could not test it
- `8a5b56b` The fixes worked, but not by improving propagation, which was already working
- `63de3bb` An empty answer and an unreachable host looked identical, so the watcher buried two running jobs
- `436db70` Name the eleven sessions from their own commits, and do not rename the windows they answer to
- `dd44e2f` Six papers read from full text, and one of them predicts Job B's number, sign and refinement behaviour
- `754af7f` The solver has no locking mitigation at all, and its fluid update is the exact line F-bar replaces
- `27f0996` The paper cited for the wall artefact measures the one stress component a buoyancy error is not made of
- `c469252` Two live searches returned zero because they had stopped evaluating, and the control is what caught it
- `e5b5b18` Every fetch attempt with its HTTP code, so a refusal cannot later read as an absence
- `47ab55a` My own scraper fetched the wrong paper once, and the filename would have hidden it
- `b512871` A second wrong file was sitting in the set, and the fix is that nothing gets saved until its own text is read
- `7d386f0` The 49 works I called DOI-less were mostly my query failing, and 17 of them now have a verified id
- `57dd75a` Thirty-eight of thirty-eight now verified against their own text, and the verifier that said otherwise was the one that was wrong
- `52e7d7f` I checked my own quotations against the pages and one of them was wrong
- `5213f6f` The five papers the accessor result makes most on-target are the five I could not get

## d23-overleaf, `claude/r9-overleaf` — 27 commits

- `faf53d1` The research index never contained the project's own deep searches, and the skill said so wrongly
- `7a0d08a` Register C1 was wrong about git: content ancestry and merge behaviour are independent
- `c621931` The corpus counts were wrong, the reviewer has been dead all round, and the preflight could not see a stale skill
- `e81bc9c` The banner told every session a false thing, and the register served a claim its author had withdrawn
- `95167b0` The round's only coordination artifact was in no commit, and its append pattern corrupts above 1024 bytes
- `88cba09` Two HPC bugs the project had solved and filed where no session loads them, and a refuted novelty claim
- `505aef7` Every session ran the whole round in bypass and none ever entered plan, because one line said so
- `854d164` The constitution now says where a finding goes, and @import stayed out because I could not test it
- `8a5b56b` The fixes worked, but not by improving propagation, which was already working
- `63de3bb` An empty answer and an unreachable host looked identical, so the watcher buried two running jobs
- `436db70` Name the eleven sessions from their own commits, and do not rename the windows they answer to
- `dd44e2f` Six papers read from full text, and one of them predicts Job B's number, sign and refinement behaviour
- `754af7f` The solver has no locking mitigation at all, and its fluid update is the exact line F-bar replaces
- `ac0f0d8` I relayed a subagent's reasoning as the paper's finding, one hour after writing up that exact failure
- `7500647` The router sent every citation check to an OAuth-dead connector, and Undermind was not in it at all
- `2c2e9e1` Relaying delivered four of six and carried two claims wider than their source
- `e9ff33f` Both headline results are carried by a markdown file and no data, and one number matches no field on disk
- `93fa50c` Both gates read the right field and still blocked real work, and one had never matched the form its own comment named
- `38cdbeb` The skill-drift check compared length, which is the identity test this project's own skill forbids
- `1e89a68` Every session ran at max effort because one line said so, and reading the plan by position hid it
- `e585b7a` Every dispatching session has 76 connectors and every dispatched session has 17
- `833e8aa` The fleet could see that work happened and not that a reply was owed, and the idle detector was reading pre-crash files
- `03d2bd6` The R10 findings are 784 KB outside git, and a published artifact's zero-limits conclusion is falsified
- `617f34b` The guard against blind interruption became the likeliest cause of a missed dispatch
- `82640de` The class the paper called its only genuine match is the one that fails the axis it said it never measured
- `d10f356` The paper refused the unfounded verdict and fell back on the one quantity its own data shows is unconverged
- `cb6617a` The figure the paper calls pinned to primary sources is the one figure nothing in the repo can redraw

**Total: 190 commits across thirteen slots between 16:00 and 02:20.**

---

# 4. THE LITERATURE, READ FROM FULL TEXT

## 4.1 What was read, and what could not be

`docs/R9_CORPUS_READ_2026-08-19.md` carries the working. Read in full via connector: Wallstedt
and Guilkey 2007, Steffen 2008, Miyamoto 2023, Quinlan 2018, Zhao Jiang Choo, Negi 2022. Later,
via d22: 38 of 38 acquired files verified against their own text.

**What could NOT be read, counted rather than estimated:** of 230 works from the deep searches,
**68 reachable and 162 not**. 105 closed with no OA location anywhere, 49 that never resolved to
a DOI (since reduced to 23), 57 that ARE open access but whose publisher host refuses a plain
client, concentrated in ScienceDirect, MDPI, Wiley and Springer. That last group is recoverable:
scraping the landing page for `citation_pdf_url` and re-requesting with a Referer got 8 of 24.

## 4.2 Findings that survived reading

- **Wallstedt and Guilkey 2007.** The mass-weighted projection is exact only for linear fields
  under symmetric particle placement; for non-linear fields more particles-per-cell does not
  remove the error, which reaches a GRID-SET plateau. **Two claims the coordinator relayed are
  NOT in the paper and are withdrawn**: the "constant systematic bias for a fixed body" framing,
  and the O(h) scaling, which was read off a figure by eye when the paper's own reference has an
  h^2 grid term.
- **Steffen 2008.** Quadrature error with B-splines analysed at length, and it explicitly finds
  **NO one-signed bias**. Quadrature is out as an explanation for a systematic offset.
- **Quinlan 2018.** Hydrostatic tank where kinetic energy decays to **machine zero, 1e-13 to
  1e-18**, with second-order pressure convergence. Ours GROWS.
- **Zhao, Jiang and Choo.** Volumetric locking; strip footing over-predicting rigid-body bearing
  capacity **45 to 55 percent** and NOT remedied by refinement, with a finer grid making it
  worse. Correct citation is **IJNME 10.1002/nme.7347, NOT CMAME**, which the coordinator got
  wrong repeatedly.
- **Amicarelli 2015.** Read in full by d21 after the coordinator relayed it: half holds and it is
  the WRONG half. The 10 percent is a peak PRESSURE COEFFICIENT, not a force. The boundary
  treatment is not named as the cause; the attribution is implicit by comparison. And three scope
  facts disqualify it INDEPENDENTLY, any one sufficient: purely SPH with a non-computational
  neighbour grid so **no velocity projection anywhere**; Adami dummy wall particles this solver
  does not share; and a 2D impinging jet with a real free stream against our hydrostatic scene at
  `mach_peak = 0.0`, where there is no stagnation point to over-predict.

## 4.3 THE BENCHMARK NEGATIVE, AND IT IS A RESULT

**No canonical floating-body benchmark states a quantitative tolerance on a static FORCE.**

- **SPHERIC Test 12**, fetched live: 10 x 5 x 29 cm prism, relative density 0.68, mass 0.986 kg,
  inertia 14 kg cm2, body 2.11 m from the flap wavemaker, probes at x = 1.16 and 2.66 m,
  reference data from Hadzic 2005 and Xing-Kaeding 2006. It **states no tolerance, no acceptance
  criterion and no error percentage**, and forces are **inferred from motion, not measured**.
- **SPHERIC Test 14** is free heave of an axisymmetric round-based body, structurally closer.
- **Kramer 2021's 0.3 percent is a MOTION uncertainty on drop height**, not a static force band.
  The paper has been at `~/can-it-ford-refs/2026-08-16/` since 16 August.

**Consequence for the criterion-3 rewrite: there is no external band to inherit. Any band is this
project's own choice and must be labelled as such.**

## 4.4 The class nobody searched, and it has a shipping product in it

Seven source classes were searched by nobody: patents, standards (ISO, SAE J-series, MIL-STD-810
wading), OEM wading specifications, theses, incident and fatality data, dashcam evidence, and
benchmark code suites. **One query found four Land Rover wading patents** and a published
**500 to 900 mm per-model wading capability**:

- US20140371976A1, Method and system for determining a wading depth of a vehicle
- US20150066339A1, Wade sensing display control system
- US20140347178A1, Wading vehicle water level display
- US10279681, Vehicle having wade sensing display and system therefor

The R10 critic's self-refuting catch: the report builds its recommended contribution reframing on
an AR&R sentence recommending an analytical model **"using manufacturer specifications"**, and
manufacturer specifications are a class it never searched.

---

# 5. THE FLOOR: WHERE THE PHYSICS GOES NEXT

## 5.1 What is established

The bulk pressure field is hydrostatic. The disturbance is at the bottom boundary. A one-line
engine change fixed 96.40 percent of the mass leak WITHOUT quieting the column, so leak and
agitation are decoupled. Three properties are separable and all three are independent: mass
conservation at the floor, the mean hydrostatic gradient, and quiescence.

## 5.2 THREE CONFIRMED FINDINGS FROM TONIGHT'S DEEP RESEARCH, adversarially voted

From run `wf_d942bc1a-e29`, 86 of 103 agents completed, 4,079,261 subagent tokens. These three
survived a 3-voter refutation panel. **They are SPH rather than MPM, so the scope test in
`docs/CANDIDATE_PAPER_SCOPE_TEST.md` must be applied before any of them is cited as a mechanism
rather than a precedent.**

1. **A wall boundary treatment can generate a spurious static pressure gradient that exactly
   cancels gravity on a fluid particle, holding it suspended in mid-air.** Source
   `mdpi.com/2077-1312/14/9/863`, vote 2-1. Mechanism: renormalized SPH extrapolation writes a
   velocity of `g*dt` onto the boundary edge point once a particle falls within one smoothing
   length of the first dummy particle, which then feeds the Neumann pressure BC. Fix: a
   multiplicative cutoff `C_cut` with exponent beta at 0.1; beta > 0.2 activates wall braking too
   early, beta < 0.01 too weak. **Critically, `C_cut` is constructed in units of particle
   diameter so the defect DOES NOT SCALE AWAY WITH RESOLUTION.** Verbatim: "the pressure
   calculated on the dummy particle through Equation (13) would generate a pressure gradient that
   counterbalances the fluid particle, preventing it from falling".
2. **A second, independent wall defect breaks hydrostatic equilibrium in a stationary tank**, and
   this is the closest published analogue to d11's column. Same source, vote **3-0**, unanimous.
   Dummy particles above the free surface on VERTICAL walls are assigned pressures that violate
   the hydrostatic profile, and **"when the pointer C_van is not employed, the water volume fails
   to remain in equilibrium"**. This EXTENDS Gotoh 2009 rather than restating it: same
   observable, different mechanism, being contaminated wall-particle pressure extrapolation
   across the free-surface truncation rather than free-surface misidentification.
3. **For a rigid body held FIXED in flow, SPH OVER-predicts steady drag against a finite-volume
   reference**, and changing ONLY the boundary treatment moves the force. Source
   `arxiv.org/pdf/2402.06231`, vote 2-1. 3D Apollo reentry capsule: C_D 1.55 without ghost-mirror
   and 1.51 with, against Eilmer's 1.42, i.e. **+9.2 and +6.3 percent**. Boundary treatment alone
   moves the force **2.6 percent at unchanged resolution**, and the authors state outright they
   could not demonstrate resolution independence.

**CORRECTION, 02:07, AND IT DEMOTES ALL THREE. d11-accessor applied the scope test to them
against the pinned vendored core and BOTH MDPI FINDINGS FAIL QUESTION 1, so they are PRECEDENT
and NOT MECHANISM.** The floor here `add_plane` at `core/solver.py:212` registers a GRID
collider, surface_type 1, slip, friction 0, restitution 0, and the entire boundary condition is
five lines in `mpm_solver_warp.py`: guard on `grid_m <= 0` at :1942, the `dotproduct < 0.0` site
at :1955, read `grid_v_out` at :1974, **project out the normal component** at :1977, write back
at :1990.

**IT WRITES VELOCITY ONTO A GRID NODE. IT NEVER WRITES PRESSURE, AND THERE IS NO BOUNDARY
PARTICLE OF ANY KIND.** A whole-tree search of `kernels/` and `core/` for dummy, ghost particle,
mirror particle, extrapolat, free surface, `C_van` and `C_cut` returns nothing relevant.

| what the finding requires | what this solver has |
|---|---|
| dummy particles carrying pressure | NONE EXIST |
| pressure extrapolation onto an edge point | NONE EXISTS |
| `C_van`, excluding dummies above the surface | NOTHING TO EXCLUDE, and no free-surface test anywhere in the BC |
| `C_cut`, a cutoff conditioning extrapolation | NO CUTOFF OF ANY KIND |

**So the floor question is now OPEN IN A SHARPER FORM, which is a better place to be than a
borrowed explanation:** the disturbance is at the bottom boundary, the boundary only projects out
a normal velocity component, and no published mechanism this project has found applies to that.
Commit `c621539`. This is the sixth candidate the coordinator relayed that died on a source read,
and the FIRST killed by a purpose-built tool rather than by luck.

**Refuted by the panel, do not cite:** the DBC depletion-gap mechanism, the +h gauge offset, and
the ghost-node density extrapolation fix, all from `link.springer.com/article/10.1007/s40571-021-00403-3`,
which lost 1-2, 0-3 and 0-3 respectively.

## 5.3 The most validated physics route, from R10 section 4.1

**A still-water flotation ladder on the canonical Yaris hull, graded against Azhar 2023's
0.35 m SPH / 0.37 m physical pair, run BEFORE any further sphere mechanism work.**

Why most validated rather than most appealing:
1. **Same vehicle, same mass, same friction.** Azhar's vehicle is a Toyota Yaris at 1097 kg with
   mu = 0.55; the canonical hull is a Toyota Yaris at 1100 kg with `floor_friction` 0.55 on all
   17 runs. **No other benchmark in the corpus matches on all three.**
2. **It is quiescent**, so every flow-dependent confound is absent by construction and a residual
   disagreement is numerical.
3. **It has an external falsifier with a stated number**, which CLAUDE.md item 6 says the entire
   gate set currently lacks. **It would be this project's first gate that can fail for an
   external reason.**
4. **Corroborated by a separate-origin bracket**, 0.34 to 0.57 m across four experiments.
5. **The competing route, more grid refinement, is refuted three times over**: locking is not
   remedied by refinement; Zhao 2019 measures a brink-depth error plateau at 3.44 / 1.90 / 1.88
   percent across a 6x mesh range; Syamlal 2017 states transient quantities cannot be
   grid-converged at all. **A fourth grid sweep is the least validated thing available.**

**The immediately following control is NOT a grid sweep:** hold `dx` fixed and vary
particles-per-cell, because three of the five live candidates predict the error moves with PPC
and a `dx`-only sweep cannot separate any of them.

---

# 6. THE DELIVERABLE: WHAT IS WRONG WITH THE PAPER

## 6.1 Four defects, three refuted by files already in this repository

1. It says **"We did not measure ground clearance from the mesh"**. It was measured:
   `docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md:155` records **0.1737 m**.
2. Its conclusion that **"only the 1100 kg configuration is a genuine class match" is FALSE**,
   because NO AR&R class is satisfied on all three axes. D.V = 0.4416 for `g64_m1100` sits
   between the two class limits and a referee reproduces it in one line.
3. The friction value **0.78 is mis-cited to `shand2011arr`**; it belongs to Smith.
4. **"1.0 to 1.8" should read 0.98 to 1.83.**

## 6.2 Three more found by d23 tonight

5. **The paper's honest refusal has a defective fallback.** It says "until it is placed on an
   independent empirical footing we report displacement magnitudes only". The refusal is right.
   **The fallback quantity is unconverged**: `final_disp_mag_m` moves +87.8 then -59.2 percent at
   1100 kg, +22.3 then -50.3 at 1609, and **-27.7 then -34.0 at 2337, falling on BOTH legs**, so
   the SIGN of the resolution effect is not consistent across masses. CLAUDE.md item 5 records
   only the two non-monotone rows and thereby understates it.
6. **The number is route-dependent.** Summary route 0.658537 m against rollout route 0.637019 m,
   gap 0.021518 m, which is 3.268 percent of the first and 3.378 percent of the second.
   CLAUDE.md's "3.4 percent" is the rollout-denominator form. Never quote it bare.
7. **The one figure the paper calls pinned to primary sources is the one figure nothing in the
   repository produces.** A `/usr/bin/grep` sweep reaching gitignored paths finds no script that
   makes `force_balance_v2.pdf` and none of its caption's distinctive numbers in any `.py`. The
   other six are reproducible.

## 6.3 The bibliography

**One citation key resolves to two different papers.** `paper/...IEEE.bib` maps `alqadami2022` to
`10.1111/jfr3.12828` (2022, numerical); `overleaf_sync/...IEEE.bib` maps the same key to
`10.3390/su151713262` (2023, 3D CFD). The two bibs are 42 and 21 entries, so they are not two
copies of one list. **CORRECTED 02:07 by d19-priorcode, commit `dc1a949`: the question as posed was a FALSE
DICHOTOMY and choosing either file would be wrong.** The authoritative bibliography is
**`overleaf/main:can_it_ford_references_IEEE.bib`, AT THE REPO ROOT, 15 entries.** Three reasons,
all read: it is the only bib on the only ref carrying `conference_101719_1.tex`, the tex the
paper actually builds from, and note the `_1` because the two local `conference_101719.tex` files
are a DIFFERENT DOCUMENT; it is the only one consistent with the shipped paper at 15 entries, 14
distinct cite keys, all 14 present and exactly one never cited (`xiong2024`), reproducing
CLAUDE.md's independently recorded ladder from a separate origin; and `paper/...bib` is NOT
STABLE ACROSS REFS, 21 entries on origin/main against 42 on two unmerged branches, and a file
differing by 21 entries depending on checkout cannot be canonical.

**`alqadami2022` appears ZERO times on `overleaf/main`**, so the collision is a landmine in the
repo copies rather than a live error in the deliverable.

**Prior art is at least fourteen works with resolved DOIs and the shipped paper cites ONE.**
Three Al-Qadami papers exist across three years and three methods: `10.1007/s11069-021-04949-6`
(2021, full-scale EXPERIMENTAL), `10.1111/jfr3.12828` (2022, NUMERICAL, the moving-vehicle one),
`10.3390/su151713262` (2023, 3D CFD). `10.1111/jfr3.12657` is **2020**, and two separate prior
instructions to relabel it 2021 were BOTH wrong. Shah's first author is **Syed MUZZAMIL Hussain
Shah**, not Hamid, confirmed against Crossref.

## 6.4 The most validated deliverable route, from R10 section 4.2

Correct the defects, replace the class claim with a labelled two-class sensitivity, and **reframe
the contribution against AR&R Project 10's own recommendations 3 and 4 rather than against
novelty.** The AR&R report contains a verbatim sentence recommending exactly this project, and
**disowns its own criteria** as "unlikely reliable enough to be adopted permanently as safety
criteria", which converts "our simulation disagrees with AR&R" from a defect into a research
question the criteria's own authors named.

**The surviving narrow claim** is: no MPM simulation of a full road vehicle in floodwater was
found, in two named searched views, with the adjacent precedent being tyre hydroplaning (Zhou
2025, Zhou 2026). **The SPH half of the old novelty claim is dead and must never be restated.**

---

# 7. THE CORPUS, THE CONNECTORS, AND THE READING INFRASTRUCTURE

## 7.1 The corpus index is a DISCOVERY instrument, not a reading one

**It holds no full text and never did.** 15 fields per record, none a body or a PDF path. Largest
text blob in the entire file is **3,477 characters**; median abstract 1,305, against tens of
thousands for a paper. **110 of 332 records carry nothing but bibliographic metadata.** The 332
records are **319 distinct works**.

**It reaches 8 of 21 deep searches.** `REPORTS` at `analysis/research_index.py:56` is a hardcoded
list of markdown files under `~/Downloads`, so a search enters only if somebody exported it by
hand. The ingested number has not moved in five weeks while the total moved three times in two
days. **The durable fix is not a better constant**: `--source-audit` now exits 1 when a completed
search reaches the corpus by no route.

**`--query` matched title and abstract and NEVER authors**, fixed on d14's branch only. On
`claude/add-ci-checks` it is still author-blind, and **on `origin/main` `research_index.py` does
not exist at all**, so a session on a fresh clone has no corpus tool whatsoever.

**A miss is not an absence.** All six closest prior-art DOIs ARE in the index; the coordinator
relayed the opposite and was refuted.

## 7.2 The connector tier, and why every routing instruction has been aspirational

**Every dispatching session has 76 MCP connectors. Every dispatched slot has 17, with ZERO
bridged claude.ai connectors.** Measured from tool MANIFESTS across seven R9 slots, and a sweep
of every `~/.claude/projects` directory agrees: all twenty r7/r8/r9 sessions show zero.

**This means every connector instruction written from the coordinator seat was written from an
environment the recipient does not have**, for three waves.

The connector-router skill was revised live and two routing defects were measured: **Scite is
OAuth-gated and therefore dead in any headless session**, yet the router sent EVERY citation and
DOI check to it; and **Undermind was absent from the table entirely** despite holding the 21
commissioned deep searches and being the only route to full text. Twelve exact `ToolSearch`
select strings are now in the file, because MCP tools are deferred and calling one before loading
it fails with `InputValidationError`, which reads exactly like a broken connector.

**But the revision's own most prominent instruction is wrong for its audience**: it says to
retract the row for Otter, Slack, Calendar, Drive and pdf-viewer as "not present in Claude Code",
which is TRUE in the main checkout and FALSE for the slots that read the skill. Both documents
scoped their probe and **only one scoped its conclusion.**

## 7.3 The reading tools that actually work

- **`docs/r10/pdftext.swift`** extracts PDF text through PDFKit, handling the subset-font CMaps
  that defeat a stdlib zlib extractor. **This Mac has no pdftotext, no numpy and no PyObjC**, and
  that gap silently shaped the whole night: papers were read as rendered page images twenty at a
  time, which is why so little full text got read and so much got relayed from summaries.
- **`fetch_verified.py`** writes every candidate to a temp path, extracts its text, matches
  against the wanted title, and KEEPS IT ONLY IF IT MATCHES. An unverifiable candidate is
  DELETED, not renamed and kept, because a quarantined file with a scary name is still a file
  something will eventually glob.
- **Four resolver routes instead of one**: OpenAlex `title.search`, Semantic Scholar (which
  indexes preprints Crossref does not), Crossref with token overlap instead of prefix
  containment, and **the register's own DOI list**. That turned 49 "no DOI" works into 23.

---

# 7A. HOW TO USE THE LITERATURE LAYER, OPERATIONALLY

This section exists because the findings above are useless without the procedure that produced
them, and because the single most expensive mistake of the round was a session trusting a
literature answer that arrived without the command that produced it.

## 7A.1 THE FOUR RULES, in the order they will save you

**RULE 1. A ZERO FROM A TOOL IS NOT AN ABSENCE UNTIL YOU KNOW WHAT THE TOOL SEARCHED.**
`--query` matched title and abstract and NEVER authors. One session queried "Al-Qadami", got
zero, read it as coverage, and relayed "none of the six closest prior-art DOIs is in the corpus"
to three sessions, two of which acted on it. **All six are present.** WebSearch separately
returned zero for a whole evening because its model pin was dead, which reads identically to a
genuine absence.

**RULE 2. WHEN YOU PASS ON A NEGATIVE RESULT, PASS ON THE COMMAND THAT PRODUCED IT. WHEN YOU
RECEIVE ONE, ASK WHAT WAS SEARCHED BEFORE YOU ACT.** None of the three receiving sessions could
have caught the error above, because a relayed conclusion arrives stripped of its predicate.
This is d14's `de18180` and it is the generalisable fix; "be more careful" is not.

**RULE 3. BEFORE CITING A PAPER AS A MECHANISM, RUN THE SCOPE TEST.**
`docs/CANDIDATE_PAPER_SCOPE_TEST.md` on `claude/r9-jobb-route`. Five questions: discretisation,
boundary or coupling scheme, regime, quantity, evidence strength. **Passing all five makes it a
MECHANISM. Passing some makes it a PRECEDENT. The write-up must say which.** It has now killed
three candidates the coordinator relayed, including one that matched on every memorable surface
feature and failed on all three of discretisation, boundary scheme and regime.

**RULE 4. CHECK LOCAL DISK BEFORE ACQUIRING ANYTHING.** Three separate passes called Kramer 2021
"the most valuable unretrieved item" while it sat at `~/can-it-ford-refs/2026-08-16/` since 16
August. d15 found 35 comparable long records already on Vista when a claim was thought to need
new runs. d22's resolver reported a DOI unfindable that was sitting in this project's own
register. **Three instances in one night of "we do not have it" meaning "we never looked at what
we own".**

## 7A.2 THE 21 DEEP SEARCHES, NAMED, AND WHICH ARE INVISIBLE

Undermind workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c`. The corpus index reads **8**. The
other **13 are invisible to every corpus query** and four of them are the ones this project
most needed.

**INGESTED (8):** Quantitative MPM Wall Penetration; Trustworthy AI Assisted Scientific
Simulation; Moving Rigid Body Free Surface Validation; Validated MPM Vehicle Water Coupling;
Settling and Force Reporting in Free Surface Flow; MPM Simulation Verification Provenance;
Multi-resolution MPM for Large-domain Flooding; Reliable AI Scientific Software.

**NOT INGESTED (13), with what is in them:**

| search | why it matters |
|---|---|
| **MPM SPH buoyancy force overestimation and hydrostatic validation benchmarks** | Its GOAL TEXT contains this project's exact configuration: the fixed half-submerged 0.15 m sphere, the accumulated-impulse-over-dt accessor, the leak fix from 4.5 to 0.008 percent leaving 36 percent error, the quadrupled tank moving the ratio 1 percent. Its summary already said the bias is more plausibly a discrete coupling error than a tank effect, and that Kramer is a MOTION benchmark not a static-force tolerance. **The project spent the round rediscovering both.** |
| **free surface elevation estimator error in particle method buoyancy validation** | Run 2026-08-19 17:44, 88 papers. **It prescribed the exact controls two sessions then invented independently**, including "a body-off hydrostatic run provides the estimator bias independently of body loading". |
| **which realism effects change a flood vehicle stability verdict** | Ranks what changes a VERDICT: bed friction, slope and orientation, watertightness. And what does NOT: air entrainment, spray, surface tension, turbulence closure, reduced sound speed, outlet boundary choice. **States plainly that no study quantifies a crowned road against a flat plane**, which is why d17's crown result is a contribution. |
| **Simulation Ready Vehicle Mesh Assets** | The CCSA/NCAC documented set is **Yaris, Camry, Silverado**, not Rogue. No redistributable OBJ/PLY/glTF/USD conversion verified in that result set. DrivAerML is CC-BY-SA but parameter-morphed generic; 3DRealCar is scans with real dimensions and no mass. |
| **Dynamic Vehicle Traction in Floodwater** | Tire-scale flooded pavement work supplies a **depth- and speed-dependent tire-force law**, not a fixed coefficient. `floor_friction = 0.55` is a fixed coefficient. |
| moving vehicle floodwater simulation open source implementations | prior-art and code |
| moving vehicle floodwater GPU particle simulation | prior-art |
| how computational researchers audit and defend simulation credibility | the credibility framing |
| GPU particle solver portability scaling and surrogate fidelity | portability |
| Small Data Physics Surrogates at 36 Conditions | surrogate design |
| Physics Simulation Validation Protocol | validation design |
| Quantitative Flood Traversability Connections | hazard framing |
| Optical Vehicle Collision Geometry | geometry |

**HOW TO REACH THEM.** Not through the index. Load the connector and inspect the workspace:

```
ToolSearch "select:mcp__undermind__get_orientation,mcp__undermind__list_workspaces,mcp__undermind__inspect_deep_searches,mcp__undermind__read_pdfs"
inspect_deep_searches(workspace_id="17299f2a-8dc8-438b-8c84-5abf19395e2c", names=[])
```

**READ THE GOAL TEXT, not just the summary.** The goal text of a commissioned search often
contains the project's own configuration and constraints, and it is the fastest way to tell
whether a search already answers the question you are about to spend GPU on.

## 7A.3 THE CLAUDE ARTIFACTS, and what is stale in them

Reachable with `Artifact` `action: "list"`, readable with `WebFetch` on the artifact URL.

| artifact | status |
|---|---|
| **Console Against Can It Ford** (2026-08-17) | **Its headline finding is now FALSE.** It concluded ZERO Anthropic rate or usage limits across 28 days and 72,126 turns, and therefore no headroom problem to solve. Tonight hit BOTH a monthly spend limit and a weekly limit. **Mark it superseded.** Still correct and valuable: Console cannot see sessions or chats; the Admin, Usage-and-Cost and Claude Code Analytics APIs are CLOSED to individual accounts; **never export `ANTHROPIC_API_KEY`**, because it silently converts every session from subscription to metered billing, with a documented case of 1,122.83 dollars accrued; and the measured usage profile, 71.7 percent of tool calls are Bash, 11:1 tool round-trips per typed message. |
| The Unbuilt Register (2026-08-17) | unread this session; check before relying on it |
| RECONCILIATION_AND_DISPATCH (2026-08-14) | superseded by tonight's dispatch record |
| RESEARCH_BRIEFS_REALISTIC_ENV (2026-08-14) | the realism brief that preceded the render work |
| The Round That Refuted Itself (2026-08-19) | tonight's fleet board, published |
| R9_Cross_Session_Readout.md (2026-08-19) | the 773-line readout, published for reading |

## 7A.4 WHAT THE R10 CRITIC SAID ABOUT R10, and it applies to any future audit

The R10 report has a built-in adversarial critic and it is harder on the report than any reader
would be. Its four findings, all of which generalise:

1. **The report NAMED its two highest-value unread items and SCHEDULED NEITHER.** Section 5
   contained no retrieval task of any kind.
2. **It proposed an untested retrieval route.** "Energies is open access so it should be
   downloadable from MDPI" returns **HTTP 403**. The critic tested it. *And the critic then
   proposed two more untested routes, both of which 404 when I tried them, while the paper was
   on local disk all along.* Untested advice is the recurring failure, not any one route.
3. **Coverage was inflated by roughly 23 works cited exactly once, in the coverage list itself.**
   If a report says N papers were read, count how many are cited in its conclusions.
4. **Seven source classes were searched by nobody:** patents, standards (ISO, SAE J-series,
   MIL-STD-810 wading), OEM wading specifications, theses, incident and fatality data, dashcam
   evidence, benchmark code suites. The self-refuting form: the report builds its recommended
   reframing on an AR&R sentence recommending an analytical model **"using manufacturer
   specifications"**, a class it never searched. One query later found four Land Rover wading
   patents and a published 500 to 900 mm per-model wading capability.

## 7A.5 THE ACQUISITION LAYER, and its measured error rate

d22-gapscan's numbers, which condition every claim sourced from a scraped PDF tonight:

- Want list **261 distinct works**: 230 from the deep searches plus **31 from the bibliography
  and register that appear in NO search at all**.
- **68 reachable, 162 not.** Barriers counted: 105 closed with no OA location, 49 that never
  resolved to a DOI (**since reduced to 23** by using four resolver routes instead of one), and
  **57 that ARE open access but whose publisher host refuses a plain client**, concentrated in
  ScienceDirect, MDPI, Wiley and Springer. That last group is the recoverable one: scraping the
  landing page for `citation_pdf_url` and re-requesting with a Referer got **8 of 24**.
- **TWO WRONG FILES IN THIRTEEN SCRAPED, a 15 percent error rate**, one of them a website Terms
  and Conditions page. Found only by building a tool that reads the file rather than trusting
  its name.

**The tools that fix it, and both are in `.claude/worktrees/r9-gapscan/`:**

- **`docs/r10/pdftext.swift`** extracts PDF text via PDFKit, handling subset-font CMaps that
  defeat a stdlib zlib extractor. **This Mac has no pdftotext, no numpy and no PyObjC**, and that
  gap silently shaped the entire night: papers were read as rendered page images twenty at a
  time, which is a large part of why so little full text got read and so much got relayed.
- **`fetch_verified.py`** writes each candidate to a temp path, extracts its text, matches the
  wanted title, and **keeps it ONLY if it matches**. An unverifiable candidate is DELETED, not
  renamed and kept, because a quarantined file with a scary name is still a file something will
  eventually glob.
- **Four resolver routes, not one:** OpenAlex `title.search`, Semantic Scholar (which indexes
  preprints Crossref does not), Crossref with token overlap rather than prefix containment, and
  **this project's own register DOI list**.

## 7A.6 THE DECISION PROCEDURE, condensed

Before asserting novelty, before citing a mechanism, before spending GPU on a question:

1. **Query by DOI, never only by author.** The predicate cannot see authors on most trees.
2. **If the index returns nothing, inspect the 13 unindexed searches before concluding absence.**
3. **Read the GOAL TEXT of any relevant search.** It may already contain your configuration.
4. **Run the scope test before calling anything a mechanism.** Say MECHANISM or PRECEDENT.
5. **Check `~/can-it-ford-refs/`, `~/Zotero/storage/` and the Desktop corpus directory before
   acquiring.**
6. **Verify any scraped PDF against its own text.** The prior is 15 percent wrong.
7. **State which view you searched.** An absence from a partial view is not an absence.

---

# 7C. WHAT `deep-research` RUN `wf_d942bc1a-e29` ACTUALLY FOUND

**135 extracted claims across 100 agent results.** The synthesis step died on the weekly limit,
so nothing merged them into a report. These are the ones that change a decision, read from the
run journal at
`~/.claude/projects/-Users-josie-can-it-ford/1d537aee-.../subagents/workflows/wf_d942bc1a-e29/journal.jsonl`.

**Provenance warning, and it is load-bearing.** Only three of these went through the 3-voter
refutation panel (section 5.2). The rest are single-agent extractions whose verifier panels died
on the account limits. **Treat everything in 7C.2 to 7C.6 as a LEAD WITH A SOURCE, not as a
verified finding.** Apply `CANDIDATE_PAPER_SCOPE_TEST.md` before citing any of it as a mechanism.

## 7C.1 THE ANSWER TO THE QUESTION THIS PROJECT COULD NOT ANSWER

**A published cross-check of a momentum/impulse-exchange force against a surface-stress integral
EXISTS, on the same analytic benchmark.** This project spent the round unable to adjudicate
between two accessors and concluded no published cross-check existed. It does.

- Method A computes force as the negative volume integral of the IBM forcing term plus a
  rigid-body inertia correction `(pi*d_p^3/6)*dv_p/dt`. Methods B, C and the overset method
  integrate the stress tensor over the surface. **Both converge at roughly first order and
  agree.**
- **And the same paper contains an explicit instance of TWO ACCESSORS ON THE SAME SIMULATION
  DISAGREEING BY MORE THAN AN ORDER OF MAGNITUDE, WITH THE CAUSE NAMED.** Substituting the Kempe
  and Frohlich force procedure, which was developed for freely-moving particles at density ratio
  below 1.2, into a prescribed-motion case raised the force error **from about 2.95 percent to
  42.2 percent**. The cause is applying a force procedure outside its design regime. **That is
  the closest published analogue to this project's factor-of-two accessor disagreement.**

## 7C.2 THE BENCHMARK TOLERANCE EXISTS AFTER ALL, AND IT NARROWS SECTION 4.3

Section 4.3 records that no canonical floating-body benchmark states a tolerance on a force.
That stands for SPHERIC Test 12 and for Kramer. **But a rigid-sphere exact-solution benchmark in
this run DOES state a protocol and a standard**, and it answers every question this project
asked:

- Errors reported as percentages of the analytic norms in **BOTH L-infinity (max over space and
  time) and L2 (RMS)**.
- Measured over a **fixed half-period window `t = [0.1, 0.6]` chosen to discard the initial
  transient**.
- At **three resolutions, `d_p/h` = 16, 32, 64**.
- **The tolerance the author treats as the achievable standard is 1 PERCENT IN THE MAXIMUM NORM
  AT 32 GRID POINTS per diameter.**

**Revise section 4.3 to: no FLOATING-BODY benchmark states a force tolerance, but a fixed-sphere
exact-solution benchmark does, and it is 1 percent in the max norm.** That is a far harder
standard than this project's 10 percent bands and it should be quoted when criterion 3 is
rewritten.

## 7C.3 THE FINDING THAT MOST DIRECTLY THREATENS THE PROJECT'S GRID LADDER

**A near-boundary treatment defect that destroys local pressure and velocity-gradient convergence
does NOT prevent the INTEGRATED force from converging.** For both diffuse-interface and
sharp-interface IBM, L-infinity errors in pressure and velocity gradient have estimated
convergence orders of **-0.2 to 0.2**, i.e. no convergence at all, and one method's max-norm
pressure error actually grows, **while the integrated force still converges.**

**Consequence: a converging force is not evidence of a converging field, and a non-converging
field does not by itself invalidate a force.** This project has been reasoning in both
directions from grid ladders.

**And the companion finding:** an empirical near-interface offset, Breugem's interface retraction
by 0.3h, **reduces force error by almost a factor of 3, from 8.11 to 2.95 percent**, while NOT
fixing the underlying non-convergence, whose order stayed at approximately zero. **A documented
case of an error whose magnitude is tunable by an empirical constant without the underlying
defect being fixed.** That is exactly the shape of a tuned band passing a gate.

## 7C.4 THE BOUND ON HOW LONG A QUIESCENT TANK STAYS TRUSTWORTHY

**A quiescent weakly-compressible tank DEGRADES OVER LONG INTEGRATION.** The still-water pressure
field stays noise-free to about **20 seconds** and develops noise by around **200 seconds**. The
static hydrostatic case in that work is analysed over only **4 seconds** of physical time.

**This directly bounds d11's column**, which never goes quiet and whose kinetic energy GROWS.
Before concluding the solver is defective, establish where the column sits on that timescale: a
record long enough to enter the degradation regime would show growth in a code with no defect at
all. **This is the single cheapest test of d11's headline and it needs no GPU beyond a
re-analysis of existing frames.**

Related, same source: **the paper states NO quantitative error tolerance anywhere and never
integrates pressure into a force.** Every validated quantity is pointwise. Acceptance is
asserted qualitatively as "close agreement".

## 7C.5 BOUNDARY TREATMENT, NOT RESOLUTION, SETS THE FLOOR

- **In DualSPHysics standard dynamic boundary conditions, the repulsion mechanism holds fluid off
  the wall, leaving an unphysical fluid-void gap of order the smoothing length h**, so boundary
  particle density and hence pressure take unphysical values at the surface. The established
  workaround is to **relocate the numerical gauge a full h into the fluid**. A reading taken at
  the nominal surface is systematically wrong regardless of how well the bulk is resolved.
- **In the canonical static test, a 2.4 x 1.2 m still-water tank with H = 0.5 m and a 0.24 m
  trigonal wedge giving a sharp corner, DBC FAILS to recover hydrostatic pressure at BOTH
  resolutions tested (dp = 0.02 and 0.01 m), while mDBC recovers it down to the solid surface at
  both. The defect is removed by CHANGING THE BOUNDARY TREATMENT, not by halving the particle
  spacing.**
- **Han and Cundall compare two force/coupling accessors inside ONE solver** and find the
  immersed boundary scheme both more accurate AND less sensitive to lattice resolution than
  momentum exchange. **Both schemes derive from the SAME underlying boundary concept**, so the
  gap is attributable to how the interface is discretised and how momentum is accounted at it,
  not to a different physical model.
- **Momentum-exchange force accuracy is CONDITIONAL on the bounce-back scheme paired with it**;
  second-order force is attained only "with appropriate bounce-back schemes". **A momentum or
  impulse-exchange accessor and its boundary treatment cannot be validated separately.**

## 7C.6 TWO CLAIMS THAT BEAR ON THE EXONERATION WITHDRAWAL

- **Inter-code agreement is not evidence of correctness.** Across eleven independent codes
  solving one specified case, the inter-code spread EXCEEDS the experimental uncertainty and
  individual RANS models fall outside the measured 95 percent confidence interval at various
  times. **Membership in an envelope is not validation.** This is the general form of exactly
  what d21 concluded about two readings agreeing by construction.
- **The momentum-exchange accessor carries an intrinsic Galilean variance error**, naming the
  ACCESSOR rather than the fluid or the wall closure. **Falsifiable extension the run supplied
  itself:** a Galilean mechanism scales with relative frame velocity, so on a body held FIXED at
  rest relative to the grid it predicts ZERO contribution and therefore **cannot explain a steady
  over-prediction on a stationary sphere.** Related: the dominant named source of MEM force error
  is the sub-grid geometric offset between boundary nodes and the solid surface, whose
  fluctuating character comes from that distance being TIME-DEPENDENT as the body moves. **For a
  fixed body the oscillatory component vanishes and a constant offset remains** — which is a
  candidate for a steady bias and is the one lead in this section pointing at a fixed-body
  steady error.
- **The citation lead to chase:** Dong et al., cited as reference [1] of the 2025 moving-wall
  paper, is a prior published error analysis of MEM force evaluation **for STATIC FLAT WALLS**.
  That is geometrically the closest published match to a body held fixed in a tank, and it is
  the error budget this project has been trying to construct from scratch.

## 7C.7 ONE MORE, ON MODEL FORM RATHER THAN DISCRETISATION

**A linearised hydrostatic buoyancy force law is a named model-form error of about 50 percent at
full submergence**, established by direct force-sensor measurement against the analytic
submerged-volume expression, and in a dynamic model it systematically inflates the body's
acceleration. **Because it lives in the FORCE LAW rather than the discretisation, no grid
refinement removes it.** The magnitude brackets this project's 35 percent. Worth checking whether
anything in the chain linearises a buoyancy term.

---

# 7B. THE WORKFLOW AND AGENT OUTPUTS, IN FULL

Every background workflow and agent run tonight, what it returned, and where the raw result
lives. Kept because three of them were killed mid-run and their partial output is still the
best evidence available on their question.

## 7B.1 `deep-research`, run `wf_d942bc1a-e29` — THE LARGEST SINGLE OUTPUT OF THE NIGHT

Launched, killed and resumed **five times** across two process crashes, a monthly spend limit
and a weekly limit. Final state: **103 agents, 86 completed, 17 errored, 4,079,261 subagent
tokens, 490 tool uses, 780 seconds of wall clock on the last pass.**

**The synthesis step never ran** — it died on the weekly limit — so the output is unmerged
verified claims rather than a report. That is not a failure of the research; the claims are
adversarially voted and usable.

**THREE CONFIRMED** (3-voter refutation panel), all in section 5.2, all since DEMOTED to
PRECEDENT by d11's source read: the spurious wall pressure gradient that cancels gravity
(2-1); the vertical-wall dummy-particle pressures breaking hydrostatic equilibrium, **3-0
unanimous**, whose observable is exactly the bodyless column; and SPH over-predicting steady
drag on a fixed body by +9.2 and +6.3 percent with boundary treatment alone moving it 2.6
percent at unchanged resolution.

**FOUR REFUTED by the panel, DO NOT CITE:** the DBC depletion-gap mechanism (1-2), the +h
gauge offset (0-3), the ghost-node density extrapolation fix (0-3), and a solid-boundary error
floor claim. All from `link.springer.com/article/10.1007/s40571-021-00403-3`.

**An earlier pass of the same run** returned a claim that bears directly on the accessor
question and whose verifiers all died, so it is UNVERIFIED and must be read at source before
use: in LBM, a momentum-exchange force reader's error **rose from 1.75 percent at 128 points
per chord to 9.21 percent at 3072**, a 24x refinement accompanied by a 5x INCREASE in accessor
error, while a control-volume reader on identical grids stayed between 1.25 and 2.06 percent.
Source `arxiv.org/pdf/2210.10377`. **That is this project's exact symptom in a different
method, with the accessor named as the cause**, and it is what prompted building the third
accessor.

**Raw results:** `~/.claude/projects/-Users-josie-can-it-ford/1d537aee-.../subagents/workflows/wf_d942bc1a-e29/journal.jsonl`,
266 lines, 190 started, 76 results, 196 agent transcript files.

## 7B.2 `r10-full-context-audit`, run `wf_5266ee59-fb9` — 25 AGENTS, COMPLETED

Two passes: the first died with `synth:report`, `synth:critic` and `rx:vista` all hitting the
monthly spend limit; the resume completed all 25. **678,161 subagent tokens on the resume, 80
tool uses. 46 core papers identified on disk, 267 findings collected.**

Produced `docs/R10_FULL_CONTEXT_AUDIT_2026-08-19.md` (1024 lines),
`docs/r10/corpus_revision.md` (925) and `docs/r10/connector_revision.md` (339), all three of
which sat UNTRACKED for an hour and are now committed at `6991626`.

**Its five headline items are section 1 of the report and are summarised in sections 6 and 9
here.** Its critic's four findings are section 7A.4. **`rx:vista` completed on the resume**, so
the Vista routing answer in section 8 is its work rather than an assumption.

**One agent's finding that appears nowhere else:** a measured 2010 Yaris inertia tensor and CG
**do exist** in the CCSA validation report, which contradicts CLAUDE.md item 4(a)'s "no
measured Yaris tensor exists anywhere", and the project's own hull particle cloud matches it
closely. **This is UNVERIFIED against the source and it contradicts a standing register item,
so verify before acting.** If it holds, item 4's reasoning for deliberately never wiring
inertia loses one of its three legs.

## 7B.3 The adversarial reviews — FOUR LAUNCHES, ZERO COMPLETIONS, AND THE ANSWER CAME ANYWAY

| attempt | fate |
|---|---|
| 1, ~18:37 | died on `deepseek-ai/DeepSeek-V4-Flash:deepinfra`, the dead model pin |
| 2, ~18:38 | same error with an explicit `opus` override, proving the override does not reach it |
| 3, 01:12 | killed by a parent-process crash mid-run |
| 4, 01:38 | killed by the **weekly limit**, mid-sentence at "Now the solver internals. This is where the independence claim lives or dies." |

**Every physics claim in this document was therefore unreviewed by any subagent.** The
resolution is the best thing in the record: **d21-jobb ran both attacks itself and both landed**,
withdrawing its own headline. Commit `87ae518`. The lesson is not that the review layer is
optional; it is that when the automated route fails, the author running the attack on themselves
is a real substitute and it worked here.

## 7B.4 The directory-provenance and Claude Code capability agents — BOTH COMPLETED

**Directory provenance** (208,462 tokens, 37 tool uses): 44 locations, 49.56 GB, up from 28 and
31.6 GB five days earlier. Canonical remote SHA `c7f0a16` resolved via `git ls-remote` rather
than any clone's cached ref. **194 commits reachable from no remote and in no bundle.** Four
world-readable 0644 token files with four byte-identical `.env` copies. **And it inverted a
standing assumption: worktrees are mostly AHEAD of main, not behind** — of 31, seventeen match
exactly, thirteen are ahead, one is stale. Output at
`~/can-it-ford-audit/2026-08-20/R10_DIRECTORY_PROVENANCE_2026-08-20.md`, deliberately outside
this public repo because it maps credential locations.

**Claude Code capability audit** (136,276 tokens, 12 tool uses): every finding in section 11,
each with a documentation URL. The two that changed behaviour tonight were the hook-input schema
and `--effort` not defaulting to `max`.

## 7B.5 The monitors, and what they were for

- **`r9_watch.sh`** — commits and Vista job state, with a filter added after it reported a
  login-banner line as a running allocation.
- **`r9_followup_debt.sh`** — NEW tonight, and the one worth keeping. It measures **commits
  landed on a slot's branch since the last dispatch actually delivered to it**, read from the
  send log rather than from what the coordinator believes was sent. **First pass: eight of twelve
  slots carried unanswered output.** Commit events say work happened; they do not say a reply is
  owed. It also flags a commit that adds a check while naming no failing input.

Both died with each process crash and were restarted each time. **Background tasks do not
survive the parent process, and nothing warns you.**

---

# 8. VISTA AND THE ALLOCATION

**The allocation was never the constraint.** 593 SU remain, expiring 2026-09-30, and tonight's
entire wave of roughly twenty jobs cost single-digit SUs.

**Walltime over-request was the constraint.** Six jobs asked **11 hours** between them and used
**3 h 53 m**:

| job | asked | used | ratio |
|---|---|---|---|
| r9_settle_longrec | 2:00:00 | 0:01:06 | 109x |
| r9_hydro | 1:00:00 | 0:02:45 | 22x |
| ciford_vehcosim | 1:30:00 | 0:04:36 | 20x |
| r9_crowned_road | 1:00:00 | 0:07:31 | 8x |
| r9_render_motion | 1:30:00 | 0:36:43 | 2.5x |
| r9_speed_surface | 4:00:00 | 2:59:11 | 1.3x |

**The clean experiment:** `r9_est_b` asked 75 minutes and was CANCELLED having never scheduled;
resubmitted as `r9_est_b2` at 15 minutes it started at once and finished in **6:24**. Slurm
backfills a short job into a gap a long request cannot fit.

**Apptainer is NOT needed and must not be added.** It appears only in the abandoned Genesis-era
scripts under `road_grid_2026-08-05/`. Every warpmpm job runs from the native venv at
`/work/11603/jcerrell0629/vista/.venv`. `module load tacc-apptainer` still fails over
non-interactive ssh; use `/opt/apps/tacc-apptainer/1.4.1/bin/apptainer` if ever needed.

**The CPU lane is open and unused.** `gg` is CPU-only, held 50 to 80 idle nodes at 144 cores each
all night, its venv imports numpy 2.5.1, scipy, trimesh, matplotlib and warp, and `pysplashsurf`
was installed into it tonight. **369 metrics.csv and 339 rollout.npz sit on Vista**, against the
21 to 51 records the settle work reasoned from.

**But do not fill idle nodes with work that does not need them.** That is the same error as
leaving an idev session idle. Inventory first; a null is a real result. Interactive idev
historically burned 98.5 to 99.1 percent of node-hours with 95 of 184 jobs ending in TIMEOUT, and
`idv94644` TIMED OUT at exactly 02:00:06 tonight.

**Five srun flags are required**, revealed one at a time:
`srun -p gh -N 1 -n 1 -t <time> --overlap --jobid=<id>`.

---

# 9. THE PLATFORMS

**Weights and Biases: the entire r9 wave is invisible to it except one run pushed by hand.** A
grep finds `wandb.init` 5, `wandb.log` 4, and **ZERO** `wandb.Artifact`, `log_artifact`,
`use_artifact`, `link_artifact` or sweep configs. **106 W&B runs each carry exactly ONE history
row**, so the 91-frame time series that every stationarity and settle finding rests on **has
never been logged**. These jobs run under `sbatch` with no interactive session, so the real
question is offline-then-sync, which is much cheaper than live logging.

**GitHub: nothing gates `main`.** `canford-checks.yml` runs six checks and marks two
(`register_integrity`, `count_claims`) `continue-on-error: true`, so they cannot fail the build.
All four workflows pin actions by mutable tag. No workflow declares `concurrency`. **461 commits
sit unmerged on origin and 440 more never left this laptop.** The best-ratio unused capability is
`$GITHUB_STEP_SUMMARY` plus `actions/upload-artifact`. **Trap: the `continue-on-error` mask is
load-bearing**, because `count_claims_check.py` false-BLOCKs in a tracked-only tree. Fix the
check to report NOT-EVALUABLE before removing the mask.

**Hugging Face: THREE licences are now published for the same project.** `CITATION.cff`
declares ODC-By-1.0, the Space card declares bsd-3-clause, and d18-platform published a THIRD in
the course of investigating the first two (`3f66ba1`). This is a live, public, self-inflicted
exposure and it should be the first thing fixed on that surface. The public dataset's viewer is
**broken by a schema cast error**, so its real 35-column file is invisible and a 4-row summary is
previewed in its place. **HF DOIs go through DataCite, not Zenodo**, and are documented for
models and datasets only, NOT Spaces, so run data must move out of the Space before a DOI is
mintable. Of the ten repos, only **two are genuinely bare**: `can-it-ford-results` (private) and
`can-it-ford-sweep-v1`. `usedStorage` counts **LFS only**, so a repo full of CSV and Python reads
0 B; the coordinator inferred emptiness from it and was wrong.

---

# 10. THE ARTIFACT INVENTORY: WHERE EVERYTHING LIVES

**Committed on `claude/add-ci-checks`**, pushed to origin at `617f34b`:

| file | lines |
|---|---|
| `docs/R10_FULL_CONTEXT_AUDIT_2026-08-19.md` | 1024 |
| `docs/r10/corpus_revision.md` | 925 |
| `docs/r10/connector_revision.md` | 339 |
| `docs/R9_SESSION_HANDOFF_2026-08-20.md` | this file |
| `docs/r10/connector_revision_AUDIT_d20.md` | 256 |
| `docs/R9_CORPUS_READ_2026-08-19.md` | 208 |
| `docs/R9_PROPAGATION_MEASUREMENT_2026-08-19.md` | 190 |
| `docs/R9_DISCREPANCY_REGISTER_2026-08-19.md` | 133 |
| `docs/R9_PROVENANCE_AUDIT_2026-08-19.md` | 103 |
| `docs/R9_SESSION_TITLES_2026-08-19.md` | 76 |

**Living ONLY in a worktree, unmerged, invisible from the main checkout:**

- `.claude/worktrees/r9-reader/docs/R9_CROSS_SESSION_READOUT_2026-08-19.md`, **773 lines**, the
  most complete account of the round in existence: 18 transcripts totalling 42,021,315 bytes and
  42 commit bodies read in full, findings C-1 through C-20, and section 5's list of what no
  session was doing.
- `.claude/worktrees/r9-reader/docs/R9_COORDINATOR_AUDIT_2026-08-19.md`, 372 lines.
- `.claude/worktrees/r9-gapscan/docs/R10_WEB_ACQUISITION_2026-08-19.md`, the 261-work want list.
- `.claude/worktrees/r9-gapscan/docs/r10/pdftext.swift` and `fetch_verified.py`.
- `.claude/worktrees/r9-jobb-route/docs/CANDIDATE_PAPER_SCOPE_TEST.md`, the five-question filter.
- `.claude/worktrees/r9-corpus-bib/docs/R9_CORPUS_BIB_GAP_2026-08-18.md`.

**Outside the repository deliberately:**

- `~/can-it-ford-audit/2026-08-20/R10_DIRECTORY_PROVENANCE_2026-08-20.md`, 296 lines. Moved out
  because it maps credential file locations and this repository is PUBLIC. Contains ZERO token
  values, verified by scanning for token-shaped strings before the move.
- `~/can-it-ford-bundles/2026-08-20/canitford-all-refs-0014.bundle`, 489 MB, 203 refs,
  `git bundle verify` reports a complete history.

**Directory state:** 44 locations, 49.56 GB, grown from 28 and 31.6 GB five days ago. **194
commits were reachable from no remote and in no bundle** at 00:13. Canonical remote SHA is
`c7f0a16`, resolved by `git ls-remote` and never from a clone's cached ref.

**Credentials, Josie's decision:** four world-readable 0644 files hold live-shaped tokens, and
`.env` has **four byte-identical copies**, so any rotation must cover all four. `.env` is
gitignored, never committed, and GitHub 404s it. `~/.zshrc` now has zero assignment-shaped
secrets.

---

# 11. CLAUDE CODE: OPERATIONAL KNOWLEDGE THIS FLEET PAID FOR

This section is worth more than any single physics finding, because every item cost a wave.

## 11.1 The highest-leverage unused capability: typed, schema-constrained returns

`claude --bg`, `claude agents --json`, and `claude -p --output-format json --json-schema '<schema>'`.
A live grep of `scripts/` for any of these returns **ZERO hits**.

**Measured cost of not using it:**
- The fleet is driven by tmux `send-keys`. On 2026-08-19 nine windows fell back to a bare zsh
  prompt and a sender pasted 4 KB of markdown into a shell, **which executed it line by line**.
  `claude --bg` never talks to a shell, so that failure class cannot occur.
- `~/.pane_signals/*_done` fires on every Stop hook, so it proves LIVENESS and not COMPLETION.
  `claude agents --json --all` returns actual session state and does not require a TTY.
- **The recorded post-mortem concluded "the fix is a typed tool return, not a better
  instruction".** A `--json-schema` with a required `verdict: verified|refuted|could-not-evaluate`
  enum makes the distinction between "equal" and "could not evaluate" **unfakeable at the
  transport layer**. That is precisely the defect behind twelve instrument failures.

## 11.2 Hooks

- **All 14 hooks in `.claude/settings.json` are unconditional `type: command`**, so four Python
  scripts run on every Bash, Read, Edit and Write call. `params_check.py` raising inside
  `check_bbox_agreement` blocked 34 commit attempts. **Scope them with `if` conditions**, e.g.
  `Bash(git commit*)`, to bound the blast radius without weakening the guard.
- **A hook must fail OPEN.** A PreToolUse hook that crashes blocks the tool call, turning any
  guardrail bug into a hard stop. Guard every hook with an existence test, wrap the body so an
  unexpected exception exits 0 with a warning on stderr, and reserve exit 2 for the condition the
  hook exists to catch.
- **A heredoc puts file CONTENT inside `tool_input.command`.** Both gates already read the right
  field and still blocked real work twice in ten minutes, because writing a file that MENTIONS a
  dangerous command is indistinguishable from running one. `_strip_heredoc.py` removes heredoc
  bodies before matching. Tested both directions: real force-push DENY, heredoc mentioning it
  ALLOWED.
- **Test the case the comment names.** `gate_concurrent_write.sh` carried a comment claiming
  `git -C . add -A` was matched. It never was, because every pattern needs the literal substring
  "git add". Found only by testing the case the comment claimed.

## 11.3 Effort

**`--effort max` is NOT the documented default.** The default is `high`, and `max` is documented
as showing diminishing returns and being prone to overthinking, to be tested before adopting
broadly. The launcher hardcoded `max` for every session, so a file-inventory slot and a physics
estimator got the same reasoning budget. Now per-slot via an `effort` column.

## 11.4 THE PLAN-FILE TRAP THAT NEARLY CANCELLED PLAN MODE

`permmode` was read as `awk '{print $NF}'`, the LAST field. Appending an `effort` column made the
last field the effort, so every slot would have read `permmode=high`, failed the case statement,
and fallen back to `acceptEdits`. **Every read-only slot would have come up able to write, and
nothing would have said so.** Columns now resolve BY HEADER NAME. A positional read of a named
column is a latent bug that fires on the next schema change, and this one fired in the same
commit that introduced it.

## 11.5 THE RESUME TRAP, which cost four failed attempts

**`resumeFromRunId` resolves a run's agent cache relative to the CURRENT session's transcript
directory.** When the process dies the session id changes, so the same run id points at a nearly
empty directory and **every resume behaves like a fresh launch while reporting success.**

Measured: the real run held **244 journal lines, 170 started, 74 results** under session
`529261e9`, while the new session's copy of the same run id held **20**.

**The fix**, and it is non-destructive:

```
SRC=~/.claude/projects/<proj>/<OLD_SESSION>/subagents/workflows/<RUN_ID>
DST=~/.claude/projects/<proj>/<NEW_SESSION>/subagents/workflows/<RUN_ID>
cp -n "$SRC"/agent-*.jsonl "$SRC"/agent-*.meta.json "$DST"/
# then merge journals keyed on (type, key), destination lines winning
```

**Second trap in the same tool: `args` are NOT stored with the run.** A bare resume exits in
**5 milliseconds** with "No research question provided". The question must be passed again on
every resume; only the agent cache is restored.

## 11.6 The send guard, and how a safety feature became the failure

`r8_send.py` refused a dispatch at `age=27012s` while the pane sat at an empty prompt and the
session had committed one minute earlier. **Five slots report an IDENTICAL age of 26311s**,
because `r8_watch` resolves transcripts through the session-id TSV and those five point at the
pre-crash file.

**The tell: five independent sessions do not fall silent in the same second.** An identical age
across slots is a property of the file being read, not of the fleet. The sender now consults the
PANE past an implausible age, because a session rendering a turn shows a spinner and an idle one
does not. Both directions tested.

## 11.7 Session-scoped facts that will bite

- **Background tasks die with the parent process.** It died twice tonight, each time taking every
  monitor, agent and workflow. Nothing warns you; the tasks simply stop.
- **`cd` moves the Bash tool's persistent cwd for the whole session.** One `cd` silently relocates
  every later relative path. Never `cd`; use absolute paths or `git -C`.
- **The shell `grep` is a ugrep wrapper with `--ignore-files`** and SKIPS gitignored paths. Use
  `/usr/bin/grep` for any inventory claim. An absent hit is not evidence of absence.
- **zsh does not word-split unquoted variables**, so `git bundle create "$BUN" $REFS` passes N
  refs as ONE argument. And `while read ... path` CLOBBERS `$PATH`, after which every external
  command fails while builtins keep working.
- **A worktree carries the CLAUDE.md from ITS branch point**, so it can be hundreds of lines
  behind. Diff headings at session start.
- **`git push` needs `PUSH_OK=1`** here, and `.git/hooks/pre-commit` refuses more than 8 staged
  files. There is NO pre-merge-commit hook, so a clean merge of any size bypasses the limit.

## 11.8 THE HARD LIMIT, live right now

**"You've hit your weekly limit, resets Aug 21 at 8pm (Europe/London)."** The third adversarial
review died on it mid-sentence. 17 of 103 deep-research agents and the synthesis step died on it.
An earlier **monthly** spend limit was hit at about 00:36 and every pane now reads "Now using
usage credits".

**This falsifies the "Console Against Can It Ford" artifact's headline finding of ZERO Anthropic
limits across 28 days and 72,126 turns**, which was true when written on 2026-08-17. That
artifact should be marked superseded rather than left standing.

**Practical consequence: no new subagent or workflow will run until the reset.** Foreground work
in a session is unaffected. Plan accordingly and do not spend a turn discovering it.

---

# 12. THE COORDINATOR'S OWN FAILURES

Recorded because they will recur and because a handoff that hides them is worth less.

**Five relay errors, all distorting toward the stronger claim:**

1. Wal07's "constant systematic bias for a fixed body" — a subagent's REASONING section relayed
   as the paper's text.
2. The same paper's O(h) plateau scaling — measured off a figure by eye.
3. "None of the six prior-art DOIs is in the corpus" — **all six are present**. The true finding
   was narrower: the query predicate cannot see authors. **AND THE MECHANISM IS SHARPER THAN
   "five errors", per d14 `de18180`: this was not three sessions each misreading a zero. ONE
   session ran the query, read the zero as coverage, and RELAYED the conclusion to THREE
   sessions, TWO OF WHICH ACTED ON IT. That is RELAY AMPLIFICATION and it has a different fix:
   when you pass on someone else's negative result, pass on the COMMAND that produced it, and
   when you receive one, ask what was searched before acting. None of the three receiving
   sessions could have caught it, because a relayed conclusion arrives without the predicate
   that produced it.**
4. "Six public empty HuggingFace repos" — `usedStorage` counts LFS only. Two are bare, not eight,
   and the one called an empty public dataset named after the field's open gap is fully populated.
5. Amicarelli relayed as a mechanism match; it fails three independent scope tests.

**Two structural failures:**

6. **Closing stale register rows on `add-ci-checks` widened the only merge conflict still
   growing.** Base 2186 lines, add-ci-checks 2232, r8-register 3009, with all 35 added lines
   absent from the reconciled copy. A row marked OPEN and UNOWNED was **already fixed on another
   branch**, producing two repairs to one file and a new union merge. **Register rows belong on
   `r8-register` until it lands.**
7. **Reported a session stalled for five hours when it was mid-turn**, and **reported twelve
   pending approvals when there were zero**, because the sweep matched the word "permission" in
   the status bar.

**The durable fix is d21's `docs/CANDIDATE_PAPER_SCOPE_TEST.md`**: five questions to ask a paper
before relaying it, with the rule that passing all five makes it a MECHANISM, passing some makes
it a PRECEDENT, and the write-up must say which. Ami15 failed questions 1, 2 and 3
independently, any one sufficient, and none was visible in the relay.

---

# 13. PER-SLOT PROMPTS, READY TO SEND

Send with `python3 scripts/r8/r8_send.py --slot <slot> --file <file>`. Each must name its own
branch, exceed 400 characters, and be unique. **Every one of these is blocked on the weekly limit
only if it needs a subagent; none of them do.**

**d11-accessor, `claude/r9-accessor`.** The floor is now the whole question and you own it. The
deep-research run confirmed, 3-0 unanimous, a published mechanism whose observable is exactly
your column: dummy particles above the free surface on vertical walls get pressures violating the
hydrostatic profile, and without a corrective pointer "the water volume fails to remain in
equilibrium". Source `mdpi.com/2077-1312/14/9/863`. It is SPH, so apply
`docs/CANDIDATE_PAPER_SCOPE_TEST.md` before citing it as a mechanism rather than a precedent, and
say which. Then: does this solver's floor treatment write pressure onto boundary state the way
that paper's dummy particles do, and is there an analogue of the `C_van` exclusion? Your column
needs no GPU to answer the first half.

**d12-kramerdata, `claude/r9-kramer-extract`.** The third accessor landed and agrees with
`sdf_wrench` to 0.9-1.9 percent, so of your four pre-registered outcomes the measurement has
picked one. Finalise the criterion-3 rewrite against it. Carry this constraint into the band:
**no canonical benchmark states a quantitative tolerance on a static force.** SPHERIC Test 12
measures displacement and states none, Test 14 is heave, Kramer's 0.3 percent is a motion
uncertainty on drop height. There is no external band to inherit, so say in the rewrite that the
band is this project's own choice and why.

**d13-renders, `claude/r9-renders` [69 pct context, will compact first].** Land anything
uncommitted now. Then the render's remaining defects are the glazing staircase on the car and the
city facade, and the glazing edge is worth more because it sits on the vehicle. The mesh route is
closed: the smoothest Rogue is missing 47.6 percent of the car. State in the caption that the
Rogue is NOT in the CCSA/NCAC documented set and that the documented midsize is a 2012 Camry.

**d14-corpusbib, `claude/r9-corpus-bib`.** Your branch is now a true superset of SKILL.md, which
turns the hardest merge into a fast-forward. Scope, but do not execute, landing the index and
skill onto `add-ci-checks`. Then the first paragraph of the skill should state that a MISS IS NOT
AN ABSENCE, with the six prior-art DOIs as the worked example, because the coordinator relayed
the opposite and three sessions acted on it.

**d15-settle, `claude/r9-settle`.** Your third-class rule is now used by three slots. Two things:
the paper falls back on displacement magnitude as its safe quantity and d23 has shown it is
unconverged with an inconsistent sign across masses, which is your rule applied to the
deliverable. And 369 metrics.csv sit on Vista against the 21 to 51 you reasoned from; you found
35 comparable, so state the denominator with its scope wherever the settle result is quoted.

**d16-landing, `claude/r9-landing`.** Execute nothing without a go, but the execution card is
ready and the register conflict is the only one still growing. The coordinator has stopped
writing register rows to `add-ci-checks`. `claude/add-ci-checks` was pushed to origin at
`617f34b`, so the ahead count is now against a moved remote. Re-derive before quoting it.

**d17-moving, `claude/r9-moving-vehicle`.** The crowned road is a genuine novelty claim and the
literature has no crown-against-flat comparison. Write it up with the paired design explicit and
the sign reversal between 2 and 4 percent camber stated as the finding rather than hidden. Your
general form of the moved-operating-point failure is now the third instance and belongs in the
register.

**d18-platform, `claude/r9-platform`.** W&B is the largest unexploited capability in the project:
106 runs carry ONE history row each, so the 91-frame series every settle finding rests on has
never been logged, and zero artifacts exist. Scope offline-then-sync from a compute node rather
than live logging. Also: two licences are published right now for the same project, ODC-By-1.0 in
`CITATION.cff` against bsd-3-clause on the Space card, and HF DOIs go through DataCite, not
Zenodo, and are not available for Spaces.

**d19-priorcode, `claude/r9-priorcode`.** You have the only prior-art table resolved against
primary records. Decide which of the two bibs is authoritative and say why, since the collision
is a landmine rather than a live error. Then add the class nobody searched: four Land Rover
wading patents exist and Land Rover publishes a 500 to 900 mm per-model wading capability. A
novelty claim that has never looked at patents or OEM specifications is a papers-only claim.

**d20-reader, `claude/r9-reader` [67 pct].** Your readout is the most complete account of the
round and it lives only in a worktree. It should land. Then measure whether the sideways
propagation improved after tonight's relays, using your original method so the two compare, and
report a null if it is a null.

**d21-jobb, `claude/r9-jobb-route` [68 pct].** The exoneration is SELF-REVIEWED ONLY: three
adversarial reviews died, the last on the weekly limit, mid-sentence at "this is where the
independence claim lives or dies". Two attacks remain open and you can run both yourself. First,
does `control_volume_force` read any quantity the coupling wrote? `cauchy()` is particle stress;
if the collider set it, the two readings are not independent. Second, was "well-conditioned"
defined before or after the four box numbers were seen? If after, the honest spread is 1.367 to
1.488.

**d22-gapscan, `claude/r9-gapscan`.** Your 15 percent scrape error rate conditions every claim
sourced from a scraped PDF tonight. Re-verify the papers that fed a CLAIM, not just the 38 in the
set. Then: `~/can-it-ford-refs/` was not in your route list and Kramer 2021 has been there since
16 August while three passes called it unretrievable, so re-run the resolve pass with the local
trees included and report how many of the 162 move.

**d23-overleaf, `claude/r9-overleaf`.** Never push to overleaf without an explicit go quoted in
the commit; that remote shares no ancestor with origin and a push OVERWRITES. You have seven
paper defects now, four from R10 and three of your own. The figure with no producing script is
the most serious because the paper describes it as pinned to primary sources. Write the checker's
verdict into the caption or pull the claim.

---

# 14. THE FIRST FIVE THINGS TO DO

1. **Settle the independence question.** It is the only thing that can void the night's headline,
   it needs no GPU, and d21 can run it. Until it is answered, every downstream conclusion rests
   on a self-reviewed result.
2. **Run the Azhar flotation ladder.** Same vehicle, same mass, same friction, quiescent, with an
   external number. It would be this project's first gate that can fail for an external reason.
3. **Fix the paper's seven defects**, three of which are refuted by files already in this repo,
   and pull or substantiate the figure nothing produces.
4. **Land d16's execution card**, one merge, seven files, zero decisions.
5. **Do not run a fourth grid sweep.** It is refuted three times over and is the least validated
   thing available.

---

# 15. WHAT I AM NOT CONFIDENT ABOUT

1. **The exoneration is self-reviewed.** Section 1.3.
2. **Section 5.2's three findings are SPH**, and this solver is MPM with a velocity projection SPH
   does not have. They are precedents until the scope test is applied.
3. **I read no external PDF myself in this session.** Everything in section 4 is either a
   connector read by another session or a live fetch of a web page. The six full-text reads are
   attributed to the sessions that made them.
4. **The 15 percent scrape error rate means any claim sourced from a scraped PDF tonight carries
   that prior**, including ones in this document.
5. **Context readings in section 3 are from a single sweep at 01:48** and will have moved.
6. **The weekly limit may change what is possible** before any of this is acted on.
