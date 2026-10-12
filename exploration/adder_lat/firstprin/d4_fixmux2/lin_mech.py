#!/usr/bin/env python3
"""Diagnose the LIN rank-deficiency mechanism of the V3 MUX2 network."""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/middepth/v3_mux2x4")
import numpy as np
import v3_model as M

def gf2_rank_rows(mat):
    """Rank of binary matrix given as list of uint64 rows (bit j = col j)."""
    r = [int(x) for x in mat]
    rank = 0
    for col in range(64):
        piv = -1
        for i in range(rank, len(r)):
            if (r[i] >> col) & 1:
                piv = i; break
        if piv < 0: continue
        r[rank], r[piv] = r[piv], r[rank]
        for i in range(rank+1, len(r)):
            if (r[i] >> col) & 1:
                r[i] ^= r[rank]
        rank += 1
    return rank

def nullspace_rows(mat):
    """Return basis for left nullspace: vectors c with sum_j c_j*row_j = 0 (as uint64 col mask)."""
    # We want c (64-bit, bit j = coeff of row j) with XOR_j c_j*row_j = 0 vector.
    # Transpose: cols of mat become rows; find right nullspace of transpose.
    n = len(mat)
    # Build 64 equations (one per column) in 64 unknowns (row coeffs)
    # eq_k: XOR over j of c_j * bit_k(row_j) = 0
    # Represent as 64x64 system: A[k][j] = bit_k(row_j); solve A c = 0.
    A = []
    for k in range(64):
        row = 0
        for j in range(n):
            if (int(mat[j]) >> k) & 1:
                row |= (1 << j)
        A.append(row)
    # Gaussian elimination on A (list of 64 uint64, bit j = coeff of unknown j)
    pivcol = []
    r = 0
    where = [-1]*64
    for col in range(64):
        piv = -1
        for i in range(r, 64):
            if (A[i] >> col) & 1:
                piv = i; break
        if piv < 0: continue
        A[r], A[piv] = A[piv], A[r]
        where[col] = r
        for i in range(64):
            if i != r and ((A[i] >> col) & 1):
                A[i] ^= A[r]
        r += 1
    # free variables -> nullspace basis
    basis = []
    for f in range(64):
        if where[f] == -1:
            v = 1 << f
            for col in range(64):
                if where[col] != -1 and ((A[where[col]] >> f) & 1):
                    v |= (1 << col)
            basis.append(v)
    return basis  # each basis vec: bitmask over row indices

def seq_block(stages, key, start, nblocks=1):
    V = np.arange(start, start+64*nblocks, dtype=np.uint64)
    K = np.full(64*nblocks, np.uint64(key), dtype=np.uint64)
    x = M.apply_stages((V ^ K) & np.uint64(0xFFFFFFFFFFFFFFFF), stages)
    S = (x ^ M.rotl(K, 13)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    return S

stages = M.BASE_STAGES
for ns in [1,2,3,4]:
    st = stages[:ns]
    ranks = []
    for b in range(8):
        blk = seq_block(st, 0x0, b*64)
        ranks.append(gf2_rank_rows(blk))
    print(f"{ns}-stage ranks over 8 blocks (key=0): {ranks}", flush=True)

# nullspace stability for 4-stage
print("--- nullspace analysis, 4-stage, key=0 ---", flush=True)
blks = [seq_block(stages, 0x0, b*64) for b in range(4)]
bases = [nullspace_rows(b) for b in blks]
for i, bas in enumerate(bases):
    print(f"block {i}: nullity={len(bas)}", flush=True)
# check if block0's null vectors annihilate block1's rows
def annihilates(c, mat):
    acc = 0
    for j in range(64):
        if (c >> j) & 1:
            acc ^= int(mat[j])
    return acc == 0
for v in bases[0][:4]:
    ok = [annihilates(v, blks[i]) for i in range(4)]
    print(f"  nullvec {v:#018x} annihilates blocks: {ok}", flush=True)
