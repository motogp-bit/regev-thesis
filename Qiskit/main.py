import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector
from funcs import *
import math
from sympy import Matrix
from sympy.polys.matrices import DomainMatrix
from qiskit_aer import AerSimulator
from qiskit import transpile

backend = AerSimulator()
Ns = 446393 #p = 509, q = 877, d = 5
N = 77 #11*7, d = 3
n = int(np.ceil(np.log2(N)))
d = int(np.sqrt(n))
delta = 1/2
k = 4
T = 1
primes = []
current = 2
while len(primes) < d:
    if is_prime(current):
        primes.append(current)
    current += 1
QFT_gate = QFT(n).to_gate()
R = np.sqrt(2* d) + 1 #R > sqrt(2d)

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
samples = []
amps_nd = gaussian(n, D / 2, R, d)
for _ in range(d + k):

    regs = [QuantumRegister(n, f'dim_{i}') for i in range(d)]
    product = QuantumRegister(n, 'product')

    cr_e = ClassicalRegister(n * d, 'cr_e')
    cr_p = ClassicalRegister(n, 'cr_p')

    qc = QuantumCircuit(*regs, product, cr_e, cr_p)
    qc.initialize(amps_nd, qc.qubits[:n*d])

    qc, product = QMME(qc, regs, get_bases(N, d, primes, 2), N)

    qc.measure(product, cr_p)

    for reg in regs:
        qc.append(QFT_gate, reg)

    for j in range(d):
        qc.measure(regs[j], cr_e[j*n:(j+1)*n])

    tqc = transpile(qc,backend) #doing this to avoid multiple decompose()
    result = backend.run(tqc, shots=1).result()
    counts = result.get_counts()
    bitstring = list(counts.keys())[0]
    e_bits = bitstring[n:]  
    e_vals = [int(e_bits[j*n:(j+1)*n], 2) for j in range(d)]


    samples.append(e_vals)

b = get_bases(N, d, primes, 1)
samples = [[x / D for x in row] for row in samples]
m = []
for i in range(2 * d + k):
    temp = []
    for j in range(d + k):
        if i == j:
            if i > d:
                temp.append(1/delta)
            else:
                temp.append(1)
        elif (i <= d and j <= d) or (i > d and j > d):
            temp.append(0)
        elif i <= d and j > d:
            temp.append(0)
        else:
            temp.append(samples[i-d][j] / delta)
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
        X *= pow(b[i],cand[i],N) #classical modular exponentiation
    p = math.gcd(X-1, N)
    if p > 1 and p < N:
        print(p)
        break






