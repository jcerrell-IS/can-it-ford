# Lane P, poster build, 2026-07-25

Working directory `/Users/josie/can-it-ford`, verified with `pwd`. Git dir is `.git`, not a
worktree, so the project-scoped `scite` MCP is live here (confirmed with `claude mcp list`:
`scite: https://api.scite.ai/mcp - Connected`). No SSH from this lane. Nothing committed.

Skills loaded: `provenance-audit`, `flood-mpm-debugging-reference`, `connector-router`,
`anthropic-skills:canva-design-assistant`. `can-it-ford-science` and `can-it-ford-cluster` are
NOT installed on this Mac and were not looked for. Nothing was silently substituted.
`/context` is not invocable in this harness and was not run.

## CAN Cerrell_TACC_42x56.pdf EXIST BY SUNDAY NIGHT

**YES. It already exists.** `/Users/josie/can-it-ford/Cerrell_TACC_42x56.pdf`, 404,019 bytes,
1 page, page size 4032 x 3024 pt = exactly 56 x 42 in landscape. Two gaps remain, neither of
which blocks a printable file: the two logo slots are empty because no logo asset exists
anywhere in the repo, and the reserved QR area is empty by your instruction.

## BUILD PATH

HTML plus headless Chrome, zero installs, reproducible from the repo.

- Source: `poster.html` at repo root. `@page { size: 56in 42in; margin: 0; }`, LANDSCAPE.
  The pane monitor:0.1 proposal of `42in 56in` was portrait and is not what shipped.
- Figures embedded as SVG for vector quality. `figures/fig1_l1_three_class.pdf` and
  `figures/traction_bias.pdf` were converted to SVG with `pdftocairo -svg`, which was already
  on the Mac at `/opt/homebrew/bin/pdftocairo`. No raster figure is used.
- Render command, exactly:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --allow-file-access-from-files --virtual-time-budget=30000 \
  --print-to-pdf=Cerrell_TACC_42x56.pdf "file:///Users/josie/can-it-ford/poster.html"
```

- Verify with `pdfinfo Cerrell_TACC_42x56.pdf`. Success is `Pages: 1` and
  `Page size: 4032 x 3024 pts`. The most likely failure mode is `Pages: 2`, which means a
  column overflowed; it happened twice during this build and was fixed by tightening type,
  not by cutting content.
- Layout is a header band, a three-column grid at 16.4 / 16.4 / 18.667 in, and a full-width
  footer band. Column three is 18.667 in because `figures/fig1_CAPTION.md:54` states the figure
  is authored at exactly one third of the 56 in board width for 1:1 placement, so its specified
  point sizes are the printed point sizes.

**Environment confirmed, not assumed.** `/opt/homebrew/bin/python3` has no matplotlib and there
is no `python` on PATH. No figure can be regenerated from this Mac. Everything was embedded, not
rebuilt.

## THE FIVE DECISIONS

**1. QR strip: DROPPED for content, slot reserved and empty.** Repo confirmed PRIVATE via
`gh repo view`. You reported the Gradio Space resolves but is in HuggingFace Configuration
error and renders a red error page to any scanner. No GitHub QR, no DesignSafe QR. A
QR-sized area, 3.6 x 3.6 in, is reserved at bottom right of the footer as `div.qr-reserve`. It
is empty white space with no border, so **if no URL arrives the PDF is already correct and
needs no edit**. If a verified URL arrives, drop one `<img>` inside that div and re-render.

**2. Hero: `figures/fig1_l1_three_class.svg`.** Backed by asset table row 1, the only VERIFIED
figure row in the table. Placed at native 1:1 in column three with the full caption from
`figures/fig1_CAPTION.md`, including the caption's own known issue: four of the 70 cells are
decided by floating-point representation at the cap boundary rather than by the criterion, and
two of the twelve hatched cells would differ under an exactly inclusive comparison. The Vista
mp4 still was NOT used; this lane does not SSH and no still frame exists on the Mac.
`figures/hero_shot_test.png` was not used, per its RETRACTED status.

**3 and 4. Pipeline diagram: rebuilt as `figures/pipeline_diagram_poster.svg`.** The original
`figures/can_it_ford_pipeline_diagram.svg` was NOT modified, because it is embedded at
`README.md:32` and is a provenance record. Changes in the new file:

- "Genesis MPM" replaced with "kks32/mpm-engine", in both the pipeline box and the L2 rung.
- "SPH water + rigid" replaced with "MPM water + rigid".
- "PhysGaussian bridge" struck, replaced with "60k surface sample" and "column fill", which is
  what `vehicle.py` actually does.
- The entire core-finding box deleted, including the friction-invariance sentence, per section
  6.5's outright retraction of the L1 versus L2 divergence claim.
- L1 rung corrected to "d > 0.30 m or D x V > 0.30" and "= NO-FORD (small passenger)".
- L2 rung now reads "no verified verdict yet" rather than asserting NO-FORD.
- The `<desc>` accessibility text was rewritten; it also named Genesis MPM.

**Correction to your instruction, live-checked.** You said the 0.60 4WD figure is stale and
`four_wd` raises ValueError at `vehicle_params.py:184`. The numbers you gave are right and I
used them, but the reason is not. Live read: the class keys are now `small_passenger`,
`large_passenger`, `large_4wd`, renamed in `63e677f`. `small_passenger` carries
`depth_m 0.30, haz_m2s 0.30` at line 167, exactly as you said. **0.60 is not stale as a
value**: it is the live `large_4wd` haz at line 179. What is stale is the old key name. The
ValueError is at **line 188**, not 184, and it fires for any key absent from
`AR_R_STABILITY_LIMITS`, which is why the retired `four_wd` would raise. Labelling the rung
small-passenger-only is still correct, because it matches `gen_scenario_sweep.py`'s default and
asset-table note 8's warning not to straddle two classes.

**5. Mock poster signup Google Sheet: STILL OPEN.** No link was provided and this lane cannot
verify it. Not in scope, not done, recorded here so it is not lost.

## SCOPE CORRECTION, IMPORTANT

The brief said Results and Conclusions do not exist and to draft both. **They did exist**, in
`docs/POSTER_TEXT_BLOCKS.md` sections 6 and 7, written 2026-07-25 by pane ford-F4 with a full
provenance table. Drafting fresh would have produced a second competing version of
better-sourced text.

Per your ruling, sections 6 and 7 were left **intact** as the long-form source for the July 31
paper, and the condensed poster cut was written as **new section 12**, with **new section 13**
carrying a line-by-line diff of what was cut. Cuts are prose only. No number, no table row, no
caveat and no PENDING tag was dropped. New section 11 records the F0 evidence.

## PROVENANCE CONFLICT, NEEDS YOUR CALL, DOES NOT BLOCK PRINTING

There are now **two different F0 grid-gate handoffs with contradictory numbers**:

| | This session's F0 (Vista) | The Mac pane's F0 (15:39) |
|---|---|---|
| lim | 9.4217 m | 14.9890 m |
| dx at n_grid 64 | 0.14721 | 0.2342 |
| n_particles at 64 | 19,333 | 5,323 |
| solid_volume at 64 | 7.71011 m3 | 8.5475 m3 |
| **ratio at 64** | **2.1763** | **2.413** |
| water layers at 64 | 4 | 3 |

**The Mac pane is wrong, and the cause is identifiable.** It computed
`lim = 3.5 * 4.2826 = 14.989`, which uses the raw bounding box and **skips `load_vehicle`'s
y-long-axis swap**. The live code rotates about z when `ext[0] > ext[1]`, and the raw Yaris
bbox is `[4.2826, 1.7464, 1.518]`, so that branch fires. After the swap `extent` is
`[1.7464, 4.2826, 1.518]` and `lim = max(2.2*4.2826, 3.5*1.7464, 1.8) = 9.4217`. That pane
explicitly considered 9.4216 and rejected it as "not the convention in use".

**2.17 is corroborated three ways and 2.41 stands alone:** ledger A9 gives 7.698 / 3.5427 =
2.173; F4's section 6.3 independently states "2.17 times the hull's true volume"; this
session's direct measurement gives 2.1763 and a solid volume of 7.71011 m3 against A9's 7.698,
a 0.16 percent difference. **The poster prints 2.17.** The Mac F0 handoff and its INDEX line
should be corrected or withdrawn by whoever owns that pane. Not touched by this lane.

The water-layer disagreement, 4 versus 3, follows from the same lim error. **It does not appear
on the poster**, so it is not a print blocker.

## CITATION GATE

Run through scite before anything landed:

- `10.1111/jfr3.12527` resolves to "Full-scale testing of stability curves for vehicles in flood
  waters". DOI and attribution to Smith, Modra and Felder 2019 are **correct**. Shipped.
- `10.1111/jfr3.12885` resolves to "Confirmation of vehicle stability criteria through a
  combination of smoothed particle hydrodynamics and laboratory measurements". DOI and
  attribution to Azhar et al. 2023 are **correct**, but scite returned no full-text excerpts,
  so **mu = 0.55 is still not confirmed at source**. The poster therefore presents mu = 0.55 as
  "a sensitivity bound, not a cited value", which is what section 9's PENDING tag instructs.
  Azhar is not in the printed reference list, because nothing on the poster cites it.

## DO-NOT-SHIP LIST, ENFORCED

Confirmed absent from `Cerrell_TACC_42x56.pdf`:

- "+13.2 percent at n_grid 128" and "+56 percent at 192". Not printed. This session's own
  measurement gives 12.3 and 37.2 percent, which do not match those figures, so they stay dead.
- 0.432718 m3. Not printed at all. 0.452204 m3 appears **once**, explicitly tagged PENDING and
  named as a number whose generating routine is not in the repository.
- Nothing from `data/track1_sweep_v2/manifest.csv`. This is why
  `figures/phase_space_poster_figure.svg` was NOT used as hero despite being regenerated today:
  it overlays L2 drift markers sourced from that file.
- No FORD verdict is asserted anywhere. No FLOAT verdict appears at all.

Also corrected in the new text, flagged not silently changed: `paper/poster_methods.md:13` has
the Yaris mass attribution **backwards**. It says the deck weight is 1078 kg and calls 1100 kg
the MASH standard. Per the resolved July 23 finding, 1100 kg is the LS-DYNA deck header value
and both 1078 kg and the MASH label are NCAC-webpage annotations. The poster sources 1100 kg to
the deck header. `paper/poster_methods.md` is not owned by this lane and was not edited.

## WHAT IS STILL MISSING, NAMED NOT GUESSED

1. **Both logo slots are empty.** No NSF logo, no CNS shield, no TACC mark exists anywhere in
   the repo. I searched at `-maxdepth 3` and found only text files. The header reserves two
   2.5 in slots, `div.logo-slot.left` and `div.logo-slot.right`. Drop the files in and add one
   `<img>` to each. **This is the single largest remaining gap** and the requirement explicitly
   asks for the current CNS shield, not the nautilus version, which I cannot verify without the
   asset.
2. Author list and order remain unconfirmed. The poster prints Cerrell, Iqbal, Hsiao, Kumar and
   names Sarah Etter in the Introduction and Acknowledgments. Ask Kumar.
3. Kumar's departmental affiliation is not printed. The TACC line that is printed is the one
   `README.md:200` supports.
4. The QR area is reserved and empty pending a working Gradio URL.

## LATE BREAK: THE L1 BOUNDARY FIX LANDED MID-BUILD, HERO REGENERATED

At 17:15, five minutes before this handoff was first written, `2026-07-25_ford-F2-l1-boundary.md`
landed and `git status` showed `data/scenario_sweep.csv` and `vehicle_params.py` modified. That
invalidated the Results 1 table and the hero figure on a poster that was already rendered.

Verified live, not taken from the summary. The CSV moved from md5
`40b7c3a8c8976e12878d3fb56db69afb` (4524 bytes) to `4bf0c759611508190ef71822998391d3`
(4506 bytes, mtime 2026-07-25 17:11:09):

| | before | after |
|---|---|---|
| Small passenger FORD / NO-FORD | 12 / 58 | **14 / 56** |
| Large passenger | 19 / 51 | 19 / 51 |
| Large 4WD | 24 / 46 | **26 / 44** |
| all three cleared | 12 | **14** |
| Large 4WD only | 5 | **7** |
| 4WD and large passenger | 7 | **5** |
| no class fords | 46 | **44** |
| class-sensitive | 12 | 12, unchanged |

**The headline survives.** "12 of 70 class-sensitive" is still exactly right, and the (0.30 m,
1.5 m/s) example still reads NO-FORD small passenger and FORD large 4WD, confirmed by direct
row read. Class-sensitive membership moved exactly as `fig1_CAPTION.md` had predicted:
(0.1, 3.0) and (0.2, 1.5) left, (0.2, 3.0) and (0.4, 1.5) entered.

**Regeneration path used.** All three local interpreters were tried by absolute path, not by
glob: `~/miniforge3/envs/can-it-ford/bin/python` and `~/anaconda3/envs/can-it-ford/bin/python`
do not exist, and `/opt/homebrew/bin/python3` has no matplotlib. So the figure was rebuilt in a
Vista scratch directory at `/tmp/fig1work`, never in either repo. Nothing was written into
`/work/11603/jcerrell0629/vista/can-it-ford`, nothing pulled, nothing pushed. Vista's own copy
of the CSV is still the pre-fix one and was deliberately not used.

Script self-verification, quoted verbatim from the run:

```
verified: 70 rows, small_passenger=14, large_passenger=19, large_4wd=26, class_sensitive=12
cells by classes-that-ford: {0: 44, 1: 7, 2: 5, 3: 14}
source md5=4bf0c759611508190ef71822998391d3 bytes=4506 mtime=2026-07-25 17:34:14
```

Checks required before re-embedding, all passed: counts read 14 / 5 / 7 / 44, they sum to 70,
14 + 5 = 19 matches large_passenger, and 19 + 7 = 26 matches large_4wd.

**Tripwire, changed not loosened.** One line, in both the scratch copy and the Mac original at
`analysis/plot_l1_three_class.py:26`:

```
- EXPECTED_FORD = {"small_passenger": 12, "large_passenger": 19, "large_4wd": 24}
+ EXPECTED_FORD = {"small_passenger": 14, "large_passenger": 19, "large_4wd": 26}
```

`EXPECTED_SENSITIVE = 12` was left alone because the live CSV still gives 12. The tripwire did
its job and was not weakened. Note `analysis/` is not this lane's declared territory; the change
was made on your explicit instruction and the pre-edit file is backed up in the session
scratchpad.

**Hero swap.** `figures/fig1_l1_three_class.pdf` mtime was checked immediately before writing
and again just before the copy, both times reading 2026-07-25 06:17 at 35,261 bytes, so no other
lane touched it mid-flight. The superseded PDF is backed up at
`scratchpad/fig1_PREFIX_backup.pdf`. The new one is 103,740 bytes, mtime 17:35, reconverted to
SVG for embedding.

**Coupled artifact updated in the same pass.** `figures/fig1_CAPTION.md` had the stale counts in
four places: the caption prose, the provenance md5 and byte count, the values-plotted table, and
the per-class totals table. All corrected. Its "Known issue in the source data, unresolved"
section is now retitled RESOLVED and records which four cells flipped and which two hatched cells
relocated. The poster's own inline caption also dropped its floating-point caveat sentence,
which the fix made obsolete.

**Deliverable re-rendered and re-verified**: 1 page, 4032 x 3024 pt, 403,657 bytes. Figure legend
and Results table now agree at 14 / 5 / 7 / 44.

## ACCOUNTING FOR THE UNEXPLAINED LINE COUNT

`git diff --stat` reads **120 insertions, 41 deletions across 9 files**, not +13,864. The status
bar figure includes untracked files, which `git diff` does not count. Untracked content totals
28,761 lines. This lane contributed 6,751 of them, and 6,312 of those are two machine-generated
`pdftocairo` vector conversions:

| file | lines |
|---|---|
| `figures/fig1_l1_three_class.svg` | 3,350 |
| `figures/traction_bias.svg` | 2,962 |
| `poster.html` | 372 |
| `figures/pipeline_diagram_poster.svg` | 67 |

That is SVG path data, not authored prose. Nothing was committed by this lane and nothing should
be committed until the rest of the untracked tree is accounted for by whoever owns it.

## FILES WRITTEN BY THIS LANE

- `poster.html`, new
- `Cerrell_TACC_42x56.pdf`, new, the deliverable
- `figures/pipeline_diagram_poster.svg`, new
- `figures/fig1_l1_three_class.svg`, new, vector conversion
- `figures/traction_bias.svg`, new, vector conversion, not currently placed
- `docs/POSTER_TEXT_BLOCKS.md`, appended sections 11, 12 and 13. Sections 1 to 10 untouched.

Not touched: `README.md`, `figures/can_it_ford_pipeline_diagram.svg`, `paper/`, `out/`,
`mpm-engine/`, `simulation/`, `paper_draft.md`, any CSV, any `vehicle_params.py`. Nothing
committed, nothing pushed.
