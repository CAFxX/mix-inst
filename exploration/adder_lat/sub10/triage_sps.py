"""Fisher triage on S-P-S construction."""
import sys, numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/sub10")
from lin_diff import screen_lin_diff
from model_spn2 import mix_sub10_vec

def gen_seq(mix_fn, key, n=1<<18):
    """Sequential outputs: mix(i, key) for i in 0..n-1."""
    xs = np.arange(n, dtype=np.uint64)
    return mix_fn(xs, key)

if __name__ == "__main__":
    keys = [0x123456789ABCDEF0, 0xFFFFFFFFFFFFFFFF]
    seq = {}
    for k in keys:
        print(f"generating 2^18 outputs for key {k:#x}...")
        seq[k] = gen_seq(mix_sub10_vec, np.uint64(k))
    print("running Fisher triage...")
    res = screen_lin_diff(seq, verbose=True)
    print(f"LIN: {res['lin_verdict']}, DIFF: {res['diff_verdict']}")
