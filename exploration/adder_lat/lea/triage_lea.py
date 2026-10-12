#!/usr/bin/env python3
"""LEA-F Fisher triage: 3-round Feistel with AND+compressor F.

Uses lin_diff.screen_lin_diff verbatim (S1 gate's own rule).
KEEP iff LIN PASS and DIFF PASS (0 Holm rejections).
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/lea")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")

import numpy as np
from lea_feistel import lea_feistel_vec
from lin_diff import screen_lin_diff

# Fixed round params (a,b,c,d,e,f,g,h,i per round; i = linear diffusion tap)
PARAMS_BASE = [(3, 7, 11, 15, 5, 9, 13, 17, 21),
               (5, 9, 13, 17, 7, 11, 15, 19, 23),
               (7, 11, 15, 19, 9, 13, 17, 21, 25)]

# 10 test keys (deterministic)
KEYS = [0x123456789ABCDEF0, 0x0FEDCBA987654321, 0xAAAAAAAAAAAAAAAA,
        0x5555555555555555, 0x0000000000000000, 0xFFFFFFFFFFFFFFFF,
        0xDEADBEEFCAFEBABE, 0x0123456789ABCDEF, 0xFEDCBA9876543210,
        0x1111111111111111]

N = 1 << 18  # 262144 sequential outputs per key


def main():
    seq_outputs = {}
    print(f"Generating {N} outputs per key for {len(KEYS)} keys...", flush=True)
    V = np.arange(N, dtype=np.uint64)
    for ki, k in enumerate(KEYS):
        k0 = k & 0xFFFFFFFF
        k1 = (k >> 32) & 0xFFFFFFFF
        k2 = k0 ^ k1
        params = [(k0, *PARAMS_BASE[0]), (k1, *PARAMS_BASE[1]), (k2, *PARAMS_BASE[2])]
        out = lea_feistel_vec(V, np.uint64(k), params)
        seq_outputs[k] = out
        print(f"  key {ki}: done", flush=True)
    print("Running Fisher triage...", flush=True)
    res = screen_lin_diff(seq_outputs, verbose=True)
    print(f"\nLIN verdict: {res['lin_verdict']}")
    print(f"DIFF verdict: {res['diff_verdict']}")
    if res['lin_verdict'] == 'PASS' and res['diff_verdict'] == 'PASS':
        print("TRIAGE: KEEP")
    else:
        print("TRIAGE: REJECT")


if __name__ == "__main__":
    main()
