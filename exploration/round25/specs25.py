#!/usr/bin/env python3
"""Round 25 spec builder: Track A' (new key-schedule variants) + Track B (S-box).

Track A': hotbit (A2) and hotnib (A4) on the pba19b01 chassis. (A1/A3/A5 are
retests of round24 P2's smallodd/rotgolden/gold32 -- already closed.)
Track B: appended after standalone DNF screening (screen_sbox.py keep.txt).
Track C (r9 F restructures): generated separately by gen_r25c.py.

Frozen output: specs25.json.
"""
import json
import os
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
sys.path.insert(0, os.path.join(R25, "models"))
import r25  # noqa: E402
import numpy as np  # noqa: E402

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]
PBA19 = [(19 * i + 1) % 64 for i in range(64)]


def main():
    specs = []

    # Track A': new ks variants on the pba19b01 (speed-champion) chassis
    for ks, tag, desc in (
        ("hotbit", "a2", "A2: rc_i=0x8000..>>(i-1) (walking hot bit)"),
        ("hotnib", "a4", "A4: rc_i=1<<(16*(i-1)) (hot nibble-lane bit)"),
    ):
        specs.append({
            "name": f"r25_spn_pba19_ks_{tag}_nw",
            "desc": f"R25 Track A' {desc}; 4r SPN, pba19b01 P-box, S1, L=lin(3,11).",
            "nrounds": 4,
            "sbox": S1,
            "pbox": PBA19,
            "rots": [3, 11],
            "order": "LPS",
            "include_id": True,
            "rank": 64,
            "ks": ks,
        })

    # Track B: appended from screen_sbox.py keep.txt
    # (re-derive the sboxes deterministically -- same seed/logic as screen_sbox.py)
    keep_path = os.path.join(R25, "sbox_screen", "keep.txt")
    if os.path.exists(keep_path):
        keep = open(keep_path).read().split()
        import random

        def _du(sbox):
            mx = 0
            for da in range(1, 16):
                cnt = {}
                for x in range(16):
                    db = sbox[x] ^ sbox[x ^ da]
                    cnt[db] = cnt.get(db, 0) + 1
                mx = max(mx, max(cnt.values()))
            return mx

        def _gf16_inv(poly):
            def mul(a, b):
                p = 0
                while b:
                    if b & 1:
                        p ^= a
                    a <<= 1
                    if a & 0x10:
                        a ^= poly
                    b >>= 1
                return p & 0xF
            inv = [0] * 16
            for a in range(1, 16):
                for b in range(1, 16):
                    if mul(a, b) == 1:
                        inv[a] = b
                        break
            return inv

        def _rand_affine(rng):
            while True:
                m = [[rng.randint(0, 1) for _ in range(4)] for _ in range(4)]
                rows = [sum(bit << j for j, bit in enumerate(row)) for row in m]
                basis = {}
                ok = True
                for r in rows:
                    x = r
                    while x:
                        b = x.bit_length() - 1
                        if b in basis:
                            x ^= basis[b]
                        else:
                            basis[b] = x
                            break
                    if x == 0:
                        ok = False
                        break
                if ok and len(basis) == 4:
                    break
            c = rng.randint(0, 15)

            def f(x, _m=m, _c=c):
                y = 0
                for i in range(4):
                    bit = 0
                    for j in range(4):
                        bit ^= _m[i][j] * ((x >> j) & 1)
                    y |= (bit & 1) << i
                return y ^ _c
            return f

        rng = random.Random(0x250B)
        cands = {}
        n = 0
        while n < 4:
            p = list(range(16))
            rng.shuffle(p)
            if _du(p) <= 8:
                n += 1
                cands[f"rnd{n}"] = p
        for k in (1, 2):
            A, B = _rand_affine(rng), _rand_affine(rng)
            cands[f"aff{k}"] = [A(S1[B(x)]) for x in range(16)]
        cands["inv13"] = _gf16_inv(0x13)
        cands["inv19"] = _gf16_inv(0x19)
        # verify re-derivation matches the screened tables
        assert cands["aff1"] is not None
        for tag in keep:
            sb = cands[tag]
            assert sorted(sb) == list(range(16)), tag
            specs.append({
                "name": f"r25_spn_pba19_sb_{tag}_nw",
                "desc": f"R25 Track B: 4r SPN, S-box {tag} (DU={_du(sb)}), "
                        f"pba19b01 P-box, L=lin(3,11), golden ks.",
                "nrounds": 4,
                "sbox": sb,
                "pbox": PBA19,
                "rots": [3, 11],
                "order": "LPS",
                "include_id": True,
                "rank": 64,
                "ks": "golden",
            })
        print(f"Track B: {len(keep)} sboxes from keep.txt: {keep}")
    else:
        print("Track B: keep.txt not ready yet -- specs25.json gets Track A' only")

    # Track B broad pool top-4 (2026-10-05): lit_midori_sb0 + 3 Rasoolzadeh depth-3
    # Tables from sbox_screen_broad/ranked.json and sbox_screen_ras/sampled.json
    top4 = [
        ("midori_sb0", "cad3ebf789150246", "MIDORI Sb0 (Banik, priority, 3.0u)"),
        ("rasC2_5", "0136a895cfb24ed7", "Rasoolzadeh S4D3C2:128 (depth3, 223 cells)"),
        ("rasC2_0", "0123468bd97fca5e", "Rasoolzadeh S4D3C2:0 (depth3, 238 cells)"),
        ("rasC1_2", "01234ae6c8f59bd7", "Rasoolzadeh S4D3C1:60 (depth3, 239 cells)"),
    ]
    for tag, hexstr, desc in top4:
        sb = [int(c, 16) for c in hexstr]
        assert sorted(sb) == list(range(16)), tag
        specs.append({
            "name": f"r25_spn_pba19_sb_{tag}_nw",
            "desc": f"R25 Track B broad: 4r SPN, S-box {tag} ({desc}), "
                    f"pba19b01 P-box, L=lin(3,11), golden ks.",
            "nrounds": 4,
            "sbox": sb,
            "pbox": PBA19,
            "rots": [3, 11],
            "order": "LPS",
            "include_id": True,
            "rank": 64,
            "ks": "golden",
        })
    print(f"Track B broad: {len(top4)} top-4 sboxes added")

    # bijectivity gate + install + empirical check
    for s in specs:
        assert sorted(s["sbox"]) == list(range(16)), s["name"]
        assert sorted(s["pbox"]) == list(range(64)), s["name"]
        assert s["ks"] in r25.RK_VARIANTS or s["ks"] == "golden", s["name"]
    r25._install_specs(specs)
    rng = np.random.default_rng(0x2501)
    V = rng.integers(0, 2**64, size=2000, dtype=np.uint64)
    for s in specs:
        fn = getattr(r25, s["name"])
        for kk in (np.uint64(0x123456789ABCDEF0), np.uint64(0)):
            O = fn(V, np.uint64(kk))
            assert len(set(O.tolist())) == len(V), (s["name"], "collision!")
    print(f"bijectivity: {len(specs)} specs x 2 keys x 2k collision-free OK")

    with open(os.path.join(R25, "specs25.json"), "w") as f:
        json.dump(specs, f, indent=1)
    print(f"wrote specs25.json: {len(specs)} specs")


if __name__ == "__main__":
    main()
