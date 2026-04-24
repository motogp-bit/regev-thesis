from qiskit import QuantumCircuit, QuantumRegister
from pmbp import PMBP
from gate_defs import MSQUARE, QQMULT
import numpy as np

def QMME(qc, e_regs, precomputed_bases, N):
    d = len(precomputed_bases)
    n = int(np.ceil(np.log2(N)))
    k = 2
    acc = QuantumRegister(n, name='acc')
    acc_inv = QuantumRegister(n, name='temp')
    dirty_ancilla = QuantumRegister(n, name = "da")
    clean_ancilla = QuantumRegister(n, name = "ca")
    clean_ancilla_1 = QuantumRegister(1, name = "ca1")
    pmbp_root = QuantumRegister(n, name = "pmbp_root")
    qc.add_register(acc, acc_inv, dirty_ancilla, clean_ancilla, clean_ancilla_1, pmbp_root)

    qc.x(acc[0])
    curr_bit_bases = [precomputed_bases[j][i] for j in range(d)]
    curr_e_bits = [e_regs[j][i] for j in range(d)]
    qc.append(PMBP(qc, curr_e_bits, curr_bit_bases, n, i, k), [*pmbp_root, *clean_ancilla])
    qc.append(MOD_PROD(n,n,n,N), [*pmbp_root, *clean_ancilla, *acc, *acc_inv, *dirty_ancilla, *clean_ancilla_1])
    qc.append()
    for i in reversed(range(d)):
        qc.append(msquare_gate, [*acc, *acc_sq])
        for m in range(n):
            qc.swap(acc[m], acc_sq[m])
        qc.append(msquare_gate.inverse(), [*acc, *acc_sq])
        curr_bit_bases = [precomputed_bases[j][i] for j in range(d)]
        curr_e_bits = [e_regs[j][i] for j in range(d)]
        qc, pmbp_root_reg = PMBP(qc, curr_e_bits, curr_bit_bases, n, i, k)
        qc.append(qmult_gate, [*acc, *pmbp_root_reg, *temp_res])

        for m in range(n):
            qc.swap(acc[m], temp_res[m])
        qc.append(qmult_gate.inverse(), [*acc, *pmbp_root_reg, *temp_res])

    return qc, acc