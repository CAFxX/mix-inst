#!/usr/bin/env python3
"""D10 fast screen: Hypothesis D10 (batch 13) — two untested axes.

Axis 1: rot+shift 2-term LIN class. LIN(z) = z ^ rotl(z,a) ^ (z<<b) [or (z>>b)]
  on the D9-established S1-viable vehicle: 4r SCSC, Midori Sb0, CHI_A AND-chi,
  pba19, golden KS, full LIN on ALL rounds. D8 tested 1-XOR shifts (dead) and
  2-XOR rotation pairs (alive) — rot+shift 2-term is untested.
  Screen: bijectivity pre-filter (GF(2) rank of the 64x64 LIN map) -> D-screen
  on bijective ones -> keep bijective + D<50 multi-key.

Axis 2: all-S-box SSSS Midori template with full 2-XOR LIN on all rounds
  (rotation pairs (5,13),(1,2),(7,19)) — no chi AND gates, untested dynamics.
  Plus 3r SSS long shots.

Spec extension: optional "lin_terms": [[kind,n],...], kind in rotl/shl/shr.
  Takes precedence over "rots" (which keeps its legacy [a,b] rotl-pair meaning).
  LIN semantics everywhere: z = z ^ T1(z0) ^ T2(z0) applied to the PRE-LIN z.

Committed positive control: DIAG_scsc_rasc20_513_all must reproduce D9's
  exact D0=20 before ANY new result is trusted (process rule from D9/D8).
"""
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
from lin_diff import lin_cell_logp

DD = "/home/hatch/workspace/mix/exploration/directed_design"
RC_GOLDEN = [0x9E3779B97F4A7C15, 0x3C6EF372FE94F82A,
             0xDAA66D2C7DDF743F, 0x78DDE6E5FD29F054,
             0x2545F4914F6CDD1D, 0x94D049BB133111EB]
M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
U64 = np.uint64

SBOX_R = [0, 1, 2, 3, 4, 6, 8, 11, 13, 9, 7, 15, 12, 10, 5, 14]       # rasC2_0
SBOX_M = [12, 10, 13, 3, 14, 11, 15, 7, 8, 9, 1, 5, 0, 2, 4, 6]       # midori_sb0
PBOX_PBA19 = [(19 * i + 1) % 64 for i in range(64)]
CHI_A = [(1, 2, 13), (7, 19, 5)]
KS_STEPS = [13]
CONTROL_D0 = 20  # D9 d9_screen.txt DIAG_scsc_rasc20_513_all exact value


def _rotl(x, r):
    r %= 64
    if r == 0:
        return x
    r = U64(r)
    return ((x << r) | (x >> (U64(64) - r))) & M64


def _lin_term(x, kind, n):
    n %= 64
    if n == 0:
        return x
    if kind == "rotl":
        return _rotl(x, n)
    if kind == "shl":
        return (x << U64(n)) & M64
    if kind == "shr":
        return x >> U64(n)
    raise ValueError(kind)


def resolve_lin_terms(spec):
    """[(kind, n), ...]; 'lin_terms' wins, else legacy 'rots' as rotl pair."""
    lt = spec.get("lin_terms")
    if lt is not None:
        terms = [(str(k), int(n)) for k, n in lt]
    else:
        terms = [("rotl", int(v)) for v in spec["rots"]]
    for kind, n in terms:
        assert kind in ("rotl", "shl", "shr"), kind
        assert 0 <= n < 64, n
    return terms


def lin_rank(terms):
    """GF(2) rank of the 64-bit linear map z -> z ^ T1(z) ^ T2(z) ...
    terms: [(kind,n)]. rank 64 == bijective."""
    rows = []
    for j in range(64):
        r = 1 << j
        for kind, n in terms:
            if kind == "rotl":
                r |= 1 << ((j - n) % 64)
            elif kind == "shl":
                if j - n >= 0:
                    r |= 1 << (j - n)
            elif kind == "shr":
                if j + n < 64:
                    r |= 1 << (j + n)
        rows.append(r)
    rank = 0
    for col in range(64):
        piv = None
        for i in range(rank, 64):
            if (rows[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        pr = rows[rank]
        for i in range(64):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= pr
        rank += 1
    return rank


def _sbox64(x, table):
    sb = np.asarray(table, dtype=np.uint64)
    y = np.zeros_like(x)
    for i in range(16):
        y |= sb[((x >> U64(4 * i)) & U64(0xF)).astype(np.int64)] << U64(4 * i)
    return y & M64


def _chi(x, a, b, c, flavor):
    ra, rb, rc = _rotl(x, a), _rotl(x, b), _rotl(x, c)
    if flavor == "and":
        return (x ^ (ra & rb) ^ rc) & M64
    if flavor == "keccak":
        return (x ^ (ra & ((~rb) & M64)) ^ rc) & M64
    raise ValueError(flavor)


def _pbox64(x, pbox):
    pb = np.asarray(pbox, dtype=np.uint64)
    y = np.zeros_like(x)
    for i in range(64):
        y |= ((x >> U64(i)) & U64(1)) << pb[i]
    return y & M64


def lin_on_round(spec, i, layer_type, lin_override=None):
    mode = lin_override if lin_override is not None else spec.get("lin", "all")
    if isinstance(mode, set):
        return i in mode
    if mode == "all":
        return True
    if mode == "sbox":
        return layer_type == "sbox"
    if mode == "chi":
        return layer_type == "chi"
    if mode == "none":
        return False
    raise ValueError(mode)


def mix_np_spec(V, key, spec, lin_override=None):
    """Bit-exact numpy model of a batch-13-style spec dict."""
    terms = resolve_lin_terms(spec)
    x = np.asarray(V, dtype=np.uint64)
    k = U64(key)
    layers = spec["layers"]
    rc = RC_GOLDEN[: len(layers)]
    for i, L in enumerate(layers):
        rk = U64(0)
        for s in KS_STEPS:
            rk ^= _rotl(k, s * (i + 1))
        rk ^= U64(rc[i])
        t = x ^ rk
        if L["type"] == "sbox":
            y = _sbox64(t, L["sbox"])
        elif L["type"] == "chi":
            a, b, c = (int(v) for v in L["chi"])
            y = _chi(t, a, b, c, L["flavor"])
        else:
            raise ValueError(L["type"])
        z = _pbox64(y, spec["pbox"])
        if lin_on_round(spec, i, L["type"], lin_override):
            z0 = z
            for kind, n in terms:
                z = z ^ _lin_term(z0, kind, n)
            z &= M64
        x = z
    return x & M64


def diff_probe(spec, key, lin_override=None, n_deltas=12):
    N = 1 << 16
    S = np.asarray(mix_np_spec(np.arange(N, dtype=np.uint64), key, spec,
                               lin_override), dtype=np.uint64)
    n = 1 << 15
    worst_z = 0.0
    for kk in range(n_deltas):
        dl = U64(1) << U64(kk)
        xs = np.arange(n, dtype=np.uint64)
        ys = xs ^ dl
        dx = (S[xs] ^ S[ys]).astype(np.uint64)
        h8 = np.bincount((dx & U64(0xFF)).astype(np.int64),
                         minlength=256).astype(float)
        exp = n / 256.0
        chi2 = float((((h8 - exp) ** 2) / exp).sum())
        df = 255
        z = abs(chi2 - df) / math.sqrt(2.0 * df)
        worst_z = max(worst_z, z)
    return worst_z


def mk_spec(tag, pattern, sbox, chi_triples, flavor, lin_terms=None, rots=None,
            lin_mode="all", desc=""):
    layers = []
    ci = 0
    for ch in pattern:
        if ch == "S":
            layers.append({"type": "sbox", "sbox": list(sbox)})
        else:
            a, b, c = chi_triples[ci % len(chi_triples)]
            layers.append({"type": "chi", "chi": [a, b, c], "flavor": flavor})
            ci += 1
    spec = {"name": tag, "desc": desc, "layers": layers, "pattern": pattern,
            "pbox": PBOX_PBA19, "lin": lin_mode, "_d10": True}
    if lin_terms is not None:
        spec["lin_terms"] = [[k, n] for k, n in lin_terms]
        # legacy mirror for readers that only understand rots (unused for LIN)
        spec["rots"] = [n for _, n in lin_terms]
    else:
        spec["rots"] = list(rots)
    return spec


def screen_one(spec, V, keys, do_probe=True):
    """Returns (d0, logp, dm, dp0, dp1, t)."""
    t1 = time.time()
    S = mix_np_spec(V, keys[0], spec)
    d0, logp = lin_cell_logp(S)
    t_eval = time.time() - t1
    dm, dp0, dp1 = "-", "-", "-"
    if d0 <= 100 and do_probe:
        ds = []
        for k in keys:
            d, _ = lin_cell_logp(mix_np_spec(V, k, spec))
            ds.append(str(d))
        dm = ",".join(ds)
        dp0 = f"{diff_probe(spec, keys[0]):.1f}"
        dp1 = f"{diff_probe(spec, keys[2]):.1f}"
    return d0, logp, dm, dp0, dp1, t_eval


def main():
    N = 4096 * 64
    V = np.arange(N, dtype=np.uint64)
    keys = [0x0, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0]
    outp = os.path.join(DD, "results", "d10_screen.txt")
    # incremental checkpointing: every result is appended+flushed immediately,
    # so a VM reboot never loses more than the in-flight candidate.
    if os.path.exists(outp):
        os.remove(outp)

    def emit(ax, tag, d0, logp, dm, dp0, dp1, t):
        with open(outp, "a") as f:
            f.write(f"{ax} {tag} D0={d0} logp={logp:.1f} Dmulti={dm} "
                    f"dprobe0={dp0} dprobe1={dp1} t={t:.1f}s\n")
        print(f"{tag:34s} {d0:6d} {logp:6.1f} {dm:>22s} "
              f"{dp0:>8s} {dp1:>8s} {t:5.1f}s", flush=True)

    # ---- committed positive control (must reproduce D9 exactly) ----
    ctl = mk_spec("DIAG_scsc_rasc20_513_all", "SCSC", SBOX_R, CHI_A, "and",
                  rots=[5, 13], lin_mode="all")
    d0, logp, dm, dp0, dp1, t = screen_one(ctl, V, keys)
    print(f"CONTROL {ctl['name']}: D0={d0} (expect {CONTROL_D0})", flush=True)
    if d0 != CONTROL_D0:
        print(f"FATAL: positive control FAILED (D0={d0} != {CONTROL_D0}); "
              f"screen untrustworthy, aborting.", flush=True)
        sys.exit(2)
    emit("CONTROL", ctl["name"], d0, logp, dm, dp0, dp1, t)
    print("CONTROL OK — proceeding with D10 screens", flush=True)

    # ---- Axis 1: rot+shift 2-term LIN enumeration ----
    print("=== Axis 1: bijectivity pre-filter ===", flush=True)
    AX1_ROTS = [1, 2, 5, 7, 13, 19, 27]
    AX1_SHIFTS = [1, 2, 3, 4, 5, 6, 7]
    AX1_DIRS = ["shl", "shr"]
    ax1_bij = []
    ax1_dead = []
    for a in AX1_ROTS:
        for b in AX1_SHIFTS:
            for d_ in AX1_DIRS:
                terms = [("rotl", a), (d_, b)]
                rk = lin_rank(terms)
                if rk == 64:
                    ax1_bij.append((a, b, d_))
                else:
                    ax1_dead.append((a, b, d_, rk))
    print(f"bijective: {len(ax1_bij)}/{len(AX1_ROTS)*len(AX1_SHIFTS)*len(AX1_DIRS)}",
          flush=True)
    with open(outp, "a") as f:
        f.write(f"# axis-1 bijectivity: {len(ax1_bij)}/"
                f"{len(AX1_ROTS)*len(AX1_SHIFTS)*len(AX1_DIRS)} bijective\n")
        for a, b, d_, rk in ax1_dead:
            f.write(f"# NOT bijective: rotl{a}+{d_}{b} rank={rk}\n")
        for a, b, d_ in ax1_bij:
            f.write(f"# bijective: rotl{a}+{d_}{b}\n")
    for a, b, d_, rk in ax1_dead:
        print(f"  NOT bijective: rotl{a}+{d_}{b} rank={rk}", flush=True)

    print(f"{'candidate':34s} {'D0':>6s} {'logp':>6s} "
          f"{'Dmulti':>22s} {'dprobe0':>8s} {'dprobe1':>8s} {'t':>5s}",
          flush=True)
    for a, b, d_ in ax1_bij:
        tag = f"ax1_scsc_midori_r{a}_{d_}{b}"
        spec = mk_spec(tag, "SCSC", SBOX_M, CHI_A, "and",
                       lin_terms=[("rotl", a), (d_, b)], lin_mode="all",
                       desc=f"D10 axis-1: LIN=x^rotl(x,{a})^({d_}{b})")
        d0, logp, dm, dp0, dp1, t = screen_one(spec, V, keys)
        emit("AX1", tag, d0, logp, dm, dp0, dp1, t)

    # ---- Axis 2: all-S-box SSSS + 3r SSS long shots ----
    print("=== Axis 2: SSSS / SSS ===", flush=True)
    ax2 = [
        ("ax2_ssss_midori_513", "SSSS", SBOX_M, [5, 13]),
        ("ax2_ssss_midori_12", "SSSS", SBOX_M, [1, 2]),
        ("ax2_ssss_midori_719", "SSSS", SBOX_M, [7, 19]),
        ("ax2_ssss_midori_1327", "SSSS", SBOX_M, [13, 27]),
        ("ax2_ssss_rasc20_513", "SSSS", SBOX_R, [5, 13]),
        ("ax2_sss_midori_513", "SSS", SBOX_M, [5, 13]),
        ("ax2_sss_midori_12", "SSS", SBOX_M, [1, 2]),
        ("ax2_sss_rasc20_513", "SSS", SBOX_R, [5, 13]),
    ]
    for tag, pattern, sbox, rots in ax2:
        spec = mk_spec(tag, pattern, sbox, CHI_A, "and", rots=rots,
                       lin_mode="all",
                       desc=f"D10 axis-2: {pattern} pure-S-box, LIN{rots}")
        d0, logp, dm, dp0, dp1, t = screen_one(spec, V, keys)
        emit("AX2", tag, d0, logp, dm, dp0, dp1, t)

    print("wrote results/d10_screen.txt (incremental)")


if __name__ == "__main__":
    main()
