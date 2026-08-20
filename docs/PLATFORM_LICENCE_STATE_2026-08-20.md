# THE LICENCE STATE, MEASURED LIVE, AND THE REPORTED PROBLEM IS NOT THE REAL ONE

Measured 2026-08-20 against the live Hugging Face Hub and the local tree. Supersedes the
handoff's section 9 claim that "THREE licences are now published for the same project" and
the R10 platforms finding that proposed changing `CITATION.cff` to BSD-3-Clause.

**That proposal was killed by the workflow's own adversarial verifier, and the verifier was
right.** This document says why, and names the two problems that ARE real.

---

## 1. THE COMPLETE STATE, EVERY SURFACE

| surface | licence declared | covers | verdict |
|---|---|---|---|
| `LICENSE` at repo root | **BSD 3-Clause**, (c) 2026 Josie Cerrell | the code | correct |
| `hf_space/README.md` front matter | `bsd-3-clause` | the Space, which ships code | correct, **but not live** |
| live Space `josiecerrell/can-it-ford` | **NONE** | public | **problem 2** |
| live Space `josiecerrell/can-it-ford-demo` | **NONE** | public | **problem 2** |
| `CITATION.cff` and `citations/CITATION.cff` | `ODC-By-1.0`, with `type: dataset` | the data | **problem 1** |
| live dataset `can-it-ford-sweep-v1` | `cc-by-4.0` | the data | **problem 1** |
| live dataset `can-it-ford-speed-surface` | `cc-by-4.0` | the data | **problem 1** |
| live dataset `can-it-ford-results` (private) | `cc-by-4.0` | the data | **problem 1** |

Account is `josiecerrell`, **PRO**, personal access token with `write` role. Eight repos:
3 datasets (2 public), 4 Spaces (2 public), 1 model.

---

## 2. WHAT IS NOT A PROBLEM, AND WHY THE PROPOSED FIX WOULD HAVE BEEN WRONG

**BSD-3-Clause alongside an open-data licence is not a conflict. It is correct separation.**
`CITATION.cff` line 4 reads `type: dataset` and its message reads "If you use this dataset or
code, please cite it as below." ODC-By is an OPEN DATA licence and is the right family for a
dataset; BSD-3-Clause is a SOFTWARE licence and is the right family for the code and the Space.

The R10 platforms reader proposed: *"change line 12 from ODC-By-1.0 to BSD-3-Clause, because
CITATION.cff licenses the software artifact the citation describes."* **The premise is false**,
the file declares itself a dataset, and applying a software licence to a dataset is a
downgrade in rights clarity, not an improvement. The adversarial verifier killed it. Recorded
here so nobody re-proposes it from the same reasoning.

So "three licences for one project" is **refuted as stated**. There are two artifact classes
and they are correctly separated.

---

## 3. PROBLEM 1: THE DATA CARRIES TWO DIFFERENT LICENCES, BOTH PUBLIC

`CITATION.cff` says **ODC-By-1.0**. All three Hub datasets say **cc-by-4.0**. Same artifact,
two licences, both world-readable, and the citation file is what a paper's data-availability
statement would point at.

They are not interchangeable:

- **ODC-By-1.0** is an Open Data Commons attribution licence, written for databases. It
  attaches to the database rights as well as the contents, which is the point of using it for
  a dataset in a jurisdiction that recognises them.
- **CC-BY-4.0** is a general Creative Commons attribution licence. Since 4.0 it does cover
  sui generis database rights, so it is a defensible dataset licence too, and it is the far
  more widely recognised of the two on the Hub.

**This is a rights decision, not an engineering one, and it belongs to Josie and Krishna
Kumar as the two named authors in `CITATION.cff`.** Nothing here changes a public licence
without that decision.

The practical consideration, stated without recommending: CC-BY-4.0 is what the Hub datasets
already advertise and what most downstream tooling expects; ODC-By-1.0 is the more precise
instrument for a database specifically. Whichever is chosen, it should be identical on the
`.cff`, both copies of it, and all three Hub dataset cards.

---

## 4. PROBLEM 2: ONE PUBLIC SPACE CARRIED NO LICENCE. RESOLVED.

**THIS SECTION ORIGINALLY SAID TWO SPACES, AND THAT WAS MY OWN FALSE CLAIM.** Corrected the
same day, before it could be quoted.

What I did: read the Hub's repo listing, saw tags `gradio, region:us` on both public Spaces
with no `license:` among them, and concluded neither declared one. What is actually true, from
fetching both live READMEs:

| Space | live README front matter | Hub tag listing |
|---|---|---|
| `josiecerrell/can-it-ford` | **`license: bsd-3-clause` was already there** | did not surface it |
| `josiecerrell/can-it-ford-demo` | genuinely absent | did not surface it |

**The Hub's tag listing is a partial view of a Space's front matter, and I read absence from
it.** That is the same predicate-shaped false negative this project keeps recording, committed
by me one commit after writing up two others. The tag list is not the licence.

**Fixed on the one Space that needed it.** `can-it-ford-demo` now carries
`license: bsd-3-clause`, one line added to the front matter and nothing else touched, matching
the repo's own `LICENSE` and its sibling Space. Verified by re-downloading the live README
rather than trusting the upload's exit code. Commit
`59f1b9875419423439de70974142f3581fd251f3`.

---

## 5. ONE MORE THING THE SWEEP FOUND

`josiecerrell/can-it-ford-sweep-v1` is **public, has 30 downloads, and its own README says it
"has never contained any data file"**. That is honest and it is also a public artifact under
this project's name that returns nothing to 30 people who fetched it. It carries `cc-by-4.0`
on nothing. Worth deciding whether it should be deleted, made private, or populated; the
handoff already flagged it as one of the two genuinely bare repos.

---

## 6. THE CORRECTION TO THE RECORD

The handoff's section 9 says "THREE licences are now published for the same project" and cites
`CITATION.cff` ODC-By-1.0, the Space card bsd-3-clause, and a third published during the
investigation. Measured live, the third is **cc-by-4.0 on the datasets**, and the framing was
wrong: the BSD one is not a competing declaration about the same artifact, it is the code
licence. **One real conflict, on the data, plus two public Spaces with no licence at all.**
