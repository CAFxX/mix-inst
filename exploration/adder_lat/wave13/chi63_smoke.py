#!/usr/bin/env python3
"""Wave-14 smoke: odd-width chi (bijective) + nonlinear cap bit, per-stage rotl.

Construction (novel-nonlinearity pivot, outside x^= space):
  stage(x): y[62:0] = chi_63(x[62:0])   # chi on odd width 63 -> BIJECTIVE
            y[63]   = x[63] ^ (x[A] & x[B])   # nonlinear cap bit, A,B in 0..62
            out     = rotl(y, r_i)            # 0-delay wiring; moves cap bit
  full: x ^= K (pre-whiten); n stages.

Why: even-width chi (al_chi6, 20.4u) S2-KILLED on deterministic trails
(ledgered 2026-10-08, max|z|~103) -- the even-width kernel. Odd-width chi
is bijective (Daemen), removing the mechanism; cost class ~3.3u/stage
(al_chi6b 19.8u/6st), so 5st ~ 17u is plausibly sub-frontier.
UNEXPLORED: odd-width chi never tried in this program.

Proxy: random-64 domain (18:12 lesson), 2^14 pairs, all 115 deltas, report
max|z| + constbits. Positive controls: (1) round-trip invertibility on
2^16 random vectors (bijectivity claim); (2) even-width chi_64 control
must show the known weak signature (validates the gate can see chi trails).
"""
import sys
import numpy as np

sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat')
import s2proxy_v3 as P

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RNG = np.random.default_rng(0xC41)


def rotl64(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x & M64


def chi_w(x, w, off1=1, off2=2):
    """chi on low w bits: y[i] = x[i] ^ ((~x[i+off1]) & x[i+off2]), indices mod w."""
    y = np.zeros_like(x)
    mask = (np.uint64(1) << np.uint64(w)) - np.uint64(1)
    for i in range(w):
        a = (x >> np.uint64((i + off1) % w)) & np.uint64(1)
        b = (x >> np.uint64((i + off2) % w)) & np.uint64(1)
        bit = ((x >> np.uint64(i)) & np.uint64(1)) ^ ((~a & np.uint64(1)) & b)
        y |= bit << np.uint64(i)
    return y & M64


def make_oddchi(nstages, rots, A=5, B=37):
    def mix_fn(xs, K):
        x = (xs ^ K) & M64
        for i in range(nstages):
            lo = x & ((np.uint64(1) << np.uint64(63)) - np.uint64(1))
            ylo = chi_w(lo, 63)
            abit = (x >> np.uint64(A)) & np.uint64(1)
            bbit = (x >> np.uint64(B)) & np.uint64(1)
            cap = (((x >> np.uint64(63)) & np.uint64(1)) ^ (abit & bbit)) << np.uint64(63)
            x = rotl64(ylo | cap, rots[i])
        return x & M64
    return mix_fn


def maxz_rand64(mix_fn, nPairs=1 << 14):
    xs = RNG.integers(0, 2**64, size=nPairs, dtype=np.uint64)
    K = np.full(nPairs, np.uint64(0x123456789ABCDEF0))
    worst, wd, wb, totc = 0.0, None, None, 0
    for d0 in P.all_deltas():
        y0 = mix_fn(xs, K)
        y1 = mix_fn(xs ^ np.uint64(d0), K)
        d = (y0 ^ y1).astype(np.uint64)
        bitmat = ((d[:, None] >> np.uint64(np.arange(64)[None, :])) & np.uint64(1)).astype(np.float64)
        mm = bitmat.mean(axis=0)
        z = (mm - 0.5) / np.sqrt(0.25 / nPairs)
        az = np.abs(z)
        totc += int((az >= 200).sum())
        if az.max() > worst:
            worst, wd, wb = float(az.max()), d0, int(np.argmax(az))
    return worst, wd, wb, totc


def invertibility_check(nstages, rots, A=5, B=37, n=1 << 16):
    """Round-trip: encrypt then decrypt using chi_63 inverse via fixed-point iteration."""
    # chi_63 inverse: iterate x <- y ^ f(x) converges for odd width (Daemen).
    xs = RNG.integers(0, 2**64, size=n, dtype=np.uint64)
    K = np.uint64(0x123456789ABCDEF0)
    mix_fn = make_oddchi(nstages, rots, A, B)
    ys = mix_fn(xs, np.full(n, K))
    # decrypt stage by stage (reverse order)
    x = ys.copy()
    for i in reversed(range(nstages)):
        x = rotl64(x, 64 - rots[i])  # inverse rotation
        cap_in = (x >> np.uint64(63)) & np.uint64(1)
        ylo = x & ((np.uint64(1) << np.uint64(63)) - np.uint64(1))
        # invert chi_63 by iteration
        z = ylo.copy()
        for _ in range(64):
            zn = ylo ^ (chi_w(z, 63) ^ z)  # z <- y ^ (chi(z)^z)
            if np.array_equal(zn, z):
                break
            z = zn
        abit = (z >> np.uint64(A)) & np.uint64(1)
        bbit = (z >> np.uint64(B)) & np.uint64(1)
        x63 = cap_in ^ (abit & bbit)
        x = (z | (x63 << np.uint64(63))) & M64
    x = (x ^ K) & M64
    bad = int((x != xs).sum())
    return bad


def main():
    # Positive control 1: bijectivity of the construction
    for nst in (4, 5, 6):
        rots = [7, 23, 41, 13, 59, 31][:nst]
        bad = invertibility_check(nst, rots)
        print(f"[invert] oddchi {nst}st round-trip mismatches: {bad}/65536", flush=True)
    # Positive control 2: even-width chi_64 must show weakness (gate sees chi trails)
    def even_chi64(xs, K):
        x = (xs ^ K) & M64
        for _ in range(6):
            x = chi_w(x, 64)
        return x & M64
    z, d, b, c = maxz_rand64(even_chi64)
    print(f"[control] even-chi64 6st z={z:.1f} d={d:#x}@{b} constbits={c} (expect weak)", flush=True)
    # Smoke: odd-width chi + cap at 4/5/6 stages
    for nst in (4, 5, 6):
        rots = [7, 23, 41, 13, 59, 31][:nst]
        z, d, b, c = maxz_rand64(make_oddchi(nst, rots))
        mark = "KEEP?" if z < 25 else "weak"
        print(f"[{mark}] oddchi {nst}st z={z:.1f} d={d:#x}@{b} constbits={c}", flush=True)


if __name__ == "__main__":
    main()
