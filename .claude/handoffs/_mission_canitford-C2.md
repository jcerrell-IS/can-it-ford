# Mission: pane C2, canitford:0.2, 2026-07-24 evening

You are pane C2. Read this file in full, then execute it. Do not summarize it before acting.

## Hard constraints, read before anything else

These override any general instruction you may infer from project docs.

1. NEVER delete, move, rename, or edit anything you find during this audit. Produce a table and a flag list only. This is the directory-provenance-audit skill's own explicit constraint and it is absolute tonight.
2. DO NOT run git commit. DO NOT run git push. Fourteen contexts currently share the single working tree at /Users/josie/can-it-ford: these twelve tmux panes plus two live Claude Code sessions named Vista and Vista (fork) writing to this repo right now. One designated committer exists tonight and it is not you.
3. Local main is 2 commits ahead of origin/main (af1db6d, 85e2252) under an explicit push hold.
4. Do not import warpmpm, do not run a simulation, do not request idev or GPU. Vista's warpmpm/vehicle.py is mid-edit by another session and gh-dev job 864505 is occupied.
5. Verify live. Never restate a claim from a doc, a memory, a prior chat, or a summary as current fact. If you have not checked live, say so explicitly.
6. No em-dashes anywhere. No inline comments or docstrings in any language.
7. Pane C1 is running concurrently and owns .claude/settings.json and the CLAUDE.md currency audit. Do not touch settings.json. If your findings imply a settings change, write it in your handoff for C1 or a later session to apply.

## Already resolved, do not report these as open

Verified live tonight before this mission was written. Confirm live if you cite them, but do not present them as open findings.

- The embedded nested repo can-it-ford/can-it-ford already has a real merged fix: commit daf453e, "Remove accidentally-committed embedded git repository, add to gitignore", confirmed on origin/main. What may remain is an untracked leftover DIRECTORY, which is a much lower-stakes cleanup than the original gitlink bug. Confirm which situation is actually live now and describe it precisely.
- resume_pane.sh's Vista-hardcoding bug already has a real fix: commit 6b58811, "Fix resume_pane.sh: require explicit fallback environment instead of hardcoded Vista default". Verify live whether it now handles a non-Vista pane correctly rather than reporting it as still open and flag-only.
- The W&B key rotation question: a recent session reports the rotation done and verified against real services on all three machines. Do not spend real effort re-deriving it. If you check at all, note that this project has proven that claude mcp list showing Connected only confirms an HTTP handshake, not that the bearer token works.

## Your task

Load the directory-provenance-audit skill and follow its workflow exactly.

PART 1, path reconciliation. Establish live whether each of these exists and what it actually contains:
- can-it-ford/can-it-ford, the embedded nested repo, previously frozen at ca91b123a
- ~/can-it-ford-BACKUP-before-history-purge, a real backup outside the project root, reported to hold uncommitted edits to README.md, SESSION_STATE.md, paper_draft.md and vehicle_params.py that never landed in real history
- /home1/11603/jcerrell0629/can-it-ford on Vista, whether it still exists as a real git repo separate from the canonical /work path
- /work/11603/jcerrell0629/ls6/can-it-ford, whether it exists alongside the canonical /work/11603/jcerrell0629/vista/can-it-ford. Two project documents directly disagree on whether this was already resolved, so treat it as open until you confirm live.

Use the GitHub-blob-hash method the skill specifies, not mtime or file size. Pull canonical HEAD state from GitHub, then git hash-object every local copy and compare directly.

For the embedded nested repo specifically: if and only if every file matches canonical, SHOW what rm -rf can-it-ford/can-it-ford would remove. Do not run it. Do not stage it. Show and stop.

PART 2, working-directory confirmation. The deny-rule protection in settings.json cannot reach the BACKUP directory at all, since it sits outside the project root. The only real protection is confirming every pane's actual working directory. Check this explicitly across every currently running pane:
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_current_path}'
Report any pane whose cwd is not /Users/josie/can-it-ford.

PART 3, sensitive-content sweep, skill Section 7. Grep for secret-shaped and personal or health keyword strings across the same directories. Sample and actually READ a handful of real matches before reporting any hit. Domain vocabulary like "diagnostic" in an engineering log produces false positives indistinguishable from a raw grep count. Never print a raw credential value in your output; compare hashes instead.

Known live item worth confirming, from a session earlier tonight: token_setup_template.md is tracked in the repo and records a truncated PAT prefix, github_pat_11CDJE. Truncated, so not usable as a credential, but it is a token fingerprint committed to a repo that was public until July 23. Confirm live whether that string is still in the tracked file, and whether it appears in git history.

## Output

Two files, both required:
- .claude/handoffs/2026-07-24_canitford-C2.md, the flag list and your narrative
- AUDIT_TABLE_2026-07-24.md at the repo root, the reconciliation table itself

Note there is an existing HANDOFF_AUDIT_2026-07-24/ directory at the repo root containing AUDIT_TABLE.md and a byte-identical duplicate pair, "handoff_kb 2/" beside "topics/", about 460 lines duplicated. Check it before writing, so you extend or supersede it deliberately rather than creating a third overlapping artifact by accident. Say which you chose.

When finished, run: tmux wait-for -S canitford-C2-done

## If you finish early

Do not idle and do not invent unrelated work. Filter the next candidate against tonight's three anchors: poster July 27, paper July 31, or one verified rendered physically plausible MPM simulation with a vehicle in it. If it does not serve one of those, write it in your handoff as optional or deferred.
