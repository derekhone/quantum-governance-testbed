# quantum-governance-testbed

**Preregistered experiments: can evidence from imperfect quantum hardware be trusted enough to cross an execution boundary?**

Part of the Remnant Fieldworks — Coherent Inheritance Framework (CIF) / ExecutionProof program.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21927327.svg)](https://doi.org/10.5281/zenodo.21927327)

Zenodo: [10.5281/zenodo.21927327](https://doi.org/10.5281/zenodo.21927327)
GitHub: [derekhone/quantum-governance-testbed](https://github.com/derekhone/quantum-governance-testbed)

Status: **executed on live IBM Quantum hardware** · QG-001 **FAIL** · QG-004 **PASS** · QG-002 in flight

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

All results below ran on live IBM Quantum hardware (Heron r2, `ibm_marrakesh`),
4096 shots, on the DM-002 sterile-neutrino substrate circuit (single data qubit,
6 Trotter steps, analytic survival probability `P_analytic = 0.087782`).

| ID | question | verdict |
|---|---|---|
| **QG-001** | Does the governance verdict survive different noise treatments? | **FAIL** |
| **QG-002** | Does the same verdict hold on two or more independent processors? | in flight |
| **QG-003** | At what circuit depth does error degrade evidence below the trust boundary? | planned (preregistration after QG-001/002) |
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

### An observation QG-002 raised early

QG-002's `ibm_marrakesh` arm returned survival 0.097412 (10.97% relative error, **FAIL**)
on the same circuit, same backend and same shot count where QG-001's raw arm returned
0.094727 (7.91%, PASS), and where the published DM-002 run returned 4.6%. Run-to-run
drift on one processor moved a verdict across the threshold without any treatment being
applied at all. This is recorded as a secondary observation, not a preregistered result,
and it reinforces rather than undercuts QG-001: the 10% threshold sits inside this
circuit's own run-to-run variation.

## The locked experiments

Execution order: QG-001 → QG-004 → QG-002. QG-003 follows after.

## Preregistration & SHA lock

`PREREGISTRATION.md` SHA-256: `eec1aab45d1da74b170a0b8aabe5d6c1c0d0e753d130f0f03185202e6539cba9`

Frozen in `MANIFEST.sha256` **before any hardware result was computed**, and re-verified
intact after execution. Results are published regardless of PASS / FAIL / HOLD — QG-001's
FAIL is published here for exactly that reason.

## Provenance disclosure

The runner scripts and locally written ProofRecord files were lost to an ephemeral
workspace destruction after execution but before publication. Every hardware result was
re-fetched from IBM Quantum's server-side job records, which are authoritative and
independently queryable by job ID. The `run.py` files here are faithful reconstructions,
and the ProofRecord hashes were regenerated. See **[RECONSTRUCTION_NOTICE.md](RECONSTRUCTION_NOTICE.md)**
for the full disclosure of what is authoritative and what is not.

## ProofRecord schema

Identical to the dark-matter-quantum-sim and intent-fidelity-testbed series (self-binding
SHA-256 records).

## License

MIT © 2026 Remnant Fieldworks Inc.
