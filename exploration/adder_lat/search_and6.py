#!/usr/bin/env python3
"""Search 6-stage AND schedules for (z<18, min S0).
Phase 1: random schedules -> v3 proxy logN=16, keep z<18.
Phase 2: S0 survivors via run_synth.py, report sorted by delay.
"""
import random
import sys
import os
import subprocess

sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat')
from s2proxy_v3 import s2proxy_v3
from gen_waveP import build

EXP = "/home/hatch/workspace/mix/exploration"


def rand_sched(rng):
    # 6 stages, (a,b,c) with a<b to avoid degeneracy, spread out
    sched = []
    for _ in range(6):
        a = rng.randrange(0, 64)
        b = rng.randrange(0, 64)
        while b == a:
            b = rng.randrange(0, 64)
        c = rng.randrange(0, 64)
        sched.append((a, b, c))
    return sched


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    zmax = float(sys.argv[3]) if len(sys.argv) > 3 else 18.0
    rng = random.Random(seed)
    survivors = []
    for i in range(n):
        sched = rand_sched(rng)
        st = [('and', a, b, c) for (a, b, c) in sched]
        z, d, b = s2proxy_v3(st, logN=16)
        tag = f"as6_{seed}_{i}"
        if z < zmax:
            survivors.append((z, tag, sched))
            print(f"z={z:6.1f} KEEP {tag} {sched}", flush=True)
        else:
            print(f"z={z:6.1f} drop {tag}", flush=True)
    print(f"\n# {len(survivors)}/{n} survivors (z<{zmax}), running S0...", flush=True)
    results = []
    for z, tag, sched in survivors:
        st = [('and', a, b, c) for (a, b, c) in sched]
        build(tag, st, f"and6 sched search {tag} z={z:.1f}", 'SKINNY')
        cdir = os.path.join(EXP, "fast_battery/candidates", tag)
        wd = f"/tmp/s0_{tag}"
        r = subprocess.run(
            [sys.executable, os.path.join(EXP, "run_synth.py"),
             os.path.join(cdir, "rtl.v"), tag, wd],
            capture_output=True, text=True, timeout=600)
        # parse crit from output
        import re
        m = re.search(r"crit=([\d.]+)", r.stdout)
        crit = float(m.group(1)) if m else -1
        results.append((crit, z, tag, sched))
        print(f"S0 {tag}: crit={crit:.1f}u z={z:.1f} {sched}", flush=True)
    results.sort()
    print("\n# TOP 10 by S0:", flush=True)
    for crit, z, tag, sched in results[:10]:
        print(f"{crit:5.1f}u z={z:5.1f} {tag} {sched}", flush=True)


if __name__ == '__main__':
    main()
