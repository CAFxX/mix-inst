#!/usr/bin/env python3
"""Batch-26: delayed-operand AND cascade ("skip hybrid") screen (track 5).

Co-designed 2026-10-11 (supVI) from the mechanism lessons:
- lin term double duty (b23/b24 VALID kills): sparse fixed-point breaking +
  per-stage linear diffusion. The lin term STAYS (^rotl(x,c)).
- XOR-tree cost disease: viable shape = EXACTLY 3 XOR terms/stage
  (x, AND-term, lin-term) -> ~3.3u/stage, same gate shape as frontier.
- 4/5-stage quality wall for all STAGE-LOCAL AND forms (b22 arm A 0/200
  min z=179.5; t6 controls). The delayed operand makes the form NON-stage-local,
  so the wall evidence does not transfer -- must test, not assume.

Form: state (x, p); p_{i+1} = x_i (pure delay -- a wire in unrolled
combinational RTL, ZERO gate cost):
    x' = x ^ (rotl(p,a) & rotl(x,b)) ^ rotl(x,c)
Arms:
  D5/D6: p0 = x0 (pure delay line), 5/6 stages (~16.5u/~19.8u est).
  K5:    p0 = key (the 2nd input rs2 made STRUCTURAL), 5 stages.
  C5:    frontier-form 5st negative control (expect 0 KEEP; the known-dead
         form that must KILL -- reproduces batch-22 control min z=179.5).

De-dup (grep-verified 2026-10-11): no delayed/two-time-step form in any
hybrid batch; XFC's u is a computed nonlinear chain (different mechanism);
track-8 owns the two-lane two-state axis; no batch ever used the key as a
stage operand (key only via whiten_in/whiten_out).

Mechanism story:
- Fixed-point breaking: stage-0 (D5/D6) IS the frontier form (p0=x0); the
  sparse-corner story is no worse than frontier, lin duty (i) intact.
- b22's self-correlation disease avoided: the AND mask bit p[i-a] comes from
  the PREVIOUS stage's state, decorrelated from the masked bit x[i] (b22's
  mask shared x[i] itself -> maximally correlated -> 8500x worse).
- Dual-timescale diffusion: current-state lin (fast) + delayed AND operand
  (slow -- differences from the previous stage re-injected masked by current
  state).
- a!=b enforced (het6a lesson: same-state a==b stages go linear and muddy the
  axis story). Cross-state a==b would be meaningful, but the uniform
  constraint keeps the mechanism story clean.

Triage = EXACT S1 DIFF via lin_diff.diff_cell_logps, all 10 keys, N=2^18,
KEEP bar max|z|<10. KEEP survivors get the LIN proxy (lin_cell_logp on keys
0x0 / 0xFF..F, bar D<=64 -- the het6a lesson).

Positive controls:
  (a) b33c exact schedule through the frontier pipeline -> KEEP z~3.3
      (pipeline validation; FAILS LOUD if not KEEP).
  (b) C5 frontier-5st -> expect 0 KEEP (known-dead form must KILL).
Fail-loud: assert draws == 160; assert kills > 0 (non-vacuous).
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

def eval_dly(stages, p0_mode):
    # stages[i] = (a,b,c); p0 = x0 ("x0") or key ("key"); p_{i+1} = x_i
    out = []
    for key in KEYS10:
        x = whiten_in(key)
        p = x.copy() if p0_mode == "x0" else np.full(N, np.uint64(key),
                                                    dtype=np.uint64)
        for (a, b, c) in stages:
            xn = (x ^ (rotl(p, a) & rotl(x, b)) ^ rotl(x, c)) & M64
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
    # a != b enforced (het6a linear-stage lesson); c free (no degeneracy)
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
        if form == "dly":
            stages = draw_rots(rng, nstages)
            (wz, wkey), S_list = eval_dly(stages, p0_mode)
        else:  # frontier control
            stages = [tuple(int(rng.integers(1, 64)) for _ in range(3))
                      for _ in range(nstages)]
            wz, wkey = eval_frontier(stages)
            S_list = None
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
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB26
    rng = np.random.default_rng(seed)
    t0 = time.time()
    wz, wkey = eval_frontier(B33C_SCHED)
    print("POSCTRL b33c: worst|z|=%.2f killkey=%#x -> %s" % (
        wz, wkey, "KEEP-OK" if wz < 10 else "FAIL"), flush=True)
    assert wz < 10, "POSITIVE-CONTROL FAILURE: b33c z=%.2f >= 10" % wz
    allr = [{"arm": "posctrl_b33c", "form": "frontier", "p0": None,
             "z": float(wz), "killkey": wkey, "keep": True,
             "stages": B33C_SCHED}]
    allr += run_arm(rng, "D5", "dly", 5, 40, p0_mode="x0")
    allr += run_arm(rng, "D6", "dly", 6, 40, p0_mode="x0")
    allr += run_arm(rng, "K5", "dly", 5, 40, p0_mode="key")
    allr += run_arm(rng, "C5", "frontier", 5, 40)
    json.dump(allr, open("search_b26_results.json", "w"))
    draws = [r for r in allr if r["arm"] != "posctrl_b33c"]
    nk = sum(1 for r in draws if r["keep"])
    nkill = len(draws) - nk
    print("TOTAL: %d draws, %d keep, %d kill (%.1fs)" % (
        len(draws), nk, nkill, time.time() - t0), flush=True)
    assert nkill > 0, "POSITIVE-CONTROL FAILURE: 0 kills in %d draws" % len(draws)
    assert len(draws) == 160, "DRAW-COUNT MISMATCH: %d != 160" % len(draws)
    print("GATE CHECKS PASS: non-vacuous (%d kills), draw count exact." % nkill,
          flush=True)

if __name__ == "__main__":
    main()
