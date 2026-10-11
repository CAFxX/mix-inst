#!/usr/bin/env python3
"""Batch-23: constant-xor AND cascade screen (track 5).

Co-designed from the batch-22 autopsy (self-masking KILLED 2026-10-11):
- The 3-term shape (x^AND^lin) is quality-dead at 5 stages even for the
  frontier's own form (arm A: 0/200, min z=179.5) -> 3-term needs 6 stages.
- Denser 5-stage skeletons (lin2/fat) are quality-clean but cost 23-25u:
  the XOR tree charges ~1.5u per extra term (cost disease).
- Within the AND-cascade construction class, 19.8u is the Pareto floor.
  The next challenger must come from OUTSIDE the (x^AND^lin-terms) shape.

NEW AXIS: CONSTANT-XOR AND CASCADE  x ^= (ra&rb)^C_i
Keccak-style dense round constants REPLACE the lin term (task direction
(a): masking without the extra term, via a different primitive).
- Cost: XOR-with-constant absorbs into XNOR2/wire in synthesis; the stage
  stays 2 logic levels (AND2 + XOR2/XNOR2), est ~3.0u/stage vs 3.3u for
  the frontier form. Attacks the cost disease at its root (the XOR tree).
- Fixed points: e_p -> e_p^C_i (~33 active bits for dense C_i); the ANDs
  fire on the next stage. No sparse fixed point. Constants are public;
  the differential argument is over the input, unaffected.
- Genuinely new: no batch has used in-stage constants (all prior forms
  key only via pre/post-whitening).

Arms (triage = EXACT S1 DIFF via lin_diff.diff_cell_logps, all 10 keys,
KEEP bar max|z|<10 -- same methodology as b21c/b22):
  E: x^=(ra&rb)^C_i, 5 stages, 200 draws (5x3.0 = 15u est)
  F: x^=(ra&rb)^C_i, 6 stages, 200 draws (6x3.0 = 18u est)
C_i drawn per stage with popcount in [24,40] (dense); recorded in results.

Positive control: fail-loud assert total kills > 0 and draw count == 400.
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

def popcount64(w):
    return bin(w).count("1")

def eval_sched(stages):
    V = np.arange(N, dtype=np.uint64)
    worst, wkey = 0.0, None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for a, b, C in stages:
            x = (x ^ (rotl(x, a) & rotl(x, b)) ^ np.uint64(C)) & M64
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst: worst, wkey = wz, key
    return worst, wkey

def draw_stages(rng, nstages):
    stages, seen = [], set()
    while len(stages) < nstages:
        a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
        if a == b: continue
        C = (int(rng.integers(0, 2**32)) << 32) | int(rng.integers(0, 2**32))
        if not (24 <= popcount64(C) <= 40): continue
        key = (a, b, C)
        if key in seen: continue
        seen.add(key); stages.append(key)
    return stages

def run_arm(rng, name, nstages, n):
    results = []
    for t in range(n):
        stages = draw_stages(rng, nstages)
        wz, wkey = eval_sched(stages)
        keep = wz < 10
        print("try %s %3d maxworst|z|=%10.1f killkey=%#x %s" % (
            name, t, wz, wkey if wkey is not None else 0,
            "KEEP" if keep else "kill"), flush=True)
        results.append({"arm": name, "nstages": nstages,
                        "z": float(wz), "killkey": wkey,
                        "keep": bool(keep),
                        "stages": [(a, b, hex(C)) for a, b, C in stages]})
    keeps = [r for r in results if r["keep"]]
    zs = sorted(r["z"] for r in results)
    print("=== %s: %d/%d KEEP ===" % (name, len(keeps), len(results)), flush=True)
    for r in sorted(keeps, key=lambda r: r["z"])[:10]:
        print("KEEP %s z=%.2f %s" % (name, r["z"], r["stages"]), flush=True)
    print("SUMMARY %s: %d/%d keep, min z=%.1f, median z=%.1f" % (
        name, len(keeps), len(results), zs[0], zs[len(zs)//2]), flush=True)
    return results

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB23
    rng = np.random.default_rng(seed)
    t0 = time.time()
    allr = []
    allr += run_arm(rng, "E-cx5", 5, 200)
    allr += run_arm(rng, "F-cx6", 6, 200)
    json.dump(allr, open("search_b23_results.json", "w"))
    nk = sum(1 for r in allr if r["keep"])
    nkill = len(allr) - nk
    print("TOTAL: %d draws, %d keep, %d kill (%.1fs)" % (
        len(allr), nk, nkill, time.time() - t0), flush=True)
    assert nkill > 0, "POSITIVE-CONTROL FAILURE: 0 kills in %d draws" % len(allr)
    assert len(allr) == 400, "DRAW-COUNT MISMATCH: %d != 400" % len(allr)
    print("GATE CHECKS PASS: non-vacuous (%d kills), draw count exact." % nkill,
          flush=True)

if __name__ == "__main__":
    main()
