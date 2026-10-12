"""t6_b54_h6: batch-54 hetMA5p1 cascade (triage z=9.44, andpos=1)."""
STAGES = [('MUXD', 3, 14, 23, 52), ('AND3', 37, 30, 14), ('MUXD', 48, 38, 17, 21), ('MUXD', 16, 21, 56, 26), ('MUXD', 15, 19, 40, 36)]
def mix_np(V, K):
    import numpy as np
    M = np.uint64(0xFFFFFFFFFFFFFFFF)
    def rotl(x, r):
        r %= 64
        return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M if r else x
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M
    for st in STAGES:
        if st[0] == "MUXD":
            _, s, a, b, d = st
            g = ((rotl(x, s) & rotl(x, a)) | ((~rotl(x, s)) & rotl(x, b))) & M
            x = (x ^ g ^ rotl(x, d)) & M
        else:
            _, p, q, r = st
            x = (x ^ (rotl(x, p) & rotl(x, q)) ^ rotl(x, r)) & M
    x = (x ^ rotl(k, 13)) & M
    return x
def mix(v, k):
    import numpy as np
    return int(mix_np(np.uint64(v), np.uint64(k)))
