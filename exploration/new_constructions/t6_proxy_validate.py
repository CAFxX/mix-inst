#!/usr/bin/env python3
"""Validate the det-decay/max|z| proxy as a rotation screener (track 6).
as6_200_106: 6-stage AND-schedule, S1 DIFF-KILLED (classic wall signature).
al_and6a: 6-stage AND-schedule, S1 CLEAN.
If the proxy distinguishes them, it can cheaply screen rotation schedules.
"""
import importlib.util
import os
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions")
from t6_diffwall_verify2 import load_model, rotl, bitstats, foldstats, M64


def stages_from_model(mod, V, K):
    x = (V ^ K) & M64
    states = []
    for st in mod.STAGES:
        a, b, c = (st[1], st[2], st[3]) if isinstance(st[0], str) else st
        x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
        states.append(x)
    return states, (x ^ rotl(K, 13)) & M64


def analyze(name, mod):
    keys = [0x123456789ABCDEF0, 0xF0B52A9E7D8BA2B5, 0x092988F142674743]
    deltas = list(range(18))
    rng = np.random.default_rng(4242)
    n = 1 << 18
    print("=== %s === STAGES=%s" % (name, mod.STAGES), flush=True)
    worst = (0, 0.0, None)
    per_stage = {}
    for key in keys:
        K = np.full(n, np.uint64(key), dtype=np.uint64)
        for k in deltas:
            d = np.uint64(1) << np.uint64(k)
            V = rng.integers(0, 2**64, size=n, dtype=np.uint64)
            s0, o0 = stages_from_model(mod, V, K)
            s1, o1 = stages_from_model(mod, V ^ d, K)
            det, z = bitstats(o0, o1)
            if (det, z) > (worst[0], worst[1]):
                worst = (det, z, (key, k))
            if k not in per_stage:
                per_stage[k] = [foldstats(a, b) for a, b in zip(s0, s1)]
    det, z, cfg = worst
    key, k = cfg
    print("  worst: det_bits=%d max|z|=%.1f at key=%#x delta=2^%d" % (det, z, key, k),
          flush=True)
    print("  per-stage det-bit decay:", per_stage[k], flush=True)


analyze("as6_200_106 (DEAD 6-stage)", load_model("as6_200_106"))
analyze("al_and6a (CLEAN 6-stage)", load_model("al_and6a"))
print("DONE", flush=True)
