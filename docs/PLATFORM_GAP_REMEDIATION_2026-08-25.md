# Platform gap remediation: GitHub, Overleaf, Hugging Face, 2026-08-25

Live pass. Every claim below was produced by running a command against the live service or
the live tree in this session. HEAD `0845e1c` on `claude/add-ci-checks`.

**Tags**: [DONE] = executed and verified live. [STAGED] = built locally, awaiting a gated
push. [OPEN] = identified, not acted on. [CONFIRMED] = measured this session.

---

## 1. DONE and live on GitHub right now

### 1a. Repository description was the empty string

`gh repo view` returned `"description": ""`. The README's own line 3 was a perfectly good
description that had never been copied into the field GitHub actually renders in search
results, link previews, and the sidebar. **[DONE]**

Now live, 269 characters:

> Can a specific vehicle ford a flooded road? A three-level model ladder (depth threshold,
> AR&R hazard criterion, and coupled MPM water plus rigid-vehicle simulation on GH200/A100)
> with every verdict gated and reproducible. NSF SCIPE REU 2026, GeoElements Lab, UT Austin.

It deliberately does **not** claim a working reconstruct-to-decide front end, because there
is not one. See section 4.

### 1b. Repository topics were null

The repo was unfindable by GitHub topic search. **Twelve topics are now set** and verified
live: `civil-engineering`, `computational-fluid-dynamics`, `flood-modeling`,
`gaussian-splatting`, `gpu-computing`, `hpc`, `material-point-method`, `python`,
`reproducible-research`, `scientific-computing`, `simulation`, `vehicle-stability`. **[DONE]**

These were chosen to align with the tags the Hugging Face Space already carries, so the two
public surfaces describe the project the same way.

---

## 2. STAGED: `origin/main` publishes three false statements

**This is the largest single gap found.** `main` is the default branch, the repo is public,
and it is **471 commits behind** the working branch. Three statements it serves right now
are false, and all three are already corrected on the working branch. **[CONFIRMED]**

| # | What `main` says today | Reality |
|---|---|---|
| 1 | "**Gradio demo:** not yet deployed." | The Space returns **HTTP 200** and is live. The Vercel site is live and is already set as the repo homepage, while appearing nowhere in the README. |
| 2 | Dataset licence is **ODC-By-1.0** (`CITATION.cff:12`) | All Hugging Face repos advertise **cc-by-4.0**. `main` is the lone outlier, and it is the file a data-availability statement points at. |
| 3 | "uniform-box fallback (**no NHTSA-measured Yaris**)" | **A measured 2010 Yaris tensor exists**, on slide 7 of DOI `10.13021/G8JS5D`, the document this project already cites for its own hull provenance: 1078 kg; roll 388, pitch 1498, yaw 1647 kg m^2; CG Z 558 mm. |

Statement 3 is the one worth dwelling on. The repo asserts a measurement does not exist while
citing, for a different purpose, the very document that prints it. The corrected README keeps
the decision not to wire the tensor in, which remains right, but grounds it in the measurement
rather than in an absence.

**Built and waiting:** commit `30218a8` on local branch `fix/public-repo-accuracy`, parented
directly on `origin/main`. **[STAGED]**

```
 CITATION.cff           |   7 +-
 LICENSE                |  14 +++
 README.md              |  11 +-
 THIRD_PARTY_NOTICES.md | 323 +++++++++++++++++++++++++++++++++++++++++++++++++
 4 files changed, 350 insertions(+), 5 deletions(-)
```

Documentation and metadata only. No code, no data, no figures. It was assembled with git
plumbing against a temporary index, so the working tree was never checked out or switched and
no other session's files were touched.

It also carries two things `main` has never had: the **SCOPE clause** in `LICENSE`, separating
this project's own code from redistributed third-party material, and `THIRD_PARTY_NOTICES.md`,
the per-asset inventory recording **five UNRESOLVED assets** where no permission has been
established, headed by the CCSA/GMU finite-element vehicle models and the hull derived from them.

**Not pushed.** A push is gated by this project's own standing rule.

---

## 3. Hugging Face: no repair needed, and one of my earlier findings was wrong

**Verdict: the Hugging Face presence is the best-documented public surface this project has.**
No action taken and none required. **[CONFIRMED]**

| Repo | Type | Files | Contents |
|---|---|---|---|
| `can-it-ford` | Space | live gradio | verdict explorer, 6 topic tags, HTTP 200 |
| `can-it-ford-speed-surface` | dataset | 6 | 4 real CSVs, current data, 50 downloads |
| `can-it-ford-sweep-v1` | dataset | 2 | placeholder, no data, explicitly labelled |
| `can-it-ford-sweep-v1` | **model** | **39** | `manifest.csv` + **36 timeseries CSVs** |

**Correction to an earlier finding in `RESUME_EXTRACTION_2026-08-25.md`.** That document
briefly recorded the model repo as holding **0 files**. That was wrong and is withdrawn. The
probe omitted the `/models/` path segment, and an empty response from a malformed URL was read
as an empty repository. The repo holds 39 files. **A miss is not an absence until you know
what the predicate actually queried**, which is a rule this project already writes down.

The real structure is not an empty repo, it is a **repo-type mismatch**: the superseded
box-proxy sweep is published under a *model* repo while the identically-named *dataset* repo
is the empty one. Both are deliberately labelled, and both point readers to `speed-surface`.

Both cards were read in full and both are candid in a way that is worth keeping. The empty
dataset opens "This repository holds no data. Please read this before citing or fetching it,"
and explains it is retained rather than deleted "because it has accumulated downloads while
empty, and something on the other end of those requests would break silently if the name
disappeared." The model card names the box-proxy geometry, the two kept classes (1390 kg
sedan, 2300 kg pickup), the SUV that was run and dropped for an unphysical density, and what
superseded it. **Leave both alone.**

The only cosmetic gap: neither same-named repo mentions the other's existence. Both route to
`speed-surface`, so a reader is not misled, only mildly surprised. **[OPEN, low priority]**

---

## 4. Overleaf: two real citation defects

The canonical paper is `overleaf/main:conference_101719_1.tex`, 6,149 words, 17 sections,
7 figures, 15 bibliography entries, 14 distinct cite keys. **[CONFIRMED]**

### 4a. Five prior vehicle-fording works are cited nowhere. [OPEN, staged material]

Grepped both the tex and the bib for each DOI. **All five return zero hits.** [CONFIRMED]

| Work | DOI | In paper | In corpus |
|---|---|---|---|
| He et al. 2026, *J. Comput. Nonlinear Dyn.* | `10.1115/1.4071177` | **no** | yes |
| Wasfy et al. 2015, ASME IDETC | `10.1115/DETC2015-47142` | **no** | yes, tagged `vehicle-fording` |
| Khapane & Ganeshwade 2014, SAE | `10.4271/2014-01-0936` | **no** | yes |
| Al-Qadami et al. 2022, *J. Flood Risk Manag.* | `10.1111/jfr3.12828` | **no** | yes |
| Al-Qadami et al. 2023, *Sustainability* | `10.3390/su151713262` | **no** | yes |

This matters more than a normal citation gap because the paper's contribution is framed
around validation of a fording pipeline, and Al-Qadami et al. 2022 claim the first moving
full-scale vehicle simulation. A reviewer who knows this literature will notice its absence.

**Material prepared:** `paper/prior_art_additions.bib`. Every field is pulled from the live
Crossref record for each DOI, not hand-typed, and the file was normalised to pure ASCII
because the Crossref records carry an en-dash and four U+2010 hyphens that break pdflatex or
silently mangle the author names. **[STAGED]** Not pushed to Overleaf.

The prose to accompany them is not drafted. That needs the papers read, not just their
metadata resolved, and the corpus holds **no full text**.

### 4b. `xiong2024` is in the bibliography and cited nowhere. [OPEN]

15 bib entries, 14 cite keys, and the orphan is `xiong2024`. **[CONFIRMED]** BibTeX drops
uncited entries silently, so it does not print and causes no error, which is exactly why it
has survived. It is the box-proxy vehicle validation reference (Xiong et al. 2024, *Water
Resources Research*, `10.1029/2023WR036739`) that `README.md` still lists under Key citations.
Either cite it where the box-proxy lineage is discussed, or drop it from the bib.

### 4c. What is NOT a defect, checked and cleared

**The paper's solver attribution is correct, and notably careful.** Line 205 reads: "These 17
runs were executed with the Warp-based MPM solver `warpmpm` from `kks32/mpm-engine` (MIT), not
with Genesis; Genesis is the engine the Fig. 1 pipeline is designed around and the solver
behind the 9-condition pilot above, so the two should not be read as the same." A source
comment at lines 43 to 44 records that an earlier draft had credited Genesis for warpmpm runs
and that this was fixed. **[CONFIRMED]** The engine conflation this project guards against
does not exist in the current paper.

The figure caption is equally careful, marking the reconstruction stages "conceptual, not the
path used for any result reported here". The paper is honest about the unbuilt front end.

---

## 5. Other gaps found

| Gap | Detail | Status |
|---|---|---|
| CI does not protect the default branch | `.github/workflows/canford-checks.yml` is **absent from `origin/main`**. It runs on pushes from other branches (12 of 12 recent runs green) but nothing gates `main`. | [OPEN] |
| Two CI steps cannot fail the build | `register_integrity` and `count_claims` both carry `continue-on-error: true`. Both currently report 0 blocking defects, so the badge is honest today, but it would be green either way. | [OPEN, by design] |
| Stale pull requests | **#9** open since **2026-07-31**, roughly four weeks. **#15** open since 2026-08-18. | [OPEN] |
| Open issues | **#6** vehicle geometry unresolved; **#5** `DRIFT_THRESHOLD` hardcoded, unlinked to its citation reframing. | [OPEN] |
| Vista `/home1` near quota | **90.78 percent** used, 21.1 of 23.3 GB. `taccinfo` prints an explicit warning. A full home directory fails jobs in ways that look like solver bugs. | [OPEN] |
| Solver Poiseuille comparison never run | `tests/test_physics_gates.py` reports 11 pass, 1 skip, and prints "SKIPS ARE NOT PASSES". The analytical side is verified; the solver comparison is not. | [OPEN] |
| Zotero connector down | Three `zotero-mcp-server` processes run, but `localhost:23119` refuses because **Zotero desktop is closed**. MCP server healthy, backend absent. Opening the app fixes it. | [OPEN, trivial] |
| Leaked `github_pat_` | Printed into a session transcript earlier today when a redaction failed. Valid to **2026-11-20**, `repo` scope. Bounded to one token; that config holds exactly one secret. | [OPEN, rotate] |

---

## 6. What is still gated on a decision

Nothing in section 1 needs anything: it is live.

**One push decides section 2.** Commit `30218a8` either reaches `main` or it does not. Until
it does, the public default branch keeps serving a dead-demo notice, a superseded licence, and
a claim that a measurement does not exist while citing the document that prints it.

**Overleaf writes are separately gated.** `paper/prior_art_additions.bib` is ready to apply but
was not pushed, because the Overleaf remote shares no ancestor with this repo and a push there
overwrites rather than merges.
