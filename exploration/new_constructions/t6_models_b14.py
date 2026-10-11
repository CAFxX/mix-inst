"""Track 6, batch 14: hetero-STRENGTH AND-cascade.

Some stages have the rc linear term, some don't.
  3rc: rc on stages 0,2,4 → 15 gates ≈ 16.7u target
  4rc: rc on stages 0,1,3,4 → 16 gates ≈ 17.9u target

Avalanche: 3rc dev 4.68, 4rc dev 3.83 (both good).
"""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
def _rotl64(x,r):
    r%=64; return x if r==0 else ((x<<np.uint64(r))|(x>>np.uint64(64-r)))&M64
SCHED=[(1,2,13),(7,19,5),(3,11,29),(17,31,7),(11,23,37),(19,41,23)]
HAS3=[True,False,True,False,True,False]
HAS4=[True,True,False,True,True,False]
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
def _mk(has_rc,fname):
    def f(v,k): return _hs(v,k,has_rc)
    f.__name__=fname; return f
CANDIDATES_B14={
    "t6_hs3rc": (_mk(HAS3,"hs_hs3rc"), "6-stage AND hetero-strength: rc on 0,2,4"),
    "t6_hs4rc": (_mk(HAS4,"hs_hs4rc"), "6-stage AND hetero-strength: rc on 0,1,3,4"),
}
MIX_NP_B14={n:_vec(f) for n,(f,_) in CANDIDATES_B14.items()}
if __name__=="__main__":
    for name,(fn,_) in CANDIDATES_B14.items():
        assert fn(np.uint64(0),np.uint64(0x123456789ABCDEF0))!=fn(np.uint64(1),np.uint64(0x123456789ABCDEF0))
        v0=np.uint64(0x123456789ABCDEF0);k0=np.uint64(0xFEDCBA9876543210);o0=fn(v0,k0)
        fl=[bin(int(o0^fn(v0^(np.uint64(1)<<np.uint64(i)),k0))).count('1') for i in range(64)]
        print(f"{name}: avg={sum(fl)/len(fl):.1f} dev={(sum((f-32)**2 for f in fl)/len(fl))**.5:.2f}")
