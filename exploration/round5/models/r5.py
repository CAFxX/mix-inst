"""Round 5: new constructions/combinations/configurations for the RV64 `mix`
design-space search. Does NOT repeat round-4 candidates.

Winner to beat: h_xorspn3 = xorshift64 pre-diffusion + 3-round SPN
(S1 S-box + Midori M + ShuffleCell), 34.5u, CAL_PASS.

Tracks:
  T1 template mutations of h_xorspn3 (S-box / shuffle / key-schedule sweeps)
  T2 round-count sweep (2 rounds w/ stronger boxes; 4/5 rounds for M9 margin)
  T3 new pre-diffusion composed with 2-3 round SPN
  T4 new hybrids (Feistel w/ SPN F; SPN-then-xorshift; sandwiches;
     heterogeneous rounds; chi as post-layer)
  T5 differential-first: every candidate also gets a weight-1 differential
     profile (max per-bit flip bias) to attack the M9 structure directly.

All candidates: fixed-key bijective (structural argument in docstring),
vectorized numpy models named mix_r5_<name>_np(val, key).
"""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round4/models")
from screen_lib import U64, MASK64, rotl64_np, sbox16_np  # noqa: E402
from r4_hybrid import (  # noqa: E402
    _xorshift64_np, _midori_M_np, _shuffle_np, _rk_np, _tchi64_np,
)

M64 = (1 << 64) - 1
M32 = (1 << 32) - 1

# ---- 4-bit S-boxes (all verified permutations) ----
S1 = [0x0, 0x1, 0x2, 0x4, 0x3, 0x8, 0xF, 0xC,
      0x9, 0x5, 0xB, 0x6, 0x7, 0xE, 0xD, 0xA]          # Blink/THF (h_xorspn3)
GIFT = [0x1, 0xA, 0x4, 0xC, 0x6, 0xF, 0x3, 0x9,
        0x2, 0xD, 0xB, 0x7, 0x5, 0x0, 0x8, 0xE]        # GIFT-128
SKINNY = [0xC, 0x6, 0x9, 0x0, 0x1, 0xA, 0x2, 0xB,
          0x3, 0x8, 0x5, 0xD, 0x4, 0xE, 0x7, 0xF]      # SKINNY-64
MIDORI_SB0 = [0xC, 0xA, 0xD, 0x3, 0xE, 0xB, 0xF, 0x7,
              0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6]  # Midori64 Sb0
PRESENT = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
           0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]    # PRESENT
SBOXES = {"s1": S1, "gift": GIFT, "skinny": SKINNY,
          "midori": MIDORI_SB0, "present": PRESENT}
for _n, _t in SBOXES.items():
    assert len(set(_t)) == 16, _n
SBOX_NP = {n: np.array(t, dtype=np.uint64) for n, t in SBOXES.items()}

# ---- nibble shuffles (free wiring) ----
PERM_D = [0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8]  # h_xorspn3
PERM_R = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]  # reversal


def _shuffle_perm_np(x, perm):
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros(x.shape, dtype=np.uint64)
    for i, p in enumerate(perm):
        y |= ((x >> np.uint64(4 * p)) & np.uint64(0xF)) << np.uint64(4 * i)
    return y


def _rk_rot_np(k, i, rot):
    return rotl64_np(k, U64(rot * (i + 1))) ^ np.uint64(
        ((i + 1) * 0x9E3779B97F4A7C15) & M64)


def _xorshift_np(x, a, b, c):
    """xorshift64 with arbitrary triple; each step is a unitriangular linear
    map, hence bijective for ANY (a,b,c)."""
    x = np.asarray(x, dtype=np.uint64)
    x ^= x >> np.uint64(a)
    x ^= (x << np.uint64(b)) & np.uint64(M64)
    x ^= x >> np.uint64(c)
    return x & np.uint64(M64)


def _spn_rounds(x, k, nrounds, sbox="s1", perm=None, rk_rot=13,
                sbox_seq=None):
    """n SPN rounds: xor rk, 16x S-box, Midori M, nibble shuffle.
    sbox_seq: optional list of S-box names, one per round (heterogeneous)."""
    sb = SBOX_NP[sbox]
    for i in range(nrounds):
        sbi = SBOX_NP[sbox_seq[i]] if sbox_seq else sb
        x = sbox16_np(x ^ _rk_rot_np(k, i, rk_rot), sbi)
        x = _midori_M_np(x)
        x = _shuffle_np(x) if perm is None else _shuffle_perm_np(x, perm)
    return x


def _xorspn(x, k, nrounds, sbox="s1", perm=None, rk_rot=13, sbox_seq=None,
            xs=(12, 25, 27)):
    """xorshift pre-diffusion + n-round SPN + whitening."""
    x = _xorshift_np(np.asarray(x, dtype=np.uint64) ^
                     np.asarray(k, dtype=np.uint64), *xs)
    k = np.asarray(k, dtype=np.uint64)
    x = _spn_rounds(x, k, nrounds, sbox, perm, rk_rot, sbox_seq)
    return (x ^ _rk_rot_np(k, nrounds, rk_rot)) & MASK64


# ================= T1: template mutations of h_xorspn3 =================

def mix_r5_gift_np(val, key):
    """T1: h_xorspn3 with GIFT S-box. Bijective (S-box perm, Midori M
    invertible, shuffle wiring, xorshift bijective)."""
    return _xorspn(val, key, 3, sbox="gift")


def mix_r5_skinny_np(val, key):
    """T1: h_xorspn3 with SKINNY-4 S-box. Bijective (as above)."""
    return _xorspn(val, key, 3, sbox="skinny")


def mix_r5_midori_np(val, key):
    """T1: h_xorspn3 with Midori Sb0. Bijective (as above)."""
    return _xorspn(val, key, 3, sbox="midori")


def mix_r5_present_np(val, key):
    """T1: h_xorspn3 with PRESENT S-box. Bijective (as above)."""
    return _xorspn(val, key, 3, sbox="present")


def mix_r5_rotks7_np(val, key):
    """T1: h_xorspn3, key-schedule rotation 13 -> 7. Bijective (rk still a
    keyed permutation applied by xor)."""
    return _xorspn(val, key, 3, rk_rot=7)


def mix_r5_shufrev_np(val, key):
    """T1: h_xorspn3, nibble shuffle replaced by nibble reversal (free
    wiring). Bijective."""
    return _xorspn(val, key, 3, perm=PERM_R)


# ================= T2: round-count sweep =================

def mix_r5_xorspn2_gift_np(val, key):
    """T2: xorshift + 2-round SPN with stronger GIFT S-box (2 rounds failed
    with S1: 146 rej). Bijective."""
    return _xorspn(val, key, 2, sbox="gift")


def mix_r5_xorspn2_skinny_np(val, key):
    """T2: xorshift + 2-round SPN with SKINNY S-box. Bijective."""
    return _xorspn(val, key, 2, sbox="skinny")


def mix_r5_xorspn4_np(val, key):
    """T2: xorshift + 4-round SPN (S1+Midori). Buys differential margin vs
    M9 at the cost of ~1 extra round of delay. Bijective."""
    return _xorspn(val, key, 4)


def mix_r5_xorspn5_np(val, key):
    """T2: xorshift + 5-round SPN (S1+Midori). Delay-curve probe; expected to
    approach/bust the 44.3u bar. Bijective."""
    return _xorspn(val, key, 5)


# ================= T3: new pre-diffusion =================

def mix_r5_xs2spn3_np(val, key):
    """T3: double xorshift (12,25,27) then (13,7,17) + 3-round SPN(S1).
    Both stages bijective (unitriangular)."""
    x = _xorshift_np(np.asarray(val, dtype=np.uint64) ^
                     np.asarray(key, dtype=np.uint64), 12, 25, 27)
    x = _xorshift_np(x, 13, 7, 17)
    k = np.asarray(key, dtype=np.uint64)
    x = _spn_rounds(x, k, 3)
    return (x ^ _rk_rot_np(k, 3, 13)) & MASK64


def mix_r5_xsaltspn3_np(val, key):
    """T3: xorshift with alternate triple (13,7,17) + 3-round SPN(S1).
    Bijective for any triple."""
    return _xorspn(val, key, 3, xs=(13, 7, 17))


def mix_r5_xsmul3spn3_np(val, key):
    """T3: xorshift64, then multiply by small odd 3 (x + (x<<1), cheap,
    bijective mod 2^64), then 3-round SPN(S1)."""
    x = _xorshift_np(np.asarray(val, dtype=np.uint64) ^
                     np.asarray(key, dtype=np.uint64), 12, 25, 27)
    x = (x + ((x << np.uint64(1)) & np.uint64(M64))) & np.uint64(M64)
    k = np.asarray(key, dtype=np.uint64)
    x = _spn_rounds(x, k, 3)
    return (x ^ _rk_rot_np(k, 3, 13)) & MASK64


# ================= T4: new hybrids =================

def mix_r5_spnxs3_np(val, key):
    """T4: post-diffusion order swap: 3-round SPN(S1+Midori) THEN xorshift64.
    Bijective (composition of bijections)."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    x = _spn_rounds(x, k, 3)
    x = _xorshift_np(x ^ _rk_rot_np(k, 3, 13), 12, 25, 27)
    return x & MASK64


def mix_r5_xsspnxs_np(val, key):
    """T4: xorshift - 3-round SPN - xorshift sandwich. Bijective."""
    x = _xorshift_np(np.asarray(val, dtype=np.uint64) ^
                     np.asarray(key, dtype=np.uint64), 12, 25, 27)
    k = np.asarray(key, dtype=np.uint64)
    x = _spn_rounds(x, k, 3)
    x = _xorshift_np(x ^ _rk_rot_np(k, 3, 13), 12, 25, 27)
    return x & MASK64


def mix_r5_hetero_np(val, key):
    """T4: heterogeneous rounds: S-box cycles S1 -> GIFT -> SKINNY per round.
    Bijective (each round bijective)."""
    return _xorspn(val, key, 3, sbox_seq=["s1", "gift", "skinny"])


def _midori32_np(x):
    """32-bit Midori-like: two 4-nibble columns, parity-xor per column."""
    x = np.asarray(x, dtype=np.uint64) & np.uint64(M32)
    sh = np.array([4 * i for i in range(8)], dtype=np.uint64)
    nib = (x[:, None] >> sh) & np.uint64(0xF)
    out = np.empty_like(nib)
    for c in range(2):
        col = nib[:, 4 * c:4 * c + 4]
        par = col[:, 0] ^ col[:, 1] ^ col[:, 2] ^ col[:, 3]
        out[:, 4 * c:4 * c + 4] = par[:, None] ^ col
    return ((out << sh).sum(axis=1)) & np.uint64(M32)


def _feist_F_spn32_np(R, rk32):
    """Feistel F: 32-bit mini-SPN (S1 x8, Midori32, nibble interleave)."""
    R = np.asarray(R, dtype=np.uint64) & np.uint64(M32)
    sh = np.array([4 * i for i in range(8)], dtype=np.uint64)
    nib = ((R[:, None] >> sh) & np.uint64(0xF)).astype(np.uint64)
    sb = SBOX_NP["s1"]
    y = np.zeros(np.shape(R), dtype=np.uint64)
    for i in range(8):
        y |= sb[nib[:, i]] << np.uint64(4 * i)
    y = _midori32_np(y)
    return (y ^ np.asarray(rk32, dtype=np.uint64)) & np.uint64(M32)


def mix_r5_feistspn4_np(val, key):
    """T4: 4-round Feistel, F = 32-bit mini-SPN (S1+Midori32). Bijective by
    Feistel structure (F need not be bijective)."""
    x = np.asarray(val, dtype=np.uint64) ^ np.asarray(key, dtype=np.uint64)
    k = np.asarray(key, dtype=np.uint64)
    L = (x >> np.uint64(32)) & np.uint64(M32)
    R = x & np.uint64(M32)
    for i in range(4):
        rk32 = _rk_rot_np(k, i, 13) & np.uint64(M32)
        F = _feist_F_spn32_np(R ^ rk32, rk32)
        L, R = R, (L ^ F) & np.uint64(M32)
    rkL = (_rk_rot_np(k, 4, 13) >> np.uint64(32)) & np.uint64(M32)
    rkR = _rk_rot_np(k, 4, 13) & np.uint64(M32)
    return (((L ^ rkL) << np.uint64(32)) | (R ^ rkR)) & MASK64


def mix_r5_chipost_np(val, key):
    """T4: xorshift + 3-round SPN(S1+Midori) + triangular-chi post-layer.
    Chi-as-postlayer (it failed as F / inside sandwiches); triangular chi is
    bijective by back-substitution."""
    x = _xorshift_np(np.asarray(val, dtype=np.uint64) ^
                     np.asarray(key, dtype=np.uint64), 12, 25, 27)
    k = np.asarray(key, dtype=np.uint64)
    x = _spn_rounds(x, k, 3)
    x = _tchi64_np(x ^ _rk_rot_np(k, 3, 13))
    return x & MASK64


CANDIDATES = [
    # (name, fn, track, composition)
    ("r5_gift", mix_r5_gift_np, "T1",
     "xorshift64 + 3rd SPN (GIFT S-box + Midori M + ShuffleCell)"),
    ("r5_skinny", mix_r5_skinny_np, "T1",
     "xorshift64 + 3rd SPN (SKINNY-4 S-box + Midori M + ShuffleCell)"),
    ("r5_midori", mix_r5_midori_np, "T1",
     "xorshift64 + 3rd SPN (Midori Sb0 + Midori M + ShuffleCell)"),
    ("r5_present", mix_r5_present_np, "T1",
     "xorshift64 + 3rd SPN (PRESENT S-box + Midori M + ShuffleCell)"),
    ("r5_rotks7", mix_r5_rotks7_np, "T1",
     "xorshift64 + 3rd SPN (S1 + Midori M), key-schedule rot 13->7"),
    ("r5_shufrev", mix_r5_shufrev_np, "T1",
     "xorshift64 + 3rd SPN (S1 + Midori M), nibble shuffle -> reversal"),
    ("r5_xorspn2_gift", mix_r5_xorspn2_gift_np, "T2",
     "xorshift64 + 2rd SPN (GIFT S-box + Midori M)"),
    ("r5_xorspn2_skinny", mix_r5_xorspn2_skinny_np, "T2",
     "xorshift64 + 2rd SPN (SKINNY S-box + Midori M)"),
    ("r5_xorspn4", mix_r5_xorspn4_np, "T2",
     "xorshift64 + 4rd SPN (S1 + Midori M), differential-margin probe"),
    ("r5_xorspn5", mix_r5_xorspn5_np, "T2",
     "xorshift64 + 5rd SPN (S1 + Midori M), delay-curve probe"),
    ("r5_xs2spn3", mix_r5_xs2spn3_np, "T3",
     "double xorshift (12,25,27)+(13,7,17) + 3rd SPN (S1 + Midori M)"),
    ("r5_xsaltspn3", mix_r5_xsaltspn3_np, "T3",
     "xorshift64 (13,7,17) + 3rd SPN (S1 + Midori M)"),
    ("r5_xsmul3spn3", mix_r5_xsmul3spn3_np, "T3",
     "xorshift64 + x3 (small odd mult) + 3rd SPN (S1 + Midori M)"),
    ("r5_spnxs3", mix_r5_spnxs3_np, "T4",
     "3rd SPN (S1 + Midori M) then xorshift64 post-diffusion"),
    ("r5_xsspnxs", mix_r5_xsspnxs_np, "T4",
     "xorshift64 - 3rd SPN (S1 + Midori M) - xorshift64 sandwich"),
    ("r5_hetero", mix_r5_hetero_np, "T4",
     "xorshift64 + 3rd SPN, heterogeneous S-boxes S1/GIFT/SKINNY per round"),
    ("r5_feistspn4", mix_r5_feistspn4_np, "T4",
     "4-round Feistel, F = 32-bit mini-SPN (S1 + Midori32)"),
    ("r5_chipost", mix_r5_chipost_np, "T4",
     "xorshift64 + 3rd SPN (S1 + Midori M) + triangular-chi post-layer"),
]
