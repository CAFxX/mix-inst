"""t6_b57_1: batch-57 muxD5f cascade (fisher triage z=2.41 n_reject=0)."""
STAGES = [('MUXD', 20, 37, 54, 24), ('MUXD', 63, 45, 11, 49), ('MUXD', 38, 50, 18, 16), ('MUXD', 46, 45, 27, 16), ('MUXD', 62, 47, 3, 37)]
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
