"""
SPN-based MIX model — bit-accurate reference for the proposed RISC-V `mix`.

One round:  x ^= ROTL64(key, 13*(i+1)) ^ RC[i]   (round key + round constant)
            x  = SBOX16(x)                        (16x parallel 4-bit PRESENT S-box)
            x  = PERM(x)                          (PRESENT 64-bit pLayer, free wiring)

out = MIX(val, key):
    x  = val ^ key
    for i in 0..R-1: x = PERM(SBOX16(x ^ RK[i]))
    out = x ^ RK[R]

Every stage is bijective (xor, bijective S-box, permutation) => for fixed key,
MIX(., key) is a permutation of 2^64. Full-cycle uniformity is therefore EXACT.
"""
import numpy as np

M64 = (1 << 64) - 1
U64 = np.uint64
MASK64 = U64(0xFFFFFFFFFFFFFFFF)

# PRESENT 4-bit S-box: bijective, differential uniformity 4 (optimal for 4b),
# max linear bias 4/16.
SBOX = np.array([0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
                 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2], dtype=np.uint64)
assert len(set(SBOX.tolist())) == 16, "S-box must be bijective"

# PRESENT pLayer for 64-bit block / 16 nibbles: P(i) = 16*i mod 63 (i<63), P(63)=63.
# Each S-box's 4 output bits land in 4 distinct S-boxes => full diffusion in 2 rounds.
P = np.array([(16 * i) % 63 for i in range(63)] + [63], dtype=np.int64)
assert len(set(P.tolist())) == 64, "permutation must be bijective"

_GOLDEN = 0x9E3779B97F4A7C15


def _rc(i):
    return ((i + 1) * _GOLDEN) & ((1 << 64) - 1)


def rotl64_scalar(v, r):
    r &= 63
    v &= M64
    return v if r == 0 else (((v << r) | (v >> (64 - r)))) & M64


def rotl64_np(v, r):
    r = np.asarray(r, dtype=np.uint64) & U64(63)
    return np.where(r == 0, v, (((v << r) | (v >> (U64(64) - r)))) & MASK64)


def sbox16_scalar(x):
    y = 0
    for s in range(16):
        y |= int(SBOX[(x >> (4 * s)) & 0xF]) << (4 * s)
    return y


def perm_scalar(x):
    y = 0
    for i in range(64):
        if (x >> i) & 1:
            y |= 1 << int(P[i])
    return y


def mix_spn_scalar(val, key, rounds=10):
    val &= M64
    key &= M64
    x = val ^ key
    for i in range(rounds):
        rk = rotl64_scalar(key, 13 * (i + 1)) ^ _rc(i)
        x = perm_scalar(sbox16_scalar(x ^ rk))
    x ^= rotl64_scalar(key, 13 * (rounds + 1)) ^ _rc(rounds)
    return x & M64


# ---- numpy vectorized ----
_SHIFTS = (np.arange(16, dtype=np.uint64) * U64(4))


def sbox16_np(x):
    shp = x.shape
    xf = np.asarray(x, dtype=np.uint64).reshape(-1)
    nib = ((xf[:, None] >> _SHIFTS) & U64(0xF))
    y = (np.take(SBOX, nib.astype(np.int64)) << _SHIFTS).sum(axis=1)
    return y.reshape(shp)


def perm_np(x):
    y = np.zeros_like(x)
    for i in range(64):
        b = (x >> U64(i)) & U64(1)
        y |= b << U64(int(P[i]))
    return y


def mix_spn_np(val, key, rounds=10):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(rounds):
        rk = rotl64_np(k, U64(13 * (i + 1))) ^ U64(_rc(i))
        x = perm_np(sbox16_np(x ^ rk))
    x ^= rotl64_np(k, U64(13 * (rounds + 1))) ^ U64(_rc(rounds))
    return x


if __name__ == "__main__":
    import random
    rng = random.Random(1234)
    for r in (4, 6, 8, 10, 12):
        for _ in range(300):
            v = rng.getrandbits(64)
            kk = rng.getrandbits(64)
            a = mix_spn_scalar(v, kk, r)
            b = int(mix_spn_np(U64(v), U64(kk), r))
            assert a == b, (r, hex(v), hex(kk), hex(a), hex(b))
    print("scalar == vector model for rounds {4,6,8,10,12}: OK")
    # bijectivity spot check at 64b is impossible exhaustively; each stage is
    # bijective by construction (xor / bijective sbox / permutation).
