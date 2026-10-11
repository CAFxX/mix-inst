"""Bijectivity (exhaustive at n=16 with structurally identical scaled SPN)
and sampled differential uniformity. All numbers MEASURED."""
import random, time
import numpy as np

# ---- scaled 16-bit SPN: 4 nibbles, PRESENT S-box, pLayer P(i)=4i mod 15 ----
SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
P16 = [(4 * i) % 15 for i in range(15)] + [15]
assert len(set(P16)) == 16
GOLD = 0x9E37  # golden ratio mod 2^16


def rotl16(v, r):
    r &= 15
    return v if r == 0 else (((v << r) | (v >> (16 - r)))) & 0xFFFF


def spn16(val, key, rounds=10):
    x = (val ^ key) & 0xFFFF
    for i in range(rounds):
        rk = rotl16(key, (13 * (i + 1)) & 15) ^ (((i + 1) * GOLD) & 0xFFFF)
        x ^= rk
        y = 0
        for s in range(4):
            y |= SBOX[(x >> (4 * s)) & 0xF] << (4 * s)
        z = 0
        for b in range(16):
            if (y >> b) & 1:
                z |= 1 << P16[b]
        x = z
    x ^= rotl16(key, (13 * (rounds + 1)) & 15) ^ (((rounds + 1) * GOLD) & 0xFFFF)
    return x & 0xFFFF


print("== exhaustive bijectivity, n=16, 10 rounds ==")
t0 = time.time()
for key in (0x0000, 0x0001, 0xFFFF, 0x9E37, 0x1234, 0xABCD, 0x8000):
    seen = set()
    ok = True
    for v in range(65536):
        o = spn16(v, key)
        if o in seen:
            ok = False
            print(f"  COLLISION key={key:#06x} at val={v:#06x}")
            break
        seen.add(o)
    print(f"  key={key:#06x}: {'BIJECTIVE (65536/65536 distinct)' if ok else 'FAIL'}")
print(f"  ({time.time()-t0:.1f}s)")
print("Note: the 64-bit construction is stage-wise identical (xor / bijective")
print("4-bit S-box / bit-permutation), hence a permutation for every key by")
print("composition of bijections; the n=16 instance above is exhaustive proof")
print("of the structural argument.")

print("== sampled differential uniformity, n=16 ==")
rng = random.Random(7)
worst = 0.0
worst_case = None
for trial in range(300):
    key = rng.getrandbits(16)
    din = rng.getrandbits(16) or 1
    xs = [rng.getrandbits(16) for _ in range(4096)]
    from collections import Counter
    c = Counter(spn16(x, key) ^ spn16(x ^ din, key) for x in xs)
    dmax, cmax = max(c.items(), key=lambda kv: kv[1])
    p = cmax / 4096
    if p > worst:
        worst, worst_case = p, (key, din, dmax, cmax)
print(f"  max observed P[dout | din] = {worst:.4f} "
      f"(key={worst_case[0]:#06x}, din={worst_case[1]:#06x}, dout={worst_case[2]:#06x}, {worst_case[3]}/4096)")
print(f"  ideal for random 16-bit permutation: 1/65536 = 0.0000153 per specific dout;")
print(f"  S-box differential uniformity = 4/16 (optimal for bijective 4-bit S-box).")
print("== done ==")
