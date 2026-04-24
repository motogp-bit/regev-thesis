from qiskit import QuantumCircuit, QuantumRegister
import numpy as np
from qiskit.circuit.library import DraperQFTAdder, QFT

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

def doubly_controlled_mod_adder(n, N):
    qr = QuantumRegister(n, 't')
    c1 = QuantumRegister(1, 'c1')
    c2 = QuantumRegister(1, 'c2')
    anc = QuantumRegister(1, 'anc')
    
    qc = QuantumCircuit(c1, c2, qr, anc, name="CCModAdd")

    qft_gate = QFT(n, do_swaps=False).to_gate()
    qc.append(qft_gate, qr)

    b_val = 1 
    for j in range(n):
        angle = 2 * np.pi * b_val / (2**(j + 1))
        qc.mcp(angle, [c1[0], c2[0]], qr[j])
    qc.append(qft_gate.inverse(), qr)

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


def QQMULT(n_a, n_b, n_res, N, k=2):# |a> |b> |0^n> |1> -> |a> |b> |ab mod N> |0 or 1>
    reg_a = QuantumRegister(n_a, 'a')
    reg_b = QuantumRegister(n_b, 'b')
    reg_res = QuantumRegister(n_res, 'res')
    anc = QuantumRegister(1, 'anc')  
    qc = QuantumCircuit(reg_a, reg_b, reg_res, anc, name="QQMULT")
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


def ENCODE(n, x): #assign a value to an empty register
    qc = QuantumCircuit(n)
    bits = format(x, f"0{n}b")[::-1]
    for i, b in enumerate(bits):
        if b == '1':
            qc.x(i)
    return qc.to_gate()

def CL_ASSIGN(n, a): #clean a register 
    a = QuantumRegister(n, "a")
    anc = QuantumRegister(n, "anc")
    qc = QuantumCircuit(a, anc)
    qc.append(ENCODE(n, a), anc)
    for i in range(n):
        qc.swap(a[i], anc[i])
    qc.append(ENCODE(n, a).inverse(), anc)
    return qc.to_gate()
"""
def doubly_controlled_mod_adder(n, N):
    qr = QuantumRegister(n, 't')
    c1 = QuantumRegister(1, 'c1')
    c2 = QuantumRegister(1, 'c2')
    anc = QuantumRegister(1, 'anc')
    
    qc = QuantumCircuit(c1, c2, qr, anc, name="CCModAdd")

    qft_gate = QFT(n, do_swaps=False).to_gate()
    qc.append(qft_gate, qr)

    b_val = 1 
    for j in range(n):
        angle = 2 * np.pi * b_val / (2**(j + 1))
        qc.mcp(angle, [c1[0], c2[0]], qr[j])
    qc.append(qft_gate.inverse(), qr)

    return qc.to_gate()

def MUL_ADD_MOD(n, N):
    a = QuantumRegister(n, 'a')
    b = QuantumRegister(n, 'b')
    t = QuantumRegister(n, 't') # The target register
    anc = QuantumRegister(1, 'anc')
    qc = QuantumCircuit(a, b, t, anc)
    for i in range(n):
        qc.append(doubly_controlled_mod_adder(n, N, weight=2**i), 
                  [a[i], *b, *t, anc[0]])
    return qc.to_gate()

def MUL_ADD_MOD(n, S, N): #|a> |b> |t> |0^S> -> |a> |b> |(t+ab) mod N> |0^S>
    a = QuantumRegister(n, "a")
    b = QuantumRegister(n, "b")
    t = QuantumRegister(n, "t")
    work = QuantumRegister(S, "work")
    prod = QuantumRegister(n, "prod")
    qc = QuantumCircuit(a, b, t, prod, work)
    qc.append(QQMULT(n, n, n, N), [*a, *b, *prod, *work])
    qc.append(QADD(n, N), [*prod, *t])
    qc.append(QQMULT(n, n, n, N).inverse(), [*a, *b, *prod, *work])
    return qc.to_gate()
"""


def MUL_ADD_MOD(n_a, n_b, n_t, N): #|a> |b> |t> |0^S> -> |a> |b> |(t+ab) mod N> |0^S>
    a = QuantumRegister(n_a, 'a')
    b = QuantumRegister(n_b, 'b')
    t = QuantumRegister(n_t, 't')
    anc = QuantumRegister(1, 'anc')
    qc = QuantumCircuit(a, b, t, anc, name="ModMAC")

    qft_gate = QFT(n_t, do_swaps=False).to_gate()
    iqft_gate = qft_gate.inverse()

    qc.append(qft_gate, t)

    for i in range(n_a):
        for j in range(n_b):
            weight = 2**(i + j)
            for m in range(n_t):
                angle = 2 * np.pi * weight / (2**(m + 1))
                qc.mcp(angle, [a[i], b[j]], t[m])
            
            for m in range(n_t):
                angle = -2 * np.pi * N / (2**(m + 1))
                qc.p(angle, t[m])
    
            qc.append(iqft_gate, t)

            qc.cx(t[n_t-1], anc[0]) 
            qc.append(qft_gate, t)
    
            for m in range(n_t):
                angle = 2 * np.pi * N / (2**(m + 1))
                qc.cp(angle, anc[0], t[m])
            qc.append(iqft_gate, t)
            qc.cx(t[n_t-1], anc[0]) 
            qc.append(qft_gate, t)

    qc.append(iqft_gate, t)
    return qc

def SWAP():
    reg1 = QuantumRegister(reg1, "reg1")
    reg2 = QuantumRegister(reg2, "reg2")
    qc = QuantumCircuit(reg1, reg2)
    for q1, q2 in zip(reg1, reg2):
        qc.swap(q1, q2)
    return qc.to_gate()
        
def QQMULT_IP(n, S, N, a, a_inv): #|x> |0^n> |g> |0^S> -> |ax mod N> |0^n> |(g * -a^-1) mod N> |0^S> for some a 
    x = QuantumRegister(x, "x")
    a_n = QuantumRegister(n, "a_n")
    g = QuantumRegister(n, "g")
    anc = QuantumRegister(S, "anc")
    anc1 = QuantumRegister(1, "anc")
    qc = QuantumCircuit(x, a_n, g, anc)
    qc.append(ENCODE(n, a),[*a_n])
    qc.append(MUL_ADD_MOD(n, S, N), [*x, *a_n, *g, *anc1])
    qc.append(CL_ASSIGN(n,N, (- a_inv) % N), [*a_n, *anc])
    neg_a_inv = -a_inv % N 
    qc.append(ENCODE(n,neg_a_inv), [*a_n]) 
    qc.append(MUL_ADD_MOD(n,S,N), [*g, *a_n, *x, *anc1])
    qc.append(CL_ASSIGN(n,N, (-a) % N), [*a_n, *anc])
    neg_a_inv = - a % N 
    qc.append(ENCODE(n, a),[*a_n])
    qc.append(MUL_ADD_MOD(n,S,N), [*x, *a_n, *g, *anc1])
    qc.append(CL_ASSIGN(n,N,a_inv), [*a_n, *anc])
    qc.append(SWAP(), [*x, *g])
    return qc.to_gate

def MOD_PROD(n, S, a, b, ainv, binv, N): #|a> |a^-1> |b> |b^-1> |g> |0^S> -> |a> |a^-1> |ab> |ab^-1> |g> |0^S>
    a_n = QuantumRegister(n,"a")
    a_inv = QuantumRegister(n, "a_inv")
    b_n = QuantumRegister(n,"b")
    b_inv = QuantumRegister(n, "b_inv")
    g = QuantumRegister(n, "g")
    anc = QuantumRegister(1, "anc")
    qc = QuantumCircuit(a,a_inv,b,b_inv,g,anc)
    qc.append(ENCODE(n, ainv)[*a_inv])
    qc.append(ENCODE(n, binv) [*b_inv])
    qc.append(MUL_ADD_MOD(n,S,N), [*a_n,*b_n,*g,*anc])
    qc.append(MUL_ADD_MOD(n,S,N).inverse(), [*a_inv,*g,*b_n,*anc])
    qc.append(MUL_ADD_MOD(n,S,N),[*a_n, *b_n, *g])
    qc.append(MUL_ADD_MOD(n,S,N), [*a_inv,*b_inv,*b_n])
    qc.append(MUL_ADD_MOD(n,S,N).inverse(), [*a_n,*b_n,*b_inv])
    qc.append(MUL_ADD_MOD(n,S,N), [*a_inv,*b_inv, *b_n])
    qc.append(SWAP(),[b_n, g])
    qc.append(SWAP(), [b_inv, g])
    return qc.to_gate
    
    
    
    
    
    
    