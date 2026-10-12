import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
import numpy as np
from lin_diff import gf2_rank64
import random

def apply_random_dag(X, seed=0):
    # 6 levels, 64 parallel gates per level.
    # Each gate takes 2 RANDOM inputs from previous level (not offset-based).
    # Gate types: 4 AND + 2 XOR (randomly placed).
    random.seed(seed)
    N = X.shape[0]
    b = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        b[i] = ((X >> np.uint64(i)) & np.uint64(1)).astype(np.uint8)
    prev = b
    # Random gate types: 4 AND, 2 XOR
    types = [0,0,0,0,1,1]
    random.shuffle(types)
    for j in range(6):
        t = types[j]
        # Random wiring: for each of 64 gates, pick 2 random inputs from prev
        curr = np.zeros((64, N), dtype=np.uint8)
        for i in range(64):
            a = random.randrange(64)
            bb = random.randrange(64)
            x, y = prev[a], prev[bb]
            curr[i] = (x & y) if t==0 else (x ^ y)
        prev = curr
    G = np.zeros(N, dtype=np.uint64)
    for i in range(64):
        G |= (prev[i].astype(np.uint64) << np.uint64(i))
    return X ^ G

for seed in [1, 2, 3]:
    N = 16*64
    X = np.arange(N, dtype=np.uint64)
    Y = apply_random_dag(X, seed=seed)
    D = sum(1 for b in range(16) if gf2_rank64(Y[b*64:(b+1)*64]) <= 61)
    print(f"Random wiring seed {seed}: D={D}/16")
