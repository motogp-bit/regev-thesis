import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation

def get_gaussian_gate(n, a, s):
    z = np.linspace(-a, a - 1, 2**n)
    amplitudes = np.exp(-np.pi * (z**2) / (2 * s**2))
    
    amplitudes /= np.linalg.norm(amplitudes)
    
    gate = StatePreparation(amplitudes).to_gate()
    gate.name = "Gaussian_Prep"
    return gate

n_qubits = 4
s_param = 2.0
a_range = 5

gaussian_gate = get_gaussian_gate(n_qubits, a_range, s_param)

qc = QuantumCircuit(n_qubits)
qc.append(gaussian_gate, range(n_qubits))
