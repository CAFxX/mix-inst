#!/usr/bin/env python3
"""Batch-21c: 4-stage fat-AND cascade screen (track 5).

Stage: x ^= (ra&rb)^(rc&rd)^re. Est ~19.6u (4x4.9u/stage).
If S1-DIFF-clean -> dominates b33c (19.8u/6133 cells) on delay AND cells.
Triage = EXACT S1 DIFF, all 10 keys. KEEP bar max|z|<10.
"""
import sys, json, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps
from screen_lib import KEYS, N
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x

def eval_sched(stages):
    V = np.arange(N, dtype=np.uint64)
    worst, wkey = 0.0, None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for a, b, c, d, e in stages:
            x = (x ^ (rotl(x, a) & rotl(x, b)) ^ (rotl(x, c) & rotl(x, d)) ^ rotl(x, e)) & M64
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst: worst, wkey = wz, key
    return worst, wkey

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB21C
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    rng = np.random.default_rng(seed)
    results, t0 = [], time.time()
    for t in range(n):
        stages, seen = [], set()
        while len(stages) < 4:
            a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
            c = int(rng.integers(1, 64)); d = int(rng.integers(1, 64))
            e = int(rng.integers(0, 64))
            if a == b or c == d or (a, b, c, d, e) in seen: continue
            seen.add((a, b, c, d, e)); stages.append((a, b, c, d, e))
        wz, wkey = eval_sched(stages)
        keep = wz < 10
        print("try fat4 %3d maxworst|z|=%10.1f killkey=%#x %s" % (
            t, wz, wkey if wkey is not None else 0, "KEEP" if keep else "kill"), flush=True)
        results.append({"z": float(wz), "killkey": wkey, "keep": bool(keep), "stages": stages})
    keeps = [r for r in results if r["keep"]]
    print("=== %d/%d KEEP (%.1fs) ===" % (len(keeps), len(results), time.time() - t0), flush=True)
    for r in sorted(keeps, key=lambda r: r["z"])[:10]:
        print("KEEP z=%.2f %s" % (r["z"], r["stages"]), flush=True)
    zs = sorted(r["z"] for r in results)
    print("SUMMARY fat4: %d/%d keep, min z=%.1f, median z=%.1f" % (
        len(keeps), len(results), zs[0], zs[len(zs)//2]), flush=True)
    json.dump(results, open("search_b21c_results.json", "w"))

if __name__ == "__main__":
    main()
