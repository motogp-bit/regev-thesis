from qiskit import QuantumCircuit, QuantumRegister
import numpy as np
from gate_defs import QQMULT, CMMC

def PMBP(qc, e_qubits, bases, n, i_level, k=2, workspace, ancilla):
    d = len(e_qubits)
    
    cl = []
    qc.x(workspace[0])
    for j in range(d):
        #val = int(bases[j])
        #leaf_width = max(val.bit_length(), 1) 
        #reg = QuantumRegister(leaf_width, f'leaf_b{i_level}_e{j}')
        #qc.add_register(reg)
        #qc.x(reg[0]) 
        qc.append(CMMC(n, val), [e_qubits[j], *work])
        qc.append(QQMULT(n, n, n, k), [*acc, *work, *acc])
        cl.append(reg)

    layer_idx = 0
    while len(cl) > 1:
        l = len(cl)
        nl = []
        
        if (l % 2 == 1):
            nl.append(cl[l // 2]) 
            
        for j in range(0, l // 2):
            left = cl[j]
            right = cl[l - j - 1]
            
            target_width = min(left.size + right.size, n)
            
            res = QuantumRegister(target_width, f'node_b{i_level}_L{layer_idx}_{j}')
            qc.add_register(res)
            
            qc.append(QQMULT(left.size, right.size, target_width, k), 
                      [*left, *right, *res])
            
            nl.append(res)
            
        cl = nl
        layer_idx += 1
        
    return qc, cl[0]

def PMBP_tree(qc, e_qubits, bases, n, N, inverse_bases):

    d = len(e_qubits)

    values = []
    for i in range(d):
        reg = QuantumRegister(n, f"v{i}")
        qc.add_register(reg)
        values.append(reg)

    work = QuantumRegister(n, "work")
    qc.add_register(work)

    for j in range(d):
        qc.append(CMMC(n, bases[j]), [e_qubits[j], *values[j]])

    current = values
    size = d

    while size > 1:

        next_level = []

        for j in range(0, size // 2):

            left = current[j]
            right = current[size - 1 - j]

            qc.append(QQMULT(n, n, n, N), [
                *left,
                *right,
                *work
            ])

            next_level.append(work)

        current = next_level
        size = len(current)
    return qc, current[0]