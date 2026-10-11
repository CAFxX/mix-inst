#!/usr/bin/env python3
"""Batch-22: self-masking AND cascade screen (track 5).

Co-designed from the fat autopsy (batch-21b terminally closed 2026-10-11):
- The lin term is LOAD-BEARING: without it, sparse fixed points are
  deterministic (e_p -> e_p exactly when all rotations nonzero; the ANDs
  never fire on a single active bit). fat4 killkey=0x0 194/200.
- The COST DISEASE is the XOR tree: every term beyond (x^AND^lin) costs
  ~1.4-1.6u/stage in Yosys mapping (b33c-form 3.3u/stage; lin2 4.7u;
  fat 4.9u). The viable cost shape is EXACTLY 3 XOR terms.
- The 4-stage quality wall holds for every AND form tested -> quality
  needs 5 stages; 5 x 3.3u = 16.5u est < 19.8u frontier IF a 3-term
  stage clears the DIFF wall at 5 stages.

NEW AXIS: SELF-MASKING AND  x ^= (x&rb)^rc
Same 3-term gate shape as the frontier form x^=(ra&rb)^rc (est ~3.3u/stage),
but the AND probes the output bit ITSELF (zero rotation on one operand)
instead of two rotated copies. Different masking primitive: per-bit
differential masking is endogenous
  Dx'[i] = Dx[i] ^ (Dx[i]&x[i+b]) ^ Dx[i+c]
(the bit's own difference is masked by the AND with prob ~1/2/stage)
rather than relying on cross-bit AND firing + additive lin term.
Fixed-point check: e_p -> e_p + e_{p-c} (lin term breaks the sparse fixed
point -- mechanism intact). b,c in [1,64): b=0 degenerates the AND
(x&x=x, stage goes linear); c=0 drops the passthrough (collapses diffs).
NEVER tested in any batch screen (verified by grep: no zero-rotation AND
operand in batch1-21 screens).

Arms (triage = EXACT S1 DIFF via lin_diff.diff_cell_logps, all 10 keys,
KEEP bar max|z|<10 -- same methodology as b21c):
  A: frontier form x^=(ra&rb)^rc, 5 stages, 200 draws (CONTROL -- never
     screened at 5st; calibrates the 5-stage 3-term wall)
  B: self-masking x^=(x&rb)^rc, 5 stages, 200 draws (NEW AXIS)
  C: frontier form, 4 stages, 100 draws (long-shot control)
  D: self-masking, 4 stages, 100 draws (long shot; 4x3.3=13.2u if clears)

Positive control: fail-loud assert total kills > 0 at end (the harness
must not go vacuous and keep everything).
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

def eval_sched(apply, stages):
    V = np.arange(N, dtype=np.uint64)
    worst, wkey = 0.0, None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for s in stages:
            x = apply(x, s)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst: worst, wkey = wz, key
    return worst, wkey

def apply_frontier(x, s):
    a, b, c = s
    return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64

def apply_selfmask(x, s):
    b, c = s
    return (x ^ (x & rotl(x, b)) ^ rotl(x, c)) & M64

def draw_stages(rng, nstages, form):
    stages, seen = [], set()
    while len(stages) < nstages:
        if form == "frontier":
            a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
            c = int(rng.integers(1, 64))
            if a == b: continue
            key = (a, b, c)
        else:
            b = int(rng.integers(1, 64)); c = int(rng.integers(1, 64))
            key = (b, c)
        if key in seen: continue
        seen.add(key); stages.append(key)
    return stages

def run_arm(rng, name, form, nstages, n):
    apply = apply_frontier if form == "frontier" else apply_selfmask
    results = []
    for t in range(n):
        stages = draw_stages(rng, nstages, form)
        wz, wkey = eval_sched(apply, stages)
        keep = wz < 10
        print("try %s %3d maxworst|z|=%10.1f killkey=%#x %s" % (
            name, t, wz, wkey if wkey is not None else 0,
            "KEEP" if keep else "kill"), flush=True)
        results.append({"arm": name, "form": form, "nstages": nstages,
                        "z": float(wz), "killkey": wkey,
                        "keep": bool(keep), "stages": stages})
    keeps = [r for r in results if r["keep"]]
    zs = sorted(r["z"] for r in results)
    print("=== %s: %d/%d KEEP ===" % (name, len(keeps), len(results)), flush=True)
    for r in sorted(keeps, key=lambda r: r["z"])[:10]:
        print("KEEP %s z=%.2f %s" % (name, r["z"], r["stages"]), flush=True)
    print("SUMMARY %s: %d/%d keep, min z=%.1f, median z=%.1f" % (
        name, len(keeps), len(results), zs[0], zs[len(zs)//2]), flush=True)
    return results

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB22
    rng = np.random.default_rng(seed)
    t0 = time.time()
    allr = []
    allr += run_arm(rng, "A-front5", "frontier", 5, 200)
    allr += run_arm(rng, "B-self5", "selfmask", 5, 200)
    allr += run_arm(rng, "C-front4", "frontier", 4, 100)
    allr += run_arm(rng, "D-self4", "selfmask", 4, 100)
    json.dump(allr, open("search_b22_results.json", "w"))
    nk = sum(1 for r in allr if r["keep"])
    nkill = len(allr) - nk
    print("TOTAL: %d draws, %d keep, %d kill (%.1fs)" % (
        len(allr), nk, nkill, time.time() - t0), flush=True)
    # Positive control: the harness must kill bad draws; a screen that keeps
    # everything (or kills nothing) is vacuous -> fail LOUD.
    assert nkill > 0, "POSITIVE-CONTROL FAILURE: 0 kills in %d draws" % len(allr)
    assert len(allr) == 600, "DRAW-COUNT MISMATCH: %d != 600" % len(allr)
    print("GATE CHECKS PASS: non-vacuous (%d kills), draw count exact." % nkill,
          flush=True)

if __name__ == "__main__":
    main()
