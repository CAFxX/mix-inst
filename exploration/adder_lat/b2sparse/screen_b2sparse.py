#!/usr/bin/env python3
"""(b2) sparse-GF screen: d-constrained 3-stage word-AND with cheap linear
diffusion between stages and ONE GF(2^64) multiplication at the end.

Co-design per adder_lat/b2sparse/DESIGN.md (O127: the cheap-linear arm is
QUALITY-CLOSED — the GF mult is load-bearing for diffusion, not just rank;
keeping one at the end preserves the diffusion backstop while attacking
~2/3 of the GF cost).

Form per candidate:
  x = v ^ k
  3 stages: 2 d-constrained ANDs (d in {1..5,59..63}) then
            x ^= rotl(x,p) ^ rotl(x,q)   [cheap linear, (p,q) per candidate]
  x = gf_mul(x, 0x94D049BB133111EB)      [ONE GF mult at END]
  x ^= rotl(k,13)

Gates per candidate (all must pass for KEEP):
  (a) sequential-affinity pre-check: and_layer_rank >= 8 per AND
  (b) mechanism re-check: full 64-seq rank >= 62 on the NEW form
  (c) Fisher triage: lin_diff.screen_lin_diff verbatim (S1 gate's own rule),
      KEEP iff LIN PASS and DIFF PASS (0 Holm rejections, both families)

N=300, seeded RNG (0xB200). JSONL checkpoint per candidate, resumable.
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
from triage_core import check_canaries
from screen_lib import KEYS, N
from lin_diff import screen_lin_diff

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
DSET = [1, 2, 3, 4, 5, 59, 60, 61, 62, 63]
P_GF = 0x94D049BB133111EB  # al_w3p_a's P: rank-63, full battery+Q1 pass (DESIGN.md)
N_CAND = 300
SEED = 0xB200
HB = "/home/hatch/workspace/mix/exploration/adder_lat/supervisor_heartbeat.txt"
JSONL = os.path.join(HERE, "b2sparse_screen.jsonl")
KEYS10 = [int(k) for k in KEYS[:10]]
DRAW_CAP = 10000  # fail-loud cap on stochastic draw loops (b45 lesson)


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def gf_mul_np(x, C):
    """Vectorized carry-free multiply by constant C (verbatim from
    fast_battery/candidates/al_w3p_a/model.py::_gf)."""
    res = np.zeros(np.shape(x), dtype=np.uint64)
    p = np.asarray(x, dtype=np.uint64).copy()
    c = int(C)
    while c:
        if c & 1:
            res ^= p
        hi = (p >> np.uint64(63)) & np.uint64(1)
        p = ((p << np.uint64(1)) & M64) ^ (hi * np.uint64(0x1B))
        c >>= 1
    return res & M64


def b2_model(V, key, stages, pq):
    """V: array-like; stages: 3 x [(a,b),(a,b)]; pq: (p,q) linear diffusion."""
    K = np.full(np.shape(V), np.uint64(key), dtype=np.uint64)
    p, q = pq
    x = (np.asarray(V, dtype=np.uint64) ^ K) & M64
    for ands in stages:
        for a, b in ands:
            x = (x ^ (rotl(x, a) & rotl(x, b))) & M64
        x = (x ^ rotl(x, p) ^ rotl(x, q)) & M64
    x = gf_mul_np(x, P_GF)
    return (x ^ rotl(K, 13)) & M64


def gf2_rank(rows64):
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
    V = np.arange(64, dtype=np.uint64)
    g = (V ^ (rotl(V, a) & rotl(V, b))) & M64
    return gf2_rank([int(v) for v in g])


def full_rank(stages, pq):
    V = np.arange(64, dtype=np.uint64)
    y = b2_model(V, int(KEYS10[0]), stages, pq)
    return gf2_rank([int(v) for v in y])


def fisher_triage(stages, pq, tag):
    """S1 gate's own rule, verbatim. Returns (keep, lin_v, diff_v, nrej)."""
    V = np.arange(N, dtype=np.uint64)
    seq = {}
    for key in KEYS10:
        seq[key] = b2_model(V, key, stages, pq).astype(np.uint64)
    res = screen_lin_diff(seq, verbose=False)
    nrej = len(res["lin_rejected"]) + len(res["diff_rejected"])
    keep = (res["lin_verdict"] == "PASS" and res["diff_verdict"] == "PASS")
    return keep, res["lin_verdict"], res["diff_verdict"], nrej


def heartbeat(msg):
    with open(HB, "a") as f:
        f.write("%s b2sparse-screen: %s\n" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), msg))


def gen_schedule(rng):
    stages = []
    for _ in range(3):
        ands = []
        for _ in range(2):
            a = int(rng.integers(0, 64))
            d = DSET[int(rng.integers(0, len(DSET)))]
            ands.append((a, (a + d) % 64))
        stages.append(ands)
    # (p,q): distinct non-zero rotations, drawn per candidate
    it = 0
    while True:
        it += 1
        if it > DRAW_CAP:
            print("DRAW-LOOP-FAIL (p,q)", flush=True)
            sys.exit(3)
        p = int(rng.integers(1, 64))
        q = int(rng.integers(1, 64))
        if p != q:
            return stages, (p, q)


def calibrate():
    """1. al_w3p_a (S1-clean, full battery+Q1 pass) under the Fisher triage
    must KEEP — validates the instrument on the word-AND family (same as W3'').
    2. (p,q) discrimination self-check ON THE b2 FORM: the W3'' smoke test
    found (29,36)->fr 57 (bad) and (57,1)->fr 63 (good); the rank probe must
    discriminate on this form too. A dummy all-zero (a,b) schedule is used —
    the probe isolates the (p,q) contribution."""
    sys.path.insert(0,
        "/home/hatch/workspace/mix/exploration/fast_battery/candidates/al_w3p_a")
    import model as w3p_a
    V = np.arange(N, dtype=np.uint64)
    seq = {}
    for key in KEYS10:
        seq[key] = w3p_a.mix_np(V, int(key))
    res = screen_lin_diff(seq, verbose=False)
    ok1 = (res["lin_verdict"] == "PASS" and res["diff_verdict"] == "PASS")
    print("CALIB-1 al_w3p_a: lin=%s diff=%s -> %s" %
          (res["lin_verdict"], res["diff_verdict"], "KEEP" if ok1 else "kill"),
          flush=True)
    # discrimination self-check: al_w3p_a's real AND schedule, vary (p,q).
    # (A degenerate fixed-(0,1) AND stack collapses rank to ~7-11 no matter
    # the (p,q) — it cannot isolate the linear layer. Use the proven schedule.)
    a_stages = w3p_a.STAGES
    fr_bad = full_rank(a_stages, (29, 36))
    fr_good = full_rank(a_stages, (57, 1))
    ok2 = (fr_bad < 62 and fr_good == 63)
    print("CALIB-2 (p,q) discrimination on b2 form: (29,36)->fr=%d "
          "(expect <62), (57,1)->fr=%d (expect 63) -> %s" %
          (fr_bad, fr_good, "PASS" if ok2 else "FAIL"), flush=True)
    return ok1 and ok2


def main():
    t_start = time.time()
    heartbeat("screen start N=%d seed=%#x" % (N_CAND, SEED))
    print("=== canary gate ===", flush=True)
    if not check_canaries():
        heartbeat("ABORT: canary gate FAILED")
        print("CANARY GATE FAILED - aborting", flush=True)
        sys.exit(2)
    heartbeat("canary gate PASS")
    print("=== calibration (al_w3p_a + (p,q) discrimination) ===", flush=True)
    if not calibrate():
        heartbeat("ABORT: calibration FAILED")
        print("CALIBRATION FAILED - aborting", flush=True)
        sys.exit(2)
    heartbeat("calibration PASS")

    rng = np.random.default_rng(SEED)
    done = 0
    if os.path.exists(JSONL):
        with open(JSONL) as f:
            done = sum(1 for _ in f if _.strip())
        print("resuming: %d already done" % done, flush=True)
    # regenerate the same candidate stream and skip `done`
    cands = [gen_schedule(rng) for _ in range(N_CAND)]
    cands = cands[done:]

    out = open(JSONL, "a")
    n_keep = 0
    for idx, (stages, pq) in enumerate(cands, start=done):
        rec = {"idx": idx, "stages": stages, "pq": pq}
        # (a) sequential-affinity pre-check
        aff_fail = None
        for si, ands in enumerate(stages):
            for ai, (a, b) in enumerate(ands):
                if and_layer_rank(a, b) < 8:
                    aff_fail = (si, ai, a, b)
                    break
            if aff_fail:
                break
        if aff_fail:
            rec.update({"affine_and": aff_fail, "verdict": "REJECT-affine"})
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print("[%03d] REJECT-affine AND %s" % (idx, aff_fail), flush=True)
            continue
        # (b) mechanism re-check: full rank on the NEW form
        fr = full_rank(stages, pq)
        if fr < 62:
            rec.update({"full_rank": fr, "verdict": "kill-rank"})
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print("[%03d] kill-rank fr=%d" % (idx, fr), flush=True)
            continue
        # (c) Fisher triage (S1 gate's own rule)
        keep, lin_v, diff_v, nrej = fisher_triage(stages, pq, idx)
        verdict = "KEEP" if keep else "kill"
        if keep:
            n_keep += 1
        rec.update({"full_rank": fr, "lin": lin_v, "diff": diff_v,
                    "n_reject": nrej, "verdict": verdict})
        out.write(json.dumps(rec) + "\n")
        out.flush()
        print("[%03d] %s fr=%d lin=%s diff=%s nrej=%d" %
              (idx, verdict, fr, lin_v, diff_v, nrej), flush=True)
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
