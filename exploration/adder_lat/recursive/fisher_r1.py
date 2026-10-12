#!/usr/bin/env python3
"""Fisher triage for R1 hierarchical: generate 2^18 sequential outputs, run screen_lin_diff."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
from lin_diff import screen_lin_diff
from sim_hier import apply_r1_hier, build_hierarchical_wiring

def main():
    w1, w2, w3 = build_hierarchical_wiring()
    N = 1 << 18
    print(f"Generating {N} sequential outputs...", flush=True)
    outputs = []
    for x in range(N):
        y = apply_r1_hier(x, w1, w2, w3)
        outputs.append(y)
        if (x+1) % 65536 == 0:
            print(f"  {x+1}/{N}", flush=True)
    print("Running screen_lin_diff...", flush=True)
    import numpy as np
    seq_dict = {0: np.array(outputs, dtype=np.uint64)}
    result = screen_lin_diff(seq_dict, verbose=True)
    print(f"\nResult: {result}")

if __name__ == "__main__":
    main()
