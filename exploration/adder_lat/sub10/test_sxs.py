"""Test S-XOR-S: S-box + 1-level XOR linear + S-box."""
import numpy as np
from model_spn2 import sbox_layer, SB0

def rotl64(x, n):
    n = n % 64
    return ((x << np.uint64(n)) | (x >> np.uint64(64-n))) & np.uint64(0xFFFFFFFFFFFFFFFF)

def mix_sxs(x, k, rot=16):
    """y = S( (S(x) ^ rotl(S(x), rot)) ) ^ k. Key at end."""
    t = sbox_layer(x)
    t = t ^ rotl64(t, rot)
    t = sbox_layer(t)
    return t ^ k

if __name__ == "__main__":
    k = np.uint64(0x123456789ABCDEF0)
    x0 = np.uint64(0x0123456789ABCDEF)
    y0 = mix_sxs(np.array([x0]), k)[0]
    diffs = []
    for i in range(64):
        xi = x0 ^ (np.uint64(1) << np.uint64(i))
        yi = mix_sxs(np.array([xi]), k)[0]
        diffs.append(bin(int(y0) ^ int(yi)).count('1'))
    print(f"S-XOR-S avalanche: min={min(diffs)} max={max(diffs)} mean={sum(diffs)/len(diffs):.1f}")
    # Try different rotations
    for rot in [8, 16, 24, 32]:
        diffs = []
        for i in range(64):
            xi = x0 ^ (np.uint64(1) << np.uint64(i))
            # inline with rot
            def m(x_, k_):
                t_ = sbox_layer(x_)
                t_ = t_ ^ rotl64(t_, rot)
                t_ = sbox_layer(t_)
                return t_ ^ k_
            yi = m(np.array([xi]), k)[0]
            diffs.append(bin(int(y0) ^ int(yi)).count('1'))
        # recompute y0 for this rot
        y0r = m(np.array([x0]), k)[0]
        diffs = []
        for i in range(64):
            xi = x0 ^ (np.uint64(1) << np.uint64(i))
            yi = m(np.array([xi]), k)[0]
            diffs.append(bin(int(y0r) ^ int(yi)).count('1'))
        print(f"  rot={rot}: mean={sum(diffs)/len(diffs):.1f} min={min(diffs)} max={max(diffs)}")
