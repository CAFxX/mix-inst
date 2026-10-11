"""Hill-climb from the best hetero candidate: mutate rotations, keep improvements.
Objective: strict proxy max|z| (N=2^19, 20 deltas)."""
import numpy as np, json, sys, time
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
from s2proxy import s2proxy

DELTAS = [1<<i for i in range(0,64,4)] + [0xFF, 1<<0|1<<32, 0xAAAAAAAAAAAAAAAA, 0x5555555555555555]

# best from candidates5.json strict reverify: z=8.3
BEST = [['t3', 57, 53, 18, 11], ['and', 62, 10, 33], ['and', 15, 50, 55],
        ['and', 43, 49, 33], ['t3', 21, 1, 59, 35]]

def mutate(rng, stages):
    st = [list(s) for s in stages]
    i = int(rng.integers(0, 5))
    j = int(rng.integers(1, len(st[i])))
    old = st[i][j]
    while True:
        v = int(rng.integers(1, 64))
        if v != old and v not in st[i][1:]:
            break
    st[i][j] = v
    return [tuple(s) for s in st]

def main():
    rng = np.random.default_rng(42)
    cur = [tuple(s) for s in BEST]
    cur_z, _, _ = s2proxy(cur, deltas=DELTAS, n=1<<19)
    print(f"start z={cur_z:.2f}", flush=True)
    best_z, best = cur_z, cur
    t0 = time.time()
    it = 0
    while time.time() - t0 < 1500:  # 25 min
        it += 1
        nxt = mutate(rng, cur)
        z, _, _ = s2proxy(nxt, deltas=DELTAS, n=1<<19)
        if z < cur_z:
            cur, cur_z = nxt, z
            print(f"it={it} IMPROVED z={z:.2f} {nxt}", flush=True)
            if z < best_z:
                best_z, best = z, nxt
    print(f"done: best z={best_z:.2f} {best}")
    json.dump({"z": best_z, "stages": [list(s) for s in best]},
              open('/home/hatch/workspace/mix/exploration/adder_lat/rootcause/hillbest.json','w'))

if __name__ == '__main__':
    main()
