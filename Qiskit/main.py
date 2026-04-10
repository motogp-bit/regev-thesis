import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector
from funcs import *

N = 446.393 #p = 509, q = 877, d = 5
Ns = 77 #11*7, d = 3
d = np.log2(Ns)
ns = 7

#classical preprocessing
primes = [2, 3, 5]
#R = ?
center = 11

def modexp(d, primes, exp, N):
    #exp = [e1,e2 ... ed], d = 3
	rt = 1
	for i in range(len(e1)):
		factor = 1
		for base in range(d):
			if exp[base][n - i - 1] == 1:
				factor = (factor * primes[base]) % N
		rt = (rt * factor) % N
		rt = (rt * rt) % N
	return rt			
		
	

def gaussian_signed(n, sigma):
    N = 2**n
    amps = np.zeros(N)

    shift = 10  # maps e -> index

    for e in range(-10, 10):  
        idx = e + shift
        amps[idx] = np.exp(-np.pi * (e**2) / (sigma**2))

    return amps / np.linalg.norm(amps)

for loop in range(d):
amps_1d = gaussian_signed(ns, R)
amps_3d = np.kron(np.kron(amps_1d, amps_1d), amps_1d)

qc = QuantumCircuit(3*n)
qc.initialize(amps_3d, qc.qubits)
state = Statevector.from_instruction(qc)
print(state)

######################

n_out = int(np.ceil(np.log2(Ns)))

# --- Registers ---
e1 = QuantumRegister(n, 'e1')
e2 = QuantumRegister(n, 'e2')
e3 = QuantumRegister(n, 'e3')
product = QuantumRegister(n_out, 'product')  
# output register

qc = QuantumCircuit(e1, e2, e3, product)
qc.initialize(amps_3d, e1[:] + e2[:] + e3[:])

qc.x(product[0])  

product = qmme()
product.measure(pr)
state = Statevector.from_instruction(qc)
print(state)
#qc has collapsed to the values that equal u

###################################

qc.measure(cr)
samples.append(cr / D)

END LOOP
# From now on we are doing purely classical postprocessing 
Binv = transpose(samples)
B = Gauss(Binv)
exps = LLL(B)
for exp in exps:
	rt += exp
total = 1
PARITY REDUCTION
p = gcd(X-1,N)
q = N // p 





	