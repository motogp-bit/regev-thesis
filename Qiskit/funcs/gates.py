from qiskit import QuantumCircuit, QuantumRegister
import numpy as np
from qiskit.circuit.library import FullAdderGate ,ModularAdderGate, IntegerComparatorGate,HRSCumulativeMultiplier

def CMMC(n, constant, bit):
    ctrl = QuantumRegister(1, name='ctrl')
    reg = QuantumRegister(n, name='reg')
    qc = QuantumCircuit(ctrl, reg)
    bitmask = format(int(1 ^ constant), f'0{n}b')[::-1]
    for j in range(n):
        if bitmask[j] == 1:
            qc.cx(ctrl[0], reg[bit])
    return qc.to_gate()

def SWAP(n):
    qc = QuantumCircuit(2*n)
    for i in range(n):
        qc.swap(i, i+n)

    return qc.to_gate(label=f"SWAP({n})")

#def IN_PLACE_MODULAR_ADDER(N): |a> |b> |0^n> -> |a> |ab mod N> |0^n>
#def MOD_MULT(n,N): #|a> |b> |0^n> -> |a> |b> |ab mod N>

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

#def MSQUARE(n, N): #|a> |0^n> -> |a> |a^2 mod N>

    
    
    
    
    
    
    
    