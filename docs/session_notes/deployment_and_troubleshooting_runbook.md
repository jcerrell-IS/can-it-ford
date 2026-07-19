# Deploying the Canonical CLAUDE.md + Skill Everywhere, With Troubleshooting

Covers Vista, Mac, and LS6. Every phase has a "what to do if this doesn't go as expected" branch — read those before coming back to ask, they cover the failure modes that actually happen in this project.

---

## Phase 0 — Recon before touching anything (do not skip)

The canonical file was built from a summary of the Mac's `CLAUDE.md`, not its literal content. Confirm before overwriting.

```bash
hostname; pwd
```

**On Mac:**
```bash
cat ~/can-it-ford/CLAUDE.md
wc -c ~/can-it-ford/CLAUDE.md
```

**Troubleshooting Phase 0:**
| Result | Meaning | Next step |
|---|---|---|
| `No such file or directory` | The other session's version never actually got moved into place, or is at a different path | `find ~/can-it-ford -maxdepth 2 -iname "CLAUDE.md"`, `find ~ -maxdepth 3 -iname "CLAUDE_md*"` for a stray Downloads copy |
| File exists but content looks nothing like the "CURRENT GOAL / stop-and-ask / Bug 1-3" description | The summary I have is inaccurate or a further edit happened since | Paste the actual content back here before proceeding — do not let me guess again |
| File matches the description closely | Canonical file below is a safe merge | Proceed to Phase 1 |
| `git status` inside `~/can-it-ford` shows `CLAUDE.md` as modified/staged, uncommitted | Overwriting risks losing uncommitted work from that other session | Run `git diff CLAUDE.md`, decide whether to commit it first before replacing |

---

## Phase 1 — Reconcile, if Phase 0 surfaced real differences

If the real Mac file matches what I described closely: skip to Phase 2, the canonical file already accounts for it.

If it genuinely differs: paste the real content here. Do not proceed to overwrite based on a guess — this is exactly the mistake that produced two divergent files in the first place.

---

## Phase 2 — Settle the skill collision

**On both Mac and Vista:**
```bash
ls -la ~/.claude/skills/bug-triage-protocol/
wc -l ~/.claude/skills/bug-triage-protocol/SKILL.md
head -20 ~/.claude/skills/bug-triage-protocol/SKILL.md
```

**Troubleshooting Phase 2:**
| Result | Meaning | Next step |
|---|---|---|
| Directory doesn't exist on one machine | Never installed there, not a collision | Fresh install, Phase 4 |
| File exists, description block mentions "nine named failure classes" or "six-question rabbit-hole checklist" | This is the other session's version | Decide: keep it as-is, replace with mine, or ask me to fold its 9-class list into mine as an addition (I'd need its actual content to do that faithfully, not the summary) |
| File exists, matches what I built earlier tonight (sections 0-7, dynamic N-panel logic) | Mine survived | No action needed here |
| Byte counts differ between Mac and Vista even though both "look like mine" | One is an older draft | `diff` them directly, keep the newer/more complete one, redeploy to the other |

**Default recommendation if you don't want to inspect both in detail right now:** standardize on the version I built in this conversation (I have its complete, verified content — the other one I only have a summary of). If you later want the 9-failure-class list folded in, show me that file directly and I'll merge it properly instead of guessing.

---

## Phase 3 — Deploy the canonical CLAUDE.md to Vista

**On Mac, confirm the download, then transfer:**
```bash
ls ~/Downloads/ | grep -i CLAUDE_md_CANONICAL
scp ~/Downloads/CLAUDE_md_CANONICAL_july13.md jcerrell0629@vista.tacc.utexas.edu:~/CLAUDE_md_CANONICAL_july13.md
```

**On Vista:**
```bash
ssh jcerrell0629@vista.tacc.utexas.edu
cp /work/11603/jcerrell0629/vista/CLAUDE.md /work/11603/jcerrell0629/vista/CLAUDE.md.bak_$(date +%Y%m%d_%H%M)
diff /work/11603/jcerrell0629/vista/CLAUDE.md.bak_$(date +%Y%m%d_%H%M) ~/CLAUDE_md_CANONICAL_july13.md | head -100
```
Read the diff. If it looks right:
```bash
cp ~/CLAUDE_md_CANONICAL_july13.md /work/11603/jcerrell0629/vista/CLAUDE.md
tail -20 /work/11603/jcerrell0629/vista/CLAUDE.md
```

**Troubleshooting Phase 3:**
| Result | Meaning | Next step |
|---|---|---|
| `scp: No such file or directory` (local side) | Filename mismatch, likely a `(1)` suffix from a repeat download | `ls ~/Downloads/ \| grep CLAUDE` to find the real name, retry with that |
| `scp` hangs before a password prompt | Wrong username/host, or a stalled connection | Ctrl-C, verify `jcerrell0629@vista.tacc.utexas.edu` exactly, retry |
| `scp` succeeds but file is 0 bytes or truncated on Vista | Transfer was interrupted (network blip, MFA timeout mid-transfer) | Delete the partial file, re-run scp |
| `diff` shows far more differences than expected, or looks like it's comparing against a version you don't recognize | The Vista file changed again since your last check | Stop, read the current file fully with `cat`, don't blindly overwrite |
| `cp` succeeds but `tail` shows old content | Wrong destination path, likely a typo | `pwd` to confirm you're not accidentally inside `can-it-ford/` when the standalone file lives one level up |

---

## Phase 4 — Deploy the canonical CLAUDE.md to Mac (git-tracked this time)

```bash
cp ~/can-it-ford/CLAUDE.md ~/can-it-ford/CLAUDE.md.bak_$(date +%Y%m%d_%H%M)
cp ~/Downloads/CLAUDE_md_CANONICAL_july13.md ~/can-it-ford/CLAUDE.md
cd ~/can-it-ford
git status
git diff CLAUDE.md
```

If it looks right:
```bash
git add CLAUDE.md
git commit -m "Reconcile CLAUDE.md: unified canonical version, corrects stale crash root-cause claim"
git pull --rebase
git push
```

**Troubleshooting Phase 4:**
| Result | Meaning | Next step |
|---|---|---|
| `git diff` shows the file wasn't tracked before | This is the first time it's been committed | Fine, `git add` will start tracking it now |
| `git pull --rebase` reports a conflict | Someone (a parallel Claude Code session) pushed a different `CLAUDE.md` change in the meantime | Do NOT force-resolve blindly — read both versions, this is the exact collision Finding 2 warned about, happening live |
| `git push` rejected, "fetch first" | Same as above, someone pushed since your last pull | `git pull --rebase` again, then retry push |
| File not found at `~/can-it-ford/CLAUDE.md` at all in Phase 0 | It may live at repo root under a different name, or genuinely doesn't exist yet | `find ~/can-it-ford -iname "*CLAUDE*"` |

---

## Phase 5 — Deploy the skill everywhere it's missing

**Mac:**
```bash
mkdir -p ~/.claude/skills/bug-triage-protocol
cp ~/Downloads/bug-triage-protocol-SKILL.md ~/.claude/skills/bug-triage-protocol/SKILL.md
```

**Vista (from Mac):**
```bash
scp ~/Downloads/bug-triage-protocol-SKILL.md jcerrell0629@vista.tacc.utexas.edu:~/.claude/skills/bug-triage-protocol/SKILL.md
```
If `~/.claude/skills/bug-triage-protocol/` doesn't exist yet on Vista, `scp` won't create it — SSH in first and `mkdir -p` before retrying.

**LS6, only if you run Claude Code natively there:**
```bash
scp ~/Downloads/bug-triage-protocol-SKILL.md jcerrell0629@ls6.tacc.utexas.edu:~/.claude/skills/bug-triage-protocol/SKILL.md
```
`ssh jcerrell0629@ls6.tacc.utexas.edu` first if the target directory doesn't exist yet, same `mkdir -p` pattern.

**Troubleshooting Phase 5:**
| Result | Meaning | Next step |
|---|---|---|
| `scp: /home/.../skills/bug-triage-protocol/SKILL.md: No such file or directory` | Parent directory doesn't exist on that machine yet | SSH in, `mkdir -p ~/.claude/skills/bug-triage-protocol`, retry the scp |
| Permission denied | Unusual for your own home directory — check `whoami` matches `jcerrell0629`, not some other context | If genuinely denied, this needs TACC support, not a workaround |
| File lands but is a different size than the Mac original | Partial transfer | `wc -c` both sides, compare, redo if mismatched |

---

## Phase 6 — LS6's CLAUDE.md is a SEPARATE decision, do not copy the canonical file there

LS6 does gsplat work, not MPM. Per this project's own "never mix these" cluster rule, copying the Vista/Mac MPM-focused canonical file to LS6 would actively mislead a Claude Code session running there.

```bash
ssh jcerrell0629@ls6.tacc.utexas.edu
find ~ -maxdepth 3 -iname "CLAUDE.md" 2>/dev/null
```

**Troubleshooting Phase 6:**
| Result | Meaning | Next step |
|---|---|---|
| Nothing found | No CLAUDE.md exists on LS6 yet | Only create one if you actually run Claude Code natively on LS6 — if you only SSH there manually or via Claude Code on the Mac reaching out, skip this entirely |
| Found, gsplat-focused content | Already correctly scoped | Leave it alone, don't touch it as part of this reconciliation |
| Found, but mentions the MPM crash / Track 2 content | Someone copied the wrong file here previously | Flag it back to me, this needs its own scoped rewrite, not a copy-paste fix |

---

## Phase 7 — Confirm every location actually reads correctly

**On each machine, in the relevant directory, start a fresh Claude Code session and ask directly:**
```
What's the current goal, what are you not supposed to decide on your own, and what's the status of the Track 2 CUDA crash?
```

**Troubleshooting Phase 7:**
| Response | Meaning | Next step |
|---|---|---|
| Echoes the rendered-video goal, the stop-and-ask list, and says box size/vehicle-position/argparse are ruled out with domain bounds as the live hypothesis | Working correctly | Done for that machine |
| Still says vehicle mass ~1450kg without caveat, or describes the overlap fix as unresolved | Reading a stale cached/old session context, not the new file | Start a genuinely fresh session (not just a new message in an old one), or ask it to explicitly re-read CLAUDE.md |
| Doesn't mention the skill when you describe a multi-bug situation | Skill isn't loading, either not installed at that path or description text isn't matching | `ls -la ~/.claude/skills/` to confirm the folder name and file name exactly match `bug-triage-protocol/SKILL.md` |

---

## General troubleshooting table — the recurring error classes in this project

| Error text contains | Likely cause | First move |
|---|---|---|
| `No such file or directory` (local) | Wrong local path or placeholder text typed literally | `ls`/`find` locally first |
| `No such file or directory` (remote, after connecting) | Remote path wrong or target directory doesn't exist | SSH in separately, `ls`/`mkdir -p` before retrying |
| `Permission denied` on your own paths | Unusual, check `whoami` | If genuine, TACC support, not a workaround |
| `Permission denied` on `/scratch/10386/lsmith9003` or `/work/10386/lsmith9003` | Expected, it's Luke's space | Slack Luke, don't debug |
| `git` conflict or rejected push | A parallel session touched the same file | Read both versions before resolving, don't force |
| Command hangs, no prompt | Network/VPN or TACC-side issue | Check TACC status page, retry in a few minutes |
| File present but wrong size | Interrupted transfer | Redo the transfer, don't assume it's fine |
