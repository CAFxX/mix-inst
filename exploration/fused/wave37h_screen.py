#!/usr/bin/env python3
"""Wave-37h: single-lane, N-stage, 1-AND + L-linear per stage.

Rationale (2026-10-11): 37b two-lane got best-ever quality (z=2.81) but is
DOMINATED on the Pareto axes (21u/10276 cells/29680 area vs b33c
19.8u/6133/19817) -- 2 lanes = 2x logic. The transferable insight is DENSE
linears (L=3) + hill-climb. This applies that to a SINGLE lane (area-efficient)
with fewer stages than b33c's 6.

Stage: x_{n+1} = x ^ (xa&xb) ^ xc1 ^ xc2 ^ xc3  (L=3, 5 terms, 3 XOR levels)
N stages (arg). Pre-whiten x^K, post-whiten ^rotl(K,13) (b33c convention).

Triage: marg -> SEQ z<10 -> RND64. Controls inherited from wave37 (PASS).
"""
import json
import random
import sys
import time

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from wave35_lib import rotl, M64, _marg_proxy, seq_exact_diff, rnd64_exact_diff

NSTAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 4
NLIN = int(sys.argv[2]) if len(sys.argv) > 2 else 3
N_TRY = int(sys.argv[3]) if len(sys.argv) > 3 else 40
SEED = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0x37A1
OUTP = f"wave37h_{NSTAGES}st_L{NLIN}_diag"
assert NSTAGES >= 1 and NLIN >= 1, "fail-loud: vacuous"


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
        lins = tuple(rng.randint(0, 63) for _ in range(NLIN))
        sched.append((a, b, lins))
    return sched


def make_mix(sched):
    def mix_fn(xs, K):
        xs = np.asarray(xs, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        x = (xs ^ K) & M64
        for a, b, lins in sched:
            v = x ^ (rotl(x, a) & rotl(x, b))
            for c in lins:
                v ^= rotl(x, c)
            x = v & M64
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
            rec = {"try": tried, "sched": [list(s) for s in sched]}
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
            print(f"[37h-{NSTAGES}st-L{NLIN}] TRY {tried}: marg={worst[0]:+.1f}{zs}{zrs} "
                  f"{status} ({time.time()-t0:.0f}s)", flush=True)
    seq_zs.sort()
    n = len(seq_zs)
    print(f"DONE [37h-{NSTAGES}st-L{NLIN}]: {N_TRY} tries, marg-pass {marg_pass}/{N_TRY}, KEEP {n_keep}", flush=True)
    if seq_zs:
        print(f"  seq-z dist: min={seq_zs[0]:.1f} med={seq_zs[n//2]:.1f} max={seq_zs[-1]:.1f}", flush=True)
    print(f"  raw: {OUTP}.jsonl", flush=True)


if __name__ == "__main__":
    main()
