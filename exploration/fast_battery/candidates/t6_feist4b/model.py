"""Model t6_feist4b (batch 12)."""
import numpy as np

M64=np.uint64(0xFFFFFFFFFFFFFFFF)
M32=np.uint64(0xFFFFFFFF)
RC32=[np.uint64(0x9E3779B9),np.uint64(0x3C6EF372),np.uint64(0xDAA66D2C),np.uint64(0x78DDE6E5)]
def _rotl32(x, r):
    r %= 32
    if r == 0:
        return x & M32
    return (((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & M32)

def _rotl64(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64

def _F_and2(R, rk, sched):
    # 2-stage 32-bit AND-cascade: R ^= (ra&rb)^rc
    x = np.uint64(R) & M32
    for (a, b, c) in sched:
        x = (x ^ (_rotl32(x, a) & _rotl32(x, b)) ^ _rotl32(x, c)) & M32
    return (x ^ np.uint64(rk)) & M32

def _feistel4(v, k, fsched):
    x = (np.uint64(v) ^ np.uint64(k)) & M64
    L = (x >> np.uint64(32)) & M32
    R = x & M32
    kh = (np.uint64(k) >> np.uint64(32)) & M32
    kl = np.uint64(k) & M32
    for i in range(4):
        rk = (_rotl32(kl, 7 * (i + 1)) ^ RC32[i % 4]) & M32
        F = _F_and2(R, rk, fsched)
        L, R = R, (L ^ F) & M32
    out = ((np.uint64(R) << np.uint64(32)) | np.uint64(L)) & M64
    return (out ^ np.uint64(k)) & M64

def _vec(fn):
    def f(V, K):
        V = np.asarray(V, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        return np.array([fn(int(v), int(k)) for v, k in zip(V.flat, K.flat)],
                        dtype=np.uint64).reshape(V.shape)
    return f

SCHED=[(7, 19, 3), (13, 29, 11)]

def _scalar(v,k):
    return _feistel4(v,k,SCHED)
_mix_np=_vec(_scalar)

def mix(v,k):
    return _scalar(int(v),int(k)) if np.ndim(v)==0 and np.ndim(k)==0 else _mix_np(v,k)
def mix_np(V,K):
    return _mix_np(V,K)
meta={'desc':'4-round Feistel, F=2-stage, alt schedule'}
