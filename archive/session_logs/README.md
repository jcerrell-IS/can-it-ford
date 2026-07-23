# archive/session_logs/

Old session dumps, backups of the live session log, and manual tmux pane captures.

Kept, not deleted, because they are the raw record of past Claude Code sessions and may
be needed to reconstruct a decision or find a lost finding. They are not live inputs to
any script: the `_inbox` sweep and the session exporter do not read anything in here.

Large binaries (`*.zip`, `LIVE_SESSION_LOG.md.bak-*`) and `pane*_export.txt` are present
on disk but intentionally kept out of git (see `.gitignore`), so the repo does not carry
tens of MB of session-log history. See `ARCHIVE_INDEX.md` at the repo root for the full
list of what was moved here and from where.
