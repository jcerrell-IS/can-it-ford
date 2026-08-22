# Status of seven ranked open items, 2026-08-22

Worked 2026-08-22 14:29 to 14:41 BST from `Josephines-MacBook-Air.local`,
`/Users/josie/can-it-ford`, branch `claude/add-ci-checks`, HEAD `5bb00cd`, main
checkout.

Claims are tagged `[READ]` where I ran the command and read the output this
session, `[RECALLED]` where a document or memory is the source and I did not
re-derive it, and `[INFERRED]` where I reasoned from those reads.

**Result: 6 DONE, 1 OPEN. Five of the seven were already closed before this
session started.** One item (6) needed real work and got it. One item (7) is
genuinely open and the answer is a negative.

**No SU were spent. No simulation was run. Nothing was merged or pushed.**

---

## Premise correction, stated first because it affects how the list should be read

**There is no "CLAUDE.md v9 Part 5".** `[READ]` A live grep of
`/Users/josie/can-it-ford/CLAUDE.md` (1,005 lines) for `^# Part`, `^## Part`,
`^### Part`, `Part 5`, `v9` and `VERSION 9` returns **zero matches**.

This is not new. CLAUDE.md's own "AUGUST 8 2026 LITERATURE ADDENDUM" section
records the identical problem: a dispatch asked for addenda under "Part 2.4" and
"Part 4.3", and *"neither exists: this file has no numbered Part headers at
all, verified by a full live read on 2026-08-08."* `[READ]`

The seven items are still real and I worked all seven on their merits. But the
citation cannot be resolved, so **each item below names the document that
actually governs it** rather than inheriting authority from a section that does
not exist. Two of the seven carry factual errors in their framing, flagged in
place: see items 4 and 7.

---

## Verdict summary

| # | Item | Verdict | Closed by |
|---|---|---|---|
| 1 | g96_m2337 at g128 | **DONE** | already run, 3 independent stores |
| 2 | `failure_modes.py` gravity fork | **DONE** | `e495b56`, 2026-08-12; re-verified today |
| 3 | C2 crash root cause | **DONE** | `C1_ROOT_CAUSE_2026-08-07.md` 8b; mechanism verified live today |
| 4 | Date `solidify_watertight` / `is_gaussian_ply` | **DONE** | `387404b` 2026-07-30 and `00b735c` 2026-08-12 |
| 5 | `stop_signal_and_check.sh` | **DONE** | `578cdad`, 2026-08-12 |
| 6 | `check_claims.py` C5/C8 false positives | **DONE** | fixed and tested this session |
| 7 | Poster and paper submission status | **OPEN** | nothing confirms either submission |

---

## 1. g96_m2337 at g128: DONE

**Do not run this. It has already been run three separate times, and re-running
it would spend SU to reproduce a stored result.**

### SU check, done first as instructed

`scripts/tacc.sh --status`, live `[READ]`:

| Field | Value |
|---|---|
| Project | `BCS20003` |
| Avail SUs | **579** |
| Expires | 2026-09-30 |

The brief said 581; live is 579. Also read, and worth knowing separately:
**Vista `/home1` is at 90.78 percent of quota** and the status banner prints a
filesystem-quota warning `[READ]`.

**Affordability, for the record even though the run is unnecessary.** Prior g128
jobs on Vista partition `gh`, from `sacct` `[READ]`: `r6rep_g128` 00:03:24,
`r7pin_g128` 00:04:09. At the `gh` rate of 1.0 SU per node-hour and the 0.25 h
minimum billing floor `[RECALLED]`, one such run bills **0.25 SU** against 579
available. Cost was never the blocker. Redundancy is.

### The run already exists, three times over

`[READ]` from the filesystem:

| Store | Contents | Tracked in git |
|---|---|---|
| `data/g128_canonical_2026-08-13/canon_g128_m2337` | register item 44's run, with an in-job g96 control | 0 files |
| `data/g128_canonical_repeat/canon_g128_m2337` | the determinism repeat | 0 files |
| `data/g128_2026-08-18/g128_m2337_{metrics.csv,summary.json}` | a 2026-08-18 re-run | 6 files tracked |
| `data/g128_sweeps_2026-08-18/` | 3 `sweepD` + 5 `sweepV`, all at g128 | 16 files tracked |

`data/g128_canonical_2026-08-13/00_provenance.txt` states the purpose in its own
words `[READ]`:

> `purpose: register J15 direct test, canonical Yaris set at g128 with an in-job g96 control`
> `expected g96 anchor: g96_m2337 ratio_slide 1.80047 frozen / 1.74225 live re-classified (register J16)`

It ran 2026-08-13T10:57:44-05:00 on `c301-001.ls6.tacc.utexas.edu`, **LS6, not
Vista**, all six arms `RC=0`, ending `ALLDONE` at 11:03:57. Six minutes of wall
time for the whole set.

### The 2026-08-18 g128 m2337 result

From `g128_m2337_summary.json` `[READ]`: `n_grid` 128, `dx` 0.0736074,
`water_layers` 8, `n_water` 450,912, `n_vehicle` 71,155, `realized_rho`
658.839, `final_disp_mag_m` **0.068154**, `determinism_identical` **true**,
`C3_oob_particle_frames` **0**, `fill_ratio` 1.00124.

### The stronger point: the gap J15/J16 turned on is also closed

Register D9's ranked open list, item (3), reads *"J15's item, the canonical set
at g128, remains the highest-value single run"*, and the register's own follow-up
note says the safe unambiguous form of the gap is that *"the 3 `sweepD` and 5
`sweepV`, including the only STUCK run, have no g128 data at any mass, which is
the strongest form and is what the open item turns on"* `[READ]`.

**`data/g128_sweeps_2026-08-18/` contains exactly those eight runs at g128**
`[READ]`: `sweepD_g128_d0p25/d0p35/d0p45` and
`sweepV_g128_v0p5/v1p0/v2p0/v2p5/v3p0`, each with a metrics CSV and a summary
JSON, 16 files, all tracked. So the canonical 17 now have g128 companions across
3 masses + 3 depths + 5 velocities = 11 g128 runs `[INFERRED from the file
inventory]`.

**Register D9 item (3) should be marked discharged.** I did not edit the register;
that is the register owner's call and CLAUDE.md forbids this session touching it
casually.

**STATUS: DONE.** The run exists. Do not spend the 0.25 SU.

---

## 2. `failure_modes.py` gravity fork: DONE

**The value was already 9.81 before this session. I regenerated anyway, because
the item asked for a byte-comparison, and the artifacts came back byte-identical.**

### The constant, live

`simulation/failure_modes.py:14-16` `[READ]`:

```
G = 9.81  # unified 2026-08-12 with the solver and the five 9.81 post-processing
          # sites (register A6). Was 9.80665, a 0.0342 percent fork that fed the
          # published 16 SLIDE / 1 STUCK verdicts via :170 and :174.
```

So there was nothing to change. This matches CLAUDE.md item 15, which records the
fork as CLOSED by `e495b56` on 2026-08-12 `[READ]`.

### The regeneration and byte-comparison, run today

Backed both artifacts up to the scratchpad, ran
`analysis/classify_failure_modes.py` under
`/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3` (numpy
2.5.1, pandas 3.0.5), then compared `[READ]`:

| Artifact | md5 before | md5 after | `cmp` |
|---|---|---|---|
| `data/failure_modes_by_run_classified.csv` | `09d5d7bc42689c89885856aa3f1f4da8` | `09d5d7bc42689c89885856aa3f1f4da8` | **BYTE-IDENTICAL** |
| `data/failure_modes_by_run.json` | `3de1be9c9e47a8cea52872fbc1964de3` | `3de1be9c9e47a8cea52872fbc1964de3` | **BYTE-IDENTICAL** |

`git status --porcelain` on both paths is **empty** after the run, so git also
sees no change `[READ]`. The script printed its own independent check,
`JSON runs payload matches committed copy: True`.

**The classifier's own summary line: `17 runs: 16 SLIDE, 1 STUCK`** `[READ]`,
reproducing the published result exactly.

Quoting CLAUDE.md's own requirement, the count is threshold-dependent and the
thresholds belong beside it: `slide_m` 0.05 m, `slide_speed_ms` 0.05 m/s,
`float_m` 0.05 m, `sustain_frames` 3 `[READ from the classifier docstring]`.

### One discrepancy found while doing this, and it is worth recording

**CLAUDE.md item 12 trap (a) says filtering on `ratio >= 1` "reports 13 topples
that never happened". The live count is 12, not 13.** `[READ]`

Counted directly from the 17 `ratio_topple` values in the regenerated CSV: twelve
are `>= 1`, and `triggered_topple` is `False` on all seventeen.

**The likely origin of the 13 is a rounding artifact** `[INFERRED]`. The third
run, `g48_m2337`, carries `ratio_topple` **0.999903**, which is 1 part in 10,000
below the threshold and displays as `1.000` at three decimal places. Anyone who
counted from a 3 dp rendering would get 13.

The substance of trap (a) is untouched: `triggered_*` and `ratio_*` disagree, and
filtering on the ratio manufactures topples that never happened. Only the count
is off by one. **Recommended: change 13 to 12 in CLAUDE.md item 12 and name
`g48_m2337` at 0.999903 as the reason the number is fragile.** I did not edit
CLAUDE.md: it is currently modified in the working tree by another session, and
the standing rule forbids touching another session's live file.

**STATUS: DONE.** No change was needed, and the byte-comparison the item asked
for was run and passed.

---

## 3. C2 crash root cause: DONE, and the answer is the rigid body

**It is the BOX, in z. Not water hitting a domain wall.** The question this item
poses was answered on 2026-08-07 and I verified the governing mechanism live
today.

### First, the three different things called "C2", so nothing is conflated

The item is right that there is more than one. There are at least three `[READ]`:

| Label | Where | What it is |
|---|---|---|
| Register **C2** | `CANONICAL_CORRECTIONS_REGISTER:180`, Section C | the **Genesis** `grid_density` crash boundary: gd 80 and 88 pass 3/3, gd 90+ fails |
| Ladder **C2** | `C1_ROOT_CAUSE_2026-08-07.md` section 8b | the **warpmpm** free-rigid-path P2G edge-guard trip. **This is the item's C2** |
| The buoyancy validation | CLAUDE.md A-2, the `c1sdf` arms | the SDF-collider buoyancy check, 7.3 to 7.7 percent |

Register Section C carries its own heading warning: *"Genesis-specific, T1. These
do NOT apply to warpmpm"*, and the register elsewhere states plainly *"Do not
cite C2 as support"* across that boundary `[READ]`. So the register's C2 is a
different crash in a different engine and is not this item.

### The answer

`docs/C1_ROOT_CAUSE_2026-08-07.md` section 8b, heading and body `[READ]`:

> **What trips the guard is the BOX, in z, not water in x.**

Three independent legs, all in that section `[READ]`:

1. **Water is clamped and cannot reach those coordinates.** `project_water()`
   clamps water to `>= wall - 0.25dx = 0.5521` in x and y and
   `>= floor - 0.25dx = 0.4048` in z, and `settle_pinned` calls it before every
   step, so the clamp is live during settle too. The observed minima, **0.2205 at
   g64 and 0.1464 at g96**, are below all three bounds, so they cannot be water
   on any axis.
2. **The signature is a body crossing, not a leak.** The trip sits just barely
   under `1.5*dx` at both resolutions, 0.220822 and 0.147215.
3. **There is a mechanism, and I verified it live today rather than taking the
   document's word.** The body passes through the floor by design because every
   plane is `restitution=0.0`. Read live at
   `third_party/mpm-engine-544c93dd-solver-core/kernels/mpm_solver_warp.py:1915`
   `[READ]`: the line is `if restitution != 0.0:` and only inside that branch is
   the plane appended to `self.rigid_surface_colliders`. **A plane at restitution
   0.0 is therefore never registered as a rigid-surface collider, so it is
   invisible to the rigid body.**

**The water hypothesis was actively considered and is formally withdrawn.**
Section 8b states that an earlier revision *"attributed the trip to water leaking
laterally past the wall planes (J.1 finding 3's rind). That was wrong and is
withdrawn."* `[READ]` The mechanism was first established in commit `20dd999`'s
body nine hours earlier.

### Read section 8b with its two retractions

Section 8b opens with a banner: **"THIS SECTION CONTAINS TWO RETRACTIONS. READ
8b-CORRECTION BELOW BEFORE CITING ANYTHING FROM IT."** `[READ]` Withdrawn are:
"C2 is UNRUNNABLE on the free-rigid path" (it reached frame ~195 of a 200-frame
budget), the free-fall arithmetic and 216 m descent budget, the claimed 54-frame
heave period with its Ca=0 match, and the later "leans toward Ca=0.5".

**The root-cause finding above is not one of the retracted parts.** It is what
8b-CORRECTION leaves standing, alongside one further positive result: the box does
not descend monotonically, and shows genuine reversals of 0.144, 0.170, 0.249 and
0.065 m against a noise floor of 7.4e-05 m, so **something pushes back
intermittently** `[READ]`.

### What is actually still open, and it is not the root cause

**(a) The fix does not work.** `20dd999` deepened C2 to 18 cells;
`scripts/c2only.sbatch:19-20` passes `--depth-cells 18` explicitly; that is job
`894676`, and **all four of its C2 arms crashed at the same guard anyway**
`[READ]`.

**(b) The diagnostic that would make any recurrence legible was specified on
2026-08-07 and has never been implemented.** Verified live today in the pinned
engine at `third_party/mpm-engine-544c93dd-solver-core/core/solver.py`, the guard
around line 506 `[READ]`:

```python
g = x[:, 1:] if self.periodic_x else x
if g.min() < 1.5 * dx or g.max() > lim - 2.5 * dx:
    raise RuntimeError(
        f"particles within 2 cells of the grid edge (x in "
        f"[{g.min():.4f}, {g.max():.4f}] m, domain [0, {lim}] m, dx={dx:.4f}): "
        ...
```

Three defects in that message, all live:

1. `g.min()` and `g.max()` are global across the guarded axes, so **the message
   never says which axis tripped**.
2. It **never says which particle**, or its material, which is precisely why
   "water, hull, or rotated corner" had to be inferred indirectly.
3. When `periodic_x` is true, `g = x[:, 1:]`, so the guarded columns are **y and
   z**, and the message still labels them **"x"**. That is actively misleading,
   not merely unhelpful.

`REGIME_LADDER_DISPATCH_2026-08-07.md` section 4 "Fix B" specifies the remedy:
print `x.min(0)` per axis and the material of the argmin particle before the
raise `[READ]`.

**I did not implement it, and the reason is a decision for Josie.** That file is
a **pinned, vendored third-party engine** (`544c93dd`), which this project pins
deliberately for reproducibility, and the change cannot be validated without a
GPU run. Patching a pinned dependency is not something to do unasked.

**STATUS: DONE** for the question posed. The root cause is the rigid body drifting
in z through a floor plane it cannot see, not water reaching a domain wall.
**Successor item, OPEN and now precisely specified:** implement Fix B in the
pinned solver's P2G guard message, which needs a decision on patching a vendored
pin.

---

## 4. Dating `solidify_watertight` and `is_gaussian_ply`: DONE

**Confirmed as the item asked, before claiming it: both files are git-tracked.**

### The confirmation the item required

`git ls-files` `[READ]` returns both:

```
renders/yaris_render_s1/sim_standing.py
renders/yaris_render_s1/vehicle_live.py
```

And the **tracked blob at HEAD**, not just the working file, carries both
functions `[READ]`: `git show HEAD:renders/yaris_render_s1/vehicle_live.py`
contains `def solidify_watertight` at line **88** and `def is_gaussian_ply` at
line **184**. `git diff HEAD` on both paths is **empty**, so the working file and
the committed blob are identical `[READ]`.

So the blocker is resolved and the contribution is datable.

### The dates

Two are defensible, and they differ by 13 days. **State which you mean.**

| Date | Commit | Path | What it establishes |
|---|---|---|---|
| **2026-07-30** 18:51:37 -0500 | `387404b` | `analysis/render_v1/as_ran_local_copies/vehicle_live.py` | **earliest git-provable existence.** I confirmed `def solidify_watertight` is present in that blob at that commit `[READ]` |
| **2026-08-12** 21:09:43 +0200 | `00b735c` | `renders/yaris_render_s1/vehicle_live.py` | the date it entered version control **on the canonical path** |

`is_gaussian_ply` has a third, earlier date, but for a **different
implementation**: `bridge/gaussian_io.py:81` was committed by `837c554` on
**2026-08-06**, and its signature is `path: str` where the canonical one is
`path: Path` `[READ]`. Do not merge these into one date.

**For the paper, 2026-07-30 is the honest earliest date** and it is what a
reviewer could verify from the public history `[INFERRED]`. Neither date is the
date the code was written; git can only date entry into version control, and the
"as ran" copy proves the code predates its canonical tracking.

### A correction to this item's own framing

The item says the restructure left **"24 source files tracked, 501 artifacts
excluded"**. **Both halves are wrong, and the first is the exact conflation
CLAUDE.md warns about in bold.**

Measured live `[READ]`, using `git check-ignore` per file:

| Quantity | Value |
|---|---|
| Top-level `.py` under `renders/yaris_render_s1/` on disk | **24** |
| Of those, ignored | **0** |
| Of those, **un-ignored** (visible to git and to this shell's grep) | **24** |
| Of those, **TRACKED** | **2** |
| Total files under `renders/yaris_render_s1/` | **905** |
| Ignored entries reported by git (directories collapse, so this is not a file count) | 68 |

CLAUDE.md says it directly: *"DO NOT READ 'un-ignored' AS 'tracked'. Corrected
2026-08-12 after an independent check caught this exact conflation here: only 2 of
the 24 are tracked."* `[READ]` The carve-out is the walk-down idiom at
`.gitignore` lines 32-34.

**And "501" appears nowhere in CLAUDE.md.** `[READ]` A grep returns only
substrings inside unrelated numbers (`1501.5`, `7.280446501465449`). The figure
has no source in the document the item cites.

**STATUS: DONE.** Both drivers tracked, contribution datable, earliest provable
date 2026-07-30.

---

## 5. `stop_signal_and_check.sh`: DONE

**The file does not exist. It was removed ten days ago, and the removal did
exactly what this item asks for.**

`[READ]`:

- `find` over the repo and `~/.claude` (bounded, maxdepth 4): **no file named
  `stop_signal*` anywhere**.
- No hook references it. Grep of `.claude/settings.json`,
  `.claude/settings.local.json` and `~/.claude/settings.json` for `stop_signal`:
  **zero matches**.
- `git log --all -- '*stop_signal*'` returns the removal commit: **`578cdad`,
  2026-08-12 23:25:34 +0200, "hooks: remove unwired stop_signal_and_check.sh; add
  multigeom rollout renderer; update multigeom validation doc; sync .mcp.json"**.
- `.claude/hooks/` at HEAD holds **14 files** and none is this one.

The item offered two acceptable outcomes, wire it or remove it. **It was
removed**, which is the outcome the 2026-08-12 audit
(`REMEDIATION_PLAN_AUDIT_2026-08-12.md:221`, *"exists in `.claude/hooks/` but is
wired to no event"*) prescribed `[READ]`.

The three documents that still mention it are historical records of the problem,
not live references. One of them,
`RECONCILIATION_AND_DISPATCH_2026-08-14.md:1079`, already notes the hooks
directory has 14 files and that the script is absent, which agrees with today's
measurement from a separate origin `[READ]`.

**STATUS: DONE.** Nothing to wire, nothing to remove.

---

## 6. `check_claims.py` C5/C8 false positives: DONE, fixed this session

**This is the one item that needed work. It got a fix, and the fix is tested in
both directions.**

I read `docs/CONCURRENT_SESSION_NOTICE_2026-08-07.md` first, as CLAUDE.md
requires before touching this file, and confirmed `scripts/check_claims.py` was
clean in the working tree and last committed 2026-08-18 by `cb13f88`, so it was
not another session's live edit `[READ]`.

### The defect, reproduced

Running `check_claims.py --all` before the fix `[READ]`: **224 ERROR, 202 WARN**,
of which **C5 = 5 ERROR** and **C8 = 40 ERROR**.

**All 5 C5 hits were false positives**, read one by one `[READ]`. Examples: the
banned-phrase guard's own rule text *"the 17 runs use warpmpm, not Genesis MPM"*;
`hf_space/README.md:72`, *"**\"Genesis MPM\"** as the physics engine. The gated
runs are warpmpm. Corrected above."*; and
`MANUAL_SETUP_STEPS_2026-08-07.md:163`, *"Never label the gated runs Genesis"*.
Every one is the correction being stated, and one is a legitimate reference to
Genesis as the Track 2 path.

**The overwhelming majority of the 40 C8 hits were the same class** `[READ]`:
*"has NO peer-reviewed source"*, *"not a cited physical threshold"*, *"No direct
peer-reviewed citation was found"*, *"FALSE attribution"*, and verbatim quotations
of CLAUDE.md item 13 and register D7.

**The structural cause is exact, and the file already documents it.** C8's
`context` list is `peer[- ]review|\bcited\b|literature|standard|established|
sourced`. **That is the same vocabulary the correction is written in**, so a line
asserting the fix matches the context and fires. The `Rule` dataclass's own
comment says this in so many words `[READ]`:

> If set, a line matching this is NEVER a hit. For rules whose context word is
> the same word the CORRECTION uses [...] would otherwise be flagged as the very
> claim it retracts. Negation is the common case in this repo, so suppress it here
> rather than making every author read past a false ERROR.

**The mechanism was built for exactly this and C5 and C8 simply never got one.**
Three other rules already use `exclude=` (lines 230, 251, 291), so this fix is the
house pattern, not a new one. The `Rule.exclude` field was added by the
2026-08-07 session whose notice CLAUDE.md points at.

### The fix

Added an `exclude=` pattern to **C5** and **C8**, each with a comment recording the
measurement that justifies it. Every alternative in both patterns is drawn from an
observed false-positive line, not invented.

- **C5** excludes lines carrying `warpmpm`, `never`, `not genesis`, `mislabel`,
  `corrected`, `track 2`, `box-proxy`.
- **C8** excludes negation and retraction forms (`no peer-reviewed`, `no direct`,
  `not a cited`, `not a <word>-cited`, `uncited`, `unsourced`, `never`, `false
  attribution`, `corrected`, `refuted`, `withdrawn`, `do not cite/present/give`,
  `must not`), plus the two framings the correction always uses,
  `onset-of-motion` and `internal detector`.

### The result, measured both ways

| Rule | ERROR before | ERROR after |
|---|---|---|
| C5 | 5 | **0** |
| C8 | 40 | **2** |
| **Total (all tracked files)** | **224** | **182** |

**Regression test, which is the half that matters** `[READ]`. I wrote four
synthetic lines committing the actual violations and ran the checker over them:

```
The 17 gated runs were produced with Genesis MPM at grid density 64.
DRIFT_THRESHOLD is the established peer-reviewed standard from the flood literature.
Our gated runs use Genesis, and sim_standing.py drives it.
The 0.05 m drift_threshold is a cited literature value.
```

Result: **4 ERROR, 0 WARN**, two C5 and two C8. **The rules still catch what they
exist to catch.** A guard that stops firing is worse than one that over-fires, so
this test is the acceptance criterion, not the hit-count reduction.

The 2 surviving C8 hits are not correction language and are left deliberately:
one is a research question in `provenance-audit/SKILL.md:175`, the other states
where the literal is set in code. Both deserve the human read the script's own
footer asks for.

**File changed: `scripts/check_claims.py` only. Uncommitted, staged as an explicit
path with this document.**

**STATUS: DONE.**

---

## 7. Poster and final-paper submission status: OPEN

**I read the documents' content as instructed. The answer is a negative, and it
is the same for both: no document in this repository confirms that either the
poster or the paper was ever actually submitted to anyone.**

What the documents confirm is **artifact readiness**, which is a different claim.

### The poster

`docs/POSTER_COMPLIANCE_2026-07-27.md`, checked live 2026-07-25 against
`Instructions.docx.md`, audits 21 requirements `[READ]`. Content requirements 8
through 20 all **PASS**. The four that do not:

| # | Requirement | Verdict, verbatim |
|---|---|---|
| 1, 2 | poster dimensions | **"AMBIGUOUS, resolve before Monday"** |
| 6 | *"in the Final Posters folder no later than Monday, July 27 at 9am CST"* | **"Not verifiable from this machine" -> "OPEN, presenter action"** |
| 7 | *"Sign up for a mock poster presentation time"* | **"Not verifiable from this machine" -> "OPEN, presenter action"** |
| 21 | logos from the poster-resources folder | **"NOT MET, needs the resources folder"** |

**Requirement 6 is the submission itself, and it is recorded as unverified and
outstanding.** `[READ]`

The dimension ambiguity was never recorded as resolved: the poster is 56 x 42
landscape, the instruction says preferred 42x56 and maximum 42" x 60", and the
document sets out two defensible readings that disagree on whether it complies. Its
recommended action was *"Send one message to Rosalia Gomez or the TACC Education
and Outreach team [...] before Monday 09:00"* `[READ]`. **No document records that
message being sent or answered.**

The artifact itself exists: `figures/Cerrell_TACC_42x56.pdf`, 404,092 bytes, mtime
2026-07-25 23:13 `[READ]`. The repo-root copy the audit also names is **gone**
`[READ]`.

### The paper

`docs/SUBMISSION_MANIFEST_2026-07-31.md` is a **reproducibility record**, and a
careful one. Read in full `[READ]`, it documents:

- Overleaf commit `32b0d123c3f3ce53aa9594d995a7a86aac930cca`, timestamped
  2026-07-30T19:46:19-05:00, with tex and bib md5s.
- A clean rebuild: 7 pages, 0 LaTeX errors, 0 undefined citations or references,
  14 bibitems, braces balanced 241/241, 15 labels against 12 refs, zero dangling.
- Zero `FLAG` and zero `PLACEHOLDER` renders in the compiled PDF.
- Seven figures with md5s, true formats and generators, of which **two carry
  provenance gaps**: figure 4 `force_balance.jpg` is `PROVENANCE_MISSING` and
  figure 7 is `PROVENANCE_PARTIAL`.

Its nine section headings are: Submitted commit, FLAG render count, Figures,
Citations, Reported numbers, Fig. 4 arithmetic, Known limitations, Self-corrections,
Stale artifacts `[READ]`.

**There is no venue, no submission portal, no submission date, no confirmation or
receipt, and no acceptance anywhere in it.** A grep for `submitted to`, `submission
portal`, `venue`, `conference`, `deadline`, `received`, `confirmation`, `EasyChair`
and `acceptance` returns only incidental matches inside filenames and a
bibliography-checking sentence `[READ]`. "Submitted commit" names the commit that
was final, not an act of submission.

### Affirmative evidence against "final and submitted"

**The paper has been substantively revised 21 days past its target date.** The
Overleaf remote tip is `3053956`, **2026-08-20 01:48:02**, subject *"Correct four
sourced defects, and stop resting a conclusion on the unconverged quantity"*
`[READ]`. A paper that was finally submitted on 2026-07-31 would not be receiving
sourced-defect corrections three weeks later `[INFERRED]`.

### What this item actually needs

**Nothing in this repository can close it.** Both remaining questions are facts
about the outside world that only Josie holds:

1. Was `Cerrell_TACC_42x56.pdf` uploaded to the Final Posters folder before
   2026-07-27 09:00 CST, and was the mock presentation slot booked?
2. Was the paper submitted anywhere, and if so, to what venue, on what date, and
   with what outcome?

**STATUS: OPEN.** Blocker: both answers are outside the repository. The
documents were read as instructed and they record artifact readiness, not
submission. **Recommend one line from Josie on each, recorded in a tracked file so
the next session does not have to re-read these documents to rediscover that they
do not say it.**

---

## What changed on disk this session

| Path | Change |
|---|---|
| `scripts/check_claims.py` | `exclude=` added to rules C5 and C8, with justifying comments. Item 6. |
| `docs/CLAUDE_MD_OPEN_ITEMS_STATUS_2026-08-22.md` | this file |

`data/failure_modes_by_run_classified.csv` and `data/failure_modes_by_run.json`
were **regenerated and came back byte-identical**, so they are unchanged on disk
and unchanged in git `[READ]`.

**Nothing else was touched.** No merge, no push, no branch, no delete, no SU spent,
no simulation run. CLAUDE.md and the register were deliberately not edited: both
are in another session's working set, and item 2 and item 1 each produced a
recommended edit to them that is written out above for their owner to apply.

## Limits of this pass

- **NOT ADVERSARIALLY REVIEWED.** No subagent was spawned. Every measurement is
  single-session, and each names the command that produced it so it is cheaply
  refutable.
- **Item 3's 0.2205 and 0.1464 minima are `[READ]` from
  `C1_ROOT_CAUSE_2026-08-07.md`, not re-derived from a trace.** What I verified
  independently is the mechanism: the `restitution != 0.0` gate at
  `mpm_solver_warp.py:1915` and the hardcoded `"x"` label in the P2G guard.
- **Item 1's g128 stores were inventoried and one summary was read. I did not
  re-classify those runs or check them against gates.** The claim is that the run
  exists and completed, not that its verdict has been adjudicated.
- **The working tree is shared.** Nine tracked files were modified by other
  sessions during this pass. Every filesystem statement is timestamped 14:29 to
  14:41 BST.

*Written 2026-08-22. Six of seven items were already closed; the list was stale,
not the work.*
