#!/usr/bin/env python3
"""Design C (bit-Feistel) reference models.

Scalar (bit-exact, parametrized by half-width w):
    F(x)[i] = (x[(i+a)%w] & x[(i+b)%w]) ^ (x[(i+c)%w] & x[(i+d)%w])
    round: (L,R) -> (R, R ^ F(L))            (swap folded into wiring)
    2 rounds, output = L2:R2.

Vectorized numpy model for the 64-bit instance (w=32):
    F(x) = (rotr32(x,a) & rotr32(x,b)) ^ (rotr32(x,c) & rotr32(x,d))
because rotr32(x,k)[i] == x[(i+k) mod 32].

Usage:
    python3 c_model.py            # bijectivity brute-force at n=8 + self-check
"""
import sys

import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)


# ------------------------------------------------------------ scalar model
def F_scalar(x, a, b, c, d, w):
    y = 0
    for i in range(w):
        t = ((((x >> ((i + a) % w)) & 1) & ((x >> ((i + b) % w)) & 1))
             ^ (((x >> ((i + c) % w)) & 1) & ((x >> ((i + d) % w)) & 1)))
        y |= t << i
    return y


def feistel_scalar(x, a, b, c, d, w):
    """True Feistel round (bijective for ANY F):

        (L1, R1) = (R ^ F(L), L)        # F-input half L passed through
        (L2, R2) = (R1 ^ F(L1), L1)

    Inversion: L = R1, R = L1 ^ F(L); L1 = R2, R1 = L2 ^ F(L1). Always works.

    NOTE: the brief's literal formulas "(L0,R0) -> (R0, R0 ^ F(L0))" are NOT
    bijective: F's input L0 does not appear in the output (for F=0 the map is
    (L0,R0) -> (R0,R0), erasing L0). The prose "L'=L, R'=R^F(L), then swap"
    gives the round above, which is the bijective one implemented here.
    """
    L = (x >> w) & ((1 << w) - 1)
    R = x & ((1 << w) - 1)
    L1, R1 = R ^ F_scalar(L, a, b, c, d, w), L
    L2, R2 = R1 ^ F_scalar(L1, a, b, c, d, w), L1
    return (L2 << w) | R2


# ------------------------------------------------------- vectorized model
def rotr32(v, k):
    v = np.asarray(v, dtype=np.uint64)
    k = k % 32
    if k == 0:
        return v & M32
    return (((v >> np.uint64(k)) | (v << np.uint64(32 - k))) & M32)


def F_vec(L, a, b, c, d):
    L = np.asarray(L, dtype=np.uint64)
    return ((rotr32(L, a) & rotr32(L, b)) ^ (rotr32(L, c) & rotr32(L, d))) & M32


def feistel_vec(x, a, b, c, d):
    x = np.asarray(x, dtype=np.uint64)
    L0 = (x >> np.uint64(32)) & M32
    R0 = x & M32
    L1 = (R0 ^ F_vec(L0, a, b, c, d)) & M32
    R1 = L0
    L2 = (R1 ^ F_vec(L1, a, b, c, d)) & M32
    R2 = L1
    return ((L2 << np.uint64(32)) | R2) & M64


# ------------------------------------------------------------- self-check
def self_check(a, b, c, d, n=4096, seed=0xC1A0):
    """Vectorized model must match the scalar model bit-exactly."""
    rng = np.random.default_rng(seed)
    X = rng.integers(0, 2**64, size=n, dtype=np.uint64)
    V = feistel_vec(X, a, b, c, d)
    S = np.array([feistel_scalar(int(x), a, b, c, d, 32) for x in X],
                 dtype=np.uint64)
    bad = int(np.sum(V != S))
    return bad


def bijective_small(a, b, c, d, w):
    """Exhaustive bijectivity check on 2w bits. Returns #collisions."""
    seen = set()
    coll = 0
    for x in range(1 << (2 * w)):
        y = feistel_scalar(x, a, b, c, d, w)
        if y in seen:
            coll += 1
        seen.add(y)
    return coll, len(seen)


def main():
    offs = [(1, 3, 5, 7), (1, 5, 9, 13), (3, 7, 11, 15)]
    w = 4  # 8-bit total: 4+4 split
    print(f"Bijectivity brute-force: 2w = {2*w} bits, {1 << (2*w)} inputs")
    allok = True
    for (a, b, c, d) in offs:
        aa, bb, cc, dd = a % w, b % w, c % w, d % w
        coll, nseen = bijective_small(aa, bb, cc, dd, w)
        ok = coll == 0 and nseen == (1 << (2 * w))
        allok &= ok
        print(f"  offsets ({a},{b},{c},{d}) mod {w} -> ({aa},{bb},{cc},{dd}): "
              f"collisions={coll} distinct={nseen} "
              f"{'BIJECTIVE' if ok else 'NOT BIJECTIVE'}")
    # extra sanity: a couple of arbitrary small offset sets (structure, not params)
    for (a, b, c, d) in [(0, 1, 2, 3), (2, 2, 1, 3)]:
        coll, nseen = bijective_small(a, b, c, d, w)
        ok = coll == 0 and nseen == (1 << (2 * w))
        allok &= ok
        print(f"  sanity  ({a},{b},{c},{d}): collisions={coll} distinct={nseen} "
              f"{'BIJECTIVE' if ok else 'NOT BIJECTIVE'}")
    print("Vectorized vs scalar self-check (64-bit):")
    for (a, b, c, d) in offs:
        bad = self_check(a, b, c, d)
        allok &= bad == 0
        print(f"  offsets ({a},{b},{c},{d}): mismatches={bad}/4096 "
              f"{'MATCH' if bad == 0 else 'MISMATCH'}")
    print("ALL OK" if allok else "FAILURES PRESENT")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
