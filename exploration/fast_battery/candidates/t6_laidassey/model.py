"""Track 6: Genuinely new constructions for RV64 mix.

NOT SPN. NOT chi/AND cascades. Orthogonal directions:
  1. narrow_arx : 4x16-bit ARX lanes (add-rotate-xor), lane mixing
  2. trivium64  : Trivium-inspired NFSR cascade on 64-bit state
  3. feistel_arx: 32-bit Feistel, ARX F-function
  4. laidassey  : Lai-Massey with ARX half-round function

Each provides mix(v, k) -> 64-bit output, bit-exact across Python/C/Verilog.
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint32(0xFFFFFFFF)
M16 = np.uint16(0xFFFF)


def _rotl64(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x & M64


def _rotl32(x, r):
    r %= 32
    x = np.uint32(x)
    return np.uint32(((x << np.uint32(r)) | (x >> np.uint32(32 - r)))) if r else x


def _rotl16(x, r):
    r %= 16
    x = np.uint16(x)
    return np.uint16(((x << np.uint16(r)) | (x >> np.uint16(16 - r)))) if r else x


RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF)]


# ---------------------------------------------------------------- narrow_arx
# 4x16-bit lanes. Each round: lane-local ARX (add const, rotate, xor neighbor),
# then cross-lane XOR mixing. 16-bit adds have ~1/4 the carry delay of 64-bit.
# Rationale: ARX nonlinearity from addition carry chain, but narrow so fast.
def narrow_arx_4r(v, k):
    x = np.uint64(v); kk = np.uint64(k)
    # split into 4x16-bit lanes (little-endian lane order)
    L = [np.uint16((x >> np.uint64(16 * i)) & np.uint64(0xFFFF)) for i in range(4)]
    KR = [np.uint16((kk >> np.uint64(16 * i)) & np.uint64(0xFFFF)) for i in range(4)]
    for rnd in range(4):
        # lane-local ARX: add rotated key + round const, rotate, xor neighbor
        for i in range(4):
            c = int((RC64[rnd] >> np.uint64(16 * i)) & np.uint64(0xFFFF))
            lane = (int(L[i]) + int(_rotl16(KR[i], 3 + rnd)) + c) & 0xFFFF
            L[i] = _rotl16(np.uint16(lane), 7)
        # cross-lane diffusion: xor-shift network
        L[0] ^= _rotl16(L[1], 5); L[2] ^= _rotl16(L[3], 11)
        L[1] ^= _rotl16(L[2], 3); L[3] ^= _rotl16(L[0], 9)
    out = np.uint64(0)
    for i in range(4):
        out |= np.uint64(L[i]) << np.uint64(16 * i)
    return int(out & M64)


# ---------------------------------------------------------------- trivium64
# Trivium-inspired: 64-bit state as shift register with AND-XOR feedback taps.
# 6 "macro-rounds", each clocks the register 8 positions with nonlinear feedback.
# Rationale: Trivium's AND-based nonlinearity is 1 gate deep; shifting is free
# (wiring). Diffusion via tap positions spread across the state.
# Taps chosen: feedback bit i uses state bits at (i+8), (i+8)&(i+13), (i+29).
def trivium64_6r(v, k):
    s = int(np.uint64(v) ^ np.uint64(k))  # 64-bit state
    for rnd in range(6):
        for _ in range(8):  # clock 8 positions per macro-round
            # nonlinear feedback: AND of two taps XOR linear taps
            fb = ((s >> 8) & 1) ^ (((s >> 8) & 1) & ((s >> 13) & 1)) ^ ((s >> 29) & 1) ^ ((s >> 47) & 1)
            s = ((s << 1) | fb) & ((1 << 64) - 1)
        # round constant injection to break symmetry
        s ^= int(RC64[rnd])
    return s ^ int(np.uint64(k) >> np.uint64(32))  # post-whiten


# ---------------------------------------------------------------- feistel_arx
# 32-bit Feistel, 8 rounds. F(y, rk) = ARX: add rk, rotate, xor-shift, add.
# Rationale: Feistel halves the width the F-function sees (32-bit adds are
# faster than 64-bit); 8 rounds of cheap ARX may beat 4 rounds of heavy SPN.
def _F_arx(y, rk):
    y = np.uint32(y); rk = np.uint32(rk)
    y = np.uint32(y + rk)
    y = _rotl32(y, 7)
    y ^= y >> np.uint32(11)
    y = np.uint32(y + _rotl32(rk, 13))
    y = _rotl32(y, 5)
    return y


def feistel_arx_8r(v, k):
    x = np.uint64(v); kk = np.uint64(k)
    L = np.uint32(x & np.uint64(0xFFFFFFFF))
    R = np.uint32((x >> np.uint64(32)) & np.uint64(0xFFFFFFFF))
    for i in range(8):
        rk = np.uint32((kk >> np.uint64(8 * (i % 8))) & np.uint64(0xFFFFFFFF))
        # derive round key by rotation to avoid all-zero issues
        rk = _rotl32(rk ^ np.uint32(RC64[i % 6] & np.uint64(0xFFFFFFFF)), 3 * i)
        Ln = R
        Rn = np.uint32(L ^ _F_arx(R, rk))
        L, R = Ln, Rn
    return int((np.uint64(R) << np.uint64(32)) | np.uint64(L))


# ---------------------------------------------------------------- laidassey
# Lai-Massey (IDEA-like): split 64 into 2x32. Each round: d = H(L^R),
# L ^= d, R ^= d, then swap. H is ARX: multiply-free, add/rotate/xor only.
# Rationale: Lai-Massey needs only one H evaluation per round (vs Feistel's
# one F per round but with swap). H on 32-bit XOR-difference.
def _H_lm(d, rk):
    d = np.uint32(d); rk = np.uint32(rk)
    d = np.uint32(d + rk)
    d = _rotl32(d, 9)
    d ^= d >> np.uint32(7)
    d = np.uint32(d + _rotl32(d, 4))
    return d


def laidassey_6r(v, k):
    x = np.uint64(v); kk = np.uint64(k)
    L = np.uint32(x & np.uint64(0xFFFFFFFF))
    R = np.uint32((x >> np.uint64(32)) & np.uint64(0xFFFFFFFF))
    for i in range(6):
        rk = _rotl32(np.uint32(kk & np.uint64(0xFFFFFFFF)) ^ np.uint32(RC64[i] & np.uint64(0xFFFFFFFF)), 5 * i)
        d = _H_lm(np.uint32(L ^ R), rk)
        L = np.uint32(L ^ d)
        R = np.uint32(R ^ d)
        if i < 5:  # no final swap
            L, R = R, L
    # final half-round (no swap): one more H for output mixing
    d = _H_lm(np.uint32(L ^ R), _rotl32(np.uint32(kk >> np.uint64(32)), 11))
    L = np.uint32(L ^ d); R = np.uint32(R ^ d)
    return int((np.uint64(R) << np.uint64(32)) | np.uint64(L))


# registry (scalar fns for goldens; vectorized wrappers below)
def _vec(fn):
    vf = np.vectorize(lambda v, k: fn(int(v), int(k)), otypes=[np.uint64])
    return lambda V, K: vf(np.asarray(V, dtype=np.uint64), np.asarray(K, dtype=np.uint64))

CANDIDATES = {
    "t6_narrow_arx": (narrow_arx_4r, "4-round 4x16-bit ARX lanes + cross-lane XOR"),
    "t6_trivium64": (trivium64_6r, "Trivium-inspired 64-bit NFSR, 6 macro-rounds"),
    "t6_feistel_arx": (feistel_arx_8r, "8-round 32-bit Feistel, ARX F-function"),
    "t6_laidassey": (laidassey_6r, "6-round Lai-Massey, ARX H-function"),
}

# vectorized entry points (for check_rtl / s1_screen)
def mix_np_narrow_arx(V, K): return _vec(narrow_arx_4r)(V, K)
def mix_np_trivium64(V, K): return _vec(trivium64_6r)(V, K)
def mix_np_feistel_arx(V, K): return _vec(feistel_arx_8r)(V, K)
def mix_np_laidassey(V, K): return _vec(laidassey_6r)(V, K)

MIX_NP = {
    "t6_narrow_arx": mix_np_narrow_arx,
    "t6_trivium64": mix_np_trivium64,
    "t6_feistel_arx": mix_np_feistel_arx,
    "t6_laidassey": mix_np_laidassey,
}


if __name__ == "__main__":
    # smoke: print goldens
    for name, (fn, desc) in CANDIDATES.items():
        g1 = fn(0x0, 0x123456789ABCDEF0)
        g2 = fn(0x123456789ABCDEF0, 0x0)
        print(f"{name}: {desc}")
        print(f"  golden1 = {g1:#018x}")
        print(f"  golden2 = {g2:#018x}")

def _mix_scalar(v, k):
    return laidassey_6r(v, k)

def mix(v, k):
    # dispatch: scalar -> scalar fn, array -> vectorized
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP['t6_laidassey'](v, k)

def mix_np(V, K):
    return MIX_NP['t6_laidassey'](V, K)
