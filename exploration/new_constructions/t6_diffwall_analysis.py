#!/usr/bin/env python3
"""DIFF-wall structural analysis (track 6, 2026-10-10).

Question: why do ALL x^=F boolean cascades (4-5 stage, any stage function,
any diffusion, dual-lane/skip/sandwich) die at S1 DIFF with catastrophic
worst|z|, while al_and6a (6-stage x^=(ra&rb)^rc) is S1-clean?

Method: mirror the S1 DIFF screen's construction (sequential input pairs,
weight-1 input deltas 2^k k=0..17, per-key) but vectorized, and report the
per-(delta,key,outbit) differential bias |z|. Also trace bias growth through
the stages of a dead skeleton to localize the injection point.

Candidates:
  dead: t6_lane3b, t6_skip4a, t6_lane4a, t6_sand4a (batch-32, S1-FLAG)
  clean: al_and6a (frontier, S1/S2/S3/S4 clean)
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


# ---- re-implement dead skeletons with per-stage state capture ----
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


def and6a_stages(V, K):
    mod = load_model("al_and6a")
    x = (V ^ K) & M64
    states = []
    for a, b, c in mod.STAGES:
        x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
        states.append(x)
    out = (x ^ rotl(K, 13)) & M64
    return states, out


def bias_profile(stage_fn, keys, logN=17, deltas=range(18)):
    """For each (key, weight-1 delta 2^k): max over output bits of |z| of
    P(out_delta_bit=1) vs 0.5, over 2^logN sequential input pairs."""
    n = 1 << logN
    V = np.arange(n, dtype=np.uint64)
    rows = []
    for ki, key in enumerate(keys):
        K = np.full(n, np.uint64(key), dtype=np.uint64)
        _, out0 = stage_fn(V, K)
        for k in deltas:
            d = np.uint64(1) << np.uint64(k)
            _, out1 = stage_fn(V ^ d, K)
            dout = out0 ^ out1
            # per-bit counts of 1
            bits = np.unpackbits(dout.view(np.uint8)).reshape(n, 64)
            cnt = bits.sum(axis=0)
            p = cnt / n
            se = np.sqrt(0.25 / n)
            z = (p - 0.5) / se
            wz = float(np.abs(z).max())
            argb = int(np.abs(z).argmax())
            rows.append((ki, k, wz, argb, float(p[argb])))
    return rows


def stage_growth(stage_fn, key, k_delta, logN=17):
    """Track max|z| of the *state* differential after each stage."""
    n = 1 << logN
    V = np.arange(n, dtype=np.uint64)
    K = np.full(n, np.uint64(key), dtype=np.uint64)
    d = np.uint64(1) << np.uint64(k_delta)
    s0, _ = stage_fn(V, K)
    s1, _ = stage_fn(V ^ d, K)
    out = []
    for a, b in zip(s0, s1):
        if isinstance(a, tuple):  # dual-lane: use a^ b fold? report per lane
            la, lb = a
            ra, rb = b
            for name, x, y in (("laneA", la, ra), ("laneB", lb, rb)):
                dout = x ^ y
                bits = np.unpackbits(dout.view(np.uint8)).reshape(n, 64)
                p = bits.sum(axis=0) / n
                z = (p - 0.5) / np.sqrt(0.25 / n)
                out.append((name, float(np.abs(z).max())))
        else:
            dout = a ^ b
            bits = np.unpackbits(dout.view(np.uint8)).reshape(n, 64)
            p = bits.sum(axis=0) / n
            z = (p - 0.5) / np.sqrt(0.25 / n)
            out.append(("", float(np.abs(z).max())))
    return out


def main():
    keys = [0x123456789ABCDEF0, 0xF0B52A9E7D8BA2B5, 0x092988F142674743]
    cands = {
        "t6_lane3b(DEAD)": lane3b_stages,
        "t6_skip4a(DEAD)": skip4a_stages,
        "al_and6a(CLEAN)": and6a_stages,
    }
    print("=== output differential bias profile (max|z| over outbits) ===")
    print("key#, delta2^k, worst|z|, at_outbit, P(bit=1)")
    for name, fn in cands.items():
        print(f"--- {name} ---")
        rows = bias_profile(fn, keys)
        worst = sorted(rows, key=lambda r: -r[2])[:6]
        for ki, k, wz, b, p in worst:
            print(f"  key{ki} d=2^{k:<2d} worst|z|={wz:12.1f} outbit={b:<2d} P={p:.4f}")
    print()
    print("=== per-stage bias growth, key0, delta 2^0 ===")
    for name, fn in cands.items():
        print(f"--- {name} ---")
        for lane, wz in stage_growth(fn, keys[0], 0):
            print(f"  stage {lane} max|z|={wz:12.1f}")


if __name__ == "__main__":
    main()
