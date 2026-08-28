# ROUND 3, D7 CORPUS-SPRINT2

Read `ROUND3_SHARED.md` first.

## Your manifest blocker is a size limit, not a permission. It is readable.

You reported: "Manifest appends remain impossible: I cannot read the file, and
writing blind would destroy 6,241 rows."

Measured live at 22:43:

    /Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13/00_RESEARCH_MANIFEST.tsv
    6242 lines  (6241 rows + header, exactly your number)
    3,383,152 bytes
    mode -rw-r--r--  owner josie:staff
    header: original_path  symlink_name  facet  source_type  date  date_source
            keywords  verdict  status

I read it. It is not permission-denied. **A whole-file Read fails on size, and
you concluded the file was unreadable.** Those are different failures with
different fixes, and this is the fifth instance of that conflation today.

You never needed to read it whole to append to it:

- Targeted reads: `sed -n '1p;4000,4020p' <manifest>`, `awk -F'\t' '$8=="UNCLEAR"'`,
  `/usr/bin/grep -c` for counts. Read the slice you need.
- Appends: `>>` never rewrites the existing rows, so a blind append cannot
  destroy 6,241 rows. Guard it anyway: record `wc -l` and byte size before,
  append, then assert the line count rose by exactly the number of rows you
  added and the first 6,242 lines are byte-identical (`head -6242 | shasum`
  before and after).
- Never rewrite the file in place without a `_BUILD_LOG/*.bak.tsv` snapshot
  first. You already have that convention: three `.bak.tsv` snapshots are in
  `_BUILD_LOG/`. Keep using it.

So: **the 276 REU `.md` files can be verdicted this pass.** That was your only
stated reason for deferring them. Do it.

## Your relays landed, both of them

**82c51733 went to D6 and it was the right call.** You said "That artifact is
directly on the question and nobody has opened it. Read it next." I opened it to
confirm the routing: it is "Code-Level Analysis: PLY Loading in kks32/mpm-engine
(splats module & load_vehicle)", and its TL;DR names `load_vehicle()` in
`src/warpmpm/vehicle.py` delegating to `load_gaussians_ply()` in
`src/warpmpm/splats/io.py`. D6 has it, with the readable path, and it is D6's
own highest-leverage gap.

**Isik and He 2023 went to D4.** Your correction (Comp. Particle Mech.
10(3):503-517, not 2022) matters more than a year fix: the project CLAUDE.md
currently says 2022 in its research-integration section. D4 will record it in
the register. **Nobody edits CLAUDE.md**, that is the 2026-08-07 breach pattern,
and it is flagged to Josie as needing a single-owner edit.

## One claim of yours to re-check before it hardens

You wrote that no flood-vehicle study has shown mesh resolution moving the
predicted stability threshold, so the Silverado SLIDE-to-STUCK flip between g96
and g128 is unprecedented rather than embarrassing.

The first half is a CLAUDE.md standing rule and stands. The second half needs a
qualifier that arrived after you wrote it: D5 established that the flip is
**friction-dependent**, requiring mu at or above roughly 0.40, and register J15
had already published the same flip from plain shared-n_grid refinement. So it
is a resolution-at-a-given-friction result, not resolution alone. Keep the
framing, add the mu.

## Your next scope

1. Verdict the 276 REU `.md` files into the manifest, using the append pattern
   above.
2. Add the five unindexed REU knowledge-base docs you already identified
   (`DesignSafe_TACC_playbook.md`, `INDEX.md`, `_SUPPORTING_REPOS.md`,
   `WEEK1_PREP_STUDY_GUIDE.md`, `PyTorch_Geometric_cheatsheet.md`), one row each.
3. Publish, as a small standalone TSV, the **id-to-readable-path map** for all
   63 artifacts in `/Users/josie/Claude/reu/`. Five sessions reported artifacts
   as unreadable this round because they only checked `~/Downloads`. A map that
   resolves an 8-hex id to a path outside the blocked directory prevents the
   next five.
4. Your `00_COMPASS_ARTIFACT_SUBJECT_INDEX_v2_2026-08-14.tsv` has 41 artifacts
   with titles read from the actual H1. There are 63 `.md` artifacts in
   `~/Claude/reu` alone. Reconcile the gap and say what the 22 are.

## Skills and state

Call `directory-provenance-audit`. No GPU needed. Vista queue empty at 641 SU,
LS6 unreachable non-interactively.
