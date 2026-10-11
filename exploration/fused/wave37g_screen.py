#!/usr/bin/env python3
"""Wave-37g: single-lane 4-stage, 1-AND + 2-linear per stage.

Cost-driven pivot from 37b (cost-blocked at 21u). Stage:
    x_{n+1} = x ^ (xa&xb) ^ xc ^ xd
4 terms -> 2 XOR levels + AND = 3 levels/stage. 4 stages + pre/post-whiten
est ~14 levels ≈ 17u < 19.8u.

De-dup: track-5 lin2 was 1AND+2lin at *5* stages (23.2u, quality-clean);
4-stage is untested (the 4-stage wall held for sparser forms). Track-6
batch-34 did AND3/AOI dense forms at 5/4st (different: 3-term complex).
This is 3-term simple (AND2+2lin) at 4st with hill-climb-ready schedules.

Triage: marg -> SEQ exact-DIFF z<10 -> RND64. Controls: b33c/V0.
"""
import json
import random
import sys
import time

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from wave35_lib import rotl, M64, _marg_proxy, seq_exact_diff, rnd64_exact_diff

NSTAGES = 4
N_TRY = int(sys.argv[1]) if len(sys.argv) > 1 else 40
SEED = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x3761
OUTP = "wave37g_4st_diag"


def _dpair(rng):
    a = rng.randint(1, 63)
    b = rng.randint(1, 63)
    while b == a:
        b = rng.randint(1, 63)
    return a, b


def sample(rng):
    sched = []
    for _ in range(NSTAGES):
        a, b = _dpair(rng)
        c = rng.randint(0, 63)
        d = rng.randint(0, 63)
        sched.append((a, b, c, d))
    return sched


def make_mix(sched):
    def mix_fn(xs, K):
        xs = np.asarray(xs, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        x = (xs ^ K) & M64
        for a, b, c, d in sched:
            x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c) ^ rotl(x, d)) & M64
        return (x ^ rotl(K, 13)) & M64
    return mix_fn


def main():
    rng = random.Random(SEED)
    t0 = time.time()
    seq_zs, marg_pass, n_keep = [], 0, 0
    with open(f"{OUTP}.jsonl", "w") as jf:
        for tried in range(1, N_TRY + 1):
            sched = sample(rng)
            mix_fn = make_mix(sched)
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
            print(f"[37g-4st] TRY {tried}: marg={worst[0]:+.1f}{zs}{zrs} "
                  f"{status} ({time.time()-t0:.0f}s)", flush=True)
    seq_zs.sort()
    n = len(seq_zs)
    print(f"DONE [37g-4st]: {N_TRY} tries, marg-pass {marg_pass}/{N_TRY}, KEEP {n_keep}", flush=True)
    if seq_zs:
        print(f"  seq-z dist: min={seq_zs[0]:.1f} med={seq_zs[n//2]:.1f} max={seq_zs[-1]:.1f}", flush=True)
    print(f"  raw: {OUTP}.jsonl", flush=True)


if __name__ == "__main__":
    main()
