#!/usr/bin/env python3
"""D8 step 3: per-round diffusion instrumentation.

Implements the SCSC round stepper directly (tappable), cross-checked
bit-exact against the generated model.py files. For x = HIGH | i (i in
[0,64), HIGH random 58-bit-aligned), records after each round:
  #varying bit positions, ANF-degree histogram (in the 6 input bits i).

Compares LIN variants: none, [13], [5,13], and probes.
"""
import importlib.util
import numpy as np
import os
import sys
import time
from collections import Counter

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"

SBOX_R = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]
PBOX = [(19 * i + 1) % 64 for i in range(64)]
RC = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
      0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054]
M64 = 0xFFFFFFFFFFFFFFFF
CHI_TRIPLES = [(1, 2, 13), (7, 19, 5)]  # rounds 1, 3
KS_STEP = 13


def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << r) | (x >> (64 - r))) & M64


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


def lin64(x, rots):
    y = x
    for r in rots:
        y ^= rotl(x, r)
    return y & M64


def run_rounds(x, key, rots, pattern="SCSC", tap=False):
    """rots: [] | [r] | [a,b]. Returns final state; if tap, list of states
    after each round (post-LIN)."""
    states = []
    ci = 0
    st = x
    for i, ch in enumerate(pattern):
        rk = rotl(key, KS_STEP * (i + 1)) ^ RC[i]
        t = st ^ rk
        if ch == "S":
            y = sbox64(t)
        else:
            a, b, c = CHI_TRIPLES[ci % len(CHI_TRIPLES)]
            ci += 1
            y = chi64(t, a, b, c)
        z = pbox64(y)
        if rots:
            z = lin64(z, rots)
        st = z
        if tap:
            states.append(st)
    return (st, states) if tap else st


def mobius_degree(tt):
    a = [(tt >> i) & 1 for i in range(64)]
    step = 1
    while step < 64:
        for i in range(0, 64, 2 * step):
            for j in range(i, i + step):
                a[j + step] ^= a[j]
        step *= 2
    deg = 0
    for mask in range(64):
        if a[mask]:
            w = bin(mask).count("1")
            if w > deg:
                deg = w
    return deg


def profile(states_list, label):
    """states_list: list of (round_idx, state_int64_array(64,)). Print per-round
    #varying + degree hist."""
    print(f"--- {label} ---")
    for ri, S in states_list:
        degs = []
        nvar = 0
        for j in range(64):
            tt = 0
            for i in range(64):
                tt |= ((int(S[i]) >> j) & 1) << i
            if tt == 0 or tt == (1 << 64) - 1:
                degs.append(0)
            else:
                nvar += 1
                degs.append(mobius_degree(tt))
        hist = Counter(degs)
        print(f"  after round {ri}: varying={nvar:2d} deg_hist={dict(sorted(hist.items()))}")


def main():
    # bit-exactness check vs generated models
    rng = np.random.default_rng(7)
    for name, rots in [("dd9_scsc_nolin_a", []), ("dd9_scsc_linall_a", [5, 13]),
                       ("dd10_scsc_singlerot_a", [13])]:
        spec = importlib.util.spec_from_file_location(
            "model_" + name, f"{FB}/candidates/{name}/model.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        ok = True
        for _ in range(30):
            v = int(rng.integers(0, 2**64, dtype=np.uint64))
            k = int(rng.integers(0, 2**64, dtype=np.uint64))
            if run_rounds(v, k, rots) != m.mix(v, k):
                ok = False
                print(f"MISMATCH {name} v={v:#x} k={k:#x}")
                break
        print(f"bit-exact vs {name}: {'OK' if ok else 'FAIL'}")

    # per-round diffusion profiles, random HIGH, i in [0,64)
    key = 0x123456789ABCDEF0
    for trial in range(2):
        HIGH = int(rng.integers(0, 2**64, dtype=np.uint64)) & ~0x3F
        xs = np.array([HIGH | i for i in range(64)], dtype=np.uint64)
        for label, rots in [("nolin", []), ("singlerot[13]", [13]),
                             ("lin(5,13)", [5, 13])]:
            _, states = run_rounds_vec(xs, key, rots, tap=True)
            prof = [(ri, np.array([int(v) for v in st], dtype=np.uint64))
                    for ri, st in enumerate(states)]
            profile(prof, f"{label} trial{trial} HIGH={HIGH:#x}")


def run_rounds_vec(xs, key, rots, pattern="SCSC", tap=False):
    states = []
    ci = 0
    st = [int(x) for x in xs]
    for i, ch in enumerate(pattern):
        rk = rotl(key, KS_STEP * (i + 1)) ^ RC[i]
        out = []
        for s in st:
            t = s ^ rk
            if ch == "S":
                y = sbox64(t)
            else:
                a, b, c = CHI_TRIPLES[ci % len(CHI_TRIPLES)]
                y = chi64(t, a, b, c)
            z = pbox64(y)
            if rots:
                z = lin64(z, rots)
            out.append(z)
        st = out
        if ch == "C":
            ci += 1
        if tap:
            states.append(st)
    return (st, states) if tap else st


if __name__ == "__main__":
    main()
