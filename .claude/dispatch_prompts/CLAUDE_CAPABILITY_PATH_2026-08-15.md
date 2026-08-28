# MAKING CLAUDE BETTER AT THIS: WHAT THE RESEARCH SAID, WHAT GOT BUILT, AND WHAT LAST NIGHT PROVED IS STILL MISSING
2026-08-15. Sources: five Claude-about-Claude artifacts in `~/Claude/reu`, the
Undermind trustworthy-AI report, and direct observation of a 13-session fleet run
on 2026-08-14 into 08-15. Implementation status read live from `.claude/`.

---

## PART 0 — CREDIT FIRST: THE RESEARCH WAS ACTED ON

`2c1e05ae` named two failure classes and ranked fixes. Checked live today, most
of Tier 0 and Tier 1 exist:

| Recommended | Status |
|---|---|
| `params_check.py` consistency gate | **BUILT** `.claude/checks/params_check.py` |
| physics-skeptic adversarial subagent | **BUILT** `.claude/agents/physics-skeptic.md` |
| PreToolUse hooks that block on exit 2 | **BUILT** 10 PreToolUse hooks wired |
| Stop hook | **BUILT** 1 |
| SessionStart protocol injector | **BUILT** 2 |
| `.mcp.json` project-scoped | **BUILT** deepwiki, scite, wolfram, github |
| Skills in git | **BUILT** 13 skills |
| Slash commands | **BUILT** 6 |
| register integrity checker | **BUILT** `register_integrity.py` |
| provenance verifier | **BUILT** `.claude/agents/provenance-verifier.md` |

17 hooks across 7 events. So the honest starting point is: **Failure Class 1
(cross-surface desync) and Class 2 (undetected physics bugs) are substantially
addressed.** The remaining problems are not the ones the July artifacts were
written about.

---

## PART 1 — WHAT THE ARTIFACTS RECOMMENDED THAT IS STILL UNDONE

**1.1 GitHub Actions running the same checks as the hooks.** `2c1e05ae` Tier 1
asked for `params_check.py` in CI, not only in a local hook. A local-only gate
protects one machine. Vista's checkout has four modified tracked files including
`CLAUDE.md` and `failure_modes.py` and nothing checks them.

**1.2 The immutable per-run manifest.** The Undermind deployment order called
this "the single cheapest provenance win available, one field": does
`summary.json` record the git SHA of `sim_standing.py` **at the moment the run
executed**? Still unanswered. Last night added a second field that must be in it:
`settle_frames`. D11 `af9d293` measured that **no artifact records it**.

**1.3 Undermind is configured but NOT AUTHENTICATED.** It appears in this
session's auth-required list. Six deep-research reports exist as markdown that
must be grepped rather than queried.

**1.4 Metamorphic tests as standing gates.** Recommended as "none currently
exist". Last night one was built (the R7 mirror control) and it immediately found
a resolution ceiling **that no existing gate detects**. It is still a one-off
script in `$SCRATCH`, not a gate.

---

## PART 2 — THE FAILURE CLASS THE ARTIFACTS COULD NOT HAVE ANTICIPATED

Every artifact was written for a **single session**. Last night ran **thirteen
concurrent sessions plus a coordinator**. That produced failures with no
precedent in the research, all directly observed:

**F3a — Broadcast homogenization.** The coordinator sent byte-identical prompts
to 13 sessions six times. Josie diagnosed it before I did: *"now each session is
doing the same thing without regard to each other."* Thirteen agents duplicating
one another is worse than one agent, because it also consumes thirteen
confirmation queues.

**F3b — Relay degradation.** D4 recorded, twice, that a relayed finding lost its
load-bearing qualifier and was **"recoverable only by reading the source commit
bodies."** The coordinator relayed a causal claim ("removing the resolution
confound flips the verdict") that D5 then had to retract as false.

**F3c — Confirmation saturation.** Roughly 25 commit approvals were handled
manually. Each blocked one session for minutes while it sat at a Yes/No prompt.
Several sessions were idle at prompts for 15+ minutes. This was the single
largest source of lost session-time in the run.

**F3d — Single-point remote failure.** All 13 sessions multiplex one SSH
ControlMaster per host. At seven concurrent sessions the server began refusing
with `Session open refused by peer`, **every session lost LS6 simultaneously**,
and running `srun` steps died mid-flight after writing ~1.8 GB that was then
orphaned.

**F3e — Verification theatre.** The coordinator ran three repeats of g128
*specifically* to avoid a single-draw claim, then quoted a single ratio from
them. D4 `1cfa5e0`: *"The repeats were run correctly and then a single ratio was
quoted from them anyway."*

**F3f — A stub passing as a real import.** `import warpmpm` succeeded on LS6
against a **6-line file** whose body is
`raise RuntimeError("stub: solver not needed for the PLY format check")`. The
coordinator reported "environment verified, warpmpm OK" and told every session to
use that PYTHONPATH. D11's mirror run had already failed on it at 16:06 and
nobody read the log.

**F3g — Coordinator clock drift.** The coordinator advanced its own time estimate
across many tool calls without checking it, drifted ~1 hour, and time-boxed
sessions against a deadline that did not exist. The machine had the answer
(`squeue -o %L`) the whole time.

**F3h — Transient-as-converged.** The coordinator measured the mirror control
inside the very transient it had diagnosed an hour earlier, and reported it as a
finding. Three sessions had to retract it.

**The pattern under F3e, F3g and F3h is one thing:** the coordinator had the
correct procedure available, had *stated* it to others, and did not apply it to
itself. Nothing in the current hook set watches the coordinator.

---

## PART 3 — RANKED ENHANCEMENTS

### E1. A TACC MCP server. Highest ROI by a wide margin.

Today every cluster interaction is `scripts/tacc.sh` shelling out and parsing
text. Last night that cost, concretely: ~40 minutes of dead GH200 time before
`--overlap` was discovered; a whole-fleet LS6 outage from socket saturation; long
runs killed by a `TACC_TIMEOUT=60` default; and `squeue` re-parsed as text dozens
of times.

An MCP server fixes all four because it owns **one** connection pool and returns
**typed** results:

```
tacc_alloc_status(host)     -> {jobid, node, partition, remaining_s, su_balance, queue[]}
tacc_submit(host, cmd, partition, walltime, nodes, detach=True)
      -> auto-injects --overlap when a live idev is detected
      -> auto-wraps in setsid nohup ... </dev/null so a socket drop cannot kill it
tacc_poll(host, jobid)      -> {state, elapsed_s, remaining_s, node}
tacc_tail(host, path, n)    -> log tail without a full ssh round-trip
tacc_env_probe(host, module)-> {interpreter, version, source_file, source_lines, is_stub}
```

`tacc_env_probe` is the direct fix for **F3f**: it must assert the resolved
module's source file exceeds a minimum line count and exposes expected symbols,
so a 6-line stub reports `is_stub: true` instead of `OK`. That single field would
have saved several hours.

Connection pooling is the fix for **F3d**: 13 sessions calling one MCP server is
one SSH session, not seven competing ones.

### E2. A corpus MCP server.

128 research artifacts across four roots. Last night **five sessions
independently reported artifacts as unreadable** because each checked
`~/Downloads` only, while every one of those files existed in
`/Users/josie/Claude/reu/`. That is a five-instance false-negative class caused
purely by lookup method.

```
corpus_resolve(id8)          -> every readable path for an 8-hex artifact id
corpus_search(query, k)      -> title + section hits across all roots
corpus_read(id8, section)    -> a section, not a 3 MB whole-file read
corpus_cited_status(doi)     -> is this DOI already cited anywhere in the repo?
```

`corpus_cited_status` is the machine version of the gap that cost the most
scientific credibility last night: **four vehicle-fording papers sat in our own
catalogs, uncited, while the project was preparing to claim novelty.**

### E3. Predicate-based commit auto-approval.

`pretooluse_git_commit_gate.py` already exists. Extend it to auto-approve when
**all** of these hold, and prompt only otherwise:

- path-limited form (`git commit -m ... -- <paths>`) with no bare `-a`
- ≤ 8 staged files (matches the existing pre-commit hook)
- every path inside the session's declared scope, read from its dispatch file
- no path matching `\.(ply|obj|stl|npz|npy|env|key|pem|pth)$|secret|token|credential`
- `git status` column 1 shows nothing staged that this session did not touch

That converts ~25 blocking prompts into ~3 genuine ones, and it is strictly safer
than a human clicking Yes 25 times, because the predicate cannot get bored.

### E4. A dispatch-uniqueness gate.

Direct fix for **F3a**. Before a coordinator sends to N sessions, hash each
dispatch body. If any two hash equal, refuse and name the pair. A shared
*addendum* is legitimate; an identical *assignment* is the bug.

### E5. Claim-shape enforcement in the physics-skeptic agent.

Direct fix for **F3e**. Add to its checklist, as hard failures:
- a measured numeric claim must carry **N** and a **spread**, never a point value
- a **ratio** whose denominator is itself measured must report both terms
  separately (D4: *"the ratio is not a statistic"*; D11: it *"INVERTS with run
  length"*)
- any convergence claim must state the **settle length** and **frame count**
- an absence claim must state **which view was searched** (the H0 rule, now with
  a second instance: `~/Downloads` TCC)

### E6. Stamp the run manifest.

`summary.json` must record, per run: `sim_standing.py` sha256 **at execution
time**, `settle_frames`, `n_grid`, `dx`, `realized_depth/dx`, band, PPC, and the
repeat-run determinism floor if one was measured. Five of those seven were
invisible in published numbers until last night.

### E7. Promote the mirror control to a standing gate.

It found a resolution ceiling between n_grid 100 and 104 that **no existing gate
detects**, at a cost of 20 to 130 seconds per rung. It belongs in
`.claude/checks/`, run on any solver change, with D4's caveat attached: the
scene's lattice is not exactly symmetric (`by/h` non-integer at every
resolution), so the control reports a **relative** change against its own
baseline rather than an absolute guarantee.

### E8. Authenticate Undermind.

Currently configured and unauthenticated, so six deep-research reports are
grep-only. Reading the **catalogs** rather than the summaries is what surfaced
the six uncited papers; a query interface makes that routine instead of heroic.

---

## PART 4 — HARDWIRING, PER APPLICATION

**Vista / LS6.** E1 above. Add two facts as server-enforced invariants rather
than documentation: LS6 **cannot run warpmpm** (stub), and `srun --jobid=`
**requires `--overlap`**. Both were learned expensively and both are one-line
guards in a typed tool.

**Undermind.** E8, plus a `corpus_cited_status` bridge so a report's catalog can
be diffed against the repo bibliography automatically. The single highest-value
artifact of the round would be that diff run continuously.

**Gradio — and this is the one I would argue for hardest.** Not for fleet
coordination; tmux plus the monitor already works. Build it for **frame review**.
The single most valuable diagnostic of the entire night came from Josie watching
a video and asking *"why do the cars move at the beginning, that makes no
physical sense?"* That found `settle_frames=8`, which then invalidated a 6.1x
spread, inverted a gate ordering, and explained three separate false results. No
automated gate caught it. A Gradio app that scrubs frames, overlays the
per-frame body position and velocity, and has a **"flag this frame"** button
writing to a findings file would industrialize the best instrument available.

**GitHub.** Already an MCP server. Add E1's CI half: run `params_check.py`,
`register_integrity.py` and `count_claims_check.py` on push, so Vista's drifted
checkout cannot stay invisible.

**Weights & Biases / HF.** `7b8dbc33` recommended both. Neither is wired. W&B is
genuinely useful here for one specific thing: **the determinism floor**. Logging
repeat-run spread per configuration turns "did anyone repeat this?" from an
archaeology question into a dashboard.

---

## PART 5 — THE HONEST LIMIT

`35a13e3e` states it plainly and last night confirmed it: *"a hard residual of
non-determinism, context rot, and destructive-command risk survives any setup."*
Every failure in Part 2 was committed by a Claude instance that had the correct
procedure written down, in its own context, and sometimes had just told another
session to follow it.

So the design principle is not "instruct better". It is: **anything that must be
true should be a typed tool return or a hook exit code, not a sentence.** E1's
`is_stub`, E3's predicate, E4's hash comparison and E5's required fields are all
the same move, which is taking a rule that was already written down and making it
impossible to skip.

The corresponding human principle: last night the highest-value signals came from
Josie catching a physical implausibility by eye, and from sessions refuting the
coordinator. Preserve both. Build the Gradio review app, and never let a
coordinator's claim reach a document without a session having had the chance to
test it.
