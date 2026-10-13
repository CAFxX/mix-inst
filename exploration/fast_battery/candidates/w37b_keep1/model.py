"""Wave-37b two-lane repair (L=3): intra-linear + AND-cross. KEEP hit1 (z=2.85)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
R1,R2,P,Q,M = 45,32,8,40,22
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
S0 = (10,20,(61, 8, 4),11,49,59,51,(46, 31, 40),48,7)
S1 = (16,40,(25, 16, 1),63,53,46,59,(12, 39, 25),33,25)
S2 = (31,30,(45, 32, 52),28,36,11,33,(20, 41, 33),39,61)
STAGES = [S0, S1, S2]
def mix_np(V, K):
    v = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (v ^ k) & M64
    y = (_rotl(v, R1) ^ _rotl(k, R2) ^ (_rotl(v, P) & _rotl(k, Q))) & M64
    for (a,b,cx,f,g,h,i,cy,mx,ny) in STAGES:
        xn = x ^ (_rotl(x,a) & _rotl(x,b)) ^ (_rotl(x,f) & _rotl(y,g))
        for c in cx: xn ^= _rotl(x, c)
        yn = y ^ (_rotl(y,h) & _rotl(y,i)) ^ (_rotl(x,mx) & _rotl(y,ny))
        for c in cy: yn ^= _rotl(y, c)
        x, y = xn & M64, yn & M64
    return (x ^ _rotl(y, M) ^ _rotl(k, 13)) & M64
def mix(v, k):
    return int(mix_np(np.uint64(v), np.uint64(k)))
