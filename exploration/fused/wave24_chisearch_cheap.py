#!/usr/bin/env python3
"""Wave-24e: chi-final schedule search for the CHEAP prefix.

Prefix: [t3(1,7,13,29), and(3,11,17), and(5,15,25), and(9,21,43)]
(~14.55u + chi ~3.95u = ~18.5u est, well under 20.1u IF S1-clean).
fz24_o [t3,t3,and,and,CHI] is S1-clean but 20.3u (0.2u over).
"""
import random, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave24_proxy import proxy_24

PREFIX = [("t3", (1, 7, 13, 29)),
          ("and", (3, 11, 17)),
          ("and", (5, 15, 25)),
          ("and", (9, 21, 43))]

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
    seed = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0xC4EA9
    rng = random.Random(seed)
    best = []
    tried = 0
    while tried < n:
        s = tuple(rng.randint(5, 59) for _ in range(4))
        if not ok_sched(s):
            continue
        tried += 1
        z, d, b = proxy_24(PREFIX + [("chi", s)], logN=16)
        print(f"TRY {tried}: chi{s} z={z:6.1f} (d0={d:#x})", flush=True)
        best.append((z, s))
    best.sort()
    print("TOP5:", [(f"{z:.1f}", s) for z, s in best[:5]], flush=True)

if __name__ == "__main__":
    main()
