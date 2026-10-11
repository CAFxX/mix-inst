#!/usr/bin/env python3
"""D8 step 1: reproduce the S1 LIN failure locally on dd9_scsc_nolin_a,
extract the left-nullspace masks of rank-deficient 64-output blocks,
and study their stability across blocks/keys.

Also computes LAT4(rasC2_0) to look for correlation-1 / large entries.
"""
import importlib.util
import json
import numpy as np
import os
import sys
import time

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"
os.makedirs(WORK, exist_ok=True)


def load_model(name):
    spec = importlib.util.spec_from_file_location(
        "model_" + name, f"{FB}/candidates/{name}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def gf2_rank_nullspace(block):
    """block: (64,) uint64. Returns (rank, nullmask_rows list of uint64 masks v
    with v . row_i == 0 for all rows, as a basis)."""
    # rows as Python ints; elimination to row-echelon, track transform on identity
    a = [int(x) for x in block]
    # We want left nullspace: v (1x64) with v @ A = 0, A is 64x64 (rows).
    # Transpose: work with columns. Simpler: do elimination on A^T's rows.
    # Represent matrix as list of 64 ints (rows). Nullspace of rows = vectors v
    # with sum_i v_i * row_i = 0 (as 64-bit vector) => v in kernel of the
    # linear map given by rows as a 64x64 matrix acting on column vectors on the left.
    # Do Gauss-Jordan on the 64x64 matrix, tracking column ops via an index perm,
    # then read off kernel basis.
    n = 64
    mat = a[:]  # rows
    pivcol = [-1] * n  # pivcol[row] = pivot column
    row_of_col = [-1] * n
    r = 0
    for c in range(n - 1, -1, -1):
        piv = -1
        for i in range(r, n):
            if (mat[i] >> c) & 1:
                piv = i
                break
        if piv < 0:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        for i in range(n):
            if i != r and ((mat[i] >> c) & 1):
                mat[i] ^= mat[r]
        pivcol[r] = c
        row_of_col[c] = r
        r += 1
    rank = r
    # free columns -> kernel basis vectors (as row masks v with v @ A = 0,
    # i.e., for each free col f: v has 1 at f and at pivot cols c where
    # mat[row_of_col[c]] has bit f set)
    basis = []
    for f in range(n):
        if row_of_col[f] >= 0:
            continue
        v = 1 << f
        for rr in range(rank):
            if (mat[rr] >> f) & 1:
                v |= 1 << pivcol[rr]
        basis.append(v)
    return rank, basis


def block_ranks(S, nblocks):
    """Vectorized GF(2) rank for nblocks consecutive 64-row blocks of S."""
    ranks = np.zeros(nblocks, dtype=np.int32)
    for m in range(nblocks):
        blk = S[m * 64:(m + 1) * 64]
        a = [int(x) for x in blk]
        r = 0
        for c in range(63, -1, -1):
            piv = -1
            for i in range(r, 64):
                if (a[i] >> c) & 1:
                    piv = i
                    break
            if piv < 0:
                continue
            a[r], a[piv] = a[piv], a[r]
            # vectorize inner loop with numpy
            col_bit = np.array([ (x >> c) & 1 for x in a[r+1:] ], dtype=np.uint64)
            # can't easily vectorize XOR of python ints; do plain loop but only rows below
            for i in range(r + 1, 64):
                if (a[i] >> c) & 1:
                    a[i] ^= a[r]
            r += 1
        ranks[m] = r
    return ranks


def lat4(sbox):
    L = np.zeros((16, 16), dtype=int)
    for u in range(16):
        for v in range(16):
            s = 0
            for x in range(16):
                if bin(u & x).count("1") % 2 == bin(v & sbox[x]).count("1") % 2:
                    s += 1
            L[u, v] = s - 8  # in {-8..8}; corr = L/8
    return L


def main():
    t0 = time.time()
    name = "dd9_scsc_nolin_a"
    m = load_model(name)
    print(f"loaded {name}, {time.time()-t0:.1f}s", flush=True)

    # --- LAT4 of rasC2_0 ---
    SBOX_R = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]
    L = lat4(SBOX_R)
    big = [(u, v, L[u, v]) for u in range(16) for v in range(16) if abs(L[u, v]) >= 4]
    big.sort(key=lambda t: -abs(t[2]))
    print("LAT4(rasC2_0) entries with |L|>=4 (corr=L/8):")
    for u, v, e in big[:20]:
        print(f"  u={u:2d} v={v:2d} L={e:+d} corr={e/8:+.3f}")
    n_one = sum(1 for u in range(16) for v in range(16) if abs(L[u, v]) == 8 and (u, v) != (0, 0))
    print(f"nontrivial |corr|=1 pairs: {n_one}")

    # --- reproduce LIN D on key=0, first 256 blocks ---
    key = 0
    N = 256 * 64
    t1 = time.time()
    V = np.arange(N, dtype=np.uint64)
    S = np.asarray(m.mix_np(V, np.full(N, np.uint64(key), dtype=np.uint64)), dtype=np.uint64)
    print(f"model eval {N} outputs: {time.time()-t1:.1f}s", flush=True)
    t1 = time.time()
    ranks = block_ranks(S, 256)
    print(f"rank of 256 blocks: {time.time()-t1:.1f}s", flush=True)
    import collections
    hist = collections.Counter(ranks.tolist())
    print("rank histogram (key=0, 256 blocks):", dict(sorted(hist.items())))
    d = int((ranks <= 61).sum())
    print(f"D = {d}/256 blocks with rank<=61")

    # --- nullspace extraction for deficient blocks ---
    null_acc = []
    for bi in [0, 1, 2, 3]:
        blk = S[bi * 64:(bi + 1) * 64]
        rank, basis = gf2_rank_nullspace(blk)
        print(f"block {bi}: rank={rank}, nullity={len(basis)}")
        for v in basis[:6]:
            print(f"    mask {v:#018x} hw={bin(v).count('1')}")
        null_acc.append((bi, rank, basis))

    # stability: is there a mask in EVERY block's nullspace? check first basis
    # vector of block 0 against all 256 blocks
    if null_acc[0][2]:
        v0 = null_acc[0][2][0]
        dots = np.zeros(256, dtype=np.uint64)
        for bi in range(256):
            blk = S[bi * 64:(bi + 1) * 64]
            # dot(v0, row) for each row: parity of (v0 & row)
            d = 0
            for x in blk:
                d |= bin(v0 & int(x)).count("1") & 1
            dots[bi] = d
        print(f"mask {v0:#018x}: #blocks where it fails to annihilate = {int(dots.sum())}/256")

    json.dump({"rank_hist": {str(k): int(v) for k, v in hist.items()}, "D256": d},
              open(f"{WORK}/step1_ranks.json", "w"), indent=1)
    print("wrote step1_ranks.json")


if __name__ == "__main__":
    main()
