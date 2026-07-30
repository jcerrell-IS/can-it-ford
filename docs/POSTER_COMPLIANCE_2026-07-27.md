# Poster compliance audit against Instructions.docx.md

Checked live 2026-07-25. Source of requirements: `Instructions.docx.md` (2193 B, mtime
2026-07-15 01:05), the only copy on this machine. No original `.docx` and no poster-resources
folder are present locally.

Artifacts audited: `poster.html`, `Cerrell_TACC_42x56.pdf` (repo root, 403657 B, 17:45:06),
`figures/Cerrell_TACC_42x56.pdf` (404092 B, 17:13:54).

Deadline: **Monday 2026-07-27, 09:00 CST. Final.** Late upload transfers printing cost and
arrangement to the presenter.

---

## A. Hard submission requirements

| # | Requirement, as written | State | Verdict |
|---|---|---|---|
| 1 | "The dimensions of the poster must not exceed 42" x 60"" | `@page { size: 56in 42in }` at `poster.html:7`, `.poster` width 56in height 42in at `:20-21`. PDF MediaBox 4032 x 3024 pt = 56.00 x 42.00 in | **AMBIGUOUS, resolve before Monday.** See section B |
| 2 | "Preferred poster size: 42x56" | Poster is 56 x 42, the same size rotated to landscape | See section B |
| 3 | "Files cannot be larger than 40MB" | 404092 B = 0.39 MB | **PASS**, 99 percent headroom |
| 4 | "Save your file as: Last Name_TACC_Poster Size" example `Gomez_TACC_42x56` | `Cerrell_TACC_42x56.pdf` | **PASS** on pattern. See section B on the size token |
| 5 | "must be uploaded in PDF format" | Valid 1-page PDF, producer Skia/PDF m150 (Chrome print of `poster.html`) | **PASS** |
| 6 | "in the Final Posters folder no later than Monday, July 27 at 9am CST" | Not verifiable from this machine | **OPEN, presenter action** |
| 7 | "Sign up for a mock poster presentation time" | Not verifiable from this machine | **OPEN, presenter action** |

## B. The one requirement that is genuinely at risk

The poster is **56 in wide by 42 in tall**, landscape. The instruction states a preferred size
of **42x56** and a maximum of **42" x 60"**.

Two readings, and they disagree:

- **Reading 1, size as an unordered pair.** "Not exceed 42 x 60" means the short side may not
  exceed 42 and the long side may not exceed 60. A 56 x 42 poster has a short side of 42 and a
  long side of 56, so it complies, and `42x56` is the correct size token for the filename.
  Under this reading nothing is wrong.
- **Reading 2, width by height.** The preferred size is 42 wide and 56 tall, portrait, and the
  maximum is 42 wide and 60 tall. A 56 in width then exceeds the 42 in limit and the poster is
  non-compliant, and the filename says 42x56 while the page is 56x42.

Both readings are defensible from the text. The instruction never uses the words width, height,
portrait or landscape.

**Recommended action, and it is cheap.** Send one message to Rosalia Gomez or the TACC Education
and Outreach team asking whether a 56 x 42 landscape poster is acceptable, before Monday 09:00.
Do not rotate the layout on a guess: `poster.html` is a fixed-dimension CSS grid built for
landscape, and re-flowing it to 42 x 56 portrait would reposition every block and require the
figures to be re-fitted. That is a layout rebuild, not a page-size change, and it is not worth
doing unless the answer comes back that landscape is disallowed.

## C. Content requirements

| # | Requirement, as written | Where it is satisfied | Verdict |
|---|---|---|---|
| 8 | Introduction includes "Full Name" | `poster.html:250`, "I am **Josie Cerrell**" | **PASS** |
| 9 | Introduction includes "Major and Institution" | `:250`, "an **Integrated Sciences** major at **Claremont McKenna College**" | **PASS** |
| 10 | Introduction includes "Mention REU Program and Mentors" | `:250`, names the NSF REU Site by full title, TACC, UT Austin, GeoElements Lab, PI Dr. Krishna Kumar, and mentors Hassan Iqbal, Cheng-Hsi Hsiao and Sarah Etter | **PASS** |
| 11 | Introduction includes "Research project" | `:252`, the flooded-road framing and the world-model blind spot | **PASS** |
| 12 | Acknowledgments "thank the National Science Foundation" | `:354`, named | **PASS** |
| 13 | Acknowledgments thank "The University of Texas at Austin Texas Advanced Computing Center" | `:354`, exact phrase present | **PASS** |
| 14 | Acknowledgments "cite the NSF REU Site: Cyberinfrastructure Research for Societal Advancement, Award # 2447887" | `:354`, exact title and award number present | **PASS** |
| 15 | "Consider your target audience (general audience)" | Introduction opens on drivers and invisible hazards before any technical term | **PASS** |
| 16 | "Emphasize the relevance/significance of the project (societal impact)" | `:252`, "Flooded roads kill people who could not tell they were dangerous" | **PASS** |
| 17 | "Highlight future directions" | `<h3>Future directions</h3>` at `:344` | **PASS** |
| 18 | "Limit yourself to a few key analyses/data points" | Two figures on the board: the pipeline diagram and the L1 three-class grid | **PASS**, arguably under-filled, see D |
| 19 | "Provide enough details that someone can understand if you're not present" | Full Methods, Results and Conclusion blocks, both figures carry long alt text | **PASS** |
| 20 | "Posters should not attempt to replace a research paper" | Board carries the condensed cut. The long-form sections 6 and 7 of `POSTER_TEXT_BLOCKS.md` stay in the repo for the July 31 paper | **PASS** |
| 21 | "Review the poster resources folder... templates, logos" | Both `.logo-slot` divs at `:237` and `:243` are empty, and `.qr-reserve` at `:368` is empty. No logo asset exists anywhere in the repo | **NOT MET**, needs the resources folder |

## D. Findings that are not instruction violations but affect the deliverable

**D1. Two different poster PDFs exist and they are not identical.**

| Path | Bytes | mtime | md5 |
|---|---|---|---|
| `Cerrell_TACC_42x56.pdf` | 403657 | 17:45:06 | `e43ca960...` |
| `figures/Cerrell_TACC_42x56.pdf` | 404092 | 17:13:54 | `ae91282a...` |

Exactly one of these gets uploaded. The root copy is newer by 32 minutes. Pick deliberately and
delete or rename the other, because two files with the same required filename is the kind of
thing that gets the wrong one uploaded at 08:55 on a Monday.

**D2. The poster predates the best result of the summer.** Both PDFs were printed at 17:13 and
17:45. The corrected-geometry coupled MPM run landed at 18:30, its render at 18:31, and the hero
assets `figures/yaris_hero_frame.png` and `figures/yaris_flood.gif` at 19:26. None of that is on
the board. Concretely, the Results section still reads:

- Result 2, "Grid resolution biases traction one way, and truth is outside the measured range."
  This is the pre-fix framing. Parity fill now converges to 1.0023 at n_grid 64, so the claim
  that truth lies outside the measured range is no longer the current state.
- Result 3, "The cause is upstream of the grid." Still a correct diagnosis, but it now has a fix
  and the poster does not say so.
- Result 5, "What is not on this poster," states that no L2 verdict exists. A verified L2 result
  now exists.

**D3. No L2 figure on the board.** The only two images are the pipeline diagram and the L1 grid.
There is no coupled-MPM visual, which is both the strongest asset and the one a general audience
responds to. Requirement 18 asks for a few key data points, so adding one L2 figure stays inside
the instruction rather than violating it.

**D4. The PDF has no extractable text.** It is a Chrome print in which the content rasterized,
so the file carries no selectable or searchable text layer. Not an instruction violation and it
does not affect printing, but it does mean no accessibility or text check can be run on the PDF
itself, only on `poster.html`.

## E. Priority order before Monday 09:00

1. Ask about 56 x 42 landscape. One message, removes the only hard-requirement risk.
2. Decide which of the two PDFs is the deliverable, remove the other.
3. Update the Results section for the fix and place one L2 figure, then reprint.
4. Get the logos from the poster resources folder and fill the two slots.
5. Sign up for a mock presentation slot and build the 5-minute track. The talk is timed and the
   instruction is explicit that you do not read from the board.

Items 1, 2, 4 and 5 are administrative. Item 3 is the only one that touches content, and it is
the one that makes the board match what the project actually achieved.
