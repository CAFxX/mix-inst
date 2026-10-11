"""Round 7 (TEAM B): F-function S-box variants of r6_feist8_spn.

Fixed: 8-round Feistel, val^key whitening, rotl7/rotl13 XOR linear layer in F,
rk schedule = rotl64(k,13*(i+1)) ^ ((i+1)*0x9E3779B97F4A7C15).
Varies only the S-box choice / S-box-layer count inside F.

S-box tables (4-bit, 16 entries):
  S1    = [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]  (round-6 winner)
  GIFT  = [0x1,0xA,0x4,0xC,0x6,0xF,0x3,0x9,0x2,0xD,0xB,0x7,0x5,0x0,0x8,0xE]
  MSB0  = Midori64 Sb0 = [0xC,0xA,0xD,0x3,0xE,0xB,0xF,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6]

Candidates:
  r7_feist8_gift      F = GIFT-layer -> linear -> GIFT-layer -> ^rk32
  r7_feist8_s1_1sbox  F = S1-layer -> linear -> ^rk32            (cheap)
  r7_feist8_s1_3sbox  F = S1 -> lin -> S1 -> lin -> S1 -> ^rk32   (strong)
  r7_feist8_msb0      F = MSB0-layer -> linear -> MSB0-layer -> ^rk32
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'round5', 'models'))
from r5 import _rk_np  # noqa: F401  (imported for schedule consistency)

S1   = [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]
GIFT = [0x1,0xA,0x4,0xC,0x6,0xF,0x3,0x9,0x2,0xD,0xB,0x7,0x5,0x0,0x8,0xE]
MSB0 = [0xC,0xA,0xD,0x3,0xE,0xB,0xF,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6]
for _n, _t in (("S1", S1), ("GIFT", GIFT), ("MSB0", MSB0)):
    assert len(set(_t)) == 16, _n

SBOXES = {"s1": S1, "gift": GIFT, "msb0": MSB0}
MASK32 = np.uint64(0xFFFFFFFF)


def _sbox_layer32_np(x, sb):
    """Apply 4-bit S-box to the 8 nibbles of a 32-bit word."""
    out = np.zeros_like(x)
    xv = x.copy()
    sba = np.array(sb, dtype=np.uint64)
    for i in range(8):
        nib = ((xv >> np.uint64(4*i)) & np.uint64(0xF)).astype(np.int64)
        snib = np.take(sba, nib)
        out |= snib << np.uint64(4*i)
    return out & MASK32


def _lin32_np(x):
    """x ^ rotl32(x,7) ^ rotl32(x,13), 32-bit."""
    r7 = (((x << np.uint64(7)) | (x >> np.uint64(25))) & MASK32)
    r13 = (((x << np.uint64(13)) | (x >> np.uint64(19))) & MASK32)
    return (x ^ r7 ^ r13) & MASK32


def _F_np(R, rk64, sbox, nlayers):
    """F-function: nlayers of (S-box layer [+ linear between layers]) + ^rk32.

    nlayers=1: S -> lin -> ^rk32
    nlayers=2: S -> lin -> S -> ^rk32
    nlayers=3: S -> lin -> S -> lin -> S -> ^rk32
    """
    R = R & MASK32
    for j in range(nlayers):
        R = _sbox_layer32_np(R, sbox)
        if j < nlayers - 1:
            R = _lin32_np(R)
    if nlayers == 1:
        R = _lin32_np(R)  # keep linear present even for 1 layer
    return (R ^ (rk64 & MASK32)) & MASK32


def _feistel8_np(x, k, sbox, nlayers):
    """8-round Feistel with val^key whitening and {R,L} output (no final swap)."""
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    L = (L ^ ((k >> np.uint64(32)) & MASK32)) & MASK32
    R = (R ^ (k & MASK32)) & MASK32
    for i in range(1, 9):
        rkv = _rk_np(k, i)
        F = _F_np(R, rkv, sbox, nlayers)
        L, R = R, (L ^ F) & MASK32
    return (R << np.uint64(32)) | L


def r7_feist8_gift(val, key):
    return _feistel8_np(val, key, GIFT, 2)

def r7_feist8_s1_1sbox(val, key):
    return _feistel8_np(val, key, S1, 1)

def r7_feist8_s1_3sbox(val, key):
    return _feistel8_np(val, key, S1, 3)

def r7_feist8_msb0(val, key):
    return _feistel8_np(val, key, MSB0, 2)


CANDIDATES_R7 = [
    ("r7_feist8_gift",     r7_feist8_gift,     "8r Feistel, F=GIFT S-box x2 + rotl7/13 lin"),
    ("r7_feist8_s1_1sbox", r7_feist8_s1_1sbox, "8r Feistel, F=S1 x1 + rotl7/13 lin (cheap)"),
    ("r7_feist8_s1_3sbox", r7_feist8_s1_3sbox, "8r Feistel, F=S1 x3 + rotl7/13 lin (strong)"),
    ("r7_feist8_msb0",     r7_feist8_msb0,     "8r Feistel, F=Midori-Sb0 x2 + rotl7/13 lin"),
]
