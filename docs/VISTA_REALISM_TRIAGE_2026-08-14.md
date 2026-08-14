# Vista realism_track triage, 2026-08-14

Dispatch 2 of `docs/RECONCILIATION_AND_DISPATCH_2026-08-14.md`. Produces a
merge / park / discard recommendation for each of the 12 commits on
`origin/vista-realism-track-2026-08-13`. **No merge was performed. Nothing was
pushed. `main` was not written to.**

Branch: `claude/fork-vista-triage`, worktree
`/Users/josie/can-it-ford/.claude/worktrees/fork-vista-triage`, created off `main`
at `1a868f3`.

## Method and source tagging

Every claim below is tagged:

- `[live]` re-derived this session by a command against `/Users/josie/can-it-ford`
  or against the GitHub remote. Reproduction command given where it is short.
- `[body]` quoted from a commit message. Recorded as what that session *said*,
  not as independently confirmed fact.
- `[inferred]` my reasoning from `[live]` facts. Not measured.

Nothing here is carried from a session summary, the handoff, or the dispatch
document without a live re-check. Where the dispatch document and live state
disagree, both are shown.

Vista's and LS6's filesystems were **not** touched: out of scope for this
dispatch, and no claim below needs them. Consequences are stated in
"What I did not verify".

---

## 1. Correction notice: the "one filesystem" claim is stale

**Required by this dispatch's definition of done.**

Two artifacts still assert that these 12 commits exist on a single filesystem:

1. Commit `68e4a30` (on `claude/rtfd-test-phase-1-4-569130`), body read `[live]`:
   > "Vista's /work/.../vista/can-it-ford is 12 ahead / 173 behind origin/main. The 12
   > are the realism_track series 1e4c6d5 through 4b38aa3 ... `$WORK` is not a git
   > remote and the allocation expires 2026-09-30, so they exist on one filesystem."

2. Memory file `/Users/josie/can-it-ford/.claude/memory/vista-unpushed-realism-commits.md`,
   read `[live]`, lines 17-18:
   > "`$WORK` is not a git remote and that allocation expires 2026-09-30, so those
   > commits exist on exactly one Lustre filesystem."

**Both are now false.** All 12 commits are on the GitHub remote. `[live]`, and this
is a network read of `origin`, not a read of a local tracking ref, which is the only
test that distinguishes "my clone has a stale copy" from "the remote actually has it":

```
$ git -C /Users/josie/can-it-ford ls-remote --heads origin | grep -E 'vista-realism|track2/coupled'
3e66d8a180e4a443fde0519b9aaa3e566f80c6f8	refs/heads/track2/coupled-realism-explore
4b38aa37f14fe69dad66f5e30ff5d1daa30cd7c2	refs/heads/vista-realism-track-2026-08-13
```

`4b38aa3` is the tip of the 12. `origin/track2/coupled-realism-explore` is at
`3e66d8a`. Both match the dispatch document exactly.

**Nothing is at risk from loss.** The correct present-day concern is the opposite
one: the branch is safe but unreviewed, and, as section 3 shows, 8 of its 12 commits
have already been superseded on `main` by an independent line of work that its
authors could not see.

Both artifacts are outside my declared scope (`68e4a30` belongs to Dispatch 1, the
memory file to whoever owns memory). **Neither was edited.** This section is the
notice; the correction itself is theirs to apply.

A second staleness in the same two artifacts, `[live]`: the memory file also points
readers to `docs/FLAG_VISTA_UNPUSHED_WORK_2026-08-13.md` on
`claude/rtfd-test-phase-1-4-569130` for "recommended branch-push and bundle recovery
commands". Those recovery commands are now moot for this branch. They were never
moot for `claude/rtfd-test-phase-1-4-569130` itself, which is the genuinely orphaned
branch and is Dispatch 1's subject.

---

## 2. Two findings that change what this branch is

### 2.1 The compute is LS6, not Vista. The branch name is wrong.

This matters because the reconciliation document's own Phase 1 warns that treating
the three machines as one double-counts, and because Vista-versus-LS6 routing is a
standing project rule.

`[body]`, three separate commits say so in their own words:

- `cdcdf9d`: "Vista unreachable from LS6 (MFA, keyboard-interactive denied), so the
  coupled run could not be executed here."
- `001a62c`: "Ran on LS6 A100 (jobs 3361315, 3361371), **not Vista**: Vista
  unreachable via MFA and the brief puts warpmpm SDF work on LS6 anyway. **Zero Vista
  SU spent.**"
- `a3ab0d0` adds a file literally named `.remember/ls6_session_2026-08-12.md`.

**Corroboration that is genuinely independent**, which matters because the three
sentences above are all from the same authoring session and are therefore one source
quoted three times, not three sources. `[live]` `main`'s commit `6434258`, written by
the *other* line of work, states it in its own subject: "**Rung (b) ran on LS6 A100**
and FAILED", and its body records "Job 3361315, gpu-a100-dev, node c301-004". That is
a different session, on a different branch, naming the same job id.

**A weaker argument, retained but demoted.** Every job id cited across the 12 is
7-digit in the 336xxxx range (3361315, 3361371, 3361423, 3361443, 3361504, 3362500,
3362516, 3362547) while this project's Vista job ids are 6-digit. This is suggestive
but is **not** independent: those ids come from the branch's own commits and directory
names, the same source as the quoted sentences. A job number is also a per-cluster
counter, not a machine identifier. `[live]` correcting a citation error in an earlier
draft of this section: of `866887`, `894731` and `895330`, only **`894731`** actually
appears in CLAUDE.md; the other two do not, so CLAUDE.md cannot be cited for the Vista
id range. The LS6 conclusion rests on `6434258` and on the commit bodies, not on digit
counting.

**Unresolved attribution, stated rather than guessed.** `main`'s recovery commit
`8695539` says `[body]` the artifacts "were committed on
`/work/11603/jcerrell0629/vista/can-it-ford`", which is a Vista path. That is
consistent with the compute evidence only if the git clone lived on Vista `$WORK`
while the jobs were submitted to LS6, or if `8695539`'s path attribution is
imprecise. Resolving it requires reading Vista, which is outside this dispatch's
scope. **What is not in doubt is the compute: LS6, zero Vista SU.** Do not describe
these runs as Vista runs in any figure, caption or write-up, whatever the branch is
called.

### 2.2 `main` grew an independent, parallel `realism_track` line that went further

`[live]` `main` already contains `realism_track/` with 58 files. Commits on `main`
touching `realism_track/` that are not on this branch: **10 by ancestry, of which 8
are the 08-13 00:16 to 05:50 line** shown below; the other 2 are `4513d40` and
`02f08eb`, the re-commits of this branch's own first two. Both numbers are given
because a bare count here is scope-sensitive. Interleaving the two lines by commit
timestamp:

| When (2026) | Line | Commit | Subject |
|---|---|---|---|
| 08-12 15:33 | both | `1e4c6d5` / `4513d40` | validate SDF-collider coupling path |
| 08-12 16:21 | both | `cdcdf9d` / `02f08eb` | submit-ready GH200 rung-b job |
| 08-12 17:08 to 18:32 | branch only | `001a62c` … `45be8c3` | 6 commits |
| 08-13 00:16 to 05:50 | **main only** | `6434258` … `5e0f764` | **8 commits** |
| 08-13 10:25 to 10:38 | branch only | `d59c48e` … `4b38aa3` | 4 commits |

The 08-12 15:33 and 16:21 pairs are not merely similar, they are the same change
committed twice. `[live]`, by patch-id, which compares the diff and ignores the
commit metadata:

```
1e4c6d5 6068b9cd5a5bd027    cdcdf9d bf4ba3faa9a9236f
4513d40 6068b9cd5a5bd027    02f08eb bf4ba3faa9a9236f
```

`main`'s 08-13 line then did three things that decide most of this triage:

- `8695539` (04:54) **recovered this branch's artifacts onto `main`**, in its own
  words `[body]` "the rung-b artifacts, which existed on one clone only", listing
  `rung_b_relax_3361371/`, `diag_wrench_3361423/`, `rung_b_settled_3361443/`,
  `pressure_probe_3361504/` and their drivers. It deliberately did **not** touch
  `FINDINGS.md`: "Both clones edited it independently (423 insertions, 314 deletions
  apart) and taking either side wholesale would silently revert the other's
  corrections."
- `b62d554` (05:23) then did that `FINDINGS.md` merge: `[body]` "Genuine three-way
  merge, 496 insertions and 0 deletions, so nothing either side wrote was lost, plus
  a RECONCILIATION SEAM section."
- `be20075` (01:11) independently **re-derived this branch's numbers** rather than
  trusting them: `[body]` "Provenance note on the numbers 3,894 and 12,416: these
  appear in another session's commit `20e2063`. They were not taken on trust. Both
  reproduce exactly from the committed artifacts."

`[live]` verification that the recovery and the merge really landed, per path. Of the
45 paths the 12 commits touch, measured with `git ls-tree` against each ref (an
earlier `git rev-parse ref:path` version of this check silently mis-reported absent
paths and its numbers are withdrawn):

| Status on `main` | Count |
|---|---|
| byte-identical blob already on `main` | **32** |
| absent from `main` | **11** |
| present but different | **2** |

The 2 that differ are `realism_track/FINDINGS.md` and
`simulation/validate_coupling_force.py`. Of the 11 absent, 2 are `.remember/` files
(`.remember/` is not tracked on `main` at all, `[live]` 0 files) and **9 are the
final four commits' artifacts**.

`[live]` `main`'s `FINDINGS.md` carries this branch's prose through `45be8c3`
(08-12 18:32) and none of the final four. Distinctive-string counts, `main` vs branch:
`0.459` 1/2, `6,266` 1/2, `particle_F_trial` 3/3, `3,894` 8/5, `12,416` 6/3,
`RECONCILIATION SEAM` 1/0; then `3362500` **0**/4, `2.1813` **0**/1,
`leaked_cumulative` **0**/2, `h_eff` **0**/2, `5,838` **0**/1.

**So the split is clean: commits 1-8 are already on `main` in substance; commits
9-12 exist nowhere else.**

---

## 3. Per-commit recommendation

Classes are the four the dispatch asked for. "Discard" here means *discard the
commit object*, because its content is already on `main`; it never means discard the
finding.

| # | Commit | Time (08-12/13) | Class | Recommendation |
|---|---|---|---|---|
| 1 | `1e4c6d5` | 12 15:33 | already-superseded-on-main | **Discard.** Exact duplicate of `4513d40` |
| 2 | `cdcdf9d` | 12 16:21 | already-superseded-on-main | **Discard.** Exact duplicate of `02f08eb` |
| 3 | `001a62c` | 12 17:08 | already-superseded-on-main | **Discard.** Artifacts on `main`; its causal claim was retracted twice |
| 4 | `868302e` | 12 17:39 | **do not merge** | **Discard, actively.** Would revert two landed fixes |
| 5 | `20e2063` | 12 17:52 | **retraction (1 of 2)** | **Discard.** Retraction already recorded on `main` |
| 6 | `a3ab0d0` | 12 17:56 | merge-candidate, narrow | **Extract one item.** The BULK trap is on no other ref |
| 7 | `0d81f2f` | 12 18:24 | already-superseded-on-main | **Discard.** Contains a third, minor retraction |
| 8 | `45be8c3` | 12 18:32 | **retraction (2 of 2)** | **Discard.** Both retractions already on `main` |
| 9 | `d59c48e` | 13 10:25 | **merge-candidate, high value** | **Merge**, after the section 4 adjudication |
| 10 | `c74ac23` | 13 10:31 | **merge-candidate, high value** | **Merge**, after the section 4 adjudication |
| 11 | `a6b66b6` | 13 10:36 | **merge-candidate, high value** | **Merge.** Figures verified reproducible; also extract its g96 non-reproducibility finding |
| 12 | `4b38aa3` | 13 10:38 | **exploratory-park** | **Park.** Rewrites a verdict `main` has independently rewritten |

### The two explicit retractions

`68e4a30` says `[body]` the 12 cover "an SDF-collider coupling validation, a
pressure-deficit diagnosis, and **two explicit retractions**". It does not name
them. `[live]` by subject line, exactly two of the 12 announce a retraction, and
they are:

**Retraction 1, `20e2063`, "wrench diagnostic retracts the pose-loop hypothesis".**
It retracts `001a62c`'s attribution, four commits earlier, of the rung-b force error
to the pose-update loop: `001a62c` had said `[body]` the g96 behaviour indicated "a
bug in the pose-update loop rather than discretisation error". `20e2063` refutes it
with a held-still control: `[body]` the fixed mode read -48.49% at g64 and +349.55%
at g96 "with the body held completely still, so the pose-update loop is not the
primary defect", and it states "the prior section's attribution of the gap to
collider motion is superseded". `[live]` `main` reached the same retraction
independently in `d98837f` ("Retract the added-mass cause: an experiment I had not
run refutes it"), citing the same job 3361423.

**Retraction 2, `45be8c3`, "deficit is a constant pressure offset; two claims
retracted".** The two claims are both its own line's:
(a) the surface-layer model from `0d81f2f`, `[body]` "REFUTES my surface-layer model
... a 54% change where the model required constancy", and it further notes the
apparently-successful pre-registered prediction "was coincidental: a force-inferred
aggregate matched a mean while the profile was wrong";
(b) `a3ab0d0`'s lead, `[body]` "RETRACTS 'hydrostatic seeding requires no engine
change'", because `mpm_utils.py:1086-1089` rebuilds `particle_F` from
`particle_F_trial` every stress evaluation and no importer exists for the latter.

A third retraction exists but is not one of the two: `0d81f2f` `[body]` "Retracts my
claim that the reference uses `box_bottom_cells=8.0` ... I took `run_c1_sdf`'s
signature default." That one is worth carrying forward on its own, because it means
job 3361443 ran at 75-84% submersion and its fixed arm is not the intended control.
`[live]` `main` carries this: `0.459` and `6,266` are present in `main`'s
`FINDINGS.md`.

### Commit 4, `868302e`, is the one active hazard

Its subject is "commit `validate_coupling_force.py`, untracked since first use". That
premise is **true of the clone it was written on and false of `origin/main`.**
`[live]` `main` has tracked the file since 2026-08-07 (`541d832` added it, `057b3e9`
landed the C1-SDF/C3 harness content), which is also what CLAUDE.md's own closed-items
section records.

`[live]` the two versions:

| | lines | sha256 (first 24) | `CV2` | `a_expected_compressible` |
|---|---|---|---|---|
| branch (`e017d71`) | 1075 | `2e437a293e2cfd17fc78b96a` | **0** | 1 |
| `main` (`5e7bc79`) | 904 | `70f54e33f228cfdd24b5a575` | 1 | 2 |

The branch copy is a **different lineage**, an untracked working copy that evolved
separately on another clone, not simply an older revision. `[live]` it lacks the
`CV2` rename (`3b3f5d9`, "Rename coupling-validation C2 to CV2 to clear a
two-namespace collision") and one of the two `a_expected_compressible` usages
(`e7a1fd6`, the C3 estimator fix). `[inferred]` taking the branch side of this file
in a merge would revert both.

One half of that commit's provenance claim verifies and one half does not. Stated
separately, because an earlier draft of this document merged them under a single
`[live]` tag, which was a false provenance tag:

- **Verified `[live]`:** the branch blob's sha256 is
  `2e437a293e2cfd17fc78b96ace03881...`, exactly the value the commit body claims.
- **NOT verified, `[body]` only, and unverifiable from this checkout:** that this
  value is "the sha256 recorded in all 29 `coupling_validation` manifests".
  `[live]` `/usr/bin/grep -rl '2e437a293e2cfd17' data/` returns **0 hits**, and only
  **1** `coupling_validation*` directory is present locally, not 29. The manifests may
  exist on the LS6 clone; they are not here. **Do not restate the 29-manifest claim as
  confirmed.**

And the pin is weaker than "sound" even on the branch's own account. `868302e` says so
itself `[body]`: the hash was taken at backfill time on 2026-08-12, the manifests
record `tracked_in_git: false`, and it "does not retroactively prove the file was
identical during the 2026-08-07 runs; that caveat in the manifests still stands."
Preserve the sha256 and that caveat together, never the sha256 alone. Discard the
commit.

### Commit 6, `a3ab0d0`, has one item that exists on no other ref

`[live]` its `FINDINGS.md` prose largely reached `main` via `b62d554` (`1.9939e9`
appears 3 times on both). But the **BULK default-argument trap does not**: `[live]`
`__defaults__` = 0 on `main` and 0 on the branch's `FINDINGS.md`, `13293` = 0 on
both, so the trap as `a3ab0d0` states it in its commit body survives only in the
commit message.

The trap, `[body]`, and it is a live code hazard rather than a result:

> "`sound_speed()` and `substeps_and_dt()` take `bulk` as a default argument bound at
> def time and `BoxTank` calls both bare, while `set_material` reads the module
> global. Reassigning `BULK` would stiffen the fluid while leaving `dt` and the settle
> gate on the old 12.845 m/s, under-resolving ~110x and passing the gate far too
> early."

`[live]` this is not hypothetical: `d59c48e`'s own `surface_and_leak.py` was written
to defend against exactly it, `[body]` "It patches bulk through both the module
global and the `__defaults__` of `sound_speed`/`substeps_and_dt`, then aborts unless
`tank.sound_speed` matches." **Recommendation: lift this paragraph into the code as a
comment or into `FINDINGS.md`, and drop the commit.** It is the one thing in commits
1-8 that would be lost by discarding them.

### Two further extraction candidates, from commits 10 and 11

Both were missed in an earlier draft of this document. Neither is a reason to change a
merge recommendation, and both should survive whatever happens to the commits.

**A settle gate whose threshold moves with the thing it gates**, from `c74ac23`
`[body]`: "the settle gate `c/vmax >= 20` has a threshold that scales with c, so it
gets easier as the fluid stiffens. Frames used fall 354 to 62 to 20, with D stopping
at exactly `settle_min_frames`. C and D are therefore less settled in absolute terms
and their force numbers are unusable; they are quoted for the leak trend only. A bulk
sweep needs an absolute criterion." `[live]` confirmed in the artifacts: C and D report
`settle_gate_met` **True** at 62 and 20 frames against A's 353. This matters beyond
this branch because the gate is shared with `main`'s runs, and it is a second instance
of the pattern register item 6 already names, a check that cannot fail.

**A g96 settle that does not reproduce**, from `a6b66b6` `[body]`: on a
byte-identical configuration the canonical run and the probe met the gate at 776 and
777 frames with vmax 0.6341 and 0.6232, while run E ran the full 900 and ended at
1.5132. Attributed there to warp's order-nondeterministic P2G atomics with vmax as an
extreme-value statistic over 1.5M particles. **This collides with `main`'s
explanation of the same symptom.** `main`'s `b62d554` attributes the g96 discards to a
**cap artifact** ("900 was about 13 percent short", gate met at 1030 once the cap rose
to 3000). Both cannot be the whole story, and the two accounts have never been put
side by side. Worth recording as an open item wherever the register lands it.

### Commits 9-12, the only genuinely new content

`[live]` all 9 of their artifact files are absent from `main`, and `main`'s
`FINDINGS.md` contains none of their strings.

`[live]` and this is checked against **every** ref rather than against `main` alone,
because "absent from `main`" would not rule out a copy parked on some other branch.
`git branch -a --contains` returns exactly one ref for each of `d59c48e`, `c74ac23`,
`a6b66b6` and `4b38aa3`, namely `remotes/origin/vista-realism-track-2026-08-13`, and
sweeping every local and remote ref for the distinctive artifact directory
`realism_track/surface_leak_3362500/` finds it on that branch only. **These four
commits and their evidence exist on one branch and nowhere else in the repository.**

I verified their headline numbers **against the committed JSON artifacts rather than
the commit prose**, which is the check the project's own rules ask for. All of the
following are `[live]`:

`c74ac23` claims correcting the free surface moves bbc 8.0 from -49.88% to +2.98% and
bbc 3.0 from -9.32% to +2.85%, "two very different geometries agreeing to 0.13
points". From the artifacts:

| Run | `settle_gate_met` | `err_vs_reported_pct` | `err_vs_half_density_pct` | `frac_below_floor` | `pile_excess_frac` |
|---|---|---|---|---|---|
| A, g64, bbc 8.0 | True | **-49.8787** | **+2.9823** | 0.18077 | 0.21838 |
| B, g64, bbc 3.0 | True | **-9.3180** | **+2.8483** | 0.18161 | 0.21344 |

Reproduces exactly, and 2.9823 - 2.8483 = 0.134 points. The leak-intervention trend
also reproduces: `leaked_per_substep` 2541.2 (A) to 397.0 (C) to 13.1 (D),
`pile_excess_frac` 0.2184 to 0.0172 to 0.0041, `surface_gap_m` 0.5698 to 0.0939 to
0.0544, monotone on three points as claimed.

`a6b66b6` calls run E a discard. Confirmed from `E_full_g96.json`:
`settle_gate_met` **False**, `settle_frames_run` 900, `settle_vmax_final`
**1.5131868**. The gate is `sound_speed/vmax >= 20`, and the artifact records its own
achieved ratio, `diagnostics_after_settle/sound_speed_over_vmax` = **8.488861**, so E
finished at 20/8.488861 = **2.36x** the permitted vmax. Deriving it from that field
avoids taking the sound speed from commit prose; as a cross-check the prose value
c = 12.8452 reproduces the field exactly (12.8452 / 1.5131868 = 8.4889), which also
confirms that c is the g96 value and not a g64 one carried across. Its own
`surface_gap_m` is 0.5994 and `surface_gap_Pa` 5880.4.

**A provenance gap I asserted in an earlier draft is RETRACTED.** That draft said the
`+1.00%` and `+1.28%` mass-based-head figures "cannot currently be regenerated from
the repository", because `surface_and_leak.py` contains no `h_eff`, `mass_based` or
`linear_particle_density` symbol and `a6b66b6` adds no script. Both of those
observations are true `[live]` and **the conclusion drawn from them was wrong.**
Absence of a symbol is not absence of the inputs.

`[live]` the artifacts store the full free-surface histogram, `hist_z` and
`hist_count`, 183 bins each, alongside `bulk_density_particles_per_m`. That is
everything `a6b66b6`'s definition needs. I regenerated all three published rows from
committed fields only, taking `z_b0 = z_half_density - h_sub_half_density_m` and
`rho*g*A = F_partial_half_density_N / h_sub_half_density_m`, then
`h_eff = (sum of hist_count above z_b0) / bulk_density_particles_per_m`:

| Run | `z_b0` | n above | `h_eff` | analytic | measured | error | gate |
|---|---|---|---|---|---|---|---|
| A, g64, bbc 8.0 | 1.6194 | 99,898 | 0.5509 m | 11,712 N | 11,829 N | **+1.00%** | met |
| B, g64, bbc 3.0 | 0.8833 | 249,944 | 1.3181 m | 28,023 N | 28,382 N | **+1.28%** | met |
| E, g96, bbc 3.0 | 0.8833 | 906,074 | 1.3978 m | 29,719 N | 32,948 N | **+10.87%** | **NOT met** |

Identical to `FINDINGS.md:990-992` in every column. **The figures are reproducible from
the committed artifacts**, and commit 11's recommendation is a plain merge, not a
merge-with-caveat. Committing the six-line recomputation would still be worth doing so
the next reader does not have to re-derive `z_b0`, but that is tidiness, not a
blocker.

**The regenerated g96 row is the most decision-relevant number in this document and
the branch never puts it in a headline.** Post-correction, the same fixed collider
reads `+1.28%` at g64 and `+10.87%` at g96, a **9.59-point** grid gap. See section 4.

`4b38aa3` is parked rather than merged for a structural reason, not a physics one:
`[live]` it rewrites `FINDINGS.md`'s top-line verdict block, and `main` independently
rewrote the same document's narrative in `b62d554`, `8590313` and `5e0f764` and
recorded the result in register items J1b, J1d and J1e. Merging a verdict rewrite
written without sight of those is how a reviewed correction gets silently reverted.
Merge 9-11 first, adjudicate section 4, then write one verdict block deliberately.

---

## 4. FLAG, operating-protocol item 2: two results that genuinely disagree

**This is flagged, not resolved. Resolving it is a judgment call and needs data I
cannot get within this dispatch's scope.**

Engine tag: **warpmpm throughout this section.** No Genesis result appears here.

**Scope correction, and it is essential.** An earlier draft of this section said the
two lines disagree about "the same physical quantity". That was too broad, and it
committed the exact merge-two-different-things error that constraint 1 below forbids.
`[live]` `realism_track/surface_and_leak.py:92` hardcodes
`box_mode="collider_sdf"` with no CLI override, so **every branch run, A through E, is
a fixed SDF collider.** The branch has zero free-rigid coupled-path measurements.
`main`'s load-bearing claim in `8590313` is about the coupled path
("THE FREE-RIGID FORCE-COUPLED PATH IS GRID-CONVERGED"), taken from rows with
`"mode": "coupled"`.

So the genuine overlap is narrower and must be stated as one row, not as a whole
result: **the g64 fixed-collider partial-submersion error.** `main`'s `b62d554`
records that row as **-49.92%**; the branch's run A re-measures the same
configuration at **-49.8787%** `[live]`, which is the same row to four significant
figures, and then re-scores it to **+2.98%** (half-density surface) or **+1.00%**
(mass-based head). That is a real disagreement about one shared quantity. Everything
`main` says about the *coupled* path is untouched by this branch, because the branch
never measured it.

**`main`'s position**, `[body]` from `8590313` and `b62d554`: the deficit is real and
grid-converged. Coupled path about -25% at frac 0.78 rising to about -30% at frac
0.86, agreeing between g64 and g96 to 0.10 and 1.51 points; the fixed SDF collider is
*not* grid-converged, off by 13.25 and 19.07 points. `8590313` states the limit of
its own claim: "WHAT THIS DOES NOT SAY: that the coupled path is correct ... the
deficit is GRID-CONVERGED and therefore not a resolution artifact, so a finer grid
will not remove it."

**The branch's position**, `[body]` from `d59c48e` and `c74ac23`, `[live]` verified
against its artifacts above: the deficit is largely a **reference** artifact. The tank
leaks, the rescue clamp piles about 18% of water below the floor plane and about 21%
against it, `column_surface` sums particle volume per column and so reports the
height water *would* have if distributed normally, the reported free surface is
therefore about 0.57 to 0.60 m too high, and `f_partial` takes `h_sub` from it. Correct
the surface and the same runs land within about 3% (artifact field) or about 1%
(prose recomputation) of analytic.

**Why this is a real collision and not two framings.** `main`'s `b62d554` explicitly
left open the exact quantity the branch then explains: `[body]` "The deficits as
pressure over the 2.1662 m2 section are 2747, 5444, 3613 and 3967 Pa, not a
resolution-independent constant, and **none is the ~6.2 kPa job 3361504's direct
profile reports. That is open.**" The branch's `d59c48e` answers it: `[body]` the
inferred surface error is 0.5951 m at g64 and 0.5854 m at g96, "which is 5,838 and
5,743 Pa of head against measured pressure offsets of 6,121 and 6,266 Pa". If that
attribution holds, `main`'s -25%/-30% is measured against an inflated reference and is
not a physical deficit.

**The evidence does not leave this fully open, and an earlier draft of this document
hedged where it should not have.** Two things can be said now.

**First, the correction may overshoot rather than dissolve the deficit.** `d59c48e`'s
own next sentence, which the earlier draft quoted around, is `[body]`: "Correcting it
moves the g64 gate-met fixed run from **-49.92% to +7.83%**." A deficit that crosses
zero to a surplus is not a deficit that has been explained away, it is a reference that
has been over-corrected, under-corrected, or both at different submersions. The branch
itself then produces three different corrected values for the same family of runs
(+7.83%, +2.98%, +1.00%) as its surface estimator improves, which is consistent with
the estimator, not the physics, doing the moving.

**Second, and this is the strongest single piece of evidence in either direction,
`main`'s "the fixed SDF collider is not grid-converged" appears to SURVIVE the
correction.** `[live]` from my own regeneration in section 3: post-correction the fixed
collider reads **+1.28% at g64 and +10.87% at g96, a 9.59-point gap**, which is the
same order as the 13.25 and 19.07 points `8590313` reports for the fixed collider
pre-correction. The correction therefore does not remove the fixed collider's
grid-dependence; it shifts both grids and leaves a comparable spread.

**The caveat that stops this being decisive**, stated because it is load-bearing:
`[live]` the g96 run E is `settle_gate_met` **false**, so by the branch's own rule it
is a discard, and `a6b66b6` says so. A 9.59-point gap resting on one gate-failed point
is an indication, not a result. It is still more evidence than the earlier draft's
"has to be recomputed" implied, and it points toward `main`.

**What would actually settle it, and what it costs.** Re-score `main`'s ten gate-met
matched-submersion points against a directly measured surface and see whether the
0.10/1.51 coupled gaps and the 13.25/19.07 fixed gaps survive. **This is NOT free, and
an earlier draft of this document was wrong to say it costs no SU.** `[live]` the
instrument reads live particle positions (`surface_and_leak.py:25`,
`z = tank.solver.x()[:n_w, 2]`), and **none of `main`'s `realism_track` artifacts
stores them**: 0 hits for `hist_z`, `hist_count`, `z_half_density` and
`n_below_floor`, and 0 `.npz` files. Re-scoring `main`'s points therefore requires
re-running the settle on GPU. Route it to LS6 as batch.

What *is* free is the branch's own side: `[live]` its artifacts do commit the
histogram, which is how section 3's regeneration was possible without any compute. So
the asymmetry to plan around is that the branch's runs are fully re-analysable today
and `main`'s are not.

`[live]` the same script also defends against `a3ab0d0`'s BULK trap in code, which is
independent evidence that the trap is real: `:19-20` patch
`sound_speed.__defaults__` and `substeps_and_dt.__defaults__`, and `:94-95`
`sys.exit("BULK PATCH FAILED: ...")` unless `tank.sound_speed` matches the expected
value.

**A second, larger consequence, stated because it must not be buried.** `c74ac23`
says `[body]` "The reference case is **NOT** fully submerged. Measured surface 2.1813
sits below the box top at 2.3554, about 88% submerged." `run_c1_sdf` at `frac 1.0` is
the source of the project's canonical **7.3 to 7.7%** buoyancy figure, and `frac` is
computed from the same `column_surface` this branch says is inflated. `a6b66b6` adds
`[body]` that the 7.3-7.7% figure is "taken from one run per resolution, needs repeats
and an error bar".

An earlier draft said "I have not tested this". That was an unnecessary hedge: the test
is two subtractions on data already in hand, and `[live]` **it fails on both grids**,
where `box_top_z = 2.3554356` per `FINDINGS.md:569`:

| Run | reported surface | measured surface | box top | fully submerged? |
|---|---|---|---|---|
| B, g64 | 2.7606 | **2.1813** | 2.3554 | **No**, 0.174 m short |
| E, g96 | 2.8759 | **2.2765** | 2.3554 | **No**, 0.079 m short |

Both artifacts nonetheless carry `fully_submerged_by_reported_surface = True`, which is
the defect in one line: the flag and the measurement disagree, and the flag is what the
`frac` premise rests on.

**Two limits on how far that carries.** These are the branch's *reproduction* of the
reference geometry, not the canonical `run_c1_sdf` artifacts themselves, so this is
evidence about the premise and not a direct measurement of the canonical run. And E is
gate-failed. **So: the frac 1.0 premise is now doubtful on reproduced runs at both
grids, which is a stronger statement than "untested" and a weaker one than "the
canonical figure is wrong".** Adjudicating it is Dispatch 4's, on the register.

Three constraints on anyone who picks this up, carried from the dispatch and
preserved verbatim in force:

1. The three buoyancy numbers are for three different things and must never be
   merged: **7.3 to 7.7%** (warpmpm, SDF collider, canonical), **+0.035%** (which is
   *not* a buoyancy figure at all, it is a residual-acceleration identity, commit
   `d8a479f`), and **-105.8% / -39.9%** (Genesis `LegacyCoupler`, which are
   **failures**). The Genesis document's own framing is to be preserved exactly: no
   "X% agreement with analytic buoyancy" claim is made for Genesis, and the -39.9% is
   "an artifact of fitting an acceleration to a decelerating descent".
2. Register J1a records the 7.3-7.7% figures as coming from `run_c1_sdf` at frac 1.0,
   and the deliberate choice to run fraction 1.000 was made to avoid scoring a
   partially submerged case against a fully submerged reference. **Do not "correct"
   that choice.** The finding above is not that the choice was wrong; it is that the
   instrument used to *verify* the choice was met may be misreading. Those are
   different problems and the second does not license undoing the first.
3. The corrections register is Dispatch 4's scope and was **not** edited here. If
   this is adjudicated, register items J1b and J1d are the entries that change.

---

## 5. Merge mechanics, if commits 9-11 are taken

`[live]` dry-run with `git merge-tree --write-tree --name-only main
origin/vista-realism-track-2026-08-13`, which is read-only with respect to refs and
the working tree:

```
CONFLICT (add/add): Merge conflict in realism_track/FINDINGS.md
CONFLICT (add/add): Merge conflict in simulation/validate_coupling_force.py
```

**Exactly two conflicts, and both are add/add** because `[live]` the merge-base
`b00bf7b` (2026-07-25, 174 commits behind current `main`) contains neither path: both
files were created independently on the two lines. Everything else auto-merges: 32
paths are already byte-identical and 11 are clean additions.

Resolution guidance, `[inferred]` from the evidence above:

- `simulation/validate_coupling_force.py`: **resolve by hand, keeping `main`'s `CV2`
  rename and C3 estimator fix.** An earlier draft said "take `main`'s side wholesale".
  That is **wrong**, and it is contradicted by `main`'s own commit `79fec32:12`
  `[live]`: "divergence is BIDIRECTIONAL, so no wholesale copy is safe." `[live]` the
  numbers: going branch to `main` the diff is 7 insertions and 178 deletions, so 178
  lines exist only on the branch and 7 only on `main`.

  `[live]` at the API level the branch-only surface is small and specific: two items,
  `def run_c1b(n_grid, rho_box=600.0, depth_cells=18.0, submersion_frac=0.80, ...)` and
  `--submersion-frac`. `main` has **zero** functions or CLI arguments the branch lacks.
  Note also, against a claim made during review, that `run_c1b` is **not** missing from
  `main`: `[live]` it is present in both `main:simulation/validate_coupling_force.py`
  and `main:simulation/coupling_force/rung_b_coupled.py`, with a different signature.
  So the branch's 178 lines are largely a *different revision* of shared functionality,
  not functionality absent from `main`.

  Judgement `[inferred]`: `main` reaches the same capability by another route, varying
  submersion with `--depth-cells` at fixed grid (`8590313`), so `--submersion-frac` is
  probably redundant rather than a loss. Confirm that before dropping it.
- `realism_track/FINDINGS.md`: **do not take either side wholesale**, which is
  `8695539`'s own recorded warning and is what `b62d554` had to do by hand once
  already. `main`'s copy is 1355 lines and has the RECONCILIATION SEAM section; the
  branch's is 1031 lines. The content unique to the branch is the final four commits'
  sections only, since `[live]` everything through `45be8c3` is already merged in.
- A cheaper alternative that avoids the `FINDINGS.md` conflict entirely: cherry-pick
  only the **8** artifact and script files from commits 9-11, which are pure additions
  touching no existing path, exactly the shape `8695539` used successfully. `[live]`
  the count is 8, not the 9 an earlier draft gave: `run_surface_leak.sbatch`,
  `run_surface_leak_g96.sbatch`, `surface_and_leak.py`, the four
  `surface_leak_3362500/*.json`, and `surface_leak_g96_3362516/E_full_g96.json`. The
  ninth file in the "absent from `main`" set,
  `realism_track/run_surface_leak_repeat.sbatch`, belongs to commit **12**, which this
  document recommends parking, so taking it would quietly import part of the parked
  commit. Then write the `FINDINGS.md` section once, deliberately, after section 4 is
  adjudicated.

---

## 6. What I did not verify

Stated so no reader mistakes an unchecked item for a checked one.

- **Vista's and LS6's live filesystem state.** Out of scope. The dispatch's claims
  that Vista's clone is "1 ahead / 5 behind" and that `1e4c6d5`/`4b38aa3` "no longer
  resolve there" are **carried, not verified**. They do not affect any conclusion
  here: section 1's correction rests entirely on `git ls-remote` against GitHub.
- **Whether `main`'s coupled-path -25%/-30% survives the surface correction.**
  Section 4. Not computed, and **not computable without new GPU time**, because
  `main`'s artifacts do not store particle z. The fixed-collider half of the question
  now has partial evidence (the 9.59-point post-correction gap), which points toward
  `main`, but rests on one gate-failed run.
- **Whether the canonical `run_c1_sdf` runs themselves are fully submerged.** Section 4
  shows the branch's *reproductions* are not, at both grids. I did not open the
  canonical `data/coupling_validation/c1sdf_sdf_g{64,96}.json` artifacts to test the
  same thing on the runs that actually produced the 7.3-7.7% figure. That is the next
  cheap step for whoever adjudicates it, and it needs no compute.
- **The 29-manifest sha256 claim in `868302e`.** `[live]` 0 hits under `data/` and only
  1 `coupling_validation*` directory present locally. Unverifiable from this checkout;
  marked `[body]` in section 3, not `[live]`.
- **`physics-skeptic` review: RUN, and it changed this document.** See the review
  record below.
- The 12 commits' content was read at commit-body and artifact level. I did not read
  all 1031 lines of the branch's `FINDINGS.md` or all 1355 of `main`'s; the
  comparisons in section 2.2 are string-presence counts, which establish presence and
  absence but not that a shared passage says the same thing.

---

## 7. Summary

- **Correction issued** (section 1): the "one filesystem" claim in `68e4a30` and in
  `vista-unpushed-realism-commits.md` is stale. All 12 commits are on GitHub. Neither
  artifact was edited; both are outside this scope.
- **8 of 12 commits are already on `main` in substance** and should be discarded as
  commits. One of those, `868302e`, should be discarded *actively*: merging it would
  revert two landed fixes.
- **1 item should be extracted** rather than merged or dropped: `a3ab0d0`'s BULK
  default-argument trap, which survives on no other ref.
- **3 commits are genuine merge candidates** (`d59c48e`, `c74ac23`, `a6b66b6`), their
  headline numbers reproduce from their own artifacts, and 1 should be parked
  (`4b38aa3`).
- **1 flag raised** (section 4): the branch's final four commits answer a question
  `main` explicitly left open. The overlap is **one row**, the g64 fixed collider, not
  a whole result, because the branch measured only the fixed SDF collider and never the
  coupled path. On the evidence now in hand `main`'s grid-convergence finding appears to
  **survive** the correction. Not adjudicated here.

No merge was performed. Nothing was pushed. `main`, the corrections register,
`claude/rtfd-test-phase-1-4-569130`, Vista and every credential file were untouched.

---

## 8. Review record

`physics-skeptic` reviewed this document adversarially and **found five errors that
inverted its own recommendations.** All five were then re-verified independently
against the repository before being accepted, and all five are corrected above:

1. **§4 compared two different coupling paths.** The branch is fixed-SDF-collider only
   (`surface_and_leak.py:92`); `main`'s headline is the coupled path. Corrected, and
   the overlap narrowed to the single g64 fixed row.
2. **§4's "costs no SU" was wrong.** `main` stores no particle z, so re-scoring its
   points needs a GPU run. Corrected.
3. **§3's provenance gap on `+1.00%`/`+1.28%` was refuted.** The histogram is
   committed; I regenerated all three rows exactly. The claim is retracted in place and
   commit 11 upgraded to a plain merge.
4. **§4 hedged where evidence existed**, omitting a sign flip and a 9.59-point
   post-correction grid gap that favour `main`. Corrected.
5. **§5's two resolution instructions were both wrong**: 8 files not 9, and "take
   `main`'s side wholesale" is contradicted by `79fec32:12`. Both corrected.

Also corrected from the same review: a false `[live]` tag on the 29-manifest sha256
claim, an overstated "provenance pin is sound", a non-independent job-id argument with
a wrong CLAUDE.md citation, a scope-free commit count, and two missed extraction
candidates.

**One review finding was checked and NOT adopted.** The review stated that `run_c1b`
exists only on the branch. `[live]` it is present on `main` in two files; the real
difference is its signature and the `--submersion-frac` argument. Section 5 records
the corrected version.

The review's own scope limit, carried here because it bounds finding 3 above: it
searched tracked `main`, the branch, and the on-disk working tree, but not `.git/`,
`third_party/`, or any other machine.
