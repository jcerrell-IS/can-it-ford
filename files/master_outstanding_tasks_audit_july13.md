# Master Outstanding-Tasks Audit — everything given, what's actually confirmed done

Built by going back through every task list I gave in this conversation, checking each
against your actual follow-up screenshots/messages, plus lighter cross-referencing
against recent related chats. Status key:

✅ CONFIRMED DONE — you showed evidence (screenshot/message) this was run
🔄 PARTIAL — some of the batch confirmed, some not
⚠️ UNCONFIRMED — no evidence either way, likely skipped when a new question pulled focus
🚫 SUPERSEDED/INTENTIONALLY GATED — doesn't need doing, or was replaced by later work

**The honest pattern, stated once:** every diagnostic/document-building step got done
thoroughly. Nearly every *deployment* step (put the corrected file where it belongs,
verify it landed, run the archaeology commands, send or explicitly hold the Kumar
message) has no confirmation it actually happened. This isn't a scattered mistake, it's
one consistent shape — each new screenshot pulled attention to the next diagnostic
question before the previous batch's actions were confirmed.

---

## This conversation, in order

### 1. Original 8-pane bug triage plan (`2026-07-13_bug_triage_and_panel_execution_plan.md`)

| Item | Status |
|---|---|
| Pane 0.7: crash isolation test | 🔄 Attempted, failed on wrong path. Corrected commands given later — re-run with the fix not confirmed |
| Pane 0.0: ffmpeg fix + full-scale FloodScene run (target_length=4.66, mass=1390kg) | 🔄 Some FloodScene activity seen (yaw/roll/disp output, CSVs pulled) but the specific full-scale/correct-mass version unconfirmed |
| Pane 0.1: depth sweep at consistent mass | 🔄 Same — sweep CSVs exist (d0p22, d0p38, d0p30) but consistency of mass/scale across them unconfirmed |
| Pane 0.2: bridge scaffold git check + DRIFT_THRESHOLD citation fix in STATUS.md + README audit | ⚠️ Never mentioned again after being assigned |
| Pane 0.3: send Kumar update (gated) + pull stranded CSVs + fix conda + dedupe zshrc + confirm W&B key | 🔄 CSVs pulled ✅. Kumar update explicitly still held (correct — gate hasn't cleared). Conda root cause found (`conda run` not activating) but fix not applied. zshrc dedup — no evidence. W&B key — still unconfirmed after 3+ days across multiple sessions |
| Pane 0.4: consolidated STATUS.md write + Al-Qadami cross-check | Al-Qadami grep ran (correctly empty) ✅. STATUS.md consolidated write ⚠️ unconfirmed |
| Pane 0.5: verification/QA (argparse re-confirm, wandb_backfill diff, git log summary) | ⚠️ No evidence this pane was ever opened |
| Pane 0.6: output pulling + visual QA + SESSION_STATE.md maintenance | ⚠️ No evidence this pane was ever opened |

### 2. First Pane 0.7 diagnostic file

| Item | Status |
|---|---|
| §1: pwd/ls/find sequence | ✅ Done — found the file at `simulation/can_it_ford_L2_mpm.py` |
| §1: `git log --all --follow`, `git show 8d1ea39`/`1d5ad45`/`67915be` | ⚠️ Not confirmed in this conversation (though a *parallel* session did run an equivalent test and found the answer — see cross-chat section below) |
| §1: diff `.bak2`/`.bak4`/`.bak5` against current file | ⚠️ Never confirmed — these backups may still hold information nobody has looked at |
| §2: fix the Mac-shell pane's missing SSH step | ⚠️ Unconfirmed whether that specific pane got fixed |

### 3. Corrected Pane 0.7 sequence (real path) + git-history appendix

| Item | Status |
|---|---|
| Re-run baseline/overlap/mass/combined tests with `simulation/` path | ⚠️ Unconfirmed |
| `echo $SCRATCH` + re-run `find $SCRATCH` | ✅ Confirmed done, screenshot showed real path + still-empty result |
| `git status` / `git rev-parse --is-inside-work-tree` on `/work/11603/jcerrell0629/vista` | ✅ Confirmed — found not a git repo |

### 4. Claude Code vs. chat analysis + prompt template

No hard action items — this was analysis/recommendation. One offer (draft a `SESSION_DIGEST.md` template) was never taken up; you moved to the next topic instead. 🚫 Not a missed task, just an unexercised option.

### 5. Rewritten `bug-triage-protocol` skill + Claude Code setup guide

| Item | Status |
|---|---|
| Upload skill to this Project's Skills (chat-side) | ⚠️ No way for me to verify from here |
| Add orientation block to Vista `CLAUDE.md` (incremental append) | 🚫 Superseded — the file turned out to be somewhere unexpected, so this got folded into the full rebuild instead |
| Copy skill to `~/.claude/skills/bug-triage-protocol/` on Mac | ✅ Confirmed — "total 24" screenshot showed clean single-file install |
| Copy skill to same path on Vista | ⚠️ Never confirmed. Offered again after the Mac check, never taken up |

### 6. CLAUDE.md path investigation (four screenshots, `~/work` vs `~/`, `$HOME` vs `$SCRATCH`, git-repo check)

All confirmed done — this is the one thread where every prescribed diagnostic command was actually run and reported back, screenshot by screenshot, ending in the full 16-screenshot `cat` of the real file. ✅

### 7. Corrected CLAUDE.md (first version) — deployment steps

| Item | Status |
|---|---|
| scp the corrected file to Vista | ⚠️ Unconfirmed — no screenshot shows this |
| Backup + diff + replace on Vista | ⚠️ Unconfirmed |
| Re-verify Track 2 path after replace | ⚠️ Unconfirmed |
| Test whether an existing/new Claude Code session actually reads the updated file | ⚠️ Unconfirmed |

**This is the single most consequential unconfirmed item.** Two full correction passes have now been written for this file and there's no evidence either has actually been placed on Vista yet.

### 8. Cross-session verification (`cross_session_verification_july13.md`)

| Item | Status |
|---|---|
| `cat` the Vista file to check patch status | ⚠️ Unconfirmed |
| `cat` the Mac file (`~/can-it-ford/CLAUDE.md`) to read its real content | ⚠️ Unconfirmed — I still only know that file from a chat summary, never its literal text |
| `wc -l` the skill on both machines | ⚠️ Unconfirmed |
| Decide reconciliation approach (unified vs. deliberately separate) | ⚠️ No answer given yet |

### 9. Full deployment playbook (`full_deployment_playbook_july13.md`)

| Item | Status |
|---|---|
| Section 2: check for a second Vista `CLAUDE.md` inside `can-it-ford/` itself, run the `cd can-it-ford && claude` echo test | ⚠️ This was the explicit "Do This Now" — never reported back. Still an open question that gates several later decisions |
| Sections 3-9 (patch application, skill reconciliation, duplicate sweep, LS6 check, cross-machine consistency check) | ⚠️ All unconfirmed |

---

## Cross-chat — lighter treatment, I only have summaries for these, not full transcripts

### "Terminal setup and deployment tasks for Kumar prep" (04:36am, same night, different chat)

- The box-size isolation test that answers §1 above: **run, and answered** — box size cleared, domain-widening commit implicated. This is genuinely done, just not in this conversation's thread.
- `viability_audit.py` glob bug: **found**, fix-applied status not confirmed even in that chat's own summary.
- Conda `which python3` root cause: **found** (resolves to system Python, `conda run` not activating), the actual fix (getting `conda run` to activate properly) not confirmed as applied.

### "Cornell notes on debugging pipeline and research gaps" (08:30am, most recent chat in the project)

- Mac `CLAUDE.md` rebuild: **confirmed installed**, byte-for-byte verified (10,809 bytes).
- Prescribed next step there: open a new Claude Code session and ask it "what's the current goal and what are you not supposed to decide on your own" — unconfirmed whether this was actually done.

### Older, still-flagged-and-reflagged items (July 10 and earlier)

- **W&B API key (commit 50eff29):** flagged in at least three separate sessions across three days (July 10's "PhysGaussian bridge scaffold" chat, tonight's original triage, tonight's cross-verification). Never confirmed revoked. This is the single oldest unresolved item in the whole project and the one with the clearest security stakes.
- **Kumar's July 9 7:35pm Slack message about the ply scene:** flagged as unanswered as of July 10. Current status unknown — check directly rather than assume either way.
- **Cheng-Hsi's offer to share a real truck splat file (~50MB):** flagged as never followed up on, as of July 10. May now be moot given Track 1's FloodScene mesh is confirmed working — worth a quick mental check on whether it's still worth pursuing before spending time on it.

---

## Final verdict, prioritized — what to actually do next

Given everything above, the tasks with the highest ratio of (already fully specified) to (never confirmed done) are:

1. **Deploy the CLAUDE.md that's actually attached to this message** (`CLAUDE_md_FINAL_july13.md`) to Vista — this has been written twice now and never confirmed placed anywhere.
2. **Run the Section 2 check from the deployment playbook** — whether a second Vista `CLAUDE.md` exists inside the repo. This gates whether step 1 is even sufficient.
3. **Diff the `.bak2`/`.bak4`/`.bak5` files** — cheap, never done, might shortcut the whole crash investigation if one of them already contains a working fix.
4. **Confirm the W&B key revocation** — oldest open item in the project, directly security-relevant, keeps getting reflagged without anyone actually checking wandb.ai.
5. Everything else in this document, roughly in the order it's listed above.

Given how much has piled up, I'd genuinely recommend treating this list itself as the next input to `bug-triage-protocol` — it's already triaged, just needs execution, not more analysis.
