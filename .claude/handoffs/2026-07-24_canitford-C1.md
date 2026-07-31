# Pane C1 handoff, 2026-07-24 evening

Scope: CLAUDE.md currency audit (Part 1), stale-file exclusion (Part 2), flood-mpm skill staleness check (Part 3).

HEAD note: this audit was performed at HEAD `4d2242b`. While it ran, three commits landed from other panes (`60a01a2`, `63e677f`, `9f5d82e`). Re-checked at the end: none of them touches `CLAUDE.md` or `.claude/settings.json`, and the project CLAUDE.md md5 is still `e87e02d2cb8de1f7896a3034f9e06109` at 3652 bytes. Every finding below stands as written.

Constraints honored: no git commit, no git push, no warpmpm import, no simulation, no idev/GPU request. No file owned by C2 was touched, and `AUDIT_TABLE_2026-07-24.md` does not exist yet so there was no collision. Everything below was read live this pass with `md5`/`md5sum`/`wc`/`stat`/`git`/`ls`/`grep` on Mac and over ssh to Vista and LS6. Nothing is restated from a doc, a memory, or a prior chat.

---

## Headline findings

1. **The global CLAUDE.md fingerprint holds on all three machines. No drift.** Safe Resume Protocol confirmed present on Mac, Vista, and LS6.
2. **The project CLAUDE.md md5 in the SESSION_STATE fingerprint block is now out of date, and this is benign and attributable.** The change is commit `4d2242b`, which added the verified-facts-ledger gate. Not unattributed drift.
3. **Vista and LS6 project clones are one commit behind Mac and do not carry the ledger-gate rule.** Expected under the push hold, but it means remote panes are being told less than Mac panes.
4. **Two of the seven pre-existing deny rules point at paths that do not exist, so they are silent no-ops.** This is exactly the failure mode the mission warned about. Flagged, not removed.
5. **The v6 doc is confirmed to have never existed as a file.** Searched Mac, Vista, and LS6 by filename and by content.
6. **Part 3 needs no edit. The flood-mpm skill is already corrected to 1100 kg and RESOLVED, with the coupling caveat intact.** The prior session's report was accurate.
7. **New contradiction found, not previously recorded:** the canonical project CLAUDE.md states a vehicle effective density plausibility band of 100 to 300 kg/m3, but the collider-box rho basis that the flood-mpm skill tells every pane to use is 310.50, outside that band. Details in the open-items section.

---

## PART 1, CLAUDE.md currency audit

### Canonical files established

There are two distinct canonical slots, not one file. Both are established:

| Slot | Canonical path | md5 | Bytes | Basis |
|---|---|---|---|---|
| Global (user) | `/Users/josie/.claude/CLAUDE.md` and its byte-identical twins at `/home1/11603/jcerrell0629/.claude/CLAUDE.md` on Vista and LS6 | `a954a8e03b76c69e1a491a437048b83c` | 2004 | matches the recorded fingerprint exactly on all three machines |
| Project | `/Users/josie/can-it-ford/CLAUDE.md` | `e87e02d2cb8de1f7896a3034f9e06109` | 3652 | newest content, git-tracked, clean working tree, HEAD `4d2242b` |

Everything else found is non-canonical.

### Global CLAUDE.md, three-machine check

| Machine | Path | md5 | Bytes | mtime | Safe Resume Protocol |
|---|---|---|---|---|---|
| Mac | `/Users/josie/.claude/CLAUDE.md` | `a954a8e0...83c` | 2004 | 2026-07-15 06:50:41 | PRESENT |
| Vista | `/home1/11603/jcerrell0629/.claude/CLAUDE.md` | `a954a8e0...83c` | 2004 | 2026-07-17 16:45:15 | PRESENT |
| LS6 | `/home1/11603/jcerrell0629/.claude/CLAUDE.md` | `a954a8e0...83c` | 2004 | 2026-07-24 00:54:38 | PRESENT |

Result: PASS. Identical hash three times, matching the fingerprint recorded at 2026-07-25 03:32 UTC in SESSION_STATE.md. The Safe Resume Protocol requirement in Section 4 step 4 of the provenance-audit skill is satisfied on every machine. The previously recorded LS6 misfiling (the 706-line project document sitting in the global slot) remains resolved.

### Project CLAUDE.md, fingerprint mismatch, explained

Recorded in SESSION_STATE.md: `08a4ebac53bc85ebe3e03f7bd423d952`, 3336 bytes, mtime 2026-07-24 20:39:23, last commit `9b9cac4`.
Live now: `e87e02d2cb8de1f7896a3034f9e06109`, 3652 bytes, mtime 2026-07-24 22:35:48.

Cause established by `git log` and `git diff`, not inferred. `git status --porcelain CLAUDE.md` is empty, so this is committed state and not a pane's uncommitted edit. The only change between `9b9cac4` and HEAD `4d2242b` is a five-line addition:

```
+- Before asserting any parameter, threshold, citation, mesh property, or
+  milestone as fact, read docs/VERIFIED_FACTS_LEDGER_july24.md. Section B
+  lists claims already proven false. Section F is the complete vehicle
+  asset inventory: there is ONE usable mesh, not three. Do not re-derive
+  anything in Section A.
```

Verdict: attributed, committed, benign. **The fingerprint block in SESSION_STATE.md should be updated to `e87e02d2cb8de1f7896a3034f9e06109` / 3652 bytes / last commit `4d2242b`,** otherwise the next pane running the drift check will re-investigate this same non-issue. I did not edit SESSION_STATE.md: it is a shared coordination file, the protected-file hook gates it, and other panes are writing to it tonight.

### Project CLAUDE.md copies across machines

| Location | md5 | Bytes | Status |
|---|---|---|---|
| Mac `/Users/josie/can-it-ford/CLAUDE.md` | `e87e02d2` | 3652 | CANONICAL |
| Vista `/work/11603/jcerrell0629/vista/can-it-ford/CLAUDE.md` | `08a4ebac` | 3336 | one commit behind, missing the ledger-gate rule |
| LS6 `/work/11603/jcerrell0629/vista/can-it-ford/CLAUDE.md` | `08a4ebac` | 3336 | one commit behind, missing the ledger-gate rule |
| LS6 `/scratch/11603/jcerrell0629/can-it-ford/CLAUDE.md` | `8cadc7a9` | 2748 | third variant, older still, stale clone |
| Vista+LS6 `/work/11603/jcerrell0629/vista/CLAUDE.md` | `6ff5e0d2` | 38831 | the large misfiled project document, inert in this location |
| Vista `/home1/11603/jcerrell0629/CLAUDE.md` | `2c65dba2` | 1501 | home root, NOT `.claude/`, so the harness does not load it, but it is a confusable duplicate |

Consequence worth stating plainly: Vista and LS6 panes are reading a project CLAUDE.md that does not contain the "read the verified facts ledger before asserting any parameter" rule. That gap closes on its own the moment the push hold lifts and the remotes pull `4d2242b`. It is not fixable by me tonight without a push, which is forbidden by constraint 1 and 2.

### Canonical project CLAUDE.md diffed against T1

Per Section 4 step 3, every parameter claim and pointer in the canonical file was checked against a live source rather than against another document.

| Claim in CLAUDE.md | Live check | Verdict |
|---|---|---|
| `vehicle_params.py` mass_kg: 1100.0 | `vehicle_params.py:83` reads `"mass_kg": 1100.0` | VERIFIED |
| `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply` is the canonical mesh | file exists, 12,445,769 bytes, mtime 2026-07-18 21:44 | VERIFIED |
| `docs/VERIFIED_FACTS_LEDGER_july24.md` (target of the new gate rule) | exists, 38,305 bytes, mtime 2026-07-24 22:54 | VERIFIED |
| DEPRECATED: `yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` | exists | VERIFIED |
| DEPRECATED: `reference_data/..._2026-07-21.json.OLD-4906B` | does NOT exist at that path | CONTRADICTED, see Part 2 |
| DEPRECATED: `data/track1_sweep_v3/` | does NOT exist | CONTRADICTED, see Part 2 |
| DEPRECATED: `docs/session_notes/2026-07-16_l1_l2_dxv_crossref.md` | exists, git-tracked | VERIFIED |
| DEPRECATED: `files/CLAUDE_md_*_july13.md` | three files match the glob | VERIFIED |
| Physics anchor: vehicle effective density 100 to 300 kg/m3 | contradicted by the 310.50 rho basis in active use | OPEN, see below |

The canonical project CLAUDE.md contains no "DONE" milestone markers and asserts no solver or scene provenance, so the abstract-vs-code gap that Section 4 step 5 warns about does not apply to it. It is rules and pointers, which is the correct content for that file.

---

## PART 2, stale-file exclusion

`exclude_stale_files_from_claude_code.md` exists at `/Users/josie/files/exclude_stale_files_from_claude_code.md` (8118 bytes, mtime 2026-07-24 13:23). Its verification prompt was executed as written.

### Every candidate path, confirmed live

Checked with `test -e` from the repo root. Existence checks only, no reads of deprecated content.

| Candidate path | Exists? | Action |
|---|---|---|
| `00_MASTER_CORRECTIONS_INDEX.md` (repo root) | NO | no rule, wrong path |
| `reference_docs/briefing_vault/00_MASTER_CORRECTIONS_INDEX.md` | YES | rule ADDED, this is the real location |
| `PROVISIONAL_STATUS.md` | YES, git-tracked | already denied, kept |
| `drift_threshold_citation_research.md` | NO | no rule |
| `Verifying_the_0_05_m_Drift_Threshold_..._2019_.md` | NO | no rule |
| `Smith__Modra_and_Felder__2019__..._Attribution.md` | NO | no rule |
| `data/track1_sweep_v3/` and `data/track1_sweep_v3/manifest.csv` | NO | existing rule is a no-op, flagged below |
| `data/track1_sweep_v2/` and `data/track1_sweep_v2/manifest.csv` | YES, git-tracked | deliberately NOT denied, see deferred |
| `designsafe-staging/` | YES | rule ADDED, broadened from the single script |
| `designsafe-staging/scripts/can_it_ford_L2.py` | YES, git-tracked | already denied, kept |
| `08_GeoElements_Project_Brain.md` (un-suffixed) | NO | no rule, only the `_UPDATED` twin exists so the KILL-list precedent is already resolved |
| `vehicle_geometry_research/yaris_sedan_watertight_DEPRECATED_lowres_do_not_use.ply` | YES | already denied, kept |
| `reference_data/vehicle_data_master_reference_2026-07-21.json.OLD-4906B` | NO at that path | existing rule is a no-op, flagged below |
| `docs/session_notes/2026-07-16_l1_l2_dxv_crossref.md` | YES, git-tracked | already denied, kept |
| `files/CLAUDE_md_*_july13.md` | YES, 3 files | already denied, kept |
| `citations/drift_threshold_grounding.md` | YES | deliberately left readable, it is the canonical replacement |
| `reference_data/MPM_Flood-Vehicle_Reference_Data__..._NEON_TABLE_SUPERSEDED.md` | YES | rule ADDED, newly found, was not on any prior list |

### Two pre-existing deny rules are silent no-ops

This is the precise failure the mission flagged, and it is already present in the file:

- `Read(reference_data/vehicle_data_master_reference_2026-07-21.json.OLD-4906B)` matches nothing. The only `.OLD-4906B` file in the repo is at `can-it-ford/reference_data/vehicle_data_master_reference_2026-07-21.json.OLD-4906B`, inside the untracked nested directory. The live canonical file at `reference_data/vehicle_data_master_reference_2026-07-21.json` (11,836 bytes) is correctly not denied.
- `Read(data/track1_sweep_v3/**)` matches nothing. Only `data/track1_sweep_v1` and `data/track1_sweep_v2` exist on disk.

I did not remove either rule. They are inert rather than harmful, they are part of another pane's uncommitted work, and constraint 6 plus the mission's "add to it, never replace it" both point at leaving them. The first is now covered in substance by the new `Read(can-it-ford/**)` and `Read(**/*_DEPRECATED*)`-class rules. **Recommend the designated committer either delete these two dead rules or leave them with a note, but do not let a future pane read their presence as proof the paths exist.**

### The "MASTER CLAUDE INSTRUCTIONS v6, July 7" question, CONFIRMED

The working assumption is correct. It never existed as a file.

Searched by filename across `/Users/josie` (all of it), `$HOME` and `/work/11603/jcerrell0629` on Vista, and the same on LS6. Zero hits on any machine. The single filename-similar hit, `CAN_IT_FORD_TRAJECTORY_v6.md`, sits inside a Claude Desktop local-agent-mode session project cache, is a different document by title, and is not a repo file.

Searched by content for the literal string "MASTER CLAUDE INSTRUCTIONS" across the repo, `/Users/josie/files`, Downloads, Desktop, and Documents. Every hit is a document *referring to* v6, never v6 itself:
- `citations/CONSOLIDATED_CITATION_AND_CORRECTIONS_REFERENCE.md:73` cites it as the source of the build-real-MPM decision.
- `files/AUDIT_two_pasted_documents_july23.md:7` labels it "DOCUMENT A", meaning it arrived as pasted text.
- `files/tonight_session_audit.md:136` already records "Gap 6, the MASTER CLAUDE INSTRUCTIONS v6 file may never have existed on disk".

Verdict: ORPHAN as a file, real as pasted chat content. **No deny rule was added for it, because a rule for a nonexistent path is precisely the silent no-op the mission told me to avoid.** Its T3 status and its stale "DONE" render milestones remain correctly captured in the provenance-audit skill's own register, which is the right place for it.

### settings.json, the merge applied

File: `/Users/josie/can-it-ford/.claude/settings.json`. Read live before editing, merged surgically, validated as JSON afterward (13 deny rules, 11 allow rules, 3 hook groups intact).

All seven pre-existing deny rules preserved verbatim, verified programmatically, zero removed. All pre-existing `allow` rules and all `Stop` / `PreToolUse` / `SessionStart` hook wiring untouched. My delta is six added lines and nothing else:

```
  Read(PROVISIONAL_STATUS.md)                                                   [kept]
  Read(designsafe-staging/scripts/can_it_ford_L2.py)                            [kept]
  Read(vehicle_geometry_research/yaris_sedan_watertight_DEPRECATED_...ply)      [kept]
  Read(reference_data/vehicle_data_master_reference_2026-07-21.json.OLD-4906B)  [kept, no-op]
  Read(data/track1_sweep_v3/**)                                                 [kept, no-op]
  Read(docs/session_notes/2026-07-16_l1_l2_dxv_crossref.md)                     [kept]
  Read(files/CLAUDE_md_*_july13.md)                                             [kept]
+ Read(reference_docs/briefing_vault/00_MASTER_CORRECTIONS_INDEX.md)
+ Read(reference_data/MPM_Flood-Vehicle_Reference_Data__Sedan__SUV__Pickup__NEON_TABLE_SUPERSEDED.md)
+ Read(designsafe-staging/**)
+ Read(can-it-ford/**)
+ Read(**/*_DEPRECATED*)
+ Read(**/*_SUPERSEDED*)
```

Rationale per added rule:
- `00_MASTER_CORRECTIONS_INDEX.md` at its real briefing_vault path: `CONSOLIDATED_CITATION_AND_CORRECTIONS_REFERENCE.md:73` states its framing predates the MPM decision, so it reads as current but is not.
- `NEON_TABLE_SUPERSEDED.md`: found this pass, self-labeled superseded, was on no prior candidate list.
- `designsafe-staging/**`: broadens the existing single-script rule. A frozen submission-prep snapshot should not be readable as current state by definition. The folder itself stays on disk for the actual DesignSafe submission.
- `can-it-ford/**`: the untracked nested directory. SESSION_STATE records that no pane should treat it as live, and it is where the real `.OLD-4906B` copy actually lives.
- `**/*_DEPRECATED*` and `**/*_SUPERSEDED*`: the self-enforcing glob upgrade from the exclude doc. These also catch the duplicate copies sitting in `.claude/worktrees/` and in the nested directory, which no single-path rule reaches.

Honest caveat on the two globs: `.claude/hooks/gate_protected_files.sh` already denies `*DEPRECATED*`, `*SUPERSEDED*`, `*.OLD-*`, and `*_OLD_*` at the hook layer. The glob rules are therefore partly redundant inside this repo's hooked sessions. They are still worth having, because per the exclude doc's quoted desktop documentation, `settings.json` permission rules also apply to Claude Desktop sessions, where the repo's PreToolUse hooks do not run.

**Not committed, per constraint 1.** The change sits uncommitted in the shared tree alongside the other panes' edits to the same file. `git diff -- .claude/settings.json` will show my six lines plus the pre-existing uncommitted reformatting and the added `Read` matcher that were already there before I arrived. Those are not mine.

---

## PART 3, flood-mpm-debugging-reference staleness check

Live file: `/Users/josie/.claude/skills/flood-mpm-debugging-reference/SKILL.md`, 13,758 bytes, mtime 2026-07-23 21:57. Read directly, not via a summary.

**Finding: the correction already landed. No edit was needed and none was made.**

The file does NOT show the old unresolved 1078 kg / rho 304.28 framing. Line 19 reads, in part:

> **RESOLVED 2026-07-23, do not reopen:** the NCAC Yaris mass is **1,100 kg** (Option A), taken from the LS-DYNA deck header of `yaris-coarse-v1l.key` ... The earlier 1,078 kg / rho 304.28 recommendation is **superseded** by commit `aa13ac1` ... Do not reintroduce 1,078 kg.

Line 35 repeats the resolution and, as the mission required, the mass-and-rho coupling warning is intact and untouched:

> **Coupled-variable caveat:** both rho values presuppose the real-mesh (Yaris) solid volume of ~3.543 m3 (1078/304.28 = 1100/310.47 = 3.543). Do NOT paste rho=304.28 into the 4.66x1.79x1.44m box-proxy path (12.01 m3), that yields ~3654 kg. rho only means a mass against a specific volume.

The prior session's report that this was corrected citing `aa13ac1` is accurate. Independently cross-checked against T1: `vehicle_params.py:83` reads `"mass_kg": 1100.0`, and the skill's claim about that line is correct.

### But: a second, different staleness in the same file, NOT fixed, flagged for decision

The skill closes a question that the mission's own hard-constraint section says is still open.

- Skill line 35 instructs: "use **1100 kg / rho=310.47** everywhere."
- The mission states, and `aa13ac1` retains via `volume_basis_still_open`, that the volume basis is unresolved: collider box 3.5427 m3 versus raw enclosed mesh 6.8185 m3, giving rho 310.50 versus 161.33. Mass is settled, rho is not.

So the one file every pane is told to trust for this number tells them to paste a single rho, while the ledger and the commit both say the basis for that rho has not been chosen. That is the same shape as the errors this project keeps repeating.

Compounding it, the canonical project CLAUDE.md line 15 sets the vehicle effective density plausibility anchor at 100 to 300 kg/m3. The value 310.50 falls outside that band; 161.33 falls inside it. A pane following CLAUDE.md's own anchor and a pane following the skill's "use 310.47 everywhere" will disagree, and CLAUDE.md's coupled-variables rule tells them not to resolve it by pattern-analogy.

I did not edit the skill. The mission scoped Part 3 to correcting the mass number and its resolved status, and that specific correction is not needed. This is a different claim, it touches the open volume-basis question that the mission explicitly said not to close, and the fix is a judgment call about which basis is right, which is not mine to make tonight. Proposed minimal edit, for whoever owns this next, changing only the instruction and leaving the coupling caveat alone:

```
- 1. **Vehicle mass/density.** RESOLVED 2026-07-23 (commit `aa13ac1`): use **1100 kg / rho=310.47** everywhere.
+ 1. **Vehicle mass/density.** MASS RESOLVED 2026-07-23 (commit `aa13ac1`): use **1100 kg** everywhere.
+    rho is NOT resolved: `aa13ac1` retains `volume_basis_still_open`, collider box 3.5427 m3 giving
+    rho 310.50 versus raw enclosed mesh 6.8185 m3 giving rho 161.33. Do not paste a single rho into a
+    script on the strength of the mass being fixed. Note also that CLAUDE.md's plausibility anchor is
+    100 to 300 kg/m3, which 310.50 exceeds and 161.33 satisfies.
```

---

## Audit table, provenance-audit Section 10 format

| Claim | Tier supporting | Source exists? | Says it? | Verdict | Root-cause conflation | Action |
|---|---|---|---|---|---|---|
| Global CLAUDE.md identical on 3 machines, md5 `a954a8e0` | T1 md5 over ssh | yes | yes | VERIFIED | none | none, fingerprint holds |
| Safe Resume Protocol present on all 3 machines | T1 grep over ssh | yes | yes | VERIFIED | none | none |
| Project CLAUDE.md is md5 `08a4ebac` / 3336 bytes | T2 SESSION_STATE block | yes | no longer | CONTRADICTED | fingerprint recorded before commit `4d2242b` landed | update the SESSION_STATE fingerprint to `e87e02d2` / 3652 |
| Vista and LS6 project clones are in sync with Mac | T3 assumption | yes | no | CONTRADICTED | push hold means remotes cannot have `4d2242b` | closes when the push hold lifts, no action available to C1 |
| `.OLD-4906B` exists at `reference_data/` | T2 CLAUDE.md DEPRECATED list | no | n/a | ORPHAN | path recorded from the nested copy's name, not its location | dead deny rule flagged, real copy covered by `can-it-ford/**` |
| `data/track1_sweep_v3/` exists | T2 CLAUDE.md DEPRECATED list | no | n/a | ORPHAN | directory removed after the rule was written | dead deny rule flagged |
| "MASTER CLAUDE INSTRUCTIONS v6" exists as a file | T3 chat reference | no, on any of 3 machines | n/a | ORPHAN | pasted chat text remembered as a document | confirmed, no rule added |
| flood-mpm skill still says 1078 kg unresolved | T3 prior-session report | yes | no | CONTRADICTED, correction did land | none, the prior report was right | none needed |
| flood-mpm skill: "use rho=310.47 everywhere" | T3 skill text | yes | yes | CONTRADICTED by `aa13ac1` `volume_basis_still_open` | mass being settled read as rho being settled | proposed diff above, not applied |
| `vehicle_params.py` mass_kg is 1100.0 | T1 live grep | yes | yes | VERIFIED | none | none |

No KILL list this pass. Nothing was deleted, moved, or renamed. The stale carriers found were neutralized by deny rules instead, which is the reversible option.

---

## Open items for the designated committer

1. Uncommitted in the shared tree from C1: `.claude/settings.json`, six added deny rules. Nothing else. No other file was written by C1 except this handoff.
2. Update the SESSION_STATE.md project CLAUDE.md fingerprint to `e87e02d2cb8de1f7896a3034f9e06109` / 3652 bytes / commit `4d2242b`, or the next drift check re-investigates a resolved non-issue. C1 did not edit SESSION_STATE.md by design.
3. Decide on the two dead deny rules (`.OLD-4906B`, `track1_sweep_v3`). Inert either way, but they must not be read as evidence those paths exist.
4. Decide on the flood-mpm skill rho instruction, proposed diff in Part 3.
5. Vista and LS6 project clones lack the ledger-gate rule until the push hold lifts.

## Deferred and optional, filtered against the three anchors

Filtered against poster July 27, paper July 31, one verified rendered physically plausible MPM sim with a vehicle. These serve one of those but were not in scope, so they are recorded rather than done:

- **`data/track1_sweep_v2/**` deny rule. DEFERRED, deliberately.** The exclude doc rates it "lower confidence, needs verification, not confirmed invalid the way v3 is" and explicitly says to add it only after live re-confirmation. I did not re-confirm v2's validity live tonight, so adding the rule would violate the same evidence standard this audit exists to enforce. Serves the poster anchor if v2 is ever a figure source. Needs one live check of the v2 manifest's `density_plausible` column first.
- **`.claude/worktrees/` duplicate stale copies.** Four worktrees each carry their own copy of `drift_threshold_grounding.md`, the DEPRECATED `.ply`, and the SUPERSEDED reference table. The two new globs cover the DEPRECATED and SUPERSEDED ones. A blanket `Read(.claude/worktrees/**)` was NOT added because another pane may be actively working in one tonight, and the byte-size precedent in the audit skill says stale copies are dangerous but active worktrees are legitimate. Recommend resolving after tonight's panes finish.
- **Volume-basis resolution (3.5427 m3 versus 6.8185 m3).** Directly blocks a physically plausible sim, which is anchor three, and it is the highest-leverage open number found tonight. Out of C1's scope, it needs a geometry decision, not an audit.
