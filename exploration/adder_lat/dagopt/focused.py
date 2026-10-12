#!/usr/bin/env python3
"""
Low-bit focused DAG: nonlinearity on bits 0-17 (which vary in Fisher),
high bits mixed linearly for 64-input dependence.
"""

import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/dagopt")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")

import numpy as np
from lin_diff import gf2_rank64

def apply_focused(X, seed=0):
    """
    6-level DAG:
    L1-L3: 64 parallel gates on low 18 bits (offsets small, AND-heavy).
    L4-L6: Mix in high bits via XOR, expand fan-in.
    XIG at end.
    """
    import random
    random.seed(seed)
    N = X.shape[0]
    # Bit planes
    b = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        b[i] = ((X >> np.uint64(i)) & np.uint64(1)).astype(np.uint8)
    
    # L1: 64 AND gates, inputs from low 18 bits only
    # Gate i takes ( (i*2)%18, (i*2+1)%18 )
    l1 = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        a = (i * 2) % 18
        bb = (i * 2 + 1) % 18
        l1[i] = b[a] & b[bb]
    
    # L2: 64 XOR gates, combine L1
    # Gate i takes (i, i+1 mod 64) from L1
    l2 = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        l2[i] = l1[i] ^ l1[(i+1) % 64]
    
    # L3: 64 AND gates
    l3 = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        l3[i] = l2[i] & l2[(i+7) % 64]
    
    # L4: 64 XOR gates, mix in high bits (18-63)
    # Gate i takes l3[i] XOR b[(i % 46) + 18]
    l4 = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        hb = b[(i % 46) + 18]
        l4[i] = l3[i] ^ hb
    
    # L5: 64 XOR gates, expand
    l5 = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        l5[i] = l4[i] ^ l4[(i+16) % 64]
    
    # L6: 64 XOR gates
    l6 = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        l6[i] = l5[i] ^ l5[(i+32) % 64]
    
    # Pack and XIG
    G = np.zeros(N, dtype=np.uint64)
    for i in range(64):
        G |= (l6[i].astype(np.uint64) << np.uint64(i))
    return X ^ G

def test():
    N = 16 * 64
    X = np.arange(N, dtype=np.uint64)
    Y = apply_focused(X)
    D = sum(1 for b in range(16) if gf2_rank64(Y[b*64:(b+1)*64]) <= 61)
    print(f"D={D}/16")
    # Cost: L1 AND (1u), L2 XOR (1.8), L3 AND (1u), L4 XOR (1.8), L5 XOR (1.8), L6 XOR (1.8), XIG (1.8)
    # = 1 + 1.8 + 1 + 1.8 + 1.8 + 1.8 + 1.8 = 11.0u. OVER.
    print("Cost: 11.0u (OVER)")

if __name__ == "__main__":
    import time
    t0 = time.time()
    test()
    print(f"Time: {time.time()-t0:.1f}s")
