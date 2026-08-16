# R5-D1 FLAG: items blocked on access, not on effort

Date 2026-08-17. Branch `claude/r5-research`. Written per the dispatch's standing
protocol: try a different approach, then a connector, then **write a named flag
file and keep working**.

**None of these is blocked on effort or ideas. Each needs a credential, a
browser, or a subscription that this session does not have.** Ordered by value to
the paper.

---

## FLAG-1. Nihei 2025 corrigendum content

- **DOI**: `10.1016/j.rineng.2025.107527`, corrigendum to
  `10.1016/j.rineng.2025.107189`.
- **Why it matters**: the original supplies the rolling-resistance figures
  **0.0250 and 0.0242** and the brake-state result that D4 built on in `cf9e85c`.
  Until the corrigendum is read, those numbers are **provisional**.
- **Routes tried, ten**: `doi.org`, ScienceDirect direct, `linkinghub`, DOAJ,
  Unpaywall, OpenAlex, Semantic Scholar, Europe PMC, the scite connector, and
  scite's licensed `getft.io` access link. Scite confirms the erratum
  relationship but holds no text; its access link 302s to the same 403 path.
- **Hypothesis tested and refuted**: that it is an author-name fix. Crossref
  author lists for the original and the corrigendum are identical.
- **Why I stopped**: the Elsevier landing page carries `tdm-reservation: 1`, a
  machine-readable opt-out from automated retrieval. Going further would be
  circumventing a stated access control.
- **UNBLOCK**: open `https://doi.org/10.1016/j.rineng.2025.107527` in a browser.
  About one minute. It is CC-BY once open. Report whether any numeric value
  changed.

## FLAG-2. Three closed-access full texts

| DOI | paper | why it matters |
|---|---|---|
| `10.1115/1.4071177` | He et al. 2026 | occupies the validation axis; the proposed L-7 amendment leans on it |
| `10.1007/s11433-023-2137-5` | Zhang et al. 2023 | closest method twin, GPU SPH vehicle wading. Its "validates code-to-code, not experimentally" is **MEDIUM confidence** and rests on a search-engine rendering |
| `10.1016/j.compfluid.2023.106144` | Lyu et al. 2023 | entirely particle-based 3D SPH vehicle wading |

- **Status**: all three `oa_status: closed`, no OA location in Unpaywall or
  OpenAlex, no repository deposit, no abstract in Crossref for two of them.
- **UNBLOCK**: institutional access. A UT Austin library proxy would resolve all
  three. Note that Al-Qadami 2023 was closed at the publisher and still obtained
  free via the UPCommons repository copy, so a repository search is always worth
  one try first; for these three it has already been done and returned nothing.

## FLAG-3. Nihei small-car drifting, measured values

- **DOI**: `10.2208/jscejj.24-16110`, Japanese Journal of JSCE, 2025.
- **Why it matters**: its abstract says full-scale drifting occurred at depth and
  velocity **smaller** than model-experiment thresholds predict, which is the
  strongest single statement found in this dispatch about model-scale thresholds
  being non-conservative. The actual numbers are in the body.
- **Status**: closed access, Japanese-language journal. Abstract read; body not.
- **UNBLOCK**: J-STAGE access, or a reader of Japanese with a subscription.

## FLAG-4. `martinezgomariz2018` bibliography entry

- **Where**: `paper/can_it_ford_references_IEEE.bib`.
- **Problem**: title is the literal placeholder `{{VERIFY: exact title}}`, with no
  DOI and no journal, so its intended referent cannot be determined from the
  entry. It is cited in zero `.tex` files, so this is latent, not live.
- **Why I did not fix it**: it is outside my declared scope, and guessing which
  Martinez-Gomariz paper was meant would be fabricating a citation.
- **UNBLOCK**: ask whoever wrote the entry which paper they meant. The same file
  has a second placeholder-title entry, `alqadami2022`, whose referent I *can*
  supply: `10.1111/jfr3.12828`.

## FLAG-5. Five Elicit rows with no resolvable DOI

Rows 14, 21, 24, 29 and 36 of the extraction CSV. Crossref bibliographic search
returned no confident match, best similarities 0.22 to 0.65. Row 24 is probably
the AR&R Project 10 material already in `citations/`, but the title does not
match closely enough to assert it.

- **UNBLOCK**: these are mostly grey literature (technical reports, conference
  material). A targeted search of UNSW WRL, Engineers Australia and national road
  authority repositories would likely find them. Low value relative to FLAG-1
  through FLAG-3.

---

## What is NOT blocked

Everything in D1's definition of done is complete and committed. The 28
non-catalog works are unread but readable at abstract level by anyone with time;
they were deprioritised on judgement, not blocked. See
`docs/R5_RESEARCH_INDEX_AND_ERRATA_2026-08-16.md` for the consolidated state and
for the errata table covering every number I withdrew.
