import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector
from funcs import *
from sympy.ntheory import sqrt_mod
import math
from sympy import Matrix
from sympy.polys.numberfields import lll

N = 446.393 #p = 509, q = 877, d = 5
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



	

regs = [QuantumRegister(n, f'dim_{i}') for i in range(d)]


reg_size = 2**d #2^n/d
amps_nd = gaussian(n, D / 2, R, d)


product = QuantumRegister(n, 'product')
qc = QuantumCircuit(*regs)
qc.initialize(amps_nd, qc.qubits)
qc.add_register(product)
state = Statevector.from_instruction(qc)
print(state)

qc.add_register(product)



e = []
product = qmme(qc, e, get_bases(N, d, primes, 2), N)
b = get_bases(N, d, primes, 1)
qc.measure(product)
state = Statevector.from_instruction(qc)
print(state)
#qc has collapsed to the values that equal u

qc.measure(cr)
samples.append(cr / D)

#END LOOP
samples = [[x + D/2 for x in row] for row in samples]
m = []
for i in range():
    temp = []
    for j in range():
        if i == j:
            if i > d:
                temp.append(1/delta)
            else:
                temp.append(1)
        elif (i and j <= d) or (i and j > d):
            temp.append(0)
        elif i <= d and j > d:
            temp.append(0)
        else:
            temp.append(w[i-d][j] / delta)
    m.append(temp)
M = Matrix(m)
exps = lll(M)
Exps = Matrix(exps)
GS_exps = Matrix.orthogonalize(Exps)
cands = []
for i in range(len(GS_exps)):
    if np.linalg.norm(GS_exps[i]) < np.sqrt(k) * 2^(k/2) * T:
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






	