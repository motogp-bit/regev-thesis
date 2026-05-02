from qiskit import QuantumCircuit, QuantumRegister
from pmbp import PMBP
from gate_defs import MSQUARE, QQMULT
import numpy as np

def QMME(qc, e_regs, precomputed_bases, N):
    d = len(precomputed_bases)
    n = int(np.ceil(np.log2(N)))
    k = 2
    bases = b = QuantumRegister(n * d)
    binv = QuantumRegister(n * d)
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
    qc.append(PMBP(qc, curr_e_bits, curr_bit_bases, n, i, k), [*acc, *acc_inv, *clean_ancilla])
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

def QMME(qc, bases, N, S):
    n = int(np.ceil(np.log2(N)))
    d = len(bases)
    bases_inv = []
    for base in bases:
        bases_inv.append(pow(base, -1, N))
    e_regs = qc.qubits[:n]
    acc = qc.qubits[n:2*n]
    accinv = qc.qubits[2*n:3*n]
    temps = qc.qubits[3*n:2*n*d + 3*n + S]
    anc = qc.qubits[2*n*d + 3*n + S: 2*n*d + 3*n + S + n*(d-1)]
    ancinv = qc.qubits[2*n*d + 3*n + S + n*(d-1): 2*n*d + 3*n + S + 2*n*(d-1)]
    
    qc.append(PMBP(bases,bases_inv,n ,d, 0, N, S))
    for j in range(1, d):
        qc.append(MSQUARE(n, N), [*acc, *accinv, *anc[(j-1)*n:j*n], *ancinv[(j-1)*n:j*n]]) #if MSQUARE requires more ancillas, pass them here
        qc.append(SWAP(n),[*acc, *anc])
        qc.append(SWAP(n),[*accinv[(j-1)*n:j*n], *ancinv[(j-1)*n:j*n]])
        qc.append(PMBP(bases,bases_inv,n ,d, j, N, S),[*e_regs, *acc, *accinv, *temps])
    return qc