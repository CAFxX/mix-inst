"""Verify the exact AND differential formula:
  (dA)_j = x_{j-a}.d_{j-b} XOR x_{j-b}.d_{j-a} XOR d_{j-a}.d_{j-b}
  E[(-1)^{(dA)_j}] = 1  iff d_{j-a}=d_{j-b}=0, else 0.
And test 5-stage prefixes of and6a (does good schedule's 5-stage fail?)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def stage_np(x, a, b, c):
    return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)) & M64

AND6A = [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)]

# --- verify formula on random single stage ---
rng = np.random.default_rng(0)
a,b,c = 7,19,5
n = 1<<18
for trial, d0 in enumerate([np.uint64(1), np.uint64(1)<<np.uint64(33), np.uint64(0xF)]):
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    x0, x1 = xs, xs ^ d0
    y0, y1 = stage_np(x0,a,b,c), stage_np(x1,a,b,c)
    dA_actual = ((rotl(x0,a)&rotl(x0,b)) ^ (rotl(x1,a)&rotl(x1,b)))
    # predicted: (dA)_j = x_{j-a} d_{j-b} ^ x_{j-b} d_{j-a} ^ d_{j-a} d_{j-b}
    d = x0 ^ x1
    # vectorized check via bit loops (slow but exact) on subset
    ok = True
    for s in range(min(n, 2000)):
        xv = int(xs[s]); dv = int(d[s]); av = int(dA_actual[s])
        for j in range(64):
            xa_j_a = (xv >> ((j-a)%64)) & 1
            xa_j_b = (xv >> ((j-b)%64)) & 1
            dd_j_a = (dv >> ((j-a)%64)) & 1
            dd_j_b = (dv >> ((j-b)%64)) & 1
            pred = (xa_j_a & dd_j_b) ^ (xa_j_b & dd_j_a) ^ (dd_j_a & dd_j_b)
            act = (av >> j) & 1
            if pred != act:
                ok = False; break
        if not ok: break
    print(f"d0={d0:#x}: exact AND-diff formula {'HOLDS' if ok else 'FAILS'} (2000 samples x 64 bits)")

    # verify correlation claim: E[(-1)^{(dA)_j}] = 1 iff d_{j-a}=d_{j-b}=0 else 0
    # use fixed d0 (single bit p): d_{j-a}=1 iff j-a=p, etc.
    dA_bits = ((dA_actual[:,None] >> np.uint64(np.arange(64)[None,:])) & np.uint64(1)).astype(float)
    corr = 1 - 2*dA_bits.mean(axis=0)  # E[(-1)^{bit}]
    # for single-bit d0 at p: quiet (corr should be ~1) iff j not in {p+a, p+b}
    p = int(np.log2(int(d0))) if bin(int(d0)).count('1')==1 else -1
    if p >= 0:
        loud = {(p+a)%64, (p+b)%64}
        qcorr = [corr[j] for j in range(64) if j not in loud]
        lcorr = [corr[j] for j in loud]
        print(f"   quiet-bit |corr|: max={max(abs(v) for v in qcorr):.4f} (expect ~1.0), "
              f"touched-bit |corr|: max={max(abs(v) for v in lcorr):.4f} (expect ~0.0)")

print()
print("--- 5-stage prefixes of and6a (good 6-stage schedule) ---")
def maxq_and_z(stages, d0, n=1<<18, seed=5):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    x0, x1 = xs, xs ^ np.uint64(d0)
    diffs = []
    for (aa,bb,cc) in stages:
        x0 = stage_np(x0,aa,bb,cc); x1 = stage_np(x1,aa,bb,cc)
        diffs.append((x0^x1).copy())
    # quiet at last stage
    aL,bL,_ = stages[-1]
    d = diffs[-2].astype(np.uint64)
    bitmat = ((d[:,None] >> np.uint64(np.arange(64)[None,:])) & np.uint64(1)).astype(np.uint8)
    js = np.arange(64)
    quiet = ((bitmat[:,(js-aL)%64]==0)&(bitmat[:,(js-bL)%64]==0)).mean(axis=0)
    # final z
    df = diffs[-1].astype(np.uint64)
    bm = ((df[:,None] >> np.uint64(np.arange(64)[None,:])) & np.uint64(1)).astype(float).mean(axis=0)
    z = np.abs(bm-0.5)/np.sqrt(0.25/n)
    return quiet.max(), z.max()

for name, st in [("and6a-first5", AND6A[:5]), ("and6a-last5", AND6A[1:6])]:
    for d0 in [1, 1<<46]:
        q, z = maxq_and_z(st, d0)
        print(f"{name} d0={d0:#x}: maxP[quiet]={q:.4f} final max|z|={z:.1f}")
