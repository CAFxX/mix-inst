#!/usr/bin/env python3
"""D8 step 6b: screen candidate linear layers, NUMPY-vectorized (fast).

Same as step6 but vectorized over V (like model.py's mix_np): ~1s per
candidate instead of ~60s.
"""
import numpy as np
import os
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
from lin_diff import lin_cell_logp

WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"

SBOX_R = np.array([0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14],
                  dtype=np.uint64)
PBOX = np.array([(19 * i + 1) % 64 for i in range(64)], dtype=np.uint64)
RC = np.array([0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
               0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054], dtype=np.uint64)
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
CHI_TRIPLES = [(1, 2, 13), (7, 19, 5)]
KS_STEP = 13
U64 = np.uint64


def _rotl(x, r):
    r %= 64
    if r == 0:
        return x
    r = U64(r)
    return ((x << r) | (x >> (U64(64) - r))) & M64


def _sbox64(x):
    y = np.zeros_like(x)
    for i in range(16):
        y |= SBOX_R[((x >> U64(4 * i)) & U64(0xF)).astype(np.int64)] << U64(4 * i)
    return y & M64


def _chi(x, a, b, c):
    return (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c)) & M64


def _pbox64(x):
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> U64(i)) & U64(1)) << PBOX[i]
    return y & M64


# ---- candidate LIN layers (numpy) ----
def lin_none(x): return x
def lin_rot13(x): return (x ^ _rotl(x, 13)) & M64
def lin_513(x): return (x ^ _rotl(x, 5) ^ _rotl(x, 13)) & M64
def lin_shift1(x): return (x ^ (x >> U64(1))) & M64
def lin_shift7(x): return (x ^ (x >> U64(7))) & M64
def lin_shift31(x): return (x ^ (x >> U64(31))) & M64
def lin_rot13_p63(x):
    y = (x ^ _rotl(x, 13)) & M64
    return (y & ~U64(1 << 63)) | (x & U64(1 << 63))
def lin_rot13_p0(x):
    y = (x ^ _rotl(x, 13)) & M64
    return (y & ~U64(1)) | (x & U64(1))
def lin_13_27(x): return (x ^ _rotl(x, 13) ^ _rotl(x, 27)) & M64
def lin_1_2(x): return (x ^ _rotl(x, 1) ^ _rotl(x, 2)) & M64
def lin_7_19(x): return (x ^ _rotl(x, 7) ^ _rotl(x, 19)) & M64


def mix_np_vec(V, key, lin_fn, placement):
    x = np.asarray(V, dtype=np.uint64)
    k = U64(key)
    ci = 0
    for i, ch in enumerate("SCSC"):
        rk = _rotl(k, KS_STEP * (i + 1)) ^ RC[i]
        t = x ^ rk
        if ch == "S":
            y = _sbox64(t)
        else:
            a, b, c = CHI_TRIPLES[ci]
            y = _chi(t, a, b, c)
            ci += 1
        z = _pbox64(y)
        if placement == "all" or (placement == "sbox" and ch == "S"):
            z = lin_fn(z)
        x = z
    return x & M64


def main():
    cands = [
        ("none/all", lin_none, "all"),
        ("rot13/all", lin_rot13, "all"),
        ("lin513/all", lin_513, "all"),
        ("shift1/all", lin_shift1, "all"),
        ("shift7/all", lin_shift7, "all"),
        ("shift31/all", lin_shift31, "all"),
        ("rot13p63/all", lin_rot13_p63, "all"),
        ("rot13p0/all", lin_rot13_p0, "all"),
        ("pair13-27/all", lin_13_27, "all"),
        ("pair1-2/all", lin_1_2, "all"),
        ("pair7-19/all", lin_7_19, "all"),
        ("rot13/sbox", lin_rot13, "sbox"),
        ("rot13p63/sbox", lin_rot13_p63, "sbox"),
        ("shift1/sbox", lin_shift1, "sbox"),
        ("shift7/sbox", lin_shift7, "sbox"),
        ("lin513/sbox", lin_513, "sbox"),
        ("pair13-27/sbox", lin_13_27, "sbox"),
    ]
    key = 0x0
    N = 4096 * 64
    V = np.arange(N, dtype=np.uint64)
    print(f"{'candidate':18s} {'D/4096':>8s} {'logp':>7s} {'eval_s':>6s}", flush=True)
    results = []
    for tag, fn, placement in cands:
        t1 = time.time()
        S = mix_np_vec(V, key, fn, placement)
        t_eval = time.time() - t1
        d, logp = lin_cell_logp(S)
        results.append((tag, d, logp))
        print(f"{tag:18s} {d:8d} {logp:7.1f} {t_eval:6.1f}s", flush=True)
    with open(f"{WORK}/step6b_results.txt", "w") as f:
        for tag, d, logp in results:
            f.write(f"{tag} D={d} logp={logp:.1f}\n")
    print("wrote step6b_results.txt")


if __name__ == "__main__":
    main()
