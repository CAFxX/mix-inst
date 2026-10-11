#!/usr/bin/env python3
"""Wave-14 triage core: EXACT S1-DIFF triage (the b33 method), both domains.

- lin_diff.diff_cell_logps over V=arange(N) (sequential inputs, PRIMARY —
  the S1-DIFF methodology and the harsher domain per wave-34), all 10 keys.
- Secondary: random-64 domain (seed 0x14A11), same 10 keys.
- KEEP bar: max worst|z| < 10 on the sequential domain (calibrated gate).

Positive controls (run FIRST, before any candidate is trusted):
  KILL canary: as6_200_106 schedule -> expect z ~= 71.4 (exact-DIFF kill)
  KEEP canary: t6_b33b schedule   -> expect z ~= 3.0
  KEEP canary: al_and6a schedule  -> expect z ~ 3
"""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps, N_DIFF_PAIRS  # noqa: F401
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
BAR = 10.0

# Canary schedules (character-for-character from the program's records)
AS6_200_106 = [(24, 57, 5), (11, 45, 31), (8, 50, 4), (32, 23, 12),
               (31, 29, 6), (61, 20, 38)]                      # expect KILL z~71.4
T6_B33B = [(58, 53, 21), (52, 17, 18), (25, 23, 40), (54, 55, 13),
           (42, 33, 61), (53, 57, 29)]                          # expect KEEP z~3.0
AL_AND6A = [(1, 2, 13), (7, 19, 5), (3, 11, 29), (17, 31, 7),
            (11, 23, 37), (19, 41, 23)]                         # expect KEEP z~3


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def and6_form(V, key, stages):
    """The b33 stage form: pre-whiten; 6x x^=(ra&rb)^rc; final x^=rotl(k,13)."""
    K = np.full(V.shape, np.uint64(key), dtype=np.uint64)
    x = (V ^ K) & M64
    for a, b, c in stages:
        x = (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64
    return ((x ^ rotl(K, 13)) & M64).astype(np.uint64)


def exact_diff_worst(model_fn, V):
    """Max worst|z| over the 10 S1 keys. model_fn(V, key) -> uint64 array."""
    worst = 0.0
    worst_key = None
    for key in KEYS10:
        S = model_fn(V, key)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_key = wz, key
    return worst, worst_key


def triage(model_fn, tag):
    Vseq = np.arange(N, dtype=np.uint64)
    rng = np.random.default_rng(0x14A11)
    Vrnd = rng.integers(0, 2**64, size=N, dtype=np.uint64)
    wz_seq, k_seq = exact_diff_worst(model_fn, Vseq)
    wz_rnd, k_rnd = exact_diff_worst(model_fn, Vrnd)
    keep = wz_seq < BAR
    print(f"[{tag}] seq: maxworst|z|={wz_seq:8.1f} killkey={k_seq:#x} | "
          f"rnd64: maxworst|z|={wz_rnd:8.1f} killkey={k_rnd:#x} -> "
          f"{'KEEP' if keep else 'kill'}", flush=True)
    return keep, wz_seq, wz_rnd


def check_canaries():
    print("=== positive controls ===", flush=True)
    ok = True
    k1, z1s, z1r = triage(lambda V, k: and6_form(V, k, AS6_200_106),
                          "KILL-canary as6_200_106")
    if k1 or z1s < BAR:
        print(f"FAIL: kill canary not killed (KEEP={k1}, z_seq={z1s:.1f})")
        ok = False
    k2, z2s, z2r = triage(lambda V, k: and6_form(V, k, T6_B33B),
                          "KEEP-canary t6_b33b")
    if not k2:
        print(f"FAIL: b33b keep canary killed (z_seq={z2s:.1f})")
        ok = False
    k3, z3s, z3r = triage(lambda V, k: and6_form(V, k, AL_AND6A),
                          "KEEP-canary al_and6a")
    if not k3:
        print(f"FAIL: al_and6a keep canary killed (z_seq={z3s:.1f})")
        ok = False
    print("=== canaries %s ===" % ("PASS" if ok else "FAIL"), flush=True)
    if not ok:
        raise SystemExit("positive-control gate FAILED — harness not trusted")
    return True


if __name__ == "__main__":
    check_canaries()
