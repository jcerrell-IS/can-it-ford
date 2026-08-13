# Reconciling the friction flip with the resolution flip

**Date** 2026-08-13. **Branch** `claude/friction-resolution-reconcile-84465d`, off `main` at
`1a868f3`. **Merged in** `warpmpm-continue` at `66912e3`, all five commits, by hand.
**`main` is not modified.** The merge is left for Josie to fast-forward.

**Scope note, stated because this file is not in the dispatch's write list.** The dispatch
enumerated the files this round may write and required a write-up carrying the check output
and the SLIDE paragraph. A new document is the only way to satisfy both, so this file was
created rather than folding the material into a listed file. It touches nothing else. If
that was not intended, delete it; register `A6b` cites it for a reproduction recipe and
would need repointing.

---

## 1. One-line answer

The two flips are **different mechanisms breaking different clauses of the same criterion**,
they are **separately sufficient but not shown independent**, and the "both at g96"
coincidence is a **label**, not a shared configuration: the three bodies involved run at
three different `dx`. Full entry is register **D9**.

Two things were found on the way that were not the assignment and matter more than the
merge:

- **`main` shipped a two-line comment growth in `simulation/failure_modes.py` that silently
  repointed 33 line citations across 18 files.** Register `A6b`. Fixed in this merge.
- **Register `D8b`'s headline is refuted for the copy that actually ran the 17 gated runs.**
  It read a later revision of `sim_standing.py`. Register `D8c`. The correction the dispatch
  asked me to make to CLAUDE.md item 3 would have introduced the error it was meant to
  remove, so **it was not made**; see section 4.

---

## 2. Reproducing the counts in this document

Every count below is scope-sensitive, so each is given with its scope and a command. The
shell `grep` in this environment is a ugrep wrapper that skips gitignored paths (CLAUDE.md
H0), so all of these use `git grep` against a ref or `/usr/bin/grep`.

**The 33 repointed citations.** Scope: tracked content of ref `main`; `third_party/`
excluded; strict token match rejecting `classify_failure_modes.py:N` and
`failure_modes_by_run*` substrings.

```bash
git -C /Users/josie/can-it-ford grep -nE 'failure_modes\.py:[0-9]' main -- . | /usr/bin/grep -v '^main:third_party/'
```

That yields **51 citation instances across 22 files**. **18** cite `:14`, where `G` lives in
both forms, and are geometry-independent. **33 across 18 files** cite a line above `:14`;
those are the ones the growth moved. Of the 33, **28 in 14 files are stale and are restored**
by reverting to one line, and **5 in 4 files were authored after the growth and break**; they
are listed in section 5. **"All 33 were broken" would be false** and an earlier draft of
register `A6b` implied it; a count of citations that moved is not a count of citations that
are wrong.

**The 51 undercounts, and the scope must say so.** Bare continuation references carry no
filename token and are not matched: `analysis/classify_rogue_silverado_sweep.py:25-26` has
`", :211"` and `", :176"`, both genuine citations of this file and both correct post-shift.
Counting continuations gives **53**, which coincidentally equals a naive unfiltered match
while being composed differently. Any published total must state whether continuations are
in scope.

**The stale `sim_standing.py:132` sites.** Scope: tracked content of the merged tree.

```bash
git -C <merge-worktree> grep -nE 'sim_standing\.py:13[23]' -- .
```

**24 tracked sites: 14 prose-or-code and 10 stamped run artifacts** under
`realism_track/ladder_gated_geometry_3362208/`. The artifacts are not retro-edited. Note
this pattern **misses the bare form** `(:132-137)` used in CLAUDE.md item 3, which carries
no `sim_standing.py:` prefix; that site was found by reading, not by the pattern. A citation
form that a search cannot find is worse than one that is wrong.

**Correction to my own working note.** An intermediate scan in this session reported "22
declaration sites absent from the worktree". That was a bug in the scan, not a fact: it
pruned any directory path containing `/.claude/worktrees`, which is every directory inside
the worktree, so the worktree side came back empty and every file looked missing. The true
figure is **7 files**. Recorded because the number appeared in a tool run before it was
checked.

---

## 3. What the merge actually had to reconcile

`main` moved 103 files since the merge base `4435010`; the branch moved 12. Three files
conflicted.

| file | resolution | why |
|---|---|---|
| `simulation/failure_modes.py` | **one physical line**, carrying `main`'s full comment text | restores 327-line geometry; see section 4 |
| `scripts/check_claims.py` C10c | **took `main`'s** | `main` deliberately stopped hardcoding the volatile ratio tally (`05a5b84`); the branch re-added `12`, which is the defect `main` had just fixed |
| `scripts/check_claims.py` C6 | **took the branch's** (auto-merged, no conflict) | only the branch had the dead-code finding for `viability_dashboard_scaffold.py:11` |
| register `A6` / `A6a` | **merged by hand**, both sides' unique content kept | see below |
| register `D6c` | **`main`'s frame** plus the branch's G-free observation | `main`'s wording avoids quoting the volatile tally at all |

**Both branches performed the same G unification independently, and the outputs agree byte
for byte.** `e495b56` on `main` and `6ea4329` on the branch both set `G = 9.81` and
regenerated the stores. Verified by `git rev-parse`: `data/failure_modes_by_run.json` and
`data/failure_modes_by_run_classified.csv` are the **same blob** on both refs, so the merge
had nothing to reconcile in either store. That is an unplanned independent replication of
the regeneration. It is **not** independent confirmation of the verdicts: both runs read the
same 17 `metrics.csv`.

**Carried verbatim, no content decision made:** `analysis/run_provenance.py` (blob
`06b97a7`, absent from `main`, added by `6d6544f`). DP-3 owns reconciling its copies. The
only other copy in git is on `claude/warpmpm-gravity-provenance-435363`, which points at the
same commit, so the two copies are the same blob and this merge does not pre-empt anything.

### 3.1 A sixth commit arrived mid-merge and was deliberately excluded

**`warpmpm-continue` moved while this work was in progress.** `git log main..warpmpm-continue`
at the start of the session returned exactly the five commits the dispatch names, ending at
`66912e3`. At **17:36:47** another live session committed **`4924940`**, "Harden the
provenance backfill: atomic, idempotent, and correctly scoped", advancing the branch tip. The
first attempt at this merge resolved the branch name to that new tip and silently carried it,
which was caught only by checking the merge commit's second parent against the SHA the
dispatch named.

**It was excluded and the merge was redone against `66912e3` explicitly.** Three reasons:

1. `4924940` is **unpushed**. `git ls-remote origin refs/heads/warpmpm-continue` returns
   `66912e3`, so that commit exists only in the other session's local repo. Merging it here
   and pushing would publish another session's local work under this merge — the exact
   failure CLAUDE.md's concurrent-session rules were written for after 2026-08-07.
2. It touches **`analysis/run_provenance.py` and nothing else**, a 111-insertion/32-deletion
   rework of the one file this round was told never to touch because **DP-3 owns it**.
   Carrying it would have moved that file's content on a branch off `main` without review.
3. The dispatch names `66912e3` and five commits. Merging six silently is not what was asked.

**Nothing is lost.** `4924940` remains on `warpmpm-continue` for its author to push and for
DP-3 to reconcile; this branch simply does not include it. The blob this merge carries for
`analysis/run_provenance.py` is `06b97a7`, verified after the redo, **not** `4924940`'s
`20388716`. If Josie wants the hardening included, merging `warpmpm-continue` again on top
will bring it and conflict with nothing here.

**Standing lesson, and it generalises past this repo.** `git merge <branchname>` resolves the
name at invocation, not at the moment you read the log. In a tree with concurrent sessions,
**merge the SHA you verified, never the branch name** — and check the resulting commit's
parents against it.

---

## 4. The two findings that were not the assignment

### 4.1 `main` repointed 33 citations with a comment (register `A6b`)

`6ea4329` kept the `G` edit to one physical line **and wrote down why**. `e495b56` used a
three-line comment, growing the file 327 -> 329 and shifting every line at or above the old
`:15` by +2. The damage is silent because the shifted citations land on real, plausible,
wrong lines:

| citation | means | landed on, `main` before this merge |
|---|---|---|
| `:46`, `:47`, `:48` | the three `0.05` literals; `:47` is the SPEED | `@dataclass`, `class FailureThresholds:`, `slide_m` |
| `:127-128` | `accel = np.gradient(...)`, `force = mass*accel` | `else:`, `omega = np.zeros_like(vel)` |
| `:170` | `surge_accel_g` | `surge_speed`, a different quantity |
| `:174` | `weight_n` | `vertical_force` |
| `:176` | `driven_downstream`, the AND in D8's criterion | `weight_n` |
| `:179-185` | the three sustained joint conditions | `driven_upward` and the SLIDE block |

`e495b56`'s own comment says the fork fed the verdicts "via `:170` and `:174`", and after
its own edit those two lines are `surge_speed` and `vertical_force`. **The comment
invalidates its own citation by existing.**

Resolved by collapsing to one physical line that keeps `main`'s full text and adds the rule
to the source itself. The file is 327 lines again and all landmarks verified live.

### 4.2 `D8b` read a later revision of `sim_standing.py` (register `D8c`)

**Framing first, because my own first draft got it wrong.** This is not "the wrong file". The
gated driver lived at the **top-level path** at run time, and that path was **overwritten in
place on 2026-08-08**. `docs/vista_source_reads_2026-07-25.md:355-356` records the Vista
driver MEASURED on 2026-07-25 as "17435 bytes, byte-identical to the local
`renders/yaris_render_s1/sim_standing.py`", and `_incoming/sim_standing.py` is exactly 17435
bytes. The discriminator is **content and date, not path**.

| content | lines | sha256 | floor plane |
|---|---|---|---|
| gated driver, preserved at `_incoming/sim_standing.py` | 389 | `5215c38b...` | **`:132-133`**, walls `:134-136` |
| the 2026-08-08 revision, now at the top-level path | 564 | `4696c3b2...` | `:210-211`, walls `:213-214` |

**The evidence is cryptographic.**
`_incoming/conv_2026-07-26_idev/00_provenance.txt:6` is written by the run itself and records
`driver sha256: 5215c38bed607ef6...`; `shasum -a 256 _incoming/sim_standing.py` returns
exactly that, and the top-level copy returns `4696c3b2...`. **My first draft led with the
file's mtime; that leg is withdrawn** — an rsync-preserved mtime is not provenance.

**Ten for ten.** Every line CLAUDE.md items 2 and 3 cite (`:126`, `:127`, `:129-131`,
`:132-137`, `:150`, `:156-162`, `:161`, `:183-186`, `:190-198`, `:202`) resolves exactly
against the gated driver and to unrelated code against the revision. Ten citations written by
different sessions on different dates do not all land correctly by chance.

**Two limits on the evidence, carried so it is not over-read.** The driver sha is recorded
**once**, for one idev session on 2026-07-26, and that record does not map its tasks onto
named runs; `conv_2026-07-25/` and `sweep_2026-07-26/` are empty. And `summary.json` carries
`mesh_sha256`, `solver_git_sha` and `canitford_git_commit` but **no driver hash**, so driver
identity is not a per-run stamped field. All 17 do stamp the same `canitford_git_commit`,
`d43081a6` — at which `renders/yaris_render_s1/sim_standing.py` was **untracked**. **Git holds
no blob for the gated driver at any commit.** The only surviving copy is gitignored with no
history. That is a live provenance risk, not a footnote.

**Not "the same program", which my first draft also said.** `diff` gives 188 added and **13
modified** lines, at least one behavioural: the `fill_ratio` denominator moved off the
hardcoded `HULL` constant onto `hull_m3` measured from the mesh, documented as a bug fix in
the revision's own header, and `--mass` went from required to defaulted. What is byte-identical
is the floor `add_plane` call itself, verified by hashing the two-line spans.

**So CLAUDE.md item 3's `(:132-137)` was correct.** The dispatch asked for it to be repointed
to `:210-211` and `:213-214`. **That change was not made**, because making it would point the
project's standing rules away from the driver that produced the published verdicts. What was
done instead: item 3 now **names the copy** its line numbers belong to, gives the top-level
copy's numbers alongside, and records that the repoint was proposed and refused with a
pointer to `D8c`. If Josie disagrees with that call, the change is one edit; the evidence is
in `D8c`.

**The tell was inside the file `D8b` was correcting, in the same sentence.** Its provenance
string reads "`sim_standing.py:132-133` floor ...; **`:136`** walls ...". `D8b` called
`:132-133` stale and left `:136` standing, three tokens away. The same file also cites
`:160-162` and `:190-198` for the kick and clamp, both correct against the gated driver,
which `D8b` explicitly declined to check. One citation frame, one file, one read session,
and the resolution was applied to one member of four.

**The 2026-08-13 "fix" propagated the error into new code.** `rung_e_floor_friction.py` was
edited that day so `:18`, `:97-99` and the stamped `friction_source` at `:451` all attributed
the **17 gated runs'** floor to `:210-211` — content that did not exist until thirteen days
after they ran. **Corrected here** (that file is in scope). Arm JSONs already stamped on Vista
keep the old string; expect a seam, labelling only, since 0.55 was right throughout.

**Two of `D8b`'s own line numbers went stale inside this merge.** It was written against the
branch's `validate_coupling_force_ladder.py`; `main` grew that file and the branch never
touched it, so `main`'s copy survives and `D8b`'s `:893` is now `:1002`, `:897` is now
`:1006`. Corrected in `D8c`.

---

## 5. Broken citations handed to their owners

These 5 were authored **after** `e495b56`, against the shifted numbering, so reverting
`failure_modes.py` to one line breaks them. **All 5 are outside this round's write scope.**
Each needs a -2 correction:

| site | cites | should cite |
|---|---|---|
| `analysis/slide_verdict_fragility.py:14` | `:181-183` | `:179-181` |
| `analysis/classify_rogue_silverado_sweep.py:25` | `:184`, `:211` | `:182`, `:209` |
| `analysis/classify_rogue_silverado_sweep.py:26` | `:130`, `:176` | `:128`, `:174` |
| `docs/SESSION_TRACK1B_2026-08-13.md:197` | `:48` | `:46` |
| `simulation/validate_coupling_force_ladder.py:348` | `:135-151` | `:133-149` |

`sim_standing.py:132`-family sites, out of scope, now understood as **correct for the gated
driver and wrong only if read against the 2026-08-08 revision**:
`docs/COUPLING_VALIDATION_J1_2026-08-07.md:79`, `docs/OPTION_A_SESSION1_FINDINGS.md:89`,
`docs/REGIME_LADDER_RESULTS_2026-08-07.md:410`, `docs/limitations.md:105`,
`docs/vista_source_reads_2026-07-25.md:261`, `scripts/ladder.sbatch:19`,
`simulation/validate_coupling_force_ladder.py:97,188,1002`. **None needs renumbering.** What
needs adding, wherever they are next touched, is the content identity.

**One site is wrong against BOTH contents** and appears in no prior enumeration:
`docs/semi_empirical_baseline_findings.md:82` cites `sim_standing.py:84` and `:235` for
`mu = 0.55`. Against the gated driver those are `dx = self.grid.dx` and a
`canonicalize(load_vehicle(...))` call. The real sites are **`:76`** (the `floor_friction=0.55`
keyword default) and **`:227`** (the `--floor-friction` argparse default). Out of scope here.

---

## 6. What the friction result does and does not do to the 16 SLIDE verdicts

**It does not overturn them, and it does not predict they should have been STUCK.** D8's
body is a 600 kg/m^3 cube of side 1.472 m in the rung-e tank, not the 310.494 kg/m^3 Yaris
hull in the gated scene; its floor is registered through `enable_floor_restitution`, which
reaches the rigid path only and never the water, whereas the gated floor drives both
channels (D8a); it has no ground clearance and cannot yaw or roll; it was run at a **single
grid**, g96, with **no grid-refinement check of the horizontal channel at all**; and every
number sits on an artificial sound speed of **12.845 m/s**, about 118x below real water,
never swept, which Isik and He 2022 record can qualitatively flip a rigid-body outcome. The
17 gated runs already carry `mu = 0.55`, which is D8's non-sliding arm, so the rung says
nothing about whether they should slide. What it does do is real and was predicted: it
converts section 8 of `REGIME_LADDER_RESULTS_2026-08-07.md` from conjecture into
measurement, and it retires the horizontal relevance of **every earlier ladder rung**, all
of which ran at `mu = 0`, the arm that slides, overstating horizontal motion by 40 to 65x
relative to the gated configuration. Its sharpest consequence for the 16 is indirect and is
an **inference, not a measurement**: section 5.3 puts any buoyancy error into the normal
force, J1b/J1d measure that error at about -25 to -30 percent and grid-converged, and D8
shows `mu*N` is what holds the body horizontally, so the 16 SLIDE verdicts inherit that
error in their holding term. The **sign** is the usable part and it is robust:
under-predicting buoyancy over-predicts `N`, over-predicts `mu*N`, and therefore
**under-predicts sliding**, so sixteen runs that slide anyway are conservative in the
safety-relevant direction, consistent with L-4. The **magnitude** is not quotable yet,
because the amplification `F_b/N` runs from 0.48x at a submerged fraction of 0.10 through
1.81x at 0.20 and 4.13x at 0.25 to 14.2x at 0.29, diverging as the body approaches the
equilibrium float fraction 0.3105, and that fraction has never been measured for the hull.
**The verdict this actually exposes is the other one**: `sweepV_g64_v0p5`, the single STUCK,
is the run an over-predicted holding force could be pinning, and it already sits at
`margin_frames` -3.

---

## 7. Check output

Run in the merge worktree at the commit described here.

### `register_integrity.py`

```
register_integrity.py summary
  register          docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
  sections          10 (A, B, C, D, E, F, G, H, I, J)
  items defined     113
  cross-references  14 distinct, cue-anchored
  paths checked     39 backticked, 5 unresolved
  hex tokens        35 cited: 20 git, 2 upstream-pinned, 10 research-artifact, 3 unresolved
  blocking defects  0
```

**0 blocking defects.** The 5 unresolved paths and 3 unresolved hex tokens are all
pre-existing warnings on `main` and none was introduced here; the one this round did add,
a forward reference to this file, resolves now that the file exists.

### `params_check.py`

```
params_check.py: no blocking issues found
```

Eleven warnings, all pre-existing and all documented as expected: the abandoned Track 2
density literal, the four "inertia never reaches the solver" notes that CLAUDE.md item 4
says are correct and must not be fixed, `lit:geometry_bbox` at fill_ratio 1.0023,
`lit:sound_speed_cfl` (15/17 runs below the Monaghan 10x convention, worst
`sweepV_g64_v3p0` at 4.28x, **the same artificial sound speed D9 flags as the shared
uncontrolled variable**), three `lit:resolution_convergence_gci` notices that the refinement
ratio is not constant so no GCI band can be computed, and `lit:manifest_provenance` skipped.

### `count_claims_check.py`

Run in the merge worktree it reports **25 blocking defects**. **Those are an artifact of the
worktree, not of this merge**, and that was demonstrated rather than asserted:

- The same script run in the **main worktree** reports **0** blocking defects.
- The difference is entirely untracked declaration sites. A worktree checkout contains only
  tracked files; **7 files** carrying `NAME = 0.05` declarations are untracked and therefore
  absent, which drops the live per-name counts from `5/7/8/1` to `3/4/7/1`.
- Overlaying those 7 files into the merge worktree, re-running, and then removing them again
  gives:

```
count_claims_check.py summary
  claims in registry 1 (CC1)
  assertions found  27, classified and compared
  live per-name     DRIFT_THRESHOLD_M 5, L2_DRIFT_M 7, DRIFT_THRESHOLD 8, DRIFT_M 1, THRESHOLD 1/2 loose
  defensible totals 22, 23, 24
      22  (bare literals only, archive/ excluded)
      23  (bare literals only, archive/ included)
      23  (plus the gp_surrogate default, archive/ excluded)
      24  (plus the gp_surrogate default, archive/ included)
  blocking defects  0
```

  identical to `main`.
- Independently: the merge diff touches **zero** lines carrying a DRIFT count assertion, and
  adds **zero** new `NAME = 0.05` declarations.

**So the merged content passes all three checks with 0 blocking defects.** The standing
caveat is that `count_claims_check.py` **cannot be trusted from inside a git worktree** and
must be run from the main checkout, because its live re-derivation walks the filesystem
while a worktree holds tracked files only. That is worth fixing in the check itself; it is
not fixed here.

---

## 8. Flags

**F-1. `D8b` and `CLAUDE.md` item 3 disagreed about a line number and the disagreement was
resolvable.** Resolved in favour of item 3 on the evidence in section 4.2 and register
`D8c`. Recorded here because the dispatch pre-committed to the opposite resolution, so
anyone reading the dispatch will expect `:210-211` in item 3 and will not find it.

**F-1a. A concurrent session's unpushed commit was carried by the first merge attempt and
has been excluded.** Full account in section 3.1. Flagged under "about to carry work I did
not create and cannot verify": `4924940` reworks `analysis/run_provenance.py`, which DP-3
owns and this round was told not to touch, and it exists on no remote. It was **not**
reviewed here and **no judgement is offered on its content** — only on whether this merge
should publish it, and it should not.

**F-2. A destructive slip, caught and reversed.** Cleaning up the temporary overlay, an
`rm -rf` on a directory I had created removed the pre-existing **tracked** `archive/` tree
in the merge worktree, 8 files. Restored immediately with `git checkout -- archive/` and
verified clean against the index before staging. Nothing was committed in the deleted state
and no file outside the worktree was touched. Recorded rather than quietly fixed.

**F-2a. Adversarial review was run and it changed the result.** The `physics-skeptic` agent
was given the five load-bearing claims of this session and returned **"Not CLEAN"** with five
blocking issues. All five were independently re-verified against primary sources and **all
five were upheld**. Three changed what is written here: the `_incoming`-versus-top-level
framing was wrong and is replaced by content-and-date (section 4.2); the mtime evidence leg
was withdrawn in favour of the on-node sha256; and `A6b`'s "every one of them moved" was an
implied universal that is false, corrected to 28 stale of 33. Two more produced new work: the
`rung_e_floor_friction.py` sites were corrected rather than left, and the
`semi_empirical_baseline_findings.md:82` site was added. **One blocking issue was checked and
found moot**: it warned that `D7a`'s `:46-48`/`:47` is branch-dependent after `e495b56` and
that merging it unchanged writes a wrong line number onto one side. That is true of `main`,
and it is **resolved by** this merge rather than created by it, because restoring the 327-line
geometry makes `:46-48`/`:47` correct again everywhere. The same applies to
`check_claims.py:154` and `:234`.

**F-3. Not verified here, inherited.** `D8`'s three stated limits stand unchanged: the
harness's own `flow_reached_body` gate is False for all three `mu = 0.55` arms and both
`--no-kick` arms; single grid; unswept artificial sound speed. Nothing in this merge
addresses any of them.

**F-4. Out-of-scope files left broken on purpose.** The 5 citations in section 5. They break
as a direct consequence of a fix made here, so they are this round's debt even though the
files are not this round's to edit.

---

## 9. Open, ranked

1. **Cross `mu` x `n_grid` on one body.** The only thing that converts "separately
   sufficient" into "independent". Neither branch ran it.
2. **Sweep the artificial sound speed.** The one variable both flips share and neither
   controls.
3. **The canonical set at g128** (`J15`). Unchanged as the highest-value single run.
4. **Measure the hull's submerged fraction** so the `F_b/N` amplification in section 6 can be
   evaluated instead of bounded.
5. **Get the gated driver into git.** The only surviving copy of the code that produced all
   17 published verdicts is untracked, gitignored, and has no blob at any commit — including
   the `d43081a6` those runs stamp. One `git add -f` of
   `renders/yaris_render_s1/_incoming/sim_standing.py` closes it, and `summary.json` should
   stamp a `driver_sha256` the way it already stamps `mesh_sha256` and `solver_git_sha`.
   Cheap, and it is the root cause of everything in section 4.2.
6. **Make `count_claims_check.py` worktree-aware**, or have it refuse to report blocking
   defects when it detects it is running inside one.
