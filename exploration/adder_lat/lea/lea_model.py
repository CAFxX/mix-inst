#!/usr/bin/env python3
"""LEA-arm: carry-save redundant mixer (track-3, 2026-10-12).

Carlo's direction: sub-adder latency via carry-save (LEA/AGU territory).
State is a (sum, carry) redundant pair through N rounds -- NEVER
carry-propagate mid-construction. Nonlinearity via AND partial products
(multiplier-style), reduced with 3-2 compressors. ONE 64-bit CPA at the
end to collapse to binary. Key XORed into the compressor tree.

This module: bit-exact Python model + bijectivity probe.
"""

M64 = (1 << 64) - 1


def rotl(x, r, w=64):
    r %= w
    if r == 0:
        return x & ((1 << w) - 1)
    return (((x << r) | (x >> (w - r))) & ((1 << w) - 1))


def csa32(a, b, c, w=64):
    """3-2 compressor (full adder): a+b+c -> (sum, carry) with sum+2*carry = a+b+c.
    sum = a^b^c (2 XOR levels); carry = maj(a,b,c)<<1."""
    mask = (1 << w) - 1
    s = (a ^ b ^ c) & mask
    carry = (((a & b) | (a & c) | (b & c)) << 1) & mask
    return s, carry


def lea_round(s, c, k, a, b, d, e, w=64):
    """One carry-save round.
    p1 = rotl(s,a) & rotl(s,b)   (nonlinear partial products on sum)
    p2 = rotl(c,d) & rotl(c,e)   (nonlinear partial products on carry)
    (s1,c1) = 3-2(s, c, p1)
    (s2,c2) = 3-2(s1, c1, p2)
    s' = s2 ^ k ; c' = c2
    """
    mask = (1 << w) - 1
    p1 = rotl(s, a, w) & rotl(s, b, w)
    p2 = rotl(c, d, w) & rotl(c, e, w)
    s1, c1 = csa32(s, c, p1, w)
    s2, c2 = csa32(s1, c1, p2, w)
    return ((s2 ^ k) & mask), (c2 & mask)


def lea_mix(v, k, rounds_params, w=64):
    """Full mixer: v,k -> 64-bit output.
    rounds_params: list of (k_i, a, b, d, e) per round.
    Init: s = v ^ k0, c = k1 (split key into two words).
    After N rounds: output = s + c (mod 2^w) -- the ONE CPA.
    """
    mask = (1 << w) - 1
    # Key schedule: split 64-bit key into per-round words via rotation
    # (simple; a real design would use a proper schedule)
    s = (v ^ k) & mask
    c = rotl(k, 32, w)
    for (ki, a, b, d, e) in rounds_params:
        s, c = lea_round(s, c, ki, a, b, d, e, w)
    return (s + c) & mask


def test_bijectivity(w=8, n_rounds=3, trials=5):
    """Brute-force bijectivity on w-bit width: for random keys, check
    v -> lea_mix(v,k) is a permutation of 2^w values."""
    import random
    rng = random.Random(0x1EA)
    for t in range(trials):
        k = rng.getrandbits(w)
        params = []
        for _ in range(n_rounds):
            ki = rng.getrandbits(w)
            a, b = rng.randrange(w), rng.randrange(w)
            d, e = rng.randrange(w), rng.randrange(w)
            params.append((ki, a, b, d, e))
        seen = set()
        for v in range(1 << w):
            out = lea_mix(v, k, params, w)
            if out in seen:
                return False, f"collision at v={v}, trial {t}"
            seen.add(out)
        if len(seen) != (1 << w):
            return False, f"not surjective, trial {t}"
    return True, f"bijective on {trials} random keys at w={w}"


if __name__ == "__main__":
    import sys
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    ok, msg = test_bijectivity(w=w, n_rounds=3, trials=5)
    print(("PASS" if ok else "FAIL") + ": " + msg)
