#!/usr/bin/env python3
"""Wave-30 axis B3: fz27_h repair co-design with the WIDENED marginal proxy.

v1 searches (2-cell proxy) were inadequate: fz30_d passed v1 but failed the
real screen on different cells (whack-a-mole). This search uses marg_proxy2
(10 PB cells + 20 RD cells, calibrated: fz24_o PASS / fz27_h,fz30_d FLAG).

Search: perturb the 14 fz27_h body rotations +-2 (chi fixed (29,17,33,51)).
Filter: marg2 PASS only (~6s/try). Rank hits by worst-cell margin (higher
better). Top hits -> build + bit-exact + S0; S0 <= 20.1 -> real s1_screen
(which runs LIN/DIFF first, so no separate DIFF proxy needed in the loop).
"""
import random, sys, time
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from marg_proxy2 import marg_proxy2

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
            v = min(63, max(1, r + rng.randint(-2, 2)))
            nr.append(v)
        out.append((kind, tuple(nr)))
    return out

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xB30
    rng = random.Random(seed)
    print("BASELINE fz27_h: marg2 FLAG known (margin -31.9)", flush=True)
    hits = []
    tried = 0
    t_start = time.time()
    while tried < n:
        body = perturb(rng)
        if body == BASE:
            continue
        tried += 1
        stages = body + [CHIFIX]
        ok, worst = marg_proxy2(stages, verbose=False)
        m, cell = worst
        if ok:
            print(f"TRY {tried}: HIT margin={m:+.1f} body={[r for _, r in body]}", flush=True)
            hits.append((m, body))
        elif tried % 25 == 0:
            print(f"TRY {tried}: ... ({len(hits)} hits, {time.time()-t_start:.0f}s)", flush=True)
    print(f"DONE {tried} tries, {len(hits)} hits, {time.time()-t_start:.0f}s", flush=True)
    for m, body in sorted(hits, reverse=True)[:10]:
        print(f"  HIT margin={m:+.1f} body={[r for _, r in body]}", flush=True)

if __name__ == "__main__":
    main()
