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
2. **PURSUED 2026-08-18 (unit 46), and the answer is: confirmed on every state I
   can reach, but the live head is unreachable.** See section 6.
3. Whether any of the four *should* be cited is a judgement for the paper's owner.
   I establish only that they are not, and that the guard does not show it.
4. `Pazouki` and `Khapane` were matched as author strings, not identifiers, so
   those counts could catch unrelated mentions. The identifier-based rows
   (`4071177`, `47142`, `2014-01-0936`) are the reliable ones.

---

## 6. Unit 46: I chased the Overleaf head, and a control probe stopped me overclaiming

Section 5 item 2 named the live Overleaf head as the most likely way unit 45 is
wrong. This is that check.

**Route 1, the Overleaf MCP connector: BLOCKED.** `list_files` fails at
`git clone https://git.overleaf.com/6a5958d10484feadf65a934e` with
`fatal: Authentication failed`. This is exactly what project memory predicted: the
token was removed from local disk on 2026-08-08 but **never revoked**, so the
connector has no credential.

**Route 2, locally fetched refs: partially available.** The repo has an `overleaf`
remote and `refs/remotes/overleaf/main` is present at **`6466dfa`**. So I checked
it, plus `92ce4de`, the commit project memory names as a shared paper state.

**The result, on every `.tex` state I can reach:**

| state | date | `4071177` | `47142` | `Pazouki` | `Khapane` | `2014-01-0936` | `Wasfy` |
|---|---|---|---|---|---|---|---|
| `paper/conference_101719.tex` | 2026-07-30 | 0 | 0 | 0 | 0 | 0 | 0 |
| `paper/canonical_2026-08-02/...` | 2026-08-02 | 0 | 0 | 0 | 0 | 0 | 0 |
| `overleaf/main` @ `6466dfa` | 2026-07-31 | 0 | 0 | 0 | 0 | 0 | 0 |
| `92ce4de` | 2026-07-30 | 0 | 0 | 0 | 0 | 0 | 0 |

**Four independent `.tex` states, zero hits in all of them.** Unit 45's finding is
confirmed everywhere it can be tested.

### 6a. The control probe, and why it changes the conclusion

**A zero is only worth what the probe is worth**, so I ran positive controls on
`92ce4de`, strings that *should* be present:

```
Yaris     : 1 file    probe works
warpmpm   : 0 files   <-- FAILS
AR&R      : 0 files   <-- FAILS
```

**`warpmpm` returning zero is disqualifying for currency.** Project memory records
the Genesis-to-Warp-MPM engine relabelling as landed on overleaf/main across four
commits. If `warpmpm` is absent, **`92ce4de` predates those fixes** and is an early
snapshot, not a current head. Its date, 2026-07-30, agrees.

Likewise `6466dfa` is dated **2026-07-31**, and `git merge-base --is-ancestor` shows
it and `92ce4de` are **unrelated**, not one ahead of the other. So the fetched
`overleaf/main` ref is roughly **18 days stale** and is not the live head either.

### 6b. What this licenses me to say, and what it does not

**Licensed:** the four papers are absent from every `.tex` state available in this
repo, spanning 2026-07-30 to 2026-08-02, including the fetched `overleaf/main`.

**NOT licensed:** that they are absent from the current Overleaf document. CLAUDE.md
is explicit that a checkout which is behind cannot prove a file never existed, and
my own control shows both refs are behind. **I am not claiming the live head is
clean.** I am claiming four stale states are, and that the live one cannot be read.

This *strengthens* unit 45 rather than weakening it, because unit 45's claim was
about an instrument, not about the paper: the guard says `cited` while no reachable
`.tex` cites them. But it stops short of the stronger claim I could have made if the
control had passed, and I want that boundary explicit rather than blurred.

### 6c. NEW FLAG-6: the Overleaf head is unverifiable, and that blocks more than this

**Nobody can currently verify any claim about what the paper says.** The token is
off disk but unrevoked, the MCP connector cannot authenticate, and the newest local
copy is 16 days old. That affects every "the paper does/does not say X" statement in
this dispatch, not only unit 45.

**What unblocks it:** a fresh Overleaf Git authentication token from Overleaf account
settings, which is a human action. Rotating it also closes the still-live old token
that project memory records as valid server-side. **One task, two problems.**
