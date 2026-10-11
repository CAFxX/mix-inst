#!/usr/bin/env python3
"""Resume search_and6_120 from i=58 (died 12:01:48Z at sched 57, no traceback;
0/58 survivors in log). seed=200, n=120, zmax=18. Appends to the same log.
Same phase-1 + phase-2 logic as search_and6.py, RNG draws 0..57 consumed first.
"""
import random
import sys
import os
import re
import subprocess

sys.path.insert(0, '/home/hatch/workspace/mix/exploration/adder_lat')
from s2proxy_v3 import s2proxy_v3
from gen_waveP import build

EXP = "/home/hatch/workspace/mix/exploration"
SEED, N, START, ZMAX = 200, 120, 58, 18.0


def rand_sched(rng):
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
    rng = random.Random(SEED)
    for _ in range(START):
        rand_sched(rng)  # consume draws 0..START-1 (already logged)
    print(f"\n# RESUMED 2026-10-10T13:1xZ: seed={SEED} i={START}..{N-1} zmax={ZMAX}", flush=True)
    survivors = []
    for i in range(START, N):
        sched = rand_sched(rng)
        st = [('and', a, b, c) for (a, b, c) in sched]
        z, d, b = s2proxy_v3(st, logN=16)
        tag = f"as6_{SEED}_{i}"
        if z < ZMAX:
            survivors.append((z, tag, sched))
            print(f"z={z:6.1f} KEEP {tag} {sched}", flush=True)
        else:
            print(f"z={z:6.1f} drop {tag}", flush=True)
    print(f"\n# {len(survivors)}/{N-START} resumed survivors (z<{ZMAX}), running S0...", flush=True)
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
        m = re.search(r"^DUT\s+\S+.*?crit=([\d.]+)", r.stdout, re.M)
        # NOTE: do NOT use r"crit=([\d.]+)" -- the first crit= token in
        # run_synth.py output is the mul64 REFERENCE line (ref_crit=103.5),
        # not the DUT's. Parse the DUT line explicitly. (2026-10-10 bugfix)
        crit = float(m.group(1)) if m else -1
        results.append((crit, z, tag, sched))
        print(f"S0 {tag}: crit={crit:.1f}u z={z:.1f} {sched}", flush=True)
    results.sort()
    print("\n# TOP 10 by S0:", flush=True)
    for crit, z, tag, sched in results[:10]:
        print(f"{crit:5.1f}u z={z:5.1f} {tag} {sched}", flush=True)


if __name__ == '__main__':
    main()
