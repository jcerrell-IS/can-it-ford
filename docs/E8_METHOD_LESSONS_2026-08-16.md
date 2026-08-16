# Two method results from the E8 work, written to be reusable

Dispatch R5-D2, 2026-08-16. Branch `claude/r5-exposure`.

**These are general results, not E8 facts.** They are filed under `docs/E8_*` because
that is D2's writable scope. **They belong in
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md` or `CLAUDE.md`, and D2 is
forbidden to edit either.** Whoever owns those files should lift them; this document
is a holding place, not the right home.

Both were produced by being wrong first, in this session, and both have already
caught more than one person tonight.

---

## L-A. A control on a probe's REACH is not a control on its SENSITIVITY

**The rule:** proving that a probe can see *something* does not prove it would see
*the specific thing you are testing for*. Those are two different propositions, and
conflating them produces a false negative wearing the costume of a verified one.

**How it happened.** I scanned three PDFs with `strings` for Creative Commons licence
markers and found none in any of them. Knowing a bare negative is worthless, I ran a
control: could `strings` see anything at all in these files? It returned **413 URLs**
in one, **199** in another, and **0** in the third. I concluded the probe was
**"valid"** for the first two and blind only for the third, and published that.

Then I resolved the DOIs. **Both "valid" files carry Creative Commons licences**, one
`cc-by` and one `cc-by-nc-nd`. The probe was **0 for 3**, including both files where
my own control had just pronounced it reliable.

The control tested reach. The claim needed sensitivity. **The correct control was to
run the identical probe against a document of known CC-BY status and confirm it
fires.** I never did that, and nothing in the control I did run would have revealed
the gap.

**The check to actually run:** before trusting a negative result, test the probe
against a positive case you already know the answer to. If it does not fire on the
known positive, the negative means nothing.

**Related failures the same night, same shape:** the coordinator ran two `awk` probes
over `git ls-tree` output, one of which reported a **false zero**, because `ls-tree`
is tab-delimited and several `citations/` filenames contain spaces. My own first pass
had the identical defect and produced a 14-screenshot count where the truth is 15,
plus two wrong subtotals. Three people, one shape of error, in one evening.

**Corollary worth stating separately:** when a probe's output feeds a published
number, print the enumeration, not just the total. A total cannot be audited; a list
can. This is the same conclusion `CLAUDE.md` already reached for the
`DRIFT_THRESHOLD` count, arrived at again from a different direction.

---

## L-B. `isOa: true` is not permission. Beware bronze open access

**The rule:** open-access status and redistribution licence are **different fields**,
and the boolean is the one that misleads. Any tool or reader that checks only "is it
open access" will get redistribution wrong.

**The four states that matter**, as returned by a DOI lookup:

| `oaStatus` | `license` | Free to read | Free to redistribute |
|---|---|---|---|
| gold | `cc-by` | yes | **yes**, with attribution |
| hybrid | `cc-by-nc-nd` | yes | **yes**, with attribution, **non-commercial, no derivatives** |
| **bronze** | **absent** | **yes** | **NO** |
| closed | absent | no | no |

**Bronze is the trap.** It means the publisher has made the article free to read on
their own site, at their discretion and revocably, under **no open licence at all**.
`isOa` returns `true`. There is no `license` field, because there is no licence.
**Free to read is not free to republish.**

**The instance.** Smith, Modra & Felder 2019, `10.1111/jfr3.12527`, returns
`isOa: true`, `oaStatus: "bronze"`, no `license`. The repo publicly reproduces the
complete article, all 15 pages, and page 1 carries **"© 2019 CIWEM and John Wiley &
Sons Ltd"** legibly inside the reproduction. Two files beside it in the same
directory, `10.1111/jfr3.70154` and `10.1029/2020WR028616`, returned explicit
`cc-by` and `cc-by-nc-nd` and are fine.

Three files, two publishers, **three different answers**. Do not generalise a journal's
licensing from one of its articles: `10.1111/jfr3.12885` and `10.1111/jfr3.12527` are
the same journal and, on current evidence, not the same licence status.

**The check to actually run:** read the **`license` field**, never `isOa` alone. If
`license` is absent, treat it as closed for redistribution regardless of what `isOa`
says.

**Live consequence for this repo:** at least one citation,
Azhar/Pauwels/Bui 2023 `10.1111/jfr3.12885`, is described in project files as "open
access" **with no licence named**. That phrasing cannot distinguish gold from bronze,
so it cannot support a redistribution decision. Any other citation described the same
way needs the same re-check.

---

## Why these are worth promoting

Both are **falsifiable checks**, not advice. L-A names a control to run; L-B names a
field to read. Each was established by a specific error with a specific cost, and each
generalises past the case that produced it.

Neither has been reviewed by the physics-skeptic subagent, which is scoped to physical
and structural claims and has no purchase on either. **Mark both UNREVIEWED by that
agent, by scope rather than by omission.**
