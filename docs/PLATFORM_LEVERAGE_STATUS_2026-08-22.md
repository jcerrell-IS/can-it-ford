# Platform leverage status, 2026-08-22

Audit of the HuggingFace and W&B integration work scoped by slot d18-platform: what
actually shipped, what was only planned, and what waits on a decision.

Every claim is tagged by how it was obtained. **[live]** means read from the API, the CLI
or the filesystem during this session. **[relayed]** means taken from another session's
write-up and not re-derived here.

**Nothing was published.** No repository visibility changed, no Space deployed, no Release
cut, no DOI minted, no credential printed or committed.

**Provenance of this file.** An earlier partial run of this same unit wrote a version at
01:22 to 01:41. This is a rewrite after an independent live re-check at 02:19 to 02:26.
**Three of its findings were wrong and are corrected here, not quietly dropped**, in
sections 3 and 7. The corrections all run the same direction: the situation is better than
it recorded, and the recommended fix is much cheaper.

---

## 1. Headline: the brief's premise is out of date in both halves

The brief says the Space is "kept PRIVATE pending two README claims being corrected".
Neither half is the live state.

| | brief says | live **[live]** |
|---|---|---|
| Space `josiecerrell/can-it-ford` | private | **PUBLIC**, `private=false`, stage `RUNNING` |
| the two README claims | still wrong | **corrected**, and there were **three**, not two |

Measured 02:20 with `hf spaces list`, `hf datasets list`, `hf models list` and the Hub API,
authenticated as `josiecerrell` (`hf auth whoami`).

Full account visibility:

| repo | type | visibility | state |
|---|---|---|---|
| `can-it-ford` | space | **public** | RUNNING, cpu-basic, 11 files, gradio |
| `can-it-ford-demo` | space | **public** | redirect stub |
| `can-it-ford-lab` | space | private | docker/jupyterlab |
| `can-it-ford-page` | space | private | static |
| `can-it-ford-speed-surface` | dataset | **public** | 4 CSVs + card, **38 downloads** |
| `can-it-ford-sweep-v1` | dataset | **public** | no data file, **29 downloads** |
| `can-it-ford-results` | dataset | private | 107 files, 2 downloads |
| `can-it-ford-sweep-v1` | model | **public** | superseded box-proxy lineage, tagged `superseded` |

**This is Josie's switch, not mine.** Flipping a public repo to private is a visibility
change on artifacts that already carry download counts, so I did not touch any of them.

**Update to the brief on `can-it-ford-sweep-v1`.** The brief records it as holding only
`.gitattributes` with 22 downloads. Live it now carries a README that states in its own
first line that the repository holds no data and explains why it is being labelled rather
than deleted (downloads would break silently if the name disappeared), and it is at 29
downloads **[live]**. So it has been *labelled* since the brief was written, but it is
**still public** and the delete-or-privatise decision is still open and still Josie's.

## 2. The three README claims: corrected on the live page

All three appear on the live Space only inside a section headed "Corrections to the
previous version of this page", stated as retracted with the correct value beside them
**[live, read from the Space's `README.md` at `resolve/main`]**:

1. **"Genesis MPM"** as the physics engine. The gated runs are warpmpm.
2. **"a corrected density of rho = 115.7, giving the roughly 1390 kg target mass."**
   Canonical is 1100 kg and 310.494 kg/m^3.
3. **"L2 is being rebuilt and has not produced a published verdict."** Stale; seventeen
   gated runs exist with classified outcomes.

**A substring search cannot answer this question and nearly gave the wrong answer.**
Grepping the live README for `115.7`, `1390` and `Genesis` returns a hit for all three,
because the retraction quotes the text it is retracting. The strings are present; the
claims are not asserted. Read the section, do not count the matches.

The retraction is correct against canonical sources, checked live: `vehicle_params.py`
`mass_kg: 1100.0`; `renders/yaris_render_s1/gates.py` `RHO_REF = 310.49`;
`simulation/can_it_ford_L2_mpm.py:27` `VEHICLE_RHO = 115.7`, which is the superseded
box-proxy path.

## 3. The `hf_space/` divergence: real, dormant, and far cheaper to fix than recorded

`origin/main:.github/workflows/sync-to-hub.yml` fires on a push to `main` touching
`hf_space/**` or the workflow itself, plus `workflow_dispatch`, and runs **[live]**:

```
hf upload josiecerrell/can-it-ford ./hf_space . --repo-type space \
  --exclude "__pycache__/*" --exclude "*.pyc"
```

No `--delete`, so extra files on the Hub are not removed; the hazard is **same-path
overwrite** of `app.py`, `README.md` and `requirements.txt`.

Git-side versus live-side, both read this session **[live]**:

| | `origin/main:hf_space/` and `HEAD:hf_space/` | live Space |
|---|---|---|
| files | 3 | 11 |
| `app.py` | 125 lines, **zero `gr.Tab`**, `AR_R` inline | 359 lines, **5 tabs**, imports `arr_verdict` |
| `requirements.txt` | `gradio` | `gradio==6.24.0`, `plotly==6.9.0` |

So a push to `main` touching `hf_space/` replaces the five-tab app with the one-tab
calculator and leaves seven files orphaned.

**It will not fire on the pending merge.**
`git diff --name-only origin/main HEAD -- 'hf_space/**' '.github/workflows/sync-to-hub.yml'`
returns **empty** **[live]**. Landing these commits touches neither trigger path. **The
hazard is dormant, which is worse than imminent**: it can sit undetected and will bite
whoever next legitimately improves the demo.

**Read this branch as `behind/ahead`, and only the behind half is worth quoting.** At 02:22
it measured **0 behind / 419 ahead**; at 02:30, after another session committed under me,
**0 behind / 425 ahead** **[live, both]**. The ahead count moved six in eight minutes and
will be stale by the time you read it. The **0 behind** held, the empty trigger-path diff
held, and `HEAD:hf_space/` was still 3 files at both readings, so every conclusion above
survives the re-read. This is rule B5 in the board's own words, reproduced by accident.

### CORRECTION 1: the Space's files are **not** missing from git

The earlier run recorded that "8 of the Space's 11 files exist nowhere in git". **That is
false, and it was reached from a partial view** (`HEAD` and `origin/main` only).

Searched across **1456 commits over 168 refs** with `git log --all` **[live]**, then
confirmed at the branch tip: **`claude/r9-platform` carries all ten authored files**,
including `arr_verdict.py`, `surface.py`, `speed_surface.py`, `ingest_speed_surface.py` and
all three under `data/`. Its `hf_space/app.py` is the 358-line five-tab version. The only
live file absent from git is `.gitattributes`, which the Hub creates itself.

The commit that added `arr_verdict.py` is `bef6da0` on that branch, and its own subject
records the extraction. Nothing is at risk of loss, and **no backup capture is needed**.

### CORRECTION 2: the branch copy and the live Space barely differ

I downloaded all ten live files and compared them byte for byte against the
`claude/r9-platform` blobs **[live]**:

| files | result |
|---|---|
| `app.py`, `arr_verdict.py`, `ingest_speed_surface.py`, `requirements.txt`, `surface.py`, `data/load_surface_manifest.json` | **byte-identical** |
| `data/canonical_runs.csv`, `data/load_surface.csv` | **content-identical**, CRLF on the Hub against LF in git |
| `README.md` | body **byte-identical**; live carries 7 extra lines of Hub-added frontmatter (`short_description`, 5 `tags`) |
| `speed_surface.py` | branch has **41 lines the Space does not**, unreachable from `app.py` |

**The CSV pair is a line-ending artifact, not a data difference, and it is a trap.** The
byte deltas are 18 and 369 against line counts of 18 and 369, exactly one byte per line;
the Hub copies carry 18 and 369 CR bytes and the git blobs carry zero; stripping CR makes
the sha256 match. Python's `csv.writer` emits CRLF by default and `text=auto` normalises to
LF on commit. **Any future naive hash comparison of Space against git will report these two
files permanently stale.** Compare with `git hash-object --path=`, or strip CR first.

So `claude/r9-platform:hf_space/` **is** the live Space, plus one dead function, minus the
Hub's own card metadata. **Landing that tree is close to a no-op against the live page**,
not the risky reconciliation the earlier version implied. Two things to fix first:

- Carry the live `short_description` and `tags` into the committed `README.md`, or the sync
  strips them from the Space card.
- `speed_surface.py:228` on that branch declares `ial_ARMS`, used at `:247`. It compiles and
  is internally consistent, but the name is almost certainly a truncated `MATERIAL_ARMS`.
  **Newly flagged here [live], not previously recorded.** It is dead on the Space because
  `app.py` never calls `arm_ratio_table`, so it is cosmetic today and a landmine if anyone
  later wires that tab up.

**Not mine to land.** `.github/workflows/` is claimed by `d16-landing` on the board, and
`hf_space/**` is claimed by `d18-platform`. I edited neither.

## 4. Deliverable status against d18's three

### (1) HuggingFace dataset card: SHIPPED

`josiecerrell/can-it-ford-speed-surface`, 4 CSVs, 243-line card **[live]**. The three things
the brief required are on the card itself, each confirmed by reading it:

- **units**: a "Column notes" section defining `v_car_ms`, `v_water_ms`,
  `v_rel_angle_deg_from_broadside` and `force_horiz_mag_N`.
- **scope**: depth fixed at 0.3 m, headed "Status: PROVISIONAL, and deliberately not
  frozen".
- **the caveat**: the vehicle is **prescribed, not free**, followed by "No FORD or NO-FORD
  verdict is derivable from this dataset."

The underlying data is real and on disk: `data/r9_speed_surface.tsv` (629 KB) and
`analysis/r9_speed_surface.py` (36 KB) are **tracked on this branch** **[live]**, so d17's
output exists and nothing on the card is placeholder.

### (2) HuggingFace Space rendering the surface: SHIPPED and RUNNING

Five tabs, read from the live `app.py` **[live]**: `AR&R verdict calculator`,
`Where the verdict flips`, `Load surface (v_car x v_water)`, `Repeat spread`,
`Limitations`. Stage `RUNNING`, `cpu-basic`, last modified 2026-08-21T01:13:06Z.

**The AR&R joint-rule fix from PR #11 is intact on the live page.** It moved out of
`app.py` into `arr_verdict.py`, which carries the `AR_R` table, `l1_verdict` and
`l0_depth_threshold`, with all three classes and all three caps: 0.30/3.0/0.30,
0.40/3.0/0.45, 0.50/3.0/0.60 **[live]**. Checking `app.py` alone shows zero `AR_R` matches
and reads as a regression; it is not one.

### (3) W&B "sweep view" of the repeat ensembles: DONE, but not as a Sweep

**The open question in the brief is resolved: the 17 canonical warpmpm runs and the grid
study ARE logged.** Measured live against the API, not taken from either prior note:

- **Exactly 17 runs** tagged `L2 / gated-17 / warpmpm`, splitting 3 / 11 / 3 across
  `n_grid` 48 / 64 / 96 **[live]**. Names match the canonical set: `g{48,64,96}_m{1100,1609,2337}`,
  `sweepD_g64_d{0p25,0p35,0p45}`, `sweepV_g64_v{0p5,1p0,2p0,2p5,3p0}`.
- **The grid study is the 9 `g*_m*` runs** inside that 17 **[live]**.
- The memory note saying they were not logged is **stale**; it predates the upload.
- **Carry this caveat with any number from them**: all 17 report `_runtime = 0` **[live]**.
  They are Mac backfills, not solver telemetry.
- **Zero W&B Sweeps exist in the project** **[live]**, by GraphQL against `project.sweeps`.

**A Sweep is the wrong primitive here, and that is d18's own correction, not mine**
**[relayed]**: in W&B an agent picks the cells, while d17's matrix is pre-registered, so a
Sweep would dissolve the pre-registration. Grouped runs plus tables is the right shape.

**The deliverable exists as a Report.** Verified present, created 2026-08-22T00:26:02Z by
the earlier partial run of this unit, in the **private** project
`jcerrell29-claremont-mckenna-college/can-it-ford` (`access: PRIVATE`, confirmed live):

> Repeat ensembles as distributions: the v_car x v_water load surface

It leads with the comparison that matters, because the seed ensemble alone is misleadingly
tight **[relayed from the report, statistics not re-derived by me]**:

| spread | what varies | size | is it an error bar? |
|---|---|---|---|
| seed | 5 seeds in one cell | CV 0.066% to 0.338% | yes, and it is tiny |
| split | how one fixed abs(v_rel) divides | S = 0.759 to 1.281 | **no, this is the result** |
| window | f20-60 against f250-400 | -68.9% to +83.9% | no, the load is still changing |

Project state now: **108 runs, 2 reports, 0 sweeps, 4 dataset artifact collections, 2
run_table collections** **[live]**. No runs were created this session.

## 5. Worth-it table

This **updates** the table in `docs/R9_PLATFORM_ROI_2026-08-19.md` section 1, which lives on
the unmerged branch `claude/r9-platform` and is not reachable from `claude/add-ci-checks`.
Verdicts only, with what changed.

| platform | verdict | effort | why, and what changed |
|---|---|---|---|
| **Zenodo DOI** | **WORTH IT, do this first** | ~1 h | the only item producing something a paper can cite. **Re-verified independently [live]**: record `14014709` returns `access_right: restricted`, `files: 0`, DOI `10.5281/zenodo.14014709`. A restricted record still mints a resolvable DOI, so citability does not require publishing. Do **not** use the Zenodo GitHub integration, which archives a public Release. |
| **HF dataset + card** | **WORTH IT, SHIPPED** | done | card carries units, scope and the prescribed-not-free caveat. **Correction to d18's table: not merely built, it is live and PUBLIC.** |
| **HF Space** | **WORTH IT, SHIPPED** | done | RUNNING, 5 tabs, AR&R fix intact. **Also PUBLIC, not private.** See section 3. |
| **W&B grouped runs + tables** | **WORTH IT, shipped** | done | 17 gated runs and the grid study confirmed logged; carry the Mac-backfill caveat. |
| **W&B Reports** | **WORTH IT, done** | ~1 h | the distributions report. Private project, so this is not publishing. |
| **W&B Sweeps** | **not worth it** | ~3 h | would need 100 draws re-logged as sweep runs, inflating 108 to about 208 for no analytical gain, and would dissolve the pre-registration. A report renders the same distributions. |
| **GitHub Actions** | **worth it, NOT MINE** | d16-landing | unchanged; it also owns the `hf_space/` reconciliation in section 3, now known to be cheap. |
| **W&B Artifacts** | **not worth it, yet** | ~2 h | run tables are small and git already versions the sources. 4 dataset collections exist **[live]**. |
| **GitHub Releases** | **NOT WORTH IT, unsafe today** | ~1 h | **re-verified [live]**: `jcerrell-IS/can-it-ford` is `private: false`, 479 MB, **0 releases**. A release asset would be world-readable and permanent. |
| **GitHub Pages** | **not worth it** | ~2 h | **re-verified [live]**: Pages API returns **404**, not enabled. Public by construction and strictly worse than the Space. |
| **HF model hosting** | **not worth it** | n/a | there is no model. The one `model` repo serves the deprecated box-proxy lineage and is tagged `superseded`. |
| **HF Inference** | **not worth it** | n/a | nothing to run inference on. |

## 6. What is live, what changed here, what waits on Josie

**Live and public right now, none of it by my hand:** the Space, the speed-surface dataset,
the `can-it-ford-demo` stub, and the `sweep-v1` dataset and model.

**Changed this session:** this document only. No Hub write, no visibility change, no commit
to any workflow, no new W&B run, no branch touched.

**Waiting on Josie, three decisions:**

1. **Should the public artifacts stay public?** The brief's hard limit and the live state
   disagree. Four repos would need flipping, and two carry download counts, so flipping
   them breaks whatever is fetching them. `can-it-ford-sweep-v1` is the awkward one: it is
   labelled but still public, and delete-versus-privatise is unresolved.
2. **Landing the `hf_space/` reconciliation**, so a future push to `main` stops being able
   to strip four tabs from the live page. `d16-landing` owns the workflow;
   `claude/r9-platform` already holds the correct tree. Two small fixes first, section 3.
3. **Zenodo**, if a citable DOI is wanted. Restricted is sufficient and re-confirmed.

Also still open and not mine: `CITATION.cff` declares ODC-By-1.0 while `LICENSE` is
BSD-3-Clause **[relayed]**. A dataset card and a Zenodo record each need one answer.

## 7. Method notes, including two traps

- **`hf api` does not exist.** The brief names it; `hf` 1.27.0 answers
  `Error: No such command 'api'` **[live]**. Working subcommands are `hf auth whoami`,
  `hf spaces list|info`, `hf datasets list`, `hf models list`, `hf download`. For anything
  else, call `https://huggingface.co/api/...` directly.
- **W&B auth was checked on the `viewer` field, not the status code**, per the brief's
  warning. An unauthenticated GraphQL call returns HTTP 200 with `viewer: null`. Live it
  returns `viewer: {username: jcerrell29, entity: jcerrell29-claremont-mckenna-college}`,
  so the credential is valid. No key value was printed; presence was tested via `.netrc`.
- **The absence claim in section 3 was the earlier run's biggest error, and its shape is
  the general lesson.** "Exists nowhere in git" was concluded from `HEAD` and `origin/main`.
  The files were on an unmerged branch the whole time. A partial view cannot prove absence;
  state which refs were searched. Mine were 168, via `git log --all`.
- **The CRLF trap in section 3 would have produced a false "the live data is newer".** Two
  CSVs looked bigger on the Hub. They are the same bytes with different line endings.
- Local `python3` has no `wandb`. The venv is `~/.venvs/canitford-mpm/bin/python`
  (wandb 0.28.2), which is why `scripts/wb` exists as a wrapper.
- The Zenodo restricted-DOI claim was re-derived from the API here, so it counts as a
  second origin rather than the same source cited twice. The report's internal statistics
  in section 4 were **not** re-derived and are marked relayed.
