#!/usr/bin/env python3
"""Design B large-offset triage: avalanche proxy + diagnostic constant-column
count + full Fisher triage (lin_diff.screen_lin_diff verbatim) for offsets
(1,3), (1,7), (3,11), (1,33), (3,35). All offsets ODD (bipartite constraint).
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")

import numpy as np
from lin_diff import screen_lin_diff
from screen_lib import KEYS, N
from verify_bij import design_b_vec as model


def keyed(V, key, a, b):
    return model(np.asarray(V, dtype=np.uint64) ^ np.uint64(key), 64, a, b)


def popcount_vec(x):
    # NOTE: screen_b.py's copy loops range(6) ("64 bits" comment) — it only
    # counts the low 6 bits. Count all 64 here.
    x = np.asarray(x, dtype=np.uint64)
    c = np.zeros(np.shape(x), dtype=np.uint64)
    for _ in range(64):
        c += x & np.uint64(1)
        x >>= np.uint64(1)
    return c


def avalanche_proxy(a, b, ntrials=4096, key=0x243F6A8885A308D3):
    rng = np.random.default_rng(0xBEEF)
    V = rng.integers(0, 2**64, size=ntrials, dtype=np.uint64)
    out0 = keyed(V, key, a, b)
    fracs = []
    for p in range(64):
        out1 = keyed(V ^ (np.uint64(1) << np.uint64(p)), key, a, b)
        fracs.append(float(np.mean(popcount_vec(out0 ^ out1))) / 64.0)
    return float(np.mean(fracs)), float(np.min(fracs))


def const_cols(a, b, key, nblocks_check=64):
    """# output columns constant over the full N=2^18 sequential stream."""
    V = np.arange(N, dtype=np.uint64)
    Y = keyed(V, int(key), a, b)
    nconst = 0
    for p in range(64):
        col = ((Y >> np.uint64(p)) & np.uint64(1)).astype(np.uint8)
        if col.min() == col.max():
            nconst += 1
    return nconst


def fisher_triage(a, b, verbose=True):
    V = np.arange(N, dtype=np.uint64)
    seq = {int(k): keyed(V, int(k), a, b) for k in KEYS[:10]}
    res = screen_lin_diff(seq, verbose=verbose)
    nrej = len(res["lin_rejected"]) + len(res["diff_rejected"])
    keep = (res["lin_verdict"] == "PASS" and res["diff_verdict"] == "PASS")
    return keep, res["lin_verdict"], res["diff_verdict"], nrej


if __name__ == "__main__":
    cands = [(1, 3), (1, 7), (3, 11), (1, 33), (3, 35)]
    print("== avalanche proxy ==", flush=True)
    for a, b in cands:
        t0 = time.time()
        mean, mn = avalanche_proxy(a, b)
        print(f"  offsets=({a},{b}): mean_av={mean:.4f} min_av={mn:.4f} "
              f"({time.time()-t0:.1f}s)", flush=True)
    print("== constant output columns over 2^18 sequential inputs ==", flush=True)
    for a, b in cands:
        t0 = time.time()
        cc = [const_cols(a, b, k) for k in KEYS[:3]]
        print(f"  offsets=({a},{b}): const_cols(keys0..2)={cc} "
              f"(vary={ [64-c for c in cc] }) ({time.time()-t0:.1f}s)", flush=True)
    print("== Fisher triage ==", flush=True)
    for a, b in cands:
        t0 = time.time()
        keep, lv, dv, nrej = fisher_triage(a, b, verbose=False)
        print(f"FISHER({a},{b}): {'KEEP' if keep else 'KILL'} "
              f"lin={lv} diff={dv} nrej={nrej} ({time.time()-t0:.1f}s)", flush=True)
