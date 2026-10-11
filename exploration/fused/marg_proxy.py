#!/usr/bin/env python3
"""Targeted marginal proxy for wave-30 axis B (fz27_h repair co-design).

Replicates EXACTLY the two cells that killed fz27_h (19.9u, S1-FLAG):
  PB: SINGLE-BIT scenario (64 inputs), key=0xffffffffffffffff -> 64 per-bit
      monobit z -> Fisher combined logp (chi2 df=128)
  RD: SEQ scenario, key=0x5555555555555555, N outputs -> 9 reduction logps
      (lemire x3, mask8, mask32(chi2lo,chi2hi,coll), mod x2) -> Fisher (df=18)

Verdict vs the Holm bar of the FULL screen (PB M=320, RD M=20, alpha=0.01):
  PB bar: ln(0.01)-ln(320) = -10.37 ; RD bar: ln(0.01)-ln(20) = -7.60.
A candidate is marginal-proxy-clean iff pb_logp > PB_BAR + MARGIN and
rd_logp > RD_BAR + MARGIN. Calibrated against fz24_o (pass) and fz27_h
(fail) before use.

Usage: marg_proxy.py <stages-expr> [logN_rd]  -- stages-expr is a Python
literal list of (kind, rots) tuples evaluated with no builtins.
"""
import math, sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from screen_lib import lemire_z, mask_z, mask32_z, mod_z, chi2_z
from screen_cal import perbit_zarray, logp_twosided_normal, fisher_logp
from wave24_proxy import apply_stage, M64

PB_BAR = math.log(0.01) - math.log(320)
RD_BAR = math.log(0.01) - math.log(20)
MARGIN = 2.0  # required clearance above the bar (log-p units)

def mix_np_fn(stages):
    def mix_fn(xs, K):
        x = (np.asarray(xs, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)) & M64
        for st in stages:
            x = apply_stage(x, st)
        return x
    return mix_fn

def _reduction_logps(S):
    lps = []
    for X in (10, 1000, 4294967296):
        lps.append(logp_twosided_normal(lemire_z(S, X)))
    w = (np.asarray(S, dtype=np.uint64) & np.uint64(0xFFFFFFFF)).astype(np.int64)
    lps.append(logp_twosided_normal(mask_z(S, 8)))
    lo = w & 0xFFFF
    hi = (w >> 16) & 0xFFFF
    n = S.shape[0]
    lps.append(logp_twosided_normal(chi2_z(np.bincount(lo, minlength=1 << 16).astype(float), n)))
    lps.append(logp_twosided_normal(chi2_z(np.bincount(hi, minlength=1 << 16).astype(float), n)))
    _, counts = np.unique(w, return_counts=True)
    coll = int(((counts * (counts - 1)) // 2).sum())
    exp_coll = (n * (n - 1) / 2) / (1 << 32)
    lps.append(logp_twosided_normal((coll - exp_coll) / math.sqrt(exp_coll)))
    for y in (7, 1000):
        lps.append(logp_twosided_normal(mod_z(S, y)))
    assert len(lps) == 9, len(lps)
    return lps

def marg_proxy(stages, logN_rd=18, verbose=True):
    mix_fn = mix_np_fn(stages)
    # PB cell: SINGLE-BIT, key 0xff..ff
    V = (np.uint64(1) << np.arange(64, dtype=np.uint64))
    K = np.full(64, np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64)
    S = mix_fn(V, K)
    zs = perbit_zarray(S)
    pb_logp = fisher_logp([logp_twosided_normal(z) for z in zs])
    # RD cell: SEQ, key 0x55..55
    n = 1 << logN_rd
    V = np.arange(n, dtype=np.uint64)
    K = np.full(n, np.uint64(0x5555555555555555), dtype=np.uint64)
    S = mix_fn(V, K)
    rd_logp = fisher_logp(_reduction_logps(S))
    pb_ok = pb_logp > PB_BAR + MARGIN
    rd_ok = rd_logp > RD_BAR + MARGIN
    if verbose:
        print(f"pb_logp={pb_logp:.2f} (bar {PB_BAR:.2f}+{MARGIN} -> {'OK' if pb_ok else 'REJ'}) "
              f"worst_perbit_z={zs.max():.2f}", flush=True)
        print(f"rd_logp={rd_logp:.2f} (bar {RD_BAR:.2f}+{MARGIN} -> {'OK' if rd_ok else 'REJ'})", flush=True)
    return pb_ok and rd_ok, pb_logp, rd_logp

if __name__ == "__main__":
    stages = eval(sys.argv[1], {"__builtins__": {}})
    logN = int(sys.argv[2]) if len(sys.argv) > 2 else 18
    ok, p, r = marg_proxy(stages, logN)
    print("MARG_PROXY:", "PASS" if ok else "FLAG")
