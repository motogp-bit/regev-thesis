from qiskit import QuantumCircuit, QuantumRegister
from .pmbp import PMBP
from .gates.gates import MSQUARE, QQMULT
import numpy as np

def QMME(qc, e_regs, precomputed_bases, N, k=2):
    d = len(precomputed_bases)
    n = int(np.ceil(np.log2(N)))
    
    acc = QuantumRegister(n, name='acc')
    acc_sq = QuantumRegister(n, name='acc_sq')
    temp_res = QuantumRegister(n, name='temp_res')
    qc.add_register(acc, acc_sq, temp_res)

    qc.x(acc[0]) 

    msquare_gate = MSQUARE(n, k)
    qmult_gate = QQMULT(n, n, n, k) # n x n -> n bits (Modular)

    for i in reversed(range(d)):
        qc.append(msquare_gate, [*acc, *acc_sq])
        
        for m in range(n):
            qc.swap(acc[m], acc_sq[m])
        
        qc.append(msquare_gate.inverse(), [*acc, *acc_sq])

        current_bit_bases = [precomputed_bases[j][i] for j in range(d)]
        current_e_bits = [e_regs[j][i] for j in range(d)]
        
        pmbp_gate, pmbp_root_reg = PMBP(current_e_bits, current_bit_bases, n, i, k)
        
        for reg in pmbp_gate.definition.metadata['registers']:
            if reg not in qc.qregs:
                qc.add_register(reg)
        qc.append(pmbp_gate, pmbp_gate.qubits)
        
        qc.append(qmult_gate, [*acc, *pmbp_root_reg, *temp_res])

        for m in range(n):
            qc.swap(acc[m], temp_res[m])
            
        qc.append(QQMULT.inverse(), [*acc, *pmbp_root_reg, *temp_res])
        qc.append(pmbp_gate.inverse(), pmbp_gate.qubits)

    return acc