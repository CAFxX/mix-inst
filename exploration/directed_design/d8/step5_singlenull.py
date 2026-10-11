#!/usr/bin/env python3
"""D8 step 5: nullspace masks of singlerot[13] rank-deficient blocks.

Is ONES (parity) always in the nullspace? What are the other dependencies?
Check stability across blocks.
"""
import importlib.util
import numpy as np
import os
import sys
import time
from collections import Counter

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"


def load_model(name):
    spec = importlib.util.spec_from_file_location(
        "model_" + name, f"{FB}/candidates/{name}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def nullspace_basis(block):
    n = 64
    mat = [int(x) for x in block]
    pivcol = [-1] * n
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
    basis = []
    for f in range(n):
        if row_of_col[f] >= 0:
            continue
        v = 1 << f
        for rr in range(r):
            if (mat[rr] >> f) & 1:
                v |= 1 << pivcol[rr]
        basis.append(v)
    return r, basis


def annihilates(v, block):
    for x in block:
        if bin(v & int(x)).count("1") & 1:
            return False
    return True


def main():
    m = load_model("dd10_scsc_singlerot_a")
    key = 0
    N = 512 * 64
    V = np.arange(N, dtype=np.uint64)
    S = np.asarray(m.mix_np(V, np.full(N, np.uint64(key), dtype=np.uint64)),
                   dtype=np.uint64)
    ONES = (1 << 64) - 1
    # check ONES annihilates every block
    bad = 0
    for bi in range(512):
        if not annihilates(ONES, S[bi * 64:(bi + 1) * 64]):
            bad += 1
    print(f"ONES fails to annihilate {bad}/512 blocks (expect 0: even parity always)")
    # nullspaces of deficient blocks
    nshown = 0
    for bi in range(512):
        blk = S[bi * 64:(bi + 1) * 64]
        rank, basis = nullspace_basis(blk)
        if rank <= 61 and nshown < 4:
            print(f"block {bi}: rank={rank} nullity={len(basis)}")
            for v in basis:
                print(f"    {v:#018x} hw={bin(v).count('1')}")
            nshown += 1
    # collect hw distribution of null vectors across 64 deficient blocks
    hws = []
    nblocks = 0
    for bi in range(512):
        blk = S[bi * 64:(bi + 1) * 64]
        rank, basis = nullspace_basis(blk)
        if rank <= 61:
            nblocks += 1
            for v in basis:
                hws.append(bin(v).count("1"))
        if nblocks >= 64:
            break
    print(f"hw histogram of null vectors over {nblocks} deficient blocks:",
          dict(sorted(Counter(hws).items())))


if __name__ == "__main__":
    main()
