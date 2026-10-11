#!/usr/bin/env python3
"""Batch-28 pilot: MUX-gate cascade (track 5).

New axis co-designed 2026-10-11 (supVI). Status of the 3-term single-state
space after batch-26:
- 2-input gates EXHAUSTED: AND (frontier; 5st wall), OR/NAND/NOR/ORN
  (dominated-by-construction, t6), ANDN (t6 owns andnM6, live).
- 3-input gates: AND3 (dead, b34), MAJ3 (dead 5st b19; cost-doomed 6st at
  4.1u/st), XOR3 (linear).
- Delay/time-shift forms STRUCTURALLY WEAK (batch-26): any wire spent on the
  past dilutes per-stage freshness -- delayed AND -> Fibonacci ANF-degree
  growth (1,2,3,5,8,13 vs 2^i); delayed lin -> Fibonacci sparse-corner
  bit-count growth. The 3-term budget leaves no room for the past.

Remaining untested 3-term gate: MUX2 (2:1 selector).
    x' = x ^ mux(ra,rb,rc) ^ rd,   mux(s,a,b) = (s&a)|(~s&b)

- 3 XOR terms (x, MUX, lin), stage-local, fresh -- satisfies every surviving
  constraint (cost disease, freshness, lin double-duty).
- Mechanism story (honest: thinner than the delay co-design, hence PILOT):
  the mux is "always live" -- its output always equals an input-dependent
  value (selects a or b), vs AND's 25% firing density. Per-gate differential
  uniformity is 1/2 (max DDT 4/8), same as AND, but the SELECT structure is a
  different DDT class than MASKING. a==b excluded (mux(s,a,a)=a, linear --
  het6a lesson); s==a / s==b collapse to OR/AND (valid, rare, allowed).
- Cost: XOR2+MUX2+XOR2; est ~3.5-3.8u/stage -> 5st ~17.5-19u (CHALLENGER if
  quality clears), 6st ~21-23u (cost-doomed, runs as the wall control).
- De-dup grep-verified: no mux/select gate in any batch, any track.

Arms: MU5 (5st, 40 draws -- the challenger arm), MU6 (6st, 40 draws --
wall control), C5 (frontier-5st negative control, expect 0 KEEP).

Triage = EXACT S1 DIFF via lin_diff.diff_cell_logps, all 10 keys, N=2^18,
KEEP bar max|z|<10 + LIN proxy (keys 0x0/0xFF..F, bar D<=64, het6a lesson).
Positive controls: (a) b33c -> KEEP z~3.3 (FAILS LOUD); (b) C5 -> expect
0 KEEP (known-dead form must KILL). Fail-loud: draws == 120, kills > 0.
"""
import sys, json, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps, lin_cell_logp
from screen_lib import KEYS, N
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]  # PARETO.md, z=3.3

def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x

def whiten_in(key):
    V = np.arange(N, dtype=np.uint64)
    return (V ^ np.uint64(key)) & M64

def whiten_out(x, key):
    return ((x ^ rotl(np.uint64(key), 13)) & M64).astype(np.uint64)

def mux(s, a, b):
    return (((s & a) | ((~s) & b)) & M64)

def diff_worst(S_list):
    worst, wkey = 0.0, None
    for key, S in S_list:
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, wkey = wz, key
    return worst, wkey

def eval_frontier(stages):
    out = []
    for key in KEYS10:
        x = whiten_in(key)
        for (a, b, c) in stages:
            x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
        out.append((key, whiten_out(x, key)))
    return diff_worst(out)

def eval_mux(stages):
    # stages[i] = (s,a,b,d): x' = x ^ mux(rs,ra,rb) ^ rd
    out = []
    for key in KEYS10:
        x = whiten_in(key)
        for (s, a, b, d) in stages:
            x = (x ^ mux(rotl(x, s), rotl(x, a), rotl(x, b))
                 ^ rotl(x, d)) & M64
        out.append((key, whiten_out(x, key)))
    return diff_worst(out), out

def lin_proxy(S_list):
    worst_d, wkey = 0, None
    for key, S in S_list:
        if key in (0x0, 0xFFFFFFFFFFFFFFFF):
            d, _ = lin_cell_logp(S)
            if d > worst_d:
                worst_d, wkey = d, key
    return worst_d, wkey

def draw_rots(rng, nstages):
    # all-distinct (established pattern); a==b would be linear (het6a lesson)
    stages = []
    for _ in range(nstages):
        while True:
            r = [int(rng.integers(1, 64)) for _ in range(4)]
            if len(set(r)) == 4:
                break
        stages.append(tuple(r))
    return stages

def run_arm(rng, name, form, nstages, n):
    results = []
    for t in range(n):
        if form == "mux":
            stages = draw_rots(rng, nstages)
            (wz, wkey), S_list = eval_mux(stages)
        else:
            stages = [tuple(int(rng.integers(1, 64)) for _ in range(3))
                      for _ in range(nstages)]
            wz, wkey = eval_frontier(stages)
            S_list = None
        keep = wz < 10
        ld, lkey = (lin_proxy(S_list) if keep and S_list is not None
                    else (None, None))
        if ld is not None and ld > 64:
            keep = False
        print("try %s %3d maxworst|z|=%10.1f killkey=%#x %s%s" % (
            name, t, wz, wkey if wkey is not None else 0,
            "KEEP" if keep else "kill",
            (" LINPROXY-D=%d@%#x" % (ld, lkey)) if ld is not None else ""),
            flush=True)
        results.append({"arm": name, "form": form, "z": float(wz),
                        "killkey": wkey, "keep": bool(keep),
                        "lin_D": ld, "lin_key": lkey, "stages": stages})
    keeps = [r for r in results if r["keep"]]
    zs = sorted(r["z"] for r in results)
    print("=== %s: %d/%d KEEP ===" % (name, len(keeps), len(results)), flush=True)
    for r in sorted(keeps, key=lambda r: r["z"])[:10]:
        print("KEEP %s z=%.2f D=%s %s" % (name, r["z"], r["lin_D"], r["stages"]),
              flush=True)
    print("SUMMARY %s: %d/%d keep, min z=%.1f, median z=%.1f" % (
        name, len(keeps), len(results), zs[0], zs[len(zs) // 2]), flush=True)
    return results

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB28
    rng = np.random.default_rng(seed)
    t0 = time.time()
    wz, wkey = eval_frontier(B33C_SCHED)
    print("POSCTRL b33c: worst|z|=%.2f killkey=%#x -> %s" % (
        wz, wkey, "KEEP-OK" if wz < 10 else "FAIL"), flush=True)
    assert wz < 10, "POSITIVE-CONTROL FAILURE: b33c z=%.2f >= 10" % wz
    allr = [{"arm": "posctrl_b33c", "form": "frontier",
             "z": float(wz), "killkey": wkey, "keep": True,
             "stages": B33C_SCHED}]
    allr += run_arm(rng, "MU5", "mux", 5, 40)
    allr += run_arm(rng, "MU6", "mux", 6, 40)
    allr += run_arm(rng, "C5", "frontier", 5, 40)
    json.dump(allr, open("search_b28_results.json", "w"))
    draws = [r for r in allr if r["arm"] != "posctrl_b33c"]
    nk = sum(1 for r in draws if r["keep"])
    nkill = len(draws) - nk
    print("TOTAL: %d draws, %d keep, %d kill (%.1fs)" % (
        len(draws), nk, nkill, time.time() - t0), flush=True)
    assert nkill > 0, "POSITIVE-CONTROL FAILURE: 0 kills in %d draws" % len(draws)
    assert len(draws) == 120, "DRAW-COUNT MISMATCH: %d != 120" % len(draws)
    print("GATE CHECKS PASS: non-vacuous (%d kills), draw count exact." % nkill,
          flush=True)

if __name__ == "__main__":
    main()
