#!/usr/bin/env python3
"""Wave-35 per-try diagnostic (incarnation-10 rebuild).

Logs PER-TRY worst-z (marg margin, SEQ z, RND64 z) to stdout AND to a JSONL
file -- wave-34 lesson: a screen that logs only aggregates+HITs leaves no
evidence when it dies at 0 hits. RND64 runs only on SEQ-KEEPs (it's the
expensive confirmation); the z-distribution deliverable is (marg, seq z)
for every try.

Usage: wave35_diag.py <TEMPLATE> <N_TRY> [SEED] [OUTPREFIX]
"""
import json
import random
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave35_lib import make_mix, _marg_proxy, seq_exact_diff, rnd64_exact_diff

TEMPLATE = sys.argv[1]
N_TRY = int(sys.argv[2])
DEFSEED = {"A": 0xA35, "B": 0xB35, "C": 0xC35, "E": 0xE35, "G": 0x935}
SEED = int(sys.argv[3], 0) if len(sys.argv) > 3 else DEFSEED[TEMPLATE]
OUTP = sys.argv[4] if len(sys.argv) > 4 else f"wave35_{TEMPLATE}_diag"
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
    t0 = time.time()
    seq_zs, marg_pass, n_keep = [], 0, 0
    with open(f"{OUTP}.jsonl", "w") as jf:
        for tried in range(1, N_TRY + 1):
            sched = sample_sched(rng, N_AND)
            mix_fn = make_mix(TEMPLATE, sched)
            rec = {"try": tried, "sched": sched}
            ok_m, worst = _marg_proxy(mix_fn)
            rec["marg_ok"] = bool(ok_m)
            rec["marg_margin"] = worst[0]
            rec["marg_desc"] = worst[1]
            z = zr = None
            keep = False
            if ok_m:
                marg_pass += 1
                z, _ = seq_exact_diff(mix_fn)
                rec["z"] = z
                seq_zs.append(z)
                if z < 10.0:
                    zr, _ = rnd64_exact_diff(mix_fn)
                    rec["zr"] = zr
                    keep = zr < 10.0
                    if keep:
                        n_keep += 1
            status = ("KEEP" if keep else
                      ("SEQ-KILL" if (z is not None and z >= 10.0) else
                       ("RND64-KILL" if (zr is not None and zr >= 10.0) else "MARG-KILL")))
            rec["status"] = status
            jf.write(json.dumps(rec) + "\n")
            jf.flush()
            zs = f" z={z:.1f}" if z is not None else ""
            zrs = f" zr={zr:.1f}" if zr is not None else ""
            print(f"[{TEMPLATE}] TRY {tried}: marg={worst[0]:+.1f}{zs}{zrs} "
                  f"{status} ({time.time()-t0:.0f}s)", flush=True)
    seq_zs.sort()
    n = len(seq_zs)
    print(f"DONE [{TEMPLATE}]: {N_TRY} tries, marg-pass {marg_pass}/{N_TRY}, "
          f"KEEP {n_keep}", flush=True)
    if seq_zs:
        print(f"  seq-z dist: min={seq_zs[0]:.1f} med={seq_zs[n//2]:.1f} "
              f"max={seq_zs[-1]:.1f}", flush=True)
    print(f"  raw: {OUTP}.jsonl", flush=True)


if __name__ == "__main__":
    main()
