#!/usr/bin/env python3
"""Step 7: Greedy rank repair for Design B.
Start from Hungarian-optimal assignment, then perform minimal swaps to
achieve rank 64 while preserving row weight 4 and cross-nibble structure.
This is a feasibility repair, not a re-optimization."""
import numpy as np
import json
from scipy.optimize import linear_sum_assignment

W = json.load(open("ddt_lat_weights.json"))
Wcomb = np.array(W["W_combined"])
flow_score = Wcomb.sum(axis=0); flow_score /= flow_score.max()
HOT = {1: 1.0}
def group_nibbles(g): return [((g % 16) + d) % 16 for d in (0, 5, 9, 13)]
def bit_of(i): return i % 4
def nibble_of(i): return i // 4

pairs = [(g, n) for g in range(64) for n in group_nibbles(g)]
bits = [(i, c) for i in range(64) for c in range(4)]
N = 256
C = np.full((N, N), 1e9)
for r, (g, n) in enumerate(pairs):
    for c, (i, cc) in enumerate(bits):
        if nibble_of(i) != n: continue
        b = bit_of(i)
        s = 2.0 * flow_score[b] - 1.5 * HOT.get(b, 0.0) + 0.01 * ((g + b) % 4)
        if g == i: s += 8.0
        elif g // 4 == nibble_of(i): s += 2.0
        C[r, c] = -s
row, col = linear_sum_assignment(C)

# Build assignment: assign[(g,n)] = bit i
assign = {}
for r, c in zip(row, col):
    g, n = pairs[r]; i, cc = bits[c]
    assign[(g, n)] = i

def build_matrix(assign):
    M = np.zeros((64, 64), dtype=np.uint8)
    for (g, n), i in assign.items():
        M[g, i] = 1
    return M

def gf2_rank(A):
    A = A.copy(); r = 0; nr, nc = A.shape
    for c in range(nc):
        piv = None
        for rr in range(r, nr):
            if A[rr, c]: piv = rr; break
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]
        for rr in range(nr):
            if rr != r and A[rr, c]: A[rr] ^= A[r]
        r += 1
    return r

M = build_matrix(assign)
rk = gf2_rank(M)
print(f"initial rank: {rk}")

# Greedy repair: while rank < 64, find a swap that increases rank.
# A swap: pick two pairs (g1,n1)->i1 and (g2,n2)->i2, swap to (g1,n1)->i2, (g2,n2)->i1.
# Valid only if nibble(i2)==n1 and nibble(i1)==n2 (nibble constraints).
# To keep it tractable, only consider swaps within the same nibble-pair structure.
import random
random.seed(0)

# Precompute score for each (pair -> bit) for delta evaluation
def pair_bit_score(g, n, i):
    b = bit_of(i)
    s = 2.0 * flow_score[b] - 1.5 * HOT.get(b, 0.0) + 0.01 * ((g + b) % 4)
    if g == i: s += 8.0
    elif g // 4 == nibble_of(i): s += 2.0
    return s

# Group pairs by nibble for efficient swapping
# pairs_by_nibble[n] = list of (g, n) pairs
pairs_by_nibble = {n: [] for n in range(16)}
for (g, n) in assign.keys():
    pairs_by_nibble[n].append(g)

iterations = 0
while rk < 64 and iterations < 100:
    iterations += 1
    improved = False
    # Try swaps within each nibble (swap bits between two groups that both need nibble n)
    for n in range(16):
        groups = pairs_by_nibble[n]
        # Try all pairs of groups
        for a in range(len(groups)):
            for b in range(a+1, len(groups)):
                g1, g2 = groups[a], groups[b]
                i1, i2 = assign[(g1, n)], assign[(g2, n)]
                if i1 == i2: continue
                # Swap: (g1,n)->i2, (g2,n)->i1
                # Check nibble constraints: nibble(i2)==n? Yes (both from nibble n). ✓
                # Compute score delta
                old_s = pair_bit_score(g1, n, i1) + pair_bit_score(g2, n, i2)
                new_s = pair_bit_score(g1, n, i2) + pair_bit_score(g2, n, i1)
                # Only consider if not too harmful (within 10% of best)
                # Actually, for rank repair, accept any swap that increases rank
                # if score doesn't drop too much.
                if new_s < old_s - 5.0:
                    continue
                # Try the swap
                assign[(g1, n)], assign[(g2, n)] = i2, i1
                M_new = build_matrix(assign)
                rk_new = gf2_rank(M_new)
                if rk_new > rk:
                    rk = rk_new
                    M = M_new
                    improved = True
                    # print(f"iter {iterations}: swap (g{g1},n{n})<->(g{g2},n{n}), rank {rk}, score delta {new_s-old_s:.2f}")
                    break
                else:
                    # revert
                    assign[(g1, n)], assign[(g2, n)] = i1, i2
            if improved:
                break
        if improved:
            break
    if not improved:
        print(f"iter {iterations}: no improving swap found, rank stuck at {rk}")
        break

print(f"final rank: {rk} after {iterations} iterations")
if rk == 64:
    np.save("M_designB_fixed.npy", M)
    print("saved M_designB_fixed.npy")
    # verify properties
    rw, cw = M.sum(1), M.sum(0)
    print(f"row weights: {sorted(set(rw.tolist()))}, col weights: {sorted(set(cw.tolist()))}")
    ok = all(len(set(nibble_of(i) for i in np.where(M[g])[0])) == 4 for g in range(64))
    print(f"cross-nibble: {ok}")
else:
    print("FAILED to reach rank 64")
