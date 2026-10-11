"""Round 23 numpy models (vectorized): parameterized r22c-neighborhood SPN.

Baseline r22c_spn_mix4r_lp_nw: 4r keyed SPN x_{i+1} = L(P(S16(x_i ^ rk_i))),
P(i)=(5i+27)%64 (O34 validated single-64-cycle P-box), L = lin(3,11) =
x^rotl(x,3)^rotl(x,11), S16 = 16x S1 4-bit S-box,
rk_i = rotl64(key,13*(i+1)) ^ ((i+1)*GOLDEN64).

Round 23 varies, one axis at a time:
  P1: 3-round SPN (round-count cliff probe)
  P2: linear layer (a,b) pairs + odd-term 3-rotation linears at 4r
  P3: P-box sweep (validated affine + random permutations) at 4r
  P4: S-box variants in the S16 slot at 4r (must be 4-bit permutations)
  P5: L(P(S)) vs P(L(S)) order flip at 4r

Bijectivity argument (SPN chassis — every layer must be bijective):
  S-box layer bijective iff the 4-bit table is a permutation;
  P-box bijective iff the 64-map is a permutation;
  L bijective iff GF(2) rank 64 (checked pre-synthesis for every spec).
Each round is then bijective, hence the fixed-key cipher is bijective.
Empirical 2M x 2-key collision-free check runs per candidate (S0 gate).
"""
import numpy as np

MASK32 = np.uint64(0xFFFFFFFF)
MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
GOLDEN64 = np.uint64(0x9E3779B97F4A7C15)

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]


def _rotl64_np(x, r):
    r %= 64
    if r == 0:
        return x & MASK64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & MASK64


def _rk64_np(k, i, ks="golden"):
    with np.errstate(over="ignore"):
        r = _rotl64_np(k, 13 * (i + 1))
        if ks == "golden":
            return (r ^ (np.uint64(i + 1) * GOLDEN64)) & MASK64
        elif ks == "norot_const":
            # P9 probe: no round constant (tests ABC constant-folding null)
            return r & MASK64
        else:
            raise ValueError(ks)


def _sbox_layer64_het_np(x, tabs):
    """Per-lane S-box layer: lane i uses tabs[i] (each a 4-bit permutation).
    Bijective iff every lane table is a permutation (checked at spec build)."""
    out = np.zeros_like(np.asarray(x, dtype=np.uint64))
    xv = np.asarray(x, dtype=np.uint64) & MASK64
    assert len(tabs) == 16
    for i in range(16):
        t = np.asarray(tabs[i], dtype=np.uint64)
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(t, nib) << np.uint64(4 * i)
    return out & MASK64


def _sbox_layer64_np(x, tab):
    out = np.zeros_like(np.asarray(x, dtype=np.uint64))
    xv = np.asarray(x, dtype=np.uint64) & MASK64
    t = np.asarray(tab, dtype=np.uint64)
    for i in range(16):
        nib = ((xv >> np.uint64(4 * i)) & np.uint64(0xF)).astype(np.int64)
        out |= np.take(t, nib) << np.uint64(4 * i)
    return out & MASK64


def _perm_np(x, pmap):
    """Bit permutation: out[pmap[i]] = in[i]."""
    out = np.zeros_like(np.asarray(x, dtype=np.uint64))
    xv = np.asarray(x, dtype=np.uint64) & MASK64
    for i, d in enumerate(pmap):
        out |= ((xv >> np.uint64(i)) & np.uint64(1)) << np.uint64(d)
    return out & MASK64


def _lin_rots_np(x, rots, include_id=True):
    """L(x) = [x ^] rotl(x,r1) ^ ... over the rots list.
    include_id=True:  x ^ R^a ^ R^b            (2 rots -> 3 terms, p(1)=1)
    include_id=False:     R^a ^ R^b ^ R^c      (3 rots, r21 3rot_ns form, p(1)=1)
    Both forms have p(1)=1 -> gcd(p, z^64+1)=1 -> rank 64 guaranteed.
    (With-identity 3-rotation x^R^a^R^b^R^c has p(1)=0 and CAN be singular.)"""
    xv = np.asarray(x, dtype=np.uint64) & MASK64
    y = xv if include_id else np.zeros_like(xv)
    for r in rots:
        y = (y ^ _rotl64_np(xv, r)) & MASK64
    return y


def _gf2_rank64(apply):
    M = np.zeros((64, 64), dtype=np.uint8)
    for i in range(64):
        y = int(apply(np.uint64(1) << np.uint64(i)))
        for j in range(64):
            M[j, i] = (y >> j) & 1
    r = 0
    for c in range(64):
        piv = None
        for rr in range(r, 64):
            if M[rr, c]:
                piv = rr
                break
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        for rr in range(64):
            if rr != r and M[rr, c]:
                M[rr] ^= M[r]
        r += 1
    return r


def _is_perm16(tab):
    return sorted(tab) == list(range(16))


def _is_perm64(pmap):
    return sorted(pmap) == list(range(64))


def _spn(v, k, nrounds, sbox, pbox, rots, order="LPS", include_id=True,
         sbox_rounds=None, ks="golden"):
    """One round: t = S(x^rk); LPS: x' = L(P(t)); PLS: x' = P(L(t)).
    sbox forms: 16-list (homogeneous all rounds), 16x16-list (per-lane all
    rounds), or sbox_rounds (list of nrounds, each 16-list or 16x16-list).
    Every lane table must be a 4-bit permutation (spec-build gate) — then
    each S-layer is bijective and the fixed-key cipher is bijective.
    ks: "golden" (default rk=rotl(key,13(i+1))^(i+1)*GOLDEN) or "norot_const"
    (rk=rotl(key,13(i+1)), P9 cost-model probe)."""
    x = np.asarray(v, dtype=np.uint64) & MASK64
    kk = np.asarray(k, dtype=np.uint64) & MASK64
    if sbox_rounds is None:
        sbox_rounds = [sbox] * nrounds
    assert len(sbox_rounds) == nrounds
    for i in range(nrounds):
        sb = sbox_rounds[i]
        if isinstance(sb[0], (list, tuple)):
            t = _sbox_layer64_het_np(x ^ _rk64_np(kk, i, ks), sb)
        else:
            t = _sbox_layer64_np(x ^ _rk64_np(kk, i, ks), sb)
        if order == "LPS":
            if pbox is not None:
                t = _perm_np(t, pbox)
            t = _lin_rots_np(t, rots, include_id)
        elif order == "PLS":
            t = _lin_rots_np(t, rots, include_id)
            if pbox is not None:
                t = _perm_np(t, pbox)
        else:
            raise ValueError(order)
        x = t & MASK64
    return x & MASK64


# O34 baseline P-box: (5*i+27)%64
_O34_P = [(5 * i + 27) % 64 for i in range(64)]


def _selftest_r23():
    # baseline reproduces r22c exactly
    import sys
    sys.path.insert(0, "/home/hatch/workspace/mix/exploration/round22/models")
    import r22
    rng = np.random.default_rng(0x23)
    V = rng.integers(0, 2**64, size=2000, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=2000, dtype=np.uint64)
    a = _spn(V, K, 4, S1, _O34_P, (3, 11), "LPS")
    b = r22.r22c_spn_mix4r_lp_nw(V, K)
    assert np.all(a == b), "r23 baseline != r22c!"
    # rank checks for the spec'd linear layers happen in specs23.py
    print("r23 self-test: baseline == r22c on 2000 vectors OK")


# Named candidate functions are installed by specs23 (getattr-compatible
# with check_rtl's dotted.model.fn interface).
def _install_specs(specs):
    for s in specs:
        name = s["name"]
        # normalize sbox_lanes -> sbox_rounds (per-lane tables, all rounds)
        sr = s.get("sbox_rounds")
        if sr is None and s.get("sbox_lanes"):
            sr = [s["sbox_lanes"]] * s["nrounds"]
        def _fn(v, k, _s=s, _sr=sr):
            return _spn(v, k, _s["nrounds"], _s["sbox"], _s["pbox"],
                        _s["rots"], _s["order"], _s.get("include_id", True),
                        _sr, _s.get("ks", "golden"))
        _fn.__name__ = name
        globals()[name] = _fn


# Auto-install on import so check_rtl's getattr(import_module(...), fn) works.
# (Loads the frozen specs23.json directly to avoid a circular import with
# specs23.py, which itself imports this module for helpers.)
try:
    import json as _json
    import os as _os
    _specfile = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                              "..", "specs23.json")
    if _os.path.exists(_specfile):
        _all = _json.load(open(_specfile))
        for _s in _all:
            _s["rots"] = tuple(_s["rots"])
        _install_specs(_all)
        del _s, _all
    del _specfile, _json, _os
except Exception:
    pass


if __name__ == "__main__":
    _selftest_r23()
    print("r23 model self-test passed")
