# R8 d8-naming: `determinism_identical` renamed, and three findings larger than the rename

Written 2026-08-18 by slot `d8-naming`, branch `claude/r8-naming`, worktree
`.claude/worktrees/r8-naming`. Every number below was measured live this session in the
main checkout at `/Users/josie/can-it-ford`, not carried from a summary. Each claim carries
a provenance tag: **read directly**, **recalled**, or **inferred**.

Engine tag for every solver claim in this document: **warpmpm**. The driver is
`renders/yaris_render_s1/sim_standing.py`.
No Genesis path is involved anywhere in this work.
CLAUDE.md August 4 audit item 1 is the authority and was read live.

---

## 0. The one-paragraph version

`determinism_identical` compares two loads of the same hull on a particle count and a grid
limit. It is a hull-load reproducibility check. It is not, and cannot be, a determinism check.
It reads `true` on all 17 published runs. The name has been changed to `hull_load_identical`
at every site this branch can reach, backward-compatible on read and forward-only on write, and
no artifact has been regenerated. Three things found on the way are more serious than the name:
**(a)** the script that computes every published verdict column is committed nowhere on any
branch; **(b)** the false claim reaches a **committed PDF on `origin/main` in a public
repository**, under the heading `ESTABLISHED`; and **(c)** the four circulating site counts were
never four scopes of one quantity, they were **three different patterns**, and two of them
reproduce exactly once you say which pattern you meant.

---

## 1. The defect, stated precisely

**Read directly**, `renders/yaris_render_s1/sim_standing.py:389` before this change:

```python
det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
```

`v1` and `v2` are two loads of the same watertight hull. `lim1` and `lim2` are the derived grid
limits. The flag therefore compares a **particle count** and a **grid limit**, and nothing else.
A different random surface sample of the same hull preserves both while placing every particle
differently, so the flag returns `true` by construction for runs whose trajectories differ.

Two facts that look contradictory are both true, and only the **name** is wrong:

| statement | status |
|---|---|
| `determinism_identical` is `True` on 17 of 17 canonical runs | **read directly**: `data/all_runs_inventory.csv`, 17 rows, 42 columns, all `True` |
| `renders/yaris_render_s1/gates_results_all_runs.json` holds 20 records, 17 `True` plus 3 `"ABSENT"` | **read directly**, my own `json.load` and `Counter` |
| the runs are nonetheless not reproducible | **single source, not reproduced by me**, see section 8 |

The ledger instruction was to rename rather than delete, because hull loading genuinely **is**
bit-identical and that is what localises the non-determinism to the solve. That instruction is
followed here.

---

## 2. The enumeration, with its scope stated

**Scope for every count in this section:** tree `/Users/josie/can-it-ford`, `*.py` only,
excluding `.claude/worktrees/`, `third_party/`, `__pycache__/` and `.git/`. Enumerated by a
Python `re` walk that printed every path and line, not by a shell `grep`, per CLAUDE.md item 13's
tooling warning. Counts are the **pre-change** state of the main checkout. `[T]` = tracked by
git, `[u]` = untracked.

### Pattern A, the field name `determinism_identical`: **32 sites in 16 files**

| file | sites | git |
|---|---|---|
| `renders/yaris_render_s1/sim_standing.py` | 1 | T |
| `renders/yaris_render_s1/_incoming/sim_standing.py` | 1 | u |
| `renders/yaris_render_s1/gates_all_runs.py` | 1 | u |
| `renders/yaris_render_s3_enhanced/sim_enhanced.py` | 1 | u |
| `render_s2/multigeom_2026-08-08/sim_standing.py` | 1 | u |
| `analysis/render_v1/as_ran_local_copies/sim_standing.py` | 1 | T |
| `analysis/check_run_validity_2026-08-10.py` | 2 | T |
| `analysis/build_runs_inventory.py` | 2 | T |
| `analysis/classify_three_class_matched.py` | 1 | T |
| `analysis/make_poster_figures.py` | 3 | T |
| `analysis/make_poster_figures_BIG.py` | 3 | T |
| `analysis/make_poster_figures_BIG_GRIDAWARE.py` | 3 | T |
| `analysis/make_poster_figures_GRIDAWARE.py` | 3 | T |
| `deliverables/for_kumar/03_scripts/make_poster_figures_accessible.py` | 3 | u |
| `deliverables/for_kumar 2/03_scripts/make_poster_figures_accessible.py` | 3 | u |
| `deliverables/figures_src/make_poster_figures_accessible.py` | 3 | u |

Split by git status: **19 sites in 9 tracked files**, **13 sites in 7 untracked files**.
Split by role: **5 writer files** (they emit the key into a `summary.json` or a
`gates_results*.json`), **11 reader files**.

### Pattern B, the caption prose `all runs deterministic`: **23 sites in 9 files**

Three sites in each of the seven `make_poster_figures*` scripts (four tracked, three untracked
`_accessible` copies), plus one each in `deliverables/poster/build_poster.py` and its
`_pre_style3_2026-07-26/` copy.

**Two of the three sites per generator contain no field name at all.** They read
`"... one hull at 1100 kg, all runs deterministic. "` and
`"Grid 64, realized depth %.4f m, 1.5 m/s surge, all runs deterministic.\n"`. Any search for
`determinism_identical` misses them. My own scope-confirmation enumeration missed them, and so
did every count listed in section 3.

### Pattern C, the prose `determinism record` / `bit-reproducible`: **8 sites in 5 files**

Six are defects, in three files, all untracked and all outside this branch's write scope:

- `deliverables/poster/build_poster.py:81-82` and its `_pre_style3_2026-07-26/` copy:
  `SCOPE_YES = ("ESTABLISHED   20 coupled runs. All 17 that carry a determinism record are "
  "bit-reproducible; ...")`
- `deliverables/slides/build_slides.py:200` and `:209`:
  `"20 runs. The 17 carrying a determinism record are bit-reproducible."` and
  `"20 coupled runs; 17 bit-reproducible, 3 record none"` under an `ESTABLISHED` heading.

Two are **correct usages and are not defects**, both tracked, both left alone
(**read directly**, full context checked before classifying):
`analysis/three_class_matched_grid.py:40` and `analysis/preflight_hull_guard.py:82` both state
that the **mesh pipeline** is not bit-reproducible, which is true and is not this claim.

### Union

**56 sites in 21 files.** 29 sites in 11 tracked files, 27 sites in 10 untracked files.

---

## 3. Reconciling the four circulating figures

This project's standing rule is that a bare total is the defect, not any particular value. The
four figures were **not** four scopes of one quantity. Three different patterns were being
counted, and nobody said which. Two of the four reproduce exactly once the pattern is named.

| figure in circulation | what it actually counted | reproduces? |
|---|---|---|
| **19 sites, 9 files** (mine, scope confirmation) | pattern A, tracked-only scope | **exact**, and it was correctly scope-labelled at the time |
| **23 sites, 9 files** (adversarial pass) | **pattern B**, full-repo scope | **exact, both numbers.** Not a variant of pattern A at all |
| **5 writers, 7 generators** (Round 7 ledger) | pattern A. 5 writers at **full-repo** scope; 7 generators at **tracked-only** scope | **exact on both halves**, but the two halves use different scopes inside one sentence |
| **4 writers, 2 generators** (coordinator, earlier) | pattern A. *inferred*: 4 = the copies literally named `sim_standing.py`, which misses the differently-named `sim_enhanced.py`; 2 = generator *families* (`make_poster_figures*` and `make_poster_figures_accessible*`) rather than files | **inferred, not confirmed.** I can construct this reading but cannot verify the intent |

The one that matters: **the adversarial 23-in-9 was right and was measuring the publication-facing
prose, which is the more serious quantity.** My scope-confirmation guess that 23 came from
"32 minus the three `deliverables/` copies" was wrong. It arrived at the same number by a
coincidence of arithmetic, which is exactly how a bare total misleads.

I am not adjudicating by picking the largest. Each figure is correct for the pattern and scope it
was measuring. **State the pattern and the scope, or state no number.**

---

## 4. What this branch changed

Eight tracked files, all inside the worktree. Backward-compatible on read, forward-only on write,
following the `gates_all_runs.py:105` `s.get(..., "ABSENT")` pattern named in the dispatch.

| file | change |
|---|---|
| `renders/yaris_render_s1/sim_standing.py` | `det_ok` to `hull_load_ok`; summary key to `hull_load_identical`; explanatory comment block |
| `analysis/build_runs_inventory.py` | CSV column renamed (forward-only); explicit both-key fallback added after the generic comprehension; console header `det` to `hull_ld` |
| `analysis/check_run_validity_2026-08-10.py` | both-key read; warning text corrected; comment stating what `True` does **not** mean |
| `analysis/classify_three_class_matched.py` | `determinism_identical_FLAG_DO_NOT_TRUST` to `hull_load_identical`, both-key read. That suffix was this script's own local workaround for the misleading name and is no longer needed |
| `analysis/make_poster_figures.py` + `_BIG`, `_BIG_GRIDAWARE`, `_GRIDAWARE` | **five** sites each: three captions, one both-key set comprehension, one gate-table row |

**Invariant enforced mechanically at patch time**, not by eye: no code line may contain
`determinism_identical` outside a `.get()` fallback, and no bare subscript
`["determinism_identical"]` may survive. A bare subscript would raise `KeyError` the moment an
artifact carries only the new key. Every file re-parsed with `ast.parse` after writing.

### The stdout prefix is deliberately unchanged

`print("DETERMINISM ...")` keeps its `DETERMINISM ` prefix. Three scripts outside this scope
capture solver logs with an anchored `/usr/bin/grep -E '^(PREFLIGHT|INSTRUMENT|SUBSTEP_TERMS|DETERMINISM|...)'`:
`scripts/run_three_class_matched.sh:167`, `scripts/run_three_class_full33.sh:79`,
`scripts/run_three_class_massswap.sh:124` (**read directly**). Renaming the prefix would silently
drop those lines from every captured log with no error. The line text now reads
`DETERMINISM hull_load_identical=%s (hull load only, NOT trajectory)`, so the anchor survives and
the meaning is correct. **Follow-up for whoever owns `scripts/`:** the anchor token is still the
misleading word.

### The new captions

The replacement captions assert only what the **code alone** establishes, which is airtight and
is sufficient to remove the false claim. They deliberately do **not** assert the repeats result,
which I could not reproduce (section 8):

> `1100 kg. The summary flag hull_load_identical is True on all 17 runs; that compares two loads
> of the same hull on particle count and grid limit only and is NOT evidence that the runs are
> reproducible.`

> `... one hull at 1100 kg. Hull loading is bit-identical across these runs; their trajectories
> are not known to be.`

The gate-table row was relabelled and **downgraded from `PASS` to `NOTED`**. The value is a true
statement about hull loading, so the check does pass what it measures, but a green `PASS` beside
the old name read as a reproducibility guarantee the flag cannot provide.

### Verified by running it, not by inspection

`analysis/build_runs_inventory.py` was executed against the real 17 pre-rename
`_incoming/*/summary.json` files, with its output path redirected to a scratchpad file. Result:
**17 rows, 42 columns, `hull_load_identical` populated `True` on all 17, zero blank or `ABSENT`
rows.** The backward-compatible read works end to end on the actual artifacts. `data/` was not
written: `git status --porcelain -- data/` is empty and
`data/all_runs_inventory.csv` still hashes to
`9c3cf047682855052e89102c6f548fb1c1c4133e840670bb128a7eb0c83d6a41` with
`determinism_identical` as column 13.

---

## 5. What this branch deliberately did NOT change, and why

### 5.1 The as-ran archives, on sha evidence

**Read directly**, `shasum -a 256` on every copy, against the driver sha stamped in `jobA.out`
and quoted in `docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md`:

| file | sha256 | what it is |
|---|---|---|
| `renders/yaris_render_s1/sim_standing.py` | `4696c3b2...d10d9` | **the live driver.** Matches the published driver sha exactly |
| `render_s2/multigeom_2026-08-08/sim_standing.py` | `4696c3b2...d10d9` | byte-identical to the live driver |
| `renders/yaris_render_s1/_incoming/sim_standing.py` | `5215c38b...c9d45` | older as-ran copy |
| `analysis/render_v1/as_ran_local_copies/sim_standing.py` | `5215c38b...c9d45` | older as-ran copy, `diff` against `_incoming` is **0 lines** |
| `renders/yaris_render_s3_enhanced/sim_enhanced.py` | `a4b46c4f...70c7e` | separate enhanced driver |

`diff` between the live driver and `_incoming` is **228 lines**. So `_incoming/sim_standing.py`
is **not** the live driver; it is byte-identical to the copy under
`analysis/render_v1/as_ran_local_copies/`, whose own `README.md` states plainly: *"Archived
snapshot, 2026-07-25 ... This is a snapshot, not the working copy"* and *"the patched local code
that actually executed, pulled from Vista"* (**read directly**).

**Therefore `analysis/render_v1/as_ran_local_copies/sim_standing.py` was left byte-identical,
even though it is inside this slot's granted write scope.** Renaming a field in an as-ran archive
would falsify the record of what actually executed. This is a deliberate deviation from the
dispatch file list, made on evidence, and it is reversible: the rename can be applied later if
someone decides the archive should track the live name.

**Correction to a premise carried in the dispatch.** Register D4a records `_incoming/` as the
canonical per-run tree. That is true of the per-run **output** directories:
`analysis/build_runs_inventory.py` reads `_incoming/*/summary.json` and that is where the 17
canonical summaries live (**read directly**). It is **not** evidence that
`_incoming/sim_standing.py` is a live driver. The sha table above shows it is not.

### 5.2 No artifact regenerated

Nothing under `data/`, no `summary.json`, no `gates_results_all_runs.json`, no figure, no PDF.
`git status --porcelain -- data/ renders/yaris_render_s1/gates_results_all_runs.json` is empty
(**read directly**, after all edits).

---

## 6. Patches for the three files no worktree can reach

These three are untracked, so they exist only in the main checkout at
`/Users/josie/can-it-ford/` and are invisible to every worktree. Apply by hand, in the main
checkout, by someone with authority there.

Their ignore status differs and the difference matters (**read directly**,
`git check-ignore -v`; line numbers re-derived live 2026-08-18 and deliberately **not** cited
positionally, per CLAUDE.md, because `.gitignore` here has gone stale three times in one day):

- `renders/yaris_render_s1/gates_all_runs.py` matches the **negation** `!renders/yaris_render_s1/*.py`,
  so it is **NOT ignored**. It has simply never been `git add`ed. It shows as `??` in
  `git status` every time anyone looks.
- `renders/yaris_render_s1/_incoming/sim_standing.py` **is** ignored, by `renders/yaris_render_s1/*`.
  The carve-out is top-level only.
- `renders/yaris_render_s3_enhanced/sim_enhanced.py` **is** ignored, by `renders/*`.

### 6.1 `renders/yaris_render_s1/gates_all_runs.py` — APPLY

Reader and writer in one. Line 105.

```python
# CURRENT
        determinism_identical=s.get("determinism_identical", "ABSENT"),

# REPLACEMENT
        # RENAMED 2026-08-18. Backward-compatible read, forward-only write: pre-rename
        # summaries carry determinism_identical and none is being rewritten.
        hull_load_identical=s.get(
            "hull_load_identical", s.get("determinism_identical", "ABSENT")),
```

Note the enclosing `dict(...)` call means this keyword is also the **output** key written into
`gates_results_all_runs.json`, so this single line is both halves of the contract.

### 6.2 `renders/yaris_render_s3_enhanced/sim_enhanced.py` — APPLY

Live enhanced driver, distinct sha, not an archive. Lines 505 to 506, and 695.

```python
# CURRENT  (:505-506)
    det_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
    print("DETERMINISM identical=%s" % det_ok, flush=True)

# REPLACEMENT
    # RENAMED 2026-08-18. Hull-load reproducibility only: particle count and grid limit.
    # Not a trajectory check and not evidence of determinism. The "DETERMINISM " stdout
    # prefix is kept because scripts/run_three_class_*.sh capture logs with an anchored
    # /usr/bin/grep -E '^(...|DETERMINISM|...)'.
    hull_load_ok = (v1.n_particles == v2.n_particles) and (lim1 == lim2)
    print("DETERMINISM hull_load_identical=%s (hull load only, NOT trajectory)"
          % hull_load_ok, flush=True)
```

```python
# CURRENT  (:695)
        "determinism_identical": bool(det_ok),

# REPLACEMENT
        # FORWARD-ONLY WRITE: new key only. Existing summaries keep the old key.
        "hull_load_identical": bool(hull_load_ok),
```

### 6.3 `renders/yaris_render_s1/_incoming/sim_standing.py` — DO NOT APPLY

As-ran archive, sha `5215c38b...`, byte-identical to
`analysis/render_v1/as_ran_local_copies/sim_standing.py`, 228 diff lines behind the live driver.
See section 5.1. Leave it alone.

### 6.4 `render_s2/multigeom_2026-08-08/sim_standing.py` — YOUR CALL, not in this slot's scope

Currently byte-identical to the live driver (`4696c3b2...`). Once the live driver changes, the
two diverge whatever you do. Two defensible options, stated so nobody has to re-derive them:
apply the same patch as section 4 to keep it tracking the live driver, **or** leave it as the
as-ran record of the multigeom series. Applying it changes what that series records as having
run. Prefer leaving it unless someone intends to re-run multigeom from that copy.

---

## 7. FINDING: the script behind every published verdict is committed nowhere

**Read directly**, all four commands run this session against the main checkout:

```
git log --all --oneline -- renders/yaris_render_s1/gates_all_runs.py     -> no output
git ls-files --cached  -- renders/yaris_render_s1/gates_all_runs.py      -> no output
git rev-list --all --objects -- renders/yaris_render_s1/gates_all_runs.py -> no output
git for-each-ref | wc -l                                                  -> 155
```

**`renders/yaris_render_s1/gates_all_runs.py` has no commit history on any of 155 refs, and no
blob for that path exists in any reachable commit.** It exists on one disk, in one directory.

That is not a peripheral script. **Read directly** from its source, it imports
`AR_R_STABILITY_LIMITS` and `L1_verdict` from `vehicle_params`, applies
`DRIFT_THRESHOLD_M = 0.05`, `L0_DEPTH_THRESHOLD_M = 0.15` and `KRAMER_PASSENGER_HE_M = 0.30`,
computes `L0_verdict`, `L1a_verdict`, `L1b_verdict`, `L2_verdict` and `rungs_no_ford` for every
run, and writes `renders/yaris_render_s1/gates_results_all_runs.json`. **It is the script that
produces the project's headline verdict table.**

It is also, per section 6, **not gitignored**. Nothing was hiding it. It has been sitting in
`git status` as `??` and has never been added.

Context, **read directly**: 22 untracked `.py` files sit under `renders/yaris_render_s1/` against
2 tracked (`sim_standing.py`, `vehicle_live.py`, commit `00b735c`). Both figures reproduce
CLAUDE.md exactly. `gates_all_runs.py` is one of the 22.

This is a provenance hole, not a naming issue. Renaming a field inside a file that no commit has
ever seen does not fix it. **Recommendation: commit `gates_all_runs.py` before or with the
rename**, so the verdict table has a history. That is outside this slot's write scope and needs
a decision from whoever owns `renders/`.

---

## 8. FINDING: the false claim is in a committed PDF on a public remote

**Do not test this with `strings`.** `/usr/bin/strings` on the poster returns **0** hits for
`all runs deterministic`, because PDF text streams are Flate-compressed. Decompressing the
streams and flattening to letters returns **1**. A `strings`-based check will "disprove" this
finding, falsely.

**Read directly**, by extracting the blob from the remote-tracking ref rather than the working
tree, `git cat-file blob origin/main:public_release/Cerrell_TACC_42x56.pdf` (6,102,270 bytes),
then decompressing its streams:

- `all runs deterministic` present, 1 occurrence
- `bit-reproducible` present, 1 occurrence
- `carry a determinism record` present, 1 occurrence

**The repository is public** (`github.com/jcerrell-IS/can-it-ford`, and this account has served
removed blobs by SHA before). So the claim is world-readable, permanent, and sits under the
heading `ESTABLISHED`.

Reconstructed from the PDF text operators (**read directly**), the poster's Fig 2 caption reads:

> Fig 2. Final displacement against surge velocity at fixed realized depth 0.2944 m, grid 64,
> one hull at 1100 kg, **all runs deterministic.** Vertical rule marks v = 1.0189 m/s ...

and the scope banner reads:

> **ESTABLISHED**   20 coupled runs. **All 17 that carry a determinism record are
> bit-reproducible**; the 3 dry-start runs record none. ...

Note the poster caption omits the `(determinism_identical = True)` parenthetical that the figure
generator emits, which is why a search for the field name finds it in
`deliverables/poster/figures/g1_velocity_sweep.pdf` but not in the poster itself.

**Where the string is present** (all confirmed by stream decompression, **read directly**):

| artifact | committed? |
|---|---|
| `public_release/Cerrell_TACC_42x56.pdf` | **COMMITTED, on `origin/main`, public** |
| `figures/g1_velocity_sweep.pdf` | **COMMITTED** |
| `figures/_pre_accuracy_fix_2026-07-26/g1_velocity_sweep.pdf` | **COMMITTED** |
| `deliverables/poster/Cerrell_TACC_42x56.pdf` | untracked |
| `deliverables/poster/Cerrell_TACC_42x56dup.pdf` | untracked |
| `deliverables/poster/_pre_style3_2026-07-26/Cerrell_TACC_42x56.pdf` | untracked |
| `deliverables/for_kumar/01_deliverables/Cerrell_TACC_42x56.pdf` | untracked |
| `deliverables/for_kumar 2/01_deliverables/Cerrell_TACC_42x56.pdf` | untracked |
| `deliverables/poster/figures/g1_velocity_sweep.pdf` | untracked |

**Two limits, so nobody over-reads the table.** My extractor handles Flate only, so a **0** from
it is not proof of absence; `figures/_BIG/g1_velocity_sweep.pdf` and
`deliverables/paper/overleaf/figs/g1_velocity_sweep.pdf` returned 0 and may be raster-wrapped.
And the `.png` copies returned 0 to `grep` **by construction**, since a raster carries no text
layer, so that test says nothing at all about them.

**No poster was regenerated and none should be by this slot.** Remediation of a document already
shown to a mentor and already pushed to a public remote is a human decision. Ready-to-paste
errata text is in section 11.

---

## 9. Provenance of the premise, including what I could NOT verify

**Verified by me, live, this session:** the `det_ok` line and what it compares; the flag's value
on all 17 runs in both stores; the `gates_results_all_runs.json` 20-record structure;
`gates_all_runs.py:105`'s existing `.get(..., "ABSENT")` pattern; the artifact footprint;
the driver shas; the PDF contents.

**NOT verified by me. Single source. Marked unreviewed.** The statement that *all 20 A2 repeats
are bit-different with divergence by frame 0* rests solely on
`docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md`, which exists on **no branch this one can
reach**: it is present in seven sibling worktrees and absent from the main checkout and from
`docs/` on this branch. The underlying `d4_jobA` metrics are **not on this Mac** (searched
`/Users/josie` to depth 4 and the repo to depth 5, no `d4_jobA*` anywhere), so I could not
recompute the 20 sha256 values independently. The physics-skeptic subagent cannot help here:
there is no local data for it to check. **The replacement captions in section 4 were written so
that they do not depend on this claim.**

**Corroboration from genuinely separate origins**, which matters because one source cited twice
is not two sources. Three independent authors each hit this defect and each worked around it
locally instead of fixing the name (**all read directly**):

1. `scripts/run_three_class_matched.sh:90-98`, a committed shell script:
   *"Register item 17 records this stack as NON-DETERMINISTIC at fixed configuration, and
   register J-item notes determinism_identical reported True on six runs that differ. ... Compare
   the two metrics.csv directly; do not read determinism_identical."*
2. `analysis/classify_three_class_matched.py:189`, which named its own output field
   `determinism_identical_FLAG_DO_NOT_TRUST`.
3. `docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md` section 1a.

Different files, different authors, different dates, different methods. That is corroboration.
It still does not substitute for me re-measuring the repeats, and I have not.

---

## 10. What breaks if someone regenerates the artifacts

Nothing here has been regenerated. If someone does, **read this first.**

1. **`data/all_runs_inventory.csv` changes its header.** Column 13 goes from
   `determinism_identical` to `hull_load_identical`. Its sha changes from
   `9c3cf047682855052e89102c6f548fb1c1c4133e840670bb128a7eb0c83d6a41`. Every reader inside this
   branch accepts both, so nothing in-scope breaks. **Readers outside this branch are the
   hazard**, and the three `deliverables/*/make_poster_figures_accessible.py` copies still do a
   bare `r["determinism_identical"]` subscript and will raise `KeyError`, not degrade quietly.
2. **Every `summary.json` regenerated by the patched driver loses the old key.** There are 40+
   `summary.json` files carrying it across `renders/`, `render_s2/`, `data/g128_*`,
   `data/g128_canonical_*`, `data/rogue_silverado_sweep_*`, plus 9 `data/*.csv`. A partial
   regeneration produces a **mixed-key corpus**, which the both-key readers handle, but which
   makes any future count of "how many runs carry the flag" scope-sensitive all over again.
3. **`gates_results_all_runs.json` would change key name and could silently lose its 3
   `"ABSENT"` records' meaning** if the patch in section 6.1 is not applied first. Apply 6.1
   before regenerating anything that runs `gates_all_runs.py`.
4. **A regenerated poster figure is not a regenerated poster.** `deliverables/poster/build_poster.py`
   carries its own caption text (section 2, pattern B and C) and is untracked. Re-running
   `make_poster_figures.py` fixes the figure PDFs and leaves the poster's own text false.
5. **Regenerating figures does not unpublish the committed PDF.** `public_release/Cerrell_TACC_42x56.pdf`
   is already on a public remote. Rebuilding it locally changes the working tree, not what GitHub
   has already served.

**The largest risk is a well-meant "just regenerate everything to make it consistent" pass.**
It would rewrite the as-ran record, break three out-of-branch readers with a `KeyError`, and
still leave the poster text wrong.

---

## 11. Items for other slots, not actioned here

- **For `d7-register`:** `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` around line 794
  lists `` `determinism_identical` is **true** on all three `` as one of *"three independent
  resolution gains"* at g128 (**read directly**). The corrections authority is itself reading the
  flag as evidence of a resolution gain. That is the exact misreading this rename exists to
  prevent. The register is outside this slot's write scope, so it is flagged, not edited.
- **For whoever owns `deliverables/`:** the six pattern-C defect sites in `build_poster.py`,
  its `_pre_style3` copy and `build_slides.py`, plus the nine pattern-B sites in the three
  `make_poster_figures_accessible.py` copies. Suggested errata line:

  > **Erratum, 2026-08-18.** The poster and slides state that 17 of 20 coupled runs are
  > "bit-reproducible" and that "all runs" are "deterministic". Both statements rest on the
  > summary field `determinism_identical`, which compares two loads of the same hull on particle
  > count and grid limit only. It is a hull-load check and is not evidence of run-to-run
  > reproducibility. The field has been renamed `hull_load_identical`. Hull loading is
  > bit-identical; the trajectories are not established to be.

- **For whoever owns `scripts/`:** the `DETERMINISM ` stdout anchor token is still the misleading
  word. Changing it requires updating the three anchored `grep -E` captures in the same commit.

---

## 12. A note on the frozen-worktree hazard, so nobody draws the wrong conclusion

This worktree's `CLAUDE.md` is **855 lines and so is the main checkout's**, so the usual
heading-diff shows no drift. **That is inheritance, not the hazard being gone.** This branch was
cut from `claude/add-ci-checks` after the 855-line version landed in commit `2c6a877`, so it
inherited it. Sibling worktrees launched from older bases still see 676 lines and are missing
whole sections. The next person to run the heading-diff here and see a clean result should not
conclude the frozen-worktree hazard has been fixed; it has been avoided on this one branch by
the choice of base commit.

---

## 13. Reproducing every count in this document

The enumeration is a Python `re` walk that prints each path and line, not a shell `grep`. The
shell `grep` in this environment wraps ugrep with `--ignore-files` and skips gitignored paths,
which would drop 13 of the 32 pattern-A sites without saying so.

```
python3 - <<'EOF'
import os, re, subprocess
ROOT = "/Users/josie/can-it-ford"
SKIP = (".claude/worktrees", "third_party", "__pycache__", "/.git/")
PATS = {"A_field_name": r"determinism_identical",
        "B_caption":    r"all runs deterministic",
        "C_prose":      r"determinism record|bit-reproducible"}
for k, rx in PATS.items():
    rx = re.compile(rx); n = 0; files = set()
    for dp, dns, fns in os.walk(ROOT):
        if any(s in dp + "/" for s in SKIP):
            dns[:] = []; continue
        for fn in (f for f in fns if f.endswith(".py")):
            p = os.path.join(dp, fn)
            for i, l in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                if rx.search(l):
                    n += 1; files.add(p)
                    print("  %s:%d  %s" % (os.path.relpath(p, ROOT), i, l.strip()[:96]))
    print("=== %s : %d sites in %d files ===" % (k, n, len(files)))
EOF
```

PDF text, which `strings` cannot see:

```
python3 - <<'EOF'
import re, sys, zlib
raw = open(sys.argv[1], 'rb').read(); out = []
for m in re.finditer(rb'stream\r?\n', raw):
    s = m.end(); e = raw.find(b'endstream', s)
    if e < 0: continue
    b = raw[s:e]
    try: b = zlib.decompress(b)
    except Exception: pass
    out.append(b)
flat = re.sub(rb'[^A-Za-z]', b'', b'\n'.join(out) + raw).lower()
for n in (b'allrunsdeterministic', b'bitreproducible'):
    print(flat.count(n), n.decode())
EOF
```

Driver identity:

```
shasum -a 256 /Users/josie/can-it-ford/renders/yaris_render_s1/sim_standing.py
# expected before this change: 4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9
```
