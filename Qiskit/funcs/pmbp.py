from qiskit import QuantumCircuit, QuantumRegister
import numpy as np
from .gates.gates import QQMULT, CMMC

def PMBP(e_qubits, bases, n_modulus, i_level, k=2):
    d = len(e_qubits)
    qc = QuantumCircuit(name=f"PMBP_bit_{i_level}")
    
    cl = []
    
    for j in range(d):
        val = int(bases[j])
        leaf_width = max(val.bit_length(), 1) 
        
        reg = QuantumRegister(leaf_width, f'leaf_b{i_level}_e{j}')
        qc.add_register(reg)
        
        qc.x(reg[0]) 
        
        qc.append(CMMC(leaf_width, val), [e_qubits[j], *reg])
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
            
            target_width = min(left.size + right.size, n_modulus)
            
            res = QuantumRegister(target_width, f'node_b{i_level}_L{layer_idx}_{j}')
            qc.add_register(res)
            
            qc.append(QQMULT(left.size, right.size, target_width, k), 
                      [*left, *right, *res])
            
            nl.append(res)
            
        cl = nl
        layer_idx += 1
        
    return qc.to_gate(), cl[0]