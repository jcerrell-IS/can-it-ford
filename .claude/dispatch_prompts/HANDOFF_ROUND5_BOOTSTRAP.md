# BOOTSTRAP PROMPT — CAN IT FORD, ROUND 5
Paste this whole file as the first message of a fresh Claude Code session in
`/Users/josie/can-it-ford`. It is written to be self-sufficient: it assumes you
have read nothing and know nothing about the previous rounds.

---

## 0. WHAT YOU ARE DOING

You are the **coordinator** of a new tmux session running **four** dispatch
sessions plus a monitor. You will: build the session, read the research the
previous round failed to read, write four genuinely distinct dispatches, and
supervise them.

You are not doing physics yourself. Your job is orchestration, verification and
relay.

**Before anything else, run these three and read the output:**

```bash
cat /Users/josie/can-it-ford/.claude/dispatch_prompts/NIGHT_FINDINGS_2026-08-15.md
```
```bash
cat /Users/josie/can-it-ford/.claude/dispatch_prompts/RECONCILE_ROUND4_2026-08-15.md
```
```bash
cat /Users/josie/can-it-ford/.claude/tooling/INSTALL.md
```

Those three carry the verified findings, the reconciliation of 13 prior
sessions with its four lists (unpushed / resolved / still-open / dangerous
crossovers), and the tooling that exists.

---

## 1. THE SINGLE MOST IMPORTANT THING: THE RESEARCH WAS NEVER FULLY READ

The previous round read roughly **12 documents in full** out of about **400
research-shaped files**. It also **never searched for Elicit reports at all**.
Measured live 2026-08-15:

```
~/Downloads    55        ~/Documents   186
~/Desktop     117        ~/Claude       42        total ~400
```

### 1a. THE ELICIT GAP, and it is the worst one

Nobody looked. Two unique Elicit outputs exist (many duplicate copies):

**`Elicit - Flood-Crossing Tire–Ground Friction and Speed Evidence.bib`**, 7
entries, at
`~/Desktop/CAN_IT_FORD_MASTER_2026-07-26/05_REFERENCES/01_bibliographies/`.
It contains, unread by anyone:
- **"CFD Method Development for Simulating Water Fording for a Passenger Car"**,
  2021, doi `10.4271/2021-01-0205` — a **FIFTH** vehicle-fording simulation. The
  previous round narrowed the novelty claim on the basis of four; this makes five.
- **"Full-scale experimental assessment of passenger vehicle stability in
  flooding flow"**, 2025, doi `10.1016/j.rineng.2025.107189` — a **2025
  full-scale experiment**, newer than anything in the register.
- **"A numerical approach to understand the responses of passenger vehicles
  MOVING through floodwaters"**, 2022.
- **"Hydrodynamic effect on NON-STATIONARY vehicles at varying Froude numbers
  under subcritical flows"** — non-stationary is precisely the gap CLAUDE.md L-1
  records as unaddressed by every foundational study.
- **"Effects of Surface Anomalies and Tire Mechanics on ATV Tire Friction
  Coefficients"**, 1996, doi `10.4271/961000` — friction.
- Wasfy 2015 `10.1115/DETC2015-47142`, Martinez-Gomariz 2017.

**`Elicit - extract-results-review-5e368aae-....csv`**, **1,345 rows**, at
`.../05_REFERENCES/03_citation_provenance_notes/`. Its columns include:
`Depth-velocity threshold or critical depth reported for vehicle instability,
with units` and `Driving/propulsive force or rolling friction coefficient used
or measured`. **That is a structured extraction of 1,345 papers containing
exactly the two quantities this project argues about, and it has never been
opened.**

### 1b. TWO WHOLE DESKTOP TREES WERE NEVER OPENED

`~/Desktop/CAN_IT_FORD_MASTER_2026-07-26/` and `~/Desktop/_ARCHIVE_2026-07-26/`.
The previous round's "128 artifacts" figure came from a narrower search and is
an undercount. Do not inherit it.

### 1c. WHAT *WAS* READ, so you do not redo it

Fully read: `65474f37` (mu=0.55 provenance), `82c51733` (PLY loading),
`211aad60` (particle resolution / force convergence), `baa355db` (experimental
configuration table), `genesis_vs_mpmengine_fluid_research.md` (photoreal
pipeline, splashsurf), `UNDERMIND_FINDINGS_DEPLOYMENT_ORDER_2026-08-08.md`, and
the **paper catalogs** of the wall-penetration (16) and moving-rigid (44)
reports.

Read as summary only, catalogs NOT fully mined: the settling report (**68
papers**, only ~14 rows read), the multi-resolution report (**78 papers**,
summary only), the trustworthy-AI report (13, titles only).

**Reading the catalogs rather than the summaries is what surfaced four uncited
fording papers.** Two catalogs remain unmined.

### 1d. HOW TO FIND RESEARCH, ROBUSTLY

Artifacts are named `compass_artifact_wf-<8hex>-...md` **but many have been
renamed**. Never conclude a document is missing from one directory:

```bash
find ~/Downloads ~/Documents ~/Desktop ~/Claude -maxdepth 6 \( -iname '*compass*' -o -iname '*undermind*' -o -iname '*elicit*' -o -iname '*_CURRENT.md' -o -iname '*research*' -o -iname '*report*' \) -type f 2>/dev/null
```

**Use the `canford-corpus` MCP server instead** (see section 3). Its
`corpus_resolve` takes an 8-hex id and returns every readable copy.
`~/Downloads` intermittently returns `Operation not permitted` under macOS TCC;
last round that produced **five independent false "artifact missing" reports**.
A zero result from one root is a broken probe, not an absence.

---

## 2. TMUX SESSION AND THE AUTO-DISPATCHER — BOTH ARE BUILT

Do not hand-roll these. Run:

```bash
bash /Users/josie/can-it-ford/.claude/tooling/round5_launch.sh
```

It creates the four worktrees and branches, builds session `canford5` with
**one window per dispatch** (never tiled: 13 tiled panes on a 66-column client
was unreadable last round), and applies the full visual scheme:

- a distinct colour per dispatch (D1 blue, D2 orange, D3 green, D4 magenta)
  carried on the **pane border**, the **border title** and the **window-status**
  entry, so a glance at any of the three identifies the session
- `pane-border-lines heavy`, because a single-line border vanishes at small font
- `pane-border-status top` always on, showing `D# LABEL | branch | cwd`
- a status bar with the repo branch and clock, mouse on, 200k scrollback
- `bash round5_launch.sh --restyle` reapplies styling to a live session

Then start the follow-up engine in window 0:

```bash
python3 /Users/josie/can-it-ford/.claude/tooling/round5_autodispatch.py --watch
```

It polls every 90s and, for any session idle over 4 minutes, composes a
follow-up **from that session's own git state**: its branch, its real last
commit, its uncommitted files, its unpushed count, and **what its siblings just
committed so it is told what not to duplicate**. Every outgoing message is
sha256'd and a hash already sent to anyone is never sent again. Use
`--dry-run` first to read what it would say, `--status` for the table alone.

Sessions coordinate through an append-only board at
`/Users/josie/can-it-ford/.claude/state/round5_board.md`: read before starting a
unit, append one row when you finish one.

## 3. CONNECTORS AND CLAUDE CODE FEATURES TO USE

### MCP servers configured in `/Users/josie/can-it-ford/.mcp.json`
| server | use it for |
|---|---|
| **canford-corpus** | resolve/search/read the ~400 research files; `corpus_cited_status(doi)` answers "is this already cited in the repo?" |
| **canford-tacc** | Vista/LS6 with typed returns: `tacc_alloc_status`, `tacc_env_probe` (has `is_stub`), `tacc_submit` (auto-injects `--overlap` and detaches), `tacc_tail`, `tacc_gpu` |
| **scite** | verify every DOI before it is written as settled |
| **scholar-sidekick** | `verifyCitation` catches a REAL DOI paired with an INVENTED title, which `resolveIdentifier` cannot |
| **wolfram** | any physical parameter, unit conversion or equation before it becomes a claim |
| **deepwiki** | how a library actually behaves; treat its answer as a hypothesis and verify against source |
| **undermind** | authenticated as of 2026-08-15; query the six deep-research reports directly |
| **github** | PR/issue work; the repo is PUBLIC |

`elicit` (the MCP server, distinct from the Elicit *files*) currently fails on
its own schema: `tools[4].outputSchema.type` expected object. Vendor-side, not
fixable here.

### Subagents
- **physics-skeptic** — MANDATORY before finalising any percentage, force,
  verdict count or distance. If unavailable, mark the claim UNREVIEWED; never
  fake the review.
- **provenance-verifier** — for "does this trace to a primary source".

### Skills worth invoking
`provenance-audit`, `directory-provenance-audit`, `flood-mpm-debugging-reference`,
`mpm-technical-deep-reference`, `mpm-render-pipeline`,
`tacc-terminal-and-file-transfer`, `bug-triage-protocol`, `connector-router`.

### Hooks already live (do not rebuild)
10+ PreToolUse gates including `gate_destructive`, `gate_concurrent_write`,
`banned_phrase_guard` (blocks bulk staging), `pretooluse_git_commit_gate`
(runs `params_check.py`), plus `commit_autoapprove.py`, which **auto-approves a
path-limited commit of ≤8 safe files** so you are not clicking Yes 25 times.

### Other Claude Code features to use deliberately
- **`/clear`** between phases rather than letting a session pass ~70% context.
- **Plan mode** before any multi-file edit.
- **Background Bash** (`run_in_background`) for anything over ~2 minutes.
- **`dispatch_uniqueness.py`** — run it on your four dispatch files BEFORE
  sending. Identical assignments to N sessions is the failure the last round
  committed six times.

---

## 4. NON-NEGOTIABLE RULES

1. **The repo is PUBLIC.** Nothing pushes without Josie's explicit per-branch
   go-ahead. `pushcheck` first. `PUSH_OK=1` is required by a git hook.
2. **Never** `git add -A`, `git add .`, or `git commit -a`. Stage explicit
   paths; commit path-limited (`git commit -m msg -- path`). A shared index
   means a bare commit sweeps another session's staged work; this happened on
   2026-08-07.
3. **Writing to an absolute `/Users/josie/can-it-ford/...` path from inside a
   worktree lands in the MAIN checkout**, on a branch that is not yours. The
   monitor watches for this.
4. **Never edit `CLAUDE.md`, the register, or `sim_standing.py`** without saying
   so. `sim_standing.py`'s sha256 stamps every run.
5. **`grep` here is a ugrep wrapper that skips gitignored paths.** Use
   `/usr/bin/grep` for any absence or inventory claim.
6. **E8:** derived NCAC/CCSA hull geometry must not reach the public repo. Note
   the open exposure in section 5.
7. No em-dashes, anywhere.
8. State every number's settle length, N, and spread. See section 5.

---

## 5. STATE YOU ARE INHERITING

**Unpushed:** ~188 commits across 11 branches, all worktrees clean.
`pushcheck` passes on nine; **D1 is BLOCKED** on
`docs/FLAG_CREDENTIAL_EXPOSURE_2026-08-13.md`; D3's branch is DO-NOT-PUSH by
design. **Nothing is bundled** — `git bundle` is the cheap insurance and needs
no authorization.

**Open and unowned:**
- **The canonical Yaris hull is ALREADY PUBLIC** on `origin/main`:
  `vehicle_geometry_research/yaris_coarse_v1l_watertight.ply`, blob `46a9f730`,
  12,445,769 bytes, plus 3 more `.ply` and 15 rendered videos, while E8's
  licence question is UNRESOLVED. Deleting does not unpublish.
- **12 to 15 credentials, ZERO rotated.**
- The Zhao 2019 outflow BC **does not hold a level**; cause identified (Anura3D
  impose BCs at grid nodes, ours is particle-level), fix not implemented.
- Chrono **segfaults** on ingested terrain.
- `settle_frames=8` is still the shipped default and no artifact records it.
- Two uncommitted main-tree edits (`CLAUDE.md` +73, register +96) from a live
  session, versus D4's 22 unpushed register commits. **Sequence before either
  moves**, or one silently erases the other.

**Verified findings you must not re-derive:**
- `settle_frames=8` sits inside a ~100-frame ring and produced four false
  results; spread 6.07x→**1.94x**, gate ordering **inverted**.
- **CLAUDE.md item 5 SURVIVED** a 31-fold settle control. It is real.
- The at-rest gate is **tunable**: every resolution has a passing band, so a
  PASS is not validation. PPC-alone and band-alone are both refuted.
- A resolution ceiling sits between **n_grid 100 and 104**, i.e. dx **0.0906 to
  0.0942 m**, reproducible, time-growing. Never quote its ratio: the floor is a
  random variable spanning 0.52 to 1.69 m.
- Chrono `GetNormal` fails on **100% of vertex hits**, general not
  architecture-specific (x86 matched aarch64 to 3 s.f.).
- mu=0.55 is **not** an outlier: Martinez-Gomariz 2017 measured 0.52-0.62 by the
  same method. The gap is measured-versus-adopted. 0.3 was never measured;
  Bonham & Hattersley derived it from a braking coefficient of 0.5 reduced 10%
  sideways, 20% slip, 20% debris.
- Canonical runs sit at depth/dx **2.000**, matched-dx at **3.500**, both below
  the `H/dp >= 5` minimum-wave-capture heuristic.

**Machines:** Vista = aarch64 GH200, has real warpmpm and the ONLY
`set_sdf_pose`. LS6 = x86, has **no usable warpmpm**, use it for Chrono and
`pysplashsurf` (wheels exclude aarch64). `srun --jobid=` needs `--overlap` or
the step dies. Sockets need `ssh vista` / `ssh ls6` once per 8h.

---

## 6. THE FOUR DISPATCHES ARE WRITTEN

Paste each into its window after launching `claude` there. Verified mutually
distinct by `dispatch_uniqueness.py`; each names the files it owns and writes
nowhere else.

```
.claude/dispatch_prompts/round5/R5_D1_MINE_RESEARCH.md    the Elicit gap + 2 unmined catalogs
.claude/dispatch_prompts/round5/R5_D2_E8_CREDENTIALS.md   public hull licence + rotation list
.claude/dispatch_prompts/round5/R5_D3_SAFE_THE_WORK.md    bundle 188 commits + register collision
.claude/dispatch_prompts/round5/R5_D4_PHYSICS_GATE.md     grid-node BC or Kramer 2021 validation
```

Each carries an identical STANDING PROTOCOL block covering self-sufficiency
(find it yourself, via the connectors, rather than asking), claim discipline
(N and spread, settle length, physics-skeptic), git rules, and an instruction to
keep going after each unit rather than waiting to be prompted.

**Before sending anything of your own, read**
`/Users/josie/can-it-ford/.claude/tooling/ERRORS_AND_RESOLUTIONS.md`. It is the
complete ledger of what went wrong in rounds 3-4 and the mechanism that now
prevents each one. If you are about to do something it lists, stop.

## 7. HOW TO BEHAVE, learned the expensive way

The previous coordinator had every rule below written down and broke all of
them anyway. They are here because instructions alone did not work.

- **Never quote a single draw from repeats you ran.** Report N and spread.
- **Never estimate elapsed time.** Read `remaining` from `tacc_alloc_status`.
- **An import succeeding is not an environment working.** Check `is_stub`.
- **Relay a commit SHA, not a summary.** Two relays lost load-bearing
  qualifiers and were recoverable only from the source commit body.
- **Give each session its own work.** Broadcasting identical text to N sessions
  makes N agents duplicate one job.
- **A falsifiable control beats a plausible claim.** The best results of the
  last round were negative: PPC refuted, three non-monotone results dissolved,
  and item 5 survived — which is what made item 5 credible.
- **The human eye is an instrument.** Josie found the settle bug by watching a
  video and asking why the cars moved before the water arrived. No gate caught
  it. There is a Gradio frame reviewer at
  `/Users/josie/can-it-ford/.claude/tooling/frame_review_app.py`; use it and
  show her frames.
