#!/usr/bin/env python3
"""Batch-42 PILOT: odd-width (bijective) chi FINAL on a 5-stage AND-rotation
cascade (track 6). Direct answer to the standing challenge on batch-31:
"How do you know that no variant would pass S1?" -- batch-31's chi64-final
kill rested on chi_64 being non-bijective (PROVEN: chi_n bijective iff n
odd; chi_4: 16->12, chi_6: 64->56, verified by exhaustion). Odd-width chi
is bijective and was NEVER screened as a final layer. This pilot tests it.

De-dup (grep-verified 2026-10-11 across new_constructions/, hybrid/batch21/,
fused/):
- batch-31 chif4a/5a/5b: 4/5-stage AND + chi64-final -- S1 DIFF-killed
  catastrophically (worst|z| ~5000-7000). Mechanism: even-width
  non-bijectivity (proof, not samples). This pilot's ONLY delta is
  chi64 -> odd-width bijective chi lanes.
- batch-4 t6_chi3col8/10: chi_3 as the ROUND function of an 8-10 round
  full cipher -- killed on S0 COST (43.3u). Different construction
  (full cipher vs single final layer), different cost class.
- batch-3 ascon5: 5-bit S-box full cipher -- different construction.
- No hybrid batch, no fused wave ever screened an odd-chi final on an
  AND cascade.

Co-design rationale:
- The 5-stage AND cascade ALONE is DIFF-dead (b22: 0/200, min z=179.5)
  -- weak differentials, not destroyed ones.
- Batch-31's chi64-final made it CATASTROPHICALLY worse (z~5000+),
  consistent with the non-bijective final actively collapsing
  differentials. A bijective final CANNOT collapse differentials.
- Keccak-chi is a degree-2, DU-optimal (2^-2 per S-box) local
  nonlinearity. Hypothesis: one bijective chi layer repairs the
  cascade's weak differentials below the z<10 bar.
- Falsifier built in: if pilot z centers near the bare-5st baseline
  (~179), the wall lives in the cascade and no final repairs it --
  informative kill, close the "final-repair" hypothesis (scoped).
- Cost thesis: 5st x ~3.3u = 16.5u + chi layer (~AND2+XOR2+INV per bit,
  ~2 LUT levels, est 1.5-2.5u) ~= 18-19u < 19.8u. Measured S0 decides
  (b33 playbook); triage z does NOT rank S0 within a form (b40/b41
  lesson) -> S0 the top-2 keeps per arm on any KEEP (spread settlement).
- Exact-DIFF triage is blind to the S1 marginal/inner-DIFF gate
  (track-5/8 lesson): a triage KEEP that dies at S1 marginal kills the
  SCHEDULE, not the form. The b33 playbook's S1 battery is the gate.

Forms (x = andcascade_5st(v^k); S = chi_final(x) ^ rotl(k,13),
matching batch-31's structure so the only delta is the final):
  chi5f5: chi_5 on 12 contiguous 5-bit lanes (bits 0..59), identity 60..63
  chi3f5: chi_3 on 21 contiguous 3-bit lanes (bits 0..62), identity bit 63
  and5:   bare 5-stage cascade + post-whiten (CONTROL: verifies the
          harness sees the 5-stage wall; gives the repair baseline)
Cuts (each with reason):
- 6 stages excluded: 6x3.3 + final ~= 22u, cost-doomed over the bar.
- Lane geometry fixed contiguous: cascade rotations already diffuse;
  lane permutation is a follow-up variable if the pilot shows life.
- a==b excluded fail-loud: affine collapse (proof).
- Duplicate stage-tuples re-drawn (b41 precedent).
- LIN proxy N/A (pure rotation cascade; b39/b40/b41 precedent) -- the S1
  battery's LIN family gates escalation.

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive control:
and1/b33c 6-stage must give z=3.3 (fail-loud, run `calibrate` first).
Bijectivity of the chi LUTs asserted fail-loud (the axis's premise).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).

Usage: t6_b42_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: chi5f5 | chi3f5 | and5 (control) | and1 (calibration only)
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


# LUTs for the lane finals; bijectivity asserted fail-loud (axis premise).
CHI5_LUT = np.array([_chi_scalar(v, 5) for v in range(32)], dtype=np.uint64)
CHI3_LUT = np.array([_chi_scalar(v, 3) for v in range(8)], dtype=np.uint64)
assert len(set(CHI5_LUT.tolist())) == 32, "chi_5 must be bijective"
assert len(set(CHI3_LUT.tolist())) == 8, "chi_3 must be bijective"


def chi5_final(x):
    y = x & np.uint64(0xF000000000000000)  # bits 60..63 passthrough
    for j in range(12):
        lane = ((x >> np.uint64(5 * j)) & np.uint64(0x1F)).astype(np.uint64)
        y |= CHI5_LUT[lane] << np.uint64(5 * j)
    return y & M64


def chi3_final(x):
    y = x & np.uint64(0x8000000000000000)  # bit 63 passthrough
    for j in range(21):
        lane = ((x >> np.uint64(3 * j)) & np.uint64(0x7)).astype(np.uint64)
        y |= CHI3_LUT[lane] << np.uint64(3 * j)
    return y & M64


def apply_stage(x, a, b, c):
    return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64


def eval_sched(form, stages):
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    worst_key = None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for a, b, c in stages:
            x = apply_stage(x, a, b, c)
        if form == "chi5f5":
            x = chi5_final(x)
        elif form == "chi3f5":
            x = chi3_final(x)
        elif form == "and5":
            pass
        else:
            raise ValueError(form)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_key = wz, key
    return worst, worst_key


# b33c schedule for the positive control (and1, 6 stages)
B33C_SCHED = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
              (41, 53, 51), (54, 40, 6), (12, 15, 11)]


def eval_calib():
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for a, b, c in B33C_SCHED:
            x = apply_stage(x, a, b, c)
        S = ((x ^ rotl(K, 13)) & M64).astype(np.uint64)
        _, wz, _, _ = diff_cell_logps(S, key)
        worst = max(worst, wz)
    return worst


def draw_stage(rng):
    while True:
        a = int(rng.integers(1, 64))
        b = int(rng.integers(1, 64))
        if a != b:
            break
    return (a, b, int(rng.integers(1, 64)))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        wz = eval_calib()
        print("CALIBRATION and1/b33c: maxworst|z|=%.1f (expect 3.3)" % wz,
              flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    form = sys.argv[1]
    nstages = 5
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB42
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    assert form in ("chi5f5", "chi3f5", "and5"), form
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    for t in range(n_try):
        stages, seen = [], set()
        while len(stages) < nstages:
            s = draw_stage(rng)
            if s in seen:
                continue
            seen.add(s)
            stages.append(s)
        assert all(s[0] != s[1] for s in stages), "degenerate a==b draw"
        wz, key = eval_sched(form, stages)
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
    print("=== %s-%d: %d/%d KEEP (seed=%#x) ==="
          % (form, nstages, len(keep), n_try, seed), flush=True)
    if keep_path and keep:
        print("KEEP schedules -> %s" % keep_path, flush=True)
    if kills == 0 and len(keep) == n_try:
        print("GATE-FAIL: 0 kills -- harness may be vacuous", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
