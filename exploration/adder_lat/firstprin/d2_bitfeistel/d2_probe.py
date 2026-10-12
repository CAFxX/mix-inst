#!/usr/bin/env python3
"""Quick structural probe: per-bit flip probabilities under single-bit input
deltas, and low-8 difference chi2 z-scores (the DIFF screen's core statistic).
Predicts Fisher-DIFF outcome in seconds.
"""
import math
import sys

import numpy as np

import d2_model as M
from d2_sweep import apply2
from d2_sweep2 import apply3

N = 1 << 18
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def build(form, taps, rounds, key):
    V = np.arange(N, dtype=np.uint64)
    K = np.uint64(key)
    if form == "1a":
        return M.apply(V, rounds, K, taps, taps)
    if form == "2a":
        return apply2(V, rounds, K, taps, taps)
    return apply3(V, rounds, K, taps)


def probe(form, taps, rounds, key=0x9E3779B97F4A7C15):
    S = build(form, taps, rounds, key)
    n = 1 << 17
    print(f"form={form} taps={taps} rounds={rounds}: per-bit P(flip|delta 2^k), "
          f"k=0..7, and low-8 chi2 z")
    for k in range(8):
        dl = np.uint64(1) << np.uint64(k)
        xs = np.arange(n, dtype=np.uint64)
        ys = xs ^ dl
        keep = xs < ys
        dx = (S[xs[keep]] ^ S[ys[keep]]).astype(np.uint64)
        npairs = int(keep.sum())
        pbit = [(float((dx >> np.uint64(j)) & np.uint64(1).sum()) if False else
                 float(np.sum((dx >> np.uint64(j)) & np.uint64(1))) / npairs)
                for j in range(8)]
        h8 = np.bincount((dx & np.uint64(0xFF)).astype(np.int64),
                         minlength=256).astype(float)
        exp = npairs / 256.0
        chi2 = float((((h8 - exp) ** 2) / exp).sum())
        z = abs(chi2 - 255) / math.sqrt(2 * 255)
        pb = " ".join(f"{p:.2f}" for p in pbit)
        print(f"  k={k}: pflip[0..7]=[{pb}] low8 z={z:8.1f}")
    # self-flip: P(out[k] flips | delta 2^k) for all k, full 64-bit random x
    rng = np.random.default_rng(0x5E1F)
    X = rng.integers(0, 2**64, size=4096, dtype=np.uint64)
    if form == "1a":
        A = lambda v: M.apply(v, rounds, np.uint64(key), taps, taps)
    elif form == "2a":
        A = lambda v: apply2(v, rounds, np.uint64(key), taps, taps)
    else:
        A = lambda v: apply3(v, rounds, np.uint64(key), taps)
    base = A(X)
    pself = np.zeros(64)
    for k in range(64):
        dl = np.uint64(1) << np.uint64(k)
        dx = A(X ^ dl) ^ base
        pself[k] = float(np.sum((dx >> np.uint64(k)) & np.uint64(1))) / 4096
    print(f"  P(out[k] flips | delta 2^k): min={pself.min():.3f} "
          f"mean={pself.mean():.3f} max={pself.max():.3f}")
    print(f"  even-k: min={pself[0::2].min():.3f} max={pself[0::2].max():.3f} | "
          f"odd-k: min={pself[1::2].min():.3f} max={pself[1::2].max():.3f}")


if __name__ == "__main__":
    probe("2a", (3, 5, 17, 21), 2)
    probe("2a", (3, 5, 17, 21), 3)
    probe("3a", (3, 11, 17, 27, 9, 31), 2)
