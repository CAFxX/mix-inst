#!/usr/bin/env python3
"""R25 Track B: S-box candidate generation + standalone mapped-DNF-depth screen.

Generates 8 candidates biased for shallow mapped DNF depth:
  - 4 random 4-bit permutations with DU<=8 (S1 has DU 4; allow some slack)
  - 2 affine-equivalents of S1: S'(x) = A(S1(B(x)^b1))^b2 (same DU/LAT/deg)
  - 2 inverse-based in GF(2^4): x -> x^{-1} (DU 4 optimal), two polynomials
Each is synthesized STANDALONE (16 parallel nibbles) through the authorized
run_synth.py flow; the mapped delay in u is the DNF-depth proxy.
Keeps the 3 shallowest for full-S0 in the pba19b01 construction.
"""
import itertools
import os
import random
import subprocess
import sys

EXP = "/home/hatch/workspace/mix/exploration"
R25 = os.path.join(EXP, "round25")
OUT = os.path.join(R25, "sbox_screen")

S1 = [0, 1, 2, 4, 3, 8, 15, 12, 9, 5, 11, 6, 7, 14, 13, 10]


def du_of(sbox):
    """Differential uniformity of a 4-bit S-box."""
    n = 16
    mx = 0
    for da in range(1, n):
        cnt = {}
        for x in range(n):
            db = sbox[x] ^ sbox[x ^ da]
            cnt[db] = cnt.get(db, 0) + 1
        mx = max(mx, max(cnt.values()))
    return mx


def gf16_inv(poly):
    """Multiplicative inverse in GF(2^4) defined by poly (e.g. 0x13 = x^4+x+1)."""
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


def rand_affine(rng):
    """Random invertible 4x4 binary matrix + constant -> affine map."""
    while True:
        m = [[rng.randint(0, 1) for _ in range(4)] for _ in range(4)]
        # invertibility via GF(2) rank
        rows = [sum(bit << j for j, bit in enumerate(row)) for row in m]
        basis = {}
        for r in rows:
            x = r
            while x:
                b = x.bit_length() - 1
                if b in basis:
                    x ^= basis[b]
                else:
                    basis[b] = x
                    break
            else:
                continue
            if x == 0:
                break
        if len(basis) == 4:
            break
    c = rng.randint(0, 15)

    def f(x):
        y = 0
        for i in range(4):
            bit = 0
            for j in range(4):
                bit ^= m[i][j] * ((x >> j) & 1)
            y |= (bit & 1) << i
        return y ^ c
    return f


def main():
    rng = random.Random(0x250B)
    cands = {"S1_baseline": S1}

    # 4 random permutations with DU <= 8
    n = 0
    while n < 4:
        p = list(range(16))
        rng.shuffle(p)
        if du_of(p) <= 8:
            n += 1
            cands[f"rnd{n}"] = p

    # 2 affine-equivalents of S1
    for k in (1, 2):
        A, B = rand_affine(rng), rand_affine(rng)
        cands[f"aff{k}"] = [A(S1[B(x)]) for x in range(16)]

    # 2 inverse-based (different irreducible polynomials)
    cands["inv13"] = gf16_inv(0x13)  # x^4+x+1
    cands["inv19"] = gf16_inv(0x19)  # x^4+x^3+1

    for name, sb in cands.items():
        assert sorted(sb) == list(range(16)), name
        print(f"{name}: DU={du_of(sb)}")

    # emit standalone verilog for each, using the generator's own QM-DNF
    # emission (gen_r25.dnf_for_sbox_bit) so the proxy measures exactly what
    # the full candidate's S-layer would contain
    sys.path.insert(0, R25)
    sys.path.insert(0, os.path.join(R25, "models"))
    import gen_r25
    os.makedirs(OUT, exist_ok=True)
    results = {}
    for name, sb in cands.items():
        lines = [f"module sbox_{name}(input [63:0] x, output [63:0] y);",
                 "reg [63:0] y;",
                 "always @(*) begin"]
        lines += ["    " + l.strip() for l in
                  gen_r25._v_sbox16_stmts(sb, "x", "y")]
        lines += ["end", "endmodule"]
        vp = os.path.join(OUT, f"sbox_{name}.v")
        with open(vp, "w") as f:
            f.write("\n".join(lines) + "\n")

    # synthesize each through the authorized flow
    for name in cands:
        vp = os.path.join(OUT, f"sbox_{name}.v")
        wd = os.path.join(OUT, f"synth_{name}")
        os.makedirs(wd, exist_ok=True)
        r = subprocess.run(
            [sys.executable, os.path.join(EXP, "run_synth.py"),
             vp, f"sbox_{name}", wd],
            capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        # parse RESULT delay
        delay = None
        for line in out.split("\n"):
            if line.startswith("RESULT"):
                for tok in line.split():
                    if tok.startswith("delay="):
                        delay = float(tok.split("=")[1].rstrip("u"))
        results[name] = delay
        print(f"{name}: standalone delay = {delay}u")

    # rank (exclude baseline from selection, keep for reference)
    ranked = sorted(((v, k) for k, v in results.items() if k != "S1_baseline" and v is not None))
    print("\nRanked (non-baseline):")
    for v, k in ranked:
        print(f"  {v}u  {k}  DU={du_of(cands[k])}")
    keep = [k for _, k in ranked[:3]]
    print(f"\nBaseline S1: {results['S1_baseline']}u")
    print(f"KEEP: {keep}")
    with open(os.path.join(OUT, "keep.txt"), "w") as f:
        f.write("\n".join(keep) + "\n")


if __name__ == "__main__":
    main()
