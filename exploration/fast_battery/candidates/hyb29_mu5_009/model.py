"""hyb29_mu5_009: batch-29 MU5-324local MUXD cascade (fisher triage z=2.88 n_reject=0)."""
STAGES = [('MUXD', 62, 50, 55, 2), ('MUXD', 48, 58, 23, 30), ('MUXD', 44, 45, 7, 60), ('MUXD', 49, 26, 32, 35), ('MUXD', 5, 51, 43, 39)]
def mix_np(V, K):
    import numpy as np
    M = np.uint64(0xFFFFFFFFFFFFFFFF)
    def rotl(x, r):
        r %= 64
        return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M if r else x
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M
    for st in STAGES:
        assert st[0] == "MUXD"
        _, s, a, b, d = st
        g = ((rotl(x, s) & rotl(x, a)) | ((~rotl(x, s)) & rotl(x, b))) & M
        x = (x ^ g ^ rotl(x, d)) & M
    x = (x ^ rotl(k, 13)) & M
    return x
def mix(v, k):
    import numpy as np
    return int(mix_np(np.uint64(v), np.uint64(k)))
