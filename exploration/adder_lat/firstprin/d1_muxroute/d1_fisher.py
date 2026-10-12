#!/usr/bin/env python3
"""D1 Fisher triage: screen_lin_diff verbatim on the 2-stage D1-D network."""
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
import d1_model as M  # noqa: E402

KEYS10 = [int(k) for k in KEYS]


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "H"
    apply = {"D": M.apply_2stage, "H": M.apply_2stage_H}[which]
    print(f"D1 Fisher triage: 2-stage D1-{which}, 10 keys, N=2^18", flush=True)
    t0 = time.time()
    seq = M.gen_seq(KEYS10, N, apply)
    print(f"seq gen: {time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    res = screen_lin_diff(seq, verbose=True)
    print(f"screen: {time.time()-t0:.1f}s", flush=True)
    print("VERDICT lin=%s diff=%s nrej_lin=%d nrej_diff=%d" % (
        res["lin_verdict"], res["diff_verdict"],
        len(res["lin_rejected"]), len(res["diff_rejected"])))
    import json
    json.dump({"variant": which,
               "lin_verdict": res["lin_verdict"], "diff_verdict": res["diff_verdict"],
               "nrej_lin": len(res["lin_rejected"]), "nrej_diff": len(res["diff_rejected"]),
               "lin_detail": res["lin_detail"], "diff_detail": res["diff_detail"]},
              open(os.path.join(HERE, f"fisher_2stage_{which}.json"), "w"), indent=1)
    print(f"wrote fisher_2stage_{which}.json")


if __name__ == "__main__":
    main()
