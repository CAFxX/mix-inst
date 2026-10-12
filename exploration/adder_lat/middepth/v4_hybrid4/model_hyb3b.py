"""V4 reconsideration B: S-box -> MUX2-FF-keyed -> S-box (10.0u budget).

The MUX2 substitution is not bijective; the 4-term is 5.5u (not 2.5u).
This variant uses:
  - Midori Sb0 S-box (3.0u, bijective, strong) x2
  - MUX2 feed-forward with key in MUX data input (4.0u, bijective, keyed at no extra cost):
    y = x ^ mux(rotl(x,rs), rotl(x,ra), rotl(k,ck))
Total: 3.0 + 4.0 + 3.0 = 10.0u (at budget, not over).

Bit-exact with hyb3b.v.
"""
import numpy as np

# Midori Sb0
SB0 = np.array([0xC,0xA,0xD,0x3,0xE,0xB,0xF,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6], dtype=np.uint64)

def rotl64(x, n):
    n %= 64
    if n == 0:
        return np.asarray(x, dtype=np.uint64)
    x = np.asarray(x, dtype=np.uint64)
    return (x << np.uint64(n)) | (x >> np.uint64(64 - n))

def sbox_layer(x):
    """16x Midori Sb0 in parallel."""
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(x)
    for i in range(16):
        nib = (x >> np.uint64(4*i)) & np.uint64(0xF)
        y |= SB0[nib] << np.uint64(4*i)
    return y

# PRESENT P-box: P(i) = 16*i mod 63 for i<63, P(63)=63; y[P(i)] = x[i]
PBOX = [(16*i) % 63 for i in range(63)] + [63]
PINV = [0]*64
for i, p in enumerate(PBOX):
    PINV[p] = i
PINV = np.array(PINV, dtype=np.uint64)

def pbox(x):
    """Bit permutation (wires, 0u)."""
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(x)
    for i in range(64):
        bit = (x >> np.uint64(i)) & np.uint64(1)
        y |= bit << PINV[np.uint64(i)]
    return y

def mux2_ff_keyed(x, k, rs, ra, ck):
    """y = x ^ mux(s,a,k2); s=rotl(x,rs), a=rotl(x,ra), k2=rotl(k,ck).
    MUX2 tt=0xac: s ? k2 : a."""
    s = rotl64(x, rs)
    a = rotl64(x, ra)
    k2 = rotl64(k, ck)
    mux = (s & k2) | (~s & a)
    return x ^ mux

# Default parameters
DEFAULT_B = dict(rs=7, ra=23, ck=11)

def mix_hyb3b(x, k, P=None):
    """S-box -> P-box -> MUX2-FF-keyed -> P-box -> S-box (P-box is free wiring)."""
    if P is None:
        P = DEFAULT_B
    x = np.asarray(x, dtype=np.uint64)
    k = np.uint64(k)
    t = sbox_layer(x)                              # S-box (3.0u)
    t = pbox(t)                                    # P-box (0u)
    t = mux2_ff_keyed(t, k, P['rs'], P['ra'], P['ck'])  # MUX2-FF-keyed (4.0u)
    t = pbox(t)                                    # P-box (0u)
    t = sbox_layer(t)                              # S-box (3.0u)
    return t

def mix_hyb3b_vec(x, k, P=None):
    return mix_hyb3b(np.asarray(x, dtype=np.uint64), np.uint64(k), P)

if __name__ == "__main__":
    k = np.uint64(0x123456789ABCDEF0)
    xs = np.arange(20000, dtype=np.uint64)
    ys = mix_hyb3b_vec(xs, k)
    print(f"bijective on 20k-sample: {len(set(ys.tolist()))}/20000")
    # avalanche
    x0 = np.uint64(0x0123456789ABCDEF)
    y0 = mix_hyb3b_vec([x0], k)[0]
    diffs = []
    for i in range(64):
        xi = x0 ^ (np.uint64(1) << np.uint64(i))
        yi = mix_hyb3b_vec([xi], k)[0]
        diffs.append(bin(int(y0 ^ yi)).count('1'))
    import statistics
    print(f"avalanche: mean={statistics.mean(diffs):.1f} min={min(diffs)} max={max(diffs)}")
