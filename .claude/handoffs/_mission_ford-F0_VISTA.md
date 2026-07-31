# F0 ADDENDUM, 2026-07-25. Render on Vista, not locally.

## Do not install anything, on either machine

There is no matplotlib on this Mac and none will be installed. Python here is 3.14.6, too new for reliable matplotlib wheels; pip would try to build from source. Abandon any local venv or pip plan entirely.

## Verified Vista stack, gate already passed by the orchestrator

    /work/11603/jcerrell0629/vista/.venv/bin/python
    Python 3.12.13, matplotlib 3.11.0, numpy 2.5.1, pdf backend OK

PANDAS IS NOT INSTALLED on Vista. Use the csv module plus numpy. Do not import pandas, it will fail.

## The trap you must avoid, read this twice

Vista's checkout is BEHIND the Mac by 4 or more commits, and the new schema is in UNPUSHED local commits. Vista's copy of data/scenario_sweep.csv currently has only five columns:

    depth_m,velocity_ms,L0_verdict,L1_haz,L1_verdict

It does NOT have small_passenger, large_passenger, large_4wd, or L1_class_sensitive. If you run your script against Vista's own checkout you will plot the wrong data, produce a plausible-looking figure, and nothing will error.

So: you must copy the Mac's current CSV over and verify it, every time.

## Procedure

1. Write analysis/plot_l1_three_class.py LOCALLY on the Mac, per your original mission. Use csv and numpy only, matplotlib with the pdf backend, no pandas, no seaborn.

2. Verify the four counts LOCALLY against the Mac's data/scenario_sweep.csv before anything else: small_passenger FORD = 12, large_passenger = 19, large_4wd = 24, L1_class_sensitive true in 12 of 70 rows. If any disagree, STOP and report. Record the file's size, mtime and md5 in your handoff.

3. scp BOTH the script and the CSV to Vista, putting the CSV somewhere that does not overwrite Vista's tracked copy. Recommended, do not clobber the repo file:

    scp analysis/plot_l1_three_class.py jcerrell0629@vista.tacc.utexas.edu:/work/11603/jcerrell0629/vista/can-it-ford/analysis/
    scp data/scenario_sweep.csv jcerrell0629@vista.tacc.utexas.edu:/tmp/scenario_sweep_mac.csv

4. Verify the transfer by comparing md5 on both ends. md5 -q on the Mac, md5sum on Vista. If they differ, stop.

5. Run on the Vista LOGIN NODE only. CPU only. No idev, no GPU, no srun. Absolute interpreter, and point the script at the copied CSV, not the repo copy:

    ssh jcerrell0629@vista.tacc.utexas.edu '/work/11603/jcerrell0629/vista/.venv/bin/python /work/11603/jcerrell0629/vista/can-it-ford/analysis/plot_l1_three_class.py --csv /tmp/scenario_sweep_mac.csv --out /tmp/fig1_l1_three_class.pdf'

6. scp the PDF back to figures/ on the Mac. Confirm it arrived, is non-zero, and is a real PDF (file command or the %PDF header).

## Unchanged constraints

Read-only on data. NO commits, NO pushes, on either machine. You are not the committer. Do not import warpmpm. Do not request idev or GPU. No em-dashes. No inline comments or docstrings. Vector PDF, axis labels with units, no dark background behind text, legible at 300 dpi placed at roughly one third width of a 56 x 42 inch board.

Still required: shade the 12 class-sensitive cells distinctly, mark AR&R caps at depth 0.30 / 0.40 / 0.50 and DV 0.30 / 0.45 / 0.60, and write figures/fig1_CAPTION.md citing Shand, Cox, Blacka and Smith 2011, AR&R Project 10 Stage 2, P10/S2/020, Table 3, page 14.

Another session is working on Vista right now in /work/11603/jcerrell0629/vista/mpm-engine. Do not touch that directory. Do not git pull, git checkout, or otherwise change Vista's repo state.

Write .claude/handoffs/2026-07-25_ford-F0.md. When finished: tmux wait-for -S ford-F0-done
