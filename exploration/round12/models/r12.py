"""Round 12 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round12/gen_r12.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
  F = S1 layer -> linear -> ^rk32
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).

Round 12 attacks the linear/diffusion structure inside F and F cost:
  F1: 5 rounds + 3-rotation linear: lin(a,b,c) = x^rotl(x,a)^rotl(x,b)^rotl(x,c)
      (same 2-XOR XOR-tree depth as the 2-rotation layer, better per-round
      diffusion) -- re-attacks the 5-round phase transition.
  F2: partial S-box F: S1 on the low 16 bits only, full-32-bit lin(3,11),
      at 6/7/8 rounds -- cheaper F, more rounds.
  F3: 3-rotation linear at 6 rounds: better diffusion/round at ~41u?
  F4: heterogeneous: 16-bit-half rotation mixing in the linear layer,
      lin16(x) = x ^ rotl32(x,3) ^ rot16half(x,7), at 6 rounds.
"""
import numpy as np

S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)  # THF/Blink (r7-r11)

MASK32 = np.uint64(0xFFFFFFFF)
MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)


def _rotl32_np(x, r):
    r %= 32
    if r == 0:
        return x & MASK32
    return ((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & MASK32


def _rotl64_np(x, r):
    r %= 64
    if r == 0:
        return x & MASK64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & MASK64


def _sbox_layer32_np(x):
    """Eight 4-bit S1 S-boxes over the 32-bit word."""
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1, nib) << np.uint64(4 * i)
    return out & MASK32


def _sbox_half32_np(x):
    """S1 on the low 16 bits (4 nibbles) only; high 16 bits pass through."""
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(4):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1, nib) << np.uint64(4 * i)
    out |= xv & np.uint64(0xFFFF0000)
    return out & MASK32


def _lin_abc_np(x, a, b, c):
    """3-rotation linear: x ^ rotl(x,a) ^ rotl(x,b) ^ rotl(x,c)."""
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b) ^ _rotl32_np(x, c)) & MASK32


def _lin_ab_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


def _rot16half_np(x, n):
    """Rotate each 16-bit half of x left by n (within the half)."""
    n %= 16
    lo = x & np.uint64(0xFFFF)
    hi = (x >> np.uint64(16)) & np.uint64(0xFFFF)
    if n:
        lo = ((lo << np.uint64(n)) | (lo >> np.uint64(16 - n))) & np.uint64(0xFFFF)
        hi = ((hi << np.uint64(n)) | (hi >> np.uint64(16 - n))) & np.uint64(0xFFFF)
    return ((hi << np.uint64(16)) | lo) & MASK32


def _lin_16rot_np(x):
    """Heterogeneous linear: x ^ rotl32(x,3) ^ rot16half(x,7)."""
    return (x ^ _rotl32_np(x, 3) ^ _rot16half_np(x, 7)) & MASK32


def _rk32_std_np(k, i):
    """Affine schedule (r7/r8/r9): low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64))."""
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32


def _feistel_nw_np(x, k, rounds, F):
    """Balanced Feistel, 32-bit halves, {R,L} output, no whitening."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, rounds + 1):
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _mk(name, rounds, F):
    def fn(val, key):
        return _feistel_nw_np(val, key, rounds, F)
    fn.__name__ = name
    return fn


# F1: 5 rounds + 3-rotation linear
def _F_abc(a, b, c):
    def F(R, rk32):
        return (_lin_abc_np(_sbox_layer32_np(R), a, b, c) ^ rk32) & MASK32
    return F


r12_feist5_lin3711_nw = _mk("r12_feist5_lin3711_nw", 5, _F_abc(3, 7, 11))
r12_feist5_lin31119_nw = _mk("r12_feist5_lin31119_nw", 5, _F_abc(3, 11, 19))
r12_feist5_lin71319_nw = _mk("r12_feist5_lin71319_nw", 5, _F_abc(7, 13, 19))
r12_feist5_lin31125_nw = _mk("r12_feist5_lin31125_nw", 5, _F_abc(3, 11, 25))

# F2: partial S-box (low 16 bits) + full lin(3,11), 6/7/8 rounds
def _F_half():
    def F(R, rk32):
        return (_lin_ab_np(_sbox_half32_np(R), 3, 11) ^ rk32) & MASK32
    return F


r12_feist6_s1half311_nw = _mk("r12_feist6_s1half311_nw", 6, _F_half())
r12_feist7_s1half311_nw = _mk("r12_feist7_s1half311_nw", 7, _F_half())
r12_feist8_s1half311_nw = _mk("r12_feist8_s1half311_nw", 8, _F_half())

# F3: 6 rounds + 3-rotation linear
r12_feist6_lin3711_nw = _mk("r12_feist6_lin3711_nw", 6, _F_abc(3, 7, 11))
r12_feist6_lin71319_nw = _mk("r12_feist6_lin71319_nw", 6, _F_abc(7, 13, 19))

# F4: heterogeneous 16-bit-half rotation mixing, 6 rounds
def _F_16rot(R, rk32):
    return (_lin_16rot_np(_sbox_layer32_np(R)) ^ rk32) & MASK32


r12_feist6_s1_16rot_nw = _mk("r12_feist6_s1_16rot_nw", 6, _F_16rot)

ALL = [
    r12_feist5_lin3711_nw, r12_feist5_lin31119_nw, r12_feist5_lin71319_nw,
    r12_feist5_lin31125_nw,
    r12_feist6_s1half311_nw, r12_feist7_s1half311_nw, r12_feist8_s1half311_nw,
    r12_feist6_lin3711_nw, r12_feist6_lin71319_nw,
    r12_feist6_s1_16rot_nw,
]
