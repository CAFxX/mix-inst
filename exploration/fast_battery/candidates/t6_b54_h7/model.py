"""t6_b54_h7: batch-54 hetMA5p1 cascade (triage z=9.88, andpos=1)."""
STAGES = [('MUXD', 28, 34, 23, 6), ('AND3', 14, 30, 8), ('MUXD', 21, 46, 37, 34), ('MUXD', 60, 15, 31, 34), ('MUXD', 17, 55, 4, 28)]
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
