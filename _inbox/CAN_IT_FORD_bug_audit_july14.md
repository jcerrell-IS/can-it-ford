# Can It Ford: Full Bug Audit and State-of-Project Report
### Compiled July 14, 2026, cross-referenced against live GitHub + HuggingFace state, not just chat summaries

This supersedes the informal bug lists scattered across prior sessions. Every item below was checked against either (a) a live fetch of GitHub/HuggingFace today, or (b) the actual conversation text (not just its AI-generated summary) where a bug was first raised. Where a summary said "fixed" but the underlying conversation showed otherwise, I flagged the discrepancy explicitly rather than trusting the summary. That distinction matters a lot here, see the "summary vs. live text" mismatches called out below.

---

## 0. The one thing to read first

**Your biggest technical bottleneck as of a few days ago (the vehicle mesh) is solved.** FloodScene ingests raw Gaussian splat PLY files directly, no mesh conversion, no PhysGaussian bridge needed for the vehicle. You ran `truck_trimmed.ply` successfully and completed a real 36-run full-scale sweep with real 6-DOF output across three vehicle classes.

**Your biggest current risk is that none of this is on GitHub yet, and the README there is now five days stale and actively wrong.** Kumar reads that repo directly. This is job one.

---

## 1. BUGS CONFIRMED RESOLVED (do not re-investigate)

| # | Bug | Resolution evidence |
|---|---|---|
| 1 | Vehicle mesh unusable / "no real vehicle mesh exists" | **Reframed, not just fixed.** `truck_trimmed.ply` is a raw 3DGS splat (191,107 Gaussians, no face topology) and was never supposed to become a triangle mesh. `FloodScene` (kks32/mpm-engine, `examples/flood_vehicle.py`) ingests splats directly via `load_gaussians_ply` + `solidify_columns`. Ran clean: 1,810 solid particles seeding 7,454 MPM vehicle particles, 90 frames, 71cm displacement, 9.7deg yaw, roll <0.01deg, confirmed upright via a mid-run frame. |
| 2 | No real 6-DOF vehicle output (Kumar's explicit ask from the July 10 meeting) | Delivered. The 36-run sweep produced real dx/dy/dz/yaw/pitch/roll per run, not the earlier kinematically-fixed-quaternion result from `box_sdf_collider_setup.py`. |
| 3 | CLAUDE.md fragmentation (3 drifting copies) | Consolidated to one canonical v3, md5-identical on Vista parent and Mac (gitignored, symlinked so it can't drift again). |
| 4 | Exposed W&B API key (commit `50eff29`) | Rotated (new 86-char-format key), live in `~/.zshrc` and `~/.netrc`. 88 existing runs confirmed legitimate, none from the exposure window. |
| 5 | HuggingFace Space `CONFIG_ERROR` | **Confirmed live today via direct HF runtime API check: `stage: RUNNING`, domain `READY`.** This is genuinely fixed, not just "drafted." See Section 5 below for what it actually shows. |
| 6 | DesignSafe staging folder appearing empty | Red herring. Commit `25bca69` deliberately moved that data to the repo root. Nothing was lost. |
| 7 | Water block z-base sitting inside the 2-cell P2G stencil margin (the original boundary-violation crash affecting both tracks) | Root-caused and fixed on Track 1 (kks32/mpm-engine); the first clean 500-step Track 1 run (peak force 6389.93N) came after this fix. |
| 8 | `argparse` positional-argument bug across `can_it_ford_L2.py`, `can_it_ford_L2_mpm.py`, `can_it_ford_L2_mpm_ytest.py` | Fixed with real `argparse`, committed `69d27af`. |
| 9 | `can_it_ford_mu_sweep.py` had 4 unresolved physics bugs | Quarantined (commit `af33b26`), no longer live. |
| 10 | `make_phase_space_v2.py` mislabeled SPH output as "Genesis MPM" and carried a false Smith 2019 annotation | Both corrected/removed (commit `eec681b`). |
| 11 | `viability_audit.py` glob bug (missed all `particles_mpm_*` files) | Fixed and pushed. |
| 12 | Stale `DOI: [INSERT AFTER JULY 10]` placeholder in `paper_draft.md` | Updated (commit `02b4784`). |
| 13 | DRIFT_THRESHOLD = 0.05m falsely attributed to Smith, Modra & Felder 2019 Eq. 6 | Corrected. Real basis is Xia et al. 2014 and Shah et al. 2018 (incipient-velocity criteria), reframed as an un-cited conservative numerical detector, not a hard published value. |
| 14 | N=19 conformal-prediction threshold falsely attributed to Luo et al. IJRR 2024 | Corrected; this is a real split-conformal statistical requirement, not tied to that specific paper. |
| 15 | Genesis issue #600 (grid tunneling) suspected as Track 2 crash cause | Ruled out. `grid_density=128` was already live before this was tested and the crash still occurred. |
| 16 | Storm drain scene reconstruction (Drain A / Drain B) | COLMAP structure-from-motion gate-passed: Drain A 279/279 (100%), Drain B 265/266 (99.6%), confirmed July 10. |
| 17 | Genesis vs. Taichi GLFW conflict, MacBook migration issues | Resolved during MacBook migration; correct env pattern (`conda run -n can-it-ford python3`) documented and holding. |

---

## 2. BUGS CONFIRMED STILL OPEN

| # | Bug | Current status / what's actually true |
|---|---|---|
| 1 | **GitHub README is stale and wrong** | Confirmed via direct fetch today. Still reads "Status (July 9, 2026)," still describes the pre-breakthrough state (SPH-to-MPM migration in progress, box proxy vehicle `1.0x1.6x1.5m`, `CUDA_ERROR_ILLEGAL_ADDRESS` as the blocker). Zero mention of FloodScene, the splat-native vehicle breakthrough, or the 36-run sweep. **This is your #1 priority repo item.** |
| 2 | **FloodScene work was never pushed to GitHub** | `simulation/flood_vehicle.py` returns a live 404 on the repo. The single most important result of the last two days does not exist anywhere Kumar can see it. |
| 3 | Track 2 Genesis-native `can_it_ford_L2_mpm.py`, `CUDA_ERROR_ILLEGAL_ADDRESS` | Still crashes at `substep_pre_coupling` inside `p2g`. Got zero further attention on July 13-14 while Track 1 succeeded. **Recommendation: deprioritize/shelve this rather than keep debugging it** (see Section 8). If you ever return to it, `dmesg -T \| grep -i xid` run immediately after a reproduced crash is the one lead nobody has actually tried yet. |
| 4 | **SSH `~/.ssh/config` `ControlPersist` parse error at line 25** | **Flag: an earlier session summary said this was "fixed by...", but the actual conversation text shows it was only ever worked around** (`ssh -F /dev/null`, `rsync -e "ssh -F /dev/null"`), never fixed at the source. It resurfaced as the likely cause of both an `ssh` failure and an `rsync` failure on July 14. Low priority since the workaround works, but don't let anyone (including me) tell you it's fixed until `sed -n '20,30p' ~/.ssh/config` gets a real heredoc rewrite. |
| 5 | SLURM `wandb` `ModuleNotFoundError` on the sweep batch job | Job `829351` (and a predecessor) crashed twice at line 5 because `pip install wandb` landed in a different Python environment than the one the `.slurm` script activates (the correct one is `/work/11603/jcerrell0629/vista/.venv`). A fix was prescribed but the actual successful 36-run sweep ran via **interactive `idev`, not this SLURM path**. Your results are real and usable; the *unattended* batch path is unconfirmed working for any future larger sweep. |
| 6 | Vehicle density implausibility (new, from the 36-run sweep) | `density_plausible=False` for all 3 classes: sedan 336.61, pickup 306.51, SUV 482.61 kg/m3, vs. a documented 100-300 kg/m3 range. Diagnosed as `solidify_columns` applying the identical truck-shaped splat silhouette to every vehicle class regardless of real footprint (confirmed via cubic-scaling math), not a mass/scale bug. **Not yet fixed.** |
| 7 | `bug-triage-protocol` Claude Code skill, 3-version conflict | Still unresolved. v1 (general, correctly global), v2 (Can-It-Ford-specific, buried in git history at `f6be080`), v3 (expanded version, briefly mis-deployed globally and reverted). Decision needed: v2 or v3 into the repo-local skills path. |
| 8 | Dead W&B key still in git history | Rotation is done, but the old key string is still recoverable from commit `50eff29` via `git log`. Purge via `git filter-repo` was deliberately deferred to closer to DesignSafe publication, not forgotten, just not urgent yet. |
| 9 | W&B run tagging (SPH-pilot vs. MPM-real) | Explicitly called "still incomplete" in the July 14 session. All 88+ runs exist but aren't cleanly separable by track/method in the dashboard yet. |
| 10 | Vehicle-number reconciliation gap (new finding, this audit) | The 36-run sweep used sedan 4.6m/1,240kg (1998 Dodge Neon), SUV 4.8m/2,020kg (1998 Ford Explorer), pickup 5.5m/1,930kg (1998 Chevrolet C1500). The live GitHub README's `vehicle_params.py` table shows **different** numbers: sedan 4.66m/1,390kg, SUV 4.96m/1,990kg, pickup 5.89m/2,300kg. Both are legitimately sourced from SAE 1999-01-1336, but one pulls specific named vehicle entries and the other pulls class averages. Not a "someone was wrong" bug, but it needs an explicit reconciliation decision before this goes in the paper or poster, or a reviewer/Kumar will ask which number is real. |
| 11 | Two collider APIs now coexist in kks32/mpm-engine | `add_sdf_collider` (old) vs. `add_cdf_collider` (new, CPIC/Hu et al. 2018, added via Kumar's 14-commit engine push). Whether `box_sdf_collider_setup.py` or any live script should migrate is unconfirmed. Low priority since FloodScene uses neither. |
| 12 | `truck_trimmed.ply` upload provenance | The specific question "did Kumar's July 10 re-upload actually replace the old file on Vista, or is the live copy still the backup" was flagged "STILL OPEN, THE ACTUAL GATE" on July 13 and never explicitly closed. Functionally moot now since the current live file works, but the historical question itself is technically still unanswered if it ever matters for provenance/citation purposes. |
| 13 | Kumar confirmation gaps (his 7 open asks, items 4-5) | Whether Kumar actually opened the GitHub link pushed via API in a prior session: never confirmed. Whether the two source papers (AR&R/Shand for L1, NWS for L0) were actually sent to him: status unconfirmed, verify before next meeting. |
| 14 | DesignSafe: Kumar as Data Depot team member | Publication requires Kumar to be structurally added as a team member on your specific Data Depot project entry (flagged July 13). Not confirmed done. |
| 15 | `git diff bcc478b..00bfbf1` fails `fatal: bad revision` in one Claude Code pane but succeeded in another | Never resolved, likely a stale/shallow-clone issue in the failing pane. Probably moot now but worth a `git fetch --unshallow` if it recurs. |

---

## 3. STATUS UNKNOWN, needs you to check (not confirmed either way)

| # | Item | What to check |
|---|---|---|
| 1 | Zotero freeze-on-quit fix | You were told to update Zotero to 8.0.4+ and update Better BibTeX to fix a known citation-key-migration hang. Did you actually apply it? Is the freeze gone? |
| 2 | gsplat training on the Drain A/B COLMAP output | COLMAP (structure-from-motion) gate-passed for both scenes on July 10. Was gsplat *training* on LS6 ever actually run on that output, or does it still only exist as camera poses/sparse points? |
| 3 | Real scene splat ever fed into FloodScene | Every FloodScene run so far (including the 36-run sweep) appears to use its own procedural/synthetic water block, not a reconstructed Drain A/B scene. Worth a direct grep of `flood_vehicle.py` to confirm whether it even has a code path for loading an external scene splat, or whether this needs new engineering. |
| 4 | Whether the 36 real calibration points clear the conformal-prediction N>=19 threshold | A July 13 note said crepes conformal prediction "cannot produce a finite 95% split-conformal threshold below N=19 real calibration points... nowhere near 19 exist yet." That assessment and the 36-run sweep completion appear close together in time and I can't confirm from the record which came first in that specific conversation. **Worth 5 minutes to just check: do you now have >=19 usable calibration points from the sweep, yes or no.** This could be a fast, real, currently-uncounted win. |
| 5 | TACC allocation consumption | As of July 13: Vista ~80% consumed, LS6 ~74%, Frontera ~32% (all expire after your end date). The 36-run sweep plus any reruns will have eaten into this further, worth a fresh check before planning more large sweeps. |
| 6 | Has Kumar been told about the FloodScene breakthrough yet | Multiple "already confirmed him told" notes exist for *older* findings (e.g., the July 9 Track 2 crash), but nothing confirms he's seen the July 13-14 breakthrough or the 36-run sweep results. Worth a short Slack update regardless of the README push. |

---

## 4. NEW ISSUES SURFACED BY THIS AUDIT SPECIFICALLY (not previously logged anywhere)

1. **HuggingFace Space bloat.** The live Space mirrors your *entire* repo tree, not just the Gradio app: citation PDFs, `designsafe-staging/`, screenshot images, everything. It still runs fine (Gradio only cares about `app.py` + `requirements.txt`), but it's slower to rebuild than necessary and puts things like citation source PDFs on a public demo surface that doesn't need them. Low priority cleanup, not a bug.
2. **`box_sdf_collider_setup.py` violates your own no-comments/no-docstrings rule.** The live GitHub copy has a module docstring and inline `#` comments. Minor, but worth a pass before Kumar reads it closely, given how explicit that rule is for you elsewhere.
3. **A summary-vs-live-text mismatch on the SSH bug (see Section 2, item 4)** is itself worth flagging as a pattern: the auto-generated chat summaries are good at capturing outcomes but occasionally round "worked around" up to "fixed." I verified this one against the actual message text and it's still open. This is exactly the discipline your project already enforces for code claims; it applies to my own summaries too now.

---

## 5. LIVE PLATFORM CHECK RESULTS (checked directly today, not from memory)

**GitHub (`jcerrell-IS/can-it-ford`):**
- README.md fetched live: dated July 9, describes pre-breakthrough state (see Section 2.1-2.2).
- `simulation/flood_vehicle.py`: 404, does not exist in the repo.
- `simulation/box_sdf_collider_setup.py`: exists, live, confirmed sedan-scale `(4.66, 1.79, 1.44)`, so that particular correction did make it in, but the file still has comments/docstrings (see Section 4.2).
- `data/track1_sweep_v1/manifest.csv`: 404, sweep results not pushed.
- Commit history: hit an unauthenticated GitHub API rate limit mid-check, could not pull a full recent commit list. Worth a `git log --oneline -20` directly on your own machine to see the true recent history rather than relying on my rate-limited external check.

**HuggingFace (`josiecerrell/can-it-ford`):**
- Runtime API confirms `"stage":"RUNNING"`, domain `"stage":"READY"`. **This Space is live and working right now.**
- `app.py` and `requirements.txt` inspected directly: clean, minimal, correct (L0 + L1 only, explicit `L2_NOTICE` string says "under active rebuild, no verdict published yet," which is honest and appropriately hedged).
- Last updated: July 13, 2026.

**Weights & Biases:**
- API is reachable (405 on an unauthenticated probe, expected). I did not and should not check your actual runs or tags directly, since that needs your own login and the standing rule is secrets/auth never go through me. You'll need to eyeball the run tagging yourself (see Section 3, item unclear... actually Section 2.9).

---

## 6. TOOL / COMMAND CORRECTIONS (things I was getting wrong or that need to be standardized)

**tmux, corrected per your explicit instruction:** whenever you ask for a divided/split tmux session, the answer is never Ctrl+B keyboard shortcuts typed from inside a live session. It's always the kill-and-rebuild one-liner, run from outside tmux:
```bash
tmux kill-session -t ford 2>/dev/null; tmux new-session -d -s ford; tmux split-window -h -t ford:0.0; tmux split-window -v -t ford:0.0; tmux split-window -v -t ford:0.2; tmux set -g mouse on; tmux attach -t ford
```
This is now saved to memory as a standing rule.

**Other confirmed-true environment facts worth keeping close, since they've each caused real wasted time before:**
- Track 1 (kks32/mpm-engine) must **never** run through Apptainer. Track 2 (Genesis) must **never** use the `mpmenv` venv. Conflating these has happened more than once.
- `$GENESIS_PATH` is unset at the start of every new Vista shell session, must be re-exported every time.
- Canonical Vista repo path is `/work/11603/jcerrell0629/vista/can-it-ford`. `~/can-it-ford` does not exist on Vista. Always `pwd` before running anything.
- On the Mac, use `conda run -n can-it-ford python3`, never bare `python3` (grabs system Python) and never `pip install`/`pip upgrade` against that env.
- `genesis` and `taichi` must never be imported in the same Python process on the Mac (GLFW conflict).
- Heredoc file writes are more reliable than nano edits for config files, especially `~/.ssh/config`, which has broken from manual edits more than once.
- `git pull --rebase` when mixing API pushes with local commits, never plain `git pull`.
- ARM64/GH200 `ffmpeg`: the system doesn't have it and `module avail ffmpeg` returns nothing. Fix is `pip install imageio-ffmpeg` inside the active venv (ships a static `aarch64` binary), not trying to find a system package.
- `rsync` tunnels through `ssh` silently, so it inherits any broken `~/.ssh/config` without necessarily printing a clear "config error" the way plain `ssh` does. If `rsync` fails mysteriously, check the SSH config before assuming it's an `rsync`-specific problem.

---

## 7. UNDERUTILIZED TOOLS: what you have that could do more for you

**Zotero.** Already being built out (6 collections, 5-tag system, Better BibTeX auto-export). Once the freeze issue is confirmed fixed, the piece you haven't used yet is the **Word/Google Docs plugin for one-click in-text citation insertion** when you write the final paper, this will save real time over hand-formatting citations. Also underused: the "Related" tab for linking sources that support the same threshold (e.g., all four DRIFT_THRESHOLD-adjacent papers together).

**HuggingFace, beyond hosting the demo.** You're using Spaces for the Gradio app, which is good, but two other HF features are relevant and untouched:
- **HF Datasets**: you could host the 36-run sweep CSV (and eventually the phase-space data) as a versioned HF Dataset, giving Kumar/Hassan/Cheng-Hsi a stable, citable, browsable link separate from the repo, and it's a natural DesignSafe-adjacent artifact.
- **A second, richer Space or a tab in the existing one**: once L2 has a real verdict, the Space could visualize the actual 36-run phase space interactively (you already have Plotly phase-space code in the repo), which is a stronger poster/demo artifact than the current arithmetic-only L0/L1 slider.

**Weights & Biases.** You have an Academic (Pro-feature) plan, confirmed, don't assume free-tier limits. The feature you're not using: **W&B Reports**, a shareable, narrative document that mixes live charts pulled straight from your logged runs with your own written commentary. This is a genuinely strong fit for both a Kumar progress update (link instead of a screenshot dump) and a poster-prep dry run (the "story" panels for the poster map almost directly onto a Report's structure). Once run tagging (SPH-pilot vs. MPM-real) is cleaned up, a Report becomes much more useful since you can filter by tag.

**Canva.** Template confirmed (56"x42" landscape), but board dimensions with Rosie are still unconfirmed. Worth doing that check now rather than at the last minute, since it gates whether the Canva canvas needs resizing.

**DesignSafe / TAP (TACC Analysis Portal).** Flagged previously as "worth experimenting with" for in-browser rendering without file transfers. Still untried. Given render pipeline hardening is on your build-order list, this could remove a whole rsync-and-view step if it works, worth a 20-minute spike once the higher-priority repo push is done.

**Mermaid Chart / Lucid connectors** (both available to you, currently unused for this project): either could generate a clean, correct pipeline diagram (video -> gsplat -> particle seeding -> MPM -> verdict) for the poster or README faster than hand-building one in Canva, and would stay editable as the pipeline itself changes.

---

## 8. PIPELINE STATE: what's actually done, what's missing, and your specific COLMAP-vs-PhysGaussian question

**Direct answer: neither is your current bottleneck.**

- **COLMAP is done** for both real scene captures (Drain A, Drain B), gate-passed at 100% and 99.6% registration on July 10.
- **PhysGaussian is no longer needed at all for the vehicle.** FloodScene ingests the vehicle splat directly; the PhysGaussian-bridge idea (originally scoped as the hardest missing piece of the whole rebuild) has been bypassed by a simpler, already-working mechanism.

**The actual remaining gap is connecting the two halves you already have:** a working, splat-native vehicle simulation (FloodScene) on one side, and a gate-passed real scene reconstruction (Drain A/B) on the other, that have never been joined. Concretely:

1. Confirm whether gsplat *training* (not just COLMAP structure-from-motion) was ever run on the Drain A/B output on LS6.
2. Determine whether FloodScene has any code path for loading an external scene splat as the water/road geometry, or whether it only supports its own procedural water block. If the latter, **this is now the single genuinely novel piece of engineering left in the whole pipeline**, since the vehicle half turned out not to need custom bridging after all.
3. If FloodScene has no such path, decide whether to extend it (reuse the same `load_gaussians_ply` mechanism that already works for the vehicle, pointed at the scene splat instead) or whether a lighter-weight approach suffices for the poster timeline given how little time is left.

**Full remaining-work list, roughly in priority order:**

1. Push the FloodScene work (`flood_vehicle.py`, sweep script, sweep results) to GitHub and rewrite the README status section. **Do this before anything else.**
2. Fix the vehicle density implausibility bug (`solidify_columns` silhouette artifact).
3. Resolve whether a real reconstructed scene can feed FloodScene as water/road geometry (Section 8 above).
4. Reconcile the vehicle_params.py table against the actual sweep vehicle numbers.
5. Decide the `bug-triage-protocol` skill version (v2 vs v3).
6. Confirm the SLURM sbatch path actually works, for any future unattended sweep runs.
7. Confirm the Zotero freeze fix landed.
8. Check whether the 36 sweep runs clear the conformal-prediction N>=19 threshold.
9. Apply the failure-mode classifier (stuck/slide/topple/float + violation magnitude, already written in `failure_modes.py`) to the new real 36-run sweep data. This was previously blocked by the kinematically-fixed collider bug; that blocker no longer exists since FloodScene produces real rotation.
10. Confirm Kumar is added as a Data Depot team member, then plan DesignSafe publication for ~July 21-24 as already scheduled.
11. Confirm board dimensions with Rosie, finalize Canva poster build.
12. Send Kumar a short Slack update on the breakthrough, independent of the GitHub push.
13. Purge the dead W&B key from git history (still fine to defer to closer to DesignSafe publication, just don't forget it entirely).

---

## 9. Do This Now

1. **On MacBook, right now:** confirm the fixed tmux one-liner works for your next split session (Section 6).
2. **On Vista, in the repo:** `git status` and `git log --oneline -10` to see your own true recent history (mine got rate-limited).
3. **Push `flood_vehicle.py` and the sweep script/results to GitHub**, then rewrite the README status section to match reality. This is the highest-leverage single action available to you right now.
4. **Check the conformal-prediction N>=19 question directly** (Section 3, item 4), this might already be a free win.
5. **Confirm the Zotero freeze is actually gone** before trusting the citation workflow for the paper.

**Check-in:** Want me to draft the corrected README status section right now (I already have the exact live text to diff against), or do you want to handle the GitHub push yourself first and have me review the diff after?
