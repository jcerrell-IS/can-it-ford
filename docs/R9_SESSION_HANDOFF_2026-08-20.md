# R9 coordinator handoff, night of 2026-08-19 into 2026-08-20

Written by the coordinating session at 01:25. Every number here was read live at the time of
writing or is attributed to the commit that measured it. Where a claim is relayed rather than
read, it says so, because relaying without checking was this session's dominant failure and it
happened five times.

---

## 1. THE HEADLINE: JOB B IS SOLVED, AND THE ANSWER IS THE UNCOMFORTABLE ONE

**The force accessor is exonerated. The fluid really is pushing about 35 percent harder than
analytic buoyancy, and the disturbance is confined to the floor.**

The chain, in the order it happened, each link killing a hypothesis:

1. **E1 died at two resolutions** (`054594d`). The near-field surface-offset hypothesis
   predicted an offset scaling as `1.3875*dx`, so 26.02 mm at g64 falling to 17.34 mm at g96.
   Measured across three arms: **+0.98, +0.07 and -1.14 mm**, a 2.1 mm span straddling zero,
   and at g96 the sign REVERSES so applying the correction makes the ratio worse, 1.310 to
   1.342.
2. **The static pressure gradient was cleared, then narrowed** (`1f98170`, `f673c45`). The
   hydrostatic column's mean gradient is right to -0.67 +/- 3.31 percent with Job B 10 to 19
   blocked SE away, so a systematic error in the MEAN GRADIENT is excluded. But the column
   NEVER GOES QUIET: KE/PE grows rather than decays, 11 orders of magnitude above Quinlan
   2018's machine-zero well-balancedness standard, so "the pressure field is exonerated" as a
   general claim was withdrawn by its own author.
3. **Volumetric locking was refuted on its own signature** (`3f4c1ec`). A particles-per-cell
   sweep at fixed grid, 3.375 to 64 per cell and up to 4,784,798 particles, came back FLAT:
   k_fit 0.687, 0.726, 0.727, 0.829, log-log slope +0.0596 where PPC^-2 would predict a 98.4
   percent fall. Locking's first prong requires a RISE. It does not rise.
4. **Quadrature was excluded twice on independent grounds.** Steffen 2008 reports no
   one-signed bias, and the column's KE/PE RISES with ppc at 9.89 sigma where quadrature
   predicts a fall (`03cd132`).
5. **Both existing accessors were found to SHARE A NUMERATOR** (`ea1d385`, `f0bdb0f`).
   `sphere_heave.py:782` takes ONE `fz`; `:818` and `:819` divide THAT SAME `fz` by two
   different denominators. So criterion 3 never graded a force, it graded a normalisation, and
   a factor-of-two disagreement between the accessors said nothing about the force. Every hour
   spent adjudicating between them was spent inside a question with no answer.
6. **A third, genuinely independent accessor confirmed the force** (`f7f0c89`).
   `control_volume_force` reads `cauchy()` and `vol()` only, sharing no code, no grid nodes and
   no knowledge of the collider. At g64 bcfix, submergence 113.77 mm, analytic 44.630 N,
   `sdf_wrench` 60.476 N:

   | box | Fz_cv | ratio | conditioning |
   |---|---|---|---|
   | L=0.18 z=0.38 | 61.373 | 1.3752 | 21.94 pct |
   | L=0.22 z=0.38 | 61.613 | 1.3805 | 14.68 pct |
   | L=0.22 z=0.30 | 61.009 | 1.3670 | 9.75 pct |
   | L=0.30 z=0.30 | 66.402 | 1.4878 | 5.22 pct, worst conditioned |

   The three well-conditioned boxes agree with `sdf_wrench` to **0.9 to 1.9 percent**, against
   a verdict pre-registered in `run_r9g.sh` BEFORE the run.

**WHAT IS STILL OPEN.** The exoneration is under adversarial review as of this writing, on one
specific attack: whether the two accessors are genuinely independent or are two readings of the
SAME corrupted fluid state, which would void it. Also whether "well-conditioned" was defined
before or after the four numbers were seen, since the excluded fourth box gives 1.4878 rather
than ~1.37.

**THE NEXT MEASUREMENT.** The floor. The bulk pressure field is hydrostatic and the anomaly
sits at the bottom boundary. d11-accessor owns the floor treatment (they ran the one-line
engine A/B that fixed 96.40 percent of the leak) and d21-jobb owns the sphere scene.

---

## 2. THE PATTERN THAT ORGANISES EVERYTHING ELSE

**Eleven instrument failures were found in one night, all the same shape: a code path that
returns a value indistinguishable from a measurement when it could not measure.**

| # | instrument | how it failed toward looking correct |
|---|---|---|
| 1 | `stationarity.py` | `n < 10` returned 0.0, and 0.0 is the pass value |
| 2 | `grep -c ... \|\| echo 0` | "0\n0" is not an integer, comparison errored, fell to else |
| 3 | `all([])` | verdict True over zero data |
| 4 | add/add merge control | both arms returned 1 because the branch did not exist |
| 5 | `--query` | matched title and abstract, never authors, so 0 was unreachable-not-absent |
| 6 | `r8_preflight.sh` | checked CLAUDE.md drift, silently ignored the authority skill |
| 7 | `gh run view --json` | `conclusion: success` on a step that exited 1 |
| 8 | mesh acceptance checks | watertight, manifold, right bbox, all on a one-blob-per-particle mesh |
| 9 | caption strip | clipped the very number it was asked to carry, silently |
| 10 | WebSearch | returned zero on a dead model pin, reading exactly like absence |
| 11 | control-volume synthetic check | pressure and weight consistent BY CONSTRUCTION, blind to conditioning |

Number 11 is the sharpest: the tank-wide version returned **-162.6 N against 44.6 analytic**,
and it was not an algebra bug. `p_face*A = 4254.85` against `W = 4417.45`, so the answer is
**1.05 percent of either term** and a 1 percent error anywhere is a 95 percent error in the
result. The synthetic check passed at -1.38 percent because its inputs were consistent by
construction. **The fix is not a better check, it is to report a conditioning number beside
every differenced quantity.**

Six of the first eight were caught by their own authors, after publication. The review layer
caught none of them, because it was dead all round (see section 5).

---

## 3. WHAT EACH SESSION ESTABLISHED

155 distinct commits since 17:00 across fourteen branches.

- **d11-accessor** (16c). Hydrostatic column pre-registered before the run. Rejected its own
  PASS on dispersion, then found the rejection was itself an over-correction because it used a
  raw std where criterion 3 mandates a blocked SE. Diagnosed the scatter as ACOUSTIC RINGING,
  measured: tau_int 1.78 and 2.51 frames against a 2.447-frame acoustic transit at
  c = sqrt(K/rho) = 12.2585 m/s. Found the column drains with NO BODY in it, `n_below_floor`
  0 to 46,926 over 180 frames. One-line engine A/B (`< 0.0` against `<= 0.0`) fixed **96.40
  percent** of the leak. Then found the column never quiets and corrected its own exoneration.
- **d12-kramerdata** (6c). REFUSED to submit Job C on the recorded ladder-stop, spending zero
  SUs. Established criterion 3 grades a normalisation not a force, from source. Pre-registered
  four criteria against four outcomes so the measurement picks the answer. Caught its own
  `CODE_META` claiming nothing was transcribed while being hand-transcribed.
- **d13-renders** (16c). Cycles path tracing replaces a painter's-algorithm plotter. Found
  `pysplashsurf`'s docstring wrong about its units, producing a mesh that passes watertight,
  manifold and bbox checks while enclosing 0.0002 m3 instead of 1.457. Priced the mesh swap
  and REFUSED it with numbers: the waterline crosses the ROCKER, so a substituted body moves
  the drawn waterline 1.78x at the median and 27x at p5. **The smoothest Rogue on disk is
  missing 47.6 percent of the car.**
- **d14-corpusbib** (8c). The corpus index holds NO FULL TEXT: 15 fields, none a body or PDF,
  largest text blob 3,477 characters, 110 of 332 records with no abstract. Built from 8 of 21
  deep searches. `--query` matched title and abstract, never authors. Then absorbed 75 lines
  to turn the hardest merge in the landing sequence into a fast-forward.
- **d15-settle** (10c). Velocity equilibrates and displacement CANNOT, because displacement
  integrates velocity, so no window of it is stationary at any length. 400 frames costs 21
  seconds. The terminal-frame problem demonstrated: distance peaks 0.667 m and ends 0.291 m,
  **43.6 percent of its own peak**, which gives CLAUDE.md item 5 a mechanism. Found 35
  comparable long records already existed, so a claim that needed new runs did not.
- **d16-landing** (7c). The branch is 5 BEHIND as well as ahead. CI green for two days with a
  check exiting 1 inside it. Refuted the coordinator's register row C1 with a two-arm control.
  Produced an execution card: one merge, seven files, zero decisions.
- **d17-moving** (19c). Ground-frame moving vehicle, two videos delivered and verified five
  ways. Closed C-1, the only item the cross-session readout listed as unowned. The crowned road
  cuts load **36.5 percent** level-fixed, but the depth-matched difference **REVERSES SIGN**
  between 2 and 4 percent camber, -18.6 to +6.0.
- **d18-platform** (15c). Dataset, Space and W&B live. Caught its own overwrite of a published
  physics fix. **The whole r9 wave is invisible to W&B except one run pushed by hand.**
- **d19-priorcode** (15c). Prior art is **at least fourteen works**, every DOI resolved against
  Crossref, and the shipped paper cites ONE. Found `alqadami2022` resolving to TWO DIFFERENT
  PAPERS in two bib copies. Refuted its own "does not converge" headline on four points.
- **d20-reader** (4c). Read 18 transcripts totalling 42 MB and 42 commit bodies in full. Found
  the research-corpus skill in FOUR states across nine worktrees, with eight of nine sessions
  unable to see a night of corrections, and the propagation damage timed to the minute: fix at
  00:21, sibling committed the pre-fix claim at 00:43. **Every dispatching session has 76 MCP
  connectors and every dispatched session has 17.**
- **d21-jobb** (13c). E1 refuted at two resolutions. Locking refuted on its PPC signature.
  Withdrew its own non-convergence claim. Built the third accessor and the reusable
  five-question scope test for candidate papers.
- **d22-gapscan** (16c). Want list of **261 distinct works**; 68 reachable, 162 not, with
  barriers counted: 105 closed, 49 no-DOI, 57 OA-but-host-refuses. Found WebSearch dead on the
  same model pin as the Agent path. Records every fetch with its HTTP code so a refusal cannot
  later read as an absence.
- **d23-overleaf** (new, launched 01:18). Owns the paper.

---

## 4. WHAT THE LITERATURE ACTUALLY SAYS, READ FROM FULL TEXT

Six papers read via the connector, plus later work. Full working in
`docs/R9_CORPUS_READ_2026-08-19.md`.

- **Wallstedt and Guilkey 2007.** The mass-weighted projection is exact only for linear fields
  under symmetric particle placement; for non-linear fields increasing PPC does not remove the
  error, which reaches a GRID-SET plateau. Two claims I relayed from a subagent summary were
  NOT in the paper and are withdrawn: the "constant systematic bias for a fixed body" framing,
  and the O(h) scaling, which was read off a figure by eye when the paper's own reference has
  an h^2 grid term.
- **Steffen 2008.** Quadrature error with B-splines, explicitly NO one-signed bias.
- **Quinlan 2018.** Hydrostatic tank where kinetic energy decays to **machine zero, 1e-13 to
  1e-18**, second-order pressure convergence. Ours grows.
- **Zhao, Jiang and Choo.** Volumetric locking, strip footing over-predicting bearing capacity
  45 to 55 percent and NOT remedied by refinement. Correct citation is **IJNME
  10.1002/nme.7347, not CMAME**, which I got wrong repeatedly.
- **Amicarelli 2015.** Read in full by d21 after I relayed it: half holds and it is the wrong
  half. The 10 percent is a peak PRESSURE COEFFICIENT not a force; the boundary treatment is
  not named as the cause; and three scope facts disqualify it independently, any one
  sufficient. Purely SPH with a non-computational neighbour grid so no velocity projection
  anywhere; Adami dummy wall particles this solver does not share; and a 2D impinging jet with
  a real free stream against our hydrostatic scene at mach_peak 0.0.
- **SPHERIC Test 12**, fetched live: 10 x 5 x 29 cm prism, relative density 0.68, mass 0.986
  kg. **States NO quantitative tolerance, no acceptance criterion, no error percentage**, and
  forces are inferred from motion rather than measured. Test 14 is free heave of an
  axisymmetric round-based body.
- **The field does not publish a tolerance on a static FORCE.** Kramer's 0.3 percent is a
  motion uncertainty on drop height. This matters for the criterion-3 rewrite: there is no
  external band to inherit, so any band is this project's own choice and must be labelled so.
- **Patents and OEM specs were never searched by anyone.** One query found four Land Rover
  wading patents (US20140371976A1, US20150066339A1, US20140347178A1, US10279681) and a
  published **500 to 900 mm per-model wading capability**. A novelty claim that has not looked
  at patents or manufacturer specifications is a papers-only claim.

---

## 5. INFRASTRUCTURE: WHAT WAS BROKEN AND WHAT IS FIXED

**Fixed tonight, with falsifiers named and tested:**

- `gate_destructive.sh` and `gate_concurrent_write.sh` blocked real work twice in ten minutes
  because a HEREDOC carries file content inside `tool_input.command`. Now strip heredoc bodies
  before matching. Real force-push DENY, heredoc mentioning it ALLOWED. Also closed a
  pre-existing hole: the comment claimed `git -C . add -A` was matched and it never was.
- `r8_preflight.sh` skill-drift check compared `wc -l`. Two 3-line files differing in the
  middle line compared equal. Now hashes.
- `r8_launch.sh` hardcoded `--effort max` for every session. Documented default is `high` and
  max is documented as prone to overthinking. Now per-slot. Adding that column would have
  SILENTLY cancelled plan mode on every read-only slot, because `permmode` was read as `$NF`.
  Columns now resolve by header name.
- `r8_send.py` refused d18 at age 27012s while its pane sat idle. Five slots report an
  IDENTICAL age of 26311s, which is the pre-crash transcript. Five sessions do not fall silent
  in the same second. Now falls back to the pane past an implausible age; both directions
  tested.
- `orient_live.sh` banner said the CI "runs nowhere". It has run seven times, green, over a
  check exiting 1.
- `r9_followup_debt.sh`, NEW. Measures what nobody was measuring: commits landed on a slot's
  branch since the last dispatch actually delivered to it. First pass: EIGHT of twelve slots
  carried unanswered output.

**Still broken:**

- **The `physics-skeptic` and Agent path died on `deepseek-ai/DeepSeek-V4-Flash:deepinfra` for
  the entire round**, and an explicit model override does not reach it. WebSearch shared the
  same pin. Both work again as of 01:12. Every physics claim made before then is marked
  UNREVIEWED and that is accurate, not a formality.
- **Coordinator sessions have 76 MCP connectors, slot sessions have 17 with zero bridged
  claude.ai connectors.** Every connector instruction written from the coordinator seat is
  written from an environment the recipient does not have.
- **The account hit its monthly spend limit** at about 00:36. 88 of 103 agents in one workflow
  died on it. Panes read "Now using usage credits". This falsifies the "Console Against Can It
  Ford" artifact's headline finding of ZERO limits across 28 days and 72,126 turns, which was
  true when written on 2026-08-17.

---

## 6. VISTA, AND THE ALLOCATION QUESTION ANSWERED

- **The allocation was never the constraint.** 593 SU remain of an expiring-2026-09-30 grant,
  and tonight's entire wave of roughly twenty jobs cost single-digit SUs.
- **Walltime over-request was the constraint.** Six jobs asked **11 hours** between them and
  used **3 h 53 m**. `r9_settle_longrec` asked 2:00:00 and ran 00:01:06. The clean experiment:
  `r9_est_b` asked 75 minutes and NEVER SCHEDULED; resubmitted at 15 minutes it started at once
  and finished in 6:24. Slurm backfills a short job into a gap a long request cannot fit.
- **Apptainer is NOT needed and should not be added.** It appears only in the abandoned
  Genesis-era scripts under `road_grid_2026-08-05/`. Every warpmpm job runs from the native
  venv at `/work/11603/jcerrell0629/vista/.venv`. Both apptainer binaries exist if ever needed
  and `module load tacc-apptainer` still fails over non-interactive ssh.
- **The CPU lane is open and unused.** `gg` is CPU-only and has held 50 to 80 idle nodes at 144
  cores each all night. Its venv imports numpy 2.5.1, scipy, trimesh, matplotlib and warp, and
  `pysplashsurf` was installed into it tonight. **369 metrics.csv and 339 rollout.npz** sit on
  Vista, against the 21 to 51 records the settle work has been reasoning from.
- **Do not fill idle nodes with work that does not need them.** That is the same error as
  leaving an idev session idle. Inventory first; a null is a real result.

---

## 7. THE COORDINATOR'S OWN FAILURES, RECORDED BECAUSE THEY WILL RECUR

Five relay errors, all the same shape and all in the same direction, toward the stronger claim:

1. Wal07's "constant systematic bias for a fixed body" — a subagent's REASONING section
   relayed as the paper's text.
2. The same paper's O(h) plateau scaling — measured off a figure by eye.
3. "None of the six prior-art DOIs is in the corpus" — all six are present. The true finding
   was narrower: the query predicate cannot see authors, and `research_index.py` does not exist
   on `origin/main` at all.
4. "Six public empty HuggingFace repos" — `usedStorage` counts LFS only, so a repo full of CSV
   and Python reads 0 B. Two are bare, not eight, and the one I called an empty public dataset
   named after the field's open gap is fully populated.
5. Amicarelli relayed as a mechanism match; it fails three independent scope tests.

Plus two structural ones:

- **I widened the only merge conflict still growing.** Closing stale register rows directly on
  `add-ci-checks` added 35 lines absent from the reconciled `r8-register`, and a row marked
  OPEN and UNOWNED was already fixed on another branch, producing two repairs to one file.
  Register rows belong on `r8-register` until it lands.
- **I reported a session stalled for five hours** when it was mid-turn, and reported twelve
  pending approvals when there were zero, because my sweep matched the word "permission" in the
  status bar.

The durable fix is d21's `docs/CANDIDATE_PAPER_SCOPE_TEST.md`: five questions to ask a paper
before relaying it, with the rule that passing all five makes it a MECHANISM, passing some
makes it a PRECEDENT, and the write-up must say which.

---

## 8. WHERE TO PICK UP

1. **Read the adversarial review when it lands.** It is attacking the exoneration's
   independence claim, which is the one thing that could void the night's headline result.
2. **The floor is the next measurement.** Bulk field hydrostatic, disturbance at the bottom
   boundary, and the one-line engine A/B already fixed 96.40 percent of the leak without
   quieting the column.
3. **Rewrite criterion 3.** d12 has four criteria pre-registered against four outcomes. The
   third accessor has now landed, so the outcome is determined and the rewrite can be finalised
   without anyone choosing.
4. **d23-overleaf owns the paper.** Four defects in the submitted draft, three refuted by files
   already in this repo, plus a bib key resolving to two different works. It must NOT push to
   overleaf: that remote shares no ancestor with origin and a push OVERWRITES.
5. **Land the merges.** d16's execution card is one merge, seven files, zero decisions, and
   explicitly says to read nothing above it.
6. **194 commits were on no remote and in no bundle** at 00:13. A 489 MB all-refs bundle was
   made at 00:14 and verifies complete, and `claude/add-ci-checks` was pushed at 01:17
   (`faf53d1..617f34b`, verified local equals remote). The other thirteen branches are still
   local only.
7. **Four world-readable 0644 token files exist** and four byte-identical copies of `.env`
   mean any rotation must cover all four. The write-up is at
   `~/can-it-ford-audit/2026-08-20/` and deliberately OUTSIDE this public repo.
