"""t6_xorh5_15: xorh5 hetero cascade (fisher triage z=3.29 n_reject=0)."""
STAGES = [('XOR4', 19, 26, 20, 42), ('MUXD', 63, 35, 47, 51), ('MUXD', 56, 43, 63, 9), ('MUXD', 18, 56, 15, 20), ('MUXD', 57, 2, 31, 54)]
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
