"""Weak-key analysis: round-key structure + fixed-point counts."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round7/models"))
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round5/models"))
from r7 import r7_feist8_s1_1sbox
from r5 import _rk_np

M64 = (1<<64)-1
C = 0x9E3779B97F4A7C15

def rk_list(k):
    return [int(_rk_np(np.uint64(k), i)) for i in range(1,9)]

def rotl64(x,r):
    r%=64
    return ((x<<r)|(x>>(64-r)))&M64

print("== round keys (low32 shown) ==")
keys = {
  "k=0": 0,
  "k=all-ones": M64,
  "k=0x5555...": 0x5555555555555555,
  "k=0xAAAA...": 0xAAAAAAAAAAAAAAAA,
  "k=1 (single bit0)": 1,
  "k=1<<63": 1<<63,
  "k=1<<32": 1<<32,
}
for name,k in keys.items():
    rks = rk_list(k)
    lo = [r & 0xFFFFFFFF for r in rks]
    hi = [(r>>32)&0xFFFFFFFF for r in rks]
    print(f"{name}: k=0x{k:016x}")
    print(f"   rk lo32: {[f'{v:08x}' for v in lo]}")
    # check distinctness / zero
    print(f"   distinct rk64: {len(set(rks))}/8, any rk64==0: {any(r==0 for r in rks)}, any lo32==0: {any(v==0 for v in lo)}")
    # verify schedule formula
    ok = all(rks[i]== (rotl64(k,13*(i+2)) ^ (((i+2)*C)&M64)) for i in range(8))
    print(f"   formula rk(k,i)=rotl64(k,13*(i+1))^((i+1)*C): {ok}")

print()
print("== F fixed points per round key (k=0): F(R)=R count over 2^24 R values ==")
# F(R,rk)=lin32(sboxlayer(R))^rklo ; vectorized
S1a = np.array([0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10], dtype=np.uint64)
def sbox_layer32_np(x):
    out = np.zeros_like(x); xv=x.copy()
    for i in range(8):
        nib=((xv>>np.uint64(4*i))&np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1a,nib)<<np.uint64(4*i)
    return out & np.uint64(0xFFFFFFFF)
def lin32_np(x):
    r7=(((x<<np.uint64(7))|(x>>np.uint64(25)))&np.uint64(0xFFFFFFFF))
    r13=(((x<<np.uint64(13))|(x>>np.uint64(19)))&np.uint64(0xFFFFFFFF))
    return (x^r7^r13)&np.uint64(0xFFFFFFFF)
N=1<<24
R=np.arange(N,dtype=np.uint64)
for i,rkv in enumerate(rk_list(0)):
    F=(lin32_np(sbox_layer32_np(R))^np.uint64(rkv&0xFFFFFFFF))&np.uint64(0xFFFFFFFF)
    fp=int(np.sum(F==R))
    print(f"  round {i+1}: rklo=0x{rkv&0xFFFFFFFF:08x}  F fixed points in 2^24: {fp} (expect ~{N/2**32:.1f})")

print()
print("== mix(v,k)=v fixed points ==")
for name,k in [("k=0",0),("k=random",0x123456789ABCDEF0),("k=all-ones",M64)]:
    N=1<<22
    v=np.arange(N,dtype=np.uint64)
    kk=np.full(N,np.uint64(k))
    out=r7_feist8_s1_1sbox(v,kk)
    fp=int(np.sum(out==v))
    print(f"  {name}: fixed points in 2^22 inputs: {fp} (expect ~{N/2**64:.2e})")

print()
print("== complementation / symmetry probes (k=0, N=2^20) ==")
N=1<<20
v=np.arange(N,dtype=np.uint64)*np.uint64(0x9E3779B97F4A7C15)
k0=np.zeros(N,dtype=np.uint64)
h1=r7_feist8_s1_1sbox(v,k0)
# test mix(v^c,k) == mix(v,k)^c for c = all-ones and single bits
for c in [0xFFFFFFFFFFFFFFFF, 0x00000000FFFFFFFF, 0xFFFFFFFF00000000, 1, 1<<32]:
    h2=r7_feist8_s1_1sbox(v^np.uint64(c),k0)
    match = np.mean(h2==(h1^np.uint64(c)))
    print(f"  c=0x{c:016x}: P(mix(v^c,k)==mix(v,k)^c) = {match:.4f}")
# related: mix(~v,~k) vs ~mix(v,k)
kk=np.full(N,np.uint64(M64))
h3=r7_feist8_s1_1sbox(v^np.uint64(M64),kk)
match=np.mean(h3==(h1^np.uint64(M64)))
print(f"  P(mix(~v,~k)==~mix(v,k)) = {match:.4f}")
