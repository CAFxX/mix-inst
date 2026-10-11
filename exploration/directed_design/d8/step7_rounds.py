#!/usr/bin/env python3
"""D8 step 7: multi-key robustness of passing LINs + round-count/pattern screen.

Q1: are the 2-XOR pairs robustly clean on keys 0 / FFF..F / 1234..?
Q2: does 3-round mixed (SCS, CSC, SSC, CCS, CSC...) with full 2-XOR LIN pass?
Q3: does LIN on 3/4 rounds (drop one) pass?
"""
import numpy as np
import os
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
from lin_diff import lin_cell_logp
from step6b_linscreen import (mix_np_vec, lin_513, lin_13_27, lin_1_2,
                              _rotl, _sbox64, _chi, _pbox64,
                              CHI_TRIPLES, KS_STEP, RC, M64, U64)

WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"


def mix_np_pattern(V, key, lin_fn, pattern, lin_rounds):
    """pattern: e.g. 'SCS'. lin_rounds: set of round indices with LIN on."""
    x = np.asarray(V, dtype=np.uint64)
    k = U64(key)
    ci = 0
    for i, ch in enumerate(pattern):
        rk = _rotl(k, KS_STEP * (i + 1)) ^ RC[i]
        t = x ^ rk
        if ch == "S":
            y = _sbox64(t)
        else:
            a, b, c = CHI_TRIPLES[ci % len(CHI_TRIPLES)]
            y = _chi(t, a, b, c)
            ci += 1
        z = _pbox64(y)
        if i in lin_rounds:
            z = lin_fn(z)
        x = z
    return x & M64


def D_of(V, key, lin_fn, pattern, lin_rounds):
    S = mix_np_pattern(V, key, lin_fn, pattern, lin_rounds)
    d, logp = lin_cell_logp(S)
    return d, logp


def main():
    N = 4096 * 64
    V = np.arange(N, dtype=np.uint64)
    keys = [0x0, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0]

    print("=== Q1: multi-key robustness (4r SCSC, lin all rounds) ===", flush=True)
    for tag, fn in [("lin513", lin_513), ("pair13-27", lin_13_27), ("pair1-2", lin_1_2)]:
        ds = []
        for k in keys:
            d, logp = D_of(V, k, fn, "SCSC", {0, 1, 2, 3})
            ds.append((d, logp))
        print(f"{tag:12s}: " + " ".join(f"k={k:#x} D={d} lp={lp:.1f}"
                                        for k, (d, lp) in zip(keys, ds)), flush=True)

    print("=== Q2: 3-round mixed patterns, full 2-XOR LIN ===", flush=True)
    for pattern in ["SCS", "CSC", "SSC", "CCS", "SCS", "CSS"]:
        lr = set(range(len(pattern)))
        d, logp = D_of(V, 0x0, lin_513, pattern, lr)
        print(f"{pattern} lin513/all: D={d} logp={logp:.1f}", flush=True)

    print("=== Q3: 4r SCSC, LIN dropped on one round ===", flush=True)
    for drop in [0, 1, 2, 3]:
        lr = {0, 1, 2, 3} - {drop}
        d, logp = D_of(V, 0x0, lin_513, "SCSC", lr)
        print(f"SCSC lin513 drop-r{drop}: D={d} logp={logp:.1f}", flush=True)


if __name__ == "__main__":
    main()
