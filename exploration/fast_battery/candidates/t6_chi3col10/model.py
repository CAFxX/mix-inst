"""Track 6, batch 4: new diffusion structures.

Batch 3 verdicts: t6_trivium64 and t6_gimli both S1-KILLED (catastrophic LIN/DIFF).
Stream-cipher/NFSR structures at 64-bit lack nonlinearity per clock.
t6_trivium64b S1 still running.

Batch 4 explores diffusion mechanisms NOT yet tried on any track:
  1. t6_theta5/6/7   : 4-bit S-box (rasC2_0) + Keccak-theta-style parity diffusion.
                       Theta: compute parity of 8 rows x 8 cols, XOR parities back.
                       Gives near-complete diffusion in 2 XOR levels (vs rotation-XOR's slow spread).
  2. t6_midori6/7/8  : Midori64 reduced rounds — Midori Sb0 + Midori MixColumn (XOR-only).
                       Real 64-bit cipher structure, testing if fewer rounds suffice for a hash finalizer.
  3. t6_chi3col8/10  : Xoodoo-style 3-bit column chi on interleaved bit groups + rotations.
                       Column-oriented (vs al_ track's 64-bit-wide chi on rotated copies).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

# rasC2_0 4-bit S-box (frontier)
SBOX_RASC2_0 = np.array([0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14],
                        dtype=np.uint64)
# Midori Sb0 (lowest standalone depth: 3.0u)
SBOX_MIDORI0 = np.array([0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7,
                         0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6],
                        dtype=np.uint64)


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _sbox_nibbles(x, sbox):
    y = np.zeros_like(x)
    for i in range(16):
        y |= sbox[((x >> np.uint64(4 * i)) & np.uint64(0xF))] << np.uint64(4 * i)
    return y & M64


def _theta64(x):
    """Keccak-theta-style parity diffusion on 8x8 bit matrix.
    Row parity p[i] = XOR of row i bits. Then x'[i][j] = x[i][j] ^ p[(i+1)%8] ^ rot(p[(i+2)%8]).
    2 XOR levels for full-state diffusion."""
    # extract 8x8 matrix: bit (i*8+j) -> mat[i][j]
    rows = [((int(xi) >> (8 * i)) & 0xFF) for i in range(8) for xi in [x]]
    # parity of each row (XOR of all 8 bits)
    par = []
    for i in range(8):
        p = 0
        r = rows[i]
        for j in range(8):
            p ^= (r >> j) & 1
        par.append(p)
    # diffuse: new bit (i,j) = old(i,j) ^ par[(i+1)%8] ^ par[(i+2)%8]
    out = 0
    for i in range(8):
        d = par[(i + 1) % 8] ^ par[(i + 2) % 8]
        for j in range(8):
            b = (rows[i] >> j) & 1
            out |= ((b ^ d) << (8 * i + j))
    return np.uint64(out) & M64


def theta_spn(v, k, nrounds):
    s = np.uint64(v) ^ np.uint64(k)
    for rnd in range(nrounds):
        s = _sbox_nibbles(s, SBOX_RASC2_0)
        s = _theta64(s)
        s ^= RC64[rnd % len(RC64)] ^ _rotl64(np.uint64(k), 13 * (rnd + 1))
    return (s ^ (np.uint64(k) >> np.uint64(32))) & M64


def _midori_mixcolumn(x):
    """Midori MixColumn: 4x4 nibble matrix, each column mixed via XORs.
    Column (a0,a1,a2,a3) -> (a3^a1^a2, a0^a2^a3, a0^a1^a3, a0^a1^a2)... actual Midori M:
    [0 1 1 1]   applied per column.
    [1 0 1 1]
    [1 1 0 1]
    [1 1 1 0]
    """
    # nibbles n[0..15], column c = nibbles c, c+4, c+8, c+12
    n = [(int(x) >> (4 * i)) & 0xF for i in range(16)]
    o = [0] * 16
    for c in range(4):
        a0, a1, a2, a3 = n[c], n[c + 4], n[c + 8], n[c + 12]
        o[c] = a1 ^ a2 ^ a3
        o[c + 4] = a0 ^ a2 ^ a3
        o[c + 8] = a0 ^ a1 ^ a3
        o[c + 12] = a0 ^ a1 ^ a2
    y = 0
    for i in range(16):
        y |= (o[i] & 0xF) << (4 * i)
    return np.uint64(y) & M64


def _midori_shuffle(x):
    """Midori ShuffleCell: nibble permutation."""
    # Midori64 shuffle: [0,10,5,15,14,4,11,1,9,3,12,6,7,13,2,8]
    perm = [0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8]
    n = [(int(x) >> (4 * i)) & 0xF for i in range(16)]
    y = 0
    for i in range(16):
        y |= (n[perm[i]] & 0xF) << (4 * i)
    return np.uint64(y) & M64


def midori_red(v, k, nrounds):
    s = np.uint64(v) ^ np.uint64(k)
    for rnd in range(nrounds):
        s = _sbox_nibbles(s, SBOX_MIDORI0)
        s = _midori_shuffle(s)
        s = _midori_mixcolumn(s)
        s ^= RC64[rnd % len(RC64)] ^ _rotl64(np.uint64(k), 13 * (rnd + 1))
    return (s ^ (np.uint64(k) >> np.uint64(32))) & M64


def _chi3col(x):
    """3-bit column chi, Xoodoo-style, on interleaved groups.
    Group bits (i, i+21, i+42) for i in 0..20 (63 bits), bit 63 passthrough.
    y0 = x0 ^ (~x1 & x2), y1 = x1 ^ (~x2 & x0), y2 = x2 ^ (~x0 & x1)."""
    xi = int(x)
    y = 0
    for i in range(21):
        b0 = (xi >> i) & 1
        b1 = (xi >> (i + 21)) & 1
        b2 = (xi >> (i + 42)) & 1
        y |= ((b0 ^ ((~b1 & 1) & b2)) << i)
        y |= ((b1 ^ ((~b2 & 1) & b0)) << (i + 21))
        y |= ((b2 ^ ((~b0 & 1) & b1)) << (i + 42))
    y |= (((xi >> 63) & 1) << 63)
    return np.uint64(y) & M64


def chi3col(v, k, nrounds):
    s = np.uint64(v) ^ np.uint64(k)
    for rnd in range(nrounds):
        s = _chi3col(s)
        s = _rotl64(s, 7) ^ _rotl64(s, 29)
        s ^= RC64[rnd % len(RC64)] ^ _rotl64(np.uint64(k), 13 * (rnd + 1))
    return (s ^ (np.uint64(k) >> np.uint64(32))) & M64


def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f


def _mk_rounds(fn, n, fname):
    # Named wrapper (never a bare lambda): the gen script emits `_mix_scalar`
    # as `return {fn.__name__}(v, k)`; a lambda's __name__ ('<lambda>') is not
    # a valid identifier and produced a SyntaxError at S1 load (2026-10-08).
    def f(v, k):
        return fn(v, k, n)
    f.__name__ = fname
    return f


CANDIDATES_B4 = {
    "t6_theta5": (_mk_rounds(theta_spn, 5, "theta_spn5"), "S-box + theta parity, 5 rounds"),
    "t6_theta6": (_mk_rounds(theta_spn, 6, "theta_spn6"), "S-box + theta parity, 6 rounds"),
    "t6_theta7": (_mk_rounds(theta_spn, 7, "theta_spn7"), "S-box + theta parity, 7 rounds"),
    "t6_midori6": (_mk_rounds(midori_red, 6, "midori_red6"), "Midori64 reduced, 6 rounds"),
    "t6_midori7": (_mk_rounds(midori_red, 7, "midori_red7"), "Midori64 reduced, 7 rounds"),
    "t6_midori8": (_mk_rounds(midori_red, 8, "midori_red8"), "Midori64 reduced, 8 rounds"),
    "t6_chi3col8": (_mk_rounds(chi3col, 8, "chi3col8"), "3-bit column chi + rot, 8 rounds"),
    "t6_chi3col10": (_mk_rounds(chi3col, 10, "chi3col10"), "3-bit column chi + rot, 10 rounds"),
}

MIX_NP_B4 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B4.items()}

if __name__ == "__main__":
    # self-test: determinism + basic avalanche smoke
    import hashlib
    for name, (fn, desc) in CANDIDATES_B4.items():
        a = fn(np.uint64(0), np.uint64(0x123456789ABCDEF0))
        b = fn(np.uint64(1), np.uint64(0x123456789ABCDEF0))
        assert a != b, name
        print(f"{name}: ok ({desc})")

def _mix_scalar(v, k):
    return chi3col10(v, k)

def mix(v, k):
    import numpy as np
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP_B4['t6_chi3col10'](v, k)

def mix_np(V, K):
    return MIX_NP_B4['t6_chi3col10'](V, K)
