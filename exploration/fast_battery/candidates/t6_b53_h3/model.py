"""t6_b53_h3: batch-53 hetMA5 cascade (triage z=9.18, andpos=4)."""
STAGES = [('MUXD', 53, 11, 12, 21), ('MUXD', 32, 29, 48, 44), ('MUXD', 1, 50, 35, 39), ('MUXD', 37, 63, 16, 17), ('AND3', 46, 45, 55)]
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
