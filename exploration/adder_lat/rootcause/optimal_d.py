"""Falsification test for point 3: can ANY last-stage (a5,b5) save a 5-stage design?

Key simplification: the 64 pairs {j-a5, j-b5} are just all cyclic distance-d
pairs {k, k+d} with d = b5-a5 (mod 64). So:
  max_j P[quiet] = max_k P[d4_k=0 AND d4_{k+d}=0],  d = b5-a5.

We compute, from the Monte-Carlo d4 distribution, min_d max_k P[miss at dist d].
If min_d (...) >> 0.009 for all d, NO (a5,b5) choice can make 5 stages pass.
This proves the wall is structural, not a rotation-tuning issue.
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def stage_np(x, a, b, c):
    return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)) & M64

AND5XA = [(1,4,13),(5,16,7),(7,22,19),(11,37,5),(13,43,23)]
AND6A5 = [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37)]  # and6a first5

def get_d4(stages4, d0, n=1<<16, seed=11):
    """Difference after 4 stages (input to 5th stage)."""
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    x0, x1 = xs, xs ^ np.uint64(d0)
    for (a,b,c) in stages4:
        x0 = stage_np(x0,a,b,c); x1 = stage_np(x1,a,b,c)
    return (x0 ^ x1).astype(np.uint64)

def min_over_d(d4):
    """Compute max_k P[miss] for each d=1..63, return best d and value."""
    n = len(d4)
    bitmat = ((d4[:,None] >> np.uint64(np.arange(64)[None,:])) & np.uint64(1)).astype(np.uint8)
    # bitmat[s,k] = bit k of sample s
    results = {}
    for d in range(1, 64):
        # P[bit_k=0 and bit_{k+d}=0] for each k, take max
        b0 = bitmat  # n x 64
        b1 = np.roll(bitmat, -d, axis=1)  # bit_{k+d}
        miss = ((b0==0)&(b1==0)).mean(axis=0).max()
        results[d] = miss
    best_d = min(results, key=lambda d: results[d])
    return best_d, results[best_d], results

for name, st4 in [("and5xa-d4", AND5XA[:4]), ("and6a-first4", AND6A5[:4])]:
    for d0 in [1, 1<<46]:
        d4 = get_d4(st4, d0, n=1<<16)
        bd, bv, allr = min_over_d(d4)
        # show top-5 best d and worst d
        srt = sorted(allr.items(), key=lambda kv: kv[1])
        print(f"{name} d0={d0:#x}: best d={bd} -> maxP[miss]={bv:.4f} "
              f"(need <0.009 to pass)")
        print(f"   5 best d: {[(d, round(v,4)) for d,v in srt[:5]]}")
        print(f"   5 worst d: {[(d, round(v,4)) for d,v in srt[-5:]]}")
    print()
