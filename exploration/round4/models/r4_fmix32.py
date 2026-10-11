"""Round 4, family H: keyed 32-bit Murmur-fmix on halves with bijective cross.

Untried: fmix32 has proven constants and excellent avalanche; two 32-bit
const mults are far cheaper than one 64-bit. Keyed per half, then a
Feistel-style cross.

  H1 fmix32h_a: x=val^key; a=lo32,b=hi32;
     a=fmix32(a^ka); b=fmix32(b^kb); a^=b^kc; b^=ROTL32(a,9)^kd; out={b,a}
  H2 fmix32h_b: cross; fmix; cross (sandwich):
     a^=b; b^=ROTL32(a,3)^kc0; a=fmix32(a^ka); b=fmix32(b^kb);
     a^=b^kc1; b^=ROTL32(a,9)^kd1; out={b,a}

fmix32(h,k): h^=k; h^=h>>16; h*=0x85ebca6b; h^=h>>13; h*=0xc2b2ae35; h^=h>>16.
Final xorshift repairs the odd-mult bit-0 law (bit 0 = h[0]^h[16], nonlinear).

Bijectivity (fixed key): every fmix32 step bijective on 32 bits (xorshift-down
triangular; odd mult); each cross half-step bijective (a^=b^c; b^=F(a)^d).
Composition => permutation of 2^64.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, check_model_equiv, bijectivity_spotcheck)

M32 = np.uint64(0xFFFFFFFF)
_C1 = np.uint64(0x85EBCA6B)
_C2 = np.uint64(0xC2B2AE35)


def _rotl32_np(v, r):
    r = int(r) & 31
    v = np.asarray(v, dtype=np.uint64) & M32
    if r == 0:
        return v
    return (((v << np.uint64(r)) | (v >> np.uint64(32 - r))) & M32)


def _fmix32_np(h, k):
    h = (np.asarray(h, dtype=np.uint64) ^ np.asarray(k, dtype=np.uint64)) & M32
    h = (h ^ (h >> np.uint64(16))) & M32
    h = (h * _C1) & M32
    h = (h ^ (h >> np.uint64(13))) & M32
    h = (h * _C2) & M32
    h = (h ^ (h >> np.uint64(16))) & M32
    return h


def mix_fmix32h_a_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    a = x & M32
    b = (x >> np.uint64(32)) & M32
    ka = k & M32
    kb = (k >> np.uint64(32)) & M32
    a = _fmix32_np(a, ka)
    b = _fmix32_np(b, kb)
    kc = _rotl32_np(ka ^ kb, 7)
    kd = kc ^ np.uint64(0x9E3779B9)
    a = (a ^ b ^ kc) & M32
    b = (b ^ _rotl32_np(a, 9) ^ kd) & M32
    return (((b & M32) << np.uint64(32)) | (a & M32)) & MASK64


def mix_fmix32h_b_np(val, key):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    a = x & M32
    b = (x >> np.uint64(32)) & M32
    ka = k & M32
    kb = (k >> np.uint64(32)) & M32
    kc0 = _rotl32_np(ka ^ kb, 3)
    a = (a ^ b) & M32
    b = (b ^ _rotl32_np(a, 3) ^ kc0) & M32
    a = _fmix32_np(a, ka)
    b = _fmix32_np(b, kb)
    kc1 = _rotl32_np(ka ^ kb, 7)
    kd1 = kc1 ^ np.uint64(0x9E3779B9)
    a = (a ^ b ^ kc1) & M32
    b = (b ^ _rotl32_np(a, 9) ^ kd1) & M32
    return (((b & M32) << np.uint64(32)) | (a & M32)) & MASK64


# ---- scalar versions ----
def _rotl32_s(v, r):
    r &= 31
    v &= 0xFFFFFFFF
    return (((v << r) | (v >> (32 - r))) & 0xFFFFFFFF) if r else v


def _fmix32_s(h, k):
    h = (h ^ k) & 0xFFFFFFFF
    h = (h ^ (h >> 16)) & 0xFFFFFFFF
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) & 0xFFFFFFFF
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    return (h ^ (h >> 16)) & 0xFFFFFFFF


def mix_fmix32h_a_s(v, k):
    x = (v ^ k) & 0xFFFFFFFFFFFFFFFF
    a, b = x & 0xFFFFFFFF, (x >> 32) & 0xFFFFFFFF
    ka, kb = k & 0xFFFFFFFF, (k >> 32) & 0xFFFFFFFF
    a, b = _fmix32_s(a, ka), _fmix32_s(b, kb)
    kc = _rotl32_s(ka ^ kb, 7)
    kd = (kc ^ 0x9E3779B9) & 0xFFFFFFFF
    a = (a ^ b ^ kc) & 0xFFFFFFFF
    b = (b ^ _rotl32_s(a, 9) ^ kd) & 0xFFFFFFFF
    return ((b << 32) | a) & 0xFFFFFFFFFFFFFFFF


def mix_fmix32h_b_s(v, k):
    x = (v ^ k) & 0xFFFFFFFFFFFFFFFF
    a, b = x & 0xFFFFFFFF, (x >> 32) & 0xFFFFFFFF
    ka, kb = k & 0xFFFFFFFF, (k >> 32) & 0xFFFFFFFF
    kc0 = _rotl32_s(ka ^ kb, 3)
    a = (a ^ b) & 0xFFFFFFFF
    b = (b ^ _rotl32_s(a, 3) ^ kc0) & 0xFFFFFFFF
    a, b = _fmix32_s(a, ka), _fmix32_s(b, kb)
    kc1 = _rotl32_s(ka ^ kb, 7)
    kd1 = (kc1 ^ 0x9E3779B9) & 0xFFFFFFFF
    a = (a ^ b ^ kc1) & 0xFFFFFFFF
    b = (b ^ _rotl32_s(a, 9) ^ kd1) & 0xFFFFFFFF
    return ((b << 32) | a) & 0xFFFFFFFFFFFFFFFF


if __name__ == "__main__":
    for s, n in [(mix_fmix32h_a_s, mix_fmix32h_a_np),
                 (mix_fmix32h_b_s, mix_fmix32h_b_np)]:
        check_model_equiv(s, n, n.__name__)
        bijectivity_spotcheck(n, n.__name__)
