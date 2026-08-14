"""QG-003 - Noise-Induced Boundary Crossing.

Submits the axion circuit at nine depth levels to a single backend, raw arm only,
and scores each level against the analytic P(|00>) at that step count.

PROVENANCE: this file is a faithful RECONSTRUCTION. The executed original was
destroyed by an ephemeral-workspace wipe. The authoritative record of what ran is
the set of nine IBM Quantum job IDs listed in the ProofRecord under results/.
See RECONSTRUCTION_NOTICE.md and AMENDMENT_V2.md section 2.1.

HONEST SCOPE: a two-qubit toy circuit on one IBM backend. Not a production
governance system, and not a general claim about quantum hardware.
"""
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, "common")

from circuits import axion_circuit  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager  # noqa: E402
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2  # noqa: E402

DEPTH_SCHEDULE = [1, 2, 4, 6, 8, 12, 16, 24, 32]
SHOTS = 4096
THRESHOLD = 0.10
BACKEND_NAME = "ibm_marrakesh"
MAX_QUEUE = 1000  # preregistered kill condition
MIN_LEVELS = 5    # fewer completed levels than this -> HOLD


def analytic_p00(steps: int) -> float:
    """Analytic P(|00>) at this exact step count, not the infinite-step limit."""
    qc = axion_circuit(steps=steps)
    qc.remove_final_measurements()
    return float(abs(Statevector.from_instruction(qc)[0]) ** 2)


def main() -> None:
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
    backend = service.backend(BACKEND_NAME)

    status = backend.status()
    print(f"{BACKEND_NAME}: pending={status.pending_jobs} operational={status.operational}")
    if status.pending_jobs > MAX_QUEUE:
        print(f"KILL CONDITION: queue {status.pending_jobs} > {MAX_QUEUE}. Deferring.")
        return

    pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
    sampler = SamplerV2(mode=backend)

    submitted = []
    for steps in DEPTH_SCHEDULE:
        transpiled = pass_manager.run(axion_circuit(steps=steps))
        two_q = sum(1 for inst in transpiled.data if len(inst.qubits) == 2)
        job = sampler.run([transpiled], shots=SHOTS)
        submitted.append(
            {
                "steps": steps,
                "depth": transpiled.depth(),
                "two_q": two_q,
                "p_analytic": analytic_p00(steps),
                "job_id": job.job_id(),
            }
        )
        print(f"submitted steps={steps} depth={transpiled.depth()} job={job.job_id()}")
        time.sleep(1)

    # Persist job IDs before waiting on any result. The job IDs are the only
    # thing that cannot be recovered if this process or its disk disappears.
    with open("jobs.json", "w") as handle:
        json.dump(submitted, handle, indent=2)

    results = []
    for entry in submitted:
        job = service.job(entry["job_id"])
        while str(job.status()) not in ("DONE", "ERROR", "CANCELLED"):
            time.sleep(30)
            job = service.job(entry["job_id"])
        if str(job.status()) != "DONE":
            print(f"steps={entry['steps']} did not complete: {job.status()}")
            continue

        counts = job.result()[0].data.c.get_counts()
        shots = sum(counts.values())
        p_measured = counts.get("00", 0) / shots
        rel_err = abs(p_measured - entry["p_analytic"]) / entry["p_analytic"]
        results.append(
            {
                **entry,
                "counts": counts,
                "shots": shots,
                "p_measured": p_measured,
                "rel_err": rel_err,
                "verdict": "PASS" if rel_err <= THRESHOLD else "FAIL",
            }
        )
        print(f"steps={entry['steps']:3d} p={p_measured:.6f} rel_err={rel_err * 100:6.2f}%")

    verdicts = [r["verdict"] for r in results]
    if len(verdicts) < MIN_LEVELS:
        experiment_verdict = "HOLD"
    elif "PASS" in verdicts and "FAIL" in verdicts:
        experiment_verdict = "PASS"  # a crossover region exists and is located
    else:
        experiment_verdict = "FAIL"  # no crossover: all PASS or all FAIL

    with open("results.json", "w") as handle:
        json.dump({"results": results, "experiment_verdict": experiment_verdict}, handle, indent=2)
    print(f"experiment verdict: {experiment_verdict}")


if __name__ == "__main__":
    main()
