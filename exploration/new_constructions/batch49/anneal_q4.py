#!/usr/bin/env python3
"""Batch-49: heuristic search for bijective QUADRATIC 4-bit S-boxes.

State: 44-bit quadratic ANF (per output bit: 1 const + 4 linear + 6 quad).
Energy = 64*collisions + DU + LATbias/8. Multi-start simulated annealing.
Goal: bijective, all components degree exactly 2, min (DU, LATbias).
"""
import random
import sys

N = 16
# parameter layout per output bit: [const, l0..l3, q01,q02,q03,q12,q13,q23]
QPAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
NB = 11


def build(params):
    s = []
    for x in range(N):
        v = 0
        b = [(x >> i) & 1 for i in range(4)]
        for o in range(4):
            p = params[o * NB:(o + 1) * NB]
            y = p[0]
            for i in range(4):
                y ^= p[1 + i] & b[i]
            for k, (i, j) in enumerate(QPAIRS):
                y ^= p[5 + k] & b[i] & b[j]
            v |= (y << o)
        s.append(v)
    return s


def profile(s):
    coll = N - len(set(s))
    # DDT / DU
    du = 0
    for din in range(1, N):
        cnt = [0] * N
        for x in range(N):
            cnt[s[x] ^ s[x ^ din]] += 1
        du = max(du, max(cnt))
    # LAT max bias
    lb = 0
    for mi in range(1, N):
        for mo in range(1, N):
            c = 0
            for x in range(N):
                if (bin(x & mi).count('1') + bin(s[x] & mo).count('1')) & 1 == 0:
                    c += 1
            b_ = abs(c - 8)
            if b_ > lb:
                lb = b_
    return coll, du, lb


def energy(s):
    coll, du, lb = profile(s)
    return 64 * coll + du + lb / 8.0, (coll, du, lb)


def comp_degrees(s):
    degs = set()
    for mask in range(1, N):
        f = [0] * N
        for x in range(N):
            v = 0
            for o in range(4):
                if (mask >> o) & 1 and (s[x] >> o) & 1:
                    v ^= 1
            f[x] = v
        a = f[:]
        for i in range(4):
            for x in range(N):
                if x & (1 << i):
                    a[x] ^= a[x ^ (1 << i)]
        degs.add(max(bin(x).count('1') for x, c in enumerate(a) if c))
    return sorted(degs)


def anneal(seed, steps=60000):
    rng = random.Random(seed)
    params = [rng.getrandbits(1) for _ in range(4 * NB)]
    s = build(params)
    e, prof = energy(s)
    best = (e, params[:], prof, s[:])
    T0, T1 = 8.0, 0.05
    for t in range(steps):
        T = T0 * (T1 / T0) ** (t / steps)
        i = rng.randrange(len(params))
        params[i] ^= 1
        s2 = build(params)
        e2, prof2 = energy(s2)
        if e2 < e or rng.random() < 2.718281828 ** ((e - e2) / T):
            e, prof, s = e2, prof2, s2
            if e2 < best[0]:
                best = (e2, params[:], prof2, s2[:])
        else:
            params[i] ^= 1
    return best


def main():
    nstart = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    results = []
    for k in range(nstart):
        e, params, prof, s = anneal(0xB492 + k)
        results.append((e, prof, s))
        print("start %d: energy=%.3f coll=%d DU=%d LATbias=%d compdeg=%s S0=%d" %
              (k, e, prof[0], prof[1], prof[2], comp_degrees(s), s[0]), flush=True)
    results.sort(key=lambda r: (r[1][0], r[1][1], r[1][2]))
    e, prof, s = results[0]
    print("BEST coll=%d DU=%d LATbias=%d compdeg=%s" %
          (prof[0], prof[1], prof[2], comp_degrees(s)))
    print("BEST_LUT=[%s]" % ",".join(str(v) for v in s))


if __name__ == "__main__":
    main()
