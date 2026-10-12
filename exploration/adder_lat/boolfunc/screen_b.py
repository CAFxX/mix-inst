#!/usr/bin/env python3
"""Design B (bipartite thin-Toffoli) triage.

1. Quick avalanche proxy for offsets (1,3), (1,7), (3,11): mean fraction of
   output bits flipped by a single input-bit flip, min over input bits.
2. Full Fisher triage (lin_diff.screen_lin_diff verbatim) on the best offset:
   N=2^18 sequential inputs, 10 keys (KEYS from screen_lib, N=2^18).
   KEEP iff LIN PASS and DIFF PASS (0 Holm rejections, both families).
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # verify_bij.py (design_b_vec)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")

import numpy as np
from lin_diff import screen_lin_diff
from screen_lib import KEYS, N

from verify_bij import design_b_vec as model

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def keyed(V, key, a, b):
    return model(np.asarray(V, dtype=np.uint64) ^ np.uint64(key), 64, a, b)


def popcount_vec(x):
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


def fisher_triage(a, b, verbose=True):
    V = np.arange(N, dtype=np.uint64)
    seq = {int(k): keyed(V, int(k), a, b) for k in KEYS[:10]}
    res = screen_lin_diff(seq, verbose=verbose)
    nrej = len(res["lin_rejected"]) + len(res["diff_rejected"])
    keep = (res["lin_verdict"] == "PASS" and res["diff_verdict"] == "PASS")
    return keep, res["lin_verdict"], res["diff_verdict"], nrej


def live_count(a, b):
    """Upper bound on #varying output bits under sequential inputs x<2^18.

    Input bits 0..17 vary; 18..63 are constant. All constants are 0/1-valued
    but constant either way, so: AND live iff both inputs live; XOR live iff
    either input live. (Over-approximates: XOR of dependent live signals could
    cancel, so true live count <= this.)
    """
    live_in = set(range(18))
    e = set()
    for i in range(32):
        if (2 * i in live_in) or ((2 * i + a) % 64 in live_in
                                   and (2 * i + b) % 64 in live_in):
            e.add(2 * i)
        if 2 * i + 1 in live_in:
            e.add(2 * i + 1)
    o = set()
    for i in range(32):
        if 2 * i in e:
            o.add(2 * i)
        c1, c2 = (2 * i + 1 + a) % 64, (2 * i + 1 + b) % 64
        if (2 * i + 1 in e) or (c1 in e and c2 in e):
            o.add(2 * i + 1)
    return len(o)


if __name__ == "__main__" and len(sys.argv) > 2:
    # CLI form: screen_b.py <a> <b> -> Fisher triage only on (a,b)
    a, b = int(sys.argv[1]), int(sys.argv[2])
    print(f"live-bit upper bound for ({a},{b}): {live_count(a, b)}/64", flush=True)
    keep, lv, dv, nrej = fisher_triage(a, b)
    print(f"FISHER({a},{b}): {'KEEP' if keep else 'KILL'} "
          f"lin={lv} diff={dv} nrej={nrej}", flush=True)
elif __name__ == "__main__":
    cands = [(1, 3), (1, 7), (3, 11)]
    print("== avalanche proxy ==", flush=True)
    scored = []
    for a, b in cands:
        t0 = time.time()
        mean, mn = avalanche_proxy(a, b)
        dt = time.time() - t0
        scored.append((mn, mean, a, b))
        print(f"  offsets=({a},{b}): mean_av={mean:.4f} min_av={mn:.4f} ({dt:.1f}s)",
              flush=True)
    scored.sort()
    # All three tie at min_av=0.0000 (some input bits have literally zero
    # avalanche) — the proxy cannot discriminate; they are all broken the same
    # way. Fisher-triage the canonical offset (1,3) (also the Verilog default).
    print("== Fisher triage on canonical (1,3) ==", flush=True)
    keep, lv, dv, nrej = fisher_triage(1, 3)
    print(f"FISHER(1,3): {'KEEP' if keep else 'KILL'} "
          f"lin={lv} diff={dv} nrej={nrej}", flush=True)
