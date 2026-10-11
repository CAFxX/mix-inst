"""
MIX64 reference model — bit-accurate Python model of the proposed RISC-V
`mix rd, rs1(val), rs2(key)` instruction datapath.

Datapath (all stages bijective in `val` for any fixed `key`):
  1. x  = val + key                      (mod 2^64, nonlinear via carries)
  2. x ^= x >> 30 ; x ^= (x << 27)       (free linear pre-diffusion, ASIC wiring)
  3. a  = lo32(x) * C1, b = hi32(x) * C2 (TWO PARALLEL 32-bit multiplies,
     C1/C2 odd -> bijective; delay ~0.55x of one 64-bit multiply)
  4. two Feistel rounds with key-dependent 32-bit rotates (bijective):
       a1 = a + b ;        b1 = b  ^ ROTL32(a1, key[4:0])
       b2 = b1 + a1 ;      a2 = a1 ^ ROTL32(b2, key[9:5])
  5. x = (b2:a2) ^ key ; x = ROTL64(x, key[5:0])
  6. x ^= x >> 31 ; x ^= (x << 17)       (final polish, low-bit diffusion)

Critical path ~= one 32-bit multiply + a handful of add/XOR/mux levels,
i.e. comfortably under one full 64x64 multiplier delay.
"""

M64 = (1 << 64) - 1
M32 = (1 << 32) - 1

# Odd 32-bit constants (murmur3 fmix32 pair, well studied)
C1 = 0x85EBCA6B
C2 = 0xC2B2AE35
assert C1 & 1 and C2 & 1


def rotl32(v, r):
    r &= 31
    v &= M32
    if r == 0:
        return v
    return (((v << r) | (v >> (32 - r)))) & M32


def rotl64(v, r):
    r &= 63
    v &= M64
    if r == 0:
        return v
    return (((v << r) | (v >> (64 - r)))) & M64


def mix64(val, key):
    val &= M64
    key &= M64
    x = (val + key) & M64                      # 1: key injection (nonlinear)
    x ^= (x >> 30)                             # 2a: pre-diffusion
    x = (x ^ ((x << 27) & M64)) & M64          # 2b
    lo = x & M32
    hi = (x >> 32) & M32
    a = (lo * C1) & M32                        # 3: twin nonlinear multiplies
    b = (hi * C2) & M32
    r1 = key & 31
    r2 = (key >> 5) & 31
    a1 = (a + b) & M32                         # 4: Feistel round 1
    b1 = b ^ rotl32(a1, r1)
    b2 = (b1 + a1) & M32                       #    Feistel round 2
    a2 = a1 ^ rotl32(b2, r2)
    x = ((b2 << 32) | a2) & M64
    x ^= key                                   # 5: second key injection
    x = rotl64(x, key & 63)
    x ^= (x >> 31)                             # 6a: final polish
    x = (x ^ ((x << 17) & M64)) & M64          # 6b
    return x


# ----------------------------------------------------------------------------
# Parameterized reduced-width variant (for exhaustive bijectivity proofs).
# n = total width (even), halves = n/2 (must be a power of two).
# ----------------------------------------------------------------------------
def mix_n(val, key, n, c1, c2, s1, s2, s3):
    assert n % 2 == 0
    w = n // 2
    assert w & (w - 1) == 0
    M = (1 << n) - 1
    mh = (1 << w) - 1

    def rotl(v, r, ww):
        r &= ww - 1
        v &= (1 << ww) - 1
        if r == 0:
            return v
        return (((v << r) | (v >> (ww - r)))) & ((1 << ww) - 1)

    val &= M
    key &= M
    x = (val + key) & M
    x ^= (x >> s1)
    x = (x ^ ((x << s2) & M)) & M
    lo = x & mh
    hi = (x >> w) & mh
    a = (lo * c1) & mh
    b = (hi * c2) & mh
    r1 = key & (w - 1)
    r2 = (key >> 5) & (w - 1)
    a1 = (a + b) & mh
    b1 = b ^ rotl(a1, r1, w)
    b2 = (b1 + a1) & mh
    a2 = a1 ^ rotl(b2, r2, w)
    x = ((b2 << w) | a2) & M
    x ^= key
    x = rotl(x, key & (n - 1), n)
    x ^= (x >> s3)
    return x & M


def mix16(val, key):
    # n=16 scaled shifts: s1 = 30*16/64 ~ 7, s2 = 27*16/64 ~ 6, s3 = 31*16/64 ~ 7
    return mix_n(val, key, 16, 0xA3, 0xC9, 7, 6, 7)


# ----------------------------------------------------------------------------
# Baselines for head-to-head comparison (unkeyed; key folded in as val^key)
# ----------------------------------------------------------------------------
def splitmix64_final(z):
    z = (z + 0x9E3779B97F4A7C15) & M64
    z ^= z >> 30
    z = (z * 0xBF58476D1CE4E5B9) & M64
    z ^= z >> 27
    z = (z * 0x94D049BB133111EB) & M64
    z ^= z >> 31
    return z & M64


def murmur3_fmix64(h):
    h ^= h >> 33
    h = (h * 0xFF51AFD7ED558CCD) & M64
    h ^= h >> 33
    h = (h * 0xC4CEB9FE1A85EC53) & M64
    h ^= h >> 33
    return h & M64


def baseline_splitmix(val, key):
    return splitmix64_final(val ^ key)


def baseline_murmur(val, key):
    return murmur3_fmix64(val ^ key)
