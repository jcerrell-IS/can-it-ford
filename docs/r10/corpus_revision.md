# Corpus revision: the research index covers 8 of 21 completed deep searches

Written 2026-08-20 by the corpus-engineer pass. Proposal only. Nothing in
`analysis/research_index.py`, `.claude/skills/research-corpus/SKILL.md` or
`data/` was edited by this pass. Every number below is tagged for how it was
obtained.

## 0. How each claim here was obtained

- **read-directly**: I ran the command or read the file in this session.
- **inferred**: derived from something I read, arithmetic stated inline.
- **relayed**: taken from another document, not independently re-derived.

The adversarial-review subagent is dead fleet-wide, per the standing note in
`CLAUDE.md` under the heading "THE ADVERSARIAL REVIEW PATH IS DEAD FLEET-WIDE,
2026-08-19". Nothing here has been through it. Treat every claim as
**UNREVIEWED**.

---

## 1. The searches that are missing, and what each one carries

### 1.1 The arithmetic

read-directly, `mcp__undermind__list_workspaces` and
`inspect_deep_searches(names=[])` on workspace
`17299f2a-8dc8-438b-8c84-5abf19395e2c`, 2026-08-20:

    21   deep searches in the workspace, ALL of them status=completed
     8   named in research_index.REPORTS
    13   reaching the index by no route at all

read-directly, `python3 analysis/research_index.py --stats` and a walk of
`data/research_corpus_index.json`, 2026-08-20:

    332  records in the index          (319 distinct normalised titles)
    222  with an abstract              (110 metadata-only)
     76  cited_in_repo
     43  cited_reader_facing
     60  with no DOI                   (57 carry a Semantic Scholar link, 3 carry no link)
     44  documents indexed             (39 on-topic; all are Claude artifacts,
                                        Perplexity reports, .bib or Elicit files)

**The skill's count of 19 completed searches is now stale.** It is 21, because
two more completed on 2026-08-19 after the skill was last written (read-directly
from the live listing).

**Correction to the skill's framing, measured:** the skill says the index "was
built from 44 documents that are Claude artifacts and Perplexity reports", which
is right, but it implies the deep searches were simply not exported. They largely
were. Six of the thirteen missing searches have a full Undermind markdown export
sitting on disk right now, and **two of those six are inside the canonical repo**
(read-directly, `/usr/bin/find`):

    /Users/josie/can-it-ford/docs/Dynamic_Vehicle_Traction_in_Floodwater.md
    /Users/josie/can-it-ford/vehicle_geometry_research/Simulation_Ready_Vehicle_Mesh_Assets.md

They are not read because `REPORTS` is a hardcoded list and neither path is in it.
`index_documents()` cannot pick them up either: `doc_type()` classifies any `.md`
that is not `compass_artifact*`, not under a path containing `perplexity`, and not
`elicit*` as `"document"`, and `index_documents()` then does
`if dt == "document" and not fn.startswith("compass_artifact"): continue`. An
Undermind export is structurally invisible to both paths (read-directly, builder
source).

### 1.2 The thirteen, with what each settles

Paper counts are read-directly: from the live workspace listing for the seven
that exist only in the workspace, and from `Paper Catalog (N papers)` plus a
`/usr/bin/grep -cE '^\| *[0-9]+ *\|'` row count on the export for the six that
have a file. The two agree wherever both are available.

#### A. Workspace-only, no export anywhere on disk (7 searches, 468 papers)

read-directly: `/usr/bin/find` across `~/Downloads`, `~/Desktop`, `~/Documents`
returned no export for any of these seven. This is a partial view (it did not
walk the whole home directory or any remote machine), so state it as "none found
in those three trees", not "none exists".

| search | completed | papers | bears on |
|---|---|---|---|
| free surface elevation estimator error in particle method buoyancy validation | 2026-08-19 | 88 | the 35 to 64 percent buoyancy excess, and specifically whether the error is in the DENOMINATOR |
| moving vehicle floodwater simulation open source implementations | 2026-08-19 | 105 | the safe-speed surface, moving-body coupling, reusable open-source code |
| how computational researchers audit and defend simulation credibility | 2026-08-18 | 92 | how to report a binary verdict from unconverged continuous quantities |
| MPM SPH buoyancy force overestimation and hydrostatic validation benchmarks | 2026-08-18 | 32 | the same buoyancy failure, from the force side |
| GPU particle solver portability scaling and surrogate fidelity | 2026-08-18 | 56 | Vista vs LS6 solver choice, aarch64, GNS surrogate fidelity |
| which realism effects change a flood vehicle stability verdict | 2026-08-18 | 47 | where to spend the remaining allocation |
| moving vehicle floodwater GPU particle simulation | 2026-08-18 | 48 | moving-vehicle prior art and how motion was actually solved |

Live questions each one already answers, quoted from the search's own summary
(read-directly from `inspect_deep_searches`; the underlying papers are **relayed**,
none re-checked against a primary source by me):

**free surface elevation estimator error (88 papers).** This is the only search in
the workspace aimed at the buoyancy overestimate as a measurement artefact rather
than a solver defect. Its summary splits the excess into three separable channels
(surface reconstruction, pressure/hydrostatics, body-boundary coupling) and names
a cheap discriminator that needs no GPU: recompute elevation with nested exclusion
radii including zero, plus a body-off hydrostatic run to get the estimator bias
independently of body loading. Papers: `[Sch19e]` Schulz and Sutmann image-particle
boundaries, `[Kra21b]` Kramer floating-sphere benchmark, `[Neg22]` and `[Neg22b]`
on verifying SPH boundary conditions, `[Zha22d]` on circumventing volumetric
locking, `[Val15b]` solid wall models for WCSPH. Bears directly on the memory note
"[Two force accessors differ by a factor of two]" and on the sphere-heave work.

**MPM SPH buoyancy force overestimation (32 papers).** Independent origin from the
one above (different goal text, different date, 32 vs 88 papers, only partial
paper overlap), so the two do corroborate rather than restate. Its summary states
that the supplied studies do **not** establish a universal 50 percent bias and do
**not** show that velocity-projection impulse exchange intrinsically double-counts
gravity, which is a hard negative against a hypothesis this project has entertained.
Names `[Kra21b]` as the most reproducible published floating-body benchmark, with
experimental uncertainty about 0.3 percent of drop height, and flags that it is a
**motion** benchmark and carries no stated static-force tolerance. That last point
matters: the project has been grading a static force against a motion benchmark.
PDF availability measured on this search: **7 of 32 papers have a retrievable PDF**
(read-directly, counted from the `PDF ✓` / `PDF X` column over all 32 rows).

**which realism effects change a flood vehicle stability verdict (47 papers).**
Answers the allocation question outright. Effects with threshold evidence: bed
friction `[Smi19]`, road slope and flow orientation `[Mil20, Kra16, Sha19d]`,
watertightness `[Kra16, Boc19]`. Effects with **no** demonstrated verdict shift:
air entrainment, spray, surface tension, turbulence closure, reduced sound speed,
and outlet boundary choice. It states plainly that the ten-times-flow-speed sound
speed rule has no primary derivation in the retrieved literature, and that no
retrieved study quantifies a crowned or cambered road against a flat plane. This
is the single highest-value missing search for deciding what to run next, and it
also supplies `[Zha19e]`, the Zhao 2019 in/outflow BC paper this project already
treats as canonical.

**moving vehicle floodwater GPU particle simulation (48 papers).** Contains
`[Lyu23]` at relevance 1.48, the entirely particle-based 3D SPH vehicle wading
model that `CLAUDE.md` (heading "A NOVELTY CLAIM IN THIS PROJECT'S OWN TOOLING
CORPUS IS REFUTED") uses to refute the first-of-kind claim, plus `[Zha23h]` 3D
large-scale SPH vehicle wading with GPU acceleration. Neither DOI is in the index
(inferred: the index has no route to this search). Separates prescribed-motion
from solved-motion work and names `[Was15, Paz16, Maz18, Can18]` as the solved
group, with `[Can18]` explicitly open-source.

**moving vehicle floodwater simulation open source implementations (105 papers).**
The largest of the seven. Directly addresses the gap recorded in memory as
"[The AV safe-speed surface is the open gap]": its summary confirms that the
moving-vehicle studies still reduce stability to thresholds and produce **no
continuous safe-speed surface** resolving vehicle speed independently of current
velocity. Also states that a **body-following refinement window appears
unreported** and that body-fixed formulations are established for Eulerian
immersed-boundary and level-set solvers `[Yan09, Yan10]` but not for MPM. Names
reusable code: DualSPHysics `[Cre15]`, Chrono DVI coupling `[Can18, Maz18]`,
OpenFOAM FloatStepper `[Roe23]`, sdfibm `[Zha20o]`, IBAMR `[Bha19]`.

**GPU particle solver portability scaling and surrogate fidelity (56 papers).**
Bears on the memory note "[Chrono builds on GH200]" and on the standing engine
decision. Two findings that cut against current project text: the retrieved
literature **neither confirms nor refutes** that DualSPHysics is intrinsically
x86-only today, so the standing "hard aarch64 blocker" claim in `CLAUDE.md` under
the August 5 literature heading is not supported by this search either way; and
**no cited surrogate work preserves a discrete threshold**, only trajectory error
(GNS at about 5 percent trajectory error on granular problems), which is decisive
for whether a surrogate can carry a FORD verdict. Also: no cited study reports the
same vehicle case in both MPM and SPH, so cross-code agreement has no published
prior for a spread.

**how computational researchers audit and defend simulation credibility (92
papers).** The V&V spine the paper's Methods and Limitations sections need:
`[Obe02b, Roy11, Rie20, Cel07, Roy10, Oli12, Har17]`. States that Richardson and
GCI are defensible only in an asymptotic regime and that a nonmonotone result
should be reported as numerical uncertainty rather than reduced to significant
figures, which is exactly the g48/g64/g96 situation. Also states cross-architecture
agreement is evidence of robustness, **not** physical validity, which bears on the
LS6 reproduction work.

#### B. Export exists on disk, still not ingested (6 searches, 312 catalog rows)

| search | papers | export location | in repo? |
|---|---|---|---|
| Quantitative Flood Traversability Connections | 82 | `~/Downloads/Quantitative_Flood_Traversability_Connections.md` | no |
| Physics Simulation Validation Protocol | 81 | `~/Downloads/Physics_Simulation_Validation_Protocol.md` | no |
| Small Data Physics Surrogates at 36 Conditions | 47 | `~/Downloads/Small_Data_Physics_Surrogates_at_36_Conditions.md` | no |
| Dynamic Vehicle Traction in Floodwater | 43 | `docs/Dynamic_Vehicle_Traction_in_Floodwater.md` | **YES** |
| Simulation Ready Vehicle Mesh Assets | 36 | `vehicle_geometry_research/Simulation_Ready_Vehicle_Mesh_Assets.md` | **YES** |
| Optical Vehicle Collision Geometry | 23 | `~/Downloads/Optical_Vehicle_Collision_Geometry.md` | no |

**These six parse with the existing parser, unchanged.** read-directly: I imported
`research_index` and called its own `parse_report()` on all six. Every export uses
the identical Undermind layout the parser already targets: `## Paper Catalog (N
papers)`, the six-column table `| n | year | cit/yr | Title ([link](url)) |
authors | journal |`, then `### Paper Details` with headers of the form
`1\. · 100% match · 2019 · 5.6 cit/yr\`. Measured dry-run result:

    slug                 parsed  abstracts  with_doi  doi_new_to_index
    vehicle-traction         43         31        34                11
    vehicle-mesh             36         34        21                15
    validation-protocol      81         46        74                50
    traversability           82         45        77                72
    surrogates-36            47         45        42                40
    collision-geometry       23         22        20                19

    union of the six          292 records
    keys not already in index 240
    NEW DOIs not in index     196
    no-DOI records among them  44

inferred: adding these six to `REPORTS` takes the index from **332 records to
572**, a 72 percent increase, from a six-line edit to one constant and no parser
change. Reproduce with `/private/tmp/.../scratchpad/dryrun.py`, or re-derive by
importing `research_index` and calling `parse_report(slug, path)` per file.

What each of the six settles, from its own summary (read-directly from the export
files; the papers themselves are **relayed**):

- **Quantitative Flood Traversability Connections (82).** Frames the pipeline as a
  calibrated probabilistic link-performance model rather than a binary closure
  rule, giving `P[LS | h, v, slope, vehicle, t]`. This is the framing the
  `probabilistic_verdict.py` work already reaches by a different route, so it is
  corroboration with a separate origin. Also carries the 40 to 50 percent
  unsteady-drag figure the project cites as Azhar.
- **Physics Simulation Validation Protocol (81).** Overlaps the credibility search
  above but from July, and it is asymmetric on the verdict: a FORD claim requires
  validated six-DOF outcomes and a conservative margin, whereas a NO-FORD claim may
  be issued whenever uncertainty spans or exceeds the boundary. That asymmetry is a
  direct defence of this project's published NO-FORD results and appears nowhere in
  the index. Has the highest new-DOI yield of the six by absolute count after
  traversability (50 new DOIs).
- **Small Data Physics Surrogates at 36 Conditions (47).** States the effective
  sample size is the 36 conditions, not the 90 frames or the particle count, and
  recommends a GP or kriging response surface with leave-one-condition-out rather
  than a trajectory-level GNS. Bears on `analysis/gp_surrogate.py`.
- **Dynamic Vehicle Traction in Floodwater (43).** The traction closure: buoyancy
  reduces normal load, drag and rolling resistance set the demand. Full-scale
  anchors `[1]` Smith 2019 and `[10]` Smith 2017, coupled CFD-MBD closure `[3, 4]`.
  This is the search behind the memory note "[Moving-vehicle fork: the DOIs that
  matter]".
- **Simulation Ready Vehicle Mesh Assets (36).** The CCSA/NCAC finding, already
  transcribed into the skill. Its hard negative (no citable redistributable
  OBJ/PLY/glTF/USD conversion verified to exist) is a novelty-adjacent claim that
  should be re-checked before it enters the paper.
- **Optical Vehicle Collision Geometry (23).** Splat-to-collider provenance:
  appearance geometry, contact geometry and inertial parameters are distinct
  assets, and inertia errors materially affect 3D collision trajectories. Bears on
  item 4 of the August 4 ground truth (inertia is not wired, and should not be).

### 1.3 A defect this exposes in the current headline

read-directly, measured 2026-08-20. `repo_cited_dois()` treats `docs/` as
reader-facing and scans every `.md` in it. `docs/Dynamic_Vehicle_Traction_in_Floodwater.md`
is a raw Undermind dump carrying 34 DOI strings. Recomputing the reader-facing set
with that one file excluded:

    43   papers currently flagged cited_reader_facing
    34   still flagged with the raw dump excluded
     9   whose ONLY reader-facing route is that raw dump

The nine: `10.1016/j.jfluidstructs.2015.06.010`, `10.1016/j.oceaneng.2022.111607`,
`10.1115/1.4064971`, `10.1115/detc2018-85006`, `10.31436/iiumej.v22i1.1502`,
`10.4028/www.scientific.net/amm.592-594.1210`, `10.4271/2010-01-0770`,
`10.4271/2021-01-0252`, `10.4271/2022-01-0768`.

So the headline "43 of 332 reach a reader-facing document" is inflated by 9: those
nine reach a search dump that happens to live in `docs/`, not any prose a reviewer
would read. The honest ladder is **34 reaching written project prose, 43 counting
the raw dump, 3 actually printing in the paper**. This does not make the field
wrong, it makes the label wrong, which is the same failure the skill already
records for `cited_in_repo` versus `cited_reader_facing`.

### 1.4 A second defect, unrelated to the deep searches

read-directly. `parse_report()` opens with
`if not os.path.isfile(path): return {}`. Seven of the eight current `REPORTS`
paths live under `~/Downloads`, and **zero** live inside the repo. All eight
resolve today (verified 2026-08-20). But if any one goes missing or `~/Downloads`
returns EPERM, `--build` writes a smaller index and prints a smaller
`papers_per_report` count with no error and no non-zero exit. The module docstring
claims the design survives "a macOS privacy denial on `~/Downloads`", and that is
true of the **query** path only, never of `--build`. This is the same silent-zero
shape as the memory note "[TCC block makes recursive search return zero]".

---

## 2. Adding an MCP-sourced ingest path, at diff level

### 2.1 The constraint, stated plainly

`analysis/research_index.py` is pure standard library (`argparse`, `json`, `os`,
`re`, `sys`) and runs as `python3 analysis/research_index.py --build` in a plain
shell. **It cannot call an MCP connector.** MCP tools are available only inside an
agent turn, not to a subprocess. Any design that has the builder "fetch from
Undermind" is not implementable as written.

So the practical architecture is a **two-phase, connector-out-of-band** one:

    phase 1  (agent turn, has MCP)   inspect_deep_searches  ->  data/deep_searches/<slug>.json
    phase 2  (plain shell, no MCP)   research_index.py --build reads that directory

This mirrors the design choice the builder already documents for `~/Downloads`:
fetch once, commit the artifact, never make the query path depend on a fragile
source.

### 2.2 Immediate zero-risk fix, do this first

Six lines added to the `REPORTS` constant. No parser change, no schema, no new
directory. Verified by dry run to yield 240 new records.

```diff
 REPORTS = [
     ("wall-penetration", f"{DL}/Quantitative_MPM_Wall_Penetration.md"),
     ("trustworthy-ai", f"{REU}/Trustworthy_AI_Assisted_Scientific_Simulation.md"),
     ("moving-rigid-body", f"{DL}/Moving_Rigid_Body_Free_Surface_Validation.md"),
     ("validated-coupling", f"{DL}/Validated_MPM_Vehicle_Water_Coupling.md"),
     ("settling-force", f"{DL}/Settling_and_Force_Reporting_in_Free_Surface_Flow.md"),
     ("mpm-verification", f"{DL}/MPM_Simulation_Verification_Provenance.md"),
     ("multi-resolution", f"{DL}/Multi-resolution_MPM_for_Large-domain_Flooding.md"),
     ("reliable-ai", f"{DL}/Reliable_AI_Scientific_Software.md"),
+    # Six completed deep searches whose exports were already on disk and which
+    # no route reached. Two are inside the repo. Dry-run 2026-08-20: 292 records
+    # parsed, 240 keys new, 196 DOIs new. Parser needed no change.
+    ("vehicle-traction", f"{REPO}/docs/Dynamic_Vehicle_Traction_in_Floodwater.md"),
+    ("vehicle-mesh",
+     f"{REPO}/vehicle_geometry_research/Simulation_Ready_Vehicle_Mesh_Assets.md"),
+    ("validation-protocol", f"{DL}/Physics_Simulation_Validation_Protocol.md"),
+    ("traversability", f"{DL}/Quantitative_Flood_Traversability_Connections.md"),
+    ("surrogates-36", f"{DL}/Small_Data_Physics_Surrogates_at_36_Conditions.md"),
+    ("collision-geometry", f"{DL}/Optical_Vehicle_Collision_Geometry.md"),
 ]
```

**Before applying:** copy the four `~/Downloads` exports into
`data/deep_searches/raw/` and point `REPORTS` at the in-repo copies instead.
Leaving them in `~/Downloads` reproduces the silent-zero risk of section 1.4 four
more times. Do not delete the `~/Downloads` originals in the same pass; per the
standing "Before any destructive action" rule, confirm the copies are
byte-identical first with `cmp`.

### 2.3 The JSON ingest path, for the seven with no export

**New directory**, committed:

    data/deep_searches/
        _manifest.json              one row per completed search in the workspace
        <slug>.json                 one file per search, the ingest payload
        raw/                        optional, the markdown exports where they exist

**Schema for `<slug>.json`.** Deliberately a superset of what `parse_report()`
already produces per record, so the merge in `build()` needs no special case:

```json
{
  "schema": "canford.deep_search.v1",
  "slug": "which-realism-effects-change-a-flood-vehicle-stability-verdict",
  "name": "which realism effects change a flood vehicle stability verdict",
  "workspace_id": "17299f2a-8dc8-438b-8c84-5abf19395e2c",
  "status": "completed",
  "completed_at": "2026-08-18T04:56Z",
  "exported_at": "2026-08-20",
  "exported_by": "mcp__undermind__inspect_deep_searches",
  "n_papers_reported": 47,
  "goal": "...verbatim research goal...",
  "summary": "...verbatim summary of results...",
  "papers": [
    {
      "cite_key": "Smi19",
      "title": "Full-scale testing of stability curves for vehicles in flood waters",
      "year": "2019",
      "doi": "10.1111/jfr3.12527",
      "link": "https://doi.org/10.1111/jfr3.12527",
      "authors": "Grantley P. Smith, B. Modra, S. Felder",
      "journal": "Journal of Flood Risk Management",
      "cit_per_year": "5.6",
      "abstract": "",
      "relevance": 1.45,
      "pdf_available": false
    }
  ]
}
```

Two fields are new and both earn their place. `relevance` is Undermind's own
ranking and is not recoverable from the markdown export in a machine-readable
form. `pdf_available` is what decides whether `read_pdfs` can actually return
anything for that paper, and it is measurable at export time only.

**Builder changes.** Three additions, roughly 45 lines, no change to
`parse_report`, `tags_for`, `repo_cited_dois` or any query path.

```diff
 REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 INDEX = os.path.join(REPO, "data", "research_corpus_index.json")
+DEEP_SEARCH_DIR = os.path.join(REPO, "data", "deep_searches")
```

```diff
+def parse_deep_search_json(path: str) -> tuple[str, dict[str, dict]]:
+    """Ingest one MCP-exported deep search. Returns (slug, {key: record}).
+
+    WHY A FILE AND NOT A CONNECTOR CALL. This module is pure stdlib and runs in a
+    plain shell; MCP tools exist only inside an agent turn. A session that HAS the
+    connector writes these files; --build only ever reads them. That is the same
+    fetch-once-commit-the-artifact choice this module already makes for the
+    markdown reports, and for the same reason: the query path must not be able to
+    fail on a source it cannot reach.
+    """
+    with open(path, encoding="utf-8") as fh:
+        blob = json.load(fh)
+    if blob.get("schema") != "canford.deep_search.v1":
+        raise ValueError(f"{path}: unknown schema {blob.get('schema')!r}")
+    slug = blob["slug"]
+    recs: dict[str, dict] = {}
+    for i, p in enumerate(blob.get("papers", []), start=1):
+        doi = norm_doi(p.get("link", "")) or (p.get("doi") or "").lower().strip()
+        key = doi or f"{slug}#{i}"
+        abst = collapse(p.get("abstract") or "")
+        recs[key] = {
+            "doi": doi, "link": p.get("link", ""),
+            "title": collapse(p.get("title", "")),
+            "year": str(p.get("year") or ""),
+            "cit_per_year": str(p.get("cit_per_year") or ""),
+            "authors": collapse(p.get("authors") or ""),
+            "journal": collapse(p.get("journal") or ""),
+            "abstract": abst, "reports": [slug], "report_index": {slug: i},
+            "has_abstract": bool(abst),
+            "cite_key": p.get("cite_key", ""),
+            "relevance": p.get("relevance"),
+            "pdf_available": bool(p.get("pdf_available")),
+        }
+    # A declared count that does not match the rows is a truncated export, which
+    # is exactly the silent-zero shape this repo keeps being bitten by.
+    declared = blob.get("n_papers_reported")
+    if declared is not None and len(recs) != declared:
+        raise ValueError(f"{path}: {len(recs)} rows but n_papers_reported="
+                         f"{declared}; export is truncated, not merely short")
+    return slug, recs
```

Then inside `build()`, immediately after the existing `for slug, path in REPORTS`
loop and before `docs = index_documents()`:

```diff
+    if os.path.isdir(DEEP_SEARCH_DIR):
+        for fn in sorted(os.listdir(DEEP_SEARCH_DIR)):
+            if not fn.endswith(".json") or fn.startswith("_"):
+                continue
+            slug, recs = parse_deep_search_json(
+                os.path.join(DEEP_SEARCH_DIR, fn))
+            per_report[slug] = len(recs)
+            for key, r in recs.items():
+                if key in merged:
+                    m = merged[key]
+                    for s in r["reports"]:
+                        if s not in m["reports"]:
+                            m["reports"].append(s)
+                    m["report_index"].update(r["report_index"])
+                    if r["abstract"] and not m["abstract"]:
+                        m["abstract"] = r["abstract"]
+                        m["has_abstract"] = True
+                    for f in ("year", "authors", "journal", "cit_per_year",
+                              "link", "cite_key"):
+                        if not m.get(f) and r.get(f):
+                            m[f] = r[f]
+                else:
+                    merged[key] = dict(r)
```

The merge body is identical to the one already in `build()` for `REPORTS`. Factor
both into one `merge_into(merged, recs)` helper rather than duplicating it; the
diff is shown expanded only so the change is legible.

Finally, in the `--build` print block and in the returned dict, add:

```diff
+        "n_deep_searches_ingested": sum(1 for f in
+            (os.listdir(DEEP_SEARCH_DIR) if os.path.isdir(DEEP_SEARCH_DIR) else [])
+            if f.endswith(".json") and not f.startswith("_")),
```

### 2.4 Also fix the silent-zero, in the same pass

```diff
 def parse_report(slug: str, path: str) -> dict[str, dict]:
     if not os.path.isfile(path):
-        return {}
+        # Returning {} here USED to make a vanished source indistinguishable from
+        # a report with no papers. 7 of 8 REPORTS live under ~/Downloads, which
+        # has returned EPERM in this project before. Raise, and let --build's
+        # caller decide, rather than writing a smaller index with no error.
+        raise FileNotFoundError(f"REPORTS entry '{slug}' -> {path}")
```

and in `main()` under `--build`, catch it and exit non-zero with the slug named.
An index that is quietly 68 papers short is worse than a build that refuses.

### 2.5 The phase-1 export procedure, for whoever has the connector

Per search, one call, then one file write:

```
mcp__undermind__inspect_deep_searches(
    workspace_id="17299f2a-8dc8-438b-8c84-5abf19395e2c",
    names=["/<exact name>"],
    detail_level="full",        # 'full' is what carries the abstracts
    limit=50, offset=0)         # page until offset >= n_papers
```

Three traps, all read-directly from tool behaviour this session:

1. `limit` maxes at 50 and defaults to 20. A search with 105 papers needs three
   pages. A single unpaged call silently returns the top 20 and looks complete.
   The `n_papers_reported` guard in `parse_deep_search_json` is what catches this,
   which is why that guard raises rather than warns.
2. `detail_level` defaults to `compact`, which carries **no abstract**. Exporting
   at the default produces a metadata-only file that looks fine and tags badly,
   because `tags_for()` runs over title plus abstract.
3. DOIs are not in the paper rows at `compact` or `full`; they come from
   `get_paper_info(show_doi=true)`. The markdown export puts the DOI in the
   `([link](...))` cell, which is why `norm_doi()` exists. For a JSON export,
   either call `get_paper_info` or accept that some records land with a Semantic
   Scholar link and no DOI, which is already true of 60 of the current 332
   (57 of those 60 carry a Semantic Scholar link; only 3 carry no link at all,
   measured 2026-08-20).

---

## 3. Proposed replacement text for `.claude/skills/research-corpus/SKILL.md`

Apply this as the new head of the file, replacing everything from the
frontmatter through the end of the section currently headed
"# The project's own research is indexed. Query it before asserting."
Keep the rest of the existing skill (the established-facts sections, the method
families, the validation targets, the framing constraints, and the
`--query` warning at the end) unchanged, except for the two edits in 3.2 below.

### 3.1 New frontmatter and opening

````markdown
---
name: research-corpus
description: Query the project's own research index before making any method claim, novelty claim, citation, or "nobody has done this" statement, and before proposing a numerical method or a validation target. The index holds metadata only, no full text; reading a paper means read_pdfs against the Undermind workspace. Trigger on "has anyone done X", "is this novel", "what do we know about", "which paper says", "what should we cite", "how should we validate", "what method should I use", any DOI about to enter paper/ or docs/, any claim that a technique is untried, and before writing Methods or Limitations text. Also trigger before proposing a settle length, a convergence claim, or a verdict threshold.
---

# The index holds NO full text, and it covers 8 of 21 deep searches.

`data/research_corpus_index.json` stores **titles, authors, journals, years, DOIs
and, for some records, the abstract Undermind printed.** It stores **no full text
of any paper**, and it never has. Nothing you can learn from this index is
"reading the paper". **Reading a paper means `mcp__undermind__read_pdfs` against
workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c`**, and that only works where
Undermind actually retrieved a PDF or someone uploaded one; on the one search
counted in full on 2026-08-20, **7 of 32 papers had a retrievable PDF**. If no PDF
is available, say the paper is unread rather than paraphrasing its abstract as if
it were findings.

Measured live 2026-08-20, state the scope with any of these:

    332  records in the index, which are 319 DISTINCT WORKS
         (11 titles appear under 24 record keys, so 13 records are duplicates)
    222  carry an abstract; the other 110 are metadata-only, because each
         Undermind report details its top 50 only
     60  carry no DOI; 57 of those carry a Semantic Scholar link, 3 carry nothing
     76  have a DOI-shaped string somewhere in the tracked tree  (cited_in_repo)
     43  have one in paper/, docs/, deliverables/ or citations/  (cited_reader_facing)
     34  of those 43 survive excluding one raw Undermind dump that happens to
         sit in docs/; the other 9 reach a search dump, not project prose
      4  hold an entry in the SHIPPED bibliography
      3  are \cite'd and therefore print in the reference list

     21  deep searches completed in the Undermind workspace
      8  of them reach the index at all
     13  reach it by NO route, carrying 780 catalog rows between them

**"REACH" IS NOT "CITED" AND "IN THE INDEX" IS NOT "IN THE CORPUS".** Both
conflations have already been made and corrected in this project. A zero from
`research_index.py` is evidence about 8 searches out of 21, and about metadata
only. It is never evidence that the project has not researched something.

## Before you conclude the corpus is silent, do all three

1. `python3 analysis/research_index.py --method <tag>` and `--doi <doi>`.
   `--query` is a literal substring match over title and abstract ONLY, so it
   cannot match an author, a method tag, a journal or a DOI, and it is title-only
   for the 110 records with no abstract. Never report an absence measured with
   `--query` alone.
2. `mcp__undermind__inspect_deep_searches(workspace_id=
   "17299f2a-8dc8-438b-8c84-5abf19395e2c", names=[])` and read the goal plus
   summary of any search that looks relevant. Thirteen of the twenty-one are in
   no local file at all.
3. `mcp__undermind__read_pdfs` for anything you are about to quote a number from.

## The thirteen searches the index does not cover

Seven exist only in the workspace: free surface elevation estimator error in
particle method buoyancy validation (88 papers), moving vehicle floodwater
simulation open source implementations (105), how computational researchers audit
and defend simulation credibility (92), MPM SPH buoyancy force overestimation and
hydrostatic validation benchmarks (32), GPU particle solver portability scaling
and surrogate fidelity (56), which realism effects change a flood vehicle
stability verdict (47), moving vehicle floodwater GPU particle simulation (48).

Six have an export on disk that the builder does not read: Quantitative Flood
Traversability Connections (82), Physics Simulation Validation Protocol (81),
Small Data Physics Surrogates at 36 Conditions (47), Dynamic Vehicle Traction in
Floodwater (43, and it is committed at `docs/`), Simulation Ready Vehicle Mesh
Assets (36, committed at `vehicle_geometry_research/`), Optical Vehicle Collision
Geometry (23).

Full working, and the proposed ingest path: `docs/r10/corpus_revision.md`.

## The tool

`analysis/research_index.py`, pure standard library, reads the committed index at
`data/research_corpus_index.json`. It never touches `~/Downloads` on a query,
which has returned EPERM in past sessions and made a recursive search silently
report zero hits. **`--build` is a different matter: 7 of its 8 source paths live
under `~/Downloads` and a missing one currently returns an empty dict silently.**

```bash
python3 analysis/research_index.py --stats                    # method coverage
python3 analysis/research_index.py --method added-mass -v     # by method tag
python3 analysis/research_index.py --doi 10.1002/nme.7217     # one paper
python3 analysis/research_index.py --gaps --method validation-dataset
```

Status flags: `IN-PAPER` reaches a reader-facing directory, which is not the same
as printing in the paper; `repo-only` is somewhere in the tree; `UNCITED` is
neither. 25 method tags exist. Run `--stats` rather than guessing tag names.
Rebuild with `--build` only when a new report or deep-search export is added.
````

### 3.2 Two edits to the parts of the skill that stay

**a. The prior-art table.** The skill's line "Four prior vehicle fording or wading
simulations exist" understates it, and `CLAUDE.md` already records this under the
heading "AUGUST 15 2026, THE RESEARCH CORPUS IS NOW QUERYABLE FROM INSIDE THE
REPO" ("the deep-search layer puts it at eight or nine. Do not cite four."). Add
to the table, from `/moving vehicle floodwater GPU particle simulation`
(relayed, not checked against a primary source):

| Lyu et al 2023, entirely particle-based 3D SPH vehicle wading | `10.1016/j.compfluid.2023.106144` |
| Zhang et al 2023, 3D large-scale SPH vehicle wading, GPU accelerated | search cite key `[Zha23h]` |

and change the sentence to "At least eight prior vehicle fording or wading
simulations exist, and `paper/` cites none of them."

**b. The "Known limits of the index itself" section.** Replace the bullet
"**60 of 332 papers carry no DOI** and cannot be diffed" with: "**60 of 332
records carry no DOI.** 57 of those carry a Semantic Scholar id already sitting in
the `link` field and are identifiable that way; only **3** are unidentifiable.
Separately, 332 records are 319 distinct works." Add a bullet: "**The index covers
8 of the workspace's 21 completed deep searches.** Its silence is evidence about
those 8 only."

---

## 4. A check that goes RED when a completed deep search reaches the corpus by no route

### 4.1 What it is

Proposed path: `.claude/checks/corpus_reach_check.py`. Prototyped and **run** this
session at
`/private/tmp/claude-501/-Users-josie-can-it-ford/529261e9-9166-4d02-ad8e-e39c7d5fbf2c/scratchpad/proto/corpus_reach_check.py`.
Conventions match `count_claims_check.py` and `register_integrity.py`: exit 1 on
any BLOCK, exit 0 otherwise, and **fail open** on an unexpected exception per the
standing "Hooks must fail open" rule in the global instructions.

It reads a committed manifest, `data/deep_searches/_manifest.json`, and for every
search with `status == "completed"` asks whether ANY of three routes reaches it:

    REPORTS       the slug matches a REPORTS entry whose file EXISTS on disk
    json-ingest   data/deep_searches/<slug>.json exists
    documents     index_documents() actually returns a file with that basename

Route `documents` is computed by calling the builder's own `index_documents()`
rather than by assuming. Today it resolves to zero Undermind exports, and that is
a measurement, not an assumption.

Three further BLOCK conditions, because a check that only ever asks one question
passes for the wrong reason:

- `report-path-missing`: a `REPORTS` entry whose file does not exist. Catches the
  silent-zero of section 1.4 without waiting for the builder fix.
- `manifest-stale`: `refreshed_at` older than 14 days. Without this, a manifest
  nobody refreshes lets the check pass forever while new searches pile up. This is
  the failure this whole document is about, so the check has to be able to catch
  its own blind spot.
- `manifest-unreadable` / missing: BLOCK, not fail-open. "Cannot measure reach" is
  not "reach is complete". This is the one place the fail-open rule is deliberately
  overridden, and it is overridden narrowly: only for `ValueError` and `OSError` on
  the manifest itself. Everything else still exits 0 with a warning on stderr.

### 4.2 The input that makes it FAIL, named

**The manifest of the workspace as it stands on 2026-08-20, against `REPORTS` as
it stands on 2026-08-20.** Run this session against a manifest built from the live
`inspect_deep_searches(names=[])` listing:

    deep searches completed 21   reaching corpus 8   unreached 13
    BLOCK  deep-search-unreached: 'free surface elevation estimator error in particle
           method buoyancy validation' completed 2026-08-19T17:47Z with 88 papers and
           reaches the corpus by NO route
    ... 12 more ...
    EXIT=1

**The single narrowest input that trips it:** the deep search named
`free surface elevation estimator error in particle method buoyancy validation`,
completed 2026-08-19T17:47Z, 88 papers. It is not in `REPORTS`, no
`data/deep_searches/*.json` exists at all, and a `/usr/bin/find` across
`~/Downloads`, `~/Desktop` and `~/Documents` found no export of it. It fails all
three routes independently. Delete the other twenty rows from the manifest and the
check still exits 1 on that one row.

**Both arms were evaluated, per the memory note "[Both arms failed, reported as
agreement]".** A check that only ever prints RED is not evidence of anything:

| input | result | exit |
|---|---|---|
| live manifest, 21 completed, `REPORTS` as-is | 13 unreached, BLOCK | 1 |
| same manifest, 21 stub `<slug>.json` files present | 0 unreached, no finding | 0 |
| all 21 routes present, `refreshed_at` set to 2026-07-01 | BLOCK manifest-stale, 50 days | 1 |
| manifest file containing the bytes `not json` | BLOCK manifest-unreadable | 1 |
| manifest absent | BLOCK, "reach is unmeasurable" | 1 |

### 4.3 Source

```python
#!/usr/bin/env python3
"""RED when a COMPLETED deep search reaches the corpus by no route.

Exit 1 on any BLOCK, matching count_claims_check.py and register_integrity.py.
Fails open on an unexpected exception, per the standing hooks rule, with one
deliberate exception: an unreadable or missing manifest BLOCKs, because "reach is
unmeasurable" is not "reach is complete".
"""
from __future__ import annotations
import datetime, json, os, re, sys

REPO = os.environ.get("CANFORD_REPO", "/Users/josie/can-it-ford")
MANIFEST = os.environ.get("CANFORD_DS_MANIFEST",
                          os.path.join(REPO, "data", "deep_searches", "_manifest.json"))
INGEST_DIR = os.environ.get("CANFORD_DS_DIR",
                            os.path.join(REPO, "data", "deep_searches"))
STALE_DAYS = 14


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def builder_reports():
    sys.path.insert(0, os.path.join(REPO, "analysis"))
    import research_index as ri
    return [(slug, path, os.path.isfile(path)) for slug, path in ri.REPORTS]


def builder_document_paths():
    """Basenames index_documents() actually INGESTS, resolved live not assumed."""
    sys.path.insert(0, os.path.join(REPO, "analysis"))
    import research_index as ri
    return {os.path.basename(d["path"]) for d in ri.index_documents()}


def main() -> int:
    findings = []
    if not os.path.isfile(MANIFEST):
        print(f"BLOCK  no deep-search manifest at {MANIFEST}; corpus reach is "
              f"unmeasurable, which is not the same as complete", file=sys.stderr)
        return 1
    try:
        man = json.load(open(MANIFEST, encoding="utf-8"))
    except (ValueError, OSError) as exc:
        print(f"BLOCK  manifest-unreadable: {MANIFEST}: {exc}; reach is "
              f"unmeasurable, which is not the same as complete", file=sys.stderr)
        return 1

    reports = builder_reports()
    report_slugs = {slugify(s) for s, _, ok in reports if ok}
    report_file_slugs = {slugify(os.path.splitext(os.path.basename(p))[0])
                         for _, p, ok in reports if ok}
    for slug, path, ok in reports:
        if not ok:
            findings.append(("BLOCK", "report-path-missing",
                             f"REPORTS entry '{slug}' points at {path}, which does "
                             f"not exist; parse_report() returns {{}} silently and "
                             f"the papers vanish"))

    doc_basenames = builder_document_paths()
    ingest_slugs = set()
    if os.path.isdir(INGEST_DIR):
        ingest_slugs = {slugify(os.path.splitext(f)[0])
                        for f in os.listdir(INGEST_DIR)
                        if f.endswith(".json") and not f.startswith("_")}

    completed = [s for s in man.get("searches", []) if s.get("status") == "completed"]
    unreached = []
    for s in completed:
        sl = slugify(s["name"])
        routes = []
        if sl in report_slugs or sl in report_file_slugs:
            routes.append("REPORTS")
        if sl in ingest_slugs:
            routes.append("json-ingest")
        if any(slugify(os.path.splitext(b)[0]) == sl for b in doc_basenames):
            routes.append("documents")
        if not routes:
            unreached.append(s)

    for s in unreached:
        findings.append(("BLOCK", "deep-search-unreached",
                         f"'{s['name']}' completed {s.get('updated','?')} with "
                         f"{s.get('n_papers','?')} papers and reaches the corpus "
                         f"by NO route"))

    try:
        ref = datetime.date.fromisoformat(man["refreshed_at"])
        age = (datetime.date.today() - ref).days
        if age > STALE_DAYS:
            findings.append(("BLOCK", "manifest-stale",
                             f"manifest refreshed_at {man['refreshed_at']} is {age} "
                             f"days old (> {STALE_DAYS}); it cannot show a search "
                             f"launched since"))
    except Exception as exc:
        findings.append(("BLOCK", "manifest-undated",
                         f"refreshed_at unreadable ({exc}); staleness unmeasurable"))

    n_reached = len(completed) - len(unreached)
    print(f"deep searches completed {len(completed)}   reaching corpus {n_reached}"
          f"   unreached {len(unreached)}")
    for lvl, tag, msg in findings:
        print(f"{lvl}  {tag}: {msg}")
    return 1 if any(f[0] == "BLOCK" for f in findings) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                      # fail open
        print(f"corpus_reach_check: non-fatal internal error: {exc}", file=sys.stderr)
        sys.exit(0)
```

### 4.4 The manifest this check needs

`data/deep_searches/_manifest.json`, refreshed by a session with the connector.
The content as of 2026-08-20, read-directly from `inspect_deep_searches(names=[])`:

```json
{
 "workspace_id": "17299f2a-8dc8-438b-8c84-5abf19395e2c",
 "refreshed_at": "2026-08-20",
 "searches": [
  {"name": "free surface elevation estimator error in particle method buoyancy validation", "status": "completed", "updated": "2026-08-19T17:47Z", "n_papers": 88},
  {"name": "moving vehicle floodwater simulation open source implementations", "status": "completed", "updated": "2026-08-19T16:31Z", "n_papers": 105},
  {"name": "how computational researchers audit and defend simulation credibility", "status": "completed", "updated": "2026-08-18T05:42Z", "n_papers": 92},
  {"name": "MPM SPH buoyancy force overestimation and hydrostatic validation benchmarks", "status": "completed", "updated": "2026-08-18T05:11Z", "n_papers": 32},
  {"name": "GPU particle solver portability scaling and surrogate fidelity", "status": "completed", "updated": "2026-08-18T04:56Z", "n_papers": 56},
  {"name": "which realism effects change a flood vehicle stability verdict", "status": "completed", "updated": "2026-08-18T04:56Z", "n_papers": 47},
  {"name": "moving vehicle floodwater GPU particle simulation", "status": "completed", "updated": "2026-08-18T04:55Z", "n_papers": 48},
  {"name": "Moving Rigid Body Free Surface Validation", "status": "completed", "updated": "2026-08-14T14:28Z", "n_papers": 44},
  {"name": "Settling and Force Reporting in Free Surface Flow", "status": "completed", "updated": "2026-08-14T14:25Z", "n_papers": 68},
  {"name": "Quantitative MPM Wall Penetration", "status": "completed", "updated": "2026-08-14T14:20Z", "n_papers": 16},
  {"name": "Multi-resolution MPM for Large-domain Flooding", "status": "completed", "updated": "2026-08-14T14:21Z", "n_papers": 78},
  {"name": "Trustworthy AI Assisted Scientific Simulation", "status": "completed", "updated": "2026-08-08T02:33Z", "n_papers": 13},
  {"name": "MPM Simulation Verification Provenance", "status": "completed", "updated": "2026-08-07T23:30Z", "n_papers": 68},
  {"name": "Reliable AI Scientific Software", "status": "completed", "updated": "2026-08-08T02:25Z", "n_papers": 79},
  {"name": "Validated MPM Vehicle Water Coupling", "status": "completed", "updated": "2026-07-30T01:28Z", "n_papers": 60},
  {"name": "Simulation Ready Vehicle Mesh Assets", "status": "completed", "updated": "2026-07-21T10:38Z", "n_papers": 36},
  {"name": "Dynamic Vehicle Traction in Floodwater", "status": "completed", "updated": "2026-07-21T06:17Z", "n_papers": 43},
  {"name": "Small Data Physics Surrogates at 36 Conditions", "status": "completed", "updated": "2026-07-15T02:29Z", "n_papers": 47},
  {"name": "Physics Simulation Validation Protocol", "status": "completed", "updated": "2026-07-15T02:29Z", "n_papers": 81},
  {"name": "Quantitative Flood Traversability Connections", "status": "completed", "updated": "2026-07-15T02:21Z", "n_papers": 82},
  {"name": "Optical Vehicle Collision Geometry", "status": "completed", "updated": "2026-07-15T02:20Z", "n_papers": 23}
 ]
}
```

**Provenance of `n_papers`, and a round-trip result worth keeping.** Every
`n_papers` above is the WORKSPACE's own count, read-directly from
`inspect_deep_searches`, not from any local file. That distinction is load-bearing:
if the manifest took the count from a local export, a truncated export would
self-certify and the guard in `parse_deep_search_json` could never fire.

Measured 2026-08-20 as a control, the eight already-ingested searches:

    workspace count   44  68  16  78  13  68  79  60
    papers_per_report 44  68  16  78  13  68  79  60

All eight agree exactly. So the Undermind markdown export round-trips losslessly
at the catalog level through the existing `parse_report()`, on eight independent
cases. That is the evidence that ingesting the six on-disk exports of section 1.2B
is a faithful ingest rather than a hopeful one, and it was checked against the
workspace, not inferred from the parser agreeing with itself.

### 4.5 Wiring

Do **not** wire this as a PreToolUse hook. Per the standing "Hooks must fail open"
rule and the memory note "[Untracked .claude/tooling/ is a worktree landmine]",
a check that imports `analysis/research_index.py` will fail in any worktree whose
branch point predates that file. Wire it as:

- a step in the `audit-facts` skill, alongside the existing checks, and
- a CI job that is allowed to fail the build, **without** `continue-on-error`.
  The memory note "[count_claims_check false-BLOCKs on any tracked-only tree]"
  records that `canford-checks.yml` currently masks a failure that way. Before
  adding this check to CI, confirm it behaves in a tracked-only checkout: it reads
  only committed files (`data/deep_searches/`, `analysis/research_index.py`) plus
  the `REPORTS` paths, and those last are outside the repo, so **in CI the
  `report-path-missing` arm will BLOCK on all 7 `~/Downloads` entries.** That is
  correct behaviour and it is also why section 2.2 says to move the exports into
  `data/deep_searches/raw/` first. Do not add this check to CI before that move,
  or it will be red for a reason unrelated to deep-search reach and will be
  muted, which is how the last one got muted.

---

## 5. Order of application

1. Copy the four `~/Downloads` exports into `data/deep_searches/raw/`, verify with
   `cmp`, do not delete the originals.
2. Apply the `REPORTS` diff of 2.2, pointed at the in-repo copies. Rebuild.
   Expected: 332 to about 572 records. Verify against the dry-run figures before
   committing, and if they differ, the parser hit something the dry run did not.
3. Apply the `parse_report` raise of 2.4 and the `main()` catch.
4. Land `data/deep_searches/_manifest.json` and `corpus_reach_check.py`. It will
   be RED on the seven workspace-only searches. That is the point.
5. Export those seven to JSON per 2.5, apply the ingest path of 2.3, rebuild.
   Check goes GREEN.
6. Apply the skill text of section 3, with the counts re-measured **after** step 5,
   not copied from this document. Every count in section 3.1 is correct for
   2026-08-20 and will be wrong the moment step 2 lands.
