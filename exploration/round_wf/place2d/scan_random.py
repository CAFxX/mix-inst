#!/usr/bin/env python3
"""Scan random O34-valid P-boxes for (S, W2d). Checkpoint to random_scan.json."""
import json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place2d import lane_graph, placeability, index_metrics
import place2d as P2
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "random_scan.json")
def random_valid(rng):
    for _ in range(50000):
        c = list(range(64)); rng.shuffle(c)
        P = [0]*64
        for k in range(64): P[c[k]] = c[(k+1)%64]
        if P2._o34_ok(P): return P, c
    return None, None
def main():
    n = int(sys.argv[1]) if len(sys.argv)>1 else 200
    seed0 = int(sys.argv[2]) if len(sys.argv)>2 else 100
    rng = random.Random(seed0)
    res = []
    t0=time.time()
    for i in range(n):
        P, c = random_valid(rng)
        m = index_metrics(P)
        w2d = placeability(P, seeds=(1,), iters=8000)
        res.append({"S": m["S"], "W1d": m["W1d"], "W2d": w2d, "tour": c})
        if i % 25 == 0: print(f"[{i}/{n}] S={m['S']} W2d={w2d} ({time.time()-t0:.0f}s)", flush=True)
    # pareto: max S, min W2d
    res.sort(key=lambda r: (r["W2d"], -r["S"]))
    json.dump(res, open(OUT, "w"))
    print(f"done {n} in {time.time()-t0:.0f}s -> {OUT}")
    print("best W2d at S>=340:")
    f = sorted([r for r in res if r["S"]>=340], key=lambda r: r["W2d"])[:8]
    for e in f: print(f"  S={e['S']} W2d={e['W2d']} W1d={e['W1d']}")
    print("best W2d at S>=350:")
    f = sorted([r for r in res if r["S"]>=350], key=lambda r: r["W2d"])[:8]
    for e in f: print(f"  S={e['S']} W2d={e['W2d']} W1d={e['W1d']}")
if __name__ == "__main__": main()
