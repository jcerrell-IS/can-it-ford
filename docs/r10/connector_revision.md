# Connector revision, r10

**Probe window: 2026-08-19 23:12 to 23:22 UTC (2026-08-20 00:12 to 00:22 BST).**
Probed from a Claude Code session, cwd `/Users/josie/can-it-ford`, main checkout (not a
worktree). Every "WORKS" row below means a real call returned real data inside that window
and the evidence is quoted. Anything I could not test is in its own section at the bottom
and is marked UNTESTED, never PASS and never FAIL.

This file does NOT edit either `connector-router/SKILL.md`. It is the correction sheet for
them. Both copies are named and both are wrong in different places.

**Sources this file corrects:**
- `/Users/josie/.claude/skills/connector-router/SKILL.md` (global copy, read directly this
  session, 35 lines, no probe dates anywhere)
- `/Users/josie/can-it-ford/.claude/skills/connector-router/SKILL.md` (repo copy, read
  directly this session, probed 2026-08-19 22:44 to 22:50 UTC by slot d20-reader)

---

## 0. The finding that reframes everything else: there are FOUR config layers, not two

Read directly this session. The repo skill accounts for `.mcp.json` and implies
`~/.claude.json`. There are four, and the fourth is the one nobody has been reading.

| layer | file | servers it supplies |
|---|---|---|
| 1. project `.mcp.json` | `/Users/josie/can-it-ford/.mcp.json` | `deepwiki`, `scite`, `wolfram`, `canford-corpus`, `canford-tacc` |
| 2. global `~/.claude.json` `mcpServers` | `/Users/josie/.claude.json` | `deepwiki`, `hf`, `blender`, `zotero`, `undermind`, `context7`, `exa`, `elicit`, `scholar-sidekick`, `overleaf` |
| 3. per-project `~/.claude.json` `projects[cwd].mcpServers` | same file, `projects` block | for `/Users/josie/can-it-ford`: `scite`, `elicit`, `consensus`, `jupyter-executor`, `undermind`, `overleaf`, `zotero`, `hf-mcp-server` |
| 4. **Claude Desktop config, bridged in** | `~/Library/Application Support/Claude/claude_desktop_config.json` | **`filesystem`, `memory`, `sequential-thinking`, `github`, `overleaf`** |
| 5. claude.ai connectors, bridged in | not a local file | **31 UUID-prefixed servers**, counted by hand off this session's deferred-tool listing (Otter, Slack, Google Calendar, Google Drive, Scholar Gateway, Canva, Figma, Lucid, Asana, Supabase, Webflow, Amplitude, and more) |

Read directly: layer 4 was found by listing the JSON keys of the Desktop config, which
returned `filesystem`, `memory`, `sequential-thinking`, `github`, `overleaf` in that order.
That is where `mcp__github__*` comes from, and it is why the repo skill's advice about
"an http entry with no `headers` block" does not describe the github failure seen tonight.

**Consequence:** grepping `.mcp.json` and concluding a connector is absent is a partial
view. Two of the highest-value connectors in this environment (Otter, Scholar Gateway) are
in neither local file.

---

## 1. Table: every connector either SKILL.md mentions

Column "in skill" says which copy names it: **G** = global copy, **R** = repo copy.

| connector | in skill | test I ran this session | result | corrected routing advice |
|---|---|---|---|---|
| **Undermind** | R | `get_orientation`, then `inspect_deep_searches(workspace_id=17299f2a-8dc8-438b-8c84-5abf19395e2c, status_only=true)` | **WORKS.** Account `jcerrell29@students.claremontmckenna.edu`. **21 deep searches, all status `completed`**, newest "free surface elevation estimator error in particle method buoyancy validation" (Aug 19 17:44), oldest "Optical Vehicle Collision Geometry" (Jul 15 02:10) | Unchanged, and the workspace id in the task brief is **confirmed correct**. Still the first stop for any absence claim about the literature. `get_orientation` is cheap and states the connected account, so run it once per session before betting on a workspace id |
| **DeepWiki** | G, R | `read_wiki_structure("kks32/mpm-engine")` | **WORKS.** Returned the 8-chapter page tree including "2.4.2 CDF Thin-Boundary Colliders (CPIC)" and "4.3 Flood and Vehicle Simulation" | Unchanged. Treat its answers as hypotheses to check against vendored source under `third_party/`, never as fact. Note a **duplicate** DeepWiki exists as `mcp__8fce264e-...`; prefer the bare `mcp__deepwiki__` |
| **Wolfram Alpha** | G, R | `WolframAlpha("density of water at 20 C in kg/m^3")` | **WORKS.** Returned 998.2 kg/m^3, with the 1 atm assumption printed in the input interpretation | Unchanged. Read the "Input interpretation" block, not just the number: it silently assumed 1 atm here. A **duplicate** exists at `mcp__e8b78a84-...__WolframAlpha` |
| **Scite** | G, R | No `mcp__scite__*` tool name is exposed at all this session, and the session-start notice lists `scite` under "require authentication" | **OAUTH-GATED, DEAD HEADLESS.** Confirms the repo skill | **The repo skill's conclusion "route to Scholar Sidekick instead" is now only half right.** Scite *content* is reachable two other ways that need no OAuth, both verified below: `mcp__zotero__scite_*` and `mcp__0712b3a5-...__search_literature`. Do not write off Scite data because the Scite server is dead |
| **Scholar Sidekick** | G, R | `mcp__scholar-sidekick__resolveIdentifier("10.1051/matecconf/201820307003")` | **WORKS**, with a caveat. Returned first author **Syed Muzzamil Hussain Shah** (not Hamid), MATEC Web Conf. 203, 2018. **But `_source.fetchedAt` was `2026-08-19T22:46:57Z`**, i.e. the record was served from the cache the d20 probe populated 35 minutes earlier | **THERE ARE THREE SCHOLAR SIDEKICK SURFACES AND ONE OF THEM IS BROKEN.** See section 2. Use `mcp__scholar-sidekick__` (lowercase, stdio). A cached hit proves the MCP process is alive, not that the upstream API is; force a fresh identifier if upstream liveness is the question |
| **Consensus** | G ("Consensus or Scholar Gateway"), R (as UNPROBED) | `search("vehicle instability in floodwater stability thresholds")` | **WORKS.** 20 papers found, **only 3 returned**, top hit Nihei et al 2025 full-scale flooding experiments, then Martinez-Gomariz et al 2018 state-of-the-art review | **Promote from UNPROBED to WORKS, and add the cap the skill never mentions: 3 results per search without a linked Consensus account.** For a field-level sweep that cap is crippling; prefer Undermind or Scholar Gateway and use Consensus for a fast sanity read. A **duplicate** exists at `mcp__4c34fb83-...__search` |
| **Scholar Gateway** | G (named, never routed or probed) | `mcp__88a938f6-...__semanticSearch("critical water depth ... passenger car ... floodwater", topN=2)` | **WORKS, and it is the most under-rated connector in this environment.** Returned full-text chunks from *Journal of Flood Risk Management*, including Bocanegra, Valles-Moran & Frances 2019 `10.1111/jfr3.12551` and Lumbroso & Davison 2016 `10.1111/jfr3.12230`. Self-identifies as Wiley-backed, corpus last updated **May 2026** | **Promote to a first-class row.** It reaches Wiley full text for the exact journal this project lives in (JFRM), which the corpus index cannot: register-side, the index holds no full text. Pair with Undermind, not instead of it: Undermind reads open-access PDFs, Scholar Gateway reads paywalled Wiley. Note it demands a provenance line and a session footer in its own response contract |
| **GitHub (MCP)** | R ("DO NOT USE") | `mcp__github__search_repositories("repo:jcerrell-IS/can-it-ford")` | **FAILS: `Authentication Failed: Bad credentials`** | **The verdict stands but the repo skill's stated MECHANISM is wrong for this server.** This is not a missing `headers` block: the `github` server comes from the Claude Desktop config (layer 4) and carries an `env` block, so the failure is a stale token, not a missing header. Route to `gh` CLI, verified live: `gh auth status` reports logged in as **`jcerrell-IS`** via keyring, scopes `admin:public_key, gist, read:org, repo` |
| **GitHub, live file read** | G, R | `gh auth status` | **WORKS** | Unchanged and now evidenced. `gh` + `git -C /Users/josie/can-it-ford` remains the route for any code-state claim |
| **Otter.ai** | G (routed), R (**"NOT PRESENT in Claude Code"**) | `mcp__797ffcc1-...__otter_get_user_info` | **WORKS.** Returned "Josephine Cerrell", `jcerrell29@students.claremontmckenna.edu`, server clock 2026-08-19 16:18:55 PDT | **THE REPO SKILL IS WRONG HERE. RETRACT THAT ROW.** Otter is reachable from this Claude Code session as a bridged claude.ai connector. The global skill's routing ("what did we decide", "what did Kumar say" goes to Otter first) is correct and should be restored |
| **Slack** | G (routed), R (**"NOT PRESENT"**) | `mcp__b89e1ca1-...__slack_search_channels("general")` | **WORKS.** Returned `#general` on **geoelements.slack.com**, created 2019-11-18 by **Krishna Kumar**, permalink `geoelements.slack.com/archives/CQR8JBFV5` | **RETRACT THE "NOT PRESENT" ROW.** Note the trap: the *plugin* Slack (`plugin:slack-by-salesforce:slack`) IS in the session-start "requires authentication" list and is dead, while this *connector* Slack works. Same product, two surfaces, opposite verdicts |
| **Google Calendar** | G (routed), R (**"NOT PRESENT"**) | `mcp__c8e1e1f1-...__list_calendars(pageSize=10)` | **WORKS.** 5 calendars: "FALL 2025", Claremont Club Soccer Practices, US Holidays, CMC Academic Schedule, Josephine Cerrell Calendar (Canvas) | **RETRACT.** Two independent Calendar paths exist and both work: the native one above, and the Zapier bundle `mcp__36e3f815-...__google_calendar_find_calendars`, which returned the identical 5 calendars. Prefer the native one, it does not consume Zapier task billing (the Zapier call reported `billingTasksUsed: 2`) |
| **Google Drive / Docs** | G (routed), R (**"NOT PRESENT"**) | `mcp__d2a4acff-...__list_recent_files(pageSize=5)` | **WORKS.** Returned 5 real files owned by `jcerrell29@...`, newest `image001.png` 2026-08-18 | **RETRACT.** Again two paths: native (`mcp__d2a4acff-...`) and Zapier (`mcp__36e3f815-...__google_drive_*`, plus Docs and Gmail). Prefer native for reads |
| **pdf-viewer** | G (routed), R (**"NOT PRESENT"**) | `mcp__pdf-viewer__list_pdfs` | **WORKS.** Returned a complete repo PDF inventory, `truncated: false`, scoped by `allowedDirectories: ["/Users/josie/can-it-ford"]`. I did not count the entries, so no total is claimed | **RETRACT.** Useful beyond viewing: it is a fast repo-scoped PDF inventory. It is sandboxed to the repo, so citations under `~/Downloads` or `~/Desktop` are invisible to it |
| **PDF Tools** | G (routed as "pdf-viewer or PDF Tools") | `mcp__PDF_Tools__get_allowed_directories` | **WORKS.** Boundary is `/Users/josie/Documents`, `/Users/josie/Downloads`, `/Users/josie/Desktop`, `/Users/josie/can_it_ford`, `/Users/josie/can-it-ford`, `/Users/josie/can-it-ford-untracked-preserve`, `/Users/josie/__pycache__`, `/Users/josie/Claude`, `/Users/josie/can-it-ford/kumar_july9_update` | Use PDF Tools, not pdf-viewer, whenever the PDF is outside the repo. Note `can_it_ford` with an underscore is in the allow list and is not this repo |
| **Hugging Face** | G, R | `mcp__hf__hf_whoami` | **WORKS.** `josiecerrell`, `is_pro: true`, credential is a **write-scoped personal access token** created 2026-07-23, zero organizations | Unchanged. **Trap the skill does not carry: two HF servers exist and only one works.** `hf` (global, carries an `Authorization` header) works; `hf-mcp-server` (project-scoped, url `https://huggingface.co/mcp?login`) is in the session-start "requires authentication" list. Use the `mcp__hf__` prefix |
| **canford-corpus** | R | `corpus_inventory`, then `corpus_search("connector", titles_only)` | **WORKS, same single denial as 35 minutes earlier.** 6 roots. Five OK. `~/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13` reads **310 of 389**, `PARTIAL/TCC-DENIED`. `~/Downloads` reads **591 of 591**, OK | Unchanged and re-confirmed independently. The TCC denial is **stable, not transient**: two probes 35 minutes apart give the identical 310/389. Do not retry expecting it to clear; the fix is a macOS Full Disk Access grant, not a re-run |
| **canford-tacc** | R | `tacc_alloc_status(host="vista")` | **WORKS, and demonstrably live rather than cached.** 1 RUNNING job `923291` `r9_est_e` on `c609-001`, elapsed 27:41, **remaining 17:19**. `su_remaining` **595** | Unchanged. **The SU figure moved from 597 to 595 between the two probes**, which is the cleanest available proof this connector is reading live rather than replaying. Keep using `remaining_s`/`remaining` instead of clock arithmetic |
| **Overleaf** | R | `status_summary()` | **WORKS.** `mainFile: conference_101719_1.tex`, 17 sections, 1 file | Unchanged in substance. **But the repo skill's precondition is not executable here:** I was DENIED permission to run `wc -c ~/.config/overleaf-mcp/token` and denied `ls -l` on that directory, so I could not verify the token is non-empty. The skill's "check the token first" step will be blocked in any session with the same permission set. Substitute check: call `status_summary` and require a non-empty `mainFile`, which is what I did |
| **Zotero** | R | `zotero_get_collections(limit=40)` | **WORKS.** Returned `Paper cited - IEEEtran` (6FSSIWN2), `Can it Ford - REU 2026` (DVV5B4IP), `Can it Ford???` (NSH8D498) with its 6 children | Unchanged, and **upgraded**: see the Scite bridge in section 2. Also still true that repo `.bib` and Overleaf `.bib` use different keys for six works, so do not auto-export |
| **Context7** | R | `resolve-library-id("NVIDIA Warp", query="warp kernel launch and CUDA graph capture")` | **WORKS.** `/nvidia/warp`, 1910 snippets, High reputation, benchmark 75.18 | Unchanged, with one addition: the query returns **five** libraries called "Warp" and four of them are the Warp *terminal*, which has nothing to do with this project. Always read the description line before taking an id |
| **Elicit** | R | `get_usage()` | **WORKS.** `hasUsageRemaining: true`, **7 percent** of the period used, period `2026-07-21` to `2026-08-21` | Unchanged, but note **the billing period rolls over on 2026-08-21**, one day after this probe. A quota reading taken today does not describe next week. A **duplicate** exists at `mcp__68f669a0-...` |
| Canva, Figma, Lucid | G ("only when actively building a visual") | Not called | **UNTESTED, PRESENT.** All three expose full tool sets (`mcp__6dc4d270-...` Canva, `mcp__Figma__*` and `mcp__1c9d5917-...` Figma, `mcp__b34ae897-...__lucid_*`) | Advice unchanged. Presence is confirmed from the tool listing; reachability is not, because I did not call them |
| AllTrails, AWS Marketplace, Box, Coupler.io, Tableau, Supabase, Vercel, Webflow, Spendflo, Indeed, Spotify, Strava | G (explicit not-a-fit list) | Not called | **UNTESTED.** Of these, only **Supabase** (`mcp__e1968daf-...`), **Webflow** (`mcp__8e6cb396-...`) and **Coupler.io** (`mcp__11231335-...`) are actually present as servers here | The "not a fit" judgement stands. Correct the list: AllTrails, Box, Tableau, Vercel, Spendflo, Indeed, Spotify, Strava are **not present**, so listing them as "checked, not a fit" overstates what was checked |
| Clinical Trials, PubMed, bioRxiv | G (not-a-fit list) | Not called | **PRESENT** as `plugin_bio-research_c-trials`, `plugin_bio-research_pubmed`, `plugin_bio-research_biorxiv` | Judgement unchanged, they do not touch this project |

---

## 2. The duplicate-surface trap, measured. This is the highest-value new finding.

Several products are exposed **more than once**, under different prefixes, from different
config layers, with **different auth**. Picking the wrong prefix returns a hard error that
reads exactly like a dead connector. Two of these were measured tonight and they disagree.

### 2a. Scholar Sidekick: three surfaces, one broken

| prefix | origin | probe | result |
|---|---|---|---|
| `mcp__scholar-sidekick__` | global `~/.claude.json`, stdio `npx` | `resolveIdentifier("10.1051/matecconf/201820307003")` | **WORKS.** Full Crossref record |
| `mcp__c6171af6-acdf-43e5-9f08-2811560492f0__` | claude.ai connector | `checkRetraction("10.1111/jfr3.12828")` | **WORKS.** `isRetracted: false`, title "A numerical approach to understand the responses of passenger vehicles moving through floodwaters" |
| `mcp__Scholar_Sidekick__` (capitals, underscores) | Desktop extension | `checkRetraction("10.1111/jfr3.12828")` | **FAILS: `You are not subscribed to this API.`** |

That third failure is the RapidAPI path. A session that reaches for the capitalised name
first gets a flat refusal and has every reason to conclude Scholar Sidekick is dead. It is
not. **Use `mcp__scholar-sidekick__` (lowercase-hyphen) as the default and
`mcp__c6171af6-...__` as the fallback. Never `mcp__Scholar_Sidekick__`.**

### 2b. Scite is dead as a server and alive as content, by two independent routes

- `mcp__zotero__scite_check_retractions(collection="Paper cited - IEEEtran", limit=50)`
  returned **"Checked 12 items with DOIs, no retractions or editorial notices found."**
  The tool's own description states it needs **no Scite account and no API key**; it hits
  public Scite endpoints. Sibling tools `scite_enrich_item`, `scite_enrich_search` and a
  top-level `mcp__zotero__search` / `mcp__zotero__fetch` exist on the same server.
- `mcp__0712b3a5-e74c-446d-ac4f-f52280b84e24__search_literature(dois=["10.1016/j.compfluid.2018.10.007"], term="inflow outflow boundary condition brink depth", limit=1)`
  returned the Zhao, Bolognin & Liang 2019 record with **5 full-text excerpts**, Smart
  Citation snippets with `section` labels, `tally` 8 mentioning / 18 citing publications,
  `oaStatus: bronze`, and a resolved OA PDF link. This is the Smart-Citations schema, which
  is Scite's signature output; the server identity is **inferred** from that schema, not
  read from a config, so treat the label as provisional.

**Corrected routing:** for "is this paper retracted", go to `mcp__zotero__scite_check_retractions`
for a whole collection in one call, or Scholar Sidekick `checkRetraction` for one DOI. For
"what does the full text actually say" when the PDF is blocked, go to
`mcp__0712b3a5-...__search_literature` with **`dois` plus `term` together**, which is what
produced excerpts here; `dois` alone returns metadata only.

### 2c. Other duplicates found, not individually probed

Undermind (`mcp__52146218-...`), DeepWiki (`mcp__8fce264e-...`), Wolfram
(`mcp__e8b78a84-...`), Consensus (`mcp__4c34fb83-...`), Elicit (`mcp__68f669a0-...`),
Hugging Face (`mcp__677ab2f7-...`), Figma (`mcp__1c9d5917-...` and `mcp__Figma__*`), Google
Workspace (`mcp__36e3f815-...` and `mcp__3f46535f-...`, byte-identical tool lists),
Desktop Commander (`mcp__Desktop_Commander__*` and
`mcp__plugin_desktop-commander_desktop-commander__*`), pdf-viewer (`mcp__pdf-viewer__*` and
`mcp__plugin_pdf-viewer_pdf__*`). **I probed only the bare-name copy in each pair.** Do not
assume the twin behaves the same: 2a is the counterexample.

---

## 3. Exact ToolSearch select strings. Copy, do not retype.

MCP tools here are **deferred**: the name appears in the system reminder but the schema does
not, so calling one directly fails with `InputValidationError` and reads like a broken
connector. Load first. Batch everything you expect to need into ONE call.

Every string below was **used successfully this session** unless marked otherwise.

```
# --- verified working this session ---

ToolSearch  select:mcp__undermind__get_orientation,mcp__undermind__inspect_deep_searches,mcp__undermind__read_pdfs,mcp__undermind__search_papers,mcp__undermind__get_paper_info

ToolSearch  select:mcp__deepwiki__read_wiki_structure,mcp__deepwiki__read_wiki_contents,mcp__deepwiki__ask_question

ToolSearch  select:mcp__wolfram__WolframAlpha

ToolSearch  select:mcp__scholar-sidekick__resolveIdentifier,mcp__scholar-sidekick__verifyCitation,mcp__scholar-sidekick__auditBibliography,mcp__scholar-sidekick__checkRetraction

ToolSearch  select:mcp__canford-corpus__corpus_inventory,mcp__canford-corpus__corpus_search,mcp__canford-corpus__corpus_read,mcp__canford-corpus__corpus_resolve,mcp__canford-corpus__corpus_headings,mcp__canford-corpus__corpus_cited_status

ToolSearch  select:mcp__canford-tacc__tacc_alloc_status,mcp__canford-tacc__tacc_gpu,mcp__canford-tacc__tacc_tail,mcp__canford-tacc__tacc_env_probe,mcp__canford-tacc__tacc_hostinfo

ToolSearch  select:mcp__overleaf__status_summary,mcp__overleaf__get_sections,mcp__overleaf__get_section_content,mcp__overleaf__read_file,mcp__overleaf__list_files,mcp__overleaf__list_projects

ToolSearch  select:mcp__zotero__zotero_get_collections,mcp__zotero__zotero_search_items,mcp__zotero__zotero_get_item_fulltext,mcp__zotero__scite_check_retractions,mcp__zotero__scite_enrich_item,mcp__zotero__zotero_get_collection_items

ToolSearch  select:mcp__hf__hf_whoami,mcp__hf__hub_repo_details,mcp__hf__hub_repo_search,mcp__hf__hf_fs

ToolSearch  select:mcp__plugin_context7_context7__resolve-library-id,mcp__plugin_context7_context7__query-docs

ToolSearch  select:mcp__elicit__get_usage,mcp__elicit__search_papers,mcp__elicit__create_report,mcp__elicit__get_report

ToolSearch  select:mcp__consensus__search

# --- connectors the skill said were absent. They are not. ---

ToolSearch  select:mcp__797ffcc1-24b3-465c-be18-5c93defc0868__otter_get_user_info,mcp__797ffcc1-24b3-465c-be18-5c93defc0868__otter_search,mcp__797ffcc1-24b3-465c-be18-5c93defc0868__otter_fetch

ToolSearch  select:mcp__b89e1ca1-ee05-4781-b3e8-45d2ab989f6f__slack_search_channels,mcp__b89e1ca1-ee05-4781-b3e8-45d2ab989f6f__slack_read_channel,mcp__b89e1ca1-ee05-4781-b3e8-45d2ab989f6f__slack_search_public,mcp__b89e1ca1-ee05-4781-b3e8-45d2ab989f6f__slack_read_thread

ToolSearch  select:mcp__c8e1e1f1-ac0b-434a-91f2-620937c3bc0a__list_calendars,mcp__c8e1e1f1-ac0b-434a-91f2-620937c3bc0a__list_events,mcp__c8e1e1f1-ac0b-434a-91f2-620937c3bc0a__search_events

ToolSearch  select:mcp__d2a4acff-0e08-424f-a498-2de419f1b303__search_files,mcp__d2a4acff-0e08-424f-a498-2de419f1b303__read_file_content,mcp__d2a4acff-0e08-424f-a498-2de419f1b303__list_recent_files

ToolSearch  select:mcp__pdf-viewer__list_pdfs,mcp__pdf-viewer__display_pdf

ToolSearch  select:mcp__PDF_Tools__get_allowed_directories,mcp__PDF_Tools__read_pdf_pages,mcp__PDF_Tools__search_pdf_text,mcp__PDF_Tools__convert_pdf_to_markdown,mcp__PDF_Tools__read_pdf_layout

# --- new, high value, not in either skill ---

ToolSearch  select:mcp__88a938f6-f477-4a40-818a-eab819d8e81b__semanticSearch

ToolSearch  select:mcp__0712b3a5-e74c-446d-ac4f-f52280b84e24__search_literature,mcp__0712b3a5-e74c-446d-ac4f-f52280b84e24__search_patents

ToolSearch  select:mcp__17d783e9-b8ba-4626-92d9-218ed2d88d76__web_search_exa,mcp__17d783e9-b8ba-4626-92d9-218ed2d88d76__web_fetch_exa

# --- fallback only, when the lowercase Scholar Sidekick is unavailable ---

ToolSearch  select:mcp__c6171af6-acdf-43e5-9f08-2811560492f0__checkRetraction,mcp__c6171af6-acdf-43e5-9f08-2811560492f0__verifyCitation,mcp__c6171af6-acdf-43e5-9f08-2811560492f0__resolveIdentifier
```

**Do NOT load these** (measured failures this session):
`mcp__Scholar_Sidekick__*` (returns "not subscribed"), `mcp__github__*` (returns "Bad
credentials"), `mcp__memory__read_graph` (schema-dialect error, see section 4).

Two shortcuts that work and save round-trips:

- A **keyword** query loads a whole server at once, no `select:` needed. Example:
  `ToolSearch {query: "computer-use", max_results: 30}` returns the entire computer-use
  toolkit, because the server name is a substring of every tool name.
- `select:` accepts a comma-separated list of any length, so one call can span several
  servers. I loaded 8 tools across 8 servers in a single call this session.

---

## 4. Connectors present in this environment that NEITHER skill mentions

Grouped by whether they earn a routing row for this project.

### 4a. Should be routed. These are directly useful to Can It Ford.

| connector | prefix | probed? | what it is good for here |
|---|---|---|---|
| **Scholar Gateway (Wiley)** | `mcp__88a938f6-f477-4a40-818a-eab819d8e81b__semanticSearch` | **YES, WORKS** | Full text of paywalled Wiley journals, above all *Journal of Flood Risk Management*, which carries Bocanegra 2019, Martinez-Gomariz 2018, Al-Qadami 2022 and Azhar 2026. Corpus updated May 2026. This is the one connector that reads the body of the literature the paper argues against. Returns chunk-level passages with DOIs, so it can settle "does this paper actually say X" without a PDF |
| **Scite-schema literature server** | `mcp__0712b3a5-e74c-446d-ac4f-f52280b84e24__search_literature` | **YES, WORKS** | Full-text excerpts plus Smart Citations with a `section` label, editorial notices, OA status and a resolved access URL, all without OAuth. The route the memory note "Scite excerpts when the PDF is blocked" describes, still live. Pass `dois` AND `term` together |
| **Exa web search** | `mcp__17d783e9-b8ba-4626-92d9-218ed2d88d76__web_search_exa` | **YES, WORKS** | Configured in the global `~/.claude.json` and named in neither skill. Returned the Zhao 2019 abstract, the TU Delft record with `10.1016/j.compfluid.2018.10.007`, pages 27 to 33, Computers and Fluids vol 179, matching what CLAUDE.md already records. Good for publisher pages, repository records and anything with no DOI |
| **Zotero's built-in Scite bridge** | `mcp__zotero__scite_check_retractions`, `scite_enrich_item`, `scite_enrich_search` | **YES, WORKS** | Whole-collection retraction sweep in one call. Verified 12 DOIs in `Paper cited - IEEEtran`, all clean |
| **Google Workspace via Zapier** | `mcp__36e3f815-...` and `mcp__3f46535f-...` | **partly** (`google_calendar_find_calendars`) | Gmail, Docs, Drive and Calendar in one bundle, including Docs read and write. The only route to Google **Docs** content. Costs Zapier task billing (`billingTasksUsed: 2` on one call), so prefer the native Calendar and Drive servers for reads |
| **Gmail (native)** | `mcp__460969e1-...` | no | Mentor and REU correspondence. Untested |
| **DeepWiki via connector** | `mcp__8fce264e-...` | no | Fallback if the bare `deepwiki` entry ever fails |

### 4b. Present, project-relevant, but incidental

- **Blender** (`mcp__Blender__*`, global stdio `uvx`). Directly relevant to the Cycles
  render stack in the memory notes. **UNTESTED**: it needs Blender running with the MCP
  add-on connected, and I did not start Blender.
- **Desktop Commander** (`mcp__Desktop_Commander__*`). Persistent shells and REPLs, SSH,
  ripgrep at scale, and reads outside the workspace. Relevant to the Vista and LS6 workflow.
  UNTESTED.
- **filesystem** (`mcp__filesystem__*`, Desktop layer). Reads outside the repo without the
  Bash permission prompts that blocked two of my checks tonight. UNTESTED.
- **MacOS-MCP** (`mcp__MacOS-MCP__*`). CLAUDE.md already carries a screen-recording
  permission note for its `Snapshot` tool. UNTESTED here.
- **sequential-thinking**, **mcp-registry**, **scheduled-tasks**, **terminal**,
  **ccd_session_mgmt**, **claude-in-chrome**, **computer-use**, **Control_Chrome**,
  **chrome-devtools**. Present. Not probed. `mcp__mcp-registry__list_connectors` WAS called
  and returned `{"connectors": []}` with a note that the card did not render, so it cannot be
  used to enumerate what is installed. Do not treat that empty list as an absence: it
  returned empty while dozens of servers were demonstrably live in the same session.
- **Word**, **PowerPoint** (`mcp__Word__By_Anthropic___*`, `mcp__PowerPoint__By_Anthropic___*`).
  Present. Relevant only if a deliverable ever needs .docx or .pptx.
- **ToolUniverse** (`mcp__ToolUniverse__*`), **wolfram duplicate**, **visualize**
  (`mcp__visualize__*`), **mermaid validator** (`mcp__e0bb6f21-...`), **three.js**
  (`mcp__076ab041-...`).

### 4c. Present and genuinely not a fit

Asana (`mcp__90153baf-...`), Linear-style issue tracker (`mcp__62d507fc-...`), Supabase
(`mcp__e1968daf-...`), Webflow (`mcp__8e6cb396-...`), Amplitude (`mcp__e8563865-...`),
Domo (`mcp__47fc8beb-...`), Coupler.io (`mcp__11231335-...`), Canva (`mcp__6dc4d270-...`),
Lucid (`mcp__b34ae897-...`), AWS (`mcp__AWS_API_MCP_Server__*`), Kubernetes
(`mcp__Kubernetes_MCP_Server__*`), the whole `plugin_bio-research_*` family (biorxiv,
clinical trials, ChEMBL, Open Targets, PubMed). Extend the global skill's "not a fit" list
to these, and **drop the entries in that list that are not present at all** (AllTrails, Box,
Tableau, Vercel, Spendflo, Indeed, Spotify, Strava), because listing an absent product as
"checked, not a fit" claims a check that never happened.

### 4d. Present but BROKEN, and the failure does not look like an auth failure

- **`mcp__memory__read_graph`** returns
  `Tool 'read_graph' has an invalid outputSchema: JSON Schema declares an unsupported
  dialect ("$schema": "http://json-schema.org/draft-07/schema#"). The default validator
  supports JSON Schema 2020-12 only`. That is a **harness-side schema-validation refusal**,
  not a server fault and not an auth fault. The `memory` server is from the Desktop config
  layer. Other `mcp__memory__*` tools may or may not carry the same dialect; I tested one.
  **Do not read this error as "the memory server is down".**

### 4e. Present in config but never observed as tools

- **`jupyter-executor`** (project-scoped stdio in `~/.claude.json`). No `mcp__jupyter*` tool
  name appears anywhere in this session's deferred list. Either it failed to start or it
  exposes no tools. Unresolved.
- **`scite`** (`.mcp.json` and project). No `mcp__scite__*` tool exposed; listed under
  "requires authentication" at session start. Consistent with the repo skill.
- **`hf-mcp-server`** (project). Listed under "requires authentication". The separate `hf`
  server covers the same product and works.

---

## 5. What a negative from a connector does and does not license

Carried forward from the repo skill because all four still hold, plus three new ones
measured tonight.

Unchanged:
- A zero from `research_index.py --query` is a literal substring match over title and
  abstract only. **Not an absence.**
- A partial count from `corpus_inventory` is a TCC denial. **Not an absence.**
- An OAuth prompt is not a failure, it is a connector that needs a human. Route around it.
- A subagent's absence result is not an absence.

New, from this probe:
- **A hard product error can be a wrong-surface error.** `Scholar_Sidekick` returning "not
  subscribed" while `scholar-sidekick` returns a full record is the proof. Before declaring
  a connector dead, check whether a duplicate prefix exists and try it.
- **A schema-dialect error is a harness refusal, not a server outage.** See `memory` above.
- **`mcp__mcp-registry__list_connectors` returning `[]` is not evidence that nothing is
  installed.** It returned `{"connectors": []}` this session while more than twenty distinct
  servers had already answered real calls in the same session.
- The repo skill's own generalisation, "an http entry with no `headers` block returns 401
  and that is a missing header, not a dead token", **is not the explanation for the github
  failure tonight**. That server has an `env` block and returns `Bad credentials`. Match the
  error string to the mechanism instead of reusing last time's diagnosis.

---

## 6. What I could NOT test, and why

Stated plainly so nothing here reads as a clean sweep.

1. **Scite (`.mcp.json` http entry).** Cannot be tested. No `mcp__scite__*` tool schema is
   exposed to load, and the session is non-interactive so the OAuth flow cannot be
   completed. Same for `hf-mcp-server` and the plugin servers listed at session start:
   `plugin:bio-research:{biorender,owkin,synapse,wiley}`, `plugin:data:*`,
   `plugin:engineering:{asana,atlassian,datadog,github,linear,notion,pagerduty}`,
   `plugin:slack-by-salesforce:slack`. **These need authorising by a human**, via claude.ai
   connector settings for claude.ai connectors and via `claude mcp` or `/mcp` in an
   interactive session for the rest.
2. **The Overleaf token file.** Bash permission was DENIED for both
   `wc -c /Users/josie/.config/overleaf-mcp/token` and `ls -l` on that directory. I
   therefore **cannot confirm the token is non-empty**, and the repo skill's stated
   precondition is not runnable under this permission set. The connector itself answered
   correctly, which is weaker evidence but is evidence.
3. **Blender.** Requires a running Blender with the add-on connected. Not started.
4. **Canva, Figma, Lucid, Gmail, Google Docs write paths, Desktop Commander, filesystem,
   MacOS-MCP, sequential-thinking, Word, PowerPoint, ToolUniverse, and every server in
   section 4c.** Present in the tool listing, not called. Presence is read directly;
   reachability is **unknown**.
5. **Every duplicate twin listed in 2c.** I probed the bare-name copy of each pair only.
6. **`jupyter-executor`.** Configured, no tools observed, cause not determined.
7. **Write paths anywhere.** Every probe in this document is read-only. Nothing was sent,
   posted, published, or modified through any connector. A working read does not prove a
   working write, and Overleaf, Slack, Gmail, Drive and Zotero writes are all untested.
8. **Whether any of this survives in a worktree.** I probed from the main checkout. The repo
   skill records that a worktree carries the skill file from its own branch point, and
   separately that a PreToolUse hook on the untracked `.claude/tooling/` blocked Bash from
   all 16 worktrees. `canford-corpus` and `canford-tacc` are launched from absolute paths
   under `.claude/tooling/`, which is untracked, so **a worktree may not have those files at
   all.** Unverified tonight.
