#!/usr/bin/env python3
"""Wave-30 axis B2: chi-schedule neighborhood repair of fz27_h.

fz27_h's 19.9u came from chi (29,17,33,51); its marginal kill is on that
schedule. Search chi schedules in the +-2 neighborhood (body fixed to the
fz24_o body), filtered by the calibrated marginal proxy (MUST PASS) and the
DIFF proxy (z<25@16, baseline-calibrated). Hits -> S0; any <=20.1u -> s1.
"""
import random, sys, time
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from marg_proxy import marg_proxy
from wave24_proxy import proxy_24

BODY = [("t3", (1, 7, 13, 29)),
        ("t3", (3, 11, 19, 37)),
        ("and", (5, 15, 21)),
        ("and", (9, 23, 43))]
BASE_CHI = (29, 17, 33, 51)

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xC230
    rng = random.Random(seed)
    z0, _, _ = proxy_24(BODY + [("chi", BASE_CHI)], logN=16)
    print(f"BASELINE fz27_h chi{BASE_CHI}: DIFFproxy z={z0:.1f}@16", flush=True)
    seen = {BASE_CHI}
    hits = []
    tried = 0
    t_start = time.time()
    while tried < n:
        s = tuple(min(63, max(1, b + rng.randint(-2, 2))) for b in BASE_CHI)
        if s in seen:
            continue
        seen.add(s)
        tried += 1
        stages = BODY + [("chi", s)]
        ok_m, pb, rd = marg_proxy(stages, 18, verbose=False)
        if not ok_m:
            continue
        z, d, b = proxy_24(stages, logN=16)
        stat = "HIT" if z < 25 else "ok"
        print(f"TRY {tried}: chi{s} marg PASS pb={pb:.1f} rd={rd:.1f} DIFFz={z:6.1f} {stat}",
              flush=True)
        if z < 25:
            hits.append((z, s, pb, rd))
    print(f"DONE {tried} tries, {len(hits)} hits, {time.time()-t_start:.0f}s", flush=True)
    for z, s, pb, rd in sorted(hits)[:10]:
        print(f"  HIT z={z:.1f} chi{s} pb={pb:.1f} rd={rd:.1f}", flush=True)

if __name__ == "__main__":
    main()
