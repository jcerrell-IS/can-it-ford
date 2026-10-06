# figures/

Generated figures, grouped by what they are for. The figures used in the paper, and the scripts
that draw them, are listed in the main [`README.md`](../README.md#paper-figures).

| Group | Files | Made by |
|---|---|---|
| Paper Fig. 3, L1 for AR&R's three vehicle classes | `fig1_l1_three_class.*` | `analysis/plot_l1_three_class.py` |
| L1 phase space under the full AR&R rule | `phase_space_JOINTRULE.*`, `phase_space_interactive_JOINTRULE.html`, `phase_space_poster_figure_JOINTRULE.*`, `can_it_ford_phase_space_v2_JOINTRULE.png` | `analysis/plot_phase_space_live_JOINTRULE.py`, `analysis/make_phase_space_JOINTRULE.py`, `analysis/make_phase_space_v2.py` |
| Earlier figures built from the early coupled-run records | `fig2_mass_sensitivity.*`, `fig3_geometry_pipeline.pdf`, `fig4_velocity_regime.*` | `analysis/fig2_mass_sensitivity.py`, `analysis/plot_geometry_pipeline.py`, `analysis/fig4_velocity_regime.py` |
| July 2026 poster figures from the 17 early coupled runs | `g1_*` to `g9_*` | `analysis/make_poster_figures.py` |
| Renders of the early coupled runs | `render_v1/`, `hero_enhanced.png`, `hero_g64_m1100.mp4`, `yaris_*`, `readme_hero_g64_m1100.png` | `analysis/render_v1/`, `analysis/enhance_hero.py` |
| README image of the steady-current campaign | `readme_hero_stage1e_u100.png` | no generating script in this repository; LS6 job 3484188 |
| Mesh and proxy checks | `car_check.png`, `sedan_proxy_visual_check.png`, `hero_shot_test.png` | `analysis/render_v1/g1_car_check.py`, `scripts/render_hero_shot.py` |
| Traction-bias figure | `traction_bias.*` | `analysis/plot_traction_bias.py` |
| Poster assets | `Cerrell_TACC_42x56.pdf`, `poster.html`, `pipeline_diagram_poster.svg`, `qr_*` | poster layout |

The 17 early coupled runs measured their own start-up surge rather than a steady current, so
figures drawn from them show displacements, not verdicts (see [`FINDINGS.md`](../FINDINGS.md)).
Figures that applied the retracted product-only L1 rule are in
[`archive/product_only_rule_2026-07/`](../archive/product_only_rule_2026-07/).
