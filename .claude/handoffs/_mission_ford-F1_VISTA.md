# F1 ADDENDUM, 2026-07-25. Render on Vista, not locally.

## Do not install anything, on either machine

There is no matplotlib on this Mac and none will be installed. Python here is 3.14.6, too new for reliable matplotlib wheels; pip would try to build from source. Abandon any local venv or pip plan entirely.

## Verified Vista stack, gate already passed by the orchestrator

    /work/11603/jcerrell0629/vista/.venv/bin/python
    Python 3.12.13, matplotlib 3.11.0, numpy 2.5.1, pdf backend OK

PANDAS IS NOT INSTALLED on Vista. Use numpy and literal data. Do not import pandas, it will fail.

## Your data is literal, so you have less transfer risk than F0

Your series are given numbers, not a CSV read. Hardcode them in the script as literals rather than reading any file, which removes the stale-data risk entirely:

    n_grid   60k         400k
    64       7.697913    7.832869
    96       7.096399    7.387112
    128      6.355574    7.194586
    192      4.439533    6.926466
    256      n/a         6.591542

Horizontal reference line at the true hull volume 3.542739 m3.

Still verify live, before plotting, that docs/VERIFIED_FACTS_LEDGER_july24.md Section A9 actually contains the 60k column values above. If the ledger disagrees with any of them, STOP and report rather than plotting. Quote the ledger lines you checked in your handoff.

Also verify live that the solidify_columns docstring at vehicle.py lines 65 to 71 really says wheel wells and window openings are deliberately merged into the solid. That claim goes in the caption, so it must be read, not assumed. If the file is not on the Mac, read it on Vista at /work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py, READ ONLY. Another session is actively editing that file, so do not write to it, do not git anything in that directory, and note the line numbers you actually saw.

## Procedure

1. Write analysis/plot_geometry_pipeline.py LOCALLY. numpy and matplotlib pdf backend only, no pandas.
2. scp the script to Vista:
   scp analysis/plot_geometry_pipeline.py jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford/analysis/
3. Run on the Vista LOGIN NODE only, CPU only, no idev, no GPU:
   ssh jcerrell0629@vista.tacc.utexas.edu '/work/11603/jcerrell0629/vista/.venv/bin/python /work/11603/jcerrell0629/vista/can-it-ford/analysis/plot_geometry_pipeline.py --out /tmp/fig3_geometry_pipeline.pdf'
4. scp the PDF back into figures/ on the Mac. Confirm non-zero size and a real %PDF header.

## Unchanged constraints

Read-only. NO commits, NO pushes, on either machine. You are not the committer. Do not import warpmpm. Do not request idev or GPU. No em-dashes. No inline comments or docstrings. Vector PDF, axis labels with units, no dark background behind text, legible at 300 dpi at roughly one third width of a 56 x 42 inch board.

The figure must make its point without the caption: the 60k curve collapsing was a SAMPLING limit, not a resolution limit, and neither curve converges to the true hull volume because the over-fill is by design.

Write figures/fig3_CAPTION.md stating both facts: the sampling artifact, and that the residual over-fill is deliberate and will never reach 3.5427.

Note in your handoff which files you found still carrying the older explanation that the n_grid=128 hollowing was a resolution limit, for example docs/v3_invalidation_status.md and the provenance-audit skill's Known-Error Register. Do not edit them.

Write .claude/handoffs/2026-07-25_ford-F1.md. When finished: tmux wait-for -S ford-F1-done
