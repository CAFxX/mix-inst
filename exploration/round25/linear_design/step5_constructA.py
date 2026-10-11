#!/usr/bin/env python3
"""Step 5: Analytical linear-layer construction.
Design A: 5u target (slow bits through <=1 XOR level, Huffman-balanced).
Design B: 6u, k=4 (better diffusion than baseline at same latency).
Uses Hungarian assignment for the bit-to-group routing."""
import json
import numpy as np
from scipy.optimize import linear_sum_assignment

S = [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14]

# Bit indexing: global bit g = 4*n + b (n=nibble 0..15, b=bit 0..3).
# Arrival times from step1: s[1]->2u (fast), s[0],s[2],s[3]->4u (slow).
ARRIVAL = {}
for n in range(16):
    for b in range(4):
        ARRIVAL[4*n + b] = 2 if b == 1 else 4
FAST = [g for g in range(64) if ARRIVAL[g] == 2]  # 16 bits
SLOW = [g for g in range(64) if ARRIVAL[g] == 4]  # 48 bits
print(f"fast bits: {len(FAST)}, slow bits: {len(SLOW)}")

W = json.load(open("ddt_lat_weights.json"))
Wcomb = np.array(W["W_combined"])  # [in_bit][out_bit], in_bit->out_bit flow

# Trail penalty: avoid routing strong linear-approx output bits to strong input bits.
# From step3: top approximations include in1->out1 (|W|=8). Build penalty matrix
# Pen[out_bit][in_bit] = max |W| over approximations (a->b) with b having out_bit set,
# weighted by whether a has in_bit set. Simplified: use Wcomb transposed.
# If S-output bit j strongly correlates with S-input bit i (Wcomb[i][j] high),
# then routing j -> (next round's input bit i) builds an iterative trail. Penalize.
TRAIL = Wcomb.T  # TRAIL[out_bit][in_bit]

def nibble_of(g):
    return g // 4

def bit_of(g):
    return g % 4

# ---- Hungarian assignment for Design A ----
# Structure: 64 outputs.
#   48 outputs: y = slow XOR fast  (k=2, latency 5u)
#   16 outputs: y = fast XOR fast XOR fast XOR fast (k=4, latency 4u)
# Assignment 1: match each slow bit to a fast bit (48 pairs). 48x48? No:
#   We have 48 slow bits and need 48 fast-uses from 16 fast bits (fanout 3).
#   Step 1: assign each slow bit to one of 16 fast bits (48 -> 16, many-to-one).
#   This is NOT Hungarian (not bijective). Use greedy + refinement, OR:
#   Replicate: create 48 "fast slots" (16 fast bits x 3 copies), Hungarian 48x48.
#
# Score(slow s, fast-slot f):
#   + diffusion: bonus if nibble(s) != nibble(f) (cross-nibble) [always true if we enforce]
#   + bit-flow: Wcomb[bit(s)][bit(f)] -- wait, direction?
#     The pair (s,f) gets XORed. For diffusion, we want s and f to carry
#     DIFFERENT information. Score by DDT/LAT decorrelation (low Wcomb = more independent).
#   - trail: TRAIL[bit(f)][bit(s)]... hmm.
#
# Actually for a XOR pair, the "goodness" is: the two bits should be from
# different nibbles (enforced structurally) and should not be strongly
# correlated (else the XOR cancels information).
#
# Let me define score(s, f) = -correlation(s,f) + spread_bonus.
# correlation approximated by Wcomb[bit(s)][bit(f)] + Wcomb[bit(f)][bit(s)].

def pair_score(s, f):
    bs, bf = bit_of(s), bit_of(f)
    ns, nf = nibble_of(s), nibble_of(f)
    if ns == nf:
        return -1000  # forbid same-nibble (must cross)
    # prefer low mutual flow (independent information)
    corr = Wcomb[bs, bf] + Wcomb[bf, bs]
    # prefer high total flow (both bits are "important")
    imp = Wcomb[:, bs].sum() + Wcomb[:, bf].sum()
    # trail penalty: if f (fast, bit bf) strongly predicts s's bit...
    # f is s[1] (bit 1). s is slow (bits 0,2,3).
    # Avoid routing where the pair creates a strong 2-bit linear relation.
    return imp - 3 * corr

# Build 48x48 cost matrix: rows=slow bits, cols=fast slots (16 fast x 3 copies)
print("\nBuilding Hungarian for slow-fast pairing...")
C = np.zeros((48, 48))
for i, s in enumerate(SLOW):
    for k in range(48):
        f = FAST[k % 16]
        C[i, k] = -pair_score(s, f)  # Hungarian minimizes
row, col = linear_sum_assignment(C)
total = C[row, col].sum()
print(f"Hungarian 48x48 solved, total cost = {total:.2f}")
pairing = [(SLOW[r], FAST[c % 16]) for r, c in zip(row, col)]
# check all cross-nibble
assert all(nibble_of(s) != nibble_of(f) for s, f in pairing), "same-nibble pair found!"
print(f"pairing OK: 48 slow-fast pairs, all cross-nibble")

# Assignment 2: 16 fast-only groups (4 fast bits each, k=4).
# 16 fast bits, each used 4 times (fanout 4) -> 64 fast-uses in 16 groups of 4.
# Greedy: distribute so each group has 4 different nibbles.
# Since there are 16 fast bits (one per nibble, bit=1), and 16 groups,
# put fast bit n in group g where g != n (avoid trivial), 4 per group.
# Simple: group g gets fast bits [(g+1)%16, (g+4)%16, (g+7)%16, (g+11)%16] (offsets)
# This ensures 4 distinct nibbles per group and each fast bit in 4 groups.
fast_groups = []
for g in range(16):
    members = [(g + d) % 16 for d in (1, 4, 7, 11)]
    fast_groups.append([4 * n + 1 for n in members])  # bit 1 of each nibble
# verify
assert all(len(set(nibble_of(x) for x in grp)) == 4 for grp in fast_groups)
flat = [x for grp in fast_groups for x in grp]
assert sorted(flat) == sorted(FAST * 4), "fast bit usage mismatch"
print("fast-only groups OK: 16 groups x 4 bits, distinct nibbles, fanout 4 each")

# Build the full 64x64 matrix M for Design A.
# Outputs 0..47: y[i] = slow_i XOR fast_{pair[i]}  (k=2)
# Outputs 48..63: y[48+g] = XOR of fast_groups[g]  (k=4)
M_A = np.zeros((64, 64), dtype=np.uint8)
for i, (s, f) in enumerate(pairing):
    M_A[i, s] = 1
    M_A[i, f] = 1
for g, grp in enumerate(fast_groups):
    for x in grp:
        M_A[48 + g, x] = 1

def gf2_rank(M):
    A = M.copy()
    r = 0
    nr, nc = A.shape
    for c in range(nc):
        piv = None
        for rr in range(r, nr):
            if A[rr, c]:
                piv = rr
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for rr in range(nr):
            if rr != r and A[rr, c]:
                A[rr] ^= A[r]
        r += 1
    return r

print(f"\nDesign A rank: {gf2_rank(M_A)} (need 64)")

# Latency of Design A (unit-delay):
# Outputs 0..47: max(4,2)+1 = 5u. Outputs 48..63: 2+2 = 4u. Max 5u.
lat_A = 0
for j in range(64):
    inputs = np.where(M_A[j])[0]
    arr = [ARRIVAL[i] for i in inputs]
    k = len(inputs)
    # optimal binary tree: Huffman on arrivals
    import heapq
    heap = arr[:]
    heapq.heapify(heap)
    # Huffman for min max(arrival+depth): repeatedly combine two smallest
    # Actually for XOR tree minimizing max leaf depth+arrival, Huffman is optimal.
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, max(a, b) + 1)
    lat_A = max(lat_A, heap[0])
print(f"Design A max latency (Huffman): {lat_A}u")

# Save M_A
np.save("M_designA.npy", M_A)
print("saved M_designA.npy")
