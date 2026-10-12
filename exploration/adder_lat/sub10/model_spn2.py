"""2-round 4-bit SPN: y = S(P(S(x ^ k))) with Midori Sb0 + PRESENT P-box.
Target: <8u (2 + 3 + 0 + 3)."""
import numpy as np

# Midori Sb0
SB0 = np.array([0xC,0xA,0xD,0x3,0xE,0xB,0xF,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6], dtype=np.uint64)

# PRESENT P-box: P(i) = 16*i mod 63 for i<63, P(63)=63
# y[P(i)] = x[i]
PBOX = [(16*i) % 63 for i in range(63)] + [63]
# Inverse for implementation: y[i] = x[Pinv(i)]
PINV = [0]*64
for i, p in enumerate(PBOX):
    PINV[p] = i
PINV = np.array(PINV, dtype=np.uint64)

def sbox_layer(x):
    """16x Midori Sb0 in parallel. x: uint64 array."""
    y = np.zeros_like(x)
    for i in range(16):
        nib = (x >> np.uint64(4*i)) & np.uint64(0xF)
        # vectorized table lookup
        y |= SB0[nib] << np.uint64(4*i)
    return y

def pbox(x):
    """Bit permutation (wires). x: uint64 array."""
    y = np.zeros_like(x)
    for i in range(64):
        bit = (x >> np.uint64(i)) & np.uint64(1)
        y |= bit << np.uint64(PINV[i])
    return y

def mix_sub10(x, k):
    """y = S(P(S(x ^ k)))."""
    t = x ^ k
    t = sbox_layer(t)
    t = pbox(t)
    t = sbox_layer(t)
    return t

def mix_sub10_vec(x, k):
    """Vectorized version."""
    return mix_sub10(np.asarray(x, dtype=np.uint64), np.uint64(k))

if __name__ == "__main__":
    # Smoke test: bijectivity for fixed key (small sample)
    k = 0x123456789ABCDEF0
    xs = np.arange(1000, dtype=np.uint64)
    ys = mix_sub10_vec(xs, k)
    assert len(set(ys.tolist())) == 1000, "NOT bijective on sample!"
    print("bijective on 1000-sample: OK")
    # Avalanche: 1-bit input change -> how many output bits change?
    x0 = np.uint64(0x0123456789ABCDEF)
    y0 = mix_sub10_vec([x0], k)[0]
    diffs = []
    for i in range(64):
        xi = x0 ^ (np.uint64(1) << np.uint64(i))
        yi = mix_sub10_vec([xi], k)[0]
        diffs.append(bin(y0 ^ yi).count('1'))
    print(f"avalanche: min={min(diffs)} max={max(diffs)} mean={sum(diffs)/len(diffs):.1f}")
