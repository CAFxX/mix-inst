"""Wave-37b two-lane repair (L=3): intra-linear + AND-cross. KEEP hit2 (z=5.76)."""
import numpy as np
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
R1,R2,P,Q,M = 35,10,24,1,56
def _rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x
S0 = (39,29,(17, 44, 52),29,53,28,41,(56, 53, 63),29,5)
S1 = (34,2,(25, 11, 10),36,15,12,14,(8, 27, 59),46,7)
S2 = (62,47,(13, 5, 60),4,41,11,33,(25, 46, 23),42,59)
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
