#!/usr/bin/env python3
"""Hill climb with AND/OR/XOR, fast proxy."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/dagopt")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")

from dag_sim_or import apply_xig_or, cost_or, AND, XOR, OR
from dag_sim import compute_fanin
import numpy as np
import random

OFFSETS = [1, 2, 4, 8, 16, 32]

def quick_lin_D(gate_types, n_blocks=16):
    """Quick LIN: D = #blocks with rank<=61. Lower is better."""
    from lin_diff import gf2_rank64
    N = n_blocks * 64
    X = np.arange(N, dtype=np.uint64)
    Y = apply_xig_or(X, gate_types, OFFSETS)
    D = 0
    for b in range(n_blocks):
        rows = Y[b*64:(b+1)*64]
        if gf2_rank64(rows) <= 61:
            D += 1
    return D

def mutate(gt):
    """Randomly change one gate type (keep cost <10u)."""
    gt = gt.copy()
    i = random.randrange(6)
    # Choose a different type
    choices = [AND, OR, XOR]
    choices.remove(gt[i])
    gt[i] = random.choice(choices)
    # Check cost
    if cost_or(gt) >= 10.0:
        return None  # reject
    return gt

def main():
    random.seed(456)
    # Start: 2 AND, 2 OR, 2 XOR = 2+2+3.6+1.8 = 9.4u
    best_gt = [AND, AND, OR, OR, XOR, XOR]
    print(f"Start: {best_gt}, cost={cost_or(best_gt):.1f}")
    best_D = quick_lin_D(best_gt)
    print(f"Initial D={best_D}/16")
    
    for it in range(100):
        cand = mutate(best_gt)
        if cand is None:
            continue
        D = quick_lin_D(cand)
        if D < best_D:
            best_D = D
            best_gt = cand
            print(f"Iter {it}: NEW BEST D={D}, gt={best_gt}, cost={cost_or(best_gt):.1f}")
        elif it % 20 == 0:
            print(f"Iter {it}: D={D} (best {best_D})")
    
    print(f"\nBest: {best_gt}, D={best_D}/16, cost={cost_or(best_gt):.1f}")

if __name__ == "__main__":
    main()
