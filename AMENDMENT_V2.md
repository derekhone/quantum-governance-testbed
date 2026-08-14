# Preregistration Amendment v2 — QG series

**Filed:** 2026-08-14, after QG-001 (FAIL) and QG-004 (PASS) were published at
DOI 10.5281/zenodo.21927975.

This single amendment replaces what would otherwise have been three separate
filings. It does three things: it resolves the QG-002 HOLD, it documents QG-003,
and it fixes the process defect that this series exposed. The preregistration
discipline is unchanged; only the paperwork is consolidated.

---

## 1. QG-002 — HOLD resolved to FAIL

QG-002 was preregistered in `PREREGISTRATION.md` (SHA-256
`eec1aab45d1da74b170a0b8aabe5d6c1c0d0e753d130f0f03185202e6539cba9`) and locked
before any hardware access. Its kill condition read: HOLD unless at least two
backends complete.

At first publication only `ibm_marrakesh` had returned, so an honest HOLD was
recorded and no cross-backend verdict was claimed. The `ibm_kingston` job
(`d9v93gob1g9c73a8b3fg`) remained queued for approximately five hours and then
completed. Two backends have now completed, the kill condition is satisfied, and
the experiment is scored as preregistered.

| Backend | Survival | Rel. error | Verdict | Job ID |
|---|---|---|---|---|
| ibm_marrakesh | 0.097412 | 10.97% | FAIL | `d9v93gl0vrcc73bounp0` |
| ibm_kingston | 0.086914 | 0.99% | PASS | `d9v93gob1g9c73a8b3fg` |

**QG-002 verdict: FAIL.** The governance verdict did not reproduce across
backends. Same circuit, same 4096 shots, same analytic target of 0.087782, no
error mitigation on either run. The only variable was which physical processor
executed the job, and the verdict flipped, with roughly an eleven-fold spread in
relative error.

No scoring rule was altered after the fact. This is the preregistered criterion
applied to a late-arriving job.

**Evidence tier: full.** Preregistered and hash-locked before execution.

---

## 2. QG-003 — Noise-Induced Boundary Crossing

### 2.1 Evidence-tier disclosure — read this before the result

The original `PREREGISTRATION.md` deferred QG-003 deliberately, on the grounds
that choosing a depth schedule before seeing QG-001 and QG-002 data would force
arbitrary choices. That deferral was correct.

A QG-003 preregistration was written and the design was fixed before any job was
submitted. That file was then destroyed, together with the runner and the working
results, by a second ephemeral-workspace wipe on the same day — the same failure
mode already disclosed in `RECONSTRUCTION_NOTICE.md`. It had not been pushed to
this repository, and it had not been hash-locked here, before execution began.

Therefore:

> **QG-003 is recorded at a reduced evidence tier. Its design was fixed before
> execution in practice, but that fact is not cryptographically provable and
> should not be treated as if it were. Do not cite QG-003 as a hash-locked
> preregistered result. It is an honestly reported hardware measurement whose
> design document is a post-loss reconstruction.**

What *is* independently verifiable, by anyone with the job IDs:

- The nine IBM Quantum job records exist server-side with their own submission
  timestamps, step counts and measured counts.
- Every analytic target below is recomputable from first principles from
  `common/circuits.py`, which is unchanged and hash-locked.
- All nine measured values were re-fetched from IBM after the wipe and matched
  the pre-loss recorded values exactly, to every digit.

What is not verifiable is the ordering claim: that the document preceded the
jobs. We assert it, we cannot prove it, and we mark it accordingly rather than
letting a reconstruction pass as a lock.

### 2.2 Question

> At what circuit depth does accumulated hardware error grow large enough that a
> governance system should stop trusting the result?

### 2.3 Substrate change, and why it was necessary

QG-001, QG-002 and QG-004 use the DM-002 sterile-neutrino circuit. That circuit
cannot answer a depth question. At theta = pi/4 the Hamiltonian has a single
non-commuting term, so Trotterization is exact and, more importantly, the
transpiler collapses every Trotter step into one rotation. Measured transpiled
depth is 6 at 2 steps and still 6 at 48 steps, with zero two-qubit gates. Varying
the step count varies nothing the hardware sees.

QG-003 therefore uses `axion_circuit` from the same hash-locked substrate file,
`common/circuits.py`. Its XX interaction term is compiled as a CNOT–RZ–CNOT
sandwich that the transpiler cannot collapse, so depth and two-qubit gate count
scale linearly with the step count. The substrate library itself is unmodified.

### 2.4 Design

- Backend: `ibm_marrakesh`. Shots: 4096. Optimization level: 1.
- Arms: one, `raw` (SamplerV2, no error mitigation). QG-001 already characterised
  the mitigation axis at fixed depth; QG-003 isolates depth. One arm per level
  also keeps the queue footprint small.
- Observable: P(|00>).
- Target: for each level, the analytic P(|00>) **at that step count**, not the
  infinite-step limit, so that Trotter discretisation error is never charged to
  hardware noise.
- Scoring, per level: PASS iff |P_measured - P_analytic| / P_analytic <= 0.10.

| Level | Steps | Transpiled depth | 2q gates | P_analytic |
|---|---|---|---|---|
| D1 | 1 | 14 | 2 | 0.912668 |
| D2 | 2 | 26 | 4 | 0.974505 |
| D3 | 4 | 50 | 8 | 0.980555 |
| D4 | 6 | 74 | 12 | 0.981481 |
| D5 | 8 | 98 | 16 | 0.981793 |
| D6 | 12 | 146 | 24 | 0.982012 |
| D7 | 16 | 194 | 32 | 0.982088 |
| D8 | 24 | 290 | 48 | 0.982142 |
| D9 | 32 | 386 | 64 | 0.982161 |

### 2.5 Kill condition

Defer submission if the backend queue exceeds 1000 pending jobs. HOLD if fewer
than five levels complete. Never simulate or interpolate a level that did not run
on hardware.

### 2.6 Experiment-level verdict rule

- **PASS (boundary found):** at least one level PASSes and at least one FAILs, so
  a crossover region exists and is located.
- **FAIL (no crossover):** all levels PASS, or all levels FAIL.
- **HOLD:** fewer than five levels complete.

Note the deliberate asymmetry: a level-level FAIL is an expected and useful
outcome here. QG-003 asks where the boundary is, not whether the hardware is
good. Eight failing levels out of nine is a located boundary, not eight defeats.

---

## 3. Process defect and the corrected routine

The defect this series exposed is not scientific. Every number survived, because
IBM holds the authoritative execution record server-side and job IDs were kept.
What did not survive was the *ordering proof*: a preregistration that exists only
on an ephemeral disk is not locked, however sincerely it was written first.

The corrected routine, effective now, is one step longer and closes the gap:

1. Write the preregistration.
2. **Push it to this repository and record its SHA-256 in `MANIFEST.sha256`
   before a single job is submitted.** The commit timestamp then carries the
   ordering claim, and no local disk failure can weaken it.
3. Submit jobs. Record job IDs immediately, in the repository, not locally.
4. Fetch results, score against the locked criteria, publish regardless of
   outcome.

Consolidation, per the same instruction that produced this single file: one
amendment per phase rather than one per experiment, and one release covering a
phase rather than a release per result. Fewer artifacts, same locks, and the lock
now lands before execution instead of after it.
