# Reconstruction Notice — QG series runner scripts

**Date:** 2026-08-14
**Scope:** `experiments/QG-001_verdict_stability/run.py`,
`experiments/QG-004_mitigation_truth/run.py`,
`experiments/QG-002_verdict_portability/run.py`

## What happened

QG-001, QG-004 and QG-002 were executed on live IBM Quantum hardware on
2026-08-14. The runner scripts and the locally written ProofRecord files were
held in an **ephemeral working directory** that was destroyed by an environment
restart before they were pushed to this repository.

The **hardware execution itself was not lost.** Every circuit submission is
retained server-side by IBM Quantum under its job ID. All twelve job IDs were
recorded before the loss, and every result was re-fetched directly from IBM's
API after the restart.

## What is authoritative, and what is not

| artifact | status |
| --- | --- |
| IBM Quantum job IDs | **authoritative** — server-side, immutable, independently queryable |
| Per-arm counts, survival probabilities, expectation values | **authoritative** — re-fetched from IBM after the loss |
| `PREREGISTRATION.md` and its SHA-256 lock | **authoritative** — pushed to GitHub before execution, hash re-verified intact after the loss (`eec1aab4…9cba9`) |
| Substrate circuit (`common/circuits.py`) | **authoritative** — re-fetched from `derekhone/dark-matter-quantum-sim` (`src/dm_sim/circuits.py`), unmodified |
| Analytic constants `P_analytic = 0.087782`, `P_false = 0.543891` | **authoritative** — recomputed from first principles after the loss and matched exactly |
| Runner scripts (`run.py`) | **RECONSTRUCTED** — see below |
| ProofRecord `record_hash` values | **REGENERATED** — see below |

### Runner scripts are reconstructions

The `run.py` files in this repository were rewritten after the loss to match the
execution they performed. They are faithful to the preregistered conditions and
to the API configuration actually used (documented per-arm in each file), but
they are **not the byte-identical files that were executed.** They are published
so the method is inspectable and repeatable, not as execution evidence. The
execution evidence is the IBM job IDs.

### ProofRecord hashes were regenerated

The pre-loss ProofRecord files carried these self-binding hashes:

- QG-001: `e42c88bc8a30f413227b93874bdd2ec97e460863e83c39b7a1b826b66e45de3a`
- QG-004: `5030b425c0fb4c703b3487a93a36ab9c23982f64f567990cf0bce2feb5095201`

Those files no longer exist, so those hashes cannot be re-derived byte-for-byte.
The ProofRecords published here were rebuilt from the re-fetched IBM job results
and carry **new** hashes. The prior hashes are recorded above for completeness
and are **not** claimed to verify against any file in this repository.

The scientific content is unchanged. Every per-arm survival probability in the
republished records matches the pre-loss values to full printed precision,
because both derive from the same immutable IBM job results.

## Why this notice exists

Remnant Fieldworks' covenant for this corpus is that records are preserved and
corrections are published as dated disclosures rather than silent replacements.
A workspace loss that changes a record hash is exactly the kind of event that
gets quietly smoothed over. It is disclosed here instead.

---

## Second workspace loss — 2026-08-14 (QG-003)

The ephemeral working directory was destroyed a **second time** on the same day,
during the QG-003 depth sweep.

**Lost:** the QG-003 preregistration file, the QG-003 runner script, and the
locally written QG-003 findings note. None had been pushed to this repository
before the loss, so **none carried a published SHA-256 lock.**

**Not lost:** the nine IBM Quantum job IDs, which had been recorded outside the
ephemeral directory. All nine results were re-fetched from IBM after the loss and
**every one matched the pre-loss recorded value exactly (9/9)**. The analytic
targets were independently recomputed from the hash-locked
`common/circuits.py` and matched at all nine depth levels.

### What this costs QG-003

QG-003 is published at a **reduced evidence tier.** The design was fixed before
the jobs were submitted in practice, but that ordering is **asserted, not
provable** — the preregistration hash was never published ahead of execution.
QG-003 must not be cited as hash-locked preregistration. QG-001, QG-002 and
QG-004 are unaffected: their preregistration was pushed and hash-locked before
any job was submitted.

`experiments/QG-003_depth_boundary/run.py` is a reconstruction on the same terms
as the other runners: faithful to the conditions executed, not the byte-identical
file. The execution evidence is the nine job IDs.

The full disclosure, and the corrected process that prevents a third occurrence
(push the preregistration hash to GitHub **before** submitting any job), is in
**[AMENDMENT_V2.md](AMENDMENT_V2.md)**.

All work has since been moved off ephemeral storage.
