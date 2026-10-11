#!/usr/bin/env python3
"""Batch-21f: mixed-stage screen (track 5). Each of 5 stages is randomly
lin2-type [x^=(ra&rb)^rc^rd] or std-type [x^=(ra&rb)^rc].
Est delay: n_lin2*4.65 + (5-n_lin2)*3.3. Target: 2 lin2 + 3 std = 19.2u.
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
        for typ, p in stages:
            if typ == "lin2":
                a, b, c, d = p
                x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c) ^ rotl(x, d)) & M64
            else:
                a, b, c = p
                x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst: worst, wkey = wz, key
    return worst, wkey

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB21F
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    rng = np.random.default_rng(seed)
    results, t0 = [], time.time()
    for t in range(n):
        stages, seen = [], set()
        nlin2 = 0
        while len(stages) < 5:
            if rng.random() < 0.4:
                a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
                c = int(rng.integers(0, 64)); d = int(rng.integers(0, 64))
                if a == b or c == d: continue
                key = ("lin2", a, b, c, d)
            else:
                a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
                c = int(rng.integers(0, 64))
                if a == b: continue
                key = ("std", a, b, c)
            if key in seen: continue
            seen.add(key); stages.append((key[0], key[1:]))
            if key[0] == "lin2": nlin2 += 1
        wz, wkey = eval_sched(stages)
        keep = wz < 10
        print("try mix %3d nlin2=%d maxworst|z|=%10.1f killkey=%#x %s" % (
            t, nlin2, wz, wkey if wkey is not None else 0, "KEEP" if keep else "kill"), flush=True)
        results.append({"z": float(wz), "killkey": wkey, "keep": bool(keep),
                        "nlin2": nlin2, "stages": [(typ, list(p)) for typ, p in stages]})
    keeps = [r for r in results if r["keep"]]
    print("=== %d/%d KEEP (%.1fs) ===" % (len(keeps), len(results), time.time() - t0), flush=True)
    for r in sorted(keeps, key=lambda r: r["z"])[:10]:
        print("KEEP nlin2=%d z=%.2f %s" % (r["nlin2"], r["z"], r["stages"]), flush=True)
    for nl in range(6):
        sub = [r for r in results if r["nlin2"] == nl]
        if sub:
            hk = sum(1 for r in sub if r["keep"]); zs = sorted(r["z"] for r in sub)
            print("SUMMARY nlin2=%d: %d/%d keep, min z=%.1f" % (nl, hk, len(sub), zs[0]), flush=True)
    json.dump(results, open("search_b21f_results.json", "w"))

if __name__ == "__main__":
    main()
