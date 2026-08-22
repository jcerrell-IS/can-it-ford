# Confirming two prior reports, and the hf_space merge question answered

Checked 2026-08-22 15:20 to 15:30 BST from `Josephines-MacBook-Air.local`,
`/Users/josie/can-it-ford`, branch `claude/add-ci-checks`, HEAD `d3fc4d7`.

Scope: confirm the claims in `docs/PRIOR_DISPATCH_VERIFICATION_2026-08-22.md` and
`docs/CLAUDE_MD_OPEN_ITEMS_STATUS_2026-08-22.md`, and settle the one action they
left conditional. **Nothing was merged. Nothing was pushed. No SU spent.**

Both source documents were read at their committed content, not a stale copy:
worktree blob SHAs match the HEAD blobs exactly (`9255ffc5` and `3efd008f`,
`git hash-object --path`) `[READ]`.

**Headline: all three commit-message claims are accurate. The one conditional
action, the `hf_space/` merge, must NOT happen, and the reason is the opposite of
the one assumed.**

---

## 1. The r7 smoke test: what it actually found

The prior document verified the **job state** and explicitly disclaimed opening the
results. Doing that here closes the gap.

**The smoke test is job 918501, and it is a g48 plumbing gate that measures no
physics.** From `docs/R7_INFLOW_OUTFLOW_VEHICLE_2026-08-18.md:130` on
`claude/r7-inflow` `[READ]`:

- **4 of 4 runs `rc=0`, `ALLDONE`.**
- **11 of 11 plumbing assertions PASS**, specifically: the recycle arm drops
  exactly the two x-normal planes, the closed arm drops none, water count is
  identical in every arm, and the outflow plane lands exactly where the closed
  arm's downstream wall sits.
- Its own sentence: *"It measures no physics and is not quoted as a result
  anywhere below."*

So the correct form is **the smoke test validated the plumbing and gated the full
run**. It did not produce a physics finding, and no physics number should ever be
attributed to 918501.

The physics comes from job **918506**, 34 of 34 `rc=0` `[READ]`. Its headline is a
null on verdicts and a large move underneath them:

- **No canonical verdict moves.** 5 of 5 SLIDE stays SLIDE at the g64 baseline and
  at g96 m2337, 5 of 5 STUCK stays STUCK at v0.5.
- **The closed tank manufactures a free-surface slope of +0.0711 m/m at g64,
  which is 1.36x a 3 degree road** (tan 3 deg = 0.0524 m/m).
- Displacement at the canonical horizon rises **+35.4, +38.3 and +15.0 percent**;
  by row 250, **+307, +521 and +88 percent**.
- Two things got worse and are reported rather than buried: the below-floor leak
  roughly triples at g64 under recycling (1.54 to 5.38 percent).

**One pre-registered prediction was refuted** `[READ]`, section 9: the wrapper
predicted recirculation would need about 130 frames and stay outside the 90-frame
horizon. Measured, it reaches the vehicle at **row 64** at g64 (identically in all
five repeats) and **row 70** at g96, both **inside** the canonical horizon. Only
v0.5 behaved as predicted, at rows 161 to 162.

A **second** claim is also undermined, and it is a separate matter from the
prediction above: the "wall reflection at frame 112.3" reproduces arithmetically
to 0.04 of a frame but is **probably mis-mechanised**, because the still-water
assumption is wrong at Fr 0.88, where the correct figure would be roughly 478
frames, not 112 `[READ]`. The document says plainly this is a consistency check,
not a demonstration.

---

## 2. The "negative answer" is item 7: poster and paper submission status

**Item 7, and it is the literal seventh.** `[READ]` No document in this repository
confirms that either the poster or the paper was ever actually submitted to
anyone. What the documents confirm is **artifact readiness**, a different claim.

Why it is still open:

- `docs/POSTER_COMPLIANCE_2026-07-27.md` requirement 6 **is** the submission (the
  Final Posters folder before 2026-07-27 09:00 CST) and is recorded verbatim as
  *"Not verifiable from this machine"* then *"OPEN, presenter action"*.
- `docs/SUBMISSION_MANIFEST_2026-07-31.md` is a reproducibility record. It carries
  no venue, no portal, no submission date, no receipt, no acceptance. "Submitted
  commit" names the commit that was final, not an act of submission.
- Affirmative evidence against "final and submitted": the Overleaf tip is
  `3053956`, **2026-08-20**, *"Correct four sourced defects"*, 21 days past the
  target date.

**Blocker: both answers are outside the repository.** No command in this repo can
close it. It needs one line from Josie on each.

---

## 3. The README patch: complete for what it was scoped to fix

**Confirmed. Two of the seven items required a `README.md` edit, and both landed
in `1780169`.** The other five did not need one, so "only two named in the commit"
is correct rather than incomplete. Read live against the current file `[READ]`,
which is clean against HEAD:

| # | Item | Needed a README edit? | State now |
|---|---|---|---|
| 1 | W&B badge, owner/org | no | present, `README.md:6` |
| 2 | `l2_results_from_wandb.csv`, 9 conditions | no | present, `:143`, "9 unique conditions" |
| 3 | Gradio demo stale | **yes** | **fixed**, `:175` reads "live"; badge at `:7` |
| 4 | Corpus merge vs Citations | no | no change required |
| 5 | DesignSafe staged | no | present, `:86` and `:166`, "pending" |
| 6 | HF Space understates its dataset by 20 | no, not a `README.md` defect | **STILL OPEN**, see 5 |
| 7 | Dataset licence stale | **yes** | **fixed**, `:166` reads CC-BY-4.0 |

No `ODC-By` or `odc-by` string survives anywhere in `README.md` `[READ]`.

---

## 4. The `hf_space/` merge: DO NOT DO IT

**The merge did not happen, and it must not. `claude/r9-platform` is not a
superset of `claude/add-ci-checks`; it is a divergent, undeployed variant.**

`git diff claude/add-ci-checks claude/r9-platform -- hf_space/` returns 5 changed
files, 527 insertions, 467 deletions `[READ]`, and the changes run in **both**
directions. `r9-platform` is also **missing `hf_space/.gitattributes` entirely**
(11 files on `add-ci-checks`, 10 on `r9-platform`).

The decisive test is against the live Hub Space, which is the authority. Every
file fetched live from
`huggingface.co/spaces/josiecerrell/can-it-ford/resolve/main/` `[READ]`:

| file | live md5 | `add-ci-checks` | `r9-platform` |
|---|---|---|---|
| `speed_surface.py` | `851f4224` | **match** | `046116a0`, differs |
| `data/load_surface.csv` | `8e8d6d3d` | **match** | `f091fda6`, differs |
| `data/canonical_runs.csv` | `fc2bc4ba` | **match** | `2ef79cb5`, differs |
| `.gitattributes` | `a859f8a8` | **match** | **absent** |

**`add-ci-checks` is byte-identical to the deployed Space on every file tested.
`r9-platform` matches on none.** So merging `r9-platform`'s `hf_space/` would
**regress git away from production** and re-open the exact desync that `adb5634`,
`e91ab13` and `ca5ee11` closed on 2026-08-22 `[INFERRED from the md5 table]`.

The history explains it: both diverged from `4db2789`. `r9-platform` then
published (`e0eabac`, *"PUBLISHED. Dataset, Space and W&B are live"*) and later
recorded `bef6da0`, *"I overwrote a published physics fix on a PUBLIC page"*.
`add-ci-checks` afterwards reconciled **from** the live Space. The Hub round trip
is what makes `add-ci-checks` current `[INFERRED]`.

**One thing on `r9-platform` is genuinely absent from `add-ci-checks`**: a 41-line
`arm_ratio_table()` in `speed_surface.py`. It is **not deployed** (`grep
arm_ratio_table` on the live file returns 0) `[READ]`, and it defines its list as
**`ial_ARMS`**, a mangled identifier. Definition and use agree, so it would run,
but the name is the signature of a botched edit `[INFERRED]`. If that function is
wanted, it should be cherry-picked deliberately and the identifier fixed, not
swept in by a directory merge.

---

## 5. `can-it-ford-demo`: it WAS investigated, and the finding still holds exactly

**Confirmed investigated**, in `PRIOR_DISPATCH_VERIFICATION` Part 5, at length.
Re-read live today from `api/spaces/josiecerrell/can-it-ford-demo` `[READ]`, and
every field still matches that document field for field:

`private` False, `runtime.stage` **`NO_APP_FILE`**, `cardData`
`{"title": "Can It Ford Demo", "sdk": "gradio"}` with **no `license` key**,
`lastModified` 2026-08-20T23:58:57Z, siblings `.gitattributes`, `README.md`,
`phase_space_results.csv`.

**Verdict unchanged: an abandoned, never-finished earlier Space, already converted
into a correct redirect stub.** It is not a duplicate of the working demo, because
it has no `app.py` at all. No action required. The two residual items (the
provenance-free `phase_space_results.csv` it still serves, and the missing licence
field) are public writes and stay Josie's call.

---

## Two small corrections to the prior documents

1. **`PRIOR_DISPATCH_VERIFICATION` 4.3 cites the manifest key as
   `"rows_checked": 368`. The key is actually `records`.** `[READ]` Top-level keys
   are `engine, families, force_magnitude_consistency, hulls, not_claimed,
   records, source, windows`. **The value 368 is correct**; only the key name is
   wrong. The "three measurements say 368" conclusion stands.
2. `PRIOR_DISPATCH_VERIFICATION` Part 3 lists the r7 physics as quoted, not
   re-derived, and flags this itself. Section 1 above now sources those figures to
   the results document directly and separates 918501 from 918506, which the
   earlier summary ran together.

---

## What is still open, ranked, after this pass

1. **`hf_space/README.md` line 40 still reads `348` where the data says `368`.**
   Re-measured independently today: `load_surface.csv` holds **368** data rows and
   the manifest's `records` field is **368** `[READ]`. The file is still
   uncommitted (` M`), and **the deployed public page carries the same error**,
   confirmed by fetching it live `[READ]`. This is the prior report's own ranked
   item 1 and it is untouched. **Not fixed here**: it is an uncommitted file in a
   shared tree, and correcting it properly also means republishing a public page,
   which needs Josie's go-ahead.
2. **`claude/r7-inflow` is unmerged.** Completed work, ExitCode 0:0, pushed to
   origin, invisible from the integration branch and from `main`.
3. **Item 7 above**, poster and paper submission status, needs one line from Josie.

## Limits

- **NOT ADVERSARIALLY REVIEWED.** No subagent spawned. Single-session
  measurements, each naming the command that produced it.
- **The Hub is a live third-party surface.** Its files were read at 15:2x BST. A
  push to either Space invalidates the md5 table in section 4.
- **I did not open `profiles.npz`** or re-derive any r7 physics number. Section 1's
  figures are read from the results document on `claude/r7-inflow`. What I verified
  independently is that the document exists on that branch and what it says about
  918501 versus 918506.
- **The working tree is shared.** One other session was active during this pass.
  Every filesystem statement is timestamped 15:20 to 15:30 BST.

*Written 2026-08-22. Confirmed rather than re-ran. No merge, no push, no delete,
no branch. One file staged and committed: this one.*
