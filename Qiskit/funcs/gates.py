from qiskit import QuantumCircuit, QuantumRegister
import numpy as np
from qiskit.circuit.library import FullAdderGate ,ModularAdderGate, IntegerComparatorGate,HRSCumulativeMultiplier

def CMMC(n, constant):
    ctrl = QuantumRegister(1, name='ctrl')
    reg = QuantumRegister(n, name='reg')
    qc = QuantumCircuit(ctrl, reg)
    bin_const = format(int(constant), f'0{n}b')[::-1]

    for j in range(n):
        target_bit = int(bin_const[j])
        initial_bit = 1 if j == 0 else 0
        
        if target_bit != initial_bit:
            qc.cx(ctrl[0], reg[j])

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

    for i in range(n - 1):
        if c_bits[i] == 1:
            qc.cx(x[i], anc[i+1])
            qc.ccx(anc[i], x[i], anc[i+1])
        else:
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
"""
#
#def IN_PLACE_MODULAR_ADDER(N): |a> |b> |0^n> -> |a> |ab mod N> |0^n>

def CLEAR(n, value):
    qc = QuantumCircuit(n)
    for i in range(n):
        if (value >> i) & 1:
            qc.x(i)
    return qc.to_gate()

def SWAP(n):
    qc = QuantumCircuit(2*n)
    for i in range(n):
        qc.swap(i, i+n)

    return qc.to_gate(label=f"SWAP({n})")

#def MOD_RED(N):  |c> |0^n> |0^gn> -> |c> |c mod N> |0^gn>
#def MULTIPLIER(): |a> |b> |0^2n> |0^S> -> |a> |b> |ab> |0^S> using some multiplication algorithm
#POTENTIAL IMPLEMENTATION for MOD_RED

"""
def MOD_RED(gn, n, N):  # |C> |0> |0^n> |0> |0^gn> -> |0^gn> |0 or 1> |C mod N> |0> |0^gn>
    c = QuantumRegister(gn, 'c')
    flag = QuantumRegister(1, 't')
    value = QuantumRegister(n)
    carry = QuantumRegister(1)      
    anc = QuantumRegister(gn)       
    qc = QuantumCircuit(c, flag, anc, value)
    qc.cx(flag)
    comparator = IntegerComparatorGate(num_state_qubits=gn, value=N, geq=False)
    adder = FullAdderGate(num_state_qubits=gn)
    qc.append(CMMC(gn, N), [*flag, *anc])
    qc.append(comparator, [*c, *flag])
    qc.append(adder.inverse(), [*flag,*carry, *c, *anc]).control(1)
    qc.append(CLEAR(gn, N), [*anc])
    qc.append(SWAP(n), [*c[:n], *value])
    return qc.to_gate()
"""


def MOD_MULT(n,N): #|a> |b> |0^n> |0^2n> -> |a> |b> |ab mod N> |0^2n>
    a = QuantumRegister(n)
    b = QuantumRegister(n)
    ab = QuantumRegister(2*n)
    abmodn = QuantumRegister(n)
    ancS = QuantumRegister(S)
    qc = QuantumCircuit(a, b, ab, abmodn, ancS)
    qc.append(MULTIPLIER, [*a, *b, *ab, *ancS])
    qc.append(MOD_RED(2*n, n, N), [*ab, *abmodn, *ancS])
    qc.append(MULTIPLIER.inverse(), [*a, *b, *ab, *ancS])
    return qc.to_gate()
    
def MUL_ADD_MOD(n, N): #|a> |b> |t> |0^n> -> |a> |b> |(t+ab) mod N> |0^n>
    a = QuantumRegister(n, 'a')
    b = QuantumRegister(n, 'b')
    t = QuantumRegister(n, 't')
    ab = QuantumRegister(2*n, "ab")
    anc_ab = QuantumRegister(S, "anc_ab")
    abmodn = QuantumRegister(n)
    qc = QuantumCircuit(a, b, t, ab)
    qc.append(MOD_MULT(n,N), [*a, *b, *ab, *abmodn, *anc_ab])
    qc.append(IN_PLACE_MODULAR_ADDER(N), [*t, *abmodn])
    qc.append(MOD_MULT(n, N).inverse(), [*a, *b, *abmodn])
    return qc.to_gate()
        
def QCMULT_IP(n, N, a, a_inv): #|x> |0^n> |g> |0> -> |ax mod N> |0^n> |(g * -a^-1) mod N> |0^S> for some a 
    x = QuantumRegister(x, "x")
    a_n = QuantumRegister(n, "a_n")
    g = QuantumRegister(n, "g")
    anc1 = QuantumRegister(2*n)
    anc2 = QuantumRegister(2*n)
    anc3 = QuantumRegister(n)
    ctrl = QuantumRegister(1, "anc")
    qc = QuantumCircuit(x, a_n, g, ctrl, anc1, anc2, anc3)
    qc.x(ctrl)
    qc.append(CMMC(n, a),[*ctrl, *a_n])
    qc.append(MUL_ADD_MOD(n, N), [*x, *a_n, *g, *anc1, *anc2, *anc3])
    qc.append(CMMC(n, N - a_inv), [*ctrl, *a_n])
    qc.append(MUL_ADD_MOD(n, N), [*g, *a_n, *x, *anc1, *anc2, *anc3])
    qc.append(CMMC(n, a), [*ctrl, *a_n])
    qc.append(MUL_ADD_MOD(n, N), [*x, *a_n, *g, *anc1, *anc2, *anc3])
    qc.append(CMMC(n, 0), [*ctrl, *a_n])
    qc.append(SWAP(), [*x, *g])
    return qc.to_gate()

def MOD_PROD(n, N): #|a> |a^-1> |b> |b^-1> |g> -> |a> |a^-1> |ab> |ab^-1> |g>
    a_n = QuantumRegister(n,"a")
    a_inv = QuantumRegister(n, "a_inv")
    b_n = QuantumRegister(n,"b")
    b_inv = QuantumRegister(n, "b_inv")
    g = QuantumRegister(n, "g")
    anc1 = QuantumRegister(2*n)
    anc2 = QuantumRegister(n)
    anc3 = QuantumRegister(S)
    qc = QuantumCircuit(a_n,a_inv, b_n, b_inv, g, anc1, anc2, anc3)
    qc.append(MUL_ADD_MOD(n, N), [*a_n,*b_n,*g, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N).inverse(), [*a_inv,*g,*b_n, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N),[*a_n, *b_n, *g, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N), [*a_inv,*b_inv,*b_n, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N).inverse(), [*a_n,*b_n,*b_inv, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N), [*a_inv,*b_inv, *b_n, *anc1, *anc2, *anc3])
    qc.append(SWAP(n), [*b_n, *g])
    qc.append(SWAP(n), [*b_inv, *g])
    return qc.to_gate

def MSQUARE(n, N): #|a> |a^-1> |0^n> |0^n> |g> |0^n> -> |a> |a^-1> |a^2> |(a^2)^-1> |g> |0^n>
    a = QuantumRegister(n)
    a_inv = QuantumRegister(n)
    aa = QuantumRegister(n)
    aa_inv = QuantumRegister(n)
    anc1 = QuantumRegister(2*n)
    anc2 = QuantumRegister(2*n)
    anc3 = QuantumRegister(n)
    g = QuantumRegister(n)
    qc = QuantumCircuit(a, a_inv, aa, aa_inv, g, anc1, anc2, anc3)
    for i in range(n):
        qc.cx(a[i], aa[i])
        qc.cx(a_inv[i], aa_inv[i])
    qc.append(MOD_PROD(n, N), [*a, *a_inv, *anc1, *anc2, *g, *anc1, *anc2, *anc3])
    return qc.to_gate()
"""
def CLEAR_LAYER(n, N, a, ainv): #|a> |a_inv> |0^n> |g> |0 or 1> -> |0^n> |0^n> |0^n> |g> |0 or 1>
    a_n = QuantumRegister(n)
    a_inv = QuantumRegister(n)
    anc = QuantumRegister(n)
    anc1 = QuantumRegister(2*n)
    anc2 = QuantumRegister(2*n)
    anc3 = QuantumRegister(n)
    g = QuantumRegister(n)
    ctrl = QuantumRegister(1)
    qc = QuantumCircuit(a_n,a_inv,anc, anc1, anc2, anc3, ctrl)
    qc.append(QCMULT_IP(n, N, a, ainv), [*ctrl, *a_n, *anc, *g, *anc1, *anc2, *anc3]).control(1)
    qc.append(QCMULT_IP(n, N, ainv, a), [*ctrl, *a_inv, *anc, *g, *anc1, *anc2, *anc3]).control(1)
    return qc.to_gate()
"""
    
    
    
    
    
    
    
    