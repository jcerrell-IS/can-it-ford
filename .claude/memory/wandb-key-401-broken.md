---
name: wandb-key-401-broken
description: "W&B key rotation CONFIRMED by hash July 30; ~/.netrc is NOT stale (matches live); the OLD key is still publicly readable on GitHub via dangling commit 50eff29 and revocation on wandb.ai remains the one open action"
metadata: 
  node_type: memory
  type: project
  originSessionId: a4dec10a-24a0-4ec5-825a-dfb8cef24336
  modified: 2026-07-31T01:12:35.035Z
---

**Updated 2026-07-30, three claims below are now corrected by direct hash comparison (T1).**

1. **Rotation is CONFIRMED, no longer just claimed.** The key on the public deletion line
   and the live `~/.zshrc` key are both 86 chars and their sha256 prefixes differ
   (`1fb673a2…` exposed vs `906a741c…` live). They are different keys.
2. **`~/.netrc` is NOT stale.** Its wandb password hashes to `906a741c…`, identical to the
   live key. Any note saying netrc still holds an old value is wrong; stop repeating it.
3. **"the leaked key from 50eff29" is misleading.** `50eff29` is the commit that *removed*
   the hardcoded key (`-API_KEY = "…"` replaced by `wandb.login(key=os.environ.get(...))`).
   The key lived in the commits *before* it. But the removal diff still displays the value,
   and GitHub **still serves that commit** at
   `https://github.com/jcerrell-IS/can-it-ford/commit/50eff29d92ad25eba92387bdf3752ceb1200844f.patch`
   with no authentication, even though filter-repo (run 2026-07-23) left it unreachable from
   `origin/main`. Full SHA `50eff29d92ad25eba92387bdf3752ceb1200844f`, file
   `analysis/wandb_backfill.py`, dated 2026-07-03.

**The one open action is REVOCATION on wandb.ai, not rotation.** Unreachable from a branch
is not deleted: GitHub serves dangling commits by SHA indefinitely unless GitHub Support is
asked to purge them. Rewriting history again does nothing about a SHA someone already has.

RESOLVED July 13, 2026. Earlier that day the Mac's WANDB_API_KEY was broken: ~/.zshrc had
four stacked `export WANDB_API_KEY=` lines, two placeholders, and an active 86-char
wrong-format value (ended 0YpT) that got a 401 from api.wandb.ai. Josie then edited
~/.zshrc herself (live, from another pane, which explained the file changing mid-session)
down to a single active export at line 196 with a new value ending iNbz.

Confirmed working: sourcing ~/.zshrc in a fresh shell and running the round-trip with the
env python (/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python3, wandb
0.28.0) returned "connected OK, run count: 88". Note W&B keys are 86 chars now, not the
old 40-hex format, so length alone is not a defect signal anymore.

Exposure scan (Step 4) came back CLEAN: all 88 runs are state=finished, all created by
user jcerrell29, newest is 2026-07-07, and NONE were created on/after 2026-07-09 (the
key-exposure window). No evidence the leaked key from 50eff29 was used to create or tamper
with runs in this project. Caveat: this only covers this project's run list, not deletions,
other projects, or read-only access.

STILL OPEN after this: (1) ~/.netrc line 3 `password` still holds the OLD dead key (ended
0YpT) as of mtime 01:24; it is a stale fallback that will 401 whenever the env var is
absent, and it is a copy of a leaked-era key that should be purged. Fix = replace line 3's
value with the new key (same one now in ~/.zshrc) or delete the machine block. (2) Whether
the OLD exposed key from 50eff29 was explicitly revoked in wandb.ai settings is a separate
web-UI action, not confirmable from the API, still open (STILL OPEN item 3).

**Why:** item 3 (revoke/rotate the exposed key) is the oldest unresolved security item; a
session prompt had asserted rotation was already done and working when it was not.

**How to apply:** treat the Mac key as working now, but do not consider the security item
closed until ~/.netrc is reconciled and the old key is confirmed revoked on wandb.ai.
Env-var precedence means the Python API works even with a stale netrc, so a green
round-trip does NOT prove netrc is clean. Related: [[wandb-key-exposure-50eff29]].
