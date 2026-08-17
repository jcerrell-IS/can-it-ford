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

## L-C. A credential can be identified without reading it, and counting mentions is not evidence

**Two rules, from one case.**

**C-1. Identity from format and endpoint, never from the value.** A credential's
issuer can almost always be settled without a single character of the secret entering
anyone's context or transcript:

| Question | Safe probe |
|---|---|
| Which issuer? | `grep -oE 'https?://[A-Za-z0-9._-]+'` on the config. `-o` emits **only** the matched substring, so a token on the same line cannot come with it |
| What kind of token? | Parse the config and report the value's **length** and **prefix class** (`github_pat_`, `ghp_`, `hf_`, `sk-ant-`), never its characters |
| Real secret or placeholder? | **Character-class and entropy.** A placeholder is uppercase-and-underscore only, no digits, no lowercase, and around 3.5 bits/char. A real token runs 5.5 to 6.0 |

This matters because the project's own record shows a prior session **leaking a token
into its own transcript while investigating that token**, which turned the transcript
into a credential-bearing location. The investigation created a new instance of the
thing it was investigating. These probes make that failure impossible rather than
merely discouraged.

Worked instance: credential H was identified as a **GitHub fine-grained PAT** from
endpoint `api.githubcopilot.com` plus length 93 plus prefix class `github_pat_`. A
second entry at the same endpoint was ruled out as a **placeholder** from entropy
3.51 bits/char and an uppercase-only character class. Neither required reading a value.

**C-2. Counting mentions is not counting evidence.** Four places in one document
described H. Three said "Copilot MCP bearer", one said "GitHub fine-grained PAT". I
weighted three against one, concluded the lone dissenter was wrong, and published that
as "the worst single defect here".

**The lone dissenter was right.** All four were describing the **same** credential:
three described how it is *used* (a Bearer header to Copilot's MCP endpoint), one
described what it *is*. They were never in conflict, so the majority was never
evidence.

**The check to actually run:** before treating agreement as corroboration, ask whether
the agreeing statements could all be **restatements of one another or of one
underlying fact**. If they could, go to the primary source instead. One read of the
config settled in a single step what no amount of weighing secondary descriptions
could.

This is `CLAUDE.md`'s existing "one source cited twice is not two sources" rule,
reached from the opposite direction: there, repetition inflated confidence; here,
repetition inflated a **majority**. Same defect, and the same fix.

---

## L-D. Name the capability before you file something as human-blocked

**The rule:** before recording any item as blocked on a human, **state exactly which
capability that human has and you lack.** If the answer is not one of these four, it is
not blocked and you should do it:

1. **Credentials or authentication you must not hold** (revoking a token at an issuer,
   an interactive login, an account you have no business being inside).
2. **An interactive token or session** you cannot obtain non-interactively.
3. **A decision that is genuinely theirs** (a licence choice, a spend, an accepted
   risk, anything irreversible or outward-facing).
4. **A physical action** (looking at a screen, plugging something in, being in a room).

**Everything else is work, and filing it as blocked hands it to someone else while it
sits perfectly doable.**

**The instance.** I filed "does an NHTSA-hosted copy of this Yaris exist" as blocked on
a human. It was **two web fetches and a checksum**. Attempting it produced the single
strongest piece of evidence in the dispatch: all four CCSA archives are byte-identical
to the published upstream releases, verified against CCSA's own SHA384 values. That
finding sat one untried command away from being filed as somebody else's problem.

It was not isolated. **Two of my three "blocked" items this round were one untried
approach away**: this, and the AR&R report's terms, which I recorded as needing a PDF
text extractor I did not have, and then wrote in about ten lines of `zlib`.

**And it is not personal to me.** The coordinator reports the same pattern in its own
work and in D3's and D4's during the same round. Between us we over-attributed work to
Josie repeatedly. That is the real cost and it is worth naming precisely: **a wrongly
filed block does not merely delay the item, it inflates the queue of the one person in
the loop who cannot be parallelised.** Four sessions each handing over one "small" item
is four items she has to triage, three of which nobody needed to hand her.

**The check to actually run:** write the sentence "this is blocked because Josie can
X and I cannot." If you cannot complete that sentence with one of the four capabilities
above, delete the block and do the work. If you can, keep the block **and say which
one**, so the next reader can tell a real dependency from an unattempted one.

**Corollary, from the same round:** "I do not have tool X" is usually a claim about
convenience, not capability. Before it justifies a block, ask whether X can be built
from primitives already available. The AR&R extractor was `zlib` plus a regex.

---

## L-E. Verify every scripted replacement, and audit the document set, not the edit

**The rule:** when you edit documents with a script, **assert on every replacement**,
and afterwards **grep the whole set for the class of defect**, not just the lines you
touched.

**Three failures in one session, same shape:**

1. `77148c1`: a placeholder SHA (`1a6a...`) committed into a retraction table, because
   the table was written before the commit it referenced existed.
2. `bde09d8`: a table my commit message described in detail and which **never landed**.
   My script printed `MISS` for that replacement; I did not read the output.
3. This commit: a **bare "UNTRACK the 16 files" imperative survived** in the section 5
   recommendation list, in the same document where I had written the warning about
   stale removal lines. An earlier edit targeted `"the 15 ... screenshots"` while a
   prior count correction had already rewritten that text to `"the 16 ... files"`, so
   the replacement silently matched nothing. **No print, no assert, no notice.**

**Why 3 is the dangerous one.** 1 and 2 are visible defects: a reader sees a broken SHA
or a missing table. **3 is invisible and actively harmful**, because the surviving line
reads as current advice. This is exactly the failure the coordinator named: *a stale
"recommend removal" line is how someone deletes something in six months for a reason
that stopped applying tonight.* It survived **in the document that contains that
warning**.

**The two checks to actually run:**

- **Assert, do not print.** `assert old in text` before every replace. A printed
  `MISS` in a wall of output is not a guard; an exception is.
- **Audit by defect class across the whole set**, after the edits:
  `grep -nE '^[^>|]*\*\*(UNTRACK|Remove|Delete)' docs/*.md | grep -v '~~'`
  finds surviving imperatives regardless of which file or wording they hid in. That one
  command found defect 3 after five commits had passed over the file.

**Generalisation:** editing is per-line, but **correctness is per-document-set**. After
a supersession, the question is never "did my edit apply" but "does any stale
instruction survive anywhere". Those have different tests, and only the second one
catches a line you forgot existed.

---

## Why these are worth promoting

Both are **falsifiable checks**, not advice. L-A names a control to run; L-B names a
field to read. Each was established by a specific error with a specific cost, and each
generalises past the case that produced it.

Neither has been reviewed by the physics-skeptic subagent, which is scoped to physical
and structural claims and has no purchase on either. **Mark both UNREVIEWED by that
agent, by scope rather than by omission.**
