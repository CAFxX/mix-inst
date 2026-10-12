#!/usr/bin/env python3
"""Simulator for recursive (a^b)^(c&d) constructions. Fast bijectivity testing."""

import random
import sys

def f_4(a, b, c, d):
    """(a^b)^(c&d) — 4-input, 2-layer, NL=4."""
    return (a ^ b) ^ (c & d)

def f_3(a, b, c):
    """(a&b)^c — 3-input, 2-layer."""
    return (a & b) ^ c

def build_wiring_r1():
    """R1 wiring: maximize disjointness.
    Stage1: out[i] = f(in[i], in[i+16], in[i+32], in[i+48])
    Stage2: out[i] = f(s1[i], s1[i+4], s1[i+8], s1[i+12]) — check disjointness
    Stage3: similar.
    """
    # Stage 1: each output takes 4 inputs spaced by 16
    w1 = [(i, (i+16)%64, (i+32)%64, (i+48)%64) for i in range(64)]
    # Stage 2: take s1 outputs whose input sets are disjoint
    # s1[j] depends on {j, j+16, j+32, j+48}
    # For disjointness, need j1,j2,j3,j4 with all 16 values distinct mod 64
    # If we take j, j+1, j+2, j+3: sets are {j..j+3}, {j+16..j+19}, etc. — disjoint if we mod carefully
    # Actually {j, j+16, j+32, j+48} for j in {i, i+1, i+2, i+3}:
    # Union = {i..i+3, i+16..i+19, i+32..i+35, i+48..i+51} — 16 distinct (mod 64, if i+51 < 64 or wrap handled)
    # For i up to 63, wrap mod 64. Need to check distinctness.
    w2 = []
    for i in range(64):
        js = [(i+k)%64 for k in range(4)]
        # Verify disjoint input sets
        inputs = set()
        for j in js:
            for d in [0, 16, 32, 48]:
                inputs.add((j+d)%64)
        # If not 16 distinct, this wiring doesn't give full 16-input dependence
        w2.append(tuple(js))
    # Stage 3: similar, take s2 outputs
    w3 = []
    for i in range(64):
        js = [(i+k)%64 for k in range(4)]
        w3.append(tuple(js))
    return w1, w2, w3

def apply_r1(x, w1, w2, w3):
    """Apply 3-stage R1. x is int (64-bit). Returns int."""
    # Stage 1
    s1 = 0
    for i in range(64):
        a, b, c, d = w1[i]
        bit_a = (x >> a) & 1
        bit_b = (x >> b) & 1
        bit_c = (x >> c) & 1
        bit_d = (x >> d) & 1
        out = f_4(bit_a, bit_b, bit_c, bit_d)
        s1 |= (out << i)
    # Stage 2
    s2 = 0
    for i in range(64):
        j0, j1, j2, j3 = w2[i]
        bit_a = (s1 >> j0) & 1
        bit_b = (s1 >> j1) & 1
        bit_c = (s1 >> j2) & 1
        bit_d = (s1 >> j3) & 1
        out = f_4(bit_a, bit_b, bit_c, bit_d)
        s2 |= (out << i)
    # Stage 3
    s3 = 0
    for i in range(64):
        j0, j1, j2, j3 = w3[i]
        bit_a = (s2 >> j0) & 1
        bit_b = (s2 >> j1) & 1
        bit_c = (s2 >> j2) & 1
        bit_d = (s2 >> j3) & 1
        out = f_4(bit_a, bit_b, bit_c, bit_d)
        s3 |= (out << i)
    return s3

def test_bijectivity(apply_fn, wiring, n_pairs=1000000):
    """Test bijectivity via random pairs. Returns (is_bijective, collision_count)."""
    seen = set()
    collisions = 0
    for _ in range(n_pairs):
        x = random.getrandbits(64)
        y = apply_fn(x, *wiring)
        if y in seen:
            collisions += 1
            if collisions >= 5:
                return False, collisions
        seen.add(y)
    # Also check: if no collisions in outputs, likely bijective (but not proven)
    # For stronger test, check that distinct inputs give distinct outputs
    # (we already do this via set)
    return collisions == 0, collisions

def build_wiring_r2():
    """R2 wiring: (a&b)^c, 3 inputs per output."""
    # Stage 1: out[i] = f(in[i], in[i+21], in[i+42]) — spread out
    w1 = [(i, (i+21)%64, (i+42)%64) for i in range(64)]
    # Stage 2, 3: similar
    w2 = [((i+k)%64 for k in range(3)) for i in range(64)]
    w2 = [tuple(x) for x in w2]
    w3 = [tuple((i+k)%64 for k in range(3)) for i in range(64)]
    return w1, w2, w3

def apply_r2(x, w1, w2, w3):
    """Apply 3-stage R2 with (a&b)^c."""
    s1 = 0
    for i in range(64):
        a, b, c = w1[i]
        out = f_3((x>>a)&1, (x>>b)&1, (x>>c)&1)
        s1 |= (out << i)
    s2 = 0
    for i in range(64):
        a, b, c = w2[i]
        out = f_3((s1>>a)&1, (s1>>b)&1, (s1>>c)&1)
        s2 |= (out << i)
    s3 = 0
    for i in range(64):
        a, b, c = w3[i]
        out = f_3((s2>>a)&1, (s2>>b)&1, (s2>>c)&1)
        s3 |= (out << i)
    return s3

if __name__ == "__main__":
    random.seed(42)
    print("=== R1 Bijectivity Test ===")
    w1, w2, w3 = build_wiring_r1()
    bij, coll = test_bijectivity(apply_r1, (w1, w2, w3), n_pairs=200000)
    print(f"R1 structured wiring: bijective={bij}, collisions={coll}")

    print("\n=== R2 Bijectivity Test ===")
    w1, w2, w3 = build_wiring_r2()
    bij, coll = test_bijectivity(apply_r2, (w1, w2, w3), n_pairs=200000)
    print(f"R2 structured wiring: bijective={bij}, collisions={coll}")
