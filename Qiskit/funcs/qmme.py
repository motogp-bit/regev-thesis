from qiskit import QuantumCircuit, QuantumRegister
from pmbp import PMBP
from gates import MSQUARE, QQMULT
import numpy as np

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
    return qc, acc