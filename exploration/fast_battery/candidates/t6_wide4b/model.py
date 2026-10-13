"""Model t6_wide4b (batch 11)."""
import numpy as np

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _wide4_cascade(v, k, sched):
    x = (np.uint64(v) ^ np.uint64(k)) & M64
    for (a, b, c, d, e) in sched:
        ra, rb, rc, rd, re = [_rotl64(x, t) for t in (a, b, c, d, e)]
        x = (x ^ (ra & rb) ^ (rc & rd) ^ re) & M64
    x = (x ^ _rotl64(np.uint64(k), 13)) & M64
    return x

def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f

SCHED = [(5, 17, 35, 53, 11), (29, 47, 13, 31, 7), (19, 37, 55, 23, 41), (11, 33, 51, 17, 43)]

def _scalar(v,k):
    return _wide4_cascade(v,k,SCHED)
_mix_np=_vec(_scalar)

def mix(v,k):
    return _scalar(int(v),int(k)) if np.ndim(v)==0 and np.ndim(k)==0 else _mix_np(v,k)
def mix_np(V,K):
    return _mix_np(V,K)
meta={'desc':'4-stage WIDE AND-cascade, alternate schedule'}
