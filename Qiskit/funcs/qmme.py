from qiskit import QuantumCircuit, QuantumRegister
from .pmbp import PMBP
from .gates import MSQUARE, SWAP
import numpy as np

def QMME(qc, bases_unpc, N, S, num_qubits, d):
    n = int(np.ceil(np.log2(N)))
    d = len(bases_unpc)
    bases = [int(x) for x in np.asarray(bases_unpc).flat]
    bases_inv = []
    bases_inv = [pow(int(x), -1, N) for x in np.asarray(bases).flat]
    e_regs = qc.qubits[:num_qubits * d]
    acc = qc.qubits[num_qubits * d:num_qubits * d + n]
    accinv = qc.qubits[num_qubits * d + n:num_qubits * d + 2*n]
    temps = qc.qubits[num_qubits * d + 2*n:num_qubits * d + 2*n*d + 2*n + S]
    anc = qc.qubits[num_qubits * d + 2*n*d + 2*n + S: num_qubits * d + 2*n*d + 2*n + S + n*(d-1)]
    ancinv = qc.qubits[num_qubits * d + 2*n*d + 2*n + S + n*(d-1): num_qubits * d + 2*n*d + 2*n + S + 2*n*(d-1)]
    
    qc.append(PMBP(bases,bases_inv,n ,d, 0, N, S, num_qubits))
    for j in range(1, d):
        qc.append(MSQUARE(n, N), [*acc, *accinv, *anc[(j-1)*n:j*n], *ancinv[(j-1)*n:j*n]]) #if MSQUARE requires more ancillas, pass them here
        qc.append(SWAP(n),[*acc, *anc])
        qc.append(SWAP(n),[*accinv[(j-1)*n:j*n], *ancinv[(j-1)*n:j*n]])
        qc.append(PMBP(bases,bases_inv,n ,d, j, N, S, num_qubits),[*e_regs, *acc, *accinv, *temps])
    return qc, acc