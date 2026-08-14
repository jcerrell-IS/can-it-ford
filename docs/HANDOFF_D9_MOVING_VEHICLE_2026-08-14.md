# Handoff to Dispatch 9: the moving-vehicle files are committed, do not recreate them

Written by the Dispatch 8 preflight thread, 2026-08-14. Everything below was verified
live in that session.

## Ownership

Per the standing ops addendum, **D9 owns `simulation/moving_vehicle_sdf_exploratory.py`
and the SDF driver from here on.** Dispatch 8 committed that file once, because 8.2 named
it by explicit path and instructed the commit, and will not touch it again. This note is
in D8's own branch rather than as an edit to anything D9 owns.

## Where the work is

It is no longer untracked, and the branch is no longer absent from origin.

```
branch  claude/moving-vehicle-exploratory-2026-08-11
commit  187d8689413c9d2a20e0c5f9eaac03131b8a1169
proof   git ls-remote --heads origin | grep moving-vehicle
```

**Pull this branch; do not rebuild these files from scratch.** Before the commit the four
files were untracked on a branch whose name was absent from origin, so they existed on one
laptop disk only.

```
simulation/moving_vehicle_sdf_exploratory.py      29788 B
analysis/render_moving_vehicle_surface.py         11668 B
analysis/render_moving_vehicle_placeholder.py      5539 B
docs/MOVING_VEHICLE_SDF_EXPLORATORY_2026-08-11.md 12676 B
```

One correction to how the branch was described in the dispatch: only the branch **name**
was missing from origin. `feecf5f` was already reachable from `origin/main` and four other
origin refs, so exactly one commit was ever orphaned, not the whole history.

## Do not cite sections 5, 6 or 8

The document carries three unfilled placeholders. Line numbers re-derived with
`/usr/bin/grep -n` on 2026-08-14, and checked against the section boundaries rather than
assumed:

| placeholder | line | section | section span |
|---|---|---|---|
| `<!--LADDER-->` | 143 | **5.** The finding: this scene cannot resolve its own water column | 108-161 |
| `<!--BOWWAVE-->` | 164 | **6.** What the scene does show | 162-167 |
| `<!--COST-->` | 205 | **8.** Cost, and why no Vista job was submitted | 203-208 |

**The sharpest trap is section 5**: it states a negative finding whose supporting table is
one of the placeholders. A negative result with no table under it reads as settled and is
not. Sections 1-4, 7 and 9-11 have no placeholder in them.

## The related branch D9 will probably want

The Vista 6-DOF driver was recovered in the same preflight and is now on origin:

```
branch  track1/sdf-6dof-driver
commit  09d2b8fb1763ca85ef3e53d4fc71a7d135e126b5
carries simulation/rigid6dof.py                    307 lines
        tests/test_rigid6dof.py                    314 lines
        docs/TRACK1_6DOF_DRIVER_2026-08-13.md      133 lines
        run_c4_free_sdf at simulation/validate_coupling_force.py:851
```

Two things about it that are easy to get wrong, both verified live rather than inferred:

1. **The SHA `a231a73` quoted in the dispatch text is not the tip and is not on the
   branch.** It is a dangling pre-rebase commit on a different parent. It carries nothing
   unique: `git patch-id --stable` returns `8079edb9e4427b5b8dbde9570e0199d5685fbe9e` for
   both `a231a73^..a231a73` and `77d11d4^..77d11d4`. Use `09d2b8f`. `a231a73` still
   dangles on Vista and will vanish at the next `gc`.
2. **The "25/25 tests passing" figure is UNVERIFIED as to passing.** The count
   reconciles by inspection: 21 `def test_` functions, one carrying
   `@pytest.mark.parametrize` with 5 cases, so pytest collects 25. It was not executed.
   Vista's system `python3` has no `pytest` and `$HOME` is 89.15% full, so no install was
   attempted. If D9 needs the suite green, run it somewhere with an environment and say
   so; do not inherit the claim.
