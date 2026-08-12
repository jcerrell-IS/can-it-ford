# ULTRA REVIEW, 2026-08-11

Phase-by-phase live audit. Read-mostly: the only intended write is this file.

**Environment tags are mandatory in this document.** `[MAC]`, `[VISTA]`, `[LS6]`,
`[GITHUB]`. An untagged environment claim below is a defect in this report.

**Interpreter note, applies to every `[MAC]` python claim.** The `python3` on PATH
is `/opt/homebrew/bin/python3` 3.14.6 and it has no numpy, no pandas and no
matplotlib. Neither do `/usr/bin/python3`, `python3.12`, `python3.13` or
`python3.14`. Every `[MAC]` python result below therefore names the interpreter
that produced it. See VERIFIED BROKEN item B-1.

**Side effect disclosed.** `analysis/classify_failure_modes.py` writes two files as
a side effect of running. It was run during Phase 3. Both outputs came back
byte-identical to the committed copies (`git diff --stat` empty), so the tree was
not dirtied, but the run was not read-only.

**Concurrency.** Three other Claude sessions were reported active in this repo
during this audit, and Vista job `903115` (idev, `c642-011`) was running throughout.
The uncommitted `.gitignore` change described below may belong to another session.
Nothing was staged, committed or reverted on its behalf.

---

## 1. VERIFIED WORKING

### Git and GitHub

**W-1 `[GITHUB]` The repository is reachable, public, and pushed today.**
```
gh repo view jcerrell-IS/can-it-ford --json visibility,pushedAt
  -> {"pushedAt":"2026-08-11T13:16:01Z","visibility":"PUBLIC"}
```

**W-2 `[GITHUB]` `gh` is authenticated with write scope.**
```
gh auth status
  -> Logged in to github.com account jcerrell-IS (keyring), Active account: true
     Git operations protocol: ssh, Token scopes: admin:public_key, gist, read:org, repo
```

**W-3 `[MAC]` Commit `a991216` exists, and it is an ancestor of `main`.**
```
git cat-file -t a991216                          -> commit
git rev-parse --verify a991216                   -> a991216f990843b15919f5c0d19b5ba3f68c2992
git merge-base --is-ancestor a991216 main        -> exit 0
```
Authored 2026-07-30 20:29:15 -0500, parent `dfc994b`. Register H1's statement that
`paper/conference_101719.tex` "is marked SUPERSEDED by commit `a991216`" is
**correct as to existence**. See F-1 for the part of H1 that does not survive.

**W-4 `[MAC]` The pre-push gate fires, including on a dry run.**
```
git push --dry-run
  -> BLOCKED: push not pre-approved. Re-run as: PUSH_OK=1 git push ...
     error: failed to push some refs to 'https://github.com/jcerrell-IS/can-it-ford.git'
```
This is the documented `.git/hooks/pre-push` behaviour working. Worth knowing that
it blocks `--dry-run` too, so there is no un-gated way to preview a push.

### Canonical data, Phase 4

**W-5 `[MAC]` The 17-run count is intact and unchanged.**
```
wc -l data/all_runs_inventory.csv                -> 18   (17 rows + header)
/Users/josie/can-it-ford-env/bin/python3 -c "import pandas as pd; \
  d=pd.read_csv('data/all_runs_inventory.csv'); print(len(d),'rows'); print(d['run'].tolist())"
  -> 17 rows
```
Run names, in file order: `g48_m1100`, `g48_m1609`, `g48_m2337`, `g64_m1100`,
`g64_m1609`, `g64_m2337`, `g96_m1100`, `g96_m1609`, `g96_m2337`,
`sweepD_g64_d0p25`, `sweepD_g64_d0p35`, `sweepD_g64_d0p45`, `sweepV_g64_v0p5`,
`sweepV_g64_v1p0`, `sweepV_g64_v2p0`, `sweepV_g64_v2p5`, `sweepV_g64_v3p0`.

**W-6 `[MAC]` The 14 FORD count is intact, and the live file is the 10-column one.**
```
/Users/josie/can-it-ford-env/bin/python3 -c "import pandas as pd; \
  d=pd.read_csv('data/scenario_sweep.csv'); print(len(d.columns),'cols',len(d),'rows'); \
  print(d['L1_verdict'].value_counts().to_dict())"
  -> 10 cols 70 rows
  -> {'NO-FORD': 56, 'FORD': 14}
```
Neither number has drifted. 14 FORD of 70 is exactly what CLAUDE.md and the
register cite, and the 10-column live file is in place rather than the 5-column
snapshot the session-start reminder warns about.

**W-7 `[MAC]` The published 16 SLIDE / 1 STUCK verdicts reproduce byte-for-byte today.**
```
/Users/josie/can-it-ford-env/bin/python3 analysis/classify_failure_modes.py
  -> 17 runs: 16 SLIDE, 1 STUCK
  ->   SLIDE   ratio >= 1 in 17 runs, triggered in 16
  ->   TOPPLE  ratio >= 1 in 13 runs, triggered in  0
  ->   FLOAT   ratio >= 1 in  1 runs, triggered in  0
  -> JSON runs payload matches committed copy: True
git diff --stat -- data/failure_modes_by_run_classified.csv data/failure_modes_by_run.json
  -> (empty)
```
`sweepV_g64_v0p5` is the STUCK run, matching CLAUDE.md item 12. The
`TOPPLE ratio >= 1 in 13 runs, triggered in 0` line is the item-12 trap (a) firing
exactly as documented: filtering on ratio rather than on `triggered_*` would report
13 topples that never happened.

### Scripts, Phase 3

**W-8 `[VISTA]` `warpmpm` imports on the login node, in 2 seconds, exit 0.**
```
scripts/tacc.sh vista 'source /work/11603/jcerrell0629/vista/.venv/bin/activate && \
  cd /work/11603/jcerrell0629/vista/can-it-ford && \
  S=$SECONDS; timeout 180 python3 -c "import warpmpm"; echo "WALL_SECONDS=$((SECONDS-S)) RC=$?"; hostname'
  -> WALL_SECONDS=2 RC=0
  -> login2.vista.tacc.utexas.edu
```
Package resolves to `/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/__init__.py`.
**This refutes the standing memory `vista-login-warpmpm-import-hangs.md`**, which
records a 600 s block at near-zero CPU returning RC=124 on `login1`. On `login2`
today, inside the project venv, it is 2 seconds and RC=0. The memory is stale as
written. It was measured on a different login node, so it is possible the block is
node-specific rather than fully retired; that is not settled here.

**W-9 `[MAC]` `simulation/validate_coupling_force.py` runs C2 to completion and emits Archimedes numbers.**
```
/Users/josie/.venvs/canitford-mpm/bin/python3 simulation/validate_coupling_force.py \
  --variant c2 --n-grid 64 --max-frames 5
  -> EXIT=0
```
Selected output fields:
```
"variant": "C2_equilibrium_draft",  "n_grid": 64,  "n_total": 254171,
"draft_measured": 0.9194214425515383,
"draft_incompressible": 0.8832883419119752,   "err_vs_incompressible_pct": 4.090748051915755,
"draft_compressible":  0.8609135001070722,    "err_vs_compressible_pct":  6.796030313985023,
"settle_gate_met": false
```
See F-2, this is the most consequential finding in the pass.

> NAMING, added 2026-08-12: the identifier in the transcript above was renamed
> `C2_equilibrium_draft` -> `CV2_equilibrium_draft` to clear a collision with the gate
> metric `C2_veh_zmin_rise`. The quoted output is left exactly as observed on
> 2026-08-11 and is not retroactively edited. See register Section J item 1.

**W-10 `[MAC]` The `--n-grid 32` rejection is a deliberate guard, not a bug.**
```
/Users/josie/.venvs/canitford-mpm/bin/python3 simulation/validate_coupling_force.py \
  --variant c2 --n-grid 32 --max-frames 5
  -> EXIT=1
  -> ValueError: n_grid=32: water lattice spans [0.6330, 8.7887] m but the P2G edge
     guard requires (0.4416, 8.6857) m for dx=0.2944. wall is fixed at 4*DX_CANON to
     keep geometry invariant across the refinement step, so only n_grid >= 64
     satisfies this.
```
The guard is at `simulation/validate_coupling_force.py:212`. The exit-1 here is the
script correctly refusing an invalid configuration, and it names the reason and the
minimum valid grid. Do not record `--n-grid 32` as a failure of the harness.

**W-11 `[MAC]` `.claude/checks/params_check.py` runs clean and its documented gate inventory is confirmed.**
```
/Users/josie/can-it-ford-env/bin/python3 .claude/checks/params_check.py
  -> EXIT=0
  -> params_check.py: no blocking issues found
```
All four literature-cited tags named in CLAUDE.md's GATE INVENTORY emitted:
`lit:geometry_bbox`, `lit:sound_speed_cfl`, `lit:resolution_convergence_gci`,
`lit:manifest_provenance`. The CLAUDE.md instruction to run the script rather than
grep for `lit:resolution_convergence_gci` is correct: it is assembled at runtime and
appears only in output.

Two of its warnings are worth carrying forward as-is:
- `[lit:sound_speed_cfl] 15/17 runs below the 10x convention`, worst
  `sweepV_g64_v3p0` at 4.28x. Matches register B8 exactly.
- `[lit:manifest_provenance] across 32 manifests: canitford_git_commit missing in 32,
  grid_density missing in 32, mesh_sha256 missing in 32, solver_git_sha missing in 32,
  vehicle_mass missing in 32, runs cannot be traced to code plus data plus environment.`

**W-12 `[MAC]` Three further canonical scripts start clean.**
```
/Users/josie/can-it-ford-env/bin/python3   render_frames.py --help                    -> EXIT=0
/Users/josie/.venvs/canitford-mpm/bin/python3 simulation/validate_coupling_force_ladder.py --help -> EXIT=0
/Users/josie/can-it-ford-env/bin/python3   simulation/failure_modes.py --help         -> EXIT=0
```
Note `analysis/classify_failure_modes.py --help` does not print help, it runs the
full classifier. Harmless here, but it means `--help` is not a safe probe on that
script.

`renders/yaris_render_s1/sim_standing.py` was **not** run. It was offered as a smoke
candidate but sits under the do-not-touch path in the same instruction set, and it
is a simulation driver that writes outputs. Resolving that conflict is not mine to
make silently.

---

## 2. VERIFIED BROKEN

### B-1 `[MAC]` No python on PATH can run any script in this repo. NEW.

```
for p in /usr/bin/python3 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.13 \
         /opt/homebrew/bin/python3.14; do "$p" -c "import numpy,pandas"; done
  -> ModuleNotFoundError: No module named 'numpy'      (all four)
python3 render_frames.py --help
  -> ModuleNotFoundError: No module named 'matplotlib'   EXIT=1
python3 simulation/validate_coupling_force.py --variant c2 --n-grid 32 --max-frames 5
  -> ModuleNotFoundError: No module named 'numpy'        EXIT=1
```
Working environments exist but are undocumented, off PATH, and **no single one is
complete**:

| venv | numpy | pandas | matplotlib | warp | trimesh |
|---|---|---|---|---|---|
| `/Users/josie/.venvs/canitford-mpm` | 2.5.1 | **NO** | 3.11.1 | 1.16.0 | 5.0.0 |
| `/Users/josie/can-it-ford-env` | 2.5.1 | 3.0.5 | 3.11.1 | **NO** | **NO** |
| `/Users/josie/can-it-ford-demo/.venv` | 2.5.1 | 3.0.5 | **NO** | **NO** | **NO** |
| `/Users/josie/can-it-ford-render-p5/venv` | 2.5.1 | **NO** | **NO** | **NO** | 5.0.0 |
| `/Users/josie/ford_buildenv` | **NO** | **NO** | **NO** | **NO** | **NO** |

Consequence: solver work needs `canitford-mpm` (has `warp`), dataframe analysis needs
`can-it-ford-env` (has `pandas`), and nothing does both. Any instruction in this repo
of the form `python3 <script>` is wrong as written on this machine. CLAUDE.md names
no interpreter anywhere.

### B-2 `[VISTA]` Vista's `CLAUDE.md` is 18 days stale and carries two claims the Mac copy has since refuted. NEW as measured.

```
md5 /Users/josie/can-it-ford/CLAUDE.md                                  -> 76c0b703036b15b5a0fa258fb1bea572
wc -l /Users/josie/can-it-ford/CLAUDE.md                                -> 544

scripts/tacc.sh vista 'md5sum .../vista/can-it-ford/CLAUDE.md; wc -l .../CLAUDE.md'
  -> e87e02d2cb8de1f7896a3034f9e06109
  -> 68
scripts/tacc.sh vista 'cd .../can-it-ford && git log -1 --format="%ci" -- CLAUDE.md'
  -> 2026-07-24 22:36:04 -0500
```
544 lines against 68. Not a drift, a different document. Vista's HEAD is `b00bf7b`.

The two refuted claims, read live from Vista's copy:
1. `"vehicle effective density 100-300 kg/m^3 band"`. The Mac copy states the
   canonical value is **310.494 kg/m^3** and that "the 100-300 band is STALE".
2. `"coup_friction is a numerical stability coefficient, NOT physical mu"`. The Mac
   copy states, confirmed 2026-08-05 by direct source read at
   `legacy_coupler.py:322`, that `coup_friction` **is** the Coulomb friction
   coefficient, "superseding all earlier statements that coup_friction was
   numerical-only".

This is the machine the simulations run on. It is operating under standing rules the
canonical copy explicitly retired.

**This also refutes the session-start hook's own orientation line**, which asserts
`CLAUDE.md (project root) = Multi-Pane Standing Rules, confirmed synced
Mac/Vista/LS6/GitHub`. It is not synced with Vista. That line is injected into every
session, so the false claim recurs on every startup until fixed.

### B-3 `[LS6]` LS6 is unreachable. Known cause, external.

```
scripts/tacc.sh ls6 'echo LS6_OK; hostname'                              -> exit 255
scripts/tacc.sh ls6 'test -d $WORK/.venv && echo VENV_EXISTS || echo VENV_MISSING' -> exit 255
  -> Lonestar6 is currently in maintenance mode.  Remote access
  -> will be unavailable until after the maintenance is complete.
  -> jcerrell0629@ls6.tacc.utexas.edu: Permission denied (keyboard-interactive).
```
Two attempts, per instruction, no further retries. This is **not** the expired
ControlMaster socket that `tacc.sh` guesses at in its own error message: TACC's
banner states maintenance mode before the auth failure. The wrapper's advice
("Re-authenticate once interactively: `ssh ls6`") will not work while maintenance is
active and is misleading here.

### B-4 `[VISTA]` Bare `python3` on Vista cannot import `warpmpm`. Test-methodology defect, not a code defect.

```
scripts/tacc.sh vista 'cd .../can-it-ford && timeout 60 python3 -c "import warpmpm"'
  -> ModuleNotFoundError: No module named 'warpmpm'                       RC=1
# with PYTHONPATH but no venv:
  -> File ".../warpmpm/core/solver.py", line 15, in <module>
     import warp as wp
     ModuleNotFoundError: No module named 'warp'                          RC=1
```
Recorded because the prompt's own smoke command is the bare form and it fails. The
module is fine (W-8); the invocation is not. Correct form requires
`source /work/11603/jcerrell0629/vista/.venv/bin/activate` first.

### B-5 `[MAC]` `[GITHUB]` Register E3 is false. Rogue and Silverado hulls have both entered simulations.

`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md:200` states:
> Rogue and Silverado meshes exist but never entered a simulation.

Contradicted on both machines.

`[MAC]` `data/class_specific_runs_2026-08-08.csv` holds 7 rows naming those runs with
job ids: `class_rogue_g64` and `class_silverado_g64` (job 896273),
`hull_rogue_dxm` / `hull_silverado_dxm` / `hull_yaris_dxm` (job 896302),
`hull_rogue_g96` / `hull_silverado_g96` (job 896302).

`[VISTA]` The run directories and result files exist:
```
scripts/tacc.sh vista 'find .../class_specific_2026-08-08 .../render_s3_hullsweep -name summary.json'
  -> class_specific_2026-08-08/class_rogue_g64/summary.json
  -> class_specific_2026-08-08/class_silverado_g64/summary.json
  -> render_s3_hullsweep/hull_rogue_g96/summary.json
  -> render_s3_hullsweep/hull_rogue_dxm/summary.json
  -> render_s3_hullsweep/hull_yaris_dxm/summary.json
  -> render_s3_hullsweep/hull_silverado_dxm/summary.json
  -> render_s3_hullsweep/hull_silverado_g96/summary.json
scripts/tacc.sh vista 'ls .../vista/hulls/'
  -> rogue_g96_pd8_coarse_watertight.ply
  -> silverado_g96_pd8_coarse_watertight.ply
```
Compounding defect: the register **never mentions these runs anywhere else**. A
search of the whole register for `rogue|silverado|class_specific|multigeom` returns
line 200 (the false claim), line 209 (the class-to-vehicle mapping), line 217
(licensing), line 354 (an index row) and line 378 (J12). The corrections authority
has no record that the multi-geometry work happened. Not fixed here, per instruction.

### B-6 `[MAC]` `[GITHUB]` PR #9 is open, conflicting, and it holds a correction that `main` still lacks.

Not a discrepancy about whether `a991216` exists. It does (W-3). The two commits are
the **same change applied twice on different bases**, and they differ in one
substantive line.
```
git log -1 --format="%H %ci %P" a991216
  -> a991216f99... 2026-07-30 20:29:15 -0500  parent dfc994b
git log -1 --format="%H %ci %P" 0901eeb
  -> 0901eeb220... 2026-07-31 17:27:28 -0500  parent 1767d87
diff <(git show a991216 --format="") <(git show 0901eeb --format="")
  -> 18c18
  -> < +%   Remote head was bbd5bd8 on 2026-07-31; heads move, so always check
  -> --- 
  -> > +%   Remote head was af77160 on 2026-07-31; heads move, so always check
```
`0901eeb`'s own message says why: "The quoted remote head was refreshed from
`bbd5bd8` to `af77160` ... `bbd5bd8` was four Overleaf pushes stale and would have
shipped already wrong."

So `main` carries the version the author identified as wrong, and the fix is stuck:
```
git merge-base --is-ancestor 0901eeb main   -> exit 1  (NOT an ancestor)
git branch -a --contains 0901eeb            -> paper/mark-superseded, origin/paper/mark-superseded
gh pr view 9 --json state,mergeable,mergeStateStatus
  -> {"state":"OPEN","mergeable":"CONFLICTING","mergeStateStatus":"DIRTY"}
```
And **both SHAs are now stale anyway**:
```
grep -n "Remote head was" paper/conference_101719.tex   -> 13: ... bbd5bd8 ...
git ls-remote overleaf refs/heads/main                  -> 6466dfa1c9d1adb9753bc5d48d885ab1eee16971
```
Register H1 quotes `6466dfa` for the Overleaf head, which is correct and current.
Its "the two-paper-copy question is CLOSED" is defensible for the question it names.
What it does not say, and what is true, is that the header doing the marking cites a
remote head two revisions out of date, and that the PR written to fix that is open
and conflicting.

### B-7 `[MAC]` Finished paper work is sitting undelivered on a local branch.

```
git rev-list --left-right --count overleaf/main...claude/overleaf-gci-citations-2026-08-08
  -> 0       1
git log --oneline overleaf/main..claude/overleaf-gci-citations-2026-08-08
  -> 396094e Cite Roache, Celik et al., Bai/Schroeder and Sun/Shinar/Schroeder,
             and state why no GCI is reported
git show --stat 396094e
  -> can_it_ford_references_IEEE.bib | 50 +++++++
  -> conference_101719_1.tex         |  4 ++++
```
Overleaf is canonical for the paper. This commit is one ahead of `overleaf/main` and
has never been pushed. It is the GCI-citation work, and `params_check.py` is
currently emitting three `lit:resolution_convergence_gci` warnings that say a GCI
band cannot be computed, which is precisely what this commit documents. Delivering it
needs a fresh Overleaf token (see O-9) and a deliberate decision, because
`git push overleaf main` overwrites rather than merges.

Other unmerged work, listed without judgement on whether it should land:

| branch | ahead of main | last commit |
|---|---|---|
| `claude/overleaf-gci-citations-2026-08-08` | 30 (1 vs overleaf/main) | 2026-08-08 |
| `audit/g-mergetest-2026-08-04` | 6 | 2026-08-04 |
| `push-ready-2026-08-04` | 4 | 2026-08-04 |
| `worktree-c1-triage` | 3 | 2026-08-07 |
| `claude/figure-validation-sources-826ba6` | 2 | 2026-08-04 |
| `claude/bingham-material-sweep-2026-08-07` | 1 | 2026-08-08 |
| `paper/mark-superseded` (PR #9) | 1 | 2026-07-31 |

`worktree-c1-triage`'s content did land by another route:
`docs/COUPLING_VALIDATION_J1_2026-08-07.md` is on `main` via `ecb2d51`, so those
three commits are duplicate-by-content, not lost work.

### B-8 `[MAC]` `main` has 2 unpushed commits and an unreviewed dirty file.

```
git rev-list --left-right --count origin/main...main   -> 0   2
git log --oneline origin/main..main
  -> 65b3450 Close the class_specific CSV provenance gap with an honest reconstruction
  -> 9f503fc Register D7: resolve the drift-tolerance declaration count with /usr/bin/grep
git status --porcelain
  ->  M .gitignore
  -> ?? docs/COUPLING_VALIDATION_J1_2026-08-07.md.bak-premerge
git diff .gitignore
  -> +render_s2/
```
The `.gitignore` edit matches a change that was proposed and explicitly deferred
earlier today. With three concurrent sessions live, the default assumption per
CLAUDE.md is that it belongs to another session. Left untouched.

---

## 3. UNABLE TO VERIFY

### U-1 `[LS6]` Everything about LS6.

Blocked by B-3. Unverified: whether `$WORK/.venv` exists, the drainA COLMAP state
in register K1, and whether LS6's `CLAUDE.md` matches either the Mac or Vista copy.

**What would settle it:** re-run `scripts/tacc.sh ls6 'echo LS6_OK; hostname'` after
TACC clears maintenance. A non-255 exit means the audit can proceed. Check the TACC
user portal for the maintenance window end rather than polling.

### U-2 `[MAC]` `[VISTA]` Whether register J1 is now closeable.

`docs/COUPLING_VALIDATION_J1_2026-08-07.md:246-270` says **"Do not close J.1"**, on
four grounds. Its ground 1 is now stale:
> **C2 has no number at all**, 0 of 4 invocations. This is the Archimedes test J.1
> names first. Blocked by the P2G edge guard at `core/solver.py:508`, which is a
> scene-geometry problem in the C2 tank, not a resolution cost.

W-9 shows C2 now runs to exit 0 and emits `err_vs_incompressible_pct 4.09` and
`err_vs_compressible_pct 6.80` against measured draft 0.9194 m. The edge guard is now
an explicit precondition with a diagnostic message (W-10) rather than an unhandled
block.

What that does **not** establish: the run used `--max-frames 5` and returned
`"settle_gate_met": false`. A truncated smoke run that does not close its own settle
gate is not the validation J1 asks for. Grounds 2 (C1 sign-inverted, -122% to -326%),
3 (C3 zero-`a_ideal` metric) and 4 (C0 is a dry drop) were not retested here.

**What would settle it:** run C2 at full settle on both `--n-grid 64` and `--n-grid 96`
with no `--max-frames` cap, confirm `settle_gate_met: true` in both, then re-run C1 at
the same two resolutions and check whether the sign inversion persists. Only then
revisit the J1 doc's verdict. Do not close J1 on the 5-frame result in W-9.

### U-3 `[MAC]` `[VISTA]` Whether the 2337 kg class vehicle is a Dodge Ram or a Chevrolet Silverado.

Register line 209 maps **2337 kg = 2018 Dodge Ram 1500, a 2270P test vehicle**.
Register J12 (line 378) speaks of "the Rogue and **Ram** decks". But the hull that
actually ran is `silverado_g96_pd8_coarse_watertight.ply`, and
`data/class_specific_runs_2026-08-08.csv` gives `class_silverado_g64` a mass of
**2270.0 kg**, not 2337. Register line 217 lists "Rogue, Ram, 2014 Silverado" as
three separate CCSA-hosted models.

I did not establish whether 2270P/Silverado and the Ram are the same NCAC asset under
two names, or two different vehicles, and guessing would put a wrong vehicle identity
into the paper's class mapping.

**What would settle it:** open the NCAC/CCSA model page for the 2270P test vehicle and
read the make and model off it, then reconcile against register line 209 and the
`vehicle` column in `data/class_specific_runs_2026-08-08.csv`. This is a
primary-source lookup, not a repo question.

### U-4 `[MAC]` The "Part 5 numbered open-items list" named in the audit instruction.

There is no document in this repo matching that description. A search for `Part 5`
across `docs/`, root `*.md` and `.claude/` returns two files:
`docs/PROJECT_HISTORY_AND_LESSONS_2026-07-26.md:109` ("Part 5: two honest asterisks",
two prose caveats about particle-count reproducibility, not a numbered open-items
list) and a July 13 session archive. CLAUDE.md itself has no numbered Part headers at
all, which its own AUGUST 8 LITERATURE ADDENDUM already records.

Phase 6 below was therefore run against the two open-item lists that do exist and are
canonical: register `SECTION J` and CLAUDE.md's `STILL OPEN, not closed` block.

**What would settle it:** point me at the file. If "master instructions" means a
document held outside this repo, it was not in my context.

---

## Appendix: Phase 6 open-items triage

Against `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` SECTION J, all 14 items,
no sampling. Items 2, 3, 4 and 8 are already marked CLOSED in the register text
itself and are listed for completeness.

| # | Item | Status | Evidence |
|---|---|---|---|
| J1 | Coupling-force validation, C1/C2 at canonical + one refinement | **CONFIRMED STILL OPEN**, but its stated blocker is STALE | See U-2. C2 now runs (W-9); J1 doc's "0 of 4 invocations" no longer holds. `[MAC]` |
| J2 | superseded by H5 | already CLOSED in register | register line 367 |
| J3 | `failure_modes_result.json` citations | already CLOSED in register | register line 368 |
| J4 | classifier run on all 17 | already CLOSED in register, and re-confirmed live | W-7 `[MAC]` |
| J5 | Which length `vehicle_params.py` actually uses, E4 | **RESOLVED, NOT RECORDED** | `vehicle_params.py:131` reads `"bbox_m": (4.30, 1.70, 1.47)`. Live import confirms `bbox_m: [4.3, 1.7, 1.47]`. The answer is **4.30**, not 4.2826. Register E4 (line 202) still says "UNRESOLVED: which value the live `vehicle_params.py` uses." `[MAC]` |
| J6 | Retrieve Xia 2011 and Shu 2011 publisher PDFs | **CONFIRMED STILL OPEN** | `ls citations/ \| grep -i "xia\|shu"` returns nothing `[MAC]` |
| J7 | `channel_recirc_v2` velocity tail, 329 of 3.66M particles | **CONFIRMED STILL OPEN** | `recirc_out_v2/` holds only CONTROL and smoke CSV/JSON pairs; `RECIRC_CHANNEL_V2.md` (59288 B) and `V3.md` (63804 B) exist on Vista, both dated 2026-08-04, and the standing handoff records they have never been read `[VISTA]` |
| J8 | in/outflow BC attribution | already CLOSED in register | register line 374 |
| J9 | Whether the p2g source read matches Genesis 1.1.1 not 1.2.0 | **CONFIRMED STILL OPEN** | Register C1 (line 92) still reads "Prior crash forensics were pinned to 1.2.0 source and are unconfirmed as the same code." Not retestable from the Mac `[MAC]` |
| J10 | DesignSafe DOI, Kumar sign-off, gated on E8 | **CONFIRMED STILL OPEN** | Gated on J11, which is open `[MAC]` |
| J11 | CCSA/NCAC mesh redistribution rights, E8 | **CONFIRMED STILL OPEN** | Register line 219 still reads "UNRESOLVED and load-bearing: which side of that line the canonical Yaris falls on" `[MAC]` |
| J12 | Three-mass FE swap-in from LS-DYNA decks | **CONFIRMED STILL OPEN**, and needs rewording | The FE-deck swap-in is not done. But J12 is now misleading: watertight PLY hulls for Rogue and Silverado **have** run (B-5), by a different route than the deck extraction J12 describes. See also U-3 on Ram vs Silverado `[MAC]` `[VISTA]` |
| J13 | Compute the tank's blockage ratio | **CONFIRMED STILL OPEN** | Three docs discuss it; register line 248 still says "our own tank has a computable blockage ratio", line 379 "Nobody has computed ours." No number found `[MAC]` |
| J14 | Write G14 and G15 negative findings into the paper | **CONFIRMED STILL OPEN** | `grep -c "G14\|G15" paper/canonical_2026-08-02/conference_101719_1.tex` -> 0 `[MAC]` |

CLAUDE.md `STILL OPEN, not closed` block, one item:

| Item | Status | Evidence |
|---|---|---|
| O-9. Overleaf token off local disk but NOT revoked | **CONFIRMED STILL OPEN** | `grep olp_ .git/config` returns nothing, and `git remote -v` shows `overleaf https://git.overleaf.com/6a5958d10484feadf65a934e` carrying no credential. Both halves of the CLAUDE.md claim hold: the token is off disk, so a push will prompt, and nothing here can confirm server-side revocation. Rotating it in Overleaf account settings is still required, and is now also a prerequisite for delivering B-7 `[MAC]` |

Phase 5 stale-marker sweep, for completeness. The prescribed pattern returned only
three hits repo-wide across both files:
- `register:200` "never entered a simulation" -> **CONTRADICTED**, see B-5.
- `CLAUDE.md:266-267` "UNKNOWN" x2 -> **not a contradiction.** Both sit inside item
  15's verbatim quote of its own withdrawn earlier text, which the surrounding lines
  explicitly retract. Correct as written; do not edit.
