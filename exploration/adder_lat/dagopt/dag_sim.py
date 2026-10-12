#!/usr/bin/env python3
"""
DAG Optimizer: 6-level parametrized Boolean DAG for 64-bit mix.

Parametrization:
- 6 levels, each with 64 parallel 2-input gates.
- Level j: gate type T_j in {AND, XOR}, offset a_j.
- Gate i at level j takes inputs (i, i+a_j) mod 64 from level j-1.
- Level 0 = primary inputs (64 bits).
- XIG form: f_i = x_i XOR g_i, where g_i is L6 output i (for bijectivity).

This gives 12 parameters: 6 gate types + 6 offsets.
"""

import random
import numpy as np

# Gate types
AND = 0
XOR = 1

def apply_dag_vectorized(X, gate_types, offsets):
    """
    X: numpy array of uint64, shape (N,) — N input values.
    gate_types: list of 6 ints (AND/XOR).
    offsets: list of 6 ints.
    Returns: numpy array of uint64, shape (N,) — 64-bit outputs (g_i, before XIG).
    
    Vectorized: process all N inputs in parallel using numpy.
    Each "bit" is a numpy array of shape (N,) with values 0/1.
    """
    N = X.shape[0]
    # Extract 64 bit-planes: bits[b, n] = bit b of X[n]
    # Shape: (64, N)
    bits = np.zeros((64, N), dtype=np.uint8)
    for b in range(64):
        bits[b] = ((X >> np.uint64(b)) & np.uint64(1)).astype(np.uint8)
    
    prev = bits  # (64, N)
    for j in range(6):
        t = gate_types[j]
        a = offsets[j]
        curr = np.zeros((64, N), dtype=np.uint8)
        for i in range(64):
            x = prev[i]
            y = prev[(i + a) % 64]
            if t == AND:
                curr[i] = x & y
            else:  # XOR
                curr[i] = x ^ y
        prev = curr
    
    # Pack 64 bit-planes back to uint64
    Y = np.zeros(N, dtype=np.uint64)
    for b in range(64):
        Y |= (prev[b].astype(np.uint64) << np.uint64(b))
    return Y

def apply_xig(X, gate_types, offsets):
    """f_i = x_i XOR g_i. X, returns Y as uint64 array."""
    G = apply_dag_vectorized(X, gate_types, offsets)
    return X ^ G

def compute_fanin(gate_types, offsets):
    """
    Compute transitive fan-in size for each output.
    Returns: list of 64 ints (should be 64 for full coverage).
    """
    # Track which primary inputs each node depends on (as bitmask over 64, use Python set for simplicity)
    # Level 0: node i depends on {i}
    prev_sets = [{i} for i in range(64)]
    for j in range(6):
        a = offsets[j]
        curr_sets = []
        for i in range(64):
            s = prev_sets[i] | prev_sets[(i + a) % 64]
            curr_sets.append(s)
        prev_sets = curr_sets
    return [len(s) for s in prev_sets]

def estimate_levels(gate_types):
    """Estimate unit-delay: AND=1.0, XOR=1.8. Plus 1.8 for XIG final XOR."""
    cost = sum(1.0 if t == AND else 1.8 for t in gate_types)
    cost += 1.8  # XIG
    return cost

def quick_avalanche(X_sample, gate_types, offsets, n_trials=100):
    """
    Quick diffusion proxy: for random inputs, flip each of 64 bits,
    count output bits changed. Returns mean avalanche (should be ~32).
    X_sample: not used, we generate random.
    """
    N = n_trials
    X = np.random.randint(0, 2**64, size=N, dtype=np.uint64)
    Y0 = apply_xig(X, gate_types, offsets)
    total_changed = 0
    for b in range(64):
        Xf = X ^ (np.uint64(1) << np.uint64(b))
        Yf = apply_xig(Xf, gate_types, offsets)
        diff = Y0 ^ Yf
        # Count bits set in diff for each of N
        # Use bit_count via unpacking (numpy doesn't have vectorized bit_count for uint64 in older versions)
        for n in range(N):
            total_changed += bin(int(diff[n])).count('1')
    mean_avalanche = total_changed / (N * 64)
    return mean_avalanche

if __name__ == "__main__":
    # Test with R1-like parameters
    # R1: 3 stages of (a^b)^(c&d), but our DAG is 6 levels of 2-input gates.
    # Let's start with: L1-L3 AND, L4-L6 XOR, hierarchical offsets.
    gate_types = [AND, AND, AND, XOR, XOR, XOR]
    offsets = [1, 16, 4, 1, 16, 4]  # placeholder
    
    print("Fan-in:", compute_fanin(gate_types, offsets)[:5], "...")
    print("Levels cost:", estimate_levels(gate_types), "u")
    
    # Quick test
    X = np.array([0, 1, 2, 3], dtype=np.uint64)
    Y = apply_xig(X, gate_types, offsets)
    print("Test outputs:", [hex(int(y)) for y in Y])
