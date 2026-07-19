# Setting Up Claude Code So It Doesn't Duplicate Work

## The actual problem this solves

Chat-Claude (here) has `recent_chats`/`conversation_search` — it can look back at what was discussed in this Project automatically. Claude Code has no equivalent memory tool. Its only continuity is whatever's readable on disk: `CLAUDE.md`, `SESSION_STATE.md`, `STATUS.md`, git history, and the actual files. If those aren't read *first*, every session starts from zero and risks redoing work — which is exactly what happened with the three Kumar-draft panes.

The fix isn't a smarter prompt. It's making orientation the mandatory first step, written into `CLAUDE.md` itself so it happens whether or not you remember to ask for it.

## 1. Add this block to your Vista `CLAUDE.md` (and the Mac one, if you use Claude Code there too)

```markdown
## Standing orientation rule — read before proposing any new work

At the start of every session, before proposing what to do next:
1. Read this file (CLAUDE.md), SESSION_STATE.md, PROVISIONAL_STATUS.md, and
   kumar_july9_update/STATUS.md in full.
2. Run `git log --oneline -15` and `git status`. Trust this over any written
   summary if they conflict — commits are ground truth, docs can be stale.
3. Check `logs/*_result.md` for recent findings not yet folded into STATUS.md.
4. State a short summary of what you understand has already been tried or
   resolved, and wait for confirmation or correction before running anything.
5. Confirm current shell state (login node / compute node / local Mac) via
   `hostname; pwd` before prescribing any ssh/idev command. Never chain
   ssh and idev blindly — check which one actually applies first.
```

This is the same state-check-first and orient-first logic as the `bug-triage-protocol` skill, just placed somewhere Claude Code reads automatically instead of somewhere it has to be told to check.

## 2. Install `bug-triage-protocol` for Claude Code too

Skills don't sync between this chat and Claude Code, and don't sync between machines either. Copy `bug-triage-protocol-SKILL.md` to:
```
~/.claude/skills/bug-triage-protocol/SKILL.md          (Mac)
/work/11603/jcerrell0629/vista/.claude/skills/bug-triage-protocol/SKILL.md    (Vista, if you run claude natively there)
```
One-time copy per machine, not automatic — same constraint your own Operating Manual already flagged for other skills.

## 3. How to actually kick off a session without writing full context every time

Once step 1 is in `CLAUDE.md`, you don't need to restate project history — Claude Code will read it and summarize back what it thinks is true before acting. Your job shrinks to:

- **State the actual new thing**: "here's a new crash log" / "test the overlap fix" / "resolved: file lives in simulation/, not root."
- **Correct its orientation summary if it's wrong**, once, before it proceeds — cheaper than letting it act on a wrong assumption.
- **Say "run bug-triage-protocol" when the task is genuinely a multi-item triage**, same trigger phrase as here.

## 4. One thing this doesn't solve, worth knowing

Claude Code's orientation is only as good as what's actually written to disk. If a finding from a chat session here (like tonight's git-history discoveries) never gets committed to `STATUS.md` or `SESSION_STATE.md`, Claude Code has no way to know it happened. The §7 "session-close reminder" in `bug-triage-protocol` exists specifically to close this gap — take it up when offered, since it's the only bridge between what gets discovered in chat and what Claude Code can see later.
