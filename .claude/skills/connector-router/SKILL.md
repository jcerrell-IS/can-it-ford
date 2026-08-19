---
name: connector-router
description: Use this on every turn as a standing check, not only when explicitly asked. Before answering a technical claim, citation, code-state claim, meeting/mentor question, or deadline question, check whether a connected tool should verify it first, per the routing table below, instead of answering from memory alone. Carries the measured reachability table and the exact ToolSearch select string for every connector that actually works from Claude Code.
---

# Connector router (auto-trigger, no explicit ask needed)

## READ THIS FIRST: configured is not reachable, and the difference has cost whole rounds

Every row below was **probed live on 2026-08-19 between 23:44 and 23:50 BST** by slot
d20-reader, from a Claude Code session in a git worktree. A row saying WORKS means a real
call returned real data at that time, and the evidence is quoted. Re-probe before betting a
round on one.

**The failure this file exists to stop:** a session concludes a connector is broken, works
around it for an hour, and the connector was fine. It has happened at least twice. A
`.mcp.json` http entry with no `headers` block returns 401 and two sessions read that as a
dead token; all three tokens were valid. So: **never conclude a connector is dead from one
error. Check this table, then check the exact select string below, then re-probe.**

## Step 1, the step sessions get wrong: load the tool before calling it

MCP tools are DEFERRED. The name appears in the system reminder but the schema does not, so
calling it directly fails with `InputValidationError` and reads like a broken connector.
**Load with ToolSearch first, and batch every tool you expect to need into ONE call.**

Copy the string, do not retype it.

    ToolSearch  select:mcp__undermind__inspect_deep_searches,mcp__undermind__get_paper_info,mcp__undermind__read_pdfs,mcp__undermind__search_papers
    ToolSearch  select:mcp__deepwiki__ask_question,mcp__deepwiki__read_wiki_structure,mcp__deepwiki__read_wiki_contents
    ToolSearch  select:mcp__wolfram__WolframAlpha
    ToolSearch  select:mcp__scholar-sidekick__verifyCitation,mcp__scholar-sidekick__resolveIdentifier,mcp__scholar-sidekick__auditBibliography,mcp__scholar-sidekick__checkRetraction
    ToolSearch  select:mcp__canford-corpus__corpus_inventory,mcp__canford-corpus__corpus_search,mcp__canford-corpus__corpus_read,mcp__canford-corpus__corpus_resolve
    ToolSearch  select:mcp__canford-tacc__tacc_alloc_status,mcp__canford-tacc__tacc_gpu,mcp__canford-tacc__tacc_tail,mcp__canford-tacc__tacc_env_probe
    ToolSearch  select:mcp__overleaf__status_summary,mcp__overleaf__get_sections,mcp__overleaf__get_section_content,mcp__overleaf__read_file
    ToolSearch  select:mcp__zotero__zotero_get_collections,mcp__zotero__zotero_search_items,mcp__zotero__zotero_get_item_fulltext
    ToolSearch  select:mcp__hf__hf_whoami,mcp__hf__hub_repo_details,mcp__hf__hub_repo_search
    ToolSearch  select:mcp__plugin_context7_context7__resolve-library-id,mcp__plugin_context7_context7__query-docs
    ToolSearch  select:mcp__elicit__search_papers,mcp__elicit__get_usage
    ToolSearch  select:mcp__consensus__search

## Step 2, the reachability table, measured not assumed

| connector | status 2026-08-19 23:44-23:50 | evidence from the live probe |
|---|---|---|
| **Undermind** | **WORKS** | 21 completed deep searches in workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c`. `read_pdfs` returned full text of four papers earlier the same evening |
| **DeepWiki** | **WORKS** | `read_wiki_structure kks32/mpm-engine` returned the full page tree, including "2.4.2 CDF Thin-Boundary Colliders (CPIC)" and "4.3 Flood and Vehicle Simulation" |
| **Wolfram** | **WORKS** | "density of water at 20 C" returned 998.2 kg/m^3 |
| **Scholar Sidekick** | **WORKS** | `resolveIdentifier 10.1051/matecconf/201820307003` returned the Crossref record and settled a live name-variant question: first author is **Syed Muzzamil Hussain Shah**, not Hamid |
| **canford-corpus** | **WORKS, with one denial** | 6 roots. Five OK; `~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13` reads **310 of 389** files, `PARTIAL/TCC-DENIED`. Its own rule: a partial count is a broken probe, not an absence |
| **canford-tacc** | **WORKS** | vista: 2 jobs COMPLETING, `su_remaining` 597 |
| **Overleaf** | **WORKS** | `status_summary` returned `conference_101719_1.tex`, 17 sections, 1 file. Still confirm the token file is non-empty before trusting a write path |
| **Zotero** | **WORKS** | returned real collections including `Can it Ford???` and its six children |
| **Hugging Face** | **WORKS** | authenticated as `josiecerrell`, pro, write-scoped personal access token |
| **Context7** | **WORKS** | `NVIDIA Warp` resolved to `/nvidia/warp`, 1910 snippets, High reputation |
| **Elicit** | **WORKS** | 6 percent of the period used, quota remaining |
| **Scite** | **OAUTH-GATED, DEAD HEADLESS** | its own tool description says calling it "start[s] the OAuth flow, you'll receive an authorization URL to share with the user". A session with no human at the keyboard cannot finish it |
| **GitHub MCP** | **DO NOT USE** | use `gh` CLI and `git`. An http entry with no `headers` block returns 401 and two sessions misread that as a dead PAT |
| Otter.ai, Slack, Google Calendar, Google Drive/Docs, pdf-viewer | **NOT PRESENT in Claude Code** | these are chat-surface connectors. They are not in `.mcp.json` or `~/.claude.json`, so routing to them from a Claude Code session routes to nothing |

## Step 3, the routing table

| Topic in the message | Route to | Why |
|---|---|---|
| **"Has anyone done X", "is this novel", "what should we cite", any absence claim about the literature** | **Undermind `inspect_deep_searches`, then `read_pdfs`** | **The single most important row and it was missing from this file until 2026-08-19.** The 21 deep searches are the project's own commissioned research. The corpus index holds **no full text**, 110 of 332 records have no abstract, and it is built from 8 of the 21, so a zero from `research_index.py --query` is not evidence of absence. Load the `research-corpus` skill too |
| Reading a paper that decides something | **Undermind `read_pdfs`**, batched, up to 20 papers in one call | Reads actual full text including figures and tables. The index cannot: its largest text blob is 3,477 characters |
| Claim about how a GitHub repo actually behaves (kks32/mpm-engine, Genesis, PhysGaussian, gsplat, warp-mpm) | DeepWiki | Treat its answer as a hypothesis to verify against source, never as fact |
| A physical parameter, unit conversion, or equation about to be used or stated | Wolfram | Cheap sanity check before it becomes a sim input |
| **A DOI, PMID, arXiv id, or a whole .bib about to enter the paper, poster, or a message to Kumar** | **Scholar Sidekick, NOT Scite** | Scite is OAuth-dead here. Scholar Sidekick catches the dominant fabrication pattern, a real resolving DOI with an invented title, which "the link works" never catches. Whole file in one call: `auditBibliography` |
| Whether a paper is retracted | Scholar Sidekick `checkRetraction` | |
| "Is this an established mechanism", needing the field rather than one paper | Consensus, or Elicit for extraction across papers | Both reachable. Consensus was loaded but not probed on 2026-08-19; treat as UNPROBED rather than working |
| Claim about current code state, whether something is "done", or a number from a script | `gh` CLI and `git`, plus a live file read. **NOT the github MCP** | The most repeated failure mode here is trusting a summary over the live file |
| Anything needing the paper on Overleaf | Overleaf MCP, after `wc -c ~/.config/overleaf-mcp/token` is non-zero | It reports Connected with a 0-byte token and only fails on the first real fetch |
| Live SLURM state, SU balance, remaining wall time on a Vista or LS6 job | canford-tacc `tacc_alloc_status` | Use `remaining_s` rather than estimating elapsed time. A coordinator once drifted its own clock by an hour against a deadline that did not exist |
| Reading a local research artifact, and any "the file is not there" conclusion | canford-corpus `corpus_inventory` FIRST | A TCC denial reads exactly like an absence. Run the inventory so a denial is visible as a denial |
| Current API, signature or default of a NAMED library (Warp, Taichi, PyTorch, numpy, trimesh, gsplat) | Context7 | Library-general goes to Context7, repo-specific to DeepWiki. When both apply, Context7 first |
| Gradio demo or Hugging Face deploy status | Hugging Face | Direct source |
| Anything in the Zotero library | Zotero | Note the repo `.bib` and Overleaf `.bib` use different keys for six works |

## Step 4, what a negative from a connector does and does not license

- A zero from `research_index.py --query` is a literal substring match over title and
  abstract only. It cannot match an author. **Not an absence.**
- A partial count from `corpus_inventory` is a TCC denial. **Not an absence.**
- A 401 from an http MCP entry with no `headers` block is a missing header. **Not a dead
  token.**
- An OAuth prompt is not a failure, it is a connector that needs a human. Say so and route
  around it rather than retrying.
- **A subagent's absence result is not an absence.** A tooling document in this project's own
  corpus rests a novelty claim on "subagent found none" and that claim is now refuted.

## The honest limits of this file

- **It is a per-turn behavioural rule, not a background job.** Nothing runs while no
  conversation is open.
- **TWO COPIES EXIST AND NEITHER IS A SUPERSET.** `~/.claude/skills/connector-router/` and
  this one. On 2026-08-19 the global copy carried a Scholar Sidekick `ssk audit` row this one
  lacked, while this one carried the Context7, Overleaf and github-MCP rows the global lacked.
  Only this repo copy was revised on 2026-08-19; **the global copy is stale and was not in
  the revising session's write scope.** Reconcile them by hand before trusting either.
- **This file is branch-tracked, so a worktree carries the version from ITS branch point.**
  On 2026-08-19 the research-corpus skill existed in four different states across nine live
  worktrees, two of them with no file at all, and eight of nine sessions could not see a
  sibling's corrections. Check what your worktree actually holds before citing a skill as
  authority.

## Refresh

Trigger: "update the connector router", or a new connector is added. **Re-probe rather than
edit from memory**, and stamp the probe date in the table. A row without a date is a claim
about the past.
