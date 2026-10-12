"""Bit-sliced functional model of Repair A (bipartite Toffoli) + offset search.

Stage E: even targets, odd controls frozen (a,b odd).
Stage O: odd targets, even controls frozen.
Configs: 1-stage (E), 2-stage (E+O), 3-stage (E+O+E).
Proxy: per-k (k=0..17) low-8-bit chi2 of output differences (DIFF essence).
"""
import numpy as np, math, itertools, sys

N = 1 << 18
X = np.arange(N, dtype=np.uint64)
BITS = [((X >> np.uint64(i)) & np.uint64(1)).astype(np.uint8) for i in range(64)]

def stage(bits, a, b, parity):
    """parity=0: even targets; parity=1: odd targets. Returns new bit list."""
    out = list(bits)
    for t in range(parity, 64, 2):
        c1 = bits[(t + a) % 64]
        c2 = bits[(t + b) % 64]
        out[t] = bits[t] ^ (c1 & c2)
    return out

def run(bits, seq):
    """seq: list of (a,b,parity)."""
    for (a, b, p) in seq:
        bits = stage(bits, a, b, p)
    return bits

def assemble(bits):
    S = np.zeros(N, dtype=np.uint64)
    for i, b in enumerate(bits):
        S |= b.astype(np.uint64) << np.uint64(i)
    return S

def diff_proxy(S):
    """Sum over k=0..17 of chi2 z-scores of low8(S[x]^S[x^2^k]). Lower is better."""
    idx = np.arange(N, dtype=np.uint64)
    total_z = 0.0
    worst = 0.0
    for k in range(18):
        dl = np.uint64(1) << np.uint64(k)
        dx = (S ^ S[idx ^ dl]) & np.uint64(0xFF)
        h = np.bincount(dx.astype(np.int64), minlength=256).astype(float)
        exp = N / 256.0
        chi2 = float((((h - exp) ** 2) / exp).sum())
        z = abs(chi2 - 255) / math.sqrt(2.0 * 255)
        total_z += z
        worst = max(worst, z)
    return total_z, worst

def eval_seq(seq):
    S = assemble(run(BITS, seq))
    tz, wz = diff_proxy(S)
    return tz, wz

def main():
    odds = [i for i in range(1, 64, 2)]
    pairs = [(a, b) for a in odds for b in odds if a != b]
    print(f"pairs: {len(pairs)}", flush=True)

    # 2-stage (E+O), same pair both stages
    res2 = []
    for (a, b) in pairs:
        tz, wz = eval_seq([(a, b, 0), (a, b, 1)])
        res2.append((tz, wz, a, b))
    res2.sort()
    print("top 15 two-stage (same pair), by total z:", flush=True)
    for tz, wz, a, b in res2[:15]:
        print(f"  (a,b)=({a},{b}) total_z={tz:.1f} worst_z={wz:.1f}", flush=True)

    # 3-stage (E+O+E), same pair
    res3 = []
    for (a, b) in pairs:
        tz, wz = eval_seq([(a, b, 0), (a, b, 1), (a, b, 0)])
        res3.append((tz, wz, a, b))
    res3.sort()
    print("top 15 three-stage (same pair), by total z:", flush=True)
    for tz, wz, a, b in res3[:15]:
        print(f"  (a,b)=({a},{b}) total_z={tz:.1f} worst_z={wz:.1f}", flush=True)

    # mixed pairs on top-12 of two-stage
    top = [(a, b) for _, _, a, b in res2[:12]]
    resm = []
    for (a1, b1), (a2, b2) in itertools.product(top, top):
        tz, wz = eval_seq([(a1, b1, 0), (a2, b2, 1)])
        resm.append((tz, wz, a1, b1, a2, b2))
    resm.sort()
    print("top 15 two-stage (mixed pairs), by total z:", flush=True)
    for tz, wz, a1, b1, a2, b2 in resm[:15]:
        print(f"  E=({a1},{b1}) O=({a2},{b2}) total_z={tz:.1f} worst_z={wz:.1f}", flush=True)

if __name__ == "__main__":
    main()
