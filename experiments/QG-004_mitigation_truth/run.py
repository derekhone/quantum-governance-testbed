#!/usr/bin/env python3
"""QG-004 - Mitigation Cannot Manufacture Truth.

Runs the DM-002 substrate circuit under the same five error-treatment arms as
QG-001, but evaluates every arm against a DELIBERATELY FALSIFIED target: the
survival probability for theta = pi/8 (P_false = 0.543891) rather than the
circuit's true theta = pi/4 (P_true = 0.087782).

The question is adversarial: can progressively stronger error mitigation drag a
hardware result far enough to endorse a prediction the circuit never made?

Preregistered in PREREGISTRATION.md section 5 (SHA-256 locked before execution).

  PASS iff false_pass_count == 0   (governance system is sound)
  FAIL iff any arm passes the threshold against the falsified target
  HOLD iff any arm returns < 100 counts

-------------------------------------------------------------------------------
RECONSTRUCTED SCRIPT - see RECONSTRUCTION_NOTICE.md at the repository root.
The authoritative execution evidence is the IBM Quantum job IDs in the
ProofRecord. See QG-001/run.py for the qiskit-ibm-runtime API notes that apply
identically here.
-------------------------------------------------------------------------------
"""

import json
import os
import sys
import hashlib
import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "common"))

from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: E402

_qg001 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "QG-001_verdict_stability")
sys.path.insert(0, _qg001)
from run import run_arm, build_circuit, ARMS, SHOTS, STEPS, THRESHOLD  # noqa: E402

THETA_TRUE = np.pi / 4
THETA_FALSE = np.pi / 8  # falsified target: NOT the angle the circuit implements
DELTA_M2 = 1.0
ENERGY = 1.0
L = 1.0
EXPERIMENT_ID = "QG-004-mitigation-truth-v1"


def survival(theta):
    return 1.0 - (np.sin(2 * theta) ** 2) * np.sin(1.27 * DELTA_M2 * L / ENERGY) ** 2


def main():
    token = json.load(open(os.path.expanduser(
        "~/.config/abacusai_auth_secrets.json")))["IBM QUANTUM"]["secrets"]["api_token"]["value"]
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    candidates = [b for b in service.backends() if b.status().operational
                  and b.status().pending_jobs < 1000]
    backend = min(candidates, key=lambda b: b.status().pending_jobs)

    p_true = survival(THETA_TRUE)    # 0.087782
    p_false = survival(THETA_FALSE)  # 0.543891
    print(f"backend={backend.name}  P_true={p_true:.6f}  P_false={p_false:.6f}")

    circuit = build_circuit()
    arm_results = []
    false_pass_count = 0
    for arm in ARMS:
        r = run_arm(service, backend, arm, circuit)
        p = r["survival_probability"]
        r["distance_from_true"] = abs(p - p_true)
        r["distance_from_false"] = abs(p - p_false)
        r["rel_err_vs_true"] = abs(p - p_true) / p_true
        r["rel_err_vs_false"] = abs(p - p_false) / p_false
        r["passes_against_falsified_target"] = r["rel_err_vs_false"] <= THRESHOLD
        r["closer_to_false_than_true"] = r["distance_from_false"] < r["distance_from_true"]
        if r["passes_against_falsified_target"]:
            false_pass_count += 1
        arm_results.append(r)
        print(f"  {arm:6s} P={p:.6f} d_true={r['distance_from_true']:.6f} "
              f"d_false={r['distance_from_false']:.6f} "
              f"false_pass={r['passes_against_falsified_target']}")

    if any(r.get("shots", SHOTS) < 100 for r in arm_results):
        verdict = "HOLD"
    else:
        verdict = "PASS" if false_pass_count == 0 else "FAIL"

    record = {
        "experiment_id": EXPERIMENT_ID,
        "series": "quantum-governance-testbed",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parameters": {
            "backend": backend.name, "shots": SHOTS, "trotter_steps": STEPS,
            "theta_true": "pi/4", "theta_false": "pi/8",
            "delta_m2": DELTA_M2, "energy": ENERGY, "L": L,
            "substrate": "DM-002 sterile neutrino oscillation circuit",
            "arms": ARMS, "optimization_level": 1,
        },
        "observable": "false_pass_count against a deliberately falsified target",
        "result": {
            "P_true": round(p_true, 6),
            "P_false": round(p_false, 6),
            "separation": round(abs(p_false - p_true), 6),
            "arms": arm_results,
            "false_pass_count": false_pass_count,
            "any_arm_closer_to_false": any(r["closer_to_false_than_true"] for r in arm_results),
        },
        "threshold": "PASS iff false_pass_count == 0 against the falsified target",
        "verdict": verdict,
        "honest_scope": "toy single-qubit circuit on IBM hardware; not a production governance system",
    }
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["record_hash"] = hashlib.sha256(payload).hexdigest()

    out = os.path.join(os.path.dirname(__file__), "results",
                       f"{EXPERIMENT_ID}.proofrecord.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(record, open(out, "w"), indent=2)
    print(f"\nVERDICT: {verdict}  false_pass_count={false_pass_count}")
    print(f"record_hash: {record['record_hash']}")


if __name__ == "__main__":
    main()
