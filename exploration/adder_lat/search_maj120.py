#!/usr/bin/env python3
"""120-schedule 4-stage MAJ search (track-3 pivot, 2026-10-10).

Rationale: P1h [majx4] was a SINGLE fixed schedule (z=256) -- the and6
experience (same proxy, z 4.0..256 across 120 random schedules) proves
schedule variance is enormous. Never schedule-searched for maj. Economics:
t6_maj6 real S0 = 29.4u/6 = 4.9u per maj stage -> 4-stage ~19.6u, sub-frontier
IF S2-clean. Phase 1: v3 proxy logN=16, keep z<18 (same bar as and6 search).
S0 only for survivors (fixed DUT-line crit parser).
"""
import random
import sys
import os
import re
import subprocess

AD = "/home/hatch/workspace/mix/exploration/adder_lat"
EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, AD)
from s2proxy_v3 import s2proxy_v3
from gen_waveP import build

SEED, N, ZMAX = 300, 120, 18.0


def rand_sched(rng):
    sched = []
    for _ in range(4):
        a = rng.randrange(0, 64)
        b = rng.randrange(0, 64)
        while b == a:
            b = rng.randrange(0, 64)
        c = rng.randrange(0, 64)
        while c == a or c == b:
            c = rng.randrange(0, 64)
        d = rng.randrange(0, 64)
        sched.append((a, b, c, d))
    return sched


def main():
    rng = random.Random(SEED)
    survivors = []
    for i in range(N):
        sched = rand_sched(rng)
        st = [('maj', a, b, c, d) for (a, b, c, d) in sched]
        z, dd, bb = s2proxy_v3(st, logN=16)
        tag = f"mj4_{SEED}_{i}"
        if z < ZMAX:
            survivors.append((z, tag, sched))
            print(f"z={z:6.1f} KEEP {tag} {sched}", flush=True)
        else:
            print(f"z={z:6.1f} drop {tag}", flush=True)
    print(f"\n# {len(survivors)}/{N} survivors (z<{ZMAX}), running S0...", flush=True)
    results = []
    for z, tag, sched in survivors:
        st = [('maj', a, b, c, d) for (a, b, c, d) in sched]
        build(tag, st, f"maj4 sched search {tag} z={z:.1f}", 'SKINNY')
        cdir = os.path.join(EXP, "fast_battery/candidates", tag)
        wd = f"/tmp/s0_{tag}"
        r = subprocess.run(
            [sys.executable, os.path.join(EXP, "run_synth.py"),
             os.path.join(cdir, "rtl.v"), tag, wd],
            capture_output=True, text=True, timeout=900)
        m = re.search(r"^DUT\s+\S+.*?crit=([\d.]+)", r.stdout, re.M)
        crit = float(m.group(1)) if m else -1
        results.append((crit, z, tag, sched))
        print(f"S0 {tag}: crit={crit:.1f}u z={z:.1f} {sched}", flush=True)
    results.sort()
    print("\n# TOP 10 by S0:", flush=True)
    for crit, z, tag, sched in results[:10]:
        print(f"{crit:5.1f}u z={z:5.1f} {tag} {sched}", flush=True)


if __name__ == '__main__':
    main()
