#!/usr/bin/env python3
"""Wave-14 screen: W1 (narrow-lane carry-fused ARX) + W3 (GF-diffused word-AND).

Gate 0 (FAIL-LOUD): positive controls reproduce EXACTLY --
  as6_200_106 -> KILL, seq z == 71.4
  t6_b33b     -> KEEP, seq z == 3.0
  al_and6a    -> KEEP, seq z ~= 3.2
Then: seeded randomized schedule sweeps on BOTH domains (sequential PRIMARY,
random-64 secondary), KEEP bar max|z| < 10 on sequential (triage_core).
KEEPs -> hill-climb (local schedule mutation) -> JSONL.

Cost eligibility (from work/calib.json): W1 2st ~= 50-58u / 3st ~= 81-87u;
W3 2st ~= 35u / 3st ~= 53u -- all < 123.4u adder-like bar; none < 19.8u.
"""
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")

from triage_core import (  # noqa: E402
    M64, BAR, KEYS10, triage, exact_diff_worst, and6_form,
    AS6_200_106, T6_B33B, AL_AND6A,
)
from screen_lib import N  # noqa: E402

WORK = os.path.join(HERE, "work")
OUT_JSONL = os.path.join(WORK, "screen_wave14.jsonl")

GF_POLY_XOR = np.uint64(0x1B)  # x^64+x^4+x^3+x+1 reduction bits
GF_CONSTS = [0x9E3779B97F4A7C15, 0xBF58476D1CE4E5B9, 0x94D049BB133111EB]


def rotl64(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def rotl16(x, r):
    r %= 16
    return ((x << np.uint64(r)) | (x >> np.uint64(16 - r))) & np.uint64(0xFFFF) \
        if r else x


# ---------------------------------------------------------------- GF(2^64)
def gf64_mul_scalar(a, C):
    """Obviously-correct scalar GF(2^64) multiply (Russian peasant)."""
    res = 0
    p = a
    c = C
    while c:
        if c & 1:
            res ^= p
        hi = (p >> 63) & 1
        p = ((p << 1) & 0xFFFFFFFFFFFFFFFF) ^ (0x1B if hi else 0)
        c >>= 1
    return res


def gf64_mul_vec(a, C):
    """Vectorized GF(2^64) multiply by constant C over a uint64 array."""
    res = np.zeros(a.shape, dtype=np.uint64)
    p = a.copy()
    c = int(C)
    while c:
        if c & 1:
            res ^= p
        hi = (p >> np.uint64(63)) & np.uint64(1)
        p = ((p << np.uint64(1)) & M64) ^ (hi * GF_POLY_XOR)
        c >>= 1
    return res


def selftest_gf():
    rng = np.random.default_rng(0x6F)
    vals = rng.integers(0, 2**64, size=257, dtype=np.uint64)
    for C in GF_CONSTS:
        got = gf64_mul_vec(vals, C)
        for i, v in enumerate(vals):
            exp = gf64_mul_scalar(int(v), C)
            assert int(got[i]) == exp, f"GF mismatch C={C:#x} i={i}"
    print("GF(2^64) vectorized == scalar on 3 consts x 257 vals: OK", flush=True)


# ---------------------------------------------------------------- models
def w1_form(V, key, sched):
    """W1: 4x16-bit lanes; per stage li = li + rotl16(l[(i+1)%4], a) [+ C_i];
    laneperm; x ^= rotl64(x, b). sched = list of (a, perm4, b, Cs|None)."""
    K = np.full(V.shape, np.uint64(key), dtype=np.uint64)
    x = (V ^ K) & M64
    for (a, perm, b, Cs) in sched:
        L = [(x >> np.uint64(16 * i)) & np.uint64(0xFFFF) for i in range(4)]
        nl = []
        for i in range(4):
            s = L[i] + rotl16(L[(i + 1) % 4], a)
            if Cs is not None:
                s = s + np.uint64(Cs[i])
            nl.append(s & np.uint64(0xFFFF))
        L = [nl[perm[i]] for i in range(4)]
        x = (L[0] | (L[1] << np.uint64(16)) | (L[2] << np.uint64(32))
             | (L[3] << np.uint64(48))) & M64
        x = (x ^ rotl64(x, b)) & M64
    return ((x ^ rotl64(K, 13)) & M64).astype(np.uint64)


def w3_form(V, key, sched):
    """W3: per stage: n_and times x ^= (rotl(x,a)&rotl(x,b)); then
    x = gf64_mul(x, P). sched = (stages, P); stages = list of [(a,b),...]."""
    stages, P = sched
    K = np.full(V.shape, np.uint64(key), dtype=np.uint64)
    x = (V ^ K) & M64
    for ands in stages:
        for (a, b) in ands:
            x = (x ^ (rotl64(x, a) & rotl64(x, b))) & M64
        x = gf64_mul_vec(x, P)
    return ((x ^ rotl64(K, 13)) & M64).astype(np.uint64)


# ---------------------------------------------------------------- gate 0
def gate_exact_canaries():
    print("=== GATE 0: exact positive-control reproduction ===", flush=True)
    Vseq = np.arange(N, dtype=np.uint64)
    z1, k1 = exact_diff_worst(lambda V, k: and6_form(V, k, AS6_200_106), Vseq)
    print(f"kill canary as6_200_106: seq z={z1:.1f} (expect 71.4 KILL)",
          flush=True)
    assert z1 >= BAR, f"kill canary NOT killed: z={z1}"
    assert abs(z1 - 71.4) < 0.05, f"kill canary z drifted: {z1} != 71.4"
    z2, k2 = exact_diff_worst(lambda V, k: and6_form(V, k, T6_B33B), Vseq)
    print(f"keep canary t6_b33b:      seq z={z2:.1f} (expect 3.0 KEEP)",
          flush=True)
    assert z2 < BAR, f"b33b keep canary killed: z={z2}"
    assert abs(z2 - 3.0) < 0.05, f"b33b z drifted: {z2} != 3.0"
    z3, k3 = exact_diff_worst(lambda V, k: and6_form(V, k, AL_AND6A), Vseq)
    print(f"keep canary al_and6a:     seq z={z3:.1f} (expect ~3.2 KEEP)",
          flush=True)
    assert z3 < BAR, f"al_and6a keep canary killed: z={z3}"
    assert abs(z3 - 3.2) < 0.15, f"al_and6a z drifted: {z3} != ~3.2"
    print("=== GATE 0 PASS: harness trusted ===", flush=True)


# ---------------------------------------------------------------- schedules
PERMS4 = list(itertools.permutations(range(4)))
ODD16 = [1, 3, 5, 7, 9, 11, 13, 15]
ODD64 = [b for b in range(1, 64, 2) if b != 32]


def gen_w1(n, seed):
    rng = np.random.default_rng(seed)
    out = []
    # hand-structured seeds (b33-style: alternate rotations, lane rotations)
    hand = [
        (5, (1, 2, 3, 0), 17), (11, (1, 2, 3, 0), 41),
        (7, (2, 3, 0, 1), 23), (13, (3, 0, 1, 2), 29),
    ]
    for r in (2, 3):
        sched = []
        for i in range(r):
            a, perm, b = hand[i % len(hand)]
            Cs = tuple(int(rng.integers(0, 2**16)) for _ in range(4))
            sched.append((a, perm, b, Cs))
        out.append(("W1-hand", sched))
    for _ in range(n):
        r = 2 if rng.random() < 0.5 else 3
        sched = []
        for _ in range(r):
            a = ODD16[int(rng.integers(0, len(ODD16)))]
            perm = PERMS4[int(rng.integers(0, len(PERMS4)))]
            b = ODD64[int(rng.integers(0, len(ODD64)))]
            Cs = (tuple(int(rng.integers(0, 2**16)) for _ in range(4))
                  if rng.random() < 0.7 else None)
            sched.append((a, perm, b, Cs))
        out.append(("W1-rnd", sched))
    return out


def gen_w3(n, seed):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        r = 2 if rng.random() < 0.6 else 3
        n_and = 1 if rng.random() < 0.6 else 2
        P = GF_CONSTS[int(rng.integers(0, len(GF_CONSTS)))]
        stages = []
        for _ in range(r):
            ands = []
            for _ in range(n_and):
                a = int(rng.integers(1, 64))
                b = int(rng.integers(1, 64))
                if b == a:
                    b = (b % 63) + 1
                ands.append((a, b))
            stages.append(ands)
        out.append(("W3-rnd", (stages, P)))
    return out


def sched_tag(fam, sched):
    if fam == "W1-rnd" or fam == "W1-hand":
        parts = []
        for (a, perm, b, Cs) in sched:
            cs = "2op" if Cs is None else "".join(f"{c:04x}" for c in Cs)
            parts.append(f"a{a}p{''.join(map(str,perm))}b{b}{cs}")
        return f"{fam}:" + "|".join(parts)
    stages, P = sched
    parts = []
    for ands in stages:
        parts.append("+".join(f"{a},{b}" for a, b in ands))
    return f"{fam}:P{P:016x}:" + "|".join(parts)


def run_one(task):
    fam, sched = task
    tag = sched_tag(fam, sched)
    try:
        if fam.startswith("W1"):
            keep, zseq, zrnd = triage(lambda V, k: w1_form(V, k, sched), tag)
        else:
            keep, zseq, zrnd = triage(lambda V, k: w3_form(V, k, sched), tag)
        return {"tag": tag, "fam": fam, "keep": bool(keep),
                "z_seq": float(zseq), "z_rnd": float(zrnd)}
    except Exception as e:  # never let one bad schedule kill the sweep
        return {"tag": tag, "fam": fam, "keep": False, "z_seq": -1.0,
                "z_rnd": -1.0, "error": repr(e)}


def main():
    t0 = time.time()
    selftest_gf()
    gate_exact_canaries()

    tasks = gen_w1(400, 0x714E) + gen_w3(200, 0x314159)
    print(f"sweep: {len(tasks)} schedules "
          f"({sum(1 for f, _ in tasks if f.startswith('W1'))} W1, "
          f"{sum(1 for f, _ in tasks if f.startswith('W3'))} W3)", flush=True)

    from multiprocessing import Pool
    keeps = []
    done = 0
    with open(OUT_JSONL, "a") as f, Pool(3) as pool:
        for res in pool.imap_unordered(run_one, tasks, chunksize=1):
            done += 1
            f.write(json.dumps(res) + "\n")
            f.flush()
            if res["keep"]:
                keeps.append(res)
                print(f"  KEEP #{len(keeps)} {res['tag']} "
                      f"zseq={res['z_seq']:.1f} zrnd={res['z_rnd']:.1f}",
                      flush=True)
            if done % 50 == 0:
                el = time.time() - t0
                print(f"  ... {done}/{len(tasks)} triaged, "
                      f"{len(keeps)} KEEPs, {el/60:.0f}min elapsed", flush=True)

    print(f"=== sweep done: {done} triaged, {len(keeps)} KEEPs "
          f"in {(time.time()-t0)/60:.0f}min ===", flush=True)

    # hill-climb around KEEPs (local schedule mutation), one round
    if keeps:
        print("=== hill-climb on KEEPs ===", flush=True)
        # NOTE: hill-climb needs sched objects, not tags; re-derive by
        # re-running the generators deterministically and matching tags.
        sched_by_tag = {sched_tag(f, s): (f, s)
                        for f, s in gen_w1(400, 0x714E) + gen_w3(200, 0x314159)}
        rng = np.random.default_rng(0xC11B)
        hc_tasks = []
        for k in keeps:
            fam, sched = sched_by_tag[k["tag"]]
            hc_tasks.extend(mutate(fam, sched, rng, 40))
        with open(OUT_JSONL, "a") as f, Pool(3) as pool:
            for res in pool.imap_unordered(run_one, hc_tasks, chunksize=1):
                f.write(json.dumps({**res, "hillclimb": True}) + "\n")
                f.flush()
                if res["keep"]:
                    keeps.append(res)
                    print(f"  HC-KEEP {res['tag']} zseq={res['z_seq']:.1f}",
                          flush=True)
    print(f"=== FINAL: {len(keeps)} KEEPs -> {OUT_JSONL} ===", flush=True)


def mutate(fam, sched, rng, n):
    out = []
    for _ in range(n):
        if fam.startswith("W1"):
            ns = []
            for (a, perm, b, Cs) in sched:
                na = ODD16[int(rng.integers(0, len(ODD16)))] \
                    if rng.random() < 0.3 else a
                nperm = list(perm)
                if rng.random() < 0.3:
                    i, j = rng.choice(4, 2, replace=False)
                    nperm[i], nperm[j] = nperm[j], nperm[i]
                nperm = tuple(nperm)
                nb = ODD64[int(rng.integers(0, len(ODD64)))] \
                    if rng.random() < 0.3 else b
                nCs = Cs
                if Cs is not None and rng.random() < 0.4:
                    nCs = list(Cs)
                    nCs[int(rng.integers(0, 4))] = \
                        int(rng.integers(0, 2**16))
                    nCs = tuple(nCs)
                ns.append((na, nperm, nb, nCs))
            out.append((fam, ns))
        else:
            stages, P = sched
            ns = []
            for ands in stages:
                nands = []
                for (a, b) in ands:
                    na = int(rng.integers(1, 64)) if rng.random() < 0.4 else a
                    nb = int(rng.integers(1, 64)) if rng.random() < 0.4 else b
                    if nb == na:
                        nb = (nb % 63) + 1
                    nands.append((na, nb))
                ns.append(nands)
            nP = (GF_CONSTS[int(rng.integers(0, len(GF_CONSTS)))]
                  if rng.random() < 0.2 else P)
            out.append((fam, (ns, nP)))
    return out


if __name__ == "__main__":
    main()
