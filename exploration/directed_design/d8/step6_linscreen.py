#!/usr/bin/env python3
"""D8 step 6: screen candidate linear layers with the fast S1-LIN D screen.

Each candidate LIN is a Python function on 64-bit ints. SCSC template,
golden KS, pba19, rasC2_0, CHI_A triples. D = S1-LIN rank-deficiency count
on key=0 (4096 blocks); null expectation ~21.6. D<100 => promising.

Key theoretical question: is BIOJECTIVITY of the LIN layer the requirement
that single-rot[13] violates? Test bijective 1-XOR layers (shift, rot+passthrough).
"""
import numpy as np
import os
import sys
import time
from collections import Counter

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
from lin_diff import lin_cell_logp

WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"

SBOX_R = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]
PBOX = [(19 * i + 1) % 64 for i in range(64)]
RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
      0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054]
M64 = 0xFFFFFFFFFFFFFFFF
CHI_TRIPLES = [(1, 2, 13), (7, 19, 5)]
KS_STEP = 13


def rotl(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & M64 if r else x


def sbox64(x):
    y = 0
    for i in range(16):
        y |= SBOX_R[(x >> (4 * i)) & 0xF] << (4 * i)
    return y & M64


def chi64(x, a, b, c):
    return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64


def pbox64(x):
    y = 0
    for i in range(64):
        y |= ((x >> i) & 1) << PBOX[i]
    return y


# ---- candidate LIN layers (each: 64-bit -> 64-bit) ----
def lin_none(x):
    return x

def lin_rot13(x):
    return (x ^ rotl(x, 13)) & M64

def lin_513(x):
    return (x ^ rotl(x, 5) ^ rotl(x, 13)) & M64

def lin_shift1(x):
    return (x ^ (x >> 1)) & M64          # bijective (triangular), 1 XOR

def lin_shift7(x):
    return (x ^ (x >> 7)) & M64          # bijective (triangular), 1 XOR

def lin_rot13_p63(x):
    # x ^ rotl(x,13), but bit 63 passes through (bijective, 1 XOR delay)
    r = rotl(x, 13)
    y = (x ^ r) & M64
    y = (y & ~(1 << 63)) | (x & (1 << 63))
    return y

def lin_rot13_p0(x):
    r = rotl(x, 13)
    y = (x ^ r) & M64
    y = (y & ~1) | (x & 1)
    return y

def lin_13_27(x):
    return (x ^ rotl(x, 13) ^ rotl(x, 27)) & M64   # bijective 2-XOR pair


def mix_seq(N, key, lin_fn, placement):
    """placement: 'all' | 'sbox' (LIN after S rounds only). Returns uint64 array."""
    V = np.arange(N, dtype=np.uint64)
    st = [int(v) for v in V]
    ci = 0
    for i, ch in enumerate("SCSC"):
        rk = rotl(key, KS_STEP * (i + 1)) ^ RC[i]
        out = []
        for s in st:
            t = s ^ rk
            if ch == "S":
                y = sbox64(t)
            else:
                a, b, c = CHI_TRIPLES[ci]
                y = chi64(t, a, b, c)
            z = pbox64(y)
            if placement == "all" or (placement == "sbox" and ch == "S"):
                z = lin_fn(z)
            out.append(z)
        st = out
        if ch == "C":
            ci += 1
    return np.array(st, dtype=np.uint64)


def main():
    cands = [
        ("none/all", lin_none, "all"),
        ("rot13/all", lin_rot13, "all"),
        ("lin513/all", lin_513, "all"),
        ("shift1/all", lin_shift1, "all"),
        ("shift7/all", lin_shift7, "all"),
        ("rot13p63/all", lin_rot13_p63, "all"),
        ("rot13p0/all", lin_rot13_p0, "all"),
        ("pair13-27/all", lin_13_27, "all"),
        ("rot13/sbox", lin_rot13, "sbox"),
        ("rot13p63/sbox", lin_rot13_p63, "sbox"),
        ("shift1/sbox", lin_shift1, "sbox"),
        ("lin513/sbox", lin_513, "sbox"),
    ]
    key = 0x0
    N = 4096 * 64
    print(f"{'candidate':18s} {'D/4096':>8s} {'logp':>7s} {'eval_s':>6s}",
          flush=True)
    results = []
    for tag, fn, placement in cands:
        t1 = time.time()
        S = mix_seq(N, key, fn, placement)
        t_eval = time.time() - t1
        d, logp = lin_cell_logp(S)
        results.append((tag, d, logp))
        print(f"{tag:18s} {d:8d} {logp:7.1f} {t_eval:6.1f}s", flush=True)
    with open(f"{WORK}/step6_results.txt", "w") as f:
        for tag, d, logp in results:
            f.write(f"{tag} D={d} logp={logp:.1f}\n")
    print("wrote step6_results.txt")


if __name__ == "__main__":
    main()
