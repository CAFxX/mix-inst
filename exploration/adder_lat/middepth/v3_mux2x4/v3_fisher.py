#!/usr/bin/env python3
"""V3 Fisher triage: screen_lin_diff verbatim on the 4-stage MUX2 network.

Usage: v3_fisher.py [stages.json] [label]
  stages.json omitted -> BASE_STAGES.
Prints per-key LIN/DIFF details and the final verdict.
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
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/sbox_screen/het8")

from lin_diff import screen_lin_diff  # noqa: E402
from screen_lib import KEYS, N  # noqa: E402
import v3_model as M  # noqa: E402

KEYS10 = [int(k) for k in KEYS]


def main():
    if len(sys.argv) > 1:
        stages = [tuple(st) for st in json.load(open(sys.argv[1]))]
        label = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
    else:
        stages = M.BASE_STAGES
        label = "BASE"
    print(f"V3 Fisher triage: {label} stages={stages}", flush=True)
    t0 = time.time()
    seq = M.gen_seq(stages, KEYS10, N)
    print(f"seq gen: {time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    res = screen_lin_diff(seq, verbose=True)
    print(f"screen: {time.time()-t0:.1f}s", flush=True)
    print("VERDICT lin=%s diff=%s nrej_lin=%d nrej_diff=%d" % (
        res["lin_verdict"], res["diff_verdict"],
        len(res["lin_rejected"]), len(res["diff_rejected"])))
    json.dump({"label": label, "stages": stages,
               "lin_verdict": res["lin_verdict"], "diff_verdict": res["diff_verdict"],
               "nrej_lin": len(res["lin_rejected"]), "nrej_diff": len(res["diff_rejected"]),
               "lin_detail": res["lin_detail"], "diff_detail": res["diff_detail"]},
              open(f"fisher_{label}.json", "w"), indent=1)
    print(f"wrote fisher_{label}.json")


if __name__ == "__main__":
    main()
