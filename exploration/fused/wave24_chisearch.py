#!/usr/bin/env python3
"""Wave-24c: random schedule search for the CHI final stage.

Fixed prefix: [t3(1,7,13,29), t3(3,11,19,37), and(5,15,21), and(9,23,43)]
(fz23_b backbone). Search (a,b,c,d) for final x ^= (~ra&rb)^rc^rd.
fz24_c baseline (13,27,41,7): proxy z=22.1. Target: z < 12.
Danger-zone-free: rots in 5..59, pairwise distance >= 4, avoid multiples.
"""
import random, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave24_proxy import proxy_24

PREFIX = [("t3", (1, 7, 13, 29)),
          ("t3", (3, 11, 19, 37)),
          ("and", (5, 15, 21)),
          ("and", (9, 23, 43))]

def ok_sched(s):
    if any(v < 5 or v > 59 for v in s):
        return False
    for i in range(4):
        for j in range(i + 1, 4):
            if abs(s[i] - s[j]) < 4:
                return False
    return True

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xC41
    rng = random.Random(seed)
    # baseline first
    z, d, b = proxy_24(PREFIX + [("chi", (13, 27, 41, 7))], logN=16)
    print(f"BASELINE chi(13,27,41,7): z={z:.1f}", flush=True)
    best = []
    tried = 0
    while tried < n:
        s = tuple(rng.randint(5, 59) for _ in range(4))
        if not ok_sched(s):
            continue
        tried += 1
        stages = PREFIX + [("chi", s)]
        z, d, b = proxy_24(stages, logN=16)
        print(f"TRY {tried}: chi{s} z={z:6.1f} (d0={d:#x})", flush=True)
        best.append((z, s))
    best.sort()
    print("TOP5:", [(f"{z:.1f}", s) for z, s in best[:5]], flush=True)

if __name__ == "__main__":
    main()
