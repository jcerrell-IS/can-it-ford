# R5-D1 unit 34: an unintegrated 2026-08-07 audit contradicts register B5 on the hull density

Date 2026-08-17. Branch `claude/r5-research`. **ESCALATION for D4 and whoever owns
the register. I am not adjudicating this.**

Reading the never-opened `03_Gaussian_Splatting_and_Reconstruction` corpus
directory surfaced `mesh_realism_splat_audit_2026-08-07.md`. It reaches the
opposite conclusion to register **B5** about the canonical Yaris density, it
implemented and measured a fix, and **none of it is in the repo, the register or
CLAUDE.md.**

---

## 1. The conflict, both sides verbatim

**Canonical, register B5:**

> **B5. Vehicle effective density: 310.494 kg/m3** for the canonical Yaris hull.
> The 100-300 kg/m3 plausibility band is STALE. Delete it from any gate or check.

CLAUDE.md carries the same reading at line 61: "vehicle effective density 310.494
kg/m^3 for the canonical Yaris hull, the 100-300 band is STALE".

**The unintegrated audit, section 3.1:**

> The NCAC decks are **zero-thickness shell elements** ... mesh2sdf wraps each
> panel in a thin closed skin ... its enclosed volume is essentially the sheet
> metal, because the cabin stays connected to the outside through window openings,
> door gaps and panel seams.
>
> **Therefore 1100 / 3.5427 = 310.5 kg/m3 is mass divided by sheet-metal volume.**
> It is not a vehicle density, and its being "just outside the 100-300 band" is not
> a mild anomaly, it is this artifact.

**These are opposite conclusions from the same number.** B5 says trust 310.494 and
discard the band. The audit says the band is fine and the *volume* is the artifact.

## 2. The audit implemented a fix and measured it

Section 4, described as parameter-free apart from voxel pitch: flood-fill the
exterior from the grid boundary at 25 mm, mark unreached non-surface voxels solid,
marching cubes.

| vehicle | mass kg | raw vol m3 | raw rho | flood-filled vol m3 | filled rho | band |
|---|---:|---:|---:|---:|---:|---|
| Yaris | 1100 | 3.5427 | 310.5 | **4.5628** | **241.1** | out to **in** |
| Rogue | 1571.3 | 4.9503 | 317.4 | 6.0985 | 257.7 | out to **in** |
| Silverado | 2270 | 7.9621 | 285.1 | 9.2623 | 245.1 | in to in |

So on the audit's own measurement the corrected Yaris density is **241.1 kg/m3,
inside the 100-300 band**, and the band is not stale at all.

Its stated limit, which matters and which it does not hide:

> **Flood fill recovers only genuinely enclosed voids. It does not seal the
> cabin**, because the windows are open at any voxel resolution. So 4.5628 m3 is a
> **lower bound** ... The true value for a sealed car lies between 4.56 m3 and
> roughly 6.8 m3 ... A real sedan displaces ~55-60% of its bbox ... **the remaining
> gap is real and is mostly the cabin.**

## 3. It is entirely unintegrated, checked live

```
term            register   CLAUDE.md   repo .md/.py (excl .claude, third_party)
genus              0           0          0
flood-fill         0           0          0
sheet metal        0           0          - (0 in both canonical files)
sieve              0           0          -
zero-thickness     0           0          -
mesh2sdf           0           0          -
```

The audit's supporting measurements are equally absent: Yaris genus **222**, Rogue
94, Silverado 35, against genus ~0 for a clean envelope; Yaris cabin interior
sampling **16.0%** inside. Nothing on any of it in either canonical file.

The audit itself lives outside the repo, at
`/Users/josie/canitford_census_2026-08-07/mesh_realism_splat_audit_2026-08-07.md`,
symlinked into the Desktop corpus. That is presumably why it was never integrated.

## 4. A supersession worry I checked, and it resolves in the audit's favour

The audit's section 3.1 argues from "near-identical volumes for wildly different
vehicles": a 2026-07-29 Silverado hull at 3.5468 m3 against the Yaris's 3.5427,
0.1% apart. **That specific evidence is superseded**, and by the audit's own later
section: its section 4 table gives Silverado **7.9621 m3**. `MULTIGEOM_VALIDATION_2026-08-11`
independently measures Silverado `solid_volume_m3` at **7.943659** and the surface
at 7.967135, agreeing with the audit's section 4 rather than its 3.1.

So the near-identical-volume anomaly belonged to an older hull generation and the
audit is internally consistent about that. **It does not undermine the sheet-metal
thesis**, which rests on the genus measurements, the unenclosed cabins, and the
triangle-soup area arithmetic, none of which section 4 or MULTIGEOM contradicts.

## 4a. The fix does NOT make the band problem go away, and the reason matters

The `check_claims` guard fired on this document four times, correctly quoting
CLAUDE.md item 9 at me: the 17 gated runs "realise 302.55 to 663.58, every one
above the band". That is a second fact the audit's table does not address, and
working it through separates **two different causes**.

The audit's three vehicles each carry **their own** mass, and all three land in
band once flood-filled. But the project's canonical sweep is **three masses on one
Yaris hull** (register E3, and unit 15). Applying the audit's corrected Yaris
volume of 4.5628 m3 to all three:

| mass | raw rho (/3.5427) | flood-filled rho (/4.5628) | band |
|---:|---:|---:|---|
| 1100 kg | 310.50 | **241.08** | **in** |
| 1609 kg | 454.17 | 352.63 | still above |
| 2337 kg | 659.67 | 512.19 | still above |

The raw column brackets item 9's realised 302.55 to 663.58 closely, which is a
consistency check on both numbers.

**So there are two separate reasons the realised densities sit above the band, and
the audit addresses only the first:**

1. **Hull volume** measures sheet metal rather than displaced volume. The flood
   fill fixes this, and it moves the 1100 kg case from 310.5 into band at 241.1.
2. **Mass overrides on a fixed hull.** 1609 and 2337 kg are applied to the same
   Yaris geometry, so their densities stay above the band no matter how the volume
   is corrected. That is register E3's "one hull with mass overrides only", and no
   geometry fix can resolve it.

Nobody should read this document as "apply the flood fill and the band problem
goes away". It goes away for one of three runs.

## 5. Why this matters beyond the register

**It bears on D4's P-2 work, and cuts against part of it.** The audit's section 3.2
is titled "This is also the P-2 passthrough mechanism":

> A genus-222 hull with an open cabin **genuinely lets water through**. So P-2 is
> not purely a numerical containment failure; a large part of it is the geometry
> honestly reporting that the car is a sieve.

D4's conclusion (`26971c0`, re-derived in `5dbe04d`) is that P-2 is "numerically a
**pile-up** test, not a leakage test", because 77 to 97% of the bounding box is
void. Both can be true at once, the box contains void **and** the hull is
permeable, but "not a leakage test" needs qualifying if the hull genuinely leaks
through an open cabin. **That reconciliation is D4's, not mine.**

**It bears on my own units 19 and 20.** I wrote there that the vehicle is "a
homogeneous solid particle cloud at a fixed effective density of 310.494 kg/m3",
treating that number as the physical density. On this audit's reading it is mass
divided by sheet-metal volume. My statement about the *code* is still exactly right
(`sim_standing.py:170-171` does compute `vehicle_mass / solid_volume`), but my
implicit framing of 310.494 as a vehicle density inherits B5's reading, which is
the reading in dispute. I have not edited those units, because which reading is
correct is the open question.

## 6. A measurement defect of my own, owned

While checking whether the fix reached the repo I first reported per-value counts
like "4.5628 in 2 files" and "241.1 in 27 files". **Those were substring matches
and are unreliable for numeric strings**: `241.1` matches `1241.1` and `241.15`,
and I could not reproduce the `4.5628` count under a bounded re-run. I discarded
them and switched to phrase tests (`flood.fill`, `genus`), which are far less
noise-prone and returned a clean zero. Fourth measurement-method defect I have
caught in my own work this dispatch, after the `\bcar` boundary, the contaminated
pool, and the journal-stub DOIs. The pattern is the same each time: **a match count
is not evidence until you have looked at what matched.**

## 7. Status

**What I am asking for**, and it is two separate decisions:

1. **D4**: does the open-cabin geometry change the P-2 "pile-up not leakage"
   conclusion, and is the 241.1 flood-filled density the better input than 310.494?
2. **Register owner**: B5 and CLAUDE.md line 61 currently state a conclusion this
   audit contradicts. Whichever survives, the other should be marked, because right
   now the canonical files carry only one side and the other side is a measured
   result sitting outside the repo.

UNVERIFIED:
1. **I have not verified any of the audit's measurements myself.** Genus 222, the
   16.0% cabin sampling, the 4.5628 flood-filled volume and the 241.1 density are
   all its numbers. Verifying them needs trimesh and a mesh load, and no Mac
   interpreter here has numpy.
2. I have not read the audit's sections 5 through 8, including its own "WHAT I DID
   NOT VERIFY".
3. Whether the flood-fill fix was ever applied to a gated run is unknown. The
   canonical 17 all carry `solid_volume` from `n_particles * h**3`, so on its face
   they use the raw path, but I have not traced it.
4. The audit is dated 2026-08-07 and I have not checked whether any later document
   inside the repo supersedes its section 4 the way MULTIGEOM supersedes its 3.1.
