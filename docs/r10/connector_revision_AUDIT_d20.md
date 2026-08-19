# Audit of `docs/r10/connector_revision.md`, by slot d20-reader

**Written 2026-08-20 00:45 BST.** Audits the r10 workflow's connector side file from outside
the workflow, as commissioned. The main report
`docs/R10_FULL_CONTEXT_AUDIT_2026-08-19.md` **had not landed** at the time of writing;
`docs/r10/` held only `connector_revision.md` (33,546 bytes, 00:25) and `corpus_revision.md`
(50,504 bytes, 00:27).

## Verdict in one line

**The side file is largely right, it corrects me on several real points, and its single most
prominent instruction is wrong for the audience it is aimed at.** It probed a session with
**76 MCP servers**; every session that reads the skill it corrects has **17**.

---

## 1. Where it corrects me and is right

Accepted without reservation. My probe grepped `.mcp.json` and the `mcpServers` block of
`~/.claude.json` and concluded absence from that. That is a two-layer view of a five-layer
system, and concluding absence from a partial view is the exact failure this project
documents. Specifically it is right that:

- **There are more config layers than I accounted for**, including the per-project
  `projects[cwd].mcpServers` block, the Claude Desktop config, and bridged claude.ai
  connectors that are in no local file at all.
- **Scite content is reachable without OAuth** via `mcp__zotero__scite_*`. My skill said
  "route to Scholar Sidekick instead", which is half right. The Scite *server* is dead
  headless; Scite *data* is not. Those tool names were in my own session's manifest and I
  did not connect them.
- **My stated mechanism for the GitHub MCP failure was carried from memory, not measured
  here.** I wrote "an http entry with no `headers` block returns 401". The `github` server
  comes from the Desktop config with an `env` block, so on this machine it is a stale token.
  The verdict (use `gh`) is unchanged; my reason was wrong.
- **The Scholar Sidekick cache catch is a good one.** Their `resolveIdentifier` returned
  `_source.fetchedAt` of `22:46:57Z`, the entry my probe populated 35 minutes earlier. A
  cached hit proves the MCP process is alive, not that upstream is.
- **Consensus works** and carries a 3-result cap without a linked account. I had marked it
  UNPROBED, which was honest but is now superseded.
- **Scholar Gateway reaches Wiley full text for JFRM.** I never probed it.

## 2. Where it is wrong, and it is the most prominent thing in the file

The file says, in bold, of five rows in my skill:

> **THE REPO SKILL IS WRONG HERE. RETRACT THAT ROW.**

for Otter, Slack, Google Calendar, Google Drive/Docs and pdf-viewer, on the evidence that it
called each one and got real data.

**Its probes are genuine. Its correction does not transfer.** Measured from tool
**manifests**, not from usage counts:

| session | MCP prefixes | UUID-prefixed (bridged claude.ai) | pdf-viewer | PDF_Tools | Otter |
|---|---|---|---|---|---|
| main checkout `529261e9` (the coordinator's) | **76** | **31** | yes | yes | yes |
| r9-reader | 17 | **0** | no | no | no |
| r9-settle | 17 | **0** | no | no | no |
| r9-accessor | 17 | **0** | no | no | no |
| r9-corpus-bib | 17 | **0** | no | no | no |
| r9-priorcode | 17 | **0** | no | no | no |
| r9-jobb-route | 17 | **0** | no | no | no |
| r9-renders | 17 | **0** | no | no | no |

**Seven of seven slot sessions: identical 17-prefix manifest, zero bridged connectors.** A
sweep of every `~/.claude/projects` directory agrees: all twenty r7, r8 and r9 sessions show
zero, while the main checkout and several older worktrees show 4 to 9.

So my rows were **correct for every session that reads the skill** and incorrect only as a
statement about Claude Code in general. The right wording is neither mine nor theirs:

> Absent from every R9 slot session, measured on seven manifests. Present in the
> main-checkout session, which has 76 servers. Do not route a slot to these.

**Both documents scoped their probe and only one scoped its conclusion.** My skill says
"from a Claude Code session in a git worktree". Their file says "cwd
`/Users/josie/can-it-ford`, main checkout (not a worktree)". Both correct. Then their file
issues an unscoped imperative. That is scope-loss between the measurement and the
instruction, which is the failure the coordinator flagged to me tonight about its own relays,
reappearing inside the workflow's output.

**It is not a worktree property.** Older worktrees do have the bridged connectors. What all
twenty zero-connector sessions share is the launcher: `r8_launch.sh` runs
`claude --model opus --effort max --permission-mode bypassPermissions`. That is the leading
hypothesis, and it is a hypothesis: I have not isolated which flag or launch path causes it.

## 3. The structural finding, which neither document states

**Every dispatching session has 76 connectors. Every dispatched session has 17.** A 4.5x
capability gap between the coordinator and every slot it briefs.

Consequences, in order of cost:

1. **A coordinator can verify something no slot can.** Anything reached through Otter, Slack,
   Calendar, Drive, Scholar Gateway or the PDF servers is checkable at the top and
   unreachable below. A relay of such a result cannot be independently confirmed by its
   recipient, which is the precondition for the relay-fidelity failure already measured
   tonight, where two Wallstedt claims were carried wider than their source.
2. **The routing table has been aspirational for the whole of R7, R8 and R9.** Otter, Slack,
   Calendar and Drive rows have been unreachable for every slot in three waves.
3. **Scholar Gateway is the concrete loss.** The side file calls it the most under-rated
   connector here and shows it returning Wiley full text from *Journal of Flood Risk
   Management*, the journal this project lives in. No slot can reach it. Any full-text need
   below the coordinator must go through Undermind, which reads open access only.

**Recommendation, and it is one line:** either launch slots so they inherit the bridged
connectors, or state in the skill that the routing table has two tiers and mark which rows a
slot cannot use. Do not leave the table implying a capability the reader does not have.

## 4. On its coverage claim

The commission asked whether the workflow's coverage claim is honest, counting how many of
the papers it says it read are actually cited in its conclusions. **That check belongs to the
main report and cannot be run yet, because the main report does not exist.** This side file
makes no N-papers-read claim, so there is nothing to test here. It does mark UNTESTED items
separately from PASS and FAIL throughout, including Canva, Figma, Lucid and the not-a-fit
list, which is the right shape.

One accuracy note in its favour: it corrects the global skill's "checked, not a fit" list by
observing that most of those products are **not present at all**, so listing them as checked
overstates what was checked. That is the same class of correction I am making about its own
retraction, applied by it to someone else.

## 5. Two errors of my own, recorded

1. **I nearly published a contaminated measurement.** My first attempt to test whether my
   session has `pdf-viewer` grepped my own transcript for the string, and matched it, because
   I had just **read** the side file, which contains `mcp__pdf-viewer__list_pdfs` as example
   text. A transcript grep cannot distinguish a tool I hold from a tool name I read. The
   manifest check above is the corrected method, and it reverses the answer.
2. **My original absence claim was reached by the wrong route even though it landed on the
   right answer for slots.** I grepped two config files. Seven manifests are the evidence
   that actually supports the claim, and I only gathered them after being contradicted.

## Falsifiers

- The 17-versus-76 split dies if any R9 slot manifest contains a UUID-prefixed server.
  Command: for each slot transcript, extract the largest set of `mcp__NAME__` matches from a
  ToolSearch result line and test for `mcp__[0-9a-f]{8}-`.
- The launcher hypothesis dies if a session launched by `r8_launch.sh` in the main checkout
  shows the bridged connectors, or if an interactively-launched worktree session shows none.
  Neither control has been run.
- Section 2 does not dispute a single one of the side file's probes. It disputes only that
  its conclusion transfers. If the slots are relaunched with the bridged connectors, its
  wording becomes correct and mine becomes stale.

**Unreviewed.** Every child `claude` process on this machine still dies on
`deepseek-ai/DeepSeek-V4-Flash:deepinfra`, so no adversarial pass was possible.

---

# Addendum, 2026-08-20 00:55: why the report is absent, and the 784 KB nobody can reach

Written after the coordinator supplied the run's failure mode. Everything below the first
paragraph is my own measurement, not a relay.

## The run did not fail silently, it hit a spend limit

The coordinator reports 22 of 25 agents completed and three errored, all three with
"You've hit your monthly spend limit", and that the three were `synth:report`,
`synth:critic` and `rx:vista`, i.e. exactly the agents that produce the deliverable. The run
was resumed at 00:41; completed agents replay from cache.

**Do not read the missing report as a silent failure.** I had it recorded as "has not
landed", which is true and uninformative. A workflow that loses only its synthesis stage
leaves a tree that looks like an abandoned run and is not one.

## Measured: the findings exist, and they exist nowhere a person will look

Read directly from the run journal at
`~/.claude/projects/-Users-josie-can-it-ford/529261e9-.../subagents/workflows/wf_5266ee59-fb9/journal.jsonl`:

| quantity | measured |
|---|---|
| journal records | 50 |
| records carrying a result payload | **23** |
| total result payload | **784,798 bytes** |
| agent identification | opaque `v2:<hash>` keys, **no labels** |
| of that, reachable in `docs/` | `connector_revision.md` 33,546 + `corpus_revision.md` 50,504 = **84,050 bytes** |

**About 700 KB of findings from 23 completed agents exist only in that journal.** Three
properties make that worse than it sounds:

1. **It is outside the repository.** The path is under `~/.claude/projects/`, not under
   `/Users/josie/can-it-ford`. It is in no commit, on no branch and in no bundle, which is
   the same condition the shared board was in earlier tonight.
2. **The results are not addressable.** The `key` field is a content hash. Nothing in the
   journal says which agent produced which payload, so recovering a specific finding means
   reading payloads until one matches.
3. **It is transient by design.** Session scratch directories are cleaned. Nothing warns
   before that happens.

**This is the same shape as the C-10 finding about session transcripts, one level up.** There
the index of the wave covered 38.7 percent of it; here the deliverable covers 10.7 percent of
what the run produced, and the rest is in a file whose only copy is outside version control.

**Recommendation, and it does not need the workflow to finish:** dump the 23 payloads to
`docs/r10/` as numbered files before anything cleans that directory. That is recoverable now
and unrecoverable later. I have not done it: writing 700 KB of another agent's unreviewed
output into the repo is a decision about what the repo carries, not a mechanical step, and it
is the workflow owner's call.

**One number corrected in passing:** the coordinator says 22 completed; the journal carries
23 result payloads. I have not reconciled the difference and it does not change anything
here. Quote whichever you can re-derive.

## The spend limit supersedes a published artifact this project relies on

`Console Against Can It Ford`, https://claude.ai/code/artifact/62a71c41-2845-436c-b777-61d901b8e65b,
updated 2026-08-17, concludes from 28 days and 72,126 turns that there were **zero** Anthropic
rate or usage limits and therefore no headroom problem to solve.

**That conclusion is now superseded.** Tonight the fleet spent roughly 8.8 million subagent
tokens across two workflows, hit the monthly spend limit, and lost the three agents that
produce a report. Every pane reads "Now using usage credits".

It was true when written. The artifact is not wrong about its own measurement window; it is
wrong as a standing statement, and the difference is exactly the one this project keeps
paying for. **An absence measured over a window is not a property of the system.** 28 days
without a limit does not establish that no limit exists, and the artifact's own headline
invites that reading.

**I did not edit the artifact.** My write scope is repo paths, an artifact is an
outward-facing surface, and I have not read its full text so I could not amend it without
risking content loss. The URL above is the exact target. What the correction needs to say is
one sentence: the zero-limits finding holds for 2026-07-20 to 2026-08-17 and was **falsified
on 2026-08-19**, when a 25-agent workflow lost its synthesis stage to a monthly spend limit.

## Two corrections accepted, and one of them is my own pattern used on me

The coordinator withdrew two claims from its audit of this slot, unprompted.

1. **"d20-reader is STALLED, silent five hours since 19:29" was false.** I was mid-turn. A
   commit-based liveness check cannot distinguish "not committing" from "working a long
   turn". **That is C-2's shape exactly**, a check that returns a confident verdict on a
   state it cannot observe, and it was applied to me rather than by me. It is the ninth
   instance of that class tonight and the first where I was the subject.
2. **"One live approval prompt in every pane" was false**, matching the word "permission" in
   a status bar. Corrected sweep: zero fleet-wide.

Both were caught by their author. That is now the third time tonight a correction has not
needed an auditor, which is worth more than any of the individual corrections.

## Confirmed: I am running outside my declared permission mode

`r8_plan.tsv` sets `d20-reader` to `acceptEdits` in its scope column while the pane reads
`bypasspermissions on`. Permission mode is fixed at launch, so the plan file describes an
intent the running session does not honour. I flagged this at 23:44 from my own transcript,
which records `bypassPermissions` and no `plan` record at all, and the coordinator's sweep
now confirms it fleet-wide.

**It is not academic.** Everything I have written tonight, including this file, was written
with access the plan says I should not have. Nothing here is unapplied, and that is the
opposite of what the brief predicted. The general form belongs in the coordinator audit's
section on the launcher: **a per-slot permission column that is read after launch configures
nothing.**
