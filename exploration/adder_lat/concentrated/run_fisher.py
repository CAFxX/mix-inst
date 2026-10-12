#!/usr/bin/env python3
"""Run Fisher LIN+DIFF on concentrated XIG."""
import numpy as np, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
from lin_diff import screen_lin_diff
from model import eval_f

N = 1 << 18
print("Generating 2^18 sequential inputs x 2 keys...", flush=True)

def gen_inputs(key_high):
    x = np.zeros((N, 64), dtype=np.uint8)
    for i in range(N):
        # Vary low 18 bits
        for b in range(18):
            x[i, b] = (i >> b) & 1
    if key_high:
        x[:, 18:] = 1
    return x

x0 = gen_inputs(False)
x1 = gen_inputs(True)

print("Evaluating f...", flush=True)
y0 = eval_f(x0)
y1 = eval_f(x1)

def pack(y):
    n = y.shape[0]
    out = np.zeros(n, dtype=np.uint64)
    for i in range(64):
        out |= y[:, i].astype(np.uint64) << np.uint64(i)
    return out

seq = {0x0: pack(y0), 0x1: pack(y1)}
print("Running screen_lin_diff...", flush=True)
res = screen_lin_diff(seq, verbose=True)

import json
with open("fisher_conc.json", "w") as f:
    # Convert numpy types for JSON
    def conv(o):
        if isinstance(o, (np.integer, np.floating)):
            return float(o)
        return o
    json.dump({k: {kk: conv(vv) for kk, vv in v.items()} if isinstance(v, dict) else conv(v)
               for k, v in res.items()}, f, indent=2)
print("Saved fisher_conc.json")
print("LIN:", res["lin_verdict"], "DIFF:", res["diff_verdict"])
