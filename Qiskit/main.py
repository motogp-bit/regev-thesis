import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector
from funcs import *
from sympy.ntheory import sqrt_mod
import math
from sympy import Matrix
from sympy.polys.numberfields import lll

backend = Aer.get_backend("qasm_simulator")
N = 446393 #p = 509, q = 877, d = 5
Ns = 77 #11*7, d = 3
n = int(np.ceil(np.log2(Ns)))
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

R = np.sqrt(2* d) + 1 #R > sqrt(2d)

temp = 0
r = 2*np.sqrt(d)*R
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

    product = qmme(qc, regs, get_bases(N, d, primes, 2), N)

    qc.measure(product, cr_p)

    for reg in regs:
        qc.append(QFT(n), reg)

    for j in range(d):
        qc.measure(regs[j], cr_e[j*n:(j+1)*n])

    result = backend.run(qc, shots=1).result()
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
M = Matrix(m)
exps = lll(M)
Exps = Matrix(exps)
cands = []
for i in range(len(Exps)):
    if np.linalg.norm(Exps[i]) < np.sqrt(k) * 2**(k/2) * T:
        cands.append(exps[i])


for cand in cands:
    f_exps = []
    factor = 1
    for i in range(d):
        f_exps.append((cand[i] - (cand[i] % 2)) / 2)
        factor = (factor * (b[i] if cand[i] % 2 == 1 else 1)) % N
    prod = 1
    f_sqrt = sqrt_mod(factor, N)
    X = 1
    for i in range(d):
        X *= pow(b[i],f_exps[i],N) #classical modular exponentiation
    X= (X * f_sqrt) % N
    p = math.gcd(X-1, N)
    if p > 1 and p < N:
        print(p)
        break






	