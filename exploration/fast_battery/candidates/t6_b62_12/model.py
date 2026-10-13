"""t6_b62_12: batch-62 muxD5f cascade (weakness-gated triage z=2.84 n_reject=0)."""
STAGES = [('MUXD', 17, 22, 10, 55), ('MUXD', 63, 62, 49, 57), ('MUXD', 29, 39, 36, 6), ('MUXD', 9, 4, 44, 36), ('MUXD', 5, 54, 31, 34)]
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
