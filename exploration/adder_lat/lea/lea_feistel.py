#!/usr/bin/env python3
"""LEA-F: Feistel with carry-save-inspired F (track-3 LEA arm, 2026-10-12).

PIVOT from LEA-CS: the 64-bit CPA measures 83.0u in S0 (run_synth.py),
which alone exceeds the 18.6u frontier. Carlo's spec (carry-save + final
CPA) is cost-dead on arrival. This variant keeps the LEA-territory IDEA
(AND partial products + compressor tree, NO carry propagation in F) but
uses a Feistel chassis: bijective for ANY F, NO final CPA.

F(R, k):  p1 = rotl(R,a) & rotl(R,b)      (1 AND level)
          p2 = rotl(R,c) & rotl(R,d)      (1 AND level, parallel)
          out = p1 ^ p2 ^ R ^ k           (2 XOR levels)
        = 3 levels total.

Round: L' = R ; R' = L ^ F(R, k_i)       (1 XOR level)
Per round: 4 levels. 3 rounds = 12 levels.
"""

import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")

import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
M32 = np.uint64(0xFFFFFFFF)


def rotl32(x, r):
    r %= 32
    if r == 0:
        return x & M32
    return (((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32)


def leaF(R, k, a, b, c, d, e, f, g, h, i):
    """F-function: 4 AND pairs + linear diffusion + key. 32-bit.
    Doubled AND density (co-design fix 2026-10-12): 3-round Feistel needs
    more nonlinearity per round to diffuse sequential inputs.
    """
    p1 = rotl32(R, a) & rotl32(R, b)
    p2 = rotl32(R, c) & rotl32(R, d)
    p3 = rotl32(R, e) & rotl32(R, f)
    p4 = rotl32(R, g) & rotl32(R, h)
    return (p1 ^ p2 ^ p3 ^ p4 ^ rotl32(R, i) ^ np.uint64(k)) & M32


def lea_feistel(v, k, rounds_params):
    """v: 64-bit input. k: 64-bit key.
    rounds_params: list of (k_i, a,b,c,d,e,f,g,h,i) per round.
    Feistel on 32-bit halves. Output 64-bit."""
    L = np.uint64((np.uint64(v) >> np.uint64(32)) & M32)
    R = np.uint64(np.uint64(v) & M32)
    for (ki, a, b, c, d, e, f, g, h, i) in rounds_params:
        Fout = leaF(R, ki, a, b, c, d, e, f, g, h, i)
        L, R = R, (L ^ Fout) & M32
    # Final swap undone (standard): output = (R, L)
    return ((R << np.uint64(32)) | L) & M64


def lea_feistel_vec(V, k, rounds_params):
    """Vectorized over array V."""
    V = np.asarray(V, dtype=np.uint64)
    L = ((V >> np.uint64(32)) & M32)
    R = (V & M32)
    for (ki, a, b, c, d, e, f, g, h, i) in rounds_params:
        p1 = rotl32(R, a) & rotl32(R, b)
        p2 = rotl32(R, c) & rotl32(R, d)
        p3 = rotl32(R, e) & rotl32(R, f)
        p4 = rotl32(R, g) & rotl32(R, h)
        Fout = (p1 ^ p2 ^ p3 ^ p4 ^ rotl32(R, i) ^ np.uint64(ki)) & M32
        L, R = R, (L ^ Fout) & M32
    return ((R << np.uint64(32)) | L) & M64


if __name__ == "__main__":
    # Smoke test: bijectivity on 8-bit mini version (4-bit halves)
    import random
    rng = random.Random(0x1EA)

    def rotl4(x, r):
        r %= 4
        return ((x << r) | (x >> (4 - r))) & 0xF if r else x & 0xF

    def Feistel8(v, k, params):
        L, R = (v >> 4) & 0xF, v & 0xF
        for (ki, a, b, c, d) in params:
            p1 = rotl4(R, a) & rotl4(R, b)
            p2 = rotl4(R, c) & rotl4(R, d)
            Fout = (p1 ^ p2 ^ R ^ ki) & 0xF
            L, R = R, (L ^ Fout) & 0xF
        return ((R << 4) | L) & 0xFF

    for trial in range(3):
        k = rng.getrandbits(8)
        params = [(rng.getrandbits(4), rng.randrange(4), rng.randrange(4),
                   rng.randrange(4), rng.randrange(4)) for _ in range(3)]
        seen = set()
        for v in range(256):
            out = Feistel8(v, k, params)
            if out in seen:
                print(f"FAIL: collision at v={v}")
                break
            seen.add(out)
        else:
            print(f"PASS: 8-bit Feistel bijective (trial {trial})")
            continue
        break
