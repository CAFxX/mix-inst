#!/usr/bin/env python3
"""Harness check: run the b45 2-rotor form through the IDENTICAL code path
(build_outputs + diff_cell_logps) as mechanism_experiment.py. If the 2-rot
form gives sane z while the 1-rot form gives 1e5+, the kill is real and the
harness is trusted. Single variable changed: the linear layer."""
import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps
from screen_lib import KEYS, N
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions/batch48")
from mechanism_experiment import chi3, rotl, M64, KEYS10

def build_outputs_2rot(stages, key):
    V = np.arange(N, dtype=np.uint64)
    K = np.uint64(key)
    x = (V ^ K) & M64
    for a, b in stages:
        y = chi3(x)
        x = (y ^ rotl(y, a) ^ rotl(y, b)) & M64
    return ((x ^ rotl(K, 13)) & M64).astype(np.uint64)

# draw-1 stages as 2-rot pairs (same first rotations, second rotation = first+7 mod 64, nonzero, !=first)
stages_1rot = [23, 19, 21, 43]
stages_2rot = [(a, (a + 7) % 64 or 1) for a in stages_1rot]
worst = 0.0; wk = None
for key in KEYS10:
    S = build_outputs_2rot(stages_2rot, key)
    _, wz, _, _ = diff_cell_logps(S, key)
    if wz > worst: worst, wk = wz, key
print("2-rot form, stages=%s: triage maxworst|z|=%.1f killkey=%#x %s"
      % (stages_2rot, worst, wk, "KEEP" if worst < 10 else "kill"), flush=True)
print("HARNESS-CHECK COMPLETE", flush=True)
