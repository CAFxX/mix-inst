"""Round 11 numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round11/gen_r11.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template (fixed for round 11): 6-round Feistel, no whitening,
  F = S-box layer -> x^rotl32(x,a)^rotl32(x,b) -> ^rk32
with the affine r7/r8/r9 key schedule (rk32 = low32(rotl64(k,13*(i+1)) ^ (i+1)*GOLDEN64)).

Round 11 attacks the one primitive not yet varied: the S-box.
  F1: 4-bit S-box sweep: PRESENT / GIFT / SKINNY-4 / Piccolo x {(3,11),(7,13)}
  F2: 8-bit S-box probe: 4x SKINNY-8 S-boxes at (3,11)
  F3: heterogeneous: alternating S1 / PRESENT S-boxes per nibble at (3,11)

S-box tables live in round11/sboxes.json (verified vs primary cipher specs).
"""
import json
import os

import numpy as np

with open(os.path.join(os.path.dirname(__file__), "..", "sboxes.json")) as f:
    _SB = json.load(f)

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]  # THF/Blink (r7-r10)
SBOX4 = {
    "s1": np.array(S1, dtype=np.uint64),
    "present4": np.array(_SB["present4"], dtype=np.uint64),
    "gift4": np.array(_SB["gift4"], dtype=np.uint64),
    "skinny4": np.array(_SB["skinny4"], dtype=np.uint64),
    "piccolo4": np.array(_SB["piccolo4"], dtype=np.uint64),
}
SBOX8 = {
    "skinny8": np.array(_SB["skinny8"], dtype=np.uint64),
}
for _k, _v in SBOX4.items():
    assert len(set(int(x) for x in _v)) == 16, _k
for _k, _v in SBOX8.items():
    assert len(set(int(x) for x in _v)) == 256, _k

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


def _sbox_layer32_np(x, sbox):
    """Eight 4-bit S-boxes over the 32-bit word (nibble i -> sbox)."""
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(sbox, nib) << np.uint64(4 * i)
    return out & MASK32


def _sbox_layer32_mix_np(x, sbox_even, sbox_odd):
    """Heterogeneous: sbox_even on even nibbles, sbox_odd on odd nibbles."""
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        sb = sbox_even if i % 2 == 0 else sbox_odd
        out |= np.take(sb, nib) << np.uint64(4 * i)
    return out & MASK32


def _sbox8_layer32_np(x, sbox8):
    """Four 8-bit S-boxes over the 32-bit word (byte i -> sbox8)."""
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(4):
        byt = ((xv >> np.uint64(8 * i)) & np.uint64(0xFF)).astype(np.int64)
        out |= np.take(sbox8, byt) << np.uint64(8 * i)
    return out & MASK32


def _lin_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


def _rk32_std_np(k, i):
    """Affine schedule (r7/r8/r9): low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64))."""
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32


def _feistel6_nw_np(x, k, F):
    """6-round balanced Feistel, 32-bit halves, {R,L} output, no whitening."""
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 7):
        nR = (L ^ F(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _mk_4bit(name, sbox_key, a, b):
    sb = SBOX4[sbox_key]

    def fn(val, key):
        return _feistel6_nw_np(
            val, key,
            lambda R, rk32: (_lin_np(_sbox_layer32_np(R, sb), a, b) ^ rk32) & MASK32)
    fn.__name__ = name
    return fn


# F1: 4-bit S-box sweep x {(3,11),(7,13)}
r11_feist6_present311_nw = _mk_4bit("r11_feist6_present311_nw", "present4", 3, 11)
r11_feist6_present713_nw = _mk_4bit("r11_feist6_present713_nw", "present4", 7, 13)
r11_feist6_gift311_nw = _mk_4bit("r11_feist6_gift311_nw", "gift4", 3, 11)
r11_feist6_gift713_nw = _mk_4bit("r11_feist6_gift713_nw", "gift4", 7, 13)
r11_feist6_sk4311_nw = _mk_4bit("r11_feist6_sk4311_nw", "skinny4", 3, 11)
r11_feist6_sk4713_nw = _mk_4bit("r11_feist6_sk4713_nw", "skinny4", 7, 13)
r11_feist6_piccolo311_nw = _mk_4bit("r11_feist6_piccolo311_nw", "piccolo4", 3, 11)
r11_feist6_piccolo713_nw = _mk_4bit("r11_feist6_piccolo713_nw", "piccolo4", 7, 13)


# F2: 8-bit S-box probe (4x SKINNY-8 at (3,11))
def r11_feist6_sk8311_nw(val, key):
    sb8 = SBOX8["skinny8"]

    def F(R, rk32):
        return (_lin_np(_sbox8_layer32_np(R, sb8), 3, 11) ^ rk32) & MASK32

    return _feistel6_nw_np(val, key, F)


# F3: heterogeneous — alternating S1 (even nibbles) / PRESENT (odd nibbles)
def r11_feist6_s1mix311_nw(val, key):
    s1 = SBOX4["s1"]
    pr = SBOX4["present4"]

    def F(R, rk32):
        return (_lin_np(_sbox_layer32_mix_np(R, s1, pr), 3, 11) ^ rk32) & MASK32

    return _feistel6_nw_np(val, key, F)


CANDIDATES_R11 = [
    ("r11_feist6_present311_nw", r11_feist6_present311_nw,
     "6r Feistel, F=PRESENT-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_present713_nw", r11_feist6_present713_nw,
     "6r Feistel, F=PRESENT-Sbox+lin(7,13), NO whitening"),
    ("r11_feist6_gift311_nw", r11_feist6_gift311_nw,
     "6r Feistel, F=GIFT-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_gift713_nw", r11_feist6_gift713_nw,
     "6r Feistel, F=GIFT-Sbox+lin(7,13), NO whitening"),
    ("r11_feist6_sk4311_nw", r11_feist6_sk4311_nw,
     "6r Feistel, F=SKINNY4-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_sk4713_nw", r11_feist6_sk4713_nw,
     "6r Feistel, F=SKINNY4-Sbox+lin(7,13), NO whitening"),
    ("r11_feist6_piccolo311_nw", r11_feist6_piccolo311_nw,
     "6r Feistel, F=Piccolo-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_piccolo713_nw", r11_feist6_piccolo713_nw,
     "6r Feistel, F=Piccolo-Sbox+lin(7,13), NO whitening"),
    ("r11_feist6_sk8311_nw", r11_feist6_sk8311_nw,
     "6r Feistel, F=4xSKINNY8-Sbox+lin(3,11), NO whitening"),
    ("r11_feist6_s1mix311_nw", r11_feist6_s1mix311_nw,
     "6r Feistel, F=alternating S1/PRESENT per nibble+lin(3,11), NO whitening"),
]
