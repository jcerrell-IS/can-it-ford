# Mission: pane C1, canitford:0.1, 2026-07-24 evening

You are pane C1. Read this file in full, then execute it. Do not summarize it before acting.

## Hard constraints, read before anything else

These override any general instruction you may infer from project docs.

1. DO NOT run git commit. DO NOT run git push. Fourteen contexts currently share the single working tree at /Users/josie/can-it-ford: these twelve tmux panes plus two live Claude Code sessions named Vista and Vista (fork) that are writing to this repo right now. Concurrent commits into one shared tree produce unreadable history. One designated committer exists tonight and it is not you. If you produce something that deserves a commit, show the diff in your handoff file and stop there.
2. Local main is 2 commits ahead of origin/main (af1db6d, 85e2252) under an explicit push hold. Any push of main would send them.
3. Do not import warpmpm, do not run a simulation, do not request idev or GPU. Vista's warpmpm/vehicle.py is mid-edit by another session and gh-dev job 864505 is occupied.
4. Verify live. Never restate a claim from a doc, a memory, a prior chat, or a summary as current fact. cat, grep, or git log it first. If you have not checked live, say so explicitly.
5. No em-dashes anywhere. No inline comments or docstrings in any language.
6. Before overwriting or deleting any file, check what is already there first.
7. Pane C2 is running concurrently on a related audit. Do not edit files C2 owns. C2 produces AUDIT_TABLE_2026-07-24.md and its own handoff. If you both want the same file, yours yields and you note it.

## Already resolved, do not re-derive or report as open

Verified live tonight before this mission was written. Confirm each against the live file if you intend to cite it, but do not spend a round rediscovering it.

- Yaris mass is RESOLVED at 1100 kg. Commit aa13ac1 (2026-07-23 10:52:47 CDT) explicitly corrected the earlier 1078 kg recommendation from 761ff84 (same day, 05:36:33) on the grounds that 1078 preferred a secondary NCAC webpage annotation over the primary LS-DYNA deck header. Live vehicle_params.py line 83 reads mass_kg 1100.0. This is settled.
- Still genuinely open, do not close it: the VOLUME basis. aa13ac1 retains volume_basis_still_open, collider box 3.5427 m3 versus raw enclosed mesh 6.8185 m3, giving rho 310.50 versus 161.33. Mass is settled, rho is NOT.
- The canonical CLAUDE.md files are already fingerprinted. See the block dated 2026-07-25 03:32 UTC at the top of SESSION_STATE.md: global md5 a954a8e03b76c69e1a491a437048b83c at 2004 bytes, identical on Mac, Vista and LS6; project CLAUDE.md md5 08a4ebac53bc85ebe3e03f7bd423d952 at 3336 bytes. Use those as your starting point rather than re-deriving them, and flag any mismatch loudly since that would mean drift within the last hour.

## Your task

Two parts.

PART 1, CLAUDE.md currency audit. Load the provenance-audit skill and follow its Section 4 exactly. This project has had at least three CLAUDE.md-class candidates historically, a v3 comprehensive from July 13, a Master Instructions v6 from July 7, and a consolidated canonical v3 from July 15, plus whatever is live now. Version numbers alone do not tell you which is newest, read dates and content. Find every CLAUDE.md-class file across the Mac clone, Vista, and LS6. Establish exactly one canonical file. Diff every status claim, parameter value, and DONE marker in it against a live check, not against another document's claim.

Specifically confirm the Safe Resume Protocol text is present in the global CLAUDE.md on each machine. Per the fingerprint above all three now match, so this should pass; report it either way.

PART 2, stale-file exclusion. Execute exclude_stale_files_from_claude_code.md's verification prompt if that file exists, otherwise work from the DEPRECATED list in the project CLAUDE.md's File provenance section. For each candidate path, confirm live whether it actually exists at that exact path. Do not add a deny rule for a path that turns out wrong, because a wrong-path deny rule silently does nothing rather than erroring.

Also specifically try to locate the on-disk filename of "CAN IT FORD MASTER CLAUDE INSTRUCTIONS v6, July 7". The working assumption from a prior search is that it never existed as a file and was only pasted chat text. Confirm that rather than repeating it.

Then merge a permissions.deny array with Read() rules for every confirmed-existing stale path into .claude/settings.json.

IMPORTANT on settings.json: it currently has uncommitted modifications already in the working tree, and it already contains a deny array with seven Read() rules. Read the live file first and preserve everything already there. Add to it, never replace it. Pane C0 is NOT running tonight so you will not collide with it, but the existing uncommitted edits are real work by someone else.

PART 3, one concrete staleness check. Open the live flood-mpm-debugging-reference skill file directly and confirm whether it still states the Yaris mesh weight as 1078 kg open and unresolved with rho 304.28. A prior session reports this was corrected to 1100 kg citing commit aa13ac1. If the live skill file still shows the old unresolved framing, that correction never landed in the one place every pane is told to trust for this number, which is higher leverage than fixing it in any single pane's output. Keep the mass and rho coupling warning in that file intact, correct only the number and its resolved status.

## Output

Write .claude/handoffs/2026-07-24_canitford-C1.md including the single canonical CLAUDE.md path you established, every path you confirmed did or did not exist, the settings.json diff you applied, and the flood-mpm-debugging-reference finding either way.

When finished, run: tmux wait-for -S canitford-C1-done

## If you finish early

Do not idle and do not invent unrelated work. Filter the next candidate against tonight's three anchors: poster July 27, paper July 31, or one verified rendered physically plausible MPM simulation with a vehicle in it. If it does not serve one of those, write it in your handoff as optional or deferred instead of doing it.
