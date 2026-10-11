#!/usr/bin/env python3
"""D8 step 9: chi-triple sensitivity for the 3-round chi-first template.

Compare triple pairs on CCS (3r, lin513 all rounds): D (key=0) + DIFF probe.
CHI_A = [(1,2,13),(7,19,5)] (al_and6a-validated).
CHI_B = [(17,31,7),(11,23,37)] (wider, batch-9).
Plus systematic variations. Goal: is CHI_A near-optimal, or is there better?
"""
import numpy as np
import os
import sys
import time
import math

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
from lin_diff import lin_cell_logp
from step6b_linscreen import (lin_513, _rotl, _sbox64, _chi, _pbox64,
                              KS_STEP, RC, M64, U64)

WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"
SBOX_R = None  # use step6b's


def mix_np_triples(V, key, triples, pattern="CCS"):
    """triples: list of (a,b,c) for the chi rounds in order."""
    x = np.asarray(V, dtype=np.uint64)
    k = U64(key)
    ci = 0
    n = len(pattern)
    for i, ch in enumerate(pattern):
        rk = _rotl(k, KS_STEP * (i + 1)) ^ RC[i]
        t = x ^ rk
        if ch == "S":
            y = _sbox64(t)
        else:
            a, b, c = triples[ci]
            y = _chi(t, a, b, c)
            ci += 1
        z = _pbox64(y)
        z = lin_513(z)  # all rounds
        x = z
    return x & M64


def diff_probe(S, n_deltas=12):
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
    CHI_A = [(1, 2, 13), (7, 19, 5)]
    CHI_B = [(17, 31, 7), (11, 23, 37)]
    triple_sets = [
        ("CHI_A", CHI_A),
        ("CHI_B", CHI_B),
        ("A_swap", [CHI_A[1], CHI_A[0]]),
        ("close37", [(3, 4, 17), (5, 6, 23)]),
        ("close51", [(1, 3, 29), (2, 5, 41)]),
        ("wideA", [(1, 2, 37), (7, 19, 43)]),
        ("narrow", [(1, 2, 5), (3, 4, 7)]),
        ("mid", [(5, 9, 21), (11, 15, 33)]),
    ]
    N = 4096 * 64
    V = np.arange(N, dtype=np.uint64)
    key = 0x0
    print(f"{'triples':10s} {'D/4096':>8s} {'logp':>7s} {'diff|z|':>8s}", flush=True)
    for tag, triples in triple_sets:
        t1 = time.time()
        S = mix_np_triples(V, key, triples, "CCS")
        d, logp = lin_cell_logp(S)
        # DIFF probe needs N=2^16; reuse first 2^16 of S
        wz = diff_probe(S[:1 << 16])
        print(f"{tag:10s} {d:8d} {logp:7.1f} {wz:8.1f}  ({time.time()-t1:.0f}s)",
              flush=True)


if __name__ == "__main__":
    main()
