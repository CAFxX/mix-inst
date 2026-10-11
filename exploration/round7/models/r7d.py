"""Round 7 models (TEAM D): structural variants round 6 did NOT try.

Candidates:
  r7_ufeist48_16 : unbalanced Feistel, L=48/R=16, 8 rounds, 16->48 F
  r7_ufeist16_48 : unbalanced Feistel, L=16/R=48, 8 rounds, 48->16 F
  r7_misty       : 8-round balanced Feistel 32/32, F = 3-round inner Feistel 16/16
  r7_spn_s1rotl  : 4-round 64-bit SPN, S1 nibbles + rotl-xor linear + rk64

S-box S1 (verified permutation): [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]
Round keys: rk(k,i) = rotl64(k,13*(i+1)) ^ ((i+1)*0x9E3779B97F4A7C15), i=1..8
(same as the round-6 winner r6_feist8_spn).
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'round5', 'models'))
from r5 import SBOX_NP, _rk_np

K = np.uint64
S1 = SBOX_NP["s1"]
M16 = K(0xFFFF)
M32 = K(0xFFFFFFFF)
M48 = K(0xFFFFFFFFFFFF)
M64 = K(0xFFFFFFFFFFFFFFFF)


def _rotl64_np(x, n):
    n %= 64
    if n == 0:
        return x & M64
    return (((x << K(n)) | (x >> K(64 - n))) & M64)


def _rotl16_np(x, n):
    n %= 16
    if n == 0:
        return x & M16
    t = (x << K(n)) | (x >> K(16 - n))
    return t & M16


def _rotl4_np(x, n):
    n %= 4
    if n == 0:
        return x & K(0xF)
    t = (x << K(n)) | (x >> K(4 - n))
    return t & K(0xF)


def _sbox_nibbles_np(x, nnib):
    """Apply S1 to the low nnib nibbles of x."""
    out = np.zeros(np.shape(x), dtype=np.uint64)
    for i in range(nnib):
        nib = ((x >> K(4 * i)) & K(0xF)).astype(np.int64)
        out |= np.take(S1, nib) << K(4 * i)
    return out


# ---------------------------------------------------------------------------
# Candidate 1: r7_ufeist48_16 -- unbalanced Feistel, L=48 / R=16, 8 rounds
# Round: newL = (R<<32)|(L>>16), newR = (L&0xFFFF) ^ F(R)
# Inverse: R = newL>>32; L = ((newL&0xFFFFFFFF)<<16) | (newR ^ F(R)).
# F: 16->48: S1 on 4 nibbles -> each nibble expanded to 12 bits via
#     e(n) = n^rotl4(n,1)^rotl4(n,2) replicated x3 -> xor 48-bit rk chunk.
# ---------------------------------------------------------------------------
def _ufeist_F_16to48_np(R16, rk48):
    s = _sbox_nibbles_np(R16 & M16, 4)
    out = np.zeros(np.shape(s), dtype=np.uint64)
    for j in range(4):
        n = (s >> K(4 * j)) & K(0xF)
        e = (n ^ _rotl4_np(n, 1) ^ _rotl4_np(n, 2)) & K(0xF)
        rep = (e | (e << K(4)) | (e << K(8))) & K(0xFFF)
        out |= rep << K(12 * j)
    return (out ^ (rk48 & M48)) & M48


def r7_ufeist48_16_np(V, Kk):
    x = (V ^ Kk) & M64
    L = (x >> K(16)) & M48
    R = x & M16
    for i in range(1, 9):
        F = _ufeist_F_16to48_np(R, _rk_np(Kk, i) & M48)
        nL = (((R << K(32)) | (L >> K(16))) & M48)
        nR = ((L & M16) ^ F) & M16
        L, R = nL, nR
    return ((L << K(16)) | R) & M64


def r7_ufeist48_16(val, key):
    return int(r7_ufeist48_16_np(K(val), K(key)))


# ---------------------------------------------------------------------------
# Candidate 2: r7_ufeist16_48 -- mirror: L=16 / R=48, 8 rounds
# Round: newL = R>>32, newR = ((R&0xFFFFFFFF)<<16) | ((L ^ F(R))&0xFFFF)
# Inverse: R = (newL<<32)|(newR>>16); L = (newR&0xFFFF) ^ F(R).
# F: 48->16: S1 on 12 nibbles -> xor-fold 48->16 -> x^rotl16(x,3)^rotl16(x,7)
#     -> xor 16-bit rk chunk.
# ---------------------------------------------------------------------------
def _ufeist_F_48to16_np(R48, rk16):
    s = _sbox_nibbles_np(R48 & M48, 12)
    f = ((s >> K(32)) ^ (s >> K(16)) ^ s) & M16
    f = (f ^ _rotl16_np(f, 3) ^ _rotl16_np(f, 7)) & M16
    return (f ^ (rk16 & M16)) & M16


def r7_ufeist16_48_np(V, Kk):
    x = (V ^ Kk) & M64
    L = (x >> K(48)) & M16
    R = x & M48
    for i in range(1, 9):
        F = _ufeist_F_48to16_np(R, _rk_np(Kk, i) & M16)
        nL = (R >> K(32)) & M16
        nR = ((((R & K(0xFFFFFFFF)) << K(16)) | ((L ^ F) & M16)) & M48)
        L, R = nL, nR
    return ((L << K(48)) | R) & M64


def r7_ufeist16_48(val, key):
    return int(r7_ufeist16_48_np(K(val), K(key)))


# ---------------------------------------------------------------------------
# Candidate 3: r7_misty -- 8-round balanced Feistel 32/32, F contains a
# 3-round inner Feistel on 16/16 halves with S1 S-boxes (recursive).
# F(R32, rk64): (a16,b16) = split(R); 3x (a,b) = (b, a ^ G(b)),
#   G(b) = sbox16(b) ^ subkey_j, subkey_j = (rk64>>(16*j))&0xFFFF;
#   F_out = (a<<16)|b, then xor (rk64 & 0xFFFFFFFF).
# Outer round identical to winner: (L,R) = (R, L^F(R)). Both inner and outer
# Feistel rounds are invertible for ANY round function.
# ---------------------------------------------------------------------------
def _g16_np(b, rk16):
    s = _sbox_nibbles_np(b & M16, 4)
    return (s ^ (rk16 & M16)) & M16


def _misty_F_np(R32, rk64):
    a = (R32 >> K(16)) & M16
    b = R32 & M16
    for j in range(3):
        rk16 = (rk64 >> K(16 * j)) & M16
        na = b
        nb = (a ^ _g16_np(b, rk16)) & M16
        a, b = na, nb
    out = ((a << K(16)) | b) & M32
    return (out ^ (rk64 & M32)) & M32


def r7_misty_np(V, Kk):
    x = (V ^ Kk) & M64
    L = (x >> K(32)) & M32
    R = x & M32
    for i in range(1, 9):
        F = _misty_F_np(R, _rk_np(Kk, i))
        nL = R
        nR = (L ^ F) & M32
        L, R = nL, nR
    return ((R << K(32)) | L) & M64


def r7_misty(val, key):
    return int(r7_misty_np(K(val), K(key)))


# ---------------------------------------------------------------------------
# Candidate 4: r7_spn_s1rotl -- 4-round 64-bit SPN.
# Round: S1 on 16 nibbles -> x^rotl64(x,7)^rotl64(x,13) -> ^rk64.
# Whiten in/out with key.
# NOTE: the task's proposed linear x^rotl64(x,7)^rotl64(x,13)^rotl64(x,29) is
# PROVABLY SINGULAR: over GF(2), x^64+1 = (x+1)^64, so ANY rotation-XOR sum
# with an even number of terms is divisible by (x+1) (rank 63, verified).
# Dropped rotl64(x,29); the 3-term map x^rotl64(x,7)^rotl64(x,13) is always
# invertible (gcd(1+x^7+x^13,(x+1)^64)=1 since the polynomial has odd weight).
# ---------------------------------------------------------------------------
def _lin64_s1rotl_np(x):
    return (x ^ _rotl64_np(x, 7) ^ _rotl64_np(x, 13)) & M64


def r7_spn_s1rotl_np(V, Kk):
    x = (V ^ Kk) & M64
    for i in range(1, 5):
        x = _sbox_nibbles_np(x, 16)
        x = _lin64_s1rotl_np(x)
        x = (x ^ _rk_np(Kk, i)) & M64
    return (x ^ Kk) & M64


def r7_spn_s1rotl(val, key):
    return int(r7_spn_s1rotl_np(K(val), K(key)))


CANDIDATES_R7D = [
    ("r7_ufeist48_16", r7_ufeist48_16, r7_ufeist48_16_np,
     "unbalanced Feistel 48/16, 8r, 16->48 F (sbox+replicate-xor expand)"),
    ("r7_ufeist16_48", r7_ufeist16_48, r7_ufeist16_48_np,
     "unbalanced Feistel 16/48, 8r, 48->16 F (sbox+xor-fold compress)"),
    ("r7_misty", r7_misty, r7_misty_np,
     "8r balanced Feistel 32/32, F = 3r inner Feistel 16/16 w/ S1"),
    ("r7_spn_s1rotl", r7_spn_s1rotl, r7_spn_s1rotl_np,
     "4r 64-bit SPN: S1 nibbles + x^rotl64(x,7)^rotl64(x,13) + rk64"),
]
