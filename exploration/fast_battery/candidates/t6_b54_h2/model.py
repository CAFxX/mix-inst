"""t6_b54_h2: batch-54 hetMA5p1 cascade (triage z=4.58, andpos=1)."""
STAGES = [('MUXD', 24, 40, 21, 2), ('AND3', 34, 46, 29), ('MUXD', 31, 57, 17, 11), ('MUXD', 28, 21, 14, 45), ('MUXD', 7, 27, 63, 48)]
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
