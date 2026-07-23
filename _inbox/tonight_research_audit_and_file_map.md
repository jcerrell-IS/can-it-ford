# Tonight's Research, Audited and Placed. What to Keep, What's Stale, Where Everything Goes

Built by reading every file this actually touches, not by assuming. Where I couldn't verify something live (Vista, LS6, your Mac, your actual repo state), that's stated, not guessed.

---

## Read this first: one file resolves more than anything else tonight

**`vehicle_data_master_reference_2026-07-21.json`**, already sitting in your project knowledge, is the single most valuable thing that came out of tonight. It:

- **Settles the Dodge Neon inertia conflict for good.** Ixx 441 / Iyy 1748 / Izz 1945 is correct, matches your existing verified file. The Perplexity upload's 2618/515/2684 was wrong. Don't use those numbers, don't re-litigate this.
- **Flags a real, small, previously-unknown precision issue**: the actual NCAC Yaris page states modeled weight is **1,078 kg**, not the 1,100 kg MASH nominal you've been computing rho from. That's `rho = 1078 / 3.5427 = 304.28 kg/m³`, about 2% different from what you've been using. Small, but worth a fix before this goes in the paper, not after.
- **Confirms, by direct inspection, that the NHTSA vPIC JSON files in your project contain zero physical data.** I checked myself: they're Make/Model name lookups, nothing else. Stop treating them as a physics source, they were never going to have one.
- **Gives real, working, checksummed download URLs for the Yaris**, coarse and detailed both, which nobody had pulled directly before tonight.
- **Explicitly supersedes** `vehicle_class_research_summary_2026-07-21.json`. That file is now stale, keep it for history, don't cite from it.

**Action: pull this one file to Vista now**, it's the thing every other vehicle-parameter decision should check against going forward.
```
scp "vehicle_data_master_reference_2026-07-21.json" jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford/reference_data/
```

---

## Stale, superseded, or confirmed empty, don't reach for these anymore

| File | Status | Why |
|---|---|---|
| `vehicle_class_research_summary_2026-07-21.json` | Superseded | Explicitly superseded by the master reference above, same day, more verified |
| `NHTSA_vPIC_JSON_-_dodge_neon_1998`, `json_NHTSA_vPIC__Ford_1998_explorer`, `json_NHTSA_vPIC_Chevrolet_1998_C1500` | Confirmed empty for your purpose | Verified directly just now, Make/Model name lookups only, zero weight/inertia/dimension data. Fine for confirming a vehicle existed, useless for physics |
| `MPM_Flood-Vehicle_Reference_Data__Sedan__SUV__Pickup.md` (the Perplexity upload) | Partially stale | The Silverado section and friction discussion are fine and cross-check clean. The Dodge Neon inertia table specifically is wrong, contradicted by the master reference. Don't delete the file, just don't trust that one table |
| Anything still citing the old "16 divergence points, 30.4% agreement" figure | Stale, per your own July 20 audit | Superseded by 14 points / 39.1% agreement, already flagged in your project history, repeating it here since it's exactly the kind of thing that resurfaces if a file gets re-read out of order |

**What I can't audit from here:** whether Vista's actual `vehicle_params.py` or `can_it_ford_L2.py` currently reflect the corrected Yaris rho (304.28 vs whatever's hardcoded now). That needs a live grep, not a guess, listed below.

---

## New files worth pulling out of project knowledge, ranked, with exact destinations

| Priority | File | Where it goes | Why |
|---|---|---|---|
| 1 | `vehicle_data_master_reference_2026-07-21.json` | Vista, `reference_data/` | Covered above, the load-bearing one |
| 2 | `genesis_vs_mpmengine_fluid_research.md` | Vista, `docs/` or repo `docs/` | Your six-question physics research, sourced, already in project knowledge from earlier tonight |
| 3 | `Simulation-Ready_Vehicle_3D_Assets_for_MPM_SPH_Flood_Traversability_Simulation.md` | Vista, `reference_data/` | The DrivAerNet finding specifically, real mesh, no LS-DYNA conversion needed, worth having on hand if you go that route |
| 4 | `vehicle_files_to_pull.md` | Mac only, working notes | This is a task-tracking doc, not citable research, keep it local, don't clutter the repo with it |
| 5 | `MPM_Flood-Vehicle_Reference_Data__Sedan__SUV__Pickup.md` | Vista, `reference_data/`, with a note | Keep for the Silverado/friction sections, flag the Neon table as superseded right in the filename or a header if you move it |

None of tonight's export_all/zshrc work belongs in `can-it-ford` at all, that's Mac tooling, keep it in `~/.zshrc` and the scripts folder, not the research repo.

---

## The forking question, direct answer

Forking `kks32/mpm-engine` was already the right call, already covered. For everything else found tonight, **no, don't fork**:

- **DrivAerNet** (`github.com/Mohamedelrefaie/DrivAerNet`): don't fork, just clone or download the specific mesh you want. You're not modifying their code, you're taking an asset.
- **splashsurf**: same logic, use it as a tool, fork only if you end up patching it to build on aarch64, which is a real possibility given the wheel gap I flagged earlier, worth revisiting if `pip install` fails on Vista.
- **CarCrashNet**: not worth forking or cloning yet, it's VTKHDF simulation output, not a mesh source, lower priority than everything above.

Forking is for code you'll edit and want tracked. Everything else above is a data/asset source, plain download is faster and there's nothing to sync back.

---

## What to actually check live before trusting any of this further

I can read files, I can't SSH into Vista, LS6, or your Mac from here. These are the specific live checks worth running, not guesses:

```
# On Vista, confirm what rho is currently hardcoded to
grep -rn "1100\|1078\|rho.*=.*30[0-9]" ~/vista/can-it-ford/simulation/can_it_ford_L2*.py ~/vista/can-it-ford/vehicle_params.py 2>/dev/null

# Confirm the master reference actually landed where you think
ls -la ~/vista/can-it-ford/reference_data/
```

**Check-in:** want me to draft the exact one-line rho fix (1100 to 304.28-based) as a ready-to-paste sed command, or do you want to look at the surrounding code first in case it's used in more than one place?
