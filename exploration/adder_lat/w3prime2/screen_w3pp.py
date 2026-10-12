#!/usr/bin/env python3
"""W3'' screen: d-constrained 3-stage word-AND with CHEAP linear diffusion.

Co-design per adder_lat/w3prime2/DESIGN.md (cost autopsy: GF mults are ~90%
of W3' cost; the GF multiplier is LINEAR so a cheaper linear diffusion
preserves the nonlinearity budget).

Form per candidate:
  x = v ^ k
  3 stages: 2 d-constrained ANDs (d in {1..5,59..63}) then
            x ^= rotl(x,p) ^ rotl(x,q)   [was: x = gf_mul(x,P)]
  x ^= rotl(k,13)

Gates per candidate (all must pass for KEEP):
  (a) sequential-affinity pre-check: and_layer_rank >= 8 per AND
  (b) mechanism re-check: full 64-seq rank >= 62 on the NEW form
  (c) Fisher triage: lin_diff.screen_lin_diff verbatim (S1 gate's own rule),
      KEEP iff LIN PASS and DIFF PASS (0 Holm rejections, both families)

N=300, seeded RNG (0x5EED2). JSONL checkpoint per candidate, resumable.
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
N_CAND = 300
SEED = 0x5EED2
HB = "/home/hatch/workspace/mix/exploration/adder_lat/supervisor_heartbeat.txt"
JSONL = os.path.join(HERE, "w3pp_screen.jsonl")
KEYS10 = [int(k) for k in KEYS[:10]]
DRAW_CAP = 10000  # fail-loud cap on stochastic draw loops (b45 lesson)


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def w3pp_model(V, key, stages, pq):
    """V: array-like; stages: 3 x [(a,b),(a,b)]; pq: (p,q) linear diffusion."""
    K = np.full(np.shape(V), np.uint64(key), dtype=np.uint64)
    p, q = pq
    x = (np.asarray(V, dtype=np.uint64) ^ K) & M64
    for ands in stages:
        for a, b in ands:
            x = (x ^ (rotl(x, a) & rotl(x, b))) & M64
        x = (x ^ rotl(x, p) ^ rotl(x, q)) & M64
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
    y = w3pp_model(V, int(KEYS10[0]), stages, pq)
    return gf2_rank([int(v) for v in y])


def fisher_triage(stages, pq, tag):
    """S1 gate's own rule, verbatim. Returns (keep, lin_v, diff_v, nrej)."""
    V = np.arange(N, dtype=np.uint64)
    seq = {}
    for key in KEYS10:
        seq[key] = w3pp_model(V, key, stages, pq).astype(np.uint64)
    res = screen_lin_diff(seq, verbose=False)
    nrej = len(res["lin_rejected"]) + len(res["diff_rejected"])
    keep = (res["lin_verdict"] == "PASS" and res["diff_verdict"] == "PASS")
    return keep, res["lin_verdict"], res["diff_verdict"], nrej


def heartbeat(msg):
    with open(HB, "a") as f:
        f.write("%s w3pp-screen: %s\n" % (
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
    """Positive control: al_w3p_a (S1-clean, full battery+Q1 pass) must KEEP
    under the Fisher triage. Validates the instrument on the word-AND family."""
    sys.path.insert(0,
        "/home/hatch/workspace/mix/exploration/fast_battery/candidates/al_w3p_a")
    import model as w3p_a
    V = np.arange(N, dtype=np.uint64)
    seq = {}
    for key in KEYS10:
        # vectorized (bit-exact vs the scalar loop: mix() == int(mix_np(scalar))
        # per model.py; the scalar loop costs ~75 min for 10 keys, mix_np ~s)
        seq[key] = w3p_a.mix_np(V, int(key))
    res = screen_lin_diff(seq, verbose=False)
    ok = (res["lin_verdict"] == "PASS" and res["diff_verdict"] == "PASS")
    print("CALIB al_w3p_a: lin=%s diff=%s -> %s" %
          (res["lin_verdict"], res["diff_verdict"], "KEEP" if ok else "kill"),
          flush=True)
    return ok


def main():
    t_start = time.time()
    heartbeat("screen start N=%d seed=%#x" % (N_CAND, SEED))
    print("=== canary gate ===", flush=True)
    if not check_canaries():
        heartbeat("ABORT: canary gate FAILED")
        print("CANARY GATE FAILED - aborting", flush=True)
        sys.exit(2)
    heartbeat("canary gate PASS")
    print("=== fisher calibration (al_w3p_a) ===", flush=True)
    if not calibrate():
        heartbeat("ABORT: fisher calibration FAILED (al_w3p_a not KEEP)")
        print("FISHER CALIBRATION FAILED - aborting", flush=True)
        sys.exit(2)
    heartbeat("fisher calibration PASS")

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
