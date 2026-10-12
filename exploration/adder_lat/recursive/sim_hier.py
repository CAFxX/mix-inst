#!/usr/bin/env python3
"""R1 with Carlo's hierarchical wiring: each Stage-3 output depends on ALL 64 inputs."""

import random

def f_4(a, b, c, d):
    """(a^b)^(c&d)"""
    return (a ^ b) ^ (c & d)

def build_hierarchical_wiring():
    """Carlo's hierarchical wiring for full 64-input coverage.
    
    Stage 1: out[i] = f(in[i], in[i+1], in[i+2], in[i+3])
    Stage 2: out[i] = f(s1[i], s1[i+16], s1[i+32], s1[i+48])
    Stage 3: out[i] = f(s2[i], s2[i+4], s2[i+8], s2[i+12])
    """
    w1 = [((i)%64, (i+1)%64, (i+2)%64, (i+3)%64) for i in range(64)]
    w2 = [((i)%64, (i+16)%64, (i+32)%64, (i+48)%64) for i in range(64)]
    w3 = [((i)%64, (i+4)%64, (i+8)%64, (i+12)%64) for i in range(64)]
    return w1, w2, w3

def compute_input_set(w1, w2, w3, out_idx):
    """Compute the set of input indices that Stage-3 output out_idx depends on."""
    # Stage 3: out depends on 4 Stage-2 outputs
    s2_indices = w3[out_idx]
    # Stage 2: each s2[j] depends on 4 Stage-1 outputs
    s1_indices = set()
    for j in s2_indices:
        for k in w2[j]:
            s1_indices.add(k)
    # Stage 1: each s1[k] depends on 4 inputs
    inputs = set()
    for k in s1_indices:
        for m in w1[k]:
            inputs.add(m)
    return inputs

def apply_r1_hier(x, w1, w2, w3):
    """Apply 3-stage R1 with hierarchical wiring. x is int."""
    s1 = 0
    for i in range(64):
        a, b, c, d = w1[i]
        out = f_4((x>>a)&1, (x>>b)&1, (x>>c)&1, (x>>d)&1)
        s1 |= (out << i)
    s2 = 0
    for i in range(64):
        j0, j1, j2, j3 = w2[i]
        out = f_4((s1>>j0)&1, (s1>>j1)&1, (s1>>j2)&1, (s1>>j3)&1)
        s2 |= (out << i)
    s3 = 0
    for i in range(64):
        j0, j1, j2, j3 = w3[i]
        out = f_4((s2>>j0)&1, (s2>>j1)&1, (s2>>j2)&1, (s2>>j3)&1)
        s3 |= (out << i)
    return s3

def test_bijectivity(n_pairs=500000):
    w1, w2, w3 = build_hierarchical_wiring()
    seen = set()
    for _ in range(n_pairs):
        x = random.getrandbits(64)
        y = apply_r1_hier(x, w1, w2, w3)
        if y in seen:
            return False
        seen.add(y)
    return True

if __name__ == "__main__":
    w1, w2, w3 = build_hierarchical_wiring()
    
    print("=== Verifying 64-input coverage (Carlo's requirement) ===")
    all_64 = True
    for i in range(64):
        inputs = compute_input_set(w1, w2, w3, i)
        if len(inputs) != 64:
            print(f"FAIL: output {i} depends on {len(inputs)} inputs, not 64")
            all_64 = False
            break
    if all_64:
        print("PASS: All 64 Stage-3 outputs depend on ALL 64 inputs.")
    
    print("\n=== Bijectivity test (500k pairs) ===")
    random.seed(123)
    bij = test_bijectivity(500000)
    print(f"Bijective (no collisions in 500k): {bij}")
