# Full Deployment Playbook: CLAUDE.md + bug-triage-protocol, Everywhere

Every command below has a "if this doesn't match" branch. Read that before pinging me again for the same category of problem — most "I can't find it" situations fall into one of the patterns in Section 0.

---

## 0. Universal troubleshooting reference — check here FIRST for any unexpected output

| You see | Likely cause | Do this |
|---|---|---|
| `No such file or directory` | Wrong path, or file genuinely doesn't exist yet | `find` broadly before assuming: `find $HOME -iname "<filename>" 2>/dev/null`, then `find /work/11603/jcerrell0629 -iname "<filename>" 2>/dev/null` on Vista |
| `Permission denied` | You're not looking at your own path — likely wandered into Luke's (`lsmith9003`) space or similar | Stop. Run `pwd` and `whoami`. Don't attempt workarounds on anyone else's paths — this is a known house rule. |
| `scp` hangs, no progress | Network/VPN issue, or TACC MFA token expired mid-transfer | Cancel (Ctrl+C), re-run `ssh` alone first to confirm the connection still authenticates, then retry `scp` |
| File exists, but byte count doesn't match what I expect | Usually whitespace/line-ending differences (Mac vs. downloaded), not a real content difference | Compare with `diff`, not just `wc -c`: `diff file1 file2`. If diff is empty, they're the same content. |
| Two files, unsure which is newer/authoritative | Don't guess from memory | `ls -la --time-style=full-iso <both paths>` and trust the timestamp, not which one you remember editing last |
| Command runs but nothing happens / no output at all | You may be on the wrong machine or wrong node type for that command | Run `hostname; pwd` first, always — this is the standing rule from earlier tonight |
| Old duplicate file found somewhere unexpected | Don't `rm` it blindly | `diff` it against the canonical version first, then move (not delete) to an archive folder — matches how the July 7 duplicate audit handled this exact situation |
| Unsure if a skill actually loaded in Claude Code | Don't assume from install location alone | Ask Claude Code directly: "what's in your bug-triage-protocol skill, summarize section 2" — if it can't answer, it didn't load |

---

## 1. The full inventory — every location in scope

| # | Machine | Path | Artifact | Status going in |
|---|---|---|---|---|
| 1 | Vista | `/work/11603/jcerrell0629/vista/CLAUDE.md` | CLAUDE.md | Mine, corrected ~3:43am, needs the Finding-1 patch below |
| 2 | Vista | `/work/11603/jcerrell0629/vista/can-it-ford/CLAUDE.md` | CLAUDE.md (possible second copy) | **Unknown — check Step 2, this determines a lot** |
| 3 | Vista | `~/.claude/skills/bug-triage-protocol/SKILL.md` | skill | Unknown which version is installed |
| 4 | Mac | `~/can-it-ford/CLAUDE.md` | CLAUDE.md | Built by a parallel session ~3:25am, needs the same Finding-1 patch |
| 5 | Mac | `~/.claude/skills/bug-triage-protocol/SKILL.md` | skill | Unknown which version is installed |
| 6 | Mac | old duplicate folders (`~/Desktop/NEW_FORD_FILES/`, `~/Downloads/NEW_FORD_FILES/`, `~/Archive/...`) | possible stale CLAUDE.md copies | Should be archived already per July 7 audit, worth a quick sweep |
| 7 | LS6 | wherever your LS6 workdir is | CLAUDE.md | Not touched tonight, lower priority, quick existence check only |

Work through these in order — 2 and 3 gate everything else on Vista.

---

## 2. Vista, Step A — does Claude Code even need two files here?

```bash
ssh jcerrell0629@vista.tacc.utexas.edu
hostname; pwd
```

```bash
find /work/11603/jcerrell0629/vista/can-it-ford -maxdepth 1 -iname "CLAUDE.md"
```

**If this returns a file:** you have a second, separate `CLAUDE.md` inside the repo itself, distinct from the one at the parent `/work/11603/jcerrell0629/vista/` level. Read it:
```bash
cat /work/11603/jcerrell0629/vista/can-it-ford/CLAUDE.md
```
Compare against the parent one. If they're different documents (not just a copy), you now have a THIRD divergent version, on top of the Vista-parent and Mac-repo ones already found. Paste both back to me before I tell you which one to keep.

**If this returns nothing:** only the parent-level file exists on Vista, matching what we already knew. Proceed to Step B.

**Why this matters:** I genuinely don't know, without you checking, whether a Claude Code session started from *inside* `can-it-ford/` on Vista would pick up the parent directory's `CLAUDE.md` automatically. If it doesn't, and sessions get started from inside the repo (which is the more natural place to work), the corrected file at the parent level may never actually get read. Test this directly rather than trust either of us guessing:
```bash
cd /work/11603/jcerrell0629/vista/can-it-ford
claude
```
Then ask it: "what's in your CLAUDE.md, summarize in 3 bullets." If it echoes back content that matches the parent file, it's finding it fine. If it says it has no CLAUDE.md or gives generic answers, you need a copy placed inside the repo directory too.

---

## 3. Vista, Step B — apply the Finding-1 correction

```bash
grep -n "git show 8d1ea39" /work/11603/jcerrell0629/vista/CLAUDE.md
```
If this returns a line, the file still has the now-outdated overlap-fix framing. Replace it:

```bash
cp /work/11603/jcerrell0629/vista/CLAUDE.md /work/11603/jcerrell0629/vista/CLAUDE.md.bak_finding1
```

Open it in whatever editor you're comfortable with (`nano`, `vim`, or have Claude Code do it in Plan Mode) and replace the paragraph starting "Commit 8d1ea39 (...)" with:

```
- CORRECTED July 13 (was: check git show 8d1ea39 for an overlap fix to re-derive).
  Overlap/vehicle-position has since been tested directly (box reverted to old size,
  domain kept widened) and RULED OUT as the crash cause, along with grid_density,
  domain padding, box size, and the argparse bug individually. Live suspect as of
  July 13 08:30: the domain-widening commit itself (lower_bound=(-2.5,-1.0,-0.1),
  upper_bound=(4.5,1.0,2.5)), independent of box size or vehicle position. Mass
  (rho=604, still uncorrected) has NOT been tested in combination with this and
  remains separately open. Mass target confirmed as 1390kg, not 1450kg — earlier
  ambiguity resolved.
```

Verify:
```bash
tail -20 /work/11603/jcerrell0629/vista/CLAUDE.md
```

---

## 4. Vista, Step C — the skill

```bash
ls -la ~/.claude/skills/bug-triage-protocol/
wc -l ~/.claude/skills/bug-triage-protocol/SKILL.md
head -10 ~/.claude/skills/bug-triage-protocol/SKILL.md
```

**Two ways to tell which version is installed:** mine has `description:` starting "Use this skill whenever Josie pastes a bug list..." and section headers like "## 0. Universal pre-flight" and "## 3. Every pane's command block starts with a state-check." The Cornell-notes version has "nine named failure classes" and a "six-question rabbit-hole checklist" — different section structure entirely.

**If it's the Cornell-notes version:** that one is scoped Claude-Code-only by design; mine works in both chat and Claude Code. Decide which behavior you actually want here — if you want both scopes covered, you may want to merge rather than pick one. Tell me which sections of each you want and I'll build a merged version rather than you losing either one's content.

**If it's mine:** confirmed intact, no action needed here.

**If the directory is empty or doesn't exist:**
```bash
mkdir -p ~/.claude/skills/bug-triage-protocol
```
Then re-run the scp from your Mac (Section 5 below has the exact command).

---

## 5. Mac, Step A — locate and patch the repo's CLAUDE.md

```bash
hostname; pwd
cat ~/can-it-ford/CLAUDE.md
```

Read it fully this time — don't trust the chat summary of what it contains. Check specifically:
```bash
grep -n "8d1ea39\|ruled out\|1450\|1390" ~/can-it-ford/CLAUDE.md
```

Apply the same Finding-1 correction from Section 3 here if this file also has the stale overlap-fix framing — same replacement text, same backup-first pattern:
```bash
cp ~/can-it-ford/CLAUDE.md ~/can-it-ford/CLAUDE.md.bak_finding1
```
Then edit and verify the same way.

**If this file is tracked by git** (unlike the Vista parent-level one):
```bash
cd ~/can-it-ford
git status CLAUDE.md
```
If it shows as tracked, commit the correction:
```bash
git add CLAUDE.md
git commit -m "Correct crash-cause framing: overlap ruled out, domain bounds implicated, mass target confirmed 1390kg"
git pull --rebase
git push
```
If it shows as untracked or the repo says "not a git repository," skip the git steps — same as the Vista file.

---

## 6. Mac, Step B — the skill

```bash
ls -la ~/.claude/skills/bug-triage-protocol/
wc -l ~/.claude/skills/bug-triage-protocol/SKILL.md
```

If you need to (re)install mine specifically:
```bash
mkdir -p ~/.claude/skills/bug-triage-protocol
```
Download `bug-triage-protocol-SKILL.md` again if needed (check `~/Downloads/` for a `(1)` suffix first), then:
```bash
mv ~/Downloads/bug-triage-protocol-SKILL.md ~/.claude/skills/bug-triage-protocol/SKILL.md
```

Same decision as Vista Section 4 applies: if the Cornell-notes version is what's actually there, decide keep/replace/merge before overwriting.

---

## 7. Mac — sweep for stale duplicates

```bash
find ~/Desktop ~/Downloads ~/Archive -iname "CLAUDE.md" 2>/dev/null
```

**If anything turns up outside `~/can-it-ford/`:** don't delete on sight. Diff it against the current canonical file:
```bash
diff <found_path> ~/can-it-ford/CLAUDE.md
```
If it's an old, already-archived duplicate (per the July 7 cleanup), leave it in the Archive folder as historical record — the July 7 audit already established archiving over deleting as the house pattern. If it's sitting somewhere live (Desktop, Downloads, not Archive) and could plausibly get picked up by a Claude Code session started from the wrong directory, move it into Archive explicitly:
```bash
mkdir -p ~/Archive/stale_claude_md_july13
mv <found_path> ~/Archive/stale_claude_md_july13/
```

---

## 8. LS6 — quick existence check only

```bash
ssh jcerrell0629@ls6.tacc.utexas.edu
find $WORK -maxdepth 2 -iname "CLAUDE.md" 2>/dev/null
find $HOME -maxdepth 2 -iname "CLAUDE.md" 2>/dev/null
```

Not touched by tonight's MPM work at all — if nothing turns up, that's expected, not a problem. Only worth building one here if you're about to start doing gsplat debugging work through Claude Code natively on LS6. Lower priority than everything above.

---

## 9. Final cross-check — the thing that actually matters

Once 1-8 are done, the real test isn't "does the file exist" — it's "do all of them agree." Run this same question against Claude Code from each location and compare answers:

> "What's the current status of the CUDA_ERROR_ILLEGAL_ADDRESS crash — what's been ruled out, and what's the live hypothesis?"

Ask it on Vista (from the parent directory, and from inside `can-it-ford/` if Step 2 found a second file there), and on the Mac. **All answers should mention the domain-widening/bounds hypothesis and explicitly say overlap and box size are ruled out.** If any location gives a different answer, that file didn't get the Finding-1 patch — go back and apply it there specifically.

---

## 10. General rule for next time you can't find something

1. `hostname; pwd` first, always — confirms which machine/location you're actually asking about.
2. `find` broadly (`$HOME`, then `/work/11603/jcerrell0629`, then `$SCRATCH`) before concluding something doesn't exist.
3. Compare files with `diff`, not byte counts or memory of what you last edited.
4. If a Claude Code session's answer seems wrong, ask it to literally quote the section it's drawing from — this tells you whether it's reading a stale file, no file, or the right one but misremembering.
5. Only then come back and ask — with the actual command output pasted, not a description of what happened.
