#!/usr/bin/env python3
"""Wave-34: co-designed two-state fused screen.

Failure analysis driving the design:
- t6_lane3b (3+3 dual-lane, 15.0u S0) S1-KILLED: LIN rej=10, DIFF z=458502.
  Construction: bn = F(b) ^ rotl(a,s) -- ONE-WAY LINEAR cross-feed, and
  b0 = rotl(k,29) is v-INDEPENDENT. The linear a->b injection is a
  deterministic differential path the ANDs cannot mask.
- Axis A two-state (wave-31): xn = x ^ (rotl(x,a)&rotl(y,b)) ^ rotl(y,c)
  -- same disease: pure-LINEAR cross term rotl(y,c)/rotl(x,f); z=90.5 bias.

Co-design rule: EVERY cross-lane influence passes through an AND.
No linear cross-lane term anywhere. Both lanes v-dependent from init.

Variants (per stage):
  V0 control = Axis A as-was: xn = x ^ (xa&yb) ^ yc ; yn = y ^ (yd&xe) ^ xf
  V1 no-linear-cross:          xn = x ^ (xa&yb)      ; yn = y ^ (yd&xe)
  V2 indep+cross:              xn = x ^ (xa&xb) ^ (xc&yd) ; yn = y ^ (ye&yf) ^ (xg&yh)
       (each lane keeps its own working AND-cascade term; cross-talk is AND-only)
  V3 = V1 with 4 stages instead of 3.

Pipeline per candidate: marg proxy (marg_2state-style) -> DIFF z@logN=16, keep z<25.
"""
import random, sys, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/rootcause")
from s2proxy_v2 import maxz_for_delta, all_deltas, M64, rotl

def _distinct_pair(rng):
    a = rng.randint(1, 63)
    b = rng.randint(1, 63)
    while b == a:
        b = rng.randint(1, 63)
    return a, b

def make_stages(variant, nstages, rng):
    stages = []
    for _ in range(nstages):
        if variant in ("V0", "V1", "V3"):
            a, b = _distinct_pair(rng)
            c = rng.randint(1, 63)
            d, e = _distinct_pair(rng)
            f = rng.randint(1, 63)
            stages.append((a, b, c, d, e, f))
        else:  # V2: 8 rots
            a, b = _distinct_pair(rng)
            c, d = _distinct_pair(rng)
            e, f = _distinct_pair(rng)
            g, h = _distinct_pair(rng)
            stages.append((a, b, c, d, e, f, g, h))
    return stages

def make_mix(variant, stages):
    def mix_fn(xs, K):
        xs = np.asarray(xs, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        x = (xs ^ K) & M64
        y = (rotl(xs, 11) ^ rotl(K, 29)) & M64
        for st in stages:
            if variant == "V0":
                a, b, c, d, e, f = st
                xn = (x ^ (rotl(x, a) & rotl(y, b)) ^ rotl(y, c)) & M64
                yn = (y ^ (rotl(y, d) & rotl(x, e)) ^ rotl(x, f)) & M64
            elif variant in ("V1", "V3"):
                a, b, c, d, e, f = st
                xn = (x ^ (rotl(x, a) & rotl(y, b))) & M64
                yn = (y ^ (rotl(y, d) & rotl(x, e))) & M64
            else:  # V2
                a, b, c, d, e, f, g, h = st
                xn = (x ^ (rotl(x, a) & rotl(x, b)) ^ (rotl(x, c) & rotl(y, d))) & M64
                yn = (y ^ (rotl(y, e) & rotl(y, f)) ^ (rotl(x, g) & rotl(y, h))) & M64
            x, y = xn, yn
        return (x ^ rotl(y, 17)) & M64
    return mix_fn

def marg_pass(mix_fn):
    import math
    from screen_lib import KEYS, strided_distinct
    from screen_cal import perbit_zarray, logp_twosided_normal, fisher_logp
    from marg_proxy import _reduction_logps
    PB_BAR = math.log(0.01) - math.log(320) + 0.5
    RD_BAR = math.log(0.01) - math.log(20) + 0.5
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

def diff_z(mix_fn, logN=16):
    worst_z, worst_d, worst_b = 0, None, None
    for d0 in all_deltas():
        z, b, n = maxz_for_delta(mix_fn, d0, logN)
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b

def screen_variant(variant, nstages, n, seed):
    rng = random.Random(seed)
    hits = []
    t0 = time.time()
    for tried in range(1, n + 1):
        stages = make_stages(variant, nstages, rng)
        mix_fn = make_mix(variant, stages)
        ok_m, worst = marg_pass(mix_fn)
        if not ok_m:
            if tried % 10 == 0:
                print(f"[{variant}] TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
            continue
        m, _ = worst
        z, d, b = diff_z(mix_fn, logN=16)
        if z < 25:
            print(f"[{variant}] TRY {tried}: HIT marg={m:+.1f} DIFFz={z:5.1f} d={d:#x}", flush=True)
            hits.append((m, z, stages))
        elif tried % 10 == 0:
            print(f"[{variant}] TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
    print(f"DONE {variant}: {len(hits)}/{n} hits", flush=True)
    for m, z, stages in sorted(hits, reverse=True)[:5]:
        print(f"  HIT marg={m:+.1f} DIFFz={z:.1f} stages={stages}", flush=True)
    return hits

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x34
    all_hits = {}
    for variant, nstages, vs in [("V0", 3, 0xA0), ("V1", 3, 0xB1),
                                 ("V2", 3, 0xC2), ("V3", 4, 0xD3)]:
        all_hits[variant] = screen_variant(variant, nstages, n, seed ^ vs)
    print("WAVE34 SUMMARY", flush=True)
    for v, h in all_hits.items():
        print(f"  {v}: {len(h)} hits", flush=True)
