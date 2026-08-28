# CLAUDE.md sections moved out on 2026-08-27

Two blocks were moved here VERBATIM from the project-root `CLAUDE.md` during a `/doctor`
pass. Nothing was summarised and nothing was dropped. Every operative rule stayed behind in
`CLAUDE.md`; this file is the working behind those rules.

Provenance: pre-move `CLAUDE.md` sha256 `072cb2c0b72362172da56a6f05cd83ecaba892f666b174006045079d57dd10ad`, 526 lines, 33884 bytes.
This is the third such move, after `CLAUDE_MD_MOVED_SECTIONS_2026-08-19.md` (171 lines) and
`CLAUDE_MD_MOVED_SECTIONS_2026-08-26.md` (710 lines), and it follows the same rule those two
followed: this file is the CONSTITUTION, a worktree carries the `CLAUDE.md` from ITS branch
point, so every line added there silently diverges across every live worktree.

Cite anything below with its own date, never as current. Where it conflicts with
`docs/CANONICAL_CORRECTIONS_REGISTER_2026-08-06.md`, the register wins.

---

## 1. The worktree-count re-measurement changelog, from the `grep` clause

Was `CLAUDE.md` lines 69-82. Removed because the block's own conclusion is "Do not quote 33,
28, 11 or 6; run the command", which makes it derivable from `git worktree list` by
definition. What stayed in `CLAUDE.md`: the count has been wrong in three directions in
twelve days, quote no figure, run the command, and the `./.claude/worktrees/` exclusion is
load-bearing regardless of the number.

```
  RE-MEASURED 2026-08-20 AND THE 2 IS NOW STALE IN THE OTHER DIRECTION.
  This clause read "`./.claude/worktrees/` holds 2 directories, not 27, so
  the multiplies-every-hit-~20x figure is stale". Live today,
  `git worktree list` returned **33 worktrees, 28 of them under
  `.claude/worktrees/`**. So the exclusion is load-bearing again and the
  ~20x inflation is real again. The lesson is the clause itself: this
  number has now been wrong in both directions within eight days, so
  RE-MEASURE IT rather than quoting any figure here, including 28.
  RE-MEASURED 2026-08-25 AND 33/28 IS NOW STALE TOO, WHICH IS THE THIRD
  DIRECTION CHANGE. Live: **11 worktrees, 6 of them under
  `.claude/worktrees/`**. The exclusion still matters but the ~20x figure
  does not describe it any more. Do not quote 33, 28, 11 or 6; run the
  command. The clause has now been wrong three times in twelve days,
  which is the point it is making about itself.
```

---

## 2. The 2026-08-19 adversarial-review outage, as recorded that day

Was `CLAUDE.md` lines 440-459, under the heading "THE ADVERSARIAL REVIEW PATH WAS DEAD
FLEET-WIDE ON 2026-08-19. THE OUTAGE ENDED."

That section says "Do not delete it and do not act on it as current." **It has not been
deleted.** It is reproduced verbatim below, and the pointer left in `CLAUDE.md` names this
file. The two rules the section exists to carry both stayed in `CLAUDE.md`: a "do not
re-attempt" instruction is advice against a retry loop and never a licence to carry a dated
infrastructure claim as standing fact, and the physics claims from 2026-08-18 and 2026-08-19
REMAIN UNREVIEWED because the path being alive again does not review them retroactively.

The outage itself ended, measured 2026-08-20 03:40.

### The outage as recorded on 2026-08-19, kept verbatim

Recorded here because it existed in five sessions' transcripts and **zero committed files**,
and a transcript is not a deliverable. Nine independent origins confirm it.

The `physics-skeptic` subagent, and any Agent call, dies with:

    deepseek-ai/DeepSeek-V4-Flash:deepinfra

**An explicit `model` override does NOT reach it.** Measured twice at 18:37 and 18:38: the
`physics-skeptic` agent at default and a `general-purpose` agent with an explicit `opus`
override produced the IDENTICAL error. The agent *launches* and then dies, which is why it
reads as a transient failure and gets retried instead of recorded.

**Consequence for every claim made on 2026-08-18 and 2026-08-19:** the operating protocol
asks for the physics-skeptic before finalising any percentage, force, verdict count or
distance. It was unavailable. Sessions d11, d12, d14, d15, d18 and d19 all correctly marked
their claims UNREVIEWED rather than faking the review. **Those claims remain unreviewed.**
Do not treat any of them as adversarially checked, and do not re-attempt the subagent
expecting a different result until the model id is fixed.
