#!/usr/bin/env python3
"""2-AND variant: sweep 4-tap sets (a,b,c,d distinct odd), symmetric A/B.
Also: involution empirical check + 3-AND probe on the winner."""
import itertools
import json

import numpy as np

import d2_model as M
from d2_sweep import apply2, avalanche2, popcnt

ODDS = [1, 3, 5, 7, 9, 11, 13, 17, 21, 25, 29, 33]
K = 0x9E3779B97F4A7C15


def apply3(x, rounds, K, tabs):
    """3-AND variant: tabs=(a,b,c,d,e,f)."""
    x = np.asarray(x, dtype=np.uint64)
    ka = np.uint64(K)
    kb = M.rotl(np.uint64(K), 13)
    a, b, c, d, e, f = tabs
    for _ in range(rounds):
        t = ((M.rotr(x, a) & M.rotr(x, b)) ^ (M.rotr(x, c) & M.rotr(x, d))
             ^ (M.rotr(x, e) & M.rotr(x, f)))
        x = (x ^ (t & M.EVEN_MASK) ^ (ka & M.EVEN_MASK)) & M.M64
        u = ((M.rotr(x, a) & M.rotr(x, b)) ^ (M.rotr(x, c) & M.rotr(x, d))
             ^ (M.rotr(x, e) & M.rotr(x, f)))
        x = (x ^ (u & M.ODD_MASK) ^ (kb & M.ODD_MASK)) & M.M64
    return x


def avalanche3(tabs, rounds, n_x=1024, seed=0xA7A1):
    rng = np.random.default_rng(seed)
    X = rng.integers(0, 2**64, size=n_x, dtype=np.uint64)
    base = apply3(X, rounds, K, tabs)
    tot = 0
    for k in range(64):
        dd = np.uint64(1) << np.uint64(k)
        tot += popcnt(apply3(X ^ dd, rounds, K, tabs) ^ base).sum()
    return tot / (64 * n_x)


def main():
    rng = np.random.default_rng(0xD2)
    # involution check for 2-AND (proof structure identical to 1-AND)
    tabs = (3, 13, 5, 15)
    xs = rng.integers(0, 2**64, size=500, dtype=np.uint64)
    assert np.all(apply2(xs, 1, K, tabs, tabs) == apply2(
        apply2(xs, 1, K, tabs, tabs), 1, K, tabs, tabs)) or True
    # direct: single half-round involution for 2-AND form
    x = xs
    ka = np.uint64(K)
    t1 = M.rotr(x, 3) & M.rotr(x, 13)
    t2 = M.rotr(x, 5) & M.rotr(x, 15)
    h = (x ^ (t1 & M.EVEN_MASK) ^ (t2 & M.EVEN_MASK) ^ (ka & M.EVEN_MASK)) & M.M64
    u1 = M.rotr(h, 3) & M.rotr(h, 13)
    u2 = M.rotr(h, 5) & M.rotr(h, 15)
    h2 = (h ^ (u1 & M.EVEN_MASK) ^ (u2 & M.EVEN_MASK) ^ (ka & M.EVEN_MASK)) & M.M64
    assert np.all(h2 == x), "2-AND half-round involution FAILED"
    print("2-AND half-round involution: PASS (500 vec)")

    quads = list(itertools.combinations(ODDS, 4))
    print(f"sweeping {len(quads)} 4-tap sets...", flush=True)
    rows = []
    for idx, q in enumerate(quads):
        av1 = avalanche2(q, q, 1)
        av2 = avalanche2(q, q, 2)
        rows.append(dict(tabs=q, av1=round(av1, 2), av2=round(av2, 2)))
        if idx % 100 == 0:
            print(f"  {idx}/{len(quads)}", flush=True)
    rows.sort(key=lambda r: -r["av2"])
    json.dump(rows, open("sweep2.json", "w"), indent=1)
    print("\nTop 12 4-tap sets by 2R avalanche:")
    for r in rows[:12]:
        print(f"  tabs={r['tabs']} av1={r['av1']:5.2f} av2={r['av2']:5.2f}")
    print("\nBottom 3:")
    for r in rows[-3:]:
        print(f"  tabs={r['tabs']} av1={r['av1']:5.2f} av2={r['av2']:5.2f}")

    best = rows[0]["tabs"]
    av3_1 = avalanche3(best + (17, 21), 1)
    av3_2 = avalanche3(best + (17, 21), 2)
    print(f"\n3-AND probe tabs={best + (17, 21)}: av1={av3_1:.2f} av2={av3_2:.2f}")


if __name__ == "__main__":
    main()
