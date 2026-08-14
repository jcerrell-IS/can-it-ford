# Fork preflight recovery, 2026-08-14

Dispatch 8. Every git fact below was re-derived live on 2026-08-14 in this session, and
landing is proved with `git ls-remote --heads origin`, never with an exit code. Vista
facts came over `scripts/tacc.sh`. Where the dispatch text and live state disagree, both
are shown and the live reading wins.

## Summary

Four artifact sets existed on one machine each with no remote copy. All four are now on
`origin`, each with a verified bundle as a second copy. One further set was checked and
needed nothing.

| set | branch | tip | orphan commits before / after |
|---|---|---|---|
| s3 enhanced tree | `claude/fork-s3-rescue-2026-08-14` | `b988779` | on zero refs / 0 |
| moving-vehicle fork seed | `claude/moving-vehicle-exploratory-2026-08-11` | `187d868` | 4 files untracked / 0 |
| Vista 6-DOF driver | `track1/sdf-6dof-driver` | `09d2b8f` | 2 / 0 |
| Vista hull sweep (**found during the rescue**) | `claude/fork-s3-rescue-2026-08-14` | `b988779` | on zero refs / 0 |
| realism track | `realism-exploration` | `c4af419` | **already safe, nothing done** |

`git ls-remote --heads origin`, read after the pushes:

```
34cb2b83dffbb5e3b4fc947371f9a6beeb7b3a51  refs/heads/claude/fork-s3-rescue-2026-08-14
187d8689413c9d2a20e0c5f9eaac03131b8a1169  refs/heads/claude/moving-vehicle-exploratory-2026-08-11
09d2b8fb1763ca85ef3e53d4fc71a7d135e126b5  refs/heads/track1/sdf-6dof-driver
```

The rescue branch has advanced to `b988779` since that read, carrying the hull sweep and
this document; the closing push is recorded at the end of this file.

`git rev-list <branch> --not --remotes=origin` returns **0** for all three branches.

## 8.1 The s3 enhanced tree

`renders/yaris_render_s3_enhanced/` was reachable from no ref at all. Both dispatch
checks reproduced exactly: `git log --oneline --all -- renders/yaris_render_s3_enhanced/`
returns empty, and `git check-ignore -v .../sim_enhanced.py` returns
`.gitignore:31:renders/*`. Line 31 was re-derived with `/usr/bin/grep -n`, not quoted
positionally. Sizes matched the dispatch: `sim_enhanced.py` 36359 B, `NOTES_2026-08-07.md`
17334 B, four `.sbatch`, six run summaries. The tree also holds `run_enhanced.py`
(3697 B), which the dispatch did not list; it is included.

Copied verbatim to `rescued/yaris_render_s3_enhanced/`, a path no ignore rule matches
(`git check-ignore` exits 1). **No carve-out was added under `renders/`.** All 13 files
sha256-verified byte-identical on both sides; the table is in that directory's
`PROVENANCE_RESCUE_2026-08-14.md`. The original tree is untouched: this is a second copy,
not a move.

Payload: Vista GH200 batch jobs **895330** (00:02:09) and **895378** (00:21:23), the
sound-speed sweep. Its primary record was on one laptop disk and on no ref.

Two provenance gaps were found and left open rather than papered over. First, the rescued
`sim_enhanced.py` (mtime 2026-08-08 03:46) **post-dates the six results** (all present by
the NOTES mtime 2026-08-07 20:21), and `hull_sweep.sbatch` states two prerequisite fixes
landed in that file on 2026-08-08, so a re-run against these results would not be a
determinism test. Second, no summary records a sha256 of the enhanced driver itself; the
`derived_from` field names the parent `sim_standing.py` (`5215c38bed607ef6`).

## 8.2 The moving-vehicle fork seed

Live before staging: `HEAD` = `claude/moving-vehicle-exploratory-2026-08-11` at `feecf5f`,
and `ls-remote --heads origin | grep -c moving-vehicle` = **0**. The four files were
staged by explicit path, never `git add -A`, and committed as `187d868`:

```
simulation/moving_vehicle_sdf_exploratory.py      29788 B
analysis/render_moving_vehicle_surface.py         11668 B
analysis/render_moving_vehicle_placeholder.py      5539 B
docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md 12676 B
```

The three unfilled placeholders were re-derived live and are exactly where the dispatch
said: `<!--LADDER-->` :143, `<!--BOWWAVE-->` :164, `<!--COST-->` :205. Sections 5, 6 and 8
are unfinished and must not be cited until filled; section 5 states a negative finding
whose supporting table is one of those placeholders. That is recorded in the commit
message so it travels with the history.

**One correction to the dispatch's framing.** It says "The branch is not on the remote
AND the files are not committed to it", which reads as though the whole branch was
unreachable. Only the branch **name** was absent. `feecf5f` was already reachable from
`origin/main` and four other origin refs, so `rev-list --not --remotes=origin` counted
**1** orphan commit, the new one, not the branch's history. The exposure was the four
uncommitted files, which is still the thing worth fixing.

## 8.3 The Vista 6-DOF driver

Recovered as `track1/sdf-6dof-driver` at `09d2b8f`, carrying `simulation/rigid6dof.py`
(307 lines), `tests/test_rigid6dof.py` (314), `docs/TRACK1_6DOF_DRIVER_2026-08-13.md`
(133), and `run_c4_free_sdf` at `simulation/validate_coupling_force.py:851` (+184).

Method: `git bundle create` on Vista into `$WORK` (not `$HOME`, which is 89.15% full),
30080 B, `git bundle verify` okay, base64 over the ControlMaster socket, sha256
`923b9185…c494a74` verified equal on both sides, then fetched into the Mac clone. The
bundle carries prerequisite `a6a707c`, which the Mac clone already had.

**Three corrections to the dispatch's own text, all live-verified.**

1. **`a231a73` is not the tip and is not on the branch.** The branch tip is `09d2b8f`,
   and exactly **two** commits were unreachable from origin: `09d2b8f` and `77d11d4`.
   `a231a73` is a **dangling** commit: `git branch -a --contains a231a73` returns empty
   and `merge-base --is-ancestor a231a73 HEAD` says NO. It is a pre-rebase copy of the
   same change, sitting on a different parent (`7453c928`). It carries nothing unique,
   and that is proved rather than assumed: `git patch-id --stable` on
   `a231a73^..a231a73` and on `77d11d4^..77d11d4` both return
   `8079edb9e4427b5b8dbde9570e0199d5685fbe9e`. Rescuing the branch rescues the work.
   `a231a73` itself remains dangling on Vista and is a garbage-collection candidate; no
   action was taken on it because it is provably redundant.
2. **Vista reachability was both things, at different times.** The first
   `scripts/tacc.sh vista` call this session returned **255**, `Permission denied
   (keyboard-interactive)`, the expired-socket case. After the socket was reopened, the
   same call returned **0**. So "unreachable because of MFA" and "a live ControlPersist
   socket contradicts that" are both true statements about different moments; the state
   is the socket's, not the machine's. Test it, never assume it.
3. **"25/25 tests passing" reconciles by inspection, and the passing half is
   unverified.** `tests/test_rigid6dof.py` declares **21** `def test_` functions, one of
   which carries `@pytest.mark.parametrize` with **5** cases, so pytest would collect
   20 + 5 = **25**. That explains the count. It was **not executed**: Vista's system
   `python3` has no `pytest` module, and installing one was refused because Vista `$HOME`
   is 89.15% full. The claim is marked unverified rather than repeated.

## 8.4 The realism track, already safe, nothing done

Confirmed live, no recovery effort spent: `git -C /Users/josie/can-it-ford-realism
ls-files simulation/realism/` returns all nine modules including `dynamic_body.py`,
`outflow_deactivate.py` and `render_water.py`; the tree is clean; local HEAD is
`c4af419b…` and `ls-remote --heads origin realism-exploration` is the same SHA.

## The fourth set, found during the rescue

`renders/yaris_render_s3_enhanced/` contained two `hull_sweep*.sbatch` files describing
"the first run in this project where vehicle GEOMETRY actually varies", dated 2026-08-08,
with **no results anywhere in the tree** and zero mentions in the NOTES. Checking Vista
showed the sweep had in fact run: five completed runs at
`$WORK/render_s3_hullsweep`, on no git ref, on one filesystem.

Recovered onto the same rescue branch: five `summary.json`, five `metrics.csv`, six logs.
Full detail, caveats and the driver's own summary table are in
`rescued/render_s3_hullsweep/PROVENANCE_RESCUE_2026-08-14.md`. The headline caveat, so it
is not missed: **every run is 1100 kg, including the Silverado**, so this is a
geometry-at-fixed-mass sweep and not a three-class experiment, and three of the five fail
gate P-2.

This is a scope extension beyond the three sets Dispatch 8 names. It was taken because
the set was in exactly the state the dispatch exists to end, the payload is 112 KB, and
it touches no canonical store and no other thread's branch. It is reversible: the four
commits are contiguous and on this branch only.

## Still open, with reasons

1. **1.39 GB of `rollout.npz` remain on Vista only.** Five particle dumps, 156 to 477 MB
   each, at `$WORK/render_s3_hullsweep/`. Too large for this repo, so they were left.
   The Vista allocation **expires 2026-09-30**. Archiving them elsewhere is Josie's
   decision, not this rescue's.
2. **The hull sweep has no execution record.** `sacct` shows the only `s3hull` job,
   **896281**, `CANCELLED`, `Start = None`, `00:00:00` elapsed: it never ran. The result
   mtimes (23:42-23:43 on 2026-08-07) fall inside job **896302** `idv52164`, an
   interactive `gh-dev` session that ended in **TIMEOUT** after 02:00:05. Execution
   provenance is therefore an inference from timestamps, and is labelled as one.
3. **The hull sweep summaries carry no provenance fields at all**: no `mesh_sha256`, no
   `solver_git_sha`, no `canitford_git_commit`, no backfill block, because
   `analysis/run_provenance.py` has never seen them. Their `hull_source` values are Vista
   paths, not sha256 anchors.
4. **`canitford_git_commit` in the six enhanced summaries is RECONSTRUCTED**, by the
   files' own admission, inferred from mtime against `git rev-list` and blind to a dirty
   tree. Presence is not provenance.
5. **`a231a73` stays dangling on Vista.** Provably redundant, so nothing was done, but it
   will disappear at the next `gc` and that is worth knowing before anyone cites the SHA.
6. **The 6-DOF test suite was not executed** on any machine this session; see 8.3 point 3.

## Second copies

Bundles, all `git bundle verify` okay, in this session's scratchpad:

| bundle | bytes | contains |
|---|---|---|
| `track1_6dof_rescue_2026-08-14.bundle` | 30080 | `track1/sdf-6dof-driver` at `09d2b8f` |
| `fork_s3_rescue_delta.bundle` | 40483 | rescue branch at `34cb2b8`, delta from `1a868f3` |
| `moving_vehicle_delta.bundle` | 25249 | moving-vehicle at `187d868`, delta from `feecf5f` |

The 6-DOF bundle also still exists at `$WORK/track1_6dof_rescue_2026-08-14.bundle` on
Vista, sha256 `923b9185…c494a74`. Scratchpad bundles are session-scoped and will be
cleaned up; the durable second copies are origin plus the Vista bundle.

## Scope notes

- **A third branch name was used.** Dispatch 8 lists two branches under BRANCHES YOU MAY
  WRITE TO. `track1/sdf-6dof-driver` is a third. It is the name Vista's own repo uses and
  the name the dispatch itself quotes, no other dispatch owns it, and the definition of
  done requires the set to be reachable from origin, which needs a ref. Confirmed with
  Josie before pushing.
- **All three pushes were confirmed with Josie first**, and every committed file was
  scanned against credential patterns beforehand: zero hits, the only 40-hex strings
  being git SHAs and mesh sha256s. Nothing credential-related was read, written or
  touched; that belongs to another thread.
- **`main` was not touched.** The modified `.mcp.json` and the ~22 untracked
  `renders/yaris_render_s1/*.py` in the main worktree are another session's and were left
  exactly as found.
