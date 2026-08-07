# Things only you can do, 2026-08-07

Everything in this file is blocked for an agent session for one of three
reasons: it needs an interactive OAuth flow, it lives on a claude.ai server that
the CLI cannot address, or it is a judgement call about your research that
should not be made for you.

Ordered by payoff. Items 1 and 2 take about five minutes together.

---

## 1. Remove 32 connectors at claude.ai (Claude chat and Cowork)

**Why this cannot be done from here.** `claude mcp remove` reaches only the
local, user and project scopes. The claude.ai connectors live on Anthropic's
servers under a `claude.ai config` scope; I confirmed by attempting a removal and
getting "No MCP server named...". Claude Code no longer loads them for this
project (`disableClaudeAiConnectors: true` in `.claude/settings.json`), but
**Claude chat and Cowork still do**, and every one of them competes for tool
selection on every message you send.

Go to **claude.ai → Settings → Connectors** and disconnect these 32:

| | | | |
|---|---|---|---|
| Postman | Supabase | Webflow | Three.js 3D Viewer |
| Vercel | Coupler.io | Tableau | Sentry |
| Jam | Spendflo | Atlassian Rovo | Figma |
| Strava | Slack | AllTrails | Spotify |
| Zapier | Zapier (2) | Lucid | Box |
| Clinical Trials | Goodnotes | Amplitude | bioRxiv |
| Microsoft 365 | Indeed | PubMed | Canva |
| AWS Marketplace | Elicit | Exa | Context7 |

Elicit, Exa and Context7 are on the remove list only because you already have
them as CLI-scoped servers in Claude Code; removing the claude.ai copies removes
a duplicate, not a capability. Clinical Trials, bioRxiv and PubMed are biomedical
literature: this project is flood hydraulics and vehicle stability.

**Keep these 6:** Otter.ai (mentor-meeting transcripts, which the
`reu-research-log` skill depends on), Gmail, Google Calendar, Google Drive (REU
deadlines and the stipend-gating paper), Scholar Gateway (citation integrity),
Mermaid Chart (figures).

Reversible at any time from the same screen.

## 2. Re-authenticate undermind

I broke this and could not fix it non-interactively. When I removed what looked
like a duplicate local-scope entry, the remove/add cycle cleared its stored OAuth
token. The config is restored byte-for-byte, but the token is gone.

In an interactive `claude` terminal in this repo, run `/mcp`, select
**undermind**, and authenticate. Success looks like `undermind ... ✔ Connected`
in `claude mcp list`. Until then it reports "Needs authentication" and its
literature-search tools will not run.

## 3. Open Zotero desktop before any citation work

Verified 2026-08-07: Zotero desktop was **not running** and port 23119 was
**closed**, while `claude mcp list` still reported zotero connected. In that
state searches return empty instead of erroring, so a session concludes "not in
your library" and is wrong.

There is a second, sharper trap underneath it. The **user-scope** zotero entry is
a bare `zotero-mcp` with no environment at all. The API key, library ID and
library type live only in the **local** (Can It Ford) entry. So in any other
project, Zotero connects and silently returns nothing.

If you want Zotero to work everywhere, copy the four env vars from the local
entry to the user-scope one. If you only ever use it here, leave it and just
remember to open the desktop app first.

## 4. Decide the `xia2013` year. This is a research call, not a cleanup.

`paper/can_it_ford_references_IEEE.bib:108` currently reads:

    year = {2013}, volume = {70}, number = {2}, pages = {1619--1630}

Volume 70(2) pp.1619-1630 is the **January 2014 print issue**, so the entry
contradicts itself. Two deliberate decisions are in conflict: `year = {2013}`
landed in commit `f9bf0f9` on 2026-07-21 with the note "Renamed from key xia2014,
confirmed 2026-07-20", and a Crossref check on 2026-07-30 concluded 2014 and was
never applied.

Either move the year to 2014 (the citation key can stay `xia2013`, nothing else
breaks) or drop the volume and issue. I did not choose for you.

**Do not "simplify" this into one Xia paper.** There are two, and both are cited
for different failure modes:

| key | paper | mode | online | print |
|---|---|---|---|---|
| `xia2010` | Formula of Incipient Velocity for Flooded Vehicles | SLIDE | 2010 | 2011 |
| `xia2013` | Criterion of Vehicle Stability in Floodwaters | TOPPLE, DRIFT_THRESHOLD | 2013 | 2014 |

Each has two defensible years, so a bare year in prose is ambiguous rather than
wrong. `scripts/check_claims.py` rule C9 now warns about exactly this.

## 5. Merge register entries K2 and K4 when only one session is open

This is the one repo task I could not safely do. At the time of writing, **three
other Claude sessions were live in this repository**, with
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` modified and uncommitted.
Editing it does a read-modify-write, so racing them could destroy their work.
CLAUDE.md's standing rule against two panes touching one file applies.

When you have a single session open, pull these into the register from
`docs/INFRA_SESSION_FINDINGS_2026-08-07.md` (already committed and pushed):

- **K2 is wrong.** It describes a slow first-import from a `gsplat_env` on Lustre
  scratch and sets a standing rule to "wait 3-5 minutes before assuming failure".
  There is no working gsplat environment on LS6 at all: no `torch` in any
  site-packages, `$SCRATCH/python-envs` absent, `$SCRATCH/gsplat` is a source
  checkout, and `my_gsplat_env` on `/home1` holds only pip and setuptools. The
  import fails instantly with `ModuleNotFoundError`, so the wait rule is harmful.
- **K4 resolves to YES, not open.** drainA training completed **2026-07-20
  19:57**, 30,000 steps across 3 ranks: `ckpt_29999_rank{0,1,2}.pt`, and
  `stats/val_step29999.json` giving **PSNR 22.7356, SSIM 0.8249, LPIPS 0.3112,
  399,491 Gaussians**, plus `videos/traj_29999.mp4`.
- **The trap under K4:** `cfg.yml` has `save_ply: false`, so no PLY was written at
  30k. The only PLY on disk is `point_cloud_2999.ply` from the 2026-07-17
  3,000-step run. Anything downstream reading a drainA PLY is reading a 3k model.
  Re-export from `ckpt_29999_rank0.pt`; do not retrain.

## 6. Optional: rotate the Hugging Face token

You said you did not care about the exposure, so this is recorded, not urged.
`~/.claude.json` holds a classic **write-scoped, account-wide** HF token in
plaintext. If you ever want it narrowed, revoke "Can it ford" at
huggingface.co/settings/tokens and issue a fine-grained token limited to the
repos you actually touch.

---

# Paste this into a claude.ai Project (for Claude chat and Cowork)

Claude chat cannot read `CLAUDE.md`. Create a Project called **Can It Ford** and
paste the block below into its custom instructions. It is the compressed set of
things that have actually gone wrong, not a summary of the project.

```text
Project: Can It Ford. Flood-vehicle stability via MPM simulation, TACC Vista and
LS6, REU under Krishna Kumar. Output is a paper and a poster.

VERIFICATION IS THE JOB. Never state a parameter, threshold, citation, file path,
engine identity or milestone as fact unless I have pasted the live source in this
conversation. You cannot read my repo. If you have not seen it here, say "I have
not verified this" rather than asserting it. A claim repeated from a summary, a
prior chat, or your own earlier message is not evidence, and a claim cited twice
from one origin is one source, not two.

ENGINE. The 17 gated runs use warpmpm via renders/yaris_render_s1/sim_standing.py.
They are NOT Genesis. Genesis is only a separate box-proxy path and has never
loaded the Yaris hull. Never label the gated runs Genesis in a figure, caption,
README, poster or the paper.

NUMBERS THAT ARE ALREADY WRONG. Do not reuse these:
- the 100-300 kg/m^3 density band is stale; the canonical Yaris hull is
  310.494 kg/m^3 and all 17 runs realise 302.55-663.58
- grid_density >= 96 is not the crash threshold, and 64 is not confirmed safe
- fill_ratio 2.17, 7.71 m^3 and 143 kg/m^3 are retired
- 1609 kg and 2337 kg have no source; do not call the mass sweep "cited classes"
- DRIFT_THRESHOLD 0.05 m has no peer-reviewed source
- no gate is a physics validation; every gate is a self-consistency check

RESULTS ARE BINARY. The grid study is non-monotone and unconverged: displacement
moves +87.8% then -59.2% across g48/g64/g96. Cite the NO-FORD verdict, never a
displacement magnitude.

SCOPE. The thresholds describe a STATIONARY vehicle in flow, so the tank setup is
the right match and the word "ford" in the title is what mismatches, not the
simulation. The 3.0 m/s cap is administrative, not vehicle-derived.

ALLOCATION. Vista is the constraint: 673 SUs left on 2026-08-07, expiring
2026-09-30. Interactive idev sessions consumed 99.1% of all node-time while every
gated run took 1 to 4 minutes as a batch job. Never suggest idev for work that
fits in sbatch.

STYLE. No em-dashes, ever. State what success looks like and the most likely
failure mode. Give exact commands, not vague suggestions. If you are unsure, say
so in one line and continue; do not pad.
```

# Cowork

Cowork shares the claude.ai connector set, so step 1 improves it directly and is
the single highest-leverage change available there. Cowork reads files you attach
rather than your local repo, so the Project instructions above are the mechanism
that carries this project's rules into it.

The most useful things to hand Cowork for this project are
`data/all_runs_inventory.csv` (the 17-run store, not `gates_results.json`, which
holds 3 dry_start records and no pass/fail field) and
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`.
