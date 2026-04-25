from qiskit import QuantumCircuit, QuantumRegister
import numpy as np
from qiskit.circuit.library import CCXGate, MCXVChain,ModularAdderGate, IntegerComparatorGate

#S should be n - 2
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


"""def compare_geq(n_res, N):
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


def QQMULT(n_a, n_b, n_res, N, k=2):# |a> |b> |0^n> |1> -> |a> |b> |ab> |0 or 1>
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
"""

def CADD_Q(n):
    a = QuantumRegister(n, 'a')
    b = QuantumRegister(n, 'b')
    ctrl = QuantumRegister(1, 'ctrl')
    anc = QuantumRegister(n, 'anc')

    qc = QuantumCircuit(ctrl, a, b, anc)
    for i in range(n):
        qc.mct([ctrl[0], a[i], b[i]], anc[i])
        
        if i < n - 1:
            qc.mct([ctrl[0], anc[i], a[i+1]], anc[i+1])
            qc.mct([ctrl[0], anc[i], b[i+1]], anc[i+1])
    for i in range(n-1, 0, -1):
        qc.ccx(ctrl[0], b[i], a[i])
        qc.ccx(ctrl[0], anc[i-1], a[i])

    qc.ccx(ctrl[0], b[0], a[0])
    for i in range(n-2, -1, -1):
        qc.mct([ctrl[0], anc[i], b[i+1]], anc[i+1])
        qc.mct([ctrl[0], anc[i], a[i+1]], anc[i+1])
        qc.mct([ctrl[0], a[i], b[i]], anc[i])
        
    return qc.to_gate()

def CADD_C(n, c):
    x = QuantumRegister(n, 'x')
    anc = QuantumRegister(n, 'anc') # anc[0] is clean, anc[1:] are dirty
    qc = QuantumCircuit(x, anc)

    c_bits = [(c >> i) & 1 for i in range(n)]

    # 1. Forward Carry Chain (Compute carries into anc)
    # This stores the carry-out of bit i into anc[i+1]
    for i in range(n - 1):
        if c_bits[i] == 1:
            # Carry if (x[i] == 1) OR (anc[i] == 1 AND x[i] == 1)
            qc.cx(x[i], anc[i+1])
            qc.ccx(anc[i], x[i], anc[i+1])
        else:
            # Carry if (anc[i] == 1 AND x[i] == 1)
            qc.ccx(anc[i], x[i], anc[i+1])

    for i in range(n - 1, 0, -1):
        qc.cx(anc[i], x[i])
        if c_bits[i] == 1:
            qc.x(x[i])
            
    if c_bits[0] == 1:
        qc.x(x[0])
    for i in range(n - 2, -1, -1):
        if c_bits[i] == 1:
            qc.ccx(anc[i], x[i], anc[i+1])
            qc.cx(x[i], anc[i+1])
        else:
            qc.ccx(anc[i], x[i], anc[i+1])

    return qc.to_gate()


def QDOUBLE(n, N):
    x = QuantumRegister(n, 'x')
    anc = QuantumRegister(2, 'anc') 
    dirty_anc = QuantumRegister(n-1, "dirty_anc")
    qc = QuantumCircuit(x, anc)
    qc.swap(x[n-1,])
    for i in range(n-2,-1,-1):
        qc.swap(x[i], x[i-1])
    qc.swap(x[0], anc[0]) 
    qc.append(CADD_C(n, N).inverse(), [*x, anc[0] + dirty_anc]) 
    qc.append(IntegerComparatorGate(n, N), [*x, anc[1]])
    qc.append(CADD_C(n, N), [*x, anc[0] + dirty_anc]) 
    qc.cx(anc[0], anc[1])
    qc.append(CADD_C(n, N), [*x, anc[1] + dirty_anc]) 
    qc.x(x[n-1])
    qc.cx(x[n-1], anc[0])
    qc.x(x[n-1])


    return qc.to_gate()
def QQMULT()

def MOD_RED(n, N):
    c = QuantumRegister(2*n, 'c')
    red = QuantumRegister(n, "cmodN")
    anc = QuantumRegister(n, 'anc')
    qc = QuantumCircuit(c, red, anc)
    return qc.to_gate()

def QQMULT_MOD(n, N, S): #|a> |b> |0^2n> |0^n> |0> -> |a> |b> |0^2n> |ab mod N> |0 or 1>
    a = QuantumRegister(n)
    b = QuantumRegister(n)
    prod = QuantumRegister(2*n)
    prod_red = QuantumRegister(n)
    anc = QuantumRegister(n + S)
    anc_1 = QuantumRegister(1) #assuming this is 0
    qc = QuantumCircuit(a, b, prod, anc)
    qc.append(QQMULT(n,n,2*n)[*a,*b, *prod, *anc])
    qc.append(MOD_RED(n, N), [*prod, *prod_red])
    qc.x(anc_1)
    qc.append(CADD_Q(2*n, n).inverse(), [*prod, *prod_red, *anc_1, *anc[:n]])
    qc.x(anc_1)
    qc.x(prod)
    mcx_gate = MCXVChain(num_ctrl_qubits=2*n, dirty_ancillas=False)
    qc.append(mcx_gate, [*prod, *anc_1, *anc])
    qc.x(anc_1)
    qc.x(prod)
    qc.append(CADD_C(2*n, N).inverse()[*prod, *anc_1])
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

def MUL_ADD_MOD(n, N, S): #|a> |b> |t> |0^S> -> |a> |b> |(t+ab) mod N> |0^S>
    a = QuantumRegister(n, 'a')
    b = QuantumRegister(n, 'b')
    t = QuantumRegister(n, 't')
    anc = QuantumRegister(n, "anc")
    anc1 = QuantumRegister(1, "anc1")
    anc2 = QuantumRegister(2, "anc2")
    qc = QuantumCircuit(a, b, t, anc, anc1, anc2)
    c_adder = ModularAdderGate(num_state_qubits=n).control(1)
    for i in range(n):
        qc.append(c_adder, a[i] + b[:] + t[:])
        qc.append(QDOUBLE(n, N), [*b])
    for _ in range(n):
        qc.append(QDOUBLE(n,N), [*b])
    return qc.to_gate()

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

def MSQUARE(n, S, N, x, x_inv):
    a = QuantumRegister(n, name = "a")
    clean_anc = QuantumRegister(n, name = "anc")
    dirty_anc = QuantumRegister(n, name = "g")
    S_anc = QuantumRegister(n, name = "S")
    sing_anc = QuantumRegister(1, name = "sanc")
    qc = QuantumCircuit(a, clean_anc, dirty_anc, S_anc, sing_anc)
    qc.append(QQMULT_IP(n, S, N, x, x_inv), [*a, *clean_anc, *dirty_anc, *S_anc, *sing_anc])
    return qc.to_gate()

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
    
    
    
    
    
    
    