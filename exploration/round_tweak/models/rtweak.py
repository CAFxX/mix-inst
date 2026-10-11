"""Generalized parametric numpy model for the tweaking (hill-climbing) track.

Spec format (dict):
  name: str
  rkmult: int            # round-key rotation multiplier (default 13)
  pre:  64-bit int       # XOR into val before round 1 (default 0)
  post: 64-bit int       # XOR into out after round 6 (default 0)
  rounds: list of 6 dicts, each:
    nl:   ('s1',) | ('chi', o1, o2)
    pin:  None | ('rev',None) | ('byteswap',None) | ('nibperm',(p0..p7)) | ('rot',k)
    mask: None | (r, mask32)          # t ^= rotr(t,r) & mask  (after nl)
    lin:  None | (a,) | (a, b) | (a, b, c)
          # (a,)|(a,b): x ^ rotl(x,a) [^ rotl(x,b)]   (identity kept)
          # (a,b,c):    rotl(x,a)^rotl(x,b)^rotl(x,c) (identity dropped)
    pout: None | perm (same format as pin)
    rc:   32-bit int                  # round constant XORed into F output
    fm:   0 | m                       # final mixing y ^ rotl(y,m), round 6
Key mode is always xor-after (keyin not swept in this track).
"""
import numpy as np

MASK32 = np.uint64(0xFFFFFFFF)
MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)
S1 = np.array([0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10],
              dtype=np.uint64)

NIBPERM_DEFAULT = (7, 2, 5, 0, 3, 6, 1, 4)


def rotl32_np(x, r):
    r = int(r) % 32
    if r == 0:
        return x & MASK32
    return (((x << np.uint64(r)) | (x >> np.uint64(32 - r))) & MASK32)


def rotr32_np(x, r):
    return rotl32_np(x, (-int(r)) % 32)


def rotl64_np(x, r):
    r = int(r) % 64
    if r == 0:
        return x & MASK64
    return (((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & MASK64)


def sbox32_np(x):
    out = np.zeros_like(np.asarray(x, dtype=np.uint64))
    xv = np.asarray(x, dtype=np.uint64) & MASK32
    for i in range(8):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(S1, nib) << np.uint64(4 * i)
    return out & MASK32


def chi_off_np(x, o1, o2):
    # b_i = a_i ^ (~a_{i+o1} & a_{i+o2}); matches r20 _chi32_np for (1,2)
    x = np.asarray(x, dtype=np.uint64) & MASK32
    return (x ^ ((~rotr32_np(x, o1)) & rotr32_np(x, o2))) & MASK32


def lin_np(x, rots):
    # rots: (a,) or (a,b) -> x ^ R^a [^ R^b]  (identity kept, odd-term)
    #       (a,b,c)       -> R^a ^ R^b ^ R^c   (identity dropped, odd-term)
    x = np.asarray(x, dtype=np.uint64) & MASK32
    if len(rots) == 3:
        y = np.zeros_like(x)
    else:
        y = x.copy()
    for r in rots:
        y ^= rotl32_np(x, r)
    return y & MASK32


def _perm_index(kind, arg):
    idx = np.arange(32)
    if kind == 'rev':
        return 31 - idx
    if kind == 'byteswap':
        return (3 - idx // 8) * 8 + (idx % 8)
    if kind == 'nibperm':
        p = np.array(arg, dtype=np.int64)
        assert p.shape == (8,) and sorted(p.tolist()) == list(range(8))
        return p[idx // 4] * 4 + (idx % 4)
    if kind == 'rot':
        return (idx - int(arg)) % 32
    raise ValueError(kind)


_PERM_CACHE = {}


def pbox_np(x, perm):
    kind, arg = perm[0], perm[1]
    ck = (kind, tuple(arg) if isinstance(arg, (list, tuple)) else arg)
    idx = _PERM_CACHE.get(ck)
    if idx is None:
        idx = _perm_index(kind, arg)
        _PERM_CACHE[ck] = idx
    x = np.asarray(x, dtype=np.uint64) & MASK32
    out = np.zeros_like(x)
    for i in range(32):
        out |= ((x >> np.uint64(int(idx[i]))) & np.uint64(1)) << np.uint64(i)
    return out & MASK32


def rk32_np(k, i, c):
    # i 1-based; matches r20 _rk32_std_np for c=13
    r = (int(c) * (int(i) + 1)) % 64
    return (rotl64_np(k, r) ^ (np.uint64(int(i) + 1) * GOLDEN64)) & MASK32


def F_np(R, rk, rs):
    x = np.uint64(R) & MASK32
    pin = rs.get('pin')
    if pin:
        x = pbox_np(x, pin)
    nl = rs['nl']
    if nl[0] == 's1':
        t = sbox32_np(x)
    else:
        t = chi_off_np(x, nl[1], nl[2])
    ms = rs.get('mask')
    if ms:
        t = (t ^ (rotr32_np(t, ms[0]) & np.uint64(ms[1]))) & MASK32
    lin = rs.get('lin')
    if lin:
        t = lin_np(t, lin)
    pout = rs.get('pout')
    if pout:
        t = pbox_np(t, pout)
    rc = np.uint64(rs.get('rc', 0))
    fm = rs.get('fm', 0)
    if fm == '311':
        # F = rotl32(chi,3) ^ rotl32(chi,11) ^ rk  (r19 fm311 form)
        return (rotl32_np(t, 3) ^ rotl32_np(t, 11) ^ rk ^ rc) & MASK32
    if fm:
        y = (t ^ rk ^ rc) & MASK32
        return (y ^ rotl32_np(y, fm)) & MASK32
    return (t ^ rk ^ rc) & MASK32


def feistel_tw_np(x, k, spec):
    c = spec.get('rkmult', 13)
    xa = (np.asarray(x, dtype=np.uint64) ^ np.uint64(spec.get('pre', 0))) & MASK64
    ka = np.asarray(k, dtype=np.uint64)
    L = (xa >> np.uint64(32)) & MASK32
    R = xa & MASK32
    for i, rs in enumerate(spec['rounds'], start=1):
        rk = rk32_np(ka, i, c)
        nR = (L ^ F_np(R, rk, rs)) & MASK32
        L, R = R, nR
    return ((((R << np.uint64(32)) | L) & MASK64) ^ np.uint64(spec.get('post', 0))) & MASK64


CANDS = {}


def register(name, spec):
    def fn(x, k, _s=spec):
        return feistel_tw_np(x, k, _s)
    fn.__name__ = name
    CANDS[name] = (spec, fn)
    return fn


def _selftest():
    import sys
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round20/models")
    import r20
    rng = np.random.default_rng(0x1234)
    V = rng.integers(0, 2**64, size=256, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=256, dtype=np.uint64)
    # chi offset identities vs r20
    assert np.all(chi_off_np(V & MASK32, 1, 2) == r20._chi32_np(V & MASK32))
    assert np.all(chi_off_np(V & MASK32, 1, 3) == r20._chi32v_np(V & MASK32))
    assert np.all(chi_off_np(V & MASK32, 3, 1) == r20._chi32w_np(V & MASK32))
    # rk identity for c=13
    for i in (1, 3, 6):
        assert np.all(rk32_np(K, i, 13) == r20._rk32_std_np(K, i)), i
    # full-candidate identity: chioff13all
    spec = {'rkmult': 13, 'pre': 0, 'post': 0, 'rounds': [
        {'nl': ('s1',), 'lin': (3, 11)},
        {'nl': ('chi', 1, 3), 'lin': (3, 11)},
        {'nl': ('s1',), 'lin': (3, 11)},
        {'nl': ('chi', 1, 3), 'lin': (3, 11)},
        {'nl': ('s1',), 'lin': (3, 11)},
        {'nl': ('chi', 1, 3), 'lin': None},
    ]}
    ref = r20.r20_feist6_alt_notr_chioff13all_nw(V, K)
    got = feistel_tw_np(V, K, spec)
    assert np.all(ref == got), "chioff13all mismatch"
    # chioff31 identity
    spec31 = {'rkmult': 13, 'pre': 0, 'post': 0, 'rounds': [
        {'nl': ('s1',), 'lin': (3, 11)},
        {'nl': ('chi', 3, 1), 'lin': (3, 11)},
        {'nl': ('s1',), 'lin': (3, 11)},
        {'nl': ('chi', 3, 1), 'lin': (3, 11)},
        {'nl': ('s1',), 'lin': (3, 11)},
        {'nl': ('chi', 1, 2), 'lin': None},
    ]}
    ref31 = r20.r20_feist6_alt_notr_chioff31_nw(V, K)
    assert np.all(ref31 == feistel_tw_np(V, K, spec31)), "chioff31 mismatch"
    # pbox sanity: rev is an involution, rot matches rotl
    assert np.all(pbox_np(pbox_np(V & MASK32, ('rev', None)), ('rev', None))
                  == (V & MASK32))
    assert np.all(pbox_np(V & MASK32, ('rot', 7)) == rotl32_np(V & MASK32, 7))
    print("rtweak selftest: ALL PASS")


if __name__ == "__main__":
    _selftest()
