# D4 BLOCKED FLAGS: two blockers, both needing a human, both about one minute of work

> **SUPERSEDED 2026-08-17 ~21:30 UTC. BOTH FLAGS ARE CLOSED. Do not act on this file
> without reading `R5_PHYSICS_BENCHMARK_UNBLOCKED.md` first.**
>
> - **FLAG-1 was already clear when it was written up as blocking.** A live typed command
>   returns `login1.vista.tacc.utexas.edu`, 627 SU, queue empty. No human ran `ssh vista`;
>   the socket simply warmed and nobody re-tested. **A blocker recorded once is not a
>   blocker now**, and the re-test costs one command.
> - **FLAG-2a is closed.** The supplementary archive is at
>   `/Users/josie/can-it-ford-refs/2026-08-16/energies-14-00269-s001.zip`, sha256
>   `04c4d78d...7623f`. It was fetched by driving a **real browser**, which the publisher
>   serves normally. Every earlier attempt used curl, WebFetch or a resolver, and MDPI
>   answers all three with 403. This file's own lesson needs the extra clause: **a fetch
>   status from an automated client is not a fetch status from a browser.**
> - FLAG-2b (the Nihei corrigendum) is **still open** and is the only one left. The same
>   browser route is the obvious next thing to try, and has not been.
>
> Clearing the flags was **not sufficient**. Two run-blocking defects sat behind them and
> are fixed in the same commit: job A pointed at a driver path that does not exist, and
> jobs B and C ran a file that had never been staged to Vista. Neither was caught because
> `--preflight` echoed its checks instead of running them.

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

**UPDATED 2026-08-18 03:50. The browser route was attempted and the extension is
DISCONNECTED** (it worked earlier in the session, for the Kramer fetch, so Chrome has
since closed). Two genuinely different fallbacks were then tried and both failed, which
narrows the recovery rather than leaving it open:

- **There is no backend route, and this is the key difference from Kramer.** Unpaywall
  returns exactly **ONE** OA location for the corrigendum, the publisher DOI, with
  `pdfUrl: null` and no repository mirror. Kramer had **eight**, which is why its DTU
  *backend* served the file while its front end refused. **Do not spend time hunting a
  mirror for this one: there is not one.** A browser against the publisher is the only
  path.
- **scite has metadata but no full text** for either the corrigendum or the original, so
  the resolver trick that recovered Kramer's prose does not work here.

**Confirmed while trying, so the next attempt starts warmer** (all read live from scite):

| | value |
|---|---|
| authors | Yasuo Nihei, Shiho Onomura, Yoshinori Bando (three, not "et al.") |
| original | "Full-scale experimental assessment of passenger vehicle stability in flooding flow", Results in Engineering **28** (2025) 107189 |
| erratum link | the ORIGINAL carries `editorialNotices: has erratum -> 10.1016/j.rineng.2025.107527`, dated 2025-12-01, so the linkage is confirmed at the publisher and not inferred |
| ScienceDirect PII | original `S259012302503244X`, corrigendum `S2590123025035820` |
| licence | both gold OA, CC-BY |

**Note the subject matter**: the original is a **full-scale experimental** study of
passenger-vehicle stability in flood flow, which is unusually close to this project's own
question. Whatever the corrigendum changes, it is worth reading properly rather than only
for the brake-state numbers it gates.

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

---

# FLAG-3, opened 2026-08-18 03:45 BST. Three items blocked, all needing a human decision.

FLAG-1 and FLAG-2a are closed (see the banner at the top). This is a NEW blocking state,
opened after the work they unblocked ran to its end. Entry point for everything below:
`R5_PHYSICS_HANDOFF_2026-08-18.md`.

## 3a. 65 commits held, unpushed. Needs Josie's per-branch go-ahead.

`claude/r5-physics` at `930f191`, worktree clean, 65 ahead of main, never pushed. The repo
is PUBLIC and the standing rule is no push without an explicit per-branch go-ahead. Nothing
in these commits is credential-bearing or geometry-bearing, but that is my assessment and
not a substitute for the go-ahead.

## 3b. The floor-BC bug: a real one-line fix with a real cost, and the cost is the decision

`FLOOR = 0.075` is **exactly 4 dx** at g64, and the plane kernel gates on
`dotproduct < 0.0` (`mpm_solver_warp.py:1955`), so **the node lying ON the floor plane
receives no boundary condition**. Consequences measured this session:

- 1.829 cm of the 7.16 cm free-surface drop
- ~7.4% of the water leaves the domain by frame 299 (4.93% below floor, 2.5% outside
  walls), so **every job B number was measured in a leaking tank**

**Why I did not fix it.** Changing `FLOOR` changes the scene, which invalidates
comparability with every run produced tonight: the g64/g96 comparison, the band sweep, and
the retro-corrected values. That is a deliberate trade, not an oversight, and it is Josie's
call rather than mine: fix it and re-run the chain, or keep comparability and carry the
leak as a stated limitation.

**Note the interaction if it is fixed:** `WALL = 0.100` is 5.333 dx at g64 but exactly
8.000 dx at g96, so the two resolutions do not have identical tank footprints (+2.48% at
g96) independently of the floor. Fixing one without the other leaves a cross-resolution
confound.

## 3c. Job C has never run, and it is the actual mission

Everything in this branch's job B chain is a **self-consistency check against the scene's
own closed form**, which is CLAUDE.md item 6's exact objection. **The external validation
the dispatch asked for is job C and it has not been attempted.** It is now fully gradeable
for the first time: `/s1` is on disk and reduced, giving measured first damped periods
**0.7869 / 0.8093 / 0.8671 s** (N=4 each, spreads 0.0010 / 0.0012 / 0.0029) and per-drop
tolerances **0.096 / 0.239 / 0.435 mm**.

**Why I did not run it.** Three GPU arms whose grading I could not review, at the end of a
session in which **four of four headline claims were overturned by adversarial review**.
Producing a fourth unverified result would have been worse than producing none.

## The rule this session earned

**On this branch the measurement has been reliable and the sentence written on top of it
has not.** Four audits, four overturned headlines, always the same mechanism: comparing
two quantities that were not the same thing. Whatever runs next, budget for the review
before the run, not after it.
