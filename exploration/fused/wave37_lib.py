#!/usr/bin/env python3
"""Wave-37: two-lane repair (intra-linear + AND-cross).

Fills the precise hole the V-series kill left (ledger rows wave-36 / wave-37):

  (V-kill-1) AND-only rule removed every linear term -> low-weight diffusion
      death: on single-bit inputs the ANDs never fire, PB lp=-inf 12/12.
      FIX: intra-lane LINEAR term (b33c-style `^xc` / `^yg`), load-bearing
      for low-weight diffusion (fat-autopsy lesson).
  (V-kill-2) rotation-coupled init y=rotl(x,11) made the two lanes affine
      copies -> cross ANDs collapsed to intra-lane ANDs up to rotation
      ("single-lane-in-disguise"); final linear part L(v)=v^rotl(v,28) had a
      4-dim kernel (gcd(28,64)=4).
      FIX: init carries a key-mixed AND term so y0 is NONLINEAR in xs;
      combiner rotation m even with r1 odd => linear part v^rotl(v,r1+m)
      has gcd(r1+m,64)=1 (bijective, trivial kernel).

Per-stage construction (ledger scope), generalized to L intra-lane linear
terms (37b co-design, 2026-10-11):
    xn = x ^ (xa&xb) ^ xc1 ^ ... ^ xcL ^ (xf&yg)
    yn = y ^ (yh&yi) ^ yj1 ^ ... ^ yjL ^ (xm&yn)
Intra-lane: AND (nonlinearity) + L linear terms (diffusion), b33c-style.
Cross-lane: strictly through ANDs (wave-34 CONFIRMED rule -- linear cross
terms build the deterministic DIFF skeleton that kills every variant).

L=1 MECHANISM-KILLED 2026-10-11 (track 8, inc 11): at key 0 the init AND is
key-killed -> y0 = rotl(x0,r1) exactly; on single-bit inputs NO AND fires in
any of 3 stages (distinct rotations of a single bit never collide), so the
whole function is LINEAR on the PB domain -> PB lp=-inf, schedule-independent.
PROVEN by firing probe (0/256 AND-outputs nonzero over 3 stages, 64 inputs).
The bootstrap needs denser linear spread: AND-fire P scales as (w/64)^2 in
the active-bit count w. L=3 verified: 128 firings over 3 stages at key 0
(stage-3 yi=yc=64/64 inputs fire), meanpop 30/64. XOR-tree depth: 5 terms
(L=2) and 7 terms (L=3) both = 3 XOR levels, so L=3 costs the same delay as
L=2 (~4.4-5u/stage); L=3 selected directly.

Init:
    x0 = xs ^ K
    y0 = rotl(xs,r1) ^ rotl(K,r2) ^ (rotl(xs,p) & rotl(K,q)), r1 odd, p != q
Combiner: out = x ^ rotl(y,m) ^ rotl(K,13), m even nonzero.

De-dup: not wave-34 (adds intra-linear terms), not b33c (two-lane +
cross-talk), not wave-35 (no S-box), not V-series (intra-linear present,
nonlinear init).

Triage: recalibrated wave35_lib pipeline (marg -> SEQ exact-DIFF z<10 ->
RND64 confirmation) + wave-35 committed controls (b33c KEEP / V0 KILL).
Cost bar: < 19.8u (frontier t6_b33c). Est ~3.8-4.3u/stage.
"""
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from wave35_lib import rotl, M64  # noqa: F401  (re-exported triage below)
from wave35_lib import _marg_proxy, seq_exact_diff, rnd64_exact_diff  # noqa: F401

_ODD_R1 = [r for r in range(1, 64) if r % 2 == 1]
_EVEN_M = [r for r in range(2, 64) if r % 2 == 0]


def _dpair(rng):
    a = rng.randint(1, 63)
    b = rng.randint(1, 63)
    while b == a:
        b = rng.randint(1, 63)
    return a, b


def sample_candidate(rng, nstages, n_lin=1, n_lin_y=None, init_and=True):
    """Random wave-37 candidate. All ints are Python ints (JSON-safe).

    n_lin = x-lane linear count; n_lin_y = y-lane linear count (default n_lin).
    init_and: y0 includes the key-mixed AND (nonlinear lane divergence).
      37c (init_and=False): y0 = rotl(xs,r1)^rotl(K,r2), saves ~2 levels on
      y-path (est 15 levels ≈ 18u). Needs fresh hill-climb (init AND was
      load-bearing: 2.85 -> 15.99 on 37b schedules).
    37d (x:L=3, y:L=1) KILLED 2026-10-11: DIFF-dead (z~21000).

    Stage tuple layout: (a, b, cx[0..Lx), f, g, h, i, cy[0..Ly), mx, ny)
      (a,b)   = x-lane intra AND rots (a != b)
      cx      = Lx x-lane linear rots
      (f,g)   = cross AND rots for xn's (xf & yg) term
      (h,i)   = y-lane intra AND rots (h != i)
      cy      = Ly y-lane linear rots
      (mx,ny) = cross AND rots for yn's (x_mx & y_ny) term
    """
    assert nstages >= 1, "non-vacuous: need >=1 stage"
    assert n_lin >= 1, "non-vacuous: need >=1 linear term"
    if n_lin_y is None:
        n_lin_y = n_lin
    assert n_lin_y >= 0, "y-lane can be linear-free (auxiliary)"
    r1 = rng.choice(_ODD_R1)
    r2 = rng.randint(1, 63)
    p = rng.randint(0, 63)
    q = rng.randint(0, 63)
    while q == p:
        q = rng.randint(0, 63)
    m = rng.choice(_EVEN_M)
    stages = []
    for _ in range(nstages):
        a, b = _dpair(rng)          # x-lane intra AND (a != b)
        cx = tuple(rng.randint(0, 63) for _ in range(n_lin))
        f = rng.randint(0, 63)      # cross AND: x-side
        g = rng.randint(0, 63)      # cross AND: y-side
        h, i = _dpair(rng)          # y-lane intra AND (h != i)
        cy = tuple(rng.randint(0, 63) for _ in range(n_lin_y))
        mx = rng.randint(0, 63)     # cross AND: x-side
        ny = rng.randint(0, 63)     # cross AND: y-side
        stages.append((a, b, cx, f, g, h, i, cy, mx, ny))
    return {"r1": r1, "r2": r2, "p": p, "q": q, "m": m,
            "n_lin": n_lin, "n_lin_y": n_lin_y, "init_and": init_and,
            "stages": stages}


def make_mix37(cand):
    r1, r2, p, q, m = (cand["r1"], cand["r2"], cand["p"], cand["q"], cand["m"])
    assert r1 % 2 == 1 and m % 2 == 0 and m != 0 and p != q, \
        f"fail-loud: bad init/combiner params {cand}"
    stages = cand["stages"]
    assert len(stages) >= 1, "fail-loud: empty stage list"
    n_lin = cand.get("n_lin", 1)
    n_lin_y = cand.get("n_lin_y", n_lin)
    init_and = cand.get("init_and", True)
    post_whiten = cand.get("post_whiten", True)

    def mix_fn(xs, K):
        xs = np.asarray(xs, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        assert xs.shape == K.shape, "fail-loud: xs/K shape mismatch"
        x = (xs ^ K) & M64
        if init_and:
            y = (rotl(xs, r1) ^ rotl(K, r2) ^ (rotl(xs, p) & rotl(K, q))) & M64
        else:
            y = (rotl(xs, r1) ^ rotl(K, r2)) & M64
        for st in stages:
            assert len(st) == 10, "fail-loud: stage tuple must have 10 fields"
            a, b, cx, f, g, h, i, cy, mx, ny = st
            assert len(cx) == n_lin and len(cy) == n_lin_y, \
                "fail-loud: linear-term count mismatch"
            xn = x ^ (rotl(x, a) & rotl(x, b)) ^ (rotl(x, f) & rotl(y, g))
            for c in cx:
                xn ^= rotl(x, c)
            yn = y ^ (rotl(y, h) & rotl(y, i)) ^ (rotl(x, mx) & rotl(y, ny))
            for c in cy:
                yn ^= rotl(y, c)
            x, y = (xn & M64), (yn & M64)
        if post_whiten:
            out = (x ^ rotl(y, m) ^ rotl(K, 13)) & M64
        else:
            out = (x ^ rotl(y, m)) & M64
        assert out.shape == xs.shape, "fail-loud: output shape mismatch"
        return out

    return mix_fn
