#!/usr/bin/env python3
"""Batch-24: heterogeneous lin/no-lin AND cascade screen (track 5).

Co-designed from the batch-23 autopsy + S0 cost probe (2026-10-11):
- The lin term does DOUBLE DUTY: breaks sparse fixed points AND provides
  per-stage linear diffusion (batch-23: constants replace only the former;
  AND-only mixing dead even at 6 stages, min z=29,702).
- S0-measured (XCHECK clean): 6-stage pure no-lin x^=(ra&rb) = 16.7u /
  3,200 cells (2.78u/stage) vs 6-stage frontier form = 19.8u / 6,104 cells
  (3.3u/stage), same rotation schedule. The lin term costs ~0.5u/stage.
- A heterogeneous mix (cheap no-lin AND-density stages + a few
  frontier-form diffusive stages) projects to ~17-18u, BELOW the 19.8u
  frontier, IF the full function clears the DIFF wall.

NEW AXIS: 6-stage mixes of
  nolin: x ^= (ra&rb)          (cheap AND density, 2.78u/stage; has the
                                 sparse fixed point WITHIN the stage)
  front: x ^= (ra&rb)^rc       (diffusion + fixed-point breaking, 3.3u/st)
The DIFF triage is on the FULL 6-stage function, so a mix can clear even
though individual nolin stages have fixed points.
k = number of front stages, k in {1,2,3,4} x 150 draws (positions random).
Cost projection: k=1 -> 17.2u; k=2 -> 17.7u; k=3 -> 18.2u; k=4 -> 18.8u.
Genuinely new: b21f mixed dense+medium (lin2/frontier); this mixes
medium+lean with a different mechanism (sparse diffusive stages among
cheap density stages).

Triage = EXACT S1 DIFF via lin_diff.diff_cell_logps, all 10 keys,
KEEP bar max|z|<10. Positive control: fail-loud assert kills > 0 and
draw count == 600 (the k=1 arm is expected to die hard -- built-in
negative control).
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
        for typ, a, b, c in stages:
            if typ == "front":
                x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
            else:
                x = (x ^ (rotl(x, a) & rotl(x, b))) & M64
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst: worst, wkey = wz, key
    return worst, wkey

def draw_stages(rng, k):
    pos = set(rng.choice(6, size=k, replace=False))
    stages, seen = [], set()
    for j in range(6):
        while True:
            a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
            if a == b: continue
            c = int(rng.integers(1, 64))
            typ = "front" if j in pos else "nolin"
            key = (typ, a, b, c)
            if key in seen: continue
            seen.add(key); stages.append((typ, a, b, c)); break
    return stages

def run_arm(rng, k, n):
    name = "k%d" % k
    results = []
    for t in range(n):
        stages = draw_stages(rng, k)
        wz, wkey = eval_sched(stages)
        keep = wz < 10
        print("try %s %3d maxworst|z|=%10.1f killkey=%#x %s" % (
            name, t, wz, wkey if wkey is not None else 0,
            "KEEP" if keep else "kill"), flush=True)
        results.append({"arm": name, "k": k, "z": float(wz),
                        "killkey": wkey, "keep": bool(keep),
                        "stages": stages})
    keeps = [r for r in results if r["keep"]]
    zs = sorted(r["z"] for r in results)
    print("=== %s: %d/%d KEEP ===" % (name, len(keeps), len(results)), flush=True)
    for r in sorted(keeps, key=lambda r: r["z"])[:10]:
        print("KEEP %s z=%.2f %s" % (name, r["z"], r["stages"]), flush=True)
    print("SUMMARY %s: %d/%d keep, min z=%.1f, median z=%.1f" % (
        name, len(keeps), len(results), zs[0], zs[len(zs)//2]), flush=True)
    return results

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB24
    rng = np.random.default_rng(seed)
    t0 = time.time()
    allr = []
    for k in (1, 2, 3, 4):
        allr += run_arm(rng, k, 150)
    json.dump(allr, open("search_b24_results.json", "w"))
    nk = sum(1 for r in allr if r["keep"])
    nkill = len(allr) - nk
    print("TOTAL: %d draws, %d keep, %d kill (%.1fs)" % (
        len(allr), nk, nkill, time.time() - t0), flush=True)
    assert nkill > 0, "POSITIVE-CONTROL FAILURE: 0 kills in %d draws" % len(allr)
    assert len(allr) == 600, "DRAW-COUNT MISMATCH: %d != 600" % len(allr)
    print("GATE CHECKS PASS: non-vacuous (%d kills), draw count exact." % nkill,
          flush=True)

if __name__ == "__main__":
    main()
