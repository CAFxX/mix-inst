#!/usr/bin/env python3
"""DIFF-wall mechanism verification (track 6, 2026-10-10).

Hypothesis: for stage x ^= (rot(x,a)&rot(x,b)) ^ rot(x,c), a weight-1 input
delta produces an output differential with a DETERMINISTIC skeleton:
  D[x1]_i = d_i ^ d_{i-c}   for all i not in {k+a, k+b}   (exact, any x)
because the AND differential D[a&b]_i = (da_i&b_i)^(db_i&a_i)^(da_i&db_i)
is value-independent (=0) wherever the input differential has no delta.
Each stage can only randomize bits the AND "probes"; the skeleton shrinks
as the differential spreads. The S1 DIFF wall = deterministic skeleton bits
SURVIVING to the output (a single deterministic outbit makes the low-8-bit
chi2 catastrophic).

Predictions:
  P1: dead designs have >=1 deterministic output-differential bit for some
      weight-1 input delta (random inputs, not just sequential).
  P2: al_and6a (clean) has ZERO deterministic output bits for all 18 deltas.
  P3: per-stage, al_and6a's deterministic-bit count -> 0 before the last
      stage; dead designs' does not.

This script counts deterministic bits (P(out_delta_bit=1) exactly 0 or 1
over N random pairs) per stage and at the output, for dead vs clean.
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
        f"m_{name}", os.path.join(FB, name, "model.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def lane3b_stages(V, K):
    sa, sb, ss = T6.LANE3B_A, T6.LANE3B_B, T6.LANE3B_S
    a = (V ^ K) & M64
    b = rotl(K, 29)
    states = []
    for ((pa, qa), da), ((pb, qb), db), s in zip(sa, sb, ss):
        an = (a ^ (rotl(a, pa) & rotl(a, qa)) ^ rotl(a, da)) & M64
        bn = (b ^ (rotl(b, pb) & rotl(b, qb)) ^ rotl(b, db) ^ rotl(a, s)) & M64
        a, b = an, bn
        states.append((a, b))
    out = (a ^ b ^ rotl(K, 13)) & M64
    return states, out


def sand4a_stages(V, K):
    sched = T6.SAND4A
    x = (V ^ K) & M64
    states = []
    for a, (b, c), d in sched:
        x = (x ^ rotl(x, a) ^ (rotl(x, b) & rotl(x, c)) ^ rotl(x, d)) & M64
        states.append(x)
    out = (x ^ rotl(K, 13)) & M64
    return states, out


def skip4a_stages(V, K):
    sched = T6.SKIP4A
    x = (V ^ K) & M64
    xm1 = np.zeros_like(x)
    states = []
    for (a, b), d, s in sched:
        xn = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, d) ^ rotl(xm1, s)) & M64
        xm1, x = x, xn
        states.append(x)
    out = (x ^ rotl(K, 13)) & M64
    return states, out


def lane4a_stages(V, K):
    sa, sb, ss = T6.LANE4A_A, T6.LANE4A_B, T6.LANE4A_S
    a = (V ^ K) & M64
    b = rotl(K, 29)
    states = []
    for ((pa, qa), da), ((pb, qb), db), s in zip(sa, sb, ss):
        an = (a ^ (rotl(a, pa) & rotl(a, qa)) ^ rotl(a, da)) & M64
        bn = (b ^ (rotl(b, pb) & rotl(b, qb)) ^ rotl(b, db) ^ rotl(a, s)) & M64
        a, b = an, bn
        states.append((a, b))
    out = (a ^ b ^ rotl(K, 13)) & M64
    return states, out


def and6a_stages(V, K):
    mod = load_model("al_and6a")
    x = (V ^ K) & M64
    states = []
    for a, b, c in mod.STAGES:
        x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
        states.append(x)
    out = (x ^ rotl(K, 13)) & M64
    return states, out


def det_bits(x0, x1):
    """Count output-differential bits that are CONSTANT (0 or 1) over pairs."""
    dout = x0 ^ x1
    n = dout.shape[0]
    bits = np.unpackbits(dout.view(np.uint8)).reshape(n, 64)
    cnt = bits.sum(axis=0)
    det = int(((cnt == 0) | (cnt == n)).sum())
    return det


def analyze(name, stage_fn, keys, deltas, logN=20, seed=12345):
    rng = np.random.default_rng(seed)
    n = 1 << logN
    print(f"=== {name} ===")
    worst_out = 0
    worst_cfg = None
    stage_rows = {}
    for key in keys:
        K = np.full(n, np.uint64(key), dtype=np.uint64)
        for k in deltas:
            d = np.uint64(1) << np.uint64(k)
            V = rng.integers(0, 2**64, size=n, dtype=np.uint64)
            s0, o0 = stage_fn(V, K)
            s1, o1 = stage_fn(V ^ d, K)
            do = det_bits(o0, o1)
            if do > worst_out:
                worst_out = do
                worst_cfg = (key, k)
            # per-stage deterministic-bit counts (fold dual lanes)
            per = []
            for a, b in zip(s0, s1):
                if isinstance(a, tuple):
                    da = det_bits(a[0], b[0]) + det_bits(a[1], b[1])
                    per.append(("fold", da))
                else:
                    per.append(("", det_bits(a, b)))
            stage_rows.setdefault(k, []).append(per)
    if worst_cfg is not None:
        print(f"  max deterministic OUTPUT bits over {len(keys)} keys x {len(deltas)} deltas: "
              f"{worst_out}  (key={worst_cfg[0]:#x} delta=2^{worst_cfg[1]})")
        # show per-stage decay for the worst delta on key0
        k = worst_cfg[1]
        print(f"  per-stage deterministic bits, key0, delta 2^{k}:")
        for per in stage_rows[k][0]:
            print(f"    {per[0] or 'stage'}: {per[1]}")
    else:
        print(f"  max deterministic OUTPUT bits over {len(keys)} keys x {len(deltas)} deltas: 0 "
              f"(NO deterministic output bit on any key/delta)")
        print("  per-stage deterministic bits: skipped (no deterministic skeleton present)")
    return worst_out


def main():
    keys = [0x123456789ABCDEF0, 0xF0B52A9E7D8BA2B5, 0x092988F142674743]
    deltas = list(range(18))
    results = {}
    results["t6_lane3b"] = analyze("t6_lane3b (DEAD)", lane3b_stages, keys, deltas)
    results["t6_sand4a"] = analyze("t6_sand4a (DEAD)", sand4a_stages, keys, deltas)
    results["t6_skip4a"] = analyze("t6_skip4a (DEAD)", skip4a_stages, keys, deltas)
    results["t6_lane4a"] = analyze("t6_lane4a (DEAD)", lane4a_stages, keys, deltas)
    results["al_and6a"] = analyze("al_and6a (CLEAN)", and6a_stages, keys, deltas)
    print()
    print("=== verdict ===")
    for name, w in results.items():
        tag = "DEAD" if w > 0 else "CLEAN"
        print(f"  {name}: max deterministic output bits = {w} -> {tag} "
              f"(predicted {'DEAD' if 'DEAD' in name or name=='t6_lane3b' or 't6' in name else 'CLEAN'})")


if __name__ == "__main__":
    main()
