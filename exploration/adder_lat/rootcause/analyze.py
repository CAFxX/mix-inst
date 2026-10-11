"""Root-cause analysis of the 5-stage DIFF wall.
Track 3, 2026-10-10. Analysis, not candidate generation.

Question: WHY do 5-stage designs fail DIFF while (good) 6-stage designs pass,
across EVERY family tested (AND-cascade, chi, 3-term-linear, hetero)?

Approach:
 1. Linear-skeleton analysis: M_r = Prod_i (I + R^{c_i}). If the linear part
    maps some single-bit input to low weight, the AND must mask a
    high-probability linear trail. Compute min weight over single-bit inputs.
 2. Monte-Carlo trail tracking: for the worst S2 delta, simulate pairs and
    record the empirical intermediate-difference distribution. Identify
    dominant trails and WHY they dominate.
 3. Beam-search for max-probability differential characteristics (independence
    approx for AND), to see the structural trail shape.
"""
import numpy as np
import sys

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def popcnt(x):
    return bin(int(x)).count("1")

# ---- candidate stage schedules (a,b,c) ----
AND6A = [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)]  # PASSES S2
AND5XA = [(1,4,13),(5,16,7),(7,22,19),(11,37,5),(13,43,23)]            # FAILS (triage zmax 60)
AND5XB = [(1,3,11),(2,9,17),(5,19,7),(7,25,13),(11,41,19)]            # FAILS (triage zmax 130)

def stage_np(x, a, b, c):
    return (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)) & M64

def cascade_np(V, stages):
    x = np.asarray(V, dtype=np.uint64)
    for (a,b,c) in stages:
        x = stage_np(x, a, b, c)
    return x

# =====================================================================
# 1. LINEAR SKELETON: M_r = Prod_i (I + R^{c_i}) applied to single bits
#    Represent as 64x64 GF(2) matrix acting on column vectors (bitmasks).
# =====================================================================
def lin_skeleton_matrix(cs):
    """Return 64x64 GF(2) matrix M = (I+R^{c_r})...(I+R^{c_1}) as list of
    64 row-masks (row i = which input bits affect output bit i). We apply
    M to a difference bitmask d: out = M*d. Represent M by columns:
    col p = M * e_p (image of single bit p)."""
    # M*e_p: start with e_p, apply (I+R^{c_1}) first, etc.
    cols = []
    for p in range(64):
        d = np.uint64(1) << np.uint64(p)
        for c in cs:
            d = d ^ rotl(d, c)
        cols.append(int(d))
    return cols  # cols[p] = image of bit p

def min_image_weight(cols):
    ws = [popcnt(c) for c in cols]
    i = int(np.argmin(ws))
    return min(ws), i, cols[i]

def report_skeleton(name, stages):
    cs = [c for (a,b,c) in stages]
    cols = lin_skeleton_matrix(cs)
    mw, p, img = min_image_weight(cols)
    ws = sorted(popcnt(c) for c in cols)
    print(f"--- linear skeleton {name}: c={cs}")
    print(f"    min image weight over single-bit inputs: {mw} (input bit {p} -> {img:#018x})")
    print(f"    weight distribution: min={ws[0]} p10={ws[6]} med={ws[32]} max={ws[63]}")
    return mw

# =====================================================================
# 2. MONTE-CARLO TRAIL TRACKING
#    For input difference d0, simulate N pairs, record per-stage differences.
# =====================================================================
def trail_montecarlo(stages, d0, n=1<<20, seed=12345):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    # track differences stage by stage
    diffs = []
    x0, x1 = xs, xs ^ np.uint64(d0)
    d = x0 ^ x1
    assert np.all(d == np.uint64(d0))
    for (a,b,c) in stages:
        x0 = stage_np(x0, a, b, c)
        x1 = stage_np(x1, a, b, c)
        d = x0 ^ x1
        diffs.append(d.copy())
    return diffs  # list of n-element arrays, one per stage

def analyze_trails(name, stages, d0, n=1<<20):
    from collections import Counter
    diffs = trail_montecarlo(stages, d0, n=n)
    print(f"--- trail MC {name}: d0={d0:#018x}, N={n}")
    for i, d in enumerate(diffs):
        cnt = Counter(int(v) for v in d)
        top = cnt.most_common(5)
        # weight stats
        ws = np.array([popcnt(int(v)) for v in d])
        # output-bit bias: max over j of |P[d_j=1]-1/2| as z
        bits = np.unpackbits(d.view(np.uint8)).reshape(n, 64)[:, ::-1]  # bit j -> col?
        # simpler: compute per-bit mean via vectorized
        bmean = np.zeros(64)
        dd = d.astype(np.uint64)
        for j in range(64):
            bmean[j] = np.mean((dd >> np.uint64(j)) & np.uint64(1))
        z = (bmean - 0.5) / np.sqrt(0.25 / n)
        jmax = int(np.argmax(np.abs(z)))
        print(f"    stage {i}: top diffs: " +
              ", ".join(f"{v:#018x}x{k}({k/n:.3f})" for v,k in top))
        print(f"           weight: mean={ws.mean():.2f} max={ws.max()} | "
              f"max|z|={np.abs(z).max():.1f} at bit {jmax} (bias={bmean[jmax]-0.5:+.4f})")
    return diffs

if __name__ == "__main__":
    print("="*70)
    print("PART 1: linear skeleton min-weight analysis")
    print("="*70)
    for name, st in [("and6a(PASS)", AND6A), ("and5xa(FAIL)", AND5XA), ("and5xb(FAIL)", AND5XB)]:
        report_skeleton(name, st)
    # also: 5-stage prefix of and6a (first 5 stages) -- does the good schedule's
    # 5-stage prefix already show the wall?
    print()
    report_skeleton("and6a-first5", AND6A[:5])
    report_skeleton("and6a-last5", AND6A[1:6])
