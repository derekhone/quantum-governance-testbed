#!/usr/bin/env python3
"""QG-001 - Verdict Stability Under Hardware Noise.

Runs the DM-002 sterile-neutrino substrate circuit on one IBM Quantum processor
under five error-treatment arms and asks whether all five arms produce the SAME
preregistered governance verdict.

Preregistered in PREREGISTRATION.md section 3 (SHA-256 locked before execution).

  PASS iff all five arms yield the same verdict under
       |P_hw - P_analytic| / P_analytic <= 0.10,  P_analytic = 0.087782
  FAIL iff any arm yields a different verdict than the majority
  HOLD iff any arm returns < 100 counts

-------------------------------------------------------------------------------
RECONSTRUCTED SCRIPT - see RECONSTRUCTION_NOTICE.md at the repository root.
The executed original was lost with an ephemeral workspace. This file reproduces
the method and the exact API configuration used per arm. The authoritative
execution evidence is the IBM Quantum job IDs recorded in the ProofRecord.
-------------------------------------------------------------------------------

API notes discovered during the original execution (qiskit-ibm-runtime 0.49.0),
retained here because they are non-obvious and cost several failed submissions:

  * channel must be "ibm_quantum_platform"; "ibm_quantum" raises ValueError.
  * SamplerV2 has NO `resilience` option namespace. Measurement mitigation on
    the Sampler is reached via `options.twirling.enable_measure = True`.
  * ZNE requires EstimatorV2, not SamplerV2.
  * An EstimatorV2 observable must span the FULL transpiled circuit width
    (156 qubits on Heron r2), not the logical width. The single-qubit Z must be
    placed at the physical qubit the transpiler chose, and SparsePauliOp labels
    are little-endian, so Z goes at string index (n - 1 - physical_qubit).
  * `result[0].data.evs` is an unsized numpy scalar; len() raises. Extract with
    float(np.asarray(x).flat[0]).
"""

import json
import os
import sys
import hashlib
import datetime

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, EstimatorV2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "common"))
from circuits import sterile_neutrino_circuit  # noqa: E402

SHOTS = 4096
STEPS = 6
THETA = np.pi / 4
DELTA_M2 = 1.0
ENERGY = 1.0
L = 1.0
THRESHOLD = 0.10
EXPERIMENT_ID = "QG-001-verdict-stability-v1"
ARMS = ["raw", "dd", "meas", "twirl", "zne"]


def analytic_survival():
    """Exact 2-flavor survival probability. Returns 0.087782 for the frozen params."""
    return 1.0 - (np.sin(2 * THETA) ** 2) * np.sin(1.27 * DELTA_M2 * L / ENERGY) ** 2


def build_circuit():
    return sterile_neutrino_circuit(
        delta_m2=DELTA_M2, energy=ENERGY, theta=THETA, L=L, steps=STEPS
    )


def zne_observable(transpiled):
    """Build a full-width Z observable on the physical qubit carrying logical q0."""
    n = transpiled.num_qubits
    phys = transpiled.layout.final_index_layout(filter_ancillas=True)[0]
    label = ["I"] * n
    label[n - 1 - phys] = "Z"  # SparsePauliOp labels are little-endian
    return SparsePauliOp("".join(label)), phys


def run_arm(service, backend, arm, circuit):
    """Execute one treatment arm. Returns a dict with survival probability."""
    if arm == "zne":
        # ZNE is only available on EstimatorV2.
        transpiled = transpile(circuit.remove_final_measurements(inplace=False),
                              backend=backend, optimization_level=1)
        obs, phys = zne_observable(transpiled)
        est = EstimatorV2(mode=backend)
        est.options.resilience.zne_mitigation = True
        est.options.resilience.zne.noise_factors = [1, 3]
        est.options.resilience.zne.extrapolator = "linear"
        est.options.default_shots = SHOTS
        job = est.run([(transpiled, obs)])
        res = job.result()
        ev = float(np.asarray(res[0].data.evs).flat[0])
        return {
            "arm": arm, "job_id": job.job_id(), "expectation_z": ev,
            "survival_probability": (1.0 - ev) / 2.0,  # P(|1>) = (1 - <Z>)/2
            "physical_qubit": int(phys), "observable_width": transpiled.num_qubits,
            "primitive": "EstimatorV2",
            "configuration": "resilience.zne_mitigation=True, noise_factors=[1,3], extrapolator=linear",
        }

    transpiled = transpile(circuit, backend=backend, optimization_level=1)
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    config = "defaults only"
    if arm == "dd":
        sampler.options.dynamical_decoupling.enable = True
        sampler.options.dynamical_decoupling.sequence_type = "XX"
        config = "dynamical_decoupling.enable=True, sequence_type=XX"
    elif arm == "meas":
        # NOTE: SamplerV2 exposes no `resilience` namespace; measurement
        # mitigation is reached through measurement twirling.
        sampler.options.twirling.enable_measure = True
        config = "twirling.enable_measure=True"
    elif arm == "twirl":
        sampler.options.twirling.enable_gates = True
        config = "twirling.enable_gates=True"

    job = sampler.run([transpiled])
    res = job.result()
    creg = next(k for k in dir(res[0].data) if not k.startswith("_"))
    counts = getattr(res[0].data, creg).get_counts()
    total = sum(counts.values())
    return {
        "arm": arm, "job_id": job.job_id(), "counts": counts, "shots": total,
        "survival_probability": counts.get("1", 0) / total,
        "primitive": "SamplerV2", "configuration": config,
    }


def main():
    token = json.load(open(os.path.expanduser(
        "~/.config/abacusai_auth_secrets.json")))["IBM QUANTUM"]["secrets"]["api_token"]["value"]
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)

    # Prefer the shortest queue; free-plan queues differ by orders of magnitude.
    candidates = [b for b in service.backends() if b.status().operational
                  and b.status().pending_jobs < 1000]
    backend = min(candidates, key=lambda b: b.status().pending_jobs)
    print(f"backend: {backend.name} (pending={backend.status().pending_jobs})")

    p_analytic = analytic_survival()
    circuit = build_circuit()
    arm_results = []
    for arm in ARMS:
        r = run_arm(service, backend, arm, circuit)
        p = r["survival_probability"]
        r["relative_error"] = abs(p - p_analytic) / p_analytic
        r["verdict"] = "PASS" if r["relative_error"] <= THRESHOLD else "FAIL"
        arm_results.append(r)
        print(f"  {arm:6s} P={p:.6f} rel_err={r['relative_error']*100:.2f}% {r['verdict']}")

    if any(r.get("shots", SHOTS) < 100 for r in arm_results):
        verdict = "HOLD"
        disagreeing = []
    else:
        verdicts = [r["verdict"] for r in arm_results]
        majority = max(set(verdicts), key=verdicts.count)
        disagreeing = [r["arm"] for r in arm_results if r["verdict"] != majority]
        verdict = "PASS" if len(set(verdicts)) == 1 else "FAIL"

    survivals = [r["survival_probability"] for r in arm_results]
    record = {
        "experiment_id": EXPERIMENT_ID,
        "series": "quantum-governance-testbed",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parameters": {
            "backend": backend.name, "shots": SHOTS, "trotter_steps": STEPS,
            "theta": "pi/4", "delta_m2": DELTA_M2, "energy": ENERGY, "L": L,
            "substrate": "DM-002 sterile neutrino oscillation circuit",
            "arms": ARMS, "optimization_level": 1,
        },
        "observable": "verdict_agreement across five error-treatment arms",
        "result": {
            "P_analytic": round(p_analytic, 6),
            "arms": arm_results,
            "max_spread": max(survivals) - min(survivals),
            "verdict_agreement": 1 if len(set(r["verdict"] for r in arm_results)) == 1 else 0,
            "disagreeing_arms": disagreeing,
        },
        "threshold": "PASS iff all five arms agree under rel_err <= 0.10",
        "verdict": verdict,
        "honest_scope": "toy single-qubit circuit on IBM hardware; not a production governance system",
    }
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["record_hash"] = hashlib.sha256(payload).hexdigest()

    out = os.path.join(os.path.dirname(__file__), "results",
                       f"{EXPERIMENT_ID}.proofrecord.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(record, open(out, "w"), indent=2)
    print(f"\nVERDICT: {verdict}  disagreeing={disagreeing}")
    print(f"record_hash: {record['record_hash']}")


if __name__ == "__main__":
    main()
