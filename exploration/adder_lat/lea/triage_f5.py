#!/usr/bin/env python3
"""LEA-F5: 5-round Feistel, minimal F (track-3 LEA arm).

Co-design: 3-round Feistel fails Fisher regardless of AND density.
5 rounds at 3 levels/round = 15 levels ≈ 16u (still <18.6u).
F(R,k) = (rotl(R,a) & rotl(R,b)) ^ k  (1 AND + 1 XOR = 2 levels).
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/lea")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")

import numpy as np
from lin_diff import screen_lin_diff

M32 = np.uint64(0xFFFFFFFF)

def rotl32(x, r):
    r %= 32
    return (((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32) if r else x & M32

def F5(R, k, a, b):
    return ((rotl32(R, a) & rotl32(R, b)) ^ np.uint64(k)) & M32

def feistel5_vec(V, k, params):
    V = np.asarray(V, dtype=np.uint64)
    L = ((V >> np.uint64(32)) & M32)
    R = (V & M32)
    for (ki, a, b) in params:
        Fout = F5(R, ki, a, b)
        L, R = R, (L ^ Fout) & M32
    return ((R << np.uint64(32)) | L) & np.uint64(0xFFFFFFFFFFFFFFFF)

KEYS = [0x123456789ABCDEF0, 0x0FEDCBA987654321, 0xAAAAAAAAAAAAAAAA,
        0x5555555555555555, 0x0000000000000000, 0xFFFFFFFFFFFFFFFF,
        0xDEADBEEFCAFEBABE, 0x0123456789ABCDEF, 0xFEDCBA9876543210,
        0x1111111111111111]
N = 1 << 18
# 5 rounds, distinct (a,b) per round
AB = [(3, 11), (7, 15), (5, 13), (9, 17), (11, 19)]

def main():
    seq_outputs = {}
    V = np.arange(N, dtype=np.uint64)
    for k in KEYS:
        params = []
        for i, (a, b) in enumerate(AB):
            ki = ((k >> (8*i)) | (k << (64-8*i))) & 0xFFFFFFFFFFFFFFFF
            params.append((ki & 0xFFFFFFFF, a, b))
        out = feistel5_vec(V, np.uint64(k), params)
        seq_outputs[k] = out
    res = screen_lin_diff(seq_outputs, verbose=False)
    print(f"LIN: {res['lin_verdict']}  DIFF: {res['diff_verdict']}")
    print("KEEP" if res['lin_verdict']=='PASS' and res['diff_verdict']=='PASS' else "REJECT")

if __name__ == "__main__":
    main()
