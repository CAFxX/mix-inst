"""D3 lane4_s1_const: single stage, four 16-bit lanes.

Lane inputs a,b,c,d = four 16-bit lanes of (val ^ key).
a *= 16'h9E37; b *= 16'h7F4B; c *= 16'h85EB; d *= 16'hC2B9
(all odd; 0x7F4B = brief's 0x7F4A corrected to the nearest odd constant —
0x7F4A is even and was a spec bug)
Feistel cross on (a,b): t = a ^ ROTL16(b,5); b ^= ROTL16(t,9); a = t
Feistel cross on (c,d): same rotations (5,9)
lane rotate (a,b,c,d) -> (b,c,d,a); whitening a^=16'h9E37 etc.;
out = {d,c,b,a}

Bijectivity (fixed key): ODD constant mults are bijections; each Feistel
half-step is bijective for ANY F; lane rotate is a bit-permutation
(bijection); xor whitening is a bijection. Composition => 2^64 permutation.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import check_model_equiv

M16 = 0xFFFF
U64 = np.uint64
LANE_CONSTS = (0x9E37, 0x7F4B, 0x85EB, 0xC2B9)  # all odd (bijective mults)
for _c in LANE_CONSTS:
    assert _c & 1, f"lane mult constant 0x{_c:04X} is EVEN - mult is not bijective!"


def _rotl16_scalar(x, r):
    r &= 15
    return (((x << r) | (x >> (16 - r))) & M16) if r else x


def _rotl16_np(v, r):
    v = np.asarray(v, dtype=np.uint64) & U64(M16)
    r = int(r) & 15
    if r == 0:
        return v
    return ((v << U64(r)) | (v >> U64(16 - r))) & U64(M16)


def _cross_scalar(p, q, r1, r2):
    t = p ^ _rotl16_scalar(q, r1)
    q = q ^ _rotl16_scalar(t, r2)
    p = t
    return p, q


def _cross_np(p, q, r1, r2):
    t = p ^ _rotl16_np(q, r1)
    q = q ^ _rotl16_np(t, r2)
    p = t
    return p, q


def mix_lane4_s1_const_scalar(val, key):
    val &= (1 << 64) - 1
    key &= (1 << 64) - 1
    x = val ^ key
    a, b, c, d = (x & M16), (x >> 16) & M16, (x >> 32) & M16, (x >> 48) & M16
    ca, cb, cc, cd = LANE_CONSTS
    a, b, c, d = (a * ca) & M16, (b * cb) & M16, (c * cc) & M16, (d * cd) & M16
    a, b = _cross_scalar(a, b, 5, 9)
    c, d = _cross_scalar(c, d, 5, 9)
    a, b, c, d = b, c, d, a
    a ^= ca; b ^= cb; c ^= cc; d ^= cd
    return (d << 48) | (c << 32) | (b << 16) | a


def mix_lane4_s1_const_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    a = x & U64(M16)
    b = (x >> U64(16)) & U64(M16)
    c = (x >> U64(32)) & U64(M16)
    d = (x >> U64(48)) & U64(M16)
    ca, cb, cc, cd = LANE_CONSTS
    a = (a * U64(ca)) & U64(M16)
    b = (b * U64(cb)) & U64(M16)
    c = (c * U64(cc)) & U64(M16)
    d = (d * U64(cd)) & U64(M16)
    a, b = _cross_np(a, b, 5, 9)
    c, d = _cross_np(c, d, 5, 9)
    a, b, c, d = b, c, d, a
    a = a ^ U64(ca); b = b ^ U64(cb); c = c ^ U64(cc); d = d ^ U64(cd)
    return (d << U64(48)) | (c << U64(32)) | (b << U64(16)) | a


if __name__ == "__main__":
    check_model_equiv(mix_lane4_s1_const_scalar, mix_lane4_s1_const_np,
                      "lane4_s1_const")
