# THE 13A AUDIT, RUN: THE PANEL ADJUDICATED TWENTY CLAIMS AND THE RECORD KEPT SEVEN

Written 2026-08-20 02:30 to 03:1x, executing the standing task in
`docs/R9_SESSION_HANDOFF_2026-08-20.md` section 13A. Every number below was measured live
from the journals named, not read from any summary. The extraction scripts are in
`/private/tmp/.../scratchpad/r10audit/` and every count reproduces from the commands in
section 6 of this file.

**The one sentence.** Three claims the handoff carries forward as leads were put to the
adversarial panel and lost, unanimously, with all three voters having pulled and
text-extracted the primary PDF. The handoff records four refutations. There were seventeen.

---

## 1. THE HANDOFF'S OWN FIGURES FOR THE JOURNAL IT POINTS AT ARE ALL WRONG, IN ONE DIRECTION

Section 7B.1 closes with "Raw results: ... journal.jsonl, 266 lines, 190 started, 76
results, 196 agent transcript files." Measured live on that exact path:

| quantity | handoff | live | gap |
|---|---|---|---|
| journal lines | 266 | **331** | +65 |
| `started` records | 190 | **231** | +41 |
| `result` records | 76 | **100** | +24 |
| agent transcript files | 196 | **237** | +41 |

The other copy of the same run, under session `529261e9`, holds 244 / 170 / 74, so the
handoff's figures are neither copy. They are a third, intermediate measurement taken while
the section 11.5 resume merge was still in flight.

This is not bookkeeping. **The twenty-four results the handoff did not know about are where
the un-adjudicated claims live**, and the whole of section 7C rests on characterising them.

---

## 2. THE PANEL: TWENTY CLAIMS, THREE SURVIVED, SEVENTEEN REFUTED

62 verdict votes are in the journal. All 62 join to a claim by parsing the
`## Claim under review` block out of each voter's own prompt, recovered from
`agent-<id>.jsonl`. Zero votes failed to join.

```
verdict votes                       62
distinct claims put to the panel    20
  survived (minority refuted)        3
  refuted (majority refuted)        17
  tied                               0
claims extracted overall           135
claims NEVER put to any panel      115
```

The handoff (sections 5.2 and 7B.1) records **three confirmed and four refuted**. The three
confirmed are correct and complete. **Thirteen refutations are recorded nowhere**, and three
of those thirteen are claims the handoff itself carries forward.

### 2.1 The handoff's stated reason for section 7C being unverified is wrong

Section 7C's provenance warning says: "the rest are single-agent extractions whose verifier
panels died on the account limits." Measured: **every panel that launched returned a
verdict.** None died. Only 20 of 135 claims were ever routed to a panel at all.

The warning's conclusion is right and should stand, so treat 7C.2 to 7C.6 as leads. Its
stated mechanism is wrong, and the correct one is worse: the un-adjudicated claims were not
casualties of the limit, they were **never selected for adjudication**, so nothing about
their survival can be inferred from the panel having run at all.

---

## 3. THREE CLAIMS THE HANDOFF CARRIES FORWARD WERE REFUTED 0-3

All three refutations are `confidence: high`, and in each case the voter fetched and
text-extracted the primary PDF. The pattern across all three is identical and worth naming:
**the numbers were transcribed correctly and the inference from them was inverted.**

### 3.1 `arxiv.org/pdf/2210.10377`, the MEA degradation. VOTED 0 keep / 3 refute

Handoff 7B.1 states this claim "is UNVERIFIED and must be read at source before use" because
"its verifiers all died", and adds that **"it is what prompted building the third accessor."**

Its verifiers did not die. Three returned, all refuting.

The claim: momentum-exchange force error "does NOT stay bounded under grid refinement",
rising 1.75 percent at 128 points per chord to 9.21 percent at 3072, a 24x refinement, while
a control-volume reader held 1.25 to 2.06 percent.

**Every number in that is verbatim correct.** Table III of Kaushal, Succi and Ansumali (Phys.
Rev. E 108, 045304, 2023) reads exactly those rows. What is refuted is the only part that
made it relevant:

- **Table III is a Reynolds sweep, not a grid-refinement study.** Each row is a different
  physical problem. Across the six rows Re rises 500x (1e3 to 5e5) while resolution rises 24x.
  The paper's own sentence immediately above the table: "The resolution demands (measured in
  points per chord) for a converged result vary as a function of Reynolds number."
- **The paper's actual fixed-Re grid convergence test is Fig. 8b**, at Re=100, and it reports
  a convergence-rate ordering with **no MEA non-convergence**.
- Fig. 14 matches a Re^(1/2) scaling, confirmed by arithmetic: ppc ratio 24.0 against
  sqrt(Re ratio) 22.36, fitted exponent 0.511.
- The abstract says the method "significantly reduces the grid size requirement for accurate
  force evaluation", the opposite of the claim's framing.
- Eq. 30 defines Cd with an absolute value, so the tabulated percentages are unsigned.

Counter-source offered independently: Peng et al., Comput. Math. Appl. 2016, momentum
exchange is second-order accurate for force with appropriate bounce-back, its documented
defect being oscillation for MOVING bodies, not refinement-insensitive bias on a fixed one.

**What unwinds.** The third accessor was built anyway and produced a real measurement, so
nothing downstream of it is affected. What is void is the **stated motivation**: the "exact
symptom in a different method, with the accessor named as the cause" was a misread of a
Reynolds sweep. The accessor-hunt should not be resumed on the strength of this paper.

### 3.2 `10.1002/fld.2353`, Han and Cundall. VOTED 0 keep / 3 refute

Handoff 7C.5 states it as a finding: "Han and Cundall compare two force/coupling accessors
inside ONE solver and find the immersed boundary scheme both more accurate AND less sensitive
to lattice resolution than momentum exchange."

The paper is real, the sentence is consistent with its Wiley abstract, and **no voter could
read the full text** (Wiley returned HTTP 402), so that limitation is on the record. Refuted
on the operative half:

- **Contradicted on the direction it predicts.** Mei, Yu, Shyy and Luo 2002, Phys. Rev. E 65,
  041203, read live from NASA NTRS full text, compares momentum-exchange against surface
  stress-integration and finds momentum-exchange "reliable, accurate, and easy to implement"
  and stress-integration "laborious ... difficult to implement". That is the reverse of the
  remedy the claim implies.
- **The IB half is contradicted too.** Peng, Ayala and Wang 2019 (arXiv 1906.05445) find IBM
  first-order and interpolated bounce-back second-order for hydrodynamic force and torque,
  with IBM significantly UNDER-estimating interface stress.
- **Name collision, not shared mechanism.** LBM "momentum exchange" computes force from
  bounce-back of distribution functions on lattice links cut by the solid surface. It is not
  this project's grid-velocity-projection impulse. The paper is 2D D2Q9 LBGK, incompressible,
  viscous drag in a bounded channel, no free surface, no buoyancy, no weak compressibility,
  no MPM.

That last bullet is `docs/CANDIDATE_PAPER_SCOPE_TEST.md` question 1 and question 3 failing
independently, which is the test the handoff's own rule 3 says to run before relaying.

### 3.3 `arxiv.org/pdf/1909.13655`, the grid-independent contact-force accessor. VOTED 0 keep / 3 refute

Sits adjacent to handoff 7C.5's boundary-treatment argument. Refuted on triviality and scope:

- **The benchmark is a momentum identity, not a measurement.** The block is free and resting
  under gravity, so at static equilibrium the reaction MUST equal its own weight. Table 2
  varies only the grid interval; the material-point count is fixed at 2601 in all four runs,
  so the "analytical solution" is the identical constant in every case. The paper's own
  numbers confirm it: 51 contacting points at 0.4902 N, total 25.0002 N, the summed particle
  weight.
- **There is no fluid anywhere in the paper.** A full-text search for
  `fluid|water|buoyan|incompressib|sound speed|weakly compress` hits only the introduction
  and reference list, all citing other authors.
- **The paper says the opposite of grid-independence.** Section 6.1: "the coupling method has
  a strong dependency on the background grid ... neither increase nor decrease the grid size
  can guarantee the increase of accuracy." Section 1 says the coupling "significantly REDUCES
  the coupling dependency", not eliminates.

### 3.4 What the refutations do NOT mean

The panel prompt ends "Default to refuted=true if uncertain." That is a deliberately harsh
prior, so **refuted here means the claim as written did not survive an adversarial pass, not
that the paper says nothing.** In every one of the three, the voters verified the quoted
material as verbatim and refuted the inference. Quote the papers if they are wanted; do not
quote the inferences.

---

## 4. THE SAME ASSERTION APPEARS TWICE, ONCE REFUTED AND ONCE UNTOUCHED, AND THE HANDOFF PRINTS BOTH

This is the structural defect behind section 3 and it will recur.

Two extractor agents independently pulled the same two assertions out of the mDBC paper
family. Agent `aca49ba20`'s versions went to the panel. Agent `a3e035fce`'s versions never
did.

| assertion | `aca49ba20` version | `a3e035fce` version |
|---|---|---|
| DBC leaves a fluid-void gap of order h | **VOTED 1 keep / 2 refute** | **NEVER VOTED ON** |
| the gauge must be relocated +h into the fluid | **VOTED 0 keep / 3 refute** | **NEVER VOTED ON** |

Handoff section 5.2 prints `aca49ba20`'s verdicts: "Refuted by the panel, do not cite: the
DBC depletion-gap mechanism, the +h gauge offset ... which lost 1-2, 0-3." Handoff section
7C.5 then prints `a3e035fce`'s wording of the same two assertions as findings: "leaving an
unphysical fluid-void gap of order the smoothing length h ... The established workaround is
to relocate the numerical gauge a full h into the fluid."

**Same assertion, two sections, opposite treatment, in one document.** Section 5.2 is right
and 7C.5 should be struck.

For the record, what the DBC refutation actually rested on: the voter verified "order of h"
appears three times in English et al. verbatim, and refuted on the word **force**. A
full-text search for `force|drag|load` returns hits only in the introduction. The paper is
about **pressure**. The gap is real; its effect on a force is not what that paper measured.

---

## 5. THE R10 JOURNAL: 399 FINDINGS, AND THE ONES THAT STILL CHANGE SOMETHING

399 findings across 20 agent results. 316 tagged `read-directly`, 47 `relayed`, 36
`inferred`. The R10 report kept 5; handoff section 7D lifted 7 more.

47 read-directly findings assert a contradiction or staleness, and 34 of those name
CLAUDE.md, the register, an item number or a skill. These are the ones that route to
13A.3 class 1 and are absent from the handoff.

### 5.1 The corrections authority contradicts itself on `floor_friction`

Register item 29 (2026-08-18) asserts `floor_friction = 0.55` **IS UNSOURCED** and "nothing
sources it". Register G4a (2026-08-07) and the submitted paper both source it to a
spring-balance measurement by Azhar et al 2023. Two rows of the same authority, opposite
verdicts, eleven days apart. **Resolve before any friction claim reaches the paper**, and
note this sits directly on top of handoff 7D.1's bracket of 0.024 to 1.15 across three
regimes.

### 5.2 CLAUDE.md item L-4 has a documented counter-example, and the register already wants it deleted

L-4 reads "Coarse resolution usually OVER-predicts peak hydrodynamic force. Over-threshold
NO-FORD verdicts are therefore conservative." Two independent findings hit it:

- **A counter-example exists.** Smith and Mack 2014, reported in WRL 2014/07 section 6.3.2,
  found numerical models at 1 m, 5 m and 10 m grids **UNDER-predicted** peak local velocity
  around a building, against both a physical model and observed real-world damage.
- **Internal contradiction.** CLAUDE.md states L-4 as a flat rule while the register's
  Section I lists that exact sentence for deletion on sight.

L-4 is the load-bearing argument that the published NO-FORD verdicts are safe-side. It should
not stay a flat rule.

### 5.3 The class labels were derived from a hull that never ran

"The class audit that licenses the run labels grades a hull SCALED by a factor lam (lengths
4.90 m and 5.20 m, clearances 0.1987 and 0.2109 m). No such hull ever entered a run: solid
volume and particle count are identical across all three masses at every grid."

That is an **eighth paper defect**, and it is upstream of handoff 6.1 item 2. The class claim
is not merely unsatisfied on three axes; the geometry that was graded does not exist in the
data.

### 5.4 The measured Yaris tensor, now on two independent origins

Two agents, `a2bcb1f09` and `a25a0c14c`, independently report a measured 2010 Yaris inertia
tensor and CG, contradicting CLAUDE.md item 4 extension (a) ("No measured Yaris tensor exists
anywhere"). The second names the location: **the very document the project cites as its own
hull provenance, register E1, DOI 10.13021/G8JS5D.** Handoff 7B.2 flags this as unverified
from one origin; there are two, and one gives a checkable address.

This does not license wiring inertia. Item 4's legs (b) and (c) stand untouched: the solver
already computes a better tensor from the real hull cloud, and the axes are transposed. Only
leg (a) is in question.

### 5.5 A stale figure the handoff requotes

The idev burn figure "98.5 to 99.1 percent" is **stale**. Re-measured live by agent
`a88f28243`: **93.8 percent**, because batch node-hours grew from near zero to 12.51 this
month. The timeout half restates cleanly: 109 of 204 idev jobs (53.4 percent) timed out
against the recorded 95 of 184 (51.6 percent). Handoff section 8 requotes the stale form.

### 5.6 Hooks fail closed when they are Python and the file is missing

"PreToolUse exit code 2 blocks the tool call, and `python3 <missing file>` exits 2. So every
hook wired as `python3 $CLAUDE_PROJECT_DIR/.claude/hooks/...` fails CLOSED if its script is
absent, while the `.sh` hooks fail open."

That is the mechanism behind the global "Hooks must fail open" rule, named exactly. An absent
Python hook script is indistinguishable from a hook that deliberately blocked.

### 5.7 Two skill facts that are simply wrong

- `flood-mpm-debugging-reference` states **LS6 is aarch64. LS6 is x86_64.** That skill loads
  before any Methods or Limitations text is written.
- `research-corpus` asserts "332 distinct external papers" and "four prior vehicle fording
  simulations", both of which CLAUDE.md corrected on 2026-08-19.

### 5.8 `xie2023physgaussian` is cited in the tex and performs zero physics validation

Read directly: PhysGaussian's entire quantitative evaluation is rendering PSNR on
synthetically deformed scenes generated with BlenderNeRF "due to the absence of ground truth
for post-deformation", scores 23.87 to 31.15 across six cases. No force, pressure or measured
dynamics anywhere. Its own limitations say material parameters are manually set, and its
future work says it did not handle liquids.

**If it is cited near a physics claim in the paper, move it.** It is evidence about appearance
only. The companion finding is the same for Kerbl 3DGS: a purely photometric objective, with
the paper stating outright that "geometry may be incorrectly placed", and every reported
metric SSIM, PSNR or LPIPS.

### 5.9 Tank confinement now has a citable precedent

Nihei et al ran at **74 percent channel blockage** (vehicle width 1.475 m in a 2.0 m channel)
while citing a criterion that blockage matters above 10 percent, and still deemed their force
evaluation "reasonably valid", because the alternative "could exceed 20 m, which is
practically infeasible for full-scale prototype vehicle ex[periments]".

Use it to declare this project's own tank confinement as a bounded, labelled assumption. Note
the asymmetry honestly: their justification is qualitative trend agreement, not a quantified
blockage correction, so it licenses a labelled assumption and not a claim of negligibility.

### 5.10 Three launcher facts that cost measurements

- **`sbatch --parsable` does not return a bare job id on Vista.** TACC's submit filter prints
  a banner to stdout, so `JID=$(sbatch --parsable ...)` captures the banner and every
  downstream `squeue`/`sacct` fails. Parse with
  `JID=$(sbatch file.sbatch 2>&1 | tail -1 | grep -oE '[0-9]+$')`.
- **`srun --overlap` matters only when an srun STEP is already running.** Proven by A/B on
  one allocation: before the occupying step existed, plain `srun` without `--overlap`
  returned RC=0. A sleep in a batch script is not a step; an idev session is.
- **TACC's srun wrapper rejects any call lacking `-p`**, with "all jobs must have a queue
  name specified".

### 5.11 The MCP deny list is bypassable by alias, verified live in this session

`.claude/settings.local.json` carries 43 deny rules, 24 naming an MCP tool. Checked against
this session's own tool manifest:

| denied name | live alias that no rule covers |
|---|---|
| `mcp__hf__hf_fs_write`, `hf_jobs`, `hf_sandbox_exec`, `dynamic_space` | the same four under `mcp__677ab2f7-...__` |
| `mcp__undermind__write_file`, `delete_file`, `delete_folder`, `delete_deep_search` | the same four under `mcp__52146218-...__` |
| `mcp__wolfram__WolframLanguageEvaluator` | `mcp__e8b78a84-...__WolframLanguageEvaluator` |
| `mcp__filesystem__write_file`, `edit_file`, `move_file`, `create_directory` | `mcp__Desktop_Commander__write_file`, `edit_block`, `move_file`, `create_directory`, and a third copy under `mcp__plugin_desktop-commander_...` |

Nine exact-name UUID aliases plus four capability aliases under a differently-named server.
`disableClaudeAiConnectors` is absent from the file and `enableAllProjectMcpServers` is true.
The UUID changes on reconnect, so a UUID-based deny list needs rechecking every time.

**Two deny rules hold** because no alias exists: `mcp__overleaf__write_file` and
`write_section`. That is the one that matters most, given the Overleaf remote shares no
ancestor with origin.

**And two are inert rather than protective**, which is the section 2 pattern again: this
session's manifest carries **no** `mcp__zotero__zotero_delete_*` tools and **no**
`mcp__canford-tacc__tacc_submit`. Those rules cannot fire because the tools they name do not
exist. The actual submit path is `scripts/tacc.sh` through Bash, which nothing denies.

---

## 6. THE DEEP SEARCHES NOBODY OPENED ALREADY ANSWER TWO LIVE QUESTIONS

Workspace `17299f2a-8dc8-438b-8c84-5abf19395e2c` holds **21 deep searches, all completed**,
confirming the handoff's count. Two of the nine never opened were read tonight.

### 6.1 "Physics Simulation Validation Protocol", 81 papers, run 2026-07-15, never opened

Handoff section 4.3 concludes that **no external band exists to inherit** for criterion 3, and
that any band is therefore this project's own choice. That conclusion stands. This search
supplies what to do instead, in the standard vocabulary:

> "At each validation point report signed discrepancy and a validation interval combining
> reference-data, numerical, and parameter uncertainty; this estimates model error rather
> than producing a binary 'validated' status."

That is ASME V&V 20 framing, and it dissolves the problem rather than solving it: the answer
to "what tolerance do I inherit" is that a validation interval replaces a tolerance. It also
prescribes at least three grid and timestep refinements with observed order and
Richardson/GCI intervals for every decision quantity, and keeping aleatory and epistemic
uncertainty separate.

**The line that bears on the paper's own contribution**, written five weeks ago and never
read:

> "Decision credibility, not numerical agreement, is the governing endpoint: a FORD claim
> requires validated six-DOF outcomes and a conservative margin to the hazard threshold,
> whereas a NO-FORD claim may be issued whenever uncertainty spans or exceeds that boundary."

All 17 gated runs are NO-FORD. That is an asymmetry which licenses the project's published
result under exactly the uncertainty it has, without the validation it lacks. It is a
stronger version of handoff section 6.4's reframe and it arrives with a citation chain.

### 6.2 "Quantitative Flood Traversability Connections", 82 papers, run 2026-07-15, never opened

Its headline is the reframe the project reached independently, months later:

> "A physics-resolved traversability pipeline is most valuable as a calibrated, probabilistic
> link-performance model, not a new binary closure rule."

And its priority 2 is `analysis/probabilistic_verdict.py`'s reason for existing, prescribed
in advance: "Treat MPM parameter sweeps and reconstruction uncertainty as distributions over
limit states (loss of traction, flotation, displacement, stalled vehicle), yielding
P[LS | h, v, slope, vehicle, t] rather than deterministic depth-velocity bands."

It also names something the project believes it lacks. The memory note "The AV safe-speed
surface is the open gap" says nobody publishes v_max(depth, flow velocity). This search
records **video-derived depth-speed functions as an immediately usable external benchmark**,
and a city-scale transport-model validation. Whether those close the gap or only bound it is
unresolved and needs the source read, but "nobody publishes it" is now a claim with a
counter-candidate.

### 6.3 Still unopened, seven of them

`moving vehicle floodwater simulation open source implementations`;
`moving vehicle floodwater GPU particle simulation`;
`how computational researchers audit and defend simulation credibility`;
`GPU particle solver portability scaling and surrogate fidelity`;
`Small Data Physics Surrogates at 36 Conditions`;
`Optical Vehicle Collision Geometry`; and
`Dynamic Vehicle Traction in Floodwater` beyond its friction finding.

---

## 7. WHAT UNWINDS, AND WHAT DOES NOT

**Unwinds.** Handoff 7C.5's Han and Cundall bullet and its DBC gap and gauge-offset bullets.
Handoff 7B.1's characterisation of the 2210.10377 claim as unverified rather than refuted,
and the accessor-hunt motivation resting on it. Handoff 7C's stated reason for its own
provenance warning. Handoff section 8's idev burn figure.

**Does not unwind.** The three panel-confirmed findings in section 5.2 stand exactly as
recorded, including their demotion to PRECEDENT by the scope test. Section 1's physics
result, including its 02:10 withdrawal, is untouched by anything here. Section 7C.1 through
7C.4 and 7C.6 through 7C.7 are unaffected: they were never adjudicated either way, and the
handoff's instruction to treat them as leads with a source remains correct.

**And one thing gets stronger.** The handoff's own rule 2, that a negative result must travel
with the command that produced it, is what this audit is. Every refutation in section 3 was
sitting in a file on this laptop, addressable in one command, for four hours.

---

## 8. RE-DERIVING EVERY NUMBER ABOVE

```
# claims, verdicts, plans, aggregators out of the deep-research journal
/usr/bin/python3 - <<'PY'
import json, glob
for p in glob.glob("/Users/josie/.claude/projects/-Users-josie-can-it-ford/*/subagents/workflows/wf_d942bc1a-e29/journal.jsonl"):
    n=c=v=0
    for line in open(p):
        d=json.loads(line)
        if d.get("type")!="result": continue
        n+=1; r=d["result"]
        c+=len(r.get("claims") or []); v+= 1 if "refuted" in r else 0
    print(p.split("/")[-4][:8], "results",n,"claims",c,"votes",v)
PY
```

To join a vote to its claim, parse `## Claim under review\n"..."` out of the first user
message of `agent-<agentId>.jsonl` in the same run directory. All 62 join.

For the R10 journal, replace the run id with `wf_5266ee59-fb9` and read `findings` instead of
`claims`, each carrying `claim`, `evidence`, `bears_on`, `confidence` and `actionable`.

For the deep searches:

```
ToolSearch "select:mcp__undermind__inspect_deep_searches"
inspect_deep_searches(workspace_id="17299f2a-8dc8-438b-8c84-5abf19395e2c", names=[])
```

Read the **goal text**, not only the summary. Both searches in section 6 name this project's
own configuration inside their goal.

---

## 9. ROUTING, PER 13A.3

| finding | class | destination |
|---|---|---|
| `floor_friction` register self-contradiction (5.1) | 1, contradicts the authority | `r8-register`, not the integration branch |
| L-4 counter-example and Section I conflict (5.2) | 1 | `r8-register`, and L-4 stops being a flat rule |
| measured Yaris tensor, two origins (5.4) | 1 | `r8-register`, against item 4 leg (a) only |
| skill errors: LS6 arch, corpus counts (5.7) | 1 | the skill files, on `r9-corpus-bib` |
| scaled-hull class labels (5.3) | deliverable | `r9-overleaf`, as paper defect eight |
| PhysGaussian citation placement (5.8) | deliverable | `r9-overleaf` |
| the three refuted relays (section 3) | 3, mechanism vs precedent | struck, not relocated |
| validation interval instead of a band (6.1) | 4, benchmark and tolerance | `r9-kramer-extract`, which owns criterion 3 |
| Nihei 74 percent blockage precedent (5.9) | 4 | wherever tank confinement is declared |
| launcher facts (5.10), MCP alias bypass (5.11) | 5, tooling | cost before adopting; the alias bypass is a decision for Josie |
| idev burn 93.8 percent (5.5) | 6 | supersedes the memory entry |

**Not done here, and it is the largest remaining piece.** 115 of 135 deep-research claims and
roughly 350 of 399 R10 findings are still unrouted. This pass read the adjudicated set in
full, the 14 read-directly findings that propagated nowhere at all, and the 34 that assert a
contradiction. The rest is a filter away, and the filter is in section 8.
