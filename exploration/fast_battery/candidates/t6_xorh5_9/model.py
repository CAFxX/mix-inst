"""t6_xorh5_9: xorh5 hetero cascade (fisher triage z=2.95 n_reject=0)."""
STAGES = [('MUXD', 53, 61, 59, 54), ('MUXD', 1, 14, 56, 44), ('MUXD', 36, 39, 26, 54), ('MUXD', 45, 48, 55, 58), ('XOR4', 46, 3, 20, 13)]
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
