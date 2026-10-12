import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/dagopt")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
import numpy as np
from lin_diff import gf2_rank64

NAND = 3
AND, XOR, OR = 0, 1, 2

def apply_nand(X, gate_types, offsets):
    N = X.shape[0]
    bits = np.zeros((64, N), dtype=np.uint8)
    for b in range(64):
        bits[b] = ((X >> np.uint64(b)) & np.uint64(1)).astype(np.uint8)
    prev = bits
    for j in range(6):
        t = gate_types[j]
        a = offsets[j]
        curr = np.zeros((64, N), dtype=np.uint8)
        for i in range(64):
            x = prev[i]; y = prev[(i+a)%64]
            if t == 0: curr[i] = x & y
            elif t == 1: curr[i] = x ^ y
            elif t == 2: curr[i] = x | y
            else: curr[i] = 1 ^ (x & y)  # NAND
        prev = curr
    Y = np.zeros(N, dtype=np.uint64)
    for b in range(64):
        Y |= (prev[b].astype(np.uint64) << np.uint64(b))
    return Y ^ X  # XIG

OFFSETS = [1,2,4,8,16,32]
# Try: NAND heavy
for gt in [
    [NAND,NAND,NAND,NAND,XOR,XOR],
    [NAND,XOR,NAND,XOR,NAND,XOR],
]:
    X = np.arange(16*64, dtype=np.uint64)
    Y = apply_nand(X, gt, OFFSETS)
    D = sum(1 for b in range(16) if gf2_rank64(Y[b*64:(b+1)*64]) <= 61)
    cost = sum(1.0 if t in (0,2,3) else 1.8 for t in gt) + 1.8
    print(f"gt={gt}, D={D}/16, cost={cost:.1f}u")
