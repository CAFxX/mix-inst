#!/usr/bin/env python3
"""D9 fast screen: generalized S1-LIN D screen + reduced DIFF probe.

Reads specs/batch12_specs.json and builds a numpy model per spec, mirroring
mk_model.py / gen_verilog.py mixed-template semantics bit-exactly:
  round i: rk = rotl64(key,13*(i+1)) ^ RC[i]; t = x ^ rk
           y = NL_i(t)   (S: nibble sbox table from spec; C: chi w/ flavor)
           z = PBOX(y); if LIN on: z = z ^ rotl(z,a) ^ rotl(z,b); x = z

Screens (D8 methodology):
  (A) D screen: V=arange(4096*64) consecutive inputs, key=0x0,
      real lin_diff.lin_cell_logp -> D/4096. D8 pass bar: D~16-33; dead: D>=1000.
  (B) multi-key D (0x0, 0xFFF...F, 0x123456789ABCDEF0) for survivors.
  (C) reduced DIFF probe: N=2^16, deltas 2^0..2^11, worst |z| of low-8-bit
      chi2, keys 0x0 and 0x1234... (dd9_a ref 3.7, dd9_k ref 8.4).

Also runs screen-only diagnostic configs (NOT part of batch-12):
  - SCSC rasC2_0 CHI_A lin513 all      (D8 control: expect D~20)
  - SCSC midori CHI_A lin513 sbox-only (sanity: expect DEAD like rasC2_0 D=281)
  - CSCS midori CHI_A lin513 sbox-only (lever-4: does chi-first allow LIN relax?)
  - CSCS midori CHI_A lin513 chi-only  (lever-4)
  - CSCS midori CHI_A drop-last        (lever-4)
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


def _rotl(x, r):
    r %= 64
    if r == 0:
        return x
    r = U64(r)
    return ((x << r) | (x >> (U64(64) - r))) & M64


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
    """Bit-exact numpy model of a batch-12-style spec dict."""
    x = np.asarray(V, dtype=np.uint64)
    k = U64(key)
    layers = spec["layers"]
    rots = [int(v) for v in spec["rots"]]
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
            for r in rots:
                z = z ^ _rotl(z0, r)
            z &= M64
        x = z
    return x & M64


def diff_probe(spec, key, lin_override=None, n_deltas=12):
    """Reduced DIFF: deltas 2^k for k in 0..n_deltas-1, pairs x in [0,2^15).
    Returns worst |z| over deltas (low-8-bit chi2)."""
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


def mk_diag(tag, pattern, sbox, chi_triples, flavor, rots, lin_mode):
    layers = []
    ci = si = 0
    for ch in pattern:
        if ch == "S":
            layers.append({"type": "sbox", "sbox": list(sbox)})
            si += 1
        else:
            a, b, c = chi_triples[ci % len(chi_triples)]
            layers.append({"type": "chi", "chi": [a, b, c], "flavor": flavor})
            ci += 1
    return {"name": tag, "layers": layers, "pattern": pattern, "pbox": PBOX_PBA19,
            "rots": list(rots), "lin": lin_mode, "_diag": True}


def main():
    specs = json.load(open(os.path.join(DD, "specs", "batch12_specs.json")))
    # screen-only diagnostic configs
    specs += [
        mk_diag("DIAG_scsc_rasc20_513_all", "SCSC", SBOX_R, CHI_A, "and",
                [5, 13], "all"),                    # D8 control: expect D~20
        mk_diag("DIAG_scsc_midori_513_sboxonly", "SCSC", SBOX_M, CHI_A, "and",
                [5, 13], "sbox"),                   # sanity: expect DEAD
        mk_diag("DIAG_cscs_midori_513_sboxonly", "CSCS", SBOX_M, CHI_A, "and",
                [5, 13], "sbox"),                   # lever-4 LIN relax?
        mk_diag("DIAG_cscs_midori_513_chionly", "CSCS", SBOX_M, CHI_A, "and",
                [5, 13], "chi"),                    # lever-4 LIN relax?
        mk_diag("DIAG_cscs_midori_513_droplast", "CSCS", SBOX_M, CHI_A, "and",
                [5, 13], {0, 1, 2}),                # lever-4 LIN relax?
    ]

    N = 4096 * 64
    V = np.arange(N, dtype=np.uint64)
    keys = [0x0, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0]
    print(f"{'candidate':32s} {'D0':>6s} {'logp':>6s} "
          f"{'Dmulti':>22s} {'dprobe0':>8s} {'dprobe1':>8s} {'t':>5s}",
          flush=True)
    results = []
    for spec in specs:
        tag = spec["name"]
        t1 = time.time()
        S = mix_np_spec(V, keys[0], spec)
        d0, logp = lin_cell_logp(S)
        t_eval = time.time() - t1
        dm, dp0, dp1 = "-", "-", "-"
        if d0 <= 100:  # screen-clean: run multi-key + DIFF probe
            ds = []
            for k in keys:
                d, _ = lin_cell_logp(mix_np_spec(V, k, spec))
                ds.append(str(d))
            dm = ",".join(ds)
            dp0 = f"{diff_probe(spec, keys[0]):.1f}"
            dp1 = f"{diff_probe(spec, keys[2]):.1f}"
        results.append((tag, d0, logp, dm, dp0, dp1))
        print(f"{tag:32s} {d0:6d} {logp:6.1f} {dm:>22s} "
              f"{dp0:>8s} {dp1:>8s} {t_eval:5.1f}s", flush=True)
    with open(os.path.join(DD, "results", "d9_screen.txt"), "w") as f:
        for tag, d0, logp, dm, dp0, dp1 in results:
            f.write(f"{tag} D0={d0} logp={logp:.1f} Dmulti={dm} "
                    f"dprobe0={dp0} dprobe1={dp1}\n")
    print("wrote results/d9_screen.txt")


if __name__ == "__main__":
    main()
