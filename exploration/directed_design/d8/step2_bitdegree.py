#!/usr/bin/env python3
"""D8 step 2: per-output-bit analysis on 64-input blocks.

For each output bit j: truth table over x in [0,64) -> ANF degree (Mobius),
constancy. Compare nolin (dd9_scsc_nolin_a) vs linall (dd9_scsc_linall_a),
keys 0 / FFF...F / 123456789ABCDEF0. Also: random-64-input rank vs
consecutive-64 rank (is it the block structure?).
"""
import importlib.util
import numpy as np
import os
import sys
import time
from collections import Counter

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"


def load_model(name):
    spec = importlib.util.spec_from_file_location(
        "model_" + name, f"{FB}/candidates/{name}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def mobius_degree(tt):
    """tt: uint64 truth table of f on 6 vars (bit i = f(i)). Return ANF degree."""
    a = [(tt >> i) & 1 for i in range(64)]
    # FWHT over GF(2)
    step = 1
    while step < 64:
        for i in range(0, 64, 2 * step):
            for j in range(i, i + step):
                a[j + step] ^= a[j]
        step *= 2
    deg = 0
    for mask in range(64):
        if a[mask]:
            deg = max(deg, bin(mask).count("1"))
    return deg


def analyze(name, key, tag):
    m = load_model(name)
    N = 64
    V = np.arange(N, dtype=np.uint64)
    S = np.asarray(m.mix_np(V, np.full(N, np.uint64(key), dtype=np.uint64)),
                   dtype=np.uint64)
    degs = []
    const_bits = []
    for j in range(64):
        tt = 0
        for i in range(64):
            tt |= ((int(S[i]) >> j) & 1) << i
        if tt == 0 or tt == (1 << 64) - 1:
            const_bits.append(j)
            degs.append(0)
        else:
            degs.append(mobius_degree(tt))
    hist = Counter(degs)
    print(f"[{tag}] {name} key={key:#x}: degree histogram {dict(sorted(hist.items()))}")
    print(f"[{tag}] constant output bits on x in [0,64): {const_bits}")
    return degs, const_bits, S


def rank_of(S):
    a = [int(x) for x in S]
    r = 0
    for c in range(63, -1, -1):
        piv = -1
        for i in range(r, 64):
            if (a[i] >> c) & 1:
                piv = i
                break
        if piv < 0:
            continue
        a[r], a[piv] = a[piv], a[r]
        for i in range(r + 1, 64):
            if (a[i] >> c) & 1:
                a[i] ^= a[r]
        r += 1
    return r


def main():
    t0 = time.time()
    keys = [0x0, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0]
    for name in ["dd9_scsc_nolin_a", "dd9_scsc_linall_a"]:
        for k in keys:
            analyze(name, k, "BLOCK0")
    # random-input rank vs consecutive rank (nolin, key=0)
    m = load_model("dd9_scsc_nolin_a")
    rng = np.random.default_rng(42)
    for trial in range(3):
        V = rng.integers(0, 2**64, size=64, dtype=np.uint64)
        S = np.asarray(m.mix_np(V, np.full(64, np.uint64(0), dtype=np.uint64)),
                       dtype=np.uint64)
        print(f"[RAND] nolin key=0 trial {trial}: rank of 64 random outputs = {rank_of(S)}")
    # consecutive block rank for linall control (first block)
    m2 = load_model("dd9_scsc_linall_a")
    V = np.arange(64, dtype=np.uint64)
    S = np.asarray(m2.mix_np(V, np.full(64, np.uint64(0), dtype=np.uint64)), dtype=np.uint64)
    print(f"[BLOCK0] linall key=0: rank of 64 consecutive outputs = {rank_of(S)}")
    print(f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
