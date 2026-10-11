"""Round 7 TEAM C models: F linear-layer & key-schedule variants of r6_feist8_spn.

Base composition (kept for all 5): val^key whitening -> 8x Feistel round
(L,R) = (R, L^F(R,rk)), F = S1-S-box(8 nibbles) -> LINEAR32 -> S1-S-box ->
^rk32, out = {R,L}. S1 = [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10] (permutation).

Axis 1 (linear layer, rk = rotl64(k,13(i+1)) ^ (i+1)*GOLDEN as in r6):
  r7_feist8_r311 : linear = x ^ rotl32(x,3)  ^ rotl32(x,11)
  r7_feist8_r517 : linear = x ^ rotl32(x,5)  ^ rotl32(x,17)
  r7_feist8_mid32: linear = 32-bit Midori almost-MDS on nibbles:
                   8 nibbles treated as TWO 4-nibble columns (one per 16-bit
                   half); per column y[i] = XOR of the other 3 nibbles
                   (the exact Midori M circulant (0,1,1,1) restricted to 32
                   bits; matches r5._midori32_np semantics). Invertible per
                   column (J+I over GF(2), 4x4, det=1), hence bijective.

Axis 2 (key schedule, F linear kept = r6's rotl7/rotl13 xor):
  r7_feist8_rksimple: rk(k,i) = rotl64(k, 13*(i+1))          (no round constant)
  r7_feist8_rkcheap : rk(k,i) = k ^ ((i+1)*0x9E3779B97F4A7C15) (no rotation)

Bijectivity: every Feistel round is a permutation for ANY F and ANY rk, and
whitening is xor, so each candidate is a fixed-key permutation of 64 bits by
structure. The linear layers are additionally verified bijective (rank 32)
by the script guard at the bottom (run at import: raises if singular).
"""
import numpy as np

K = np.uint64
M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
GOLDEN = 0x9E3779B97F4A7C15

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]
assert len(set(S1)) == 16
S1_NP = np.array(S1, dtype=np.uint64)


def _rotl32_np(x, n):
    x = np.asarray(x, dtype=np.uint64)
    n = int(n) % 32
    if n == 0:
        return x & np.uint64(M32)
    return (((x << np.uint64(n)) | (x >> np.uint64(32 - n)))) & np.uint64(M32)


def _rotl64_np(x, n):
    x = np.asarray(x, dtype=np.uint64)
    n = int(n) % 64
    if n == 0:
        return x & np.uint64(M64)
    return (((x << np.uint64(n)) | (x >> np.uint64(64 - n)))) & np.uint64(M64)


def _sbox32_np(R):
    """S1 applied to the 8 nibbles of a 32-bit word (vectorized)."""
    R = np.asarray(R, dtype=np.uint64)
    out = np.zeros(np.shape(R), dtype=np.uint64)
    for i in range(8):
        nib = ((R >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1_NP, nib) << np.uint64(4 * i)
    return out & np.uint64(M32)


# ---- linear layers (32-bit) ----
def _lin_r311_np(x):
    x = np.asarray(x, dtype=np.uint64)
    return (x ^ _rotl32_np(x, 3) ^ _rotl32_np(x, 11)) & np.uint64(M32)


def _lin_r517_np(x):
    x = np.asarray(x, dtype=np.uint64)
    return (x ^ _rotl32_np(x, 5) ^ _rotl32_np(x, 17)) & np.uint64(M32)


def _lin_r713_np(x):
    x = np.asarray(x, dtype=np.uint64)
    return (x ^ _rotl32_np(x, 7) ^ _rotl32_np(x, 13)) & np.uint64(M32)


def _lin_mid32_np(x):
    """32-bit Midori M: two independent 4-nibble columns (per 16-bit half),
    y[i] = XOR of other 3 nibbles in the column."""
    x = np.asarray(x, dtype=np.uint64) & np.uint64(M32)
    shp = np.shape(x)
    xf = x.reshape(-1)
    sh = (np.arange(8) * 4).astype(np.uint64)
    nib = ((xf[:, None] >> sh) & np.uint64(0xF))
    out = np.empty_like(nib)
    for c in range(2):
        col = nib[:, 4 * c:4 * c + 4]
        par = col[:, 0] ^ col[:, 1] ^ col[:, 2] ^ col[:, 3]
        out[:, 4 * c:4 * c + 4] = par[:, None] ^ col
    y = (out.astype(np.uint64) << sh).sum(axis=1)
    return (y.reshape(shp)) & np.uint64(M32)


# ---- key schedules ----
def _rk_full_np(k, i):
    """r6 key schedule: rotl64(k,13*(i+1)) ^ (i+1)*GOLDEN."""
    return _rotl64_np(k, 13 * (i + 1)) ^ np.uint64(((i + 1) * GOLDEN) & M64)


def _rk_nocnst_np(k, i):
    """r7_feist8_rksimple: rotation only, no round constant."""
    return _rotl64_np(k, 13 * (i + 1))


def _rk_norot_np(k, i):
    """r7_feist8_rkcheap: xor with round constant only, no rotation."""
    return np.asarray(k, dtype=np.uint64) ^ np.uint64(((i + 1) * GOLDEN) & M64)


def _feistel8_np(x, k, lin_fn, rk_fn):
    """8-round Feistel with whitening; lin_fn = 32-bit linear layer."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = ((x >> np.uint64(32)) ^ (k >> np.uint64(32))) & np.uint64(M32)
    R = (x ^ k) & np.uint64(M32)
    for i in range(8):
        rk32 = rk_fn(k, i + 1) & np.uint64(M32)
        t = _sbox32_np(R)
        t = lin_fn(t)
        t = _sbox32_np(t)
        F = (t ^ rk32) & np.uint64(M32)
        L, R = R, (L ^ F) & np.uint64(M32)
    return ((R << np.uint64(32)) | L) & np.uint64(M64)


def r7_feist8_r311(val, key):
    return _feistel8_np(val, key, _lin_r311_np, _rk_full_np)


def r7_feist8_r517(val, key):
    return _feistel8_np(val, key, _lin_r517_np, _rk_full_np)


def r7_feist8_mid32(val, key):
    return _feistel8_np(val, key, _lin_mid32_np, _rk_full_np)


def r7_feist8_rksimple(val, key):
    return _feistel8_np(val, key, _lin_r713_np, _rk_nocnst_np)


def r7_feist8_rkcheap(val, key):
    return _feistel8_np(val, key, _lin_r713_np, _rk_norot_np)


# ---- linear-layer bijectivity guard (run at import) ----
def _lin_rank(lin_fn):
    """GF(2) rank of the 32x32 linear map; 32 == bijection."""
    cols = []
    for i in range(32):
        cols.append(int(lin_fn(np.uint64(1) << np.uint64(i))) & M32)
    rank = 0
    for b in range(31, -1, -1):
        piv = None
        for i in range(rank, 32):
            if (cols[i] >> b) & 1:
                piv = i
                break
        if piv is None:
            continue
        cols[rank], cols[piv] = cols[piv], cols[rank]
        for i in range(32):
            if i != rank and ((cols[i] >> b) & 1):
                cols[i] ^= cols[rank]
        rank += 1
    return rank


for _name, _fn in [("r311", _lin_r311_np), ("r517", _lin_r517_np),
                   ("r713", _lin_r713_np), ("mid32", _lin_mid32_np)]:
    _r = _lin_rank(_fn)
    assert _r == 32, f"linear layer {_name} singular (rank {_r})"
