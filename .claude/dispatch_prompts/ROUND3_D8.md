# ROUND 3, D8 PREFLIGHT-RESCUE

Read `ROUND3_SHARED.md` first.

## You now own register_integrity.py. The deadlock is broken.

You, D1 and D11 each independently found that a denied `~/Downloads` makes the
checker report real citations as "may be fabricated", and all three of you
declined to fix it on ownership grounds. Three declines is a deadlock, not
caution, so it is assigned: **you apply your own four-point patch.**

You wrote the patch, you have 0 unpushed commits, and the file is tooling rather
than a claims file. Your stated reason for holding off was that changing its
output mid-reconciliation would muddy D4's results. That is handled by
sequencing, not by not fixing it: **you apply, you tell D4, D4 re-runs and
reports whether its reconciliation numbers move.** D4 has this instruction.

Corroboration for your patch from D11, measured inside a single session with the
register file unchanged: the tool moved from "10 research-artifact, 1
unresolved" to "0 research-artifact, 11 unresolved". 10 + 1 = 11 exactly, and
only `185968e0` was genuinely unresolved in both runs. Your independent
reproduction of register K0 line 648 (ten ids resolving on 2026-08-08, ten now,
so the eleventh entered after K0) is the third line of evidence.

**Add a fifth point to the patch**, because it removes the cause rather than
relabelling the symptom: the probe searches `~/Downloads` only. Every artifact
it fails on exists outside that directory. Verified at 22:38, 63 `.md` artifacts
readable at `/Users/josie/Claude/reu/`, mirrored under
`~/Documents/Claude/reu/` and in the Desktop corpus. Extend the resolver to
search those roots before it concludes anything, and have it report which root
resolved each id so a future reader can tell a real absence from a blocked view.

Your interim rule stays correct until this lands and should go in the code as a
comment: **a research-artifact count of 0 is a broken probe, not evidence about
the register.**

Your point about stakes is why this is being assigned rather than noted: two of
the ten are load-bearing. `65474f37` is the provenance audit for the canonical
`floor_friction`, and `5e706c91` is the forensic friction audit of the vendored
engine against this repo. A session acting on those warnings could soften ten
sound citations. Both are readable right now:

    /Users/josie/Claude/reu/compass_artifact_wf-65474f37-43a9-5ab0-817a-2b78217ff50f_text_markdown.md
    /Users/josie/Claude/reu/compass_artifact_wf-5e706c91-aee2-56f9-892b-f9b8b56051b6_text_markdown.md

Confirmed by reading 65474f37's own H1: "Citation Provenance Audit: The mu =
0.55 Friction Coefficient in Azhar, Pauwels & Bui (2023)". You are right that
the friction and citation *content* belongs to whoever owns those claims (D4
owns the register entry, D11 owns the provenance chain). Your scope is only that
the checker can now resolve them. Stay inside that.

## Your self-correction was right, keep the habit

You corrected 208 compass_artifact files to 40 files / 34 ids for
`~/Claude/reu`, and named why both numbers were right for different questions.
That is the discipline the shared addendum is asking for everywhere. One note:
my count at 22:39 was **63 `.md` files** in `/Users/josie/Claude/reu/` via
`ls *.md`. Yours was 40 files / 34 ids for compass_artifact specifically.
Different populations, both plausible. Re-derive and state which population your
number covers, so the two do not get read as a contradiction later.

## Scope discipline

You read no artifact contents, only resolved ids, and said so. Keep that. The
fifth patch point above is still id resolution, not content reading.

## Skills and state

Call `directory-provenance-audit`. Your branch has 0 unpushed and main is still
26 entries. When the patch is committed, stage explicit paths, max 8 files, and
hold the push pending Josie's per-branch check. No GPU needed. Vista queue empty
at 641 SU, LS6 unreachable non-interactively.
