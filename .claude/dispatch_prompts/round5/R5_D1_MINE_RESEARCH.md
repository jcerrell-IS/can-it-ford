# D1 — MINE THE RESEARCH NOBODY READ
worktree `.claude/worktrees/r5-research` · branch `claude/r5-research`
YOU OWN: `docs/R5_RESEARCH_*`, `data/r5_citation_*`. Write nowhere else.

## WHY YOU EXIST
The previous round read ~12 documents out of ~400 and **never searched for
Elicit reports at all**. Two exist and both are unread:

**PATHS AND COUNTS CORRECTED BY THE COORDINATOR 2026-08-16, verified live.**
The bootstrap gave both files under
`~/Desktop/CAN_IT_FORD_MASTER_2026-07-26/05_REFERENCES/...`. That is WRONG.
That directory holds exactly ONE file, `_README.md`. Do not go there. The real,
readable locations, from a `find` across Desktop, Documents, Downloads and
Claude with no permission errors:

1. `citations/Elicit - Flood-Crossing Tire–Ground Friction and Speed Evidence.bib`
   **CORRECTED 2026-08-16 15:49 by the coordinator, who got this wrong once.**
   An earlier version of this line said the Downloads copy was "the ONLY copy
   on this machine". That is FALSE. There are 36 byte-identical copies,
   sha256 `e0d4d68a13e4ed0d`, and one of them sits in `citations/` in the repo
   root itself, plus one in every worktree. The original claim came from a
   `find` over Desktop, Documents, Downloads and Claude only, then asserted a
   machine-wide absence from that partial view. That is precisely the error
   CLAUDE.md names: absence of evidence from a partial view is not evidence of
   absence, and you must say which view you searched. Read the in-repo copy.
   2,622 bytes. **8 entries, not 7.**
   Read directly by the coordinator, so treat this list as verified, not as a
   claim to re-derive:
   - Varshney, Pasunurthi, Maiti, Srinivasan, Ranganathan & Ding 2021, "CFD
     Method Development for Simulating Water Fording for a Passenger Car",
     doi `10.4271/2021-01-0205`. **This is the fifth fording simulation.**
   - Nihei, Onomura, Bando, Inoue, Kashiwada, Yoshikawa & Tanaka 2025,
     "Full-scale experimental assessment of passenger vehicle stability in
     flooding flow", doi `10.1016/j.rineng.2025.107189`. Newer than anything in
     the register.
   - Abt, "Hydrodynamic effect on non-stationary vehicles at varying Froude
     numbers under subcritical flows on flat roadways", `jfr3.12657`.
   - Al-Qadami, Mustaffa, Al-Atroush, Martinez, Teo & El-Husseini 2022, "A
     numerical approach to understand the responses of passenger vehicles
     moving through floodwaters", `jfr3.12828`. CAUTION: register D4 `75eb2e9`
     warns the Al-Qadami Yaris datum is "the old misattribution again". Verify
     before you carry any number from this one.
   - Renfroe 1996, ATV tire friction, doi `10.4271/961000`.
   - Wasfy, Wasfy & Peters 2015, doi `10.1115/DETC2015-47142`. **Already known**
     to the project, NIGHT_FINDINGS section 8. Not new.
   - Smith, Modra, Tucker, Cox & Felder 2017, `10.26190/unsworks/27416`, and
     the Martinez-Gomariz methodology PDF. **Both already known.** Not new.
   **ALSO CORRECTED 2026-08-16 15:49, and this one was wrong too.** This line
   used to read "the novelty correction rests on Varshney 2021 alone". Varshney
   2021 was NEVER a new find: it is already in
   `docs/Dynamic_Vehicle_Traction_in_Floodwater.md` as row 38 and again at
   :389, and row 37 is a SECOND, uncounted Varshney moving-mesh wading paper
   (2022). D1 established the real figure by cross-referencing all 14 catalogs
   against 772 repo text files: **15 vehicle-in-water simulations exist, 12 of
   them uncited.** Not four, not five. The authority is D1's own
   `data/r5_citation_xref.tsv`, not this paragraph.

2. `/Users/josie/Downloads/can-it-ford-main/citations/Elicit - extract-results-review-5e368aae-95c3-4774-a804-2dcc8899299e.csv`
   Second identical copy (same sha256 `b90b396e...`) at
   `~/Desktop/_ARCHIVE_2026-07-26/02_snapshots_older/CAN_IT_FORD_ARCHIVE_2026-07-25_2355/04_data/`.
   **IT IS 42 DATA ROWS AND 27 COLUMNS, NOT 1,345 ROWS.** The bootstrap's
   "1,345 rows" is a `wc -l` of 1,346 physical lines on a file whose
   "Supporting quotes" columns contain embedded newlines inside quoted fields.
   Parsed with `csv.reader` it is 42 records. That is a 32x overstatement of
   the corpus size and you must not repeat it anywhere. Forty-two papers with
   extracted thresholds is still worth mining; 1,345 was never there.
   The two columns that matter are `[08]` "Depth-velocity threshold or critical
   depth reported for vehicle instability, with units" and `[09]`
   "Driving/propulsive force or rolling friction coefficient used or measured".
   Columns `[15]`-`[20]` carry the supporting quotes and reasoning for both, so
   every extracted value has its evidence in the same row. `[11]` is "Vehicle
   motion state: stationary, towed, or self-propelled", which is directly the
   L-1 stationary-vehicle question.

Also unmined: the settling report's **68-paper** catalog and the
multi-resolution report's **78-paper** catalog. Reading catalogs rather than
summaries is what surfaced four uncited fording papers last round.

## FIRST STEP
`corpus_inventory`, then read the Elicit .bib in full. Verify every DOI with
scite or scholar-sidekick before using it: scholar-sidekick catches a real DOI
paired with an invented title, which resolveIdentifier cannot.

## DEFINITION OF DONE
(a) A cited-versus-catalogued TSV over every DOI in all six Undermind catalogs
plus the Elicit outputs: doi, title, source, cited-in-repo yes/no, sorted
uncited-first. (b) The corrected novelty statement: it is **five** fording
simulations, not four, unless you find more. (c) A table of every depth-velocity
threshold and friction coefficient the literature actually reports, with units,
mined from all 42 rows of the CSV. State which rows you could not parse, and
give the denominator every time: it is 42, never 1,345.

## STANDING PROTOCOL (identical for all four, read once)
Before starting: read `/Users/josie/can-it-ford/.claude/tooling/ERRORS_AND_RESOLUTIONS.md`,
then `git log`, then `/Users/josie/can-it-ford/.claude/state/round5_board.md`.
Do not duplicate a sibling; append your own row to the board after each unit.

SELF-SUFFICIENCY. Decide for yourself. If a path, file, number or citation is
uncertain, GO FIND IT rather than asking: `corpus_resolve`/`corpus_search` for
any research file, `scite` or `scholar-sidekick` for any DOI, `wolfram` for any
unit or parameter, `deepwiki` for library behaviour (treat as hypothesis, verify
against source), `canford-tacc` for anything on Vista or LS6. If blocked, try a
genuinely DIFFERENT second approach, then write a named flag file and KEEP
WORKING on the rest of your scope. One blocker never ends a session.

CLAIM DISCIPLINE. Tag every claim: read directly / recalled / inferred. Report N
and spread, never a single draw. State the settle length behind any simulation
number. Run the physics-skeptic subagent before finalising any percentage,
force, verdict count or distance; if unavailable, say so and mark it UNREVIEWED.
An import succeeding is not an environment working. An empty result from one
directory is a broken probe, not an absence.

GIT. Commit each coherent unit as you finish it, path-limited:
`git commit -m "msg" -- <paths>`, 8 files max. Never bulk-stage. NEVER push. The
repo is PUBLIC. Writing to an absolute /Users/josie/can-it-ford/... path from
your worktree lands in the MAIN checkout: use paths relative to your own tree.
Never edit CLAUDE.md, the register, or sim_standing.py.

WHEN YOU FINISH A UNIT, keep going. Pick the next highest-value item in YOUR
scope. The auto-dispatcher will also nudge you, but do not wait for it.
No em-dashes.

