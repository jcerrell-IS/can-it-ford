# Forward-going run-provenance capture: integration note

Originally written 2026-08-12 on LS6 (c301-003, job 3360948), as the companion to the
Vista-side `analysis/run_provenance.py` and `analysis/backfill_run_provenance.py`.
Session log: `.remember/ls6_session_2026-08-12.md`.

**Ported to the Mac and revised 2026-08-13.** The Vista original was untracked and existed
in no git object anywhere, so this copy exists to make it recoverable. Two of its three
load-bearing statements had gone stale; they are corrected below and the original wording
is quoted so the change is auditable. Reconciliation of the two writers:
`docs/PROVENANCE_WRITER_RECONCILIATION_2026-08-13.md`.

## Status, corrected 2026-08-13

The original said the patch was "verified but unapplied", and gave as the reason that a
parallel Vista session (job 906873) held `simulation/validate_coupling_force.py` open.

**The patch has since been applied on Vista.** Verified live 2026-08-13:
`simulation/validate_coupling_force.py:1069-1081` imports `collect_run_provenance` and
assigns `res["provenance_v2"]`. The forward path is live there.

**The Mac's copy of that same file carries no such hook**, so the two copies of a tracked
file have diverged on this point. Closing that gap is out of scope for the reconciliation
dispatch (DP-5 owns `simulation/coupling_force/**`), and is recorded as open.

## The patch

The exact block is `analysis/_provenance_v2_snippet.py`, kept **byte-identical** to the
Vista copy on purpose (sha256 `17f6335b2248c2a4...`): two copies of one file drifting is
the failure this whole reconciliation exists to undo. Read the snippet, do not retype it.

Anchor is the single occurrence of `res["provenance"] = PROVENANCE`. Insert the block
immediately after that line.

Two deliberate choices in the snippet:

* `mesh_paths=None` is a **positive assertion, not a gap**. `build_box_sdf()` calls
  `cube_mesh(length)` and `build_sdf(...)`; the writer loads no `.ply`, `.obj` or `.stl`.
  `mesh_sha256` is therefore recorded as `inapplicable`. **If a future variant loads a
  real vehicle mesh, pass its path here** and the hash starts being captured
  automatically. Independently re-verified 2026-08-13 across all 21 such manifests on the
  Mac: `geometry.box_side_m`, `geometry.box_volume_m3` and
  `geometry.box_particles_per_side` are present in 21/21, and no key or value matching
  `mesh`/`ply`/`obj`/`stl` occurs anywhere in that family.
* The `try/except` means a provenance failure degrades to an error string inside the
  manifest rather than killing a GPU run that already burned allocation.

## The merged writer keeps this call working

`analysis/run_provenance.py` is now a **single merged writer** covering both manifest
families. Every keyword the snippet passes (`script`, `mesh_paths`, `solver_source`,
`solver_pinned_sha`, `grid_density`, `vehicle_mass`, `bulk_modulus`) exists in the merged
`collect_run_provenance`, so **the applied Vista hook keeps working unchanged**. Verified
by signature comparison 2026-08-13.

Two behavioural changes the caller should know about:

* The confidence vocabulary is now
  `recorded / aliased / derived / resolved / inapplicable / reconstructed / unknown`, and
  every label is validated at emit time. The old `inferred` was a sixth value the Vista
  file's own `CONFIDENCE` tuple never declared; it is now `reconstructed`.
* `bulk_modulus` is `derived` from a recorded sound speed when the run script does not
  supply it, by `bulk = c**2 * rho / gamma`. Passing `bulk_modulus=BULK` as the snippet
  does still wins and is labelled `recorded`.

## Applying it, on either machine

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("simulation/validate_coupling_force.py")
src = p.read_text()
anchor = '    res["provenance"] = PROVENANCE\n'
assert src.count(anchor) == 1, f"anchor appears {src.count(anchor)} times, stop and look"
assert "provenance_v2" not in src, "already patched, stop"
p.write_text(src.replace(anchor, anchor + open("analysis/_provenance_v2_snippet.py").read()))
print("patched")
PY
python3 -m py_compile simulation/validate_coupling_force.py && echo COMPILES
```

Success looks like `COMPILES`, then the next run's JSON carries a `provenance_v2` key
whose `_meta` marks `grid_density`, `vehicle_mass`, `solver_git_sha` and `bulk_modulus` as
present.

Most likely failure mode: the `already patched, stop` assertion trips. On Vista that is
now the **expected** result, because the patch is already in place. On the Mac the anchor
assertion is the one to watch, since that file has moved since the anchor was recorded.

## The two caveats, both re-checked 2026-08-13

The original stated these were "the real reproducibility gap, not the field naming", and
that both "will keep firing until they are fixed".

1. **"The run script is untracked in git."** **CLOSED, on both machines.**
   `simulation/validate_coupling_force.py` is now `TRACKED` on the Mac (last touched by
   `79fec32`) and `TRACKED` on Vista. The original reasoning, that "no commit SHA can
   recover the code that produced the 29 existing manifests", held when it was written and
   no longer does for runs made from here on. It remains true of the 29 manifests that
   already exist, which were produced while the file was untracked.
2. **"The tree is dirty."** **Still true on Vista**, 63 dirty paths as of 2026-08-13,
   against the 46 recorded at capture. While that holds, a recorded HEAD SHA there
   describes the last commit, not the code that ran.

`run_script.sha256` is still recorded on every block, and for the 29 pre-existing
manifests it remains the only durable pointer back to the executed code.
