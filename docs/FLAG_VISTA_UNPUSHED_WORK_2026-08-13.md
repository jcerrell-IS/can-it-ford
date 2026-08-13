# FLAG: 12 unpushed commits on Vista, and a config sync would have destroyed them

Raised under flag rule 1: "You are about to discard, overwrite, or force-push over
uncommitted work you did not create and cannot verify is safe to lose." I stopped short
of the overwrite. Nothing on Vista was modified except two additions, both new paths.

## What the RTFD report said

> **A. Unpushed work.** None outstanding. Both Mac branches report 0/0 divergence at the
> end of their threads. **Vista made no commits to lose.**

## What is actually there, verified live 2026-08-13

`/work/11603/jcerrell0629/vista/can-it-ford`, branch `main`, HEAD `4b38aa3`:

```
git rev-list --left-right --count origin/main...HEAD  ->  173   12
```

**12 commits ahead**, 173 behind. The 12, newest first:

| sha | subject |
|---|---|
| `4b38aa3` | realism_track: rewrite the top-line verdict, refresh the handoff |
| `a6b66b6` | realism_track: mass-based head gives ~1% at g64; g96 settle not reproducible |
| `c74ac23` | realism_track: artifact confirmed by measurement and by intervention |
| `d59c48e` | realism_track: the -50% is a reference artifact, wrench is sound to ~8% |
| `45be8c3` | realism_track: deficit is a constant pressure offset; two claims retracted |
| `0d81f2f` | realism_track: gated settle isolates a pressure deficit, prediction tested |
| `a3ab0d0` | realism_track: re-cost sound speed against the settle, record the BULK trap |
| `20e2063` | realism_track: wrench diagnostic retracts the pose-loop hypothesis |
| `868302e` | simulation: commit validate_coupling_force.py, untracked since first use |
| `001a62c` | realism_track: rung-b coupled run executed, moving collider NOT validated |
| `cdcdf9d` | realism_track: submit-ready GH200 rung-b job, sound-speed cost analysis |
| `1e4c6d5` | realism_track: validate SDF-collider coupling path against analytic buoyancy |

Plus **5 modified tracked files** (`.claude/settings.json`, `CLAUDE.md`,
`simulation/can_it_ford_L2_mpm.py`, `simulation/failure_modes.py`,
`simulation/validate_coupling_force.py`) and about **22 untracked paths**, among them
`analysis/run_provenance.py`, two `.remember/vista_session_2026-08-12*.md` files,
`docs/GNN_SURROGATE_ASSESSMENT_2026-08-12.md`,
`docs/SEMI_EMPIRICAL_BASELINE_CITATIONS_2026-08-12.md`, and a
`.vista_conflict_backup_2026-08-11/` directory.

These are substantive results: a coupling validation, two explicit retractions, a
pressure-deficit diagnosis. They exist on one Lustre filesystem, on an allocation
expiring **2026-09-30**, and nowhere else. `$WORK` is not a git remote.

## Why this nearly went wrong

The task was "apply the protocol globally by scping to LS6 and Vista." The obvious
execution is `scp CLAUDE.md vista:.../can-it-ford/CLAUDE.md`. Vista's `CLAUDE.md` is
**locally modified**, so that copy would have silently destroyed edits that exist
nowhere else, in a file nobody would think to check afterwards.

Both LS6 clones were checked the same way first and were genuinely clean (no modified
tracked files, no untracked paths), so those were updated.

## What I did instead

- **Did not touch** `/work/11603/jcerrell0629/vista/can-it-ford/CLAUDE.md`. Confirmed
  after the fact: still md5 `27409f8f`, the pre-existing value.
- Backed it up anyway to `CLAUDE.md.bak-2026-08-13` with `cp -n`.
- Placed the canonical 773-line version alongside as
  `CLAUDE.md.canonical-2026-08-13` (md5 `e60a7a53`, matching the Mac).
- Wrote `READ_ME_FIRST_2026-08-13.md` into that tree.
- Updated only `~/.claude/CLAUDE.md` on Vista, which was byte-identical to the Mac's
  across all three machines, so there was nothing local to lose.

## Recommended, and it needs your decision, not mine

Get those 12 commits off Vista before anything else touches that tree. A branch push is
the low-risk option because it cannot affect `main`:

```bash
ssh vista 'git -C /work/11603/jcerrell0629/vista/can-it-ford push origin HEAD:refs/heads/vista-realism-track-2026-08-13'
```

Success looks like a new remote branch with 12 commits and `main` unchanged. The most
likely failure is credential prompting, since the clone uses an HTTPS remote; if it
prompts, a bundle avoids the network entirely:

```bash
ssh vista 'git -C /work/11603/jcerrell0629/vista/can-it-ford bundle create /work/11603/jcerrell0629/vista/realism_track_2026-08-13.bundle origin/main..HEAD'
```

then `scp` that bundle to the Mac and `git fetch` from it. Verify with
`git bundle verify` before deleting anything on Vista.

**I have not run either.** Both push to or create artifacts for a shared remote, and the
standing rule requires confirmation for any push.

## Status

**OPEN.** Vista's tree is exactly as it was, plus two new files.
