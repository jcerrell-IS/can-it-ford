# Mission: pane F5, ford:0.5, 2026-07-24 evening

You are pane F5. Read this file in full, then execute it. Do not summarize it before acting.

## Hard constraints

1. READ-ONLY on all data. Do not modify, regenerate, or re-run any dataset, CSV, or simulation.
2. DO NOT run git commit. DO NOT run git push. Fourteen contexts share the single working tree at /Users/josie/can-it-ford, including two live Claude Code sessions (Vista, Vista (fork)) writing right now. Local main is 3 commits ahead of origin/main (af1db6d, 85e2252, 4d2242b) under an explicit push hold.
3. Do not import warpmpm, do not run a simulation, do not request idev or GPU. gh-dev job 864505 is occupied and Vista's warpmpm/vehicle.py is mid-edit.
4. Verify live. Never restate a claim from a doc, a memory, or a summary as current fact. The whole point of this table is that every row traces to something real. If you cannot verify a row, mark it unverified and name the blocker. Do not guess.
5. No em-dashes. No inline comments or docstrings.
6. YOU ARE THE SOLE WRITER of docs/POSTER_ASSET_TABLE.md. Pane C5 is doing discovery in parallel and will write its findings to .claude/handoffs/2026-07-24_canitford-C5.md. Poll for that file, and when it exists fold its rows into your table. C5 will not touch your file.

## Your job

Build docs/POSTER_ASSET_TABLE.md, one row per figure or claim that could go on the July 27 poster.

Columns, exactly these:
- asset name
- what it shows
- the exact file that produces it
- the exact data file it reads
- exists on disk now (yes/no, with the path you checked)
- verified or unverified
- the one blocker if unverified

## Seed rows, real and already measured, put these in first

1. L0/L1 phase space, all three AR&R classes, 70 cells, 12 class-sensitive. Source data/scenario_sweep.csv. Primary-source verified against Shand et al. 2011 Table 3.

2. Grid-dependent buoyancy and traction: submerged volume falls 40 percent and traction rises 2.3x between n_grid 64 and 128 with no physical parameter changed. Measured by the Vista (fork) session tonight. Awaiting one true-hull-volume number, so this is unverified pending that single input. Name that as its blocker.

3. Geometry pipeline finding: load_vehicle resamples any mesh to 60,000 surface points at vehicle.py:162; column fill over-fills by +117 percent versus the 3.5427 m3 hull; and the n_grid=128 hollowing dead end was a 60k SAMPLING limit, not a resolution limit (volume rose 13.2 percent at 128 and 56 percent at 192 when sampled at 400k).

Note on seed 3, this is important context: the project has carried "the v3 sweep at n_grid=128 is INVALID because a surface-only ply solidifies hollow at fine grid resolution" as settled fact in several places, including the provenance-audit skill's Known-Error Register and docs/v3_invalidation_status.md. Seed 3 materially revises that explanation: the mechanism was sampling density, not grid resolution. Do not silently overwrite the old claim anywhere. Record the revision in your table's row and flag, in your handoff, every file you find still carrying the older explanation so a human can decide. Do not edit those files.

## Then find everything else

Search the repo for every figure, table, and headline number that could plausibly appear on a poster. Candidates to check, at minimum: figures/, paper/, analysis/, data/, poster_text_draft.md, paper_draft.md Section 4, README.md's headline numbers. For each, trace producer script and input data file live.

Mark any asset that depends on a rendered MPM video as BLOCKED. Do not let a BLOCKED row gate the rest of the table; the table ships without it.

Known-relevant live facts, confirmed tonight, use rather than re-derive:
- README.md:69 and paper_draft.md:89 carry 39.1 percent agreement, 9 of 23, 14 divergences. This is the LIVE figure. The older 16 divergence / 30.4 percent figure is superseded and every surviving mention is already correctly labeled.
- paper_draft.md Section 4 exists, lines 79 to 145, subsections 4.1 through 4.5.
- Commit af95d17 records that can_it_ford_L2.py produced Section 4.1/4.2's figures UNDER A STALE VEHICLE MASS and says they need regeneration rather than silent correction. Any poster asset resting on 4.1 or 4.2 inherits that caveat. Mark it clearly.
- scripts/ford_sweep_driver.py line 45 sets YARIS_PLY to yaris_coarse_v1l_watertight.ply, confirmed on origin/main and via the GitHub API.
- The driver calls wandb.init(mode="offline"), so no run appears in W&B until synced.

## Output

docs/POSTER_ASSET_TABLE.md, plus .claude/handoffs/2026-07-24_ford-F5.md summarizing what you found, what is BLOCKED, and the stale-explanation files you flagged.

Then print the finished table in your final chat message so it can be read without opening the file.

When finished, run: tmux wait-for -S ford-F5-done
