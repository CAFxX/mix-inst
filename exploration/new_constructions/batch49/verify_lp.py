import sys
# Leander-Poschmann representatives F0..F15 (decimal), via Koelsch diss. Table 5.1
# (citing Leander-Poschmann WAIFI 2007). Used here as computational input only.
LP = {
 0:[0,1,2,13,4,7,15,6,8,11,12,9,3,14,10,5],
 1:[0,1,2,13,4,7,15,6,8,11,14,3,5,9,10,12],
 2:[0,1,2,13,4,7,15,6,8,11,14,3,10,12,5,9],
 3:[0,1,2,13,4,7,15,6,8,12,5,3,10,14,11,9],
 4:[0,1,2,13,4,7,15,6,8,12,9,11,10,14,5,3],
 5:[0,1,2,13,4,7,15,6,8,12,11,9,10,14,3,5],
 6:[0,1,2,13,4,7,15,6,8,12,11,9,10,14,5,3],
 7:[0,1,2,13,4,7,15,6,8,12,14,11,10,9,3,5],
 8:[0,1,2,13,4,7,15,6,8,14,9,5,10,11,3,12],
 9:[0,1,2,13,4,7,15,6,8,14,11,3,5,9,10,12],
 10:[0,1,2,13,4,7,15,6,8,14,11,5,10,9,3,12],
 11:[0,1,2,13,4,7,15,6,8,14,11,10,5,9,12,3],
 12:[0,1,2,13,4,7,15,6,8,14,11,10,9,3,12,5],
 13:[0,1,2,13,4,7,15,6,8,14,12,9,5,11,10,3],
 14:[0,1,2,13,4,7,15,6,8,14,12,11,3,9,5,10],
 15:[0,1,2,13,4,7,15,6,8,14,12,11,9,3,10,5],
}
N=16
def anf_deg(s, mask):
    f=[0]*N
    for x in range(N):
        v=0
        for o in range(4):
            if (mask>>o)&1 and (s[x]>>o)&1: v^=1
        f[x]=v
    a=f[:]
    for i in range(4):
        for x in range(N):
            if x&(1<<i): a[x]^=a[x^(1<<i)]
    return max(bin(x).count('1') for x,c in enumerate(a) if c)
def du(s):
    m=0
    for din in range(1,N):
        cnt={}
        for x in range(N):
            d=s[x]^s[x^din]; cnt[d]=cnt.get(d,0)+1
        m=max(m,max(cnt.values()))
    return m
def latbias(s):
    w=0
    for mi in range(1,N):
        for mo in range(1,N):
            c=sum(1 for x in range(N) if (bin(x&mi).count('1')+bin(s[x]&mo).count('1'))%2==0)
            w=max(w,abs(c-8))
    return w
for i in range(16):
    s=LP[i]
    bij=len(set(s))==N
    degs=sorted(set(anf_deg(s,m) for m in range(1,N)))
    print("F%-2d bij=%s compdeg=%s DU=%d LATbias=%d S0=%d"%(i,bij,degs,du(s),latbias(s),s[0]))
