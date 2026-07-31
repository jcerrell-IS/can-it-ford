# Every figure and data file, ranked and decided, by poster section

Built 2026-07-26, second pass, full sweep of `figures/` and `data/`. Columns: what it is,
where it came from, and the actual verdict: USE, DON'T, or USE-AS-EVIDENCE (meaning: use it,
but as a labeled failure, not as a result).

---

## Section 2: The pipeline, annotated

| file | source | verdict |
|---|---|---|
| `figures/pipeline_diagram_poster.svg` | `analysis/plot_geometry_pipeline.py`, Jul 25 | **USE.** Current. |
| `figures/can_it_ford_pipeline_diagram.svg` | Jul 10, no confirmed script | DON'T. Superseded by the one above, 15 days older. |
| `figures/pipeline_diagram_canva.svg` | Jul 10 | DON'T. Same reason. |

Three versions of the same diagram existed. Only the July 25 one postdates the real solver
fix; the other two were drawn while the pipeline still ran SPH.

---

## Section 3: Methods, the abstraction ladder

| file | source | verdict |
|---|---|---|
| `figures/fig1_l1_three_class.pdf` / `.svg` | `analysis/plot_l1_three_class.py`, Jul 25 17:35 | **USE.** Tripwire in the script itself checks `EXPECTED_FORD = {small_passenger: 14, large_passenger: 19, large_4wd: 26}` and matches tonight's numbers exactly. This is your most self-verifying figure. |
| `figures/L1_three_class_corrected.png` | Jul 10 07:28, different hash, different content | **DON'T.** Same subject, 15 days stale, predates the current AR&R fix. The filename says "corrected" but it's the earlier correction, not the current one. |
| `figures/three_class_table.md` | withdrawn per `.claude/handoffs/2026-07-26_yaris-render.md` (v3 scenario fix note) | DON'T. The file itself says WITHDRAWN. Don't use, don't caption, don't cite. |

---

## Section 4: Results, the load-bearing figures

| file | source | verdict |
|---|---|---|
| `figures/g1_velocity_sweep.png/pdf` | `analysis/make_poster_figures.py` | **USE.** Already on your poster. |
| `figures/g5_mass_sensitivity.png/pdf` | same | **USE.** Already on your poster. |
| `figures/traction_bias.pdf/svg` | `analysis/plot_traction_bias.py`, full caption already written | **USE, and give it more room.** Ten stated assumptions, a full values table. Your best-documented figure, currently your smallest panel. |
| `figures/g3_verdict_matrix.png/pdf` | `analysis/make_poster_figures.py` | **USE**, but caption should note which script, since `OPEN_ITEMS.md` didn't fully confirm the generator for this specific panel. Say "regenerated from `data/scenario_sweep.csv`" rather than implying a single dedicated script. |
| `figures/g4_bow_wave.png/pdf` | same | **USE.** Supports the "measures the wrong water" point, caption with the precise 19-of-20. |
| `figures/g2_depth_sweep.png/pdf`, `g6_two_measures`, `g7_geometry_gates`, `g8_hero`, `g9_scope` | same | USE at your discretion, all current, all from the same audited generator. |
| `figures/fig2_mass_sensitivity.pdf/png`, `fig4_velocity_regime.pdf/png` | older names, likely an earlier pass predating the g-series | **DON'T**, redundant with g5 and g1. Two names for functionally the same content; the g-series is the one your poster actually cites. |
| `figures/yaris_hero_frame.png`, `yaris_hero_standing.png` | single-frame pulls from the hero renders | USE only if you want a static fallback image; the video itself is stronger. |
| `figures/car_check.png` (Jul 25 19:12) | mesh visual check, same day as the real MPM breakthrough | **USE as evidence**, in Section 5 or as a Methods sanity-check: "the check that confirmed the hull before it went into the sim." |
| `figures/sedan_proxy_visual_check.png` (Jul 23) | checks the earlier sedan-scale box proxy, Track 1's collider approach, not the real mesh | USE-AS-EVIDENCE only, label clearly as checking the box proxy, not the final hull. |
| `figures/hero_shot_test.png` (Jul 22), `validation.png` (Jul 10), `baseline_comparison_v2.png` (Jul 10) | early-timeline diagnostic renders | **DON'T**, unless you want a "here's an early test render, three days/weeks before the real one" panel. On their own they don't carry a caption-worthy claim. |

---

## Section 5: Where I was wrong, as evidence

| file | source | verdict |
|---|---|---|
| `figures/phase_space_poster_figure.png/svg` | `analysis/build_poster_phase_space.py`, but downstream of the inline-recomputed L1 that ignores depth/velocity caps | **USE-AS-EVIDENCE only.** `OPEN_ITEMS.md` item O-8 confirms this is Tier D, excluded from every deliverable. Caption: "excluded, its own generator recomputes the rule incorrectly, kept to show what got caught." |
| `data/mu_sweep_results.csv` | Jul 10, four friction values, displacement 0.328 to 0.399 m, non-monotonic | **USE-AS-EVIDENCE.** This predates the real vehicle mass existing (the 12 kg to 604 to 115.7 chase was still unresolved on Jul 10). It's the friction-invariance finding from memory, real, but from before the physics was trustworthy. Caption exactly that: "an early friction sweep, dated before vehicle mass was corrected, kept because the pattern, drift that doesn't respond to friction, is what a near-massless floating body looks like, which is itself informative about what was wrong at the time." |
| `data/phase_space_results.csv` | Jul 10, 1.2 KB, a handful of rows, inconsistent FORD/NO-FORD at identical inputs | **DON'T**, or USE-AS-EVIDENCE only with heavy caveats. Too small and too early to support any claim. |
| `figures/Cerrell_TACC_42x56.pdf` (Jul 25, 17:13, root and `figures/`) | no generating script found in scope | DON'T use as a poster. Fine to mention it existed and was superseded. |

---

## Section 6: Where I could go from here

| file | source | verdict |
|---|---|---|
| `figures/phase_space_interactive.html` | `analysis/build_phase_space_plotly.py` | **USE**, differently: not as a static poster panel, but as a QR-linked live demo. It's interactive, a printed poster can't show that, a QR code to it can. |
| `analysis/gp_surrogate.py`, `analysis/viability_dashboard_scaffold.py` | already catalogued last round | USE as described before. |
| `data/mu_sweep_results.csv` | same file as above | Also belongs here as a forward pointer: "worth re-running now that vehicle mass is correct, to see if the friction-invariance pattern was physics or a symptom of the mass bug." |

---

## Poster furniture, not data, brief note

`figures/qr_github.svg`, `qr_gradio.svg`: fine as-is, these are navigation aids not claims,
no caption needed beyond a label.

---

## The net result

Of roughly 50 files across `figures/` and `data/`, about **18 are current and citable**, **6
are near-duplicates of a current one under an older name**, and **6 are genuinely useful as
labeled evidence of an earlier, wrong state**, not as results. The rest are one-off diagnostic
images that don't carry a standalone claim. That ratio, roughly a third usable, a third
duplicate, a third context, is itself a reasonable thing to say out loud if anyone asks how
much of a project's output ends up on the final poster.
