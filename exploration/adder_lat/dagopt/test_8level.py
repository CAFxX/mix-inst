import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/dagopt")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
import numpy as np
from lin_diff import gf2_rank64

def apply_8level(X):
    # 8 levels: 4 AND + 4 XOR, offsets powers of 2
    # Cost: 4*1.0 + 4*1.8 + 1.8 (XIG) = 4 + 7.2 + 1.8 = 13.0u (OVER, but test if Fisher passes)
    N = X.shape[0]
    b = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        b[i] = ((X >> np.uint64(i)) & np.uint64(1)).astype(np.uint8)
    prev = b
    # Gate types: AND,AND,XOR,AND,AND,XOR,XOR,XOR (4 AND, 4 XOR)
    types = [0,0,1,0,0,1,1,1]  # 0=AND, 1=XOR
    offsets = [1,2,4,8,16,32,1,2]  # 8 levels
    for j in range(8):
        t, a = types[j], offsets[j]
        curr = np.zeros((64, N), dtype=np.uint8)
        for i in range(64):
            x, y = prev[i], prev[(i+a)%64]
            curr[i] = (x & y) if t==0 else (x ^ y)
        prev = curr
    G = np.zeros(N, dtype=np.uint64)
    for i in range(64):
        G |= (prev[i].astype(np.uint64) << np.uint64(i))
    return X ^ G

N = 16*64
X = np.arange(N, dtype=np.uint64)
Y = apply_8level(X)
D = sum(1 for b in range(16) if gf2_rank64(Y[b*64:(b+1)*64]) <= 61)
print(f"8-level (13.0u): D={D}/16")
