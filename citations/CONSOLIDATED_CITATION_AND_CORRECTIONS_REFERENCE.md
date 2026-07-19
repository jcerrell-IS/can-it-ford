# Consolidated Citation, Parameter, and Corrections Reference — Can It Ford?
### Built July 17, 2026, from 6 source documents plus live grep of exported Claude Code sessions.
### Purpose: single reference for any Claude Code session touching citations, DRIFT_THRESHOLD, solver choice (MPM/SPH), or the four validity parameters. Read this before re-investigating any of the questions below, they are already answered.

**How this document is organized:** each section states the CURRENT, resolved answer first, then the full history underneath so nothing is lost. If a section says RESOLVED, do not re-run that research, act on it. If a section says OPEN, that is the actual remaining work.

**Source documents consolidated here, in chronological order:**
| # | File | Date | Status now |
|---|---|---|---|
| 1 | `00_MASTER_CORRECTIONS_INDEX.md` | July 6 | Superseded on its two central claims (DRIFT_THRESHOLD citation, MPM/SPH decision), see Sections A and B |
| 2 | `Verifying_the_0_05_m_Drift_Threshold_for_Vehicle_Instability...md` | ~July 8-10 | Correct, folded into Section A, since superseded by #6 |
| 3 | `Smith__Modra_and_Felder__2019...Debunking_the_0_05_m_Drift_Threshold_Attribution.md` | ~July 8-10 | Correct, folded into Section A, since superseded by #6 |
| 4 | `citation_verification_report.md` | ~July 8-10 | Current, folded into Section C, one finding (Luo et al.) still needs action |
| 5 | `drift_threshold_citation_research.md` | referenced by #2 as "prior investigation" | Not recovered as a standalone file in this pass, its conclusions survive intact inside #2 and #6 |
| 6 | `citations/drift_threshold_grounding.md` (Vista, commit `41eb656`, July 16) | July 16 | **This is the authoritative, final resolution.** Confirmed live in `vista_claude_session_8.txt` and `vista_claude_session_4.txt`. |

---

## SECTION A: DRIFT_THRESHOLD = 0.05 m — RESOLVED July 16

### Current status (act on this)
`simulation/can_it_ford_L2_mpm.py` line 183 sets `DRIFT_THRESHOLD = 0.05`, and line 252 uses it as `verdict = "NO-FORD" if max_x_disp > DRIFT_THRESHOLD else "FORD"`, where `max_x_disp` is peak lateral displacement in metres. This value is **confirmed NOT citable to any literature source** (ARR Project 10 Stage 2, Smith-Modra-Felder 2019, or WRL 2014/07), and the project has already adopted the correct framing, committed to the repo as `citations/drift_threshold_grounding.md`.

**Correct language to use in the paper (already the project's own conclusion, don't re-derive it):**
> "DRIFT_THRESHOLD = 0.05 m is a conservative numerical onset-of-motion detection tolerance internal to the coupled MPM solver, used to classify a vehicle as having begun to move (NO-FORD) once its centroid/rigid-body lateral displacement exceeds this value. It is not a peer-reviewed physical instability criterion. The underlying physical concept, incipient motion via force balance, follows Xia et al. (2014) and Shah et al. (2018)."

**Confirmed via direct grep of `paper_draft.md` on July 16: the number 0.05 does not currently appear in the paper draft.** Nothing needs correcting there, this was caught before it propagated.

### Why it isn't citable (the actual physics reason, confirmed three independent times)
Every source anyone considered (ARR Stage 2, Smith-Modra-Felder 2019, WRL 2014/07) defines vehicle instability as an **onset condition** in the depth-velocity plane: a force balance (drag vs. buoyancy-reduced friction) that is true or false at a given flow condition. None of them defines a **distance the vehicle is allowed to travel** before being called unstable. A displacement-distance criterion only makes sense inside a simulation, where some nonzero movement must accumulate before code can detect "it started moving." That's a numerical classification device, not a physical law, and the three independent investigations (the two you uploaded, the July 16 grounding pass) all landed on the identical conclusion by different paths.

### Exact provenance of the false attribution (confirmed, not previously nailed down in earlier project docs)
`00_MASTER_CORRECTIONS_INDEX.md` (July 6) states: *"Smith et al. 2019, Eq. 6 — identified citation path for the still-uncited DRIFT_THRESHOLD = 0.05m."* This is the false claim. Its real origin: **Azhar et al. (2023)**, a different paper, contains the sentence *"the ARR limits this depth to 0.30 m and this difference of 0.05 m in flow depth may provide safety against poor road conditions or inclined ground slope."* Someone read "0.05 m" near a flood-vehicle citation and misattributed it to Smith et al.'s Eq. 6. Smith et al.'s actual Eq. 6 (verified against both the paywalled journal's cited text and the open companion report WRL TR2017/07) is `d - d_pan = 0.414 - 0.244 * Fr`, a depth-Froude stability boundary, valid only for `d - d_pan > 0`. It is not a displacement threshold. Azhar's "0.05 m" is a flow-depth safety margin discussed in a completely different study.

### The citable numbers that DO exist (a different quantity, do not conflate with DRIFT_THRESHOLD)
DRIFT_THRESHOLD (0.05 m) is metres of lateral displacement, the L2 solver's internal detector. The literature instead supplies a **depth×velocity (D×V) hazard product**, in m²/s, which is what grounds the L1 layer, not L2. Two separate, real, citable families exist, and they use the number 0.60 for **different reasons**, do not conflate them:

**ARR Project 10 Stage 2 (Shand, Cox, Blacka, Smith 2011), Table 3, p.14/PDF p.24, per-vehicle-class:**
| Class | Length | Kerb weight | Ground clearance | D×V limit (m²/s) |
|---|---|---|---|---|
| Small passenger | < 4.3 m | < 1250 kg | < 0.12 m | 0.30 |
| Large passenger | > 4.3 m | > 1250 kg | > 0.12 m | 0.45 |
| Large 4WD | > 4.5 m | > 2000 kg | > 0.22 m | **0.60** |

Explicitly branded by the report itself as "draft, interim, informal" (Executive Summary, p.vi/PDF p.8) and the Water Research Laboratory states it "does not endorse their use in defining safe depths for vehicle traffic" (p.15/PDF p.25 disclaimer). **Always state this caveat when citing it.**

There is also an OLDER, superseded 1987 ARR value quoted inside this same report as historical context: "0.6 or 0.7 m²/s depending on vehicle size" (p.3/PDF p.13). The 2011 report explicitly criticizes this older generic value as non-conservative. **If any file in the project cites "0.6-0.7 depending on vehicle size," that is the old, criticized number, not Table 3.**

**WRL Technical Report 2014/07, Table 5-2, p.38, generic hazard classification (not per-vehicle-model):**
| Class | D×V limit (m²/s) | Meaning |
|---|---|---|
| H1 | <= 0.30 | Safe for all vehicles |
| H2 | <= 0.60 | Unsafe for small vehicles |
| H3 | <= 0.60 | Unsafe for all vehicles |
| H4 | <= 1.00 | Unsafe for all vehicles and people |
| H5 | <= 4.00 | Unsafe, buildings vulnerable |

**The two 0.60 values (ARR's Large-4WD upper limit and WRL's small-vehicle-unsafe boundary) are numerically equal by coincidence, not the same criterion.** State source and vehicle class every time 0.60 appears anywhere in the paper or poster.

### Current per-class assignment used in the live v3 sweep (confirmed via grep, July 16)
| Vehicle | Dimensions/mass | ARR class assigned | D×V threshold used |
|---|---|---|---|
| Sedan | 4.66 m / 1390 kg | Large passenger | 0.45 |
| SUV | 4.96 m / 1990 kg | Large passenger (borderline, 10 kg under the 2000 kg 4WD cutoff) | 0.45 |
| Pickup | 5.89 m / 2300 kg | Large 4WD | 0.60 |

The SUV classification is a genuine borderline call flagged in the session notes, not an error, worth a one-line sensitivity note in the paper (reclassifying it as Large 4WD moves a few cells from divergence to agreement but does not change the overall pattern).

---

## SECTION B: MPM vs SPH solver decision — STATUS UPDATE, not a live open question

`00_MASTER_CORRECTIONS_INDEX.md` (July 6) frames this as an open decision between two paths: (A) rebuild on real MPM, or (B) keep SPH and get Kumar's sign-off to describe the paper as SPH. **This framing is from before the decision was made.** The Master Claude Instructions v6 (July 7, one day later) record the decision explicitly: build real MPM, not reframe to SPH, because MPM is Kumar's specialty, it's what PhysGaussian's own bridge concept assumes, and it's the correct sibling to Cheng-Hsi's NeRF-to-MPM inversion work.

**Current state as of the July 16 session evidence pulled for this document:** both tracks have real, non-trivial MPM work committed. Track 2 (Genesis, `can_it_ford_L2_mpm.py`) has `coup_friction=0.55` and `rho=115.7` confirmed live in the file (grep hit in `mac_claude_session_9.txt`, exact line: `vehicle_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=0.55, rho=115.7)`). Track 1 (`kks32/mpm-engine`) has produced a real 60-cell parameter sweep (`data/track1_sweep_v3/manifest.csv`, 3 vehicle classes × 20 depth-velocity points, all flagged `plateaued_ok=True`). **Do not re-open the MPM-vs-SPH question, it's closed. What's still open is whether the two tracks' results have been reconciled with each other and whether either has produced a fully render-verified video (check `SESSION_STATE.md` for the current answer, this document doesn't have that live).**

---

## SECTION C: Citation accuracy audit (from `citation_verification_report.md`, still current)

| Citation | Verdict | Action needed |
|---|---|---|
| Shand et al. 2011 (AR&R Project 10) | Real, but cite precisely: full report is `Shand, T.D., Cox, R.J., Blacka, M.J., & Smith, G.P. (2011). AR&R Report No. P10/S2/020, ISBN 978-0-85825-948-5`. Note author order differs between the report and a related IAHR conference paper (Shand, Smith, Cox & Blacka) | Use the report citation, not shorthand. State the "draft, interim, informal" caveat whenever the 0.60 threshold is used. |
| Smith, Modra & Felder 2019 (DOI 10.1111/jfr3.12527) | Confirmed exact, real, correctly cited, no discrepancies found | None, this one's clean |
| Luo et al. 2024, IJRR (DOI 10.1177/02783649231221580) | **Real paper, but it's about conformal-prediction safety assurances for driver-warning systems and robotic grasping, not PVWM, gsplat, or MPM.** The current abstract does not actually cite it or mention conformal prediction, so if it's being used anywhere to support the PVWM/query-conditioned world-model claim, that's a mismatch. | **OPEN.** Confirm whether Luo et al. is actually meant to support the project's conformal-prediction validation work (GCI, N>=19 per memory) rather than the PVWM framework claim, and cite it only where that specific claim is made. |

**Also confirmed:** `CanItFord_Abstract_FINAL.docx` currently contains **zero explicit in-text citations, footnotes, or DOI strings** for any of these three sources. All citation tracking currently lives in separate research docs and memory, not in the actual document Kumar reads. Worth fixing before the abstract goes anywhere final.

---

## SECTION D: The four-parameter validity question (`00_MASTER_CORRECTIONS_INDEX.md`'s central table) — updated status

| Parameter | July 6 status (per index) | Status as of latest confirmed grep (this document) |
|---|---|---|
| Vehicle mass/density | "STILL NOT SET," unit-density box, ~12kg effective mass | **RESOLVED.** `rho=115.7` confirmed live for a 1390kg sedan target, `coup_friction=0.55` confirmed live, citing Azhar et al. 2023 |
| Friction (`coup_friction`) | "STILL 0.0 in the committed script" | **RESOLVED**, see above, now 0.55 |
| Boundary condition | Closed-tank, reframed rhetorically as dam-break, sensitivity check "needed but not yet run" | **STATUS UNCONFIRMED IN THIS PASS.** Not grepped this session, verify directly before citing either the July 6 claim or assuming it's fixed |
| Fluid solver | SPH, not MPM, abstract wrong | **SUPERSEDED**, see Section B, MPM rebuild is real and committed on both tracks |

---

## SECTION E: New finding surfaced in this pass, not previously documented anywhere in project memory (July 16, v3 sweep)

Pulled directly from `vista_claude_session_4.txt`, file `docs/session_notes/2026-07-16_l1_l2_dxv_crossref.md`. This is real, current, quality-checked data (`plateaued_ok=True` on all 60 cells), and it's a stronger, more precise version of the old "friction-invariant NO-FORD" story from the synthetic SPH pilot.

**Result: 42/60 cells agree between L1 (D×V hazard, class-specific threshold) and L2 (0.05m displacement detector). Of the 18 divergences, every single one is the same direction: L1 says FORD, L2 says NO-FORD. Zero go the other way.** Per class: sedan 16/20 agree, SUV 15/20, pickup 11/20.

**The physically interesting new mechanism:** most divergences cluster at low velocity (0.5 m/s) and moderate-to-deep depth (0.45-0.60m), where D×V is small (0.225-0.30, comfortably under threshold) so L1 calls it safe, but displacement is large anyway (0.11-0.29m across the three vehicle classes). The mechanism: deep, slow water reduces normal force through near-buoyancy, so even weak drag moves the vehicle. **A pure D×V product cannot see this because it treats depth and velocity symmetrically and reports low hazard whenever velocity is low, regardless of how close to floating the vehicle already is.** This is not a miscalibration of L1, it's a structurally missing axis (buoyancy) in the D×V formulation itself. This is a stronger, more defensible version of the abstraction-ladder story than the synthetic pilot's friction-invariance finding, and it comes from real vehicle-class-specific parameters, not a generic floating box.

**Caveat carried over from the source note:** the marginal cells (e.g., pickup at d=0.15, v=2.0, disp=0.0544m) would flip under a different DRIFT_THRESHOLD. The deep-slow cluster (disp 0.11-0.29m) is robust to any reasonable threshold choice and is what should carry the finding in the paper, not the marginal ones.

---

## SECTION F: Open items (the actual remaining work, not settled questions)

1. **Luo et al. IJRR mismatch** (Section C): confirm whether it's meant to support the conformal-prediction validation work specifically, not the PVWM claim. A July 16 session flagged this could not be checked because no Luo/IJRR citation and no "skill file 03" exist anywhere in the Vista repo, and the reviewer suspected it may be Mac-only. Verify on Mac.
2. **Boundary condition sensitivity check** (Section D): still unconfirmed whether the closed-tank-to-dam-break reframing has been validated by a domain-size sensitivity check.
3. **A filename-vs-stored-value mismatch flagged in `vista_claude_session_7.txt`** (around line 1266): a table comparing "Filename says" vs "Stored `grid_density`" vs "Stored `coup_friction`" was being built, with one file confirmed to hardcode `grid_density=128, coup_friction=0.55, rho=115.7` as literals instead of reading them from config. This is the same bug class as the earlier `grid128_cf0p4` filename/actual-value mismatch already fixed once. **Not fully read in this pass, worth a direct look before trusting any filename-embedded parameter string.**
4. **A mid-session git HEAD move was directly observed** (`vista_claude_session_7.txt`): one pane's HEAD advanced from `59a9c81` to `41eb656` mid-session because a different, invisible pane committed the DRIFT_THRESHOLD grounding doc. Confirmed a clean fast-forward, nothing corrupted, but it's live proof the multi-pane coordination risk in your memory is still actively happening, not just historical.

---

## SECTION G: Files to consolidate or archive (repo cleanup, do this once the above is read)

You now have **4+ files answering the exact same DRIFT_THRESHOLD question** (`drift_threshold_citation_research.md`, the two "Verifying/Debunking" docs, and now `citations/drift_threshold_grounding.md`). They all agree, so none is wrong, but having four is clutter that risks a future session reading an older one instead of the authoritative July 16 grounding file.

**Recommended:** keep `citations/drift_threshold_grounding.md` (July 16, on Vista, in the actual repo) as the single canonical source. Move the three earlier investigation docs into an `archive/` or `research_history/` folder rather than deleting them, they're the audit trail showing the same conclusion was independently reached three times, which is itself a useful credibility point if a reviewer ever asks "how do you know 0.05m isn't in Smith et al.?"

**`00_MASTER_CORRECTIONS_INDEX.md` itself** (found via your screenshot at `josie > can-it-ford > reference_docs > briefing_vault > 00_MASTER_CORRECTIONS_INDEX.md` on your Mac) should get a correction banner at the top pointing to this consolidated file, since its two central claims (DRIFT_THRESHOLD source, MPM/SPH still-open) are both now superseded. Don't delete it, same audit-trail logic as above, just don't let a future session treat it as current.
