import sys
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from screen_lib import KEYS, N
M64 = np.uint64(0xFFFFFFFFFFFFFFFF); M32 = np.uint32(0xFFFFFFFF)
def rotl32(x, r):
    r %= 32
    return ((x << np.uint32(r)) | (x >> np.uint32(32 - r))) & M32 if r else x
def rotl64(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def feis4_np(V, K, rounds, subrots, linear_c=None):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    L = (x >> np.uint64(32)).astype(np.uint32); R = (x & np.uint64(0xFFFFFFFF)).astype(np.uint32)
    for (a,b), s in zip(rounds, subrots):
        rk = (rotl64(k, s) & np.uint64(0xFFFFFFFF)).astype(np.uint32)
        F = (rotl32(R, a) & rotl32(R, b)) ^ rk
        if linear_c is not None: F = (F ^ rotl32(R, linear_c)) & M32
        L, R = R, ((L ^ F) & M32)
    out = ((L.astype(np.uint64) << np.uint64(32)) | R.astype(np.uint64)) & M64
    return ((out ^ rotl64(k, 13)) & M64).astype(np.uint64)
V = np.arange(N, dtype=np.uint64); K = np.full(N, np.uint64(KEYS[0]), dtype=np.uint64)
rounds=[(5,17),(23,11),(7,19),(27,2)]; subrots=[3,41,19,57]
S = feis4_np(V, K, rounds, subrots)
print("bijective (all %d distinct): %s" % (N, len(np.unique(S))==N))
# avalanche: flip bit 0 of each of 1024 inputs
V2 = (np.arange(1024, dtype=np.uint64) ^ np.uint64(1))
K2 = np.full(1024, np.uint64(KEYS[0]), dtype=np.uint64)
S1 = feis4_np(np.arange(1024, dtype=np.uint64), K2, rounds, subrots)
S2 = feis4_np(V2, K2, rounds, subrots)
d = S1 ^ S2
av = np.array([bin(int(v)).count('1') for v in d])
print("avalanche bit0: mean=%.1f (expect ~32)" % av.mean())
