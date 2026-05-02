from qiskit import QuantumCircuit, QuantumRegister
import numpy as np
from gate_defs import *

def PMBP(bases, inv_bases, n, d, iteration, N, S):
    b = QuantumRegister(n * d)
    binv = QuantumRegister(n * d) 
    controls = QuantumRegister(n)
    anc = QuantumRegister(3*n + S)
    qc = QuantumCircuit()
    for j in range(d):
        qc.append(CMMC(n, bases[j], iteration), [*controls[d * j + iteration], *b[j*n:(j + 1)*n]])
        qc.append(CMMC(n, inv_bases[j], iteration), [*controls[d * j + iteration], *binv[j*n:(j + 1)*n]])
    current = [b[j*n:(j + 1)*n] for j in range(d)]
    current_inv = [binv[j*n:(j + 1)*n] for j in range(d)]
    size = d
    while size > 1:
        next_level = []
        next_level_inv = []
        for j in range(size // 2):
            if size % 2 == 1: 
                next_level.append(current[(n // 2) + 1]) 
                next_level_inv.append(current[(n // 2) + 1]) 
            left = current[j]
            right = current[size - 1 - j]
            g = current[1] if j == 0 else current[0]
            left_inv = current_inv[j]
            right_inv = current_inv[size - 1 - j]
            qc.append(MOD_PROD(n, N),[*left, *right,*left_inv, *right_inv, *g, *anc]) 
            #REWRITE SO THIS WORKS ACCORDINGLY
            next_level.append(right)
            next_level_inv.append(right_inv)
        current = next_level
        current_inv = next_level_inv
        size = len(current) // n
    return qc, current[0]
            