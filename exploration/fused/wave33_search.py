#!/usr/bin/env python3
"""Wave-33 search: [t3,and,and,and,chi] rotation search.

Rationale: 5-stage needs t3/chi for S1/DIFF but t3's extra linear XOR hurts
S3. One t3 (not two) may balance: enough DIFF strength, less linear structure.
Filter: marg2 PASS + DIFF z<25@16. Then S0/S1/S3-16MB.
"""
import random, sys, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/rootcause")
from s2proxy_v2 import maxz_for_delta, all_deltas, M64
from screen_lib import KEYS, strided_distinct
from screen_cal import perbit_zarray, logp_twosided_normal, fisher_logp
from marg_proxy import _reduction_logps
import math

def rotl_np(x, r):
    r &= 63
    return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & np.uint64(M64) if r else x

def make_mix(stages):
    def mix_fn(xs, K):
        x = (np.asarray(xs, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)) & np.uint64(M64)
        for k, rots in stages:
            if k == "t3":
                a,b,c,d = rots
                x = (x ^ (rotl_np(x,a) & rotl_np(x,b)) ^ rotl_np(x,c) ^ rotl_np(x,d)) & np.uint64(M64)
            elif k == "and":
                a,b,c = rots
                x = (x ^ (rotl_np(x,a) & rotl_np(x,b)) ^ rotl_np(x,c)) & np.uint64(M64)
            elif k == "chi":
                a,b,c,d = rots
                x = (x ^ ((~rotl_np(x,a)) & rotl_np(x,b)) ^ rotl_np(x,c) ^ rotl_np(x,d)) & np.uint64(M64)
        return x
    return mix_fn

def marg(stages):
    mix_fn = make_mix(stages)
    PB_BAR = math.log(0.01) - math.log(320) + 0.5
    RD_BAR = math.log(0.01) - math.log(20) + 0.5
    worst = (float("inf"), None)
    Vsb = (np.uint64(1) << np.arange(64, dtype=np.uint64))
    for key in KEYS:
        K = np.full(64, np.uint64(key), dtype=np.uint64)
        zs = perbit_zarray(mix_fn(Vsb, K))
        lp = fisher_logp([logp_twosided_normal(z) for z in zs])
        m = lp - PB_BAR
        if m < worst[0]: worst = (m, "PB")
    n = 1 << 16
    for scen, vfn in (("SEQ", lambda: np.arange(n, dtype=np.uint64)),
                      ("PTR-j8", lambda: strided_distinct(0, 8, n))):
        V = vfn()
        for key in KEYS:
            K = np.full(n, np.uint64(key), dtype=np.uint64)
            lp = fisher_logp(_reduction_logps(mix_fn(V, K)))
            m = lp - RD_BAR
            if m < worst[0]: worst = (m, f"RD {scen}")
    return worst[0] > 0, worst

def diffp(stages):
    mix_fn = make_mix(stages)
    wz = 0
    for d0 in all_deltas():
        z, b, n = maxz_for_delta(mix_fn, d0, 16)
        if z > wz: wz = z
    return wz

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xC33
    rng = random.Random(seed)
    hits = []
    t0 = time.time()
    for tried in range(1, n+1):
        stages = [
            ("t3", tuple(rng.randint(1,63) for _ in range(4))),
            ("and", tuple(rng.randint(1,63) for _ in range(3))),
            ("and", tuple(rng.randint(1,63) for _ in range(3))),
            ("and", tuple(rng.randint(1,63) for _ in range(3))),
            ("chi", (29,17,33,51)),
        ]
        okm, w = marg(stages)
        if not okm:
            if tried % 10 == 0:
                print(f"TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
            continue
        m = w[0]
        z = diffp(stages)
        if z < 25:
            print(f"TRY {tried}: HIT marg={m:+.1f} DIFFz={z:.1f}", flush=True)
            hits.append((m, z, stages))
        elif tried % 10 == 0:
            print(f"TRY {tried}: ... ({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
    print(f"DONE: {len(hits)} hits", flush=True)
    for m, z, stages in sorted(hits, reverse=True)[:5]:
        print(f"  HIT marg={m:+.1f} DIFFz={z:.1f} stages={stages}", flush=True)

if __name__ == "__main__":
    main()
