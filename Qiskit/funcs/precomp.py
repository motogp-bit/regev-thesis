import numpy as np

def is_prime(num):
    if num < 2: return False
    for i in range(3, int(np.sqrt(num)) + 1, 2):
        if num % i == 0: return False
    return True

def get_bases(n_modulus, N_val):
    """
    Generates a 2D table [d][L] where d = L = sqrt(n).
    Table contains (prime_j^2)^(2^i) mod N.
    """
    L = int(np.sqrt(n_modulus))
    d = L
    
    # 1. Find the first d primes
    primes = []
    current = 2
    while len(primes) < d:
        if is_prime(current):
            primes.append(current)
        current += 1
    
    # 2. Square them to get the actual bases b_j
    base_seeds = [(p**2) % N_val for p in primes]
    
    # 3. Build the table for each bit-level i
    # table[j][i] = (base_j)^(2^i) mod N
    table = np.zeros((d, L), dtype=object)
    
    for j in range(d):
        current_val = base_seeds[j]
        for i in range(L):
            table[j][i] = current_val
            # Square for the next bit-level: b^(2^(i+1)) = (b^(2^i))^2
            current_val = (current_val * current_val) % N_val
            
    return table