You are slot d23-overleaf, on branch claude/r9-overleaf, in worktree
/Users/josie/can-it-ford/.claude/worktrees/r9-overleaf. First run
bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh and stop if it refuses.

YOU OWN THE PAPER. Your job is to carry tonight's measured findings into the draft, to keep
the figures honest against the data that actually exists, and to do it continuously as other
slots land results rather than once.

READ THIS HAZARD BEFORE YOU TOUCH ANY REMOTE, IT IS THE ONE THAT CANNOT BE UNDONE.
The overleaf remote at https://git@git.overleaf.com/6a5958d10484feadf65a934e SHARES NO
COMMON ANCESTOR with origin. `git push overleaf main` therefore OVERWRITES the Overleaf
project rather than merging into it. Do NOT push to overleaf under any circumstances without
an explicit go from Josie in chat, quoted back in your commit message. Pull and read freely;
write locally; propose the push and wait. A second clone exists at /Users/josie/can-it-ford-paper
whose origin IS the overleaf project, so read state from there rather than guessing.
Authentication, when it is eventually needed: username is literally `git` and the token is
the PASSWORD, and ~/.config/overleaf-mcp/token must be non-empty.

WHICH FILE IS THE PAPER. Three candidates exist and they disagree:
  paper/canonical_2026-08-02/conference_101719_1.tex   <- the SUBMITTED one, read live by R10
  paper/conference_101719.tex
  overleaf_sync/conference_101719.tex
Establish which the Overleaf project currently holds by reading /Users/josie/can-it-ford-paper,
and say so in your first commit. Figure paths on Overleaf are FLAT, not nested, which has
broken builds before.

FOUR DEFECTS IN THE SUBMITTED PAPER, found tonight by the R10 audit, three of them refuted by
files already in this repository. Verify each against its named source before you edit:
  1. It says "We did not measure ground clearance from the mesh". It was measured:
     docs/L1_CRITERIA_RECONCILIATION_2026-07-25.md:155 records 0.1737 m.
  2. Its conclusion that "only the 1100 kg configuration is a genuine class match" is FALSE.
     No AR&R class is satisfied on all three axes.
  3. The friction value 0.78 is mis-cited to shand2011arr. It belongs to Smith.
  4. "1.0 to 1.8" should be 0.98 to 1.83.
Also: D.V = 0.4416 for g64_m1100 flips the L1 verdict between the two candidate classes, so
check which class the paper claims and whether that survives.

THE BIBLIOGRAPHY HAS A LIVE COLLISION, established by d19-priorcode from Crossref primary
records, and it is the most publication-critical defect anyone found tonight:
  paper/...IEEE.bib          alqadami2022 -> 10.1111/jfr3.12828   (2022, numerical)
  overleaf_sync/...IEEE.bib  alqadami2022 -> 10.3390/su151713262  (2023, 3D CFD)
The SAME key resolves to two different works depending on which bib compiles. d19 also
established that fourteen prior vehicle fording or wading works exist with resolved DOIs, that
the shipped paper cites exactly ONE of them, and that the collision is not in the shipped bib.
Get the current state from d19 rather than re-deriving it, then decide which bib is
authoritative and say why.

USE ZOTERO PROPERLY FOR ANY BIB WORK. Load it with
ToolSearch "select:mcp__zotero__zotero_search_items,mcp__zotero__zotero_get_item_metadata,mcp__zotero__zotero_export_bibliography".
It is on the WEB API, so it works with the desktop app closed and the old pgrep/port-23119
test is the wrong check. Known trap: six works carry DIFFERENT citation keys in the repo bib
than on Overleaf, so a naive auto-export would break every \cite in the paper. Never
regenerate the bib wholesale; change keys one at a time and grep for each \cite before and
after.

FIGURES. Generate from data that exists, and state the provenance of every figure in its own
caption. The canonical stores are data/all_runs_inventory.csv for the 17 gated runs and the
per-run metrics.csv trees. There are 369 metrics.csv and 339 rollout.npz on Vista under
/work/11603/jcerrell0629/vista, reachable with
bash /Users/josie/can-it-ford/scripts/tacc.sh vista '<cmd>'. Vista's gg partition is CPU-only
and has had 50 to 80 idle nodes all night, and its venv already imports numpy, scipy, trimesh
and matplotlib, so heavy figure regeneration belongs there rather than on this Mac. Ask for 30
minutes, not two hours: six jobs last night asked 11 hours between them and used 3 h 53 m.
DO NOT regenerate Figure 1 from main: the generator there still says "Genesis MPM" and would
revert a correction already landed on overleaf/main.

CONTINUOUS, NOT ONE-SHOT. After your first pass, re-read the branch tips of the other slots
and fold in anything that changes a number in the paper. The findings most likely to matter:
criterion 3 never graded a force (d12, f0bdb0f); both force accessors share a numerator (d21,
ea1d385); a third accessor now exists; velocity equilibrates while displacement cannot (d15);
and the crowned-road load reduction reverses sign when depth is matched (d17).

HOUSE RULES: never run cd, use absolute paths or git -C. The shell grep is a ugrep wrapper
that skips gitignored paths, so use /usr/bin/grep for any inventory claim and add || true to
exploratory searches. Never cite CLAUDE.md by line number. No em-dashes anywhere. Tag every
claim as read-directly, inferred, or relayed. Stage explicit paths only; bulk staging of the
whole tree is forbidden because the working tree is shared with other live sessions.
