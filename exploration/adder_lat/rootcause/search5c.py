"""Focused hetero search: fixed patterns, many samples, incremental save, unbuffered.
Patterns: [t3,and,and,and,t3] and 1xt3+4and variants."""
import numpy as np, json, sys, time, os
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
from s2proxy import s2proxy, cost_est

DELTAS = [1<<i for i in (0, 5, 11, 17, 23, 29, 35, 41, 47, 53, 59, 63)]
OUT = '/home/hatch/workspace/mix/exploration/adder_lat/rootcause/candidates5c.json'

def rand_rot(rng, avoid=()):
    while True:
        r = int(rng.integers(1, 64))
        if r not in avoid:
            return r

def rand_and(rng):
    a = rand_rot(rng); b = rand_rot(rng, (a,)); c = rand_rot(rng, (a,b))
    return ('and', a, b, c)

def rand_t3(rng):
    a = rand_rot(rng); b = rand_rot(rng, (a,))
    c = rand_rot(rng, (a,b)); e = rand_rot(rng, (a,b,c))
    return ('t3', a, b, c, e)

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    rng = np.random.default_rng(seed)
    hits = []
    if os.path.exists(OUT):
        hits = json.load(open(OUT))
    t0 = time.time()
    for i in range(count):
        # pattern A: [t3,and,and,and,t3] (best hit pattern)
        # pattern B: 1 t3 at random pos + 4 and
        if rng.random() < 0.5:
            st = [rand_t3(rng), rand_and(rng), rand_and(rng), rand_and(rng), rand_t3(rng)]
        else:
            pos = int(rng.integers(0, 5))
            st = [rand_and(rng) for _ in range(5)]
            st[pos] = rand_t3(rng)
        z, d, b = s2proxy(st, deltas=DELTAS, n=1<<18)
        if z < 8.0:
            hits.append((z, [list(s) for s in st]))
            print(f"HIT z={z:.1f} {st}", flush=True)
        if (i+1) % 50 == 0:
            hits.sort()
            json.dump(hits[:30], open(OUT, 'w'), indent=1)
            print(f"  ... {i+1}/{count}, {time.time()-t0:.0f}s, {len(hits)} hits", flush=True)
    hits.sort()
    json.dump(hits[:30], open(OUT, 'w'), indent=1)
    print(f"done: {len(hits)} hits / {count}")
    for (z, st) in hits[:10]:
        print(f"  z={z:.1f} {st}")

if __name__ == '__main__':
    main()
