# D4: both blockers cleared, and two defects that would have wasted the first GPU run

2026-08-17, ~21:30 UTC. Branch `claude/r5-physics`. Written after `81519b2` parked the
branch as "scope complete pending the socket". **That framing was wrong in both
directions**: the socket had already cleared, and clearing it would not have been enough,
because two run-blocking defects sat between the queue and any result.

Claim tags: **[read]** read live from a primary source this session, **[derived]**
computed here from tagged inputs, **[recalled]** carried from a doc and not re-derived.

---

## 1. FLAG-1 (TACC socket) is CLEARED. It was already clear.

`R5_PHYSICS_BLOCKED_FLAGS.md` records `Permission denied (keyboard-interactive)`, checked
twice about 13 hours apart, and concludes every GPU item needs a human to run `ssh vista`.

Live now, and this is a typed remote command, not a cached balance **[read]**:

```
login1.vista.tacc.utexas.edu
Mon Aug 17 21:19:44 UTC 2026
```

`tacc_alloc_status` returns **627 SU** (not the manifest's 629; that is the figure used
throughout this document), queue empty.

**CORRECTED 2026-08-17, and the correction is the point.** An earlier version of this
section read "Nobody ran `ssh vista`; the socket warmed and no one re-tested." **I could
not observe that, and it is very probably false.** The real ControlPath is
`~/.ssh/sockets/%C`, which holds exactly two sockets created 2026-08-17 21:52:50 and
21:53:27, **thirty-seven seconds apart**. Both hosts need an interactive password plus a
6-digit token and no automated client in this fleet can answer an MFA prompt, so two
authentications thirty-seven seconds apart is a **human** typing `ssh vista`, then
`ssh ls6`. A human almost certainly did warm them, roughly forty minutes before anyone
noticed.

I asserted a cause for an observation when I had only the observation. The mirror-image
error was made in the other direction the same evening (asserting the human *had* run it,
with no evidence at that moment), and the original "sockets are cold" check globbed
`~/.ssh/cm-*`, which is **not** this machine's ControlPath, so that evidence was
worthless; only the raw ssh probe returning the MFA banner ever measured anything.

**The lesson survives the correction intact, and is what to keep:** FLAG-2 already says a
licence status is not a fetch status. The same applies here: **a blocker recorded once is
not a blocker now.** A flag file needs a re-test before it is used to stop work, and the
re-test costs one command. What changes is only the causal story underneath it.

## 2. FLAG-2a (the Kramer time series) is CLOSED. The file is on disk.

```
/Users/josie/can-it-ford-refs/2026-08-16/energies-14-00269-s001.zip
17,549,045 bytes   sha256 04c4d78d6987e4eec6c31d692d3c5cf5adea2580ffcfe50fbbd44e6589c7623f
```

Kept **outside the repo**, beside the paper, because the repo is public and E8 is
unresolved. 78 files: `Datafile/{Descriptions,Experimental results,Numerical}` plus a
Readme. The stated size on the article page is 17,138 KB and 17,549,045 / 1024 =
17,137.7 KB, so the archive is complete **[derived]**.

**How, and why every previous attempt failed.** The routes tried before were curl,
WebFetch, and the scite full-text resolver, all of which MDPI answers with 403. Driving a
**real browser** to the article page loaded it in full, supplementary link included. The
navigation to `/s1` itself triggered the download; the blank MDPI splash that appeared was
the download redirect, not a challenge wall.

So FLAG-2's lesson extends by one clause. It reads "a licence status is not a fetch
status". It should read: **a licence status is not a fetch status, and a fetch status
from an automated client is not a fetch status from a browser.** Three sessions recorded
this file as unobtainable; none had tried the one client the publisher actually serves.

Incidentally this **confirms D4's `PROVENANCE.txt` correction independently** [read]: the
article page lists the 16 authors ending Nielsen and Eskilsson. Ferri, Crowley,
Stratigaki and Troch are not among them.

## 3. What the benchmark actually says

Reduced by `simulation/r5_physics/kramer_benchmark.py`, which recomputes everything from
the files on each run. Nothing below is transcribed.

### 3.1 `Te0` is a normaliser, not a measurement. This nearly became a false claim.

`Te0` recovers from `t / (t/Te0)` as **0.756100 s, identical across all three drop
heights and all four repetitions, spread 0.00e+00 over 12 series** **[derived]**. It is a
single fixed normalising constant. Reading it as "the measured natural period" would
contradict the paper's own Figure 13 finding that the damped period **rises** with drop
height. A number that falls out of a data file still has to be interrogated.

### 3.2 The measured damped periods, with N and spread

First damped period, from zero crossings of `x3` about its own settled level, four
repetitions per drop **[derived]**:

| drop | H0 | first damped period | N | range | spread |
|---|---|---|---|---|---|
| 0.1D | 30 mm | **0.7869 s** | 4 | [0.7865, 0.7876] | 0.0010 s |
| 0.3D | 90 mm | **0.8093 s** | 4 | [0.8088, 0.8099] | 0.0012 s |
| 0.5D | 150 mm | **0.8671 s** | 4 | [0.8658, 0.8687] | 0.0029 s |

**The paper's Figure 13 claim reproduces from the raw series: CONFIRMED**, 0.7869 <
0.8093 < 0.8671. Cycle by cycle the periods decay toward the `Te0` normaliser, e.g. 0.5D
runs 0.8671, 0.7819, 0.7885, 0.7659, 0.7669, which is what makes 0.756100 s legible as
the linear asymptote.

### 3.3 The `a33/m = 0.5` sizing assumption is now testable, and it is low

`sphere_heave.py` assumes an added-mass ratio of 0.5 to predict `T_n` and size the run,
labelled there as an estimate never compared against as truth. Against the measured
periods and the closed-form stiffness `k = rho g pi R^2 = 692.885 N/m` at Table 1's
`rho_w` and the benchmark `g` **[derived]**:

| drop | implied a33 | implied a33/m |
|---|---|---|
| 0.1D | 3.8118 kg | **0.540** |
| 0.3D | 4.4385 kg | **0.629** |
| 0.5D | 6.1410 kg | **0.870** |

So 0.5 is low even in the linear case, and 42% low at the nonlinear one. D4's predicted
`T_n = 0.7770 s` sits **1.26% below** the measured 0.7869 s at 0.1D **[derived]**. This is
a 1-DOF reading of a nonlinear record, so treat it as a diagnostic of the sizing
assumption, not as a hydrodynamic result.

### 3.4 The uncertainty semantics are confirmed from the data, and sharpened

D4 corrected the abstract's "0.3%" to an average, at 95%, of the **drop height**, making
it an absolute displacement tolerance. **The CI95 series confirms that directly**
**[derived]**: mean half-width per drop is **0.319%, 0.266% and 0.290% of H0**, averaging
about 0.29%, which is exactly "on average only about 0.3% of the respective drop heights".

The sharpening: the per-drop tolerances are **0.096 / 0.239 / 0.435 mm**, not the
0.090 / 0.270 / 0.450 mm that a flat 0.3% gives. Grade against the measured per-drop
value, not the nominal percentage.

**Job C's pass criteria are therefore now quantitative.** The manifest lists C as "not
gradeable until `/s1` exists, self-consistency only". That restriction is lifted.

## 4. Two run-blocking defects, neither of which the socket would have fixed

### 4.1 Job A pointed at a driver that does not exist

`prestage_jobs.sh:29` read
`DRIVER=$VISTA_ROOT/can-it-ford/renders/yaris_render_s1/sim_standing.py`. That path
returns **No such file or directory** **[read]**. On Vista the engine and the driver are
in **different roots**:

- `can-it-ford/` has `mpm-engine/.venv`, `mpm-engine/src` and the hull, but its `renders/`
  holds only `mpm-engine-out` and `multigeom_2026-08-12_render`.
- `can-it-ford-track1-6dof/` has `renders/yaris_render_s1/sim_standing.py` at exactly the
  expected `4696c3b2...`, but no engine.

Four further copies carry the same sha (`render_s2/multigeom_2026-08-08`, `d5_settle`,
`d5_seedpolicy`, `can-it-ford-track2-realism`); two other hashes exist under `$WORK`
(`5215c38b` in the `as_ran_local_copies` trees, `7236e474` in `class_specific`) and
neither is the published driver. **The driver identity was never in doubt; only the path
was wrong.** Fixed, and `cd $REPO` deliberately stays `can-it-ford`, because
`sim_standing.py:14` hardcodes `VEHICLE_DIR` as an absolute path, so the driver is
cwd-independent for the hull **[read]**.

### 4.2 Jobs B and C ran a file that was never staged

Both did `cd $REPO` then `$PY simulation/r5_physics/sphere_heave.py`, a **relative** path.
`find $WORK -name sphere_heave.py` returned **nothing** **[read]**. It could not have been
otherwise: this branch is 36 commits ahead of `main` and has never been pushed, while
Vista's `can-it-ford` checkout sits on `main` at `15275f2`.

Fixed by staging to `$WORK/d4_scene` and referencing it **absolutely**. Its own directory
rather than the repo checkout, so no untracked files land in a tree other machines share,
and an absolute path cannot be broken by a `cd`.

### 4.3 Why neither was caught: the preflight could not fail

`preflight()` **echoed** its four checks as strings for a human to run. Both the script's
usage text ("run ONLY the path/sha checks on Vista") and `START_HERE` section 2 ("Or just:
`prestage_jobs.sh --preflight`") described it as performing them. It performed nothing and
always exited 0.

**A check that cannot fail is not a check.** This is the same defect class as the tunable
at-rest gate and as the vacuous margin assertion caught on day one, in a third place. It
now executes against Vista and exits non-zero; run against the original paths it reports
both failures above.

## 5. State now

```
bash simulation/r5_physics/prestage_jobs.sh --preflight   # rc=0
```

- driver identity **OK**, sha `4696c3b2...` matched
- scene staged **OK**, `$WORK/d4_scene`, sha256 verified byte-identical local vs remote
- engine **OK**, `warpmpm.geometry` exposes `build_sdf`, `SDFData`
- `test_sphere_geometry.py` run on **Vista's own interpreter**: **ALL PASS, rc=0**

`nvidia-smi: command not found` on the login node is expected and is not a gate.

**The queue is fireable.** Nothing here has run on a GPU yet, and no GPU job has been
submitted: that is a live allocation and the call to spend it belongs to Josie.

## 6. Unreviewed

Section 3's numbers are `[derived]` from the published series by a method stated in the
module docstring (settled-level equilibrium, interpolated zero crossings, half-period
doubling). They have **not** been through the physics-skeptic subagent. The most
attackable choice is the equilibrium estimate: it is the mean of the last 15% of each
record, and a different window would move the crossing times slightly. The reported
spread across four repetitions does not cover that, because all four share the method.
