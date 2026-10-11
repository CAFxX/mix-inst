"""Fast v2 screening: sequential x, all 64 single-bit + key structured deltas,
logN=16. For search; verify hits with full v2 + real S2."""
import numpy as np, json, sys, time, os
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat/rootcause')
from s2proxy_v2 import apply_stage, mix_stages, M64, cost_est, maxz_for_delta

SCREEN_DELTAS = [0x400, 0x4000000] + [1 << k for k in range(64)] + \
                [3, 5, 9, 0x11, 0x8000000000000001, 0x100000001]

def screen(stages, logN=16):
    def mix_fn(xs, K):
        x = (xs ^ K) & M64
        return mix_stages(x, stages)
    worst = 0
    for d0 in SCREEN_DELTAS:
        z, _, _ = maxz_for_delta(mix_fn, d0, logN)
        if z > worst:
            worst = z
            if worst > 15:  # early exit
                break
    return worst

def rand_rot(rng, avoid=()):
    while True:
        r = int(rng.integers(1, 64))
        if r not in avoid:
            return r

def rand_stage(rng, typ):
    if typ == 'and':
        a = rand_rot(rng); b = rand_rot(rng, (a,)); c = rand_rot(rng, (a, b))
        return ('and', a, b, c)
    a = rand_rot(rng); b = rand_rot(rng, (a,))
    c = rand_rot(rng, (a, b)); e = rand_rot(rng, (a, b, c))
    return ('t3', a, b, c, e)

def main():
    seed = int(sys.argv[1]); count = int(sys.argv[2])
    out = '/home/hatch/workspace/mix/exploration/adder_lat/rootcause/candidates5d.json'
    rng = np.random.default_rng(seed)
    hits = json.load(open(out)) if os.path.exists(out) else []
    t0 = time.time()
    for i in range(count):
        # pattern [t3,and,and,and,t3] or 2xt3+3and shuffled
        if rng.random() < 0.6:
            st = [rand_stage(rng,'t3'), rand_stage(rng,'and'), rand_stage(rng,'and'),
                  rand_stage(rng,'and'), rand_stage(rng,'t3')]
        else:
            typs = ['t3','t3','and','and','and']; rng.shuffle(typs)
            st = [rand_stage(rng, t) for t in typs]
        z = screen(st)
        if z < 10.0:
            hits.append((z, [list(s) for s in st]))
            print(f"HIT z={z:.1f} {st}", flush=True)
        if (i+1) % 100 == 0:
            hits.sort(); json.dump(hits[:40], open(out, 'w'))
            print(f"  {i+1}/{count} {time.time()-t0:.0f}s {len(hits)} hits", flush=True)
    hits.sort(); json.dump(hits[:40], open(out, 'w'))
    print(f"done {len(hits)}/{count}")
    for (z, st) in hits[:10]:
        print(f"  z={z:.1f} {st}")

if __name__ == '__main__':
    main()
