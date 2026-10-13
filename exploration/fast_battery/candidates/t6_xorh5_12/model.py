"""t6_xorh5_12: xorh5 hetero cascade (fisher triage z=3.02 n_reject=0)."""
STAGES = [('MUXD', 41, 49, 1, 32), ('XOR4', 34, 37, 3, 9), ('MUXD', 53, 42, 0, 6), ('MUXD', 63, 56, 4, 20), ('MUXD', 26, 20, 2, 38)]
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
            assert st[0] == "XOR4"
            _, a, b, c, d = st
            x = (x ^ rotl(x, a) ^ rotl(x, b) ^ rotl(x, c) ^ rotl(x, d)) & M
    x = (x ^ rotl(k, 13)) & M
    return x
def mix(v, k):
    import numpy as np
    return int(mix_np(np.uint64(v), np.uint64(k)))
