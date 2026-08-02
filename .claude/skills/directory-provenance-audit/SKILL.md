---
name: directory-provenance-audit
description: Use when Josie needs to reconcile duplicate-named files (CLAUDE.md, SESSION_STATE.md, config/data files, scripts, or any repeated filename) scattered across multiple local project directories, backups, git worktrees, or old Mac-profile copies, and determine which copy is canonical using git provenance against the GitHub remote (blob hash), not modification date or file size. Trigger on "organize my project folders", "which copy is canonical", "dedupe my directories", "clean this up for handoff", "audit my directories before a fresh session", or any request to reconcile multiple copies of the same filename across directories. Also sweeps for personal/sensitive/secret content sitting in untracked or loosely-organized locations. Never deletes, moves, or modifies anything — produces a table and a flag list only; the human decides what to remove. Works on any project, not just Can It Ford.
---

# Directory Provenance Audit

## Why this exists

"Which copy is real" questions get answered wrong constantly by trusting mtime or file size — a backup made minutes ago can look "newest" while actually being a stale pre-purge snapshot, and a shorter file isn't necessarily older. The only trustworthy signal is content identity against a known-good reference: the GitHub remote's actual blob hash for that exact path, at the current HEAD of the branch that matters (usually `main`).

This skill borrows its source-tier discipline from `provenance-audit`: GitHub's live blob hash is a T1 primary artifact, a `SESSION_STATE.md` or backup's own claim about itself is T2 at best, and any prior chat summary about "which copy is right" is T3 and does not get to settle this on its own.

## Workflow

1. **Get the target list from the user.** Directories to sweep, and the specific filenames to reconcile (don't guess — ask if either is unclear). Confirm the GitHub repo (`owner/name`) that should be treated as canonical.

2. **Enumerate every occurrence.** Find each target filename across every target directory, recursively, including inside `.git/worktrees` worktree checkouts and any nested/embedded repo folders (a folder containing its own `.git` inside another repo — a real, recurring failure mode, not a hypothetical). Use a single broad `find ... -iname` pass across all directories at once rather than one search per directory, to avoid missing a location nobody thought to check.

3. **Pull canonical state from GitHub, not from a local clone.**
   - `list_commits` (or equivalent) on the default branch, `perPage=1`, to get the current HEAD sha and message. Read the message — it sometimes directly names the incident you're auditing for (e.g. "remove accidentally-committed embedded repo").
   - `search_code` with `filename:<name> repo:<owner>/<repo>` for each target filename to get its exact canonical path(s) and blob sha. A filename can canonically exist at more than one path (an intentionally-archived copy) or have moved paths over time — don't assume there's only one canonical location per filename until you've checked.
   - A bare `git ls-remote HEAD` only gives you a ref-level commit hash. It cannot tell you whether a specific file matches. Don't rely on it alone.

4. **Hash every local copy and compare directly.** `git hash-object <file>` works with or without a surrounding `.git` directory — use it on every located copy, then compare byte-for-byte against the canonical blob sha from step 3. Also capture: size, mtime, and (where the copy sits inside a real git repo) `git remote get-url origin`, current branch, `HEAD` sha, and `git status --short`. Two different reasons a copy can be non-canonical: same repo but wrong commit (stale/branch/worktree), or not the same lineage at all (different project, coincidental filename collision).

5. **Deduplicate mount/grant overlaps before counting anything as a "copy."** If two different granted paths list byte-identical directory contents (check with a raw listing diff), they're the same physical folder granted twice under different names — not two independent copies. Report this explicitly; don't double-count it in the table.

6. **Classify every non-canonical hit with a specific one-line reason**, not a generic "outdated": stale backup, different branch/worktree, superseded path (file moved elsewhere in the repo), orphaned embedded/nested repo, different project entirely (same filename, unrelated lineage), or WIP/in-progress on an active branch. Vague reasoning defeats the point of the audit.

7. **Sensitive-content sweep, same directories.** Grep for secret-shaped strings (`api_key`, `token`, `wandb`, `ghp_`, `sk-`, private-key headers) and personal/health keywords (`therap`, `medicat`, `diagnos`, `prescription`, `mental health`, `ssn`, `panic attack`, `anxiety`, `depress`). **Always sample and read a handful of actual matches before reporting a hit as real** — domain vocabulary (e.g. "diagnostic" in an engineering-debugging log) produces false positives that look identical to genuine personal disclosures in a raw grep count. Report the true hits only, and say plainly when a keyword produced zero real hits despite a high raw count.
   - Check for `.env` / credential-shaped files specifically: confirm not just that they exist, but whether they're actually `.gitignore`d and untracked (`git ls-files` should return nothing for them).
   - Check `git status --short` output for staged (`A`/`M` in the first column) large or raw files — a file about to be committed is a live risk even if it was never a problem before.
   - If the project has a documented prior secret-exposure incident, try to verify current rotation status by comparing a hash of the current value against the historically-exposed value — never print either raw value in the final report, compare hashes only.

8. **Output exactly two things, nothing else:**
   - One table: filename | every path it exists at | canonical (yes/no) | one-line reasoning for every non-canonical copy.
   - A flag list for anything sensitive/secret, each with exact path and why it's risky — no full file content quoted, secrets described by key name only, never by value.

9. **Never delete, move, rename, or edit anything found.** End with a short "recommended next human decisions" list — actions the audit surfaced but did not take. The human decides what to remove.

## Output delivery

For anything beyond a handful of rows, write the table to a file rather than pasting it into chat — an audit like this is a reference document Josie will reopen while deciding what to clean up, not a one-shot answer.
