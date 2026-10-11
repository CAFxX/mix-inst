"""Bigger hetero search: 600 designs, 12 deltas, N=2^18. Two-stage filter."""
import numpy as np, json, sys, time
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
from s2proxy import s2proxy, cost_est
from search5 import rand_design

DELTAS12 = [1<<i for i in (0, 5, 11, 17, 23, 29, 35, 41, 47, 53, 59, 63)]
DELTAS25 = [1<<i for i in range(0,64,3)] + [0xFF, 1<<0|1<<32, 0xAAAAAAAAAAAAAAAA]

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    rng = np.random.default_rng(seed)
    cands = []
    t0 = time.time()
    for i in range(count):
        n_t3 = int(rng.integers(1, 4))
        st = rand_design(rng, n_t3)
        if cost_est(st) >= 20.1:
            continue
        z, d, b = s2proxy(st, deltas=DELTAS12, n=1<<18)
        if z < 7.0:
            cands.append((z, st))
            print(f"prefilter z={z:.1f} {st}", flush=True)
    print(f"--- prefilter: {len(cands)}/{count} in {time.time()-t0:.0f}s ---", flush=True)
    # strict verify
    verified = []
    for (z, st) in sorted(cands)[:15]:
        z2, d2, b2 = s2proxy(st, deltas=DELTAS25, n=1<<20)
        verified.append((z2, st))
        print(f"strict z={z2:.1f} (was {z:.1f}) {st}", flush=True)
    verified.sort()
    top = [(z, [list(s) for s in st]) for (z, st) in verified[:10]]
    with open('/home/hatch/workspace/mix/exploration/adder_lat/rootcause/candidates5b.json', 'w') as f:
        json.dump(top, f, indent=1)
    print("saved candidates5b.json")

if __name__ == '__main__':
    main()
