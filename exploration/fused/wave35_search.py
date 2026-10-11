#!/usr/bin/env python3
"""Wave-35: two-state diffusion screen (AND-cascade + S-box layer).

Templates:
  A: [A, A, S, A, A]   (4 AND stages, S-box layer in the middle)
  B: [S, A, A, A]      (S-box first: AND stages never see sequential inputs)
  C: [A, S, A, S, A]   (3 AND stages, 2 S-box layers, nibble-misaligning rot)

KEEP bar: marg proxy PASS, SEQ exact-DIFF max|z| < 10 (all 10 keys),
          RND64 exact-DIFF max|z| < 10 (confirmation on survivors).
Controls verified separately (wave35_controls.py): b33c z=3.34 KEEP,
V0 z=739994 KILL.
"""
import json
import random
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave35_lib import make_mix, _marg_proxy, seq_exact_diff, rnd64_exact_diff

TEMPLATE = sys.argv[1] if len(sys.argv) > 1 else "A"
N_TRY = int(sys.argv[2]) if len(sys.argv) > 2 else 200
SEED = int(sys.argv[3], 0) if len(sys.argv) > 3 else {"A": 0xA35, "B": 0xB35, "C": 0xC35, "E": 0xE35, "G": 0x935}[TEMPLATE]

N_AND = {"A": 4, "B": 3, "C": 3, "E": 5, "G": 4}[TEMPLATE]


def sample_sched(rng, n):
    stages, seen = [], set()
    while len(stages) < n:
        a = rng.randint(1, 63)
        b = rng.randint(1, 63)
        if a == b:
            continue
        c = rng.randint(0, 63)
        if (a, b, c) in seen:
            continue
        seen.add((a, b, c))
        stages.append((a, b, c))
    return stages


def main():
    rng = random.Random(SEED)
    hits = []
    t0 = time.time()
    for tried in range(1, N_TRY + 1):
        sched = sample_sched(rng, N_AND)
        inter_rot = 0
        if TEMPLATE == "C":
            inter_rot = rng.randint(1, 63)
            while inter_rot % 4 == 0:
                inter_rot = rng.randint(1, 63)
        mix_fn = make_mix(TEMPLATE, sched, inter_rot)
        ok_m, worst = _marg_proxy(mix_fn)
        if not ok_m:
            if tried % 10 == 0:
                print(f"[{TEMPLATE}] TRY {tried}: marg-KILL ({len(hits)} hits, "
                      f"{time.time()-t0:.0f}s)", flush=True)
            continue
        m, _ = worst
        z, cfg = seq_exact_diff(mix_fn)
        if z >= 10.0:
            if tried % 10 == 0:
                print(f"[{TEMPLATE}] TRY {tried}: DIFF-KILL z={z:.1f} "
                      f"({len(hits)} hits, {time.time()-t0:.0f}s)", flush=True)
            continue
        zr, cfgr = rnd64_exact_diff(mix_fn)
        if zr >= 10.0:
            print(f"[{TEMPLATE}] TRY {tried}: RND64-KILL z={z:.1f} zr={zr:.1f}",
                  flush=True)
            continue
        print(f"[{TEMPLATE}] TRY {tried}: HIT marg={m:+.1f} z={z:.2f} zr={zr:.2f} "
              f"sched={sched} ir={inter_rot}", flush=True)
        hits.append({"try": tried, "marg": m, "z": z, "zr": zr,
                     "sched": sched, "inter_rot": inter_rot})
    print(f"DONE [{TEMPLATE}]: {len(hits)}/{N_TRY} hits", flush=True)
    with open(f"wave35_{TEMPLATE}_hits.json", "w") as f:
        json.dump(hits, f, indent=1)
    for h in sorted(hits, key=lambda h: h["z"])[:10]:
        print(f"  HIT z={h['z']:.2f} zr={h['zr']:.2f} {h['sched']} ir={h['inter_rot']}",
              flush=True)


if __name__ == "__main__":
    main()
