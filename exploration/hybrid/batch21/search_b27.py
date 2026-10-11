#!/usr/bin/env python3
"""Batch-27: delayed-LIN AND cascade screen (track 5).

Backup axis co-designed 2026-10-11 (supVI) from the batch-26 degree analysis:
batch-26's delayed AND operand dilutes per-stage nonlinearity -- ANF degree
grows Fibonacci (d_{i+1} = d_{i-1}+d_i: 1,2,3,5,8,13) not exponential (2^i),
so D5-5st has the degree of a ~3.7-stage frontier form. This axis keeps the
delay idea but puts it in the LIN term, preserving exponential degree growth:

    x' = x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(p,c),   p_{i+1} = x_i

- Degree: d_{i+1} = 2*d_i (AND on current state) -- same as frontier.
- Fixed-point breaking: at the sparse corner the AND is ~0, so
  x' = x ^ rotl(p,c); p is the previous state (input-dependent from stage 1;
  p0=x0 breaks at stage 0). The lin term still breaks sparse fixed points.
- lin duty (ii) is now time-shifted: each stage diffuses the PREVIOUS state's
  bits linearly; current differences propagate via identity + AND masking.
  Whether time-shifted diffusion clears the DIFF wall is the empirical
  question -- b23/b24 killed constant/no-lin, but a delayed STATE lin is
  neither (it is input-dependent and diffusive, just one stage late).
- Cost: same 3-term gate shape as frontier (~3.3u/stage est).
- De-dup: no batch has delayed the lin term (b23 = constants all stages;
  b24 = mixed no-lin/frontier stages; every lin term ever screened taps the
  current state). Genuinely new.

Arms: L5 (p0=x0, 5st ~16.5u), L6 (p0=x0, 6st ~19.8u), LK5 (p0=key, 5st),
      LK6 (p0=key, 6st), C5 (frontier-5st negative control, expect 0 KEEP).

Triage = EXACT S1 DIFF via lin_diff.diff_cell_logps, all 10 keys, N=2^18,
KEEP bar max|z|<10 + LIN proxy (keys 0x0/0xFF..F, bar D<=64, het6a lesson).
Positive controls: (a) b33c schedule -> KEEP z~3.3 (pipeline validation,
FAILS LOUD); (b) C5 -> expect 0 KEEP (known-dead form must KILL).
Fail-loud: assert draws == 200; assert kills > 0 (non-vacuous).
a!=b enforced (het6a linear-stage lesson -- the AND is same-state here).
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

def eval_dlin(stages, p0_mode):
    # stages[i] = (a,b,c); delay in the LIN term: x' = x^(ra&rb)^rotl(p,c)
    out = []
    for key in KEYS10:
        x = whiten_in(key)
        p = x.copy() if p0_mode == "x0" else np.full(N, np.uint64(key),
                                                    dtype=np.uint64)
        for (a, b, c) in stages:
            xn = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(p, c)) & M64
            p, x = x, xn
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
    stages = []
    for _ in range(nstages):
        while True:
            a = int(rng.integers(1, 64)); b = int(rng.integers(1, 64))
            if a != b:
                break
        c = int(rng.integers(1, 64))
        stages.append((a, b, c))
    return stages

def run_arm(rng, name, form, nstages, n, p0_mode=None):
    results = []
    for t in range(n):
        if form == "dlin":
            stages = draw_rots(rng, nstages)
            (wz, wkey), S_list = eval_dlin(stages, p0_mode)
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
        results.append({"arm": name, "form": form, "p0": p0_mode,
                        "z": float(wz), "killkey": wkey, "keep": bool(keep),
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
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB27
    rng = np.random.default_rng(seed)
    t0 = time.time()
    wz, wkey = eval_frontier(B33C_SCHED)
    print("POSCTRL b33c: worst|z|=%.2f killkey=%#x -> %s" % (
        wz, wkey, "KEEP-OK" if wz < 10 else "FAIL"), flush=True)
    assert wz < 10, "POSITIVE-CONTROL FAILURE: b33c z=%.2f >= 10" % wz
    allr = [{"arm": "posctrl_b33c", "form": "frontier", "p0": None,
             "z": float(wz), "killkey": wkey, "keep": True,
             "stages": B33C_SCHED}]
    allr += run_arm(rng, "L5", "dlin", 5, 40, p0_mode="x0")
    allr += run_arm(rng, "L6", "dlin", 6, 40, p0_mode="x0")
    allr += run_arm(rng, "LK5", "dlin", 5, 40, p0_mode="key")
    allr += run_arm(rng, "LK6", "dlin", 6, 40, p0_mode="key")
    allr += run_arm(rng, "C5", "frontier", 5, 40)
    json.dump(allr, open("search_b27_results.json", "w"))
    draws = [r for r in allr if r["arm"] != "posctrl_b33c"]
    nk = sum(1 for r in draws if r["keep"])
    nkill = len(draws) - nk
    print("TOTAL: %d draws, %d keep, %d kill (%.1fs)" % (
        len(draws), nk, nkill, time.time() - t0), flush=True)
    assert nkill > 0, "POSITIVE-CONTROL FAILURE: 0 kills in %d draws" % len(draws)
    assert len(draws) == 200, "DRAW-COUNT MISMATCH: %d != 200" % len(draws)
    print("GATE CHECKS PASS: non-vacuous (%d kills), draw count exact." % nkill,
          flush=True)

if __name__ == "__main__":
    main()
