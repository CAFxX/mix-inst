#!/usr/bin/env python3
"""Direction-2 Fisher triage: screen_lin_diff VERBATIM on the bit-Feistel.

Usage: d2_fisher.py <form> <tapsA> <tapsB> <rounds> [label]
  form: 1a | 2a | 3a   (ANDs per bit)
Positive control: MU5-324 (expected lin=PASS diff=PASS nrej=0/0).
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")

from lin_diff import screen_lin_diff  # noqa: E402
from screen_lib import KEYS, N  # noqa: E402
import d2_model as M  # noqa: E402
from d2_sweep import apply2  # noqa: E402
from d2_sweep2 import apply3  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


def gen_seq(form, tapsA, tapsB, rounds, keys, n):
    seq = {}
    V = np.arange(n, dtype=np.uint64)
    for key in keys:
        K = np.uint64(key)
        if form == "1a":
            S = M.apply(V, rounds, K, tapsA, tapsB)
        elif form == "2a":
            S = apply2(V, rounds, K, tapsA, tapsB)
        else:
            S = apply3(V, rounds, K, tapsA)
        seq[key] = S.astype(np.uint64)
    return seq


def main():
    form, tapsA, tapsB = sys.argv[1], sys.argv[2], sys.argv[3]
    rounds = int(sys.argv[4])
    label = sys.argv[5] if len(sys.argv) > 5 else f"d2_{form}_r{rounds}"
    tapsA = tuple(int(v) for v in tapsA.split(","))
    tapsB = tuple(int(v) for v in tapsB.split(","))
    keys10 = [int(k) for k in KEYS]
    print(f"D2 Fisher triage: {label} form={form} tapsA={tapsA} "
          f"tapsB={tapsB} rounds={rounds}", flush=True)
    t0 = time.time()
    seq = gen_seq(form, tapsA, tapsB, rounds, keys10, N)
    print(f"seq gen: {time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    res = screen_lin_diff(seq, verbose=True)
    print(f"screen: {time.time()-t0:.1f}s", flush=True)
    print("VERDICT lin=%s diff=%s nrej_lin=%d nrej_diff=%d" % (
        res["lin_verdict"], res["diff_verdict"],
        len(res["lin_rejected"]), len(res["diff_rejected"])))
    json.dump({"label": label, "form": form, "tapsA": tapsA, "tapsB": tapsB,
               "rounds": rounds,
               "lin_verdict": res["lin_verdict"],
               "diff_verdict": res["diff_verdict"],
               "nrej_lin": len(res["lin_rejected"]),
               "nrej_diff": len(res["diff_rejected"]),
               "lin_detail": res["lin_detail"],
               "diff_detail": res["diff_detail"]},
              open(f"fisher_{label}.json", "w"), indent=1)
    print(f"wrote fisher_{label}.json")


if __name__ == "__main__":
    main()
