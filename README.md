# quantum-governance-testbed

**Preregistered experiments: can evidence from imperfect quantum hardware be trusted enough to cross an execution boundary?**

Part of the Remnant Fieldworks — Coherent Inheritance Framework (CIF) / ExecutionProof program.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21927327.svg)](https://doi.org/10.5281/zenodo.21927327)

Zenodo: [10.5281/zenodo.21927327](https://doi.org/10.5281/zenodo.21927327)
GitHub: [derekhone/quantum-governance-testbed](https://github.com/derekhone/quantum-governance-testbed)

Status: **preregistered & SHA-locked** (`MANIFEST.sha256`) · awaiting IBM Quantum hardware access

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

## The locked experiments

| ID | question | status |
|---|---|---|
| **QG-001** | Does the governance verdict stay the same under different noise treatments (raw, DD, measurement mitigation, twirling, ZNE)? | preregistered |
| **QG-002** | Does the same verdict hold on two or more independent IBM processors? | preregistered |
| **QG-003** | At what circuit depth does error degrade evidence below the trust boundary? | planned (preregistration after QG-001/002) |
| **QG-004** | Can mitigation flip a verdict from FAIL to PASS on a deliberately falsified analytic target? | preregistered |

Execution order: QG-001 → QG-004 → QG-002. QG-003 follows after.

## Preregistration & SHA lock

`PREREGISTRATION.md` SHA-256: `eec1aab45d1da74b170a0b8aabe5d6c1c0d0e753d130f0f03185202e6539cba9`

Frozen in `MANIFEST.sha256` **before any hardware result is computed**. Results will be
published regardless of PASS / FAIL / HOLD.

## ProofRecord schema

Identical to the dark-matter-quantum-sim and intent-fidelity-testbed series (self-binding
SHA-256 records).

## License

MIT © 2026 Remnant Fieldworks Inc.
