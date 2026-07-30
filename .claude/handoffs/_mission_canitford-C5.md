# Mission: pane C5, canitford:0.5, 2026-07-24 evening

You are pane C5. Read this file in full, then execute it. Do not summarize it before acting.

## Hard constraints

1. READ-ONLY on all data. Do not modify, regenerate, or re-run any dataset, CSV, or simulation.
2. DO NOT run git commit. DO NOT run git push. Fourteen contexts share the single working tree at /Users/josie/can-it-ford, including two live Claude Code sessions (Vista, Vista (fork)) writing right now. Local main is 3 commits ahead of origin/main under an explicit push hold.
3. Do not import warpmpm, do not run a simulation, do not request idev or GPU. gh-dev job 864505 is occupied.
4. Verify live. Never restate a claim from a doc or a summary as current fact. If you cannot verify something, say so and name the blocker rather than guessing.
5. No em-dashes. No inline comments or docstrings.
6. DO NOT WRITE docs/POSTER_ASSET_TABLE.md. Pane F5 is the sole writer of that file. You are its discovery and verification feed. Two writers on one file is the exact last-writer-wins failure this project is trying to eliminate.

## Your job

You and F5 share one goal: a complete, honest asset table for the July 27 poster. F5 owns the table file. You own DISCOVERY and EXISTENCE VERIFICATION, which is the half that takes the most reading.

Produce, in your handoff, a list of candidate poster assets with these fields filled per asset:
- asset name
- what it shows, in one sentence
- the exact file that produces it (script path, verified to exist)
- the exact data file it reads (verified to exist, with size and mtime)
- exists on disk now: yes or no, with the path you actually checked
- verified or unverified
- the one blocker if unverified

Search at minimum: figures/, figures/poster_exports/, paper/, analysis/, data/, poster_text_draft.md, paper_draft.md, README.md, and any *.png/*.svg/*.pdf under the repo that looks like a result.

For every figure you find, trace it backward: which script generated it, and which data file did that script read. Open the script and read its input path live rather than inferring from the filename. A figure whose generating script or input data cannot be located is an ORPHAN and must be labeled that way.

Mark any asset that depends on a rendered MPM video as BLOCKED. Do not let BLOCKED items gate anything else.

## Live facts confirmed tonight, use rather than re-derive

- README.md:69 and paper_draft.md:89 carry the LIVE divergence figure: 39.1 percent agreement, 9 of 23 conditions, 14 divergences. The older 16 divergence / 30.4 percent figure is superseded, and every surviving mention is already correctly labeled as provisional, stale, or superseded. Do not re-open that question.
- paper_draft.md Section 4 exists at lines 79 to 145 with subsections 4.1 through 4.5. It is not a stub.
- IMPORTANT CAVEAT to attach to any asset resting on Section 4.1 or 4.2: commit af95d17 records that can_it_ford_L2.py generated those figures under a stale vehicle mass, and states they need regeneration rather than silent correction. Flag every asset that inherits this.
- Three stale git worktrees exist under .claude/worktrees/ holding frozen copies of paper_draft.md, README.md and PROVISIONAL_STATUS.md. Do not treat anything under .claude/worktrees/ as a live asset. Exclude that path from your search and say you did.
- PROVISIONAL_STATUS.md is deny-listed for reading in .claude/settings.json. If you try to read it you will be denied. That is expected, not an error. Work around it.
- figures/hero_shot_test.png exists but a prior pane judged that its water renders as disconnected pastel cubes rather than a connected fluid body, failing this project's own rendered-output rule. Verify that judgment yourself by looking at the file before repeating or contradicting it.
- The GitHub repo went PRIVATE on 2026-07-23, so any QR code asset pointing at the public repo URL would resolve to 404 for a poster viewer. Check whether figures/qr_codes/ exists and flag accordingly.

## Output

Write .claude/handoffs/2026-07-24_canitford-C5.md with your candidate asset list in the field format above, clearly enough that F5 can fold each row straight into the table without re-deriving it.

Write it as soon as you have a solid first pass rather than holding everything until the end, because F5 is polling for your file and will fold in what it finds. If you learn more after writing, append a clearly marked second section rather than rewriting the first.

When finished, run: tmux wait-for -S canitford-C5-done
