"""S-box + single MUXD stage: y = MUXD(S(x ^ k)). Target <10u."""
import numpy as np, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/sub10")
from model_spn2 import sbox_layer

M = np.uint64(0xFFFFFFFFFFFFFFFF)
def rotl(x, r):
    r %= 64
    if r == 0: return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & M

def mix_s_muxd(x, k, stage=(17,22,10,55)):
    """x,k: arrays. Single MUXD stage after S-box."""
    s,a,b,d = stage
    t = (x ^ k) & M
    t = sbox_layer(t)
    g = ((rotl(t,s) & rotl(t,a)) | ((~rotl(t,s)) & rotl(t,b))) & M
    t = (t ^ g ^ rotl(t,d)) & M
    t = (t ^ rotl(k,13)) & M
    return t

if __name__ == "__main__":
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
    from lin_diff import screen_lin_diff
    seq = {}
    for k in [0x123456789ABCDEF0, 0xFFFFFFFFFFFFFFFF]:
        xs = np.arange(1<<18, dtype=np.uint64)
        seq[k] = mix_s_muxd(xs, np.uint64(k))
    res = screen_lin_diff(seq, verbose=False)
    print(f"LIN: {res['lin_verdict']}, DIFF: {res['diff_verdict']}")
