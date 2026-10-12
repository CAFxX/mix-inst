"""t6_b53_h2: batch-53 hetMA5 cascade (triage z=6.45, andpos=0)."""
STAGES = [('AND3', 31, 29, 60), ('MUXD', 18, 11, 35, 55), ('MUXD', 31, 32, 62, 42), ('MUXD', 18, 26, 41, 25), ('MUXD', 17, 38, 56, 22)]
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
