# Verification of the RTFD Phase 1-4 report, 2026-08-13

Every claim below was checked live against the working trees, git history and the
manifests on this Mac, and against LS6 and Vista over `scripts/tacc.sh`. Nothing here is
carried from the pasted report's own confidence. Source tags: **[read]** direct file or
command output, **[inferred]** derived from a read, **[recalled]** from context and not
re-checked.

Solver/engine tagging, per the standing rule: the canonical 17 runs and the
Rogue/Silverado sweep are **warpmpm**. The force-coupled `DynamicSDFBody` work is
**warpmpm** as well, through `simulation/realism/`. Nothing below involves Genesis.

---

## Summary: three load-bearing premises are refuted

| # | Pasted report says | Live state | Consequence |
|---|---|---|---|
| R1 | Force-coupled path "validated to +0.035% vs analytic buoyancy on the real Yaris hull" | The 0.035% is a **residual-acceleration identity**, not a buoyancy validation | Dispatch 1's stated premise, and Phase 3's literature-positioning item, both collapse |
| R2 | Two independent resolution-dependence findings need reconciling | They are **one finding in one commit** (`ed8bf8e`) | Dispatch 2's task as written does not exist |
| R3 | Provenance backfill `--write` "still deferred" | **Already run**, 2026-08-12, all 32 manifests | Dispatch 3 item 2 is done |

---

## R1. The +0.035% is not a buoyancy validation [read]

Commit `d8a479f` on `realism-exploration` (2026-08-13 12:21 +0200), titled
"Step 2: 0.035% is a residual-acceleration identity, not a buoyancy validation":

> `dynamic_body.py:207` integrates `dv = J/(M + m_add) + g*dt`. Set `dv = 0` and it
> rearranges to `J/dt = M*g` exactly, so the reported `Fz_err_pct` IS `100*a_z/g`.
> Verified to machine precision on all 8 runs, max `|diff|` 1.4e-16.

So +0.035% means a residual acceleration of 3.5e-4 g and nothing more. It certifies the
body came to rest. It does **not** show the fluid reproduces Archimedes. The commit
states explicitly that neither `Fz_err_pct` nor `implied_disp_volume_m3` "may be cited as
agreement with Archimedes."

**The non-circular number, from the same commit** [read]: settled displacement against
the 1.100 m3 the hull's mass requires runs **+2.4 / +16.9 / +26.6 %** (band = dx) and
**+10.7 / +16.9 / +22.1 %** (band pinned), monotone and worsening with refinement.

**This inverts Phase 3's literature-positioning item.** The pasted report says +0.035% is
"materially tighter than the previously-stated ~7.5% buoyancy agreement" and asks whether
that strengthens the novelty claim. It does the opposite twice over:

1. 0.035% is not a buoyancy agreement at all, so the comparison has no meaning.
2. The force-coupled path's actual buoyancy disagreement (+2.4 to +26.6 %) is **worse**
   than the SDF collider's 7.3 to 7.7 % (`c1sdf_894731.out`, register-confirmed range),
   not better.

Do not write the +0.035% into the paper, the poster, or any message to Kumar as a
buoyancy result.

## R2. The two "independent" resolution-dependence findings are one commit [read]

The report's Phase 1 C and Dispatch 2 treat these as separate:

- "this session's own sweep found Silverado's SLIDE margin collapsing 6.9x to 1.5x from
  g64 to g128"
- "a separate, independently-pushed commit (`ed8bf8e`) reports 'a SLIDE verdict is
  resolution-dependent,' reached a different way"

`git log -1 --format=%B ed8bf8e` shows the commit body **is** that sweep. Its part 1 is
titled "THE ROGUE/SILVERADO SWEEP, PUT THROUGH THE REAL CLASSIFIER" and tabulates
`rs_silverado_g64` `ratio_slide` **6.9669**, `rs_silverado_g96` **1.8105**,
`rs_silverado_g128` **1.5557**. That is the 6.9-to-1.5 collapse, in the commit the report
calls the other finding.

Cross-checked against the primary store
`data/rogue_silverado_slide_classification_2026-08-13.csv` [read]: identical values, one
`source_job` (3362208, LS6 A100) for the g96/g128 rows.

`ed8bf8e` part 2 is the **surge instrument**
(`simulation/validate_coupling_force_ladder.py` gaining COM and velocity 3-vectors). That
is a tool, not a second finding about the SLIDE verdict. Reading part 1 and part 2 as two
findings is what produced the phantom conflict.

**Most likely cause, and it is in the report's own preamble:** the report flags a
duplicated block in the RTFD capture, "content from roughly the back half reappears
nearly verbatim starting around line 9600." One finding read twice is exactly what that
duplication produces. The data-quality note at the top of the report predicted this class
of error and it still landed in Phase 1 C and in a whole dispatch.

**There is no conflict to resolve, so there is nothing to escalate under flag rule 2.**
What *is* open is stated in register J15 [read]: the direct test has never been run.

## R3. The provenance backfill has already been written [read]

`analysis/run_provenance.py --backfill --root /Users/josie/can-it-ford` (dry run) reports
`manifests affected: 0/32`, with `bulk_modulus` refused on 3/32, which is the documented
expected refusal for the three orphan rollouts (register D4a).

17 of the `_incoming/` manifests carry a `_provenance_backfill` block dated **2026-08-12**
with the four confidence labels. Hashing all 32 manifests named in
`/Users/josie/can-it-ford-manifest-backup-2026-08-13/pre_backfill_index.json` against
their current contents: **32 changed, 0 unchanged, 0 missing.**

So the ordering the dispatch asks for was already followed: snapshot first (tarball plus
index, 2026-08-13 00:03), then write. The snapshot is intact and rollback is available.

**Caveat that survives** [read]: the manifests are gitignored
(`.gitignore:33` matched `renders/yaris_render_s1/*` for
`_incoming/g64_m1100/summary.json`, re-derived live rather than cited positionally). The
backfill therefore lives only in untracked local files, and `canitford_git_commit` is
labelled RECONSTRUCTED in every block, an upper bound and not evidence of what ran.

---

## Confirmed as stated

- **`analysis/run_provenance.py` is dirty in `can-it-ford-warpmpm-continue`** [read].
  Status ` M`, so it is **tracked**, not untracked: added by `6d6544f` on
  `warpmpm-continue`. Ownership is therefore *not* ambiguous, contrary to Phase 1 A. The
  uncommitted diff is +111/-32 and is a coherent hardening of the same file by the same
  thread (strict UTF-8 read, repo-scoped `commit_at_time`, tolerant pin parsing).
- **Both Mac branches are at 0/0 with origin** [read]: `realism-exploration` at
  `c4af419`, `warpmpm-continue` at `66912e3`. No unpushed work, as reported.
- **Friction flips SLIDE at g96 in the ladder harness** [read], commit `66912e3`: SLIDE
  True 3/3 at mu=0.00, False 0/3 at mu=0.55, surviving `--no-kick` at 64.6x
  (1.161353 m True against 0.017969 m False).
- **The Vista OAuth token is still in plaintext `~/.bashrc`** [read], line 112,
  `CLAUDE_CODE_OAUTH_TOKEN`. Not rotated. See the standing flag file.
- **g64 settle non-determinism is documented but not in the register** [read]:
  `docs/REGIME_LADDER_RESULTS_2026-08-07.md` section 5.5 and
  `docs/FLOOR_FRICTION_RUNG_2026-08-12.md` section 3.

## Qualification the report misses, and it bounds Dispatch 1

**The two tracks do not share a body.** [read]

- Track 1, the friction/SLIDE result, runs in the ladder harness on a **box**:
  `rho_box`, `box_bottom_travel_m`, and `validate_coupling_force_ladder.py:156` says the
  property in question "is a property of the Yaris hull in the gated scene and does NOT
  apply here: this rung's body" is not that hull. The scene geometry is reproduced from
  the gated scene, the body is not.
- Track 2, the force-coupled `DynamicSDFBody`, runs on the **real Yaris hull** via
  `simulation/realism/proto_hull_float.py`, which requires `--sdf` and `--report`.

So the composite is not a parameter swap. It needs a driver that puts the Yaris hull on
the force-coupled path inside a scene that can express a horizontal SLIDE criterion. The
composite gap in Phase 1 D3 is real and correctly identified as the most consequential
item; its cost is understated.

## Tooling trap found while running the gates, and it will bite the next session

**`.claude/checks/count_claims_check.py` emits a false BLOCK when run from inside a git
worktree.** [read] Same script, same day, two roots:

| root | live per-name | defensible totals | blocking defects |
|---|---|---|---|
| `.claude/worktrees/rtfd-test-phase-1-4-569130` | `DRIFT_THRESHOLD_M` 3, `L2_DRIFT_M` 4, `DRIFT_THRESHOLD` 7, `DRIFT_M` 1 | 16, 17 | **25** |
| `/Users/josie/can-it-ford` | `DRIFT_THRESHOLD_M` 5, `L2_DRIFT_M` 7, `DRIFT_THRESHOLD` 8, `DRIFT_M` 1 | 22, 23, 24 | **0** |

Cause [inferred, from the counts and from H0]: the declaration sites live in untracked
and gitignored paths under `renders/` and `data/`, which a `git worktree add` checkout
does not carry. The worktree therefore has a genuinely smaller corpus, the count comes
out low, and the guard's assertion of 22 fails against it.

The main-root numbers reproduce CLAUDE.md item 13 exactly, 22/23/24 with the two binary
scope choices, so **the canonical count is not in regression.**

**Operative rule: run the audit stack with `--root` pointed at `/Users/josie/can-it-ford`,
never at a worktree.** `count_claims_check.py` accepts `--root` (or `COUNT_CLAIMS_ROOT`);
`register_integrity.py` is unaffected and returned 0 blocking defects from the worktree.
A session that runs the gates from a worktree and reports "25 blocking defects" is
reporting the checkout, not the repo.

## Higher-value neighbour, on the record

Register J15 [read] calls **running the canonical set at g128** "the single highest-value
open item in the project," because it is the direct test of whether 16 SLIDE / 1 STUCK is
grid-converged, and `g96_m2337` sits at a **one-frame margin** (holds the joint condition
4 frames against 3 required, series collapsing 11 -> 10 -> 4 across g48/g64/g96). That
test is cheaper than the composite and settles a published number. Recorded here as a
comparison, not as a substitution: the composite was the dispatch and the composite is
what gets built.
