"""Track 6, batch 3: cellular automata + Ascon-like bit-sliced designs.

Batch 2 results:
- t6_trivium64b: 25.5u / 1108 cells
- t6_grain64: 81.4u (too slow)
- t6_xorshift_nl: 36.7u
- t6_simon_like: 35.1u

Key insight from trivium64: structures where state update is mostly WIRING
(shift/register/permute) + shallow nonlinear feedback are extremely fast.

Batch 3:
  1. t6_ca30   : Wolfram Rule 30 cellular automaton, 16 steps on 64-bit ring
  2. t6_ca_mix : Mixed CA rules (30/90/150) alternating, 12 steps
  3. t6_ascon5 : Ascon-like: bit-sliced 5-bit S-box + linear diffusion, 6 rounds
  4. t6_gimli  : Gimli-like SP-box (but Gimli is 384-bit; this is 64-bit reduced)
"""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D), np.uint64(0x9E3779B97F4A7C15 ^ 0xDEADBEEF)]


# ------------------------------------------------------- t6_ca30
# Wolfram Rule 30: new[i] = old[i-1] XOR (old[i] OR old[i+1])
# 16 steps on 64-bit ring. Each step is 2 gate delays (OR then XOR).
# Rationale: CA gives excellent diffusion (each step spreads 1 bit to 3),
# and the update is local (wiring) + shallow. 16 steps x 2 = 32 gate delays.
def ca30(v, k):
    # state as Python int for bit manipulation
    s = int(np.uint64(v) ^ np.uint64(k))
    for rnd in range(16):
        ns = 0
        for i in range(64):
            left = (s >> ((i - 1) % 64)) & 1
            center = (s >> i) & 1
            right = (s >> ((i + 1) % 64)) & 1
            nb = left ^ (center | right)
            ns |= (nb << i)
        s = ns
        if rnd % 4 == 3:
            s ^= int(RC64[rnd // 4])
    return s ^ (int(k) >> 32)


# ------------------------------------------------------- t6_ca_mix
# Alternating CA rules for better cryptographic properties:
# Rule 30 (nonlinear) / Rule 150 (linear, x[i-1]^x[i]^x[i+1]) / Rule 90
# 12 steps: 30, 150, 90 repeating. Rationale: mixing linear and nonlinear
# rules can give better diffusion per step than pure Rule 30.
def ca_mix(v, k):
    s = int(np.uint64(v) ^ np.uint64(k))
    for rnd in range(12):
        rule = [30, 150, 90][rnd % 3]
        ns = 0
        for i in range(64):
            left = (s >> ((i - 1) % 64)) & 1
            center = (s >> i) & 1
            right = (s >> ((i + 1) % 64)) & 1
            if rule == 30:
                nb = left ^ (center | right)
            elif rule == 150:
                nb = left ^ center ^ right
            else:  # rule 90
                nb = left ^ right
            ns |= (nb << i)
        s = ns
        if rnd % 3 == 2:
            s ^= int(RC64[rnd // 3])
    return s ^ (int(k) >> 32)


# ------------------------------------------------------- t6_ascon5
# Ascon-like: 64-bit state as 5x ~13-bit rows? No — Ascon is 320-bit.
# Instead: bit-sliced 4-bit S-box (PRESENT S-box) applied to 16 nibbles,
# then linear diffusion via rotations. 6 rounds.
# PRESENT S-box: [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]
# Bit-sliced PRESENT S-box (from literature, AND-XOR form):
# We use a simple algebraic form. Actually, let me use a 4-bit S-box with
# known bitslice: the GIFT S-box bitslice is well-documented.
# GIFT S-box: [0x1,0xA,0x4,0xC,0x6,0xF,0x3,0x9,0x2,0xD,0xB,0x7,0x5,0x0,0x8,0xE]
# Bitslice (b3,b2,b1,b0) -> compute via boolean circuit.
# For simplicity and speed, use a 3-bit chi-like S-box on 21 triplets + 1 bit.
# Actually simplest: apply the Keccak chi 3-bit S-box bit-sliced across 64 bits.
# Chi 3-bit: out[i] = in[i] ^ ((~in[i+1]) & in[i+2]). Bit-sliced: 64 parallel.
# Then linear: XOR of rotations. 8 rounds.
def ascon5(v, k):
    # Represent as 3x64-bit slices? No — we have 64-bit state, apply chi
    # to consecutive triplets? That's not bit-sliced.
    # Bit-sliced approach: treat 64-bit as 64 parallel 1-bit lanes is trivial.
    # Instead: 21x 3-bit chi S-boxes on (b[3i], b[3i+1], b[3i+2]) + linear.
    # This is essentially a small SPN. Let me do it properly bit-sliced:
    # 64-bit state = 64 parallel instances is wrong.
    # Correct bitslice: we have ONE 64-bit value. Apply 3-bit S-box to
    # 21 triplets. That's 21 parallel S-boxes. Then permute bits + linear.
    x = int(np.uint64(v) ^ np.uint64(k))
    for rnd in range(8):
        # 3-bit chi on triplets (bits 0-62), bit 63 passes through
        y = 0
        for t in range(21):
            b0 = (x >> (3 * t)) & 1
            b1 = (x >> (3 * t + 1)) & 1
            b2 = (x >> (3 * t + 2)) & 1
            # chi: o0 = b0 ^ (~b1 & b2), o1 = b1 ^ (~b2 & b0), o2 = b2 ^ (~b0 & b1)
            o0 = b0 ^ ((1 ^ b1) & b2)
            o1 = b1 ^ ((1 ^ b2) & b0)
            o2 = b2 ^ ((1 ^ b0) & b1)
            y |= (o0 << (3 * t)) | (o1 << (3 * t + 1)) | (o2 << (3 * t + 2))
        y |= (x >> 63) << 63  # bit 63 unchanged
        # linear diffusion: y ^= rotl(y,19) ^ rotl(y,37)
        y = y ^ (((y << 19) | (y >> 45)) & ((1 << 64) - 1)) ^ (((y << 37) | (y >> 27)) & ((1 << 64) - 1))
        y ^= int(RC64[rnd % 6])
        x = y & ((1 << 64) - 1)
    return x


# ------------------------------------------------------- t6_gimli
# Gimli-like: 64-bit as 2x32-bit words (a, b). SP-box:
#   a ^= (b << 24) | (b >> 8)  (SP-box shift)
#   b ^= (a << 9) | (a >> 23)
#   then nonlinear: a ^= (b & ...)... Gimli uses:
#   x = a ^ (b << 1) ... let me use the actual Gimli SP-box on 2 words:
# Gimli SP-box (for 3 words x,y,z):
#   x = x ^ (z << 1) ^ ((y & z) << 2)
#   y = y ^ x        ^ ((x & z) << 1)
#   z = z ^ y        ^ ((x & y) << 3)
# For 2 words (a,b), adapt: use a,b and a rotated copy c = rotl(a,16)
# 6 rounds with small-large swap every 2 rounds (Gimli-like).
def gimli64(v, k):
    x = int(v); kk = int(k)
    a = (x ^ kk) & 0xFFFFFFFF
    b = ((x >> 32) ^ (kk >> 32)) & 0xFFFFFFFF
    for rnd in range(6):
        c = ((a << 16) | (a >> 16)) & 0xFFFFFFFF  # rotated copy
        # SP-box on (a, b, c)
        na = (a ^ (c << 1) ^ ((b & c) << 2)) & 0xFFFFFFFF
        nb = (b ^ a ^ ((a & c) << 1)) & 0xFFFFFFFF
        nc = (c ^ b ^ ((a & b) << 3)) & 0xFFFFFFFF
        a, b = na, nb
        # small swap every 2 rounds (Gimli-like)
        if rnd % 2 == 1:
            a, b = b, a
        # round constant on a
        a ^= (int(RC64[rnd]) & 0xFFFFFFFF) ^ (rnd * 0x9E3779B9 & 0xFFFFFFFF)
    return (((b & 0xFFFFFFFF) << 32) | (a & 0xFFFFFFFF)) & ((1 << 64) - 1)


CANDIDATES_B3 = {
    "t6_ca30": (ca30, "Wolfram Rule 30 CA, 16 steps"),
    "t6_ca_mix": (ca_mix, "Mixed CA rules 30/150/90, 12 steps"),
    "t6_ascon5": (ascon5, "3-bit chi triplets + linear, 8 rounds"),
    "t6_gimli": (gimli64, "Gimli-like SP-box on 2x32, 6 rounds"),
}


def _vec(fn):
    vf = np.vectorize(lambda v, k: fn(int(v), int(k)), otypes=[np.uint64])
    return lambda V, K: vf(np.asarray(V, dtype=np.uint64), np.asarray(K, dtype=np.uint64))


MIX_NP_B3 = {name: _vec(fn) for name, (fn, _) in CANDIDATES_B3.items()}

if __name__ == "__main__":
    for name, (fn, desc) in CANDIDATES_B3.items():
        g1 = fn(0x0, 0x123456789ABCDEF0)
        g2 = fn(0x123456789ABCDEF0, 0x0)
        print(f"{name}: {desc}")
        print(f"  golden1 = {g1:#018x}")
        print(f"  golden2 = {g2:#018x}")

def _mix_scalar(v, k):
    return gimli64(v, k)

def mix(v, k):
    import numpy as np
    if np.ndim(v) == 0 and np.ndim(k) == 0:
        return _mix_scalar(v, k)
    return MIX_NP_B3['t6_gimli'](v, k)

def mix_np(V, K):
    return MIX_NP_B3['t6_gimli'](V, K)
