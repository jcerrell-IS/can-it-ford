You are slot d22-gapscan, on branch claude/r9-gapscan, in worktree
/Users/josie/can-it-ford/.claude/worktrees/r9-gapscan. First run
bash /Users/josie/can-it-ford/scripts/r8/r8_preflight.sh and stop if it refuses.

YOUR JOB IS ACQUISITION AND GAP SCANNING. Every other slot works from what the project
already has. You are the only one whose job is to go and GET what it does not have, and to
say what it still does not have when you are done.

WHY YOU EXIST, measured tonight and not to be re-derived:
  - The research corpus index at data/research_corpus_index.json holds NO FULL TEXT. Its
    records have 15 fields and none is a body or a PDF path; the largest text blob in the
    whole file is 3,477 characters; 110 of 332 records have no abstract at all. It is a
    DISCOVERY instrument, not a reading one.
  - It is built from 8 of the roughly 21 deep searches in Undermind workspace
    17299f2a-8dc8-438b-8c84-5abf19395e2c. Thirteen have never been ingested, and four of
    those are the ones the project most needed.
  - Of the works the paper cites, most are absent from the corpus entirely, so corpus
    coverage cannot answer what the paper cites.
  - Six papers were read from full text tonight via the Undermind connector. The working is
    in docs/R9_CORPUS_READ_2026-08-19.md. Do not re-read those six: Wal07, Ste08, Miy23,
    Qui18b, Zha22d, Neg22.

THE PIPELINE YOU OWN, in order:

1. BUILD THE WANT LIST. Assemble every work this project needs, from: the 21 deep searches
   (inspect each one via the connector, not via the index), the paper's bibliography, the
   corrections register, CLAUDE.md, and the reference lists of the six papers already read.
   Deduplicate by DOI where present and by title otherwise. State the total.

2. RESOLVE EACH AGAINST DISK. Search /Users/josie/Downloads (about 170 PDFs),
   /Users/josie/Desktop including /Users/josie/Desktop/CAN_IT_FORD_RESEARCH_CORPUS_2026-08-13,
   /Users/josie/Documents (about 157), /Users/josie/Zotero/storage (about 25) and the repo's
   citations/ directory. Match on DOI, arXiv id, and title. Read the FIRST PAGE of a
   candidate to confirm identity before claiming a match, because filenames lie.

3. FOR EVERYTHING NOT ON DISK, GO AND FIND IT ON THE WEB. This is the part Josie asked for
   explicitly and it is the core of your slot. Use WebSearch and WebFetch. Try, in order:
   the DOI resolver, arXiv, the publisher page, an institutional repository, the author's
   own page, and any open-access mirror. When you find a legally readable full text, READ IT
   and extract what bears on the open questions below. When you find only an abstract or a
   paywall, SAY SO EXPLICITLY and record it as unobtained rather than quietly citing the
   abstract as though you had read the paper. That distinction is the whole point of this
   slot: this project has been burned by claims sourced from titles and summaries.
   Where a PDF is legally downloadable, save it under data/r10_acquired/ with a filename
   carrying its DOI or arXiv id, and record provenance.

4. SCAN THE WEB FOR WHAT NOBODY HAS ASKED. Beyond the want list, search for recent work
   (2024 to 2026) that would change this project's direction and that nobody here has seen.
   Cover at least: MPM and SPH volumetric locking and pressure oscillation remedies; force
   extraction on rigid bodies in particle methods; well-balanced and hydrostatic-consistent
   particle schemes; vehicle fording and wading simulation; flood vehicle stability
   experiments; and whether anyone publishes a SAFE SPEED SURFACE, v_max as a function of
   depth and flow velocity, which this project believes is the open gap. Report what is new
   since the project's own searches were run.

THE OPEN QUESTIONS, so you can judge relevance. Can It Ford simulates a vehicle in
floodwater with warpmpm, NOT Genesis.
  a. A rigid sphere held fixed at its waterline reads a vertical force +34 to +64 percent
     above analytic buoyancy across 24 gradings, and refinement does not fix it. Live
     candidate mechanisms: volumetric locking and per-particle pressure oscillation (Zhao,
     Jiang, Choo, CMAME 2023, arXiv 2209.02466); velocity-projection bias for a FIXED body
     (Wallstedt and Guilkey 2007); wall momentum zeroing distorting stress several grid
     lengths into a body (Schneider et al 2019, image particles, NO PDF retrievable, GET IT);
     residual non-quiescent motion.
  b. A hydrostatic column never goes quiet: kinetic energy GROWS, 11 orders of magnitude
     above Quinlan 2018's machine-zero well-balancedness standard.
  c. Two force accessors differ by a factor of two and disagree on sign.
  d. Moving vehicle runs exist in ground frame but fail a frame check at 34 percent.
  e. Which realism effects change a stability VERDICT rather than only appearance.
  f. Vehicle mesh assets and their licences: the documented CCSA/NCAC set is Yaris, Camry,
     Silverado, and no redistributable general-purpose conversion has been verified.
  g. In and outflow boundary conditions: Zhao et al 2019, Computers and Fluids 179, 27-33.

HOUSE RULES, follow them or your output is unusable:
  - NEVER run 'cd'. Use absolute paths or git -C.
  - The shell 'grep' here is a ugrep wrapper that SKIPS GITIGNORED PATHS. Use /usr/bin/grep
    for any inventory claim, and add '|| true' to exploratory grep and find.
  - Never cite CLAUDE.md by line number. Quote the heading and the sentence.
  - No em-dashes anywhere.
  - Tag every claim as read-directly, inferred, or relayed. Never state a number from memory
    when you could check it live.
  - To read a PDF use the Read tool with the 'pages' parameter, at most 20 pages per call.
    There is no pdftotext on this Mac.
  - Load connector tools with ToolSearch before calling them, for example
    ToolSearch "select:mcp__undermind__inspect_deep_searches,mcp__undermind__read_pdfs".

WRITE docs/R10_WEB_ACQUISITION_2026-08-19.md with: the want list total; how many resolved on
disk; how many you obtained from the web and read in full; how many you could reach only as
an abstract; how many you could not reach at all, each with the barrier you hit; then the
findings ordered by what they change, then a section naming what is STILL missing and what
it would take to get it. A coverage number without its complement is not a coverage number.

Commit as you go, staging explicit paths only. Bulk staging of the whole tree is forbidden
in this repo, because the working tree is shared with other live sessions and a blanket
stage captures their uncommitted work under your message. Your write scope is
docs/R10_WEB_ACQUISITION_2026-08-19.md, docs/r10/ and data/r10_acquired/.
