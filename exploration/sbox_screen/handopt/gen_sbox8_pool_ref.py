#!/usr/bin/env python3
"""Generate the 8-bit S-box pool for the next broad screen (track-2, v2).

All tables are GENERATED from first principles (GF(2^8) arithmetic), never
recalled from memory. Deterministic (fixed seeds); re-running reproduces
the pool file byte-identically.

Pool axes (each justified in POOL_DESIGN.md):
  A1  AES_SBOX / AES_SBOX_INV : GF(2^8) inversion + AES affine (FIPS 197).
      Reference strong boxes (DU=4, NL=112). Generated, then verified
      against the standard fingerprints (DU/NL/degree + known values
      S[0x00]=0x63, S[0x53]=0xed, S[0xFF]=0x16; inverse consistency).
  A2  POW8_d : power maps x -> x^d over GF(2^8), d odd with gcd(d,255)=1
      (permutations), filtered to DU <= 8 and NL >= 96. The inversion map
      (d=254) is the AES class; other d give affine-inequivalent classes.
  A3  AFF8_k : random affine-equivalent variants of the AES S-box,
      S'(x) = L2(AES(L1(x))), L1/L2 random invertible affine maps
      (seeded). Same (DU,NL,degree) as AES by construction; different
      circuits -> the screen measures cost variation inside the class,
      mirroring the 4-bit 4096-variant scheme.

Output: pools/sbox8_pool.txt, one row per box:
    NAME <256 space-separated hex bytes>

Usage: python3 gen_sbox8_pool.py [--out pools/sbox8_pool.txt]
"""
import argparse
import math
import os
import random
import sys

import numpy as np

# ---------------------------------------------------------------- GF(2^8)
# AES irreducible polynomial: x^8 + x^4 + x^3 + x + 1 = 0x11B
_POLY = 0x11B


def gf_mul(a, b):
    p = 0
    while b:
        if b & 1:
            p ^= a
        a <<= 1
        if a & 0x100:
            a ^= _POLY
        b >>= 1
    return p & 0xFF


def gf_pow(a, e):
    r = 1
    while e:
        if e & 1:
            r = gf_mul(r, a)
        a = gf_mul(a, a)
        e >>= 1
    return r


def gf_inv(a):
    return 0 if a == 0 else gf_pow(a, 254)


# AES affine transform (FIPS 197, x0 = LSB):
#   y = M . x XOR 0x63, M circulant-ish per the FIPS matrix.
def _aes_affine(x):
    # y_i = x_i ^ x_{i+4} ^ x_{i+5} ^ x_{i+6} ^ x_{i+7} ^ c_i, c=0x63
    c = 0x63
    y = 0
    for i in range(8):
        bit = ((x >> i) & 1) ^ ((x >> ((i + 4) % 8)) & 1) ^ \
              ((x >> ((i + 5) % 8)) & 1) ^ ((x >> ((i + 6) % 8)) & 1) ^ \
              ((x >> ((i + 7) % 8)) & 1) ^ ((c >> i) & 1)
        y |= bit << i
    return y


def aes_sbox():
    return [_aes_affine(gf_inv(x)) for x in range(256)]


def invert_table(tab):
    inv = [0] * 256
    for x, y in enumerate(tab):
        inv[y] = x
    return inv


# ------------------------------------------------- DU / NL via numpy
def du_of(tab):
    t = np.asarray(tab, dtype=np.uint8)
    xs = np.arange(256, dtype=np.uint8)
    du = 0
    for a in range(1, 256):
        diffs = t[xs] ^ t[xs ^ np.uint8(a)]
        c = np.bincount(diffs, minlength=256)
        m = int(c.max())
        if m > du:
            du = m
    return du


def _fwht(a):
    h = 1
    n = len(a)
    a = a.astype(np.int32)
    while h < n:
        for i in range(0, n, h * 2):
            x = a[i:i + h].copy()
            y = a[i + h:i + 2 * h]
            a[i:i + h] = x + y
            a[i + h:i + 2 * h] = x - y
        h *= 2
    return a


def nl_of(tab):
    t = np.asarray(tab, dtype=np.uint8)
    xs = np.arange(256, dtype=np.uint8)
    worst = 0
    for b in range(1, 256):
        # f(x) = parity(b & S(x)); g = (-1)^f
        fb = np.bitwise_and.outer(np.asarray([b], dtype=np.uint8), t)[0]
        par = np.unpackbits(fb).reshape(256, 8).sum(axis=1) & 1
        g = np.where(par == 0, 1, -1)
        w = _fwht(g)
        m = int(np.abs(w).max())
        if m > worst:
            worst = m
    return 128 - worst // 2


def anf_degree(tab, bit):
    f = np.array([(tab[x] >> bit) & 1 for x in range(256)], dtype=np.uint8)
    a = f.copy()
    n = 8
    size = 256
    for i in range(n):
        step = 1 << i
        for mask in range(size):
            if mask & step:
                a[mask] ^= a[mask ^ step]
    deg = 0
    for mask in range(size):
        if a[mask]:
            d = bin(mask).count("1")
            if d > deg:
                deg = d
    return deg


# ------------------------------------------------- random affine maps
def _rand_invertible_matrix(rng):
    while True:
        m = [[rng.getrandbits(1) for _ in range(8)] for _ in range(8)]
        # Gaussian elimination over GF(2) for rank
        rows = []
        for r in m:
            v = 0
            for j, b in enumerate(r):
                v |= b << j
            rows.append(v)
        rank = 0
        for col in range(8):
            piv = None
            for r in range(rank, 8):
                if (rows[r] >> col) & 1:
                    piv = r
                    break
            if piv is None:
                continue
            rows[rank], rows[piv] = rows[piv], rows[rank]
            for r in range(8):
                if r != rank and ((rows[r] >> col) & 1):
                    rows[r] ^= rows[rank]
            rank += 1
        if rank == 8:
            return m


def _apply_affine(x, m, c):
    y = c
    for i in range(8):
        if (x >> i) & 1:
            col = 0
            for r in range(8):
                col |= (m[r][i] << r)
            y ^= col
    return y & 0xFF


def affine_variant(tab, rng):
    m1 = _rand_invertible_matrix(rng)
    c1 = rng.getrandbits(8)
    m2 = _rand_invertible_matrix(rng)
    c2 = rng.getrandbits(8)
    return [_apply_affine(tab[_apply_affine(x, m1, c1)], m2, c2)
            for x in range(256)]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "sbox8_pool.txt"))
    ap.add_argument("--n-affine", type=int, default=16)
    ap.add_argument("--seed", type=int, default=0x5B08)
    a = ap.parse_args()

    pool = []  # (name, table)

    # A1: AES + inverse (generated)
    aes = aes_sbox()
    assert aes[0x00] == 0x63, f"AES S[0]={aes[0]:02x}, expected 63"
    assert aes[0x53] == 0xED, f"AES S[0x53]={aes[0x53]:02x}, expected ed"
    assert aes[0xFF] == 0x16, f"AES S[0xff]={aes[0xff]:02x}, expected 16"
    assert sorted(aes) == list(range(256)), "AES not bijective"
    assert du_of(aes) == 4, f"AES DU={du_of(aes)}, expected 4"
    assert nl_of(aes) == 112, f"AES NL={nl_of(aes)}, expected 112"
    assert all(anf_degree(aes, b) == 7 for b in range(8)), "AES degree != 7"
    pool.append(("AES_SBOX", aes))
    aes_inv = invert_table(aes)
    assert all(aes[aes_inv[x]] == x for x in range(256))
    pool.append(("AES_SBOX_INV", aes_inv))
    print(f"A1: AES_SBOX du=4 nl=112 deg=7 OK; AES_SBOX_INV OK", flush=True)

    # A2: power maps x^d, permutations with DU <= 8, NL >= 96
    for d in range(3, 256, 2):
        if math.gcd(d, 255) != 1:
            continue
        tab = [gf_pow(x, d) for x in range(256)]
        assert sorted(tab) == list(range(256))
        du = du_of(tab)
        if du > 8:
            continue
        nl = nl_of(tab)
        if nl < 96:
            continue
        pool.append((f"POW8_{d}", tab))
        print(f"A2: POW8_{d} du={du} nl={nl}", flush=True)

    # A3: random affine variants of AES (seeded)
    rng = random.Random(a.seed)
    for k in range(a.n_affine):
        v = affine_variant(aes, rng)
        assert sorted(v) == list(range(256))
        assert du_of(v) == 4 and nl_of(v) == 112
        pool.append((f"AFF8_{k:02d}", v))
    print(f"A3: {a.n_affine} affine AES-class variants du=4 nl=112 OK",
          flush=True)

    with open(a.out, "w") as f:
        f.write("# 8-bit S-box pool v2 (track-2 next broad screen)\n")
        f.write("# Generated by pools/gen_sbox8_pool.py -- DO NOT hand-edit; "
                "re-run the generator.\n")
        f.write(f"# seed={a.seed:#x} n_affine={a.n_affine}\n")
        for name, tab in pool:
            f.write(name + " " + " ".join(f"{v:02x}" for v in tab) + "\n")
    print(f"wrote {a.out}: {len(pool)} boxes", flush=True)


if __name__ == "__main__":
    main()
