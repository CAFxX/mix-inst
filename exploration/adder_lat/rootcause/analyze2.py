"""Part 2: AND differential exact formula + quiet-probability bound.

Exact single-stage result (derived):
  (dA)_j = x_{j-a}.d_{j-b} XOR x_{j-b}.d_{j-a} XOR d_{j-a}.d_{j-b}
  E[(-1)^{(dA)_j}] = 1  if d_{j-a}=d_{j-b}=0   (AND transparent, deterministic 0)
                     0  otherwise               (AND randomizes, balanced)

Corollary upper bound on output-bit bias after stage i:
  |bias_j^{(i)}| <= (1/2) * P[ d_{j-a_i}=0 AND d_{j-b_i}=0 ],  d ~ D_{i-1}.

S2 passes iff (1/2)*P[quiet] < 9/sqrt(2^22) ~= 0.0044 for all j,
i.e. P[hit {j-a,j-b}] > 99.1% for all j.

We measure, by Monte Carlo:
  - Q_i = max_j P[quiet at stage i input, pair for stage i]  (the bound)
  - actual final max|z| (to see if bound predicts failure)
for 5-stage FAILs and 6-stage PASS, plus 5-stage prefixes.
"""
import numpy as np
from collections import Counter

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def rotl(x, r):
    r %= 64
    if r == 0: return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def popcnt(x): return bin(int(x)).count("1")

AND6A = [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)]
AND5XA = [(1,4,13),(5,16,7),(7,22,19),(11,37,5),(13,43,23)]
AND5XB = [(1,3,11),(2,9,17),(5,19,7),(7,25,13),(11,41,19)]

def stage_np(x, a, b, c):
    return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)) & M64

def sim_diffs(stages, d0, n, seed):
    """Return list of per-stage difference arrays (n,), stages[0] input -> out."""
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    x0, x1 = xs, xs ^ np.uint64(d0)
    out = []
    for (a,b,c) in stages:
        x0 = stage_np(x0,a,b,c); x1 = stage_np(x1,a,b,c)
        out.append((x0 ^ x1).copy())
    return out

def quiet_prob_bound(diff_arr, a, b):
    """max_j P[d has no bit at j-a nor j-b]. Vectorized over n samples x 64 j."""
    n = len(diff_arr)
    # for each j, need (d >> (j-a))&1 == 0 and (d >> (j-b))&1 == 0
    # build bit matrix: bits[s, j] = bit j of sample s
    d = diff_arr.astype(np.uint64)
    # quiet_j = mean_s [bit_{j-a}==0 and bit_{j-b}==0]
    # use broadcasting: idx arrays
    js = np.arange(64)
    ia = (js - a) % 64
    ib = (js - b) % 64
    # bits_s_j for j in ia / ib
    # extract via shifts: bitmat[s, k] = (d[s] >> k) & 1
    # do it in chunks to save memory: 2^20 x 64 bool = 64M entries = 64MB, ok as bool? use uint8
    bitmat = ((d[:, None] >> np.uint64(np.arange(64)[None, :])) & np.uint64(1)).astype(np.uint8)
    qa = bitmat[:, ia]  # n x 64
    qb = bitmat[:, ib]
    quiet = ((qa == 0) & (qb == 0)).mean(axis=0)  # 64,
    return quiet.max(), int(np.argmax(quiet)), quiet

def max_abs_z(diff_arr):
    n = len(diff_arr)
    d = diff_arr.astype(np.uint64)
    bitmat = ((d[:, None] >> np.uint64(np.arange(64)[None, :])) & np.uint64(1)).astype(np.float64)
    m = bitmat.mean(axis=0)
    z = (m - 0.5) / np.sqrt(0.25 / n)
    return np.abs(z).max(), int(np.argmax(np.abs(z)))

def report(name, stages, d0_list, n=1<<20, seed=777):
    print(f"=== {name}: {len(stages)} stages ===")
    for d0 in d0_list:
        diffs = sim_diffs(stages, d0, n, seed)
        # quiet bound at each stage input (stage i uses diffs[i-1], pair (a_i,b_i))
        # for final output bias, the relevant quiet is at LAST stage input
        (aL,bL,cL) = stages[-1]
        qmax, jq, qvec = quiet_prob_bound(diffs[-2] if len(diffs)>=2 else None or diffs[0], aL, bL) \
            if len(stages)>=2 else (None,None,None)
        # careful: diffs[k] is output of stage k; input to last stage = diffs[-2]
        zmax, jz = max_abs_z(diffs[-1])
        # mean weight of diffs
        wmean = np.mean([popcnt(int(v)) for v in diffs[-1][:4096]])
        print(f"  d0={d0:#018x}: final max|z|={zmax:7.1f} (bit {jz}), "
              f"Qbound max P[quiet]={qmax:.4f} at j={jq} -> bound/2={qmax/2:.4f}, "
              f"mean wt={wmean:.1f}")
        # also per-stage quiet for the trajectory
        for i,(a,b,c) in enumerate(stages):
            din = None
            # input to stage i: d0 if i==0 else diffs[i-1]
            if i == 0:
                # d0 fixed: quiet = 1 if d0 has no bit at j-a,j-b else 0
                qq = 0.0
                for j in range(64):
                    if not (d0 >> ((j-a)%64)) & 1 and not (d0 >> ((j-b)%64)) & 1:
                        qq = max(qq, 1.0)
                print(f"      stage {i}: input fixed d0, max P[quiet]={qq:.2f}")
            else:
                qm, jqm, _ = quiet_prob_bound(diffs[i-1], a, b)
                print(f"      stage {i}: max P[quiet]={qm:.4f} (j={jqm})")

if __name__ == "__main__":
    # worst deltas from S2/triage: use single bits that failed
    # and5xa triage worst unknown; try bits 0, 10, 46 and a couple multi-bit
    deltas = [1<<0, 1<<10, 1<<46, 1<<63]
    report("and5xa(FAIL,5st)", AND5XA, deltas, n=1<<20)
    print()
    report("and5xb(FAIL,5st)", AND5XB, deltas, n=1<<18)
    print()
    report("and6a(PASS,6st)", AND6A, deltas, n=1<<18)
