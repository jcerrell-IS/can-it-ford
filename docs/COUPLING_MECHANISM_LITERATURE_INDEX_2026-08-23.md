# Coupling mechanism: sprint-1 close-out and literature index

**Written 2026-08-23.** Two halves, and they carry DIFFERENT evidence tiers. Do not
quote across the boundary.

- **Part 1 is READ-DIRECTLY.** Every line below it was read live from the pinned
  solver at `544c93dd02cb9c7ead89e1155a62967243244fce`, confirmed against
  `third_party/mpm-engine-544c93dd-solver-core/PINNED_SHA.txt`. It is citable.
- **Part 2 is UNDERMIND-TIER AND UNVERIFIED.** Titles, DOIs, years and abstract
  fragments come from three Undermind reports dated 2026-08-22. **No claim in Part 2
  has been checked against a primary source.** Nothing there enters the register, the
  paper, or a figure caption until it passes `provenance-audit`.

---

## Part 1. SPRINT 1 IS CLOSED. The DeepWiki hypothesis is REFUTED.

### 1.1 The question

DeepWiki, asked whether `kks32/mpm-engine` implements a real force or impulse
accumulator on the free-rigid path, described a `rigid_g2p_accumulate` kernel and a
`rigid_body_integrate` kernel and called this "APIC-style momentum-conserving
transfer." The open question was whether that names the SAME mass-weighted-average
mechanism already cited at `kernels/mpm_utils.py:1434`, or a genuinely different
accumulate-then-integrate pattern that two prior independent reads had missed.

**It is the same mechanism.** The existing citation is correct and current.

### 1.2 The decisive read

Both kernels exist and both are reachable. The kernel names were real; the
mechanism attributed to them was not.

`rigid_g2p_accumulate`, `kernels/mpm_utils.py:1370-1412`. For each material-8
particle it interpolates the grid velocity with standard quadratic B-spline weights
and does exactly two atomic adds, `:1411-1412`:

    wp.atomic_add(rigid_linear_mom,  bid, v_interp * mass_p)
    wp.atomic_add(rigid_angular_mom, bid, wp.cross(r, v_interp * mass_p))

`rigid_body_integrate`, `:1416-1459`. The linear update, `:1434`, in full:

    v_cm_new = rigid_linear_mom[b] / M

Three properties of that block settle the question, and each is independently
falsifiable:

1. **`dt` never appears in the velocity update.** It appears only in the position
   update (`x_cm_new = rigid_x_cm[b] + v_cm_new * dt`, `:1442`) and the orientation
   update (`R_new = R + skew_w * R * dt`, `:1447`). Any impulse-based or force-based
   scheme MUST carry `dt` into the velocity update, because an impulse is a force
   integrated over time. This one does not. **This is the cheapest single test and
   it is sufficient on its own.**
2. **The previous velocity is never read.** `rigid_v_cm` and `rigid_omega` appear
   inside `rigid_body_integrate` only in the signature and as write targets at
   `:1456-1457`. Neither is on the right-hand side of anything. A genuine
   integration reads `v_old`; this assigns `v_new` outright.
3. **The buffers are not temporal accumulators.** `_p2g2p_tail`
   (`kernels/mpm_solver_warp.py:1341-1360`) launches `set_vec3_to_zero` on both
   `_rigid_linear_mom` and `_rigid_angular_mom` immediately BEFORE every
   `rigid_g2p_accumulate` launch. The word "accumulate" in the kernel name means a
   parallel reduction ACROSS PARTICLES within one substep, not accumulation across
   time. Nothing survives a substep boundary.

Taken together: `sum_p(m_p * v_interp_p) / sum_p(m_p)` is the mass-weighted mean of
the interpolated grid velocity at the body's own particles, assigned to the body.
That is velocity equilibration. It is precisely the mechanism already on record.

### 1.3 Reachability, confirmed rather than assumed

The canonical driver reaches this path in three hops, all read live:

| hop | evidence |
|---|---|
| driver registers the hull as material-8 | `renders/yaris_render_s1/sim_standing.py:207` calls `set_material_range(self.n_water, self.n_total, "rigid", obj_id=0, ...)`, then `:209` calls `finalize_rigid_bodies()` |
| finalize keys on material 8 | `kernels/mpm_solver_warp.py:845`, `rigid_mask = mat_np == 8`; sets `n_rigid_bodies` |
| the tail runs the block whenever bodies exist | `kernels/mpm_solver_warp.py:1341`, `if self.n_rigid_bodies > 0:` then zero, accumulate, integrate, restitution, particle-update |

So the 17 gated runs are on this path. No separate collider type owns these kernels.

### 1.4 What DeepWiki got RIGHT, and the exact conflation

Being fair to it matters, because the half it got right is the half that makes a
patch cheap.

- **Right:** the transfer IS momentum-based in form. It sums `m_p * v_p` and
  reconstructs `omega` through `I_world_inv`, and `rigid_particle_update`
  (`:1463-1493`) sets `state.particle_C[p] = skew(omega)` at `:1490` specifically so
  the P2G scatter uses the correct affine velocity field. Calling the
  particle-side scatter "APIC-style" is defensible.
- **Wrong, and this is the whole point:** a **momentum reduction** is not a **force
  accumulator**. Summing `m_p v_p` and dividing by `M` tells the body what velocity
  the fluid grid already has; it never computes what the fluid DID to the body.
  Conflating those two is exactly the failure mode the register records at A3:
  "two-way coupling cannot be verified by reading a force, because no force is
  produced."

**Rule that follows, and it generalises past this one question:** when a summary
tool describes a mechanism as "momentum-conserving", ask which of two things it
means, a reduction over degrees of freedom or an integration over time. The word
does not distinguish them and the physics does.

### 1.5 A finding sprint 1 was not looking for: the impulse limb ALREADY EXISTS

`_apply_rigid_restitution` (`kernels/mpm_solver_warp.py:887-987`) applies genuine
impulses to this same body, immediately after `rigid_body_integrate` and before
`rigid_particle_update`. Read live at `:963-964`:

    v_cm_np[b]  = v_cm_np[b].astype(np.float64) + (J_n / M) * n
    omega_np[b] = omega_np[b].astype(np.float64) + I_world_inv @ (J_n * r_cross_n)

with a Coulomb friction impulse `J_t` following at `:977-978`. That is a correct
impulse-to-body-state application, including the lever arm, for the exact body the
17 runs use.

**Consequence, and it reframes the patch.** The engine is not missing the machinery
to accept a force on a free rigid body. It has that machinery, working, on a
different input. What is missing is any path that turns fluid interaction into a
`J` and feeds it here. That makes the defect a WIRING gap rather than an
architecture gap, and it means a patch has a working, in-repo reference for the
apply half. It does NOT mean the patch is small: the hard half is computing `J`
from a solver that has no pressure field, which is what Part 2 is for.

Caveat, stated because it is load-bearing: this limb fires only for entries in
`self.rigid_surface_colliders`, and it runs on the host in NumPy with a
device-to-host readback (`:893-901`) and a write-back (`:982-987`). A per-substep
fluid coupling on that path would need a device-side rewrite. Read it as a
correctness reference, not as a performance-ready hook.

**Sharpening that caveat, measured live 2026-08-24, because it is easy to misread as
"so the limb is dormant in the published runs."** It is not dormant: the 17 canonical
runs are ON this path. `add_plane` forwards its `restitution` argument straight to
`add_surface_collider` (`core/solver.py:220-221`), and a plane joins
`self.rigid_surface_colliders` exactly when `restitution != 0.0`
(`kernels/mpm_solver_warp.py:1915-1925`). The canonical driver registers its floor
(`renders/yaris_render_s1/sim_standing.py:210-211`) and its four walls (`:214`) with
`restitution=0.05`, so all five are in the list, the guard at
`kernels/mpm_solver_warp.py:890` passes, and `_apply_rigid_restitution` runs every
substep at `:1362`, inside the same `if self.n_rigid_bodies > 0:` block that section
1.3 already traces the 17 runs into. So genuine impulses, the normal pair at
`:963-964` carrying the lever arm `r_cross_n`, and the Coulomb friction impulse
capped at `mu * J_n` and applied at `:975-977` (the `:977-978` cited above is one
line off, `:978` is blank), are already being applied to the same rigid body Part 2.4
diagnoses as force-blind, in the same runs that produced the published verdicts. That
is not a contradiction, because what differs is the INPUT, not the body and not the
code path: every `J` on this limb originates in plane penetration geometry, and
nothing anywhere converts a fluid interaction into a `J`. It is the wiring reading at
its sharpest. The force machinery is not merely present somewhere else in the engine,
it is present and running in these very runs, wired to the floor and the walls and
not to the water. Part 2.4's verdict is unchanged by this, and so is the caveat's
operative point: the limb runs on the host in NumPy with a readback and a write-back,
so it stays a correctness reference for the apply half, not a performance-ready hook.

### 1.6 What does NOT change

- **No verdict moves.** Nothing here touches the 16 SLIDE / 1 STUCK count.
- **No register row changes on the mechanism.** The mechanism claim was already
  correct. Register A3, `docs/C1_ROOT_CAUSE_2026-08-07.md`, and
  `docs/COUPLING_VALIDATION_J1_2026-08-07.md` all already read the same lines and
  reached the same conclusion. Sprint 1 is a third independent read agreeing with
  two prior ones, not a new finding.
- **The one thing worth recording** is the negative: the DeepWiki hypothesis is
  closed, so nobody reopens it. If a future session is told the engine has an
  "APIC-style momentum-conserving" rigid transfer and reads that as an accumulator,
  point them at 1.2 above.

---

## Part 2. UNDERMIND-TIER. UNVERIFIED. Confirm before citing.

Source: three Undermind reports, all dated 2026-08-22, 270 paper-slots across them
(119 + 114 + 37, with heavy overlap between the first two).

### 2.0 READ THIS BEFORE ASSUMING THE CORPUS COVERS THESE PAPERS

Measured live 2026-08-23 01:02, and it contradicts the obvious assumption.

Another session was mid-ingest at that moment: `data/deep_searches/` gained
`free-body-load-transfer.json`, `free-body-load-transfer-expanded.json`,
`load-transfer-portability.json`, `grid-converged-force-deficit.json` and
`sink-drain-overfill.json`, and `data/research_corpus_index.json` was rewritten at
01:01. **That ingest does not make one of these papers queryable.** Every one of
those JSONs was checked and carries keys `slug, name, workspace, created, status,
n_relevant_papers, reached_index_before_2026_08_20, goal, goal_truncated` and **no
`papers` array**. `--stats` still returns `papers 332`, `index built 2026-08-20`.

This is the known defect CLAUDE.md records under the research-corpus section:
21 searches present as metadata, 8 as papers. These five make it 26 as metadata and
still 8 as papers. **Say both numbers. A search reaching the index as a stub is not
coverage.**

Corpus status below was measured per DOI with `research_index.py --doi`, after that
rebuild, so the "absent" results are stable rather than a race artifact.

### 2.1 Ranked for THIS project

Ranked by bearing on open items, not by Undermind score. Two independent tags per
row, per the portability/contrast split the second report was commissioned on.

| # | Work | DOI | Portability to warpmpm | In corpus? |
|---|---|---|---|---|
| 1 | Hyde & Fedkiw 2019, unified monolithic sub-grid solid-fluid coupling | `10.1016/J.JCP.2019.03.049` | contrast, high | **ABSENT** |
| 2 | Jiang, Schroeder & Teran 2016, angular-momentum-conserving APIC | `10.1016/j.jcp.2017.02.050` | contrast, decisive for the naming question | **ABSENT** |
| 3 | Nakamura, Matsumura & Mizutani 2021, particle-to-surface frictional contact for MPM | `10.1016/J.COMPGEO.2021.104069` | **portable, highest** | **ABSENT** |
| 4 | Hu et al. 2018, MLS-MPM with CPIC and two-way rigid coupling | `10.1145/3197517.3201293` | partially portable | **PRESENT, and already reader-facing** |
| 5 | Nangia et al. 2017, moving control volume for force and torque | `10.1016/j.jcp.2017.06.047` | validation instrument, not a patch | **ABSENT** |
| 6 | Giovacchini & Ortiz 2014, LBM force and torque by momentum exchange | `10.1103/PhysRevE.92.063302` | portable in principle, pressure-free | **ABSENT** |
| 7 | Perez, Barclay & Zhang 2023, nodal force error and its reduction for MPM | `10.1016/j.jcp.2023.112681` | diagnostic | **ABSENT** |
| 8 | Hirae, Morishima & Ando 2025, analytical integrator for coupled buoyancy | `10.1145/3757376.3771383` | reference solution | **ABSENT** |
| 9 | Fang et al. 2020, IQ-MPM interface quadrature | `10.1145/3386569.3392438` | partially portable | **ABSENT** |
| 10 | Baumgarten & Kamrin 2023, spatial integration errors in MPM | `10.1002/nme.7217` | diagnostic | **PRESENT** |
| 11 | Zhang et al. 2017, incompressible MPM for free-surface flow | `10.1016/j.jcp.2016.10.064` | contrast | **PRESENT** |

**Correction to the framing this index was commissioned under.** The briefing
treated Hu et al. 2018 as a new discovery. It is not. It is already cited in
CLAUDE.md addendum A-1 as the citation for real two-way MPM rigid coupling requiring
accumulated contact force, it is in the 332-paper corpus, and it already reaches
reader-facing prose. Three of eleven rows were already known. Check the corpus before
calling a paper new; that is what the `research-corpus` skill is for.

### 2.2 Why row 1 is first

Hyde & Fedkiw 2019's own abstract states it removes "the non-physical ansatz of
velocity equilibration for sub-grid bodies." **UNVERIFIED, abstract-only, quoted
from the Undermind return and not from the paper.** If that wording holds against
the primary source, it is a published paper naming this project's exact defect in
the project's own terms, which is stronger than any citation currently available for
the Limitations paragraph. **Verify the wording before it is quoted.** That is the
first Scite or Undermind `read_pdfs` call to make.

### 2.3 Why row 2 settles a naming dispute

If a future reader accepts "APIC-style" as the description of
`rigid_g2p_accumulate`, Jiang, Schroeder & Teran is the paper that defines what APIC
actually conserves. Part 1.4 above already shows the scatter half is APIC-consistent
and the integrate half is not. This is the citation for that distinction, in either
direction.

### 2.4 THE STRONGEST RESULT IN ALL THREE REPORTS IS A NEGATIVE

The third report, commissioned on the grid-converged partial-submersion force
deficit, reports 89 percent estimated coverage and concludes, quoted from its
summary:

> no cited paper directly documents a grid-converged underforce from assigning a
> free rigid body the grid-mass-averaged velocity

**UNVERIFIED as a coverage claim, and coverage estimates are the search engine's own
self-report.** But if it survives checking, it is the most publishable line the three
reports produced, because it converts a defect into an unreported result. A
literature search at 89 percent claimed coverage that returns no prior documentation
of the failure mode is the kind of negative that belongs in the paper, and it costs
nothing to state conservatively: not "nobody has found this", but "a targeted search
of the MPM force-transfer literature returned no prior report of it."

Its second-order finding is also useful and cheaper to check: the mechanisms the
literature DOES support for a resolution-independent bias are discrete interface and
transfer bias (quadrature error, stress recovery, cell crossing, projection accuracy
depending on particle location and density), not a uniform hydrostatic pressure
offset. That is consistent with the project's own observation that the equivalent
pressure deficit is inconsistent across conditions rather than a constant.

### 2.5 What is NOT worth chasing

- The SPH pairwise-boundary-force family (Akinci and descendants). Not transferable
  to a grid-based MPM without a redesign, and the reports agree.
- The fixed and prescribed-motion IBM and fictitious-domain bulk. Good contrast, no
  portability, and partially covered already.
- Hugging Face and Weights & Biases have no bearing on a coupling-mechanism
  literature question. There is no relevant pretrained model or dataset. Do not
  manufacture a connection.

---

## Cross-references, all live as of 2026-08-23

- `docs/C1_ROOT_CAUSE_2026-08-07.md:47,54` reads the same two kernels.
- `docs/COUPLING_VALIDATION_J1_2026-08-07.md:66` states the no-force-term finding.
- `docs/R8_FORCE_ROUTE_2026-08-18.md:558-640` section 12 covers whether `sdf_wrench`
  can carry a force-versus-resolution curve, verdict yes in principle, no today, and
  section 12b records that it is on a different code path from every published run.
- Register A3 is the corrections authority for "no force accessor exists."
- CLAUDE.md addendum A-1 already carries Hu et al. 2018 and Pazouki et al.
