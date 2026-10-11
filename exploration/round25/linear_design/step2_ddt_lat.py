#!/usr/bin/env python3
"""Step 2: DDT, LAT, and per-(input-bit -> output-bit) transition weights.
Weights quantify how much differential/linear 'flow' each bit position carries."""
import json
import numpy as np

S = [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14]
SINv = [0]*16
for i, v in enumerate(S):
    SINv[v] = i

def ddt():
    D = np.zeros((16,16), dtype=int)
    for din in range(16):
        for x in range(16):
            D[din, S[x] ^ S[x ^ din]] += 1
    return D

def lat():
    # LAT[a][b] = #{x : parity(a&x)==parity(b&S(x))} - 8
    L = np.zeros((16,16), dtype=int)
    for a in range(16):
        for b in range(16):
            s = 0
            for x in range(16):
                px = bin(a & x).count('1') & 1
                py = bin(b & S[x]).count('1') & 1
                s += 1 if px == py else -1
            L[a,b] = s // 2
    return L

def bit_weights(D, L):
    # Wd[i][j] = sum over (din,dout) of DDT[din][dout] * [din_i=1] * [dout_j=1]
    # normalized: fraction of total differential weight flowing i->j
    Wd = np.zeros((4,4))
    for din in range(16):
        for dout in range(16):
            w = D[din, dout]
            if w == 0: continue
            for i in range(4):
                if (din >> i) & 1:
                    for j in range(4):
                        if (dout >> j) & 1:
                            Wd[i, j] += w
    # Wl[i][j] = sum over (a,b) of |LAT[a][b]| * [a_i=1] * [b_j=1]
    Wl = np.zeros((4,4))
    for a in range(16):
        for b in range(16):
            w = abs(L[a,b])
            if w == 0 or (a == 0 and b == 0): continue
            for i in range(4):
                if (a >> i) & 1:
                    for j in range(4):
                        if (b >> j) & 1:
                            Wl[i, j] += w
    return Wd, Wl

if __name__ == "__main__":
    D = ddt()
    L = lat()
    print("DDT max (excl 0,0):", D[1:,1:].max(), "| DU =", D[1:, :].max())
    print("DU check:", D[D>0].max() if True else "")
    # count DDT entries by value
    vals, counts = np.unique(D[1:,:], return_counts=True)
    print("DDT value histogram (din!=0):", dict(zip(vals.tolist(), counts.tolist())))
    print("LAT max abs (excl 0,0):", np.abs(L[1:,1:]).max())
    # branch-relevant: min nonzero DDT
    print("DDT min nonzero:", D[(D>0)].min())
    Wd, Wl = bit_weights(D, L)
    print("\nDifferential bit-flow Wd[input_bit][output_bit]:")
    print(np.round(Wd / Wd.sum() * 100, 1))
    print("\nLinear bit-flow Wl[input_bit][output_bit]:")
    print(np.round(Wl / Wl.sum() * 100, 1))
    # combined normalized score
    W = Wd / Wd.sum() + Wl / Wl.sum()
    print("\nCombined W (rows=input bit, cols=output bit):")
    print(np.round(W, 4))
    # per-output-bit total flow (which output bits carry most weight)
    print("\nPer-output-bit total differential flow:", Wd.sum(axis=0).round(1))
    print("Per-output-bit total linear flow:", Wl.sum(axis=0).round(1))
    # per-input-bit total
    print("\nPer-input-bit total differential flow:", Wd.sum(axis=1).round(1))
    json.dump({"Wd": (Wd/Wd.sum()).tolist(), "Wl": (Wl/Wl.sum()).tolist(),
               "W_combined": W.tolist(),
               "DU": int(D[1:,:].max()), "LATmax": int(np.abs(L).max())},
              open("ddt_lat_weights.json", "w"), indent=1)
    # save full DDT/LAT for reference
    json.dump({"DDT": D.tolist(), "LAT": L.tolist()}, open("ddt_lat_full.json", "w"))
    print("\nwrote ddt_lat_weights.json, ddt_lat_full.json")
