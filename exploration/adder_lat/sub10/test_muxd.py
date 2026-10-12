"""MUXD cascade variants: 2-stage and 3-stage, modeled on t6_b59_47."""
import numpy as np

M = np.uint64(0xFFFFFFFFFFFFFFFF)

def rotl(x, r):
    r %= 64
    if r == 0: return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & M

# Use t6_b59_47's first 3 stages
STAGES_5 = [('MUXD', 17, 22, 10, 55), ('MUXD', 63, 62, 49, 57), ('MUXD', 29, 39, 35, 6),
            ('MUXD', 11, 5, 44, 33), ('MUXD', 52, 18, 27, 41)]  # guessed last 2

def mix_muxd(V, K, nstages):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M
    for st in STAGES_5[:nstages]:
        _, s, a, b, d = st
        g = ((rotl(x, s) & rotl(x, a)) | ((~rotl(x, s)) & rotl(x, b))) & M
        x = (x ^ g ^ rotl(x, d)) & M
    x = (x ^ rotl(k, 13)) & M
    return x

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
    from lin_diff import screen_lin_diff
    for ns in [2, 3]:
        print(f"\n=== {ns}-stage MUXD ===")
        seq = {}
        for k in [0x123456789ABCDEF0, 0xFFFFFFFFFFFFFFFF]:
            xs = np.arange(1<<18, dtype=np.uint64)
            seq[k] = mix_muxd(xs, np.uint64(k), ns)
        res = screen_lin_diff(seq, verbose=False)
        print(f"LIN: {res['lin_verdict']}, DIFF: {res['diff_verdict']}")
        for kk, dd in res['lin_detail'].items():
            print(f"  LIN D={dd['D']}/4096")
