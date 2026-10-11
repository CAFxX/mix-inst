"""Track 6, batch 13: 5-stage AND-cascade WITH per-stage round keys.

Hypothesis: al_and6a's 5-stage variant failed DIFF (worst|z|=512) partly
because it has NO per-stage key (only initial/final). Adding rk_i per stage
adds key-dependent variation that may break differential trails.

Structure:
  x = v ^ k
  5 stages: x ^= (ra&rb) ^ rc ^ rk_i, rk_i = rotl(k,13*(i+1))^RC[i]
  x ^= rotl(k,13)>>32

Target: ~20u (17.2u + key XOR cost). If DIFF passes, competitive.
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
RC64 = [np.uint64(0x9E3779B97F4A7C15), np.uint64(0x3C6EF372FE94F82A),
        np.uint64(0xDAA66D2C7DDF743F), np.uint64(0x78DDE6E5FD29F054),
        np.uint64(0x2545F4914F6CDD1D)]

def _rotl64(x, r):
    r %= 64
    return x if r == 0 else ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & M64

STAGES_A = [(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37)]
STAGES_B = [(5,13,29),(11,23,41),(7,17,37),(19,31,11),(3,29,43)]

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
def _mk(stages,fname):
    def f(v,k): return _and5k_cascade(v,k,stages)
    f.__name__=fname; return f
CANDIDATES_B13 = {
    "t6_and5ka": (_mk(STAGES_A,"and_and5ka"), "5-stage AND-cascade + per-stage rk (sched A)"),
    "t6_and5kb": (_mk(STAGES_B,"and_and5kb"), "5-stage AND-cascade + per-stage rk (sched B)"),
}
MIX_NP_B13 = {n:_vec(f) for n,(f,_) in CANDIDATES_B13.items()}
if __name__=="__main__":
    for name,(fn,_) in CANDIDATES_B13.items():
        assert fn(np.uint64(0),np.uint64(0x123456789ABCDEF0))!=fn(np.uint64(1),np.uint64(0x123456789ABCDEF0))
        v0=np.uint64(0x123456789ABCDEF0); k0=np.uint64(0xFEDCBA9876543210); o0=fn(v0,k0)
        fl=[bin(int(o0^fn(v0^(np.uint64(1)<<np.uint64(i)),k0))).count('1') for i in range(64)]
        print(f"{name}: avg={sum(fl)/len(fl):.1f} dev={(sum((f-32)**2 for f in fl)/len(fl))**.5:.2f}")
