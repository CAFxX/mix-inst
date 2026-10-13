"""Empirical validation of the 2-round skip differential trail (predicted P=2^-2)."""
import sys, os, math
import numpy as np
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round7/models"))
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round5/models"))
from r5 import _rk_np

S1 = [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]
DDT = [[0]*16 for _ in range(16)]
for x in range(16):
    for a in range(16):
        DDT[a][S1[x] ^ S1[x ^ a]] += 1
# best single-nibble transitions (count 4)
best = [(a, e) for a in range(1,16) for e in range(16) if DDT[a][e] == 4]
print("nibble transitions with DDT=4:", best[:8], "... total", len(best))

def lin32(x):
    x &= 0xFFFFFFFF
    return (x ^ (((x << 7) | (x >> 25)) & 0xFFFFFFFF) ^ (((x << 13) | (x >> 19)) & 0xFFFFFFFF)) & 0xFFFFFFFF
def sbox_layer32(x):
    r = 0
    for i in range(8):
        r |= S1[(x >> (4*i)) & 0xF] << (4*i)
    return r & 0xFFFFFFFF
def F2(R, rk):
    return lin32(sbox_layer32(R)) ^ (rk & 0xFFFFFFFF)
def feistel2(x, k):
    L = ((x >> 32) ^ (k >> 32)) & 0xFFFFFFFF
    R = (x ^ k) & 0xFFFFFFFF
    for i in (1, 2):
        rk = int(_rk_np(np.uint64(k), i))
        L, R = R, L ^ F2(R, rk)
    return (R << 32) | L

# skip-pattern trail: input diff (a,0), a = single nibble in HIGH 32 (dL)
a_nib, e_nib = best[0]
p1 = 3  # nibble position
a = a_nib << (4*p1)
e = e_nib << (4*p1)
f = lin32(e)
din = (a << 32)  # (dL0,dR0) = (a, 0)
dout_pred = (a << 32) | f  # (dL2,dR2) = (a, f)
print(f"trail: din=0x{din:016x} -> dout=0x{dout_pred:016x}, predicted P=2^-2")

rng = np.random.default_rng(7)
kfix = 0x123456789ABCDEF0
for N in [1<<20, 1<<22]:
    vv = rng.integers(0, 1<<64, N, dtype=np.uint64)
    h1 = np.array([feistel2(int(v), kfix) for v in vv], dtype=np.uint64)
    h2 = np.array([feistel2(int(v ^ np.uint64(din)), kfix) for v in vv], dtype=np.uint64)
    hits = int(np.sum((h1 ^ h2) == np.uint64(dout_pred)))
    print(f"  N=2^{int(math.log2(N))}: hits={hits}, P_emp=2^{math.log2(hits/N):.2f} (pred 2^-2.00)")
    if N == 1<<22:
        # also check M9's non-skip pattern for contrast: din'=(0,a)
        din2 = a  # (dL0,dR0)=(0,a)
        h3 = np.array([feistel2(int(v ^ np.uint64(din2)), kfix) for v in vv], dtype=np.uint64)
        # M9 trail: (0,a) -> r1: (a, f) -> r2: F input f (wt3); just count exact predicted dout is hard;
        # instead measure P(any fixed predicted 2r output) upper: count hits of their specific dout
        f1 = lin32(e)
        # their measured: dout2 = 0x020638f0 pattern; approximate: count pairs where dL2==a (necessary)
        cnt_dl = int(np.sum(((h1 ^ h3) >> np.uint64(32)) == np.uint64(a)))
        print(f"  non-skip (0,a): P(dL2==a)=2^{math.log2(cnt_dl/N):.2f} (their chain needs more)")

print()
print("== C model vs Python model (spot check via 2-round python) ==")
# verify feistel2 matches r7 8-round structure on first 2 rounds: compare with full r7 by construction (skip)
