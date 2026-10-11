"""Guided random search for 5-stage hetero (and/t3) designs with proxy max|z| < 9
and est_cost < 20.1u. Saves top candidates to candidates5.json."""
import numpy as np, json, sys, time
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
from s2proxy import s2proxy, cost_est

DELTAS = [1<<i for i in (0, 7, 13, 29, 46, 63)] + [0xFF, 1<<0 | 1<<32]

def rand_rot(rng, avoid=()):
    while True:
        r = int(rng.integers(1, 64))
        if r not in avoid:
            return r

def rand_stage(rng, typ):
    if typ == 'and':
        a = rand_rot(rng); b = rand_rot(rng, (a,))
        c = rand_rot(rng, (a, b))
        return ('and', a, b, c)
    else:
        a = rand_rot(rng); b = rand_rot(rng, (a,))
        c = rand_rot(rng, (a, b)); e = rand_rot(rng, (a, b, c))
        return ('t3', a, b, c, e)

def rand_design(rng, n_t3):
    typs = ['t3']*n_t3 + ['and']*(5-n_t3)
    rng.shuffle(typs)
    return [rand_stage(rng, t) for t in typs]

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    rng = np.random.default_rng(seed)
    results = []
    t0 = time.time()
    for i in range(count):
        n_t3 = int(rng.integers(1, 4))  # 1..3 t3 stages
        st = rand_design(rng, n_t3)
        ce = cost_est(st)
        if ce >= 20.1:
            continue
        z, d, b = s2proxy(st, deltas=DELTAS, n=1<<17)
        results.append((z, ce, n_t3, st))
        if z < 9:
            print(f"HIT z={z:.1f} cost={ce:.2f} n_t3={n_t3} {st}", flush=True)
    results.sort()
    print(f"--- searched {count} in {time.time()-t0:.0f}s, {sum(1 for r in results if r[0]<9)} hits ---")
    top = [(z, ce, n_t3, [list(s) for s in st]) for (z, ce, n_t3, st) in results[:20]]
    with open('/home/hatch/workspace/mix/exploration/adder_lat/rootcause/candidates5.json', 'w') as f:
        json.dump(top, f, indent=1)
    for (z, ce, n_t3, st) in top[:10]:
        print(f"top z={z:.1f} cost={ce:.2f} n_t3={n_t3} {st}")

if __name__ == '__main__':
    main()
