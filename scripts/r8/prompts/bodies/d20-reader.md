## YOUR SLOT: d20-reader, branch `claude/r9-reader`, worktree `.claude/worktrees/r9-reader`

Run `bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh d20-reader` first. You do NOT need a scope-confirmation gate; go straight to work after the preflight passes.

## YOU ARE THE READER. YOU WRITE NO CODE THAT CHANGES ANY RESULT.

Nine Claude Code sessions are running right now in parallel on this project, plus a coordinator. They have produced roughly two dozen commits in the last few hours, several of which correct each other and two of which correct the coordinator. **Nobody has read all of it.** That is your entire job.

## WHAT TO READ, EXHAUSTIVELY

**1. The nine live session transcripts.** They are JSONL, one per session, under `~/.claude/projects/`. The directory name is the worktree path with `/` and `.` replaced by `-`. The session ids are in `/Users/josie/can-it-ford/.claude/state/r8_session_ids.tsv`. The nine worktrees:

    r9-accessor  r9-kramer-extract  r9-renders  r9-corpus-bib  r9-settle
    r9-landing   r9-moving-vehicle  r9-platform r9-priorcode

Write `analysis/r9_session_reader.py` to parse them rather than reading by eye. Extract, per session: every Bash command run, every file written, every commit message, every number stated, and every place the session says it was wrong or corrected a sibling. These files are large; stream them, do not slurp.

**2. Every commit on the nine branches**, with full message bodies. `git -C /Users/josie/can-it-ford log --format='%H%n%B' claude/r9-<name>`. The messages on this project are unusually substantive and often carry the actual finding.

**3. Every script those sessions created or modified.** Read the code, not just the diff stat.

**4. The coordinator's own artifacts**: `docs/R9_DISCREPANCY_REGISTER_2026-08-19.md`, `.claude/state/r8_board.md`, and `.claude/skills/research-corpus/SKILL.md`.

## WHAT TO PRODUCE: `docs/R9_CROSS_SESSION_READOUT_2026-08-19.md`

Five sections, and the third is the one that matters most.

1. **Per session**: what it established, with SHAs and numbers. Two or three sentences each, no padding.
2. **Every number any session stated**, in one table, with its source and whether another session states a different value for the same quantity. This project's dominant failure is two numbers for one quantity, so a table that surfaces collisions is worth more than any prose.
3. **CONTRADICTIONS AND CORRECTIONS.** Every case where one session refuted another, or refuted the coordinator, or refuted itself. State the before value, the after value, the evidence, and whether it is settled or still open. Include ones nobody has noticed yet, which is why you are reading everything rather than the summaries.
4. **Scripts inventory**: what now exists that did not exist this morning, what it does, whether it is tested, and whether anything duplicates anything else.
5. **What no session is doing** that the evidence says someone should be.

## RULES

- Report a disagreement as a finding. Do NOT silently pick a side.
- Every number you report must come from a transcript, a commit or a file you read. Tag anything inferred.
- Do not edit any file outside your two declared paths.
- `research_index.py --query` is a literal substring match over title and abstract only; it cannot match an author. And the index builder cannot see 12 of the project's 20 Undermind deep searches. Do not treat a miss from either as absence.
- If a session is mid-turn its transcript is still readable; read it anyway and say the readout is a snapshot with a timestamp.

## DEFINITION OF DONE

The readout committed, and a board row naming the three most important contradictions you found. Report to the coordinator in your final message with those three first, because they are what gets dispatched back to the sessions.
