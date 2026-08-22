# R8 d8-naming: a false claim on a public poster, a verdict script with no history, and the rename that found them

Written 2026-08-18 by slot `d8-naming`, branch `claude/r8-naming`, worktree
`.claude/worktrees/r8-naming`. Every number below was measured live this session in the
main checkout at `/Users/josie/can-it-ford`, not carried from a summary. Each claim carries
a provenance tag: **read directly**, **recalled**, or **inferred**.

Engine tag for every solver claim in this document: **warpmpm**. The driver is
`renders/yaris_render_s1/sim_standing.py`.
No Genesis path is involved anywhere in this work.
CLAUDE.md August 4 audit item 1 is the authority and was read live.

> **Section numbering changed after commit `b36ab5d`**, when the public-poster finding was
> promoted from section 8 to section 1. Earlier commit messages on this branch cite the old
> numbers. Mapping: old 8 is now **1**; old 1 is now **2**; old 2 is now **3**; old 3 is now
> **4**; old 4 is now **5**; old 5.1 is now **6.1**; old 6.1 is now **7.1**; old 7 is now **8**.
> Sections 9, 10, 11, 12 and 13 keep their numbers.

---

## 0. The one-paragraph version

`determinism_identical` compares two loads of the same hull on a particle count and a grid
limit. It is a hull-load reproducibility check. It is not, and cannot be, a determinism check.
It reads `true` on all 17 published runs. The name has been changed to `hull_load_identical`
at every site this branch can reach, backward-compatible on read and forward-only on write, and
no artifact has been regenerated. Two things found on the way are more serious than the name.
**Section 1**: the false claim is in a **committed PDF on `origin/main` in a public repository**,
under a heading that reads `ESTABLISHED`, in a document that was presented. **Section 8**: the
script that computes every published verdict column has **no commit history on any of 155 refs**
and exists on one disk.

---

## 1. THE ESCALATION: a false claim about our own results, on a public committed poster

### 1.1 What is there

**Read directly.** Two separate false statements are rendered in
`public_release/Cerrell_TACC_42x56.pdf` as that file exists **in the commit history of
`origin/main`**, not merely in someone's working tree. The repository is public
(`github.com/jcerrell-IS/can-it-ford`), and this account has served removed blobs by SHA before,
so the content is world-readable and effectively permanent.

**Statement A**, in the poster's `Scope` panel, under the sub-heading `ESTABLISHED`. Exact
rendered text, extracted from the committed blob:

> **Scope**
> **ESTABLISHED** 20 coupled runs. **All 17 that carry a determinism record are
> bit-reproducible**; the 3 dry-start runs record none. Mesh containment 100.00 pct of a
> 2000-particle subsample. DxV bit-identical across a 2.1x mass range.

**Statement B**, in the caption of Fig 2. Exact rendered text:

> Fig 2. Final displacement against surge velocity at fixed realized depth 0.2944 m, grid 64,
> one hull at 1100 kg, **all runs deterministic.** Vertical rule marks v = 1.0189 m/s, where
> DxV crosses the AR&R small-passenger 0.30 m2/s cap. ...

### THE POSTER IS NOT SLOPPY. IT IS THE NAMING DEFECT REACHING PRINT.

Statement A is careful, specific, and correct about everything except the one word that matters.
Read it clause by clause against what was measured:

| clause in statement A | true? |
|---|---|
| "20 coupled runs" | **true**, `gates_results_all_runs.json` holds 20 records |
| "All 17 that carry a determinism record" | **true**, 17 carry the field |
| "the 3 dry-start runs record none" | **true**, those 3 carry the literal `"ABSENT"` |
| "are **bit-reproducible**" | **FALSE** |

Every factual component is right. The author counted correctly, partitioned the runs correctly,
and reported the field's value correctly. The sentence is false only because it substitutes the
**name** of the field for what the field **measures**, and the name is wrong:
`determinism_identical` compares a particle count and a grid limit between two loads of the same
hull (section 2), while the trajectories differ.

So this is not overclaiming, and describing it that way would be both weaker and less accurate.
**It is a correct statement about a field whose name does not describe what the field measures,
printed under a heading that reads `ESTABLISHED`.** A reader doing everything right, trusting the
field name as a field name, arrives at a false published claim. That is the strongest available
argument for renaming rather than merely documenting: the defect had already reached print, and
no amount of care at the writing stage would have caught it.

The same reading applies to statement B, with `ESTABLISHED` being what makes statement A the more
serious of the two.

Note that the poster's Fig 2 caption drops the `(determinism_identical = True)` parenthetical
that the figure generator emits. That is why a search for the field name finds the claim in
`deliverables/poster/figures/g1_velocity_sweep.pdf` but **not** in the poster itself, and it is
the same mechanism described in section 3.

### 1.2 THE METHOD IS LOAD-BEARING. `strings` RETURNS ZERO AND WILL FALSELY DISPROVE THIS.

**Anyone re-checking this with the obvious tool gets the wrong answer.** PDF text lives in
Flate-compressed content streams, so a byte scanner cannot see it.

```
/usr/bin/strings public_release/Cerrell_TACC_42x56.pdf | grep -c 'all runs deterministic'
    -> 0        <-- FALSE NEGATIVE, verified live as an explicit control
```

Reproduce the finding in one go. This route goes through the **blob SHA**, so it does not use
`rev:path` syntax at all:

```sh
# 1. resolve the blob that origin/main actually carries
git -C /Users/josie/can-it-ford ls-tree origin/main -- public_release/Cerrell_TACC_42x56.pdf
#   -> 100644 blob 168879947da7d271e0c17da28f8719c46ee57a68  public_release/Cerrell_TACC_42x56.pdf

# 2. extract it by blob SHA, never from the working tree
git -C /Users/josie/can-it-ford cat-file blob 168879947da7d271e0c17da28f8719c46ee57a68 \
    > /tmp/poster.pdf
#   -> 6102270 bytes, sha256 48685a7dc20b5c4d58eb7d38e8f644b04a8a2246a62a9083eedfe13d65b2ed63

# 3. decompress the content streams and read the show-strings
python3 - /tmp/poster.pdf <<'EOF'
import re, sys, zlib
raw = open(sys.argv[1], 'rb').read(); out = []
for m in re.finditer(rb'stream\r?\n', raw):
    s = m.end(); e = raw.find(b'endstream', s)
    if e < 0: continue
    b = raw[s:e]
    try: b = zlib.decompress(b)
    except Exception: pass
    out.append(b)
shown = b''.join(re.findall(rb'\(((?:[^()\\]|\\.)*)\)', b'\n'.join(out) + raw))
flat = re.sub(rb'\s+', b' ', shown); low = flat.lower()
for needle in (b'established', b'bit-reproducible', b'all runs deterministic'):
    i = low.find(needle)
    print("\n--- %s at %d ---\n%s" % (needle.decode(), i,
          flat[max(0, i-40): i+300].decode('latin-1') if i >= 0 else "NOT FOUND"))
EOF
```

Step 3's `( ... )` show-string extraction is what makes the output readable prose. A letters-only
flatten of the whole stream also detects the strings but returns unreadable glyph-spacing soup.

**Corroborated by two independent extraction routes.** `git cat-file blob origin/main:<path>`
and `git cat-file blob <blob-sha>` produced byte-identical files, both sha256
`48685a7dc20b5c4d58eb7d38e8f644b04a8a2246a62a9083eedfe13d65b2ed63`, with identical string
counts. The blob SHA itself came from `ls-tree`, which is a third path to the same object.

**Two limits on the method, stated so nobody over-reads the table below.** The extractor handles
Flate only, so a **0** from it is not proof of absence; `figures/_BIG/g1_velocity_sweep.pdf` and
`deliverables/paper/overleaf/figs/g1_velocity_sweep.pdf` both returned 0 and may be
raster-wrapped. And the `.png` copies return 0 to `grep` **by construction**, because a raster
carries no text layer, so that test says nothing about them at all.

### 1.3 Where the strings are

| artifact | committed? |
|---|---|
| `public_release/Cerrell_TACC_42x56.pdf` | **COMMITTED, on `origin/main`, public** |
| `figures/g1_velocity_sweep.pdf` | **COMMITTED** |
| `figures/_pre_accuracy_fix_2026-07-26/g1_velocity_sweep.pdf` | **COMMITTED** |
| `deliverables/poster/Cerrell_TACC_42x56.pdf` | untracked |
| `deliverables/poster/Cerrell_TACC_42x56dup.pdf` | untracked |
| `deliverables/poster/_pre_style3_2026-07-26/Cerrell_TACC_42x56.pdf` | untracked |
| `deliverables/for_kumar/01_deliverables/Cerrell_TACC_42x56.pdf` | untracked, handoff tree |
| `deliverables/for_kumar 2/01_deliverables/Cerrell_TACC_42x56.pdf` | untracked, handoff tree |
| `deliverables/poster/figures/g1_velocity_sweep.pdf` | untracked |

The generators that emit these strings are `deliverables/poster/build_poster.py:81-82` and `:100`,
its `_pre_style3_2026-07-26/` copy, and `deliverables/slides/build_slides.py:200` and `:209`.
All are untracked and all are outside this slot's write scope.

### 1.4 What is true instead, at poster-caption length, ready to drop in

**Replacement for statement A**, the `ESTABLISHED` scope line:

> **ESTABLISHED** 20 coupled runs. Hull loading is bit-identical across all 17 that carry the
> record; their trajectories are not established to be. The summary field previously called
> `determinism_identical`, now `hull_load_identical`, only ever compared a particle count and a
> grid limit between two loads of the same hull. Mesh containment 100.00 pct of a 2000-particle
> subsample. DxV bit-identical across a 2.1x mass range.

**Replacement for statement B**, the Fig 2 caption clause:

> ... grid 64, one hull at 1100 kg. Hull loading is bit-identical across these runs; their
> trajectories are not. Vertical rule marks v = 1.0189 m/s ...

**Standalone erratum**, if the poster is not re-issued:

> **Erratum, 2026-08-18.** The poster states, under `ESTABLISHED`, that "All 17 that carry a
> determinism record are bit-reproducible", and the Fig 2 caption says "all runs deterministic".
> The slides repeat the first. **The run counts and the partition in those sentences are correct,
> and so is the value they report. The error is in the word "bit-reproducible", and it was
> inherited from the name of the field rather than introduced in the writing.** The summary field
> was called `determinism_identical`, but it compares a particle count and a grid limit between
> two loads of the same hull, and nothing else. It is a hull-load check. It reads True on all 17
> runs and cannot detect whether the trajectories differ. The field has been renamed
> `hull_load_identical` so the name states what it measures. **Corrected claim: hull loading is
> bit-identical across the 17 runs; their trajectories are not established to be.**

### 1.5 What this slot did NOT do, deliberately

**No poster was regenerated. `public_release/` was not touched. No figure PDF was rebuilt.**
Whether to re-issue an artifact that has been presented and pushed to a public remote is Josie's
call and carries consequences not visible from inside this branch. Note also that rebuilding the
PDF locally would change the working tree and would **not** unpublish what GitHub has already
served.

---

## 2. The defect in the field itself

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
| the runs are nonetheless not reproducible | **single source, not reproduced by me**, see section 9 |

The ledger instruction was to rename rather than delete, because hull loading genuinely **is**
bit-identical and that is what localises the non-determinism to the solve. That instruction is
followed here.

---

## 3. The enumeration, with its scope stated

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
Split by role: **5 writer files**, **11 reader files**.

### Pattern B, the caption prose `all runs deterministic`: **23 sites in 9 files**

Three sites in each of the seven `make_poster_figures*` scripts (four tracked, three untracked
`_accessible` copies), plus one each in `deliverables/poster/build_poster.py` and its
`_pre_style3_2026-07-26/` copy.

### WHY EVERY PRIOR COUNT WAS LOW, INCLUDING MINE

**A grep for the identifier cannot find a caption that asserts the claim in prose.** Two of the
three caption sites in each generator name no field at all. They read
`"... one hull at 1100 kg, all runs deterministic. "` and
`"Grid 64, realized depth %.4f m, 1.5 m/s surge, all runs deterministic.\n"`. Every search for
`determinism_identical` misses them, and every count built from such a search is therefore low by
construction, not by carelessness. My own scope-confirmation enumeration earlier tonight missed
them for exactly this reason.

**The next person auditing a claim-versus-code mismatch will reach for the identifier first.**
That is the wrong first move. Search for the *assertion* as a reader would encounter it, then for
the identifier, and treat the two results as different quantities.

### Pattern C, the prose `determinism record` / `bit-reproducible`: **8 sites in 5 files**

Six are defects, in three files, all untracked and all outside this branch's write scope:
`deliverables/poster/build_poster.py:81-82` and its `_pre_style3_2026-07-26/` copy, and
`deliverables/slides/build_slides.py:200` and `:209`.

Two are **correct usages and are not defects**, both tracked, both left alone (**read directly**,
full context checked before classifying): `analysis/three_class_matched_grid.py:40` and
`analysis/preflight_hull_guard.py:82` both state that the **mesh pipeline** is not
bit-reproducible, which is true and is a different claim.

### Union

**56 sites in 21 files.** 29 sites in 11 tracked files, 27 sites in 10 untracked files.

---

## 4. The three-pattern decomposition RESOLVES the four-way count dispute

Four figures for "how many sites" have been in circulation and appeared to disagree. **They do
not disagree. They were measuring three different patterns, and nobody said which.** All four
are correct about different things. Two reproduce exactly once the pattern is named.

| figure in circulation | what it actually counted | reproduces? |
|---|---|---|
| **19 sites, 9 files** (mine, scope confirmation) | pattern A, tracked-only scope | **exact**, and correctly scope-labelled at the time |
| **23 sites, 9 files** (adversarial pass) | **pattern B**, full-repo scope | **exact on BOTH numbers** |
| **5 writers, 7 generators** (Round 7 ledger) | pattern A. 5 writers at **full-repo** scope; 7 generators at **tracked-only** scope | **exact on both halves**, but two scopes inside one sentence |
| **4 writers, 2 generators** (coordinator, earlier) | pattern A. *inferred*: 4 counts only the copies literally named `sim_standing.py` and so misses the differently-named `sim_enhanced.py`; 2 counts generator *families* rather than files | **inferred, not confirmed** |

**The adversarial pass was measuring a real thing and naming it imprecisely. It was not
miscounting.** Pattern B reproduces its figure exactly on both the site count and the file count,
and pattern B is the publication-facing prose, which is the more serious quantity of the two. Its
accompanying claim that the text reached the presented poster is also correct, and is section 1.

**I withdraw my own explanation for the 23.** In my scope confirmation I proposed that 23 came
from "pattern A minus the three `deliverables/` copies". That route reaches the right number by
arithmetic coincidence and gives **13 files, not 9**, so it was wrong, and the file count is what
exposes it. This is the standard: an explanation that reproduces the headline number but not the
subsidiary one has not been verified.

This is the project's standing lesson about bare totals, arriving from a fourth direction. The
earlier instances were **scope**-driven: the threshold-literal inventory at CLAUDE.md item 13,
where two independent binary choices yield four defensible totals, and the research-corpus
cited-status count, which moved on whether `.claude/worktrees/` was included. **This one is
pattern-driven**, which is harder to notice, because two people can agree on the scope perfectly
and still be counting different things. **State the pattern and the scope, or state no number.**

---

## 5. What this branch changed

Eight tracked files, all inside the worktree. Backward-compatible on read, forward-only on write,
following the `gates_all_runs.py:105` `s.get(..., "ABSENT")` pattern named in the dispatch.

| file | change |
|---|---|
| `renders/yaris_render_s1/sim_standing.py` | `det_ok` to `hull_load_ok`; summary key to `hull_load_identical`; explanatory comment block |
| `analysis/build_runs_inventory.py` | CSV column renamed (forward-only); explicit both-key fallback after the generic comprehension; console header `det` to `hull_ld` |
| `analysis/check_run_validity_2026-08-10.py` | both-key read; warning text corrected; comment stating what `True` does **not** mean |
| `analysis/classify_three_class_matched.py` | `determinism_identical_FLAG_DO_NOT_TRUST` to `hull_load_identical`, both-key read |
| `analysis/make_poster_figures.py` + `_BIG`, `_BIG_GRIDAWARE`, `_GRIDAWARE` | **five** sites each: three captions, one both-key set comprehension, one gate-table row |

**Invariant enforced mechanically at patch time**, not by eye: no code line may contain
`determinism_identical` outside a `.get()` fallback, and no bare subscript
`["determinism_identical"]` may survive, because that would raise `KeyError` the moment an
artifact carries only the new key. Every file re-parsed with `ast.parse` after writing.
After-state in the worktree: **0** bare subscripts, **0** instances of `all runs deterministic`,
and the 15 remaining mentions are 7 comments, 7 `.get()` fallbacks, and the 1 deliberately
untouched as-ran archive.

**The stdout prefix is deliberately unchanged.** `print("DETERMINISM ...")` keeps its
`DETERMINISM ` prefix, because `scripts/run_three_class_matched.sh:167`,
`run_three_class_full33.sh:79` and `run_three_class_massswap.sh:124` capture solver logs with an
anchored `/usr/bin/grep -E '^(PREFLIGHT|INSTRUMENT|SUBSTEP_TERMS|DETERMINISM|...)'`
(**read directly**). Those scripts are outside this scope, and renaming the prefix would silently
drop those lines from every captured log with no error. The line text now reads
`DETERMINISM hull_load_identical=%s (hull load only, NOT trajectory)`. **Follow-up for whoever
owns `scripts/`:** the anchor token is still the misleading word.

**The new captions assert only what the code alone establishes**, which is airtight and is enough
to remove the false claim. They deliberately do **not** depend on the repeats result I could not
reproduce (section 9). The gate-table row was relabelled and **downgraded from `PASS` to
`NOTED`**: the value is a true statement about hull loading, so the check does pass what it
measures, but a green `PASS` beside the old name read as a reproducibility guarantee the flag
cannot provide.

**Verified by running it, not by inspection.** `analysis/build_runs_inventory.py` was executed
against the real 17 pre-rename `_incoming/*/summary.json` files with its output path redirected to
a scratchpad file. Result: **17 rows, 42 columns, `hull_load_identical` populated `True` on all
17, zero blank or `ABSENT` rows.** `data/` was not written: `git status --porcelain -- data/` is
empty and `data/all_runs_inventory.csv` still hashes to
`9c3cf047682855052e89102c6f548fb1c1c4133e840670bb128a7eb0c83d6a41` with `determinism_identical`
as column 13.

---

## 6. What this branch deliberately did NOT change

### 6.1 The as-ran archives. A GRANTED SCOPE IS A CEILING, NOT AN INSTRUCTION.

**Read directly**, `shasum -a 256` on every copy, against the driver sha stamped in `jobA.out`:

| file | sha256 | what it is |
|---|---|---|
| `renders/yaris_render_s1/sim_standing.py` | `4696c3b2...d10d9` | **the live driver.** Matches the published driver sha exactly |
| `render_s2/multigeom_2026-08-08/sim_standing.py` | `4696c3b2...d10d9` | byte-identical to the live driver |
| `renders/yaris_render_s1/_incoming/sim_standing.py` | `5215c38b...c9d45` | older as-ran copy |
| `analysis/render_v1/as_ran_local_copies/sim_standing.py` | `5215c38b...c9d45` | older as-ran copy, `diff` against `_incoming` is **0 lines** |
| `renders/yaris_render_s3_enhanced/sim_enhanced.py` | `a4b46c4f...70c7e` | separate enhanced driver |

`diff` between the live driver and `_incoming` is **228 lines**. `analysis/render_v1/README.md`
states plainly (**read directly**): *"Archived snapshot, 2026-07-25 ... This is a snapshot, not
the working copy"* and *"the patched local code that actually executed, pulled from Vista"*.

**`analysis/render_v1/as_ran_local_copies/sim_standing.py` was therefore left byte-identical,
even though it sits inside this slot's granted write scope.** Renaming a field in an as-ran
archive would falsify the record of what actually executed. The sha evidence settles it without
appeal to taste. **The rule this establishes: a granted scope is a ceiling, not an instruction.**
The decision is reversible if someone later decides the archive should track the live name.

**Correction to a premise carried in the dispatch.** Register D4a records `_incoming/` as the
canonical per-run tree. That is true of the per-run **output** directories:
`analysis/build_runs_inventory.py` reads `_incoming/*/summary.json` and that is where the 17
canonical summaries live (**read directly**). It is **not** evidence that
`_incoming/sim_standing.py` is a live driver. The sha table shows it is not.

### 6.2 No artifact regenerated

Nothing under `data/`, no `summary.json`, no `gates_results_all_runs.json`, no figure, no PDF,
no poster. `git status --porcelain -- data/ renders/yaris_render_s1/gates_results_all_runs.json`
is empty (**read directly**, after all edits).

---

## 7. Patches for the three files no worktree can reach

These three are untracked, so they exist only in the main checkout and are invisible to every
worktree. Apply by hand, by someone with authority there.

Their ignore status differs and the difference matters (**read directly**, `git check-ignore -v`;
`.gitignore` line numbers deliberately **not** cited positionally, per CLAUDE.md, because that
file has gone stale three times in one day):

- `renders/yaris_render_s1/gates_all_runs.py` matches the **negation**
  `!renders/yaris_render_s1/*.py`, so it is **NOT ignored**. See section 8.
- `renders/yaris_render_s1/_incoming/sim_standing.py` **is** ignored, by
  `renders/yaris_render_s1/*`. The carve-out is top-level only.
- `renders/yaris_render_s3_enhanced/sim_enhanced.py` **is** ignored, by `renders/*`.

### 7.1 `renders/yaris_render_s1/gates_all_runs.py`: APPLY (see section 8 first)

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

The enclosing `dict(...)` call means this keyword is also the **output** key written into
`gates_results_all_runs.json`, so this single line is both halves of the contract.

### 7.2 `renders/yaris_render_s3_enhanced/sim_enhanced.py`: APPLY

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

### 7.3 `renders/yaris_render_s1/_incoming/sim_standing.py`: DO NOT APPLY

As-ran archive, sha `5215c38b...`, byte-identical to
`analysis/render_v1/as_ran_local_copies/sim_standing.py`, 228 diff lines behind the live driver.
See section 6.1.

### 7.4 `render_s2/multigeom_2026-08-08/sim_standing.py`: YOUR CALL, not in this slot's scope

Currently byte-identical to the live driver (`4696c3b2...`). Once the live driver changes, the
two diverge whatever you do. Either apply the section 5 patch to keep it tracking the live
driver, **or** leave it as the as-ran record of the multigeom series. Applying it changes what
that series records as having run. Prefer leaving it unless someone intends to re-run multigeom
from that copy.

---

## 8. FINDING: the script that computes every published verdict has no history

**`renders/yaris_render_s1/gates_all_runs.py` has ZERO commits across 155 refs.** Verified three
separate ways this session, none of them relayed (**all read directly**):

```
git log --all --oneline           -- renders/yaris_render_s1/gates_all_runs.py   -> empty
git ls-files --cached             -- renders/yaris_render_s1/gates_all_runs.py   -> empty
git rev-list --all --objects      -- renders/yaris_render_s1/gates_all_runs.py   -> empty
git for-each-ref | wc -l                                                          -> 155
```

The third probe is the strongest: **no blob for that path exists in any reachable commit**, so
this is not a case of the file having been removed at some point. It has never been in the object
graph under that path.

It is not a peripheral script. **Read directly** from its source, it imports
`AR_R_STABILITY_LIMITS` and `L1_verdict` from `vehicle_params`, applies `DRIFT_THRESHOLD_M = 0.05`,
`L0_DEPTH_THRESHOLD_M = 0.15` and `KRAMER_PASSENGER_HE_M = 0.30`, computes **`L0_verdict`,
`L1a_verdict`, `L1b_verdict`, `L2_verdict`** and `rungs_no_ford` for every run, and writes
`renders/yaris_render_s1/gates_results_all_runs.json`. **It is the script that produces the
project's headline verdict table, and it exists on one disk with no history.**

**It is NOT gitignored.** `git check-ignore -v` shows it matching the **negation**
`!renders/yaris_render_s1/*.py`, so it is un-ignored, it sits in `git status` as `??` every time
anyone looks, and it has simply never been `git add`ed. Nothing was hiding it.

Context, **read directly**: 22 untracked `.py` files sit under `renders/yaris_render_s1/` against
2 tracked (`sim_standing.py`, `vehicle_live.py`, commit `00b735c`). Both figures reproduce
CLAUDE.md exactly. `gates_all_runs.py` is one of the 22.

**This is a provenance decision, not a naming one, and this slot did not make it.** Adding an
untracked driver to the repository is out of scope here. Renaming a field inside a file that no
commit has ever seen does not fix the underlying problem either. The patch, for whenever the
decision is made, is section 7.1.

---

## 9. Provenance of the premise, including what I could NOT verify

**Verified by me, live, this session:** the `det_ok` line and what it compares; the flag's value
on all 17 runs in both stores; the `gates_results_all_runs.json` 20-record structure;
`gates_all_runs.py:105`'s existing `.get(..., "ABSENT")` pattern; the artifact footprint; the
driver shas; the poster blob and its contents by two independent extraction routes.

**NOT verified by me. Single source. Marked unreviewed.** The statement that *all 20 A2 repeats
are bit-different with divergence by frame 0* rests solely on
`docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md`, which exists on **no branch this one can
reach**: present in seven sibling worktrees, absent from the main checkout and from `docs/` on
this branch. The underlying `d4_jobA` metrics are **not on this Mac** (searched `/Users/josie` to
depth 4 and the repo to depth 5, no `d4_jobA*` anywhere), so I could not recompute the 20 sha256
values independently. **The replacement captions in sections 1.4 and 5 were written so that they
do not depend on this claim**, and say "not established to be" rather than "are not".

**The physics-skeptic subagent was not run, and this is not a faked review.** Every claim in this
document is code provenance, git object state, or string presence in a file. None is a
percentage, force, verdict count, or distance. The subagent is not the right instrument for these
and would have nothing to check.

*Recorded for the provenance trail, not independently verified by me:* two sibling slots
(`d2-persist` and `d4-bcmerge`) reported on the shared board that the physics-skeptic subagent
terminated on an API error naming an unreachable model this session, and that a model override
did not help. That is their measurement, not mine. It does not change the reasoning above, which
is that these claims are outside what the subagent is for, but it does mean the instrument was
also unavailable, so a future reader should not read the absence of a review here as a review
that was skipped when it could have been run.

**Corroboration from genuinely separate origins**, which matters because one source cited twice is
not two sources. Three independent authors each hit this defect and each worked around it locally
instead of fixing the name (**all read directly**):

1. `scripts/run_three_class_matched.sh:90-98`, a committed shell script: *"Register item 17
   records this stack as NON-DETERMINISTIC at fixed configuration, and register J-item notes
   determinism_identical reported True on six runs that differ. ... Compare the two metrics.csv
   directly; do not read determinism_identical."*
2. `analysis/classify_three_class_matched.py:189`, which named its own output field
   `determinism_identical_FLAG_DO_NOT_TRUST`.
3. `docs/R6_A2_REPEATS_AND_JOBB_MEASURED_2026-08-18.md` section 1a.

Different files, different authors, different dates, different methods. That is corroboration. It
still does not substitute for re-measuring the repeats, and I have not.

---

## 10. What breaks if someone regenerates the artifacts

Nothing here has been regenerated. If someone does, **read this first.**

1. **`data/all_runs_inventory.csv` changes its header.** Column 13 goes from
   `determinism_identical` to `hull_load_identical` and its sha changes from
   `9c3cf047682855052e89102c6f548fb1c1c4133e840670bb128a7eb0c83d6a41`. Every reader inside this
   branch accepts both. **Readers outside this branch are the hazard**: the three
   `deliverables/*/make_poster_figures_accessible.py` copies still do a bare
   `r["determinism_identical"]` subscript and will raise `KeyError`, not degrade quietly.
2. **Every `summary.json` regenerated by the patched driver loses the old key.** There are 40+
   carrying it across `renders/`, `render_s2/`, `data/g128_*`, `data/g128_canonical_*`,
   `data/rogue_silverado_sweep_*`, plus 9 `data/*.csv`. A partial regeneration produces a
   **mixed-key corpus**, which the both-key readers handle but which makes any future count of
   "how many runs carry the flag" scope-sensitive all over again.
3. **`gates_results_all_runs.json` would change key name** and could lose the meaning of its 3
   `"ABSENT"` records if section 7.1 is not applied first. Apply 7.1 before regenerating anything
   that runs `gates_all_runs.py`.
4. **A regenerated figure is not a regenerated poster.** `deliverables/poster/build_poster.py`
   carries its own caption and scope text and is untracked. Re-running `make_poster_figures.py`
   fixes the figure PDFs and leaves the poster's own text false.
5. **Regenerating does not unpublish.** `public_release/Cerrell_TACC_42x56.pdf` is already on a
   public remote. Rebuilding it locally changes the working tree, not what GitHub has served.

**The largest risk is a well-meant "just regenerate everything to make it consistent" pass.** It
would rewrite the as-ran record, break three out-of-branch readers with a `KeyError`, and still
leave the poster text wrong.

---

## 11. Items for other slots, not actioned here

- **For `d7-register`:** `docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` around line 794 lists
  `` `determinism_identical` is **true** on all three `` as one of *"three independent resolution
  gains"* at g128 (**read directly**). The corrections authority is itself reading the flag as
  evidence of a resolution gain, which is the exact misreading this rename exists to prevent.
  Flagged, not edited.
- **For whoever owns `deliverables/`:** the six pattern-C defect sites and the nine pattern-B
  sites in the three `make_poster_figures_accessible.py` copies. Errata text is in section 1.4.
- **For whoever owns `scripts/`:** the `DETERMINISM ` stdout anchor token is still the misleading
  word. Changing it requires updating the three anchored `grep -E` captures in the same commit.
- **For Josie:** whether to re-issue the poster (section 1.5).

---

## 12. A note on the frozen-worktree hazard, so nobody draws the wrong conclusion

This worktree's `CLAUDE.md` is **855 lines and so is the main checkout's**, so the usual
heading-diff shows no drift. **That is inheritance, not the hazard being gone.** This branch was
cut from `claude/add-ci-checks` after the 855-line version landed in commit `2c6a877`, so it
inherited it. Sibling worktrees launched from older bases still see 676 lines and are missing
whole sections. Do not conclude from a clean heading-diff here that the hazard has been fixed; it
has been avoided on this one branch by the choice of base commit.

---

## 13. Reproducing every count in this document

The enumeration is a Python `re` walk that prints each path and line, not a shell `grep`. The
shell `grep` in this environment wraps ugrep with `--ignore-files` and skips gitignored paths,
which would drop 13 of the 32 pattern-A sites without saying so.

```
python3 - <<'EOF'
import os, re
ROOT = "/Users/josie/can-it-ford"
SKIP = (".claude/worktrees", "third_party", "__pycache__", "/.git/")
PATS = {"A_field_name": r"determinism_identical",
        "B_caption":    r"all runs deterministic",
        "C_prose":      r"determinism record|bit-reproducible"}
for k, pat in PATS.items():
    rx = re.compile(pat); n = 0; files = set()
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

PDF text, which `strings` cannot see: section 1.2.

Driver identity:

```
shasum -a 256 /Users/josie/can-it-ford/renders/yaris_render_s1/sim_standing.py
# expected BEFORE this branch's change:
#   4696c3b2d39f4e28f9c49c9f96c5c28a786c237f19204cc32036f703277d10d9
```

### Two zsh traps that will waste your time in this repo

Both hit or tested live while producing this document.

1. **Never name a shell variable `path`.** In zsh `path` is tied to `$PATH`, so
   `path=public_release/Cerrell_TACC_42x56.pdf` destroys `$PATH` for the rest of the call and
   every external command then fails with "command not found" while builtins keep working. That
   reads as a broken tool rather than a broken variable name. Reproduced live this session. Use
   `pth`, `p`, anything else.
2. **The `$rev:$path` history-modifier trap did NOT reproduce here, and I checked rather than
   assuming.** A recorded note warns that zsh can treat the colon in `"$sha:$path"` as a `:s`
   history modifier, leaving git with a bare commit-ish that resolves happily and returns
   commit-level output with no error. Tested live against this repo: the literal, unbraced
   `"$rev:$pth"`, and braced `"${rev}:${pth}"` forms **all three** returned the same blob sha
   `168879947da7d271e0c17da28f8719c46ee57a68`, confirmed independently by `git ls-tree`. So the
   trap did not fire for this usage here. It costs nothing to brace it anyway, and the
   `ls-tree` then `cat-file blob <sha>` route in section 1.2 sidesteps the question entirely,
   which is why that is the route given.
