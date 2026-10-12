"""t6_b56_o0: batch-56 hetMOA5 cascade (fisher triage z=2.71 n_reject=0, andpos=1)."""
STAGES = [('MUXD', 30, 27, 19, 56), ('OAAND', 18, 42, 6, 16), ('MUXD', 3, 54, 40, 6), ('MUXD', 61, 33, 16, 54), ('MUXD', 41, 18, 2, 3)]
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
        elif st[0] == "OAAND":
            _, p, q, r, s = st
            x = (x ^ (((rotl(x, p) | rotl(x, q)) & rotl(x, r)) ^ rotl(x, s))) & M
        else:
            raise AssertionError(st[0])
    x = (x ^ rotl(k, 13)) & M
    return x
def mix(v, k):
    import numpy as np
    return int(mix_np(np.uint64(v), np.uint64(k)))
