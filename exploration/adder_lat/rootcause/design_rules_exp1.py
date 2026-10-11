"""Experiment 1: WHY does fz15_c (5-stage 3-term-linear, S2-clean) beat the wall?

Hypothesis: its 4-stage prefix produces a much more uniform d_4, so the
last-stage pair-miss probability drops below the 0.009 S2 threshold.

Metric: min_d max_k P[d4 misses distance-d pair] (from optimal_d.py).
Need < 0.009 for a 5-stage to have any chance.
"""
import numpy as np, sys
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
from optimal_d import get_d4 as get_d4_and, min_over_d

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x

def stage_t3(x, a, b, c, e):
    """3-term-linear: x ^ (ra&rb) ^ rc ^ re"""
    return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c) ^ rotl(x,e)) & M64

# fz15_c stages: (a,b,c,e)
FZ15C = [(1,7,13,29),(3,11,19,37),(5,15,25,41),(9,21,31,49),(13,27,37,55)]
AND5XA4 = [(1,4,13),(5,16,7),(7,22,19),(11,37,5)]  # fail prefix
AND6A4 = [(1,2,13),(7,19,5),(3,11,29),(17,31,7)]   # and6a first4

def get_d4_t3(stages4, d0, n=1<<16, seed=11):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    x0, x1 = xs, xs ^ np.uint64(d0)
    for (a,b,c,e) in stages4:
        x0 = stage_t3(x0,a,b,c,e); x1 = stage_t3(x1,a,b,c,e)
    return (x0 ^ x1).astype(np.uint64)

def mean_weight(d4):
    return np.mean([bin(int(v)).count('1') for v in d4[:4096]])

for name, st4, fn in [
    ("and5xa-prefix(FAIL)", AND5XA4, lambda s,d0: get_d4_and([(a,b,c) for a,b,c in s], d0)),
    ("and6a-first4(FAIL-as-5)", AND6A4, lambda s,d0: get_d4_and([(a,b,c) for a,b,c in s], d0)),
    ("fz15c-prefix(PASS)", FZ15C[:4], get_d4_t3),
]:
    for d0 in [1, 1<<46]:
        d4 = fn(st4, d0)
        bd, bv, allr = min_over_d(d4)
        srt = sorted(allr.items(), key=lambda kv: kv[1])
        print(f"{name} d0={d0:#x}: mean_wt={mean_weight(d4):.1f} "
              f"best d={bd} -> maxP[miss]={bv:.4f} (need <0.009)")
        print(f"   5 best d: {[(d, round(v,4)) for d,v in srt[:5]]}")
    print()
