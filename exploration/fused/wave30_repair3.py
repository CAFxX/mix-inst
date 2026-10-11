#!/usr/bin/env python3
"""Wave-30 axis B4: fz27_h repair with BOTH proxies (v3).

v3 lessons:
- v1 (2-cell marginal): fz30_d passed v1, failed real marginal on other cells.
- v2 (marg2 only): fz30_j (20.0u) passed marg2, failed real S1 DIFF (rej=9);
  the DIFF proxy (z=35.0@16) would have filtered it. Dropping the DIFF proxy
  from the loop was a mistake.
v3 loop per try: marg2 MUST PASS (~6s) AND DIFF proxy z<25@16 (~10s).
Rank hits by marg2 margin. Top -> build + bit-exact + S0; S0<=20.1 -> s1.
"""
import random, sys, time
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from marg_proxy2 import marg_proxy2
from wave24_proxy import proxy_24

BASE = [("t3", (1, 7, 13, 29)),
        ("t3", (3, 11, 19, 37)),
        ("and", (5, 15, 21)),
        ("and", (9, 23, 43))]
CHIFIX = ("chi", (29, 17, 33, 51))

def perturb(rng):
    out = []
    for kind, rots in BASE:
        nr = [min(63, max(1, r + rng.randint(-2, 2))) for r in rots]
        out.append((kind, tuple(nr)))
    return out

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB34
    rng = random.Random(seed)
    print("filters: marg2 PASS + DIFFproxy z<25@16", flush=True)
    hits = []
    tried = 0
    t_start = time.time()
    while tried < n:
        body = perturb(rng)
        if body == BASE:
            continue
        tried += 1
        stages = body + [CHIFIX]
        ok_m, worst = marg_proxy2(stages, verbose=False)
        if not ok_m:
            if tried % 50 == 0:
                print(f"TRY {tried}: ... ({len(hits)} hits, {time.time()-t_start:.0f}s)", flush=True)
            continue
        m, _ = worst
        z, d, b = proxy_24(stages, logN=16)
        if z < 25:
            print(f"TRY {tried}: HIT marg={m:+.1f} DIFFz={z:5.1f} body={[r for _, r in body]}",
                  flush=True)
            hits.append((m, z, body))
        elif tried % 50 == 0:
            print(f"TRY {tried}: ... ({len(hits)} hits, {time.time()-t_start:.0f}s)", flush=True)
    print(f"DONE {tried} tries, {len(hits)} hits, {time.time()-t_start:.0f}s", flush=True)
    for m, z, body in sorted(hits, reverse=True)[:10]:
        print(f"  HIT marg={m:+.1f} DIFFz={z:.1f} body={[r for _, r in body]}", flush=True)

if __name__ == "__main__":
    main()
