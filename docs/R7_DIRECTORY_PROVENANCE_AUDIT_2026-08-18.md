# R7 directory-provenance audit: the handoff names the wrong driver

Run 2026-08-18. Canonical repo `jcerrell-IS/can-it-ford`, branch `main`, fetched live.
Canonical blob shas are from `git ls-tree -r origin/main` after a fresh fetch, which is the
remote's own blob hash, not a local clone's opinion. Every local copy hashed with
`git hash-object`. Nothing was deleted, moved, renamed or edited.

## 1. THE FINDING THAT MATTERS: two different drivers, and the wrong one is protected

`sim_standing.py` exists in 13 places but has only **TWO distinct contents**:

| blob | size | sha256 (16) | canonical path(s) at origin/main |
|---|---|---|---|
| `b23b4ad6727c` | 17435 | `5215c38bed607ef6` | `analysis/render_v1/as_ran_local_copies/sim_standing.py` |
| `fc5b3cc0f8d7` | 26902 | `4696c3b2d39f4e28` | `renders/yaris_render_s1/sim_standing.py` |

`renders/yaris_render_s1/_incoming/sim_standing.py` is **byte-identical to the 17435-byte
as-ran copy**, not to the 26902-byte file sitting one directory above it.

**THE ROUND 7 HANDOFF IS CONTRADICTED.** Its section 2 says: "Do not edit `sim_standing.py`:
its sha256 `4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9` stamps every
published run."

Read live from job 918350's own stdout, the g160 flip, the headline result:

```
5215c38bed607ef6fa0723afa4e9593de87a1fd82818a0e92989f52daffc9d45  .../render_s2/sim_standing.py
```

**The runs stamp `5215c38b`, the 17435-byte driver. `4696c3b2` is a different file.**

Three consequences, all live:

1. **The stated guard protects the wrong file.** Anyone honouring "do not edit the file whose
   sha is 4696c3b2" leaves the driver that actually stamps the runs unprotected.
2. **Line numbers taken from the 26902-byte copy do not apply to any published run.** This is
   not hypothetical: it caused a wrong citation in this very round. `claude/r7-collect`
   wrote "sim_standing.py:240 applies a one-shot decaying kick", I repeated it into
   CLAUDE.md, and the kick is actually at `:161` of the 17435-byte driver, additive, with no
   decay term. Corrected in `6d904e1`. The ROOT CAUSE was the handoff naming the wrong file.
3. **CLAUDE.md was right all along.** Its AUGUST 4 audit item 2 cites the kick at `:156-162`,
   which matches the 17435-byte driver exactly. The handoff, not CLAUDE.md, is the stale one.

A third path holds the same content on Vista, `$WORK/render_s2/sim_standing.py`, and its
sha matches, so the run provenance itself is internally consistent. Only the handoff's
attribution is wrong.

## 2. Table

`sim_standing.py`, 13 copies, 2 distinct contents:

| path (under `/Users/josie/`) | blob | canonical? | reasoning |
|---|---|---|---|
| `can-it-ford/analysis/render_v1/as_ran_local_copies/` | b23b4ad | **YES** | matches origin/main at this path; THIS is what the runs stamp |
| `can-it-ford/renders/yaris_render_s1/` | fc5b3cc | **YES** | matches origin/main at this path, but is NOT the run driver |
| `can-it-ford/renders/yaris_render_s1/_incoming/` | b23b4ad | untracked | byte-identical to the as-ran canonical; register D4a calls `_incoming/` the per-run tree, and the hash agrees |
| `can-it-ford/render_s2/multigeom_2026-08-08/` | fc5b3cc | untracked | copy of the 26902 variant, per-run staging |
| `can-it-ford-warpmpm-continue/` x2 | both | no | separate clone, both variants present, 08-12 |
| `can-it-ford-moving-vehicle`, `-visual-trial`, `-realism/` | b23b4ad | no | sibling clones carrying the as-ran copy only |
| `can-it-ford-rescue/vista_render_s2_meta/` | b23b4ad | no | rescue tree, content current |
| `can-it-ford-BACKUP-2026-08-11/` x4 | both | no | stale backup, both variants |
| `Downloads/can-it-ford-main/` x2 | both | no | downloaded zip of main, 08-13, contents exactly canonical |

`CLAUDE.md`, 30 copies, 9 distinct contents. Canonical at origin/main is **`37983d258687`,
39052 bytes**, and 12 of the repo's worktrees carry exactly that blob. Non-canonical:

| path | blob | reasoning |
|---|---|---|
| `can-it-ford/CLAUDE.md` | 1642fb4 | **main tree working copy, 50050 bytes, ~11 KB AHEAD of origin, uncommitted under another live session.** Not stale, in progress. |
| `can-it-ford/.claude/worktrees/r7-ladder/` | 81d184a | this branch, carries the R7 additions, pushed |
| `can-it-ford/.claude/worktrees/ctx-census/` | b23e2b8 | old worktree, 22066 bytes, 08-07 |
| `can-it-ford-warpmpm-continue/` | 8e87caa | separate clone, 08-12 |
| `can-it-ford-realism/` | f5b4054 | separate clone, 08-12 |
| `can-it-ford-moving-vehicle`, `-visual-trial` | 23174e2 | two clones sharing one older content, 08-11 |
| `can-it-ford-BACKUP-2026-08-11/` x2 | 1da8c85, b23e2b8 | stale backup |
| `can-it-ford-BACKUP-before-history-purge/` x4 | aab2fd2 | pre-purge, 2282 bytes, 07-23, four copies of one tiny old file including a nested `can-it-ford/can-it-ford/` |
| `can-it-ford-audit/2026-08-04/dl/` | ebf2b5a | audit snapshot, 2748 bytes |
| `can-it-ford-bundles/2026-08-1{6,7}/` | fbd492a, 68ce06e | dated main-tree snapshots, working as designed |
| `Downloads/can-it-ford-main/` | 37983d2 | exactly canonical, just a downloaded zip |

## 3. Sensitive sweep: 34 raw matches, ZERO real credentials

Swept the four unwatched non-canonical trees for `ghp_`, `github_pat_`, `olp_`, `sk-`,
`hf_`, `AKIA`. Raw counts: BACKUP-2026-08-11 19 files, before-history-purge 6,
Downloads/can-it-ford-main 5, can-it-ford-bundles 4.

**Every sampled match is prose ABOUT the patterns, not a credential**: audit tables counting
pattern occurrences, redaction `sed` scripts that contain the patterns by construction, the
directory-provenance skill file itself, and session logs discussing rotation. Two apparent
hits are binary `rollout.npz` files, which are byte coincidences in float arrays.

Stated plainly per the skill's own instruction: **this keyword sweep produced zero real hits
despite a high raw count.** None of these paths is tracked by git (`git ls-files` returns 0
for them).

**This does NOT clear the known exposure.** The 12 recorded credentials live in `~/.zshrc`,
`~/.netrc` and `~/.claude/backups/`, which are outside the directories this audit swept, and
the standing record is 12 credentials with 0 rotated.

## 4. Recommended next human decisions, none taken here

1. **Fix the handoff's driver sha**, or better, stop citing a bare sha: name the path AND
   the byte size AND the sha, because two files one directory apart both legitimately match
   `sim_standing.py` and only one stamps the runs.
2. **Decide which `sim_standing.py` is "the" driver in prose.** Right now `renders/yaris_render_s1/sim_standing.py`
   reads like the canonical one by position while `_incoming/` is the one that runs.
3. `can-it-ford-BACKUP-before-history-purge/` holds a nested `can-it-ford/can-it-ford/`
   duplicate of a 2282-byte July CLAUDE.md. Archive candidate, forensic value only.
4. `Downloads/can-it-ford-main/` is a byte-exact copy of main. Safe to delete, zero unique
   content, but that is your call.
