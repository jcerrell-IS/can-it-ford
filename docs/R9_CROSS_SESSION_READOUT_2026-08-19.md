# R9 cross-session readout, 2026-08-19

**Snapshot 18:44:44 BST, taken with `date`, not from any session banner.** Nine sessions
were still committing while this was written: `e7a0db3` landed at 18:43, one minute before
the snapshot. Every branch tip and dirty count below is as of 18:44. Treat any tip as
possibly superseded and re-derive before acting.

Written by slot d20-reader. Write scope: this file and `analysis/r9_session_reader.py`.
Nothing else was edited, on any branch, in any tree.

## Method, and what it could not see

Built with `analysis/r9_session_reader.py` (streaming JSONL parser, `--self-test` passes
10 of 10 guards), plus `git show` of every wave commit body in full, plus direct file reads.

| layer | what I read |
|---|---|
| transcripts | **18** JSONL files, 42,021,315 bytes, all streamed, none slurped |
| commits | 42 commit bodies in full, plus diffstats |
| files | the register, the board (226 KB), SKILL.md at four refs, 17 wave scripts |
| primary literature | 4 full-text PDFs via Undermind, and 2 of the 20 deep searches |

**Tagging.** Everything below is *read directly* unless marked *inferred*. Numbers
attributed to a session are that session's measurement, not mine, unless I say I
re-derived it.

**Not reviewed.** The adversarial subagent path is dead (finding C-2). I attempted it
twice at 18:37 and 18:38 and both attempts died. **No claim in this document has been
reviewed by a second party.** My own novel claims are C-8, C-10, C-12, C-16, C-17, the
cross-session half of C-19, and the section 5 items. They are self-verified only.

---

# 1. Per session

Branch tips and dirty counts at 18:44. "dirty" is uncommitted work in flight.

### d11-accessor, `claude/r9-accessor`, tip `e4e05a8`, dirty 2
Established that Job B's defect was never two numbers disagreeing but a **specification**:
the designation of which accessor criterion 3 grades lived in one comment, and each new
tool re-decided differently (`06c7786`). Re-graded from raw geometry: **Job B FAILS at
every one of 24 gradings** across six runs, +34.4 to +64.2 percent, best run missing even
the PARTIAL band by 9.4 points; window choice moves it 2.0 points, seed 0.4, numerics
0.0006 (`8f978c1`). Then retracted its own P-2 floor answer the same day it wrote it, and
in `05fb6db` retracted the retraction's *scope*, saying plainly that the floor question is
open in principle and closed only for this decision. `e4e05a8` corrected its own
enumeration from 6 sites to 13 and withdrew a "same content" claim it had asserted without
checking.

### d12-kramerdata, `claude/r9-kramer-extract`, tip `94b56b8`, clean
Extracted all 31 numerical series of the Kramer 2021 archive and established the headline
is **grouping-key dependent**: 5 of 6 independent groups reproduce the benchmark to within
0.82 percent by author, 4 of 6 by institution, with the whole envelope set at both ends by
one group (`c2f3592`, `0cb2855`). **Withdrew its own Job B placement** in `b6fe951` after
the coordinator's attack broke the force-to-period bridge. `1f126dc` added fail-loud guards
whose first catch was a number in its own document that did not regenerate. `94b56b8`
established that the "0.3 percent experimental uncertainty" is the paper's own abstract,
reproducing from its supplementary at 0.2915 percent, and is **normalisation dependent**:
5.1x to 5.2x larger against the local signal, 53x at worst.

### d13-renders, `claude/r9-renders`, tip `3d01611`, dirty 2
`256d013` found that 54.9 percent of 9000 faces landed at Fresnel F>0.9 with 77.4 percent
of those back-facing, and that **there was no ground plane at all** to wire the asphalt to.
Reported without changing: the reconstructed hull is closed but has **genus ~100**.
`d55ac14` is a crash-recovery commit preserving two Blender Cycles files **neither
committed by their author nor ever run**. `3d01611` at 18:40 reports the water rendered as
one blob per particle because a library docstring is wrong.

### d14-corpusbib, `claude/r9-corpus-bib`, tip `5680a20`, clean
The most corrective session of the wave. Established the **five-rung ladder** (332 corpus /
76 DOI-in-tree / 43 reader-facing / 4 in shipped bib / 3 actually cited) and that the
corpus's single in-scope absence is `shah2018` (`59c12b2`, `8bad9b4`). Found `--query`
matched title and abstract only and **never authors**, so an author query could not
succeed; fixed, 0 becomes 5 for Al-Qadami. `6ecf4e5` established the structural defect:
`REPORTS` is a hardcoded eight-entry list, so `--build` **cannot reach** a new deep search
and never could, and the index holds **8 of 20**. `5680a20` measured that **332 records are
319 distinct works**.

### d15-settle, `claude/r9-settle`, tip `836ea52`, clean
`0726c18` established that `settle_frames` runs *before* recording starts, so the 91
recorded frames contain zero settle frames and the "25 of 25 need more than 8 discarded"
finding does not imply `settle_frames=48`; recommends 14. Corrected the audited population
from 25 to **51 records, 48 distinct**. `0861b52` found `stationarity.py` returned a
confident verdict on inputs it never evaluated. `e50191b` priced the asymmetric rule: the
wrong rule on a verdict moves 16 of 24, and **all 30 moves delete a SLIDE and 0 create
one**. `836ea52` established that the published 16 SLIDE / 1 STUCK was computed under the
correct rule from the start, and that `final_disp_mag_m` obeys neither rule because it is a
single terminal frame.

### d16-landing, `claude/r9-landing`, tip `e7a0db3`, clean
`50ae6ce` produced the landing plan and its headline is the *behind* half: `add-ci-checks`
is 5 behind as well as 64 ahead. `8c07765` **refuted the coordinator's register row C1**
with a two-arm control. `ba1abbb` recorded that the branch set is a rate, not a list.
Detected the **seventeen-hour clock gap** nobody else's instrument caught. `e7a0db3` at
18:43 reports the CI has been green for two days with a check exiting 1 inside it, and five
conflicting files, not one.

### d17-moving, `claude/r9-moving-vehicle`, tip `c94f3f8`, clean
Pre-registered the load surface **before any GPU run** (`d3e52fd`), then measured
S = 0.8837 against a pre-registered 0.10 (`056ba10`). `159bf7d` generalised it across five
relative speeds, S rising 0.76 to 1.28, with the worst-case split *moving* between 3.0 and
4.5 m/s. `498f1ad` landed the second g96 seed and the grid result held to under 0.04
points. Found two of its own defects by control, including a label collision that silently
overwrote four of five cells. `c94f3f8` at 18:41 reports fixed-seed determinism holds only
near rest and the bc guard was self-bypassing.

### d18-platform, `claude/r9-platform`, tip `866238a`, dirty 7
`c7000ea` established the one verdict that changes a decision: **Zenodo mints a DOI for a
restricted record**, so citability does not require publishing. `3016b16` found a **public
empty dataset already on the Hub** under this project's name with 22 downloads. `6d761e7`
corrected three false claims on the Space README. `f988882` and `a08b6eb` are two
self-corrections in four minutes. `866238a` ingested d17's real surface and **inverted
d17's headline pair** (finding C-1).

### d19-priorcode, `claude/r9-priorcode`, tip `2f3a4a9`, clean
`fdf934b` established a negative that changes a plan: the Zhao 2019 in/outflow BC is
**absent from all 16 remote heads of public Anura3D**, so `openchannel_bc.py` cannot be
validated by reading their code. `a863ee7` reframed P-2: its **zero-penetration floor is
7.88 to 10.02 percent against a 10 percent gate**. `f31a71f` measured Chrono::FSI-SPH
missing analytic buoyancy by **+48.04 percent**, with the refined run worse at +57.87.
`4d7c2c1` **refuted its own headline** using a local read of sdfibm at upstream rev `3627269`. `2f3a4a9` gave the
three-family taxonomy and explained why its own write-up was invisible to everyone.

---

# 2. Every number stated, and where it collides

Collisions are marked. A number with no collision row is uncontested *as far as this sweep
saw*, which is not the same as correct.

## 2a. Contested quantities

| quantity | value | source | competing value | competing source | status |
|---|---|---|---|---|---|
| load ratio, (2.20, 3.00) vs (4.50, 0.50) | **2.3x** (8621 / 3811 N) | d17 `056ba10`, doc lines 470-472 | **0.912x** (5176.5 / 5675.3 N) settled window | d18 `866238a` | **OPEN, C-1** |
| deep searches in workspace | **19** | coordinator `faf53d1` | **20** | d14 `6ecf4e5`, d16, and my live read | settled at 20 |
| of those, ingested | "eight checked, all absent" | coordinator `faf53d1` | **3 of those 8 ARE ingested; 8 of 20 total** | d14 `6ecf4e5` | settled, coordinator wrong |
| `make_phase_space.py` copies | **70**, split 35/35 | register C2 | **58**, split 29/29 | d16 `8c07765` | **both stale, C-8** |
| same, at 18:35 | **60**, split 30/30 | me, live | | | mechanism in C-8 |
| corpus distinct works | **332** | CLAUDE.md, SKILL.md | **319** | d14 `5680a20` | **OPEN, C-11** |
| `test_physics_gates.py` added by | `df52bee` | coordinator `faf53d1` | **`50b70c0`** | d14 `026f931` | settled, coordinator wrong |
| SLIDE, full record, magnitude | 21 of 24 | d15 | | | reproduces `probabilistic_verdict.py` |
| SLIDE, full record, surge | 19 of 24 | d2-persist via d15 | | | |
| SLIDE, transient removed | 5 of 24 | d15 | 5 on both channels | d15 `e50191b` | settled, channel-invariant |
| threshold-flip count | 17 of 24 | CLAUDE.md | **15 of 24** on surge | d2-persist | **both right, C-4** |
| verdicts moved by wrong rule | 16 of 24 magnitude, 14 of 24 surge | d15 `e50191b` | | | 30 moves, all deletions |
| Job B, measured accessor | **+50.06 pct** canonical | d12 `79dab7d` | **+34.4 to +64.2** over 24 gradings | d11 `8f978c1` | consistent, wider set |
| Job B, nominal accessor | **-29.11 to -9.67 pct** | d12 `b6fe951` | | | opposite sign, same frames |
| Job B period-equivalent | -18.37 and -12.65, both outside envelope | d12 `79dab7d` | **-18.37 to +8.02, five inside** | d12 `b6fe951` | **withdrawn, C-7** |
| P-2 zero-penetration floor | **7.88 to 10.02 pct** vs a 10 pct gate | d19 `a863ee7` | | | reframes "7 of 17 fail" |
| criterion 3 floor proxy | **7.28 to 7.67 pct** vs a 10 pct gate | d11 `05fb6db` | | | pass band is mostly floor |
| SDF-collider buoyancy error | 7.3 to 7.7 pct | CLAUDE.md A-2 | | | |
| Chrono::FSI buoyancy error | **+48.04 pct** at spacing 0.030 | d19 `f31a71f` | **+57.87 pct** at 0.020 | d19, same commit | refines the hypothesis |
| worktrees missing the CI block | **11** | d18 `f988882` | the block's message is itself false | d16 `e7a0db3` | **C-18(a)** |
| conflicting files at landing | **1** (`openchannel_bc.py`) | d16 `50ae6ce` | **5**, across four merges | d16 `e7a0db3` | self-refuted |
| CI workflow status | "runs nowhere" | banner, d16 `50ae6ce` | **ran 7 times, green over exit 1** | d16 `e7a0db3` | self-refuted |
| `DRIFT_THRESHOLD` totals | 22 / 23 / 24 | CLAUDE.md item 13 | **16/17 in a CI checkout**, a third axis, 8 totals | d16 `e7a0db3` | **OPEN** |
| fixed-seed spread, SDF path | **4.7e-6**, "effectively deterministic" | d17 `056ba10`, dispatch | **0.0037 to 0.5881 pct**, monotone in speed | d17 `c94f3f8` | **self-refuted, C-19** |
| same, corroborated | 4.687e-6 | d18 `866238a` | measured only in the regime where it holds | me, C-19 | narrower than it reads |
| hull spread, as simulated | 155x | d13, earlier | **12.55x** | d13 `3d01611` | self-refuted |
| worktrees missing the corrected skill | | | **8 of 9** | me, C-17 | **new** |
| transcript bytes named in the TSV | | | **38.7 pct** | me, C-10 | **new** |

## 2b. Numbers I re-derived myself

| quantity | my value | method |
|---|---|---|
| transcript files for the nine slots | **18**, 42,021,315 bytes | `--inventory` |
| bytes named in `r8_session_ids.tsv` | **16,261,865**, 38.7 pct | same |
| `make_phase_space.py` copies at 18:35 | **60**, exactly 2 per tree across 30 trees | `find` + `md5` |
| deep searches in the workspace | **20** completed | `inspect_deep_searches`, live |
| SKILL.md lines by ref | 0 / 152 / 249 / 523 | `wc -l` per worktree |
| `stationarity.py --self-test` | 0 failures | ran it |
| `r9_prior_code_compare.py --self-test` | PASS, 2 OK + 2 FLAGGED | ran it |

## 2c. From primary literature, read tonight, not previously in any session's record

| quantity | value | source |
|---|---|---|
| Shah 2018 scale | **1:10**, Perodua Viva | `[Sha18c]` full text, Table 1 |
| Shah 2018 critical depth | **0.0457 m** at model scale | `[Sha18c]` p.7, Fig 5 |
| Shah 2018 drive force | **0.00169 to 0.02115 N** at 1:10 | `[Sha18c]` Table 6, p.11 |
| Shah 2018 vehicle speed | **not an independent variable** | `[Sha18c]` methodology |
| IBAMR FD/BP force | surface integral, **dt absent**, Eq. 30 | `[Bha19]` s4.2.3 |
| IBAMR FD/IB force | momentum difference, **divides by dt**, Eq. 40 | `[Bha19]` s4.2.4 |
| FloatStepper heave-decay case | **does not exist** in the paper | `[Roe23]` |

---

# 3. Contradictions and corrections

**The three that matter most are C-1, C-2 and C-17.**

## C-1. d18-platform inverts d17-moving's headline pair, and d17 has not answered. OPEN.

d17-moving's committed document states, as "the contribution stated as a number" at lines
470 to 472: `(v_car 2.20, v_water 3.00)` carries 8621 N at |v_rel| 3.720 m/s while
`(v_car 4.50, v_water 0.50)` carries 3811 N at |v_rel| 4.528 m/s, so **the cell with the
lower relative speed carries 2.3x the load** (`056ba10`).

d18-platform ingested the same 348 records into the Space and recomputed (`866238a`):

| window | ratio | note |
|---|---|---|
| frames 20-60 (transient) | 8621.4 / 3811.1 = **2.262** | reproduces d17 |
| frames 250-400 (settled), 5 seeds | 5176.5 +/- 4.0 / 5675.3 +/- 13.0 = **0.912** | direction reverses |

The ratio crosses 1. Per-cell seed spread is 0.066 to 0.338 percent, so this is not noise.
Same hull, grid and depth in both windows (`fz_settle_N` 9149.19 and `f_buoy_analytic_N`
4468.622 identical), so the window is the difference.

**I verified d18's absence claim independently.** In d17's committed document,
`/usr/bin/grep -c` returns **0** for `L2full`, `5028`, `5534`, `9577` and `30211`. The
settled-window data is in the shipped TSV and appears nowhere in the document built from it.

**What survives on both sides:** the general result, S = 0.76 / 0.97 / 1.07 / 1.12 / 1.28
across |v_rel| 1.0 to 6.0. Only the specific published pair fails to survive the window
change. d18 says "it is not mine to close" and names one confound it could not close:
`hull_y_m` is empty in `c3full`.

**This is exactly the class d15-settle priced tonight**: a window choice that changes a
published number. d15's rule is full record for a verdict, demonstrated-stationary window
for a convergence or uncertainty claim. **Nobody has asked which of the two the load ratio
is.** It is neither a verdict nor an error bar, which is d15's own third class from
`836ea52`.

## C-2. The adversarial review path is dead fleet-wide. I confirmed it as the eighth slot, and the exact model id exists in no committed file.

Marked UNREVIEWED by d11 (`8f978c1`), d12 (`c2f3592`), d14 (`59c12b2`), d15 (`0726c18`,
`0861b52`, `e50191b`), d18 (`866238a`) and d19 (`fdf934b`, `a863ee7`, `f31a71f`,
`0a83b75`, `4d7c2c1`).

**My own two attempts, 18:37 and 18:38:**

| attempt | agent | model | result |
|---|---|---|---|
| 1 | `physics-skeptic` | default | failed: `deepseek-ai/DeepSeek-V4-Flash:deepinfra` |
| 2 | `general-purpose` | explicit `opus` | failed: **identical error** |

So the `model` override is **ignored**, confirming d15-settle and d19-priorcode from a
ninth origin. The agent *launches* and then dies, which is why it reads as a transient.

**The finding nobody has recorded:** the exact model string appears in three sessions'
transcripts (d12 17:03, d15 17:26 and 17:36, d19 17:21) and in **zero committed files**.
`/usr/bin/grep -ric deepseek docs/*.md` returns nothing. Transcripts are not a deliverable.
The one actionable detail, that the failure is a pinned nonexistent model and that the
override does not reach it, exists only in scrollback.

**Consequence:** essentially every physics number this wave produced is self-reviewed only.

## C-17. The authority skill exists in four states across nine live worktrees, and the preflight that exists to catch exactly this does not check it. NEW.

Measured live at 18:44:

| state | lines | worktrees |
|---|---|---|
| absent | 0 | r9-accessor, r9-kramer-extract |
| stale | **152** | r9-renders, r9-settle, r9-landing, r9-moving-vehicle, r9-platform, r9-priorcode |
| coordinator's | 249 | main checkout (`add-ci-checks`) |
| corrected | **523** | r9-corpus-bib only |

**Eight of nine sessions cannot see d14-corpusbib's night of corrections.** The 152-line
version six sessions load still asserts, verbatim:

- line 11: "256 are cited" nowhere, the clause CLAUDE.md **withdrew on 2026-08-18** and
  which register row B1 lists as OPEN
- line 111: "no physics regression test; `tests/` holds only `test_count_claims_check.py`",
  refuted by d14 `026f931` (12 test functions, added by `50b70c0`)
- line 149: "Widen with `--query` before concluding the corpus is silent", advising the
  tool whose author-blindness d14 fixed at 00:21

**The propagation is already measured, not hypothetical.** d14 fixed `--query` in `8bad9b4`
at **00:21**. d17-moving wrote into `056ba10` at **00:43**, twenty-two minutes later:
"`analysis/research_index.py --query "Al-Qadami"` returns zero, so the corpus cannot report
on this topic's closest prior art". That is the pre-fix behaviour, quoted from a worktree
that could not see the fix.

**Why it is an instrument failure and not just staleness.** `scripts/r8/r8_preflight.sh`
runs first in every session and explicitly checks CLAUDE.md drift (its own comment at :11
cites the 676-versus-855 measurement). `/usr/bin/grep -n 'SKILL\|skills'` on that file
returns **zero hits**. The instrument built to detect frozen-at-branch-point staleness
checks one file and misses the other, and the one it misses is the file register B1 calls
"authority for every session that loads it". It fails toward looking correct: the session
sees confident numbers carrying scope statements and gets no signal that a sibling refuted
them hours earlier.

This is the **fifth instrument failure of the round**, after d15's stationarity test, d18's
errored comparison, d12's `all([])`, d16's two-empty-arms control and d14's author-blind
query.

## C-3. The register still asserts three things it or a sibling has refuted. OPEN.

Read live at 18:33 from `claude/add-ci-checks`:

- **A2** still reads "None of these six papers is in the 332-paper corpus index.
  `--query "Al-Qadami"` returns zero." **Refuted** by d14 `8bad9b4`: 4 of 6 are in the 332,
  including `10.1111/jfr3.12828`, and 5 records carry the author. The coordinator retracted
  this **verbally** (d14 board row 17:44, "the coordinator withdrew the Al-Qadami
  corroboration") but **the file was never updated**. The register is the corrections
  authority and it currently serves a claim its author withdrew.
- **B1** is listed "OPEN, UNOWNED". It is closed on r9-corpus-bib (`8bad9b4`) **and on
  add-ci-checks itself** (`faf53d1`): line 13 there now reads "DO NOT SAY 256 ARE CITED
  NOWHERE". The register lists as open an item its own branch fixed.
- **B7** is listed "OPEN, UNOWNED, trivial fix". Fixed on r9-settle (`0861b52`, which reads
  9.81 with a dated correction block); still stale on add-ci-checks, where
  `classify_failure_modes.py:30` reads 9.80665. So the row is right about the landing
  target and wrong that nobody owns it.

## C-4. The "N of 24" family: one denominator, seven numerators. RESOLVED tonight.

d14-corpusbib flagged in `026f931` that d2-persist and d15-settle disagreed about which
figure becomes 15 of 24, re-derived neither, and said so. **That was the right call and
d15 then resolved it** (`e50191b`): three quantities were in play, full-record SLIDE
21 -> 19, transient-removed SLIDE 5 -> 5, threshold-flip 17 -> 15. d2-persist's 15 is the
**threshold-flip** count; d15's own limitations bullet had read it as a SLIDE count.
**d15 records the error as its own.** `836ea52` adds that 16 SLIDE / 1 STUCK was computed
under the correct rule from the start.

## C-5. openchannel_bc.py: the coordinator wrong twice, in opposite directions. RESOLVED.

Register C1 first asserted an add/add conflict, then asserted none from content ancestry.
d16-landing refuted the second (`8c07765`) with a control distinguishing both arms:
identical blobs merge clean at exit 0, differing blobs conflict at exit 1. Mechanism:
`merge-base(add-ci-checks, r8-bc-merge)` is `1a868f3` and `ls-tree` of that base for the
path returns zero files. Coordinator accepted in `7a0d08a` and named the general shape:
"same lineage" and "merges cleanly" are different predicates.

## C-6. d19-priorcode refuted its own headline twice in twelve minutes. SELF-CORRECTED.

`f31a71f` (18:17) and `0a83b75` (18:20) asserted (a) ours is the **only** one of three
implementations needing a caller-supplied dt, and (b) the vehicle-fording case is "one
build target away". `4d7c2c1` (18:29) refuted both: sdfibm at upstream rev `3627269` (github.com/ChenguangZhang/sdfibm, not a SHA in this repo) makes it four
codes, two of which need a dt, and **the dt is what direct forcing means**; and the build
target does not exist because `CH_ENABLE_MODULE_VEHICLE_MODELS:BOOL=FALSE`, so it needs a
CMake reconfigure. d19 names its own habit: "I published an inference from preconditions
without running the one command that checked it, in the same document where I criticise
that habit."

**I extended this from primary source and it holds.** `[Bha19]`, the IBAMR paper d19 named
as unverified "family D", ships **two** accessors landing in **two** of d19's families:
FD/BP is a surface integral with **dt absent** (Eq. 30, family B), FD/IB is a momentum
difference that **divides by dt** (Eq. 40, family C). So family D is not a new family, and
a fifth code needs a dt for the same structural reason. d19's corrected conclusion is
stronger than it claimed.

## C-7. d12-kramerdata withdrew a published inter-code placement. RESOLVED as withdrawn.

`79dab7d` and `0cb2855` placed Job B outside the eleven-code envelope. `b6fe951` withdrew
it: across six defensible attributions the equivalent spans **-18.37 to +8.02 percent**,
five inside and one outside. Three separate errors named, including that a level cannot
constrain a slope and that the premise sentence was false because the +50.06 grade is on
the *measured* accessor while the named target is the nominal one. What survives: Job B
fails criterion 3 on its own terms, and 5 of 6 groups reproduce to within 0.82 percent.

## C-8. The 70 / 58 / 60 copy-count collision. Both published explanations are wrong. NEW.

Register C2 reports 70 copies of `make_phase_space.py`, 2 distinct, 35/35. d16-landing
measured **58**, 29/29, and attributed the gap to "a scope difference rather than a
disagreement" although **both stated the identical scope** (`/Users/josie/can-it-ford`
including `.claude/worktrees/`, excluding `.git/`). I measure **60**, 30/30, at 18:35 under
that same scope.

**Mechanism, measured.** There are exactly **two tracked paths**, and **every working tree
contains both**:

| path | md5 prefix (NOT a git object) | boundary operator |
|---|---|---|
| `analysis/make_phase_space.py` | `a3b48fa8` | `haz > 0.60` |
| `designsafe-staging/scripts/make_phase_space.py` | `a94b9915` | `h <= 0.60` |

A per-tree count returns exactly 2 for all **30** trees. So the total is
`2 x (number of checkouts)`, the split is *forced* to be exactly half, and the three
published totals differ because the number of worktrees changed over the day: 35 trees at
00:19, 29 at 17:15, 30 at 18:35 (mine is one of them).

**It is a time difference, not a scope difference, and there is no fork between trees at
all.** The register's "35 read one form, 35 read the other" invites reading two populations
of checkouts; the truth is two files inside every checkout. d16 already established that
the branch set "is not a list, it is a rate" and did not apply that to this number.

## C-9. Job B's criterion has almost the same pathology d19 found in P-2. Both quantified.

d19 (`a863ee7`): P-2's floor with **provably zero** water in any hull voxel is
**7.88 to 10.02 percent against a 10 percent gate**, so a P-2 FAIL can be produced by a
perfect simulation, and one run reads 10.02 at frame zero.

d11 (`05fb6db`), prompted by that: criterion 3's proxy floor is **7.28 to 7.67 against
10.0**, clearing by 2.33 to 2.72 points. So criterion 3 does **not** have P-2's exact
pathology, "but only just", and **the pass band is mostly floor**: any reading between
about 7.3 and 10 percent cannot distinguish good coupling from the floor. d11 gives the
falsifiable form: Job B reads 4.48x to 8.66x the proxy floor, so the FAIL survives unless
the true floor is at least 4.48x the estimate.

Both note the proxy is from a *different scene* and is the same number that set the bands,
so band and floor are not independent.

## C-10. The wave's session index covers 38.7 percent of the wave. NEW.

`.claude/state/r8_session_ids.tsv` names one session id per slot. **Each worktree has two
transcripts**, and the TSV names the later one:

- 18 files, **42,021,315 bytes** total
- TSV-named: **16,261,865 bytes, 38.7 percent**
- worst case r9-renders: 7.3 MB named, **12.6 MB unnamed**

Three slots (accessor, kramer-extract, settle) have pre-crash files ending 2026-08-18
23:22 to 23:27; the other six ran to 16:16-16:38 on 08-19 before all nine relaunched at
16:59. Anyone auditing "what did the wave do" from the TSV, as my own dispatch instructed,
sees under 40 percent of it. `r9_session_reader.py` defaults to all files and keeps
`--tsv-only` solely to demonstrate the gap.

## C-11. 332 versus 319 corpus works. OPEN.

d14 `5680a20` at 18:32: 11 Semantic Scholar ids appear under 24 record keys with
byte-identical titles, so **332 records are 319 distinct works**. CLAUDE.md and SKILL.md
both say "332 distinct external papers". Not yet corrected in either. Also from the same
commit: "60 with no DOI and therefore unmatchable" is d14's own line and is withdrawn in
that form, 57 carry a Semantic Scholar id already sitting in the `link` field and only 3
are unidentifiable.

## C-12. The deep-search layer contradicts two standing project claims. NEW, from primary source.

I read the workspace live. **20 completed searches**, confirming d14 and d16 against the
coordinator's 19.

**(a) `shah2018` is not absent from the project's research.** d14's headline is that
`shah2018` (`10.1051/matecconf/201820307003`) is the corpus's one in-scope absence and
"its DOI appears in none of the eight reports". Correct **for the index as built**. But it
is `[Sha18c]` in the search launched **today at 16:29**, with a **PDF available**, and I
read its full text tonight. The gap is an *ingestion* gap, not a *sourcing* gap, exactly as
d14's own `6ecf4e5` argues for `ccsa2016yaris`. One metadata discrepancy to flag: the
workspace record gives first author **Syed Hamid Hussain Shah** where d14's Crossref read
gave **Syed Muzzamil Hussain Shah**. Same DOI, so a name variant, and it is the known
Muzzamil/Hamid trap.

**(b) "Four prior vehicle fording or wading simulations exist" is an undercount.** That
figure is in CLAUDE.md and repeated in SKILL.md. The 16:29 search adds at least
`[Lyu23]` (`10.1016/j.compfluid.2023.106144`, particle-based 3D SPH vehicle wading),
`[Ols18b]`, `[Xin21b]` (`10.1177/0954407020942005`) and `[Var21]`
(`10.4271/2021-01-0205`). The claim "none of them prints in the reference list" is
unaffected; the integer is not.

**(c) The moving-refinement-window negative needs its scope narrowed.** The project records
"no moving-vehicle refinement window" across 206 papers. The 16:29 search says a
body-following refinement window "appears unreported" **for MPM**. `[Nan19]`
(`10.1016/j.jcp.2019.07.004`) does implement one in IBAMR by cell-tagging with the
structure constrained to the finest level, ground-fixed frame. So the negative holds for
MPM and not for the field.

**(d) A search commissioned for Job B's exact question was never cited by the session
working on it.** "MPM SPH buoyancy force overestimation and hydrostatic validation
benchmarks", Aug 18 05:09, states the goal as a sphere held at its waterline reading
**about 50 percent larger** than analytic buoyancy. Its summary names the missing
diagnostics as "force-extraction windows, pressure-surface versus impulse-exchange
cross-checks, or systematic particles-per-cell convergence". d11 spent this round on the
window and d19 built the pressure-surface-versus-impulse taxonomy. **Neither cites it.** It
is one of the twelve searches the builder cannot see.

## C-13. Corrections sessions issued against their own board rows, within minutes.

- d18 `a08b6eb`, six minutes after its own 17:34 row: wrong path (`.claude/hooks/`, not
  `scripts/`) and an insinuation it had not tested, refuted in one command.
- d18 `f988882`: its own table's every "NO" was produced by a **failed integer comparison**,
  because `grep -c ... || echo 0` appends a second zero. Correct by luck.
- d11 `e4e05a8`: "13 sites not 6", and a "branch copies of the same content" claim that was
  false for one of two files.
- d17 `159bf7d`: a label collision meant `SUMMARY_<label>_g<n>.json` held one cell where
  five ran, and the file "existed and parsed".

## C-14. The Space shipped a renderer over an empty table.

`6d761e7` committed `hf_space/data/load_surface.csv` as **one header line and zero data
rows**. d18 states the panel was built to refuse interpolation precisely so an empty table
could not read as a result. `866238a` filled it from a pinned git blob and **removed**
`surface.py`'s Panel 2 rather than leaving it, because it was written against a placeholder
schema the real data does not use and "would have returned not-computable forever without
ever saying it could not read the file". That is a sixth instance of the cannot-evaluate
class, caught by its own author.

## C-15. Two recovered files have never been run by anyone.

`d55ac14` preserves `analysis/cycles_render.py` and `analysis/prep_cycles_scene.py` from
the 17:40 crash and says explicitly: "NEITHER HAS BEEN RUN by me and neither was committed
by its author, so treat both as a draft." Both are **currently modified** in the r9-renders
worktree with an untracked `analysis/cycles_caption.py` alongside.

## C-16. One low-severity defect I found that nobody has named.

`simulation/moving_vehicle_channel.py:1091` prints
`rec["fz_settle_over_analytic"] or 0.0`. If that key is None on an OK cell, the console
prints `fz_settle/analytic 0.0000`, which reads as a measured zero vertical reaction rather
than as absence. It is a print statement, not a verdict, and the `status != "OK"` branch
already skips, so the impact is bounded. It is the same manufacture-a-value shape d18
named. Recorded for the owner, not escalated.

## C-18. d16-landing refuted two of its own headlines at 18:43, and one of them falsifies the banner every session reads. NEW, and it cascades.

`e7a0db3`, revision 3 of the landing plan, retracts three of its own earlier claims in
place. Two matter beyond that slot.

**(a) "The CI runs nowhere" is REFUTED.** `canford-checks` has run **seven times** on
GitHub, all job-level green, because its trigger is a bare `on: push:` with no branch
filter and `add-ci-checks` reached origin on 2026-08-18. Absent-from-main and runs-nowhere
are different claims and **only the first is true**.

This falsifies a string every session is shown at startup. My own session banner, printed
by `.claude/hooks/orient_live.sh`, read: "CI NOT LIVE: .github/workflows/canford-checks.yml
is not on origin/main, so it runs nowhere." **The banner is wrong**, and it is wrong in the
direction that matters, because the CI is not merely running, it is running **green over a
check that exits 1**: `count_claims` emits 25 BLOCK lines and
`##[error]Process completed with exit code 1` on a run reported green.

**The nesting is the finding.** d18-platform committed `f988882` establishing that eleven
worktrees "never see the CI warning" and treating that as the defect. d16 has now shown
**the warning those eleven worktrees are missing is itself false**. Both sessions are
individually correct and the pair inverts the priority: propagating that banner would
propagate a false claim.

**(b) "Exactly one conflicting file" is REFUTED: there are five, across four merges.** d16
names the methodological hole itself, and it is a clean instance of the round's dominant
class: the pairwise matrix tested **feature branch against feature branch and never against
the integration target**, so `.gitignore` could not have been found by re-running it. The
new conflicts are `.gitignore`, `SKILL.md`, and `hf_space/`.

**(c) Two consequences for dispatches in section 5, which I have corrected there.**
`SKILL.md` is a genuine union merge, **neither side is a superset**, and all 75 of
`add-ci-checks`' added lines are absent from r9-corpus-bib. And `hf_space/` is **two
different Gradio apps sharing one filename**: r9-platform's `app.py` contains no `AR_R`, no
`l1_verdict` and no `l0_depth_threshold`, so taking it would **remove PR #11's L1
joint-rule fix from a public page**.

**(d) `DRIFT_THRESHOLD` gains a third scope axis.** 24 declaration sites, **17 tracked and
7 untracked**, so a CI checkout computes 16/17 against CLAUDE.md item 13's accepted
22/23/24. Item 13 documents two binary choices giving four totals; this makes it three
axes and **eight**. Item 13's rule that a bare total is what is wrong now has a third
dimension and item 13 does not say so.

## C-19. d17-moving refuted the determinism figure that d18 had used to corroborate it. NEW.

`c94f3f8` at 18:41. The claim that the SDF path is effectively deterministic at fixed seed,
relative spread **4.7e-6**, is stated by d17's own document, by the previous session and by
the dispatch. d17 re-ran the five arcs at seed 0 under a new label. Every recorded field
identical. **They did not agree:**

| \|v_rel\| | max cell difference |
|---|---|
| 1.0 | 0.0037 pct |
| 2.0 | 0.0182 pct |
| 3.0 | 0.0764 pct |
| 4.5 | 0.3876 pct |
| 6.0 | 0.5881 pct |

Monotone, a factor of 160, which is why it is a finding and not jitter: jitter would not
order itself by velocity. **The 4.7e-6 was measured on the no-forcing control**, where
almost nothing is accumulated, and carried into a forced scene where it does not hold.

**The cross-session consequence nobody has stated.** d18's `866238a` lists among its
independent verifications: "the fixed-seed repeat spread reproduces d17's stated 4.7e-6 at
4.687e-6". d18 verified the number **in the regime where it holds** and reported it as
corroboration of a general claim that d17 has now shown to be regime-limited. Neither
session is wrong; the corroboration is narrower than it reads.

It also touches C-1 quantitatively. d18 argued the settled-window inversion "is not noise"
from a per-cell seed spread of 0.066 to 0.338 percent. d17's newly measured fixed-seed
nondeterminism at the relevant speeds is 0.0764 percent at |v_rel| 3.0 and 0.3876 at 4.5,
i.e. **comparable to or larger than the spread d18 quoted**. The inversion itself survives
easily, 2.262 against 0.912 is not a 0.4 percent effect, but **the error bars in C-1 should
be widened** and the phrase "seed noise floor" should become "total repeatability floor",
which is d17's own correction.

d17's headline is untouched and now reads S = 0.76 to 1.29 with error bars from 225 runs,
sd 0.0010 to 0.0026, every step between consecutive magnitudes 19 sd or wider.

## C-20. Two more instrument failures, bringing the round to eight. NEW.

**Seventh: a CI status field that cannot distinguish passed from failed-and-masked.** d16
`e7a0db3`: `gh run view --json jobs` reports the step as `conclusion: success` while the
log for that same step carries `##[error]Process completed with exit code 1`. Only the log
separates them. Anyone auditing CI health through the JSON API, which is the obvious
programmatic route, gets a clean answer from a masked failure.

**Eighth: every cheap mesh check passing on a completely wrong mesh.** d13 `3d01611`:
`pysplashsurf.reconstruct_surface` documents that "all parameters use absolute distance
units and are not relative to the particle radius". **That is false** for `smoothing_length`
and `cube_size`, which are read as multiples of the radius. Held fixed at 3779 particles:

| interpretation | connected bodies | enclosed volume |
|---|---|---|
| absolute, per the docstring | **3779** | 0.0002 m3 |
| relative, actual behaviour | **6** | 1.4570 m3 |

3779 bodies for 3779 particles is one blob per particle, so the fluid never becomes a
fluid. And d13 records the part that makes it an instrument failure rather than a bug:
**the fragmented mesh passes `is_watertight` True, passes edge-manifold, has a bounding box
matching the particle cloud exactly, and carries ten times more triangles than the correct
mesh.** Only enclosed volume separates it from a real free surface. The acceptance checks
in use could not have caught it.

d13 also corrects one of its own figures in the same commit: the as-simulated hull spread
is **12.55x, not 155x**, because the 155x rested on a mesh (`silverado_g32_pd8_dq0.02`,
2,108 verts) that appears in one tracked guard file and **no multigeom run ever used**.

---

# 4. Scripts inventory

## Created by the wave

| file | slot | lines | self-test | verified by me |
|---|---|---|---|---|
| `analysis/kramer_extract_numerical.py` | d12 | 1789 | yes, 8 of 8 guards fire | no, needs the archive |
| `simulation/moving_vehicle_channel.py` | d17 | 1103 | yes, 13 ST groups | no, needs GPU |
| `analysis/hf_dataset_publish.py` | d18 | 843 | yes, 17 tests | no |
| `analysis/r9_speed_surface.py` | d17 | 711 | yes | no |
| `hf_space/ingest_speed_surface.py` | d18 | 461 | yes | no |
| `hf_space/speed_surface.py` | d18 | 380 | yes | no |
| `analysis/r9_prior_code_compare.py` | d19 | 379 | yes | **yes, PASS** |
| `analysis/cycles_render.py` | d13 | 366 | **none** | **never run by anyone** |
| `analysis/wandb_speed_surface.py` | d18 | 305 | yes | no |
| `analysis/prep_cycles_scene.py` | d13 | 255 | **none** | **never run by anyone** |
| `hf_space/surface.py` | d18 | 188 | yes, 12 tests | no |
| `analysis/r9_chrono_tow_drag.cpp` | d19 | 183 | n/a | flagged by d19 as outside its declared scope |
| `analysis/r9_session_reader.py` | **d20 (this slot)** | 400 | yes, 10 of 10 | **yes** |

## Modified by the wave

`analysis/research_index.py` (d14, +~1200 lines over five commits, now 1769),
`analysis/settle_audit.py` (d15, 779), `analysis/stationarity.py` (d15, 566, **I ran its
self-test, 0 failures**), `analysis/render_multigeom_shaded.py` (d13, 1056),
`simulation/r5_physics/sphere_heave.py` and `grade_job_b.py` (d11),
`simulation/r5_physics/kramer_benchmark.py` (d12),
`analysis/classify_failure_modes.py` (d15).

## Duplication

- **Real and consequential.** `analysis/r9_speed_surface.py` (d17) and
  `hf_space/speed_surface.py` + `ingest_speed_surface.py` (d18) both reduce the same 348
  records. The duplication is what produced C-1, so it earned its cost. It should not
  persist as two reducers with two window conventions.
- **Real and unresolved.** `analysis/cycles_render.py` and `prep_cycles_scene.py` (path
  tracer, never run) against `analysis/render_multigeom_shaded.py` (matplotlib, working).
  Two renderers, one exercised.
- **Not duplication.** `kramer_extract_numerical.py` reads the archive;
  `kramer_benchmark.py` reduces series. Different jobs, same slot.

## Files edited on two branches at once

`.claude/skills/research-corpus/SKILL.md` was modified by six commits on **two** branches,
five by d14 and one by the coordinator (`faf53d1`). d14 reconciled in `5680a20` by a
3-way merge with 3 conflicts, keeping the superset. That worked, and see C-17 for why it
still reached nobody.

---

# 5. What no session is doing, and should be

Ordered by cost-to-value. Each is specific enough to dispatch.

**5.1. Nobody owns C-1.** d18 measured that d17's headline pair inverts and said "it is not
mine to close". d17 has committed twice since (`498f1ad`, `c94f3f8`) without addressing it.
**Dispatch to d17-moving:** state which window the load ratio belongs to under d15's rule,
and either re-state the pair with its window or withdraw it. The general S result is not in
question. One confound to close first: `hull_y_m` empty in `c3full`.

**5.2. Nobody has committed the subagent failure.** The exact string
`deepseek-ai/DeepSeek-V4-Flash:deepinfra`, and that an explicit `model` override does not
reach it, exists in three transcripts and no file. **Dispatch:** one line into the register
or CLAUDE.md, with the two-attempt evidence, so the next wave does not rediscover it nine
times.

**5.3. Nobody is fixing skill propagation, and the preflight cannot see it.** C-17.
**Dispatch:** add a skills-drift check to `scripts/r8/r8_preflight.sh` beside the existing
CLAUDE.md check, and land the corrected SKILL.md onto `add-ci-checks` so the eight starved
worktrees inherit it at their next branch. **Corrected after reading `e7a0db3`:** this is
**not** a fast-forward. d16 measured SKILL.md as a genuine merge conflict in which
**neither side is a superset**, with all 75 of `add-ci-checks`' added lines absent from
r9-corpus-bib. It needs a union merge, which is what d16's plan already specifies.

**5.4. Three register rows are stale and the register is the corrections authority.** C-3.
**Dispatch to the coordinator:** strike A2 or annotate it with the retraction that already
happened verbally, close B1, and re-scope B7 to "fixed on r9-settle, still stale on the
landing target".

**5.5. `[Bha19]` is one read away and I have done it, but d19 has not seen it.** d19 flagged
IBAMR family D as "the cheapest remaining addition". The answer is in section 2c above:
IBAMR spans families B and C, Eq. 30 and Eq. 40. **Dispatch to d19-priorcode:** fold it in,
which strengthens the corrected headline rather than weakening it.

**5.6. Twelve deep searches are invisible and one of them answers Job B's question
directly.** C-12(d). **Dispatch to d11-accessor and d14-corpusbib jointly:** d11 should
read the Aug 18 buoyancy search before the next criterion-3 revision; d14 has already built
the interchange reader in `5680a20` and needs only the exporter.

**5.7. Two CLAUDE.md integers are now wrong.** "Four prior vehicle fording or wading
simulations" is at least eight or nine (C-12b), and "332 distinct external papers" is 319
(C-11). Neither is in anyone's declared write scope tonight. **Dispatch:** whoever owns
CLAUDE.md next.

**5.8. Nobody has run the Cycles path.** Two files, 621 lines, committed by a recovery
commit that says nobody has executed them, still uncommitted-modified in the worktree.
**Dispatch to d13-renders:** run them or mark them experimental in the file header, so the
next reader does not treat committed as exercised.

**5.10. The banner is lying to every session and two sessions have acted on it.**
C-18(a). `.claude/hooks/orient_live.sh` prints "CI NOT LIVE ... it runs nowhere" and the CI
has run seven times, green, over a check exiting 1. **Dispatch to whoever owns the hook:**
change the string to the true claim (absent from `origin/main`, but running on push from
`add-ci-checks`, and masked by `continue-on-error`), and tell d18-platform that the message
it measured eleven worktrees to be missing is one they are better off missing until it is
fixed.

**5.11. The `hf_space/` landing would silently un-fix a public page.** C-18(c).
r9-platform's `app.py` contains no `AR_R`, no `l1_verdict`, no `l0_depth_threshold`, so
taking it wholesale removes PR #11's L1 joint-rule fix from a page that is already public.
d16 flagged this as a decision and did not resolve it. **Dispatch:** it needs a human call
before any landing, and it is the only item here with an already-published consequence.

**5.9. The one thing I would add that nobody has proposed.** Every instrument failure this
round has one signature: **a code path that returns a value indistinguishable from a
measurement when it could not measure.** The round found eight.

| # | instrument | how it failed toward looking correct | found by |
|---|---|---|---|
| 1 | `stationarity.py` | `n < 10` returned 0.0, and 0.0 is the pass value | d15, own |
| 2 | `grep -c ... \|\| echo 0` | "0\n0" is not an integer, comparison errored, fell to else | d18, own |
| 3 | `all([])` / `not []` | verdict True over zero data | d12, own |
| 4 | add/add control | both arms returned 1 because the branch did not exist | d16, own |
| 5 | `--query` | matched title and abstract, never authors, so 0 was unreachable-not-absent | d14, own |
| 6 | `r8_preflight.sh` | checks CLAUDE.md drift, silently ignores the authority skill | **me, C-17** |
| 7 | `gh run view --json jobs` | `conclusion: success` on a step that exited 1 | d16, own |
| 8 | mesh acceptance checks | watertight, manifold, right bbox, 10x triangles, all on a one-blob-per-particle mesh | d13, own |

Six of eight were caught by their own authors, one by me, one by a sibling, **all after
publication**. `analysis/r9_session_reader.py --self-test` demonstrates the cheap form of
the fix: assert that each guard **fires**, and assert a known limitation explicitly (guard
5 asserts that dotted version strings *are* mis-mined) so a later "fix" cannot silently
remove the caveat. **Dispatch:** make "name the input that makes this check fail" a
required line in every commit that adds a check, rather than a lesson each slot relearns
independently.

---

## Falsifiers for my own claims

- **C-11** dies if any working tree contains one or three copies of `make_phase_space.py`,
  or if a third content hash exists. Command:
  `find /Users/josie/can-it-ford -name make_phase_space.py -not -path '*/.git/*' | xargs md5 -q | sort | uniq -c`
- **C-10** dies if `r8_session_ids.tsv` gains the pre-crash ids, or if the pre-crash files
  are shown to be replayed inside the post-crash ones. They are not: first timestamps differ
  by 17 hours.
- **C-17** dies if a session on a 152-line skill can be shown to have read the 523-line one
  by another route. The d17 `--query` quote at 00:43, 22 minutes after the 00:21 fix, is
  the positive evidence that it did not.
- **C-12(a)** dies if `[Sha18c]` resolves to a different DOI than `shah2018`. It does not:
  `10.1051/MATECCONF/201820307003`, confirmed by `get_paper_info`.

## What I could not verify

- Every physics number here is its session's measurement. I re-derived none of the forces,
  ratios or verdict counts; I verified their *provenance and collisions*, which is a
  different thing.
- No adversarial review, per C-2.
- `c94f3f8`, `e7a0db3` and `3d01611` landed between 18:40 and 18:43 and **were read in
  full** after the first draft of this file; see C-18, C-19 and C-20. Anything committed
  after 18:44 is not in this document.

## Note on the three non-git hex tokens in this file

`3627269` is an upstream revision of `github.com/ChenguangZhang/sdfibm`, not an object in
this repo. `a3b48fa8` and `a94b9915` are md5 prefixes of two file contents, not commits.
The other 48 hex tokens here are commits in this clone and all 48 resolve, checked with
`git cat-file -e` before this file was committed. Recorded because
`register_integrity.py` flags unresolved hex as a possible fabrication, and it is right to.
