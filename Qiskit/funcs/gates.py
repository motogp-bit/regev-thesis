from qiskit import QuantumCircuit, QuantumRegister
import numpy as np
from qiskit.circuit.library import FullAdderGate ,ModularAdderGate, IntegerComparatorGate,HRSCumulativeMultiplier

def CMMC(n, constant, bit):
    qc = QuantumCircuit(n+1)
    ctrl = qc.qubits[0]
    reg = qc.qubits[1:]
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

def MUL_ADD_MOD(n, N, S): #|a> |b> |t> |0^n> -> |a> |b> |(t+ab) mod N> |0^n>
    qc = QuantumCircuit(6*n + S)
    a = qc.qubits[:n]
    b = qc.qubits[n:2*n]
    t = qc.qubits[2*n:3*n]
    ab = qc.qubits[3*n:5*n]
    abmodn = qc.qubits[5*n:6*n]
    anc_ab = qc.qubits[6*n:6*n + S]
    qc = QuantumCircuit(a, b, t, ab)
    qc.append(MOD_MULT(n,N), [*a, *b, *ab, *abmodn, *anc_ab])
    qc.append(IN_PLACE_MODULAR_ADDER(N), [*t, *abmodn])
    qc.append(MOD_MULT(n, N).inverse(), [*a, *b, *abmodn])
    return qc.to_gate()

def MOD_PROD(n, N, S): #|a> |a^-1> |b> |b^-1> |g> -> |a> |a^-1> |ab> |ab^-1> |g>
    qc = QuantumCircuit(8*n + S)
    a_n = qc.qubits[:n]
    a_inv = qc.qubits[n:2*n]
    b_n = qc.qubits[2*n:3*n]
    b_inv = qc.qubits[3*n:4*n]
    g = qc.qubits[4*n:5*n]
    anc1 = qc.qubits[5*n:7*n]
    anc2 = qc.qubits[7*n:8*n]
    anc3 = qc.qubits[8*n:8*n + S]
    qc = QuantumCircuit(a_n,a_inv, b_n, b_inv, g, anc1, anc2, anc3)
    qc.append(MUL_ADD_MOD(n, N, S), [*a_n,*b_n,*g, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N, S).inverse(), [*a_inv,*g,*b_n, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N, S),[*a_n, *b_n, *g, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N, S), [*a_inv,*b_inv,*b_n, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N, S).inverse(), [*a_n,*b_n,*b_inv, *anc1, *anc2, *anc3])
    qc.append(MUL_ADD_MOD(n, N, S), [*a_inv,*b_inv, *b_n, *anc1, *anc2, *anc3])
    qc.append(SWAP(n), [*b_n, *g])
    qc.append(SWAP(n), [*b_inv, *g])
    return qc.to_gate

#def MSQUARE(n, N): #|a> |0^n> -> |a> |a^2 mod N>

    
    
    
    
    
    
    
    