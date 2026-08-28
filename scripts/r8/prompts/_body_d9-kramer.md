# SLOT d9-kramer

SCOPE. Worktree /Users/josie/can-it-ford/.claude/worktrees/r8-kramer, branch claude/r8-kramer
(off claude/r5-physics).

You may write ONLY, inside YOUR worktree:
  simulation/r5_physics/kramer_benchmark.py
  docs/R8_KRAMER_INTERCODE_2026-08-18.md   (new)
You MAY also extract into /Users/josie/can-it-ford-refs/2026-08-16/ , which is OUTSIDE the repo
by deliberate design because the repo is public and register E8 is open.
DO NOT commit any Kramer file into the repo.

NEVER TOUCH: simulation/r5_physics/sphere_heave.py; grade_job_b.py; any other branch; the main
checkout.

## WHERE THIS LEFT OFF
BLOCKER-B1 was "Kramer benchmark TIME SERIES unreachable (MDPI 403, DTU Cloudflare, OSTI
metadata only)". It is resolved and nobody noticed the size of what arrived.
/Users/josie/can-it-ford-refs/2026-08-16/energies-14-00269-s001.zip holds 78 entries:
  Datafile/Experimental results   28 entries   ALREADY EXTRACTED (27 series + Readme.pdf)
  Datafile/Numerical results      44 entries   NEVER EXTRACTED
  Datafile/Descriptions            4 entries   NEVER EXTRACTED
The 44 are ELEVEN INDEPENDENT CODES predicting the same benchmark: FNPF1, LPF0 to LPF4, RANS1 to
RANS5, each at drop heights 01D, 03D, 05D, plus "Description of numerical models.xlsx".
Descriptions holds "Details on sphere mass distribution and densities.xlsx" and a Solidworks CAD
model. `git grep -I -l "FNPF"` across every local branch head returns ZERO.
kramer_benchmark.py DEFAULT_ROOT (lines 51-52) points only at "Datafile/Experimental results".

## WHY THIS BEATS ANOTHER RUN
Job B's grade is +50.06 percent on the designated accessor, FAIL at every window, and
MANIFEST:214 says "Any FAIL stops the ladder." That number currently has NO CONTEXT: nobody
knows whether the five RANS codes agree with each other to 2 percent or to 40 percent on this
case. Reducing all 11 codes with the SAME damped-period and decay-envelope statistics
kramer_benchmark.py already applies to the four experimental repeats converts an unqualified
FAIL into a calibrated position in a published inter-model comparison. No GPU.

## ALSO IN SCOPE, a live physical assumption
sphere_heave.py:239 hardcodes added_mass_ratio = 0.5. Its own docstring at :293-300 says that is
"an ESTIMATE, not a source", that T ~ sqrt(1 + a33/m), and that raising it to 0.83 lengthens T_n
by about 10 percent and "shortens every reflection window in periods by the same factor. Any
reflection figure inherits this." Meanwhile kramer_benchmark.py:154-168 ALREADY DERIVES
implied_a33_over_m from the measured damped period and nothing consumes it. Report the measured
value and what every downstream reflection figure becomes under it. You may NOT edit
sphere_heave.py; you report the delta.

The WG1, WG2, WG3 wave-gauge columns are present in every series and parsed by nothing.
kramer_benchmark.py names them at lines 26, 27, 30, all docstring, and never reads them. They are
what separates radiation damping from viscous damping, the quantity the 0.5 stands in for.
Corroboration that a parse works: Te0 recovers as 0.756100 s from t/(t/Te0) on 01D rows 1 and 2.

## LICENCE
The Kramer 2021 supplementary is CC BY 4.0, so it MAY be redistributed with attribution. The
local copy's PROVENANCE.txt says it could not be obtained, which is now stale. Fix that text and
record the real source URL if you can recover it.

## FIRST STEP
  python3 -c "import zipfile; z=zipfile.ZipFile('/Users/josie/can-it-ford-refs/2026-08-16/energies-14-00269-s001.zip'); [print(n) for n in z.namelist()]"
Extract only the two missing subtrees, and read one numerical series header before writing a parser.

## DEFINITION OF DONE
1. All 11 codes reduced with the same statistics as the experimental repeats, one table, with
   the inter-code spread stated.
2. Job B's +50.06 percent placed against that spread, with an explicit statement of whether it is
   an outlier among published codes or inside their scatter. Do NOT re-grade Job B: the criterion
   was fixed in advance and re-scoring after seeing the failure is forbidden here.
3. The measured implied_a33_over_m reported, every reflection window recomputed under it, and the
   delta from the 0.5 estimate stated.
4. A verdict on whether WG1-3 can separate radiation from viscous damping on this data.
