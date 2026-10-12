# Test: if g(x) is constant on 0..63, what is rank of f(x)=x^g(x)?
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
import numpy as np
from lin_diff import gf2_rank64

# Simulate: g(x) = 0 (constant)
X = np.arange(64, dtype=np.uint64)
Y = X ^ np.uint64(0)  # g=0
r = gf2_rank64(Y)
print(f"g=0 constant: rank={r} (expect 6, since only low 6 bits vary)")

# g(x) = 0xFFFF (constant with high bits)
Y2 = X ^ np.uint64(0xFFFF)
r2 = gf2_rank64(Y2)
print(f"g=0xFFFF constant: rank={r2} (expect 7: 6 + 1 for high bits of C)")

# g(x) = x & 0x3F (only low 6 bits, nonlinear but limited)
Y3 = X ^ (X & np.uint64(0x3F))
r3 = gf2_rank64(Y3)
print(f"g=x&0x3F: rank={r3}")
