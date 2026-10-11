#!/usr/bin/env python3
"""Wave-31b: FIXED maj3-replacement.

Wave-31 diagnosis (2026-10-10): replacement form `x := maj(ra,rb,rc) ^ rd`
with d NOT in {a,b,c} has a DETERMINISTIC 1-bit differential trail:
input bit p -> output bit p+d with prob 1, because at out-bit p+d the maj
term's inputs (bits p+d-a, p+d-b, p+d-c) never include p, so Dmaj=0 and
Dout = 0 ^ 1 = 1 always. Composes over stages -> z=256.

Fix (overlap constraint): the linear rotation MUST be one of the maj
input rotations. Stage kind "majr2" (a,b,c): x := maj(ra,rb,rc) ^ ra.
Then at out-bit p+a, Dmaj is probabilistic (ra sees the delta), so
Dout = prob ^ 1 = probabilistic. No deterministic trail.

Search: 6-stage majr2, random (a,b,c), filter marg2 PASS + DIFF z<25@16.
"""
import random, sys, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/rootcause")
from s2proxy_v2 import maxz_for_delta, all_deltas, M64, rotl
from wave31_probe import _marg31, _maj

def apply_majr2(x, st):
    _, (a, b, c) = st
    return (_maj(rotl(x, a), rotl(x, b), rotl(x, c)) ^ rotl(x, a)) & M64

def proxy_majr2(stages, logN=16):
    def mix_fn(xs, K):
        x = (np.asarray(xs, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)) & M64
        for st in stages:
            x = apply_majr2(x, st)
        return x
    worst_z, worst_d, worst_b = 0, None, None
    for d0 in all_deltas():
        z, b, n = maxz_for_delta(mix_fn, d0, logN)
        if z > worst_z:
            worst_z, worst_d, worst_b = z, d0, b
    return worst_z, worst_d, worst_b

def _marg_majr2(stages):
    import math
    from screen_lib import KEYS, strided_distinct
    from screen_cal import perbit_zarray, logp_twosided_normal, fisher_logp
    from marg_proxy import _reduction_logps
    PB_BAR = math.log(0.01) - math.log(320) + 0.5
    RD_BAR = math.log(0.01) - math.log(20) + 0.5
    def mix_fn(xs, K):
        x = (np.asarray(xs, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)) & M64
        for st in stages:
            x = apply_majr2(x, st)
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

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB312
    rng = random.Random(seed)
    hits = []
    t0 = time.time()
    tried = 0
    while tried < n:
        tried += 1
        stages = [("majr2", tuple(rng.randint(1, 63) for _ in range(3)))
                  for _ in range(6)]
        ok_m, worst = _marg_majr2(stages)
        if not ok_m:
            if tried % 20 == 0:
                print(f"TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
            continue
        m, _ = worst
        z, d, b = proxy_majr2(stages, logN=16)
        if z < 25:
            print(f"TRY {tried}: HIT marg={m:+.1f} DIFFz={z:5.1f} "
                  f"stages={[s[1] for s in stages]}", flush=True)
            hits.append((m, z, stages))
        elif tried % 20 == 0:
            print(f"TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
    print(f"DONE: {len(hits)} hits", flush=True)
    for m, z, stages in sorted(hits, reverse=True)[:5]:
        print(f"  HIT marg={m:+.1f} DIFFz={z:.1f}", flush=True)

if __name__ == "__main__":
    main()
