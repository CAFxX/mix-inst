#!/usr/bin/env python3
"""Batch-45 PILOT: true chi S-box as the repeated STAGE (track 6).
Trigger: batch-44 COMPLETED 2026-10-11T10:15:06Z -- andorM5 0/40
(5-stage wall = sequential nonlinear depth, NOT tap count), andorM6
2/40 quality-ok but S0 cost-killed 22.0/22.9u. Sparse secondary-gate
space FULLY MAPPED -- the next lever must be elsewhere.

De-dup (grep-verified 2026-10-11, DESIGN.md):
- b42 chi3/chi5lanes: TRUE chi S-box but as a SINGLE FINAL layer on a
  5st AND cascade (0/40, min 40-61) -- position is final, not stage.
- b8 fchi6a `x ^ (ra & ~rb)`: sparse masked form, not the 3-input
  S-box; S1-killed (z 47k-160k).
- b8 het5a: sparse "chi" op r0^(r1&~r2) + per-stage rk; S0 25.2u
  dominated. Different op AND key schedule.
- b4 chi3col8/10: chi_3 as full-cipher round function (43.3u).
- directed_design batch-9 "keccak": sparse `x^(ra&~rb)^rc`, not the S-box.
- fused fz24_g/h: per-NIBBLE (4-bit) chi 5-stage -- NEVER SCREENED
  (zero hits in supervisor.log/wave24*.log); lane width 4 is provably
  non-bijective (b42 proof) vs bijective chi_3 here; different wiring.
  OPEN follow-up, not a duplicate. See DESIGN.md.
- No batch screened a true chi S-box as the repeated stage of a
  masked cascade (pre-whiten + final whiten, no per-stage rk).

Co-design rationale:
- The wall is sequential nonlinear depth. Sparse AND stages contribute
  depth only through the AND corner (killkey 0x0 dominates every killed
  arm); a chi stage has NO sparse corner -- every output bit is
  nonlinearly active on every input (dense degree-2, DU-optimal 2^-2,
  bijective). Per stage of depth, chi carries strictly more effective
  nonlinearity than a sparse AND stage.
- Cost thesis (gate count; S0 decides): per bit 1xAND2+3xXOR2+1xINV vs
  the frontier stage's 1xAND2+2xXOR2 (3.3u/stage measured) -- projected
  ~4.3-4.8u/stage. 4st ~= 17-19u (plausibly <19.3u); 5st ~= 21.5-24u
  (mechanism probe only).

Forms (x ^= k pre-whiten; S = cascade ^ rotl(k,13) final, same frame as
b33c/b41/b43/b44):
  chiS4: stage(x,a,b) = chi3(x) ^ rotl(chi3(x),a) ^ rotl(chi3(x),b) (4x)
  chiS5: same (5x)
chi3 = chi_3 on 21 contiguous 3-bit lanes (bits 0..62), bit 63 identity
-- the exact b42 lane geometry; bijectivity asserted fail-loud.

Cuts (defensible reason at each cut site; see DESIGN.md):
- chi_5 lanes: CUT from pilot (lane-width follow-up; re-test trigger =
  any chiS KEEP).
- 6st: CUT on measured cost (6x~4.5u ~= 27u > 19.3u).
- 3st: CUT (structurally below the wall).
- Per-stage round key: CUT on measured cost (b8 het5a 5.0u/stage).
- Fused x-enters-nonlinearly: CUT on evidence (b8 fchi6a S1-killed).
- Hetero chi+AND interleave: CUT from pilot (muddies the mechanism);
  queued as cost follow-up if chiS-5 keeps.
- LIN proxy triage: N/A (b39/b40/b41/b44 precedent).

Method = validated triage: EXACT S1 DIFF via lin_diff.diff_cell_logps,
10 keys, sequential inputs N=2^18. KEEP bar max|z|<10. Positive control:
and1/b33c 6-stage must give z=3.3 (fail-loud, run `calibrate` first).
KEEP schedules appended to JSONL IMMEDIATELY per-try (b39 lesson).

Pre-registered kill rule: 0/40 keeps on an arm with min orders of
magnitude above bar -> arm closed, mechanism refuted for that stage
count (scoped). Both arms dead -> dense-S-box-stage hypothesis
FALSIFIED; next axis per the widen directive.

Escalation (pre-registered): any KEEP -> bundle gen bit-exact 2000/2000
-> S0 via run_synth.py (bar strictly <19.3u MEASURED, XCHECK clean) on
a STRATIFIED sample of keeps (triage z does not rank S0 within a form)
-> S1 FAIL-FAST on the first cost-eligible keep (exact-DIFF triage is
blind to the marginal/inner-DIFF kills) -> survivors staged battery
S1->S2->S3->S4->Q1 (b33 playbook).

Usage: t6_b45_screen.py <form> <n_try> <seed> [keep_jsonl]
  form: chiS4 | chiS5 | and1 (calibration only)
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


# b42 lane geometry, verbatim: 21 contiguous 3-bit lanes, bit 63 identity.
CHI3_LUT = np.array([_chi_scalar(v, 3) for v in range(8)], dtype=np.uint64)
assert len(set(CHI3_LUT.tolist())) == 8, "chi_3 must be bijective"


def chi3(x):
    y = x & np.uint64(0x8000000000000000)  # bit 63 passthrough
    for j in range(21):
        lane = ((x >> np.uint64(3 * j)) & np.uint64(0x7)).astype(np.uint64)
        y |= CHI3_LUT[lane] << np.uint64(3 * j)
    return y & M64


def apply_stage(form, x, a, b, c=None):
    if form in ("chiS4", "chiS5"):
        y = chi3(x)
        return (y ^ rotl(y, a) ^ rotl(y, b)) & M64
    if form == "and1":
        # b33c stage form, verbatim (b44 calibration): x ^= (ra&rb) ^ rc
        return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    raise ValueError(form)


def eval_sched(form, stages):
    V = np.arange(N, dtype=np.uint64)
    worst = 0.0
    worst_key = None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        x = (V ^ K) & M64
        for s in stages:
            x = apply_stage(form, x, *s)
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
    return eval_sched("and1", [(a, b, c) for a, b, c in B33C_SCHED])[0]


def draw_stage(rng):
    while True:
        a = int(rng.integers(1, 64))
        b = int(rng.integers(1, 64))
        if a != b:
            break
    return (a, b)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        wz = eval_calib()
        print("CALIBRATION and1/b33c: maxworst|z|=%.1f (expect 3.3)" % wz,
              flush=True)
        sys.exit(0 if abs(wz - 3.3) < 0.05 else 1)
    form = sys.argv[1]
    assert form in ("chiS4", "chiS5"), form
    nstages = 4 if form == "chiS4" else 5
    n_try = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    seed = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xB451
    keep_path = sys.argv[4] if len(sys.argv) > 4 else None
    rng = np.random.default_rng(seed)
    keep = []
    kills = 0
    for t in range(n_try):
        stages, seen = [], set()
        draws = 0
        while len(stages) < nstages:
            s = draw_stage(rng)
            draws += 1
            if draws > 10000:
                # Fail LOUD, never hang silently: a draw loop that cannot
                # fill nstages in 10000 draws is a harness bug (b45 lesson:
                # a dropped stages.append(s) spun forever at 25% CPU with
                # zero log output).
                print("DRAW-LOOP-FAIL: could not fill %d stages in 10000 "
                      "draws (try %d)" % (nstages, t), flush=True)
                sys.exit(3)
            if s in seen:
                continue
            seen.add(s)
            stages.append(s)
        assert all(s[0] != s[1] for s in stages), "degenerate draw"
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
