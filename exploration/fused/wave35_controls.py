#!/usr/bin/env python3
"""Wave-35 POSITIVE CONTROLS (committed; fail-loud).

Run BEFORE trusting any wave-35 screen result. Verifies the triage pipeline:
  CONTROL-PASS: t6_b33c (frontier, known triage z=3.3) -> SEQ exact-DIFF
      max|z| < 10 across all 10 keys. If this fails, the pipeline is broken.
  CONTROL-KILL: wave-34 V0 try-1 (linear cross term; adjudicated CONFIRMED
      deterministic skeleton) -> SEQ exact-DIFF max|z| >= 10. If this fails
      (i.e. the screen calls V0 clean), the screen is vacuous and no KEEP
      from it may be trusted.

Exit 0 = both controls behave as known; exit != 0 = pipeline untrusted.
"""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from wave35_lib import seq_exact_diff, KEYS10
from wave34_probe import make_stages as v0_stages, make_mix as v0_mix
import random

B33C_STAGES = [(25, 45, 42), (44, 14, 26), (51, 54, 34),
               (41, 53, 51), (54, 40, 6), (12, 15, 11)]
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def b33c_mix(xs, K):
    xs = np.asarray(xs, dtype=np.uint64); K = np.asarray(K, dtype=np.uint64)
    x = (xs ^ K) & M64
    for a, b, c in B33C_STAGES:
        x = (x ^ (_rotl(x, a) & _rotl(x, b)) ^ _rotl(x, c)) & M64
    return (x ^ _rotl(K, 13)) & M64


def main():
    ok = True
    # CONTROL-PASS: b33c must KEEP
    z_pass, cfg = seq_exact_diff(b33c_mix)
    print(f"CONTROL-PASS b33c: max|z|={z_pass:.2f} (worst key {cfg:#x})", flush=True)
    if not (0.0 < z_pass < 10.0):
        print("CONTROL-PASS FAILED: b33c not KEEP -> pipeline untrusted", flush=True)
        ok = False
    # CONTROL-KILL: wave-34 V0 try-1 must KILL
    rng = random.Random(0x34 ^ 0xA0)
    stages = v0_stages("V0", 3, rng)  # try-1
    v0 = v0_mix("V0", stages)
    z_kill, cfg = seq_exact_diff(v0)
    print(f"CONTROL-KILL V0 try-1: max|z|={z_kill:.2f} (worst key {cfg:#x})", flush=True)
    if not (z_kill >= 10.0):
        print("CONTROL-KILL FAILED: V0 not KILL -> screen vacuous, untrusted", flush=True)
        ok = False
    print("CONTROLS " + ("PASS" if ok else "FAIL"), flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
