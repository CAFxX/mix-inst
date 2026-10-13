"""Model t6_and5kb."""
import numpy as np

M64=np.uint64(0xFFFFFFFFFFFFFFFF)
RC64=[np.uint64(0x9E3779B97F4A7C15),np.uint64(0x3C6EF372FE94F82A),np.uint64(0xDAA66D2C7DDF743F),np.uint64(0x78DDE6E5FD29F054),np.uint64(0x2545F4914F6CDD1D)]
def _rotl64(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & M64

def _and5k_cascade(v, k, stages):
    x = (np.uint64(v) ^ np.uint64(k)) & M64
    for i,(a,b,c) in enumerate(stages):
        rk = _rotl64(np.uint64(k), 13*(i+1)) ^ RC64[i % 5]
        x = (x ^ (_rotl64(x,a) & _rotl64(x,b)) ^ _rotl64(x,c) ^ rk) & M64
    x = (x ^ (_rotl64(np.uint64(k),13) >> np.uint64(32))) & M64
    return x

def _vec(fn):
    def f(V,K):
        V=np.asarray(V,dtype=np.uint64); K=np.asarray(K,dtype=np.uint64)
        return np.array([fn(int(v),int(k)) for v,k in zip(V.flat,K.flat)],dtype=np.uint64).reshape(V.shape)
    return f

STAGES=[(5, 13, 29), (11, 23, 41), (7, 17, 37), (19, 31, 11), (3, 29, 43)]

def _s(v,k):
    return _and5k_cascade(v,k,STAGES)
_mn=_vec(_s)

def mix(v,k):
    return _s(int(v),int(k)) if np.ndim(v)==0 and np.ndim(k)==0 else _mn(v,k)
def mix_np(V,K):
    return _mn(V,K)
meta={'desc':'5-stage AND-cascade + per-stage rk (sched B)'}
