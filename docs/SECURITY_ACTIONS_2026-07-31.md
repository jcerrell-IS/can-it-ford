# Security actions, 2026-07-31

Two findings that require action outside this repository, plus a false-positive
register so nobody re-flags settled items. No credential value or personal content
is reproduced here by design.

Established against `origin/main@1767d87` on 2026-07-31, using the GitHub connector
and unauthenticated `curl`. Both findings were surfaced while closing the
figures-and-repo-sync brief; neither was part of that brief.

---

## 1. W&B API key, still publicly served

**Commit:** `50eff29d92ad25eba92387bdf3752ceb1200844f`
("Add thresholds.py utility, stage wandb_backfill changes", 2026-07-03)

**Where the value sits:** `analysis/wandb_backfill.py`, on the **deletion** line of
that commit's diff. `50eff29` is the commit that *removed* the hardcoded assignment
and replaced it with an environment lookup. The key itself lived in the commits
before it. A removal diff still renders the removed value, so the fix commit is
itself the exposure surface.

Any note phrased as "the leaked key from 50eff29" invites the wrong conclusion that
this commit introduced it. It did not.

**Why "already purged" is not true:**

- `git filter-repo` was run on this repository on **2026-07-23 08:08**
  (`.git/filter-repo/` present, 191 commits mapped, `refs/heads/main` rewritten from
  `0f35620e` to `a678013`).
- After that rewrite the commit is **unresolvable locally**: `git cat-file -t 50eff29`
  fails, it is absent from the commit-map, it is not among the six commits filter-repo
  reports dropping, and `git merge-base --is-ancestor 50eff29 origin/main` fails.
- **GitHub still serves it anyway**, with no authentication, at
  `https://github.com/jcerrell-IS/can-it-ford/commit/50eff29d92ad25eba92387bdf3752ceb1200844f.patch`

GitHub retains unreferenced commit objects and serves them by SHA. Unreachable from
a branch is not deleted. Rewriting history again does nothing about a SHA someone
already holds.

**Rotation is confirmed. Revocation is not.** Compared by SHA-256, never by value:
the string on the public deletion line and the live `WANDB_API_KEY` are both 86
characters and hash differently. They are different keys, so the rotation did happen.

**Required actions, neither of which can be done from this repository:**

1. **Revoke the old key on wandb.ai.** This is the action that actually closes the
   finding. The key remains readable by anyone with the URL above until it is dead.
2. **Request a GitHub Support purge** of the unreferenced commit object, once the key
   is revoked. Cosmetic before revocation, worth doing after.

---

## 2. Personal-profile content in public history

**Commits, both ancestors of `origin/main`:**

- `4db2789` — `_inbox/LIVE_SESSION_LOG.md`, 7 occurrences
- `ca91b12` — `SESSION_STATE.md`, 1 occurrence, itself a note flagging the exposure
  as unresolved

The content is a personal-profile description of the repository owner. It is not
quoted here and should not be quoted into any future report, ticket, or commit
message.

**Current state:** `origin/main` at HEAD is clean. `SESSION_STATE.md` has zero
occurrences today and `_inbox/LIVE_SESSION_LOG.md` is not in the HEAD tree
(`_inbox/` is now gitignored). The exposure is historical only, but history is
public and cloneable.

**Not exposed:** three further copies under `docs/session_notes/archive/` carry the
same content. All three are untracked and covered by the `docs/session_notes/archive/`
ignore rule, and none has ever been in a tracked tree. They are a local-disk concern
only.

**Detection note that matters for future audits:** a path-only scan misses this
entirely. Searching commit trees for filenames containing the keyword returns nothing
across all 231 commits reachable from `origin/main`. Only a **content** scan
(`git log origin/main -S`, then filtering derived and binary files) surfaces it. An
audit that reports "clean" after a path scan has not actually checked.

**Required actions:** removal needs a history rewrite plus a GitHub Support purge
request, the same two-step as the key above. Weigh that against the fact that the
rewrite invalidates every existing clone and every commit SHA cited in the paper,
the poster, and the DesignSafe submission.

---

## 3. False positives, settled. Do not re-flag.

| Hit | Why it is not a finding |
|---|---|
| `scripts/validate_state.sh` matches the profile keyword set | Line 5 is a **guard**: a `git grep -qiE` over `CLAUDE.md` for exactly those terms. It exists to detect this content, not to contain it. Read that line for the authoritative pattern list. Protective code, keep it. |
| `figures/phase_space_interactive.html` matches one profile keyword | Base64 payload coincidence. The surrounding bytes are `...QVAdhdhX2XQ...`, inside an embedded data blob. |
| `figures/yaris_flood_standing.gif`, `kumar_july9_update/simulation_d1p0_v3p0.mp4` | Byte-level coincidence in binary media. No printable context. |
| `docs/**` matches `diagnos` | Engineering usage ("diagnostic"), not clinical. Counts are identical before and after the `a678013` cleanup, which is what shows it was never the target. |
| `docs/DIRECTORY_PROVENANCE_AUDIT_2026-07-25.md` matches `ghp_`, `sk-` | Prose describing the patterns an audit searches for, plus one already-redacted `sk-ant-oat01-...` reference. No live token. |

---

## 4. Correction to a stored note

An earlier memory note recorded `~/.netrc` as **stale**, still holding a superseded
W&B key. **That is false and has been corrected.** The `api.wandb.ai` password in
`~/.netrc` hashes identically to the live `WANDB_API_KEY` in `~/.zshrc`
(SHA-256 prefix `906a741c`), and both differ from the publicly exposed value
(`1fb673a2`). `~/.netrc` is current and needs no action.

The remaining open item from that note is revocation, item 1 above, not rotation and
not `~/.netrc`.
