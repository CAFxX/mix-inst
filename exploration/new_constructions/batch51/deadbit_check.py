"""Co-design probe: does the nibble-chi dead-bit kill the full cascade at exact-DIFF?
fz24_g: 5x [x ^= nch(x) ^ rotl(x,c)], c=(13,29,47,7,31)
fz24_i: 5x [x ^= nch(x) ^ rotl(x,1) ^ rotl(x,61)]
Test: single-bit input deltas, per-output-bit P(flip) over keys x inputs."""
import numpy as np, math
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
PL = np.uint64(0x1111111111111111)
def rotl(x,r):
    r%=64
    return ((x<<np.uint64(r))|(x>>np.uint64(64-r)))&M64 if r else x
def nch(x):
    p0=x&PL; p1=(x>>np.uint64(1))&PL; p2=(x>>np.uint64(2))&PL; p3=(x>>np.uint64(3))&PL
    q0=p0^((~p1)&p2); q1=p1^((~p2)&p3); q2=p2^((~p3)&p0); q3=p3^((~p0)&p1)
    return (q0|(q1<<np.uint64(1))|(q2<<np.uint64(2))|(q3<<np.uint64(3)))&M64
def F_g(x,k):
    x=(x^k)&M64
    for c in (13,29,47,7,31): x=(x^nch(x)^rotl(x,c))&M64
    return (x^rotl(k,13))&M64
def F_i(x,k):
    x=(x^k)&M64
    for _ in range(5): x=(x^nch(x)^rotl(x,1)^rotl(x,61))&M64
    return (x^rotl(k,13))&M64
rng=np.random.default_rng(0xB51)
N=1<<20
for name,F in (("fz24_g",F_g),("fz24_i",F_i)):
    worst=0.0; worstcell=None
    for dbit in (0,1,2,3,5,13,63):  # single-bit deltas incl within-nibble positions
        d=np.uint64(1)<<np.uint64(dbit)
        maxz=0.0
        for kk in range(4):
            k=np.uint64(rng.integers(0, 2**64, dtype=np.uint64))
            x=rng.integers(0,2**64,size=N,dtype=np.uint64)
            y0=F(x,k); y1=F(x^d,k)
            dy=(y0^y1)
            for p in range(64):
                cnt=int(np.sum((dy>>np.uint64(p))&np.uint64(1)))
                phat=cnt/N; se=math.sqrt(0.25/N)
                z=abs(phat-0.5)/se
                if z>maxz: maxz=z
        if maxz>worst: worst=maxz; worstcell=dbit
    print(f"{name}: worst |z|={worst:.1f} at delta-bit {worstcell} (bar <10)", flush=True)
