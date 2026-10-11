#!/usr/bin/env python3
"""Replicate the EXACT S1 DIFF computation (lin_diff.diff_cell_logps) on
sequential inputs for as6_200_106 (S1 DIFF-KILLED) vs al_and6a (S1 CLEAN),
then ablate: sequential -> random inputs. Finds the distinguishing ingredient.
"""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/new_constructions")
from lin_diff import diff_cell_logps, N_DIFF_PAIRS
from t6_diffwall_verify2 import load_model

KEYS = [0x0, 0xFFFFFFFFFFFFFFFF, 0xAAAAAAAAAAAAAAAA, 0x5555555555555555,
        0xDEADBEEFDEADBEEF, 0x9E3779B97F4A7C15, 0x1234,
        0x123456789ABCDEF, 0xF0B52A9E7D8BA2B5, 0x092988F142674743]


def seq_outputs(mod, key, n=N_DIFF_PAIRS * 2, sequential=True, seed=5):
    if sequential:
        V = np.arange(n, dtype=np.uint64)
    else:
        V = np.random.default_rng(seed).integers(0, 2**64, size=n, dtype=np.uint64)
    K = np.full(n, np.uint64(key), dtype=np.uint64)
    return mod.mix_np(V, K)


def run(name, mod, sequential):
    print("=== %s sequential=%s ===" % (name, sequential), flush=True)
    for key in KEYS:
        S = seq_outputs(mod, key, sequential=sequential)
        logps, wz, flp, blp = diff_cell_logps(S, key)
        nrej = sum(1 for lp in logps if lp < -20)  # rough reject count
        print("  key=%#x worst|z|=%.1f fisher_logp=%.1f bonf_logp=%.1f" %
              (key, wz, flp, blp), flush=True)


as6 = load_model("as6_200_106")
and6a = load_model("al_and6a")
run("as6_200_106 (S1 DIFF-KILLED)", as6, True)
run("al_and6a (S1 CLEAN)", and6a, True)
run("as6_200_106 random-inputs", as6, False)
run("al_and6a random-inputs", and6a, False)
print("DONE", flush=True)
