#!/usr/bin/env python3
"""Sweep odd (a,b) tap offsets: exact dependency cones + sampled avalanche.
Also evaluates the 2-AND-per-bit variant on the top candidates.
"""
import itertools
import json
import sys

import numpy as np

import d2_model as M

ODDS = [1, 3, 5, 7, 9, 11, 13, 17, 21, 25, 29, 33]
K = 0x9E3779B97F4A7C15


def popcnt(a):
    b = np.asarray(a, dtype=np.uint64).view(np.uint8).reshape(-1, 8)
    return np.unpackbits(b, axis=1).sum(axis=1)


def avalanche(ab, rounds, n_x=1024, seed=0xA7A1):
    rng = np.random.default_rng(seed)
    X = rng.integers(0, 2**64, size=n_x, dtype=np.uint64)
    base = M.apply(X, rounds, K, ab)
    tot = 0
    for k in range(64):
        d = np.uint64(1) << np.uint64(k)
        tot += popcnt(M.apply(X ^ d, rounds, K, ab) ^ base).sum()
    return tot / (64 * n_x)


def halfA2(x, a, b, c, d, ka):
    x = np.asarray(x, dtype=np.uint64)
    t1 = M.rotr(x, a) & M.rotr(x, b)
    t2 = M.rotr(x, c) & M.rotr(x, d)
    return (x ^ (t1 & M.EVEN_MASK) ^ (t2 & M.EVEN_MASK)
            ^ (np.uint64(ka) & M.EVEN_MASK)) & M.M64


def apply2(x, rounds, K, tabs, cdtabs):
    """2-AND variant: tabs=(a,b,c,d) for A, cdtabs=(e,f,g,h) for B."""
    x = np.asarray(x, dtype=np.uint64)
    ka = np.uint64(K)
    kb = M.rotl(np.uint64(K), 13)
    a, b, c, d = tabs
    e, f, g, h = cdtabs
    for _ in range(rounds):
        t1 = M.rotr(x, a) & M.rotr(x, b)
        t2 = M.rotr(x, c) & M.rotr(x, d)
        x = (x ^ (t1 & M.EVEN_MASK) ^ (t2 & M.EVEN_MASK)
             ^ (ka & M.EVEN_MASK)) & M.M64
        u1 = M.rotr(x, e) & M.rotr(x, f)
        u2 = M.rotr(x, g) & M.rotr(x, h)
        x = (x ^ (u1 & M.ODD_MASK) ^ (u2 & M.ODD_MASK)
             ^ (kb & M.ODD_MASK)) & M.M64
    return x


def avalanche2(tabs, cdtabs, rounds, n_x=1024, seed=0xA7A1):
    rng = np.random.default_rng(seed)
    X = rng.integers(0, 2**64, size=n_x, dtype=np.uint64)
    base = apply2(X, rounds, K, tabs, cdtabs)
    tot = 0
    for k in range(64):
        dd = np.uint64(1) << np.uint64(k)
        tot += popcnt(apply2(X ^ dd, rounds, K, tabs, cdtabs) ^ base).sum()
    return tot / (64 * n_x)


def main():
    rows = []
    pairs = [(a, b) for a in ODDS for b in ODDS if a != b]
    print(f"sweeping {len(pairs)} (a,b) pairs...", flush=True)
    for idx, (a, b) in enumerate(pairs):
        ab = (a, b)
        c1 = M.cones(1, ab)
        c2 = M.cones(2, ab)
        av1 = avalanche(ab, 1)
        av2 = avalanche(ab, 2)
        rows.append(dict(a=a, b=b, cone1_min=min(c1), cone1_mean=round(sum(c1)/64, 2),
                          cone2_min=min(c2), cone2_mean=round(sum(c2)/64, 2),
                          av1=round(av1, 2), av2=round(av2, 2)))
        if idx % 20 == 0:
            print(f"  {idx}/{len(pairs)}", flush=True)
    rows.sort(key=lambda r: -r["av2"])
    json.dump(rows, open("sweep1.json", "w"), indent=1)
    print("\nTop 15 by 2R avalanche:")
    for r in rows[:15]:
        print(f"  a={r['a']:3d} b={r['b']:3d} av1={r['av1']:5.2f} av2={r['av2']:5.2f} "
              f"cone2min={r['cone2_min']:3d} cone2mean={r['cone2_mean']:5.2f}")
    print("\nBottom 5:")
    for r in rows[-5:]:
        print(f"  a={r['a']:3d} b={r['b']:3d} av1={r['av1']:5.2f} av2={r['av2']:5.2f}")

    # 2-AND variant on top candidates: tabs=(a,b,c,d), B uses same
    print("\n2-AND variant (top single-AND tap sets, doubled):")
    for r in rows[:6]:
        a, b = r["a"], r["b"]
        # second AND pair: rotate the tap set by +2 positions mod 64 (keeps odd)
        c, d = (a + 2) % 64 or 1, (b + 2) % 64 or 1
        if c % 2 == 0:
            c = (c + 1) % 64
        if d % 2 == 0:
            d = (d + 1) % 64
        tabs = (a, b, c, d)
        av1 = avalanche2(tabs, tabs, 1)
        av2 = avalanche2(tabs, tabs, 2)
        print(f"  tabs={tabs} av1={av1:.2f} av2={av2:.2f}")


if __name__ == "__main__":
    main()
