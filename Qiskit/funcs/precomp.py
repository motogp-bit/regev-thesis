import numpy as np

def is_prime(num):
    if num < 2: return False
    for i in range(3, int(np.sqrt(num)) + 1, 2):
        if num % i == 0: return False
    return True

def get_bases(N,d, primes, exp):
    
    base_seeds = [(p**exp) % N for p in primes]
    
    table = np.zeros((d, d), dtype=object)
    
    for j in range(d):
        current_val = base_seeds[j]
        for i in range(d):
            table[j][i] = current_val
            current_val = (current_val * current_val) % N
            
    return table