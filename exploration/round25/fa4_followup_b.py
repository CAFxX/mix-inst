#!/usr/bin/env python3
"""FA4(b): identify the offending delta's structure and check vs MIDORI Sb0 DDT.
1. Sb0 DDT: list count-4 entries, esp. rows for nibble deltas 1 and 4.
2. Empirical at key=0, delta=2^8: top values of (dx & 0xFF) and of full dx.
3. Linear-echo test: push DDT-predicted round-1 S-box out-diffs through the
   linear layer, check low-8-bit concentration.
4. Control: same empirical histogram at key=0xffffffffffffffff (clean key)."""
import importlib.util
import sys
from collections import Counter

import numpy as np

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP)
sys.path.insert(0, FB + "/src")

SB0 = [0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7,
       0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6]
CAND = "r25_spn_pba19_sb_midori_sb0_nw"
N = 1 << 18


def load(cand):
    spec = importlib.util.spec_from_file_location(
        "model_" + cand, f"{FB}/candidates/{cand}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.mix_np


def ddt(sbox):
    t = [[0] * 16 for _ in range(16)]
    for din in range(16):
        for x in range(16):
            t[din][sbox[x] ^ sbox[x ^ din]] += 1
    return t


def main():
    T = ddt(SB0)
    c4 = [(din, dout) for din in range(16) for dout in range(16) if T[din][dout] == 4]
    print(f"Sb0 DDT: {len(c4)} entries of 4 (optimal: 15)")
    print("count-4 entries (din->dout):", ["%x->%x" % p for p in c4])
    for din in (1, 4):
        row = [(dout, T[din][dout]) for dout in range(16) if T[din][dout] >= 2]
        print(f"DDT row din={din}: {row}")

    mix_np = load(CAND)
    for key, tag in [(0x0, "key=0"), (0xFFFFFFFFFFFFFFFF, "key=ff..f")]:
        V = np.arange(1 << 17, dtype=np.uint64)
        S = np.asarray(mix_np(V, np.full(1 << 17, np.uint64(key), dtype=np.uint64)),
                       dtype=np.uint64)
        for k in (8, 10):
            dl = np.uint64(1) << np.uint64(k)
            ys = V ^ dl
            dx = (S[V] ^ S[ys]).astype(np.uint64)
            lo = (dx & np.uint64(0xFF)).astype(np.int64)
            h = np.bincount(lo, minlength=256)
            exp = len(V) / 256.0
            top = np.argsort(h)[::-1][:6]
            print(f"{tag} delta=2^{k}: exp/pair={exp:.0f} top low8: " +
                  ", ".join(f"{int(i):#04x}:{int(h[i])}" for i in top))
            hc = Counter(dx.tolist())
            topf = hc.most_common(4)
            print(f"   top full dx: " + ", ".join(f"{v:#018x}:{c}" for v, c in topf))


if __name__ == "__main__":
    main()
