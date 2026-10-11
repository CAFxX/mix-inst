#!/usr/bin/env python3
"""D8 step 4: full S1-LIN D + rank histograms for nolin / singlerot[13] / lin(5,13).

Uses the real lin_cell_logp logic (4096 blocks of 64 consecutive outputs).
Also reduced-N DIFF probe (N=2^14) via the real diff_cell_logps.
"""
import importlib.util
import numpy as np
import os
import sys
import time
from collections import Counter

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
sys.path.insert(0, FB + "/src")
from lin_diff import lin_cell_logp, diff_cell_logps

WORK = "/home/hatch/workspace/mix/exploration/directed_design/d8"


def load_model(name):
    spec = importlib.util.spec_from_file_location(
        "model_" + name, f"{FB}/candidates/{name}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fast_block_ranks(S, nblocks):
    """GF(2) rank per 64-row block, numpy-vectorized inner loop."""
    ranks = np.zeros(nblocks, dtype=np.int32)
    for m in range(nblocks):
        a = np.array([int(x) for x in S[m * 64:(m + 1) * 64]], dtype=np.uint64)
        # work with Python ints in a list for XOR; vectorize pivot search
        A = [int(v) for v in a]
        r = 0
        for c in range(63, -1, -1):
            piv = -1
            for i in range(r, 64):
                if (A[i] >> c) & 1:
                    piv = i
                    break
            if piv < 0:
                continue
            A[r], A[piv] = A[piv], A[r]
            pr = A[r]
            for i in range(r + 1, 64):
                if (A[i] >> c) & 1:
                    A[i] ^= pr
            r += 1
            if r == 64:
                break
        ranks[m] = r
    return ranks


def main():
    t0 = time.time()
    cands = [("dd9_scsc_nolin_a", "nolin"),
             ("dd10_scsc_singlerot_a", "singlerot[13]"),
             ("dd9_scsc_linall_a", "lin(5,13)")]
    key = 0x0
    N = 4096 * 64
    for name, tag in cands:
        m = load_model(name)
        t1 = time.time()
        V = np.arange(N, dtype=np.uint64)
        S = np.asarray(m.mix_np(V, np.full(N, np.uint64(key), dtype=np.uint64)),
                       dtype=np.uint64)
        t_eval = time.time() - t1
        # real S1 LIN cell
        d, logp = lin_cell_logp(S)
        # rank histogram (first 512 blocks for speed detail + full D from lin_cell)
        ranks = fast_block_ranks(S, 512)
        hist = Counter(ranks.tolist())
        print(f"[{tag}] {name} key=0x0: eval {t_eval:.1f}s | "
              f"S1-LIN D={d}/4096 logp={logp:.1f} | "
              f"rank_hist(512 blocks)={dict(sorted(hist.items()))}", flush=True)

    # reduced-N DIFF probe
    print("--- DIFF probe N=2^14 ---", flush=True)
    N2 = 1 << 14
    for name, tag in cands:
        m = load_model(name)
        for key in [0x0, 0x123456789ABCDEF0]:
            V = np.arange(N2, dtype=np.uint64)
            S = np.asarray(m.mix_np(V, np.full(N2, np.uint64(key), dtype=np.uint64)),
                           dtype=np.uint64)
            logps, wz, flp, blp = diff_cell_logps(S, key)
            print(f"[{tag}] key={key:#x}: worst|z|={wz:.1f} fisher_logp={flp:.1f} "
                  f"bonf_logp={blp:.1f}", flush=True)
    print(f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
