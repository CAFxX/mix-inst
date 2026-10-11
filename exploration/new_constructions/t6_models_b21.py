"""Track 6, batch 21: genuinely-untested axes (incarnation D restart).

Four candidates, each a first-probe of an axis never tested in any track:

  t6_sb8em2a: 2-round Even-Mansour, 8-bit S-box (AES), bit-permutation.
    All prior S-box tests were 4-bit (Midori ~6-7u/round). 8-bit S-box as
    256-entry case may synthesize to ~4-5u. Only 2 S-box layers + 3 key XORs.
    If ~12-15u with quality, it's a new family.

  t6_sb8spn3a: 3-round SPN, 8-bit S-box (AES), permutation, per-round key.
    Stronger variant of the above; ~18-22u est.

  t6_shf6a: 6-stage shift-cascade: x ^= ((x<<a)&(x>>b)) ^ rotl(x,c) ^ rk.
    Identical skeleton to al_and6a except the nonlinear term uses SHIFTS
    (free wiring like rotations, but asymmetric — edge bits starve).
    Isolates shift-vs-rotation diffusion.

  t6_or6a: 6-stage OR-cascade: x ^= (ra|rb) ^ rc ^ rk.
    De Morgan twin of al_and6a. Same cost, different algebraic properties.
    S1 signature may differ.

Avalanche triage gates S0 (64 single-bit flips on fixed key).
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678),
        np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]

# AES S-box (FIPS-197)
SB8_AES = np.array([
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b,
    0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
    0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7, 0xfd, 0x93, 0x26,
    0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2,
    0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
    0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed,
    0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f,
    0x50, 0x3c, 0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
    0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
    0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14,
    0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
    0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79, 0xe7, 0xc8, 0x37, 0x6d,
    0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f,
    0x4b, 0xbd, 0x8b, 0x8a, 0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
    0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11,
    0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f,
    0xb0, 0x54, 0xbb, 0x16],
    dtype=np.uint64)

# Bit-permutation for byte S-boxes: bit (8*j+b) [byte j, bit b] ->
# byte (j+b)%8, bit j. Each input byte's 8 bits land in 8 DIFFERENT
# output bytes (optimal byte diffusion).
PBOX = [8 * ((j + b) % 8) + j for j in range(8) for b in range(8)]
# Sanity: must be a permutation of 0..63
assert sorted(PBOX) == list(range(64)), "PBOX not a permutation"


def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def _rk(key, j):
    return (_rotl64(key, 13 * (j + 1)) ^ RC64[j % 8]) & M64


def _sb8(x):
    y = np.zeros_like(x)
    for i in range(8):
        y |= SB8_AES[((x >> np.uint64(8 * i)) & np.uint64(0xFF))] << np.uint64(8 * i)
    return y & M64


def _pbox(x):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << np.uint64(PBOX[i])
    return y & M64


# Shift-cascade schedule: (left-shift a, right-shift b, rot c)
SHF_SCHED = [(5, 13, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59),
             (11, 37, 53), (3, 19, 61)]
# OR-cascade schedule: same as al_and6a's AND schedule for direct comparison
OR_SCHED = [(3, 11, 23), (17, 29, 41), (7, 31, 47), (23, 43, 59),
            (11, 37, 53), (5, 19, 61)]


def _shl64(x, s):
    return (x << np.uint64(s)) & M64 if s < 64 else np.zeros_like(x)


def _shr64(x, s):
    return (x >> np.uint64(s)) if s < 64 else np.zeros_like(x)


def t6_sb8em2a(v, k):
    """2-round Even-Mansour, 8-bit AES S-box."""
    x = (v ^ k) & M64
    for j in range(2):
        x = (_sb8(x ^ _rk(k, j))) & M64
        x = _pbox(x)
    x = (x ^ _rk(k, 2)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_sb8spn3a(v, k):
    """3-round SPN, 8-bit AES S-box, per-round key."""
    x = (v ^ k) & M64
    for j in range(3):
        x = (_sb8(x ^ _rk(k, j))) & M64
        x = _pbox(x)
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_shf6a(v, k):
    """6-stage shift-cascade: x ^= ((x<<a)&(x>>b)) ^ rotl(x,c) ^ rk."""
    x = (v ^ k) & M64
    for j in range(6):
        a, b, c = SHF_SCHED[j]
        x = (x ^ (_shl64(x, a) & _shr64(x, b)) ^ _rotl64(x, c) ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


def t6_or6a(v, k):
    """6-stage OR-cascade: x ^= (ra|rb) ^ rc ^ rk (De Morgan twin of AND)."""
    x = (v ^ k) & M64
    for j in range(6):
        a, b, c = OR_SCHED[j]
        x = (x ^ (_rotl64(x, a) | _rotl64(x, b)) ^ _rotl64(x, c) ^ _rk(k, j)) & M64
    return (x ^ (_rotl64(k, 13) >> np.uint64(32))) & M64


CANDIDATES_B21 = {
    # t6_sb8em2a TRIAGE-KILLED 2026-10-09: 2-round Even-Mansour avg=18.0
    # (even with optimal byte-spreading P-box) — 2 S-box layers structurally
    # insufficient for 64-bit keyed finalizer. Scoped kill, not global.
    "t6_sb8spn3a": (t6_sb8spn3a, "3-round SPN, 8-bit AES S-box"),
    "t6_shf6a": (t6_shf6a, "6-stage shift-cascade ((x<<a)&(x>>b))"),
    "t6_or6a": (t6_or6a, "6-stage OR-cascade (De Morgan twin of AND)"),
}
