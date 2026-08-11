# Recovery plan, 2026-08-08

All state below was verified live between 01:24 and 01:31 BST by direct file read,
`ast.parse`, `git merge-tree`, `git ls-remote` and by executing `params_check.py`.
Nothing here is carried over from a summary. Four other sessions were editing this
tree during verification, so re-check ownership before touching any file.

## What changed since the 00:45 audit, verified

Two audit findings resolved themselves, one changed shape, one is unchanged.

| item | 00:45 audit | 01:31 verified now |
|---|---|---|
| c1-triage branch | never pushed, single disk | **PUSHED**, `refs/heads/worktree-c1-triage` = `6593404` on origin |
| `params_check.py` crash | `ValueError: 'length'` | **no longer crashes**, RC=0 |
| bbox check | would block at 3.16% / 2.63% | **silently unwired from `main()`** |
| harness SyntaxError | broken | **still broken**, blob `7e5c7cd2` unchanged |

The loss risk on the 869-line J.1 harness is gone: c1-triage is on origin. That was
the single most urgent item at 00:45 and it no longer needs action.

---

## R1. CRITICAL: `simulation/validate_coupling_force.py` does not compile

Verified live:

```
SyntaxError: closing parenthesis ')' does not match opening parenthesis '{' on line 680
  line 695:  err_headline_vs_ideal_pct if abs(a_ideal) > 1e-12 else float("nan")),
```

An attempt to guard `a_ideal == 0` deleted the dict key and the computation. The name
`err_headline_vs_ideal_pct` occurs exactly once in the whole file, at line 695 itself,
so a paren-only fix converts the SyntaxError into a NameError.

The original expression is recoverable from the c1-triage version at `6593404`:

```python
"err_headline_vs_ideal_pct": 100.0 * (a0 - a_ideal) / a_ideal,
```

### Exact fix

Replace the single broken line with the key, the original computation, and the guard
its author intended:

```python
        "err_headline_vs_ideal_pct": (100.0 * (a0 - a_ideal) / a_ideal
                                      if abs(a_ideal) > 1e-12 else float("nan")),
```

Match on content, not on line number: four sessions are live and line 695 will drift.

### Verify

```
python3 -c "import ast; ast.parse(open('simulation/validate_coupling_force.py').read()); print('OK')"
```

**Success looks like:** the word `OK` and nothing else.

**Most likely failure mode:** the surrounding dict literal opened at line 680 has other
damage from the same edit, so the parse fails at a different line. If that happens, stop
and diff against `6593404` rather than patching forward:
`git show 6593404:simulation/validate_coupling_force.py > /tmp/vcf_c1.py && diff /tmp/vcf_c1.py simulation/validate_coupling_force.py`.
At 01:31 that diff was 16 lines total, 2 removed and 8 added, so the blast radius is small.

---

## R2. Duplicated `com_frame` emission, same file

Lines 572 to 575 are two identical copies of the same pair:

```python
cxyz = com_trace[-1]
print("com_frame", f, cxyz[0], cxyz[1], cxyz[2], flush=True)
cxyz = com_trace[-1]
print("com_frame", f, cxyz[0], cxyz[1], cxyz[2], flush=True)
```

Every frame prints `com_frame` twice. Any downstream parser that counts frames from
stdout will report double the true frame count.

### Exact fix

Delete the second occurrence of the pair, keeping one.

**Success looks like:** `grep -c 'print("com_frame"' simulation/validate_coupling_force.py`
returns `1`.

**Most likely failure mode:** none, this is a pure deletion. Do it in the same pass as R1
so the file is only touched once.

---

## R3. The bbox check is unwired, and the gate now gives false assurance

`check_bbox_agreement()` is present and correct in `.claude/checks/params_check.py`, but
it is **no longer called from `main()`**. Verified by reading `main()` and by running the
script: no bbox line is emitted at all, and it exits 0.

This is worse than the crash it replaced. The crash failed loud. This reports
"no blocking issues found" while the only check covering CLAUDE.md audit item 14 does
not run.

Re-adding the call as-is will hard-block every commit, because the discrepancy is real
and open. Verified against the live constants (`gates.py:12`, `vehicle_params.py:89`):

```
 1.518 vs 1.470 ->  3.16%  exceeds G-1 tolerance of 2%
 1.746 vs 1.700 ->  2.63%  exceeds G-1 tolerance of 2%
 4.283 vs 4.300 ->  0.40%  pass
```

### Decision required, this one is not mine to make

Three options, in descending order of my recommendation:

1. **Restore the call, downgrade item 14 to a warning.** Append to `warnings` rather than
   `failures`, with the text naming item 14 as a known open discrepancy. The signal stays
   visible on every gated call, nothing is blocked, and nothing is hidden.
2. **Resolve item 14.** Reconcile `EXT_REF` against `bbox_m` so the check passes honestly.
   This is the only option that actually closes the issue, and it is a physics/geometry
   decision, not a tooling one.
3. **Leave it unwired.** Only acceptable if the removal is recorded in the register as a
   deliberate choice. Right now it is undocumented, which is how it read as a silent fix.

**Most likely failure mode of option 1:** the warning becomes wallpaper and item 14 is
never resolved. Mitigate by giving it a date and a register pointer in the string.

### Second, latent defect in the same function

`check_bbox_agreement` sorts both vectors before zipping them:

```python
ext_ref = sorted(...)   # [1.518, 1.746, 4.283]
bbox    = sorted(...)   # [1.47,  1.70,  4.30]
```

It works today only because sorting happens to recover H < W < L on both sides. It
destroys axis identity, so a genuine axis-convention mismatch, exactly the class of bug
this check exists to catch, would pass silently. Compare by axis, not by sorted order.

---

## R4. The gate's trigger is a substring test and self-locks

`.claude/hooks/pretooluse_git_commit_gate.py:19`:

```python
if "git" in command and "commit" in command:
```

This matches the raw command string. Two consequences, both observed live during the
audit:

- A read-only `git log` was gated because unrelated echo text contained the word
  "commits".
- The gate blocked a command that merely **named its own filename**, because
  `pretooluse_git_commit_gate.py` contains both substrings. The hook cannot be inspected
  or repaired through Bash without evading its own trigger.

It also fails the other way: any real commit slips through if the word is not spelled.

### Exact fix

Match tokens, not substrings. `shlex.split` keeps a quoted echo string as a single token,
so `echo "20 commits"` yields the token `20 commits`, which is not equal to `commit`.
A file path is likewise a single token.

```python
import shlex

try:
    tokens = shlex.split(command)
except ValueError:
    tokens = command.split()

is_commit = any(
    tok == "git" and "commit" in tokens[i + 1 : i + 6]
    for i, tok in enumerate(tokens)
)

if is_commit:
    ...
```

### Verify

All three must hold:

```
echo 'git log --oneline   # 20 commits'        -> NOT gated
echo 'python3 .claude/hooks/pretooluse_git_commit_gate.py'  -> NOT gated
echo 'git commit -m "x"'                        -> gated
```

**Most likely failure mode:** `shlex.split` raises on an unbalanced quote or a heredoc,
which is why the `except ValueError` fallback is there. The fallback is naive on purpose:
it fails toward gating, which is the safe direction.

---

## R5. c1-triage merge, no longer urgent

Now on origin at `6593404`, so nothing is at risk of loss. Still unmerged. Recomputed at
01:31 with `git merge-tree --write-tree`:

```
RC=1
CONFLICT (content): Merge conflict in docs/COUPLING_VALIDATION_J1_2026-08-07.md
Auto-merging CLAUDE.md                      (clean)
```

One conflicted file, unchanged in shape from the earlier check even though root's copy of
that doc has since grown from 331 to 384 lines. `CLAUDE.md` still auto-merges clean.

The conflict is **not textual**. The two branches assert opposite findings:

- main `e0b983a`: "C1 fails sign-inverted"
- c1-triage `69c6687`: "retract the C1 sign inversion, confirm the free-rigid coupling defect"

Resolving it by picking a side publishes one of two mutually exclusive physics claims.
Per the standing rules this needs a primary-source check against the actual C1 output,
not a merge tool. **Do not merge until that adjudication happens.**

A partial manual merge already occurred: `docs/COUPLING_VALIDATION_J1_2026-08-07.md.bak-premerge`
is 352 lines, root's live copy is 384, c1-triage holds 617. Roughly 230 lines of the
branch's content are still not in root. No unresolved conflict markers exist anywhere in
the tree.

---

## R6. `node_modules/` is untracked and unignored

631 untracked files from `@google-cloud/bigquery ^9.0.1`, plus `package.json` and
`package-lock.json`. Re-confirmed unignored at 01:31. Unexplained in a physics repo.
It buries real changes in `git status` and is exactly the hazard the `git add -A` ban
exists for.

### Exact fix

Append to `.gitignore`:

```
node_modules/
package-lock.json
renders_preview/
*.bak-premerge
```

**Success looks like:** `git check-ignore -q node_modules/` exits 0, and
`git status --porcelain -uall | wc -l` drops by 631.

**Most likely failure mode:** none for `node_modules`. For `renders_preview/`, confirm
first that no session is treating those `.mp4`/`.png` files as deliverables to be tracked.
Two are currently untracked there.

---

## Sequencing, mandatory

Four sessions were live during verification, and these files are already dirty in the
shared tree:

```
.claude/checks/params_check.py                 changed 01:14, someone else's live work
.claude/hooks/pretooluse_git_commit_gate.py
.claude/settings.json
simulation/validate_coupling_force.py          the R1/R2 target
docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md
docs/SESSION_CLAIMS.md
docs/COUPLING_VALIDATION_J1_2026-08-07.md
```

Do not apply R1 through R4 without claiming those paths first. R1 and R2 touch a file that
another session has open right now. All worktree locks are gone and
`.claude/hooks/gate_concurrent_write.sh` exists but is **referenced zero times** in
`settings.json`, so there is no mechanical protection in place at all.

Suggested order: R1 and R2 together in one pass on one file, then R6 which touches nothing
anyone is editing, then R4, then R3 once the option is chosen, then R5 last and only after
the C1 sign question is adjudicated against primary output.
