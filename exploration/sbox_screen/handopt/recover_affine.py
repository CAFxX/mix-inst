#!/usr/bin/env python3
"""Recover the (m1,c1,m2,c2) affine maps for the AFF8 pool entries.

The generator (gen_sbox8_pool_ref.py, fetched 2026-10-12 from
CAFxX/fanout main:projects/mix-sbox-search/pools/gen_sbox8_pool.py)
builds AFF8_k = L2(AES(L1(.))) with L1/L2 drawn from
random.Random(0x5B08) in order k=0..15. Replaying the RNG gives the
exact matrices; we verify the replayed tables match the GHA harvest
(ranked_sbox8_pool_20261012.json) byte-for-byte.

Output: affine_maps.json
  {name: {m1:[8 ints], c1:int, m2:[8 ints], c2:int}}
  m rows stored as ints: row r has bit i = m[r][i] (matches the
  generator's _apply_affine convention: y = c ^ xor over input bits i
  of column vector (m[0][i]..m[7][i])).
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_sbox8_pool_ref as G

HARVEST = os.path.expanduser(
    "~/workspace/mix/exploration/sbox_screen/ranked_sbox8_pool_20261012.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "affine_maps.json")

TOP5 = ["AFF8_06", "AFF8_03", "AFF8_00", "AFF8_12", "AFF8_02"]


def rows_of(m):
    rows = []
    for r in m:
        v = 0
        for i, b in enumerate(r):
            v |= (b & 1) << i
        rows.append(v)
    return rows


def main():
    harvest = json.load(open(HARVEST))
    htab = {}
    for rec in harvest["records"]:
        t = bytes.fromhex(rec["table"])
        assert len(t) == 256
        htab[rec["name"]] = list(t)

    aes = G.aes_sbox()
    # verify generator's AES matches the harvest AES_SBOX fingerprint
    haes = htab["AES_SBOX"]
    assert aes == haes, "generator AES != harvest AES_SBOX"
    assert aes[0x00] == 0x63 and aes[0x53] == 0xED and aes[0xFF] == 0x16

    rng = random.Random(0x5B08)
    out = {}
    for k in range(16):
        name = f"AFF8_{k:02d}"
        # replicate affine_variant but keep the maps
        m1 = G._rand_invertible_matrix(rng)
        c1 = rng.getrandbits(8)
        m2 = G._rand_invertible_matrix(rng)
        c2 = rng.getrandbits(8)
        tab = [G._apply_affine(aes[G._apply_affine(x, m1, c1)], m2, c2)
               for x in range(256)]
        assert tab == htab[name], f"replay mismatch for {name}"
        out[name] = {"m1": rows_of(m1), "c1": c1,
                     "m2": rows_of(m2), "c2": c2}
    json.dump(out, open(OUT, "w"), indent=1)
    print("verified replay for 16/16 AFF8 tables; wrote", OUT)
    for n in TOP5:
        e = out[n]
        print(n, "c1=%02x" % e["c1"], "c2=%02x" % e["c2"])


if __name__ == "__main__":
    main()
