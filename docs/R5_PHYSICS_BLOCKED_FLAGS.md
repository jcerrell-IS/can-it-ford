# D4 BLOCKED FLAGS: two blockers, both needing a human, both about one minute of work

2026-08-17. Branch `claude/r5-physics`. Written per the dispatch protocol, which says to
try a genuinely different second approach, then a connector, and **only then** write a
named flag file and keep working on the rest of scope. All three steps are done for both
flags below.

Neither blocker is a difficulty. Both are "a machine cannot do this, a person can, quickly."

---

## FLAG-1: TACC socket cold for the entire session. Blocks ALL GPU work.

**Impact: every GPU item in D4's scope, which is the entire second half of both dispatch
options.** Nothing on this branch has run on a GPU.

**Evidence, checked live twice about 13 hours apart** (typed `tacc_alloc_status`, not
inferred):

```
jcerrell0629@vista.tacc.utexas.edu: Permission denied (keyboard-interactive).
```

**Why I cannot fix it:** TACC requires an interactive password plus a 6-digit token. The
`canford-tacc` MCP pools one SSH ControlMaster; it cannot answer a token prompt.

**Recovery, about 30 seconds:**

```
ssh vista          # enter password, then the 6-digit TACC token
```

That warms the ControlMaster and every queued job becomes fireable. Then:

```
bash simulation/r5_physics/prestage_jobs.sh --preflight   # costs nothing, verifies paths
bash simulation/r5_physics/prestage_jobs.sh --go A        # emits job A and its submit line
```

**Fire Job A first and never drop it.** It is ~45 s of compute, it is fused with the
repeat runs so startup is not wasted, and **it is the only item that converts a currently
INFERRED claim into a measurement**: whether `sweepV_g64_v0p5` flips STUCK to SLIDE at a
rolling-resistance floor friction. Pass criteria are fixed in advance in
`R5_PHYSICS_BATCH_MANIFEST.md`, including the mu = 0.30 arm logged INDETERMINATE
beforehand so no outcome can be narrated as agreement afterwards.

Do **not** use idev. Interactive historically burned 98.5 to 99.1% of Vista node-hours
with 95 of 184 runs ending in TIMEOUT. Everything is batch via `tacc_submit`.

---

## FLAG-2: two documents that are open access but unfetchable from this host

Both are **gold open access, CC-BY**. This is **not** a licensing or paywall problem. It is
host-level bot filtering, and a normal browser session gets both immediately.

### 2a. Kramer 2021 Supplementary Materials, the benchmark time series

```
https://www.mdpi.com/article/10.3390/en14020269/s1
```

**Impact:** this is **half of Option B's definition of done**. The scene is built, the
constants are read from Table 1, the pass criteria are fixed. Without the series the
comparison cannot be graded at all, only the self-consistency checks can.

Routes tried, all failed: MDPI article and `/pdf` (403); MDPI `/s1` (403, independently
reproduced by the coordinator); the scite full-text resolver (403); a search for a
third-party mirror on Zenodo, GitHub or figshare, and in the OES Task 10 community that
commissioned the benchmark (nothing found).

**Recovery:** open that URL in a browser, drop the archive beside the paper in
`/Users/josie/can-it-ford-refs/2026-08-16/`. Keep it **outside the repo**: the repo is
public and E8 is unresolved.

### 2b. Nihei 2025 corrigendum

```
doi:10.1016/j.rineng.2025.107527
```

**Impact:** gates every quantitative row in `R5_PHYSICS_BRAKE_STATE.md`. D1's source record
says "Do not treat the numbers below as final until someone with **publisher access** reads
the corrigendum."

**That wording overstates it and should be corrected.** Resolved live via scholar-sidekick
and scite: the corrigendum is **gold OA, CC-BY, publishedVersion**, and scite shows the
original carrying an editorial notice "has erratum" pointing at it. **No institutional
access is required.** Routes tried: ScienceDirect article page (403) and the scite resolver
(403), i.e. bot filtering again.

**Recovery:** open the DOI in a browser, save it beside the Kramer PDF.

---

## The general lesson, because it cost time three separate ways

**A licence status and a fetch status are different things.** Three documents this session
were recorded or assumed to be behind an access barrier when they were all openly
licensed and merely bot-blocked, and one of them (the DTU-hosted Kramer PDF) turned out to
be served fine by the publisher's *backend* while its *front end* refused. Record what
failed and from where, not "blocked".

## Meanwhile

Per the protocol I kept working on the rest of scope throughout. Everything Mac-only in
`R5_PHYSICS_WHAT_SURVIVES.md` was produced while both flags were open.
