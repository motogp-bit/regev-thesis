import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector
from funcs import *

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



	

regs = []
for i in range(d):
     reg = QuantumRegister(n, name=f'reg{i}')
     regs.append(reg)


reg_size = 2**d #2^n/d
amps_1d = gaussian_signed(reg_size, R, D/2)
amps_nd = amps_1d
for _ in range(d - 1):
    amps_nd = np.kron(amps_nd, amps_1d)

product = QuantumRegister(n, 'product')
qc = QuantumCircuit(*regs)
qc.initialize(amps_nd, qc.qubits)
qc.add_register(product)
state = Statevector.from_instruction(qc)
print(state)

qc.add_register(product)



e = []
product = qmme(qc, e, get_bases(N, d, primes), N)
qc.measure(product)
state = Statevector.from_instruction(qc)
print(state)
#qc has collapsed to the values that equal u

qc.measure(cr)
samples.append(cr / D)

#END LOOP
samples = [[x + D/2 for x in row] for row in samples]
M = []
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
    M.append(temp)
exps = LLL(M)
GS_exps = Gram-Schmidt(exps)
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
    #COMPUTE SQRT MODULO N OF FACTOR
    for i in range(d):
        X = MODEXP(b[i],f_exps[i]])
    p = gcd(X-1, N)
    if p > 1 and p < N:
        return p






	