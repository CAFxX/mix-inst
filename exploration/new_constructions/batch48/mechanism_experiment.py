#!/usr/bin/env python3
"""Batch-48 MECHANISM EXPERIMENT (track 6, incarnation XVII).

Question: the reduced 1-rotation linear layer L_a(y) = y ^ rotl(y,a) is
GF(2)-singular (O45 proof: fixes the all-ones vector). In the b45-replacement
frame the stage x := L_a(chi3(x)) is therefore exactly 2-to-1, and the
4-stage cascade is 16-to-1 with all outputs confined to a 63-dim affine
subspace. Which gate (if any) catches this structure?

This script measures, on the EXACT b48 prize form (no pilot draws yet):
  (a) GF(2) rank of L_a for every a in 1..63  (odd-a vs even-a refinement)
  (b) exact-DIFF triage (diff_cell_logps, 10 keys, N=2^18) on 3 odd-a draws
  (c) S1 LIN rank test (lin_cell_logp, D over 4096 blocks) on 1 odd-a draw

Outcome decides the DESIGN: a loud kill here = mechanism confirmed pre-pilot;
survival = the pilot's prize question is live.
"""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps, lin_cell_logp, gf2_rank64
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def _chi_scalar(v, n):
    y = 0
    for k in range(n):
        vk = (v >> k) & 1
        v1 = (v >> ((k + 1) % n)) & 1
        v2 = (v >> ((k + 2) % n)) & 1
        y |= ((vk ^ ((1 ^ v1) & v2)) << k)
    return y


CHI3_LUT = np.array([_chi_scalar(v, 3) for v in range(8)], dtype=np.uint64)
assert len(set(CHI3_LUT.tolist())) == 8


def chi3(x):
    y = x & np.uint64(0x8000000000000000)
    for j in range(21):
        lane = ((x >> np.uint64(3 * j)) & np.uint64(0x7)).astype(np.uint64)
        y |= CHI3_LUT[lane] << np.uint64(3 * j)
    return y & M64


def lin_layer_rank(a):
    """GF(2) rank of y -> y ^ rotl(y,a) as a 64x64 binary matrix."""
    rows = []
    for i in range(64):
        y = np.uint64(1) << np.uint64(i)
        rows.append(int(y ^ rotl(y, a)))
    return gf2_rank64(rows)


def build_outputs(stages, key):
    V = np.arange(N, dtype=np.uint64)
    K = np.uint64(key)
    x = (V ^ K) & M64
    for a in stages:
        y = chi3(x)
        x = (y ^ rotl(y, a)) & M64
    return ((x ^ rotl(K, 13)) & M64).astype(np.uint64)


def main():
    print("=== (a) rank of L_a(y) = y ^ rotl(y,a) ===", flush=True)
    odd_ranks = {}
    even_ranks = {}
    for a in range(1, 64):
        r = lin_layer_rank(a)
        (odd_ranks if a % 2 else even_ranks)[a] = r
    print("odd  a: min rank %d, max rank %d, all==63: %s"
          % (min(odd_ranks.values()), max(odd_ranks.values()),
             all(v == 63 for v in odd_ranks.values())), flush=True)
    print("even a: min rank %d, max rank %d"
          % (min(even_ranks.values()), max(even_ranks.values())), flush=True)
    assert all(v == 63 for v in odd_ranks.values()), "odd-a must be rank 63"
    assert all(v <= 62 for v in even_ranks.values()), "even-a must be rank<=62"

    print("=== (b) exact-DIFF triage on 3 odd-a draws ===", flush=True)
    rng = np.random.default_rng(0xB480)
    for d in range(3):
        stages = []
        while len(stages) < 4:
            a = int(rng.integers(1, 64))
            if a % 2 == 0 or a in stages:
                continue
            stages.append(a)
        worst = 0.0
        worst_key = None
        for key in KEYS10:
            S = build_outputs(stages, key)
            _, wz, _, _ = diff_cell_logps(S, key)
            if wz > worst:
                worst, worst_key = wz, key
        print("draw %d stages=%s triage maxworst|z|=%.1f killkey=%#x %s"
              % (d, stages, worst, worst_key,
                 "KEEP" if worst < 10 else "kill"), flush=True)

    print("=== (c) S1 LIN rank test on 1 odd-a draw ===", flush=True)
    stages = [1, 7, 13, 29]
    key = KEYS10[0]
    S = build_outputs(stages, key)
    # parity confinement check: all outputs must share one parity
    par = (bin(int(S[0])).count("1") % 2)
    assert all(bin(int(v)).count("1") % 2 == par for v in S), \
        "output parity not constant -- mechanism premise broken"
    print("output parity constant (%d) across 2^18 outputs: CONFIRMED"
          % par, flush=True)
    d, lp = lin_cell_logp(S)
    print("S1 LIN: D=%d/4096 logp=%.2f (null E[D]=%.1f)"
          % (d, lp, 4096 * 0.005285), flush=True)
    print("MECHANISM-EXPERIMENT COMPLETE", flush=True)


if __name__ == "__main__":
    main()
