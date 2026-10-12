"""General bipartite model: configurable nonlinear gate.

Gate: out[t] = w[t] ^ G(w[t+a1], ..., w[t+ak])   (t = target parity)
  G = AND_k  (gate='and')  -> delay ANDk + XOR2
  G = NAND_k (gate='nand') -> delay NANDk + XOR2   [out = w[t] ^ ~(AND)]
Controls must have opposite parity to targets (offsets odd).
"""
import numpy as np, math, sys, time

N = 1 << 18
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
EVEN = np.uint64(0x5555555555555555)
ODD = np.uint64(0xAAAAAAAAAAAAAAAA)
X = np.arange(N, dtype=np.uint64)

def rot(w, a):
    a &= 63
    if a == 0:
        return w
    return (((w >> np.uint64(a)) | (w << np.uint64(64 - a))) & M64)

def stage(w, offs, parity, gate):
    mask = EVEN if parity == 0 else ODD
    g = None
    for a in offs:
        r = rot(w, a)
        g = r if g is None else (g & r)
    if gate == 'nand':
        g = (~g) & M64
    return (w ^ (mask & g)) & M64

def run(seq, gate):
    w = X.copy()
    for (offs, p) in seq:
        w = stage(w, offs, p, gate)
    return w

def diff_proxy(S, ks=range(18)):
    idx = np.arange(N, dtype=np.uint64)
    total_z = 0.0
    worst = 0.0
    per_k = {}
    for k in ks:
        dl = np.uint64(1) << np.uint64(k)
        dx = (S ^ S[idx ^ dl]) & np.uint64(0xFF)
        h = np.bincount(dx.astype(np.int64), minlength=256).astype(float)
        exp = N / 256.0
        chi2 = float((((h - exp) ** 2) / exp).sum())
        z = abs(chi2 - 255) / math.sqrt(2.0 * 255)
        total_z += z
        worst = max(worst, z)
        per_k[k] = z
    return total_z, worst, per_k

def infl_bits(S, k):
    """Which of the low 8 output bits ever flip for delta 2^k."""
    idx = np.arange(N, dtype=np.uint64)
    dl = np.uint64(1) << np.uint64(k)
    dx = (S ^ S[idx ^ dl]) & np.uint64(0xFF)
    m = int(np.bitwise_or.reduce(dx))
    return m

if __name__ == "__main__":
    # 3-stage bipartite NAND4, shared offset set per stage (tune me)
    offsE = (1, 7, 17, 31)
    offsO = (3, 11, 23, 29)
    seq = [(offsE, 0), (offsO, 1), (offsE, 0)]
    t0 = time.time()
    S = run(seq, 'nand')
    print(f"run 3-stage NAND4: {time.time()-t0:.1f}s", flush=True)
    tz, wz, pk = diff_proxy(S)
    print(f"total_z={tz:.1f} worst_z={wz:.1f}", flush=True)
    for k in range(18):
        m = infl_bits(S, k)
        print(f"  k={k:2d}: z={pk[k]:10.1f} lowbits-ever={bin(m).count('1')}/8", flush=True)
