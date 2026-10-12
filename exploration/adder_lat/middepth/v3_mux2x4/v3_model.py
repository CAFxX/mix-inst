#!/usr/bin/env python3
"""V3: 4-stage MUX2 network model (bit-exact vs gen_v3.py Verilog).

Stage: 64 parallel MUX2. Output bit j:
    y_j = mux(sel_j, a_j, b_j),  sel_j = rotl(x,s)[j],
    a_j = rotl(x,p1)[j], b_j = rotl(x,p2)[j]
i.e. y = (sel & a) | (~sel & b), all 64-bit words.

rotl convention (matches t8_het8_screen.rotl and Verilog (x<<r)|(x>>(64-r))):
    rotl(x,r)[j] = x[(j-r) mod 64].
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

# Base 4-stage schedule: (s, p1, p2) per stage. All distinct within a stage,
# odd rotations present, gcd(all rotations, 64) == 1 (no parity-class split).
BASE_STAGES = [
    (0, 7, 29),
    (13, 31, 53),
    (5, 19, 43),
    (11, 23, 47),
]


def rotl(x, r):
    r %= 64
    if r == 0:
        return x & M64
    r = np.uint64(r)
    return (((x << r) | (x >> (np.uint64(64) - r))) & M64)


def mux2_layer(x, s, p1, p2):
    sel = rotl(x, s)
    a = rotl(x, p1)
    b = rotl(x, p2)
    return ((sel & a) | ((~sel) & b)) & M64


def apply_stages(x, stages=BASE_STAGES):
    x = np.asarray(x, dtype=np.uint64) & M64
    for (s, p1, p2) in stages:
        x = mux2_layer(x, s, p1, p2)
    return x & M64


def gen_seq(stages, keys, n):
    """Battery-style sequence dict: x = V^K, apply stages, S = x ^ rotl(K,13)."""
    seq = {}
    V = np.arange(n, dtype=np.uint64)
    for key in keys:
        K = np.full(n, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        x = apply_stages(x, stages)
        seq[key] = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
    return seq


def dependency_cone(stages):
    """Exact per-output-bit input dependency sets after all stages."""
    # cone[j] = set of stage-(i) bit positions feeding output bit j.
    cone = [{j} for j in range(64)]
    for (s, p1, p2) in stages:
        new = [set() for _ in range(64)]
        for j in range(64):
            for r in (s, p1, p2):
                new[j] |= cone[(j - r) % 64]
        cone = new
    return cone


def check_draw(stages):
    """Structural validity: distinct nonzero p1/p2, s distinct, no parity split."""
    rots = []
    for (s, p1, p2) in stages:
        if not (1 <= p1 <= 63 and 1 <= p2 <= 63):
            return False, "p1/p2 range"
        if len({s % 64, p1, p2}) != 3:
            return False, "rotation collision in stage"
        rots += [s, p1, p2]
    import math
    g = 64
    for r in rots:
        g = math.gcd(g, r % 64)
    if g != 1:
        return False, f"gcd(rotations,64)={g} != 1 (parity-class split)"
    cone = dependency_cone(stages)
    mincov = min(len(c) for c in cone)
    if mincov < 56:
        return False, f"min cone coverage {mincov} < 56"
    return True, f"ok mincov={mincov}"


def avalanche(stages, key, nxs=4096, seed=0x5EED):
    """Mean flipped output bits per weight-1 input delta (64 deltas)."""
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=nxs, dtype=np.uint64)
    K = np.uint64(key)
    base = apply_stages((xs ^ K) & M64, stages)
    flips = []
    for j in range(64):
        dj = np.uint64(1) << np.uint64(j)
        out = apply_stages(((xs ^ K) ^ dj) & M64, stages)
        d = (out ^ base)
        flips.append(float(np.mean([bin(int(v)).count("1") for v in d])))
    return flips


def second_derivative_nonzero(stages, key, ntri=2048, seed=0xA11CE):
    """True iff F is NOT affine: exists (x,a,b) with d2 != 0. Vectorized."""
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, 2**64, size=ntri, dtype=np.uint64)
    a = rng.integers(1, 2**64, size=ntri, dtype=np.uint64)
    b = rng.integers(1, 2**64, size=ntri, dtype=np.uint64)
    K = np.uint64(key)
    F = lambda v: apply_stages((v ^ K) & M64, stages)
    d2 = F(xs) ^ F(xs ^ a) ^ F(xs ^ b) ^ F(xs ^ a ^ b)
    return bool(np.any(d2))


if __name__ == "__main__":
    ok, msg = check_draw(BASE_STAGES)
    print("base draw check:", ok, msg)
    fl = avalanche(BASE_STAGES, 0x9E3779B97F4A7C15)
    print("avalanche mean/min/max: %.2f / %.2f / %.2f" %
          (sum(fl) / 64, min(fl), max(fl)))
    print("non-affine:", second_derivative_nonzero(BASE_STAGES, 0x9E3779B97F4A7C15))
