"""3-stage hybrid: MUX2 -> 4-term linear -> MUX2 (V4 reconsideration).

The 4-term linear measured 5.5u (not 2.5u), killing all 4-stage options on
cost. This 3-stage keeps the proven DIFF-clean 4-term (O134) and the cheap
MUX2 (O138): 2.0 + 5.5 + 2.0 = 9.5u budget.

Bit-exact with hyb3.v (same parameters).
"""
import numpy as np

MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)

def rotl64(x, n):
    n %= 64
    if n == 0:
        return np.asarray(x, dtype=np.uint64)
    x = np.asarray(x, dtype=np.uint64)
    return (x << np.uint64(n)) | (x >> np.uint64(64 - n))

def mux2_layer(x, rs, ra, rb):
    """64 parallel MUX2 (tt=0xac): y[i] = s[i] ? b[i] : a[i]."""
    s = rotl64(x, rs)
    a = rotl64(x, ra)
    b = rotl64(x, rb)
    return (s & b) | (~s & a)

def lin4(x, p, q, r, s):
    """4-term rotl-xor linear: x ^ rotl(x,p)^rotl(x,q)^rotl(x,r)^rotl(x,s)."""
    return x ^ rotl64(x, p) ^ rotl64(x, q) ^ rotl64(x, r) ^ rotl64(x, s)

# Default parameters (v4_hyb3_0):
#   MUX2#1 (rs,ra,rb) = (7,23,41); 4-term (p,q,r,s) = w4t_0 KEEP [4,7,17,23];
#   MUX2#2 (rs,ra,rb) = (11,29,47); key rots c1=29, post=13.
DEFAULT = dict(rs1=7, ra1=23, rb1=41,
               p1=4, q1=7, r1=17, s1=23, c1=29,
               rs2=11, ra2=29, rb2=47)

def mix_hyb3(x, k, P=None):
    """3-stage hybrid mix. x, k: uint64 arrays/scalars.
    Key injected once at the 4-term stage (no pre/post whiten) to save 4u."""
    if P is None:
        P = DEFAULT
    x = np.asarray(x, dtype=np.uint64)
    k = np.uint64(k)
    t = mux2_layer(x, P['rs1'], P['ra1'], P['rb1'])   # MUX2 #1 (2.0u)
    t = lin4(t, P['p1'], P['q1'], P['r1'], P['s1']) ^ rotl64(k, P['c1'])  # 4-term+key (5.5u)
    t = mux2_layer(t, P['rs2'], P['ra2'], P['rb2'])   # MUX2 #2 (2.0u)
    return t

def mix_hyb3_vec(x, k, P=None):
    return mix_hyb3(np.asarray(x, dtype=np.uint64), np.uint64(k), P)

if __name__ == "__main__":
    k = np.uint64(0x123456789ABCDEF0)
    xs = np.arange(1000, dtype=np.uint64)
    ys = mix_hyb3_vec(xs, k)
    assert len(set(ys.tolist())) == 1000, "NOT bijective on sample!"
    print("bijective on 1000-sample: OK")
    # avalanche
    x0 = np.uint64(0x0123456789ABCDEF)
    y0 = mix_hyb3_vec([x0], k)[0]
    diffs = []
    for i in range(64):
        xi = x0 ^ (np.uint64(1) << np.uint64(i))
        yi = mix_hyb3_vec([xi], k)[0]
        diffs.append(bin(int(y0 ^ yi)).count('1'))
    import statistics
    print(f"avalanche: mean={statistics.mean(diffs):.1f} min={min(diffs)} max={max(diffs)}")
