"""Track 6, batch 2: variations on the Trivium breakthrough + new orthogonal ideas.

Batch 1 results:
- t6_trivium64: 19.8u / 372 cells (BREAKTHROUGH, S1 running)
- t6_narrow_arx: 91.5u (too slow, sequential adds)
- t6_feistel_arx: 533.8u (DEAD)
- t6_laidassey: 85.7u (not competitive)

Batch 2:
  1. t6_trivium64b: denser taps + more clocks (better diffusion, slightly slower?)
  2. t6_grain64   : Grain-inspired: 64-bit LFSR + 32-bit NFSR + nonlinear filter
  3. t6_xorshift_nl: xorshift128+ reduced + AND-rotation output filter
  4. t6_simon_like: Simon-inspired: x ^= (rotl(y,1)&rotl(y,8))^rotl(y,2) on 32-bit halves
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF),
        np.uint64(0x3C6EF372FE94F82A ^ 0x12345678), np.uint64(0xDAA66D2C7DDF743F ^ 0xABCDEF01)]


# ------------------------------------------------------- t6_trivium64b
# Denser taps: two AND terms + more linear taps. 8 macro-rounds x 8 clocks.
# Rationale: batch-1 taps may be too sparse for good diffusion; denser
# feedback improves mixing at modest gate cost.
def trivium64b(v, k):
    s = int(np.uint64(v) ^ np.uint64(k))
    for rnd in range(8):
        for _ in range(8):
            # denser: two AND pairs + three linear taps
            a1 = (s >> 5) & 1; b1 = (s >> 11) & 1
            a2 = (s >> 23) & 1; b2 = (s >> 31) & 1
            fb = (a1 & b1) ^ (a2 & b2) ^ ((s >> 17) & 1) ^ ((s >> 41) & 1) ^ ((s >> 53) & 1)
            s = ((s << 1) | fb) & ((1 << 64) - 1)
        s ^= int(RC64[rnd])
    return s ^ int(np.uint64(k) >> np.uint64(32))


# ------------------------------------------------------- t6_grain64
# Grain-inspired: 64-bit LFSR (linear, fast) + nonlinear filter combining
# LFSR bits with AND terms. 6 rounds x 10 clocks.
# LFSR poly: x^64 + x^59 + x^53 + x^47 + 1 (sparse, fast)
# Filter: h = l[7] ^ l[19] ^ l[33] ^ l[51] ^ (l[11]&l[29]) ^ (l[23]&l[43]) ^ (l[5]&l[37]&l[59])
def grain64(v, k):
    s = int(np.uint64(v) ^ np.uint64(k))
    for rnd in range(6):
        for _ in range(10):
            # LFSR feedback (linear)
            lfb = ((s >> 59) & 1) ^ ((s >> 53) & 1) ^ ((s >> 47) & 1) ^ (s & 1)
            # nonlinear filter output bit
            h = (((s >> 7) & 1) ^ ((s >> 19) & 1) ^ ((s >> 33) & 1) ^ ((s >> 51) & 1)
                 ^ ((((s >> 11) & 1) & ((s >> 29) & 1)))
                 ^ ((((s >> 23) & 1) & ((s >> 43) & 1)))
                 ^ ((((s >> 5) & 1) & ((s >> 37) & 1) & ((s >> 59) & 1))))
            # shift left, insert lfb ^ h ^ key bit (key mixing)
            kb = (int(k) >> ((rnd * 10) % 64)) & 1
            s = ((s << 1) | (lfb ^ h ^ kb)) & ((1 << 64) - 1)
        s ^= int(RC64[rnd])
    return s


# ------------------------------------------------------- t6_xorshift_nl
# xorshift64* variant: fast linear xorshift + nonlinear AND-rotation filter.
# xorshift: x ^= x<<13; x ^= x>>7; x ^= x<<17 (all wiring, no gates for shift)
# Then: x ^= (rotl(x,7) & rotl(x,23)) ^ rotl(x,41)  (nonlinear filter, 2 gates deep)
# 4 rounds. Rationale: xorshift gives excellent diffusion for free (wiring);
# a shallow AND filter adds nonlinearity at minimal delay.
def _rotl64_i(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & ((1 << 64) - 1) if r else x


def xorshift_nl(v, k):
    x = int(np.uint64(v) ^ np.uint64(k))
    for rnd in range(4):
        # xorshift (linear diffusion, free in hardware)
        x ^= (x << 13) & ((1 << 64) - 1)
        x ^= x >> 7
        x ^= (x << 17) & ((1 << 64) - 1)
        # nonlinear AND-rotation filter
        x ^= (_rotl64_i(x, 7) & _rotl64_i(x, 23)) ^ _rotl64_i(x, 41)
        # key injection
        x ^= int(RC64[rnd]) ^ (int(k) >> (16 * rnd))
    return x & ((1 << 64) - 1)


# ------------------------------------------------------- t6_simon_like
# Simon-inspired on 64-bit: split into 2x32, each round:
#   L ^= (rotl(R,1) & rotl(R,8)) ^ rotl(R,2) ^ rk; swap
# 10 rounds. Rationale: Simon's round function is 2 AND-depth; on 32-bit
# halves it should be fast. Different from chi (different rotation consts
# and Feistel structure vs SPN).
def _rotl32_i(x, r):
    r %= 32
    x &= 0xFFFFFFFF
    return ((x << r) | (x >> (32 - r))) & 0xFFFFFFFF if r else x


def simon_like(v, k):
    x = int(v); kk = int(k)
    L = x & 0xFFFFFFFF
    R = (x >> 32) & 0xFFFFFFFF
    for i in range(10):
        rk = (_rotl32_i(kk & 0xFFFFFFFF, 3 * i) ^ (int(RC64[i % 6]) & 0xFFFFFFFF)) & 0xFFFFFFFF
        # Simon round: L ^= f(R) ^ rk where f(y) = (rotl(y,1)&rotl(y,8))^rotl(y,2)
        f = ((_rotl32_i(R, 1) & _rotl32_i(R, 8)) ^ _rotl32_i(R, 2)) & 0xFFFFFFFF
        Ln = R
        Rn = (L ^ f ^ rk) & 0xFFFFFFFF
        L, R = Ln, Rn
    return ((R << 32) | L) & ((1 << 64) - 1)


CANDIDATES_B2 = {
    "t6_trivium64b": (trivium64b, "Trivium denser taps, 8 macro-rounds"),
    "t6_grain64": (grain64, "Grain-inspired LFSR + nonlinear filter"),
    "t6_xorshift_nl": (xorshift_nl, "xorshift + AND-rotation filter, 4 rounds"),
    "t6_simon_like": (simon_like, "Simon-inspired 32-bit Feistel, 10 rounds"),
}


def _vec(fn):
    vf = np.vectorize(lambda v, k: fn(int(v), int(k)), otypes=[np.uint64])
    return lambda V, K: vf(np.asarray(V, dtype=np.uint64), np.asarray(K, dtype=np.uint64))


MIX_NP_B2 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B2.items()}

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B2.items():
        g1 = fn(0x0, 0x123456789ABCDEF0)
        g2 = fn(0x123456789ABCDEF0, 0x0)
        print(f"{name}: {desc}")
        print(f"  golden1 = {g1:#018x}")
        print(f"  golden2 = {g2:#018x}")

def _mix_scalar(v, k):
    return xorshift_nl(v, k)

def mix(v, k):
    import numpy as np
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP_B2['t6_xorshift_nl'](v, k)

def mix_np(V, K):
    return MIX_NP_B2['t6_xorshift_nl'](V, K)
