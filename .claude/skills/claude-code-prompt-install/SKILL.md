# Claude Code prompt: install the flood-mpm-debugging-reference skill, once, via git

Run this on whichever machine has your current `can-it-ford` working copy with the least uncommitted drift, Vista is the most likely candidate since Kumar reads that repo directly. This should NOT be run separately on all three machines, that recreates the exact per-machine sync problem this project already got burned by once with CLAUDE.md and `.gitignore`. One commit, one push, then a plain `git pull` on the other two machines.

Two files are attached to this conversation:
- `flood-mpm-debugging-reference_SKILL.md`
- `CLAUDE_md_addendum.md`

Paste everything below the line into a Claude Code session on your chosen machine.

---

I need to install a new repo-level skill and update CLAUDE.md, committed to git so it reaches Vista, LS6, and my Mac through a normal `git pull`, not copied by hand to each machine separately.

## Steps

1. Confirm you're in the actual `can-it-ford` repo root, and check for uncommitted changes before touching anything:
   ```
   pwd
   git status
   ```
   If there's unexpected uncommitted work, stop and tell me what it is before proceeding, don't commit over it blindly.

2. Confirm `CLAUDE.md` is actually tracked by git here, not gitignored again:
   ```
   git check-ignore -v CLAUDE.md
   ```
   This should produce no output. If it produces output, CLAUDE.md is being ignored again, stop, tell me, and don't proceed until that's fixed, since that's the exact failure mode that already cost this project once.

3. Create the skill directory and file:
   ```
   mkdir -p .claude/skills/flood-mpm-debugging-reference
   ```
   Write the contents of `flood-mpm-debugging-reference_SKILL.md` to `.claude/skills/flood-mpm-debugging-reference/SKILL.md`, exactly as provided, don't paraphrase or shorten it.

4. Append the contents of `CLAUDE_md_addendum.md` to the end of the existing `CLAUDE.md` in the repo root. Read the current `CLAUDE.md` first to confirm you're not duplicating a section that's already there.

5. Diff before committing, confirm exactly what's changing:
   ```
   git diff CLAUDE.md
   git status
   ```

6. Commit and push:
   ```
   git add .claude/skills/flood-mpm-debugging-reference/SKILL.md CLAUDE.md
   git commit -m "add flood-mpm-debugging-reference skill and CLAUDE.md pointer"
   git push
   ```

7. Report the commit hash and confirm the push succeeded, don't just say done.

## Style rules that apply

No inline comments, no docstrings, in anything you write. Give exact commands, not vague suggestions. Show actual command output, not a summary of what you expect it to say.

## After this

On Vista and LS6 (whichever wasn't used for this), the next Claude Code session there should start with:
```
cd /work/11603/jcerrell0629/vista/can-it-ford && git pull
```
or the equivalent LS6 path, to pick up both files. That single `git pull` is the entire deployment step for the other two machines, nothing else needs to be copied by hand.
