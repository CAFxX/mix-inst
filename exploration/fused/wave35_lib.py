#!/usr/bin/env python3
"""Wave-35 shared library: two-state diffusion (AND-cascade + S-box layer).

Two-state design rationale (co-designed against the two confirmed failure modes):
  (a) catastrophic DIFF bias without determinism: the S-box layer (Midori Sb0,
      a 4-bit permutation) has NO probability-1 differential, so it breaks the
      deterministic differential skeleton that kills every AND-cascade variant.
      The AND stages provide the linear diffusion the S-box layer lacks.
  (b) sequential-input subspace collapse: on sequential inputs each nibble of x
      cycles through all 16 values, so the S-box layer is FULLY exercised --
      no collapse. Template B puts the S-box layer FIRST so the AND stages
      never see collapsed (sequential) inputs at all.

Triage (per candidate):
  1. marg proxy (PB single-bit x10 keys; RD SEQ / PTR-j8 / RND64 x10 keys)
  2. SEQ exact-DIFF: lin_diff.diff_cell_logps, all 10 keys, KEEP bar max|z| < 10
  3. RND64 exact-DIFF (same statistic on random-64 pairs): KEEP confirmation
     on survivors only. Rationale (measured 2026-10-10): SEQ amplifies the
     defect ~4x vs RND64, so SEQ is the harder gate; a SEQ-KILL is decisive.
"""
import math
import sys

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps, N_DIFF_PAIRS, DIFF_KS
from screen_lib import KEYS, N

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
assert len(KEYS10) == 10

# Midori Sb0 (depth-2, optimal 4-bit class: max DDT 4, max LAT 4)
SB0 = np.array([12, 10, 13, 3, 14, 11, 15, 7, 8, 9, 1, 5, 0, 2, 4, 6],
               dtype=np.uint64)


def rotl(x, r):
    r %= 64
    if r == 0:
        return x & M64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64


def sbox_layer(x):
    """16x parallel Midori Sb0 on 4-bit nibbles. Bijective (S-box is a perm)."""
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(x)
    for i in range(16):
        nib = (x >> np.uint64(4 * i)) & np.uint64(0xF)
        y |= SB0[nib.astype(np.int64)] << np.uint64(4 * i)
    return y & M64


# P-box: bit-scatter (9i)%64. Pure wiring (free in unit-delay). Chosen so that
# for sequential inputs (low 16 bits vary), the 16 varying bits spread as
# exactly 2 per output byte (measured optimal among odd multipliers).
# The (19i+1)%64 P-box was KILLED: it mapped 6/8 low output bits from
# constant high input bits (low8 z=182813).
_PBOX = np.array([(9 * i) % 64 for i in range(64)], dtype=np.uint64)


def pbox(x):
    x = np.asarray(x, dtype=np.uint64)
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> np.uint64(i)) & np.uint64(1)) << _PBOX[i]
    return y & M64


def splayer(x):
    """Two-state S-layer: S-box (nonlinear, no prob-1 differential) + P-box
    (cross-nibble scatter). Bijective. The P-box is load-bearing: without it
    the S-box layer leaves 48 high bits constant on sequential inputs
    (measured: marg lp -7e13)."""
    return pbox(sbox_layer(x))


def and_stage(x, a, b, c):
    """Frontier 3-term AND stage: x ^= (ra & rb) ^ rc."""
    return (x ^ (rotl(x, a) & rotl(x, b)) ^ rotl(x, c)) & M64


def make_mix(template, and_sched, inter_rot=0):
    """template in {'A','B','C','E','F','G'}; and_sched = list of (a,b,c); inter_rot for C.
    E = [A,A,A,A,S,A]: 4 ANDs diffuse SEQ input past the S-layer collapse
    threshold (measured: S-layer output lp -6.1 after 4 ANDs, -12616 after 3),
    S-layer breaks the deterministic differential skeleton, final AND mixes.
    G = [A,A,A,A,S]: boundary probe -- 4 ANDs only, S-layer last. Threshold
    measured marg lp=-6.1 passes the -9.0 pre-filter; est cost ~17.4u makes it
    the only cost-eligible 4-AND+S form (E/F at 5 ANDs measure/est ~20.7u,
    dominated). If G passes triage, the ledger's "quality needs >=5 ANDs"
    claim is falsified and G escalates to S0.
    A/B/C kept for the record (S-layer-before-diffusion variants, killed by
    the nibble-collapse mechanism)."""
    def mix_fn(xs, K):
        xs = np.asarray(xs, dtype=np.uint64)
        K = np.asarray(K, dtype=np.uint64)
        x = (xs ^ K) & M64
        ai = iter(and_sched)
        if template == "A":      # A A S A A
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))
            x = splayer(x)
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))
        elif template == "B":    # S A A A
            x = splayer(x)
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))
            x = and_stage(x, *next(ai))
        elif template == "C":    # A S A S A  (nibble-misaligning rot between S layers)
            x = and_stage(x, *next(ai))
            x = splayer(x); x = rotl(x, inter_rot)
            x = and_stage(x, *next(ai))
            x = splayer(x)
            x = and_stage(x, *next(ai))
        elif template == "E":    # A A A A S A
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))
            x = splayer(x)
            x = and_stage(x, *next(ai))
        elif template == "F":    # A A S A A A (S after 2 ANDs; the live design)
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))
            x = splayer(x)
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))
            x = and_stage(x, *next(ai))
        elif template == "G":    # A A A A S (4 ANDs, S-layer LAST, no final AND;
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))  # boundary
            x = and_stage(x, *next(ai)); x = and_stage(x, *next(ai))  # probe:
            x = splayer(x)        # threshold says S-layer-after-4-ANDs marg
        else:                     # lp=-6.1 passes the -9.0 pre-filter bar;
            raise ValueError(template)  # cost ~4x3.3+4.2=17.4u, cost-eligible
        return (x ^ rotl(K, 13)) & M64
    return mix_fn


# ---------------- marg proxy (adapted from wave34_probe, + RND64 scenario) ------
def _marg_proxy(mix_fn):
    from screen_lib import strided_distinct
    from screen_cal import perbit_zarray, logp_twosided_normal, fisher_logp
    from marg_proxy import _reduction_logps
    # Bars ANCHORED to S1-clean frontiers (recalibrated 2026-10-11):
    # b33c PB worst -9.73 / RD worst -7.88; al_and6a RD worst -7.9.
    # The inherited +0.5-margin bars (-9.87/-7.1) REJECTED both frontiers.
    # Pre-filter bars must pass known-good designs (false positives OK,
    # false negatives NOT); the real gates are S1/S2/S3.
    PB_BAR = -11.0
    RD_BAR = -9.0

    worst = (float("inf"), None)
    Vsb = (np.uint64(1) << np.arange(64, dtype=np.uint64))
    for key in KEYS:
        K = np.full(64, np.uint64(key), dtype=np.uint64)
        zs = perbit_zarray(mix_fn(Vsb, K))
        lp = fisher_logp([logp_twosided_normal(z) for z in zs])
        m = lp - PB_BAR
        if m < worst[0]:
            worst = (m, f"PB SINGLE-BIT {key:#x} lp={lp:.1f}")
    n = 1 << 16
    rng = np.random.default_rng(0x35)
    scenarios = (
        ("SEQ", np.arange(n, dtype=np.uint64)),
        ("PTR-j8", strided_distinct(0, 8, n)),
        ("RND64", rng.integers(0, 2**64, size=n, dtype=np.uint64)),
    )
    for scen, V in scenarios:
        for key in KEYS:
            K = np.full(n, np.uint64(key), dtype=np.uint64)
            lp = fisher_logp(_reduction_logps(mix_fn(V, K)))
            m = lp - RD_BAR
            if m < worst[0]:
                worst = (m, f"RD {scen} {key:#x} lp={lp:.1f}")
    return worst[0] > 0, worst


# ---------------- exact DIFF triage -------------------------------------------
def seq_exact_diff(mix_fn):
    """Max worst|z| over 10 keys, sequential inputs (the S1-DIFF methodology)."""
    NN = 1 << 18  # pairs (x, x^2^k), k<=17, span [0, 2^18)
    V = np.arange(NN, dtype=np.uint64)
    assert V.shape[0] == NN  # fail-loud: non-vacuous gate
    worst, worst_cfg = 0.0, None
    for key in KEYS10:
        K = np.full(NN, np.uint64(key), dtype=np.uint64)
        S = np.asarray(mix_fn(V, K), dtype=np.uint64)
        assert S.shape[0] == NN
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst:
            worst, worst_cfg = wz, key
    return worst, worst_cfg


def _chi2_z(dx, npairs):
    h8 = np.bincount((dx & np.uint64(0xFF)).astype(np.int64),
                     minlength=256).astype(float)
    exp = npairs / 256.0
    chi2 = float((((h8 - exp) ** 2) / exp).sum())
    df = 255
    return abs(chi2 - df) / math.sqrt(2.0 * df)


def rnd64_exact_diff(mix_fn, n_pairs=1 << 17, seed=0x64):
    """Same low-8-bit chi2 statistic as diff_cell_logps, but on random-64
    base points (pairs (xr, xr^2^k), xr uniform in [0,2^64))."""
    worst, worst_cfg = 0.0, None
    for key in KEYS10:
        K = np.full(n_pairs, np.uint64(key), dtype=np.uint64)
        rng = np.random.default_rng((seed ^ (key & 0xFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF)
        for k in DIFF_KS:
            dl = np.uint64(1) << np.uint64(k)
            xs = rng.integers(0, 2**64, size=n_pairs, dtype=np.uint64)
            ys = xs ^ dl
            S = np.asarray(mix_fn(xs, K), dtype=np.uint64)
            T = np.asarray(mix_fn(ys, K), dtype=np.uint64)
            assert S.shape[0] == n_pairs and T.shape[0] == n_pairs
            dx = (S ^ T).astype(np.uint64)
            z = _chi2_z(dx, n_pairs)
            if z > worst:
                worst, worst_cfg = z, (key, k)
    return worst, worst_cfg
