#!/usr/bin/env python3
"""Widened marginal proxy (v2) for wave-30 repair co-design.

v1 (marg_proxy.py) checked only the 2 cells that killed fz27_h; fz30_d passed
v1 but failed the real screen on DIFFERENT cells (SINGLE-BIT x {0xaa,0x55},
PTR-j8 x 0x55). The marginal failure migrates across cells under perturbation
— whack-a-mole. v2 covers:
  PB: SINGLE-BIT scenario x all 10 KEYS (10 cells, 64 inputs each)
  RD: SEQ + PTR-j8 x all 10 KEYS at N=2^16 (20 cells; reduced N catches strong
      effects; the real s1_screen at N=2^18 remains the gate)

Verdict: FLAG if any cell's Fisher logp < full-screen Holm bar + margin
(PB bar -10.37, RD bar -7.60, margin 2.0). Using the full-screen bar on fewer
cells is conservative.

Calibrate: fz24_o -> PASS, fz27_h -> FLAG, fz30_d -> FLAG.
"""
import math, sys, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from screen_lib import KEYS, strided_distinct
from screen_cal import perbit_zarray, logp_twosided_normal, fisher_logp
from marg_proxy import _reduction_logps, M64
from wave24_proxy import apply_stage

PB_BAR = math.log(0.01) - math.log(320)
RD_BAR = math.log(0.01) - math.log(20)
MARGIN = 0.5  # small safety buffer; the full-screen bar on fewer cells is already conservative
LOGN_RD = 16

def marg_proxy2(stages, verbose=True):
    def mix_fn(xs, K):
        x = (np.asarray(xs, dtype=np.uint64) ^ np.asarray(K, dtype=np.uint64)) & M64
        for st in stages:
            x = apply_stage(x, st)
        return x
    worst = (float("inf"), None)  # (min logp - bar, cell)
    # PB cells
    Vsb = (np.uint64(1) << np.arange(64, dtype=np.uint64))
    for key in KEYS:
        K = np.full(64, np.uint64(key), dtype=np.uint64)
        zs = perbit_zarray(mix_fn(Vsb, K))
        lp = fisher_logp([logp_twosided_normal(z) for z in zs])
        m = lp - (PB_BAR + MARGIN)
        if m < worst[0]:
            worst = (m, f"PB SINGLE-BIT {key:#x} lp={lp:.1f}")
    # RD cells
    n = 1 << LOGN_RD
    for scen, vfn in (("SEQ", lambda: np.arange(n, dtype=np.uint64)),
                      ("PTR-j8", lambda: strided_distinct(0, 8, n))):
        V = vfn()
        for key in KEYS:
            K = np.full(n, np.uint64(key), dtype=np.uint64)
            lp = fisher_logp(_reduction_logps(mix_fn(V, K)))
            m = lp - (RD_BAR + MARGIN)
            if m < worst[0]:
                worst = (m, f"RD {scen} {key:#x} lp={lp:.1f}")
    ok = worst[0] > 0
    if verbose:
        print(f"marg2 {'PASS' if ok else 'FLAG'} worst_margin={worst[0]:+.1f} @ {worst[1]}",
              flush=True)
    return ok, worst

if __name__ == "__main__":
    stages = eval(sys.argv[1], {"__builtins__": {}})
    t0 = time.time()
    ok, worst = marg_proxy2(stages)
    print(f"MARG2: {'PASS' if ok else 'FLAG'} ({time.time()-t0:.0f}s)")
