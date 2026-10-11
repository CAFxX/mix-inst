#!/usr/bin/env python3
"""Step 6: Design B -- 6u, k=4, uniform.
64 outputs, each XOR of 4 S-output bits from 4 different nibbles.
Each S-output bit used exactly 4 times (fanout 4).
Hungarian 256x256 for bit-to-(group,nibble) assignment."""
import json
import numpy as np
from scipy.optimize import linear_sum_assignment

S = [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14]
ARRIVAL = {4*n+b: (2 if b == 1 else 4) for n in range(16) for b in range(4)}

W = json.load(open("ddt_lat_weights.json"))
Wcomb = np.array(W["W_combined"])
# flow_score[b] = total DDT+LAT flow through output bit b (higher = more influential)
flow_score = Wcomb.sum(axis=0)  # sum over input bits
flow_score = flow_score / flow_score.max()
print("flow_score per output bit:", np.round(flow_score, 3))

# hot bits: output bits that are targets of max-bias linear approximations.
# From step3: out bit 1 is hot (|W|=8 for in0->out1, in1->out1, etc.)
# Penalize over-concentration of hot bits (trail alignment risk).
HOT = {1: 1.0}  # bit -> penalty weight

# Group definitions: 64 groups, each needs 4 distinct nibbles.
# Pattern: group g (0..63) gets nibbles based on a spread pattern.
# Use: nibbles = [(g//4 + d) % 16 for d in (0, 5, 9, 13)]?
# We want: each nibble appears in exactly 16 groups (64*4/16 = 16).
# And groups should be "spread".
# Simple pattern: group g corresponds to output bit g.
# Let group g take nibbles: (g % 16), ((g//4 + 5) % 16), ((g//4 + 9) % 16), ((g//4 + 13) % 16)?
# Hmm, let me think.
# Actually, cleanest: think of 16 "output nibbles" m = g // 4, and 4 "sub-groups" s = g % 4.
# Output nibble m's 4 bits (y[4m]..y[4m+3]) are computed by groups (m,0)..(m,3).
# For diffusion, each of these 4 groups should sample 4 different input nibbles,
# and across the 4 groups, we want good coverage.
#
# Pattern: group (m, s) takes nibbles:
#   n0 = (m + 0) % 16
#   n1 = (m + 1 + 4*s) % 16
#   n2 = (m + 2 + 8*s) % 16  -- hmm, this is ad hoc.
#
# Let me use a principled pattern based on the baseline's P-box idea but optimized.
# Actually, simplest good pattern: group (m,s) takes nibbles
#   {(4*m + s + d) % 16 : d in (0, 4, 8, 12)}? No.
#
# Let me just do: group g takes nibbles [(g + 0) % 16, (g + 5) % 16, (g + 9) % 16, (g + 13) % 16].
# Check: each nibble n appears in groups g where (g+d)%16 = n for d in (0,5,9,13),
# i.e., g in {n, n-5, n-9, n-13} mod 16, each giving 4 groups (g, g+16, g+32, g+48 for the 4 values).
# Wait, g ranges 0..63. For fixed n, g % 16 determines (g+d)%16.
# g % 16 in {n, n-5, n-9, n-13} (mod 16) -> 4 values, each with g = val, val+16, val+32, val+48 -> 16 groups. ✓
# Each group has 4 distinct nibbles? Need (0,5,9,13) distinct mod 16: yes. ✓
def group_nibbles(g):
    return [((g % 16) + d) % 16 for d in (0, 5, 9, 13)]

# verify
from collections import Counter
cnt = Counter()
for g in range(64):
    ns = group_nibbles(g)
    assert len(set(ns)) == 4, f"group {g} has duplicate nibbles"
    for n in ns:
        cnt[n] += 1
assert all(cnt[n] == 16 for n in range(16)), f"nibble coverage uneven: {cnt}"
print("group nibble pattern OK: 64 groups x 4 distinct nibbles, each nibble in 16 groups")

# Hungarian: 256 rows = (group g, nibble n) pairs; 256 cols = (S-bit i, copy c).
# Row (g,n): needs 1 bit from nibble n. Col (i,c): S-output bit i (copy c).
# Score = -inf if nibble(i) != n, else flow/trail score on bit(i).
N = 256
pairs = []  # (g, n)
for g in range(64):
    for n in group_nibbles(g):
        pairs.append((g, n))
assert len(pairs) == 256
bits = []  # (i, c)
for i in range(64):
    for c in range(4):
        bits.append((i, c))
assert len(bits) == 256

def bit_of(i):
    return i % 4
def nibble_of(i):
    return i // 4

print("building 256x256 cost matrix...")
C = np.full((N, N), 1e9)
for r, (g, n) in enumerate(pairs):
    for c, (i, cc) in enumerate(bits):
        if nibble_of(i) != n:
            continue
        b = bit_of(i)
        # score: prefer high-flow bits, penalize hot bits
        s = 2.0 * flow_score[b] - 1.5 * HOT.get(b, 0.0)
        # small tie-breaker: prefer bit diversity within group (use g to vary)
        # (deterministic tie-break via g and b)
        s += 0.01 * ((g + b) % 4)
        C[r, c] = -s

print("solving Hungarian 256x256...")
row, col = linear_sum_assignment(C)
print(f"solved, total cost = {C[row,col].sum():.2f}")
# verify no -inf assignments
assert (C[row, col] < 1e8).all(), "infeasible assignment!"

# Build M_B: 64x64, M_B[g][i] = 1 if bit i in group g
M_B = np.zeros((64, 64), dtype=np.uint8)
for r, c in zip(row, col):
    g, n = pairs[r]
    i, cc = bits[c]
    assert nibble_of(i) == n
    M_B[g, i] = 1

# verify structure
row_wts = M_B.sum(axis=1)
col_wts = M_B.sum(axis=0)
print(f"row weights: {sorted(set(row_wts.tolist()))} (want all 4)")
print(f"col weights: {sorted(set(col_wts.tolist()))} (want all 4)")
assert (row_wts == 4).all() and (col_wts == 4).all()
# verify cross-nibble
for g in range(64):
    ns = set(nibble_of(i) for i in np.where(M_B[g])[0])
    assert len(ns) == 4, f"group {g} nibbles: {ns}"
print("cross-nibble verified: all 64 groups span 4 distinct nibbles")

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

rk = gf2_rank(M_B)
print(f"Design B rank: {rk} (need 64)")
if rk != 64:
    print("RANK DEFICIENT - need to adjust")

# Latency: all rows have 4 inputs, max arrival 4u, tree depth 2 -> 6u.
# But Huffman: if a group has early bits, can we do better?
# For k=4, optimal tree on arrivals: use Huffman.
import heapq
max_lat = 0
for g in range(64):
    inputs = np.where(M_B[g])[0]
    arr = [ARRIVAL[i] for i in inputs]
    heap = arr[:]; heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap); b = heapq.heappop(heap)
        heapq.heappush(heap, max(a, b) + 1)
    max_lat = max(max_lat, heap[0])
print(f"Design B max latency (Huffman): {max_lat}u")

np.save("M_designB.npy", M_B)
print("saved M_designB.npy")
