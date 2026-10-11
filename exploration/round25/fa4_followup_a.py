#!/usr/bin/env python3
"""FA4(a): DIFF screen on near-zero keys for r25_spn_pba19_sb_midori_sb0_nw.
Also dumps per-delta logps at key=0x0 to identify the offending delta (for FA4(b)).
Cheap: ~4s per key for the DIFF family (N=2^18)."""
import importlib.util
import json
import math
import sys

import numpy as np

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP)
sys.path.insert(0, FB + "/src")
from screen_lib import N
from lin_diff import diff_cell_logps

CAND = "r25_spn_pba19_sb_midori_sb0_nw"
KEYS = [0x0, 0x1, 0x2, 0x4, 0x8000000000000000]


def load(cand):
    spec = importlib.util.spec_from_file_location(
        "model_" + cand, f"{FB}/candidates/{cand}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.mix_np


def main():
    mix_np = load(CAND)
    out = {"candidate": CAND, "keys": {}}
    for k in KEYS:
        V = np.arange(N, dtype=np.uint64)
        S = np.asarray(mix_np(V, np.full(N, np.uint64(k), dtype=np.uint64)),
                       dtype=np.uint64)
        logps, worst_z, fisher_logp, bonf_logp = diff_cell_logps(S, k)
        kd = {"worst_z": worst_z, "fisher_logp": fisher_logp,
              "bonf_logp": bonf_logp,
              "per_delta_logp": [float(x) for x in logps]}
        out["keys"][hex(k)] = kd
        worst_k = int(np.argmin(logps))
        print(f"key={k:#018x} worst|z|={worst_z:.2f} fisher_logp={fisher_logp:.2f} "
              f"bonf_logp={bonf_logp:.2f} worst_delta=2^{worst_k} (logp={logps[worst_k]:.2f})",
              flush=True)
    with open("/home/hatch/workspace/mix/exploration/round25/fa4a_result.json", "w") as f:
        json.dump(out, f, indent=1)
    print("wrote round25/fa4a_result.json")


if __name__ == "__main__":
    main()
