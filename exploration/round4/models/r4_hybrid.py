"""Round 4, HYBRID track: heterogeneous compositions of primitives.

Per direction update: actively explore cross-combinations, not just pure-family
candidates. Each candidate below composes 2+ distinct primitive types.

Primitives used:
  S1    : THF/Blink 4-bit S-box (depth-3.5 class), minimized DNF
  MID_M : Midori almost-MDS binary matrix + ShuffleCell (free wiring)
  TCHI  : triangular chi-like layer, y[i]=x[i]^((~x[i+1])&x[i+2]), y[62]=x[62],
          y[63]=x[63]. PROVABLY bijective by back-substitution (triangular).
  CCHI  : cyclic chi-like, y=x^((~ROTL(x,1))&ROTL(x,2)). Used ONLY as Feistel
          F-function (F need not be bijective there).
  CMUL  : 64-bit constant multiply by odd C (bijective mod 2^64)
  CLMUL : carry-less multiply by odd C, low 64 bits. GF(2)-linear; bijective
          because gcd(C(x),x^64)=1 for odd C.
  XS    : xorshift64 (x^=x>>12; x^=x<<25; x^=x>>27), bijective
  LM    : Lai-Massey with 16-bit-multiplier F-functions
  L64   : xor-linear x^ROTL(x,11)^ROTL(x,37) (free-ish)

Candidates (name: composition):
  h_sandwich2  : [S1 + TCHI + rotl] 2-round SPN sandwich
  h_chifeist6  : [CCHI as F] 6-round Feistel
  h_multspn    : [CMUL -> 2x SPN(S1+MID_M)] multiply feeding SPN
  h_spnmult    : [2x SPN(S1+MID_M) -> CMUL] SPN then multiplier squeeze
  h_clmulspn   : [CLMUL + S1] 2-round SPN with clmul linear layer
  h_laimassey  : [LM + 16-bit mult F] 3-round Lai-Massey
  h_xorspn     : [XS -> 2x SPN] xorshift pre-diffusion, SPN replaces mult
  h_heterofeist: [Feistel, alternating S1-F / CCHI-F] heterogeneous Feistel

Bijectivity (fixed key): structural per candidate (see notes); all
spot-checked with bijectivity_spotcheck (200k samples, no collisions).
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, rotl64_np, sbox16_np, check_model_equiv,
                        bijectivity_spotcheck)

M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
_S1 = [0x0, 0x1, 0x2, 0x4, 0x3, 0x8, 0xF, 0xC,
       0x9, 0x5, 0xB, 0x6, 0x7, 0xE, 0xD, 0xA]
assert len(set(_S1)) == 16
_S1_NP = np.array(_S1, dtype=np.uint64)
_PERM = [0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8]
_SHIFTS = np.array([4 * i for i in range(16)], dtype=np.uint64)

# Odd constants (bijective multipliers). Popcounts kept moderate for speed.
C_MUL1 = 0x9E3779B97F4A7C15  # golden-ratio, odd
C_MUL2 = 0xBF58476D1CE4E5B9  # splitmix64 gamma, odd
C_CLMUL = 0x1B  # placeholder replaced below (want dense odd)
# Dense odd 64-bit for clmul diffusion (popcount ~32):
C_CLMUL = 0xA5A5A5A5A5A5A5A7
assert C_CLMUL & 1 == 1
C_LM1 = 0x9E37  # odd 16-bit
C_LM2 = 0x7F4A  # even -> make odd
C_LM2 |= 1
assert (C_LM1 & 1) and (C_LM2 & 1)


def _rc(i):
    return np.uint64(((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _rk_np(k, i):
    return rotl64_np(k, U64(13 * (i + 1))) ^ _rc(i)


def _midori_M_np(x):
    shp = np.shape(x)
    xf = np.asarray(x, dtype=np.uint64).reshape(-1)
    nib = ((xf[:, None] >> _SHIFTS) & np.uint64(0xF))
    out = np.empty_like(nib)
    for c in range(4):
        col = nib[:, 4 * c:4 * c + 4]
        parity = col[:, 0] ^ col[:, 1] ^ col[:, 2] ^ col[:, 3]
        out[:, 4 * c:4 * c + 4] = parity[:, None] ^ col
    y = (out << _SHIFTS).sum(axis=1)
    return y.reshape(shp)


def _shuffle_np(x):
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros(x.shape, dtype=np.uint64)
    for i, p in enumerate(_PERM):
        y |= ((x >> np.uint64(4 * p)) & np.uint64(0xF)) << np.uint64(4 * i)
    return y


def _tchi64_np(x):
    """Triangular chi-like, provably bijective (back-substitution)."""
    x = np.asarray(x, dtype=np.uint64)
    # y[i] = x[i] ^ ((~x[i+1]) & x[i+2]) for i<62; y[62]=x[62]; y[63]=x[63]
    b1 = (x >> np.uint64(1)) & np.uint64(1)  # not directly; do bitwise below
    # vectorized bit-by-bit:
    y = np.zeros_like(x)
    for i in range(62):
        xi = (x >> np.uint64(i)) & np.uint64(1)
        xi1 = (x >> np.uint64(i + 1)) & np.uint64(1)
        xi2 = (x >> np.uint64(i + 2)) & np.uint64(1)
        y |= (xi ^ ((1 - xi1) & xi2)) << np.uint64(i)
    y |= (x >> np.uint64(62)) & np.uint64(0x3) << np.uint64(62)
    # fix: top two bits pass through
    y = (y & np.uint64(0x3FFFFFFFFFFFFFFF)) | (x & np.uint64(0xC000000000000000))
    return y


def _cchi32_np(x):
    """Cyclic chi-like 32-bit (for Feistel F; bijectivity not required)."""
    x = np.asarray(x, dtype=np.uint64) & np.uint64(M32)
    r1 = ((x << np.uint64(1)) | (x >> np.uint64(31))) & np.uint64(M32)
    r2 = ((x << np.uint64(2)) | (x >> np.uint64(30))) & np.uint64(M32)
    return (x ^ ((~r1) & r2)) & np.uint64(M32)


def _clmul64_np(x, C):
    """Carry-less multiply by C, low 64 bits. Bijective for odd C."""
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros(np.shape(x), dtype=np.uint64)
    j = 0
    cc = C
    while cc:
        if cc & 1:
            y ^= (x << np.uint64(j)) if j < 64 else np.uint64(0)
        cc >>= 1
        j += 1
    return y


def _xorshift64_np(x):
    x = np.asarray(x, dtype=np.uint64)
    x ^= x >> np.uint64(12)
    x ^= (x << np.uint64(25)) & np.uint64(M64)
    x ^= x >> np.uint64(27)
    return x & np.uint64(M64)


def _lm_F_np(z):
    """Lai-Massey F: 16-bit multiplier halves."""
    z = np.asarray(z, dtype=np.uint64) & np.uint64(M32)
    lo = z & np.uint64(0xFFFF)
    hi = (z >> np.uint64(16)) & np.uint64(0xFFFF)
    p = ((lo * np.uint64(C_LM1)) ^ (hi * np.uint64(C_LM2))) & np.uint64(M32)
    # rotl32(z,9)
    r = (((z << np.uint64(9)) | (z >> np.uint64(23))) & np.uint64(M32))
    return (p ^ r) & np.uint64(M32)


# ---------------- candidates (numpy) ----------------

def mix_h_sandwich2_np(val, key):
    """S1 + triangular-chi sandwich, 2 rounds. All layers bijective."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(2):
        x = sbox16_np(x ^ _rk_np(k, i), _S1_NP)
        x = _tchi64_np(x)
        x = rotl64_np(x, U64(13))
    return (x ^ _rk_np(k, 2)) & MASK64


def _feist_round_np(L, R, F):
    return R, (L ^ F) & np.uint64(M32)


def mix_h_chifeist6_np(val, key):
    """6-round Feistel, F = cyclic chi-like. Bijective (Feistel)."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    L = (x >> np.uint64(32)) & np.uint64(M32)
    R = x & np.uint64(M32)
    for i in range(6):
        rk32 = (_rk_np(k, i) & np.uint64(M32))
        F = _cchi32_np(R ^ rk32)
        L, R = _feist_round_np(L, R, F)
    # no final swap; whiten
    rkL = (_rk_np(k, 6) >> np.uint64(32)) & np.uint64(M32)
    rkR = _rk_np(k, 6) & np.uint64(M32)
    return (((L ^ rkL) << np.uint64(32)) | (R ^ rkR)) & MASK64


def mix_h_multspn_np(val, key):
    """Multiply by odd C, then 2 SPN rounds. Bijective."""
    x = (np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64))
    x = (x * np.uint64(C_MUL1)) & MASK64
    k = np.asarray(key, dtype=np.uint64)
    for i in range(2):
        x = _shuffle_np(_midori_M_np(sbox16_np(x ^ _rk_np(k, i), _S1_NP)))
    return (x ^ _rk_np(k, 2)) & MASK64


def mix_h_spnmult_np(val, key):
    """2 SPN rounds, then multiply squeeze. Bijective."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(2):
        x = _shuffle_np(_midori_M_np(sbox16_np(x ^ _rk_np(k, i), _S1_NP)))
    x = (x * np.uint64(C_MUL2)) & MASK64
    return (x ^ _rk_np(k, 2)) & MASK64


def mix_h_clmulspn_np(val, key):
    """2 rounds: S1 + clmul + rotl. clmul odd => GF(2)-bijective."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(2):
        x = sbox16_np(x ^ _rk_np(k, i), _S1_NP)
        x = _clmul64_np(x, C_CLMUL)
        x = rotl64_np(x, U64(17))
    return (x ^ _rk_np(k, 2)) & MASK64


def mix_h_laimassey_np(val, key):
    """3-round Lai-Massey, 16-bit-multiplier F. Bijective (LM structure)."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    L = (x >> np.uint64(32)) & np.uint64(M32)
    R = x & np.uint64(M32)
    for i in range(3):
        rk32 = (_rk_np(k, i) & np.uint64(M32))
        T = _lm_F_np((L ^ R ^ rk32) & np.uint64(M32))
        L, R = (L ^ T) & np.uint64(M32), (R ^ T) & np.uint64(M32)
        L, R = R, L  # swap
    rkL = (_rk_np(k, 3) >> np.uint64(32)) & np.uint64(M32)
    rkR = _rk_np(k, 3) & np.uint64(M32)
    return (((L ^ rkL) << np.uint64(32)) | (R ^ rkR)) & MASK64


def mix_h_sandwich3_np(val, key):
    """S1 + triangular-chi sandwich, 3 rounds."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    for i in range(3):
        x = sbox16_np(x ^ _rk_np(k, i), _S1_NP)
        x = _tchi64_np(x)
        x = rotl64_np(x, U64(13))
    return (x ^ _rk_np(k, 3)) & MASK64


def mix_h_xorspn3_np(val, key):
    """xorshift + 3-round SPN."""
    x = _xorshift64_np(np.asarray(val, dtype=np.uint64) ^
                       np.asarray(key, dtype=np.uint64))
    k = np.asarray(key, dtype=np.uint64)
    for i in range(3):
        x = _shuffle_np(_midori_M_np(sbox16_np(x ^ _rk_np(k, i), _S1_NP)))
    return (x ^ _rk_np(k, 3)) & MASK64


def mix_h_xorspn_np(val, key):
    """xorshift pre-diffusion, then 2-round SPN (replaces the mult)."""
    x = _xorshift64_np(np.asarray(val, dtype=np.uint64) ^
                       np.asarray(key, dtype=np.uint64))
    k = np.asarray(key, dtype=np.uint64)
    for i in range(2):
        x = _shuffle_np(_midori_M_np(sbox16_np(x ^ _rk_np(k, i), _S1_NP)))
    return (x ^ _rk_np(k, 2)) & MASK64


def _sbox8_s1_np(x):
    return sbox16_np(x, _S1_NP) & np.uint64(0xFFFFFFFF)


def mix_h_heterofeist_np(val, key):
    """6-round Feistel, even rounds S1-F, odd rounds chi-F. Bijective."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    L = (x >> np.uint64(32)) & np.uint64(M32)
    R = x & np.uint64(M32)
    for i in range(6):
        rk32 = (_rk_np(k, i) & np.uint64(M32))
        if i % 2 == 0:
            F = _sbox8_s1_np(R ^ rk32)
        else:
            F = _cchi32_np(R ^ rk32)
        L, R = _feist_round_np(L, R, F)
    rkL = (_rk_np(k, 6) >> np.uint64(32)) & np.uint64(M32)
    rkR = _rk_np(k, 6) & np.uint64(M32)
    return (((L ^ rkL) << np.uint64(32)) | (R ^ rkR)) & MASK64


# ---------------- scalar versions ----------------

def _rotl64_s(x, r):
    r &= 63
    return (((x << r) | (x >> (64 - r))) & M64) if r else (x & M64)


def _rk_s(key, i):
    return (_rotl64_s(key, 13 * (i + 1)) ^ (((i + 1) * 0x9E3779B97F4A7C15) & M64)) & M64


def _sbox16_s(x):
    y = 0
    for s in range(16):
        y |= _S1[(x >> (4 * s)) & 0xF] << (4 * s)
    return y


def _midori_M_s(x):
    nib = [(x >> (4 * s)) & 0xF for s in range(16)]
    out = [0] * 16
    for c in range(4):
        col = nib[4 * c:4 * c + 4]
        p = col[0] ^ col[1] ^ col[2] ^ col[3]
        for j in range(4):
            out[4 * c + j] = p ^ col[j]
    return sum(v << (4 * s) for s, v in enumerate(out))


def _shuffle_s(x):
    y = 0
    for i, p in enumerate(_PERM):
        y |= ((x >> (4 * p)) & 0xF) << (4 * i)
    return y


def _tchi64_s(x):
    y = x & 0xC000000000000000  # top two bits pass
    for i in range(62):
        xi = (x >> i) & 1
        y |= (xi ^ ((1 - ((x >> (i + 1)) & 1)) & ((x >> (i + 2)) & 1))) << i
    return y & M64


def _cchi32_s(x):
    x &= M32
    r1 = (((x << 1) | (x >> 31)) & M32)
    r2 = (((x << 2) | (x >> 30)) & M32)
    return (x ^ ((~r1) & r2)) & M32


def _clmul64_s(x, C):
    y = 0
    j = 0
    cc = C
    while cc:
        if cc & 1:
            y ^= (x << j) & M64
        cc >>= 1
        j += 1
    return y & M64


def _xorshift64_s(x):
    x = (x ^ (x >> 12)) & M64
    x = (x ^ ((x << 25) & M64)) & M64
    x = (x ^ (x >> 27)) & M64
    return x


def _lm_F_s(z):
    z &= M32
    lo, hi = z & 0xFFFF, (z >> 16) & 0xFFFF
    p = ((lo * C_LM1) ^ (hi * C_LM2)) & M32
    r = (((z << 9) | (z >> 23)) & M32)
    return (p ^ r) & M32


def mix_h_sandwich2_s(v, k):
    x = (v ^ k) & M64
    for i in range(2):
        x = _sbox16_s(x ^ _rk_s(k, i))
        x = _tchi64_s(x)
        x = _rotl64_s(x, 13)
    return (x ^ _rk_s(k, 2)) & M64


def mix_h_chifeist6_s(v, k):
    x = (v ^ k) & M64
    L, R = (x >> 32) & M32, x & M32
    for i in range(6):
        F = _cchi32_s(R ^ (_rk_s(k, i) & M32))
        L, R = R, (L ^ F) & M32
    rkL = (_rk_s(k, 6) >> 32) & M32
    rkR = _rk_s(k, 6) & M32
    return ((((L ^ rkL) << 32) | (R ^ rkR))) & M64


def mix_h_multspn_s(v, k):
    x = ((v ^ k) * C_MUL1) & M64
    for i in range(2):
        x = _shuffle_s(_midori_M_s(_sbox16_s(x ^ _rk_s(k, i))))
    return (x ^ _rk_s(k, 2)) & M64


def mix_h_spnmult_s(v, k):
    x = (v ^ k) & M64
    for i in range(2):
        x = _shuffle_s(_midori_M_s(_sbox16_s(x ^ _rk_s(k, i))))
    x = (x * C_MUL2) & M64
    return (x ^ _rk_s(k, 2)) & M64


def mix_h_clmulspn_s(v, k):
    x = (v ^ k) & M64
    for i in range(2):
        x = _sbox16_s(x ^ _rk_s(k, i))
        x = _clmul64_s(x, C_CLMUL)
        x = _rotl64_s(x, 17)
    return (x ^ _rk_s(k, 2)) & M64


def mix_h_laimassey_s(v, k):
    x = (v ^ k) & M64
    L, R = (x >> 32) & M32, x & M32
    for i in range(3):
        T = _lm_F_s((L ^ R ^ (_rk_s(k, i) & M32)) & M32)
        L, R = (L ^ T) & M32, (R ^ T) & M32
        L, R = R, L
    rkL = (_rk_s(k, 3) >> 32) & M32
    rkR = _rk_s(k, 3) & M32
    return ((((L ^ rkL) << 32) | (R ^ rkR))) & M64


def mix_h_sandwich3_s(v, k):
    x = (v ^ k) & M64
    for i in range(3):
        x = _sbox16_s(x ^ _rk_s(k, i))
        x = _tchi64_s(x)
        x = _rotl64_s(x, 13)
    return (x ^ _rk_s(k, 3)) & M64


def mix_h_xorspn3_s(v, k):
    x = _xorshift64_s((v ^ k) & M64)
    for i in range(3):
        x = _shuffle_s(_midori_M_s(_sbox16_s(x ^ _rk_s(k, i))))
    return (x ^ _rk_s(k, 3)) & M64


def mix_h_xorspn_s(v, k):
    x = _xorshift64_s((v ^ k) & M64)
    for i in range(2):
        x = _shuffle_s(_midori_M_s(_sbox16_s(x ^ _rk_s(k, i))))
    return (x ^ _rk_s(k, 2)) & M64


def mix_h_heterofeist_s(v, k):
    x = (v ^ k) & M64
    L, R = (x >> 32) & M32, x & M32
    for i in range(6):
        rk32 = _rk_s(k, i) & M32
        F = _sbox16_s(R ^ rk32) & M32 if i % 2 == 0 else _cchi32_s(R ^ rk32)
        L, R = R, (L ^ F) & M32
    rkL = (_rk_s(k, 6) >> 32) & M32
    rkR = _rk_s(k, 6) & M32
    return ((((L ^ rkL) << 32) | (R ^ rkR))) & M64


if __name__ == "__main__":
    pairs = [
        ("h_sandwich2", mix_h_sandwich2_s, mix_h_sandwich2_np),
        ("h_chifeist6", mix_h_chifeist6_s, mix_h_chifeist6_np),
        ("h_multspn", mix_h_multspn_s, mix_h_multspn_np),
        ("h_spnmult", mix_h_spnmult_s, mix_h_spnmult_np),
        ("h_clmulspn", mix_h_clmulspn_s, mix_h_clmulspn_np),
        ("h_laimassey", mix_h_laimassey_s, mix_h_laimassey_np),
        ("h_xorspn", mix_h_xorspn_s, mix_h_xorspn_np),
        ("h_sandwich3", mix_h_sandwich3_s, mix_h_sandwich3_np),
        ("h_xorspn3", mix_h_xorspn3_s, mix_h_xorspn3_np),
        ("h_heterofeist", mix_h_heterofeist_s, mix_h_heterofeist_np),
    ]
    for name, s, v in pairs:
        check_model_equiv(s, v, name, trials=200)
        bijectivity_spotcheck(v, name, n=200000)
