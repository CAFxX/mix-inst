"""Word-level (fast) model of Repair A + offset search.

Stage E: out = w ^ (EVEN & (rotl(w,a) & rotl(w,b)))   [even targets]
Stage O: out = w ^ (ODD  & (rotl(w,a) & rotl(w,b)))   [odd targets]
(rotl(w,a)[t] = w[(t+a)%64], so this is exactly the bit-sliced model.)
Proxy: per-k (k=0..17) low-8-bit chi2 of output differences (DIFF essence).
"""
import numpy as np, math, itertools, sys, time

N = 1 << 18
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
EVEN = np.uint64(0x5555555555555555)
ODD = np.uint64(0xAAAAAAAAAAAAAAAA)
X = np.arange(N, dtype=np.uint64)

def rotl(w, a):
    # R[t] = w[(t+a) % 64]
    a &= 63
    if a == 0:
        return w
    return (((w >> np.uint64(a)) | (w << np.uint64(64 - a))) & M64)

def stage(w, a, b, parity):
    mask = EVEN if parity == 0 else ODD
    return (w ^ (mask & (rotl(w, a) & rotl(w, b)))) & M64

def run(seq):
    w = X.copy()
    for (a, b, p) in seq:
        w = stage(w, a, b, p)
    return w

def diff_proxy(S):
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
    return diff_proxy(run(seq))

def main():
    t0 = time.time()
    odds = [i for i in range(1, 64, 2)]
    pairs = [(a, b) for a in odds for b in odds if a != b]
    print(f"pairs: {len(pairs)}", flush=True)

    res2 = []
    for (a, b) in pairs:
        tz, wz = eval_seq([(a, b, 0), (a, b, 1)])
        res2.append((tz, wz, a, b))
    res2.sort()
    print(f"2-stage same-pair done ({time.time()-t0:.0f}s). top 15:", flush=True)
    for tz, wz, a, b in res2[:15]:
        print(f"  (a,b)=({a},{b}) total_z={tz:.1f} worst_z={wz:.1f}", flush=True)

    res3 = []
    for (a, b) in pairs:
        tz, wz = eval_seq([(a, b, 0), (a, b, 1), (a, b, 0)])
        res3.append((tz, wz, a, b))
    res3.sort()
    print(f"3-stage same-pair done ({time.time()-t0:.0f}s). top 15:", flush=True)
    for tz, wz, a, b in res3[:15]:
        print(f"  (a,b)=({a},{b}) total_z={tz:.1f} worst_z={wz:.1f}", flush=True)

    top = [(a, b) for _, _, a, b in res2[:12]]
    resm = []
    for (a1, b1), (a2, b2) in itertools.product(top, top):
        tz, wz = eval_seq([(a1, b1, 0), (a2, b2, 1)])
        resm.append((tz, wz, a1, b1, a2, b2))
    resm.sort()
    print(f"mixed done ({time.time()-t0:.0f}s). top 15:", flush=True)
    for tz, wz, a1, b1, a2, b2 in resm[:15]:
        print(f"  E=({a1},{b1}) O=({a2},{b2}) total_z={tz:.1f} worst_z={wz:.1f}", flush=True)

if __name__ == "__main__":
    main()
