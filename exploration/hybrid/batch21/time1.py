import sys, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps
from screen_lib import KEYS, N
M64 = np.uint64(0xFFFFFFFFFFFFFFFF); M32 = np.uint32(0xFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
def rotl32(x, r):
    r %= 32
    return ((x << np.uint32(r)) | (x >> np.uint32(32 - r))) & M32 if r else x
def rotl64(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
def feis4_np(V, K, rounds, subrots):
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    L = (x >> np.uint64(32)).astype(np.uint32); R = (x & np.uint64(0xFFFFFFFF)).astype(np.uint32)
    for (a,b,c), s in zip(rounds, subrots):
        rk = (rotl64(k, s) & np.uint64(0xFFFFFFFF)).astype(np.uint32)
        F = (rotl32(R, a) & rotl32(R ^ rk, b)) ^ rotl32(R, c)
        L, R = R, (L ^ F) & M32
    out = ((L.astype(np.uint64) << np.uint64(32)) | R.astype(np.uint64)) & M64
    return ((out ^ rotl64(k, 13)) & M64).astype(np.uint64)
V = np.arange(N, dtype=np.uint64)
rounds = [(5,17,3),(23,11,29),(7,19,13),(27,2,21)]
subrots = [3, 41, 19, 57]
t0 = time.time()
worst = 0.0
for key in KEYS10:
    K = np.full(N, np.uint64(key), dtype=np.uint64)
    S = feis4_np(V, K, rounds, subrots)
    _, wz, _, _ = diff_cell_logps(S, key)
    worst = max(worst, wz)
print("worst|z|=%.2f elapsed=%.1fs" % (worst, time.time()-t0), flush=True)
