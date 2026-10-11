#!/usr/bin/env python3
"""Batch-25: PNL (partial nonlinear layer) + XFC (XOR-fed chain) screen (track 5).

Co-designed from the batch-21d (lin2) autopsy (2026-10-11):
- lin2-5st x^=(ra&rb)^rc^rd: 56/100 DIFF-KEEP (min z=2.4, median 6.4) --
  linear diffusion is the binding constraint at few stages. But 4.65u/st -> 23.5u.
- PNL: keep the DUAL-linear diffusion, halve the AND gates with a rotating
  32-bit MASK: x ^= ((ra&rb)&MASK_i)^rc^rd. 7 stages est ~17.9u < 19.8u frontier.
  No masked/partial batch ever run (verified by tree grep 2026-10-11).
  Thesis: lin2's quality at PNL's cost. Distinct from track-8 two-state
  (both lanes fully nonlinear there) and track-6 maj/ARX.
- XFC pilot: u_i = rot(x_i,a_i) & (rot(u_{i-1},s_i)^rot(x_i,e_i)) --
  the AND's right operand is the PREVIOUS stage's nonlinear term (XOR-misaligned
  by a fresh rotation, so density stays ~1/4 and degree grows by 1/stage).
  AND with a NONLINEAR operand = different DDT class than fresh-operand ANDs.
  (Plain chaining u_i=A&rot(u_{i-1}) was REJECTED in co-design: density
  collapses 1/4->1/128 by stage 5, the 3-AND sparsity disease.)

Triage = EXACT S1 DIFF via lin_diff.diff_cell_logps, all 10 keys, N=2^18,
KEEP bar max|z|<10. KEEP survivors get a LIN proxy (lin_cell_logp on the same
SEQ outputs, keys 0x0 and 0xFF..F -- the structured keys where het6a died;
bar max D<=64; het6a died at D=164, null mean ~21.6).

Positive controls:
  (a) b33c exact schedule through the frontier-form pipeline -> expect KEEP
      z~3.3 (pipeline validation; FAILS LOUD if not KEEP).
  (b) frontier-5st arm -> expect 0 KEEP (negative control; reproduces the
      batch-22 control min z=179.5; proves the gate kills in the 5-stage regime).
Fail-loud: assert screen draws == 410 (+1 positive control); assert kills > 0.
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

MASK_PAIRS = [(0x5555555555555555, 0xAAAAAAAAAAAAAAAA),
              (0x3333333333333333, 0xCCCCCCCCCCCCCCCC),
              (0x0F0F0F0F0F0F0F0F, 0xF0F0F0F0F0F0F0F0),
              (0x00FF00FF00FF00FF, 0xFF00FF00FF00FF00),
              (0x0000FFFF0000FFFF, 0xFFFF0000FFFF0000),
              (0x00000000FFFFFFFF, 0xFFFFFFFF00000000)]

def eval_pnl(stages, masks):
    out = []
    for key in KEYS10:
        x = whiten_in(key)
        for (a, b, c, d), mk in zip(stages, masks):
            x = (x ^ (((rotl(x, a) & rotl(x, b)) & np.uint64(mk))
                      ^ rotl(x, c) ^ rotl(x, d))) & M64
        out.append((key, whiten_out(x, key)))
    return diff_worst(out), out

def eval_xfc(stages):
    # stages[i] = (a,b,s,e,c); i=0: u=rot(x,a)&rot(x,b); i>0: u=rot(x,a)&(rot(u,s)^rot(x,e))
    out = []
    for key in KEYS10:
        x = whiten_in(key)
        a, b, s, e, c = stages[0]
        u = (rotl(x, a) & rotl(x, b)) & M64
        x = (x ^ u ^ rotl(x, c)) & M64
        for (a, b, s, e, c) in stages[1:]:
            u = (rotl(x, a) & ((rotl(u, s) ^ rotl(x, e)) & M64)) & M64
            x = (x ^ u ^ rotl(x, c)) & M64
        out.append((key, whiten_out(x, key)))
    return diff_worst(out), out

def lin_proxy(S_list):
    # LIN smoke on structured keys only; bar max D <= 64 (het6a died at 164)
    worst_d, wkey = 0, None
    for key, S in S_list:
        if key in (0x0, 0xFFFFFFFFFFFFFFFF):
            d, _ = lin_cell_logp(S)
            if d > worst_d:
                worst_d, wkey = d, key
    return worst_d, wkey

def draw_rots(rng, n):
    while True:
        r = [int(rng.integers(1, 64)) for _ in range(n)]
        if len(set(r)) == n:
            return r

def run_arm(rng, name, form, nstages, n):
    results = []
    for t in range(n):
        if form == "pnl":
            stages = [tuple(draw_rots(rng, 4)) for _ in range(nstages)]
            masks = [MASK_PAIRS[int(rng.integers(0, len(MASK_PAIRS)))][int(rng.integers(0, 2))]
                     for _ in range(nstages)]
            (wz, wkey), S_list = eval_pnl(stages, masks)
            extra = {"masks": [hex(m) for m in masks]}
        elif form == "xfc":
            stages = [tuple(draw_rots(rng, 5)) for _ in range(nstages)]
            (wz, wkey), S_list = eval_xfc(stages)
            extra = {}
        else:  # frontier control
            stages = [tuple(draw_rots(rng, 3)) for _ in range(nstages)]
            wz, wkey = eval_frontier(stages)
            S_list, extra = None, {}
        keep = wz < 10
        ld, lkey = (lin_proxy(S_list) if keep and S_list is not None
                    else (None, None))
        if ld is not None and ld > 64:
            keep = False  # LIN-proxy kill (het6a lesson)
        print("try %s %3d maxworst|z|=%10.1f killkey=%#x %s%s" % (
            name, t, wz, wkey if wkey is not None else 0,
            "KEEP" if keep else "kill",
            (" LINPROXY-D=%d@%#x" % (ld, lkey)) if ld is not None else ""),
            flush=True)
        rec = {"arm": name, "form": form, "z": float(wz),
               "killkey": wkey, "keep": bool(keep),
               "lin_D": ld, "lin_key": lkey, "stages": stages}
        rec.update(extra)
        results.append(rec)
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
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB25
    rng = np.random.default_rng(seed)
    t0 = time.time()
    # Positive control (a): b33c schedule must KEEP (pipeline validation)
    wz, wkey = eval_frontier(B33C_SCHED)
    print("POSCTRL b33c: worst|z|=%.2f killkey=%#x -> %s" % (
        wz, wkey, "KEEP-OK" if wz < 10 else "FAIL"), flush=True)
    assert wz < 10, "POSITIVE-CONTROL FAILURE: b33c z=%.2f >= 10" % wz
    allr = [{"arm": "posctrl_b33c", "form": "frontier", "z": float(wz),
             "killkey": wkey, "keep": True, "stages": B33C_SCHED}]
    allr += run_arm(rng, "P7", "pnl", 7, 150)
    allr += run_arm(rng, "P8", "pnl", 8, 80)
    allr += run_arm(rng, "X5", "xfc", 5, 60)
    allr += run_arm(rng, "X6", "xfc", 6, 60)
    allr += run_arm(rng, "C5", "frontier", 5, 60)
    json.dump(allr, open("search_b25_results.json", "w"))
    draws = [r for r in allr if r["arm"] != "posctrl_b33c"]
    nk = sum(1 for r in draws if r["keep"])
    nkill = len(draws) - nk
    print("TOTAL: %d draws, %d keep, %d kill (%.1fs)" % (
        len(draws), nk, nkill, time.time() - t0), flush=True)
    assert nkill > 0, "POSITIVE-CONTROL FAILURE: 0 kills in %d draws" % len(draws)
    assert len(draws) == 410, "DRAW-COUNT MISMATCH: %d != 410" % len(draws)
    print("GATE CHECKS PASS: non-vacuous (%d kills), draw count exact." % nkill,
          flush=True)

if __name__ == "__main__":
    main()
