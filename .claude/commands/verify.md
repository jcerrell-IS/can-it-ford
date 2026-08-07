---
description: Verify a claim traces to a primary source before it is stated as fact, written into the paper, or reported to Kumar
argument-hint: "<the claim, e.g. 'gravity in the 17 gated runs is 9.81'>"
---

Verify this claim: **$ARGUMENTS**

Delegate to the `provenance-verifier` subagent. It is read-only and returns a
verdict with evidence rather than editing anything.

While you wait, do not pre-empt its answer, and do not restate the claim as
settled in your own words.

When it returns:

- If VERIFIED, give me the `path:line` or the host and command it used. A verdict
  without a locatable source is not a verdict.
- If REFUTED or UNVERIFIED, say plainly what was standing in for evidence. The
  usual culprits here are a skill file, a session summary, a dated audit doc, or
  CLAUDE.md restating a fact rather than sourcing it. A claim cited twice from
  the same origin is one source, not two.
- If CONFLICTS lists other live values, show all of them with paths. This repo
  has known forks: four live vehicle densities, two gravity constants, and
  DRIFT_THRESHOLD declared as a literal in 16 places under four names.

Then tell me whether the claim is safe to put in the paper, the poster, or a
message to Kumar, and if not, exactly what would settle it.

Do not fix anything you find. Changing a parameter changes physics results.
