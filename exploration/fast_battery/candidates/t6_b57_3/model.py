"""t6_b57_3: batch-57 muxD5f cascade (fisher triage z=2.83 n_reject=0)."""
STAGES = [('MUXD', 15, 21, 13, 16), ('MUXD', 58, 5, 33, 25), ('MUXD', 33, 47, 27, 62), ('MUXD', 1, 41, 47, 22), ('MUXD', 8, 9, 23, 59)]
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
