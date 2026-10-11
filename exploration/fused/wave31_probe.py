#!/usr/bin/env python3
"""Wave-31: NEW construction axes outside the `x ^= F(...)` DIFF-wall space.

Axis B (maj3-replacement): x := maj(ra,rb,rc) ^ rd  (pure replacement, no
  `x ^=` identity trail; maj nonlinear in ALL args unlike chi).
  Stage kind "majr". 5- and 6-stage probes.

Axis A (two-state cross-AND): state (x,y) updated simultaneously:
  x ^= (rotl(x,a) & rotl(y,b)) ^ rotl(y,c)
  y ^= (rotl(y,d) & rotl(x,e)) ^ rotl(x,f)
  out = x ^ rotl(y,17). 3-stage probes (each stage ~2x work of AND-stage).

Filter per try: marg2 PASS + DIFF proxy z<25@16 (same bars as wave-30;
recalibrate if a hit reaches real S1).
"""
import random, sys, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/rootcause")
from s2proxy_v2 import maxz_for_delta, all_deltas, M64, rotl
from marg_proxy2 import marg_proxy2
from wave24_proxy import proxy_24, apply_stage as apply_stage24

def _maj(p, q, r):
    return ((p & q) ^ (p & r) ^ (q & r)) & M64

def apply_stage31(x, st):
    k = st[0]
    if k == "majr":
        _, (a, b, c, d) = st
        return (_maj(rotl(x, a), rotl(x, b), rotl(x, c)) ^ rotl(x, d)) & M64
    return apply_stage24(x, st)

def proxy_31(stages, logN=16):
    def mix_fn(xs, K):
        x = (xs ^ K) & M64
        for st in stages:
            x = apply_stage31(x, st)
        return x
    worst_z, worst_d, worst_b = 0, None, None
    for d0 in all_deltas():
        z, b, n = maxz_for_delta(mix_fn, d0, logN)
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b

def mix_2state(xs, K, stages):
    x = (np.asarray(xs, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)) & M64
    y = (rotl(np.asarray(xs, dtype=np.uint64), 11) ^
         rotl(np.asarray(K, dtype=np.uint64), 29)) & M64
    for _, (a, b, c, d, e, f) in stages:
        xn = (x ^ (rotl(x, a) & rotl(y, b)) ^ rotl(y, c)) & M64
        yn = (y ^ (rotl(y, d) & rotl(x, e)) ^ rotl(x, f)) & M64
        x, y = xn, yn
    return (x ^ rotl(y, 17)) & M64

def proxy_2state(stages, logN=16):
    def mix_fn(xs, K):
        return mix_2state(xs, K, stages)
    worst_z, worst_d, worst_b = 0, None, None
    for d0 in all_deltas():
        z, b, n = maxz_for_delta(mix_fn, d0, logN)
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b

def marg_2state(stages):
    # marg_proxy2 is hardcoded to apply_stage; reimplement its cell loop here
    import math
    from screen_lib import KEYS, strided_distinct
    from screen_cal import perbit_zarray, logp_twosided_normal, fisher_logp
    from marg_proxy import _reduction_logps
    PB_BAR = math.log(0.01) - math.log(320) + 0.5
    RD_BAR = math.log(0.01) - math.log(20) + 0.5
    def mix_fn(xs, K):
        return mix_2state(xs, K, stages)
    worst = (float("inf"), None)
    Vsb = (np.uint64(1) << np.arange(64, dtype=np.uint64))
    for key in KEYS:
        K = np.full(64, np.uint64(key), dtype=np.uint64)
        zs = perbit_zarray(mix_fn(Vsb, K))
        lp = fisher_logp([logp_twosided_normal(z) for z in zs])
        m = lp - PB_BAR
        if m < worst[0]:
            worst = (m, f"PB SINGLE-BIT {key:#x} lp={lp:.1f}")
    n = 1 << 16
    for scen, vfn in (("SEQ", lambda: np.arange(n, dtype=np.uint64)),
                      ("PTR-j8", lambda: strided_distinct(0, 8, n))):
        V = vfn()
        for key in KEYS:
            K = np.full(n, np.uint64(key), dtype=np.uint64)
            lp = fisher_logp(_reduction_logps(mix_fn(V, K)))
            m = lp - RD_BAR
            if m < worst[0]:
                worst = (m, f"RD {scen} {key:#x} lp={lp:.1f}")
    return worst[0] > 0, worst

def search_majr(n, stages_n, seed):
    rng = random.Random(seed)
    hits = []
    t0 = time.time()
    tried = 0
    while tried < n:
        tried += 1
        stages = [("majr", tuple(rng.randint(1, 63) for _ in range(4)))
                  for _ in range(stages_n)]
        ok_m, worst = _marg31(stages)
        if not ok_m:
            if tried % 20 == 0:
                print(f"[majr-{stages_n}] TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
            continue
        m, _ = worst
        z, d, b = proxy_31(stages, logN=16)
        if z < 25:
            print(f"[majr-{stages_n}] TRY {tried}: HIT marg={m:+.1f} DIFFz={z:5.1f}", flush=True)
            hits.append((m, z, stages))
        elif tried % 20 == 0:
            print(f"[majr-{stages_n}] TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
    return hits

def _marg31(stages):
    import math
    from screen_lib import KEYS, strided_distinct
    from screen_cal import perbit_zarray, logp_twosided_normal, fisher_logp
    from marg_proxy import _reduction_logps
    PB_BAR = math.log(0.01) - math.log(320) + 0.5
    RD_BAR = math.log(0.01) - math.log(20) + 0.5
    def mix_fn(xs, K):
        x = (np.asarray(xs, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)) & M64
        for st in stages:
            x = apply_stage31(x, st)
        return x
    worst = (float("inf"), None)
    Vsb = (np.uint64(1) << np.arange(64, dtype=np.uint64))
    for key in KEYS:
        K = np.full(64, np.uint64(key), dtype=np.uint64)
        zs = perbit_zarray(mix_fn(Vsb, K))
        lp = fisher_logp([logp_twosided_normal(z) for z in zs])
        m = lp - PB_BAR
        if m < worst[0]:
            worst = (m, f"PB SINGLE-BIT {key:#x} lp={lp:.1f}")
    n = 1 << 16
    for scen, vfn in (("SEQ", lambda: np.arange(n, dtype=np.uint64)),
                      ("PTR-j8", lambda: strided_distinct(0, 8, n))):
        V = vfn()
        for key in KEYS:
            K = np.full(n, np.uint64(key), dtype=np.uint64)
            lp = fisher_logp(_reduction_logps(mix_fn(V, K)))
            m = lp - RD_BAR
            if m < worst[0]:
                worst = (m, f"RD {scen} {key:#x} lp={lp:.1f}")
    return worst[0] > 0, worst

def search_2state(n, seed):
    rng = random.Random(seed)
    hits = []
    t0 = time.time()
    tried = 0
    while tried < n:
        tried += 1
        stages = [("x2", tuple(rng.randint(1, 63) for _ in range(6)))
                  for _ in range(3)]
        ok_m, worst = marg_2state(stages)
        if not ok_m:
            if tried % 20 == 0:
                print(f"[x2] TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
            continue
        m, _ = worst
        z, d, b = proxy_2state(stages, logN=16)
        if z < 25:
            print(f"[x2] TRY {tried}: HIT marg={m:+.1f} DIFFz={z:5.1f}", flush=True)
            hits.append((m, z, stages))
        elif tried % 20 == 0:
            print(f"[x2] TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
    return hits

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "majr6"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB31
    if which == "majr6":
        hits = search_majr(n, 6, seed)
    elif which == "majr5":
        hits = search_majr(n, 5, seed)
    elif which == "x2":
        hits = search_2state(n, seed)
    else:
        raise ValueError(which)
    print(f"DONE {which}: {len(hits)} hits", flush=True)
    for m, z, stages in sorted(hits, reverse=True)[:5]:
        print(f"  HIT marg={m:+.1f} DIFFz={z:.1f} stages={stages}", flush=True)
