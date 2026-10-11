#!/usr/bin/env python3
"""Independent pure-Python reference for fz24_o, written directly from the
task's stage-semantics spec (NOT from gen_fused24.py or model.py).

Spec:
  t3(a,b,c,d):  x = (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c) ^ rotl(x,d))
  and(a,b,c):   x = (x ^ (rotl(x,a) & rotl(x,b)) ^ rotl(x,c))
  chi(a,b,c,d): x = (x ^ ((~rotl(x,a)) & rotl(x,b)) ^ rotl(x,c) ^ rotl(x,d))
fz24_o: [t3(1,7,13,29), t3(3,11,19,37), and(5,15,21), and(9,23,43),
         chi(31,19,35,53)]
Key schedule: x ^= k  (pre); x ^= rotl(k,13) (post). 64-bit, mask M64.
"""
import random, sys

M64 = 0xFFFFFFFFFFFFFFFF

def rotl(x, r):
    r &= 63
    return ((x << r) | (x >> (64 - r))) & M64 if r else x

def ref_mix(v, k):
    x = (v ^ k) & M64
    # t3(1,7,13,29)
    x = (x ^ (rotl(x,1) & rotl(x,7)) ^ rotl(x,13) ^ rotl(x,29)) & M64
    # t3(3,11,19,37)
    x = (x ^ (rotl(x,3) & rotl(x,11)) ^ rotl(x,19) ^ rotl(x,37)) & M64
    # and(5,15,21)
    x = (x ^ (rotl(x,5) & rotl(x,15)) ^ rotl(x,21)) & M64
    # and(9,23,43)
    x = (x ^ (rotl(x,9) & rotl(x,23)) ^ rotl(x,43)) & M64
    # chi(31,19,35,53)
    x = (x ^ ((~rotl(x,31)) & rotl(x,19)) ^ rotl(x,35) ^ rotl(x,53)) & M64
    # post
    x = (x ^ rotl(k,13)) & M64
    return x

def main():
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/candidates/fz24_o")
    import model
    rng = random.Random(0xF24A0)  # fixed seed, reproducible
    N = 10000
    for i in range(N):
        v = rng.getrandbits(64)
        k = rng.getrandbits(64)
        a = ref_mix(v, k)
        b = model.mix(v, k)
        if a != b:
            print(f"MISMATCH vec {i}: v={v:#x} k={k:#x} ref={a:#x} model={b:#x}")
            sys.exit(1)
    # edge vectors (must exercise all rotation amounts and complement paths)
    edges = [0, M64, 1, 1<<63, 0x5555555555555555, 0xAAAAAAAAAAAAAAAA,
             0x0F0F0F0F0F0F0F0F, 0xF0F0F0F0F0F0F0F0, 0xFF00FF00FF00FF00,
             0x00FF00FF00FF00FF, 0x8000000000000001, 0xDEADBEEFCAFEBABE]
    for v in edges:
        for k in edges:
            if ref_mix(v,k) != model.mix(v,k):
                print(f"EDGE MISMATCH v={v:#x} k={k:#x}")
                sys.exit(1)
    print(f"BITEXACT-PASS ref==model.py on {N} random + {len(edges)**2} edge vectors")

if __name__ == "__main__":
    main()
