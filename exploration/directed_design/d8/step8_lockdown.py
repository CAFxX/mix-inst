#!/usr/bin/env python3
"""D8 step 8: lock down the 3-round chi-first finding.

- Multi-key D for CSC / CCS / CSS (lin513, all 3 rounds).
- LIN placement: drop-last (rounds 0,1) vs all-3.
- Reduced-N DIFF probe (custom, N=2^16) for top configs.
- Also: 4r SCSC drop-last (rounds 0,1,2) multi-key (saves 1.9u for free).
"""
import numpy as np
import os
import sys
import time
import math

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
from lin_diff import lin_cell_logp
from step6b_linscreen import (lin_513, _rotl, _sbox64, _chi, _pbox64,
                              CHI_TRIPLES, KS_STEP, RC, M64, U64)
from step7_rounds import mix_np_pattern

WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"


def D_of(V, key, lin_fn, pattern, lin_rounds):
    S = mix_np_pattern(V, key, lin_fn, pattern, lin_rounds)
    return lin_cell_logp(S)


def diff_probe(V, key, lin_fn, pattern, lin_rounds, n_deltas=12):
    """Reduced DIFF: deltas 2^k for k in 0..n_deltas-1, pairs x in [0,2^15).
    Returns worst |z| over deltas (low-8-bit chi2)."""
    N = 1 << 16
    S = mix_np_pattern(np.arange(N, dtype=np.uint64), key, lin_fn, pattern,
                       lin_rounds)
    S = np.asarray(S, dtype=np.uint64)
    n = 1 << 15
    worst_z = 0.0
    for k in range(n_deltas):
        dl = U64(1) << U64(k)
        xs = np.arange(n, dtype=np.uint64)
        ys = xs ^ dl
        dx = (S[xs] ^ S[ys]).astype(np.uint64)
        h8 = np.bincount((dx & U64(0xFF)).astype(np.int64), minlength=256).astype(float)
        exp = n / 256.0
        chi2 = float((((h8 - exp) ** 2) / exp).sum())
        df = 255
        z = abs(chi2 - df) / math.sqrt(2.0 * df)
        worst_z = max(worst_z, z)
    return worst_z


def main():
    N = 4096 * 64
    V = np.arange(N, dtype=np.uint64)
    keys = [0x0, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0]

    print("=== 3-round chi-first, multi-key D (lin513) ===", flush=True)
    for pattern in ["CSC", "CCS", "CSS"]:
        for lr_tag, lr in [("all3", {0, 1, 2}), ("drop-last", {0, 1})]:
            ds = []
            for k in keys:
                d, logp = D_of(V, k, lin_513, pattern, lr)
                ds.append(f"D={d} lp={logp:.1f}")
            print(f"{pattern} {lr_tag}: " + " | ".join(ds), flush=True)

    print("=== 4r SCSC drop-last (rounds 0,1,2), multi-key ===", flush=True)
    ds = []
    for k in keys:
        d, logp = D_of(V, k, lin_513, "SCSC", {0, 1, 2})
        ds.append(f"D={d} lp={logp:.1f}")
    print("SCSC drop-last: " + " | ".join(ds), flush=True)

    print("=== DIFF probe (N=2^16, deltas 2^0..2^11, worst|z|) ===", flush=True)
    for pattern, lr in [("CSC", {0, 1, 2}), ("CSC", {0, 1}),
                        ("CCS", {0, 1, 2}), ("CSS", {0, 1, 2}),
                        ("SCSC", {0, 1, 2, 3}), ("SCSC", {0, 1, 2})]:
        wz0 = diff_probe(V, 0x0, lin_513, pattern, lr)
        wz1 = diff_probe(V, 0x123456789ABCDEF0, lin_513, pattern, lr)
        print(f"{pattern} lr={sorted(lr)}: worst|z| key=0: {wz0:.1f}, "
              f"key=1234: {wz1:.1f}", flush=True)


if __name__ == "__main__":
    main()
