#!/usr/bin/env python3
"""Design C Fisher triage: 2-round bit-Feistel, F = 2-level AND-XOR network.

Uses lin_diff.screen_lin_diff verbatim (S1 gate's own rule).
N = 2^18 sequential inputs. The design is unkeyed -> single dummy key.
KEEP iff LIN PASS and DIFF PASS (0 Holm rejections).
"""
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/boolfunc")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")

import numpy as np

from c_model import feistel_vec
from lin_diff import screen_lin_diff

N = 1 << 18
OFFSETS = (1, 3, 5, 7)  # default; override with argv "a,b,c,d"


def main():
    offs = OFFSETS
    if len(sys.argv) > 1:
        offs = tuple(int(x) for x in sys.argv[1].split(","))
        assert len(offs) == 4
    print(f"Design C Fisher triage: offsets={offs}, N=2^{18} sequential inputs",
          flush=True)
    V = np.arange(N, dtype=np.uint64)
    out = feistel_vec(V, *offs)
    print("Evaluating outputs, running screen_lin_diff verbatim...", flush=True)
    res = screen_lin_diff({0: out}, verbose=True)
    print(f"\nLIN verdict: {res['lin_verdict']}")
    print(f"DIFF verdict: {res['diff_verdict']}")
    if res["lin_verdict"] == "PASS" and res["diff_verdict"] == "PASS":
        print("TRIAGE: KEEP")
    else:
        print("TRIAGE: REJECT")


if __name__ == "__main__":
    main()
