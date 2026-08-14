# Provenance, rescued hull sweep from Vista `$WORK/render_s3_hullsweep`

Recovered 2026-08-14. **This is a fourth artifact set, not one of the three Dispatch 8
names.** It was found while rescuing `renders/yaris_render_s3_enhanced/`, whose two
`hull_sweep*.sbatch` files described a run whose results were nowhere in that tree. The
scope extension is deliberate and stated here so it can be reversed: the set was in the
same one-machine-no-ref state the dispatch exists to end, the payload is 112 KB, and it
touches no canonical store and no other dispatch's branch.

Everything below was read live on 2026-08-14, over `scripts/tacc.sh vista`.

## What this is

The first run in this project where **vehicle geometry actually varies**: three
watertight hulls, two arms, five completed runs. Recovered files are the summaries,
per-frame metrics, and logs.

| file class | count | note |
|---|---|---|
| `*/summary.json` | 5 | run-level result |
| `*/metrics.csv` | 5 | per-frame timeseries, ~34 KB each |
| `*.log`, `sweep_driver.log` | 6 | driver and per-run logs |

**Not recovered, and still on one filesystem:** five `rollout.npz` particle dumps
totalling **1.39 GB** (156 to 477 MB each). They are too large for this repo. They exist
only at `/work/11603/jcerrell0629/vista/render_s3_hullsweep/`, and **the Vista allocation
expires 2026-09-30**. Whether to archive them elsewhere is a decision for Josie, not one
this rescue should take.

Three files in the remote directory were **byte-identical** by sha256 to files already
committed one directory over in `rescued/yaris_render_s3_enhanced/`, so they are not
duplicated here: `sim_enhanced.py` (`a4b46c4f…`), `run_enhanced.py` (`99cb1b4b…`) and
`hull_sweep_hullsweepdir.sbatch` (`66237e94…`).

Transfer integrity: tarred on Vista, base64 over the ControlMaster socket, sha256 of the
archive verified equal on both sides (`e8b43d7ccc9a351d7d0403f1794c68404e47e7cfe6cae1ecbaa2c4c75210be4b`).

## The results as recovered, verbatim from the driver's own summary

Read from `sweep_driver.log`, which ends `2026-08-07T23:43:54-05:00`:

```
== ARM A  matched dx, compare across these ==
label                  hull_m3   d_ref_% fill_ratio        dx   disp_m  passthru    z_rise     roll
hull_yaris_dxm        3.542739    -0.000     0.9941  0.098143  0.27086   0.09680   0.00000    0.001
hull_rogue_dxm        4.950341   +39.732     0.9954  0.098514  0.69199   0.12303  -0.00486   -0.107
hull_silverado_dxm    7.962083  +124.744     0.9994  0.098255  0.33538   0.10581   0.00000   -0.002

== ARM B  fixed n_grid 96, confound control ONLY ==
hull_rogue_g96        4.950341   +39.732     0.9999  0.108776  0.93640   0.12093  -0.02449   -0.272
hull_silverado_g96    7.962083  +124.744     1.0049  0.136124  0.23503   0.09293  -0.00000    0.002
```

The three hull volumes reproduce the qualified-mesh figures independently: 3.542739,
4.950341, 7.962083 m3.

## Five things to hold before anyone reads physics out of this

1. **This is a geometry sweep at FIXED MASS, not a three-class experiment.** Every run
   is `mass_kg = 1100.0`, including the Silverado. Realized densities are therefore
   Yaris **312.34**, Rogue **223.23**, Silverado **138.24** kg/m3, not the class
   densities (310.494 / 317.4 / 285.1) that follow from class masses. Holding mass fixed
   is a defensible way to isolate geometry, and it is a different experiment from the
   three-class one. A Silverado at 138 kg/m3 is under half its effective density.
2. **ARM B is missing no cell.** The Yaris at matched dx *is* `n_grid` 96
   (dx 0.098143), so it defines the matched-dx target and an ARM B Yaris row would
   duplicate `hull_yaris_dxm`. Five runs is the complete 2-arm design, not six-minus-one.
3. **Three of the five fail gate P-2** (`passthrough < 0.10` at `gates.py:148`):
   `hull_rogue_dxm` 0.12303, `hull_rogue_g96` 0.12093, `hull_silverado_dxm` 0.10581.
   `hull_rogue_g96` also fails P-3 (`abs(z_rise) <= 0.01`) at -0.02449. Only
   `hull_yaris_dxm` and `hull_silverado_g96` pass both. Containment-failed runs are not
   results.
4. **`determinism_identical` is True on all five and that is not evidence.** The same
   flag reports True on six runs that differ at identical config, node and driver.
5. **ARM A is the confound control that matters** and it works: dx is 0.098143 /
   0.098514 / 0.098255, within 0.4% across hulls, against the fixed-`n_grid` arm where dx
   spans 0.098 to 0.136. This is the arm to compare across; the fixed-`n_grid` arm is
   labelled by its own driver as confound control only.

## Provenance gap, stated rather than guessed

**No batch job produced these.** The only `s3hull` record in `sacct` is job **896281**,
partition `gh`, `State = CANCELLED`, `Start = None`, `Elapsed = 00:00:00`: it never ran.
The results carry mtimes 23:42-23:43 on 2026-08-07, which falls inside job **896302**,
`idv52164`, partition `gh-dev`, an **interactive** session that started 23:40:33 and ended
in **TIMEOUT** after 02:00:05.

So the most defensible statement is: produced inside an idev session, by a path that left
no job script binding, and the batch submission of the same work was cancelled. This is a
concrete instance of the recorded pattern that Vista's node-hours go to interactive
sessions rather than to batch science. It does not invalidate the numbers; it means their
execution provenance is an inference from timestamps, not a record.

Also absent, unlike the six enhanced-ladder summaries: these carry **no**
`mesh_sha256`, `solver_git_sha`, `canitford_git_commit` or `_provenance_backfill` block.
`analysis/run_provenance.py` has never run against them, because they were never on the
Mac. The `hull_source` paths they do carry are Vista paths
(`$WORK/hulls/rogue_g96_pd8_coarse_watertight.ply` and the Silverado sibling), not
sha256-anchored, and per standing project guidance a hull must be cited by sha256 and not
by path.

## Handoff

This bears directly on the three-class work, which is another thread's scope. Nothing
here was analyzed further, merged, or promoted. It is preserved, labelled, and left where
that thread can pick it up.
