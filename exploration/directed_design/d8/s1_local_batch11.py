#!/usr/bin/env python3
"""D8: local S1 LIN+DIFF screen (real lin_diff code) for batch-11.

Runs screen_lin_diff on all 10 S1 KEYS (N=2^18) per candidate.
This is the exact LIN+DIFF portion of s1_screen.py, run locally to de-risk
before GHA submission. (Marginal PB/RD skipped; GHA S1 is the verdict.)
"""
import importlib.util
import json
import numpy as np
import os
import sys
import time

EXP = "/home/hatch/workspace/mix/exploration"
FB = EXP + "/fast_battery"
sys.path.insert(0, EXP)
sys.path.insert(0, FB + "/src")
from screen_lib import KEYS, N
from lin_diff import screen_lin_diff

CANDS = ["dd11_ccs_a", "dd11_css_a", "dd11_csc_a", "dd11_ccs_wa"]
WORK = EXP + "/directed_design/d8"


def load_candidate(cand):
    spec = importlib.util.spec_from_file_location(
        "model_" + cand, f"{FB}/candidates/{cand}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.mix_np


def main():
    keys = [int(k) for k in KEYS]
    summary = {}
    for cand in CANDS:
        mix_np = load_candidate(cand)
        t0 = time.time()
        seq = {}
        for k in keys:
            V = np.arange(N, dtype=np.uint64)
            seq[k] = np.asarray(mix_np(V, np.full(N, np.uint64(k), dtype=np.uint64)),
                                dtype=np.uint64)
        res = screen_lin_diff(seq, verbose=False)
        dt = time.time() - t0
        lin_rej = [str(c) for c in res["lin_rejected"]]
        diff_rej = [str(c) for c in res["diff_rejected"]]
        verdict = "CAL_PASS" if not lin_rej and not diff_rej else "FLAG"
        summary[cand] = {
            "verdict": verdict,
            "lin_rejected": lin_rej,
            "diff_rejected": diff_rej,
            "time_s": round(dt, 1),
        }
        print(f"[{cand}] LIN rej={len(lin_rej)} DIFF rej={len(diff_rej)} "
              f"-> {verdict} ({dt:.0f}s)", flush=True)
        # per-key detail
        for kk, vv in sorted(res["lin_detail"].items()):
            print(f"    LIN {kk}: D={vv['D']} logp={vv['logp']:.1f}", flush=True)
        for kk, vv in sorted(res["diff_detail"].items()):
            print(f"    DIFF {kk}: worst|z|={vv['worst_z']:.1f} "
                  f"flp={vv['fisher_logp']:.1f}", flush=True)
    json.dump(summary, open(f"{WORK}/s1_local_batch11.json", "w"), indent=1)
    print("wrote s1_local_batch11.json")


if __name__ == "__main__":
    main()
