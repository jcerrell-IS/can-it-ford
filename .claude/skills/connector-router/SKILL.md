---
name: connector-router
description: Use this on every turn as a standing check, not only when explicitly asked. Before answering a technical claim, citation, code-state claim, meeting/mentor question, or deadline question, check whether a connected tool should verify it first, per the routing table below, instead of answering from memory alone.
---

# Connector router (auto-trigger, no explicit ask needed)

## Why this exists
Josie asked for connectors to get checked automatically whenever a topic is a real fit, without naming the tool every time. This is that standing rule. It does not run outside an active turn, there is no background process, but inside every turn where this skill is loaded, run this check before answering rather than waiting to be asked.

## The routing table (chosen for real fit, not padding)

| Topic in the message | Connector | Why |
|---|---|---|
| Claim about how a GitHub repo actually behaves (kks32/mpm-engine, Genesis, PhysGaussian, gsplat, warp-mpm) | DeepWiki | Faster and more current than recalled knowledge; this project has hit real API disputes before |
| A physical parameter, unit conversion, or equation about to be used in a script or stated as correct | Wolfram Alpha | Cheap sanity check before it becomes a sim input or a claim |
| A specific citation, DOI, or paper finding about to go in the poster, paper, or a message to Kumar | Scite | This project has a documented history of misattributed citations |
| "Is this an established mechanism" question needing literature grounding, not one paper | Consensus or Scholar Gateway | Validates a real finding against the field, not one source |
| Claim about current code state, whether something is "done," or a specific number from a script | GitHub, live file read | The most repeated failure mode here is trusting a summary over the live file |
| "What did we decide," "what did Kumar/Hassan/Cheng-Hsi say" | Otter.ai, then Slack | Meeting transcripts are higher tier than a recalled summary |
| Deadline or scheduling question | Google Calendar | Direct source, do not infer from memory |
| "Do I have a file for X," "what is in my doc" | Google Drive or Docs | Direct source |
| Reading an uploaded Genesis/Newton/paper PDF for a specific detail | pdf-viewer or PDF Tools | Read the actual page, do not recall it |
| Gradio demo or HuggingFace deploy status | Hugging Face | Direct source |

## Explicitly not auto-routed, checked, not a fit for this project
AllTrails, AWS Marketplace, Box, Clinical Trials, PubMed, bioRxiv, Coupler.io, Tableau, Supabase, Vercel, Webflow, Spendflo, Indeed, Spotify, Strava. None touch Can It Ford or her coursework. Canva, Figma, Lucid are used only when actively building a visual, not as a background check. Do not call these reflexively just because they exist.

## The honest limit
This is a per-turn behavioral rule, not a standing background job. Nothing runs while no conversation is open. What it guarantees: in every future turn where this skill is loaded, the check happens before the answer, without her naming the tool.

## Refresh
Trigger: "update the connector router," or a new connector gets added to her account. Add or remove one row, echo a one-line diff.
