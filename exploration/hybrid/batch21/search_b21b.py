#!/usr/bin/env python3
"""Batch-21b: fat-stage cascade screen (track 5).

Stage: x ^= (ra&rb)^(rc&rd)^re   (2-AND + linear, ~3.3u/stage like b33)
Control: x ^= (ra&rb)^rc         (1-AND, b33 form -- tests if 5-stage barrier
                                  was schedule luck: t6_and5a/b died as FIXED
                                  schedules, never searched)

Triage = EXACT S1 DIFF (diff_cell_logps, all 10 keys). KEEP bar max|z|<10.
Targets: 5-stage 2-AND ~16.5u (new speed point if S1-clean);
         5-stage 1-AND ~17.2u (control); 6-stage 2-AND ~19.8u (backup).
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

def eval_sched(form, stages):
    V = np.arange(N, dtype=np.uint64)
    worst, wkey = 0.0, None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            if form == "fat":
                a, b, c, d, e = st
                x = (x ^ (rotl(x, a) & rotl(x, b)) ^ (rotl(x, c) & rotl(x, d)) ^ rotl(x, e)) & M64
            else:
                a, b, c = st
                x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst: worst, wkey = wz, key
    return worst, wkey

def sample_sched(rng, form, nstages):
    stages, seen = [], set()
    while len(stages) < nstages:
        if form == "fat":
            a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
            c = int(rng.integers(1, 64)); d = int(rng.integers(1, 64))
            e = int(rng.integers(0, 64))
            if a == b or c == d: continue
            key = (a, b, c, d, e)
        else:
            a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
            c = int(rng.integers(0, 64))
            if a == b: continue
            key = (a, b, c)
        if key in seen: continue
        seen.add(key); stages.append(key)
    return stages

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB21B
    rng = np.random.default_rng(seed)
    plan = [("fat", 5, 60), ("std", 5, 40), ("fat", 6, 30)]
    results, t0 = [], time.time()
    for form, ns, n in plan:
        for t in range(n):
            stages = sample_sched(rng, form, ns)
            wz, wkey = eval_sched(form, stages)
            keep = wz < 10
            print("try %-3s %dst %3d maxworst|z|=%10.1f killkey=%#x %s" % (
                form, ns, t, wz, wkey if wkey is not None else 0, "KEEP" if keep else "kill"), flush=True)
            results.append({"form": form, "nstages": ns, "z": float(wz),
                            "killkey": wkey, "keep": bool(keep), "stages": stages})
    keeps = [r for r in results if r["keep"]]
    print("=== %d/%d KEEP (%.1fs) ===" % (len(keeps), len(results), time.time() - t0), flush=True)
    for r in sorted(keeps, key=lambda r: r["z"]):
        print("KEEP %-3s %dst z=%.2f killkey=%s %s" % (r["form"], r["nstages"], r["z"], r["killkey"], r["stages"]), flush=True)
    for form, ns, n in plan:
        sub = [r for r in results if r["form"] == form and r["nstages"] == ns]
        hk = sum(1 for r in sub if r["keep"]); zs = sorted(r["z"] for r in sub)
        print("SUMMARY %-3s %dst: %d/%d keep, min z=%.1f, median z=%.1f" % (form, ns, hk, len(sub), zs[0], zs[len(zs)//2]), flush=True)
    json.dump(results, open("search_b21b_results.json", "w"))

if __name__ == "__main__":
    main()
