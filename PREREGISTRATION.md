# Quantum Governance (QG) Series — Preregistration

**Series:** quantum-governance-testbed
**Program:** Remnant Fieldworks Inc. — Coherent Inheritance Framework / ExecutionProof
**Repository:** https://github.com/derekhone/quantum-governance-testbed
**Date:** 2026-08-14
**Status:** LOCKED (SHA-256 in `MANIFEST.sha256`)

---

## 0. Covenant

Questions, thresholds, pass rules, and kill conditions are frozen in this file and
SHA-locked **before any hardware result is computed**. Results are published
regardless of `PASS`, `FAIL`, or `HOLD`. Honest scope declarations are mandatory.

The QG series differs from the dark-matter-quantum-sim series in a deliberate way:
DM experiments asked *"does our toy Hamiltonian reproduce the expected physics?"*
QG experiments ask *"when hardware produces evidence, is the evidence trustworthy
enough to cross a governance boundary?"* Every QG experiment connects IBM Quantum
hardware directly to ExecutionProof's authorization question.

Positive control: The BELLWETHER and TRINITY series (CHSH Bell-violation entropy
witnesses on live IBM hardware) serve as the established positive control for this
series. A separate CHSH experiment is not preregistered because it already exists
in the published corpus. See:
- BELLWETHER: https://github.com/derekhone/bellwether-testbeds
- TRINITY: https://github.com/derekhone/trinity-testbeds

---

## 1. Honest scope (read this first)

These experiments run on **real IBM Quantum hardware** using **toy 2-qubit
circuits** whose analytic answers are known exactly. They test whether
**governance verdicts** (PASS/HOLD/FAIL as defined by preregistered thresholds)
are robust to hardware noise conditions, reproducible across backends, and
resistant to unjustified confidence from error mitigation.

They are:

- **NOT** claims about the scalability of quantum governance to production systems,
- **NOT** claims about the noise characteristics of any specific IBM processor,
- **NOT** certifications of IBM's error mitigation or suppression tooling,
- **NOT** comparisons between quantum computing platforms.

The value is methodological: they turn the slogan *"hardware noise could change
a decision"* into a **falsifiable, preregistered, ProofRecord-verified** property.

---

## 2. Substrate circuit

All QG experiments use the **DM-002 sterile neutrino oscillation circuit** as the
substrate. Reasons:

1. DM-002 is a clean hardware PASS (relative error 4.6%, threshold 10%) on
   `ibm_marrakesh` with 4096 shots (DOI 10.5281/zenodo.21926912).
2. It is a single-qubit circuit (1 data qubit, no entanglement), minimizing
   confounders from CNOT error.
3. The analytic survival probability is known exactly:
   `P(ν_μ → ν_μ) = 1 − sin²(2θ) sin²(1.27 Δm² L/E)`
   with θ = π/4, Δm² = 1.0, E = 1.0, L = 1.0 → P_survival = 0.087782.
4. The circuit parameters (6 Trotter steps) and state preparation (X gate + RZ/RX
   rotations) are frozen in the published `circuits.py`.

The substrate circuit is imported directly from `dark-matter-quantum-sim` without
modification. Any change to the circuit would require a new preregistration.

---

## 3. EXPERIMENT QG-001 — Verdict Stability Under Hardware Noise

### Question

Does the governance verdict (PASS/HOLD/FAIL) remain the same when the same
circuit is executed on the same backend under different noise treatment
conditions?

### Background

IBM Quantum's current tooling provides several error suppression and mitigation
techniques that can be applied at transpilation and execution time:

| technique | IBM category | mechanism |
|---|---|---|
| Raw (no treatment) | baseline | no error suppression or mitigation |
| Dynamical Decoupling (DD) | suppression | inserts identity-equivalent pulse sequences during idle periods to refocus decoherence |
| Measurement Mitigation (Meas) | mitigation | calibrates and inverts the readout confusion matrix |
| Gate Twirling (Twirl) | suppression | randomizes coherent gate errors into stochastic noise via Pauli twirling |
| Zero Noise Extrapolation (ZNE) | mitigation | amplifies noise at multiple scale factors and extrapolates to the zero-noise limit |

These are not speculative features; they are part of the production
`qiskit-ibm-runtime` Estimator and Sampler primitives.

### Conditions (frozen)

Five treatment arms, all on the same backend, same circuit, same shot count:

| arm | label | configuration |
|---|---|---|
| A | `raw` | No error suppression or mitigation. Transpile + run with default settings. |
| B | `dd` | Dynamical decoupling enabled (XX sequence). |
| C | `meas` | Measurement error mitigation enabled. |
| D | `twirl` | Pauli twirling enabled on 2-qubit gates (applies to Trotter CNOTs if DM-002 circuit uses them in the transpiled form; if the transpiled circuit has no 2-qubit gates, this arm is noted as vacuous in the record). |
| E | `zne` | Zero noise extrapolation enabled (linear, 2 noise factors). |

Each arm: 4096 shots, same backend (selected at runtime as the least-busy
operational processor), same transpilation seed (42).

### Observable

`survival_probability` = P(measuring outcome '1') for each arm.

Primary observable: `verdict_agreement` = 1 iff all five arms produce the same
verdict under the DM-002 threshold (PASS iff |P_hw − P_analytic| / P_analytic ≤
0.10, where P_analytic = 0.087782).

Secondary observables (non-verdict): per-arm survival probability, per-arm
relative error, max spread across arms, the specific arm(s) that disagree (if
any).

### Preregistered threshold

- **PASS** iff `verdict_agreement == 1` (all five arms yield the same verdict).
- **FAIL** iff any arm produces a different verdict than the majority.
- **HOLD** (kill) iff any arm returns fewer than 100 counts total (hardware
  failure / job cancellation), or if the backend reports a calibration warning
  during the run window.

If the experiment FAILs, the record must identify which arm(s) diverged and
whether the divergence was toward a more or less accurate result. A mitigation
technique that improves accuracy is not a governance failure; one that flips a
verdict from PASS to FAIL (or vice versa) is.

---

## 4. EXPERIMENT QG-002 — Cross-Backend Verdict Reproducibility

### Question

Does the same preregistered verdict hold when the identical circuit is executed
on two or more independent IBM Quantum processors?

### Background

Reproducibility is the claim the corpus currently cannot make. All IBM hardware
results to date (DM-001, DM-002, DM-003) ran on a single processor
(`ibm_marrakesh`). If a governance verdict changes on a different processor with
the same gate set and connectivity, the verdict is processor-dependent, not
physics-dependent — and a processor-dependent verdict has no business crossing
an execution boundary.

### Conditions (frozen)

- **Circuit:** DM-002 sterile neutrino, identical to the published run.
- **Shots:** 4096 per backend.
- **Backends:** Minimum 2, maximum 3, selected from the set of operational IBM
  Quantum processors available at execution time. Each must be a different
  physical processor (not a simulator). Backend names are recorded in the
  ProofRecord but not preregistered, since availability is determined at runtime.
- **Treatment:** Raw (no error suppression or mitigation) to isolate backend
  differences from mitigation differences (which are QG-001's domain).
- **Transpilation:** Optimization level 1, no fixed seed (each backend has
  different topology, so the transpiled circuit will differ).

### Observable

`survival_probability` per backend.

Primary observable: `verdict_agreement` = 1 iff all backends produce the same
verdict under the DM-002 threshold (PASS iff relative error ≤ 0.10).

Secondary observables: per-backend survival probability, per-backend relative
error, max inter-backend spread.

### Preregistered threshold

- **PASS** iff `verdict_agreement == 1` across all backends.
- **FAIL** iff any backend produces a different verdict.
- **HOLD** (kill) iff fewer than 2 operational backends are available at
  execution time, or any job fails to complete.

---

## 5. EXPERIMENT QG-004 — Mitigation Cannot Manufacture Truth

### Question

Can progressively stronger error mitigation flip a governance verdict from FAIL
to PASS on a circuit whose **analytic prediction has been deliberately
falsified**?

### Background

Error mitigation is designed to reduce the gap between a noisy hardware result
and the true (noiseless) answer. But in a governance context, the question is
not "did mitigation make the result more accurate?" — it is "could mitigation
create unjustified confidence in a result that is fundamentally wrong?"

To test this cleanly, QG-004 uses a **deliberately falsified analytic target**.
The substrate circuit is the DM-002 sterile neutrino oscillation (whose true
analytic survival probability is 0.087782 at the frozen parameters). The
falsified target is constructed by claiming the analytic answer is a different
value — specifically, by evaluating the survival formula at a **wrong mixing
angle** θ_false = π/8 (instead of the true θ = π/4), which yields:

P_false = 1 − sin²(2 × π/8) sin²(1.27 × 1.0 × 1.0 / 1.0)
        = 1 − sin²(π/4) sin²(1.27)
        = 1 − 0.5 × sin²(1.27)
        = 1 − 0.5 × 0.912218
        = 0.543891

The falsified target (0.5439) is far from the true analytic value (0.0878). No
amount of legitimate error mitigation should push a hardware measurement of the
true circuit toward a value that the circuit does not produce.

This design avoids building on DM-003, whose published FAIL verdict has been
identified as a measurement-extraction defect (see DM-003 erratum in
`dark-matter-quantum-sim`). Using a deliberately falsified target is a stronger
test: it controls the degree of falsification and does not depend on any
previous hardware bug.

### Conditions (frozen)

- **Circuit:** DM-002 sterile neutrino, unmodified.
- **True analytic answer:** P_true = 0.087782 (θ = π/4).
- **Falsified analytic target:** P_false = 0.543891 (θ_false = π/8).
- **Threshold applied against the falsified target:** PASS iff
  |P_hw − P_false| / P_false ≤ 0.10.
- **Shots:** 4096.
- **Backend:** Same as QG-001 (least-busy operational processor).

Five mitigation arms (same as QG-001):

| arm | label |
|---|---|
| A | `raw` |
| B | `dd` |
| C | `meas` |
| D | `twirl` |
| E | `zne` |

### Observable

Primary: `false_pass_count` = number of arms where the hardware result passes
the threshold when evaluated against the **falsified** target.

Secondary: per-arm survival probability, per-arm distance from P_true, per-arm
distance from P_false, whether any arm is closer to P_false than to P_true.

### Preregistered threshold

- **PASS** (the governance system is sound) iff `false_pass_count == 0` — no
  mitigation technique produces a result that passes the threshold against the
  falsified target.
- **FAIL** (the governance system has a vulnerability) iff any arm passes
  against the falsified target. The record must identify which technique(s)
  produced the false pass and how close the mitigated value was to P_false.
- **HOLD** (kill) iff any arm returns fewer than 100 counts, or hardware
  failure prevents completion.

Note: it is **expected** that all arms will produce results near P_true ≈ 0.088
(since the circuit computes the true physics), and P_false ≈ 0.544 is far
enough away that no legitimate mitigation should reach it. A FAIL here would be
a significant finding: it would mean error mitigation can manufacture evidence
that crosses a governance threshold for a prediction the circuit never made.

---

## 6. QG-003 — Noise-Induced Boundary Crossing (planned, not yet preregistered)

QG-003 is documented in the series plan but is **not preregistered in this file**.
It will receive its own preregistration amendment (`PREREGISTRATION_V2_AMENDMENT.md`)
once QG-001 and QG-002 have been executed. The design question:

> At what circuit depth does hardware error become large enough that the system
> should stop trusting the result?

This experiment requires choosing a depth schedule and a trust-boundary threshold
that should be informed by the QG-001 and QG-002 results. Preregistering it now
without that data would require arbitrary choices that reduce the experiment's
value.

---

## 7. Series plan and execution order

| ID | experiment | status | dependency |
|---|---|---|---|
| QG-001 | Verdict Stability Under Hardware Noise | preregistered, awaiting hardware | none |
| QG-002 | Cross-Backend Verdict Reproducibility | preregistered, awaiting hardware | none |
| QG-003 | Noise-Induced Boundary Crossing | planned, not yet preregistered | QG-001/002 results |
| QG-004 | Mitigation Cannot Manufacture Truth | preregistered, awaiting hardware + DM-003 erratum | none (uses falsified target) |

Execution order: QG-001, then QG-004, then QG-002.

QG-003 will be preregistered after the first three are complete.

QG-005 (CHSH positive control) is **not included**. The BELLWETHER and TRINITY
series already serve this function. Citing them is cleaner than repeating the
benchmark.

---

## 8. ProofRecord schema

Identical to the dark-matter-quantum-sim and intent-fidelity-testbed series:

```json
{
  "experiment_id": "QG-001-verdict-stability-v1",
  "series": "quantum-governance-testbed",
  "timestamp_utc": "...",
  "parameters": { ... },
  "observable": "...",
  "result": { ... },
  "threshold": "...",
  "verdict": "PASS | FAIL | HOLD",
  "honest_scope": "toy 2-qubit circuit on IBM hardware; not a production governance system",
  "record_hash": "<SHA-256 self-binding hash>"
}
```

---

## 9. Freeze

Upon writing this file's SHA-256 to `MANIFEST.sha256`, sections 0–8 are frozen
for version `v1` of the `quantum-governance-testbed` series. Any change to a
QG-001, QG-002, or QG-004 question, threshold, or pass rule requires a new
preregistration (`v2`) with a new hash and dated entry.

---

## License

MIT © 2026 Remnant Fieldworks Inc.
