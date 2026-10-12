#!/usr/bin/env python3
"""Direction 2: bit-level Feistel model.

Alternating-halves construction (DESIGN.md section 2):
  half-round A: y[2i]   = x[2i] ^ (x[2i+a] & x[2i+b]) ^ ka[2i]; y[2i+1] = x[2i+1]
  half-round B: z[2i+1] = y[2i+1] ^ (y[2i+1+c] & y[2i+1+d]) ^ kb[2i+1]; z[2i] = y[2i]
Key schedule: ka = K (evens), kb = rotl(K,13) (odds), same every round.
Bijective per fixed K by the half-split involution proof (DESIGN.md).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
EVEN_MASK = np.uint64(0x5555555555555555)  # bits 0,2,4,...
ODD_MASK = np.uint64(0xAAAAAAAAAAAAAAAA)  # bits 1,3,5,...


def rotl(x, r):
    r %= 64
    if r == 0:
        return x & M64
    x = np.asarray(x, dtype=np.uint64)
    return (((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64)


def rotr(x, r):
    return rotl(x, -r % 64)


def halfA(x, a, b, ka):
    """Even update. a,b must be odd."""
    assert a % 2 == 1 and b % 2 == 1
    x = np.asarray(x, dtype=np.uint64)
    taps = rotr(x, a) & rotr(x, b)  # bit i = x[i+a] & x[i+b]
    return (x ^ (taps & EVEN_MASK) ^ (np.uint64(ka) & EVEN_MASK)) & M64


def halfB(y, c, d, kb):
    """Odd update. c,d must be odd."""
    assert c % 2 == 1 and d % 2 == 1
    y = np.asarray(y, dtype=np.uint64)
    taps = rotr(y, c) & rotr(y, d)
    return (y ^ (taps & ODD_MASK) ^ (np.uint64(kb) & ODD_MASK)) & M64


def full_round(x, ab, cd, K):
    ka = np.uint64(K)
    kb = rotl(np.uint64(K), 13)
    return halfB(halfA(x, ab[0], ab[1], ka), cd[0], cd[1], kb)


def apply(x, rounds, K, ab=(1, 3), cd=None):
    """rounds = number of full rounds. ab=(a,b) taps for A, cd=(c,d) for B."""
    if cd is None:
        cd = ab
    x = np.asarray(x, dtype=np.uint64)
    for _ in range(rounds):
        x = full_round(x, ab, cd, K)
    return x


# ---------------------------------------------------------------------------
# Scalar bit-level reference (independent implementation for XCHECK)
# ---------------------------------------------------------------------------
def _bits(w, n=64):
    return [(w >> i) & 1 for i in range(n)]


def apply_scalar(x, rounds, K, ab=(1, 3), cd=None, n=64):
    if cd is None:
        cd = ab
    a, b = ab
    c, d = cd
    ka = K & ((1 << n) - 1)
    kb = 0
    K13 = 0
    kk = K
    for _ in range(13):  # rotl by 13 at width n
        kk = ((kk << 1) | (kk >> (n - 1))) & ((1 << n) - 1)
    K13 = kk
    xb = _bits(x, n)
    for _ in range(rounds):
        yb = [0] * n
        for i in range(0, n, 2):
            tap = xb[(i + a) % n] & xb[(i + b) % n]
            yb[i] = xb[i] ^ tap ^ ((ka >> i) & 1)
            yb[i + 1] = xb[i + 1]
        zb = [0] * n
        for i in range(0, n, 2):
            zb[i] = yb[i]
            tap = yb[(i + 1 + c) % n] & yb[(i + 1 + d) % n]
            zb[i + 1] = yb[i + 1] ^ tap ^ ((K13 >> (i + 1)) & 1)
        xb = zb
    return sum(v << i for i, v in enumerate(xb))


# ---------------------------------------------------------------------------
# Naive cyclic form: collision check (DESIGN.md section 1 evidence)
# ---------------------------------------------------------------------------
def naive_scalar(x, a, b, n=8):
    xb = _bits(x, n)
    yb = [xb[i] ^ (xb[(i + a) % n] & xb[(i + b) % n]) for i in range(n)]
    return sum(v << i for i, v in enumerate(yb))


def naive_collides(n, a, b):
    seen = {}
    for x in range(1 << n):
        y = naive_scalar(x, a, b, n)
        if y in seen:
            return True, (seen[y], x, y)
        seen[y] = x
    return False, None


# ---------------------------------------------------------------------------
# Dependency cones (exact, as Python int bitmasks)
# ---------------------------------------------------------------------------
def cones(rounds, ab=(1, 3), cd=None, n=64):
    if cd is None:
        cd = ab
    a, b = ab
    c, d = cd
    cone = [1 << j for j in range(n)]

    def halfA_c(cn):
        new = [0] * n
        for i in range(0, n, 2):
            new[i] = cn[i] | cn[(i + a) % n] | cn[(i + b) % n]
            new[i + 1] = cn[i + 1]
        return new

    def halfB_c(cn):
        new = [0] * n
        for i in range(0, n, 2):
            new[i] = cn[i]
            new[i + 1] = cn[i + 1] | cn[(i + 1 + c) % n] | cn[(i + 1 + d) % n]
        return new

    for _ in range(rounds):
        cone = halfB_c(halfA_c(cone))
    return [bin(v).count("1") for v in cone]


def selftest():
    rng = np.random.default_rng(0xD2)
    # 1. vectorized == scalar on random vectors, several tap sets
    for ab in [(1, 3), (1, 33), (7, 25), (13, 17)]:
        xs = rng.integers(0, 2**64, size=50, dtype=np.uint64)
        K = int(rng.integers(0, 2**64, dtype=np.uint64))
        for r in (1, 2, 3):
            v = apply(xs, r, K, ab)
            for x, yv in zip(xs, v):
                ys = apply_scalar(int(x), r, K, ab)
                assert int(yv) == ys, (ab, r, hex(int(x)), hex(int(yv)), hex(ys))
    # 2. involution of each half-round (DESIGN.md theorem, empirical check)
    for a, b in [(1, 3), (5, 27)]:
        xs = rng.integers(0, 2**64, size=200, dtype=np.uint64)
        ka = int(rng.integers(0, 2**64, dtype=np.uint64))
        assert np.all(halfA(halfA(xs, a, b, ka), a, b, ka) == xs)
        assert np.all(halfB(halfB(xs, a, b, ka), a, b, ka) == xs)
    # 3. full cipher bijective on a sample (no collisions over 20k random inputs)
    xs = rng.integers(0, 2**64, size=20000, dtype=np.uint64)
    ys = apply(xs, 2, 0xDEADBEEFDEADBEEF, (1, 3))
    assert len(set(int(y) for y in ys)) == 20000
    print("SELFTEST PASS: vec==scalar, half-round involution, 20k-collision-free")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
    elif len(sys.argv) > 1 and sys.argv[1] == "naive":
        n, a, b = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        hit, ex = naive_collides(n, a, b)
        print(f"naive w={n} a={a} b={b}: collides={hit} example={ex}")
    else:
        print("usage: d2_model.py selftest | naive <w> <a> <b>")
