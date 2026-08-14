#!/usr/bin/env python3
"""QG-002 - Cross-Backend Verdict Reproducibility.

Runs the identical DM-002 substrate circuit, raw (no suppression, no mitigation),
on two or more independent IBM Quantum processors, and asks whether the same
preregistered governance verdict holds on all of them.

Preregistered in PREREGISTRATION.md section 4 (SHA-256 locked before execution).

  PASS iff verdict_agreement == 1 across all backends
  FAIL iff any backend produces a different verdict
  HOLD iff fewer than 2 operational backends are available at execution time,
       OR any job fails to complete

Operational note that mattered: free/open-plan queue depths differ by orders of
magnitude (ibm_fez carried 24,640 pending jobs while ibm_marrakesh carried 5).
Backends are therefore selected at runtime by queue depth, and all jobs are
submitted before any result is awaited, so a slow backend cannot serialize the
run behind itself.

-------------------------------------------------------------------------------
RECONSTRUCTED SCRIPT - see RECONSTRUCTION_NOTICE.md at the repository root.
The authoritative execution evidence is the IBM Quantum job IDs in the
ProofRecord.
-------------------------------------------------------------------------------
"""

import json
import os
import sys
import time
import hashlib
import datetime

import numpy as np
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
from circuits import sterile_neutrino_circuit  # noqa: E402

SHOTS = 4096
STEPS = 6
THETA = np.pi / 4
DELTA_M2 = 1.0
ENERGY = 1.0
L = 1.0
THRESHOLD = 0.10
MAX_PENDING = 1000   # skip backends with hopeless free-plan queues
MAX_BACKENDS = 3     # preregistered maximum
EXPERIMENT_ID = "QG-002-verdict-portability-v1"


def analytic_survival():
    return 1.0 - (np.sin(2 * THETA) ** 2) * np.sin(1.27 * DELTA_M2 * L / ENERGY) ** 2


def main():
    token = json.load(open(os.path.expanduser(
        "~/.config/abacusai_auth_secrets.json")))["IBM QUANTUM"]["secrets"]["api_token"]["value"]
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)

    usable, skipped = [], []
    for b in service.backends():
        s = b.status()
        if s.operational and s.pending_jobs < MAX_PENDING:
            usable.append((b, s.pending_jobs))
        else:
            skipped.append({"backend": b.name, "operational": s.operational,
                            "pending_jobs": s.pending_jobs})
    usable.sort(key=lambda t: t[1])
    usable = usable[:MAX_BACKENDS]
    for b, p in usable:
        print(f"selected {b.name} (pending={p})")
    for s in skipped:
        print(f"skipped  {s['backend']} (pending={s['pending_jobs']})")

    if len(usable) < 2:
        print("HOLD: fewer than 2 usable backends")
        return

    circuit = sterile_neutrino_circuit(delta_m2=DELTA_M2, energy=ENERGY,
                                      theta=THETA, L=L, steps=STEPS)

    # Submit everything first, then poll. Never block on one backend.
    submitted = []
    for b, pending in usable:
        transpiled = transpile(circuit, backend=b, optimization_level=1)
        sampler = SamplerV2(mode=b)
        sampler.options.default_shots = SHOTS
        job = sampler.run([transpiled])
        submitted.append({"backend": b.name, "job": job, "job_id": job.job_id(),
                          "pending_at_submit": pending})
        print(f"submitted {b.name}: {job.job_id()}")

    p_analytic = analytic_survival()
    results, incomplete = [], []
    deadline = time.time() + 3 * 3600
    remaining = list(submitted)
    while remaining and time.time() < deadline:
        for entry in list(remaining):
            st = str(entry["job"].status())
            if st in ("DONE", "JobStatus.DONE"):
                res = entry["job"].result()
                creg = next(k for k in dir(res[0].data) if not k.startswith("_"))
                counts = getattr(res[0].data, creg).get_counts()
                total = sum(counts.values())
                p = counts.get("1", 0) / total
                rel = abs(p - p_analytic) / p_analytic
                results.append({
                    "backend": entry["backend"], "job_id": entry["job_id"],
                    "counts": counts, "shots": total,
                    "survival_probability": p, "relative_error": rel,
                    "verdict": "PASS" if rel <= THRESHOLD else "FAIL",
                    "pending_at_submit": entry["pending_at_submit"],
                })
                print(f"  {entry['backend']}: P={p:.6f} rel_err={rel*100:.2f}% "
                      f"{results[-1]['verdict']}")
                remaining.remove(entry)
            elif st in ("ERROR", "CANCELLED", "JobStatus.ERROR", "JobStatus.CANCELLED"):
                incomplete.append({"backend": entry["backend"],
                                   "job_id": entry["job_id"], "status": st})
                remaining.remove(entry)
        if remaining:
            time.sleep(60)

    for entry in remaining:
        incomplete.append({"backend": entry["backend"], "job_id": entry["job_id"],
                           "status": str(entry["job"].status())})

    # Preregistered kill condition: any job failing to complete forces HOLD.
    if incomplete or len(results) < 2:
        verdict = "HOLD"
    else:
        verdicts = [r["verdict"] for r in results]
        verdict = "PASS" if len(set(verdicts)) == 1 else "FAIL"

    survivals = [r["survival_probability"] for r in results]
    record = {
        "experiment_id": EXPERIMENT_ID,
        "series": "quantum-governance-testbed",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parameters": {
            "shots": SHOTS, "trotter_steps": STEPS, "theta": "pi/4",
            "delta_m2": DELTA_M2, "energy": ENERGY, "L": L,
            "substrate": "DM-002 sterile neutrino oscillation circuit",
            "treatment": "raw (no suppression, no mitigation)",
            "optimization_level": 1,
            "backends_submitted": [e["backend"] for e in submitted],
            "backends_skipped": skipped,
        },
        "observable": "verdict_agreement across independent IBM Quantum processors",
        "result": {
            "P_analytic": round(p_analytic, 6),
            "backends": results,
            "backends_completed": len(results),
            "backends_incomplete": incomplete,
            "max_spread": (max(survivals) - min(survivals)) if len(survivals) > 1 else None,
            "verdict_agreement": (1 if len(results) >= 2 and
                                  len(set(r["verdict"] for r in results)) == 1 else 0),
        },
        "threshold": "PASS iff all backends agree under rel_err <= 0.10; "
                     "HOLD if fewer than 2 backends complete",
        "verdict": verdict,
        "honest_scope": "toy single-qubit circuit on IBM hardware; not a production governance system",
    }
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["record_hash"] = hashlib.sha256(payload).hexdigest()

    out = os.path.join(os.path.dirname(__file__), "results",
                       f"{EXPERIMENT_ID}.proofrecord.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(record, open(out, "w"), indent=2)
    print(f"\nVERDICT: {verdict}  completed={len(results)} incomplete={len(incomplete)}")
    print(f"record_hash: {record['record_hash']}")


if __name__ == "__main__":
    main()
