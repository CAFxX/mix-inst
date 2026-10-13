"""Model t6_hs4rc."""
import numpy as np

M64=np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl64(x,r):
    r%=64; return x if r==0 else ((x<<np.uint64(r))|(x>>np.uint64(64-r)))&M64

def _hs(v,k,has_rc):
    x=(np.uint64(v)^np.uint64(k))&M64
    for i,(a,b,c) in enumerate(SCHED):
        ra,rb,rc=_rotl64(x,a),_rotl64(x,b),_rotl64(x,c)
        x=(x^(ra&rb)^(rc if has_rc[i] else np.uint64(0)))&M64
    return (x^_rotl64(np.uint64(k),13))&M64

def _vec(fn):
    def f(V,K):
        V=np.asarray(V,dtype=np.uint64);K=np.asarray(K,dtype=np.uint64)
        return np.array([fn(int(v),int(k)) for v,k in zip(V.flat,K.flat)],dtype=np.uint64).reshape(V.shape)
    return f

SCHED=[(1, 2, 13), (7, 19, 5), (3, 11, 29), (17, 31, 7), (11, 23, 37), (19, 41, 23)]
HAS=[True, True, False, True, True, False]

def _s(v,k):
    return _hs(v,k,HAS)
_mn=_vec(_s)

def mix(v,k):
    return _s(int(v),int(k)) if np.ndim(v)==0 and np.ndim(k)==0 else _mn(v,k)
def mix_np(V,K):
    return _mn(V,K)
meta={'desc':'6-stage AND hetero-strength: rc on 0,1,3,4'}
