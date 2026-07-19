# Cross-Session Verification — July 13, morning

Every claim below is sourced to a specific chat, checked via `recent_chats` and `conversation_search`, not asserted from memory. Written because a single-source "corrected" file (mine, written ~3:43am) turned out to already be stale by ~1 hour against work happening in parallel.

---

## 1. Crash root cause — CORRECTION to what I wrote earlier tonight

**What my corrected CLAUDE.md said:** the water/vehicle overlap fix (commit 8d1ea39) might need re-deriving for the new box size; framed as an open, untested hypothesis alongside the mass bug.

**What's actually been confirmed since (source: "Terminal setup and deployment tasks for Kumar prep," 04:36am):**
- Isolation test run: old box (1.0×1.6×1.5m) reverted, domain kept widened. Crash still happened, identical.
- Conclusion: **"Box size is cleared. The domain-widening commit itself is the regression."**

**Source: "Cornell notes on debugging pipeline and research gaps," 08:30am (most recent chat in the project):**
> "Ruled out: grid density, domain padding, box size, vehicle position, argparse. Still open."

**Correct current status:** grid_density, domain padding, box size, vehicle position (i.e., the overlap hypothesis), and argparse are all ruled out individually. The domain bounds themselves — `lower_bound=(-2.5,-1.0,-0.1)`, `upper_bound=(4.5,1.0,2.5)` — are the live suspect. Mass (rho=604, still uncorrected) has NOT been ruled out or in — it's a separate, still-open bug, not yet tested in combination with the domain finding.

**Action needed:** the Vista CLAUDE.md's "VISTA MPM TASK CONTEXT" section needs another pass replacing the "check git show 8d1ea39" framing with this ruled-out list and the domain-bounds hypothesis.

---

## 2. Two CLAUDE.md files now exist

| | Path | Machine | Built by | Structure |
|---|---|---|---|---|
| Mine | `/work/11603/jcerrell0629/vista/CLAUDE.md` | Vista | This conversation, ~3:43am | Preserves original file structure, "B01-B15" bug IDs |
| Theirs | `~/can-it-ford/CLAUDE.md` | Mac | "Cornell notes..." session, confirmed installed ~3:25am, session logged 08:30am | Rebuilt from scratch, "Bug 1/2/3" + "Cluster A-D" IDs, has a "CURRENT GOAL" section and a "stop-and-ask" list preventing any one session from deciding B11 (track reconciliation) unilaterally |

Not a literal overwrite collision (different files, different machines) but a real content-divergence risk — a Claude Code session started from Vista and one started from the Mac repo now read different framings of the same facts. Needs reconciling before either is trusted as sole source of truth.

---

## 3. Possible skill collision

Source, same Cornell-notes session: a `bug-triage-protocol` skill was built there too — "nine named failure classes... six-question rabbit-hole checklist... scoped to Claude Code only." This is structurally different from the skill built in this conversation (generalized for chat + Claude Code, 0-7 sections, dynamic N-panel logic). If both were installed at `~/.claude/skills/bug-triage-protocol/SKILL.md`, one silently overwrote the other. Needs a direct check on disk, not an assumption either way.

---

## 4. New finding, not previously tracked anywhere tonight

`viability_audit.py` globs `particles_d*.npz`. This matches `particles_d1p0_v3p0.npz` but does **not** match `particles_mpm_*.npz` — meaning every MPM-track output file has been invisible to the audit script this whole time. Source: 04:36am session, direct code read. Root cause identified; fix-applied status unconfirmed.

---

## 5. Resolved from "still open"

Bug 8 (conda/trimesh on Mac) has a confirmed cause: `conda run -n can-it-ford which python3` resolves to `/opt/homebrew/bin/python3` (system Python), not the environment's own interpreter — `conda run` isn't actually activating the environment. Source: 04:36am session.

---

## 6. Resolved ambiguity

Mass target: **1390kg**, confirmed consistently across both the 04:36am and 08:30am sessions ("~1390 kg target," "7255 kg instead of the ~1390 kg target"). The 1450kg alternative I'd left open should be dropped.

---

## Reconciliation plan — do this before trusting either CLAUDE.md fully

1. **On Vista:** `cat /work/11603/jcerrell0629/vista/CLAUDE.md` — check if the VISTA MPM TASK CONTEXT section still says "check git show 8d1ea39" or has already been updated with the ruled-out list. If not updated, apply Finding 1's correction.
2. **On Mac:** `cat ~/can-it-ford/CLAUDE.md` — read the actual "CURRENT GOAL" and "stop-and-ask" content directly rather than trusting this summary of it.
3. **Diff the two files' bug-status sections against each other** — reconcile any place they actually disagree (not just labeling differences) before either is used as sole source of truth for a new Claude Code session.
4. **Check `~/.claude/skills/bug-triage-protocol/SKILL.md` on both machines** — `wc -l` and `head -20` each to see which version is actually installed where.
5. **Add the `viability_audit.py` glob bug to whichever master bug list survives reconciliation** — it's in neither of my documents from tonight.
