# R5-D1 unit 45: the novelty guard says "cited" for four papers that never reached the paper

Date 2026-08-17. Branch `claude/r5-research`.
**This is an instrument critique, not an alarm.** The immediate hazard is not live
in the paper today. The gap in the check is real and would bite the next person who
relies on it.

---

## 1. What the guard exists for

`corpus_cited_status` describes itself as **THE NOVELTY GUARD**, and gives its
origin verbatim:

> "On 2026-08-14 four vehicle-fording papers (Wasfy 2015 DETC2015-47142, Pazouki
> 2016, Khapane 2014 SAE 2014-01-0936, He 2026 10.1115/1.4071177) sat in our own
> catalogs uncited while the project prepared to claim nobody had simulated
> fording."

So it was built for one job: stop a novelty claim that our own catalogs already
refute.

## 2. What it now reports, and what is actually true

Queried today, the guard returns **`verdict: "cited"` for all four**, each resolving
to a research note in `docs/` and **never to a `.tex`**:

| paper | guard verdict | resolves to |
|---|---|---|
| He 2026 | `cited` | `docs/Dynamic_Vehicle_Traction_in_Floodwater.md` |
| Wasfy 2015 | `cited` | `docs/Dynamic_Vehicle_Traction_in_Floodwater.md` |
| Khapane 2014 | `cited` | `docs/RESEARCH_TO_IMPLEMENTATION_2026-08-15.md` |
| Pazouki 2016 | `cited` | `docs/MULTIGEOM_VALIDATION_2026-08-11.md` |

**Four different notes**, which matters: this is not one stray file but a pattern of
research being imported into `docs/` and stopping there.

Measured directly against the repo, excluding `.claude/worktrees`:

| paper | `.tex` | `.bib` | `.md` |
|---|---:|---:|---:|
| He 2026, `10.1115/1.4071177` | **0** | **0** | 8 |
| Wasfy 2015, `DETC2015-47142` | **0** | 1 | 11 |
| Pazouki 2016 | **0** | **0** | 12 |
| Khapane 2014 | **0** | **0** | 5 |
| SAE `2014-01-0936` | **0** | **0** | 4 |

**Not one of the four appears in any `.tex` file.** The single `.bib` hit is not the
paper's bibliography: it is `citations/Elicit - Flood-Crossing Tire-Ground Friction
and Speed Evidence.bib`, an **Elicit export**, and the entry's key is the
auto-generated hash `18c43a4ba492a20af9f0d0856d763204`, which nothing cites.
`47142` appears **zero** times in `paper/can_it_ford_references_IEEE.bib`.

`docs/Dynamic_Vehicle_Traction_in_Floodwater.md` is a 436-line imported research
note (commit `7fe36dd`, "Import vehicle mesh reference research and novelty-check
notes"). It is a note, not the paper.

**So the guard's "cited" is repo-wide text presence.** That is exactly what the tool
says it checks, and it is not a bug. It is a mismatch between what it measures and
the hazard it was built to prevent: a paper claiming novelty. Text presence in an
imported markdown does not mean the paper engages the work.

**This is the same conflation that cost me a wrong claim.** My erratum 4 records it:
I reported "8 catalogued DOIs are cited in the paper" when **3** were `\cite`d and
8 was string presence. The guard has the same definitional gap baked in.

## 3. Why this is latent rather than live

I checked whether the paper currently makes a claim these four would undercut.
Searching both `.tex` files for first-of-kind language, **every hit is a false
positive**: "a **first**-principles force balance", sentence-initial "**First**, ..."
and "the **first** rewrite". **The paper makes no "we are the first" or "nobody has"
claim today.**

So the 2026-08-14 hazard, the project preparing to claim nobody had simulated
fording, **is not present in the current paper text**. I am not reporting a live
defect, and I want that stated plainly rather than buried, because the temptation
here is to bill this as bigger than it is.

**What remains is a real trap for the next person.** Anyone adding a novelty
sentence, and checking it with the tool built for that purpose, gets `verdict:
"cited"` for all four and concludes the literature is engaged. It is not.

## 4. Recommendation, one line of tool behaviour

The guard should separate two things it currently merges:

- **`text_presence`**: appears anywhere in the repo. What it reports now.
- **`paper_cited`**: appears in a `.tex` as a `\cite`, or in
  `paper/can_it_ford_references_IEEE.bib` under a key that some `.tex` cites.

For all four papers, the first is **true** and the second is **false**. A guard whose
purpose is protecting a paper claim should lead with the second.

I have not edited the tool; it is outside my scope and not in this repo.

## 5. Status

UNVERIFIED:
1. ~~I queried the guard for two of the four.~~ **CLOSED before committing: all
   four were queried through the guard and all four return `cited`**, resolving to
   four different research notes. See the table in section 2.
2. The `.tex` search covers **2 files** in `paper/`. Project memory records the
   canonical build as living on **Overleaf**, whose head I did not check, so a
   citation could exist there. That is the single most likely way this finding is
   wrong.
3. Whether any of the four *should* be cited is a judgement for the paper's owner.
   I establish only that they are not, and that the guard does not show it.
4. `Pazouki` and `Khapane` were matched as author strings, not identifiers, so
   those counts could catch unrelated mentions. The identifier-based rows
   (`4071177`, `47142`, `2014-01-0936`) are the reliable ones.
