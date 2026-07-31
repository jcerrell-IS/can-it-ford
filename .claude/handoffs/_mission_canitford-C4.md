# Mission: pane C4, canitford:0.4, 2026-07-24 evening

You are pane C4. Read this file in full, then execute it. Do not summarize it before acting.

## Hard constraints, read before anything else

These override any general instruction you may infer from project docs.

1. DO NOT run git commit. DO NOT run git push. Not once, not after asking. Fourteen contexts currently share the single working tree at /Users/josie/can-it-ford: these twelve tmux panes plus two live Claude Code sessions named Vista and Vista (fork) that are writing to this repo right now. Concurrent commits into one shared tree produce a history nobody can read or revert. One designated committer exists tonight and it is not you. If you produce something that deserves a commit, write the diff into your handoff file and stop there.
2. There is a standing hold on pushing. Local main is 2 commits ahead of origin/main (af1db6d, 85e2252) and Josie has explicitly held those. Any push of main would send them.
3. Do not import warpmpm, do not run a simulation, do not request an idev or GPU allocation. Vista's warpmpm/vehicle.py is mid-edit by another session and gh-dev job 864505 is occupied.
4. Verify live. Do not restate a claim from a doc, a memory, a prior chat, or a summary as current fact. cat, grep, or git log it first. If you have not checked live, say so explicitly.
5. No em-dashes in anything you write. No inline comments or docstrings in any language.
6. Before overwriting or deleting any file, check what is already there first.

## Your task

Convert SESSION_STATE.md from a single file every pane writes into directly, to an append-only, one-file-per-session handoff pattern. A shared file written by many concurrent panes has a real last-writer-wins failure mode where one pane's update silently vanishes under another's. That is the problem you are fixing.

1. The directory .claude/handoffs/ already exists. Create or update INDEX.md inside it listing every handoff file present, one line each, append-only. Never rewrite an existing line, only add new ones. Note there are already files in that directory including mission files named _mission_*.md; index the real handoff files, and decide sensibly whether mission files belong in the index (say which you chose and why).

2. Migrate whatever is genuinely still useful from the current SESSION_STATE.md into the new structure. SESSION_STATE.md then becomes a generated summary view rather than a file every pane edits directly. Only two panes write to it tonight: you own the canitford section, ford-F5 owns the ford section. Never both at the same instant.

3. PRESERVE VERBATIM, do not migrate, summarize, reword, or relocate: the block at the top of SESSION_STATE.md dated "2026-07-25 03:32 UTC (2026-07-24 22:32 CDT), orchestrator: CLAUDE.md drift fingerprint". It records md5s, byte sizes, and heading orders for the canonical CLAUDE.md files across all three machines, and exists specifically so the next unattributed CLAUDE.md drift is caught in one command. It must survive your restructure byte-for-byte and stay easy to find. If your new structure moves things around, that block stays at the top.

4. SESSION_STATE.md is hook-gated on Edit and Write, so you will get a confirmation prompt when you touch it. That is expected. Answer it yourself if it is a simple write confirmation; it is not a commit.

## Output

Write .claude/handoffs/2026-07-24_canitford-C4.md documenting the new convention clearly enough that every other pane and every future session understands it without asking. State what you changed, what you preserved, and anything you found that you did not fix.

When finished, run: tmux wait-for -S canitford-C4-done

## If you finish early

Do not idle and do not invent unrelated work. Filter the next candidate against tonight's three anchors: poster July 27, paper July 31, or one verified rendered physically plausible MPM simulation with a vehicle in it. If the next candidate does not serve one of those, write it in your handoff as optional or deferred instead of doing it.
