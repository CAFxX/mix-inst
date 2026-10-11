#!/usr/bin/env python3
"""Batch-47 PILOT: "fewer, fatter stages" -- 3-stage dense-quadratic cascades
(track 6).

Trigger: batch-46 CLOSED (hetero 0/80, VALID). Batch-45's headline finding
reframes the wall: the 5-stage wall is SPARSE-specific (chiS5 40/40,
chiS4 10/40, but 5.77u/stage cost-closed). The dense wall's location is
unknown -- this batch probes it at 3 stages, where the cost thesis is live
(chi ~17.3u, maj ~14.7u, both < 19.3u).

Forms (x ^= k pre-whiten; S = cascade ^ rotl(k,13) final):
  chi3S3: 3x [y=chi3(x); x = y ^ rotl(y,a) ^ rotl(y,b)]   (prize arm)
  chi5S3: 3x [y=chi5(x); x = y ^ rotl(y,a) ^ rotl(y,b)]   (geometry control)
  maj3S3: 3x [x ^= maj(ra,rb,rc) ^ rd]                    (mechanism control)
chi3 = chi_3, 21 contiguous 3-bit lanes, bit 63 identity (b42/b45 verbatim).
chi5 = chi_5, 12 contiguous 5-bit lanes (bits 0..59), bits 60..63 identity
(b42 verbatim; bijectivity asserted fail-loud).
maj(a,b,c) = (a&b)|(a&c)|(b&c) (b5 t6_maj6 form, verbatim; S1-CAL_PASS at 6st).

De-dup (grep-verified 2026-10-11, DESIGN.md): no 3-stage chi repeated stage
anywhere; maj never below 6st (fused fmaj6a is a different construction);
chi_5 never as repeated stage.

Cuts (defensible reason at each cut site; see DESIGN.md): chi_4 CUT ON PROOF
(non-bijective); maj@4st/5st CUT on measured-cost projection; 3-stage sparse
CUT on mechanism (b37); per-stage rk CUT on cost; fused CUT on evidence;
Midori 3st CUT on evidence (wave-35/O39); LIN proxy N/A.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive control:
and1/b33c 6-stage must give z=3.3 (fail-loud, run `calibrate` first).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).
Fail-loud draw-loop cap (b45 lesson).

Pre-registered kill rule: 0/40 keeps on an arm with min orders of magnitude
above bar -> arm closed (scoped). All arms dead -> "fewer, fatter stages"
FALSIFIED for the tested dense primitives; next axis per widen directive.

Escalation (pre-registered): any KEEP -> bundle gen bit-exact 2000/2000
-> S0 via run_synth.py (bar strictly <19.3u MEASURED, XCHECK clean) on a
STRATIFIED sample of keeps (lesson a: triage z does not rank S0 within a
form) -> S1 FAIL-FAST on the first cost-eligible keep (lesson b: exact-DIFF
triage is blind to the S1 marginal/inner-DIFF kill) -> survivors staged
battery S1->S2->S3->S4->Q1 (b33 playbook).

Usage: t6_b47_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: chi3S3 | chi5S3 | maj3S3 | and1 (calibration only)
"""
import json
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def _chi_scalar(v, n):
    y = 0
    for k in range(n):
        vk = (v >> k) & 1
        v1 = (v >> ((k + 1) % n)) & 1
        v2 = (v >> ((k + 2) % n)) & 1
        y |= ((vk ^ ((1 ^ v1) & v2)) << k)
    return y


# b42 lane geometries, verbatim.
CHI3_LUT = np.array([_chi_scalar(v, 3) for v in range(8)], dtype=np.uint64)
assert len(set(CHI3_LUT.tolist())) == 8, "chi_3 must be bijective"
CHI5_LUT = np.array([_chi_scalar(v, 5) for v in range(32)], dtype=np.uint64)
assert len(set(CHI5_LUT.tolist())) == 32, "chi_5 must be bijective"


def chi3(x):
    y = x & np.uint64(0x8000000000000000)  # bit 63 passthrough
    for j in range(21):
        lane = ((x >> np.uint64(3 * j)) & np.uint64(0x7)).astype(np.uint64)
        y |= CHI3_LUT[lane] << np.uint64(3 * j)
    return y & M64


def chi5(x):
    y = x & np.uint64(0xF000000000000000)  # bits 60..63 passthrough
    for j in range(12):
        lane = ((x >> np.uint64(5 * j)) & np.uint64(0x1F)).astype(np.uint64)
        y |= CHI5_LUT[lane] << np.uint64(5 * j)
    return y & M64


def _maj(a, b, c):
    return ((a & b) | (a & c) | (b & c)) & M64


# Stage schedule: ("C3",a,b) chi_3 stage; ("C5",a,b) chi_5 stage;
# ("M",a,b,c,d) majority stage; ("and1",a,b,c) calibration only.
def apply_stage(x, st):
    if st[0] == "C3":
        _, a, b = st
        y = chi3(x)
        return (y ^ rotl(y, a) ^ rotl(y, b)) & M64
    if st[0] == "C5":
        _, a, b = st
        y = chi5(x)
        return (y ^ rotl(y, a) ^ rotl(y, b)) & M64
    if st[0] == "M":
        _, a, b, c, d = st
        return (x ^ _maj(rotl(x, a), rotl(x, b), rotl(x, c)) ^ rotl(x, d)) & M64
    if st[0] == "and1":
        _, a, b, c = st
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(st[0])


def eval_sched(stages):
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    worst_key = None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for st in stages:
            x = apply_stage(x, st)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_key = wz, key
    return worst, worst_key


# b33c schedule for the positive control (and1, 6 stages) -- verbatim
# from t6_b44_screen.py so the z=3.3 reproduction is exact.
B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]


def eval_calib():
    return eval_sched([("and1", a, b, c) for a, b, c in B33C_SCHED])[0]


STAGE_TAG = {"chi3S3": "C3", "chi5S3": "C5", "maj3S3": "M"}
N_STAGES = 3


def draw_stage(rng, typ):
    if typ in ("C3", "C5"):
        while True:
            a = int(rng.integers(1, 64))
            b = int(rng.integers(1, 64))
            if a != b:
                return (typ, a, b)
    # maj stage: a,b,c pairwise distinct (maj degenerates if any coincide:
    # maj(ra,ra,rb) = ra, linear). d free.
    while True:
        a = int(rng.integers(1, 64))
        b = int(rng.integers(1, 64))
        c = int(rng.integers(1, 64))
        d = int(rng.integers(1, 64))
        if len({a, b, c}) == 3:
            return ("M", a, b, c, d)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        wz = eval_calib()
        print("CALIBRATION and1/b33c: maxworst|z|=%.1f (expect 3.3) %s" %
              (wz, "PASS" if abs(wz - 3.3) < 0.05 else "FAIL"), flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    form = sys.argv[1]
    assert form in STAGE_TAG, form
    tag = STAGE_TAG[form]
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB471
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    for t in range(n_try):
        stages, seen = [], set()
        draws = 0
        while len(stages) < N_STAGES:
            draws += 1
            if draws > 10000:
                print("DRAW-LOOP-FAIL: try %d" % t, flush=True)
                sys.exit(3)
            st = draw_stage(rng, tag)
            if st in seen:
                continue
            seen.add(st)
            stages.append(st)
        if tag in ("C3", "C5"):
            assert all(s[1] != s[2] for s in stages), "degenerate chi draw"
        else:
            assert all(len({s[1], s[2], s[3]}) == 3 for s in stages), \
                "degenerate maj draw"
        wz, key = eval_sched(stages)
        flag = "KEEP" if wz < 10 else "kill"
        if wz >= 10:
            kills += 1
        print("try %3d maxworst|z|=%8.1f killkey=%#x %s" % (t, wz, key, flag),
              flush=True)
        if wz < 10:
            keep.append((wz, stages))
            if keep_path:
                with open(keep_path, "a") as f:
                    f.write(json.dumps({"z": wz,
                                        "stages": [list(s) for s in stages],
                                        "form": form, "seed": seed}) + "\n")
    print("=== %s: %d/%d KEEP (seed=%#x) ===" % (form, len(keep), n_try, seed),
          flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
