# Contributing

This is a research repository from an NSF REU project, not a library seeking contributors. It is
public so the results can be checked. Issues and corrections are welcome, especially corrections.

## Before you open an issue

Run `make facts`. If a number in the README, the paper or the poster disagrees with what that
prints, the number is wrong and the issue is worth opening. Please paste both.

## The rules this repository holds itself to

They exist because each one was learned by breaking something.

1. **Verify live, do not trust a summary.** Before stating what a file contains, read it in this
   session. A number carried from a prior write-up is not a measurement. `docs/CANONICAL_FACTS.md`
   pairs every headline number with the command that proves it.

2. **State the scope with any count.** Counts here are scope-sensitive and have been wrong in both
   directions. "22 declaration sites" is meaningless without saying whether `archive/` was
   included.

3. **`grep` in this environment is not `grep`.** It is ugrep with `--ignore-files`, so it skips
   every gitignored path, and `data/` and parts of `renders/` are gitignored. Use `/usr/bin/grep`
   or `git grep` for anything that will be published. An absent hit is not evidence of absence.

4. **Deduplicate by name and unit, never by value.** `slide_m` (0.05 m), `slide_speed_ms`
   (0.05 m/s) and `float_m` (0.05 m) share one numeral across two units. A find-and-replace on
   "0.05" would silently turn a speed into a distance and change 16 of 17 published verdicts.

5. **Stage explicit paths.** Never `git add -A`, `git add .` or `git commit -a`. More than one
   session has worked in this tree at once, and a blanket add has committed someone else's
   in-progress work under the wrong message.

6. **Do not cite this repository's own docs positionally.** Quote the heading and the sentence,
   not `FILE.md:NNN`. These files change often enough that a line number is stale on arrival.

## Third-party material

`vehicle_geometry_research/` contains finite element vehicle models this project did not author
and for which **no licence has been established**. Read `THIRD_PARTY_NOTICES.md` before
redistributing anything from that directory. The root BSD-3-Clause licence does not cover it.
