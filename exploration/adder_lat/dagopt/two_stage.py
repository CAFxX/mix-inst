#!/usr/bin/env python3
"""
Two-stage NL=112 DAG.
Stage 1: 64x 7-input NL=112 functions (3 levels).
Stage 2: 64x 7-input NL=112 functions on Stage 1 outputs (3 levels).
Total: 6 levels, degree 4.
"""

import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/dagopt")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")

import numpy as np
import random

def nl112_7bit(a0, a1, a2, a3, a4, a5, a6):
    """
    x0 ^ (x1&x4) ^ (x2&x7) ^ (x3&x6) — NL=112, 3 levels.
    Inputs: 7 bits (as 0/1 ints or numpy arrays).
    """
    return a0 ^ (a1 & a4) ^ (a2 & a6) ^ (a3 & a5)
    # Note: mapping a0..a6 to x0,x1,x2,x3,x4,x6,x7 (skip x5)

def apply_stage_vectorized(X_bits, wiring):
    """
    X_bits: (64, N) numpy array, bit-planes.
    wiring: list of 64 tuples, each 7 input indices.
    Returns: (64, N) output bit-planes.
    """
    N = X_bits.shape[1]
    out = np.zeros((64, N), dtype=np.uint8)
    for i in range(64):
        idx = wiring[i]  # 7 indices
        a0 = X_bits[idx[0]]
        a1 = X_bits[idx[1]]
        a2 = X_bits[idx[2]]
        a3 = X_bits[idx[3]]
        a4 = X_bits[idx[4]]
        a5 = X_bits[idx[5]]
        a6 = X_bits[idx[6]]
        out[i] = nl112_7bit(a0, a1, a2, a3, a4, a5, a6)
    return out

def build_wiring():
    """
    Hierarchical wiring for 2-stage 7-input.
    Stage 1: output i takes 7 inputs: i, i+1, ..., i+6 (mod 64).
    Stage 2: output i takes 7 Stage-1 outputs: i, i+9, i+18, ... (spread).
    Goal: maximize input coverage (aim for 49 distinct).
    """
    w1 = []
    for i in range(64):
        # 7 consecutive inputs
        idx = tuple((i + j) % 64 for j in range(7))
        w1.append(idx)
    w2 = []
    for i in range(64):
        # 7 Stage-1 outputs, spaced by 9 (9*7=63, covers well)
        idx = tuple((i + j*9) % 64 for j in range(7))
        w2.append(idx)
    return w1, w2

def apply_two_stage(X, w1, w2):
    """X: (N,) uint64. Returns Y: (N,) uint64 (before XIG)."""
    N = X.shape[0]
    # Bit-planes
    bits0 = np.zeros((64, N), dtype=np.uint8)
    for b in range(64):
        bits0[b] = ((X >> np.uint64(b)) & np.uint64(1)).astype(np.uint8)
    bits1 = apply_stage_vectorized(bits0, w1)
    bits2 = apply_stage_vectorized(bits1, w2)
    # Pack
    Y = np.zeros(N, dtype=np.uint64)
    for b in range(64):
        Y |= (bits2[b].astype(np.uint64) << np.uint64(b))
    return Y

def apply_xig_two_stage(X, w1, w2):
    return X ^ apply_two_stage(X, w1, w2)

def compute_coverage(w1, w2):
    """Compute max input coverage per output."""
    # Stage 2 output i depends on 7 Stage-1 outputs (w2[i]).
    # Each Stage-1 output j depends on 7 inputs (w1[j]).
    max_cov = 0
    for i in range(64):
        s = set()
        for j in w2[i]:
            for k in w1[j]:
                s.add(k)
        max_cov = max(max_cov, len(s))
    return max_cov

if __name__ == "__main__":
    w1, w2 = build_wiring()
    print("Max input coverage:", compute_coverage(w1, w2))
    # Quick test
    X = np.array([0, 1, 2, 3], dtype=np.uint64)
    Y = apply_xig_two_stage(X, w1, w2)
    print("Test:", [hex(int(y)) for y in Y])
    # Cost: 2 stages x 3 levels = 6 levels.
    # Each NL112: 3 AND (1u) + 2 XOR (3.6u) = 4.6u? Actually: L1 3 AND, L2 2 XOR, L3 1 XOR.
    # Per stage: 3*1.0 + 3*1.8? No. Let's count: 3 AND gates (L1), then XOR tree for 4 inputs (3 AND outs + 1 linear).
    # XOR4 = 2 levels. So per stage: 1 (AND) + 2 (XOR) = 3 levels. 1.0 + 3.6 = 4.6u.
    # Two stages: 9.2u. Plus XIG 1.8u = 11.0u. OVER!
    print("Estimated cost: 11.0u (OVER BUDGET)")
