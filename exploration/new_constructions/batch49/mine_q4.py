#!/usr/bin/env python3
"""Batch-49 S-box mining: bijective QUADRATIC 4-bit S-boxes with DU/LAT
profile + no-zero-corner (S(0)!=0). Verify, don't assume: DU/LAT computed
from full DDT/LAT tables.

Construction (guaranteed bijective): triangular quadratic core
  y3 = x3
  y2 = x2 + q2(x3)            (q2: quadratic in x3 -> linear; allow)
  y1 = x1 + q1(x2,x3)         (q1: any quadratic in x2,x3)
  y0 = x0 + q0(x1,x2,x3)      (q0: any quadratic in x1,x2,x3)
then random invertible input/output affine maps A_out(Q(A_in(x))).
DU/LAT are affine-invariant, so the profile is set by (q2,q1,q0); the
affine maps + output XOR spread the class representative and fix
S(0)!=0 (no-zero-corner co-design). Filter: all 15 nonzero components
have algebraic degree exactly 2 (dense-quadratic stage property).
"""
import itertools
import random
import sys

N = 16


def apply_affine(x, mat, c):
    # mat: 4x4 over GF(2) as rows of 4-bit masks; y[i] = parity(x & mat[i]) ^ c[i]
    y = 0
    for i in range(4):
        if (bin(x & mat[i]).count('1') + ((c >> i) & 1)) & 1:
            y |= 1 << i
    return y


def rand_invertible_mat(rng):
    while True:
        m = [rng.getrandbits(4) for _ in range(4)]
        # rank check via elimination
        rows = m[:]
        r = 0
        for col in range(4):
            piv = next((k for k in range(r, 4) if (rows[k] >> col) & 1), None)
            if piv is None:
                break
            rows[r], rows[piv] = rows[piv], rows[r]
            for k in range(4):
                if k != r and (rows[k] >> col) & 1:
                    rows[k] ^= rows[r]
            r += 1
        if r == 4:
            return m


def core_sbox(q2m, q1m, q0m):
    # q2m: bit0 -> x3^2(=x3, linear); q1m: 3 bits for x2^2,x2x3,x3^2;
    # q0m: 6 bits for x1^2,x1x2,x1x3,x2^2,x2x3,x3^2 (x_i^2 = x_i linear)
    def quadval(bits, vals):
        # vals: list of (i,j) pairs with linear note
        v = 0
        for b, (i, j, lin) in zip(bits, vals):
            if b:
                v ^= lin  # placeholder; real eval below
        return v
    s = []
    for x in range(N):
        b = [(x >> i) & 1 for i in range(4)]
        # y3
        y3 = b[3]
        # y2 = x2 + q2(x3): only monomial x3^2 = x3
        y2 = b[2] ^ (b[3] if (q2m & 1) else 0)
        # y1 = x1 + q1(x2,x3): monomials x2^2=x2, x2x3, x3^2=x3
        q1 = ((b[2] if (q1m & 1) else 0) ^ (b[2] & b[3] if (q1m & 2) else 0)
              ^ (b[3] if (q1m & 4) else 0))
        y1 = b[1] ^ q1
        # y0 = x0 + q0(x1,x2,x3): x1^2=x1,x1x2,x1x3,x2^2=x2,x2x3,x3^2=x3
        q0 = ((b[1] if (q0m & 1) else 0) ^ (b[1] & b[2] if (q0m & 2) else 0)
              ^ (b[1] & b[3] if (q0m & 4) else 0) ^ (b[2] if (q0m & 8) else 0)
              ^ (b[2] & b[3] if (q0m & 16) else 0) ^ (b[3] if (q0m & 32) else 0))
        y0 = b[0] ^ q0
        s.append(y0 | (y1 << 1) | (y2 << 2) | (y3 << 3))
    return s


def comp_degree(s, mask):
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
    return max(bin(x).count('1') for x, c in enumerate(a) if c)


def ddt_du(s):
    du = 0
    for din in range(1, N):
        cnt = {}
        for x in range(N):
            d = s[x] ^ s[x ^ din]
            cnt[d] = cnt.get(d, 0) + 1
        du = max(du, max(cnt.values()))
    return du


def lat_maxbias(s):
    worst = 0
    for mi in range(1, N):
        for mo in range(1, N):
            c = sum(1 for x in range(N)
                    if (bin(x & mi).count('1') + bin(s[x] & mo).count('1')) % 2 == 0)
            worst = max(worst, abs(c - 8))
    return worst


def main():
    # Exhaust the triangular core space: q2m in 0..1, q1m in 0..7, q0m in 0..63
    # -> 1024 cores. Profile each (affine-invariant), keep best (DU, LAT).
    best = []
    for q2m in range(2):
        for q1m in range(8):
            for q0m in range(64):
                s = core_sbox(q2m, q1m, q0m)
                assert len(set(s)) == N, "triangular core must be bijective"
                du = ddt_du(s)
                lb = lat_maxbias(s)
                best.append((du, lb, q2m, q1m, q0m))
    best.sort()
    print("core classes: %d; best profiles:" % len(best))
    for du, lb, q2m, q1m, q0m in best[:8]:
        print("  DU=%d LATbias=%d core=(%d,%d,%d)" % (du, lb, q2m, q1m, q0m))
    du, lb, q2m, q1m, q0m = best[0]
    core = core_sbox(q2m, q1m, q0m)
    # Instantiate: random affines + output XOR to fix S(0)!=0 and dense components
    rng = random.Random(0xB491)
    winner = None
    for _try in range(20000):
        mi = rand_invertible_mat(rng)
        mo = rand_invertible_mat(rng)
        ci, co = rng.getrandbits(4), rng.getrandbits(4)
        s = [apply_affine(core[apply_affine(x, mi, ci)], mo, co)
             for x in range(N)]
        assert len(set(s)) == N
        if s[0] == 0:
            continue
        if not all(comp_degree(s, m) == 2 for m in range(1, N)):
            continue
        assert ddt_du(s) == du and lat_maxbias(s) == lb  # affine invariance
        winner = s
        break
    if winner is None:
        print("INSTANTIATION-FAIL")
        sys.exit(1)
    print("WINNER_DU=%d WINNER_LATBIAS=%d core=(%d,%d,%d)" % (du, lb, q2m, q1m, q0m))
    print("WINNER_LUT=[%s]" % ",".join(str(v) for v in winner))
    print("S(0)=%d (nonzero: no zero-corner)" % winner[0])


if __name__ == "__main__":
    main()
