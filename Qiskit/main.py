import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.libraries import QFT
from funcs import *
import math
from sympy import Matrix
from sympy.polys.matrices import DomainMatrix
from qiskit_aer import AerSimulator
from qiskit import transpile

backend = AerSimulator()
#Ns = 446393 #p = 509, q = 877, d = 5
N = 77 #11*7, d = 3
n = int(np.ceil(np.log2(N)))
d = int(np.sqrt(n))
k = 4
T = 1
primes = []
current = 2
S = n + 3

while len(primes) < d:
    if is_prime(current):
        primes.append(current)
    current += 1
R = int(np.exp(np.sqrt(n)))
delta = np.sqrt(d) / (np.sqrt(2) * R)

temp = 0
r = int(2*np.sqrt(d)*R)
for i in range(r + (r%2) , 2*r, 2):
    temp = i
    while (temp % 2 == 0):
        temp/=2
    if temp == 1: 
        temp = i
        break

D = temp
reg_size = 2**d #2^n/d
num_qubits = int(np.log2(D))
QFT_gate = QFT(num_qubits).to_gate()

samples = []
amps_nd = gaussian(num_qubits, D / 2, R, d)
for _ in range(d + k):

    e_regs = [QuantumRegister(num_qubits, f'dim_{i}') for i in range(d)]
    product = QuantumRegister(n, 'product')

    cr_e = ClassicalRegister(num_qubits * d, 'cr_e')
    cr_p = ClassicalRegister(n, 'cr_p')

    qc = QuantumCircuit(*e_regs, product, cr_e, cr_p)
    qc.initialize(amps_nd, qc.qubits[:num_qubits*d])

    qc, acc= QMME(qc, get_bases(N, d, primes, 2), N, S)

    qc.measure(acc, cr_p)
    for j in range(d):
        qc.append(QFT_gate, e_regs[j])
        qc.measure(e_regs[j], cr_e[j*num_qubits:(j+1)*num_qubits])

    tqc = transpile(qc,backend) #doing this to avoid multiple decompose()
    result = backend.run(tqc, shots=1).result()
    counts = result.get_counts()
    bitstring = list(counts.keys())
    p_bits, e_bits = bitstring.split(" ")
    e_vals = [int(e_bits[j*num_qubits:(j+1)*num_qubits], 2) for j in range(d)]


    samples.append(e_vals)

b = get_bases(N, d, primes, 1)
samples = [[x / D for x in row] for row in samples]
m = []
for i in range(2*d + k):
    temp = []
    for j in range(2*d + k):
        if i < d: 
            temp.append(1 if i == j else 0)
        else: 
            if j < d:
                temp.append(samples[i-d][j] / delta)
            else:
                temp.append((1/delta) if i == j else 0)
    m.append(temp)
M = m.to_Matrix()
exps = M.to_DM().lll().to_Matrix()
cands = []
for i in range(len(exps)):
    if np.linalg.norm(exps[i]) < np.sqrt(k) * 2**(k/2) * T:
        cands.append(exps[i])


for cand in cands:
    X = 1
    for i in range(d):
        X = (X * pow(b[i],int(cand[i]),N)) % N 
    p = math.gcd(X-1, N)
    if p > 1 and p < N:
        print(p)
        break






