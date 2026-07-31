# Orchestration pass, 2026-07-25

Session: "Identity and status check". Read-only except this file and one INDEX append. Nothing committed, nothing pushed, no pane dispatched, no `/loop`.

Standing rule adopted this pass: an existence claim names the machine. Every absence below says which machine was checked.

## TASK 1, the P0. Answer: 1389.744 kg. Not seven tonnes.

| Item | Value | Location |
|---|---|---|
| Vehicle box | `size=(1.0, 1.6, 1.5)` = **2.4 m3** | `simulation/can_it_ford_L2.py:61` |
| rho | **579.06** | `simulation/can_it_ford_L2.py:44`, repeated at `:135` |
| Water box | `size=(1.8, 1.8, water_depth)` | `simulation/can_it_ford_L2.py:52` |
| **mass = rho x V** | **1389.744 kg** | computed, 579.06 x 2.4 |

C2's recovered transcript was right: this file has its own box geometry. The 12.0116 m3 box belongs to `simulation/can_it_ford_L2_mpm.py`, a different file. Both parameterizations target the same 1389.744 kg sedan:

- `can_it_ford_L2.py`, 2.4 m3 box, rho 579.06, mass 1389.744 kg
- `can_it_ford_L2_mpm.py`, 12.0116 m3 box, VEHICLE_RHO 115.7, mass 1389.7 kg

Had 579.06 been pasted into the 12.0116 m3 box it would give 6955.4 kg. The hazard C3 flagged is real; it is not realized in this file.

**Sections 4.1 and 4.2 survive the mass check.**

### Coupled-variables rule: rho moved alone, and that is correct here

`git show af95d17 -- simulation/can_it_ford_L2.py` changes only rho, at two sites:

    -    vehicle_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=0.55, rho=604)
    +    vehicle_rigid = gs.materials.Rigid(needs_coup=True, coup_friction=0.55, rho=579.06)
    -             verdict=verdict, peak_x_disp=max_x_disp, rho=604,
    +             verdict=verdict, peak_x_disp=max_x_disp, rho=579.06,

No box change. That is not the bug. The rule guards against moving one of a coupled pair; here the pair was already mismatched, 604 being a leftover from before an earlier sedan-scale resize, and this commit restored consistency to a box that had already moved. 604 x 2.4 = 1449.6 kg, a 4.31 percent overshoot, not a 5x one.

### af95d17 commit message, verbatim

> Fix stale rho=604 in the live SPH pilot and MPM-ytest scripts, same bug 606de5b fixed in designsafe-staging
>
> Both simulation/can_it_ford_L2.py and simulation/can_it_ford_L2_mpm_ytest.py
> use the same 1.0x1.6x1.5m (2.4 m3) vehicle box as designsafe-staging's
> script. rho=604 was left over from before the sedan-scale resize and implies
> 1449.6 kg, 59.86 kg (4.31%) over the 1389.744 kg sedan target that
> VEHICLE_RHO=115.7 hits on the MPM script's full-scale box. Corrected both to
> 579.06 kg/m3 (1389.744 / 2.4), matching 606de5b's derivation for the same box.
>
> can_it_ford_L2.py is the script that generated paper_draft.md Section 4.1/4.2's
> current 14-divergence/39.1%-agreement figures, so those numbers were produced
> under the stale mass and should be treated as needing a fresh regeneration
> before use in the poster or paper, not silently corrected here.

That second paragraph is real and is the uncaught poster item. It touches `simulation/can_it_ford_L2.py` and `simulation/can_it_ford_L2_mpm_ytest.py`, 4 insertions and 4 deletions.

Related, from this same session: `docs/L1_L2_RECOMPUTE_2026-07-25.md` recomputed 4.1's figures under the corrected AR&R small-passenger L1 rule. Divergences 14 to **6**, agreement 39.1 to **69.6 percent**, and `REVERSE_DIVERGE = 1` where section 4.1 asserts every divergence runs one direction. That fixes the L1 half. `af95d17`'s caveat is the L2 half and still stands.

## TASK 2, conda contradiction. monitor:0.1 was right; the other two sessions, including me, were wrong.

Present on Mac at `/opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python`, Python 3.12.13:

| Package | Version |
|---|---|
| matplotlib | 3.11.0 |
| plotly | 6.9.0 |
| kaleido | present |
| numpy | 2.5.1 |
| pandas | 2.3.3 |

PDF backend verified working. Chrome present at `/Applications/Google Chrome.app`.

Why two sessions got a false negative: the install is **miniforge in the Homebrew Caskroom**, not miniconda. Probing `/opt/miniconda3`, `/opt/anaconda3` and `~/miniconda3` misses it, and `conda` is a shell function invisible to non-interactive shells, so `conda env list` returns nothing there. Both checks failed for path reasons, not because the env is absent.

**Consequence: the Vista figure round-trip in `docs/SESSION_DISPATCH_2026-07-25.md` Lane C is unnecessary.** Figures build locally. Already demonstrated: `figures/phase_space_poster_figure.png/.svg` regenerated locally this session, 302876 to 500257 bytes PNG, Jul 10 to Jul 25 07:23.

Absent on Mac, checked: `pdflatex`, `xelatex`, `tectonic`, `pandoc`, `rsvg-convert`, `inkscape`, PowerPoint, LibreOffice, `soffice`. Not checked on Vista. Only Keynote.app is present. So the automated build route is HTML plus CSS `@page` rendered by headless Chrome.

## TASK 3, the Xia citation audit. All four confirmed. Nothing edited.

**3.1 The code computes SSF, not a Xia quantity. Mismatch CONFIRMED.**

`simulation/failure_modes.py:182`:

    topple_idx = _first_sustained_index(surge_accel_g >= ssf, th.sustain_frames)

`ssf` is a plain float parameter, declared `ssf: float = 0.0` at `:84` and threaded through `classify_kinematics(kin, ssf, ...)` at `:162`. That is a Static Stability Factor test, an automotive rollover metric. It is not an overturning-moment formulation from any Xia paper.

Both citing sites attribute TOPPLE to Xia et al. 2013:
- `paper_draft.md:133`: "with the slide mechanism attributed to Xia et al. (2010), topple to Xia et al. (2013), and float to Kramer et al. (2016)"
- `analysis/failure_mode_citations.md:19`: `| TOPPLE | Overturning moment exceeds the vehicle's stability limit | sustained surge acceleration (in g) at or above the vehicle Static Stability Factor (SSF) | Xia et al. 2013 |`

Note that row states the criterion as SSF and the source as Xia 2013 in the same line, so the mismatch is visible within a single row.

No replacement citation is proposed here. F0 refused to invent one and so does this pass.

**3.2 `paper_draft.md:135` verbatim, final sentence:**

> The two Xia et al. source DOIs (10.1007/s11069-010-9639-x for slide, 10.1007/s11069-013-0889-2 for topple) and the Kramer et al. (2016) float source (10.1016/j.ijdrr.2016.04.003) were all confirmed on 2026-07-20.

F0's distinction holds: "confirmed" there covers the bibliographic record, that the DOIs resolve to those papers. It does not establish that the 2013 paper contains a toppling criterion. Those are two separate checks and the sentence does not distinguish them.

**3.3 Year label for `10.1007/s11069-013-0889-2` is inconsistent, and across more than six files.**

Labeled **2013**: `paper_draft.md:181`, `analysis/failure_mode_citations.md`, `.claude/skills/flood-mpm-debugging-reference/SKILL.md`, `vehicle_geometry_research/flood-mpm-debugging-reference_SKILL_v3_friction_corrected.md`.

Labeled **2014**: `README.md:172`, `citations/README.md:23`, `citations/vehicle_mpm_coupling_reference.md:243`, `citations/drift_threshold_grounding.md:218`, `kumar_july9_update/STATUS.md`, `PROVISIONAL_STATUS.md`, `docs/session_notes/2026-07-13_phase7_findings.md:15`, `_inbox/CAN_IT_FORD_bug_audit_july14.md`, plus several `.claude/skills/` and `files/` copies.

Both labels are defensible, 2013 online-first and 2014 print issue 70(2), but a reviewer reading both forms will count two sources. Pick one.

**3.4 "Xia et al. 2011" on the mu = 0.3 attribution. CONFIRMED present.**

`vehicle_geometry_research/flood-mpm-debugging-reference_SKILL_v3_friction_corrected.md:75`:

> Physical ground friction in this project's literature: **mu_wet approx 0.3 is the primary, best-sourced defensible value** (Bonham & Hattersley 1967, reused by Kramer et al. 2016 and Xia et al. 2011)

Repeated at `:36`. F0's finding was that "Xia et al. 2011" is unsupported for this value and collides with Shu, Xia, Falconer & Lin 2011, whose first author is Shu, not Xia.

**Scite result, routed as instructed rather than answered from memory.** DOI `10.1007/s11069-013-0889-2` resolves and the title is confirmed as "Criterion of vehicle stability in floodwaters based on theoretical and experimental studies". Scite returned metadata only, no full-text excerpts, so it neither confirmed nor refuted the toppling-content question. That specific check remains open and is named below rather than guessed.

## TASK 4

**4A. Already done earlier this session, not repeated.** `panel_monitor:0.0`'s stuck prompt was answered `3` (No) via separate send-keys calls with a pause, then the loop was retired: `CronDelete(b0c4d05c)` returned "Cancelled b0c4d05c" and `CronList` returned "No scheduled jobs". `panel_monitor` no longer appears in `tmux list-sessions`.

**4B. Both hooks are intact and functioning. Neither is half-edited.**

`git diff --stat .claude/hooks/`: `gate_destructive.sh` +3, `gate_protected_files.sh` +18/-5. Both pass `bash -n`. Live behaviour, all four gates fire correctly:

| Input | Decision |
|---|---|
| `git push origin main` | ask, "Rule 16: push needs explicit confirmation, every time." |
| `rm -rf ~` | ask, "Recursive delete. Confirm the target path first." |
| Write to `CLAUDE.md` | ask, "Shared coordination file..." |
| Read `x_DEPRECATED_y.ply` | **deny**, "Marked deprecated." |

The `rm -rf ~` case is the documented shell-expansion failure class the standard permission system missed. It is caught. Uncommitted, but working; the risk of leaving them uncommitted is losing them, not running unprotected.

## Named, not guessed

1. **Whether Xia et al. 2013 actually contains a toppling criterion.** Scite returned metadata only. F0's four independent checks, including Martinez-Gomariz et al. 2016's reproduction of the governing equation, indicate it is a sliding incipient-velocity paper, but that is F0's recovered reasoning, not a source read this pass. Needs full text or an open-access review.
2. **What SSF source should replace Xia 2013 for TOPPLE.** Deliberately not invented.
3. **Whether 4.1/4.2's L2 half needs regeneration under the corrected mass.** `af95d17` says yes. Requires rerunning `can_it_ford_L2.py`, not this lane's.
4. **The `RayTracer()` blocker at `can_it_ford_L2_mpm.py:133`.** Reported live on Vista by C0's crash-isolation work. **Not checked on Vista this pass**, no SSH from this lane. Check before spending an allocation.
5. **TASK 2 of the grid-bisection prompt (grid_density 72 / 80 / 88).** Not executed. Requires SSH, an `idev` allocation and Plan Mode approval. Not this lane's. Its gate is now passed: mass is 1389.744 kg, and the bisection is mass-independent regardless.
