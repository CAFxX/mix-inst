#!/usr/bin/env python3
"""Fisher triage for fp3: generate 2^18 sequential outputs, run screen_lin_diff.
Measures; does not optimize."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/firstprinciples")
import numpy as np
from lin_diff import screen_lin_diff
from sim import forward

def main():
    N = 1 << 18
    print(f"Generating {N} sequential outputs...", flush=True)
    # X[n,i] = bit i of n
    n_arr = np.arange(N, dtype=np.uint64)
    X = ((n_arr[:, None] >> np.arange(64, dtype=np.uint64)) & 1).astype(np.uint8)
    print("Running forward...", flush=True)
    Y = forward(X)
    powers = (1 << np.arange(64, dtype=np.uint64))
    y64 = (Y.astype(np.uint64) * powers).sum(axis=1)
    print("Running screen_lin_diff...", flush=True)
    seq_dict = {0: y64}
    result = screen_lin_diff(seq_dict, verbose=True)
    print(f"\nLIN verdict: {result['lin_verdict']}")
    print(f"DIFF verdict: {result['diff_verdict']}")
    import json
    with open("fisher_fp3.json", "w") as f:
        json.dump({k: str(v) for k, v in result.items()}, f, indent=2)
    print("wrote fisher_fp3.json")

if __name__ == "__main__":
    main()
