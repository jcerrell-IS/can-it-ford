# J-item and drainA follow-up, session of 2026-08-26 01:51 BST

Read-only except two files named at the end. Nothing staged, committed or pushed. No `.tex`
touched. Every claim tagged `[READ]` (command output or file bytes this session), `[RECALLED]`
(carried from a document, not re-derived) or `[INFERRED]`.

---

## Where this prompt's stated facts turned out wrong

1. **"real project history now extends to at least 2026-08-25."** It extends to **2026-08-26**.
   HEAD is `436a5f0`, 2026-08-26 01:06:07 `[READ]`.
2. **"the two duplicate submission-status commits."** There are **three**, and two of them share
   a byte-identical subject line. See step one.
3. **`grep -n "K2|K4"` cannot match.** Unescaped alternation needs `-E` in BRE. Run as given it
   returns zero and reads as "not found" `[READ]`. Same class as the H0 rule.
4. **`grep -rn "ReservePool" --include="*.py" .` uses the shell `grep`**, which here is ugrep
   with `--ignore-files` and skips gitignored paths. It happened to return the right answer this
   time; the method is still unsound for an absence claim.
5. **Timing note "if SSH to Vista and LS6 both work cleanly".** Both worked first try with no
   MFA prompt, via `scripts/tacc.sh` `[READ]`.

---

## Step one, the submission-status commits

**The file is NOT populated. Both status lines are blank, and there are two of them because the
block is duplicated.** `[READ]`

`docs/SUBMISSION_STATUS.md` is 8 lines, 312 bytes. Checked with `cat -e`: lines 2, 3, 6 and 7
each end `: $`, that is colon, space, end of line. **No YES, no NO, no venue.**

The three commits, in order `[READ]`:

| commit | time | subject | what it did to the file |
|---|---|---|---|
| `a83a38b` | 08-24 17:56 | Record poster and paper submission status per direct human confirmation | merge commit; **created** the file, 4 lines, with `[YES/NO]` placeholders |
| `12486ea` | 08-25 01:57 | Record poster and paper submission status per direct human confirmation | **+4, no deletions: appended a second identical copy** of the whole block instead of editing the first |
| `2d4c71a` | 08-25 02:01 | Fill in actual poster and paper submission status | +4/-4: **removed the `[YES/NO]` placeholders and put nothing in their place**, in both copies |

**Do the two agree or conflict?** Neither agrees nor conflicts, because **neither records a
value**. There is nothing to compare. `12486ea` duplicates `a83a38b` verbatim rather than
contradicting it.

**Stated plainly, as asked.** Two commits claim "per direct human confirmation" and a third
claims to "fill in actual status", and **the file records nothing**. The confirmation happened
in chat and never reached the file. Worse, `2d4c71a` made the file **less** informative than it
was: a visible unanswered `[YES/NO]` placeholder became a blank that reads as answered.

**This also refutes a claim I made yesterday.** `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`
item 6.10 read "**CLOSED.** Recorded per direct human confirmation in three commits". I had read
the commit messages and never opened the file. **That item is corrected in place this session**
and now reads STILL OPEN with the mechanism above.

**OPEN.** Nothing in the repo records whether the poster was uploaded or the paper submitted.

---

## Step two, J4 LICENSE

**A complete LICENSE is live on the public branch. It is not drafted text.** `[READ]`

- `./LICENSE`, 42 lines, is the only LICENSE at maxdepth 2 outside `third_party/`.
- It **exists on `origin/main`** and is **byte-identical to HEAD** (`git diff --quiet` returns
  clean) `[READ]`.
- Content is real BSD 3-Clause text, copyright holder named, plus a SCOPE paragraph carving out
  third-party material. A scan for `TODO|TBD|DRAFT|[...]|XXX|placeholder|pending` returns
  **nothing** `[READ]`.
- `assets/LICENSE.md` **does not exist**, on disk or in any commit `[READ]`.

**No commit anywhere records a sign-off, and one commit body says the opposite.** `1a1099d`
(08-22 01:42) states, verbatim, that the LICENSE carve-out text was **"merged tonight with the
sign-off outstanding"** `[READ]`. A search across all commit subjects and bodies for
sign-off language returns no approval for the licence.

Three commits touch `LICENSE`: `db06eee` 07-09 added BSD-3, `e1d7f75` 08-18 added the
third-party carve-out, `30218a8` 08-25 23:20 updated public-repo accuracy `[READ]`.
`THIRD_PARTY_NOTICES.md` still carries **14 UNRESOLVED mentions** `[READ]`.

**So: text LIVE and PUBLIC, sign-off NOT recorded.** Those are different states and the
distinction is the whole of J4. **I have signed off on nothing.**

**OPEN**, report-only as instructed.

---

## Step three, CLAUDE.md sync across machines

**THE SYNC CLAIM IS FALSE ON ALL THREE REMOTE POINTS. It is not re-confirmed; it is refuted.**
`[READ]`

| location | lines |
|---|---|
| Mac working tree `CLAUDE.md` | **1046** (currently dirty under a concurrent session) |
| Mac committed at HEAD `436a5f0` | **1022** |
| Vista `~/can-it-ford/CLAUDE.md` | **does not exist at that path** |
| Vista `$WORK/can-it-ford/CLAUDE.md` | **55** |
| LS6 `~/can-it-ford/CLAUDE.md` and `$WORK/can-it-ford/CLAUDE.md` | **do not exist** |
| LS6 `$WORK/canitford_archive/can-it-ford/CLAUDE.md` | **49** |

The session-start banner asserts "CLAUDE.md (project root) = Multi-Pane Standing Rules,
confirmed synced Mac/Vista/LS6/GitHub". **1046 against 55 against 49 is not synced.**

**Vista's copy is a different document, not a truncation.** Its first line is
`# Can It Ford? [em-dash] Project CLAUDE.md`, the dash replaced here to honour this project's formatting rule; the real file contains a literal em-dash, followed by a project description, whereas the Mac file
opens with `## Compact Instructions` `[READ]`. Vista's title also contains an em-dash, which
this project's own formatting rule forbids, a further tell that it predates the current rules.

**The prompt asked me to cite a match as re-confirmed if they still matched. They do not, so
there is nothing to re-confirm.** The correct statement is that the banner has been wrong for
long enough that the gap has grown, not that a previously-true claim has just drifted.

**OPEN.** Not fixed: `CLAUDE.md` is dirty under a concurrent session, and overwriting a remote
copy needs the remote checked for local modifications first.

---

## Step four, register items K2 and K4

The register is at its documented path, `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`,
**3604 lines, 415,530 bytes** `[READ]`. It has not moved or been renamed.

**K2, line 1385. Reads as already corrected.** `[READ]` It records that `gsplat_env` has a slow
first-import chain that presents as a hang on LS6 node c301-004, diagnosed by Ctrl+C traceback
to a `torchmetrics` to `matplotlib` to `ft2font` import, with `nvidia-smi` at 0 percent and
`ss -tnp` showing no outbound connection, ruling out a download stall. Root cause: cold-cache
reads of a shared env on Lustre scratch. It states a standing rule, wait 3 to 5 minutes on first
run. **This is a closed item with a mechanism and a rule. DONE.**

**K4, line 1389. Reads OPEN and is STALE.** `[READ]` Verbatim:

> K4. Open as of this date. Whether the matplotlib import timing test was run, and whether
> simple_trainer.py completed a training run on drainA, were not confirmed in this session.

**It is answered elsewhere and was never written back.** `docs/INFRA_SESSION_FINDINGS_2026-08-07.md`
and `docs/MANUAL_SETUP_STEPS_2026-08-07.md` both carry the heading
**"I-3. Register K4 resolves to YES. drainA training completed. VERIFIED."** `[READ]`

**Two things in the register are now measurably wrong about drainA.**

1. **K4's OPEN status.** Training completed. The register's own corroborating detail at line 1171
   already records the Gaussian counts: 399,491 is rank 0's shard at step 29999 and the three
   ranks sum to 1,147,694 `[READ]`.
2. **Register F.9 line 1156 is REFUTED.** It states "**There is no drainA PLY past 2026-07-17**"
   and reasons from `cfg.yml` carrying `save_ply: false`. Measured live on LS6 `[READ]`:

```
270857262 bytes  2026-08-07 19:11  $WORK/ls6/gsplat_results_backup/drainA/ply/point_cloud_29999_merged_3ranks.ply
 81472689 bytes  2026-07-17 06:18  $WORK/ls6/gsplat_results_backup/drainA/ply/point_cloud_2999.ply
```

**A 258 MB merged 3-rank PLY at step 29999 exists, dated 2026-08-07**, three weeks after the
date F.9 says nothing exists past. Five drainA PLY files in total.

**A METHOD WARNING, because I made the error myself in this session and the control caught it.**
My first search was `find $WORK -iname "*drain*" -name "*.ply"`, which ANDs two tests against
the **same filename**. The file is named `point_cloud_29999_merged_3ranks.ply`; "drainA" is in
the **path**. That search returned **zero**, and had I stopped there I would have reported the
PLY absent and wrongly confirmed F.9. A positive control (`find $WORK -name "*.ply"` returning
10) exposed it, and `-path "*drain*"` returned the five. **A zero from a malformed predicate is
not an absence.**

**OPEN.** K4 and F.9 both need register edits. **Not made this session**: the register is the
corrections authority, another session is live, and editing it under concurrency is the exact
class of edit that caused the 2026-08-07 breach.

---

## Step five, worktrees versus unpushed branches

**Three separate numbers, reported separately and not summed** `[READ]`:

| quantity | count |
|---|---|
| **worktrees** (total, `git worktree list`, includes the main checkout) | **12** |
| of those, under `.claude/worktrees/` | 6 |
| **local branches** (total) | **95** |
| **unpushed branches** (no `origin/<name>` counterpart) | **3** |

The three unpushed are `claude/cranky-swartz-026548`, `worktree-ctx-census`, and one named
`-DO-NOT-PUSH` which is unpushed by design and stays that way.

**The "24 unpushed branches" figure carried in several documents is now stale by a factor of
eight.** It was measured on 2026-08-23. Do not quote it.

CLAUDE.md's own note that this worktree number "has now been wrong three times in twelve days"
is confirmed again: 33/28, then 11/6, now **12/6**. Re-measure rather than quote, including 12.

**DONE.**

---

## Step six, J9 and J10, the ReservePool defect

**The defect is STILL PRESENT. I did not fix it, because the correct fix is not one line.**

`ReservePool` is live in two files `[READ]`: `simulation/openchannel_bc.py` (class at :514) and
`simulation/sim_overfall.py` (:49 import, :189 construction).

**The defect, from `598792e`, which is reachable in this clone** `[READ]`: the constructor guard
validates the park **BOX** against the P2G edge rule and **never the ROWS**. If
`n_water + n_reserve` overruns into the vehicle rows, the numpy write is **in bounds precisely
because the vehicle rows make the array long enough**, so nothing raises. The commit measures the
consequence: parking 20 of 37 vehicle rows leaves **mass correct**, because mass sums MASSES,
while dragging the centre of mass toward the park box and inflating inertia by the r-squared
term, **corrupting the body-frame reference**. It is silent, and it presents as physics.

**Confirmed still present by reading the live source** `[READ]`. The signature is

```
def __init__(self, n_water, n_reserve, park_lo, park_hi, dx, grid_lim, seed=0):
```

**It receives no total-row count, so it cannot validate rows at construction even in principle.**
The only guard present is the park-box edge check.

**Why I did not make the change.** The prompt permits a fix only if it is one line and obviously
safe. The correct fix adds an `n_total` parameter and a bounds check, which changes the
signature and every call site: `openchannel_bc.py` :667, :674, :700, :705 and `sim_overfall.py`
:189. That is five call sites plus the signature, not one line. A one-line guard inside
`pin_parked` would fire only at the first tick rather than at construction, and would convert a
silent corruption into a mid-run raise, which is a behaviour change I am not willing to make
unreviewed under a concurrent session.

**OPEN**, with the fix specified rather than applied.

---

## Files written

| file | change |
|---|---|
| `docs/JITEM_DRAINA_FOLLOWUP_2026-08-25.md` | this report, new |
| `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md` | item 6.10 CLOSED withdrawn and corrected to OPEN |

Nothing staged, committed or pushed. Path-limited only. No `.tex` touched. No sign-off given on
the LICENSE.

## Standing caveat

**Nothing here was checked by the physics-skeptic path.** A concurrent session was live
throughout, so any state can have moved since measurement. Re-run rather than cite.
