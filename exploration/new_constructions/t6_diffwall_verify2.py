#!/usr/bin/env python3
"""DIFF-wall mechanism verification v2 (track 6, 2026-10-10).

v1 confirmed for t6_lane3b: 17 deterministic output bits, per-stage fold
counts 126 -> 113 -> 63 (skeleton never randomizes). v2 adds max output |z|
(bias mode) and fixes the worst_cfg=None crash; logN=18 for speed.

For each candidate: over keys x 18 weight-1 deltas (random inputs):
  - deterministic output bits (P exactly 0/1)
  - max per-bit |z| (bias)
Then per-stage deterministic-bit decay for the worst (key, delta).
"""
import importlib.util
import os
import sys

import numpy as np

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions")
import t6_models_b32 as T6


def load_model(name):
    spec = importlib.util.spec_from_file_location(
        "m_" + name, os.path.join(FB, name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def lane_stages(V, K, sa, sb, ss):
    a = (V ^ K) & M64
    b = rotl(K, 29)
    states = []
    for ((pa, qa), da), ((pb, qb), db), s in zip(sa, sb, ss):
        an = (a ^ (rotl(a, pa) & rotl(a, qa)) ^ rotl(a, da)) & M64
        bn = (b ^ (rotl(b, pb) & rotl(b, qb)) ^ rotl(b, db) ^ rotl(a, s)) & M64
        a, b = an, bn
        states.append((a, b))
    return states, (a ^ b ^ rotl(K, 13)) & M64


def sand_stages(V, K, sched):
    x = (V ^ K) & M64
    states = []
    for a, (b, c), d in sched:
        x = (x ^ rotl(x, a) ^ (rotl(x, b) & rotl(x, c)) ^ rotl(x, d)) & M64
        states.append(x)
    return states, (x ^ rotl(K, 13)) & M64


def skip_stages(V, K, sched):
    x = (V ^ K) & M64
    xm1 = np.zeros_like(x)
    states = []
    for (a, b), d, s in sched:
        xn = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, d) ^ rotl(xm1, s)) & M64
        xm1, x = x, xn
        states.append(x)
    return states, (x ^ rotl(K, 13)) & M64


AND6A = None


def and6a_stages(V, K):
    global AND6A
    if AND6A is None:
        AND6A = load_model("al_and6a")
    x = (V ^ K) & M64
    states = []
    for a, b, c in AND6A.STAGES:
        x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
        states.append(x)
    return states, (x ^ rotl(K, 13)) & M64


def bitstats(x0, x1):
    """(deterministic-bit count, max|z|) of the differential x0^x1."""
    dout = x0 ^ x1
    n = dout.shape[0]
    bits = np.unpackbits(dout.view(np.uint8)).reshape(n, 64)
    cnt = bits.sum(axis=0)
    det = int(((cnt == 0) | (cnt == n)).sum())
    p = cnt / n
    z = np.abs((p - 0.5) / np.sqrt(0.25 / n)).max()
    return det, float(z)


def foldstats(s0, s1):
    """Deterministic-bit count for a (possibly dual-lane) state pair."""
    a, b = s0, s1
    if isinstance(a, tuple):
        da, _ = bitstats(a[0], b[0])
        db, _ = bitstats(a[1], b[1])
        return da + db
    d, _ = bitstats(a, b)
    return d


def analyze(name, stage_fn, keys, deltas, logN=18, seed=999):
    rng = np.random.default_rng(seed)
    n = 1 << logN
    print("=== %s ===" % name, flush=True)
    worst = (0, 0.0, None)  # det, z, (key, k)
    per_stage = {}
    for key in keys:
        K = np.full(n, np.uint64(key), dtype=np.uint64)
        for k in deltas:
            d = np.uint64(1) << np.uint64(k)
            V = rng.integers(0, 2**64, size=n, dtype=np.uint64)
            s0, o0 = stage_fn(V, K)
            s1, o1 = stage_fn(V ^ d, K)
            det, z = bitstats(o0, o1)
            if (det, z) > (worst[0], worst[1]):
                worst = (det, z, (key, k))
            if k not in per_stage:
                per_stage[k] = [foldstats(a, b) for a, b in zip(s0, s1)]
    det, z, cfg = worst
    if cfg is None:
        print("  no signal at all (clean)", flush=True)
        return
    key, k = cfg
    print("  worst: det_bits=%d max|z|=%.1f at key=%#x delta=2^%d" %
          (det, z, key, k), flush=True)
    print("  per-stage det-bit decay, worst delta:", per_stage[k], flush=True)


def main():
    keys = [0x123456789ABCDEF0, 0xF0B52A9E7D8BA2B5, 0x092988F142674743]
    deltas = list(range(18))
    analyze("t6_sand4a (DEAD)", lambda V, K: sand_stages(V, K, T6.SAND4A),
            keys, deltas)
    analyze("t6_skip4a (DEAD)", lambda V, K: skip_stages(V, K, T6.SKIP4A),
            keys, deltas)
    analyze("t6_lane4a (DEAD)", lambda V, K: lane_stages(
        V, K, T6.LANE4A_A, T6.LANE4A_B, T6.LANE4A_S), keys, deltas)
    analyze("al_and6a (CLEAN)", and6a_stages, keys, deltas)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
