#!/usr/bin/env python3
"""FA4(b2): round-by-round differential trace for the offending delta.
For key=0 (and control key), delta=2^8: after each of the 4 rounds, compute
the chi2 z-score of the low-8-bit state difference. Locates where the
non-uniformity originates and how it evolves."""
import json
import math
import sys

import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP + "/round25/models")
sys.path.insert(0, EXP + "/round25")
import r25

CAND = "r25_spn_pba19_sb_midori_sb0_nw"
N = 1 << 17


def chi2_z(counts, exp):
    chi2 = float((((counts - exp) ** 2) / exp).sum())
    df = len(counts) - 1
    return abs(chi2 - df) / math.sqrt(2.0 * df)


def round_states(v, k, spec, sbox_np):
    """Yield state after each round (numpy)."""
    x = v.copy()
    rots = tuple(spec["rots"])
    pbox = spec["pbox"]
    for i in range(spec["nrounds"]):
        rk = r25._rk64_np(np.uint64(k), i, spec.get("ks", "golden"))
        t = r25._sbox_layer64_np(x ^ rk, sbox_np)
        p = r25._perm_np(t, pbox)
        x = r25._lin_rots_np(p, rots, spec.get("include_id", True))
        yield x


def main():
    specs = json.load(open(EXP + "/round25/specs25.json"))
    spec = next(s for s in specs if s["name"] == CAND)
    sbox_np = np.array(spec["sbox"], dtype=np.uint64)
    V = np.arange(N, dtype=np.uint64)
    for key in (0x0, 0xFFFFFFFFFFFFFFFF):
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        states_x = list(round_states(V, key, spec, sbox_np))
        states_y = list(round_states(V ^ np.uint64(1 << 8), key, spec, sbox_np))
        zs = []
        for sx, sy in zip(states_x, states_y):
            dx = (sx ^ sy).astype(np.uint64)
            h = np.bincount((dx & np.uint64(0xFF)).astype(np.int64),
                            minlength=256).astype(float)
            zs.append(chi2_z(h, N / 256.0))
        # also full-state: fraction of dx with low8 == 0 (truncated)
        print(f"key={key:#018x} round-wise low8 z: " +
              " ".join(f"r{i+1}={z:.1f}" for i, z in enumerate(zs)), flush=True)


if __name__ == "__main__":
    main()
