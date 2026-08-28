# HANDOFF, CAN IT FORD, ROUND 6
Paste this whole file as the first message of a fresh Claude Code session in
`/Users/josie/can-it-ford`. It assumes you have read nothing. Every number below
was read live from a commit body, a file, or a command output during Round 5.

---

## 0. WHAT YOU ARE INHERITING

Round 5 ran four dispatch sessions in tmux `canford5` for roughly ten hours.
**Roughly 167 commits as of 2026-08-18 00:25 BST, four clean worktrees, zero
work lost.** Nothing is pushed.

**DO NOT TRUST THAT NUMBER, DERIVE IT.** The sessions were still committing
while this file was being written and the count drifted by four in the minutes
it took. That is this handoff's own section 1 biting its author, and it is why
no count below is hardcoded where a command will do:

```bash
for w in r5-research r5-exposure r5-safekeeping r5-physics; do
  printf "%-16s %s\n" "$w" "$(git -C /Users/josie/can-it-ford/.claude/worktrees/$w rev-list --count 777567a..HEAD)"
done
```

| branch | entry point, READ THIS FIRST |
|---|---|
| `claude/r5-research` | `docs/R5_RESEARCH_INDEX_AND_ERRATA_2026-08-16.md` and `WHAT_SURVIVES_2026-08-17.md` |
| `claude/r5-exposure` | `docs/E8_ACTION_INDEX_2026-08-17.md` |
| `claude/r5-safekeeping` | `docs/PUSH_LEDGER_START_HERE.md` |
| `claude/r5-physics` | `docs/R5_PHYSICS_START_HERE.md` and `WHAT_SURVIVES.md` |

Main tree was on `claude/add-ci-checks` at `ffc05d9` with 30 dirty entries at
handoff time; re-check with `git -C /Users/josie/can-it-ford status -sb`.

**READ THE ENTRY POINTS BEFORE ANY BRANCH LOG.** Each separates what survived
from what was withdrawn. The withdrawal rate is high BY DESIGN (five adversarial
review passes on physics alone), so a commit body from early in the round is
frequently superseded by a later one on the same branch.

**D1 audited its own entry point and found 3 of 12 "safe to cite" rows FALSE.**
The other three entry points have NOT had that adversarial pass. Do not trust
them at face value; re-derive anything load-bearing.

---

## 1. THE ONE RULE THAT EXPLAINS THIS WHOLE ROUND

**A check must measure the thing that would hurt you, not a proxy for it.**
Round 5 found SEVEN separate instances of a check that could not fail, or a
field measuring something adjacent to its own name:

1. the at-rest gate is tunable, every resolution has a passing band
2. a vacuous margin assertion, fed inputs it was right to accept
3. `--preflight` ECHOED its checks as strings and always exited 0
4. nothing checked that the interpreter could import the driver's dependencies
5. `corpus_cited_status` calls itself THE NOVELTY GUARD and returns "cited" for
   papers present only in `docs/` notes and never in the paper
6. `determinism_identical` is a LOAD-TIME hull check (`sim_standing.py:389`,
   particle count plus grid_lim), NOT a trajectory check
7. **the Job B grader reported PASS at -9.806% and was wrong**, because
   `find_stationary_window` returns a TUPLE and the caller did
   `win.get("start",0) if isinstance(win,dict) else 0`, silently discarding an
   explicit `undecidable_too_short` verdict and averaging the whole transient

D4's line is the transferable one: **"testing a grader only on data it can grade
does not test its refusal."**

**Corollary, from D2, three for three:** every size figure produced by hand or
by a quick unchecked script was wrong at least once. Every figure recomputed
from `git ls-tree` inside a checked script was right. **Compute from the tree,
print the enumeration, check the sum.** The coordinator hit the same trap FOUR
times: awk field 4 versus 5 producing a false zero, whitespace-in-filename
miscounts, a filter that missed `ARR table 1`, and reading `final_disp_mag_m`
while reporting it as drift.

---

## 2. WHAT IS SETTLED, DO NOT RE-DERIVE

### E8 IS CLEARED. This is the biggest change.
Josie obtained permission for **CCSA/NCAC meshes, the AR&R paper, and
Wiley/CIWEM**, global, permitting republication. E8's rule clears on "written
permission OR a confirmed licence", and three independent sources established
there is no licence to confirm.

- **Recorded as HER REPORT, artifacts PENDING.** No artifact has been seen by
  D2, D3 or the coordinator. Triangulated as a three-party fact.
- **The settledness illusion, named by D2:** three grants arriving inside ninety
  minutes creates a feeling of settledness the evidence does not support. The
  evidence is three reports and zero artifacts, and the three come from
  UNRELATED rights holders, so they do not corroborate each other.
- **All remediation is WITHDRAWN, superseded in place, NOT pending work.** No
  file is to be removed, untracked or history-rewritten on E8 grounds.
- **STILL OPEN: UNSW WRL, a FOURTH rights holder.** Table 5-1's footer reads
  "WRL Technical Report 2014/07 FINAL September 2014", a different body and year
  from AR&R (Engineers Australia, February 2011). 760,091 B, uncovered by any
  grant. Table 5-1 is confirmed by its footer; Table 5-2 and Figure 5-5 are
  cropped and their attribution is INFERENCE.

Verified independently by the coordinator, keep as fact: all four CCSA archives
are **byte-identical to the published upstream releases** by SHA384 against
CCSA's own values (yaris-coarse `4f2b837ba0c85c2e`, yaris-detailed
`f68913788cbe5207`, silverado-coarse `1874a7fc4709082d`, silverado-detailed
`662312f50a80b7c2`), 88,592,238 B total. Both ccsa.gmu.edu model pages carry NO
licence text. Downloads come from media.ccsa.gmu.edu, so the NHTSA-safe-set
hypothesis is REFUTED. Geometry on origin is 30 files, 176.25 MB, on 30 of 30
public branches; the four `.ply` are 15.8 MB, under 9 percent.

### THE NOVELTY CLAIM IS DEAD IN ITS OLD FORM
- Catalog recall MEASURED at roughly 50 percent via an OpenAlex one-hop
  traversal. The count went 4, 5, 15, 16, 32 as instruments changed. **Any
  "N fording simulations exist" sentence is a FLOOR.**
- **Fixpoint traversal is REFUTED as the fix** (D1 erratum 9, and it had already
  been run): the frontier GREW every round with the topic filter applied, 92 to
  174, branching 82.2, hop-3 at 3.3 million nodes. And a relevance test applied
  at every node is not a closed operation, so its recall is exactly as
  unmeasurable as the catalogs it was meant to replace.
- **All three novelty axes are occupied.** Al-Qadami 2023
  (`10.3390/su151713262`) is FLOW-3D on a FULL-SCALE Perodua Viva under coupled
  6-DOF motion, with a four-level mesh-independence study, validated three ways.
  Azhar 2023 (`10.1111/jfr3.12885`) is SPH, a PARTICLE METHOD, physically
  validated, and is ALREADY in the project bibliography.
- **THE PAPER CITES NO MPM METHOD LITERATURE AT ALL.** Confirmed on the COMPILED
  PDF `public_release/Cerrell_CanItFord_paper.pdf` dated 2026-08-04: controls
  fire (Yaris 16, MPM 19, "material point" 6, Shand 4) and every probe returns
  zero (Sulsky, Bardenhagen, GIMP, "Generalized Interpolation", de Vaucorbeil,
  Nairn, "volumetric locking", "history-dependent"). **21 bib entries, 9 with a
  DOI, 14 rendered references, zero MPM method papers. 37 uncited MPM method
  papers identified.** This is a FOUNDATIONS gap rather than a novelty gap, and
  it is the most actionable paper-level finding of the round.

### PHYSICS: A1 MEASURED, JOB B NOT GRADEABLE
**A1 (job 917797), 23 of 23 rc=0, graded by `failure_modes.py` and NOT by
displacement:**
- mu=0.55, **STUCK**, the control HOLDS
- mu=0.30, SLIDE at frame 8, **stays INDETERMINATE by prior agreement**
- mu=0.0250, SLIDE at frame 6, **the inferred STUCK to SLIDE flip is MEASURED**

**CAVEATS THAT MUST TRAVEL WITH IT:**
- **mu=0.0250 is 22x below canonical friction. The flip is SUB-PHYSICAL and must
  NEVER be read as occurring at a realistic value.**
- `failure_modes.py:170` takes `abs(vx)`, so **upstream slosh scores as SLIDE**:
  102 of 191 conjunction frames have vx below zero, mean -0.1617 m/s.
- **Every 250-frame magnitude is measured at or after the first wall
  reflection** (predicted 112.3 frames, observed peaks at 112, 125, 126).
  Truncate to 91 or fewer frames, or caveat every magnitude.
- `peak_surge_accel_g = 0.682 g` is a **frame-0 one-sided-gradient artifact, and
  it is IN THE PUBLISHED RECORD TOO**. Excluding frame 0 gives 0.3954 g; from
  frame 20, 0.0285 g. **The real margin to SSF is 49.8x, not 2.08x. Never quote
  it as a load.**
- FLOAT is structurally untestable in all four runs, max dz exactly 0.0.
- 250 frames against the canonical 91, so NOT like for like.
- WITHDRAWN: "A2 spread understated by 43 percent". That compared `max|dx|`
  against a `dmag` range. Deduplicate by NAME AND UNIT, never by value.
- CLOSED: engine `627367e` is byte-identical to the vendored `544c93dd` on the
  three files the register cites, at the same line numbers.

**JOB B (917909) IS NOT GRADEABLE, and the reason is physical.**
The sphere never moved (z=0.575, vz=0 throughout). **The FREE SURFACE FELL 3.09
cm.** Deficit 69.2180 minus 47.8554 is 21.3626 N; dF/d(surface) is rho*g*A_w or
692.1799 N per metre; implied drop 3.09 cm, 6.17 percent of the 0.5 m column.
The sphere is pinned to the ORIGINAL waterline, so its submerged cap shrinks and
the reaction decays. **Compression explains only 23.9 percent** (EOS
b=0.00593475 per metre gives a 1.4970 percent density rise, about 0.74 cm).
**The other 76 percent is UNEXPLAINED and is the thing to find:** water leaving
through the floor or wall bands, or the jittered seed lattice settling denser
than it was created. Extrapolation is inconclusive and must not be quoted: five
late windows give asymptotes from 13.639 to 47.277 N, spread 33.638 N against a
69.218 N target. **More frames alone will NOT fix it**, because the surface
keeps falling. D4's fix is to MEASURE the free surface instead of assuming it,
commit `a7befa4`.

---

## 3. WHAT IS LEFT TO EXECUTE

### 3a. ON THE GPU (Vista). idev `917886` on `c642-032`, about 1h57m left at handoff.
**BEFORE ANYTHING:**
`export PYTHONPATH=/work/11603/jcerrell0629/vista/can-it-ford/mpm-engine/src:/work/11603/jcerrell0629/vista/.venv/lib/python3.12/site-packages:${PYTHONPATH:-}`
Neither Vista venv has trimesh; the shared venv does, trimesh 4.12.2. **DO NOT
install into that venv, other sessions are live on it.** A job without this
fails instantly with `ModuleNotFoundError: No module named 'trimesh'`, which
cost job 917786 entirely.

- **`srun --jobid=917886 --overlap` is MANDATORY**, and on this cluster a bare
  `srun` also needs `-p`. Without `--overlap` the step hangs behind the idev
  shell and dies.
- Driver sha256 MUST be
  `4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9` at
  `$WORK/can-it-ford-track1-6dof/renders/yaris_render_s1/sim_standing.py`.
  **The engine and the driver are in DIFFERENT roots on Vista**: `can-it-ford/`
  holds mpm-engine and the hull but NO driver.
- **Output paths MUST carry `${SLURM_JOB_ID}`.** Two jobs named `d4_jobA` wrote
  identical fixed paths and would have produced an unknown mixture of two runs.
- Queue: `gh-dev` is 20 nodes and saturated, 19 of 20 with 7 pending. `gh` has
  576 and scheduled a job in under a minute. Use `squeue --start`; `(Priority)`
  means queue position, `(Resources)` means the estimate is soft.

**Queued and ready via `simulation/r5_physics/prestage_jobs.sh`, triaged in
advance by D4 against 626 SU:**
- **A2 repeats**, for the N=1 problem: the 17 canonical runs are single draws.
- **B re-run with the measured free surface.** This is now the blocker for the
  project's FIRST EXTERNAL VALIDATION.
- **C, the Kramer sphere decay. Its drop rule is VOID.** C was dropped only
  because its criterion could not be graded without the supplementary. **D4
  FETCHED that supplementary by driving a REAL BROWSER**, after curl, WebFetch
  and the scite resolver all returned 403 from MDPI:
  `/Users/josie/can-it-ford-refs/2026-08-16/energies-14-00269-s001.zip`,
  17,549,045 B, sha256 `04c4d78d6987e4ee`, containing 27 time-series files
  including `01D/03D/05D_CI95_Normalized.txt`. **C is now gradeable. Re-cost it
  and state whether the triage order changes.**
- **P2G order-dependence**, the determinism-floor mechanism: non-associative
  order-dependent reductions can "alter discrete gates". Citations
  `10.3390/app14020639` and `10.1016/j.parco.2019.04.002`.

**Do NOT use idev for scripted work.** Interactive allocations historically
burned 98.5 to 99.1 percent of this project's Vista node-hours, with 95 of 184
runs ending in TIMEOUT. Use `tacc_submit`, which injects `--overlap` and
detaches with setsid nohup so a socket drop cannot kill a run.

### 3b. RENDERS, READ THIS BEFORE PROMISING PHOTOREAL
Josie asked for renders of the meshes in the most complex and realistic
environment possible. **Verify these constraints before planning:**
- **`pysplashsurf` wheels EXCLUDE aarch64.** The marching-cubes free-surface
  reconstructor runs on **LS6 (x86) ONLY**, not Vista. Water on Vista stays a
  per-column max-z heightfield unless the surface step is done on LS6 and the
  mesh is shipped back.
- Four render defects, all read from source, none yet fixed:
  1. **Water is invisible.** `k = 1300 /m` at SSC 13000 mg/L gives a black-disc
     visual range of **0.00 m**, and the caption itself admits k is EXTRAPOLATED
     above the 670 mg/L linear bound. The optics model runs **19x past its own
     validity limit**.
  2. **The car has no material model.** `render_multigeom_rollout.py` does
     `sh = clip(n @ LIGHT,0,1)*0.6 + 0.4`. Lambert plus constant ambient, one
     light, no specular, no Fresnel, no clearcoat, no shadow. The WATER gets
     Schlick plus Beer-Lambert plus GGX; the CAR gets two lines.
  3. **The asphalt PBR set is already in the repo and unused.**
     `assets/Asphalt015_1K-JPG_Color.jpg`, `_NormalGL.jpg`, `_Roughness.jpg`, a
     complete ambientCG CC0 set. A grep of all three render modules returns the
     HDRI at 8 sites and the asphalt maps at **0**.
  4. The caption occupies roughly 70 percent of every frame.
- Published chain to follow: arXiv 2403.11156, SPH to SplashSurf to Blender.
  Render target: Zhou 2025 `10.1063/5.0276643`, tire-pavement hydroplaning in MPM.
- **State in any legend that the texture is VISUAL ONLY** and never implies
  spatially varying friction the solver does not have.
- E8 no longer blocks new frames. That hold is withdrawn.

### 3c. ON THE MAC, NO GPU NEEDED
- 26 `rollout.npz` and 71 `metrics.csv` are already on local disk, and `uv` is at
  `/opt/homebrew/bin/uv`. No system python has numpy.
- **Blocking gives the settle argument a STOPPING RULE**, which "a longer run
  changed the answer" does not: Flyvbjerg and Petersen `10.1063/1.457480`,
  Jonsson automated blocking `10.1103/PhysRevE.98.043304`, Grossfield 2019
  `10.33011/livecoms.1.1.5067` (2019, NOT 2018), Bergmann `10.1115/1.4052402`,
  which is engineering CFD and the closest venue match. **All uncited here.**
- Impact and water-entry events have **NO steady force**: report peak
  distributions, impulses or envelopes with repeat-run uncertainty, never a
  steady mean.
- Report **gate-pass FREQUENCY**, not pass or fail, for a gate known to be tunable.

### 3d. THE REGISTER MERGE, step 1 IS DONE
Side A was committed in `790d999` on `claude/add-ci-checks`, carrying both
CLAUDE.md and the register. Both sides are now in git history, so **neither can
silently vanish**, and this is an ordinary two-branch merge. Arithmetic
re-derived from committed objects and it holds: merge-base `1a868f3` at 656,
A at 760, B at 1455, target 1559, `git merge-file` exit 0, zero conflicts.
**Do not read the unchanged number 760 as an unchanged situation**; it now means
760 AND COMMITTED.

---

## 4. WHAT ONLY JOSIE CAN DO

1. **Rotate 12 credentials. ZERO are rotated. This is now the ONLY open exposure
   of any kind.** Use the source document's own `ROTATION LIST, START HERE` at
   line 123 of `docs/CREDENTIAL_EXPOSURE_2026-08-13.md`, specifically the
   1196-line copy on `claude/credential-exposure-2026-08-13-DO-NOT-PUSH`. The
   main-tree copy is only 118 lines and has NO rotation list.
   - Rows 1 and 2 are GitHub fine-grained PATs. The repo is PUBLIC and they can
     WRITE. Row 2 is exported at `~/.zshrc:750`, live in every shell.
   - `~/.claude/backups/` gains a new file carrying token-shaped material roughly
     **once a minute**. Deletion cannot win; only revocation at the issuer ends it.
   - Expect the `github` MCP server to break until the PAT is replaced. Re-auth
     Claude Code with `/login`, NOT `claude setup-token`.
   - The coordinator's honest view: the two GitHub PATs are worth doing tonight;
     the other ten are lower stakes and defensible to defer.
2. **A destination for the bundles.** Everything currently sits on ONE DISK with
   the repo it protects. `ALL-refs-MINUS-credentials.bundle`, 118 refs, verify
   OK, controlled by mirror-clone, is shippable to an ordinary destination on
   BOTH the licence and credential axes right now.
3. **Per-branch push go-ahead.** Nothing is pushed. `pushcheck` BLOCKs
   `claude/r5-exposure` on a FILENAME RULE only. **No credential value appears
   anywhere on that branch**, verified as 0 pattern hits across added lines.
4. **The WRL question:** does the Engineers Australia grant cover WRL Technical
   Report 2014/07?
5. **The Vista `9.81` fix.** `simulation/failure_modes.py`, `G = 9.80665` to
   `9.81`, was found UNCOMMITTED on Vista and captured by D3. **The line is
   written; the re-run and the byte-identical verdict comparison are NOT done.
   CLAUDE.md item 15 is STARTED, NOT CLOSED.**

---

## 5. INFRASTRUCTURE STATE

- **Insurance:** `can-it-ford-bundles/` holds dated directories for 2026-08-16,
  17 and 18, plus `incoming/` (Vista captures), `main-tree-strays/` (9 files
  with provenance), `refresh_bundle.sh`, and two watchdogs. The latest full
  bundle covered 292 at-risk commits across 137 refs, verify OK, with a
  credentials-free variant at 118 refs.
- **Vista held TWO pockets of single-copy work**, both now captured: the `9.81`
  fix, and `$WORK/can-it-ford-OLD-pre-purge` carrying 2 commits absent from this
  Mac's object store. **Captured as PATCHES and not as history**, deliberately,
  because that directory predates a credential purge and bundling it would
  re-import pre-purge objects.
- **TEN Round-4 sessions are alive with DELETED working directories.** They can
  only write via absolute paths, which land in the MAIN checkout on a branch none
  of them owns. Josie has not yet said kill or restore. The coordinator's
  recommendation is KILL: everything they committed is on their branches and
  inside the bundles. A supervisor auto-snapshots any new stray with provenance.
- **Hooks:** `gate_destructive.sh` asks on EVERY `git commit`, and on any command
  whose TEXT contains a recursive-delete literal, including inside an `echo`
  string, which caused repeated false blocks. All five gates were verified armed
  after `settings.json` changed.
- **`round5_autodispatch.py` bugs FIXED, do not reintroduce.** `list-panes -a`
  spans every tmux session and resolved D1 to D4 to the Round-4 `canford`
  session. And the spinner regex must NOT contain bare glyphs, because Claude
  Code uses the same marks for "Determining… (7m 16s)" and "Cogitated for
  23m 15s", so a bare glyph reports a finished session as working.

---

## 6. HOW TO BEHAVE

- **A monitor alert is a timestamped OBSERVATION, not current state.** Re-check
  before acting on it. The coordinator told D4 to commit files that were already
  committed, from a stale alert it did not re-verify.
- **Session-relative time is unreliable, and only when parked at a prompt.** A
  session blocked for 21 hours perceived its day-old commit as "minutes ago" and
  nearly published "this machine's clock is unreliable". Wall-clock sources are
  consistent and mutually agreeing; when a session's sense of elapsed time
  conflicts with them, the SESSION is wrong.
- **Clear blocked sessions FAST.** Two sat blocked for about 21 hours. Verify the
  target first (does the delete path even exist? is the commit path-limited and
  in scope?) then clear. Do not weaken the gate to avoid the prompt.
- **Relay a commit SHA, never a summary.**
- **One source cited twice is not two sources.** D1 broke this in the row of its
  own document that called itself the most robust finding.
- Never bulk-stage: no all-files flag, no bare dot, no all-modified commit flag.
  Stage explicit paths and commit path-limited. Never push without a per-branch
  go-ahead. The repo is PUBLIC. No em-dashes anywhere.
