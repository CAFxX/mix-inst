#!/usr/bin/env python3
"""Random search over cascaded-S-box skeletons.
Skeletons:
  A: [t3, t3, sboxL(a,b), sboxL(c,d)]          (front + 2 sbox layers)
  B: [sboxL(a,b), sboxL(c,d), sboxL(e,f)]      (pure sbox cascade)
  C: [t3, sboxL(a,b), sboxL(c,d)]              (weak front + 2 sbox)
Search at logN=14 (fast), report top hits for logN=16 verify.
"""
import random
import sys

sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat')
from s2proxy_v3 import s2proxy_v3, cost_est, set_sbox, T3A, T3B


def rand_L(rng):
    a = rng.randrange(1, 64)
    b = rng.randrange(1, 64)
    while b == a:
        b = rng.randrange(1, 64)
    return (a, b)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    sb = sys.argv[3] if len(sys.argv) > 3 else 'SKINNY'
    set_sbox(sb)
    print(f"# sbox={sb} n={n} seed={seed}", flush=True)
    rng = random.Random(seed)
    cands = []
    for i in range(n):
        kind = rng.choice(['A', 'A', 'B', 'C'])
        if kind == 'A':
            l1, l2 = rand_L(rng), rand_L(rng)
            st = [T3A, T3B, ('sboxL',) + l1, ('sboxL',) + l2]
        elif kind == 'B':
            l1, l2, l3 = rand_L(rng), rand_L(rng), rand_L(rng)
            st = [('sboxL',) + l1, ('sboxL',) + l2, ('sboxL',) + l3]
        else:
            l1, l2 = rand_L(rng), rand_L(rng)
            st = [T3A, ('sboxL',) + l1, ('sboxL',) + l2]
        cands.append((kind, st))
    results = []
    for kind, st in cands:
        z, d, b = s2proxy_v3(st, logN=14)
        ce = cost_est(st)
        results.append((z, kind, st, ce, d, b))
        print(f"z={z:7.1f} {kind} est={ce:.2f}u "
              f"{[(s[0], s[1:]) for s in st]}", flush=True)
    results.sort()
    print("\n# TOP 8 by z:", flush=True)
    for z, kind, st, ce, d, b in results[:8]:
        print(f"z={z:7.1f} {kind} est={ce:.2f}u d0={d:#x} "
              f"{[(s[0], s[1:]) for s in st]}", flush=True)


if __name__ == '__main__':
    main()
