"""Vectorized empirical validation of the 2-round skip differential trail (P=2^-2)."""
import sys, os, math
import numpy as np
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round7/models"))
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round5/models"))
from r5 import _rk_np
from r7 import _sbox_layer32_np, _lin32_np, MASK32

S1 = [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]
DDT = [[0]*16 for _ in range(16)]
for x in range(16):
    for a in range(16):
        DDT[a][S1[x] ^ S1[x ^ a]] += 1
best = [(a, e) for a in range(1,16) for e in range(16) if DDT[a][e] == 4]

def feistel2_np(x, k):
    L = ((x >> np.uint64(32)) ^ (k >> np.uint64(32))) & MASK32
    R = (x ^ k) & MASK32
    for i in (1, 2):
        rk = _rk_np(k, i)
        F = (_lin32_np(_sbox_layer32_np(R, S1)) ^ (rk & MASK32)) & MASK32
        L, R = R, (L ^ F) & MASK32
    return (R << np.uint64(32)) | L

def lin32(x):
    x &= 0xFFFFFFFF
    return (x ^ (((x << 7) | (x >> 25)) & 0xFFFFFFFF) ^ (((x << 13) | (x >> 19)) & 0xFFFFFFFF)) & 0xFFFFFFFF

a_nib, e_nib = best[0]
results = []
for p1 in [0, 3, 7]:
    a = np.uint64(a_nib << (4*p1))
    e = np.uint64(e_nib << (4*p1))
    f = np.uint64(lin32(int(e)))
    din = a << np.uint64(32)          # (dL0,dR0) = (a,0)
    # output is (R2<<32)|L2, (dL2,dR2)=(a,f) -> dout = (f<<32)|a
    dout_pred = (f << np.uint64(32)) | a
    results.append((p1, int(din), int(dout_pred)))

rng = np.random.default_rng(7)
kfix = np.uint64(0x123456789ABCDEF0)
N = 1 << 22
vv = rng.integers(0, 1 << 64, N, dtype=np.uint64)
kk = np.full(N, kfix)
h1 = feistel2_np(vv, kk)
print(f"skip-pattern 2-round trails (predicted P=2^-2), N=2^22:")
for (p1, din, dout_pred) in results:
    h2 = feistel2_np(vv ^ np.uint64(din), kk)
    hits = int(np.sum((h1 ^ h2) == np.uint64(dout_pred)))
    print(f"  nibble pos {p1}: hits={hits}, P_emp=2^{math.log2(hits/N):.3f}")

# contrast: M9's non-skip pattern (0,a). Theory: r1 has 1 active S-box (2^-2),
# r2's F input is f1 = lin(e1) with wt>=3 -> >=3 active S-boxes -> P <= 2^-2 * 2^-6 = 2^-8.
# (M9 measured 2^-10 on their specific chain.) No empirical re-run needed.
print("non-skip (0,a): theoretical best <= 2^-8 (1 + >=3 active S-boxes); M9 measured 2^-10")
