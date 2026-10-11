"""Round-2 lane4_il_b: bit-interleaved 4x16-bit lanes (D3 dead-lane fix).

Pipeline (fixed key):
  x = val ^ key
  y = INTERLEAVE(x): bit i of x -> bit (i%4)*16 + (i//4) of y.
    Lane l of y holds bits {l, l+4, l+8, ..., l+60} of x, so a small val
    still drives every lane (D3's dead-lane collapse is impossible: each
    lane always carries 16 distinct input bits).
  per 16-bit lane l: w[l] = y[l] * C[l]   (C odd => bijection mod 2^16)
  then bijective downmix: w[l] ^= w[l]>>8; w[l] ^= w[l]>>4
    (DEVIATION from the brief, required: a 16-bit multiply is
    lower-triangular in bits -- output bit j depends only on input bits
    <= j -- so without a high->low step, scenarios with constant low
    input bits (HIGH-ONLY, PTR-j8) leave output bits exactly fixed.
    First calibrated screen of the as-spec'd design: HIGH-ONLY per-bit
    max|z|=512 (fixed bits), PTR-j8 reduction max|z|=6655 -> CAL_FLAG.
    Each xor-shift step x ^= x>>s is upper-triangular with 1s on the
    diagonal, hence a bijection; cost ~ +2 unit-delays.)
  Feistel cross rounds (sequential half-steps, rotations r1/r2):
    pairs (L0,L1) rot(11,17); pairs (L2,L3) rot(11,17); pairs (L1,L2) rot(7,19); pairs (L3,L0) rot(7,19)
  z = DEINTERLEAVE(w)  (inverse bit-permutation of INTERLEAVE)
  out = z ^ ROTL64(key, 7)

Bijectivity (fixed key): INTERLEAVE/DEINTERLEAVE are bit-permutations
(bijections, free wiring); x*=C with C odd is a bijection mod 2^16; each
Feistel sequential half-step (a,b)->(a^f(b), b^g(new-a)) is bijective for
ANY f,g (here g is XOR-rotation or ADDITION mod 2^16, both bijective for
fixed t: b->b^K and b->b+K are permutations); the final
xor-with-key-derived-constant is a bijection. Composition of bijections
=> val->out is a permutation for every key.
Constants 0x9E37, 0x7F4B, 0x85EB, 0xC2B9: all asserted ODD at import time.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import check_model_equiv, bijectivity_spotcheck, rotl64_np

M16 = 0xFFFF
M64 = (1 << 64) - 1
U64 = np.uint64
CONSTS = (40503, 32587, 34283, 49849)
for _c in CONSTS:
    assert _c & 1, f"lane mult constant 0x{_c:04X} is EVEN - mult is not bijective!"


def _interleave_scalar(x):
    y = 0
    for i in range(64):
        if (x >> i) & 1:
            y |= 1 << (((i % 4) * 16) + (i // 4))
    return y


def _deinterleave_scalar(w):
    z = 0
    for i in range(64):
        if (w >> i) & 1:
            l, j = divmod(i, 16)
            z |= 1 << (l + 4 * j)
    return z


def _interleave_np(x):
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(x)
    for j in range(16):
        nib = (x >> U64(4 * j)) & U64(0xF)   # src bits x[4j+3:4j]
        y |= ((nib & U64(1))) << U64(j)
        y |= ((nib >> U64(1)) & U64(1)) << U64(16 + j)
        y |= ((nib >> U64(2)) & U64(1)) << U64(32 + j)
        y |= ((nib >> U64(3)) & U64(1)) << U64(48 + j)
    return y


def _deinterleave_np(w):
    w = np.asarray(w, dtype=np.uint64)
    z = np.zeros_like(w)
    for l in range(4):
        lane = (w >> U64(16 * l)) & U64(M16)
        for j in range(16):
            z |= ((lane >> U64(j)) & U64(1)) << U64(4 * j + l)
    return z


def _downmix_scalar(w):
    w ^= w >> 8
    w ^= w >> 4
    return w & M16


def _downmix_np(w):
    w = np.asarray(w, dtype=np.uint64)
    w = w ^ (w >> U64(8))
    w = w ^ (w >> U64(4))
    return w & U64(M16)


def _cross_scalar(p, q, r1, r2):
    r1 %= 16; r2 %= 16
    qrot = (((q << r1) | (q >> (16 - r1))) & M16) if r1 else q
    t = p ^ qrot
    trot = (((t << r2) | (t >> (16 - r2))) & M16) if r2 else t
    q = q ^ trot
    p = t
    return p, q


def _rotl16_np(v, r):
    v = np.asarray(v, dtype=np.uint64) & U64(M16)
    r = int(r) & 15
    if r == 0:
        return v
    return ((v << U64(r)) | (v >> U64(16 - r))) & U64(M16)


def _cross_np(p, q, r1, r2):
    t = p ^ _rotl16_np(q, r1)
    q = q ^ _rotl16_np(t, r2)
    p = t
    return p, q


def _cross_add_scalar(p, q, r1, r2):
    # Feistel with nonlinear G: t = p ^ ROTL16(q,r1); q = (q + ROTL16(t,r2)) mod 2^16
    # Bijective: (t, q_new) -> q = q_new - ROTL16(t,r2), p = t ^ ROTL16(q,r1).
    r1 %= 16; r2 %= 16
    qrot = (((q << r1) | (q >> (16 - r1))) & M16) if r1 else q
    t = p ^ qrot
    trot = (((t << r2) | (t >> (16 - r2))) & M16) if r2 else t
    q = (q + trot) & M16
    p = t
    return p, q


def _cross_add_np(p, q, r1, r2):
    t = p ^ _rotl16_np(q, r1)
    q = (q + _rotl16_np(t, r2)) & U64(M16)
    p = t
    return p, q



def _cross_all_scalar(a, b, c, d):
    a, b = _cross_scalar(a, b, 11, 17)
    c, d = _cross_scalar(c, d, 11, 17)
    b, c = _cross_scalar(b, c, 7, 19)
    d, a = _cross_scalar(d, a, 7, 19)
    return a, b, c, d


def _cross_all_np(a, b, c, d):
    a, b = _cross_np(a, b, 11, 17)
    c, d = _cross_np(c, d, 11, 17)
    b, c = _cross_np(b, c, 7, 19)
    d, a = _cross_np(d, a, 7, 19)
    return a, b, c, d



def mix_lane4_il_b_scalar(val, key):
    val &= M64
    key &= M64
    y = _interleave_scalar(val ^ key)
    lanes = [_downmix_scalar((((y >> (16 * l)) & M16) * CONSTS[l]) & M16)
             for l in range(4)]
    lanes = _cross_all_scalar(*lanes)
    w = (lanes[3] << 48) | (lanes[2] << 32) | (lanes[1] << 16) | lanes[0]
    z = _deinterleave_scalar(w)
    return z ^ (((key << 7) | (key >> 57)) & M64)


def mix_lane4_il_b_np(val, key):
    k = np.asarray(key, dtype=np.uint64)
    x = np.asarray(val, dtype=np.uint64) ^ k
    y = _interleave_np(x)
    lanes = [_downmix_np((((y >> U64(16 * l)) & U64(M16)) * U64(CONSTS[l]))
                      & U64(M16)) for l in range(4)]
    lanes = _cross_all_np(*lanes)
    w = ((lanes[3] << U64(48)) | (lanes[2] << U64(32)) |
         (lanes[1] << U64(16)) | lanes[0])
    z = _deinterleave_np(w)
    return z ^ rotl64_np(k, 7)


if __name__ == "__main__":
    check_model_equiv(mix_lane4_il_b_scalar, mix_lane4_il_b_np, "lane4_il_b")
    bijectivity_spotcheck(mix_lane4_il_b_np, "lane4_il_b")
