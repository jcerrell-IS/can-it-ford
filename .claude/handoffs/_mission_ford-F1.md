# Mission: pane F1, ford:0.1, 2026-07-25. Poster Figure 3, geometry pipeline

## Hard constraints
1. Mac-local. Read-only. NO commits, NO pushes. You are not the committer.
2. Do not import warpmpm, do not run a simulation, do not request idev or GPU. The numbers below are already measured; you are plotting them, not regenerating them.
3. Verify live. No em-dashes. No inline comments or docstrings.
4. Do not edit vehicle_params.py or anything under simulation/. Other sessions own them.

## Task

Load flood-mpm-debugging-reference if installed. If it is not installed, say so plainly and continue.

Build the geometry-pipeline figure. Data is measured and recorded in docs/VERIFIED_FACTS_LEDGER_july24.md Section A9, plus these 400k-sample results:

    n_grid   60k         400k        change
    64       7.697913    7.832869    +1.75%
    96       7.096399    7.387112    +4.10%
    128      6.355574    7.194586    +13.20%
    192      4.439533    6.926466    +56.02%
    256      n/a         6.591542

True hull volume 3.542739 m3, verified by trimesh, is_watertight True, 655,308 faces.

Write analysis/plot_geometry_pipeline.py producing one vector PDF: solid_volume vs n_grid, two series (60k and 400k samples), with a horizontal reference line at 3.542739.

The point the figure must make, and it must be visible without reading the caption:
the 60k curve collapsing was a SAMPLING limit, not a resolution limit, and neither curve converges to the true hull volume because solidify_columns deliberately merges wheel wells and window openings into the solid (docstring, vehicle.py:65-71).

Read that docstring live to confirm it says what this claims before you assert it in the caption. If it does not, stop and report.

Poster constraints, hard: 56 x 42 inch board, text must read at 300 dpi when placed at roughly one third width. Vector PDF, axis labels with units, no dark background behind any text. Write to figures/. Do not commit.

Then write figures/fig3_CAPTION.md stating both facts: the sampling artifact, and that the residual over-fill is by design and will never reach 3.5427.

## Context you should know

This finding materially revises something the project has carried as settled. Several files still say the v3 sweep at n_grid=128 is INVALID because a surface-only ply solidifies hollow at fine grid resolution, including docs/v3_invalidation_status.md and the provenance-audit skill's Known-Error Register. Your data says the mechanism was sampling density, not grid resolution. Do not edit those files. Note in your handoff which ones you found still carrying the older explanation so a human can decide.

## Output
figures/ PDF, figures/fig3_CAPTION.md, and .claude/handoffs/2026-07-25_ford-F1.md.
When finished: tmux wait-for -S ford-F1-done
