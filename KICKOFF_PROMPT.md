# Reusable Claude Code kickoff prompt — Can It Ford

Paste the block below at the start of any new Claude Code session on this project,
in addition to (not instead of) CLAUDE.md already being read automatically.

---

Before doing anything: read CLAUDE.md, SESSION_STATE.md, PROVISIONAL_STATUS.md,
and kumar_july9_update/STATUS.md in full. Run git log --oneline -15 and git
status, and trust those over any written summary if they conflict. Check for
a KNOWN DEAD ENDS section in CLAUDE.md and treat everything listed there as
already answered — do not re-test it.

State back in 3-4 bullets: what you understand the current goal is, what's
already been ruled out, and what the single highest-value next test is. Wait
for confirmation before running anything.

If you're about to edit a parameter that has known dependents (box size,
density, grid_density, domain bounds — see the COUPLED VARIABLES section),
name the dependents and confirm they're accounted for before editing.

Before running ssh or idev, run hostname; pwd first and only issue the command
that actually applies to where you already are.

If another Claude Code session might be touching the same file right now,
check git status for uncommitted changes before editing it yourself, and
write your findings to a session-specific scratch file (logs/paneX_result.md)
rather than editing shared status files (STATUS.md, SESSION_STATE.md)
directly, unless you've confirmed you're the sole active session.
