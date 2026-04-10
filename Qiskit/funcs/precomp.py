import numpy as np

def is_prime(num):
    if num < 2: return False
    for i in range(3, int(np.sqrt(num)) + 1, 2):
        if num % i == 0: return False
    return True

def get_bases(n_modulus, N_val):
    L = int(np.sqrt(n_modulus))
    d = L
    
    primes = []
    current = 2
    while len(primes) < d:
        if is_prime(current):
            primes.append(current)
        current += 1
    
    base_seeds = [(p**2) % N_val for p in primes]
    
    table = np.zeros((d, L), dtype=object)
    
    for j in range(d):
        current_val = base_seeds[j]
        for i in range(L):
            table[j][i] = current_val
            current_val = (current_val * current_val) % N_val
            
    return table