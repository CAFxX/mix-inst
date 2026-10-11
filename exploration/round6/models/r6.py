"""Round 6 models: deeper, stronger constructions for the LIN/DIFF gate.

Strategic shift: delay bar is now relative (<=0.9x multiplier, ~93u in current
flow). Binding constraint is LIN/DIFF, not delay. xorshift64 pre-diffusion
abandoned as core primitive (round-5 finding: 3 SPN rounds after single
xorshift64 are linearly broken, D~4000/4096).

Tracks:
  T1: Deep SPNs (5-6 rounds, no xorshift) - PRESENT/GIFT/SKINNY/Midori-Sb0
  T2: Feistel with SPN F-functions
  T3: SPN sandwich with chi middle layer
  T4: chi as post-layer on SPN core
  T5: Heterogeneous per-round functions
  T6: Lai-Massey with SPN F
"""

import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'round5', 'models'))
from r5 import (
    SBOXES, PRESENT, MIDORI_SB0,
    _spn_rounds, _shuffle_np, _midori_M_np, _rk_np,
)

# Additional S-boxes
GIFT_SBOX = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9,
             0x2, 0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]
SKINNY_SBOX = [0xC, 0x6, 0x9, 0x0, 0x1, 0xA, 0x2, 0xB,
               0x3, 0x8, 0x5, 0xD, 0x4, 0xE, 0x7, 0xF]

SBOXES["gift"] = GIFT_SBOX
SBOXES["skinny"] = SKINNY_SBOX

K = np.uint64

def _sbox_layer_np(x, sbox_name):
    """Apply 4-bit S-box to all 16 nibbles."""
    sb = SBOXES[sbox_name]
    out = np.zeros_like(x)
    for i in range(16):
        nib = (x >> np.uint64(4*i)) & np.uint64(0xF)
        # Vectorized lookup
        out |= np.uint64(sb[0]) << np.uint64(0)  # placeholder, do properly below
    # Proper vectorized implementation
    out = np.zeros_like(x)
    xv = x.copy()
    for i in range(16):
        nib = ((xv >> np.uint64(4*i)) & np.uint64(0xF)).astype(np.int64)
        # Use np.take for vectorized lookup
        snib = np.take(np.array(sb, dtype=np.uint64), nib)
        out |= snib << np.uint64(4*i)
    return out

def _present_player_np(x):
    """PRESENT bit permutation."""
    out = np.zeros_like(x)
    for i in range(64):
        bit = (x >> np.uint64(i)) & np.uint64(1)
        j = (16*i) % 63 if i < 63 else 63
        out |= bit << np.uint64(j)
    return out

def _chi64_np(x):
    """Keccak chi on 64 bits (as 64 parallel 1-bit rows, or 5-bit rows)."""
    # Use 5-bit rows: 64 bits = 12 full rows (60 bits) + 4 bits
    # Simpler: apply chi as x[i] ^= ~x[i+1] & x[i+2] cyclically on 64 bits
    # This is the "cyclic chi" - treat as 64-bit circle
    x1 = ((x << np.uint64(1)) | (x >> np.uint64(63)))
    x2 = ((x << np.uint64(2)) | (x >> np.uint64(62)))
    return x ^ (~x1 & x2)

def _spn_round_np(x, rk, sbox_name, linear="midori"):
    """Single SPN round: S-box layer + linear layer + round key."""
    x = _sbox_layer_np(x, sbox_name)
    if linear == "midori":
        x = _midori_M_np(x)
    elif linear == "present":
        x = _present_player_np(x)
    elif linear == "shuffle":
        x = _shuffle_np(x)
    return x ^ rk

def _deep_spn_np(x, k, nrounds, sbox_name, linear="midori"):
    """Deep SPN without xorshift pre-diffusion."""
    # Initial whitening
    x = x ^ k
    for i in range(nrounds):
        rk = _rk_np(k, i+1)
        x = _spn_round_np(x, rk, sbox_name, linear)
    # Final S-box (no linear, no key - or with key?)
    x = _sbox_layer_np(x, sbox_name)
    x = x ^ _rk_np(k, nrounds+1)
    return x

# ---- T1: Deep SPNs ----
def r6_spn5_s1(val, key):
    return _deep_spn_np(val, key, 5, "s1", "midori")

def r6_spn6_s1(val, key):
    return _deep_spn_np(val, key, 6, "s1", "midori")

def r6_spn5_present(val, key):
    return _deep_spn_np(val, key, 5, "present", "present")

def r6_spn5_gift(val, key):
    return _deep_spn_np(val, key, 5, "gift", "midori")

def r6_spn5_skinny(val, key):
    return _deep_spn_np(val, key, 5, "skinny", "midori")

def r6_spn5_midori(val, key):
    return _deep_spn_np(val, key, 5, "midori", "midori")

# ---- T2: Feistel with SPN F-functions ----
def _feist_F_spn_np(R, rk, sbox_name="s1"):
    """F-function: 2-round SPN on 32 bits (clean 32-bit)."""
    MASK32 = np.uint64(0xFFFFFFFF)
    R = R & MASK32
    # S-box layer 1 (only low 8 nibbles)
    R32 = np.zeros_like(R)
    sb = SBOXES[sbox_name]
    sb_arr = np.array(sb, dtype=np.uint64)
    for i in range(8):
        nib = ((R >> np.uint64(4*i)) & np.uint64(0xF)).astype(np.int64)
        snib = np.take(sb_arr, nib)
        R32 |= snib << np.uint64(4*i)
    R = R32
    # Diffusion: rotate-xor (32-bit)
    R = (R ^ (((R << np.uint64(7)) | (R >> np.uint64(25))) & MASK32)
           ^ (((R << np.uint64(13)) | (R >> np.uint64(19))) & MASK32)) & MASK32
    # S-box layer 2
    R32 = np.zeros_like(R)
    for i in range(8):
        nib = ((R >> np.uint64(4*i)) & np.uint64(0xF)).astype(np.int64)
        snib = np.take(sb_arr, nib)
        R32 |= snib << np.uint64(4*i)
    R = R32
    return (R ^ (rk & MASK32)) & MASK32

def _feistel_np(x, k, nrounds, sbox_name="s1"):
    """Feistel network on 64 bits."""
    L = (x >> np.uint64(32)) & np.uint64(0xFFFFFFFF)
    R = x & np.uint64(0xFFFFFFFF)
    # Initial whitening
    L ^= (k >> np.uint64(32)) & np.uint64(0xFFFFFFFF)
    R ^= k & np.uint64(0xFFFFFFFF)
    for i in range(nrounds):
        rk = _rk_np(k, i+1)
        F = _feist_F_spn_np(R, rk, sbox_name)
        L, R = R, L ^ F
    # Final swap (or not) and combine
    return ((R << np.uint64(32)) | L)

def r6_feist8_spn(val, key):
    return _feistel_np(val, key, 8, "s1")

def r6_feist12_spn(val, key):
    return _feistel_np(val, key, 12, "s1")

def r6_feist8_present(val, key):
    return _feistel_np(val, key, 8, "present")

# ---- T3: SPN sandwich with chi middle ----
def r6_spn3_chi_spn3(val, key):
    """SPN(3) -> chi -> SPN(3)."""
    x = val ^ key
    for i in range(3):
        x = _spn_round_np(x, _rk_np(key, i+1), "s1", "midori")
    x = _chi64_np(x)
    x = x ^ _rk_np(key, 4)
    for i in range(3):
        x = _spn_round_np(x, _rk_np(key, 5+i), "s1", "midori")
    x = _sbox_layer_np(x, "s1")
    return x ^ _rk_np(key, 8)

# ---- T4: chi post-layer on SPN core ----
def r6_spn5_chi(val, key):
    """5-round SPN + chi final layer."""
    x = _deep_spn_np(val, key, 5, "s1", "midori")
    x = _chi64_np(x)
    return x ^ _rk_np(key, 99)

def r6_spn4_chi(val, key):
    """4-round SPN + chi final layer."""
    x = _deep_spn_np(val, key, 4, "s1", "midori")
    x = _chi64_np(x)
    return x ^ _rk_np(key, 99)

# ---- T5: Heterogeneous per-round ----
def r6_hetero6(val, key):
    """6 rounds, different S-box each round."""
    sboxes = ["s1", "present", "midori", "gift", "skinny", "s1"]
    x = val ^ key
    for i in range(6):
        x = _spn_round_np(x, _rk_np(key, i+1), sboxes[i], "midori")
    x = _sbox_layer_np(x, "s1")
    return x ^ _rk_np(key, 7)

def r6_hetero5(val, key):
    """5 rounds, different S-box each round."""
    sboxes = ["s1", "present", "midori", "gift", "skinny"]
    x = val ^ key
    for i in range(5):
        x = _spn_round_np(x, _rk_np(key, i+1), sboxes[i], "midori")
    x = _sbox_layer_np(x, "s1")
    return x ^ _rk_np(key, 6)

# ---- T6: Lai-Massey with SPN F ----
def _lm_F_spn_np(d, rk):
    """F-function for Lai-Massey: 2-round SPN."""
    d = _sbox_layer_np(d, "s1")
    d = _midori_M_np(d)
    d = d ^ rk
    d = _sbox_layer_np(d, "s1")
    return d

def _laimassey_np(x, k, nrounds):
    """Lai-Massey on 64 bits."""
    L = (x >> np.uint64(32)) & np.uint64(0xFFFFFFFF)
    R = x & np.uint64(0xFFFFFFFF)
    # Extend to 64-bit for F (use full 64-bit F on difference)
    L64 = L | (L << np.uint64(32))
    R64 = R | (R << np.uint64(32))
    # Actually, Lai-Massey typically works on halves; let's do proper 32-bit
    # Simpler: use 64-bit halves via splitting differently
    # For now, implement standard Lai-Massey on 32-bit halves with 32-bit F
    L = (x >> np.uint64(32)) & np.uint64(0xFFFFFFFF)
    R = x & np.uint64(0xFFFFFFFF)
    L ^= (k >> np.uint64(32)) & np.uint64(0xFFFFFFFF)
    R ^= k & np.uint64(0xFFFFFFFF)
    for i in range(nrounds):
        rk = _rk_np(k, i+1) & np.uint64(0xFFFFFFFF)
        d = (L ^ R) & np.uint64(0xFFFFFFFF)
        # F on 32-bit: expand to 64, apply, take low 32
        d64 = np.uint64(d) | (np.uint64(d) << np.uint64(32))
        f64 = _lm_F_spn_np(d64, _rk_np(k, i+1))
        f = f64 & np.uint64(0xFFFFFFFF)
        L, R = R ^ f, L ^ f
    return ((L << np.uint64(32)) | R)

def r6_lm4_spn(val, key):
    return _laimassey_np(val, key, 4)

def r6_lm6_spn(val, key):
    return _laimassey_np(val, key, 6)

# Candidate list
CANDIDATES_R6 = [
    ("r6_spn5_s1", r6_spn5_s1, "T1: 5r SPN S1+MidoriM"),
    ("r6_spn6_s1", r6_spn6_s1, "T1: 6r SPN S1+MidoriM"),
    ("r6_spn5_present", r6_spn5_present, "T1: 5r SPN PRESENT"),
    ("r6_spn5_gift", r6_spn5_gift, "T1: 5r SPN GIFT"),
    ("r6_spn5_skinny", r6_spn5_skinny, "T1: 5r SPN SKINNY"),
    ("r6_spn5_midori", r6_spn5_midori, "T1: 5r SPN MidoriSb0"),
    ("r6_feist8_spn", r6_feist8_spn, "T2: 8r Feistel SPN-F"),
    ("r6_feist12_spn", r6_feist12_spn, "T2: 12r Feistel SPN-F"),
    ("r6_feist8_present", r6_feist8_present, "T2: 8r Feistel PRESENT-F"),
    ("r6_spn3_chi_spn3", r6_spn3_chi_spn3, "T3: SPN3-chi-SPN3 sandwich"),
    ("r6_spn5_chi", r6_spn5_chi, "T4: 5r SPN + chi post"),
    ("r6_spn4_chi", r6_spn4_chi, "T4: 4r SPN + chi post"),
    ("r6_hetero6", r6_hetero6, "T5: 6r hetero S-box"),
    ("r6_hetero5", r6_hetero5, "T5: 5r hetero S-box"),
    ("r6_lm4_spn", r6_lm4_spn, "T6: 4r Lai-Massey SPN-F"),
    ("r6_lm6_spn", r6_lm6_spn, "T6: 6r Lai-Massey SPN-F"),
]
