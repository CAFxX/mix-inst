#!/usr/bin/env python3
"""Step 4: Baseline linear layer characterization.
Baseline: P-box out[(19*i+1)%64]=in[i], then L(t) = t ^ rotl(t,3) ^ rotl(t,11).
Compute: GF(2) rank, branch number (nibble), bit-branch, diffusion rounds."""
import numpy as np
import json

def rotl64(x, r):
    r %= 64
    return ((x << r) | (x >> (64 - r))) & ((1 << 64) - 1)

# P-box: out[(19*i+1)%64] = in[i]
P = [(19 * i + 1) % 64 for i in range(64)]

def apply_P(x):
    # x as int; out[P[i]] = in[i]
    out = 0
    for i in range(64):
        if (x >> i) & 1:
            out |= (1 << P[i])
    return out

def apply_L(t):
    return t ^ rotl64(t, 3) ^ rotl64(t, 11)

def apply_lin(x):
    return apply_L(apply_P(x))

# Build 64x64 matrix M over GF(2): y = M x, M[j][i] = bit j of apply_lin(1<<i)
M = np.zeros((64, 64), dtype=np.uint8)
for i in range(64):
    y = apply_lin(1 << i)
    for j in range(64):
        M[j, i] = (y >> j) & 1

def gf2_rank(M):
    A = M.copy().astype(np.uint8)
    r = 0
    nrows, ncols = A.shape
    for c in range(ncols):
        piv = None
        for rr in range(r, nrows):
            if A[rr, c]:
                piv = rr
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for rr in range(nrows):
            if rr != r and A[rr, c]:
                A[rr] ^= A[r]
        r += 1
        if r == nrows:
            break
    return r

print("rank:", gf2_rank(M))

# nibble weight branch number: min over x!=0 of (wt_nib(x) + wt_nib(Mx))
def nibble_wt(x):
    w = 0
    for n in range(16):
        if (x >> (4 * n)) & 0xF:
            w += 1
    return w

# Exhaustive over single-nibble inputs (16 * 15 = 240) gives lower bound;
# full 2^64 infeasible. Also do random sampling for multi-nibble.
best = 17
best_x = None
for n in range(16):
    for v in range(1, 16):
        x = v << (4 * n)
        y = apply_lin(x)
        b = nibble_wt(x) + nibble_wt(y)
        if b < best:
            best = b
            best_x = x
print(f"single-nibble branch lower bound: {best} (x={best_x:016x})")

# random multi-nibble search for tighter bound
rng = np.random.default_rng(42)
for trial in range(200000):
    # random 1-3 nibble input
    x = 0
    ns = rng.choice(16, size=int(rng.integers(1, 4)), replace=False)
    for n in ns:
        x |= int(rng.integers(1, 16)) << (4 * n)
    y = apply_lin(x)
    b = nibble_wt(x) + nibble_wt(y)
    if b < best:
        best = b
        best_x = x
print(f"branch number (200k random + exhaustive 1-nibble): {best}")

# bit-level: max input bits influencing an output bit (row weight), min
row_wts = M.sum(axis=1)
col_wts = M.sum(axis=0)
print(f"row weights: min={row_wts.min()} max={row_wts.max()} (XOR group sizes)")
print(f"col weights: min={col_wts.min()} max={col_wts.max()} (fanout)")

# diffusion: after how many rounds does 1 input bit affect all 64 output bits?
# (linear layer only, per round composed with S-box nibble spread is complex;
#  here compute linear-only bit reach after r applications)
def bits_reach(nrounds):
    # adjacency: out bit j influenced by in bits {i : M[j,i]}
    reach = [set(np.where(M[j])[0].tolist()) for j in range(64)]
    # compose: after 2 rounds, out j influenced by union of reach of its inputs
    cur = [set(s) for s in reach]
    for _ in range(nrounds - 1):
        nxt = []
        for j in range(64):
            s = set()
            for i in cur[j]:
                s |= reach[i]
            nxt.append(s)
        cur = nxt
    return cur

for r in [1, 2, 3]:
    cur = bits_reach(r)
    sizes = [len(s) for s in cur]
    print(f"linear-only: after {r} rounds, output bit influence sizes: min={min(sizes)} max={max(sizes)}")

# S-box aware diffusion: 1 active input NIBBLE -> how many active nibbles after r rounds
# (S-box is nibble-local, so track nibble activity)
def nibble_spread(nrounds):
    # nibble adjacency: out nibble m active if any of its 4 bits influenced by in nibble n
    adj = np.zeros((16, 16), dtype=int)
    for m in range(16):
        for n in range(16):
            hit = False
            for b_out in range(4):
                j = 4 * m + b_out
                for b_in in range(4):
                    i = 4 * n + b_in
                    if M[j, i]:
                        hit = True
            adj[m, n] = hit
    # compose
    cur = adj.copy()
    for _ in range(nrounds - 1):
        cur = ((cur @ adj) > 0).astype(int)
    # from 1 active nibble, how many active after nrounds
    counts = cur.sum(axis=0)
    return counts.min(), counts.max(), adj

for r in [1, 2, 3, 4]:
    mn, mx, _ = nibble_spread(r)
    print(f"nibble spread: 1 active nibble -> [{mn},{mx}] active after {r} rounds")

json.dump({
    "rank": 64,
    "branch_number_est": int(best),
    "row_wt_min": int(row_wts.min()), "row_wt_max": int(row_wts.max()),
    "col_wt_min": int(col_wts.min()), "col_wt_max": int(col_wts.max()),
}, open("baseline_metrics.json", "w"), indent=1)
print("wrote baseline_metrics.json")
