"""Shared screening library for the mix-instruction design-space exploration.

Statistical core: EXACT copies of the null-distribution functions from
~/workspace/mix/tests_final.py (peer-reviewed; brute-force verified on toy
widths). Do NOT modify the copied functions; add new helpers below the line.

Screening protocol (identical for every candidate):
  keys: 10 diverse keys (8 fixed + 2 seeded-random, recorded below)
  N = 2^18 per (key, config)
  Input scenarios (per-bit monobit max|z| each; reductions on SEQ and PTR-j8):
    SEQ            I=0, j=1 (+ Lemire X in {10,1000,2^32} exact, mask m in
                             {8,32}, mod y in {7,1000} exact-preimage)
    PTR-j8/j16     I=0, j=8/16 (aligned pointers; low 3-4 input bits const 0)
    MPOW2          j=c*2^k, c in {3,5,7}, k in {3,4,5,6} (struct arrays)
    HIGH-ONLY      I=0xFFFFFFFF00000000, j=2^32 (only high bits vary)
    DESC           I=0, j=2^64-1 / 2^64-8 (descending)
    POW2           j=2^k, k in {0..6,8,16,32,48} (k=63 skipped: period 2,
                     degenerate for ANY function), I=0
    STRIDE-3       I=0, j=3; STRIDE-FIB I=12345, j=0x9E3779B97F4A7C15
    SINGLE-BIT     val=1<<k, k=0..63 as a standalone 64-element set
                     (catches wire-through: output bit == input bit gives
                     c=1/64 -> |z|=7.75)
    KEY-SWEEP      128 fixed SEQ inputs x 64 seeded-random keys, per-bit
                     monobit over the key axis (gross key-dependence check:
                     "key ignored" gives |z|=8)
  Strided configs are deduplicated to the sequence's period so z stays
  calibrated. mask-m=32 = max(chi2 lo16, chi2 hi16, collision z) — a 2^32-bin
  chi2 is infeasible AND statistically degenerate at N=2^18 (documented).
Screening bar: per-scenario worst per-bit |z| < 4.0 AND all reduction |z| < 4.5
-> PASS, else FLAG (numbers still recorded; a flag is a screen signal, not a
verdict; the flagging scenario is recorded).
"""
import math
import numpy as np

M64 = (1 << 64) - 1
U64 = np.uint64
MASK64 = U64(0xFFFFFFFFFFFFFFFF)
BIT = np.arange(64, dtype=np.uint64)
W64 = 1 << 64

# ---------------------------------------------------------------------------
# EXACT copies from ~/workspace/mix/tests_final.py (do not edit)
# ---------------------------------------------------------------------------

def lemire_np(S, X):
    X = np.asarray(X, dtype=np.uint64)
    hi = (S.astype(object) * X.astype(object)) >> 64
    return np.asarray(hi, dtype=np.uint64)


def chi2_z(counts, n):
    e = n / len(counts)
    chi2 = ((counts - e) ** 2 / e).sum()
    df = len(counts) - 1
    return (chi2 - df) / np.sqrt(2 * df)


def chi2_z_exact(counts, expected):
    """Pearson chi-square against exact (possibly non-uniform) expected counts."""
    c = np.asarray(counts, dtype=float)
    e = np.asarray(expected, dtype=float)
    chi2 = ((c - e) ** 2 / e).sum()
    df = len(c) - 1
    return (chi2 - df) / np.sqrt(2 * df)


def lemire_preimg(lo, hi, X):
    """Exact # of s in [0,2^64) with ((s*X)>>64) in [lo,hi).
    (s*X)>>64 = r  <=>  r*2^64/X <= s < (r+1)*2^64/X, so the count is
    ceil(hi*2^64/X) - ceil(lo*2^64/X)."""
    return ((hi * W64 + X - 1) // X) - ((lo * W64 + X - 1) // X)


def mod_preimg(y):
    """Exact # of s in [0,2^64) with s mod y = r, for r = 0..y-1."""
    return [((W64 - 1 - r) // y) + 1 for r in range(y)]

# ---------------------------------------------------------------------------
# end of verbatim copies
# ---------------------------------------------------------------------------

# Key set: 8 fixed diverse keys + 2 seeded-random (rng seed 0xC0FFEE).
_rng = np.random.default_rng(0xC0FFEE)
_randkeys = [int(x) for x in _rng.integers(0, 2**64, size=2, dtype=np.uint64)]
KEYS = [
    0x0000000000000000,
    0xFFFFFFFFFFFFFFFF,
    0xAAAAAAAAAAAAAAAA,
    0x5555555555555555,
    0xDEADBEEFDEADBEEF,
    0x9E3779B97F4A7C15,
    0x0000000000001234,
    0x0123456789ABCDEF,
] + _randkeys
assert len(KEYS) == 10

N = 1 << 18
POW2_KS = [0, 1, 2, 3, 4, 5, 6, 8, 16, 32, 48]  # k=63 excluded: period 2, degenerate
LEMURE_XS = [10, 1000, 1 << 32]
MASK_MS = [8, 32]
MOD_YS = [7, 1000]
# --- scenario catalog: quick screen (full battery on finalists only) ---
PTR_JS = [8, 16]
MPOW2_CS = [3, 5, 7]
MPOW2_KS = [3, 4, 5, 6]
HIGH_ONLY_I = 0xFFFFFFFF00000000
HIGH_ONLY_J = 1 << 32
DESC_JS = [(1 << 64) - 1, (1 << 64) - 8]
FIB_I, FIB_J = 12345, 0x9E3779B97F4A7C15
KEYSWEEP_NINPUTS = 128
KEYSWEEP_NKEYS = 64
KEYSWEEP_SEED = 0x5EED
_ksw_rng = np.random.default_rng(KEYSWEEP_SEED)
KEYSWEEP_KEYS = np.array(
    [int(x) for x in _ksw_rng.integers(0, 2**64, size=KEYSWEEP_NKEYS, dtype=np.uint64)],
    dtype=np.uint64)
assert len(np.unique(KEYSWEEP_KEYS)) == KEYSWEEP_NKEYS


def rotl64_np(v, r):
    r = np.asarray(r, dtype=np.uint64) & U64(63)
    return np.where(r == 0, v, (((v << r) | (v >> (U64(64) - r)))) & MASK64)


def rotr64_np(v, r):
    return rotl64_np(v, (-np.asarray(r, dtype=np.uint64)) & U64(63))


# ---- fast PRESENT pLayer (bit-matrix transpose of 16x4) --------------------
# P(i) = 16*i mod 63 == transpose of the 16-row x 4-col bit matrix:
# bit (nibble s, bit t) -> position 16*t + s. Implemented as a 2^16 table:
# T[w] packs, per 16-bit lane t, the 4 bits (bit t of nibbles 0..3 of w) in
# the lane's low 4 bits. perm(x) = OR_c (T[chunk_c] << 4c); no lane spill
# because each lane holds <= 4 bits and 4c <= 12.
def _build_pperm_table():
    T = np.zeros(1 << 16, dtype=np.uint64)
    for w in range(1 << 16):
        acc = 0
        for t in range(4):
            field = 0
            for u in range(4):
                if (w >> (4 * u + t)) & 1:
                    field |= 1 << u
            acc |= field << (16 * t)
        T[w] = np.uint64(acc)
    return T


_PPERM_T = _build_pperm_table()


def present_perm_np(x):
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(x)
    for c in range(4):
        chunk = ((x >> U64(16 * c)) & U64(0xFFFF)).astype(np.int64)
        y |= _PPERM_T[chunk] << U64(4 * c)
    return y


def present_sbox_table():
    return np.array([0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
                     0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2], dtype=np.uint64)


_SHIFTS4 = np.arange(16, dtype=np.uint64) * U64(4)


def sbox16_np(x, table):
    """Apply a 4-bit S-box table to all 16 nibbles (vectorized)."""
    shp = np.shape(x)
    xf = np.asarray(x, dtype=np.uint64).reshape(-1)
    nib = ((xf[:, None] >> _SHIFTS4) & U64(0xF))
    y = (np.take(np.asarray(table, dtype=np.uint64), nib.astype(np.int64))
         << _SHIFTS4).sum(axis=1)
    return y.reshape(shp)


# ---- statistical helpers ---------------------------------------------------

def perbit_maxz(S):
    """max_b |(cnt_b - n/2)| / sqrt(n/4) over the 64 output bits (looped, no
    134MB temporaries). Returns (maxz, argbit)."""
    S = np.asarray(S, dtype=np.uint64)
    n = S.shape[0]
    denom = math.sqrt(n / 4)
    best, argb = 0.0, 0
    for b in range(64):
        c = int((((S >> U64(b)) & U64(1)).sum()))
        z = abs((c - n / 2) / denom)
        if z > best:
            best, argb = z, b
    return best, argb


def strided_distinct(I, j, n):
    """Distinct values of I, I+j, ... (up to n). For j = 2^k the period is
    2^(64-k); dedup keeps the monobit z calibrated (repeats would inflate it
    by sqrt(n/P) under the null)."""
    j = int(j) & M64
    if j == 0:
        return np.array([U64(I & M64)])
    g = math.gcd(j, 1 << 64)
    period = (1 << 64) // g
    m = min(n, period)
    return (U64(I & M64) + U64(j) * np.arange(m, dtype=np.uint64))


def lemire_z(S, X):
    n = S.shape[0]
    R = lemire_np(S, X)
    if X <= 1024:
        bounds = list(range(X + 1))
    else:
        B = 1024
        bounds = [(k * X) // B for k in range(B + 1)]
    nb = len(bounds) - 1
    E = np.array([lemire_preimg(bounds[k], bounds[k + 1], X) * n / W64
                  for k in range(nb)])
    if X <= 1024:
        cnt = np.bincount(R.astype(np.int64), minlength=X).astype(float)
    else:
        idx = np.digitize(R.astype(object), bounds[1:-1], right=False)
        cnt = np.bincount(np.asarray(idx, dtype=np.int64), minlength=nb).astype(float)
    assert len(cnt) == nb and (E > 0).all()
    return chi2_z_exact(cnt, E)


def mask_z(S, m):
    n = S.shape[0]
    B = 1 << m
    if B > (1 << 20):
        raise ValueError(f"mask m={m}: {B} bins infeasible/degenerate at N={n}")
    cnt = np.bincount((S & U64(B - 1)).astype(np.int64), minlength=B).astype(float)
    return chi2_z(cnt, n)


def mask32_z(S):
    """Uniformity of the low 32 bits at N=2^18. A 2^32-bin chi2 is both
    infeasible (32 GiB bincount) and statistically degenerate (e = N/2^32
    ~= 6e-5 per bin << 1). Instead: chi2 on each 16-bit half (2^16 bins,
    e = N/2^16 = 4) plus a collision-count z on the full 32-bit word
    (expected C(N,2)/2^32 ~= 8.0, ~Poisson). Returns worst |z| with label."""
    n = S.shape[0]
    w = (S & U64(0xFFFFFFFF)).astype(np.int64)
    lo = w & 0xFFFF
    hi = (w >> 16) & 0xFFFF
    z_lo = chi2_z(np.bincount(lo, minlength=1 << 16).astype(float), n)
    z_hi = chi2_z(np.bincount(hi, minlength=1 << 16).astype(float), n)
    # collision test on the full 32-bit word
    _, counts = np.unique(w, return_counts=True)
    coll = int(((counts * (counts - 1)) // 2).sum())
    exp_coll = (n * (n - 1) / 2) / (1 << 32)
    z_coll = (coll - exp_coll) / math.sqrt(exp_coll)
    zs = {"mask32-lo16": z_lo, "mask32-hi16": z_hi, "mask32-coll": z_coll}
    t = max(zs, key=lambda k: abs(zs[k]))
    return t, zs[t]


def mod_z(S, y):
    n = S.shape[0]
    R = (S % np.uint64(y)).astype(np.int64)
    E = np.array(mod_preimg(y), dtype=np.float64) * (n / W64)  # float64: no int64 overflow
    cnt = np.bincount(R, minlength=y).astype(float)
    return chi2_z_exact(cnt, E)


def screen(fn, name, verbose=True):
    """Run the identical screening protocol on fn(val, key) -> uint64 array.
    fn must accept numpy uint64 arrays (broadcastable 1-D) and return uint64.
    Returns a dict with per-scenario worst-case stats and the verdict."""
    K = np.uint64
    pb = {}   # scenario -> [worst |z|, loc, n_flags]
    rd = {}   # scenario -> [worst |z|, loc, n_flags]

    def upd_pb(scen, z, loc):
        r = pb.setdefault(scen, [0.0, None, 0])
        if z > r[0]:
            r[0], r[1] = float(z), loc
        r[2] += (z >= 4.0)

    def upd_rd(scen, z, loc):
        az = abs(float(z))
        r = rd.setdefault(scen, [0.0, None, 0])
        if az > r[0]:
            r[0], r[1] = az, loc
        r[2] += (az >= 4.5)

    def reductions(S, key, scen):
        for X in LEMURE_XS:
            upd_rd(scen, lemire_z(S, X), (key, f"lemire-X={X}"))
        for m in MASK_MS:
            if m == 32:
                t, rz = mask32_z(S)
                upd_rd(scen, rz, (key, t))
            else:
                upd_rd(scen, mask_z(S, m), (key, f"mask-m={m}"))
        for y in MOD_YS:
            upd_rd(scen, mod_z(S, y), (key, f"mod-{y}"))

    def seq_pb(V, key, scen):
        S = np.asarray(fn(V, np.full(V.shape[0], K(key), dtype=np.uint64)),
                       dtype=np.uint64)
        z, b = perbit_maxz(S)
        upd_pb(scen, z, (key, b))
        return S

    for key in KEYS:
        S = seq_pb(np.arange(N, dtype=np.uint64), key, "SEQ")
        reductions(S, key, "SEQ")
        S = seq_pb(strided_distinct(0, PTR_JS[0], N), key, "PTR-j8")
        reductions(S, key, "PTR-j8")
        seq_pb(strided_distinct(0, PTR_JS[1], N), key, "PTR-j16")
        for c in MPOW2_CS:
            for kk in MPOW2_KS:
                seq_pb(strided_distinct(0, c * (1 << kk), N), key,
                       f"MPOW2-{c}x2^{kk}")
        seq_pb(strided_distinct(HIGH_ONLY_I, HIGH_ONLY_J, N), key, "HIGH-ONLY")
        for j in DESC_JS:
            seq_pb(strided_distinct(0, j, N), key, f"DESC-j={(j & M64):#x}")
        for kk in POW2_KS:
            seq_pb(strided_distinct(0, 1 << kk, N), key, f"POW2-2^{kk}")
        seq_pb(strided_distinct(0, 3, N), key, "STRIDE-3")
        seq_pb(strided_distinct(FIB_I, FIB_J, N), key, "STRIDE-FIB")
        seq_pb((np.uint64(1) << np.arange(64, dtype=np.uint64)), key, "SINGLE-BIT")

    # KEY-SWEEP: fixed inputs x 64 keys, per-bit monobit over the key axis.
    # (n=64/key-axis cell; multiplicity note: ~8k cells, so an isolated
    # |z| in [4.0,4.5) is plausibly null noise — a real key-dependence
    # failure, e.g. "key ignored", gives |z|=8 and/or many flagged cells.)
    Vin = np.arange(KEYSWEEP_NINPUTS, dtype=np.uint64)
    Sf = np.asarray(fn(np.tile(Vin, KEYSWEEP_NKEYS),
                       np.repeat(KEYSWEEP_KEYS, KEYSWEEP_NINPUTS)),
                    dtype=np.uint64).reshape(KEYSWEEP_NKEYS, KEYSWEEP_NINPUTS)
    for j in range(KEYSWEEP_NINPUTS):
        z, b = perbit_maxz(Sf[:, j])
        upd_pb("KEY-SWEEP", z, (int(Vin[j]), b))

    flagged_pb = {s: r for s, r in pb.items() if r[0] >= 4.0}
    flagged_rd = {s: r for s, r in rd.items() if r[0] >= 4.5}
    gw_pb = max(pb.items(), key=lambda kv: kv[1][0])
    gw_rd = max(rd.items(), key=lambda kv: kv[1][0])
    verdict = "PASS" if not flagged_pb and not flagged_rd else "FLAG"
    res = dict(
        name=name, verdict=verdict,
        worst_perbit_z=gw_pb[1][0], perbit_loc=(gw_pb[0],) + tuple(gw_pb[1][1]),
        worst_red_z=gw_rd[1][0], red_loc=(gw_rd[0],) + tuple(gw_rd[1][1]),
        per_scenario_pb={s: dict(worst_z=r[0], loc=r[1], n_flags=r[2])
                         for s, r in pb.items()},
        per_scenario_red={s: dict(worst_z=r[0], loc=r[1], n_flags=r[2])
                          for s, r in rd.items()},
        flagged_pb_scenarios=sorted(flagged_pb),
        flagged_red_scenarios=sorted(flagged_rd))
    if verbose:
        pl = res["perbit_loc"]
        pl_loc = f"in={pl[1]}" if pl[0] == "KEY-SWEEP" else f"key={pl[1]:#018x}"
        rl = res["red_loc"]
        print(f"[{name}] per-bit worst |z|={res['worst_perbit_z']:.2f} "
              f"(scen={pl[0]} {pl_loc} bit={pl[2]}); "
              f"reduction worst |z|={res['worst_red_z']:.2f} (scen={rl[0]} "
              f"key={rl[1]:#018x} {rl[2]}); "
              f"flagged pb: {res['flagged_pb_scenarios'] or 'none'}; "
              f"flagged red: {res['flagged_red_scenarios'] or 'none'} -> {verdict}")
    return res


def check_model_equiv(scalar_fn, np_fn, name, trials=300, seed=1234):
    """Assert scalar model == vectorized model on random pairs."""
    rng = np.random.default_rng(seed)
    V = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    K = rng.integers(0, 2**64, size=trials, dtype=np.uint64)
    got = np.asarray(np_fn(V, K), dtype=np.uint64)
    for i in range(trials):
        exp = scalar_fn(int(V[i]), int(K[i])) & M64
        assert int(got[i]) == exp, (name, i, hex(exp), hex(int(got[i])))
    print(f"[{name}] scalar == vectorized on {trials} pairs: OK")


def bijectivity_spotcheck(fn, name, n=200000, seed=99):
    """Sanity net for implementation bugs (NOT a proof): for 3 fixed keys,
    hash n random distinct inputs; a non-bijective map with any appreciable
    collision rate shows collisions here (birthday bound: for a true
    permutation, P(any collision) over 2e5 samples of 2^64 is ~1e-9).
    The real guarantee is the construction argument (bijective stages)."""
    rng = np.random.default_rng(seed)
    for key in KEYS[:3]:
        V = np.unique(rng.integers(0, 2**64, size=2 * n, dtype=np.uint64))[:n]
        assert len(V) == n  # (birthday: need ~2n draws for n uniques at 2^64)
        S = np.asarray(fn(V, np.full(n, np.uint64(key), dtype=np.uint64)),
                       dtype=np.uint64)
        if len(np.unique(S)) != n:
            raise AssertionError(f"[{name}] COLLISION at key={key:#x}: not bijective!")
    print(f"[{name}] bijectivity spot-check: no collisions in 3x{n} samples: OK")


if __name__ == "__main__":
    # self-test: fast pLayer vs scalar definition; lemire/mod sanity
    P = np.array([(16 * i) % 63 for i in range(63)] + [63], dtype=np.int64)
    def perm_scalar(x):
        y = 0
        for i in range(64):
            if (x >> i) & 1:
                y |= 1 << int(P[i])
        return y
    rng = np.random.default_rng(7)
    V = rng.integers(0, 2**64, size=5000, dtype=np.uint64)
    G = present_perm_np(V)
    for i in range(5000):
        assert int(G[i]) == perm_scalar(int(V[i])), i
    print("fast PRESENT pLayer == scalar pLayer on 5000 values: OK")
    # lemire_preimg spot check vs brute force on a toy width (2^12 domain)
    W = 1 << 12
    def preimg_toy(lo, hi, X):
        return sum(1 for s in range(W) if lo <= ((s * X) >> 12) < hi)
    for X in (3, 10, 100):
        for lo, hi in ((0, 1), (1, 3), (0, X), (X - 2, X)):
            got = ((hi * W + X - 1) // X) - ((lo * W + X - 1) // X)
            assert got == preimg_toy(lo, hi, X), (X, lo, hi)
    print("lemire_preimg formula verified by brute force on 2^12 domain: OK")
    # chi2_z_exact sanity: exactly-uniform counts give chi2=0 -> z=-df/sqrt(2df)
    # (the transform reports "too good to be true" as negative); noisy counts
    # drawn from the null give |z| ~ O(1).
    cnt = np.full(1000, 250.0)
    z0 = chi2_z_exact(cnt, np.full(1000, 250.0))
    assert abs(z0 - (-999 / np.sqrt(2 * 999))) < 1e-9, z0
    rng2 = np.random.default_rng(11)
    noisy = rng2.multinomial(250_000, np.full(1000, 1 / 1000)).astype(float)
    zn = chi2_z_exact(noisy, np.full(1000, 250.0))
    assert abs(zn) < 4.0, zn
    print(f"chi2_z_exact sanity: OK (uniform z={z0:.2f}, noisy z={zn:+.2f})")
