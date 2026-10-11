"""Round-hyb numpy models (vectorized). All functions take (val, key) as uint64
arrays/scalars and return uint64. Single source of truth for the Python side;
impl.c and rtl.v are generated from the same spec by round_hyb/gen_rhyb.py and
verified bit-exact via xcheck (C vs Python) and check_rtl (RTL vs Python).

Base template: balanced Feistel, 32-bit halves, {R,L} output, NO whitening,
with the affine r7/r8/r9 key schedule
(rk32 = low32(rotl64(k,13*(i+1)) ^ ((i+1)*GOLDEN64)), i 1-based).
Identical schedule to r20/r21; round tags s1_311, chi_311, chi_notr,
chi32v_311, chi32w_311, chi_fm11 reuse the r20/r19 numpy semantics exactly.

Hybridization round (per coordinator brief), all 6r Feistel, no whitening:
  1. rh_feist6_parsplit_notr_nw:      [ps_311, chi_311, ps_311, chi_311, ps_311, chi_notr]
  2. rh_feist6_parsplit_notr31_nw:    [ps_311, chi32w_311, ps_311, chi32w_311, ps_311, chi_notr]
  3. rh_feist6_parsplit_chioff13_nw:  [ps_chi16v_311 x6]
  4. rh_feist6_parsplit_chioff31_nw:  [ps_chi16w_311 x6]
  5. rh_feist6_parsplit_keyin_nw:     [ps_keyin_311 x6]
  6. rh_feist6_notr_psfinal_nw:       [s1_311, chi32v_311, s1_311, chi32v_311, s1_311, ps_notr]
  7. rh_feist6_notr_psfinal31_nw:     [s1_311, chi32w_311, s1_311, chi32w_311, s1_311, ps_notr]
  8. rh_feist6_parsplit_3rot_nw:      [ps_3rot x6]
  9. rh_feist6_chioff13_fm11_nw:      [s1_311, chi32v_311, s1_311, chi32v_311, s1_311, chi_fm11]
 10. rh_feist6_chioff31_fm11_nw:      [s1_311, chi32w_311, s1_311, chi32w_311, s1_311, chi_fm11]

Structural note: all are plain balanced Feistel with an arbitrary round
function F — bijective in val for fixed key regardless of F, and every
round's F sees a changing input by construction. No novel topology.
"""
import numpy as np

S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)
S1_LIST = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]

MASK16 = np.uint64(0xFFFF)
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


def _sbox_layer32_np(x, tab):
    out = np.zeros_like(x)
    xv = x & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK32


def _sbox_layer16_np(x, tab):
    out = np.zeros_like(x)
    xv = x & MASK16
    for i in range(4):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK16


def _chi32_np(x):
    x = x & MASK32
    r1 = ((x >> np.uint64(1)) | (x << np.uint64(31))) & MASK32
    r2 = ((x >> np.uint64(2)) | (x << np.uint64(30))) & MASK32
    return (x ^ ((~r1) & r2)) & MASK32


def _chi32v_np(x):
    # variant: b_i = a_i ^ (~a_{i+1} & a_{i+3})
    x = x & MASK32
    r1 = ((x >> np.uint64(1)) | (x << np.uint64(31))) & MASK32
    r3 = ((x >> np.uint64(3)) | (x << np.uint64(29))) & MASK32
    return (x ^ ((~r1) & r3)) & MASK32


def _chi32w_np(x):
    # variant: b_i = a_i ^ (~a_{i+3} & a_{i+1})  (offsets swapped vs chi32v)
    x = x & MASK32
    r3 = ((x >> np.uint64(3)) | (x << np.uint64(29))) & MASK32
    r1 = ((x >> np.uint64(1)) | (x << np.uint64(31))) & MASK32
    return (x ^ ((~r3) & r1)) & MASK32


def _chi16_np(x, o0, o1):
    # generalized 16-bit chi: b_i = a_i ^ (~a_{(i+o0)%16} & a_{(i+o1)%16})
    x = x & MASK16
    r0 = ((x >> np.uint64(o0)) | (x << np.uint64(16 - o0))) & MASK16
    r1 = ((x >> np.uint64(o1)) | (x << np.uint64(16 - o1))) & MASK16
    return (x ^ ((~r0) & r1)) & MASK16


def _lin_ab_np(x, a, b):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)) & MASK32


def _lin3_np(x, a, b, c):
    return (x ^ _rotl32_np(x, a) ^ _rotl32_np(x, b)
            ^ _rotl32_np(x, c)) & MASK32


def _rk32_std_np(k, i):
    # i 1-based, identical to r7/r8/r9/r13/r15/r18/r19/r20/r21
    r = (13 * (i + 1)) % 64
    return (_rotl64_np(k, r) ^ (np.uint64(i + 1) * GOLDEN64)) & MASK32


# ---------------- F functions ----------------
def _F_s1_311(R, rk32):
    return (_lin_ab_np(_sbox_layer32_np(R, S1), 3, 11) ^ rk32) & MASK32


def _F_chi_311(R, rk32):
    return (_lin_ab_np(_chi32_np(R), 3, 11) ^ rk32) & MASK32


def _F_chi32v_311(R, rk32):
    return (_lin_ab_np(_chi32v_np(R), 3, 11) ^ rk32) & MASK32


def _F_chi32w_311(R, rk32):
    return (_lin_ab_np(_chi32w_np(R), 3, 11) ^ rk32) & MASK32


def _F_chi_notr(R, rk32):
    return (_chi32_np(R) ^ rk32) & MASK32


def _F_chi_fm11(R, rk32):
    # cheap final mixing (r19 chi_fm11): y = chi32(R)^rk; F = y ^ rotl32(y,11)
    y = (_chi32_np(R) ^ rk32) & MASK32
    return (y ^ _rotl32_np(y, 11)) & MASK32


def _ps_t_np(R, off, keyin):
    # parsplit t: high 16 = chi16-off of (R>>16)[^ (rk>>16) if keyin],
    #             low 16 = S1 per nibble of R&0xFFFF
    hi = (R >> np.uint64(16)) & MASK16
    if keyin is not None:
        hi = (hi ^ ((keyin >> np.uint64(16)) & MASK16)) & MASK16
    return (((_chi16_np(hi, *off) << np.uint64(16))
             | _sbox_layer16_np(R & MASK16, S1))) & MASK32


def _F_ps_311(R, rk32):
    return (_lin_ab_np(_ps_t_np(R, (1, 2), None), 3, 11) ^ rk32) & MASK32


def _F_ps_notr(R, rk32):
    return (_ps_t_np(R, (1, 2), None) ^ rk32) & MASK32


def _F_ps_chi16v_311(R, rk32):
    return (_lin_ab_np(_ps_t_np(R, (1, 3), None), 3, 11) ^ rk32) & MASK32


def _F_ps_chi16w_311(R, rk32):
    return (_lin_ab_np(_ps_t_np(R, (3, 1), None), 3, 11) ^ rk32) & MASK32


def _F_ps_keyin_311(R, rk32):
    # key inside the chi16 half: chi16((R>>16) ^ (rk>>16))
    return (_lin_ab_np(_ps_t_np(R, (1, 2), rk32), 3, 11) ^ rk32) & MASK32


def _F_ps_3rot(R, rk32):
    # r16's lin3: x ^ rotl(x,3) ^ rotl(x,7) ^ rotl(x,11)
    return (_lin3_np(_ps_t_np(R, (1, 2), None), 3, 7, 11) ^ rk32) & MASK32


def _F_ps_3rot_odd(R, rk32):
    # rh2 (M1 follow-up): odd-term 3-rotation linear x^R3^R7 (nonsingular).
    t = _ps_t_np(R, (1, 2), None)
    return ((t ^ _rotl32_np(t, 3) ^ _rotl32_np(t, 7)) ^ rk32) & MASK32


TAG_F = {
    "s1_311": _F_s1_311,
    "chi_311": _F_chi_311,
    "chi_notr": _F_chi_notr,
    "chi32v_311": _F_chi32v_311,
    "chi32w_311": _F_chi32w_311,
    "chi_fm11": _F_chi_fm11,
    "ps_311": _F_ps_311,
    "ps_notr": _F_ps_notr,
    "ps_chi16v_311": _F_ps_chi16v_311,
    "ps_chi16w_311": _F_ps_chi16w_311,
    "ps_keyin_311": _F_ps_keyin_311,
    "ps_3rot": _F_ps_3rot,
    "ps_3rot_odd": _F_ps_3rot_odd,
}


# ---------------- main loop ----------------
def _feistel_np(x, k, tags):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    Fsel = [TAG_F[t] for t in tags]
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 7):
        nR = (L ^ Fsel[i - 1](R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_decrypt_np(x, k, tags):
    # Feistel decrypt with reversed round keys. State (a,b) = (L_i, R_i);
    # output packs (R_6, L_6), so init (a,b) = (L_6, R_6) = (x&m32, x>>32).
    # R_{i-1} = L_i; L_{i-1} = R_i ^ F(R_{i-1}, rk_i).
    # Scalar-friendly path (used by self-tests).
    x = np.uint64(x)
    k = np.uint64(k)
    Fsel = [TAG_F[t] for t in tags]
    a = x & MASK32          # L_6
    b = (x >> np.uint64(32)) & MASK32  # R_6
    for i in range(6, 0, -1):
        na = (b ^ Fsel[i - 1](a, _rk32_std_np(k, i))) & MASK32
        nb = a
        a, b = na, nb
    # input convention: v = (L_0 << 32) | R_0
    return ((a << np.uint64(32)) | b) & MASK64


def _mk(name, fn_or_tags):
    if isinstance(fn_or_tags, list):
        tags = fn_or_tags

        def fn(v, k):
            return _feistel_np(v, k, tags)
    else:
        fn = fn_or_tags
    fn.__name__ = name
    return fn


rh_feist6_parsplit_notr_nw = _mk(
    "rh_feist6_parsplit_notr_nw",
    ["ps_311", "chi_311", "ps_311", "chi_311", "ps_311", "chi_notr"])

rh_feist6_parsplit_notr31_nw = _mk(
    "rh_feist6_parsplit_notr31_nw",
    ["ps_311", "chi32w_311", "ps_311", "chi32w_311", "ps_311", "chi_notr"])

rh_feist6_parsplit_chioff13_nw = _mk(
    "rh_feist6_parsplit_chioff13_nw", ["ps_chi16v_311"] * 6)

rh_feist6_parsplit_chioff31_nw = _mk(
    "rh_feist6_parsplit_chioff31_nw", ["ps_chi16w_311"] * 6)

rh_feist6_parsplit_keyin_nw = _mk(
    "rh_feist6_parsplit_keyin_nw", ["ps_keyin_311"] * 6)

rh_feist6_notr_psfinal_nw = _mk(
    "rh_feist6_notr_psfinal_nw",
    ["s1_311", "chi32v_311", "s1_311", "chi32v_311", "s1_311", "ps_notr"])

rh_feist6_notr_psfinal31_nw = _mk(
    "rh_feist6_notr_psfinal31_nw",
    ["s1_311", "chi32w_311", "s1_311", "chi32w_311", "s1_311", "ps_notr"])

rh_feist6_parsplit_3rot_nw = _mk(
    "rh_feist6_parsplit_3rot_nw", ["ps_3rot"] * 6)

rh_feist6_chioff13_fm11_nw = _mk(
    "rh_feist6_chioff13_fm11_nw",
    ["s1_311", "chi32v_311", "s1_311", "chi32v_311", "s1_311", "chi_fm11"])

rh_feist6_chioff31_fm11_nw = _mk(
    "rh_feist6_chioff31_fm11_nw",
    ["s1_311", "chi32w_311", "s1_311", "chi32w_311", "s1_311", "chi_fm11"])

# M6 follow-up (2026-10-03): parsplit/alt chassis with the r19 fm11 cure on
# the final round's F (32-bit F-output mixing, Feistel stays bijective).
# NOTE: the literal 64-bit output mixing y^rotl64(y,11) is 2-to-1
# (kernel {0, 2^64-1}) and would break the bijectivity hard gate; r19's
# actual cure was F_6 = y^rotl32(y,11) inside F, which is what chi_fm11 is.
rh2_parsplit_fm11_nw = _mk(
    "rh2_parsplit_fm11_nw",
    ["ps_311", "chi_311", "ps_311", "chi_311", "ps_311", "chi_fm11"])

SPECS = [
    ("rh_feist6_parsplit_notr_nw",
     ["ps_311", "chi_311", "ps_311", "chi_311", "ps_311", "chi_notr"],
     "6r parsplit/alt-notr alternating chassis, truncated ps final, NO whitening"),
    ("rh_feist6_parsplit_notr31_nw",
     ["ps_311", "chi32w_311", "ps_311", "chi32w_311", "ps_311", "chi_notr"],
     "6r parsplit/(3,1)-notr alternating chassis, truncated ps final, NO whitening"),
    ("rh_feist6_parsplit_chioff13_nw",
     ["ps_chi16v_311"] * 6,
     "6r homogeneous parsplit-F with chi16 offsets (1,3), NO whitening"),
    ("rh_feist6_parsplit_chioff31_nw",
     ["ps_chi16w_311"] * 6,
     "6r homogeneous parsplit-F with chi16 offsets (3,1), NO whitening"),
    ("rh_feist6_parsplit_keyin_nw",
     ["ps_keyin_311"] * 6,
     "6r homogeneous parsplit-F, key inside chi16 half, NO whitening"),
    ("rh_feist6_notr_psfinal_nw",
     ["s1_311", "chi32v_311", "s1_311", "chi32v_311", "s1_311", "ps_notr"],
     "6r chioff13-notr chassis with truncated parsplit final (BIC cure), NO whitening"),
    ("rh_feist6_notr_psfinal31_nw",
     ["s1_311", "chi32w_311", "s1_311", "chi32w_311", "s1_311", "ps_notr"],
     "6r chioff31-notr chassis with truncated parsplit final (BIC cure), NO whitening"),
    ("rh_feist6_parsplit_3rot_nw",
     ["ps_3rot"] * 6,
     "6r homogeneous parsplit-F with 3-rotation linear (3,7,11), NO whitening"),
    ("rh_feist6_chioff13_fm11_nw",
     ["s1_311", "chi32v_311", "s1_311", "chi32v_311", "s1_311", "chi_fm11"],
     "6r chioff13-notr chassis with fm11 final mixing (BIC cure), NO whitening"),
    ("rh_feist6_chioff31_fm11_nw",
     ["s1_311", "chi32w_311", "s1_311", "chi32w_311", "s1_311", "chi_fm11"],
     "6r chioff31-notr chassis with fm11 final mixing (BIC cure), NO whitening"),
    ("rh2_parsplit_fm11_nw",
     ["ps_311", "chi_311", "ps_311", "chi_311", "ps_311", "chi_fm11"],
     "6r parsplit/alt chassis with fm11 final mixing (M6 follow-up BIC cure), NO whitening"),
]

ALL = [
    rh_feist6_parsplit_notr_nw,
    rh_feist6_parsplit_notr31_nw,
    rh_feist6_parsplit_chioff13_nw,
    rh_feist6_parsplit_chioff31_nw,
    rh_feist6_parsplit_keyin_nw,
    rh_feist6_notr_psfinal_nw,
    rh_feist6_notr_psfinal31_nw,
    rh_feist6_parsplit_3rot_nw,
    rh_feist6_chioff13_fm11_nw,
    rh_feist6_chioff31_fm11_nw,
    rh2_parsplit_fm11_nw,
]


# ---------------- wide constructions ----------------
# New 64-bit round-key schedule (Carlo 2026-10-03):
#   RK64(k, i) = rotl64(k, 7*i) ^ (i * 0x9E3779B97F4A7C15), i 1-based.
# Documented in ROUND_HYB_TABLE.md.
def _rk64_new_np(k, i):
    with np.errstate(over="ignore"):
        return (_rotl64_np(k, (7 * i) % 64)
                ^ (np.uint64(i) * GOLDEN64)) & MASK64


def _sbox_layer64_np(x, tab):
    out = np.zeros_like(x)
    xv = x & MASK64
    for i in range(16):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(tab, nib) << np.uint64(4 * i)
    return out & MASK64


def _lin64_np(x):
    return (x ^ _rotl64_np(x, 3) ^ _rotl64_np(x, 11)) & MASK64


# lin64(x) = x ^ rotl64(x,3) ^ rotl64(x,11) is the GF(2)[x]-linear map given
# by p(t) = 1 + t^3 + t^11. Over GF(2), x^64 + 1 = (x + 1)^64, so
# gcd(p, x^64+1) = 1  iff  (x+1) does NOT divide p  iff  p(1) != 0.
# p(1) = 1 ^ 1 ^ 1 = 1 != 0  =>  lin64 is a permutation of GF(2)^64.
# Inverse via GF(2) Gauss-Jordan on the 64x64 matrix (import-time, exact).
def _gf2_mat_inv(rows):
    n = len(rows)
    # augmented [rows | I]: low n bits = matrix row, high n bits = identity.
    aug = [rows[i] | ((1 << i) << n) for i in range(n)]
    for col in range(n):
        piv = next(i for i in range(col, n) if (aug[i] >> col) & 1)
        aug[col], aug[piv] = aug[piv], aug[col]
        for i in range(n):
            if i != col and ((aug[i] >> col) & 1):
                aug[i] ^= aug[col]
    return [aug[i] >> n for i in range(n)]


def _lin64_matrix_rows():
    rows = []
    for j in range(64):
        row = 0
        for i in range(64):
            if j in (i, (i + 3) % 64, (i + 11) % 64):
                row |= 1 << i
        rows.append(row)
    return rows


_LIN64_INV_ROWS = _gf2_mat_inv(_lin64_matrix_rows())


def _lin64_inv_scalar(xv):
    out = 0
    for j in range(64):
        if bin(xv & _LIN64_INV_ROWS[j]).count("1") & 1:
            out |= 1 << j
    return out


_S1_INV_LIST = [S1_LIST.index(v) for v in range(16)]
_S1_INV = np.array(_S1_INV_LIST, dtype=np.uint64)


def _sbox64_inv_scalar(xv):
    out = 0
    for i in range(16):
        out |= _S1_INV_LIST[(xv >> (4 * i)) & 0xF] << (4 * i)
    return out


# ---- W: full-64-bit SPN, nrounds; final key XOR after last round ----
def _spn_enc_np(x, k, nrounds):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    for i in range(1, nrounds + 1):
        x = (x ^ _rk64_new_np(k, i)) & MASK64
        x = _sbox_layer64_np(x, S1)
        x = _lin64_np(x)
    return (x ^ _rk64_new_np(k, nrounds + 1)) & MASK64


def _spn_dec_np(x, k, nrounds):
    # scalar path for self-test: inverse ops in reverse order.
    x = int(np.uint64(x))
    kk = int(np.uint64(k))
    x ^= int(_rk64_new_np(np.uint64(kk), nrounds + 1))
    x &= 0xFFFFFFFFFFFFFFFF
    for i in range(nrounds, 0, -1):
        x = _lin64_inv_scalar(x)
        x = _sbox64_inv_scalar(x)
        x ^= int(_rk64_new_np(np.uint64(kk), i))
        x &= 0xFFFFFFFFFFFFFFFF
    return np.uint64(x)


# ---- P: proper Lai-Massey with orthomorphism sigma(U,V) = (V, U^V) ----
# Per round:  D = L ^ R;  T = F(D, rk32);  (L', R') = (R ^ T, D).
# (This is sigma applied to (L^T, R^T): sigma(L^T, R^T) = (R^T, L^R) = (R^T, D).)
#
# Round-input variation proof (AGENTS.md round-13 lesson: the naive LM
# L'=R^t, R'=L^t preserved D = L^R across rounds — degenerate; killed at S0):
#   D_1 = L ^ R                                  (input-dependent)
#   (L_1, R_1) = (R ^ T_1, D_1),   T_1 = F(D_1)
#   D_2 = L_1 ^ R_1 = (R ^ T_1) ^ D_1 = L ^ T_1   (uses D_1 = L^R)
# D_2 = L ^ T_1 depends on L and on T_1 = F(D_1): F's input varies across
# rounds. The naive-LM failure mode (constant D) does not occur.
# Inverse: D = R'; T = F(D, rk); R = L' ^ T; L = D ^ R.
def _lm_enc_np(x, k, ftag):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    F = TAG_F[ftag]
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 7):
        D = (L ^ R) & MASK32
        T = F(D, _rk32_std_np(k, i))
        L, R = (R ^ T) & MASK32, D
    return ((L << np.uint64(32)) | R) & MASK64


def _lm_dec_np(x, k, ftag):
    # scalar path for self-test.
    L = int((np.uint64(x) >> np.uint64(32)) & MASK32)
    R = int(np.uint64(x) & MASK32)
    F = TAG_F[ftag]
    kk = np.uint64(k)
    for i in range(6, 0, -1):
        D = R
        T = int(F(np.uint64(D), _rk32_std_np(kk, i)))
        Rp = L ^ T
        Lp = D ^ Rp
        L, R = Lp & 0xFFFFFFFF, Rp & 0xFFFFFFFF
    return np.uint64(((L << 32) | R) & 0xFFFFFFFFFFFFFFFF)


# ---- D1/D2: 128-bit state, 64-bit halves, standard Feistel ----
# Expansion (injective): A = v ^ RK64(k,101); B = rotl64(v,13) ^ RK64(k,102).
# F_64(X, rk64) = lin64(S1_64(X)) ^ rk64, rk64 = RK64(k,i) 1-based.
# Compression: out = L' ^ R' (64 bits).
# NOT bijective by construction: collision gate (below) is mandatory.
def _wide128_enc_np(x, k, nrounds):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x ^ _rk64_new_np(k, 101)) & MASK64
    R = (_rotl64_np(x, 13) ^ _rk64_new_np(k, 102)) & MASK64
    for i in range(1, nrounds + 1):
        F = (_lin64_np(_sbox_layer64_np(R, S1))
             ^ _rk64_new_np(k, i)) & MASK64
        nL = R
        nR = (L ^ F) & MASK64
        L, R = nL, nR
    return (L ^ R) & MASK64


# ---- D3: 5-round standard 64-bit Feistel with wide-internal F ----
# F_wide(R32, rk32): X = (R || rk32) (64 bits); X = S1_64(X); X = lin64(X);
# return ((X>>32) ^ (X & 0xFFFFFFFF) ^ rk32) & 0xFFFFFFFF.
# Bijective by construction (Feistel); tests the "wider state, fewer rounds"
# hypothesis without D1/D2's compression risk.
def _F_wide_np(R32, rk32):
    X = (((R32 & MASK32) << np.uint64(32)) | (rk32 & MASK32)) & MASK64
    X = _sbox_layer64_np(X, S1)
    X = _lin64_np(X)
    return (((X >> np.uint64(32)) ^ (X & MASK32) ^ rk32)) & MASK32


def _feistel_wideF_enc_np(x, k):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 6):
        nR = (L ^ _F_wide_np(R, _rk32_std_np(k, i))) & MASK32
        L, R = R, nR
    return ((R << np.uint64(32)) | L) & MASK64


def _feistel_wideF_dec_np(x, k):
    # scalar path for self-test. State (a,b) = (L_i, R_i); output packs
    # (R_5, L_5), so init (a,b) = (L_5, R_5). R_{i-1} = L_i; L_{i-1} = R_i ^ F.
    xv = int(np.uint64(x))
    kk = np.uint64(k)
    a = xv & 0xFFFFFFFF          # L_5
    b = (xv >> 32) & 0xFFFFFFFF  # R_5
    for i in range(5, 0, -1):
        F = int(_F_wide_np(np.uint64(a), _rk32_std_np(kk, i)))
        na = (b ^ F) & 0xFFFFFFFF
        a, b = na, a
    # input convention: v = (L_0 << 32) | R_0
    return np.uint64(((a << 32) | b) & 0xFFFFFFFFFFFFFFFF)


rh_spn3_s1_nw = _mk("rh_spn3_s1_nw",
                    lambda v, k: _spn_enc_np(v, k, 3))
rh_spn4_s1_nw = _mk("rh_spn4_s1_nw",
                    lambda v, k: _spn_enc_np(v, k, 4))
rh_lm_parsplit_nw = _mk("rh_lm_parsplit_nw",
                        lambda v, k: _lm_enc_np(v, k, "ps_311"))
rh_lm_chi_nw = _mk("rh_lm_chi_nw",
                   lambda v, k: _lm_enc_np(v, k, "chi_311"))
rh_wide128_feist4_nw = _mk("rh_wide128_feist4_nw",
                           lambda v, k: _wide128_enc_np(v, k, 4))
rh_wide128_feist5_nw = _mk("rh_wide128_feist5_nw",
                           lambda v, k: _wide128_enc_np(v, k, 5))
rh_wideF_feist5_nw = _mk("rh_wideF_feist5_nw", _feistel_wideF_enc_np)

# kind: spn | lm | wide128 | wideF ; param: nrounds | ftag | nrounds | None
WIDE_SPECS = [
    ("rh_spn3_s1_nw", "spn", 3,
     "full-64-bit SPN, 3 rounds: key-add, 16x S1, lin64(3,11), final key-add, NO whitening"),
    ("rh_spn4_s1_nw", "spn", 4,
     "full-64-bit SPN, 4 rounds: key-add, 16x S1, lin64(3,11), final key-add, NO whitening"),
    ("rh_lm_parsplit_nw", "lm", "ps_311",
     "proper Lai-Massey (orthomorphism sigma) 6r, T=F_parsplit(D)^rk32, NO whitening — re-test of r13 LM skeleton with new F"),
    ("rh_lm_chi_nw", "lm", "chi_311",
     "proper Lai-Massey (orthomorphism sigma) 6r, T=lin311(chi32(D))^rk32, NO whitening — re-test of r13 LM skeleton with new F"),
    ("rh_wide128_feist4_nw", "wide128", 4,
     "128-bit state 4r Feistel, F_64=lin64(S1_64)^rk64, injective expansion, L'^R' compression — bijectivity NOT by construction (collision gate)"),
    ("rh_wide128_feist5_nw", "wide128", 5,
     "128-bit state 5r Feistel, F_64=lin64(S1_64)^rk64, injective expansion, L'^R' compression — bijectivity NOT by construction (collision gate)"),
    ("rh_wideF_feist5_nw", "wideF", None,
     "5r standard 64-bit Feistel, wide-internal F_wide(R||rk32)->S1_64->lin64->fold, bijective by construction"),
]

ALL_WIDE = [
    rh_spn3_s1_nw,
    rh_spn4_s1_nw,
    rh_lm_parsplit_nw,
    rh_lm_chi_nw,
    rh_wide128_feist4_nw,
    rh_wide128_feist5_nw,
    rh_wideF_feist5_nw,
]


def wide128_collision_gate(nrounds, nrand=1 << 24, key=0x123456789ABCDEF0):
    """Mandatory bijectivity gate for D1/D2 (not bijective by construction).
    Returns (n_collisions, detail). ANY collision -> construction kill."""
    rng = np.random.default_rng(0xC01115)
    K = np.uint64(key)
    V = rng.integers(0, 2 ** 64, size=nrand, dtype=np.uint64)
    O = _wide128_enc_np(V, K, nrounds)
    _, counts = np.unique(O, return_counts=True)
    n_dup = int(np.sum(counts > 1))
    # structured inputs: all 64 single-bit + all 2016 two-bit flips
    bits = np.arange(64, dtype=np.uint64)
    Vs = np.uint64(1) << bits
    V2 = []
    for i in range(64):
        V2.append((np.uint64(1) << np.uint64(i))
                   | (np.uint64(1) << bits[i + 1:]))
    Vs = np.concatenate([Vs] + V2)
    Os = _wide128_enc_np(Vs, K, nrounds)
    _, cs = np.unique(Os, return_counts=True)
    n_dup_s = int(np.sum(cs > 1))
    return n_dup + n_dup_s, (f"random(2^{nrand.bit_length()-1}):{n_dup} "
                             f"structured({len(Vs)}):{n_dup_s}")


def wide_selftest():
    rng = np.random.default_rng(60606)
    # 1. S1 is a permutation (SPN bijectivity leg 1).
    assert sorted(S1_LIST) == list(range(16)), "S1 not a permutation"
    print("S1 permutation check OK")
    # 2. lin64 inverse is exact (SPN bijectivity leg 2; p(1)=1 argument above).
    for _ in range(300):
        xv = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        fwd = int(_lin64_np(np.uint64(xv)))
        assert _lin64_inv_scalar(fwd) == xv, ("lin64inv", hex(xv))
    print("lin64 inverse self-test: 300 vectors OK")
    # 3. SPN encrypt/decrypt round-trips (W1, W2).
    for name, nrounds in (("rh_spn3_s1_nw", 3), ("rh_spn4_s1_nw", 4)):
        fn = globals()[name]
        for _ in range(100):
            v = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
            k = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
            enc = int(fn(np.uint64(v), np.uint64(k)))
            dec = int(_spn_dec_np(enc, k, nrounds))
            assert dec == v, ("spn-invert", name, hex(v), hex(k))
    print("SPN round-trip self-test: W1/W2 x 100 keys OK")
    # 4. LM encrypt/decrypt round-trips (P1, P2).
    for name, ftag in (("rh_lm_parsplit_nw", "ps_311"),
                       ("rh_lm_chi_nw", "chi_311")):
        fn = globals()[name]
        for _ in range(100):
            v = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
            k = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
            enc = int(fn(np.uint64(v), np.uint64(k)))
            dec = int(_lm_dec_np(enc, k, ftag))
            assert dec == v, ("lm-invert", name, hex(v), hex(k))
    print("LM round-trip self-test: P1/P2 x 100 keys OK")
    # 5. D3 Feistel round-trip (bijective by construction; guards the F_wide
    #    wiring against the same class of helper bug caught above).
    for _ in range(100):
        v = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        k = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        enc = int(rh_wideF_feist5_nw(np.uint64(v), np.uint64(k)))
        dec = int(_feistel_wideF_dec_np(enc, k))
        assert dec == v, ("wideF-invert", hex(v), hex(k))
    print("D3 wideF round-trip self-test: 100 keys OK")


# ---------------- rh2 follow-ups (failure-analysis driven) ----------------
# M1: odd-term 3-rotation linear via TAG_F["ps_3rot_odd"] (defined above).


# M2: fast-diffusing linear for SPN (41-bit spread/round).
def _lin64_fast_np(x):
    return (x ^ _rotl64_np(x, 17) ^ _rotl64_np(x, 41)) & MASK64


def _spn_fast_enc_np(x, k, nrounds=4):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    for i in range(1, nrounds + 1):
        x = (x ^ _rk64_new_np(k, i)) & MASK64
        x = _sbox_layer64_np(x, S1)
        x = _lin64_fast_np(x)
    return (x ^ _rk64_new_np(k, nrounds + 1)) & MASK64


# M3: wide128 5r with NO compression (out = L5).
def _wide128_nocomp_enc_np(x, k):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x ^ _rk64_new_np(k, 101)) & MASK64
    R = (_rotl64_np(x, 13) ^ _rk64_new_np(k, 102)) & MASK64
    for i in range(1, 6):
        F = (_lin64_np(_sbox_layer64_np(R, S1))
             ^ _rk64_new_np(k, i)) & MASK64
        nL = R
        nR = (L ^ F) & MASK64
        L, R = nL, nR
    return L & MASK64


# M5: 5-round LM with chi-F (r13 tested 4r/6r S1-F; 5r chi-F untested).
def _lm5_enc_np(x, k):
    x = np.asarray(x, dtype=np.uint64)
    k = np.asarray(k, dtype=np.uint64)
    L = (x >> np.uint64(32)) & MASK32
    R = x & MASK32
    for i in range(1, 6):
        D = (L ^ R) & MASK32
        T = _F_chi_311(D, _rk32_std_np(k, i))
        L, R = (R ^ T) & MASK32, D
    return ((L << np.uint64(32)) | R) & MASK64


rh2_parsplit_3rot_odd_nw = _mk("rh2_parsplit_3rot_odd_nw",
                               lambda v, k: _feistel_np(
                                   v, k, ["ps_3rot_odd"] * 6))
rh2_spn4_s1_fastlin_nw = _mk("rh2_spn4_s1_fastlin_nw", _spn_fast_enc_np)
rh2_wide128_feist5_nocomp_nw = _mk("rh2_wide128_feist5_nocomp_nw",
                                   _wide128_nocomp_enc_np)
rh2_lm5_chi_nw = _mk("rh2_lm5_chi_nw", _lm5_enc_np)

RH2_SPECS = [
    ("rh2_parsplit_3rot_odd_nw", "feistel_odd3rot",
     "parsplit-F x odd-term 3-rot linear (M1 follow-up)"),
    ("rh2_spn4_s1_fastlin_nw", "spn_fast",
     "4r SPN with fast-diffusing lin(17,41) (M2 follow-up)"),
    ("rh2_wide128_feist5_nocomp_nw", "wide128_nocomp",
     "128-bit 5r Feistel, out=L5 no compression (M3 follow-up)"),
    ("rh2_lm5_chi_nw", "lm5",
     "5r LM with chi-F (M5 follow-up)"),
]
ALL_RH2 = [rh2_parsplit_3rot_odd_nw, rh2_spn4_s1_fastlin_nw,
           rh2_wide128_feist5_nocomp_nw, rh2_lm5_chi_nw]


def rh2_selftest():
    rng = np.random.default_rng(70707)
    # rh2_spn4_s1_fastlin: round-trip via GF(2)-inverse of lin(17,41).
    rows = []
    for j in range(64):
        row = 0
        for i in range(64):
            if j in (i, (i + 17) % 64, (i + 41) % 64):
                row |= 1 << i
        rows.append(row)
    inv = _gf2_mat_inv(rows)

    def linfast_inv(xv):
        out = 0
        for j in range(64):
            if bin(xv & inv[j]).count("1") & 1:
                out |= 1 << j
        return out

    for _ in range(50):
        v = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        k = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        enc = int(rh2_spn4_s1_fastlin_nw(np.uint64(v), np.uint64(k)))
        # decrypt
        x = enc ^ int(_rk64_new_np(np.uint64(k), 5))
        x &= 0xFFFFFFFFFFFFFFFF
        for i in range(4, 0, -1):
            x = linfast_inv(x)
            x = _sbox64_inv_scalar(x)
            x ^= int(_rk64_new_np(np.uint64(k), i))
            x &= 0xFFFFFFFFFFFFFFFF
        assert x == v, ("spnfast-invert", hex(v))
    print("rh2 spn_fastlin round-trip: 50 keys OK")
    # rh2_lm5_chi: LM decrypt round-trip (5 rounds).
    for _ in range(50):
        v = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        k = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        enc = int(rh2_lm5_chi_nw(np.uint64(v), np.uint64(k)))
        L = (enc >> 32) & 0xFFFFFFFF
        R = enc & 0xFFFFFFFF
        kk = np.uint64(k)
        for i in range(5, 0, -1):
            D = R
            T = int(_F_chi_311(np.uint64(D), _rk32_std_np(kk, i)))
            Rp = L ^ T
            Lp = D ^ Rp
            L, R = Lp & 0xFFFFFFFF, Rp & 0xFFFFFFFF
        assert ((L << 32) | R) == v, ("lm5-invert", hex(v))
    print("rh2 lm5 round-trip: 50 keys OK")
    # rh2_parsplit_3rot_odd: Feistel invertibility via generic helper.
    for _ in range(50):
        v = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        k = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
        enc = int(rh2_parsplit_3rot_odd_nw(np.uint64(v), np.uint64(k)))
        dec = int(_feistel_decrypt_np(enc, k, ["ps_3rot_odd"] * 6))
        assert dec == v, ("3rotodd-invert", hex(v))
    print("rh2 3rot_odd round-trip: 50 keys OK")


# ---------------- self-tests ----------------
def _chi16_scalar(xv, o0, o1):
    want = 0
    for i in range(16):
        a0 = (xv >> i) & 1
        a1 = (xv >> ((i + o0) % 16)) & 1
        a2 = (xv >> ((i + o1) % 16)) & 1
        want |= (a0 ^ ((1 - a1) & a2)) << i
    return want


def _rotl32_scalar(xv, r):
    r %= 32
    return ((xv << r) | (xv >> (32 - r))) & 0xFFFFFFFF if r else xv & 0xFFFFFFFF


def _ps_keyin_manual(R, rk):
    hi = ((R >> 16) ^ (rk >> 16)) & 0xFFFF
    lo = R & 0xFFFF
    s = 0
    for i in range(4):
        s |= S1_LIST[(lo >> (4 * i)) & 0xF] << (4 * i)
    t = ((_chi16_scalar(hi, 1, 2) << 16) | s) & 0xFFFFFFFF
    t = (t ^ _rotl32_scalar(t, 3) ^ _rotl32_scalar(t, 11)) & 0xFFFFFFFF
    return (t ^ rk) & 0xFFFFFFFF


def selftest():
    # 1. chi16v / chi16w vs brute-force truth tables (capable of failing).
    rng = np.random.default_rng(31337)
    for _ in range(300):
        xv = int(rng.integers(0, 2 ** 16))
        got_v = int(_chi16_np(np.uint64(xv), 1, 3))
        got_w = int(_chi16_np(np.uint64(xv), 3, 1))
        got_12 = int(_chi16_np(np.uint64(xv), 1, 2))
        assert got_v == _chi16_scalar(xv, 1, 3), ("chi16v", hex(xv))
        assert got_w == _chi16_scalar(xv, 3, 1), ("chi16w", hex(xv))
        assert got_12 == _chi16_scalar(xv, 1, 2), ("chi16", hex(xv))
    print("chi16 self-tests: (1,2)/(1,3)/(3,1) x 300 vectors OK")
    # 2. ps_keyin vs independent manual composition.
    for _ in range(500):
        Rv = int(rng.integers(0, 2 ** 32))
        kv = int(rng.integers(0, 2 ** 32))
        got = int(_F_ps_keyin_311(np.uint64(Rv), np.uint64(kv)))
        want = _ps_keyin_manual(Rv, kv)
        assert got == want, ("ps_keyin", hex(Rv), hex(kv), hex(got), hex(want))
    print("ps_keyin manual-composition self-test: 500 vectors OK")
    # 3. Feistel invertibility round-trip per fixed key (capable of failing
    #    if the round loop or key schedule were miswired).
    for name, tags, _ in SPECS:
        fn = globals()[name]
        for _ in range(100):
            v = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
            k = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
            enc = int(fn(np.uint64(v), np.uint64(k)))
            dec = int(_feistel_decrypt_np(enc, k, tags))
            assert dec == v, ("invert", name, hex(v), hex(k))
    print(f"invertibility self-test: {len(SPECS)} candidates x 100 keys OK")
    wide_selftest()
    rh2_selftest()


if __name__ == "__main__":
    selftest()
