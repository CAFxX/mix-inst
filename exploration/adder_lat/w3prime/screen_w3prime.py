#!/usr/bin/env python3
"""W3' screen: d-constrained 3-stage word-AND schedules, exact-DIFF triage.

Co-design per wave14/W3_LIN_MECHANISM.md:
- 3 stages x 2 ANDs/stage; every (a,b) has d=(b-a)%64 in
  {1,2,3,4,5,59,60,61,62,63} (anti-affinity, enforced AT GENERATION).
- Sequential-affinity pre-check: assert no AND is affine on 64-sequential
  blocks (single-AND-layer rank >= 8; affine would be 7).
- exact-DIFF triage (triage_core, b33 harness): KEEP bar seq max|z| < 10.
- Rank probe: full candidate on 64 sequential inputs, fixed key -> rank >= 62.

N=200 schedules, seeded RNG (seed 0xW3P1). JSONL checkpoint per candidate.
Heartbeat every 25 candidates.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/wave14")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")

import numpy as np
from triage_core import triage, check_canaries, BAR
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEY0 = int(KEYS[0])
DSET = [1, 2, 3, 4, 5, 59, 60, 61, 62, 63]
PS = [0xBF58476D1CE4E5B9, 0x9E3779B97F4A7C15, 0x94D049BB133111EB]
N_CAND = 200
SEED = 0x77A3  # documented seed
HB = "/home/hatch/workspace/mix/exploration/adder_lat/supervisor_heartbeat.txt"
JSONL = os.path.join(HERE, "w3prime_screen.jsonl")


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def gf(a, C):
    res = np.zeros(a.shape, dtype=np.uint64)
    p = a.copy()
    c = int(C)
    while c:
        if c & 1:
            res ^= p
        hi = (p >> np.uint64(63)) & np.uint64(1)
        p = ((p << np.uint64(1)) & M64) ^ (hi * np.uint64(0x1B))
        c >>= 1
    return res


def w3_model(V, key, stages, P):
    K = np.full(np.shape(V), np.uint64(key), dtype=np.uint64)
    x = (np.asarray(V, dtype=np.uint64) ^ K) & M64
    for ands in stages:
        for a, b in ands:
            x = (x ^ (rotl(x, a) & rotl(x, b))) & M64
        x = gf(x, P)
    return ((x ^ rotl(K, 13)) & M64)


def gf2_rank(rows64):
    """Rank of 64 rows (python ints = 64-bit rows) over GF(2)."""
    m = list(rows64)
    r = 0
    for col in range(63, -1, -1):
        piv = None
        for i in range(r, 64):
            if (m[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        for i in range(64):
            if i != r and ((m[i] >> col) & 1):
                m[i] ^= m[r]
        r += 1
    return r


def and_layer_rank(a, b):
    """Rank of single AND layer g(x)=x^(rotl(x,a)&rotl(x,b)) on 64 seq inputs."""
    V = np.arange(64, dtype=np.uint64)
    g = (V ^ (rotl(V, a) & rotl(V, b))) & M64
    return gf2_rank([int(v) for v in g])


def full_rank(stages, P):
    V = np.arange(64, dtype=np.uint64)
    y = w3_model(V, KEY0, stages, P)
    return gf2_rank([int(v) for v in y])


def heartbeat(msg):
    with open(HB, "a") as f:
        f.write("%s w3prime-screen: %s\n" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), msg))


def gen_schedule(rng):
    stages = []
    for _ in range(3):
        ands = []
        for _ in range(2):
            a = int(rng.integers(0, 64))
            d = DSET[int(rng.integers(0, len(DSET)))]
            b = (a + d) % 64
            ands.append((a, b))
        stages.append(ands)
    return stages


def main():
    t_start = time.time()
    heartbeat("screen start N=%d seed=%#x" % (N_CAND, SEED))
    print("=== canary gate ===", flush=True)
    if not check_canaries():
        heartbeat("ABORT: canary gate FAILED")
        print("CANARY GATE FAILED - aborting", flush=True)
        sys.exit(2)
    heartbeat("canary gate PASS")

    rng = np.random.default_rng(SEED)
    done = 0
    if os.path.exists(JSONL):
        with open(JSONL) as f:
            done = sum(1 for _ in f if _.strip())
        print("resuming: %d already done" % done, flush=True)
    # regenerate the same schedule stream and skip `done`
    schedules = []
    for i in range(N_CAND):
        st = gen_schedule(rng)
        P = PS[i % len(PS)]
        schedules.append((st, P))
    schedules = schedules[done:]

    out = open(JSONL, "a")
    n_keep = 0
    for idx, (stages, P) in enumerate(schedules, start=done):
        # (a) sequential-affinity pre-check
        aff_fail = None
        for si, ands in enumerate(stages):
            for ai, (a, b) in enumerate(ands):
                rk = and_layer_rank(a, b)
                if rk < 8:
                    aff_fail = (si, ai, a, b, rk)
                    break
            if aff_fail:
                break
        rec = {"idx": idx, "stages": stages, "P": hex(P)}
        if aff_fail:
            rec.update({"affine_and": aff_fail, "verdict": "REJECT-affine"})
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print("[%03d] REJECT-affine AND %s" % (idx, aff_fail), flush=True)
            continue
        # (b) exact-DIFF triage
        keep, z_seq, z_rnd = triage(
            lambda V, k: w3_model(V, k, stages, P), "w3p-%03d" % idx)
        # (c) rank probe
        fr = full_rank(stages, P)
        verdict = "KEEP" if (keep and fr >= 62) else "kill"
        if keep and fr >= 62:
            n_keep += 1
        rec.update({"z_seq": round(float(z_seq), 2),
                    "z_rnd": round(float(z_rnd), 2),
                    "full_rank": fr, "verdict": verdict})
        out.write(json.dumps(rec) + "\n")
        out.flush()
        if (idx + 1) % 25 == 0:
            el = (time.time() - t_start) / 60
            heartbeat("progress %d/%d keeps=%d elapsed=%.0fm" %
                      (idx + 1, N_CAND, n_keep, el))
    out.close()
    heartbeat("screen DONE keeps=%d elapsed=%.0fm" %
              (n_keep, (time.time() - t_start) / 60))
    print("DONE keeps=%d" % n_keep, flush=True)


if __name__ == "__main__":
    main()
