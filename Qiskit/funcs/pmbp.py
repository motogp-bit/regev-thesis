from qiskit import QuantumCircuit
from gates import CMMC, MOD_PROD

def PMBP(bases, inv_bases, n, d, iteration, N, S):
    qc = QuantumCircuit(2*n*d + 4*n + S)
    controls = qc.qubits[:n]
    acc = qc.qubits[n:2*n]
    acc_inv = qc.qubits[2*n:3*n]
    b = qc.qubits[3*n: 3*n + n*d]
    binv = qc.qubits[3*n + n*d:3*n + 2*n*d]
    acc = qc.qubits[2*n*d + n: 2*n*d + 2*n]
    acc_inv = qc.qubits[2*n*d + 2*n: 2*n*d + 3*n]
    anc = qc.qubits[2*n*d + 3*n:2*n*d + 6*n + S]
    for j in range(d):
        qc.append(CMMC(n, bases[j], iteration), [controls[d * j + iteration], *b[j*n:(j + 1)*n]])
        qc.append(CMMC(n, inv_bases[j], iteration), [controls[d * j + iteration], *binv[j*n:(j + 1)*n]])
    current = [b[j*n:(j + 1)*n] for j in range(d)]
    current_inv = [binv[j*n:(j + 1)*n] for j in range(d)]
    size = d
    history = []

    while size > 1:
        next_level = []
        next_level_inv = []
        level_ops = []
        for j in range(size // 2):
            if size % 2 == 1:
                mid = current[(size // 2)]
                mid_inv = current_inv[(size // 2)]
                next_level.append(mid)
                next_level_inv.append(mid_inv)
            left = current[j]
            right = current[size - 1 - j]
            left_inv = current_inv[j]
            right_inv = current_inv[size - 1 - j]
            g = current[1] if j == 0 else current[0]
            qc.append(
                MOD_PROD(n, N),
                [*left, *left_inv, *right, *right_inv, *g, *anc]
            )
            level_ops.append((left, left_inv, right, right_inv, g))
            next_level.append(right)
            next_level_inv.append(right_inv)
        history.append(level_ops)
        current = next_level
        current_inv = next_level_inv
        size = len(current)

    qc.append(
        MOD_PROD(n, N),
        [*left, *left_inv, *acc, *acc_inv, *g, *anc]
    )
    
    for level_ops in reversed(history):
        for (left, left_inv, right, right_inv, g) in reversed(level_ops):
            qc.append(
                MOD_PROD(n, N),
                [*right, *right_inv, *left_inv, *left_inv, *g, *anc]
            )
                
    return qc.to_gate()
            