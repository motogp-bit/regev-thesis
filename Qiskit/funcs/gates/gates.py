from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFT
import numpy as np

from qiskit import QuantumCircuit, QuantumRegister

def CMMC(n_reg, constant):
    """
    n_reg: size of the target leaf register
    constant: precomputed b_j^(2^i)
    """
    ctrl = QuantumRegister(1, name='ctrl')
    reg = QuantumRegister(n_reg, name='reg')
    qc = QuantumCircuit(ctrl, reg, name=f"CMMC_{int(constant)}")
    
    bin_const = format(int(constant), f'0{n_reg}b')[::-1]

    for j in range(n_reg):
        target_bit = int(bin_const[j])
        initial_bit = 1 if j == 0 else 0
        
        if target_bit != initial_bit:
            qc.cx(ctrl[0], reg[j])

    return qc.to_gate()

def MSQUARE(n, k=2):
    reg_a = QuantumRegister(n, 'a')
    reg_res = QuantumRegister(n, 'res')
    qc = QuantumCircuit(reg_a, reg_res, name="MSQUARE_Opt")

    qc.append(QFT(n, approximation_degree=k, do_swaps=False), reg_res)

    for i in range(n):
        p_diag = 2 * i
        for m in range(p_diag, n):
            angle = 2 * np.pi / (2**(m - p_diag + 1))
            qc.cp(angle, reg_a[i], reg_res[m])

        for j in range(i + 1, n):
            p_off = i + j + 1 
            for m in range(p_off, n):
                angle = 2 * np.pi / (2**(m - p_off + 1))
                qc.mcp(angle, [reg_a[i], reg_a[j]], reg_res[m])

    qc.append(QFT(n, approximation_degree=k, do_swaps=False).inverse(), reg_res)

    return qc.to_gate()

def QQMULT(n_a, n_b, n_res, k=2):
    reg_a = QuantumRegister(n_a, 'a')
    reg_b = QuantumRegister(n_b, 'b')
    reg_res = QuantumRegister(n_res, 'res')
    qc = QuantumCircuit(reg_a, reg_b, reg_res, name="QMULT_Asym")

    qc.append(QFT(n_res, approximation_degree=k, do_swaps=False), reg_res)

    for i in range(n_a):        
        for j in range(n_b):    
            shift = i + j
            for m in range(shift, n_res):
                angle = 2 * np.pi / (2**(m - shift + 1))
                qc.mcp(angle, [reg_a[i], reg_b[j]], reg_res[m])

    qc.append(QFT(n_res, approximation_degree=k, do_swaps=False).inverse(), reg_res)

    return qc.to_gate()