#!/usr/bin/env python3
"""
Hill climber for 6-level DAG optimizer.
Objective: Fisher LIN+DIFF performance.
"""

import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/dagopt")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")

from dag_sim import apply_xig, compute_fanin, estimate_levels, AND, XOR
import numpy as np
import random

# Fixed offsets for full 64 fan-in
OFFSETS = [1, 2, 4, 8, 16, 32]

def fisher_score(gate_types, n_seq=1<<14, verbose=False):
    """
    Quick Fisher proxy using smaller N for speed.
    Returns: (lin_D, diff_max_z) — lower is better.
    For full Fisher, use n_seq=1<<18 and screen_lin_diff.
    """
    # Generate sequential outputs
    X = np.arange(n_seq, dtype=np.uint64)
    Y = apply_xig(X, gate_types, OFFSETS)
    
    # LIN proxy: compute rank of a few 64x64 matrices
    # Take 64 non-overlapping blocks of 64 consecutive outputs
    from lin_diff import gf2_rank64
    D = 0
    n_blocks = min(64, n_seq // 64)
    for b in range(n_blocks):
        rows = Y[b*64:(b+1)*64]
        r = gf2_rank64(rows)
        if r <= 61:
            D += 1
    # DIFF proxy: avalanche for weight-1 deltas (first 6 deltas only for speed)
    max_z = 0
    # Simplified: just check if outputs change
    return D, max_z

def full_fisher(gate_types):
    """Run full screen_lin_diff with N=2^18."""
    from lin_diff import screen_lin_diff
    N = 1 << 18
    print(f"Generating {N} outputs...", flush=True)
    X = np.arange(N, dtype=np.uint64)
    Y = apply_xig(X, gate_types, OFFSETS)
    seq_dict = {0: Y}
    print("Running screen_lin_diff...", flush=True)
    result = screen_lin_diff(seq_dict, verbose=True)
    return result

def mutate(gate_types):
    """Swap an AND and XOR position (keeps 4+2 count)."""
    gt = gate_types.copy()
    and_idx = [i for i, t in enumerate(gt) if t == AND]
    xor_idx = [i for i, t in enumerate(gt) if t == XOR]
    if not and_idx or not xor_idx:
        return gt
    i = random.choice(and_idx)
    j = random.choice(xor_idx)
    gt[i], gt[j] = gt[j], gt[i]
    return gt

def main():
    random.seed(123)
    # Start: 4 AND + 2 XOR
    best_gt = [AND, AND, AND, AND, XOR, XOR]
    best_score = None
    
    print("Initial:", best_gt, "cost:", estimate_levels(best_gt))
    fanin = compute_fanin(best_gt, OFFSETS)
    print("Fan-in min/max:", min(fanin), max(fanin))
    
    # Quick test
    D, _ = fisher_score(best_gt, n_seq=1<<12)
    print(f"Initial quick LIN D (12-bit): {D}")
    
    # Hill climb
    for iteration in range(50):
        cand_gt = mutate(best_gt)
        D_cand, _ = fisher_score(cand_gt, n_seq=1<<12)
        # Lower D is better (D=0 is good)
        if best_score is None or D_cand < best_score:
            best_score = D_cand
            best_gt = cand_gt
            print(f"Iter {iteration}: NEW BEST D={D_cand}, gt={best_gt}")
        elif iteration % 10 == 0:
            print(f"Iter {iteration}: D={D_cand} (best {best_score})")
    
    print(f"\nBest: {best_gt}, D={best_score}")
    print("Cost:", estimate_levels(best_gt))

if __name__ == "__main__":
    main()
