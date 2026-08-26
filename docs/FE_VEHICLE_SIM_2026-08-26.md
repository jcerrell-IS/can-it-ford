# The FE vehicle simulation, 2026-08-26

Successor to `FE_VEHICLE_AUDIT_2026-08-25.md`. That file records the audit; this one
records what was built and run afterwards, plus what
`MERGED_RESEARCH_READER_CORPUS_FINAL.md` changed about the physics claims.

Every number below is tagged by how it was obtained: `[READ]` directly from a file or
tool output, `[RUN]` produced by a job this session launched, `[RECALLED]` carried from
another document and not re-derived here.

---

## 1. A defect in tooling this project already pushed

`analysis/fe_vehicle/setfile_mass.py` read `*ELEMENT_MASS_PART` with

    f = line.split()
    if len(f) == 2:

**That is a Yaris-shaped test.** The two COARSE decks (Yaris v1l, Silverado v3a) write
two whitespace fields per row, `pid addmass`. The two DETAILED decks (Rogue v3, Camry
v5a) write four, `pid addmass finmass lcid`. So every Rogue and Camry row was skipped in
silence and the function returned `0.00 kg` `[READ]`.

**The failure mode is the dangerous one: it did not error, it returned a clean zero, and
a zero reads as a real absence.** On 2026-08-25 that zero was written into
`profiles/rogue_density_profile.json` as `setfile=ABSENT`, pushed to origin in `dcf519e`,
and would have been carried forward as a fact about the vehicle rather than a fact about
the parser.

Fixed 2026-08-26. The row test now accepts two-or-more fields and takes `f[0]`, `f[1]`.

**A second thing the fix exposed, and it is not recoverable from what ships.** The Rogue
writes its three largest added masses as LS-DYNA `*PARAMETER` references glued to the pid
field: `2001008&m1_1` (Passenger h3 50th), `2001047&m2_1` (Passenger h3 5th),
`2000447&m3_1` (Payload). **No `*PARAMETER` card defining `m1_1`, `m2_1` or `m3_1` exists
anywhere in the model directory** `[READ]`. Those masses cannot be resolved from the
distributed model. The parser now prints them to stderr rather than dropping them, so the
Rogue total is known to be a **lower bound** instead of looking complete.

---

## 2. Four independent mass validations, none of them fitted

With the fix, all four decks parse. Structural mass from the main deck, added mass from
the companion set file `[RUN, this session]`:

| vehicle | structural | set file | total | external reference | delta |
|---|---|---|---|---|---|
| Yaris coarse v1l | 867.81 | 228.50 | **1096.31** | 1101, CCSA FE model, slide 7 of DOI 10.13021/G8JS5D | **-0.43 %** |
| Camry detailed v5a | 1141.73 | 333.71 | **1475.44** | ~1475, published 2012 Camry curb | **~0 %** |
| Rogue detailed v3 | 1364.36 | 202.00 | **1566.36** | ~1600, published 2020 Rogue curb | **-2 %**, and a lower bound |
| Silverado coarse v3a | 1887.62 | 263.57 | **2151.19** | ~2200, published 2007 Silverado curb | **-3 %** |

Nothing here was tuned to match. The Yaris row is the strongest because the reference is
the model's own declared value in its own validation report, not a vehicle spec sheet.

**Do not read the Rogue's -2 % as agreement of the same quality as the others.** Three of
its added masses are unresolved (section 1), so its true total is higher than 1566.36 and
the -2 % is an accident of how much is missing.

---

## 3. The four density profiles, rebuilt on the corrected hulls

`profiles/*_density_profile_v3.json`. Built by mapping each vehicle's own FE mass
distribution onto the solver's own particle cloud, band by band in height, expressed as
FRACTIONAL height so the profile transfers across resolutions `[RUN]`.

| vehicle | CG uniform, error | CG profiled, error | reduction | bands |
|---|---|---|---|---|
| Yaris | +89.1 mm | **-8.0 mm** | 91 % | 15 |
| Camry | +74.3 mm | **-2.3 mm** | 97 % | 14 |
| Rogue | +92.3 mm | **-1.7 mm** | 98 % | 18 |
| Silverado | +69.0 mm | **+4.6 mm** | 93 % | 19 |

Total mass is preserved exactly at the canonical 1100 kg in every case; only the vertical
DISTRIBUTION changes. **This is not wiring an inertia tensor.** CLAUDE.md item 4 forbids
that and `.claude/checks/params_check.py check_inertia_wired()` enforces it. No tensor is
written. The solver still derives CG and inertia from its own cloud.

---

## 4. Infrastructure: LS6 reaches Vista's engine

Recorded because it contradicts a note carried in memory as "LS6 has no warpmpm", and
because it doubles the compute available to this project.

Measured live 2026-08-26 `[READ]`:

- `/scratch/11603/jcerrell0629/warpmpm_ls6_env/bin/python` survives, with torch 2.8.0+cu128.
- Its own bundled warpmpm copy at `instantsplat_probe_2026-08-13/warpmpm` **lacks**
  `solidify_watertight`, which is why a naive import fails and reads as "no warpmpm".
- **`$WORK` is shared Stockyard, so LS6 can read
  `/work/11603/jcerrell0629/vista/mpm-engine/src` directly.** With `PYTHONPATH` set to it,
  `from warpmpm.vehicle import solidify_watertight` succeeds on LS6.

So LS6 runs **the identical engine `627367e` that Vista runs**, with no copy and no
version skew. The correct statement is "LS6 has no warpmpm INSTALLED", not "LS6 cannot run
warpmpm". Allocation BCS20003 holds 9,536 SU on LS6 against 551 on Vista, so the bulk
sweeps belong there.

Recipe:

    PY=/scratch/11603/jcerrell0629/warpmpm_ls6_env/bin/python
    export PYTHONPATH=/work/11603/jcerrell0629/vista/mpm-engine/src
    #SBATCH -p gpu-a100-small -A BCS20003

---

## 5. What the research corpus changed

Read from `docs/MERGED_RESEARCH_READER_CORPUS_FINAL.md`, sha256 `18c88761181e5805`,
byte-identical to the copy in `~/Downloads` `[READ]`.

### 5.1 Volumetric locking is refuted as the mechanism, and the refutation must travel

Section 5.2. Explicit MPM volumetric locking over-predicts force transmitted to a rigid
body by 45 to 55 percent in a strip-footing benchmark and is not fixed by refinement;
Job B here measures +34 to +64 percent with the same sign `[RECALLED]`. That made locking
the obvious hypothesis, and its pre-registered discriminator was a particles-per-cell
sweep, because locking predicts error rising with PPC while velocity-projection bias
predicts flat.

**Job 923239 ran that sweep and it came out against locking**: a log-log slope of
**+0.0596** where `PPC^-2` demands **-2** `[RECALLED]`.

Two consequences, and both are now honoured in this project's render captions:

1. **Do not add F-bar as a fix.** It would be treating a diagnosis its own discriminator
   already answered.
2. **Do not write that Job B is understood.** The flat slope is *consistent with*
   velocity-projection bias, which is not the same as establishing it. Section 5.3's two
   competing mechanisms remain undiscriminated. The over-prediction is OPEN.

Separately and still standing: the pinned solver has no F-bar, no J-averaging, no pressure
smoothing, and no locking mitigation of any kind `[RECALLED]`.

Also from section 5.4: the plateau is **GRID-SET**. Never write "O(h)"; that scaling was
read off a figure by eye and is withdrawn at its root.

### 5.2 Two DOIs verified against Crossref this session

| DOI | resolves to | corpus claim | verdict |
|---|---|---|---|
| `10.1016/j.cma.2018.01.010` | Coombs, Charlton, Cortis, Augarde, "Overcoming volumetric locking in material point methods", CMAME 2018 | the canonical anti-locking reference, catalogued but cited nowhere | **confirmed**, and `research_index.py --query "volumetric locking"` still reports it `[UNCITED]` |
| `10.1016/j.proeng.2017.01.041` | Zhao, Liang, Martinelli, "Numerical Simulations of Dam-break Floods with MPM", Procedia Engineering 2017 | MPM front position moves under 1.6 % across 2x mesh and 2.5x particle density | **confirmed** |

### 5.3 This project sits inside Zhao's tested particle density

Zhao et al. swept 4, 8 and 10 material points per element. This driver sets `h = dx/2`,
confirmed on all four vehicles from the probe's own `INSTRUMENT` line (`dx/h = 2.000`
exactly), so it runs at **8.00 particles per cell by construction** `[RUN]`. That is
squarely inside the tested range. The project's particle density is not unusual by that
paper's standard, which is a mild but genuine reassurance it did not previously have.

### 5.4 The caveat corpus 6.5 attaches to Zhao is now being measured, not asserted

Section 6.5 warns that Zhao measured a **kinematic free-surface** quantity while this
project's non-monotone quantity is a **coupled rigid body**, that there is no body
anywhere in Zhao et al., and that the paper therefore "does NOT license a claim that this
project's forces are resolution-insensitive."

**That caveat had never been measured, only asserted.** LS6 job 3389807 measures it: the
same refinement ladder, in this project's own solver, reporting a kinematic observable and
a coupled-body observable side by side. Results in section 7.

### 5.5 A defect found in the corpus tooling, NOT fixed here

`research_index.py show()` prints the flag **`IN-PAPER`** whenever `cited_reader_facing`
is true. That field is defined as "the DOI string appears somewhere in a reader-facing
directory". CLAUDE.md's own ladder puts that at 43 papers against **3** that are actually
`\cite`d and print, so the label overstates by roughly 14x.

Verified on a concrete counter-example `[READ]`: the index prints `[IN-PAPER]` for
`10.1002/nme.7347` (Zhao, Jiang and Choo, "Circumventing volumetric locking in explicit
material point methods", IJNME 2022). Grepping `paper/can_it_ford_references_IEEE.bib`,
`paper/conference_101719.tex` and `paper/prior_art_additions.bib` for `nme.7347`,
`Zha22d`, `Circumventing` and `locking` returns **zero** hits; the only near-match is the
unrelated bibtex key `flyvbjerg1989blocking`. Every real occurrence is in `docs/`.

**Not fixed here** because `analysis/research_index.py` and
`data/research_corpus_index.json` were both uncommitted-dirty with another session active
in this repo. Editing them would entangle with that session's work, which CLAUDE.md
prohibits. Filed for whoever owns that file.

Worth noting alongside corpus section 6.13: that section names Coombs 2018 as the
canonical anti-locking reference and calls it the cheapest next step. It does not mention
that `10.1002/nme.7347` covers the same ground for **explicit** MPM specifically, which is
this project's solver. Both are uncited in the shipped paper.

---

## 6. The flagship: all four classes, everything applied at once

Vista job **940279**, 24 runs, 9 min 19 s, every run `rc=0`. Engine `627367e`, driver
sha256 `ff819f6dc0ade4e9` `[RUN]`.

Corrected flood-fill hull, audited v3 density profile, **6 water layers**, and dx matched
across vehicles by choosing `n_grid` per vehicle from its own `grid_lim`. That last point
matters: a fixed `n_grid` does NOT fix resolution here, because `grid_lim` follows hull
extent. The realised spread is **dx 0.098165 to 0.098794, 0.64 percent** across four
vehicles of very different size.

Two preflight numbers worth recording, neither of them tuned:

- Yaris hull `3.553211 m3` against this project's own independently built `3.542739`,
  **+0.296 percent**. The 50 mm sealing-scale calibration holds.
- Yaris `realized_rho` **310.29** against `gates.py` `RHO_REF` **310.49**, 0.06 percent.

### 6.1 The FE density profile raises displacement in all four, and moves no verdict

Mean +/- sd over 3 repeats at identical configuration and seed `[RUN]`:

| vehicle | disp A uniform | disp B profiled | change | sigma |
|---|---|---|---|---|
| Yaris | 0.677619 +- 0.000959 | 0.829297 +- 0.001124 | **+22.4 %** | 145 |
| Camry | 0.912404 +- 0.000926 | 1.057929 +- 0.000657 | **+15.9 %** | 181 |
| Rogue | 0.517841 +- 0.000448 | 0.566459 +- 0.000606 | **+9.4 %** | 91 |
| Silverado | 0.227971 +- 0.000210 | 0.241222 +- 0.001592 | **+5.8 %** | 12 |

Gate P-2, limit 0.10:

| vehicle | A | B | verdict |
|---|---|---|---|
| Yaris | 0.1228 | 0.1302 | **0/3 -> 0/3**, fails in both |
| Camry | 0.0876 | 0.0875 | 3/3 -> 3/3, passes in both |
| Rogue | 0.1279 | 0.1247 | **0/3 -> 0/3**, fails in both |
| Silverado | 0.0916 | 0.0912 | 3/3 -> 3/3, passes in both |

**No verdict moves anywhere.** That extends `0845e1c`'s finding rather than contradicting
it: the mass distribution relocates where P-2 fails, and at dx-matched 6-layer resolution
on corrected hulls it does not repair it in a single one of the four classes.

### 6.2 The headline: at matched everything, geometry alone spans a factor of four

All four runs hold mass at 1100 kg, depth at 0.30 m, velocity at 1.5 m/s, hull-generation
method identical, and dx matched to 0.64 percent. The **only** thing that varies is the
shape of the vehicle `[RUN]`:

| vehicle | AR&R class | displacement | P-2 |
|---|---|---|---|
| Camry | large passenger | **0.9124** | 0.0876 PASS |
| Yaris | small passenger | 0.6776 | 0.1228 FAIL |
| Rogue | large passenger | 0.5178 | 0.1279 FAIL |
| Silverado | large 4WD | **0.2280** | 0.0916 PASS |

**A factor of 4.00 in displacement, from geometry alone.** And the ordering follows
neither mass (all equal by construction) nor AR&R class: the largest vehicle slides least.

**Camry and Rogue are both AR&R "large passenger" and receive identical published
thresholds** (still-water depth 0.4 m, D x V <= 0.45, from Table 3 of
`citations/ARR_Project_10_Stage2_Report_Final.pdf`). At matched dx they differ by **76.2
percent in displacement and land on opposite sides of gate P-2.** This is the sharpest
form of the claim CLAUDE.md item A-3 carries from the literature, that stability depends
on displaced volume and underbody shape rather than mass, and it is now a measurement in
this project's own solver rather than a citation.

---

## 7. A retraction: the Rogue roll result was a hull artifact

On 2026-08-25 I reported that the Rogue at `n_grid` 96 showed `final_roll_deg` moving
0.274 to 0.861 degrees under the FE density profile, a 271-sigma increase, and drew two
conclusions from it: that **the SUV is the roll-active class**, and that the direction was
**backwards**, since lowering the CG increased roll.

**Both are withdrawn.** In the flagship the Rogue's roll is -0.00098 -> -0.00084 degrees,
0.1 sigma, i.e. nothing at all.

Those two runs differ in **two** things, hull and grid, so neither could be blamed. Vista
job **940319** isolates it: `n_grid` held at 96, the **only** change being the hull, from
the Poisson hull to the corrected flood-fill hull `[RUN]`:

| | roll A | roll B | delta |
|---|---|---|---|
| Poisson hull, g96 (2026-08-25) | 0.274 | 0.861 | +271 sigma |
| **Corrected hull, g96 (this control)** | -0.001193 +- 0.000897 | -0.000950 +- 0.001216 | **+0.2 sigma** |

**The roll response was a property of the hull, not of the vehicle and not of the grid.**
Changing only the hull removes all of it. The "backwards direction" anomaly disappears
with it, because there is no longer an effect whose direction to explain.

Displacement in the same control moves +10.5 percent (0.708514 -> 0.782935), consistent
with the flagship's +9.4 percent at `n_grid` 105, so the profile itself behaves normally
on this vehicle. It was only ever the roll channel that was contaminated.

**The roll-active vehicle, on corrected hulls, is the Silverado**, at 0.880 degrees where
the other three sit under 0.005. And there the FE profile **lowers** roll, 0.880038 to
0.735477, a 16.4 percent drop at 76 sigma, which is the physically expected direction for
a lowered centre of gravity. So the corrected hull fixed the sign as well as the size.

---

## 8. A bug in a render script this project already pushed

`analysis/fe_vehicle/render_sequence.py` defaulted to `--engine EEVEE`. On Blender 5.2.0
LTS that path renders this scene **almost black**: the vehicle is a silhouette and the
water loses refraction completely, at every camera angle tried `[RUN]`.

It is not a bad engine identifier. `BLENDER_EEVEE` is the only entry in
`RenderSettings.engine`'s enum on 5.2 and it assigns cleanly, so EEVEE is being selected
correctly and simply does not light this scene, most plausibly because a transmissive
isosurface with no light probe falls back to near-black.

Cycles renders the identical scene correctly at **11.6 s/frame** at 1600 px / 64 samples,
against roughly 4.7 s/frame for the black EEVEE output, so correctness costs about 2.5x
and there is no reason to prefer EEVEE here. **Default changed to CYCLES.** `--engine
EEVEE` still selects the old path.

---

## 9. LS6: the corpus 6.5 caveat, measured

LS6 job **3389807**, 36 runs, 26 min, A100-PCIE-40GB, engine `627367e` and driver sha256
`ff819f6dc0ade4e9` **identical to Vista's** `[RUN]`. Yaris and Silverado, corrected
flood-fill hulls, uniform density, `n_grid` 72 to 132, 3 repeats per cell.

Corpus section 6.5 warns that Zhao et al. 2017 measured a **kinematic free-surface**
quantity, this project measures a **coupled rigid body**, and the paper therefore does not
license a resolution-insensitivity claim here. This job measures both, side by side, on
the same ladder.

### 9.1 Nothing converges, and the body observable is worst

Spread across the whole ladder, `(max-min)/mean` `[RUN]`:

| observable | kind | Yaris | Silverado |
|---|---|---|---|
| `local_depth_bow_peak` | kinematic | 16.80 % | 20.20 % |
| `local_depth_footprint_peak` | kinematic | 45.58 % | 43.55 % |
| `passthrough_max_frac` | coupled body | 21.64 % | 22.43 % |
| **`final_disp_mag_m`** | **coupled body** | **57.59 %** | **118.31 %** |

**The caveat's direction is confirmed and its premise is not.** The coupled-body
displacement is 3.4x (Yaris) and 5.9x (Silverado) worse than the best kinematic observable,
which is the ordering corpus 6.5 predicts. But the kinematic observables here are **also**
badly unconverged, at 17 to 46 percent against the **1.53 percent** Zhao reports. So the
honest statement is stronger than the caveat: **this project cannot claim resolution
insensitivity for ANY observable, kinematic or coupled**, and citing Zhao et al. in support
of one would be wrong twice over.

### 9.2 Gate P-2's verdict is resolution-dependent, and for the pickup it is not monotone

P-2, limit 0.10, 3 repeats per cell `[RUN]`:

| `n_grid` | 72 | 84 | 96 | 108 | 120 | 132 | flips |
|---|---|---|---|---|---|---|---|
| **Yaris** | PASS | FAIL | FAIL | FAIL | FAIL | FAIL | 1 |
| **Silverado** | FAIL | **PASS** | **PASS** | FAIL | FAIL | **PASS** | **3** |

Every cell is unanimous across its 3 repeats, so these are not split decisions or noise.

**The Silverado's P-2 verdict flips three times as the grid refines**, and it is passing at
the finest grid tested after failing at two intermediate ones. **Any P-2 result quoted at a
single resolution is a statement about that grid, not about the vehicle** — and that
includes section 6's flagship table and the canonical 17.

### 9.3 This is not noise, by a factor of several hundred

| vehicle | repeat sd at fixed config | spread across the ladder | ratio |
|---|---|---|---|
| Yaris | 0.1193 % | 57.59 % | **483x** |
| Silverado | 0.1771 % | 118.31 % | **668x** |

The solver is very slightly non-deterministic at fixed configuration and seed, about 0.1
to 0.2 percent, which matches the 0.19 percent measured on 2026-08-25. Resolution moves
the answer several hundred times harder than that.

### 9.4 A confound that must travel with this ladder

**Mesh refinement and depth resolution cannot be separated in this driver.** It sets
`h = dx/2`, so refining the grid also refines the particle spacing, and `water_layers`
moves across the ladder: 5,5,6,7,8,8 for the Yaris and **3**,4,4,5,6,6 for the Silverado.
At the coarse end the Silverado resolves the flow depth on **three particle layers**, which
is severely under-resolved and is the likely reason its `g72` displacement, 1.0769, is the
largest number in the table.

So this ladder measures "refine everything together", which is the only refinement this
driver can express. It is **not** Zhao's design, which varied mesh and particle density
independently. Separating them needs an `h` that is free of `dx`, which the driver does not
expose. That is the right next experiment and it is not expensive.

