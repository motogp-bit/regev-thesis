from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFT
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister

def CMMC(n_reg, constant):
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
    QFT_gate = QFT(n,approximation_degree=k, do_swaps=False).to_gate()
    qc.append(QFT_gate, reg_res)

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

    qc.append(QFT_gate.inverse(), reg_res)

    return qc.to_gate()

from qiskit.circuit.library import DraperQFTAdder

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import DraperQFTAdder, QFT

def QADD(n, N):
    a = QuantumRegister(n, 'a')
    b = QuantumRegister(n, 'b')
    anc = QuantumRegister(1, 'anc')
    qft_gate = QFT(num_qubits=n, do_swaps=False).to_gate()
    qc = QuantumCircuit(a, b, anc, name="ModAdder")
    qc.append(qft_gate, b)
    adder = DraperQFTAdder(n, kind="fixed", overlap=0)
    qc.append(adder, [*a, *b])

    for j in range(n):
        angle = -2 * np.pi * N / (2**(j + 1))
        qc.p(angle, b[j])
    qc.append(qft_gate.inverse(), b)
    qc.cx(b[n-1], anc[0])
    qc.append(qft_gate, b)
    for j in range(n):
        angle = 2 * np.pi * N / (2**(j + 1))
        qc.cp(angle, anc[0], b[j])

    qc.append(qft_gate.inverse(), b)

    return qc.to_gate()


def compare_geq(n_res, N):
    qr = QuantumRegister(n_res, 'res')
    anc = QuantumRegister(1, 'anc')
    qc = QuantumCircuit(qr, anc, name="compare_geq")
    
    QFT_gate = QFT(n_res, do_swaps=False).to_gate()
    
    qc.append(QFT_gate, qr)
    for m in range(n_res):
        angle = -2 * np.pi * N / (2 ** (m + 1))
        qc.p(angle, qr[m])
    qc.append(QFT_gate.inverse(), qr)
    
    qc.cx(qr[-1], anc[0]) 
    
    qc.append(QFT_gate, qr)
    for m in range(n_res):
        angle = 2 * np.pi * N / (2 ** (m + 1))
        qc.p(angle, qr[m])
    qc.append(QFT_gate.inverse(), qr)
    
    return qc.to_gate()

def cond_subtract_N_gate(n_res, N):
    qr = QuantumRegister(n_res, 'res')
    anc = QuantumRegister(1, 'anc')
    qc = QuantumCircuit(qr, anc, name="cond_sub_N")
    QFT_gate = QFT(n_res, do_swaps=False).to_gate()
    qc.append(QFT_gate, qr)
    for m in range(n_res):
        angle = -2 * np.pi * N / (2 ** (m + 1))
        qc.cp(angle, anc[0], qr[m])
    qc.append(QFT_gate.inverse(), qr)
    return qc.to_gate()


def QQMULT(n_a, n_b, n_res, N, k=2):#out of place
    reg_a = QuantumRegister(n_a, 'a')
    reg_b = QuantumRegister(n_b, 'b')
    reg_res = QuantumRegister(n_res, 'res')
    anc = QuantumRegister(1, 'anc')  
    qc = QuantumCircuit(reg_a, reg_b, reg_res, anc, name="QQMULT_modN")
    QFT_gate = QFT(n_res, approximation_degree=k, do_swaps=False).to_gate()
    qc.append(QFT_gate, reg_res)
    for i in range(n_a):
        for j in range(n_b):
            shift = i + j
            for m in range(shift, n_res):
                angle = 2 * np.pi / (2 ** (m - shift + 1))
                qc.mcp(angle, [reg_a[i], reg_b[j]], reg_res[m])
    qc.append(QFT_gate.inverse(), reg_res)
    qc.append(compare_geq(n_res, N), [*reg_res, anc[0]])
    qc.append(cond_subtract_N_gate(n_res, N), [*reg_res, anc[0]])
    qc.append(compare_geq(n_res, N).inverse(), [*reg_res, anc[0]])
    return qc.to_gate()


def encode_x(n, x):
    qc = QuantumCircuit(n)
    bits = format(x, f"0{n}b")[::-1]
    for i, b in enumerate(bits):
        if b == '1':
            qc.x(i)
    return qc.to_gate()

def INV(n, N, a_inv):
    a = QuantumRegister(n, "a")
    anc = QuantumRegister(n, "anc")
    qc = QuantumCircuit(a, anc)
    val = (-a_inv) % N
    qc.append(encode_x(n, val), anc)
    for i in range(n):
        qc.swap(a[i], anc[i])
    qc.append(encode_x(n, val).inverse(), anc)
    return qc.to_gate()


def MUL_ADD_MOD(n, S, N): 
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n, "b")
    t = QuantumRegister(n, "t")
    prod = QuantumRegister(n, "prod")
    work = QuantumRegister(S, "work")
    qc = QuantumCircuit(a, b, t, prod, work)
    qc.append(QQMULT(n, n, n, N), [*a, *b, *prod, *work])
    qc.append(QADD(n, N), [*prod, *t])
    qc.append(QQMULT(n, n, n, N).inverse(), [*a, *b, *prod, *work])
    return qc.to_gate()

def swap_registers(qc, reg1, reg2):
    for q1, q2 in zip(reg1, reg2):
        qc.swap(q1, q2)
        
def MUL_INV_MUL(n, S, N, a, a_inv): #in place multiplication
    x = QuantumRegister(n, "x")
    anc = QuantumRegister(S, "anc")
    g = QuantumRegister(n, "g")
    a_n = QuantumRegister(n, "a_n")
    qc = QuantumCircuit(x, anc, g, a_n)
    qc.append(encode_x(n, a),[*a_n])
    qc.append(MUL_ADD_MOD(n, S, N), [*x, *a_n, *g, *anc])
    qc.append(INV(n,N,a_inv), [*a_n, *anc])
    neg_a_inv = -a_inv % N 
    qc.append(encode_x(n,neg_a_inv), [*a_n]) 
    qc.append(MUL_ADD_MOD(n,S,N), [*g, *a_n, *x, *anc])
    qc.append(INV(n,N,a), [*a_n, *anc])
    neg_a_inv = - a % N 
    qc.append(encode_x(n, a),[*a_n])
    qc.append(MUL_ADD_MOD(n,S,N), [*x, *a_n, *g, *anc])
    qc.append(INV(n,N,a_inv), [*a_n])
    swap_registers(qc, x, g)
    return qc.to_gate

def MOD_PROD(n, S, a, b, ainv, binv, N):
    a_n = QuantumRegister(n,"a")
    a_inv = QuantumRegister(n, "a_inv")
    b_n = QuantumRegister(n,"b")
    b_inv = QuantumRegister(n, "b_inv")
    g = QuantumRegister(n, "g")
    anc = QuantumRegister(S, "anc")
    qc = QuantumCircuit(a,a_inv,b,b_inv,g,anc)
    qc.append(encode_x(n, ainv)[*a_inv])
    qc.append(encode_x(n, binv) [*b_inv])
    qc.append(MUL_ADD_MOD(n,S,N), [*a_n,*b_n,*g,*anc])
    qc.append(MUL_ADD_MOD(n,S,N).inverse(), [*a_inv,*g,*b_n,*anc])
    qc.append(MUL_ADD_MOD(n,S,N),[*a_n, *b_n, *g])
    qc.append(MUL_ADD_MOD(n,S,N), [*a_inv,*b_inv,*b_n])
    qc.append(MUL_ADD_MOD(n,S,N).inverse(), [*a_n,*b_n,*b_inv])
    qc.append(MUL_ADD_MOD(n,S,N), [*a_inv,*b_inv, *b_n])
    swap_registers(qc, b_n, g)
    swap_registers(qc, b_inv,g)
    return qc.to_gate
    
    
    
    
    
    
    