#!/usr/bin/env python3
"""Generate Verilog RTL for the 3 fused prototypes."""
import os

OUT = "/home/hatch/workspace/mix/exploration/fused/rtl"
os.makedirs(OUT, exist_ok=True)

# --- f8_maj5: 4-stage majority-5 ---
# maj5(a,b,c,d,e) = OR of 10 AND3 triples. In Verilog, use assign with & and |.
MAJ5_STAGES = [
    (1, 7, 23, 37, 53),
    (3, 11, 29, 41, 59),
    (5, 13, 31, 43, 61),
    (2, 17, 33, 47, 57),
]
RC1 = [0x9e3779b97f4a7c15, 0x3c6ef372fe94f82a, 0xdaa66d2c7ddf743f, 0x78dde6e5fd29f054]

def rotl_expr(sig, r, w=64):
    r %= w
    if r == 0:
        return sig
    return f"{{{sig}[{w-1-r}:0], {sig}[{w-1}:{w-r}]}}"

def maj5_expr(a, b, c, d, e):
    triples = [
        f"({a}&{b}&{c})", f"({a}&{b}&{d})", f"({a}&{b}&{e})",
        f"({a}&{c}&{d})", f"({a}&{c}&{e})", f"({a}&{d}&{e})",
        f"({b}&{c}&{d})", f"({b}&{c}&{e})", f"({b}&{d}&{e})",
        f"({c}&{d}&{e})",
    ]
    return "(" + "|".join(triples) + ")"

with open(f"{OUT}/f8_maj5.v", "w") as f:
    f.write("module f8_maj5(input [63:0] v, input [63:0] k, output [63:0] o);\n")
    f.write("wire [63:0] x0 = v ^ k;\n")
    prev = "x0"
    for i, (a, b, c, d, e) in enumerate(MAJ5_STAGES):
        ra = rotl_expr(prev, a); rb = rotl_expr(prev, b); rc = rotl_expr(prev, c)
        rd = rotl_expr(prev, d); re = rotl_expr(prev, e)
        m = maj5_expr(ra, rb, rc, rd, re)
        f.write(f"wire [63:0] x{i+1} = ({m} ^ {rotl_expr(prev, (a+32)%64)} ^ 64'h{RC1[i]:016x});\n")
        prev = f"x{i+1}"
    f.write(f"assign o = {prev} ^ {rotl_expr('k', 13)};\n")
    f.write("endmodule\n")

# --- f8_nlcarry: add + XOR-rotate + add + XOR ---
with open(f"{OUT}/f8_nlcarry.v", "w") as f:
    f.write("module f8_nlcarry(input [63:0] v, input [63:0] k, output [63:0] o);\n")
    f.write("wire [63:0] x0 = v ^ k;\n")
    f.write("wire [63:0] x1 = x0 + 64'h9e3779b97f4a7c15;\n")
    f.write(f"wire [63:0] x2 = x1 ^ {rotl_expr('x1', 32)} ^ {rotl_expr('x1', 17)};\n")
    f.write("wire [63:0] x3 = x2 + 64'h3c6ef372fe94f82a;\n")
    f.write(f"assign o = x3 ^ {rotl_expr('x3', 29)} ^ {rotl_expr('k', 11)};\n")
    f.write("endmodule\n")

# --- f8_sbox8: 3 rounds of byte-S-box + shuffle + rotl ---
# S-box: b ^ ((b rol 3) & (b rol 5)) ^ ((b rol 1) | (b rol 7)), per byte
def sbox8_expr(b):
    # b is an 8-bit signal expression
    r3 = f"{{{b}[4:0], {b}[7:5]}}"  # rol 3
    r5 = f"{{{b}[2:0], {b}[7:3]}}"  # rol 5
    r1 = f"{{{b}[6:0], {b}[7]}}"    # rol 1
    r7 = f"{{{b}[0], {b}[7:1]}}"    # rol 7
    return f"({b} ^ ({r3} & {r5}) ^ ({r1} | {r7}))"

with open(f"{OUT}/f8_sbox8.v", "w") as f:
    f.write("module f8_sbox8(input [63:0] v, input [63:0] k, output [63:0] o);\n")
    f.write("wire [63:0] x0 = v ^ k;\n")
    # Byte permutation: [3,0,5,1,6,2,7,4]
    def shuffle(sig):
        # new byte i comes from old byte perm[i]
        perm = [3, 0, 5, 1, 6, 2, 7, 4]
        parts = []
        for new_pos, old_pos in enumerate(perm):
            parts.append(f"{sig}[{old_pos*8+7}:{old_pos*8}]")
        return "{" + ", ".join(parts) + "}"
    prev = "x0"
    for r in range(3):
        # S-box layer: apply to each byte
        byte_exprs = []
        for i in range(8):
            b = f"{prev}[{i*8+7}:{i*8}]"
            byte_exprs.append(sbox8_expr(b))
        f.write(f"wire [63:0] s{r} = {{{', '.join(reversed(byte_exprs))}}};\n")
        sh = shuffle(f"s{r}")
        rc = (0x9e3779b97f4a7c15 >> (r * 11)) & 0xFFFFFFFFFFFFFFFF
        f.write(f"wire [63:0] x{r+1} = ({sh} ^ 64'h{rc:016x});\n")
        f.write(f"wire [63:0] xr{r+1} = {rotl_expr(f'x{r+1}', 13)};\n")
        prev = f"xr{r+1}"
    f.write(f"assign o = {prev} ^ {rotl_expr('k', 13)};\n")
    f.write("endmodule\n")

print("RTL generated in", OUT)
