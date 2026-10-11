#!/usr/bin/env python3
"""FA4(b3): key-dependent DDT-entry selection.
For delta=2^8 at key=0 vs key=ff: histogram the round-1 S-box OUTPUT nibble
difference at nibble 2 (input delta = bit0 of nibble), and show which DDT
entries each key's alignment selects. Sequential inputs x in [0,2^17)."""
import sys

import numpy as np

EXP = "/home/hatch/workspace/mix/exploration"
sys.path.insert(0, EXP + "/round25/models")
import r25

SB0 = np.array([0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7,
                0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6], dtype=np.uint64)
N = 1 << 17


def main():
    # DDT row for nibble input delta 1
    ddt_row = {}
    for x in range(16):
        d = int(SB0[x] ^ SB0[x ^ 1])
        ddt_row[d] = ddt_row.get(d, 0) + 1
    print("DDT row din=1:", dict(sorted(ddt_row.items())))
    for key in (0x0, 0xFFFFFFFFFFFFFFFF, 0x5555555555555555):
        rk0 = int(r25._rk64_np(np.uint64(key), 0, "golden"))
        xs = np.arange(N, dtype=np.uint64)
        nib = ((xs ^ np.uint64(rk0)) >> np.uint64(8)) & np.uint64(0xF)
        n = nib.astype(np.int64)
        dout = (SB0[n] ^ SB0[n ^ 1]).astype(np.int64)
        h = np.bincount(dout, minlength=16)
        # probability mass on count-4 DDT entries (dout=2) vs uniform 1/16
        print(f"key={key:#018x} rk0_nib2={((rk0 >> 8) & 0xF):x} "
              f"P(dout=2)= {h[2]/N:.4f} (DDT count-4 entry; uniform=0.0625) "
              f"top dout: " +
              ", ".join(f"{i}:{h[i]/N:.3f}" for i in np.argsort(h)[::-1][:4]))


if __name__ == "__main__":
    main()
