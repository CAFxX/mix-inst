"""Round 4, family X: 64-bit Feistel with Simon/Simeck-like AND-rotation F.

Untried primitive: F built from 1 AND + rotations (no S-box, no mult, no add).
Feistel => bijective for fixed key regardless of F.

  F_simeck(h) = (ROTL32(h,1) & ROTL32(h,5)) ^ ROTL32(h,2)
  F_simon (h) = (ROTL32(h,1) & ROTL32(h,8)) ^ ROTL32(h,2)
  F_dbland(h) = ((r1&r5)^r2) ^ ((r7&r13)^r11)   (two AND terms)

Round: (L,R) -> (R, L ^ F(R) ^ rk[i]); rk[i] = ROTL32(key_lo,7*(i+1)) ^ RC32[i].
x = val ^ key; split; even #rounds => out = {L_R, R_R} directly.

Bijectivity (fixed key): standard Feistel => permutation of 2^64.
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import (U64, MASK64, check_model_equiv, bijectivity_spotcheck)

M32 = np.uint64(0xFFFFFFFF)
_RC_MUL = 0x9E3779B9


def _rotl32_np(v, r):
    r = int(r) & 31
    v = np.asarray(v, dtype=np.uint64) & M32
    if r == 0:
        return v
    return (((v << np.uint64(r)) | (v >> np.uint64(32 - r))) & M32)


def _rk32_np(klo, i):
    return (_rotl32_np(klo, 7 * (i + 1)) ^ np.uint64(((i + 1) * _RC_MUL) & 0xFFFFFFFF)) & M32


def _F_simeck_np(h):
    h = np.asarray(h, dtype=np.uint64) & M32
    return ((_rotl32_np(h, 1) & _rotl32_np(h, 5)) ^ _rotl32_np(h, 2)) & M32


def _F_simon_np(h):
    h = np.asarray(h, dtype=np.uint64) & M32
    return ((_rotl32_np(h, 1) & _rotl32_np(h, 8)) ^ _rotl32_np(h, 2)) & M32


def _F_dbland_np(h):
    h = np.asarray(h, dtype=np.uint64) & M32
    t1 = (_rotl32_np(h, 1) & _rotl32_np(h, 5)) ^ _rotl32_np(h, 2)
    t2 = (_rotl32_np(h, 7) & _rotl32_np(h, 13)) ^ _rotl32_np(h, 11)
    return (t1 ^ t2) & M32


def _feistel_np(val, key, rounds, F):
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    klo = k & M32
    L = (x >> np.uint64(32)) & M32
    R = x & M32
    for i in range(rounds):
        rk = _rk32_np(klo, i)
        nL = R
        nR = (L ^ F(R) ^ rk) & M32
        L, R = nL, nR
    return ((L << np.uint64(32)) | R) & MASK64


def mix_simeck_f10_np(val, key):
    return _feistel_np(val, key, 10, _F_simeck_np)


def mix_simon_f10_np(val, key):
    return _feistel_np(val, key, 10, _F_simon_np)


def mix_simeck_f12_np(val, key):
    return _feistel_np(val, key, 12, _F_simeck_np)


def mix_dbland_f8_np(val, key):
    return _feistel_np(val, key, 8, _F_dbland_np)


# ---- scalar versions (for model-equivalence check) ----
def _rotl32_s(v, r):
    r &= 31
    v &= 0xFFFFFFFF
    return (((v << r) | (v >> (32 - r))) & 0xFFFFFFFF) if r else v


def _rk32_s(klo, i):
    return (_rotl32_s(klo, 7 * (i + 1)) ^ (((i + 1) * _RC_MUL) & 0xFFFFFFFF)) & 0xFFFFFFFF


def _F_simeck_s(h):
    h &= 0xFFFFFFFF
    return ((_rotl32_s(h, 1) & _rotl32_s(h, 5)) ^ _rotl32_s(h, 2)) & 0xFFFFFFFF


def _F_simon_s(h):
    h &= 0xFFFFFFFF
    return ((_rotl32_s(h, 1) & _rotl32_s(h, 8)) ^ _rotl32_s(h, 2)) & 0xFFFFFFFF


def _F_dbland_s(h):
    h &= 0xFFFFFFFF
    t1 = ((_rotl32_s(h, 1) & _rotl32_s(h, 5)) ^ _rotl32_s(h, 2)) & 0xFFFFFFFF
    t2 = ((_rotl32_s(h, 7) & _rotl32_s(h, 13)) ^ _rotl32_s(h, 11)) & 0xFFFFFFFF
    return (t1 ^ t2) & 0xFFFFFFFF


def _feistel_s(val, key, rounds, F):
    x = (val ^ key) & 0xFFFFFFFFFFFFFFFF
    klo = key & 0xFFFFFFFF
    L = (x >> 32) & 0xFFFFFFFF
    R = x & 0xFFFFFFFF
    for i in range(rounds):
        rk = _rk32_s(klo, i)
        nL = R
        nR = (L ^ F(R) ^ rk) & 0xFFFFFFFF
        L, R = nL, nR
    return ((L << 32) | R) & 0xFFFFFFFFFFFFFFFF


def mix_simeck_f10_s(v, k): return _feistel_s(v, k, 10, _F_simeck_s)
def mix_simon_f10_s(v, k): return _feistel_s(v, k, 10, _F_simon_s)
def mix_simeck_f12_s(v, k): return _feistel_s(v, k, 12, _F_simeck_s)
def mix_dbland_f8_s(v, k): return _feistel_s(v, k, 8, _F_dbland_s)


if __name__ == "__main__":
    for s, n in [(mix_simeck_f10_s, mix_simeck_f10_np),
                 (mix_simon_f10_s, mix_simon_f10_np),
                 (mix_simeck_f12_s, mix_simeck_f12_np),
                 (mix_dbland_f8_s, mix_dbland_f8_np)]:
        check_model_equiv(s, n, n.__name__)
        bijectivity_spotcheck(n, n.__name__)
