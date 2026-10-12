"""Fisher triage on S-box -> P-box -> MUX2-FF-keyed -> P-box -> S-box (10.0u)."""
import sys, numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/middepth/v4_hybrid4")
from lin_diff import screen_lin_diff
from model_hyb3b import mix_hyb3b_vec

def gen_seq(mix_fn, key, n=1<<18):
    xs = np.arange(n, dtype=np.uint64)
    return mix_fn(xs, np.uint64(key))

if __name__ == "__main__":
    keys = [0x123456789ABCDEF0, 0xFFFFFFFFFFFFFFFF]
    seq = {}
    for k in keys:
        print(f"generating 2^18 outputs for key {k:#x}...", flush=True)
        seq[k] = gen_seq(mix_hyb3b_vec, k)
    print("running Fisher triage...", flush=True)
    res = screen_lin_diff(seq, verbose=True)
    print(f"LIN: {res['lin_verdict']}, DIFF: {res['diff_verdict']}")
