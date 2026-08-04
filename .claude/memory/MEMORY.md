# Memory index

Reconciled 2026-08-04. The root checkout's `.claude/memory/` had lost 15 files, and its index carried
a note calling them "absent from disk and untracked in git". That was wrong: all 15 are tracked on
`origin/main` and were sitting in the `figure-validation-sources-826ba6` worktree the whole time.
Nothing was lost. Local `main` carries 0 memory files, which is what made them look gone. Both sides
now hold the same set.

- [AR&R ISBN and Table 3 are verified](arr-isbn-and-table3-are-verified.md) — an audit called both unverified and had them deleted; the primary PDF is in citations/ and prints both
- [AR&R primary source access](arr-primary-source-access.md) — arr.ga.gov.au 403s; the mirror search engines suggest is the PEOPLE report, not vehicles; two fetchable reproductions + the authors' own gap list
- [Figure PDFs: raster vs vector](figure-pdfs-raster-vs-vector.md) — svg_to_paper_pdf.py has a JPEG-wrapper path and an rsvg-convert vector path; captions are always native LaTeX, and "two figures on a page" is not "two figures in one image"
- [flood_vehicle.mp4 is a model-scale truck](flood-vehicle-mp4-is-model-scale-truck.md) — the Jul 13 mp4 is the bundled 1.447m/28.7kg truck splat at defaults, not the Yaris and not full scale; reproduces to 0.43% but stays UNVERIFIED (no particle dump); ffmpeg absent on gh-dev nodes
- [Gated runs are warpmpm, not Genesis](gated-runs-are-warpmpm-not-genesis.md) — sim_standing.py imports warpmpm for the 17 runs; fixed on overleaf/main, but the Fig 1 generator on main still says "Genesis MPM"
- [gd=64 runs have heavy pass-through](gd64-runs-have-heavy-particle-passthrough.md) — the runs that complete have 21-31% of water particles inside the vehicle; "it runs" is not "it's correct"
- [Genesis P2G crash is grid_density](genesis-p2g-crash-is-grid-density.md) — crashes at gd>=96, runs at gd=64; coup_softness, CFL, 3*dx padding and t=0 overlap all ruled out by direct test July 23
- [git show corrupts binary blobs: REFUTED](git-show-mangles-binary-blobs.md) — `git show` does NOT corrupt PDFs here; the size gap was two real figure revisions
- [HF Space history still serves personal files](hf-space-history-still-serves-personal-files.md) — ADHD/profile files are 404 at HEAD but HTTP 200 at old revisions on BOTH HF and GitHub; two separate remediations needed, and `hf repo settings --private` is silently ignored on existing repos
- [L0/L1 divergence PDF is not a 7th figure](l0l1-divergence-pdf-not-a-7th-figure.md) — all 8 claims verified against scenario_sweep.csv, but deliberately not added: fig:l0l1's right panel already carries the same three regions and the 14-of-70 total
- [L1/L2 agreement is a grid artifact](l1-l2-agreement-is-a-grid-artifact.md) — each n_grid has its own perfect window and the three are disjoint, so it is convergence scatter; do not claim it in the paper
- [L1/L2 divergence is class-dependent](l1-l2-divergence-is-class-dependent.md) — the paper's class-free divergence zone is contradicted for 2 of 3 AR&R classes at 0.30m/1.5m/s; and computing D x V at the vehicle (58-66% below nominal) removes the third, flipping large_passenger on the depth limit
- [Overleaf tex is canonical](overleaf-tex-is-canonical.md) — the paper builds from conference_101719_1.tex on overleaf/main with FLAT figure paths, not paper/conference_101719.tex; head is 4e2fdbd (2026-07-30 16:29); the FILE CHOICE is settled, the content is not, always check the live head
- [Pane signals are turn-end, not done](pane-signals-are-turn-end-not-done.md) — ~/.pane_signals/*_done fires on every Stop hook, so it proves liveness not completion; verify every pane claim against a real artifact
- [Physical plausibility checklist](physical-plausibility-checklist.md) — 6 cited physics decisions locked in CLAUDE.md + skill Part 3; sedan rho and staging friction still disagree in code
- [solidify_watertight supersedes column fill](solidify-watertight-supersedes-column-fill.md) — fill_ratio is 1.0023 and rho 309.78, NOT 2.17/143; every 2.18x, 7.71 m3 and 143 kg/m3 figure is retired; ratio now passes at every n_grid so raising it is the fix for 4-layer water; the 100-300 density band is now the wrong thing, not the vehicle; patch still UNCOMMITTED
- [v2 geometry warped invalid](v2-geometry-warped-invalid.md) — v2 sweep is fit_to_bbox-warped truck_trimmed.ply (4.6x divergence, never rendered); no v2 figure on the poster until --vehicle yaris real-mesh path replaces it
- [v2 timeseries no velocity cols](v2-timeseries-no-velocity-cols.md) — v1/v2 sweeps lack vx/vy/vz, so failure_modes.py can't classify STUCK/SLIDE/TOPPLE/FLOAT; failure-mode overlay blocked until Vista re-run
- [Vista login-node warpmpm import blocks](vista-login-warpmpm-import-hangs.md) — `from warpmpm.vehicle import load_vehicle` BLOCKS on login1 (600 s wall, only 0.75 s CPU, RC=124) but completes on a compute node in 78.9 s; near-zero CPU proves a blocking call, not contention; do CPU-only geometry on the Mac by AST-extracting the pure numpy functions and validate against 5 known live numbers first
- [W&B key status](wandb-key-401-broken.md) — Mac key RESOLVED July 13 (works, 88 runs, exposure scan clean); ~/.netrc still stale, old-key revocation on wandb.ai still unconfirmed
- [Xia is 2014, not 2013](xia-2014-not-2013-citation-trap.md) — four authors incl. Yejiang Wang, print year 2014; a bolded "2013 NOT 2014" instruction was wrong
- [Zotero MCP lies about being connected](zotero-mcp-connected-but-unreachable.md) — reports "Connected" with Zotero desktop closed; searches return empty instead of erroring, so "not in your library" is wrong; check pgrep + port 23119 first
