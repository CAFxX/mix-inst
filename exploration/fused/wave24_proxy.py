#!/usr/bin/env python3
"""Wave-24 v2-proxy screen (sequential-x, diffprof-faithful).

Extends track-3's s2proxy_v2 with wave-24 stage types (maj/ch/chi/nch).
Methodology: sequential x in [0,2^logN), dedupe x<=x^d, all 64 single-bit
+ structured + nibble deltas (115 total), per-bit z-scores, max|z|.
v2 validation: and5xa 386.1 -> S2 KILL; fz15_c 10.5 -> S2 PASS.
"""
import sys
import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/rootcause")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from s2proxy_v2 import maxz_for_delta, all_deltas, M64, rotl
from gen_fused24 import SPECS

_PLANE = np.uint64(0x1111111111111111)

def _maj(p, q, r):
    return ((p & q) ^ (p & r) ^ (q & r)) & M64

def _ch(p, q, r):
    return ((p & q) ^ ((~p) & r)) & M64

def _nibchi(x):
    p0 = x & _PLANE
    p1 = (x >> np.uint64(1)) & _PLANE
    p2 = (x >> np.uint64(2)) & _PLANE
    p3 = (x >> np.uint64(3)) & _PLANE
    q0 = p0 ^ ((~p1) & p2)
    q1 = p1 ^ ((~p2) & p3)
    q2 = p2 ^ ((~p3) & p0)
    q3 = p3 ^ ((~p0) & p1)
    return (q0 | (q1 << np.uint64(1)) | (q2 << np.uint64(2))
            | (q3 << np.uint64(3))) & M64

def apply_stage(x, st):
    k = st[0]
    if k == 'and':
        _, (a, b, c) = st[0], st[1]
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    if k == 't3':
        _, (a, b, c, d) = st[0], st[1]
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c) ^ rotl(x, d)) & M64
    if k == 'maj':
        _, (a, b, c, d) = st[0], st[1]
        return (x ^ _maj(rotl(x, a), rotl(x, b), rotl(x, c)) ^ rotl(x, d)) & M64
    if k == 'ch':
        _, (a, b, c, d) = st[0], st[1]
        return (x ^ _ch(rotl(x, a), rotl(x, b), rotl(x, c)) ^ rotl(x, d)) & M64
    if k == 'chi':
        _, (a, b, c, d) = st[0], st[1]
        return (x ^ ((~rotl(x, a)) & rotl(x, b)) ^ rotl(x, c) ^ rotl(x, d)) & M64
    if k == 'nch':
        _, (c,) = st[0], st[1]
        return (x ^ _nibchi(x) ^ rotl(x, c)) & M64
    if k == 'nch2':
        _, (c1, c2) = st[0], st[1]
        return (x ^ _nibchi(x) ^ rotl(x, c1) ^ rotl(x, c2)) & M64
    if k == 'nch2L':
        _, (c1, c2, c3) = st[0], st[1]
        return (x ^ _nibchi(x) ^ rotl(x, c1) ^ rotl(x, c2) ^ rotl(x, c3)) & M64
    raise ValueError(st)

def proxy_24(stages, logN=16, verbose=False):
    def mix_fn(xs, K):
        x = (xs ^ K) & M64
        for st in stages:
            x = apply_stage(x, st)
        return x
    worst_z, worst_d, worst_b = 0, None, None
    for d0 in all_deltas():
        z, b, n = maxz_for_delta(mix_fn, d0, logN)
        if verbose and z > 9:
            print(f"    d0={d0:#018x}: max|z|={z:.1f} @bit{b}")
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b

def cost_est(stages):
    c = 0.0
    for kind, _ in stages:
        c += {'and': 3.35, 't3': 4.5, 'maj': 4.5, 'ch': 4.2,
              'chi': 3.8, 'nch': 3.8, 'nch2': 4.8, 'nch2L': 5.8}[kind]
    return c

if __name__ == '__main__':
    logN = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    only = sys.argv[2:] if len(sys.argv) > 2 else None
    for name, stages, desc in SPECS:
        if only and name not in only:
            continue
        z, d, b = proxy_24(stages, logN=logN)
        print(f"PROXY name={name} logN={logN} max|z|={z:7.1f} "
              f"(d0={d:#x} bit{b}) est={cost_est(stages):.2f}u", flush=True)
