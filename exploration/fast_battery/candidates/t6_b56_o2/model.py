"""t6_b56_o2: batch-56 hetMOA5 cascade (fisher triage z=3.06 n_reject=0, andpos=1)."""
STAGES = [('MUXD', 29, 10, 46, 63), ('OAAND', 30, 19, 7, 44), ('MUXD', 32, 48, 16, 55), ('MUXD', 56, 12, 53, 10), ('MUXD', 10, 21, 29, 27)]
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
