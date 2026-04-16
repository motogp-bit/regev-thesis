import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation

def gaussian(n, a, s, d):
    z = np.linspace(-a, a - 1, 2**n)
    amps = np.exp(-np.pi * (z**2) / (2 * s**2))
    
    amps /= np.linalg.norm(amps)
    amps_nd = amps
    for _ in range(d - 1):
        amps_nd = np.kron(amps_nd, amps)
    
    return amps_nd

