# Parallel Terminal Plan, Self-Audit, and Validation Tests, July 13 later

## Part 1, honest self-audit first, before prescribing anything new

You asked me to be skeptical of my own reasoning across this thread, not just the
code. Here is that, done straight, not defensively.

**The real blind spot:** every check in this entire thread has been Vista, Mac, and
GitHub. Nobody, including me, ever suggested checking HuggingFace, W&B beyond the key
itself, Overleaf, or DesignSafe as live external state until this message. That's a
genuine gap in my own coverage, not just yours. The same failure pattern that caused
three false "MPM works" claims (trusting a written summary instead of live state)
applies just as much to these platforms as it did to local files, and I hadn't
extended the same discipline there.

**A second, smaller gap:** the W&B key rotation was confirmed as "old key revoked, new
key set as an environment variable," but nobody has actually run a live
`wandb.login()` call end to end to confirm the new key works and the project's run
history is intact. Env var being set correctly is not the same as the key being
valid.

**A third gap:** the README lists `designsafe-staging/` as a real directory in the
repo structure. Nobody has confirmed whether anything from it was ever actually
uploaded to designsafe-ci.org itself, only that the DOI timing was deferred. Deferred
DOI publication and "nothing has been touched on the DesignSafe side" are two
different claims, and only the first has been verified.

**What this does NOT mean:** it doesn't mean anything already verified (crash cause,
mass bug, mesh scale, skill fork, CLAUDE.md deployment) needs re-checking, those were
checked against live state with hard evidence (md5 hashes, verbatim grep output, exit
codes) and hold up. This is specifically about the platforms nobody looked at yet.

---

## Part 2, what's safe to run right now, in parallel, without touching the live session

The Claude Code session from the last several messages is mid-Phase-8: writing
`docs/session_notes/2026-07-13_phase7_findings.md`, sharpening CLAUDE.md's mesh
section, checking off STATUS.md line 191, and about to `git status`/commit. **Do not
open a new pane that touches any of those same files** (CLAUDE.md, STATUS.md,
README.md, or anything under `docs/session_notes/`) until that session reports back
clean.

Everything below is either a different file, a different machine, or a pure external
web/API check, zero collision risk.

---

## Part 3, the tmux plan, N=5, each independent, each addressing a real gap

```bash
tmux new-session -d -s ford_audit -n main
tmux rename-window -t ford_audit:0 hf_check
tmux new-window -t ford_audit -n wandb_check
tmux new-window -t ford_audit -n overleaf_check
tmux new-window -t ford_audit -n designsafe_check
tmux new-window -t ford_audit -n validation_tests
tmux attach -t ford_audit
```

Switch windows with `Ctrl-b` then the window number, or `Ctrl-b w` for a picker.

### Pane 1, HuggingFace Spaces, never checked in this whole thread

```bash
hostname; pwd
curl -sI https://huggingface.co/spaces/josiecerrell/can-it-ford | head -5
```
This confirms the Space actually resolves and is live (a `200` or `30x`, not a `404`).
If it's live, open it in a browser and check: does the demo reference the retracted
"verdict=FORD peak_x_disp=0.0038m" number anywhere, or the pre-correction MPM claim.
If it does, that's a fourth place the same stale claim survived, not just a
documentation gap.

### Pane 2, W&B, close the loop on the rotation properly

```bash
hostname; pwd
python3 -c "
import wandb
api = wandb.Api()
runs = api.runs('jcerrell29-claremont-mckenna-college/can-it-ford')
print('connected OK, run count:', len(list(runs)))
for r in list(runs)[:5]:
    print(r.name, r.created_at)
"
```
This is the actual end-to-end test the env var alone doesn't give you: if this
prints a run count without an auth error, the new key genuinely works, not just
"is set." Also glance at the printed run list for anything you don't recognize,
a real check against the exposed-key blast radius, not just theoretical.

### Pane 3, Overleaf, entirely new territory

```bash
hostname; pwd
```
Then manually: log into Overleaf, confirm whether a Can It Ford project actually
exists there, and if so, whether it's synced with `paper_draft.md` in the repo or a
separate, possibly stale copy. This one can't be scripted from the terminal, Overleaf
doesn't have a simple curl-checkable public API for project content, it needs a
manual look. Report back what you find, that determines whether this needs its own
sync process or was never actually in use.

### Pane 4, DesignSafe, verify nothing was prematurely touched

```bash
hostname; pwd
ls -la ~/can-it-ford/designsafe-staging/ 2>&1
```
This confirms what's staged locally. Then manually check designsafe-ci.org, log in,
and look at project PRJ-6388's Data Depot: is it still empty, or does it contain
files. If it's still empty, the deferred-DOI decision has been fully honored. If it's
not empty, that's new information that changes the timeline conversation with Kumar.

### Pane 5, validation test script, the "series of tests" you asked for

```bash
hostname; pwd
bash ~/can-it-ford/scripts/validate_state.sh
```
See Part 4 below for the actual script content, save it to that path first.

---

## Part 4, the validation script itself

Save this as `~/can-it-ford/scripts/validate_state.sh` on the Mac (and optionally an
equivalent on Vista for the two Vista-specific checks). Read-only, checks nothing it
writes to, safe to run anytime, including right now in parallel with everything else.

```bash
#!/bin/bash
echo "=== 1, CLAUDE.md not tracked in either repo ==="
git -C ~/can-it-ford check-ignore CLAUDE.md && echo "Mac: ignored, OK" || echo "Mac: NOT IGNORED, FIX THIS"
git -C ~/can-it-ford status --short | grep -q CLAUDE.md && echo "Mac: SHOWS IN STATUS, FIX THIS" || echo "Mac: absent from status, OK"

echo "=== 2, skill fork is the correct N-panel version ==="
EXPECTED_MD5="9bbabeab21f879f0067669ecd7a1167"
ACTUAL_MD5=$(md5 -q ~/.claude/skills/bug-triage-protocol/SKILL.md 2>/dev/null)
if [ "$ACTUAL_MD5" = "$EXPECTED_MD5" ]; then
  echo "skill: correct version, OK"
else
  echo "skill: MISMATCH, expected $EXPECTED_MD5, got $ACTUAL_MD5"
fi

echo "=== 3, WANDB_API_KEY is set and not the placeholder ==="
if [ -z "$WANDB_API_KEY" ]; then
  echo "WANDB_API_KEY: NOT SET, FIX THIS"
elif [ "$WANDB_API_KEY" = "your-new-key-here" ]; then
  echo "WANDB_API_KEY: STILL PLACEHOLDER TEXT, FIX THIS"
else
  echo "WANDB_API_KEY: set to a real value, OK (not printing it)"
fi

echo "=== 4, no wandb_backfill.py plaintext key anywhere known ==="
grep -rl "WANDB_API_KEY\s*=\s*['\"]" ~/can-it-ford ~/can_it_ford ~/can-it-ford-untracked-preserve 2>/dev/null
echo "(empty output above = clean)"

echo "=== 5, the two archive duplicate folders are actually gone ==="
ls ~/Archive/CAN_IT_FORD_DUPLICATES_ARCHIVE_2026-07-07/ 2>&1

echo "=== 6, git status is otherwise clean of surprises ==="
git -C ~/can-it-ford status --short

echo "=== 7, mass bug fix actually applied to the live Vista file ==="
echo "(run this part on Vista, not Mac)"
echo 'ssh jcerrell0629@vista.tacc.utexas.edu "grep -n rho= /work/11603/jcerrell0629/vista/can-it-ford/simulation/can_it_ford_L2_mpm.py"'
```

Run it now, it takes under a minute, and every failure line tells you exactly what
still needs fixing rather than making you re-derive it.

---

## Part 5, what to do with the results

Bring back, in this chat or the next Claude Code turn:
- Pane 1's HTTP status and whether the Space references stale numbers
- Pane 2's run count and whether the run list looks right
- Pane 3's manual finding on whether Overleaf is even in use
- Pane 4's manual finding on DesignSafe's actual current contents
- Pane 5's full script output

Nothing here blocks the live Phase 8 session. Report back whenever each pane finishes,
they don't need to sync up with each other or with Phase 8's completion.
