# Extend dag_sim with OR gate
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/dagopt")
from dag_sim import AND, XOR
OR = 2

def apply_dag_or(X, gate_types, offsets):
    import numpy as np
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
            x = prev[i]
            y = prev[(i + a) % 64]
            if t == AND:
                curr[i] = x & y
            elif t == XOR:
                curr[i] = x ^ y
            else:  # OR
                curr[i] = x | y
        prev = curr
    Y = np.zeros(N, dtype=np.uint64)
    for b in range(64):
        Y |= (prev[b].astype(np.uint64) << np.uint64(b))
    return Y

def apply_xig_or(X, gate_types, offsets):
    return X ^ apply_dag_or(X, gate_types, offsets)

def cost_or(gate_types):
    # AND=1.0, OR=1.0, XOR=1.8, plus XIG 1.8
    c = sum(1.0 if t in (AND, OR) else 1.8 for t in gate_types)
    return c + 1.8

if __name__ == "__main__":
    import numpy as np
    OFFSETS = [1, 2, 4, 8, 16, 32]
    # Try: AND, OR, AND, OR, XOR, XOR
    gt = [AND, OR, AND, OR, XOR, XOR]
    print("Cost:", cost_or(gt))
    X = np.array([0, 1, 2, 3], dtype=np.uint64)
    Y = apply_xig_or(X, gt, OFFSETS)
    print([hex(int(y)) for y in Y])
