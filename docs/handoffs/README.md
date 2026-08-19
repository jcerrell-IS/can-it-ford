# Cross-session handoffs

## Why this directory exists

The R9 coordinator audit (`docs/R9_COORDINATOR_AUDIT_2026-08-19.md`, findings V3 and V4)
measured two defects in the coordination layer used for the eleven-session round of
2026-08-19:

- **V3.** One shared board, `.claude/state/r8_board.md`, with eleven concurrent appenders.
  That is the exact pattern the corpus document "Claude Code, Used Correctly" names as the
  thing to replace, because "if all chats write to a single HANDOFF.md, last writer wins
  and earlier handoffs vanish".
- **V4.** That board was **untracked**, hidden by `.gitignore:85` (`.claude/state/`). The
  single coordination artifact of an eleven-session round existed in no commit, on no
  branch and in no bundle. The tmux server died twice that night.

And slot d18-platform measured the mechanism that makes V3 concrete
(`5692f1e`): eight concurrent appenders to one file corrupt rows above **1024 bytes**,
because writes chunk and interleave at exactly that boundary. **64 percent of the board's
rows exceed it.** One observed line read writer C x 1024, writer A x 1024, writer C x 976.
**The line count stays correct, so counting rows is not a detector.**

## The pattern

One file per session, append-only, **one writer each**, so the interleave cannot occur by
construction rather than by convention:

    docs/handoffs/<date>_<slot>.md      one per session
    docs/handoffs/INDEX.md              one line per append

Tracked in git, which is the project's stated single source of truth across surfaces.

## What is here now

`R9_BOARD_SNAPSHOT_2026-08-19.md` is the 336 KB board as it stood at the end of the round,
committed so it cannot be lost. It is a snapshot, not the live file; the live board
continues at `.claude/state/r8_board.md` for the sessions still running, because rewriting
an append-only log mid-round is the one operation that would lose another session's rows.

## Falsifier for the claim that this fixes V3

This does not fix it if two sessions ever write the same handoff file. The check is that
every file in this directory has exactly one slot name in its filename and that no commit
touching it comes from two different branches.
