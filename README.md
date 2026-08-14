# quantum-governance-testbed

**Preregistered experiments: can evidence from imperfect quantum hardware be trusted enough to cross an execution boundary?**

Part of the Remnant Fieldworks — Coherent Inheritance Framework (CIF) / ExecutionProof program.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21927975.svg)](https://doi.org/10.5281/zenodo.21927975)

Zenodo (latest, v0.2.0 hardware results): [10.5281/zenodo.21927975](https://doi.org/10.5281/zenodo.21927975)
Zenodo (v0.1.0, preregistration only): [10.5281/zenodo.21927327](https://doi.org/10.5281/zenodo.21927327)
GitHub: [derekhone/quantum-governance-testbed](https://github.com/derekhone/quantum-governance-testbed)

Status: **complete — all four experiments executed on live IBM Quantum hardware**
· QG-001 **FAIL** · QG-002 **FAIL** · QG-003 **PASS (boundary found)** · QG-004 **PASS**

**Positive control:** [BELLWETHER](https://github.com/derekhone/bellwether-testbeds) and [TRINITY](https://github.com/derekhone/trinity-testbeds) (CHSH Bell-violation entropy witnesses on live IBM hardware)
**Substrate:** [DM-002 sterile neutrino oscillation](https://github.com/derekhone/dark-matter-quantum-sim) (single-qubit, clean PASS on ibm_marrakesh)
**Related erratum:** [DM-003 bit-ordering defect](https://github.com/derekhone/dark-matter-quantum-sim/blob/main/ERRATUM_DM-003.md) (FAIL→PASS)

---

## Honest scope (read this first)

These experiments run on **real IBM Quantum hardware** using **toy 2-qubit circuits** whose
analytic answers are known exactly. They test whether **governance verdicts** (PASS/HOLD/FAIL)
are robust to hardware noise conditions, reproducible across backends, and resistant to
unjustified confidence from error mitigation.

They are **NOT** claims about production governance systems, IBM processor characteristics,
or error mitigation quality. The value is methodological: they turn the question *"can
consequential evidence produced by imperfect quantum hardware be trusted enough to cross an
execution boundary?"* into falsifiable, preregistered, ProofRecord-verified properties.

## Results

All results below ran on live IBM Quantum hardware (Heron r2), 4096 shots.
QG-001, QG-002 and QG-004 use the DM-002 sterile-neutrino substrate circuit
(single data qubit, 6 Trotter steps, analytic survival probability
`P_analytic = 0.087782`) on `ibm_marrakesh` unless stated. QG-003 required a
different substrate — see that section for why.

| ID | question | verdict |
|---|---|---|
| **QG-001** | Does the governance verdict survive different noise treatments? | **FAIL** |
| **QG-002** | Does the same verdict hold on two or more independent processors? | **FAIL** |
| **QG-003** | At what circuit depth does error degrade evidence below the trust boundary? | **PASS (boundary found)** — reduced evidence tier |
| **QG-004** | Can mitigation flip a verdict on a deliberately falsified target? | **PASS** |

### QG-001 — Verdict Stability Under Hardware Noise: **FAIL**

Five error-treatment arms, one processor. PASS required all five arms to return the
same verdict under a 10% relative-error threshold. Four did. One did not.

| arm | treatment | survival P | rel. error | verdict |
|---|---|---|---|---|
| raw | none | 0.094727 | 7.91% | PASS |
| dd | dynamical decoupling (XX) | 0.089355 | 1.79% | PASS |
| meas | measurement twirling | 0.095703 | 9.02% | PASS |
| twirl | gate (Pauli) twirling | 0.094238 | 7.35% | PASS |
| **zne** | **zero-noise extrapolation** | **0.102760** | **17.06%** | **FAIL** |

Max spread across arms: 0.013405. Disagreeing arm: `zne`.

**The finding.** Zero-noise extrapolation flipped the governance verdict. The four
suppression and readout arms clustered between 0.089 and 0.096 and all cleared the
threshold; ZNE extrapolated to 0.1028 and crossed it. The dissent is not a mitigation
technique being *worse* — it is a mitigation technique moving a preregistered decision
across a boundary that four other treatments agreed on. Under this preregistration, a
technique that improves accuracy is not a governance failure; one that flips a verdict is.

This is the result the QG series was built to be able to find, and it argues that an
error-mitigation choice is a **governance-relevant** parameter, not an implementation
detail to be left to a default.

### QG-004 — Mitigation Cannot Manufacture Truth: **PASS**

Same five arms, but scored against a **deliberately falsified** target: the survival
probability for `theta = pi/8` (`P_false = 0.543891`) instead of the angle the circuit
actually implements, `theta = pi/4` (`P_true = 0.087782`). Separation: 0.456109.

| arm | survival P | distance from truth | distance from falsehood | false pass? |
|---|---|---|---|---|
| raw | 0.088135 | 0.000353 | 0.455756 | no |
| dd | 0.100098 | 0.012316 | 0.443793 | no |
| meas | 0.097168 | 0.009386 | 0.446723 | no |
| twirl | 0.090088 | 0.002306 | 0.453803 | no |
| zne | 0.095216 | 0.007434 | 0.448675 | no |

`false_pass_count = 0`. Every arm hugged the truth; none moved measurably toward the
falsified target. No arm was closer to falsehood than to truth.

**The finding.** Error mitigation did not manufacture evidence. Read together with
QG-001 this draws a usefully sharp line: mitigation **can** perturb a verdict near a
threshold (QG-001), but it did **not** fabricate support for a claim the circuit never
computed (QG-004). Noise sensitivity and dishonesty are different failure modes, and
only the first one showed up.

### The two verdicts are complementary, not contradictory

QG-001 failed on a 0.013 spread near a threshold. QG-004 passed against a 0.456
separation. A governance system can be fragile at the margin and still be unfalsifiable
at scale — which is an argument for keeping decision thresholds far from the noise floor,
not an argument that mitigation is untrustworthy.

### QG-002 — Verdict Portability Across Processors: **FAIL**

The identical circuit, shot count and raw (unmitigated) configuration, submitted to
two independent physical processors. PASS required both to return the same verdict
under the same 10% relative-error threshold. The preregistered kill condition was
that at least two backends must return results; fewer than two would force HOLD.

| backend | survival P | rel. error | verdict |
|---|---|---|---|
| **ibm_marrakesh** | **0.097412** | **10.97%** | **FAIL** |
| ibm_kingston | 0.086914 | 0.99% | PASS |

Spread: 0.010498. Relative-error ratio between the two processors: **≈11×**.

This experiment was first recorded as **HOLD** because `ibm_kingston` sat in an
extended free-tier queue. It completed roughly five hours later, satisfying the kill
condition, and the HOLD resolved to **FAIL**. The resolution is documented as a dated
amendment in **[AMENDMENT_V2.md](AMENDMENT_V2.md)** §1 rather than by editing the
original record.

**The finding.** The only variable between the two arms was the physical processor.
Nothing about the circuit, the analytic target, the shot count or the treatment
changed — and the verdict changed anyway. `ibm_kingston` produced the most accurate
raw measurement anywhere in this series (0.99%); `ibm_marrakesh` missed the threshold
on the same day. **Backend identity is a governance-relevant parameter.** A system
that certifies a result without binding the processor identity into the record is
certifying something it did not measure.

Read against QG-001: the 10% threshold sits inside this circuit's own cross-processor
variation, which is a second, independent reason not to place a decision boundary
close to the noise floor.

### QG-003 — Noise-Induced Boundary Crossing: **PASS (boundary found)**

A depth sweep on one processor (`ibm_marrakesh`), raw arm only, 4096 shots per level.
The question is where evidence stops being good enough to cross an execution boundary.

**Substrate change, and why.** The DM-002 neutrino circuit cannot answer this question.
At `theta = pi/4` its Hamiltonian has a single non-commuting term, so the Trotter
expansion is exact and the transpiler collapses every step count to **constant depth 6
with zero two-qubit gates**. There is no depth to sweep. QG-003 therefore uses the
**axion–photon coupling circuit** from the same hash-locked `common/circuits.py`, whose
`XX` term compiles to `CNOT–RZ–CNOT` and cannot be collapsed; depth scales linearly
with Trotter steps.

| steps | depth | 2q gates | P_analytic | P_measured | rel. error | verdict |
|---|---|---|---|---|---|---|
| 1 | 14 | 2 | 0.912668 | 0.882080 | 3.35% | **PASS** |
| 2 | 26 | 4 | 0.974505 | 0.867188 | 11.01% | FAIL |
| 4 | 50 | 8 | 0.980555 | 0.660645 | 32.63% | FAIL |
| 6 | 74 | 12 | 0.981481 | 0.407959 | 58.43% | FAIL |
| 8 | 98 | 16 | 0.981793 | **0.265381** | **72.97%** | FAIL |
| 12 | 146 | 24 | 0.982012 | 0.504883 | 48.59% | FAIL |
| 16 | 194 | 32 | 0.982088 | **0.864502** | **11.97%** | FAIL |
| 24 | 290 | 48 | 0.982142 | 0.822998 | 16.20% | FAIL |
| 32 | 386 | 64 | 0.982161 | 0.775879 | 21.00% | FAIL |

**The boundary is at transpiled depth 26** — two Trotter steps, four two-qubit gates.
That is early. One CNOT pair of headroom separates a trustworthy measurement from an
untrustworthy one on this circuit and this processor.

**The finding that matters more.** *The curve is not monotonic in depth.* Fidelity
collapses to the two-qubit depolarized floor (measured 0.265 against a floor of 0.25)
at depth 98, and then **recovers to 0.865 at depth 194 — roughly double the gate
count** — before diverging again. Coherent errors partially cancel at particular
depths, so a circuit can look accurate again after passing through the floor.

The governance consequence is direct: **a fixed depth cutoff is not a reliable trust
control.** "Depth ≤ N" as a policy would have admitted the depth-194 point, which is
outside the threshold and only appears close because errors happened to cancel. Depth
is a heuristic; it is not evidence.

**Evidence tier.** QG-003 is published at a **reduced evidence tier.** Its design was
fixed before the jobs were submitted in practice, but the preregistration file was lost
to a workspace destruction before it could be pushed and hash-locked, so that ordering
is asserted and not provable. QG-003 must not be cited as hash-locked preregistration.
What *is* verifiable: nine server-side IBM job records with timestamps, analytic targets
recomputable from the hash-locked `common/circuits.py`, and a 9/9 exact match of all
measured values re-fetched after the loss. Full disclosure in **[AMENDMENT_V2.md](AMENDMENT_V2.md)** §2.1.

### The series finding

Four experiments asked whether a governance system can trust quantum hardware evidence.
Three of the four metadata heuristics such a system would naturally lean on each
independently **flipped a verdict**:

| heuristic a governance system might trust | experiment | held? |
|---|---|---|
| the error-mitigation label attached to a result | QG-001 | **no** |
| the identity of the processor being interchangeable | QG-002 | **no** |
| circuit depth as a proxy for fidelity | QG-003 | **no** |
| direct comparison of output against known ground truth | QG-004 | **yes** |

The only control that held was the one that checks the answer against something
independently known to be true. Everything else was a label about the computation
rather than a measurement of it.

Two practical conclusions, stated no more strongly than the evidence supports:
**keep decision thresholds far away from the noise floor**, and **verify against ground
truth every time** rather than inferring trust from metadata. Both are claims about
governance design on toy circuits, not claims about IBM hardware or about production
systems.

## The locked experiments

Execution order as run: QG-001 → QG-004 → QG-002 → QG-003. All four are complete.

Amendments and dated corrections: **[AMENDMENT_V2.md](AMENDMENT_V2.md)** (QG-002 HOLD→FAIL
resolution, QG-003 design and evidence-tier disclosure, and the corrected preregistration
routine).

## Preregistration & SHA lock

`PREREGISTRATION.md` SHA-256: `eec1aab45d1da74b170a0b8aabe5d6c1c0d0e753d130f0f03185202e6539cba9`

Frozen in `MANIFEST.sha256` **before any hardware result was computed**, and re-verified
intact after execution. Results are published regardless of PASS / FAIL / HOLD — two of
the four verdicts here are FAILs, published for exactly that reason.

This lock covers QG-001, QG-002 and QG-004. It does **not** cover QG-003, whose
preregistration was lost before publication; see the evidence-tier note above.

## Provenance disclosure

The ephemeral working directory was destroyed **twice** on 2026-08-14. The runner scripts
and locally written ProofRecord files were lost both times, and the second loss also took
the QG-003 preregistration before it could be hash-locked. Every hardware result was
re-fetched from IBM Quantum's server-side job records, which are authoritative and
independently queryable by job ID; all values matched their pre-loss records exactly. The
`run.py` files here are faithful reconstructions, not the byte-identical executed files,
and the ProofRecord hashes were regenerated. See
**[RECONSTRUCTION_NOTICE.md](RECONSTRUCTION_NOTICE.md)** for the full disclosure of what
is authoritative and what is not.

## ProofRecord schema

Identical to the dark-matter-quantum-sim and intent-fidelity-testbed series (self-binding
SHA-256 records).

## License

MIT © 2026 Remnant Fieldworks Inc.
