#!/usr/bin/env python3
"""Wave-30 axis B: fz27_h (19.9u, marginal-killed) repair co-design search.

Fixed: chi final (29,17,33,51) — the schedule that bought the 19.9u S0.
Vary: all 14 body rotations, each -2..+2 (clamped 1..63).
Screen per try: (1) targeted marginal proxy (MUST PASS, ~1s);
(2) DIFF proxy logN=16, bar z<25: fz27_h baseline (real-S1 DIFF-clean) measures
19.6@16, so the bar is "no DIFF regression vs baseline" (the proxy is
conservative vs the real S1 DIFF family; a z<12 bar would kill the baseline
itself). Hits ranked by DIFF z; top -> S0; any <=20.1u -> real s1_screen -> S2.
"""
import random, sys, time
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from marg_proxy import marg_proxy
from wave24_proxy import proxy_24

BASE = [("t3", (1, 7, 13, 29)),
        ("t3", (3, 11, 19, 37)),
        ("and", (5, 15, 21)),
        ("and", (9, 23, 43))]
CHIFIX = ("chi", (29, 17, 33, 51))

def perturb(rng):
    out = []
    for kind, rots in BASE:
        nr = []
        for r in rots:
            d = rng.randint(-2, 2)
            v = r + d
            if v < 1: v = 1
            if v > 63: v = 63
            nr.append(v)
        out.append((kind, tuple(nr)))
    return out

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xF230
    rng = random.Random(seed)
    z0, d0, b0 = proxy_24(BASE + [CHIFIX], logN=16)
    print(f"BASELINE fz27_h: DIFFproxy z={z0:.1f}@16 (bar z<25: baseline-calibrated)", flush=True)
    hits = []
    tried = 0
    t_start = time.time()
    while tried < n:
        body = perturb(rng)
        if body == BASE:
            continue
        tried += 1
        stages = body + [CHIFIX]
        ok_m, pb, rd = marg_proxy(stages, 18, verbose=False)
        if not ok_m:
            continue
        z, d, b = proxy_24(stages, logN=16)
        stat = "HIT" if z < 25 else "ok"
        print(f"TRY {tried}: marg PASS pb={pb:.1f} rd={rd:.1f} DIFFz={z:6.1f} {stat} "
              f"body={[r for _, r in body]}", flush=True)
        if z < 25:
            hits.append((z, body, pb, rd))
    print(f"DONE {tried} tries, {len(hits)} hits, {time.time()-t_start:.0f}s", flush=True)
    for z, body, pb, rd in sorted(hits)[:10]:
        print(f"  HIT z={z:.1f} pb={pb:.1f} rd={rd:.1f} body={[r for _, r in body]}", flush=True)

if __name__ == "__main__":
    main()
